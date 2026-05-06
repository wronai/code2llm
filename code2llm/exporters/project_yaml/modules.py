"""Module metrics builder for project.yaml."""

from collections import defaultdict
from typing import Any, Dict, List, Tuple

from code2llm.core.models import AnalysisResult, ClassInfo, FunctionInfo
from code2llm.exporters.toon.helpers import _is_excluded, _rel_path
from .constants import CC_CRITICAL, CC_WARNING, FAN_OUT_THRESHOLD


def build_modules(result: AnalysisResult, line_counts: Dict[str, int]) -> List[Dict[str, Any]]:
    """Build module list with per-file metrics."""
    file_funcs, file_classes = group_by_file(result)

    all_files = set(file_funcs.keys()) | set(file_classes.keys())
    for mi in result.modules.values():
        if mi.file and not _is_excluded(mi.file):
            all_files.add(mi.file)

    modules = [
        compute_module_entry(fpath, result, line_counts, file_funcs, file_classes)
        for fpath in sorted(all_files)
    ]

    modules.sort(key=lambda m: m["cc_max"], reverse=True)
    return modules


def group_by_file(result: AnalysisResult) -> Tuple[
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


def compute_module_entry(
    fpath: str, result: AnalysisResult,
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

    inbound = compute_inbound_deps(funcs, fpath, result)
    exports = build_exports(funcs, classes, result)

    mod: Dict[str, Any] = {
        "path": rel, "lines": lc, "classes": len(classes),
        "methods": len(funcs), "cc_max": cc_max,
        "inbound_deps": len(inbound),
    }
    if exports:
        mod["exports"] = exports
    return mod


def compute_inbound_deps(
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


def build_exports(
    funcs: List[FunctionInfo],
    classes: List[ClassInfo],
    result: AnalysisResult,
) -> List[Dict[str, Any]]:
    """Build export list (classes + standalone functions) for a module."""
    exports = [build_class_export(ci, result) for ci in classes]
    exports.extend(build_function_exports(funcs, classes))
    return exports


def build_class_export(ci: ClassInfo, result: AnalysisResult) -> Dict[str, Any]:
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


def build_function_exports(
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
