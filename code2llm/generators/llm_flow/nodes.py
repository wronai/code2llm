"""LLM Flow node collection — collect and analyze CFG nodes."""

from collections import defaultdict
from typing import Any, Dict, List, Optional, Set

from .parsing import _parse_func_label


def _collect_nodes(analysis: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
    """Collect and parse nodes from analysis dict, keyed by node ID."""
    nodes = analysis.get("nodes")
    if not isinstance(nodes, dict):
        return {}

    parsed: Dict[int, Dict[str, Any]] = {}
    for k, v in nodes.items():
        try:
            node_id = int(k)
        except Exception:
            continue
        if isinstance(v, dict):
            parsed[node_id] = v
    return parsed


def _group_nodes_by_file(nodes: Dict[int, Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group nodes by their source file."""
    by_file: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for n in nodes.values():
        f = n.get("file")
        if isinstance(f, str):
            by_file[f].append(n)
    return by_file


def _is_entrypoint_file(filepath: str) -> bool:
    """Check if file is a potential entrypoint (main or CLI)."""
    return filepath.endswith("__main__.py") or filepath.endswith("cli.py")


def _extract_entrypoint_info(node: Dict[str, Any], filepath: str) -> Optional[Dict[str, Any]]:
    """Extract entrypoint info from a node if it's a function."""
    if node.get("type") != "FUNC" or not isinstance(node.get("function"), str):
        return None
    return {
        "kind": "cli" if filepath.endswith("cli.py") else "module_main",
        "file": filepath,
        "function": node.get("function"),
        "line": node.get("line"),
    }


def _deduplicate_entrypoints(entrypoints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate entrypoints by function name."""
    uniq: Dict[str, Dict[str, Any]] = {}
    for ep in entrypoints:
        key = str(ep.get("function") or "")
        if key and key not in uniq:
            uniq[key] = ep
    return list(uniq.values())


def _collect_entrypoints(nodes: Dict[int, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find entrypoint functions (main, CLI handlers)."""
    by_file = _group_nodes_by_file(nodes)
    
    entrypoints: List[Dict[str, Any]] = []
    for f, ns in by_file.items():
        if not _is_entrypoint_file(f):
            continue
        for n in ns:
            ep_info = _extract_entrypoint_info(n, f)
            if ep_info:
                entrypoints.append(ep_info)
    
    return _deduplicate_entrypoints(entrypoints)


def _collect_functions(nodes: Dict[int, Dict[str, Any]]) -> Set[str]:
    """Collect all function names from nodes."""
    out: Set[str] = set()
    for n in nodes.values():
        if n.get("type") != "FUNC":
            continue
        fn = n.get("function")
        if isinstance(fn, str) and fn:
            out.add(fn)
        else:
            parsed = _parse_func_label(str(n.get("label") or ""))
            if parsed:
                out.add(parsed)
    return out


__all__ = [
    '_collect_nodes',
    '_group_nodes_by_file',
    '_is_entrypoint_file',
    '_extract_entrypoint_info',
    '_deduplicate_entrypoints',
    '_collect_entrypoints',
    '_collect_functions',
]
