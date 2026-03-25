"""TOON exporter - split into modular components."""

from pathlib import Path
from typing import Any, Dict, List

from ...core.models import AnalysisResult

from .metrics import MetricsComputer
from .renderer import ToonRenderer
from .helpers import _is_excluded, _rel_path, _package_of, _package_of_module, _traits_from_cfg, _dup_file_set, _hotspot_description, _scan_line_counts

# Re-export constants for backward compatibility
EXCLUDE_PATTERNS = {
    'venv', '.venv', 'env', '.env', 'publish-env', 'test-env',
    'site-packages', 'node_modules', '__pycache__', '.git',
    'dist', 'build', 'egg-info', '.tox', '.mypy_cache',
    'TODO', 'examples',
}

MAX_HEALTH_ISSUES = 20
MAX_COUPLING_PACKAGES = 15
MAX_FUNCTIONS_SHOWN = 50


class ToonExporter:
    """Export to toon v2 plain-text format — scannable, sorted by severity."""

    def __init__(self):
        self.metrics_computer = MetricsComputer()
        self.renderer = ToonRenderer()

    def export(self, result: AnalysisResult, output_path: str, **kwargs) -> None:
        """Export analysis result to toon v2 format."""
        ctx = self.metrics_computer.compute_all_metrics(result)

        sections: List[str] = []
        sections.extend(self.renderer.render_header(ctx))
        sections.append("")
        sections.extend(self.renderer.render_health(ctx))
        sections.append("")
        sections.extend(self.renderer.render_layers(ctx))
        sections.append("")
        sections.extend(self.renderer.render_coupling(ctx))

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(sections) + "\n")

    # Backward compatibility methods
    def _is_excluded(self, path: str) -> bool:
        """Check if path should be excluded (venv, site-packages, etc.)."""
        return _is_excluded(path)
