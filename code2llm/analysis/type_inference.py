"""Type inference engine — extracts type annotations from AST.

Parses Python source files to extract:
- Return type annotations (-> Type)
- Argument type hints (arg: Type)
- Fallback: infer types from function name patterns

Used by FlowExporter to enrich CONTRACTS and DATA_TYPES sections.
"""

import ast
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from code2llm.core.models import FunctionInfo

logger = logging.getLogger(__name__)

# Arg name substring -> inferred type (checked in order)
ARG_NAME_TYPE_MAP = [
    ("path", "Path"),
    ("name", "str"),
    ("text", "str"),
    ("config", "Config"),
    ("result", "AnalysisResult"),
]

# Name pattern -> (consumed types, produced types)
NAME_PATTERNS: List[Tuple[List[str], List[str], List[str]]] = [
    # (name_contains, consumed, produced)
    (["analyze", "file"], ["Path"], ["AnalysisResult"]),
    (["analyze", "project"], ["Path"], ["AnalysisResult"]),
    (["parse"], ["str"], ["dict"]),
    (["to_dict"], [], ["dict"]),
    (["to_json"], [], ["str"]),
    (["to_string", "to_str", "__str__", "__repr__"], [], ["str"]),
    (["from_dict"], ["dict"], []),
    (["from_json"], ["str"], []),
    (["normalize"], ["str"], ["str"]),
    (["tokenize"], ["str"], ["list"]),
    (["match_intent"], ["str"], ["IntentMatch"]),
    (["resolve"], ["IntentMatch"], ["Entity"]),
    (["detect_smell", "detect_smells"], ["AnalysisResult"], ["CodeSmell"]),
    (["export"], ["AnalysisResult"], []),
    (["render"], ["dict"], ["str"]),
    (["format"], ["str"], ["str"]),
    (["load", "read_file"], ["Path"], []),
    (["save", "write_file"], [], []),
    (["collect_files", "find_files", "glob"], ["Path"], ["list"]),
    (["merge"], ["list"], []),
    (["build_call_graph", "build_graph"], ["AnalysisResult"], ["AnalysisResult"]),
    (["compute_metrics"], ["AnalysisResult"], ["dict"]),
]


class TypeInferenceEngine:
    """Extract and infer type information from Python source files.

    Operates on source files referenced by FunctionInfo objects to extract
    type annotations that the core analyzer doesn't capture.
    """

    def __init__(self):
        self._ast_cache: Dict[str, Optional[ast.Module]] = {}

    def enrich_function(self, fi: FunctionInfo) -> Dict[str, Any]:
        """Extract full type info for a function.

        Returns dict with:
            args: list of {name, type, has_default}
            returns: str or None
            source: 'annotation' | 'inferred' | 'none'
        """
        tree = self._get_ast(fi.file)
        if tree:
            node = self._find_function_node(tree, fi.name, fi.line)
            if node:
                return self._extract_from_node(node, fi)

        # Fallback to name-based inference
        return self._infer_from_name(fi)

    def get_arg_types(self, fi: FunctionInfo) -> List[Dict[str, str]]:
        """Get typed argument list for a function."""
        info = self.enrich_function(fi)
        return info.get("args", [])

    def get_return_type(self, fi: FunctionInfo) -> Optional[str]:
        """Get return type for a function."""
        info = self.enrich_function(fi)
        return info.get("returns")

    def get_typed_signature(self, fi: FunctionInfo) -> str:
        """Build a compact typed signature: name(arg:Type, ...) -> ReturnType"""
        info = self.enrich_function(fi)
        args = info.get("args", [])
        ret = info.get("returns")

        parts = []
        for a in args:
            if a["name"] == "self":
                continue
            if a["type"]:
                parts.append(f"{a['name']}:{a['type']}")
            else:
                parts.append(a["name"])

        sig = f"{fi.name}({', '.join(parts)})"
        if ret:
            sig += f" \u2192 {ret}"
        return sig

    def extract_all_types(
        self, funcs: Dict[str, FunctionInfo]
    ) -> Dict[str, Dict[str, Any]]:
        """Batch-extract type info for all functions.

        Returns {qualified_name: type_info_dict}.
        """
        results: Dict[str, Dict[str, Any]] = {}
        for qname, fi in funcs.items():
            results[qname] = self.enrich_function(fi)
        return results

    # ------------------------------------------------------------------
    # AST extraction
    # ------------------------------------------------------------------
    def _get_ast(self, file_path: str) -> Optional[ast.Module]:
        """Parse and cache AST for a source file."""
        if not file_path:
            return None
        if file_path in self._ast_cache:
            return self._ast_cache[file_path]

        try:
            source = Path(file_path).read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=file_path)
            self._ast_cache[file_path] = tree
        except (OSError, SyntaxError) as e:
            logger.debug("Cannot parse %s: %s", file_path, e)
            self._ast_cache[file_path] = None
            tree = None
        return tree

    def _find_function_node(
        self, tree: ast.Module, name: str, line: int
    ) -> Optional[ast.FunctionDef]:
        """Find function node by name and line number."""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == name and node.lineno == line:
                    return node
        # Fallback: match by name only (first match)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == name:
                    return node
        return None

    def _extract_from_node(
        self, node: ast.FunctionDef, fi: FunctionInfo
    ) -> Dict[str, Any]:
        """Extract type annotations from an AST function node."""
        args = self._extract_args(node)
        returns = self._annotation_to_str(node.returns) if node.returns else None

        has_annotations = returns is not None or any(a["type"] for a in args)

        if has_annotations:
            source = "annotation"
        else:
            # Try name-based inference to fill gaps
            inferred = self._infer_from_name(fi)
            if inferred["source"] == "inferred":
                # Merge: keep annotations where available, fill with inferred
                if not returns and inferred["returns"]:
                    returns = inferred["returns"]
                    source = "mixed"
                else:
                    source = "annotation"
            else:
                source = "none"

        return {
            "args": args,
            "returns": returns,
            "source": source,
            "name": fi.name,
            "qualified_name": fi.qualified_name,
        }

    def _extract_args(self, node: ast.FunctionDef) -> List[Dict[str, str]]:
        """Extract typed arguments from function definition."""
        result = []
        defaults_offset = len(node.args.args) - len(node.args.defaults)

        for i, arg in enumerate(node.args.args):
            type_str = self._annotation_to_str(arg.annotation) if arg.annotation else None
            has_default = i >= defaults_offset
            result.append({
                "name": arg.arg,
                "type": type_str,
                "has_default": has_default,
            })

        # *args
        if node.args.vararg:
            va = node.args.vararg
            type_str = self._annotation_to_str(va.annotation) if va.annotation else None
            result.append({
                "name": f"*{va.arg}",
                "type": type_str,
                "has_default": False,
            })

        # **kwargs
        if node.args.kwarg:
            kw = node.args.kwarg
            type_str = self._annotation_to_str(kw.annotation) if kw.annotation else None
            result.append({
                "name": f"**{kw.arg}",
                "type": type_str,
                "has_default": False,
            })

        return result

    def _annotation_to_str(self, node: Optional[ast.expr]) -> Optional[str]:
        """Convert an annotation AST node to string."""
        if node is None:
            return None

        handler = self._ANNOTATION_HANDLERS.get(type(node))
        if handler:
            return handler(self, node)

        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            return self._ann_binop(node)

        try:
            return ast.unparse(node)
        except (AttributeError, ValueError):
            return None

    def _ann_constant(self, node: ast.Constant) -> str:
        return str(node.value)

    def _ann_name(self, node: ast.Name) -> str:
        return node.id

    def _ann_attribute(self, node: ast.Attribute) -> str:
        value = self._annotation_to_str(node.value)
        return f"{value}.{node.attr}" if value else node.attr

    def _ann_subscript(self, node: ast.Subscript) -> Optional[str]:
        base = self._annotation_to_str(node.value)
        slice_str = self._annotation_to_str(node.slice)
        return f"{base}[{slice_str}]" if (base and slice_str) else base

    def _ann_tuple(self, node: ast.Tuple) -> str:
        parts = [self._annotation_to_str(e) for e in node.elts]
        return ", ".join(p for p in parts if p)

    def _ann_binop(self, node: ast.BinOp) -> Optional[str]:
        left = self._annotation_to_str(node.left)
        right = self._annotation_to_str(node.right)
        return f"{left} | {right}" if (left and right) else None

    _ANNOTATION_HANDLERS = {
        ast.Constant: _ann_constant,
        ast.Name: _ann_name,
        ast.Attribute: _ann_attribute,
        ast.Subscript: _ann_subscript,
        ast.Tuple: _ann_tuple,
    }

    # ------------------------------------------------------------------
    # name-based inference (fallback)
    # ------------------------------------------------------------------
    def _infer_from_name(self, fi: FunctionInfo) -> Dict[str, Any]:
        """Infer types from function name patterns."""
        name_lower = fi.name.lower()
        consumed: List[str] = []
        produced: List[str] = []

        for patterns, cons, prod in NAME_PATTERNS:
            if any(p in name_lower for p in patterns):
                consumed.extend(cons)
                produced.extend(prod)
                break

        # Build arg list with inferred types
        args = [
            {"name": a, "type": self._infer_arg_type(a, consumed), "has_default": False}
            for a in fi.args
        ]

        ret = produced[0] if produced else None
        has_any = ret is not None or any(a["type"] for a in args)

        return {
            "args": args,
            "returns": ret,
            "source": "inferred" if has_any else "none",
            "name": fi.name,
            "qualified_name": fi.qualified_name,
        }

    @staticmethod
    def _infer_arg_type(arg_name: str, consumed: List[str]) -> Optional[str]:
        """Infer type for a single argument from consumed types or name patterns."""
        if arg_name == "self":
            return None
        if consumed:
            return consumed[0]
        arg_lower = arg_name.lower()
        for pattern, typ in ARG_NAME_TYPE_MAP:
            if pattern in arg_lower:
                return typ
        return None
