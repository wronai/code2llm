"""Pipeline Detector — networkx-based pipeline auto-detection.

Uses call graph analysis with networkx to:
- Build a directed graph from function calls
- Find longest paths (pipeline candidates)
- Group pipelines by module domain (NLP, Analysis, Export, Refactor, etc.)
- Label entry/exit points
- Aggregate purity per pipeline using SideEffectDetector

Sprint 3 (v0.3.2): Replaces the custom DFS chain-tracing in FlowExporter.
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx

from ..core.models import AnalysisResult, FunctionInfo
from .side_effects import SideEffectDetector, SideEffectInfo
from .type_inference import TypeInferenceEngine

logger = logging.getLogger(__name__)

# Thresholds
MIN_PIPELINE_LENGTH = 3
MAX_PIPELINES = 12
CC_HIGH = 15

# Patterns to exclude from analysis
EXCLUDE_PATTERNS = frozenset({
    'venv', '.venv', 'env', '.env', 'publish-env', 'test-env',
    'site-packages', 'node_modules', '__pycache__', '.git',
    'dist', 'build', 'egg-info', '.tox', '.mypy_cache',
})

# Module-to-domain mapping heuristics
DOMAIN_KEYWORDS: Dict[str, List[str]] = {
    "NLP": ["nlp", "natural", "language", "intent", "entity",
            "query", "normalize", "tokenize", "match"],
    "Analysis": ["analysis", "analyzer", "analyse", "analyze",
                 "metric", "complexity", "cfg", "dfg", "call_graph"],
    "Export": ["export", "exporter", "render", "format", "output",
               "toon", "mermaid", "json_export", "yaml_export"],
    "Refactor": ["refactor", "smell", "suggest", "fix", "patch",
                 "template", "prompt", "engine"],
    "Core": ["core", "config", "model", "base", "util", "helper"],
    "IO": ["io", "file", "path", "read", "write", "load", "save",
           "cache", "storage"],
}


@dataclass
class PipelineStage:
    """A single stage in a detected pipeline."""
    name: str
    qualified_name: str
    signature: str
    cc: float
    purity: str  # pure | IO | cache | mutation
    side_effect_summary: str
    is_entry: bool = False
    is_exit: bool = False


@dataclass
class Pipeline:
    """A detected pipeline with stages, purity info, and domain."""
    name: str
    domain: str
    stages: List[PipelineStage] = field(default_factory=list)
    entry_point: str = ""
    exit_point: str = ""
    entry_type: str = "?"
    exit_type: str = "?"
    pure_count: int = 0
    total_stages: int = 0
    bottleneck: Optional[PipelineStage] = None
    path_length: int = 0

    @property
    def purity_ratio(self) -> float:
        return self.pure_count / self.total_stages if self.total_stages else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "domain": self.domain,
            "stages": [
                {
                    "name": s.name,
                    "qualified": s.qualified_name,
                    "signature": s.signature,
                    "cc": s.cc,
                    "purity": s.purity,
                    "is_entry": s.is_entry,
                    "is_exit": s.is_exit,
                }
                for s in self.stages
            ],
            "entry_point": self.entry_point,
            "exit_point": self.exit_point,
            "entry_type": self.entry_type,
            "exit_type": self.exit_type,
            "pure_count": self.pure_count,
            "total_stages": self.total_stages,
            "bottleneck": {
                "name": self.bottleneck.name,
                "cc": self.bottleneck.cc,
            } if self.bottleneck else None,
        }


class PipelineDetector:
    """Detect pipelines in a codebase using networkx graph analysis.

    Builds a call graph as a DiGraph, finds longest paths as pipeline
    candidates, groups by module domain, and labels entry/exit points.
    """

    def __init__(
        self,
        type_engine: Optional[TypeInferenceEngine] = None,
        side_effect_detector: Optional[SideEffectDetector] = None,
    ):
        self._type_engine = type_engine or TypeInferenceEngine()
        self._se_detector = side_effect_detector or SideEffectDetector()

    def detect(
        self,
        funcs: Dict[str, FunctionInfo],
        se_info: Optional[Dict[str, SideEffectInfo]] = None,
    ) -> List[Pipeline]:
        """Detect pipelines from function call graph.

        Args:
            funcs: qualified_name -> FunctionInfo mapping (pre-filtered)
            se_info: optional pre-computed side-effect info

        Returns:
            List of Pipeline objects sorted by path length desc.
        """
        if se_info is None:
            se_info = self._se_detector.analyze_all(funcs)

        # Build networkx DiGraph
        graph = self._build_graph(funcs)
        if graph.number_of_nodes() == 0:
            return []

        # Find pipeline candidates (longest paths in DAG)
        paths = self._find_pipeline_paths(graph)

        # Build Pipeline objects with stages, purity, domain
        pipelines = self._build_pipelines(paths, funcs, se_info)

        # Sort by path length desc
        pipelines.sort(key=lambda p: p.path_length, reverse=True)

        return pipelines[:MAX_PIPELINES]

    # ------------------------------------------------------------------
    # graph construction
    # ------------------------------------------------------------------
    def _build_graph(self, funcs: Dict[str, FunctionInfo]) -> nx.DiGraph:
        """Build a directed graph from function call relationships."""
        G = nx.DiGraph()

        for qname, fi in funcs.items():
            G.add_node(qname, module=fi.module, name=fi.name,
                       class_name=fi.class_name)

        for qname, fi in funcs.items():
            for callee in fi.calls:
                resolved = self._resolve_callee(callee, funcs)
                if resolved and resolved != qname:  # no self-loops
                    G.add_edge(qname, resolved)

        return G

    # ------------------------------------------------------------------
    # path finding
    # ------------------------------------------------------------------
    def _find_pipeline_paths(self, graph: nx.DiGraph) -> List[List[str]]:
        """Find longest paths in the call graph as pipeline candidates.

        Strategy:
        1. Find all source nodes (in-degree 0) as potential entry points
        2. Find all sink nodes (out-degree 0) as potential exit points
        3. For each source, find longest simple path to any sink
        4. Also consider longest paths in each weakly connected component
        """
        paths: List[List[str]] = []

        # Get source nodes (in-degree 0) as potential pipeline entry points
        sources = [n for n in graph.nodes() if graph.in_degree(n) == 0]

        # If no natural sources, use nodes with low in-degree
        if not sources:
            sources = sorted(graph.nodes(),
                             key=lambda n: graph.in_degree(n))[:5]

        # Try to find longest paths from each source
        used_nodes: Set[str] = set()
        for source in sources:
            best_path = self._longest_path_from(graph, source, used_nodes)
            if len(best_path) >= MIN_PIPELINE_LENGTH:
                paths.append(best_path)
                used_nodes.update(best_path)

        # Also try: for each weakly connected component, find the longest path
        for component in nx.weakly_connected_components(graph):
            if len(component) < MIN_PIPELINE_LENGTH:
                continue
            # Skip if heavily overlapping with existing paths
            overlap = len(component & used_nodes)
            if overlap > len(component) * 0.5:
                continue

            subgraph = graph.subgraph(component)
            path = self._longest_path_in_dag(subgraph)
            if len(path) >= MIN_PIPELINE_LENGTH:
                # Check overlap with existing paths
                new_overlap = sum(1 for n in path if n in used_nodes)
                if new_overlap <= len(path) * 0.5:
                    paths.append(path)
                    used_nodes.update(path)

        return paths

    def _longest_path_from(
        self, graph: nx.DiGraph, source: str, used: Set[str]
    ) -> List[str]:
        """Find the longest simple path from a source node."""
        best: List[str] = [source]

        # BFS/DFS with depth limit for performance
        stack: List[Tuple[str, List[str], Set[str]]] = [
            (source, [source], {source})
        ]
        max_depth = 10

        while stack:
            current, path, visited = stack.pop()
            if len(path) > len(best):
                best = path

            if len(path) >= max_depth:
                continue

            for successor in graph.successors(current):
                if successor not in visited:
                    # Prefer nodes not yet used in other pipelines
                    stack.append((
                        successor,
                        path + [successor],
                        visited | {successor}
                    ))

        return best

    def _longest_path_in_dag(self, subgraph: nx.DiGraph) -> List[str]:
        """Find the longest path in a DAG subgraph using networkx.

        Falls back to DFS if the subgraph has cycles.
        """
        try:
            # networkx dag_longest_path works on DAGs
            return nx.dag_longest_path(subgraph)
        except nx.NetworkXUnfeasible:
            # Has cycles — fall back to finding longest simple path via DFS
            sources = [n for n in subgraph.nodes()
                       if subgraph.in_degree(n) == 0]
            if not sources:
                sources = list(subgraph.nodes())[:3]

            best: List[str] = []
            for source in sources:
                path = self._longest_path_from(subgraph, source, set())
                if len(path) > len(best):
                    best = path
            return best

    # ------------------------------------------------------------------
    # pipeline construction
    # ------------------------------------------------------------------
    def _build_pipelines(
        self,
        paths: List[List[str]],
        funcs: Dict[str, FunctionInfo],
        se_info: Dict[str, SideEffectInfo],
    ) -> List[Pipeline]:
        """Convert raw paths into Pipeline objects with full metadata."""
        pipelines: List[Pipeline] = []

        for path in paths:
            stages = self._build_stages(path, funcs, se_info)
            if not stages:
                continue

            domain = self._classify_domain(path, funcs)
            name = self._derive_pipeline_name(path, funcs, domain)

            # Entry/exit labeling
            stages[0].is_entry = True
            stages[-1].is_exit = True

            # Purity aggregation
            pure_count = sum(1 for s in stages if s.purity == "pure")
            bottleneck = max(stages, key=lambda s: s.cc) if stages else None

            # Entry/exit types
            entry_type = self._get_entry_type(funcs.get(path[0]))
            exit_type = self._get_exit_type(funcs.get(path[-1]))

            pipeline = Pipeline(
                name=name,
                domain=domain,
                stages=stages,
                entry_point=path[0],
                exit_point=path[-1],
                entry_type=entry_type,
                exit_type=exit_type,
                pure_count=pure_count,
                total_stages=len(stages),
                bottleneck=bottleneck,
                path_length=len(path),
            )
            pipelines.append(pipeline)

        return pipelines

    def _build_stages(
        self, path: List[str],
        funcs: Dict[str, FunctionInfo],
        se_info: Dict[str, SideEffectInfo],
    ) -> List[PipelineStage]:
        """Build PipelineStage objects for each node in a path."""
        stages: List[PipelineStage] = []
        for qname in path:
            fi = funcs.get(qname)
            if not fi:
                continue
            cc = fi.complexity.get("cyclomatic_complexity", 0)
            se = se_info.get(qname)
            purity = se.classification if se else "pure"
            se_summary = se.side_effect_summary if se else "pure"
            sig = self._type_engine.get_typed_signature(fi)

            stages.append(PipelineStage(
                name=fi.name,
                qualified_name=qname,
                signature=sig,
                cc=cc,
                purity=purity,
                side_effect_summary=se_summary,
            ))
        return stages

    # ------------------------------------------------------------------
    # domain classification
    # ------------------------------------------------------------------
    def _classify_domain(
        self, path: List[str], funcs: Dict[str, FunctionInfo]
    ) -> str:
        """Classify pipeline domain by analyzing module names and function names."""
        scores: Dict[str, int] = defaultdict(int)

        for qname in path:
            fi = funcs.get(qname)
            if not fi:
                continue
            text = f"{fi.module} {fi.name}".lower()
            for domain, keywords in DOMAIN_KEYWORDS.items():
                for kw in keywords:
                    if kw in text:
                        scores[domain] += 1

        if scores:
            return max(scores, key=scores.get)
        return "Unknown"

    def _derive_pipeline_name(
        self, path: List[str],
        funcs: Dict[str, FunctionInfo],
        domain: str,
    ) -> str:
        """Derive a human-readable pipeline name."""
        # Use the dominant sub-module name
        module_counts: Dict[str, int] = defaultdict(int)
        for qname in path:
            fi = funcs.get(qname)
            if fi:
                parts = fi.module.split(".")
                # Use most specific module component
                for part in parts:
                    if part and part not in ("code2flow", "__init__"):
                        module_counts[part] += 1

        if module_counts:
            dominant = max(module_counts, key=module_counts.get)
            # Capitalize and use domain if module name is generic
            if dominant in ("core", "base", "utils", "helpers"):
                return domain
            return dominant.capitalize()

        return domain

    # ------------------------------------------------------------------
    # type helpers
    # ------------------------------------------------------------------
    def _get_entry_type(self, fi: Optional[FunctionInfo]) -> str:
        """Get the input type of a pipeline's entry point."""
        if not fi:
            return "?"
        args = self._type_engine.get_arg_types(fi)
        for arg in args:
            if arg["name"] == "self":
                continue
            if arg.get("type"):
                return arg["type"]
            return arg["name"]
        return "?"

    def _get_exit_type(self, fi: Optional[FunctionInfo]) -> str:
        """Get the output type of a pipeline's exit point."""
        if not fi:
            return "?"
        ret = self._type_engine.get_return_type(fi)
        return ret if ret else "?"

    # ------------------------------------------------------------------
    # callee resolution
    # ------------------------------------------------------------------
    def _resolve_callee(
        self, callee: str, funcs: Dict[str, FunctionInfo]
    ) -> Optional[str]:
        """Resolve callee name to qualified name."""
        if callee in funcs:
            return callee
        for qname in funcs:
            if qname.endswith(f".{callee}"):
                return qname
        return None
