"""Mermaid Exporter for code2llm.

Three distinct outputs:
  - export()           → flow.mmd   — full call graph with CC-based styling
  - export_call_graph() → calls.mmd  — simplified call graph (edges only, no isolates)
  - export_compact()    → compact_flow.mmd — module-level aggregation

New 3-level flow diagrams (Plan R1):
  - export_flow_compact()   → flow.mmd — architectural view (~50 nodes)
  - export_flow_detailed()  → flow_detailed.mmd — per-module view (~150 nodes)
  - export_flow_full()      → flow_full.mmd — full debug view (all nodes)
"""

from collections import defaultdict
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from .base import BaseExporter, export_format
from code2llm.core.models import AnalysisResult
from .mermaid_flow_helpers import (
    _entry_points,
    _filtered_functions,
    _group_functions_by_module,
    _render_architecture_view,
    _render_flow_edges,
    _render_flow_styles,
    _render_module_subgraphs,
)


@export_format("mermaid", description="Mermaid diagram format", extension=".mmd")
class MermaidExporter(BaseExporter):
    """Export call graph to Mermaid format."""

    # ------------------------------------------------------------------ #
    # 1. flow.mmd — full graph with CC styling
    # ------------------------------------------------------------------ #
    def export(self, result: AnalysisResult, output_path: str, **kwargs) -> Optional[Path]:
        """Export full flow diagram with CC-based node shapes and styling."""
        lines = ["flowchart TD"]

        # Subgraphs per module
        self._render_subgraphs(result, lines)

        # Edges — all cross-function calls
        self._render_edges(result, lines, limit=600)

        # CC-based styling
        self._render_cc_styles(result, lines)

        return self._write(output_path, lines)

    def _render_subgraphs(self, result: AnalysisResult, lines: List[str]) -> None:
        """Render module subgraphs with CC-shaped nodes."""
        modules: Dict[str, list] = {}
        for func_name, fi in result.functions.items():
            module = self._module_of(func_name)
            modules.setdefault(module, []).append((func_name, fi))

        for module, funcs in sorted(modules.items()):
            safe_module = self._safe_module(module)
            lines.append(f"    subgraph {safe_module}")
            for func_name, fi in funcs[:60]:
                sid = self._readable_id(func_name)
                short = fi.name[:35]
                cc = self._get_cc(fi)
                if cc >= 15:
                    lines.append(f'        {sid}{{{{{short} CC={cc}}}}}')
                elif cc >= 8:
                    lines.append(f'        {sid}("{short} CC={cc}")')
                else:
                    lines.append(f'        {sid}["{short}"]')
            lines.append("    end")

    def _render_edges(self, result: AnalysisResult, lines: List[str], limit: int = 600) -> None:
        """Render cross-function call edges up to limit."""
        seen_edges: Set[Tuple[str, str]] = set()
        for func_name, fi in result.functions.items():
            src = self._readable_id(func_name)
            for callee in fi.calls[:15]:
                resolved = self._resolve(callee, result.functions)
                if resolved and resolved != func_name:
                    dst = self._readable_id(resolved)
                    edge = (src, dst)
                    if edge not in seen_edges:
                        seen_edges.add(edge)
                        lines.append(f"    {src} --> {dst}")
                        if len(seen_edges) >= limit:
                            return
            if len(seen_edges) >= limit:
                return

    def _render_cc_styles(self, result: AnalysisResult, lines: List[str]) -> None:
        """Add CC-based class styling for high/medium complexity nodes."""
        lines.append("")
        lines.append("    classDef highCC fill:#ff6b6b,stroke:#c92a2a,color:#fff")
        lines.append("    classDef medCC fill:#ffd43b,stroke:#f08c00,color:#000")
        high_nodes = []
        med_nodes = []
        for func_name, fi in result.functions.items():
            cc = self._get_cc(fi)
            sid = self._readable_id(func_name)
            if cc >= 15:
                high_nodes.append(sid)
            elif cc >= 8:
                med_nodes.append(sid)
        if high_nodes:
            lines.append(f"    class {','.join(high_nodes[:30])} highCC")
        if med_nodes:
            lines.append(f"    class {','.join(med_nodes[:30])} medCC")

    @staticmethod
    def _get_cc(fi) -> int:
        """Extract cyclomatic complexity from FunctionInfo."""
        if isinstance(fi.complexity, dict):
            return fi.complexity.get('cyclomatic_complexity', 0)
        return fi.complexity or 0

    # ------------------------------------------------------------------ #
    # 2. calls.mmd — edges only, no isolated nodes
    # ------------------------------------------------------------------ #
    def export_call_graph(self, result: AnalysisResult, output_path: str) -> None:
        """Export simplified call graph — only connected nodes."""
        lines = ["flowchart LR"]

        # Collect connected nodes first
        connected: Set[str] = set()
        edges: List[Tuple[str, str]] = []
        for func_name, fi in result.functions.items():
            for callee in fi.calls[:10]:
                resolved = self._resolve(callee, result.functions)
                if resolved and resolved != func_name:
                    connected.add(func_name)
                    connected.add(resolved)
                    edges.append((func_name, resolved))
                    if len(edges) >= 500:
                        break
            if len(edges) >= 500:
                break

        # Group connected nodes by module
        modules: Dict[str, list] = {}
        for fn in connected:
            module = self._module_of(fn)
            fi = result.functions.get(fn)
            if fi:
                modules.setdefault(module, []).append((fn, fi))

        for module, funcs in sorted(modules.items()):
            safe_module = self._safe_module(module)
            lines.append(f"    subgraph {safe_module}")
            for func_name, fi in funcs:
                sid = self._readable_id(func_name)
                short = fi.name[:30]
                lines.append(f'        {sid}["{short}"]')
            lines.append("    end")

        # Edges
        seen: Set[Tuple[str, str]] = set()
        for src, dst in edges:
            pair = (self._readable_id(src), self._readable_id(dst))
            if pair not in seen:
                seen.add(pair)
                lines.append(f"    {pair[0]} --> {pair[1]}")

        self._write(output_path, lines)

    # ------------------------------------------------------------------ #
    # 3. compact_flow.mmd — module-level aggregation
    # ------------------------------------------------------------------ #
    def export_compact(self, result: AnalysisResult, output_path: str) -> None:
        """Export module-level graph: one node per module, weighted edges."""
        lines = ["flowchart TD"]

        # Compute module stats
        mod_funcs: Dict[str, int] = defaultdict(int)
        mod_lines: Dict[str, int] = defaultdict(int)
        for func_name, fi in result.functions.items():
            module = self._module_of(func_name)
            mod_funcs[module] += 1
            mod_lines[module] += fi.end_line - fi.line if hasattr(fi, 'end_line') and fi.end_line else 0

        # Cross-module edges with weights
        cross_edges: Dict[Tuple[str, str], int] = defaultdict(int)
        for func_name, fi in result.functions.items():
            src_mod = self._module_of(func_name)
            for callee in fi.calls:
                resolved = self._resolve(callee, result.functions)
                if resolved:
                    dst_mod = self._module_of(resolved)
                    if dst_mod != src_mod:
                        cross_edges[(src_mod, dst_mod)] += 1

        # Only modules with cross-edges
        active_mods: Set[str] = set()
        for (s, d) in cross_edges:
            active_mods.add(s)
            active_mods.add(d)

        # Add all modules with functions as fallback
        if not active_mods:
            active_mods = set(mod_funcs.keys())

        # Nodes — module boxes
        for mod in sorted(active_mods):
            sid = self._safe_module(mod)
            nf = mod_funcs.get(mod, 0)
            lines.append(f'    {sid}["{mod}<br/>{nf} funcs"]')

        # Weighted edges
        for (src, dst), weight in sorted(cross_edges.items(), key=lambda x: -x[1]):
            s = self._safe_module(src)
            d = self._safe_module(dst)
            if weight > 3:
                lines.append(f"    {s} ==>|{weight}| {d}")
            else:
                lines.append(f"    {s} -->|{weight}| {d}")

        self._write(output_path, lines)

    # ------------------------------------------------------------------ #
    # 4. NEW 3-level flow diagrams (Plan R1)
    # ------------------------------------------------------------------ #

    # Default skip patterns for noise reduction
    SKIP_PATTERNS = ('examples', 'benchmarks', 'demo_langs', 'tests', 'scripts')

    def _should_skip_module(self, module: str, include_examples: bool = False) -> bool:
        """Check if module should be skipped (examples, benchmarks, etc.)."""
        if include_examples:
            return False
        mod_lower = module.lower()
        return any(pat in mod_lower for pat in self.SKIP_PATTERNS)

    def _is_entry_point(self, func_name: str, fi, result: AnalysisResult) -> bool:
        """Detect if function is an entry point (main, cli, api entry)."""
        name = fi.name
        # Common entry point patterns
        if name in ('main', 'cli_main', 'run', 'start', 'serve'):
            return True
        if name.startswith('main_') or name.endswith('_main'):
            return True
        # CLI commands
        if 'cli' in func_name.lower() and name not in ('__init__', 'create_parser'):
            return True
        # API handlers
        if func_name.startswith('code2llm.api.'):
            return True
        # Entry points have no incoming calls from within the project
        has_incoming = any(func_name in (c.calls if hasattr(c, 'calls') else []) 
                          for c in result.functions.values())
        if not has_incoming and name not in ('__init__', '__getattr__'):
            return True
        return False

    def _build_callers_graph(self, result: AnalysisResult) -> Dict[str, Set[str]]:
        """Build reverse graph: map each function to its callers."""
        callers: Dict[str, Set[str]] = defaultdict(set)
        for func_name, fi in result.functions.items():
            for callee in fi.calls:
                resolved = self._resolve(callee, result.functions)
                if resolved:
                    callers[resolved].add(func_name)
        return callers

    def _find_leaves(self, result: AnalysisResult) -> Set[str]:
        """Find leaf nodes (functions that don't call other project functions)."""
        leaves = set()
        for func_name, fi in result.functions.items():
            has_internal_call = any(
                self._resolve(c, result.functions) for c in fi.calls
            )
            if not has_internal_call:
                leaves.add(func_name)
        return leaves

    def _longest_path_dfs(self, result: AnalysisResult, start: str, visited: Set[str]) -> List[str]:
        """DFS to find longest path from start node."""
        if start in visited:
            return []
        visited = visited | {start}
        fi = result.functions.get(start)
        if not fi:
            return [start]

        longest: List[str] = []
        for callee in fi.calls:
            resolved = self._resolve(callee, result.functions)
            if resolved and resolved not in visited:
                path = self._longest_path_dfs(result, resolved, visited)
                if len(path) > len(longest):
                    longest = path

        return [start] + longest

    def _select_longest_path(self, result: AnalysisResult, entry_points: List[str]) -> List[str]:
        """Select the longest path from all entry points."""
        max_path: List[str] = []
        for ep in entry_points:
            if ep in result.functions:
                path = self._longest_path_dfs(result, ep, set())
                if len(path) > len(max_path):
                    max_path = path
        return max_path

    def _find_critical_path(self, result: AnalysisResult, entry_points: List[str]) -> Set[str]:
        """Find the longest path from entry points (critical path)."""
        if not entry_points:
            return set()

        # Build data structures
        self._build_callers_graph(result)
        self._find_leaves(result)

        # Find longest path from each entry point
        max_path = self._select_longest_path(result, entry_points)
        return set(max_path)

    def export_flow_compact(self, result: AnalysisResult, output_path: str,
                           include_examples: bool = False) -> None:
        """Export compact architectural view (~50 nodes).
        
        Shows entry points, high-level modules, and critical path.
        """
        lines = ["flowchart TD"]
        lines.append("")
        lines.append("    %% Entry points (blue)")
        lines.append("    classDef entry fill:#4dabf7,stroke:#1971c2,color:#fff")
        lines.append("")
        filtered_funcs = _filtered_functions(
            result,
            self._module_of,
            self._should_skip_module,
            include_examples,
        )
        entry_points = _entry_points(filtered_funcs, result, self._is_entry_point)
        critical_path = self._find_critical_path(result, entry_points)
        _render_architecture_view(
            lines,
            filtered_funcs,
            entry_points,
            critical_path,
            self._module_of,
            self._readable_id,
            self._get_cc,
        )
        self._write(output_path, lines)

    def export_flow_detailed(self, result: AnalysisResult, output_path: str,
                            include_examples: bool = False) -> None:
        """Export detailed per-module view (~150 nodes).
        
        Shows all significant functions per module with CC annotations.
        """
        lines = ["flowchart TD"]
        lines.append("")
        lines.append("    %% Styling definitions")
        lines.append("    classDef highCC fill:#ff6b6b,stroke:#c92a2a,color:#fff")
        lines.append("    classDef medCC fill:#ffd43b,stroke:#f08c00,color:#000")
        lines.append("    classDef entry fill:#4dabf7,stroke:#1971c2,color:#fff")
        lines.append("")
        filtered_funcs = _filtered_functions(
            result,
            self._module_of,
            self._should_skip_module,
            include_examples,
        )
        entry_points = _entry_points(filtered_funcs, result, self._is_entry_point)
        modules = _group_functions_by_module(filtered_funcs, self._module_of)
        _render_module_subgraphs(
            lines,
            modules,
            entry_points,
            short_len=35,
            readable_id=self._readable_id,
            safe_module=self._safe_module,
            get_cc=self._get_cc,
            sort_funcs=True,
            max_funcs=40,
        )
        _render_flow_edges(lines, filtered_funcs, self._readable_id, self._resolve, calls_per_function=10, limit=200)
        _render_flow_styles(
            lines,
            filtered_funcs,
            entry_points,
            self._readable_id,
            self._get_cc,
            high_limit=30,
            med_limit=30,
            entry_limit=10,
        )
        self._write(output_path, lines)

    def export_flow_full(self, result: AnalysisResult, output_path: str,
                        include_examples: bool = False) -> None:
        """Export full debug view with all nodes (original flow.mmd).
        
        This is the original export() behavior with optional filtering.
        """
        lines = ["flowchart TD"]
        lines.append("")
        lines.append("    %% Styling definitions")
        lines.append("    classDef highCC fill:#ff6b6b,stroke:#c92a2a,color:#fff")
        lines.append("    classDef medCC fill:#ffd43b,stroke:#f08c00,color:#000")
        lines.append("    classDef entry fill:#4dabf7,stroke:#1971c2,color:#fff")
        lines.append("")
        filtered_funcs = _filtered_functions(
            result,
            self._module_of,
            self._should_skip_module,
            include_examples,
        )
        entry_points = _entry_points(filtered_funcs, result, self._is_entry_point)
        modules = _group_functions_by_module(filtered_funcs, self._module_of)
        _render_module_subgraphs(
            lines,
            modules,
            entry_points,
            short_len=35,
            readable_id=self._readable_id,
            safe_module=self._safe_module,
            get_cc=self._get_cc,
            sort_funcs=False,
            max_funcs=None,
        )
        _render_flow_edges(lines, filtered_funcs, self._readable_id, self._resolve, calls_per_function=15, limit=None)
        _render_flow_styles(
            lines,
            filtered_funcs,
            entry_points,
            self._readable_id,
            self._get_cc,
            high_limit=50,
            med_limit=50,
            entry_limit=15,
        )
        self._write(output_path, lines)

    def _readable_id(self, name: str) -> str:
        """Create human-readable Mermaid-safe unique node ID.
        
        Pattern: module__ClassName__method (ensures uniqueness across modules)
        Examples:
          code2llm.core.analyze → code2llm__core__analyze
          code2llm.core.PipelineDetector.__init__ → code2llm__core__PipelineDetector____init__
        """
        return self._sanitize_identifier(name, prefix="N")

    def _safe_module(self, name: str) -> str:
        """Create safe subgraph name."""
        return self._sanitize_identifier(name, prefix="M")

    @staticmethod
    def _sanitize_identifier(name: str, prefix: str) -> str:
        """Convert an arbitrary string into a Mermaid-safe identifier."""
        safe = (name or "").replace('.', '__')
        safe = re.sub(r'[^A-Za-z0-9_]+', '_', safe)
        if not safe:
            return prefix
        if not safe[0].isalpha():
            safe = f"{prefix}_{safe}"
        return safe

    def _module_of(self, func_name: str) -> str:
        """Extract module from qualified name.

        Returns up to 2 levels (e.g. 'code2llm.core', 'code2llm.exporters')
        so that subpackage-level cross-edges are visible in compact_flow.
        """
        parts = func_name.split('.')
        if len(parts) >= 3:
            return '.'.join(parts[:2])
        if len(parts) == 2:
            return parts[0]
        return parts[0] if parts else 'unknown'

    def _resolve(self, callee: str, funcs: dict) -> str:
        """Resolve callee to a known qualified name."""
        if callee in funcs:
            return callee
        candidates = [qn for qn in funcs if qn.endswith(f".{callee}")]
        if len(candidates) == 1:
            return candidates[0]
        return None

    def _write(self, path: str, lines: list) -> Path:
        """Write lines to file."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
        return p
