"""Mermaid calls export — calls.mmd simplified call graph."""

from typing import Dict, List, Set, Tuple
from pathlib import Path

from code2llm.core.models import AnalysisResult

from .utils import readable_id, safe_module, resolve_callee, write_file, build_name_index


def export_calls(result: AnalysisResult, output_path: str) -> None:
    """Export simplified call graph — only connected nodes."""
    lines = ["flowchart LR"]

    # Build name index for O(1) callee resolution
    name_index = build_name_index(result.functions)

    # Collect connected nodes first
    connected: Set[str] = set()
    edges: List[Tuple[str, str]] = []
    for func_name, fi in result.functions.items():
        for callee in fi.calls[:10]:
            resolved = resolve_callee(callee, result.functions, name_index)
            if resolved and resolved != func_name:
                connected.add(func_name)
                connected.add(resolved)
                edges.append((func_name, resolved))
                if len(edges) >= 500:
                    break
        if len(edges) >= 500:
            break

    # Group connected nodes by module
    from .utils import module_of
    modules: Dict[str, list] = {}
    for fn in connected:
        module = module_of(fn)
        fi = result.functions.get(fn)
        if fi:
            modules.setdefault(module, []).append((fn, fi))

    for module, funcs in sorted(modules.items()):
        safe_mod = safe_module(module)
        lines.append(f"    subgraph {safe_mod}")
        for func_name, fi in funcs:
            sid = readable_id(func_name)
            short = fi.name[:30]
            lines.append(f'        {sid}["{short}"]')
        lines.append("    end")

    # Edges
    seen: Set[Tuple[str, str]] = set()
    for src, dst in edges:
        pair = (readable_id(src), readable_id(dst))
        if pair not in seen:
            seen.add(pair)
            lines.append(f"    {pair[0]} --> {pair[1]}")

    write_file(output_path, lines)


__all__ = ['export_calls']
