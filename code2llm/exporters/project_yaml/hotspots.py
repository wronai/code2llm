"""Hotspots and refactoring priorities builder for project.yaml."""

from pathlib import Path
from typing import Any, Dict, List

from code2llm.core.models import AnalysisResult, FunctionInfo
from code2llm.exporters.toon.helpers import _is_excluded
from .constants import FAN_OUT_THRESHOLD, CC_WARNING, GOD_MODULE_LINES


def build_hotspots(result: AnalysisResult) -> List[Dict[str, Any]]:
    """Build hotspots list (high fan-out functions)."""
    spots = []
    for qname, fi in result.functions.items():
        if _is_excluded(fi.file):
            continue
        fan_out = len(set(fi.calls))
        if fan_out >= FAN_OUT_THRESHOLD:
            display = fi.name
            if fi.class_name:
                display = f"{fi.class_name}.{fi.name}"
            note = hotspot_note(fi, fan_out)
            spots.append({
                "name": display,
                "fan_out": fan_out,
                "note": note,
            })
    spots.sort(key=lambda s: s["fan_out"], reverse=True)
    return spots[:10]


def hotspot_note(fi: FunctionInfo, fan_out: int) -> str:
    """Generate descriptive note for a hotspot."""
    if "format" in fi.name.lower() or "dispatch" in fi.name.lower():
        return f"{fan_out}-way dispatch"
    if "export" in fi.name.lower():
        return f"Export with {fan_out} outputs"
    if "analyze" in fi.name.lower() or "process" in fi.name.lower():
        return f"Analysis pipeline, {fan_out} stages"
    if fi.docstring:
        return fi.docstring[:80]
    return f"Orchestrates {fan_out} calls"


def build_refactoring(
    result: AnalysisResult,
    modules: List[Dict],
    hotspots: List[Dict],
) -> Dict[str, Any]:
    """Build prioritized refactoring actions."""
    priorities = []

    # High CC functions → split
    for qname, fi in result.functions.items():
        if _is_excluded(fi.file):
            continue
        cc = fi.complexity.get("cyclomatic_complexity", 0)
        if cc >= CC_WARNING:
            display = fi.name
            if fi.class_name:
                display = f"{fi.class_name}.{fi.name}"
            rel = _rel_path(fi.file, result.project_path)
            priorities.append({
                "action": f"Split {display} (CC={cc})",
                "impact": "high" if cc >= 25 else "medium",
                "effort": "low",
                "module": Path(rel).name,
            })

    # Cycles → break
    proj_metrics = result.metrics.get("project", {})
    cycles = proj_metrics.get("circular_dependencies", [])
    for cycle in cycles[:3]:
        priorities.append({
            "action": f"Break circular dependency: {' → '.join(str(c) for c in cycle) if isinstance(cycle, list) else str(cycle)}",
            "impact": "medium",
            "effort": "low",
        })

    # High fan-out → reduce
    for spot in hotspots[:3]:
        if spot["fan_out"] >= 15:
            priorities.append({
                "action": f"Reduce {spot['name']} fan-out (currently {spot['fan_out']})",
                "impact": "medium",
                "effort": "medium",
            })

    # God modules → split
    for mod in modules:
        if mod["lines"] >= GOD_MODULE_LINES:
            priorities.append({
                "action": f"Split god module {mod['path']} ({mod['lines']}L, {mod['classes']} classes)",
                "impact": "high",
                "effort": "high",
            })

    # Sort: high impact first, then low effort first
    impact_order = {"high": 0, "medium": 1, "low": 2}
    effort_order = {"low": 0, "medium": 1, "high": 2}
    priorities.sort(key=lambda p: (
        impact_order.get(p.get("impact", "low"), 9),
        effort_order.get(p.get("effort", "medium"), 9),
    ))

    return {"priorities": priorities[:15]}
