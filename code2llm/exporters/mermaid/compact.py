"""Mermaid compact export — compact_flow.mmd module-level aggregation."""

from collections import defaultdict
from typing import Dict, Set, Tuple

from code2llm.core.models import AnalysisResult

from .utils import safe_module, resolve_callee, write_file, build_name_index


def export_compact(result: AnalysisResult, output_path: str) -> None:
    """Export module-level graph: one node per module, weighted edges."""
    lines = ["flowchart TD"]

    from .utils import module_of
    # Build name index for O(1) callee resolution
    name_index = build_name_index(result.functions)

    # Compute module stats
    mod_funcs: Dict[str, int] = defaultdict(int)
    mod_lines: Dict[str, int] = defaultdict(int)
    for func_name, fi in result.functions.items():
        module = module_of(func_name)
        mod_funcs[module] += 1
        mod_lines[module] += fi.end_line - fi.line if hasattr(fi, 'end_line') and fi.end_line else 0

    # Cross-module edges with weights
    cross_edges: Dict[Tuple[str, str], int] = defaultdict(int)
    for func_name, fi in result.functions.items():
        src_mod = module_of(func_name)
        for callee in fi.calls:
            resolved = resolve_callee(callee, result.functions, name_index)
            if resolved:
                dst_mod = module_of(resolved)
                if dst_mod != src_mod:
                    cross_edges[(src_mod, dst_mod)] += 1

    # Only modules with cross-edges
    active_mods: Set[str] = set()
    for (s, d) in cross_edges:
        active_mods.add(s)
        active_mods.add(d)

    # Add all modules with functions as fallback
    if not active_mods:
        active_mods = set(mod_funcs.keys())

    # Nodes — module boxes
    for mod in sorted(active_mods):
        sid = safe_module(mod)
        nf = mod_funcs.get(mod, 0)
        lines.append(f'    {sid}["{mod}<br/>{nf} funcs"]')

    # Weighted edges
    for (src, dst), weight in sorted(cross_edges.items(), key=lambda x: -x[1]):
        s = safe_module(src)
        d = safe_module(dst)
        if weight > 3:
            lines.append(f"    {s} ==>|{weight}| {d}")
        else:
            lines.append(f"    {s} -->|{weight}| {d}")

    write_file(output_path, lines)


__all__ = ['export_compact']
