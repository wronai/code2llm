"""Renderer dla formatu flow.toon.

Zawiera funkcje renderujące poszczególne sekcje formatu flow.toon.
"""

from collections import defaultdict
from typing import Any, Dict, List

from .flow_constants import CC_HIGH, FAN_OUT_THRESHOLD, HUB_SPLIT_RECOMMENDATIONS, HUB_TYPE_THRESHOLD


class FlowRenderer:
    """Renderer dla sekcji formatu flow.toon."""

    @staticmethod
    def render_header(ctx: Dict[str, Any]) -> List[str]:
        """Renderuj nagłówek formatu."""
        from pathlib import Path
        from ..core.models import AnalysisResult

        result: AnalysisResult = ctx["result"]
        nfuncs = len(ctx["funcs"])
        npipelines = len(ctx["pipelines"])
        nhubs = sum(1 for t in ctx["type_usage"]
                    if t["consumed"] >= HUB_TYPE_THRESHOLD)
        return [
            f"# {Path(result.project_path).name if result.project_path else 'project'}/flow"
            f" | {nfuncs} func | {npipelines} pipelines"
            f" | {nhubs} hub-types | {ctx['timestamp']}",
        ]

    @staticmethod
    def render_pipelines(ctx: Dict[str, Any]) -> List[str]:
        """Renderuj sekcję PIPELINES."""
        pipelines = ctx["pipelines"]
        if not pipelines:
            return ["PIPELINES[0]: none detected"]

        # Count domains
        domains = defaultdict(int)
        for pl in pipelines:
            domains[pl.get("domain", "Unknown")] += 1
        domain_summary = ", ".join(f"{d}:{n}" for d, n in sorted(domains.items()))

        lines = [f"PIPELINES[{len(pipelines)}] ({domain_summary}):"]
        for pl in pipelines:
            domain_tag = f"[{pl.get('domain', '?')}]"
            entry_type = pl.get("entry_type", "?")
            exit_type = pl.get("exit_type", "?")
            lines.append(
                f"  {pl['name']} {domain_tag}:"
                f" {entry_type} → {exit_type}"
            )
            for stage in pl["stages"]:
                cc_marker = "  !!" if stage["cc"] >= CC_HIGH else ""
                entry_lbl = " ▶" if stage.get("is_entry") else ""
                exit_lbl = " ■" if stage.get("is_exit") else ""
                lines.append(
                    f"              → {stage['signature']}"
                    f"{'':>{max(1, 40 - len(stage['signature']))}}"
                    f"CC={stage['cc']:<4.0f} {stage['purity']}"
                    f"{cc_marker}{entry_lbl}{exit_lbl}"
                )
            bn = pl.get("bottleneck")
            bn_str = f"BOTTLENECK: {bn['name']}(CC={bn['cc']:.0f})" if bn else "OK"
            lines.append(
                f"              PURITY: {pl['pure_count']}/{pl['total_stages']} pure"
                f"  {bn_str}"
            )
            lines.append("")

        return lines

    @staticmethod
    def render_transforms(ctx: Dict[str, Any]) -> List[str]:
        """Renderuj sekcję TRANSFORMS."""
        transforms = ctx["transforms"]
        if not transforms:
            return ["TRANSFORMS: none (fan-out < 10)"]

        lines = [f"TRANSFORMS (fan-out ≥{FAN_OUT_THRESHOLD}):"]
        for t in transforms:
            lines.append(
                f"  {t['signature']:<55s} fan={t['fan_out']:<3}"
                f"  {t['label']}"
            )
        return lines

    @staticmethod
    def render_contracts(ctx: Dict[str, Any]) -> List[str]:
        """Renderuj sekcję CONTRACTS."""
        contracts = ctx["contracts"]
        if not contracts:
            return ["CONTRACTS: none (no pipelines detected)"]

        lines = ["CONTRACTS:"]
        for contract in contracts:
            lines.append(f"  Pipeline: {contract['pipeline']}")
            for stage in contract["stages"]:
                lines.append(f"    {stage['signature']}")
                lines.append(f"      IN:  {stage['in']}")
                lines.append(f"      OUT: {stage['out']}")
                if stage.get("side_effect"):
                    lines.append(f"      SIDE-EFFECT: {stage['side_effect']}")
                if stage.get("invariant"):
                    lines.append(f"      INVARIANT: {stage['invariant']}")
                if stage.get("smell"):
                    lines.append(f"      SMELL: {stage['smell']}")
                lines.append("")
        return lines

    @staticmethod
    def render_data_types(ctx: Dict[str, Any]) -> List[str]:
        """Renderuj sekcję DATA_TYPES."""
        types = ctx["type_usage"]
        if not types:
            return ["DATA_TYPES: no type information available"]

        # Count type sources
        type_info = ctx.get("type_info", {})
        n_annotated = sum(
            1 for ti in type_info.values()
            if ti.get("source") == "annotation"
        )
        n_inferred = sum(
            1 for ti in type_info.values()
            if ti.get("source") == "inferred"
        )
        n_total = len(type_info)

        lines = [
            f"DATA_TYPES (by cross-function usage)"
            f" [{n_annotated} annotated, {n_inferred} inferred"
            f" / {n_total} functions]:"
        ]
        for t in types:
            label = f"  {t['label']}" if t["label"] else ""
            lines.append(
                f"  {t['type']:<20s} consumed:{t['consumed']:<3}"
                f" produced:{t['produced']:<3}{label}"
            )

        # Hub types summary with split recommendations
        hubs = [t for t in types if t["consumed"] >= HUB_TYPE_THRESHOLD]
        if hubs:
            lines.append("")
            lines.append("  HUB TYPES (consumed ≥10):")
            for h in hubs:
                lines.append(
                    f"    {h['type']} → {h['consumed']} consumers"
                    f" → split into:"
                )
                recs = HUB_SPLIT_RECOMMENDATIONS.get(h["type"], [])
                if recs:
                    for rec in recs:
                        lines.append(f"      - {rec}")
                else:
                    lines.append("      - (analyze consumers to suggest sub-interfaces)")

        return lines

    @staticmethod
    def render_side_effects(ctx: Dict[str, Any]) -> List[str]:
        """Renderuj sekcję SIDE_EFFECTS."""
        se = ctx["side_effects"]
        lines = ["SIDE_EFFECTS:"]

        for category, funcs in se.items():
            if funcs:
                lines.append(
                    f"  {category + ':':<10s} {', '.join(funcs[:10])}"
                )

        # Pipeline purity summary
        pipelines = ctx["pipelines"]
        if pipelines:
            lines.append("")
            lines.append("  PIPELINE PURITY:")
            for pl in pipelines:
                ratio = pl["pure_count"] / pl["total_stages"] if pl["total_stages"] else 0
                bar_len = int(ratio * 4)
                bar = "█" * bar_len + "░" * (4 - bar_len)
                pct = int(ratio * 100)
                lines.append(
                    f"    {pl['name']:<15s} {bar} {pct}% pure"
                )

        return lines
