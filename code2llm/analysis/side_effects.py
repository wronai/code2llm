"""Side-effect detector — AST-based side-effect classification.

Scans Python function bodies to detect:
- IO: open(), read(), write(), print(), file operations
- Cache: cache lookups/stores, memoization, lru_cache
- Mutation: self.x = ..., global, del, list.append/insert
- Pure: no detected side effects

Used by FlowExporter to enrich CONTRACTS and SIDE_EFFECTS sections.
"""

import ast
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from code2llm.core.models import FunctionInfo

logger = logging.getLogger(__name__)

# Side-effect classification patterns
IO_CALLS = frozenset({
    "open", "read", "write", "print", "input",
    "mkdir", "makedirs", "rmdir", "remove", "unlink", "rename",
    "read_text", "write_text", "read_bytes", "write_bytes",
    "dump", "dumps", "load", "loads",
    "save", "savefig",
    "send", "recv", "connect", "listen", "accept",
    "execute", "commit", "rollback",  # DB
})

# HTTP verbs — only IO when called on known HTTP objects (requests.get, session.post)
HTTP_METHODS = frozenset({"get", "post", "put", "delete", "patch"})
HTTP_CALLERS = frozenset({
    "requests", "session", "client", "http", "aiohttp",
    "httpx", "urllib", "conn", "api", "resp", "response",
})

IO_ATTRIBUTES = frozenset({
    "write", "read", "readline", "readlines", "writelines",
    "flush", "close", "seek", "tell",
    "send", "recv", "sendall",
})

CACHE_INDICATORS = frozenset({
    "cache", "lru_cache", "memoize", "cached_property",
    "Cache", "FileCache",
})

CACHE_CALLS = frozenset({
    "cache_get", "cache_set", "cache_delete", "cache_clear",
    "get_cached", "set_cached",
})

MUTATION_CALLS = frozenset({
    "append", "extend", "insert", "pop", "remove", "clear",
    "update", "setdefault", "add", "discard",
    "sort", "reverse",
})


class SideEffectInfo:
    """Side-effect analysis result for a single function."""

    __slots__ = (
        "function_name", "qualified_name", "classification",
        "io_operations", "cache_operations", "mutations",
        "global_refs", "self_mutations", "has_yield",
    )

    def __init__(self, function_name: str, qualified_name: str):
        self.function_name = function_name
        self.qualified_name = qualified_name
        self.classification: str = "pure"  # pure | IO | cache | mutation
        self.io_operations: List[str] = []
        self.cache_operations: List[str] = []
        self.mutations: List[str] = []
        self.global_refs: List[str] = []
        self.self_mutations: List[str] = []
        self.has_yield: bool = False

    @property
    def is_pure(self) -> bool:
        return self.classification == "pure"

    @property
    def side_effect_summary(self) -> str:
        """One-line summary of side effects."""
        parts = []
        if self.io_operations:
            parts.append(f"IO({', '.join(self.io_operations[:3])})")
        if self.cache_operations:
            parts.append(f"cache({', '.join(self.cache_operations[:2])})")
        if self.self_mutations:
            parts.append(f"mutates self.{', self.'.join(self.self_mutations[:3])}")
        if self.global_refs:
            parts.append(f"global({', '.join(self.global_refs[:2])})")
        if self.has_yield:
            parts.append("generator")
        return "; ".join(parts) if parts else "pure"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "function": self.function_name,
            "qualified_name": self.qualified_name,
            "classification": self.classification,
            "io": self.io_operations,
            "cache": self.cache_operations,
            "mutations": self.mutations,
            "globals": self.global_refs,
            "self_mutations": self.self_mutations,
            "has_yield": self.has_yield,
            "summary": self.side_effect_summary,
        }


class SideEffectDetector:
    """Detect side effects in Python functions via AST analysis.

    Scans function bodies for IO operations, cache usage, mutations,
    global references, and self-attribute mutations.
    """

    def __init__(self):
        self._ast_cache: Dict[str, Optional[ast.Module]] = {}

    def analyze_function(self, fi: FunctionInfo) -> SideEffectInfo:
        """Analyze a single function for side effects."""
        info = SideEffectInfo(fi.name, fi.qualified_name)

        tree = self._get_ast(fi.file)
        if tree:
            node = self._find_function_node(tree, fi.name, fi.line)
            if node:
                self._scan_node(node, info)
                self._classify(info)
                return info

        # Fallback: heuristic from function name and calls
        self._heuristic_classify(fi, info)
        return info

    def analyze_all(
        self, funcs: Dict[str, FunctionInfo]
    ) -> Dict[str, SideEffectInfo]:
        """Batch-analyze all functions for side effects."""
        results: Dict[str, SideEffectInfo] = {}
        for qname, fi in funcs.items():
            results[qname] = self.analyze_function(fi)
        return results

    def get_purity_score(self, fi: FunctionInfo) -> str:
        """Get purity classification: pure | IO | cache | mutation."""
        return self.analyze_function(fi).classification

    # ------------------------------------------------------------------
    # AST scanning
    # ------------------------------------------------------------------
    def _scan_node(self, func_node: ast.FunctionDef, info: SideEffectInfo) -> None:
        """Walk function body and detect side-effect patterns."""
        for node in ast.walk(func_node):
            self._check_calls(node, info)
            self._check_assignments(node, info)
            self._check_globals(node, info)
            self._check_yield(node, info)
            self._check_delete(node, info)

    def _check_calls(self, node: ast.AST, info: SideEffectInfo) -> None:
        """Detect IO and cache calls."""
        if not isinstance(node, ast.Call):
            return

        call_name = self._get_call_name(node.func)
        if not call_name:
            return

        parts = call_name.split(".")
        base_name = parts[-1]

        # IO detection
        if base_name in IO_CALLS:
            info.io_operations.append(base_name)
        elif base_name in HTTP_METHODS and len(parts) >= 2:
            # Only classify as IO if caller looks like HTTP client
            caller = parts[-2].lower()
            if caller in HTTP_CALLERS:
                info.io_operations.append(call_name)
        elif base_name in IO_ATTRIBUTES:
            info.io_operations.append(call_name)

        # Cache detection
        if base_name in CACHE_CALLS:
            info.cache_operations.append(base_name)
        elif any(ci in call_name for ci in CACHE_INDICATORS):
            info.cache_operations.append(call_name)

        # Mutation via method calls (e.g., list.append)
        if base_name in MUTATION_CALLS and len(parts) >= 2:
            info.mutations.append(call_name)

    def _check_assignments(self, node: ast.AST, info: SideEffectInfo) -> None:
        """Detect self.x = ... and augmented assignments."""
        if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            targets = []
            if isinstance(node, ast.Assign):
                targets = node.targets
            elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
                targets = [node.target]

            for target in targets:
                if isinstance(target, ast.Attribute):
                    if isinstance(target.value, ast.Name) and target.value.id == "self":
                        info.self_mutations.append(target.attr)

    def _check_globals(self, node: ast.AST, info: SideEffectInfo) -> None:
        """Detect global/nonlocal references."""
        if isinstance(node, ast.Global):
            info.global_refs.extend(node.names)
        elif isinstance(node, ast.Nonlocal):
            info.global_refs.extend(node.names)

    def _check_yield(self, node: ast.AST, info: SideEffectInfo) -> None:
        """Detect generator functions."""
        if isinstance(node, (ast.Yield, ast.YieldFrom)):
            info.has_yield = True

    def _check_delete(self, node: ast.AST, info: SideEffectInfo) -> None:
        """Detect del statements on attributes."""
        if isinstance(node, ast.Delete):
            for target in node.targets:
                if isinstance(target, ast.Attribute):
                    if isinstance(target.value, ast.Name) and target.value.id == "self":
                        info.self_mutations.append(f"del:{target.attr}")

    # ------------------------------------------------------------------
    # classification
    # ------------------------------------------------------------------
    def _classify(self, info: SideEffectInfo) -> None:
        """Classify function based on detected side effects."""
        # Priority: IO > cache > mutation > pure
        if info.io_operations:
            info.classification = "IO"
        elif info.cache_operations:
            info.classification = "cache"
        elif info.self_mutations or info.mutations or info.global_refs:
            info.classification = "mutation"
        else:
            info.classification = "pure"

    def _heuristic_classify(
        self, fi: FunctionInfo, info: SideEffectInfo
    ) -> None:
        """Classify based on function name and calls (fallback)."""
        name_lower = fi.name.lower()
        calls_lower = {c.lower() for c in fi.calls}

        io_words = {"write", "read", "open", "save", "load", "export",
                     "dump", "print", "mkdir", "rmdir", "remove"}
        cache_words = {"cache", "memoize", "lru_cache", "store", "fetch"}
        mutation_words = {"set_", "update", "modify", "mutate", "append",
                          "insert", "delete", "fix", "patch"}

        if any(w in name_lower for w in io_words):
            info.classification = "IO"
            info.io_operations.append(f"name:{fi.name}")
        elif any(any(w in c for w in io_words) for c in calls_lower):
            info.classification = "IO"
            info.io_operations.append("calls:IO")
        elif any(w in name_lower for w in cache_words):
            info.classification = "cache"
            info.cache_operations.append(f"name:{fi.name}")
        elif any(any(w in c for w in cache_words) for c in calls_lower):
            info.classification = "cache"
            info.cache_operations.append("calls:cache")
        elif any(w in name_lower for w in mutation_words):
            info.classification = "mutation"
            info.mutations.append(f"name:{fi.name}")
        else:
            info.classification = "pure"

    # ------------------------------------------------------------------
    # AST helpers
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
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == name:
                    return node
        return None

    def _get_call_name(self, node: ast.expr) -> Optional[str]:
        """Extract call name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            value = self._get_call_name(node.value)
            if value:
                return f"{value}.{node.attr}"
            return node.attr
        return None
