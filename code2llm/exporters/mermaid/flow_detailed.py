"""Mermaid flow detailed export — flow_detailed.mmd per-module view (~150 nodes)."""

from pathlib import Path

from code2llm.core.models import AnalysisResult

from .utils import readable_id, safe_module, resolve_callee, write_file, get_cc, build_name_index
from ..mermaid_flow_helpers import (
    _entry_points,
    _filtered_functions,
    _group_functions_by_module,
    _render_module_subgraphs,
    _render_flow_edges,
    _render_flow_styles,
)
from .flow_compact import should_skip_module, is_entry_point


def export_flow_detailed(result: AnalysisResult, output_path: str,
                        include_examples: bool = False) -> None:
    """Export detailed per-module view (~150 nodes).

    Shows all significant functions per module with CC annotations.
    """
    from .utils import module_of

    lines = ["flowchart TD"]

    # Build name index for O(1) callee resolution
    name_index = build_name_index(result.functions)
    lines.append("")
    lines.append("    %% Styling definitions")
    lines.append("    classDef highCC fill:#ff6b6b,stroke:#c92a2a,color:#fff")
    lines.append("    classDef medCC fill:#ffd43b,stroke:#f08c00,color:#000")
    lines.append("    classDef entry fill:#4dabf7,stroke:#1971c2,color:#fff")
    lines.append("")
    filtered_funcs = _filtered_functions(
        result,
        module_of,
        should_skip_module,
        include_examples,
    )
    entry_points = _entry_points(filtered_funcs, result, is_entry_point)
    modules = _group_functions_by_module(filtered_funcs, module_of)
    _render_module_subgraphs(
        lines,
        modules,
        entry_points,
        short_len=35,
        readable_id=readable_id,
        safe_module=safe_module,
        get_cc=get_cc,
        sort_funcs=True,
        max_funcs=40,
    )
    _render_flow_edges(lines, filtered_funcs, readable_id, resolve_callee, calls_per_function=10, limit=200, name_index=name_index)
    _render_flow_styles(
        lines,
        filtered_funcs,
        entry_points,
        readable_id,
        get_cc,
        high_limit=30,
        med_limit=30,
        entry_limit=10,
    )
    write_file(output_path, lines)


__all__ = ['export_flow_detailed']
