"""Evolution exporter YAML output — evolution.toon.yaml structured format."""

import yaml
from pathlib import Path

from code2llm.core.models import AnalysisResult

from .constants import CC_SPLIT_THRESHOLD
from .computation import build_context


def export_to_yaml(result: AnalysisResult, output_path: str) -> None:
    """Generate evolution.toon.yaml (structured YAML)."""
    ctx = build_context(result)

    # Build refactoring actions
    actions = []
    for gm in ctx["god_modules"][:3]:
        actions.append({
            "priority": "high",
            "action": "SPLIT",
            "target": gm["file"],
            "reason": f"{gm['lines']}L, {gm['classes']} classes, max CC={gm['max_cc']}",
            "effort": "~4h",
        })

    for f in ctx["funcs"][:20]:
        if f["cc"] >= CC_SPLIT_THRESHOLD:
            actions.append({
                "priority": "critical" if f["cc"] >= 25 else "high",
                "action": "SPLIT-FUNC",
                "target": f"{f['class_name']}.{f['name']}" if f["class_name"] else f["name"],
                "cc": f["cc"],
                "fan_out": f["fan_out"],
                "reason": f"CC={f['cc']} exceeds {CC_SPLIT_THRESHOLD}",
                "effort": "~1h",
            })

    for ht in ctx["hub_types"][:3]:
        if ht["consumers"] >= 20:
            actions.append({
                "priority": "medium",
                "action": "INTERFACE-SPLIT",
                "target": ht["type"],
                "consumers": ht["consumers"],
                "reason": f"Hub type with {ht['consumers']} consumers",
                "effort": "~6h",
            })

    actions.sort(key=lambda x: x.get("priority", "") == "critical", reverse=True)

    # Build risks
    risks = []
    for gm in ctx["god_modules"][:3]:
        risks.append({
            "type": "breaking_imports",
            "target": gm["file"],
            "impact": f"may break {gm['funcs']} import paths",
        })
    for ht in ctx["hub_types"][:2]:
        if ht["consumers"] >= 20:
            risks.append({
                "type": "api_change",
                "target": ht["type"],
                "impact": f"changes API for {ht['consumers']} consumers",
            })

    from datetime import datetime
    data = {
        "format": "evolution-toon-yaml",
        "timestamp": datetime.now().strftime("%Y-%m-%d"),
        "stats": {
            "total_funcs": ctx["total_funcs"],
            "total_files": ctx["total_files"],
            "avg_cc": ctx["avg_cc"],
            "max_cc": ctx["max_cc"],
            "high_cc_count": ctx["high_cc_count"],
            "critical_count": ctx["critical_count"],
        },
        "refactoring": {
            "action_count": len(actions),
            "actions": actions[:10],
        },
        "risks": {
            "count": len(risks),
            "items": risks,
        },
        "metrics_target": {
            "avg_cc": {"current": ctx["avg_cc"], "target": round(min(ctx["avg_cc"] * 0.7, 5.0), 1)},
            "max_cc": {"current": ctx["max_cc"], "target": min(ctx["max_cc"] // 2, 20)},
            "god_modules": {"current": len(ctx["god_modules"]), "target": 0},
            "high_cc": {"current": ctx["high_cc_count"], "target": max(ctx["high_cc_count"] // 2, 0)},
            "hub_types": {"current": len(ctx["hub_types"]), "target": max(len(ctx["hub_types"]) - 2, 0)},
        },
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


__all__ = ['export_to_yaml']
