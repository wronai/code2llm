"""Map Exporter — generates map.toon (structural map).

Produces a compact project header plus a key:value structural map showing
modules, imports, exports, and signatures.

Purpose: "what exists and how it's connected"
Format: header summary + M[] module list, D: details with i: imports,
e: exports, signatures
"""

from collections import defaultdict
from datetime import datetime
import re
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
    """Export to map.toon — structural map with a compact project header.

    Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions,
    m=methods
    """

    def export(self, result: AnalysisResult, output_path: str, **kwargs) -> None:
        """Export analysis result to .map format."""
        lines: List[str] = []
        lines.extend(self._render_header(result, output_path))
        lines.extend(self._render_module_list(result))
        lines.extend(self._render_details(result))

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    # ------------------------------------------------------------------
    # header
    # ------------------------------------------------------------------
    def _render_header(self, result: AnalysisResult, output_path: str) -> List[str]:
        project_name = Path(result.project_path).name if result.project_path else "project"
        total_lines = self._count_total_lines(result)
        langs = self._detect_languages(result)
        lang_str = ",".join(f"{lang}:{count}" for lang, count in langs.items()) or "unknown"

        included_files = [mi for mi in result.modules.values() if not self._is_excluded(mi.file)]
        included_funcs = [fi for fi in result.functions.values() if not self._is_excluded(fi.file)]
        included_classes = [ci for ci in result.classes.values() if not self._is_excluded(ci.file)]

        cc_scores = [fi.complexity.get("cyclomatic_complexity", 0) for fi in included_funcs]
        avg_cc = round(sum(cc_scores) / len(cc_scores), 1) if cc_scores else 0.0
        critical_count = len([cc for cc in cc_scores if cc >= 15])
        cycles = len(result.metrics.get("project", {}).get("circular_dependencies", []))

        alerts = self._build_alerts(included_funcs)
        hotspots = self._build_hotspots(included_funcs)
        trend = self._load_evolution_trend(Path(output_path).with_name("evolution.toon"), avg_cc)

        lines = [
            f"# {project_name} | {len(included_files)}f {total_lines}L | {lang_str} | {datetime.now().strftime('%Y-%m-%d')}",
            f"# stats: {len(included_funcs)} func | {len(included_classes)} cls | {len(included_files)} mod | CC̄={avg_cc} | critical:{critical_count} | cycles:{cycles}",
            f"# alerts[{len(alerts)}]: {'; '.join(alerts) if alerts else 'none'}",
            f"# hotspots[{len(hotspots)}]: {'; '.join(hotspots) if hotspots else 'none'}",
            f"# evolution: {trend}",
            "# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods",
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

    @staticmethod
    def _build_alerts(funcs: List[FunctionInfo]) -> List[str]:
        """Build a compact list of top alerts for the header."""
        alerts: List[Tuple[int, int, str]] = []
        for fi in funcs:
            display = fi.name if not fi.class_name else f"{fi.class_name}.{fi.name}"
            cc = fi.complexity.get("cyclomatic_complexity", 0)
            if cc >= 15:
                severity = 0 if cc >= 25 else 1
                alerts.append((severity, cc, f"CC {display}={cc}"))

            fan_out = len(set(fi.calls))
            if fan_out >= 10:
                severity = 0 if fan_out >= 20 else 1
                alerts.append((severity, fan_out, f"fan-out {display}={fan_out}"))

        alerts.sort(key=lambda item: (item[0], -item[1], item[2]))
        return [label for _, _, label in alerts[:5]]

    @staticmethod
    def _build_hotspots(funcs: List[FunctionInfo]) -> List[str]:
        """Build a compact list of top fan-out hotspots for the header."""
        spots: List[Tuple[int, str]] = []
        for fi in funcs:
            fan_out = len(set(fi.calls))
            if fan_out >= 5:
                display = fi.name if not fi.class_name else f"{fi.class_name}.{fi.name}"
                spots.append((fan_out, f"{display} fan={fan_out}"))

        spots.sort(key=lambda item: item[0], reverse=True)
        return [label for _, label in spots[:5]]

    @staticmethod
    def _load_evolution_trend(evolution_path: Path, current_cc: float) -> str:
        """Summarize the latest CC trend from the previous evolution.toon file."""
        previous_cc = MapExporter._read_previous_cc_avg(evolution_path)
        if previous_cc is None:
            return "baseline"

        delta = round(current_cc - previous_cc, 1)
        if delta < 0:
            direction = "improved"
        elif delta > 0:
            direction = "regressed"
        else:
            direction = "flat"

        sign = "+" if delta > 0 else ""
        return f"CC̄ {previous_cc:.1f}→{current_cc:.1f} ({direction} {sign}{delta:.1f})"

    @staticmethod
    def _read_previous_cc_avg(evolution_path: Path) -> Optional[float]:
        """Read the previous CC average from an existing evolution.toon file."""
        if not evolution_path.exists():
            return None

        try:
            content = evolution_path.read_text(encoding="utf-8")
        except Exception:
            return None

        for line in content.splitlines():
            match = re.search(r"CC̄:\s*([0-9]+(?:\.[0-9]+)?)\s*→", line)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    return None
        return None
