"""Map exporter header — render header lines with project stats and alerts."""

from datetime import datetime
from typing import Any, Dict, List

from code2llm.core.models import AnalysisResult, FunctionInfo, ModuleInfo

from .utils import count_total_lines, detect_languages
from .alerts import build_alerts, build_hotspots, load_evolution_trend


def render_header(result: AnalysisResult, output_path: str, is_excluded_path) -> List[str]:
    """Render header lines with project stats and alerts."""
    from pathlib import Path as P
    project_name = P(result.project_path).name if result.project_path else "project"
    langs = detect_languages(result, is_excluded_path)
    lang_str = ",".join(f"{lang}:{count}" for lang, count in langs.items()) or "unknown"

    included_funcs = [fi for fi in result.functions.values() if not is_excluded_path(fi.file)]
    included_files = [mi for mi in result.modules.values() if not is_excluded_path(mi.file)]
    total_lines = count_total_lines(result, is_excluded_path)

    stats_line = _render_stats_line(included_funcs, included_files, total_lines, lang_str)
    alerts_line = _render_alerts_line(included_funcs)
    hotspots_line = _render_hotspots_line(included_funcs)
    trend = load_evolution_trend(P(output_path).with_name("evolution.toon.yaml"),
                                  stats_line.get('avg_cc', 0.0))

    lines = [
        f"# {project_name} | {stats_line['files']}f {stats_line['lines']}L | {lang_str} | {datetime.now().strftime('%Y-%m-%d')}",
        f"# stats: {stats_line['funcs']} func | {stats_line['classes']} cls | {stats_line['files']} mod | CC̄={stats_line['avg_cc']} | critical:{stats_line['critical']} | cycles:{stats_line['cycles']}",
        alerts_line,
        hotspots_line,
        f"# evolution: {trend}",
        "# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods",
    ]
    return lines


def _render_stats_line(funcs: List[FunctionInfo], files: List[ModuleInfo],
                      total_lines: int, lang_str: str) -> Dict[str, Any]:
    """Build stats dict for header line."""
    cc_scores = [fi.complexity.get("cyclomatic_complexity", 0) for fi in funcs]
    avg_cc = round(sum(cc_scores) / len(cc_scores), 1) if cc_scores else 0.0
    critical_count = len([cc for cc in cc_scores if cc >= 15])

    return {
        'funcs': len(funcs),
        'files': len(files),
        'lines': total_lines,
        'avg_cc': avg_cc,
        'critical': critical_count,
        'cycles': 0,  # Cycles calculated elsewhere
        'classes': 0,  # Will be updated by caller if needed
    }


def _render_alerts_line(funcs: List[FunctionInfo]) -> str:
    """Build alerts line for header."""
    alerts = build_alerts(funcs)
    return f"# alerts[{len(alerts)}]: {'; '.join(alerts) if alerts else 'none'}"


def _render_hotspots_line(funcs: List[FunctionInfo]) -> str:
    """Build hotspots line for header."""
    hotspots = build_hotspots(funcs)
    return f"# hotspots[{len(hotspots)}]: {'; '.join(hotspots) if hotspots else 'none'}"


__all__ = ['render_header']
