"""Map exporter details — render D: details per module with imports, exports, classes, functions."""

from typing import List

from code2llm.core.models import AnalysisResult, FunctionInfo

from .utils import rel_path


def render_details(result: AnalysisResult, is_excluded_path) -> List[str]:
    """Render D: — details per module."""
    lines = ["D:"]
    mod_items = _rank_modules(result, is_excluded_path)
    for mname, mi, max_cc in mod_items:
        _render_map_module(result, mi, lines, is_excluded_path)
    return lines


def _rank_modules(result: AnalysisResult, is_excluded_path):
    """Sort modules by max CC desc, excluding excluded paths."""
    mod_items = []
    for mname, mi in result.modules.items():
        if is_excluded_path(mi.file):
            continue
        max_cc = 0.0
        for fq in mi.functions:
            fi = result.functions.get(fq)
            if fi:
                cc = fi.complexity.get("cyclomatic_complexity", 0)
                max_cc = max(max_cc, cc)
        mod_items.append((mname, mi, max_cc))
    mod_items.sort(key=lambda x: x[2], reverse=True)
    return mod_items


def _render_map_module(result, mi, lines, is_excluded_path):
    """Render a single module's detail: imports, exports, classes, funcs."""
    rel = rel_path(mi.file, result.project_path)
    lines.append(f"  {rel}:")

    # imports
    if mi.imports:
        imp_str = ",".join(sorted(mi.imports))
        lines.append(f"    i: {imp_str}")

    # exports
    exports = []
    for cq in mi.classes:
        ci = result.classes.get(cq)
        if ci:
            exports.append(ci.name)
    for fq in mi.functions:
        fi = result.functions.get(fq)
        if fi and not fi.class_name:
            exports.append(fi.name)
    if exports:
        lines.append(f"    e: {','.join(exports)}")

    # classes with method signatures
    for cq in mi.classes:
        ci = result.classes.get(cq)
        if not ci:
            continue
        _render_map_class(result, ci, lines)

    # standalone functions
    for fq in mi.functions:
        fi = result.functions.get(fq)
        if fi and not fi.class_name:
            sig = _function_signature(fi)
            lines.append(f"    {sig}")


def _render_map_class(result, ci, lines):
    """Render a single class with its method signatures."""
    doc = ""
    if ci.docstring:
        doc = f"  # {ci.docstring[:60].rstrip('.')}..."

    method_sigs = []
    for mq in ci.methods:
        fi = result.functions.get(mq)
        if fi:
            arity = len(fi.args) - (1 if fi.is_method else 0)
            method_sigs.append(f"{fi.name}({arity})")

    bases_str = ""
    if ci.bases:
        bases_str = f"({','.join(ci.bases)})"

    if method_sigs:
        lines.append(
            f"    {ci.name}{bases_str}: "
            f"{','.join(method_sigs)}{doc}"
        )
    else:
        lines.append(f"    {ci.name}{bases_str}:{doc}")


def _function_signature(fi: FunctionInfo) -> str:
    """Build compact signature: name(arg:type;arg2:type)->ReturnType"""
    args_parts = []
    for arg in fi.args:
        if arg == "self":
            continue
        args_parts.append(arg)

    args_str = ";".join(args_parts) if args_parts else ""
    ret = ""
    if fi.returns:
        ret = f"->{fi.returns}"
    return f"{fi.name}({args_str}){ret}"


__all__ = ['render_details']
