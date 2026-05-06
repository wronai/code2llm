"""Mermaid flow compact export — flow.mmd architectural view (~50 nodes)."""

from collections import defaultdict
from typing import Dict, List, Set

from code2llm.core.models import AnalysisResult

from .utils import readable_id, resolve_callee, write_file, get_cc, build_name_index


# Default skip patterns for noise reduction
SKIP_PATTERNS = ('examples', 'benchmarks', 'demo_langs', 'tests', 'scripts')


def should_skip_module(module: str, include_examples: bool = False) -> bool:
    """Check if module should be skipped (examples, benchmarks, etc.)."""
    if include_examples:
        return False
    mod_lower = module.lower()
    return any(pat in mod_lower for pat in SKIP_PATTERNS)


# Pre-computed set of functions that have at least one incoming call
_called_funcs_cache: Dict[int, Set[str]] = {}


def _get_called_funcs(result: AnalysisResult) -> Set[str]:
    """Build (and cache) the set of all functions called by other functions."""
    rid = id(result)
    if rid not in _called_funcs_cache:
        called: Set[str] = set()
        for fi in result.functions.values():
            called.update(fi.calls)
        _called_funcs_cache[rid] = called
    return _called_funcs_cache[rid]


def is_entry_point(func_name: str, fi, result: AnalysisResult) -> bool:
    """Detect if function is an entry point (main, cli, api entry)."""
    name = fi.name
    # Common entry point patterns
    if name in ('main', 'cli_main', 'run', 'start', 'serve'):
        return True
    if name.startswith('main_') or name.endswith('_main'):
        return True
    # CLI commands
    if 'cli' in func_name.lower() and name not in ('__init__', 'create_parser'):
        return True
    # API handlers
    if func_name.startswith('code2llm.api.'):
        return True
    # Entry points have no incoming calls from within the project
    called_funcs = _get_called_funcs(result)
    if func_name not in called_funcs and name not in ('__init__', '__getattr__'):
        return True
    return False


def build_callers_graph(result: AnalysisResult, name_index: Dict[str, List[str]]) -> Dict[str, Set[str]]:
    """Build reverse graph: map each function to its callers."""
    callers: Dict[str, Set[str]] = defaultdict(set)
    for func_name, fi in result.functions.items():
        for callee in fi.calls:
            resolved = resolve_callee(callee, result.functions, name_index)
            if resolved:
                callers[resolved].add(func_name)
    return callers


def find_leaves(result: AnalysisResult, name_index: Dict[str, List[str]]) -> Set[str]:
    """Find leaf nodes (functions that don't call other project functions)."""
    leaves = set()
    for func_name, fi in result.functions.items():
        has_internal_call = any(
            resolve_callee(c, result.functions, name_index) for c in fi.calls
        )
        if not has_internal_call:
            leaves.add(func_name)
    return leaves


def _longest_path_dfs(result: AnalysisResult, start: str, visited: Set[str], name_index: Dict[str, List[str]]) -> List[str]:
    """DFS to find longest path from start node."""
    if start in visited:
        return []
    visited = visited | {start}
    fi = result.functions.get(start)
    if not fi:
        return [start]

    longest: List[str] = []
    for callee in fi.calls:
        resolved = resolve_callee(callee, result.functions, name_index)
        if resolved and resolved not in visited:
            path = _longest_path_dfs(result, resolved, visited, name_index)
            if len(path) > len(longest):
                longest = path

    return [start] + longest


def _select_longest_path(result: AnalysisResult, entry_points: List[str], name_index: Dict[str, List[str]]) -> List[str]:
    """Select the longest path from all entry points."""
    max_path: List[str] = []
    for ep in entry_points:
        if ep in result.functions:
            path = _longest_path_dfs(result, ep, set(), name_index)
            if len(path) > len(max_path):
                max_path = path
    return max_path


def find_critical_path(result: AnalysisResult, entry_points: List[str]) -> Set[str]:
    """Find the longest path from entry points (critical path)."""
    if not entry_points:
        return set()
    # Build name index for O(1) resolution
    name_index = build_name_index(result.functions)
    # Build data structures
    build_callers_graph(result, name_index)
    find_leaves(result, name_index)
    # Find longest path from each entry point
    max_path = _select_longest_path(result, entry_points, name_index)
    return set(max_path)


def export_flow_compact(result: AnalysisResult, output_path: str,
                       include_examples: bool = False) -> None:
    """Export compact architectural view (~50 nodes).

    Shows entry points, high-level modules, and critical path.
    """
    from ..mermaid_flow_helpers import (
        _entry_points,
        _filtered_functions,
        _render_architecture_view,
    )
    from .utils import module_of

    lines = ["flowchart TD"]
    lines.append("")
    lines.append("    %% Entry points (blue)")
    lines.append("    classDef entry fill:#4dabf7,stroke:#1971c2,color:#fff")
    lines.append("")
    filtered_funcs = _filtered_functions(
        result,
        module_of,
        should_skip_module,
        include_examples,
    )
    entry_points = _entry_points(filtered_funcs, result, is_entry_point)
    critical_path = find_critical_path(result, entry_points)
    _render_architecture_view(
        lines,
        filtered_funcs,
        entry_points,
        critical_path,
        module_of,
        readable_id,
        get_cc,
    )
    write_file(output_path, lines)


__all__ = [
    'export_flow_compact',
    'should_skip_module',
    'is_entry_point',
    'find_critical_path',
]
