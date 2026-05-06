"""Metrics computation for TOON export.

Refactored v0.5.x: Split into metrics_core, metrics_health, metrics_duplicates.
"""

from datetime import datetime
from typing import Any, Dict, List

from code2llm.core.models import AnalysisResult

from .helpers import _is_excluded, _scan_line_counts, _hotspot_description
from .metrics_core import CoreMetricsComputer
from .metrics_health import HealthMetricsComputer
from .metrics_duplicates import DuplicatesMetricsComputer


class MetricsComputer:
    """Computes all metrics for TOON export.

    Orchestrates specialized metric computers:
    - CoreMetricsComputer: file, package, function, class metrics, coupling
    - HealthMetricsComputer: health issues and quality alerts
    - DuplicatesMetricsComputer: duplicate class detection
    """

    def __init__(self):
        self.result = None
        self.project_path = None
        self.line_counts = {}
        self._core = None
        self._health = None
        self._duplicates = None

    def compute_all_metrics(self, result: AnalysisResult) -> Dict[str, Any]:
        """Compute all metrics and return context dict."""
        self.result = result
        self.project_path = result.project_path
        self.line_counts = _scan_line_counts(self.project_path, result=result)

        # Initialize specialized computers
        self._core = CoreMetricsComputer(self.line_counts, self.project_path)
        self._health = HealthMetricsComputer()
        self._duplicates = DuplicatesMetricsComputer(self.project_path)

        ctx: Dict[str, Any] = {}
        ctx["result"] = result
        ctx["timestamp"] = datetime.now().strftime("%Y-%m-%d")

        # Core metrics
        ctx["files"] = self._core.compute_file_metrics(result)
        ctx["packages"] = self._core.compute_package_metrics(ctx["files"], result)
        ctx["func_metrics"] = self._core.compute_function_metrics(result)
        ctx["class_metrics"] = self._core.compute_class_metrics(result)
        ctx["coupling_matrix"], ctx["pkg_fan"] = self._core.compute_coupling_matrix(result)

        # Health and duplicates
        ctx["duplicates"] = self._duplicates.detect_duplicates(result)
        ctx["health"] = self._health.compute_health(ctx)

        # Hotspots and cycles
        ctx["hotspots"] = self._compute_hotspots(result)
        ctx["cycles"] = self._get_cycles(result)

        return ctx

    def _compute_hotspots(self, result: AnalysisResult) -> List[Dict[str, Any]]:
        """Top functions by fan-out."""
        spots = []
        for qname, fi in result.functions.items():
            if _is_excluded(fi.file):
                continue
            fan_out = len(set(fi.calls))
            if fan_out >= 5:
                display = fi.name
                if fi.class_name:
                    display = f"{fi.class_name}.{fi.name}"
                spots.append({
                    "name": display,
                    "qualified": qname,
                    "fan_out": fan_out,
                    "description": _hotspot_description(fi, fan_out),
                })
        spots.sort(key=lambda x: x["fan_out"], reverse=True)
        return spots[:10]

    def _get_cycles(self, result: AnalysisResult) -> List[List[str]]:
        """Get circular dependencies from project metrics."""
        proj = result.metrics.get("project", {})
        return proj.get("circular_dependencies", [])


# Backward compatibility re-exports
__all__ = [
    'MetricsComputer',
    'CoreMetricsComputer',
    'HealthMetricsComputer',
    'DuplicatesMetricsComputer',
]
