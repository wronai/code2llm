"""Map Exporter — generates map.toon (structural map).

Produces a compact key:value format showing modules, imports, signatures,
and type information. Formerly the project.toon format.

Purpose: "what exists and how it's connected"
Format: M[] module list, D: details with i: imports, e: exports, signatures
"""

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .base import Exporter
from ..core.models import AnalysisResult, FunctionInfo, ClassInfo, ModuleInfo
from ..core.config import LANGUAGE_EXTENSIONS

# Patterns to exclude (venv, site-packages, etc.)
EXCLUDE_PATTERNS = {
    'venv', '.venv', 'env', '.env', 'publish-env', 'test-env',
    'site-packages', 'node_modules', '__pycache__', '.git',
    'dist', 'build', 'egg-info', '.tox', '.mypy_cache',
}


class MapExporter(Exporter):
    """Export to map.toon — structural map with modules, imports, signatures.

    Keys: M=modules, D=details, i=imports, c=classes, f=functions, m=methods
    """

    def export(self, result: AnalysisResult, output_path: str, **kwargs) -> None:
        """Export analysis result to .map format."""
        lines: List[str] = []
        lines.extend(self._render_header(result))
        lines.extend(self._render_module_list(result))
        lines.extend(self._render_details(result))

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    # ------------------------------------------------------------------
    # header
    # ------------------------------------------------------------------
    def _render_header(self, result: AnalysisResult) -> List[str]:
        nfiles = len(result.modules)
        total_lines = self._count_total_lines(result)
        langs = self._detect_languages(result)
        lang_str = ",".join(f"{lang}:{count}" for lang, count in langs.items())

        lines = [
            f"# {Path(result.project_path).name if result.project_path else 'project'}"
            f" | {nfiles}f {total_lines}L | {lang_str}",
            "# Keys: M=modules, D=details, i=imports, c=classes, f=functions, m=methods",
        ]
        return lines

    # ------------------------------------------------------------------
    # M[] — module list with line counts
    # ------------------------------------------------------------------
    def _render_module_list(self, result: AnalysisResult) -> List[str]:
        modules = []
        for mname, mi in sorted(result.modules.items()):
            if self._is_excluded(mi.file):
                continue
            rel = self._rel_path(mi.file, result.project_path)
            lc = self._file_line_count(mi.file)
            modules.append((rel, lc))

        lines = [f"M[{len(modules)}]:"]
        for rel, lc in modules:
            lines.append(f"  {rel},{lc}")
        return lines

    # ------------------------------------------------------------------
    # D: — details per module
    # ------------------------------------------------------------------
    def _render_details(self, result: AnalysisResult) -> List[str]:
        lines = ["D:"]
        mod_items = self._rank_modules(result)
        for mname, mi, max_cc in mod_items:
            self._render_map_module(result, mi, lines)
        return lines

    def _rank_modules(self, result: AnalysisResult):
        """Sort modules by max CC desc, excluding excluded paths."""
        mod_items = []
        for mname, mi in result.modules.items():
            if self._is_excluded(mi.file):
                continue
            max_cc = 0.0
            for fq in mi.functions:
                fi = result.functions.get(fq)
                if fi:
                    cc = fi.complexity.get("cyclomatic_complexity", 0)
                    max_cc = max(max_cc, cc)
            mod_items.append((mname, mi, max_cc))
        mod_items.sort(key=lambda x: x[2], reverse=True)
        return mod_items

    def _render_map_module(self, result, mi, lines):
        """Render a single module's detail: imports, exports, classes, funcs."""
        rel = self._rel_path(mi.file, result.project_path)
        lines.append(f"  {rel}:")

        # imports
        if mi.imports:
            imp_str = ",".join(sorted(mi.imports))
            lines.append(f"    i: {imp_str}")

        # exports
        exports = []
        for cq in mi.classes:
            ci = result.classes.get(cq)
            if ci:
                exports.append(ci.name)
        for fq in mi.functions:
            fi = result.functions.get(fq)
            if fi and not fi.class_name:
                exports.append(fi.name)
        if exports:
            lines.append(f"    e: {','.join(exports)}")

        # classes with method signatures
        for cq in mi.classes:
            ci = result.classes.get(cq)
            if not ci:
                continue
            self._render_map_class(result, ci, lines)

        # standalone functions
        for fq in mi.functions:
            fi = result.functions.get(fq)
            if fi and not fi.class_name:
                sig = self._function_signature(fi)
                lines.append(f"    {sig}")

    def _render_map_class(self, result, ci, lines):
        """Render a single class with its method signatures."""
        doc = ""
        if ci.docstring:
            doc = f"  # {ci.docstring[:60].rstrip('.')}..."

        method_sigs = []
        for mq in ci.methods:
            fi = result.functions.get(mq)
            if fi:
                arity = len(fi.args) - (1 if fi.is_method else 0)
                method_sigs.append(f"{fi.name}({arity})")

        bases_str = ""
        if ci.bases:
            bases_str = f"({','.join(ci.bases)})"

        if method_sigs:
            lines.append(
                f"    {ci.name}{bases_str}: "
                f"{','.join(method_sigs)}{doc}"
            )
        else:
            lines.append(f"    {ci.name}{bases_str}:{doc}")

    # ------------------------------------------------------------------
    # utility helpers
    # ------------------------------------------------------------------
    def _function_signature(self, fi: FunctionInfo) -> str:
        """Build compact signature: name(arg:type;arg2:type)->ReturnType"""
        args_parts = []
        for arg in fi.args:
            if arg == "self":
                continue
            args_parts.append(arg)

        args_str = ";".join(args_parts) if args_parts else ""
        ret = ""
        if fi.returns:
            ret = f"->{fi.returns}"
        return f"{fi.name}({args_str}){ret}"

    def _is_excluded(self, path: str) -> bool:
        if not path:
            return False
        path_lower = path.lower().replace('\\', '/')
        for pattern in EXCLUDE_PATTERNS:
            if f'/{pattern}/' in path_lower or path_lower.startswith(f'{pattern}/'):
                return True
            if pattern in path_lower.split('/'):
                return True
        return False

    def _rel_path(self, fpath: str, project_path: str) -> str:
        if not project_path or not fpath:
            return fpath or ""
        try:
            return str(Path(fpath).relative_to(Path(project_path).resolve()))
        except (ValueError, RuntimeError):
            try:
                return str(Path(fpath).relative_to(Path(project_path)))
            except (ValueError, RuntimeError):
                return fpath

    def _file_line_count(self, fpath: str) -> int:
        try:
            return len(Path(fpath).read_text(encoding="utf-8", errors="ignore").splitlines())
        except Exception:
            return 0

    def _count_total_lines(self, result: AnalysisResult) -> int:
        total = 0
        seen = set()
        for mi in result.modules.values():
            if mi.file and mi.file not in seen and not self._is_excluded(mi.file):
                seen.add(mi.file)
                total += self._file_line_count(mi.file)
        return total

    def _detect_languages(self, result: AnalysisResult) -> Dict[str, int]:
        """Detect all supported programming languages in the project."""
        langs: Dict[str, int] = defaultdict(int)
        for mi in result.modules.values():
            if self._is_excluded(mi.file):
                continue
            # Check all supported language extensions
            detected = False
            for lang, extensions in LANGUAGE_EXTENSIONS.items():
                if any(mi.file.endswith(ext) for ext in extensions):
                    langs[lang] += 1
                    detected = True
                    break
            if not detected:
                # Fallback: try to detect from file extension
                ext = Path(mi.file).suffix.lower()
                if ext:
                    langs[ext.lstrip('.')] += 1
        return dict(langs)
