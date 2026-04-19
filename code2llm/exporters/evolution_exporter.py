"""Evolution Exporter — prioritized refactoring queue for iterative improvement.

Generates evolution.toon.yaml with:
  NEXT[N]         — ranked refactoring actions (impact × effort)
  RISKS[N]        — breaking changes and compatibility notes
  METRICS-TARGET  — measurable goals vs current baseline
  HISTORY         — comparison with previous evolution.toon.yaml
"""

import yaml
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .base import BaseExporter, export_format
from code2llm.core.models import AnalysisResult, FunctionInfo


# Thresholds
CC_SPLIT_THRESHOLD = 15
FAN_OUT_THRESHOLD = 10
GOD_MODULE_LINES = 500
HUB_TYPE_THRESHOLD = 10


@export_format("evolution", description="Evolution refactoring queue format", extension=".toon.yaml")
class EvolutionExporter(BaseExporter):
    """Export evolution.toon.yaml — prioritized refactoring queue."""

    # Exclude patterns (mirrors ToonExporter)
    EXCLUDE_PATTERNS = {
        'venv', '.venv', 'env', '.env', 'publish-env', 'test-env',
        'site-packages', 'node_modules', '__pycache__', '.git',
        'dist', 'build', 'egg-info', '.tox', '.mypy_cache',
        'examples', 'benchmarks', 'tests', 'scripts', 'demo_langs',
    }

    def _is_excluded(self, path: str) -> bool:
        """Check if path should be excluded (venv, site-packages, etc.)."""
        path_lower = path.lower().replace('\\', '/')
        for pattern in self.EXCLUDE_PATTERNS:
            if f'/{pattern}/' in path_lower or path_lower.startswith(f'{pattern}/'):
                return True
            if pattern in path_lower.split('/'):
                return True
        return False

    def export(self, result: AnalysisResult, output_path: str, **kwargs) -> Optional[Path]:
        """Generate evolution.toon."""
        ctx = self._build_context(result)

        sections: List[str] = []
        sections.extend(self._render_header(ctx))
        sections.append("")
        sections.extend(self._render_next(ctx))
        sections.append("")
        sections.extend(self._render_risks(ctx))
        sections.append("")
        sections.extend(self._render_metrics_target(ctx))
        sections.append("")
        sections.extend(self._render_patterns(ctx))
        sections.append("")
        sections.extend(self._render_history(ctx, output_path))

        path = self._ensure_dir(output_path)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(sections) + "\n")
        return path

    def export_to_yaml(self, result: AnalysisResult, output_path: str, **kwargs) -> None:
        """Generate evolution.toon.yaml (structured YAML)."""
        ctx = self._build_context(result)

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

        data = {
            "format": "evolution-toon-yaml",
            "timestamp": ctx["timestamp"],
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

    # ------------------------------------------------------------------
    # context builder
    # ------------------------------------------------------------------
    def _build_context(self, result: AnalysisResult) -> Dict[str, Any]:
        ctx: Dict[str, Any] = {
            "result": result,
            "timestamp": datetime.now().strftime("%Y-%m-%d"),
        }
        ctx["funcs"] = self._compute_func_data(result)
        ctx["god_modules"] = self._compute_god_modules(result)
        ctx["hub_types"] = self._compute_hub_types(result)

        # Overall metrics
        all_cc = [f["cc"] for f in ctx["funcs"]]
        ctx["avg_cc"] = round(sum(all_cc) / len(all_cc), 1) if all_cc else 0.0
        ctx["max_cc"] = max(all_cc) if all_cc else 0
        ctx["total_funcs"] = len(all_cc)
        ctx["total_files"] = len(set(f["file"] for f in ctx["funcs"])) or 1
        ctx["high_cc_count"] = len([c for c in all_cc if c >= CC_SPLIT_THRESHOLD])
        ctx["critical_count"] = len([c for c in all_cc if c >= 10])

        return ctx

    def _compute_func_data(self, result: AnalysisResult) -> List[Dict]:
        """Compute per-function metrics, excluding venv."""
        func_data = []
        for qname, fi in result.functions.items():
            if self._is_excluded(fi.file):
                continue
            cc = fi.complexity.get("cyclomatic_complexity", 0)
            fan_out = len(set(fi.calls))
            fan_in = len(set(fi.called_by))
            func_data.append({
                "qname": qname, "name": fi.name,
                "class_name": fi.class_name, "cc": cc,
                "fan_out": fan_out, "fan_in": fan_in,
                "impact": cc * max(fan_out, 1),
                "file": fi.file, "module": fi.module,
            })
        return sorted(func_data, key=lambda x: x["impact"], reverse=True)

    def _scan_file_sizes(self, project_path: Optional[Path]) -> Dict[str, int]:
        """Scan Python files and return line counts."""
        file_lines: Dict[str, int] = {}
        if not project_path or not project_path.is_dir():
            return file_lines
        
        for py in project_path.rglob("*.py"):
            fpath = str(py)
            if self._is_excluded(fpath):
                continue
            try:
                lc = len(py.read_text(encoding="utf-8", errors="ignore").splitlines())
                file_lines[fpath] = lc
            except Exception:
                pass
        return file_lines

    def _aggregate_file_stats(
        self, 
        result: AnalysisResult, 
        file_lines: Dict[str, int]
    ) -> Dict[str, Dict]:
        """Aggregate function and class data per file."""
        file_stats: Dict[str, Dict] = defaultdict(
            lambda: {"lines": 0, "funcs": 0, "classes": set(), "max_cc": 0}
        )
        
        # Initialize with line counts
        for fpath, lc in file_lines.items():
            file_stats[fpath]["lines"] = lc
        
        # Aggregate function data
        for qname, fi in result.functions.items():
            if self._is_excluded(fi.file):
                continue
            fs = file_stats[fi.file]
            fs["funcs"] += 1
            fs["max_cc"] = max(fs["max_cc"], fi.complexity.get("cyclomatic_complexity", 0))
            if fi.class_name:
                fs["classes"].add(fi.class_name)
        
        # Aggregate class data
        for qname, ci in result.classes.items():
            if not self._is_excluded(ci.file):
                file_stats[ci.file]["classes"].add(ci.name)
        
        return file_stats

    def _make_relative_path(self, fpath: str, project_path: Optional[Path]) -> str:
        """Convert absolute path to relative path."""
        if not project_path:
            return fpath
        try:
            return str(Path(fpath).relative_to(project_path))
        except ValueError:
            return fpath

    def _filter_god_modules(self, file_stats: Dict[str, Dict], project_path: Optional[Path]) -> List[Dict]:
        """Filter files to god modules (≥500 lines)."""
        god_modules = []
        for fpath, stats in file_stats.items():
            if stats["lines"] >= GOD_MODULE_LINES:
                rel = self._make_relative_path(fpath, project_path)
                god_modules.append({
                    "file": rel, 
                    "lines": stats["lines"],
                    "funcs": stats["funcs"], 
                    "classes": len(stats["classes"]),
                    "max_cc": stats["max_cc"],
                })
        god_modules.sort(key=lambda x: x["lines"], reverse=True)
        return god_modules

    def _compute_god_modules(self, result: AnalysisResult) -> List[Dict]:
        """Identify god modules (≥500 lines) from project files."""
        pp = Path(result.project_path) if result.project_path else None
        
        file_lines = self._scan_file_sizes(pp)
        file_stats = self._aggregate_file_stats(result, file_lines)
        return self._filter_god_modules(file_stats, pp)

    def _compute_hub_types(self, result: AnalysisResult) -> List[Dict]:
        """Identify hub types consumed by many functions."""
        type_consumers: Dict[str, int] = defaultdict(int)
        type_producers: Dict[str, int] = defaultdict(int)
        for qname, fi in result.functions.items():
            ret = fi.complexity.get("return_type", "")
            if ret:
                type_producers[ret] += 1
            for arg_type in fi.complexity.get("arg_types", []):
                if arg_type:
                    type_consumers[arg_type] += 1
        hub_types = [
            {"type": t, "consumers": c, "producers": type_producers.get(t, 0)}
            for t, c in type_consumers.items()
            if c >= HUB_TYPE_THRESHOLD
        ]
        hub_types.sort(key=lambda x: x["consumers"], reverse=True)
        return hub_types

    # ------------------------------------------------------------------
    # render sections
    # ------------------------------------------------------------------
    def _render_header(self, ctx: Dict[str, Any]) -> List[str]:
        result = ctx["result"]
        return [
            f"# code2llm/evolution | {ctx['total_funcs']} func"
            f" | {ctx['total_files']}f | {ctx['timestamp']}",
        ]

    def _render_next(self, ctx: Dict[str, Any]) -> List[str]:
        """Render NEXT — ranked refactoring queue."""
        actions: List[Dict[str, Any]] = []

        # 1. God modules → split
        for gm in ctx["god_modules"][:3]:
            actions.append({
                "priority": "!!",
                "action": "SPLIT",
                "target": gm["file"],
                "why": f"{gm['lines']}L, {gm['classes']} classes, max CC={gm['max_cc']}",
                "effort": "~4h",
                "impact_score": gm["lines"] * gm["max_cc"],
            })

        # 2. High CC functions → split
        for f in ctx["funcs"][:20]:
            if f["cc"] >= CC_SPLIT_THRESHOLD:
                display = f["name"]
                if f["class_name"]:
                    display = f"{f['class_name']}.{f['name']}"
                actions.append({
                    "priority": "!!" if f["cc"] >= 25 else "!",
                    "action": "SPLIT-FUNC",
                    "target": f"{display}  CC={f['cc']}  fan={f['fan_out']}",
                    "why": f"CC={f['cc']} exceeds {CC_SPLIT_THRESHOLD}",
                    "effort": "~1h",
                    "impact_score": f["impact"],
                })

        # 3. Hub types → interface segregation
        for ht in ctx["hub_types"][:3]:
            if ht["consumers"] >= 20:
                actions.append({
                    "priority": "!",
                    "action": "INTERFACE-SPLIT",
                    "target": f"{ht['type']}  consumed:{ht['consumers']}",
                    "why": f"Hub type with {ht['consumers']} consumers → split interface",
                    "effort": "~6h",
                    "impact_score": ht["consumers"] * 10,
                })

        # Sort by impact and limit
        actions.sort(key=lambda x: x["impact_score"], reverse=True)
        actions = actions[:10]

        if not actions:
            return ["NEXT[0]: no refactoring needed"]

        lines = [f"NEXT[{len(actions)}] (ranked by impact):"]
        for i, a in enumerate(actions, 1):
            lines.append(
                f"  [{i}] {a['priority']:2s} {a['action']:15s} {a['target']}"
            )
            lines.append(
                f"      WHY: {a['why']}"
            )
            lines.append(
                f"      EFFORT: {a['effort']}  IMPACT: {a['impact_score']}"
            )
            lines.append("")

        return lines

    def _render_risks(self, ctx: Dict[str, Any]) -> List[str]:
        """Render RISKS — potential breaking changes."""
        risks: List[str] = []

        # God module splits may break imports
        for gm in ctx["god_modules"][:3]:
            risks.append(
                f"⚠ Splitting {gm['file']} may break {gm['funcs']} import paths"
            )

        # Hub type splits change public API
        for ht in ctx["hub_types"][:2]:
            if ht["consumers"] >= 20:
                risks.append(
                    f"⚠ Splitting {ht['type']} changes API for {ht['consumers']} consumers"
                )

        if not risks:
            return ["RISKS[0]: none"]

        lines = [f"RISKS[{len(risks)}]:"]
        for r in risks:
            lines.append(f"  {r}")
        return lines

    def _render_metrics_target(self, ctx: Dict[str, Any]) -> List[str]:
        """Render METRICS-TARGET — baseline vs goals."""
        avg = ctx["avg_cc"]
        max_cc = ctx["max_cc"]
        gods = len(ctx["god_modules"])
        hubs = len(ctx["hub_types"])
        high = ctx["high_cc_count"]

        # Compute targets (halve the worst metrics)
        target_avg = round(min(avg * 0.7, 5.0), 1)
        target_max = min(max_cc // 2, 20)
        target_gods = 0
        target_high = max(high // 2, 0)

        lines = [
            "METRICS-TARGET:",
            f"  CC̄:          {avg} → ≤{target_avg}",
            f"  max-CC:      {max_cc} → ≤{target_max}",
            f"  god-modules: {gods} → {target_gods}",
            f"  high-CC(≥{CC_SPLIT_THRESHOLD}): {high} → ≤{target_high}",
            f"  hub-types:   {hubs} → ≤{max(hubs - 2, 0)}",
        ]
        return lines

    def _render_patterns(self, ctx: Dict[str, Any]) -> List[str]:
        """Render PATTERNS — shared language parser extraction patterns."""
        lines = [
            "PATTERNS (language parser shared logic):",
            "  _extract_declarations() in base.py — unified extraction for:",
            "    - TypeScript: interfaces, types, classes, functions, arrow funcs",
            "    - PHP: namespaces, traits, classes, functions, includes",
            "    - Ruby: modules, classes, methods, requires",
            "    - C++: classes, structs, functions, #includes",
            "    - C#: classes, interfaces, methods, usings",
            "    - Java: classes, interfaces, methods, imports",
            "    - Go: packages, functions, structs",
            "    - Rust: modules, functions, traits, use statements",
            "",
            "  Shared regex patterns per language:",
            "    - import: language-specific import/require/using patterns",
            "    - class: class/struct/trait declarations with inheritance",
            "    - function: function/method signatures with visibility",
            "    - brace_tracking: for C-family languages ({ })",
            "    - end_keyword_tracking: for Ruby (module/class/def...end)",
            "",
            "  Benefits:",
            "    - Consistent extraction logic across all languages",
            "    - Reduced code duplication (~70% reduction in parser LOC)",
            "    - Easier maintenance: fix once, apply everywhere",
            "    - Standardized FunctionInfo/ClassInfo models",
        ]
        return lines

    def _render_history(self, ctx: Dict[str, Any], output_path: str) -> List[str]:
        """Render HISTORY — load previous evolution.toon.yaml if exists."""
        lines = ["HISTORY:"]

        prev_path = Path(output_path)
        if prev_path.exists():
            try:
                prev_content = prev_path.read_text(encoding="utf-8")
                # Extract previous metrics line
                for line in prev_content.splitlines():
                    if line.strip().startswith("CC̄:"):
                        prev_avg = line.split("→")[0].strip().split()[-1]
                        lines.append(f"  prev CC̄={prev_avg} → now CC̄={ctx['avg_cc']}")
                        break
                else:
                    lines.append(f"  previous evolution.toon.yaml found but no metrics parsed")
            except Exception:
                lines.append(f"  (could not read previous evolution.toon.yaml)")
        else:
            lines.append(f"  (first run — no previous data)")

        return lines
