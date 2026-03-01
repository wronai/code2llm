"""Flow Exporter — generates flow.toon (data-flow format).

Produces a data-flow-focused format with PIPELINES, TRANSFORMS, CONTRACTS,
DATA_TYPES, and SIDE_EFFECTS sections.

Purpose: "how data flows through the system"
Format: pipeline stages, transform fan-out, contracts, hub-type detection

Sprint 2 (v0.3.1): AST-based type inference and side-effect detection.
Sprint 3 (v0.3.2): networkx-based pipeline detection with domain grouping.
"""

import ast
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .base import Exporter
from ..core.models import (
    AnalysisResult, FunctionInfo, ClassInfo, ModuleInfo, FlowNode
)
from ..analysis.type_inference import TypeInferenceEngine
from ..analysis.side_effects import SideEffectDetector, SideEffectInfo
from ..analysis.pipeline_detector import PipelineDetector, Pipeline

# Thresholds
CC_HIGH = 15
FAN_OUT_THRESHOLD = 10
HUB_TYPE_THRESHOLD = 10

# Patterns to exclude
EXCLUDE_PATTERNS = {
    'venv', '.venv', 'env', '.env', 'publish-env', 'test-env',
    'site-packages', 'node_modules', '__pycache__', '.git',
    'dist', 'build', 'egg-info', '.tox', '.mypy_cache',
}


# Hub-type split recommendations: type -> suggested sub-interfaces
HUB_SPLIT_RECOMMENDATIONS: Dict[str, List[str]] = {
    "AnalysisResult": ["StructureResult (modules, classes, functions)",
                       "MetricsResult (complexity, coupling)",
                       "FlowResult (call_graph, cfg, dfg)"],
    "dict": ["replace with typed alternatives (dataclass/TypedDict)"],
    "str": [],  # primitive, expected to be ubiquitous
    "list": [],
    "Any": [],
}


class FlowExporter(Exporter):
    """Export to flow.toon — data-flow focused format.

    Sections: PIPELINES, TRANSFORMS, CONTRACTS, DATA_TYPES, SIDE_EFFECTS

    Sprint 2: TypeInferenceEngine + SideEffectDetector for AST-based analysis.
    Sprint 3: PipelineDetector with networkx for graph-based pipeline detection.
    """

    def __init__(self):
        self._type_engine = TypeInferenceEngine()
        self._side_effect_detector = SideEffectDetector()
        self._pipeline_detector = PipelineDetector(
            type_engine=self._type_engine,
            side_effect_detector=self._side_effect_detector,
        )

    def export(self, result: AnalysisResult, output_path: str, **kwargs) -> None:
        """Export analysis result to flow.toon format."""
        ctx = self._build_context(result)

        sections: List[str] = []
        sections.extend(self._render_header(ctx))
        sections.append("")
        sections.extend(self._render_pipelines(ctx))
        sections.append("")
        sections.extend(self._render_transforms(ctx))
        sections.append("")
        sections.extend(self._render_contracts(ctx))
        sections.append("")
        sections.extend(self._render_data_types(ctx))
        sections.append("")
        sections.extend(self._render_side_effects(ctx))

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(sections) + "\n")

    # ------------------------------------------------------------------
    # context builder
    # ------------------------------------------------------------------
    def _build_context(self, result: AnalysisResult) -> Dict[str, Any]:
        ctx: Dict[str, Any] = {}
        ctx["result"] = result
        ctx["timestamp"] = datetime.now().strftime("%Y-%m-%d")

        # Build function lookup excluding venv etc.
        funcs = {
            qname: fi for qname, fi in result.functions.items()
            if not self._is_excluded(fi.file)
        }
        ctx["funcs"] = funcs

        # AST-based type inference (Sprint 2)
        ctx["type_info"] = self._type_engine.extract_all_types(funcs)

        # AST-based side-effect detection (Sprint 2)
        ctx["se_info"] = self._side_effect_detector.analyze_all(funcs)

        # Detect pipelines using networkx-based PipelineDetector (Sprint 3)
        raw_pipelines = self._pipeline_detector.detect(funcs, se_info=ctx["se_info"])
        ctx["raw_pipelines"] = raw_pipelines
        ctx["pipelines"] = [self._pipeline_to_dict(p) for p in raw_pipelines]

        # Compute transforms (high fan-out functions)
        ctx["transforms"] = self._compute_transforms(funcs)

        # Compute type usage across functions (now AST-based)
        ctx["type_usage"] = self._compute_type_usage(funcs, ctx["type_info"])

        # Classify side effects (now AST-based)
        ctx["side_effects"] = self._classify_side_effects(funcs, ctx["se_info"])

        # Compute contracts per pipeline (now with IN/OUT/SIDE-EFFECT)
        ctx["contracts"] = self._compute_contracts(
            ctx["pipelines"], funcs, ctx["type_info"], ctx["se_info"]
        )

        return ctx

    # ------------------------------------------------------------------
    # pipeline conversion (Sprint 3)
    # ------------------------------------------------------------------
    def _pipeline_to_dict(self, pipeline: Pipeline) -> Dict[str, Any]:
        """Convert Pipeline dataclass to dict for rendering."""
        stages = []
        for s in pipeline.stages:
            stages.append({
                "name": s.name,
                "qualified": s.qualified_name,
                "signature": s.signature,
                "cc": s.cc,
                "purity": s.purity,
                "is_entry": s.is_entry,
                "is_exit": s.is_exit,
            })

        bn = pipeline.bottleneck
        return {
            "name": pipeline.name,
            "domain": pipeline.domain,
            "stages": stages,
            "entry_point": pipeline.entry_point,
            "exit_point": pipeline.exit_point,
            "entry_type": pipeline.entry_type,
            "exit_type": pipeline.exit_type,
            "pure_count": pipeline.pure_count,
            "total_stages": pipeline.total_stages,
            "bottleneck": {"name": bn.name, "cc": bn.cc} if bn else None,
        }

    # ------------------------------------------------------------------
    # transforms — high fan-out functions
    # ------------------------------------------------------------------
    def _compute_transforms(
        self, funcs: Dict[str, FunctionInfo]
    ) -> List[Dict[str, Any]]:
        """Find functions with fan-out >= threshold."""
        transforms = []
        for qname, fi in funcs.items():
            fan_out = len(set(fi.calls))
            if fan_out >= FAN_OUT_THRESHOLD:
                transforms.append({
                    "name": fi.name,
                    "qualified": qname,
                    "fan_out": fan_out,
                    "signature": self._type_engine.get_typed_signature(fi),
                    "label": self._transform_label(fi, fan_out),
                })
        transforms.sort(key=lambda x: x["fan_out"], reverse=True)
        return transforms[:15]

    def _transform_label(self, fi: FunctionInfo, fan_out: int) -> str:
        if fi.name == "main" or fi.name == "__main__":
            return "!! script-in-disguise"
        if fan_out >= 30:
            return "!! mutation-heavy"
        if fan_out >= 20:
            return "!! side-effects"
        if fi.class_name:
            return f"PIPELINE:{fi.class_name}.entry"
        return f"fan={fan_out}"

    # ------------------------------------------------------------------
    # type usage — consumed/produced counts (AST-based, Sprint 2)
    # ------------------------------------------------------------------
    def _compute_type_usage(
        self, funcs: Dict[str, FunctionInfo],
        type_info: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Count how many functions consume/produce each type using AST data."""
        consumed: Dict[str, int] = defaultdict(int)
        produced: Dict[str, int] = defaultdict(int)

        for qname, fi in funcs.items():
            ti = type_info.get(qname, {})
            # Types from AST-extracted args (consumed)
            for arg in ti.get("args", []):
                if arg["name"] == "self":
                    continue
                type_name = arg.get("type")
                if type_name:
                    normalized = self._normalize_type(type_name)
                    if normalized:
                        consumed[normalized] += 1

            # Types from AST-extracted return (produced)
            ret = ti.get("returns")
            if ret:
                normalized = self._normalize_type(ret)
                if normalized:
                    produced[normalized] += 1

        # Merge into ranked list
        all_types = set(consumed.keys()) | set(produced.keys())
        type_list = []
        for t in all_types:
            c = consumed.get(t, 0)
            p = produced.get(t, 0)
            total = c + p
            label = self._type_label(t, c, p)
            type_list.append({
                "type": t,
                "consumed": c,
                "produced": p,
                "total": total,
                "label": label,
            })

        type_list.sort(key=lambda x: x["total"], reverse=True)
        return type_list[:20]

    def _normalize_type(self, t: str) -> str:
        t = t.strip().strip("'\"")
        # Remove Optional[], List[], Dict[] wrappers for base type
        for wrapper in ["Optional[", "List[", "Dict[", "Set[", "Tuple["]:
            if t.startswith(wrapper) and t.endswith("]"):
                t = t[len(wrapper):-1]
        return t if t and t not in ("None", "Any") else ""

    def _type_label(self, t: str, consumed: int, produced: int) -> str:
        if consumed >= HUB_TYPE_THRESHOLD:
            return "!! HUB-TYPE \u2192 split interface"
        if consumed >= 5 and produced <= 1:
            return "input-heavy (read-only flow)"
        if produced >= 5 and consumed <= 1:
            return "output-heavy"
        if consumed >= 10 and produced >= 10:
            return "ubiquitous"
        if consumed + produced <= 4:
            return "narrow scope"
        return ""

    # ------------------------------------------------------------------
    # side effect classification (AST-based, Sprint 2)
    # ------------------------------------------------------------------
    def _classify_side_effects(
        self, funcs: Dict[str, FunctionInfo],
        se_info: Dict[str, SideEffectInfo]
    ) -> Dict[str, List[str]]:
        """Classify functions by side-effect type using AST analysis."""
        io_funcs: List[str] = []
        cache_funcs: List[str] = []
        mutation_funcs: List[str] = []
        pure_funcs: List[str] = []

        for qname, fi in funcs.items():
            se = se_info.get(qname)
            classification = se.classification if se else "pure"
            short = fi.name
            if fi.class_name:
                short = f"{fi.class_name}.{fi.name}"

            if classification == "IO":
                io_funcs.append(short)
            elif classification == "cache":
                cache_funcs.append(short)
            elif classification == "mutation":
                mutation_funcs.append(short)
            else:
                pure_funcs.append(short)

        return {
            "IO": io_funcs[:15],
            "Cache": cache_funcs[:10],
            "Mutation": mutation_funcs[:15],
            "Pure": pure_funcs[:20],
        }

    # ------------------------------------------------------------------
    # contracts per pipeline (enhanced, Sprint 2)
    # ------------------------------------------------------------------
    def _compute_contracts(
        self, pipelines: List[Dict[str, Any]],
        funcs: Dict[str, FunctionInfo],
        type_info: Dict[str, Dict[str, Any]],
        se_info: Dict[str, SideEffectInfo]
    ) -> List[Dict[str, Any]]:
        """Build rich contracts for each pipeline stage with IN/OUT/SIDE-EFFECT."""
        contracts = []
        for pipeline in pipelines:
            stages_contracts = []
            for stage in pipeline["stages"]:
                fi = funcs.get(stage["qualified"])
                if not fi:
                    continue
                ti = type_info.get(stage["qualified"], {})
                se = se_info.get(stage["qualified"])

                contract = self._build_stage_contract(fi, ti, se, stage)
                stages_contracts.append(contract)

            contracts.append({
                "pipeline": pipeline["name"],
                "stages": stages_contracts,
            })
        return contracts

    def _build_stage_contract(
        self, fi: FunctionInfo,
        ti: Dict[str, Any],
        se: Optional[SideEffectInfo],
        stage: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build a rich contract for a single pipeline stage."""
        # IN types
        in_types = []
        for arg in ti.get("args", []):
            if arg["name"] == "self":
                continue
            t = arg.get("type", "")
            in_types.append(f"{arg['name']}:{t}" if t else arg["name"])
        in_str = ", ".join(in_types) if in_types else "()"

        # OUT type
        out_str = ti.get("returns") or "None"

        # Side-effect info
        side_effect = ""
        if se and not se.is_pure:
            side_effect = se.side_effect_summary

        # Smell note
        cc = stage["cc"]
        smell = ""
        if cc >= CC_HIGH:
            smell = f"CC={cc:.0f} \u2192 split"

        # Invariant (heuristic)
        invariant = self._infer_invariant(fi, ti)

        return {
            "name": fi.name,
            "signature": stage["signature"],
            "in": in_str,
            "out": out_str,
            "cc": cc,
            "purity": stage["purity"],
            "side_effect": side_effect,
            "smell": smell,
            "invariant": invariant,
            "source": ti.get("source", "none"),
        }

    def _infer_invariant(self, fi: FunctionInfo, ti: Dict[str, Any]) -> str:
        """Infer a contract invariant from function semantics."""
        name_lower = fi.name.lower()
        ret = ti.get("returns", "")

        if "normalize" in name_lower:
            return "len(output) <= len(input)"
        if "match" in name_lower and ret and "Match" in ret:
            return "confidence \u2208 [0.0, 1.0]"
        if "resolve" in name_lower:
            return "all entities exist in analysis"
        if "validate" in name_lower or "check" in name_lower:
            return "raises on invalid input"
        if "sort" in name_lower:
            return "output is sorted"
        if "filter" in name_lower:
            return "len(output) <= len(input)"
        return ""

    # ------------------------------------------------------------------
    # render sections
    # ------------------------------------------------------------------
    def _render_header(self, ctx: Dict[str, Any]) -> List[str]:
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

    def _render_pipelines(self, ctx: Dict[str, Any]) -> List[str]:
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
                f" {entry_type} \u2192 {exit_type}"
            )
            for stage in pl["stages"]:
                cc_marker = "  !!" if stage["cc"] >= CC_HIGH else ""
                entry_lbl = " \u25b6" if stage.get("is_entry") else ""
                exit_lbl = " \u25a0" if stage.get("is_exit") else ""
                lines.append(
                    f"              \u2192 {stage['signature']}"
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

    def _render_transforms(self, ctx: Dict[str, Any]) -> List[str]:
        transforms = ctx["transforms"]
        if not transforms:
            return ["TRANSFORMS: none (fan-out < 10)"]

        lines = [f"TRANSFORMS (fan-out \u2265{FAN_OUT_THRESHOLD}):"]
        for t in transforms:
            lines.append(
                f"  {t['signature']:<55s} fan={t['fan_out']:<3}"
                f"  {t['label']}"
            )
        return lines

    def _render_contracts(self, ctx: Dict[str, Any]) -> List[str]:
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

    def _render_data_types(self, ctx: Dict[str, Any]) -> List[str]:
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
            lines.append("  HUB TYPES (consumed \u226510):")
            for h in hubs:
                lines.append(
                    f"    {h['type']} \u2192 {h['consumed']} consumers"
                    f" \u2192 split into:"
                )
                recs = HUB_SPLIT_RECOMMENDATIONS.get(h["type"], [])
                if recs:
                    for rec in recs:
                        lines.append(f"      - {rec}")
                else:
                    lines.append("      - (analyze consumers to suggest sub-interfaces)")

        return lines

    def _render_side_effects(self, ctx: Dict[str, Any]) -> List[str]:
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
                bar = "\u2588" * bar_len + "\u2591" * (4 - bar_len)
                pct = int(ratio * 100)
                lines.append(
                    f"    {pl['name']:<15s} {bar} {pct}% pure"
                )

        return lines

    # ------------------------------------------------------------------
    # utility helpers
    # ------------------------------------------------------------------
    def _is_excluded(self, path: str) -> bool:
        if not path:
            return False
        path_lower = path.lower().replace('\\', '/')
        for pattern in EXCLUDE_PATTERNS:
            if f'/{pattern}/' in path_lower or path_lower.startswith(f'{pattern}/'):
                return True
            if pattern in path_lower.split('/'):
                return True
        return False
