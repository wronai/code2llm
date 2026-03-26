"""Project YAML Exporter — unified single source of truth for project diagnostics.

Generates project.yaml with:
  project:    — metadata, stats
  health:     — CC avg, critical count, alerts
  modules:    — per-file metrics, exports, methods
  hotspots:   — high fan-out orchestrators
  refactoring: — prioritized actions
  evolution:  — append-only history log
"""

import yaml
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .base import Exporter
from code2llm.core.models import AnalysisResult, FunctionInfo, ClassInfo
from .toon.helpers import _is_excluded, _rel_path, _scan_line_counts
from code2llm.core.config import LANGUAGE_EXTENSIONS


# Thresholds
CC_CRITICAL = 10
CC_WARNING = 15
CC_ERROR = 20
CC_SEVERE = 25
FAN_OUT_THRESHOLD = 10
FAN_OUT_ERROR = 15
FAN_OUT_SEVERE = 20
GOD_MODULE_LINES = 500


class ProjectYAMLExporter(Exporter):
    """Export unified project.yaml — single source of truth for diagnostics.

    Combines data from analysis.toon, analysis_view.toon, context.md, and evolution.toon.yaml
    into one machine-parseable YAML file.
    """

    def export(self, result: AnalysisResult, output_path: str, **kwargs) -> None:
        """Generate project.yaml from AnalysisResult.

        If the file already exists, the evolution section is appended (not replaced).
        """
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        # Load previous evolution entries if file exists
        prev_evolution = self._load_previous_evolution(output)

        data = self._build_project_yaml(result, prev_evolution)

        with open(output, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    # ------------------------------------------------------------------
    # top-level builder
    # ------------------------------------------------------------------
    def _build_project_yaml(
        self, result: AnalysisResult, prev_evolution: List[Dict]
    ) -> Dict[str, Any]:
        line_counts = _scan_line_counts(result.project_path)
        # Filter out venv/site-packages/etc — only count lines of non-excluded files
        filtered_lines = {
            k: v for k, v in line_counts.items()
            if not _is_excluded(k)
        }
        total_lines = sum(filtered_lines.values()) // 2  # keys stored twice (abs + rel)

        modules = self._build_modules(result, line_counts)
        health = self._build_health(result, modules)
        hotspots = self._build_hotspots(result)
        refactoring = self._build_refactoring(result, modules, hotspots)
        evolution = self._build_evolution(health, total_lines, prev_evolution)

        return {
            "version": "1",
            "project": {
                "name": Path(result.project_path).name if result.project_path else "unknown",
                "repo": result.project_path or "",
                "language": self._detect_primary_language(result),
                "analyzed_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "tool": "code2llm",
                "stats": {
                    "files": len(set(
                        fi.file for fi in result.functions.values()
                        if not _is_excluded(fi.file)
                    )) or len(result.modules),
                    "lines": total_lines,
                    "functions": len([
                        f for f in result.functions.values()
                        if not _is_excluded(f.file)
                    ]),
                    "classes": len([
                        c for c in result.classes.values()
                        if not _is_excluded(c.file)
                    ]),
                },
            },
            "health": health,
            "modules": modules,
            "hotspots": hotspots,
            "refactoring": refactoring,
            "evolution": evolution,
        }

    # ------------------------------------------------------------------
    # health
    # ------------------------------------------------------------------
    def _build_health(
        self, result: AnalysisResult, modules: List[Dict]
    ) -> Dict[str, Any]:
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

        # Detect duplicates (simple: same class name in different files)
        dup_count = self._count_duplicates(result)

        # Build alerts
        alerts = self._build_alerts(result)

        return {
            "cc_avg": cc_avg,
            "critical_count": critical_count,
            "critical_limit": CC_CRITICAL,
            "duplicates": dup_count,
            "cycles": len(cycles),
            "alerts": alerts if alerts else [],
        }

    def _build_alerts(self, result: AnalysisResult) -> List[Dict[str, Any]]:
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

    def _count_duplicates(self, result: AnalysisResult) -> int:
        name_files: Dict[str, List[str]] = defaultdict(list)
        for qname, ci in result.classes.items():
            if not _is_excluded(ci.file):
                name_files[ci.name].append(ci.file)
        return sum(1 for files in name_files.values() if len(set(files)) > 1)

    # ------------------------------------------------------------------
    # modules
    # ------------------------------------------------------------------
    def _build_modules(
        self, result: AnalysisResult, line_counts: Dict[str, int]
    ) -> List[Dict[str, Any]]:
        file_funcs, file_classes = self._group_by_file(result)

        all_files = set(file_funcs.keys()) | set(file_classes.keys())
        for mi in result.modules.values():
            if mi.file and not _is_excluded(mi.file):
                all_files.add(mi.file)

        modules = [
            self._compute_module_entry(
                fpath, result, line_counts, file_funcs, file_classes
            )
            for fpath in sorted(all_files)
        ]

        modules.sort(key=lambda m: m["cc_max"], reverse=True)
        return modules

    @staticmethod
    def _group_by_file(result: AnalysisResult) -> Tuple[
        Dict[str, List[FunctionInfo]], Dict[str, List[ClassInfo]]
    ]:
        """Group functions and classes by file path."""
        file_funcs: Dict[str, List[FunctionInfo]] = defaultdict(list)
        file_classes: Dict[str, List[ClassInfo]] = defaultdict(list)
        for fi in result.functions.values():
            if not _is_excluded(fi.file):
                file_funcs[fi.file].append(fi)
        for ci in result.classes.values():
            if not _is_excluded(ci.file):
                file_classes[ci.file].append(ci)
        return file_funcs, file_classes

    def _compute_module_entry(
        self, fpath: str, result: AnalysisResult,
        line_counts: Dict[str, int],
        file_funcs: Dict[str, List[FunctionInfo]],
        file_classes: Dict[str, List[ClassInfo]],
    ) -> Dict[str, Any]:
        """Build a single module dict for the given file."""
        rel = _rel_path(fpath, result.project_path)
        lc = line_counts.get(fpath, line_counts.get(rel, 0))
        funcs = file_funcs.get(fpath, [])
        classes = file_classes.get(fpath, [])

        cc_values = [f.complexity.get("cyclomatic_complexity", 0) for f in funcs]
        cc_max = max(cc_values) if cc_values else 0

        inbound = self._compute_inbound_deps(funcs, fpath, result)
        exports = self._build_exports(funcs, classes, result)

        mod: Dict[str, Any] = {
            "path": rel, "lines": lc, "classes": len(classes),
            "methods": len(funcs), "cc_max": cc_max,
            "inbound_deps": len(inbound),
        }
        if exports:
            mod["exports"] = exports
        return mod

    @staticmethod
    def _compute_inbound_deps(
        funcs: List[FunctionInfo], fpath: str, result: AnalysisResult
    ) -> set:
        """Count unique files that call into this module."""
        inbound = set()
        for fi in funcs:
            for caller in fi.called_by:
                caller_info = result.functions.get(caller)
                if caller_info and caller_info.file != fpath:
                    inbound.add(caller_info.file)
        return inbound

    def _build_exports(
        self,
        funcs: List[FunctionInfo],
        classes: List[ClassInfo],
        result: AnalysisResult,
    ) -> List[Dict[str, Any]]:
        exports = [self._build_class_export(ci, result) for ci in classes]
        exports.extend(self._build_function_exports(funcs, classes))
        return exports

    @staticmethod
    def _build_class_export(
        ci: ClassInfo, result: AnalysisResult
    ) -> Dict[str, Any]:
        """Build export entry for a single class."""
        class_funcs = [
            result.functions.get(m) for m in ci.methods
            if result.functions.get(m)
        ]
        method_ccs = [
            f.complexity.get("cyclomatic_complexity", 0) for f in class_funcs
        ]
        avg_cc = round(sum(method_ccs) / len(method_ccs), 1) if method_ccs else 0.0

        cls_export: Dict[str, Any] = {
            "name": ci.name, "type": "class", "cc_avg": avg_cc,
        }

        notable = []
        for mf in class_funcs:
            cc = mf.complexity.get("cyclomatic_complexity", 0)
            fan_out = len(set(mf.calls))
            if cc >= CC_CRITICAL or fan_out >= FAN_OUT_THRESHOLD:
                m_entry: Dict[str, Any] = {"name": mf.name, "cc": cc}
                if cc >= CC_WARNING:
                    m_entry["flag"] = "split"
                if fan_out >= FAN_OUT_THRESHOLD:
                    m_entry["fan_out"] = fan_out
                notable.append(m_entry)

        if notable:
            cls_export["methods"] = notable
        return cls_export

    @staticmethod
    def _build_function_exports(
        funcs: List[FunctionInfo], classes: List[ClassInfo]
    ) -> List[Dict[str, Any]]:
        """Build export entries for standalone (non-method) functions."""
        class_method_names = set()
        for ci in classes:
            class_method_names.update(ci.methods)

        exports = []
        for fi in funcs:
            if fi.qualified_name in class_method_names or fi.is_private:
                continue
            cc = fi.complexity.get("cyclomatic_complexity", 0)
            func_export: Dict[str, Any] = {
                "name": fi.name, "type": "function", "cc": cc,
            }
            if cc >= CC_WARNING:
                func_export["flag"] = "split"
            fan_out = len(set(fi.calls))
            if fan_out >= FAN_OUT_THRESHOLD:
                func_export["fan_out"] = fan_out
            exports.append(func_export)
        return exports

    # ------------------------------------------------------------------
    # hotspots
    # ------------------------------------------------------------------
    def _build_hotspots(self, result: AnalysisResult) -> List[Dict[str, Any]]:
        spots = []
        for qname, fi in result.functions.items():
            if _is_excluded(fi.file):
                continue
            fan_out = len(set(fi.calls))
            if fan_out >= FAN_OUT_THRESHOLD:
                display = fi.name
                if fi.class_name:
                    display = f"{fi.class_name}.{fi.name}"
                note = self._hotspot_note(fi, fan_out)
                spots.append({
                    "name": display,
                    "fan_out": fan_out,
                    "note": note,
                })
        spots.sort(key=lambda s: s["fan_out"], reverse=True)
        return spots[:10]

    @staticmethod
    def _hotspot_note(fi: FunctionInfo, fan_out: int) -> str:
        if "format" in fi.name.lower() or "dispatch" in fi.name.lower():
            return f"{fan_out}-way dispatch"
        if "export" in fi.name.lower():
            return f"Export with {fan_out} outputs"
        if "analyze" in fi.name.lower() or "process" in fi.name.lower():
            return f"Analysis pipeline, {fan_out} stages"
        if fi.docstring:
            return fi.docstring[:80]
        return f"Orchestrates {fan_out} calls"

    # ------------------------------------------------------------------
    # refactoring
    # ------------------------------------------------------------------
    def _build_refactoring(
        self,
        result: AnalysisResult,
        modules: List[Dict],
        hotspots: List[Dict],
    ) -> Dict[str, Any]:
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
                    "action": f"Split {display} (CC={cc} → target CC<{CC_CRITICAL})",
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

    # ------------------------------------------------------------------
    # evolution (append-only)
    # ------------------------------------------------------------------
    def _build_evolution(
        self,
        health: Dict[str, Any],
        total_lines: int,
        prev_evolution: List[Dict],
    ) -> List[Dict[str, Any]]:
        today = datetime.now().strftime("%Y-%m-%d")

        new_entry = {
            "date": today,
            "cc_avg": health["cc_avg"],
            "critical": health["critical_count"],
            "lines": total_lines,
            "note": "Automated analysis",
        }

        # Avoid duplicate entries for same date
        evolution = [e for e in prev_evolution if e.get("date") != today]
        evolution.append(new_entry)

        return evolution

    def _detect_primary_language(self, result: AnalysisResult) -> str:
        """Detect the primary language of the project based on file counts."""
        lang_counts: Dict[str, int] = defaultdict(int)
        
        # Count files by language
        for mi in result.modules.values():
            if _is_excluded(mi.file):
                continue
            detected = False
            for lang, extensions in LANGUAGE_EXTENSIONS.items():
                if any(mi.file.endswith(ext) for ext in extensions):
                    lang_counts[lang] += 1
                    detected = True
                    break
            if not detected:
                # Fallback to extension
                ext = Path(mi.file).suffix.lstrip('.').lower()
                if ext:
                    lang_counts[ext] += 1
        
        if not lang_counts:
            return "unknown"
        
        # Return the most common language
        return max(lang_counts.items(), key=lambda x: x[1])[0]

    def _load_previous_evolution(self, output_path: Path) -> List[Dict]:
        if not output_path.exists():
            return []
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if isinstance(data, dict) and "evolution" in data:
                evo = data["evolution"]
                if isinstance(evo, list):
                    return evo
        except Exception:
            pass
        return []
