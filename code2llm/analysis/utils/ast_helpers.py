"""Shared AST utility functions — eliminate duplicated _get_ast / _find_function_node
across side_effects.py, type_inference.py, call_graph.py, cfg.py, dfg.py."""

import ast
from typing import Optional

from code2llm.core.ast_registry import ASTRegistry


def get_ast(filepath: str,
            registry: Optional[ASTRegistry] = None) -> Optional[ast.Module]:
    """Return parsed AST for *filepath* using the shared registry.

    Falls back to process-wide singleton when no registry is supplied.
    """
    reg = registry or ASTRegistry.get_global()
    return reg.get_ast(filepath)


def find_function_node(
    tree: ast.Module,
    name: str,
    line: int,
) -> Optional[ast.FunctionDef]:
    """Locate a function/async-function node by name and line number.

    First pass: exact name + line match.
    Second pass: first node whose name matches (fallback for out-of-sync lines).
    """
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == name and node.lineno == line:
                return node
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == name:
                return node
    return None


def ast_unparse(node: Optional[ast.AST], default_none: str = "None") -> str:
    """Convert an AST node to its source string via ast.unparse (Python 3.9+).

    Used as a shared replacement for the duplicated *_expr_to_str* methods
    in ``cfg.py``, ``dfg.py``, and ``call_graph.py``.

    Args:
        node: AST node to convert, or None.
        default_none: value returned when *node* is None (``"None"`` for most
            callers; ``""`` for call_graph which uses empty-string sentinel).
    """
    if node is None:
        return default_none
    try:
        return ast.unparse(node) if hasattr(ast, "unparse") else str(node)
    except Exception:
        return str(node)


def expr_to_str(node: ast.expr) -> Optional[str]:
    """Convert an AST expression to a dotted string (for call-name extraction).

    Handles ``ast.Name`` (``foo``) and ``ast.Attribute`` (``obj.method``).
    Returns *None* for unsupported node types.
    """
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        value = expr_to_str(node.value)
        if value:
            return f"{value}.{node.attr}"
        return node.attr
    return None
