"""Health metrics builder for project.yaml."""

from collections import defaultdict
from typing import Any, Dict, List

from code2llm.core.models import AnalysisResult, ClassInfo, FunctionInfo
from code2llm.exporters.toon.helpers import _is_excluded
from .constants import CC_CRITICAL, CC_WARNING, CC_ERROR, CC_SEVERE, FAN_OUT_THRESHOLD, FAN_OUT_ERROR, FAN_OUT_SEVERE


def build_health(result: AnalysisResult, modules: List[Dict]) -> Dict[str, Any]:
    """Build health section with CC metrics, alerts, and issues."""
    all_cc = []
    for fi in result.functions.values():
        if _is_excluded(fi.file):
            continue
        all_cc.append(fi.complexity.get("cyclomatic_complexity", 0))

    cc_avg = round(sum(all_cc) / len(all_cc), 1) if all_cc else 0.0
    critical_count = sum(1 for c in all_cc if c >= CC_CRITICAL)

    # Detect cycles
    proj_metrics = result.metrics.get("project", {})
    cycles = proj_metrics.get("circular_dependencies", [])

    # Detect duplicates
    dup_count = count_duplicates(result)

    # Build alerts
    alerts = build_alerts(result)

    return {
        "cc_avg": cc_avg,
        "critical_count": critical_count,
        "critical_limit": CC_CRITICAL,
        "duplicates": dup_count,
        "cycles": len(cycles),
        "alerts": alerts if alerts else [],
    }


def build_alerts(result: AnalysisResult) -> List[Dict[str, Any]]:
    """Build list of health alerts for high CC and high fan-out."""
    alerts = []
    for qname, fi in result.functions.items():
        if _is_excluded(fi.file):
            continue
        cc = fi.complexity.get("cyclomatic_complexity", 0)
        if cc >= CC_WARNING:
            display = fi.name
            if fi.class_name:
                display = f"{fi.class_name}.{fi.name}"
            if cc >= CC_SEVERE:
                severity = "critical"
            elif cc >= CC_ERROR:
                severity = "error"
            else:
                severity = "warning"
            alerts.append({
                "type": "cc_exceeded",
                "target": display,
                "value": cc,
                "limit": CC_WARNING,
                "severity": severity,
            })

    fan_alerts = []
    for qname, fi in result.functions.items():
        if _is_excluded(fi.file):
            continue
        fan_out = len(set(fi.calls))
        if fan_out >= FAN_OUT_THRESHOLD:
            display = fi.name
            if fi.class_name:
                display = f"{fi.class_name}.{fi.name}"
            if fan_out >= FAN_OUT_SEVERE:
                severity = "critical"
            elif fan_out >= FAN_OUT_ERROR:
                severity = "error"
            else:
                severity = "warning"
            fan_alerts.append({
                "type": "high_fan_out",
                "target": display,
                "value": fan_out,
                "limit": FAN_OUT_THRESHOLD,
                "severity": severity,
            })

    # Sort alerts by severity (critical first), then by value desc
    sev_order = {"critical": 0, "error": 1, "warning": 2, "info": 3}
    all_alerts = alerts + fan_alerts
    all_alerts.sort(key=lambda a: (sev_order.get(a["severity"], 9), -a["value"]))
    return all_alerts[:20]


def count_duplicates(result: AnalysisResult) -> int:
    """Count duplicate class names in different files."""
    name_files: Dict[str, List[str]] = defaultdict(list)
    for qname, ci in result.classes.items():
        if not _is_excluded(ci.file):
            name_files[ci.name].append(ci.file)
    return sum(1 for files in name_files.values() if len(set(files)) > 1)
