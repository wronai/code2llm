"""Module detail rendering for TOON exporter."""

from typing import Any, Dict, List, Tuple

from ...core.models import AnalysisResult, FunctionInfo, ClassInfo, ModuleInfo

from .helpers import _rel_path


# Constants
CC_WARNING = 15


class ModuleDetailRenderer:
    """Renders detailed module information."""
    
    def render_details(self, ctx: Dict[str, Any]) -> List[str]:
        """Render D: section — per-module details sorted by max CC desc."""
        result: AnalysisResult = ctx["result"]
        dup_classes = {d["class_name"] for d in ctx["duplicates"]}
        mod_items = self._rank_modules_by_cc(result)

        lines = ["D:"]
        for mname, mi, max_cc in mod_items:
            self._render_module_detail(result, mi, dup_classes, lines)
        return lines

    def _rank_modules_by_cc(self, result: AnalysisResult) -> List[Tuple[str, ModuleInfo, float]]:
        """Sort modules by max cyclomatic complexity (desc)."""
        mod_items = []
        for mname, mi in result.modules.items():
            max_cc = 0.0
            for fq in mi.functions:
                fi = result.functions.get(fq)
                if fi:
                    cc = fi.complexity.get("cyclomatic_complexity", 0)
                    max_cc = max(max_cc, cc)
            mod_items.append((mname, mi, max_cc))
        mod_items.sort(key=lambda x: x[2], reverse=True)
        return mod_items

    def _render_module_detail(self, result: AnalysisResult, mi: ModuleInfo, dup_classes: set, lines: List[str]) -> None:
        """Render detail for a single module: imports, exports, classes, funcs."""
        rel = _rel_path(mi.file, result.project_path)
        lines.append(f"  {rel}:")

        # imports
        if mi.imports:
            imp_str = ",".join(sorted(mi.imports))
            lines.append(f"    i: {imp_str}")

        # exports (classes + top-level functions)
        exports = self._get_module_exports(result, mi)
        if exports:
            lines.append(f"    e: {','.join(exports)}")

        # classes with methods
        self._render_module_classes(result, mi, dup_classes, lines)

        # standalone functions
        self._render_standalone_funcs(result, mi, lines)

    def _get_module_exports(self, result: AnalysisResult, mi: ModuleInfo) -> List[str]:
        """Get module exports (classes + top-level functions)."""
        exports = []
        for cq in mi.classes:
            ci = result.classes.get(cq)
            if ci:
                exports.append(ci.name)
        for fq in mi.functions:
            fi = result.functions.get(fq)
            if fi and not fi.class_name:
                exports.append(fi.name)
        return exports

    def _render_module_classes(self, result: AnalysisResult, mi: ModuleInfo, dup_classes: set, lines: List[str]) -> None:
        """Render classes with call chains within a module."""
        for cq in mi.classes:
            ci = result.classes.get(cq)
            if not ci:
                continue

            dup_mark = "  ×DUP" if ci.name in dup_classes else ""
            doc = ""
            if ci.docstring:
                doc = f"  # {ci.docstring[:60]}..."
            lines.append(f"    {ci.name}{dup_mark}{doc}")

            # method items for call chain
            method_items = self._get_method_items(result, ci)

            # find root method
            root_method = self._find_root_method(method_items)

            if root_method:
                self._render_call_chain(root_method, method_items, result, lines, "      ")

    def _get_method_items(self, result: AnalysisResult, ci: ClassInfo) -> List[Tuple[FunctionInfo, float, int]]:
        """Get method items for call chain rendering."""
        method_items = []
        for mq in ci.methods:
            fi = result.functions.get(mq)
            if fi:
                cc = fi.complexity.get("cyclomatic_complexity", 0)
                arity = len(fi.args) - (1 if fi.is_method else 0)
                method_items.append((fi, cc, arity))
        return method_items

    def _find_root_method(self, method_items: List[Tuple[FunctionInfo, float, int]]) -> FunctionInfo:
        """Find root method for call chain rendering."""
        # find root method
        root_method = None
        for fi, cc, arity in method_items:
            if fi.name == "__init__":
                root_method = fi
                break
        if not root_method and method_items:
            root_method = method_items[0][0]
        return root_method

    def _render_standalone_funcs(self, result: AnalysisResult, mi: ModuleInfo, lines: List[str]) -> None:
        """Render standalone (non-class) functions within a module."""
        for fq in mi.functions:
            fi = result.functions.get(fq)
            if fi and not fi.class_name:
                args_str = ",".join(
                    a for a in fi.args if a != "self"
                )
                ret = ""
                if fi.returns:
                    ret = f"->{fi.returns}"
                lines.append(f"    {fi.name}({args_str}){ret}")

    def _render_call_chain(
        self,
        root: FunctionInfo,
        method_items: List[Tuple[FunctionInfo, float, int]],
        result: AnalysisResult,
        lines: List[str],
        indent: str,
    ) -> None:
        """Render call chain for a class - shows method calls as a tree."""
        method_map = {fi.name: (fi, cc, arity) for fi, cc, arity in method_items}
        called = set()

        def render_method(fi: FunctionInfo, depth: int, prefix: str) -> None:
            cc = fi.complexity.get("cyclomatic_complexity", 0)
            arity = len(fi.args) - (1 if fi.is_method else 0)
            cc_marker = "  !" if cc >= CC_WARNING else ""
            lines.append(
                f"{indent}{prefix}{fi.name}({arity})  CC={cc:.1f}{cc_marker}"
            )
            if depth > 3:
                return
            for call in fi.calls:
                call_name = call.split(".")[-1] if "." in call else call
                if call_name in method_map and call_name not in called:
                    called.add(call_name)
                    child, _, _ = method_map[call_name]
                    render_method(child, depth + 1, "  → ")

        render_method(root, 0, "")
