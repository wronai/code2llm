"""Article View Generator — publishable project health article.

Generates status.md from project.yaml data.
"""

from datetime import datetime
from typing import Any, Dict, List

from code2llm.exporters.base import ViewGeneratorMixin


class ArticleViewGenerator(ViewGeneratorMixin):
    """Generate status.md — publishable project health article."""

    def _render(self, data: Dict[str, Any]) -> List[str]:
        proj = data.get("project", {})
        health = data.get("health", {})
        hotspots = data.get("hotspots", [])
        refactoring = data.get("refactoring", {})
        evolution = data.get("evolution", [])

        lines: List[str] = []
        lines.extend(self._render_frontmatter(proj))
        lines.extend(self._render_health_summary(proj, health))
        lines.extend(self._render_alerts(health))
        lines.extend(self._render_hotspots(hotspots))
        lines.extend(self._render_roadmap(refactoring))
        lines.extend(self._render_evolution(evolution))
        lines.extend(self._render_footer())
        return lines

    @staticmethod
    def _render_frontmatter(proj: Dict) -> List[str]:
        stats = proj.get("stats", {})
        return [
            "---",
            f"title: \"Project Health Report: {proj.get('name', '?')}\"",
            f"date: {datetime.now().strftime('%Y-%m-%d')}",
            f"tool: code2llm",
            "---",
            "",
            f"# Project Health Report: {proj.get('name', '?')}",
            "",
            f"Automated analysis of **{proj.get('name', '?')}** "
            f"({stats.get('files', 0)} files, {stats.get('lines', 0)} lines) "
            f"generated on {proj.get('analyzed_at', '?')[:10]}.",
            "",
        ]

    @staticmethod
    def _render_health_summary(proj: Dict, health: Dict) -> List[str]:
        stats = proj.get("stats", {})
        cc_avg = health.get("cc_avg", 0)
        crit = health.get("critical_count", 0)

        if cc_avg <= 5 and crit <= 5:
            emoji, verdict = "🟢", "Good"
        elif cc_avg <= 8 and crit <= 15:
            emoji, verdict = "🟡", "Needs attention"
        else:
            emoji, verdict = "🔴", "Critical"

        return [
            "## Health Summary",
            "",
            f"**Overall: {emoji} {verdict}**",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Average CC | {cc_avg} |",
            f"| Critical functions (CC≥{health.get('critical_limit', 10)}) | {crit} |",
            f"| Duplicates | {health.get('duplicates', 0)} |",
            f"| Circular dependencies | {health.get('cycles', 0)} |",
            f"| Total functions | {stats.get('functions', 0)} |",
            f"| Total classes | {stats.get('classes', 0)} |",
            "",
        ]

    @staticmethod
    def _render_alerts(health: Dict) -> List[str]:
        alerts = health.get("alerts", [])
        if not alerts:
            return []
        lines = ["## Alerts", ""]
        for a in alerts[:10]:
            sev = a.get("severity", "warning")
            sev_icon = {"critical": "🔴", "error": "🟠", "warning": "🟡"}.get(sev, "🟡")
            lines.append(
                f"- {sev_icon} **{a.get('target', '?')}**: "
                f"{a.get('type', '?')} = {a.get('value', '?')} "
                f"(limit: {a.get('limit', '?')})"
            )
        lines.append("")
        return lines

    @staticmethod
    def _render_hotspots(hotspots: List[Dict]) -> List[str]:
        if not hotspots:
            return []
        lines = [
            "## Hotspots",
            "",
            "Functions with highest fan-out (orchestration complexity):",
            "",
        ]
        for h in hotspots[:5]:
            lines.append(f"- **{h['name']}** (fan-out: {h['fan_out']}) — {h.get('note', '')}")
        lines.append("")
        return lines

    @staticmethod
    def _render_roadmap(refactoring: Dict) -> List[str]:
        priorities = refactoring.get("priorities", [])
        if not priorities:
            return []
        lines = ["## Refactoring Roadmap", ""]
        for i, p in enumerate(priorities[:7], 1):
            impact_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(p.get("impact"), "⚪")
            lines.append(f"{i}. {impact_icon} **{p.get('action', '?')}** (effort: {p.get('effort', '?')})")
        lines.append("")
        return lines

    @staticmethod
    def _render_evolution(evolution: List[Dict]) -> List[str]:
        if len(evolution) <= 1:
            return []
        lines = [
            "## Evolution",
            "",
            "| Date | CC̄ | Critical | Lines | Note |",
            "|------|-----|----------|-------|------|",
        ]
        for e in evolution[-10:]:
            lines.append(
                f"| {e.get('date', '?')} | {e.get('cc_avg', '?')} | "
                f"{e.get('critical', '?')} | {e.get('lines', '?')} | "
                f"{e.get('note', '')} |"
            )
        lines.append("")

        first, last = evolution[0], evolution[-1]
        cc_delta = (last.get("cc_avg", 0) or 0) - (first.get("cc_avg", 0) or 0)
        if cc_delta < 0:
            lines.append(f"📈 **CC improved** by {abs(cc_delta):.1f} since {first.get('date', '?')}")
        elif cc_delta > 0:
            lines.append(f"📉 **CC worsened** by {cc_delta:.1f} since {first.get('date', '?')}")
        else:
            lines.append(f"➡️ **CC stable** since {first.get('date', '?')}")
        lines.append("")
        return lines

    @staticmethod
    def _render_footer() -> List[str]:
        return [
            "---",
            f"*Generated by code2llm on {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            "",
        ]
