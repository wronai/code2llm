"""Pipeline Classifier — domain classification and naming for pipelines.

Groups pipelines by module domain (NLP, Analysis, Export, Refactor, etc.)
and derives human-readable pipeline names.
"""

from collections import defaultdict
from typing import Dict, List, Optional

from code2llm.core.models import FunctionInfo
from code2llm.analysis.type_inference import TypeInferenceEngine

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


class PipelineClassifier:
    """Classify pipelines by domain and derive human-readable names."""

    def __init__(self, type_engine: Optional[TypeInferenceEngine] = None):
        self._type_engine = type_engine or TypeInferenceEngine()

    def classify_domain(
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

    def derive_pipeline_name(
        self,
        path: List[str],
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
                    if part and part not in ("code2llm", "__init__"):
                        module_counts[part] += 1

        if module_counts:
            dominant = max(module_counts, key=module_counts.get)
            # Capitalize and use domain if module name is generic
            if dominant in ("core", "base", "utils", "helpers"):
                return domain
            return dominant.capitalize()

        return domain

    def get_entry_type(self, fi: Optional[FunctionInfo]) -> str:
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

    def get_exit_type(self, fi: Optional[FunctionInfo]) -> str:
        """Get the output type of a pipeline's exit point."""
        if not fi:
            return "?"
        ret = self._type_engine.get_return_type(fi)
        return ret if ret else "?"
