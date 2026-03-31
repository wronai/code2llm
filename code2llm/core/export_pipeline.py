"""Export pipeline — shared context computed once for all exporters.

Instead of each exporter building its own context from scratch, the pipeline
pre-computes shared data (metrics aggregations, call graph, etc.) and passes
it to all exporters in sequence.
"""

from typing import Any, Dict, List, Optional

from code2llm.core.models import AnalysisResult


class SharedExportContext:
    """Pre-computed context shared across all exporters.

    Lazy-computes expensive aggregations on first access.
    """

    __slots__ = ("_result", "_computed")

    def __init__(self, result: AnalysisResult):
        self._result = result
        self._computed: Dict[str, Any] = {}

    @property
    def result(self) -> AnalysisResult:
        return self._result

    @property
    def functions(self) -> Dict:
        return self._result.functions

    @property
    def classes(self) -> Dict:
        return self._result.classes

    @property
    def modules(self) -> Dict:
        return self._result.modules

    @property
    def entry_points(self) -> List[str]:
        return self._result.entry_points

    @property
    def metrics_summary(self) -> Dict[str, Any]:
        """Aggregate metrics — computed once, cached."""
        if "metrics_summary" not in self._computed:
            self._computed["metrics_summary"] = self._compute_metrics_summary()
        return self._computed["metrics_summary"]

    @property
    def complexity_distribution(self) -> Dict[str, int]:
        """CC rank distribution — computed once, cached."""
        if "cc_dist" not in self._computed:
            self._computed["cc_dist"] = self._compute_cc_distribution()
        return self._computed["cc_dist"]

    @property
    def call_graph_edges(self) -> List[tuple]:
        """Flattened call graph as (caller, callee) tuples."""
        if "cg_edges" not in self._computed:
            edges = []
            for fname, finfo in self._result.functions.items():
                for callee in finfo.calls:
                    edges.append((fname, callee))
            self._computed["cg_edges"] = edges
        return self._computed["cg_edges"]

    @property
    def high_complexity_functions(self) -> List[str]:
        """Functions with CC >= 10 (ranks C/D)."""
        if "high_cc" not in self._computed:
            high = []
            for fname, finfo in self._result.functions.items():
                cc = getattr(finfo, "complexity", None)
                if cc and cc.get("cyclomatic_complexity", 0) >= 10:
                    high.append(fname)
            self._computed["high_cc"] = high
        return self._computed["high_cc"]

    # ------------------------------------------------------------------
    # Internal computation
    # ------------------------------------------------------------------

    def _compute_metrics_summary(self) -> Dict[str, Any]:
        funcs = self._result.functions
        classes = self._result.classes

        total_cc = 0
        cc_count = 0
        for f in funcs.values():
            cc_data = getattr(f, "complexity", None)
            if cc_data:
                total_cc += cc_data.get("cyclomatic_complexity", 1)
                cc_count += 1

        return {
            "total_functions": len(funcs),
            "total_classes": len(classes),
            "total_modules": len(self._result.modules),
            "average_cc": round(total_cc / cc_count, 2) if cc_count else 0,
            "entry_points": len(self._result.entry_points),
        }

    def _compute_cc_distribution(self) -> Dict[str, int]:
        dist = {"A": 0, "B": 0, "C": 0, "D": 0, "unknown": 0}
        for f in self._result.functions.values():
            cc_data = getattr(f, "complexity", None)
            if cc_data:
                rank = cc_data.get("cc_rank", "unknown")
                dist[rank] = dist.get(rank, 0) + 1
            else:
                dist["unknown"] += 1
        return dist


class ExportPipeline:
    """Run multiple exporters with a single shared context.

    Usage::

        pipeline = ExportPipeline(analysis_result)
        pipeline.run([
            ToonExporter(config),
            MermaidExporter(config),
            ContextExporter(config),
        ], output_dir="/path/to/output")
    """

    def __init__(self, result: AnalysisResult):
        self._ctx = SharedExportContext(result)

    @property
    def context(self) -> SharedExportContext:
        return self._ctx

    def run(self, exporters: List, output_dir: str) -> Dict[str, bool]:
        """Run all exporters in sequence, returning success status per exporter."""
        results = {}
        for exporter in exporters:
            name = type(exporter).__name__
            try:
                # Exporters that support shared context
                if hasattr(exporter, "export_with_context"):
                    exporter.export_with_context(self._ctx, output_dir)
                else:
                    # Fallback: pass raw AnalysisResult
                    exporter.export(self._ctx.result, output_dir)
                results[name] = True
            except Exception as e:
                results[name] = False
        return results
