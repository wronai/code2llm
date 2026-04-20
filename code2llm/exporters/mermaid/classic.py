"""Mermaid classic export — flow.mmd full graph with CC styling."""

from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path

from code2llm.core.models import AnalysisResult

from .utils import readable_id, safe_module, resolve_callee, write_file, get_cc, build_name_index


def export_classic(result: AnalysisResult, output_path: str) -> Optional[Path]:
    """Export full flow diagram with CC-based node shapes and styling."""
    lines = ["flowchart TD"]

    # Build name index for O(1) callee resolution
    name_index = build_name_index(result.functions)

    # Subgraphs per module
    _render_subgraphs(result, lines)

    # Edges — all cross-function calls
    _render_edges(result, lines, name_index, limit=600)

    # CC-based styling
    _render_cc_styles(result, lines)

    return write_file(output_path, lines)


def _render_subgraphs(result: AnalysisResult, lines: List[str]) -> None:
    """Render module subgraphs with CC-shaped nodes."""
    from .utils import module_of
    modules: Dict[str, list] = {}
    for func_name, fi in result.functions.items():
        module = module_of(func_name)
        modules.setdefault(module, []).append((func_name, fi))

    for module, funcs in sorted(modules.items()):
        safe_mod = safe_module(module)
        lines.append(f"    subgraph {safe_mod}")
        for func_name, fi in funcs[:60]:
            sid = readable_id(func_name)
            short = fi.name[:35]
            cc = get_cc(fi)
            if cc >= 15:
                lines.append(f'        {sid}{{{{{short} CC={cc}}}}}')
            elif cc >= 8:
                lines.append(f'        {sid}("{short} CC={cc}")')
            else:
                lines.append(f'        {sid}["{short}"]')
        lines.append("    end")


def _render_edges(result: AnalysisResult, lines: List[str], name_index: Dict[str, List[str]], limit: int = 600) -> None:
    """Render cross-function call edges up to limit."""
    seen_edges: Set[Tuple[str, str]] = set()
    for func_name, fi in result.functions.items():
        src = readable_id(func_name)
        for callee in fi.calls[:15]:
            resolved = resolve_callee(callee, result.functions, name_index)
            if resolved and resolved != func_name:
                dst = readable_id(resolved)
                edge = (src, dst)
                if edge not in seen_edges:
                    seen_edges.add(edge)
                    lines.append(f"    {src} --> {dst}")
                    if len(seen_edges) >= limit:
                        return
        if len(seen_edges) >= limit:
            return


def _render_cc_styles(result: AnalysisResult, lines: List[str]) -> None:
    """Add CC-based class styling for high/medium complexity nodes."""
    lines.append("")
    lines.append("    classDef highCC fill:#ff6b6b,stroke:#c92a2a,color:#fff")
    lines.append("    classDef medCC fill:#ffd43b,stroke:#f08c00,color:#000")
    high_nodes = []
    med_nodes = []
    for func_name, fi in result.functions.items():
        cc = get_cc(fi)
        sid = readable_id(func_name)
        if cc >= 15:
            high_nodes.append(sid)
        elif cc >= 8:
            med_nodes.append(sid)
    if high_nodes:
        lines.append(f"    class {','.join(high_nodes[:30])} highCC")
    if med_nodes:
        lines.append(f"    class {','.join(med_nodes[:30])} medCC")


__all__ = ['export_classic']
