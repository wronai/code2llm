"""Shared helpers for Mermaid flow rendering."""

from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple


def _filtered_functions(
    result: Any,
    module_of: Callable[[str], str],
    should_skip_module: Callable[[str, bool], bool],
    include_examples: bool = False,
) -> Dict[str, Any]:
    """Return functions after applying the flow diagram skip rules."""
    if include_examples:
        return dict(result.functions)
    return {
        name: fi for name, fi in result.functions.items()
        if not should_skip_module(module_of(name), include_examples)
    }


def _entry_points(
    filtered_funcs: Dict[str, Any],
    result: Any,
    is_entry_point: Callable[[str, Any, Any], bool],
) -> List[str]:
    """Collect entry points in a stable order."""
    return [
        name for name, fi in filtered_funcs.items()
        if is_entry_point(name, fi, result)
    ]


def _group_functions_by_module(
    funcs: Dict[str, Any],
    module_of: Callable[[str], str],
) -> Dict[str, List[Tuple[str, Any]]]:
    """Group functions by module for rendering."""
    modules: Dict[str, List[Tuple[str, Any]]] = defaultdict(list)
    for func_name, fi in funcs.items():
        modules[module_of(func_name)].append((func_name, fi))
    return modules


def _classify_architecture_module(func_name: str, module: str) -> str:
    """Assign a function to a compact architecture bucket."""
    if 'cli' in module.lower():
        return 'CLI'
    if 'exporter' in module.lower() or 'export' in func_name.lower():
        return 'Exporters'
    return 'Core'


def _group_architecture_functions(
    funcs: Dict[str, Any],
    module_of: Callable[[str], str],
) -> Dict[str, List[str]]:
    """Group functions into the compact architecture buckets."""
    arch_modules: Dict[str, List[str]] = {
        'CLI': [],
        'Core': [],
        'Exporters': [],
    }
    for func_name in funcs:
        bucket = _classify_architecture_module(func_name, module_of(func_name))
        arch_modules[bucket].append(func_name)
    return arch_modules


def _select_key_functions(
    func_names: List[str],
    funcs: Dict[str, Any],
    entry_points: Set[str],
    critical_path: Set[str],
    get_cc: Callable[[Any], int],
    threshold: int = 15,
) -> List[str]:
    """Choose the compact set of functions to show in the architectural view."""
    key_funcs: List[str] = []
    for fn in func_names:
        fi = funcs.get(fn)
        if not fi:
            continue
        cc = get_cc(fi)
        if fn in entry_points or fn in critical_path or cc >= threshold:
            key_funcs.append(fn)
    return key_funcs


def _append_flow_node(
    lines: List[str],
    func_name: str,
    fi: Any,
    short_len: int,
    entry_points: Set[str],
    readable_id: Callable[[str], str],
    get_cc: Callable[[Any], int],
    high_threshold: int = 15,
    med_threshold: int = 8,
) -> None:
    """Append a single Mermaid node with the appropriate CC styling."""
    sid = readable_id(func_name)
    short = fi.name[:short_len]
    cc = get_cc(fi)

    if func_name in entry_points:
        lines.append(f'        {sid}["{short}"]')
    elif cc >= high_threshold:
        lines.append(f'        {sid}{{{{{short} CC={cc}}}}}')
    elif cc >= med_threshold:
        lines.append(f'        {sid}("{short} CC={cc}")')
    else:
        lines.append(f'        {sid}["{short}"]')


def _render_module_subgraphs(
    lines: List[str],
    modules: Dict[str, List[Tuple[str, Any]]],
    entry_points: Sequence[str],
    short_len: int,
    readable_id: Callable[[str], str],
    safe_module: Callable[[str], str],
    get_cc: Callable[[Any], int],
    sort_funcs: bool = False,
    max_funcs: Optional[int] = None,
    high_threshold: int = 15,
    med_threshold: int = 8,
) -> None:
    """Render module subgraphs for the detailed and full flow views."""
    entry_set = set(entry_points)
    for module, module_funcs in sorted(modules.items()):
        lines.append(f"    subgraph {safe_module(module)}")

        ordered_funcs = module_funcs
        if sort_funcs:
            ordered_funcs = sorted(module_funcs, key=lambda x: (-get_cc(x[1]), x[1].name))

        visible_funcs = ordered_funcs if max_funcs is None else ordered_funcs[:max_funcs]
        for func_name, fi in visible_funcs:
            _append_flow_node(
                lines,
                func_name,
                fi,
                short_len,
                entry_set,
                readable_id,
                get_cc,
                high_threshold=high_threshold,
                med_threshold=med_threshold,
            )

        if max_funcs is not None and len(ordered_funcs) > max_funcs:
            lines.append(f'        ...["+{len(ordered_funcs) - max_funcs} more"]')
        lines.append("    end")
        lines.append("")


def _render_flow_edges(
    lines: List[str],
    funcs: Dict[str, Any],
    readable_id: Callable[[str], str],
    resolve: Callable[..., Optional[str]],
    calls_per_function: int = 10,
    limit: Optional[int] = 200,
    name_index: Optional[Dict[str, List[str]]] = None,
) -> None:
    """Render cross-function call edges with optional limits."""
    seen_edges: Set[Tuple[str, str]] = set()
    for func_name, fi in funcs.items():
        src = readable_id(func_name)
        for callee in fi.calls[:calls_per_function]:
            resolved = resolve(callee, funcs, name_index) if name_index else resolve(callee, funcs)
            if resolved and resolved != func_name:
                dst = readable_id(resolved)
                edge = (src, dst)
                if edge not in seen_edges:
                    seen_edges.add(edge)
                    lines.append(f"    {src} --> {dst}")
                    if limit is not None and len(seen_edges) >= limit:
                        return
        if limit is not None and len(seen_edges) >= limit:
            return


def _append_entry_styles(
    lines: List[str],
    entry_points: Sequence[str],
    readable_id: Callable[[str], str],
    entry_limit: int = 15,
) -> None:
    """Style the entry points in the Mermaid graph."""
    if entry_points:
        entry_ids = [readable_id(ep) for ep in entry_points[:entry_limit]]
        lines.append(f"    class {','.join(entry_ids)} entry")


def _render_flow_styles(
    lines: List[str],
    funcs: Dict[str, Any],
    entry_points: Sequence[str],
    readable_id: Callable[[str], str],
    get_cc: Callable[[Any], int],
    high_threshold: int = 15,
    med_threshold: int = 8,
    high_limit: int = 30,
    med_limit: int = 30,
    entry_limit: int = 15,
) -> None:
    """Render CC-based styling for the detailed and full flow views."""
    high_nodes: List[str] = []
    med_nodes: List[str] = []

    for func_name, fi in funcs.items():
        cc = get_cc(fi)
        sid = readable_id(func_name)
        if cc >= high_threshold:
            high_nodes.append(sid)
        elif cc >= med_threshold:
            med_nodes.append(sid)

    if high_nodes:
        lines.append(f"    class {','.join(high_nodes[:high_limit])} highCC")
    if med_nodes:
        lines.append(f"    class {','.join(med_nodes[:med_limit])} medCC")
    _append_entry_styles(lines, entry_points, readable_id, entry_limit)


def _render_architecture_view(
    lines: List[str],
    filtered_funcs: Dict[str, Any],
    entry_points: Sequence[str],
    critical_path: Set[str],
    module_of: Callable[[str], str],
    readable_id: Callable[[str], str],
    get_cc: Callable[[Any], int],
) -> None:
    """Render the compact architecture view used by export_flow_compact."""
    arch_modules = _group_architecture_functions(filtered_funcs, module_of)
    entry_set = set(entry_points)
    for arch_name, func_names in arch_modules.items():
        if not func_names:
            continue

        lines.append(f"    subgraph {arch_name}")
        key_funcs = _select_key_functions(
            func_names,
            filtered_funcs,
            entry_set,
            critical_path,
            get_cc,
            threshold=15,
        )
        for func_name in key_funcs[:15]:
            fi = filtered_funcs.get(func_name)
            if fi:
                _append_flow_node(lines, func_name, fi, 30, entry_set, readable_id, get_cc)

        if len(key_funcs) > 15:
            lines.append(f'        ...["+{len(key_funcs) - 15} more"]')
        lines.append("    end")
        lines.append("")

    _append_entry_styles(lines, entry_points, readable_id, entry_limit=10)
