"""TOON View Generator — compact ~50 lines for quick human scanning.

Generates project.toon.yaml from project.yaml data.
"""

from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

# Language detection from file extensions
_LANG_EXT_MAP = {
    '.py': 'python', '.ts': 'typescript', '.tsx': 'typescript',
    '.js': 'javascript', '.jsx': 'javascript', '.mjs': 'javascript', '.cjs': 'javascript',
    '.go': 'go', '.rs': 'rust', '.java': 'java',
    '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp', '.hpp': 'cpp', '.h': 'c',
    '.c': 'c', '.cs': 'csharp', '.rb': 'ruby', '.php': 'php',
    '.swift': 'swift', '.kt': 'kotlin', '.kts': 'kotlin',
    '.scala': 'scala', '.sh': 'shell', '.bash': 'shell', '.zsh': 'shell',
    '.dart': 'dart', '.ex': 'elixir', '.exs': 'elixir',
    '.hs': 'haskell', '.lua': 'lua', '.pl': 'perl', '.r': 'r', '.R': 'r',
}


class ToonViewGenerator:
    """Generate project.toon.yaml from project.yaml data."""

    def generate(self, data: Dict[str, Any], output_path: str) -> None:
        lines = self._render(data)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    def _render(self, data: Dict[str, Any]) -> List[str]:
        proj = data.get("project", {})
        health = data.get("health", {})
        modules = data.get("modules", [])
        hotspots = data.get("hotspots", [])
        refactoring = data.get("refactoring", {})
        evolution = data.get("evolution", [])

        lines: List[str] = []
        lines.extend(self._render_header(proj))
        lines.extend(self._render_health(health))
        lines.extend(self._render_alerts(health))
        lines.extend(self._render_modules(modules))
        lines.extend(self._render_hotspots(hotspots))
        lines.extend(self._render_refactoring(refactoring))
        lines.extend(self._render_evolution(evolution))
        return lines

    @staticmethod
    def _render_header(proj: Dict) -> List[str]:
        stats = proj.get("stats", {})
        lang = proj.get('language', 'unknown')
        return [
            f"# {proj.get('name', '?')} | "
            f"{stats.get('functions', 0)} func | "
            f"{stats.get('files', 0)}f | "
            f"{stats.get('lines', 0)}L | "
            f"{lang} | "
            f"{proj.get('analyzed_at', '?')[:10]}",
            "",
        ]

    @staticmethod
    def _render_health(health: Dict) -> List[str]:
        return [
            "HEALTH:",
            f"  CC̄={health.get('cc_avg', 0)}  "
            f"critical={health.get('critical_count', 0)} (limit:{health.get('critical_limit', 10)})  "
            f"dup={health.get('duplicates', 0)}  "
            f"cycles={health.get('cycles', 0)}",
        ]

    @staticmethod
    def _render_alerts(health: Dict) -> List[str]:
        alerts = health.get("alerts", [])
        if not alerts:
            return []
        lines = ["", f"ALERTS[{len(alerts)}]:"]
        for a in alerts[:10]:
            sev = "!!!" if a.get("severity") == "critical" else "!!" if a.get("severity") == "error" else "!"
            lines.append(
                f"  {sev:3s} {a.get('type', '?'):16s} "
                f"{a.get('target', '?')} = {a.get('value', '?')} "
                f"(limit:{a.get('limit', '?')})"
            )
        return lines

    @staticmethod
    def _render_modules(modules: List[Dict]) -> List[str]:
        # Show top modules by size (lines) - works for all languages
        top_by_lines = sorted(modules, key=lambda m: m.get("lines", 0), reverse=True)[:15]
        lines = ["", f"MODULES[{len(modules)}] (top by size):"]
        for m in top_by_lines:
            path = m.get('path', '?')
            ext = Path(path).suffix.lower()
            lang = _LANG_EXT_MAP.get(ext, ext.lstrip('.'))
            lines.append(
                f"  M[{path}] "
                f"{m.get('lines', 0)}L "
                f"C:{m.get('classes', 0)} "
                f"F:{m.get('methods', 0)} "
                f"CC↑{m.get('cc_max', 0)} "
                f"D:{m.get('inbound_deps', 0)} "
                f"({lang})"
            )

        # Language breakdown
        lang_counts: Dict[str, int] = defaultdict(int)
        for m in modules:
            ext = Path(m.get('path', '')).suffix.lower()
            lang = _LANG_EXT_MAP.get(ext, ext.lstrip('.') if ext else 'other')
            lang_counts[lang] += 1
        if lang_counts:
            sorted_langs = sorted(lang_counts.items(), key=lambda x: -x[1])
            lang_str = '/'.join(f"{l}:{c}" for l, c in sorted_langs)
            lines.append(f"  LANGS: {lang_str}")
        return lines

    @staticmethod
    def _render_hotspots(hotspots: List[Dict]) -> List[str]:
        if not hotspots:
            return []
        lines = ["", f"HOTSPOTS[{len(hotspots)}]:"]
        for h in hotspots[:5]:
            lines.append(
                f"  ★ {h.get('name', '?')} fan={h.get('fan_out', 0)}  "
                f"// {h.get('note', '')}"
            )
        return lines

    @staticmethod
    def _render_refactoring(refactoring: Dict) -> List[str]:
        priorities = refactoring.get("priorities", [])
        if not priorities:
            return []
        lines = ["", f"REFACTOR[{len(priorities)}]:"]
        for i, p in enumerate(priorities[:5], 1):
            impact = p.get("impact", "?")[0].upper()
            effort = p.get("effort", "?")[0].upper()
            lines.append(f"  [{i}] {impact}/{effort} {p.get('action', '?')}")
        return lines

    @staticmethod
    def _render_evolution(evolution: List[Dict]) -> List[str]:
        if not evolution:
            return []
        lines = ["", "EVOLUTION:"]
        for e in evolution[-3:]:
            lines.append(
                f"  {e.get('date', '?')} CC̄={e.get('cc_avg', '?')} "
                f"crit={e.get('critical', '?')} "
                f"{e.get('lines', '?')}L "
                f"// {e.get('note', '')}"
            )
        return lines
