"""HTML Dashboard Generator — web visualization with trend charts.

Generates dashboard.html from project.yaml data.
Includes: metric cards, language breakdown, evolution chart,
module size/function charts, alerts, hotspots, refactoring priorities.

Refactored v0.5.x: Split into dashboard_data (data preparation)
and dashboard_renderer (HTML generation).
"""

from pathlib import Path
from typing import Any, Dict

from .dashboard_data import DashboardDataBuilder
from .dashboard_renderer import DashboardRenderer


class HTMLDashboardGenerator:
    """Generate dashboard.html from project.yaml data.

    Orchestrates data preparation (DashboardDataBuilder) and
    HTML rendering (DashboardRenderer).
    """

    def __init__(self):
        self._data_builder = DashboardDataBuilder()
        self._renderer = DashboardRenderer()

    def generate(self, data: Dict[str, Any], output_path: str) -> None:
        html = self._render(data)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

    def _render(self, data: Dict[str, Any]) -> str:
        proj = data.get("project", {})
        health = data.get("health", {})
        modules = data.get("modules", [])
        hotspots = data.get("hotspots", [])
        refactoring = data.get("refactoring", {})
        evolution = data.get("evolution", [])
        stats = proj.get("stats", {})

        health_color, health_label = self._data_builder.health_verdict(health)
        evo_chart = self._data_builder.build_evolution_section(evolution)
        lang_data = self._data_builder.build_language_breakdown(modules)
        mod_lines_chart = self._data_builder.build_module_lines_chart(modules)
        mod_funcs_chart = self._data_builder.build_module_funcs_chart(modules)
        alerts_html = self._data_builder.build_alerts_html(health)
        hotspots_html = self._data_builder.build_hotspots_html(hotspots)
        refactor_html = self._data_builder.build_refactoring_html(refactoring)
        top_modules_html = self._data_builder.build_top_modules_html(modules)

        cc_avg = health.get("cc_avg", 0)

        return self._renderer.render(
            proj=proj, stats=stats, health=health,
            cc_avg=cc_avg, health_color=health_color, health_label=health_label,
            evo_chart=evo_chart, lang_data=lang_data,
            mod_lines_chart=mod_lines_chart, mod_funcs_chart=mod_funcs_chart,
            alerts_html=alerts_html, hotspots_html=hotspots_html,
            refactor_html=refactor_html, top_modules_html=top_modules_html,
            modules=modules, hotspots=hotspots, refactoring=refactoring,
        )


# Backward compatibility re-exports
__all__ = ['HTMLDashboardGenerator', 'DashboardDataBuilder', 'DashboardRenderer']
