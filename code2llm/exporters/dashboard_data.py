"""Dashboard Data Builder — prepares data for dashboard visualization.

Extracts and transforms project metrics into chart-ready data structures.
"""

from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

# Language detection from file extensions
_LANG_EXT_MAP = {
    '.py': 'Python', '.ts': 'TypeScript', '.tsx': 'TypeScript',
    '.js': 'JavaScript', '.jsx': 'JavaScript', '.mjs': 'JavaScript', '.cjs': 'JavaScript',
    '.go': 'Go', '.rs': 'Rust', '.java': 'Java',
    '.cpp': 'C++', '.cc': 'C++', '.cxx': 'C++', '.hpp': 'C++', '.h': 'C/C++',
    '.c': 'C', '.cs': 'C#', '.rb': 'Ruby', '.php': 'PHP',
    '.swift': 'Swift', '.kt': 'Kotlin', '.kts': 'Kotlin',
    '.scala': 'Scala', '.sh': 'Shell', '.bash': 'Shell', '.zsh': 'Shell',
    '.dart': 'Dart', '.ex': 'Elixir', '.exs': 'Elixir',
    '.hs': 'Haskell', '.lua': 'Lua', '.pl': 'Perl', '.r': 'R', '.R': 'R',
}

_LANG_COLORS = {
    'TypeScript': '#3178c6', 'JavaScript': '#f7df1e', 'Python': '#3572A5',
    'Go': '#00ADD8', 'Rust': '#dea584', 'Java': '#b07219',
    'C++': '#f34b7d', 'C': '#555555', 'C/C++': '#555555', 'C#': '#178600',
    'Ruby': '#701516', 'PHP': '#4F5D95', 'Swift': '#F05138',
    'Kotlin': '#A97BFF', 'Scala': '#c22d40', 'Shell': '#89e051',
    'Dart': '#00B4AB', 'Elixir': '#6e4a7e', 'Haskell': '#5e5086',
    'Lua': '#000080', 'Perl': '#0298c3', 'R': '#198CE7',
}


class DashboardDataBuilder:
    """Build dashboard data structures from project analysis results."""

    @staticmethod
    def health_verdict(health: Dict) -> tuple:
        """Determine health status color and label from CC average."""
        cc_avg = health.get("cc_avg", 0)
        if cc_avg <= 5:
            return "#22c55e", "Good"
        elif cc_avg <= 8:
            return "#eab308", "Warning"
        return "#ef4444", "Critical"

    @staticmethod
    def build_evolution_section(evolution: List[Dict]) -> Dict[str, Any]:
        """Build evolution chart data, or metric cards if <3 data points."""
        evo_dates = [e.get("date", "") for e in evolution]
        evo_cc = [e.get("cc_avg", 0) for e in evolution]
        evo_crit = [e.get("critical", 0) for e in evolution]
        use_chart = len(evolution) >= 3
        return {
            "dates": evo_dates, "cc": evo_cc, "crit": evo_crit,
            "use_chart": use_chart, "entries": evolution,
        }

    @staticmethod
    def build_language_breakdown(modules: List[Dict]) -> Dict[str, Any]:
        """Detect languages from module paths and build pie chart data."""
        lang_files: Dict[str, int] = defaultdict(int)
        lang_lines: Dict[str, int] = defaultdict(int)
        for m in modules:
            ext = Path(m.get("path", "")).suffix.lower()
            lang = _LANG_EXT_MAP.get(ext, ext.lstrip('.').capitalize() if ext else "Other")
            lang_files[lang] += 1
            lang_lines[lang] += m.get("lines", 0)

        sorted_langs = sorted(lang_files.items(), key=lambda x: -x[1])
        names = [l[0] for l in sorted_langs]
        files = [l[1] for l in sorted_langs]
        lines = [lang_lines[l[0]] for l in sorted_langs]
        colors = [_LANG_COLORS.get(n, '#6b7280') for n in names]
        return {"names": names, "files": files, "lines": lines, "colors": colors}

    @staticmethod
    def build_module_lines_chart(modules: List[Dict]) -> Dict[str, Any]:
        """Top 15 modules by line count."""
        top = sorted(modules, key=lambda m: m.get("lines", 0), reverse=True)[:15]
        return {
            "names": [Path(m.get("path", "")).name for m in top],
            "lines": [m.get("lines", 0) for m in top],
        }

    @staticmethod
    def build_module_funcs_chart(modules: List[Dict]) -> Dict[str, Any]:
        """Top 15 modules by function/method count."""
        top = sorted(modules, key=lambda m: m.get("methods", 0), reverse=True)[:15]
        return {
            "names": [Path(m.get("path", "")).name for m in top],
            "funcs": [m.get("methods", 0) for m in top],
        }

    @staticmethod
    def build_top_modules_html(modules: List[Dict]) -> str:
        """Build top modules table sorted by lines."""
        top = sorted(modules, key=lambda m: m.get("lines", 0), reverse=True)[:20]
        html = ""
        for m in top:
            path = m.get("path", "?")
            lines = m.get("lines", 0)
            methods = m.get("methods", 0)
            classes = m.get("classes", 0)
            cc_max = m.get("cc_max", 0)
            ext = Path(path).suffix.lower()
            lang = _LANG_EXT_MAP.get(ext, ext.lstrip('.'))
            color = _LANG_COLORS.get(lang, '#6b7280')
            html += f"""
            <tr>
                <td><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{color};margin-right:6px"></span>{Path(path).name}</td>
                <td style="color:var(--muted);font-size:.75rem">{'/'.join(Path(path).parts[:-1]) or '.'}</td>
                <td style="text-align:right">{lines:,}</td>
                <td style="text-align:right">{methods}</td>
                <td style="text-align:right">{classes}</td>
                <td style="text-align:right">{cc_max}</td>
            </tr>"""
        return html

    @staticmethod
    def build_alerts_html(health: Dict) -> str:
        """Build HTML table rows for health alerts."""
        html = ""
        for a in health.get("alerts", [])[:15]:
            sev = a.get("severity", "warning")
            sev_class = sev if sev in ("critical", "error", "warning") else "warning"
            html += f"""
            <tr class="{sev_class}">
                <td><span class="badge {sev_class}">{sev}</span></td>
                <td>{a.get('target', '?')}</td>
                <td>{a.get('type', '?')}</td>
                <td>{a.get('value', '?')}</td>
                <td>{a.get('limit', '?')}</td>
            </tr>"""
        return html

    @staticmethod
    def build_hotspots_html(hotspots: List[Dict]) -> str:
        """Build HTML table rows for hotspots."""
        html = ""
        for h in hotspots[:10]:
            html += f"""
            <tr>
                <td><strong>{h.get('name', '?')}</strong></td>
                <td>{h.get('fan_out', 0)}</td>
                <td>{h.get('note', '')}</td>
            </tr>"""
        return html

    @staticmethod
    def build_refactoring_html(refactoring: Dict) -> str:
        """Build HTML table rows for refactoring priorities."""
        html = ""
        for i, p in enumerate(refactoring.get("priorities", [])[:15], 1):
            impact_class = p.get("impact", "low")
            html += f"""
            <tr>
                <td>{i}</td>
                <td>{p.get('action', '?')}</td>
                <td><span class="badge {impact_class}">{p.get('impact', '?')}</span></td>
                <td>{p.get('effort', '?')}</td>
            </tr>"""
        return html
