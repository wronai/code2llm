"""Evolution exporter computation — metrics calculation for god modules, hub types, etc."""

from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from code2llm.core.models import AnalysisResult, FunctionInfo

from .constants import GOD_MODULE_LINES, HUB_TYPE_THRESHOLD, CC_SPLIT_THRESHOLD
from .exclusion import is_excluded


def compute_func_data(result: AnalysisResult) -> List[Dict]:
    """Compute per-function metrics, excluding venv."""
    func_data = []
    for qname, fi in result.functions.items():
        if is_excluded(fi.file):
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


def scan_file_sizes(project_path: Optional[Path], result: Optional[AnalysisResult] = None) -> Dict[str, int]:
    """Return per-file line counts, preferring already-analyzed module data."""
    file_lines: Dict[str, int] = {}

    # Fast path: derive from AnalysisResult modules (no I/O)
    if result and result.modules:
        for mi in result.modules.values():
            if mi.file and not is_excluded(mi.file):
                lc = mi.line_count if hasattr(mi, 'line_count') and mi.line_count else 0
                if lc == 0:
                    lc = len(mi.functions) + len(mi.classes)
                if lc > 0:
                    file_lines[mi.file] = lc
        if file_lines:
            return file_lines

    # Slow fallback: single os.walk (only if result is unavailable)
    if not project_path or not project_path.is_dir():
        return file_lines

    import os
    exclude = {'.git', '__pycache__', 'node_modules', 'venv', '.venv',
               'env', '.env', 'site-packages', 'dist', 'build', '.tox'}
    for dirpath, dirnames, filenames in os.walk(str(project_path)):
        dirnames[:] = [d for d in dirnames if d not in exclude]
        for fn in filenames:
            if not fn.endswith('.py'):
                continue
            fpath = os.path.join(dirpath, fn)
            try:
                with open(fpath, encoding='utf-8', errors='ignore') as f:
                    file_lines[fpath] = sum(1 for _ in f)
            except Exception:
                pass
    return file_lines


def aggregate_file_stats(
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
        if is_excluded(fi.file):
            continue
        fs = file_stats[fi.file]
        fs["funcs"] += 1
        fs["max_cc"] = max(fs["max_cc"], fi.complexity.get("cyclomatic_complexity", 0))
        if fi.class_name:
            fs["classes"].add(fi.class_name)
    
    # Aggregate class data
    for qname, ci in result.classes.items():
        if not is_excluded(ci.file):
            file_stats[ci.file]["classes"].add(ci.name)
    
    return file_stats


def make_relative_path(fpath: str, project_path: Optional[Path]) -> str:
    """Convert absolute path to relative path."""
    if not project_path:
        return fpath
    try:
        return str(Path(fpath).relative_to(project_path))
    except ValueError:
        return fpath


def filter_god_modules(file_stats: Dict[str, Dict], project_path: Optional[Path]) -> List[Dict]:
    """Filter files to god modules (≥500 lines)."""
    god_modules = []
    for fpath, stats in file_stats.items():
        if stats["lines"] >= GOD_MODULE_LINES:
            rel = make_relative_path(fpath, project_path)
            god_modules.append({
                "file": rel, 
                "lines": stats["lines"],
                "funcs": stats["funcs"], 
                "classes": len(stats["classes"]),
                "max_cc": stats["max_cc"],
            })
    god_modules.sort(key=lambda x: x["lines"], reverse=True)
    return god_modules


def compute_god_modules(result: AnalysisResult) -> List[Dict]:
    """Identify god modules (≥500 lines) from project files."""
    pp = Path(result.project_path) if result.project_path else None
    
    file_lines = scan_file_sizes(pp, result)
    file_stats = aggregate_file_stats(result, file_lines)
    return filter_god_modules(file_stats, pp)


def compute_hub_types(result: AnalysisResult) -> List[Dict]:
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


def build_context(result: AnalysisResult) -> Dict[str, Any]:
    """Build context dict with all computed metrics."""
    ctx = {
        "result": result,
    }
    ctx["funcs"] = compute_func_data(result)
    ctx["god_modules"] = compute_god_modules(result)
    ctx["hub_types"] = compute_hub_types(result)

    # Overall metrics
    all_cc = [f["cc"] for f in ctx["funcs"]]
    ctx["avg_cc"] = round(sum(all_cc) / len(all_cc), 1) if all_cc else 0.0
    ctx["max_cc"] = max(all_cc) if all_cc else 0
    ctx["total_funcs"] = len(all_cc)
    ctx["total_files"] = len(set(f["file"] for f in ctx["funcs"])) or 1
    ctx["high_cc_count"] = len([c for c in all_cc if c >= CC_SPLIT_THRESHOLD])
    ctx["critical_count"] = len([c for c in all_cc if c >= 10])

    return ctx


__all__ = [
    'compute_func_data',
    'scan_file_sizes',
    'aggregate_file_stats',
    'make_relative_path',
    'filter_god_modules',
    'compute_god_modules',
    'compute_hub_types',
    'build_context',
]
