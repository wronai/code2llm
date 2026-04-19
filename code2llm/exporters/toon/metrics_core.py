"""Core metrics computation for TOON export.

File-level, package-level, function-level, and class-level metrics,
plus coupling matrix and fan-in computation.
"""

from collections import defaultdict
from typing import Any, Dict, List, Tuple, Optional

from code2llm.core.models import AnalysisResult, FunctionInfo

from .helpers import _is_excluded, _rel_path, _package_of, _package_of_module


class CoreMetricsComputer:
    """Computes core structural and complexity metrics."""

    def __init__(self, line_counts: Dict[str, int], project_path: str):
        self.line_counts = line_counts
        self.project_path = project_path

    def compute_file_metrics(self, result: AnalysisResult) -> Dict[str, Dict[str, Any]]:
        """Per-file metrics derived from AnalysisResult."""
        files: Dict[str, Dict[str, Any]] = {}
        project_path = result.project_path

        # aggregate from functions (skip excluded paths)
        for qname, fi in result.functions.items():
            fpath = fi.file
            if _is_excluded(fpath):
                continue
            if fpath not in files:
                rel = _rel_path(fpath, project_path)
                lc = self.line_counts.get(fpath, self.line_counts.get(rel, 0))
                files[fpath] = self._new_file_record(rel, lc)
            cc = fi.complexity.get("cyclomatic_complexity", 0)
            files[fpath]["cc_scores"].append(cc)
            files[fpath]["max_cc"] = max(files[fpath]["max_cc"], cc)
            files[fpath]["methods"] += 1
            if fi.class_name:
                files[fpath]["classes"].add(fi.class_name)

        # aggregate from classes without functions (skip excluded)
        for qname, ci in result.classes.items():
            fpath = ci.file
            if _is_excluded(fpath):
                continue
            if fpath not in files:
                rel = _rel_path(fpath, project_path)
                lc = self.line_counts.get(fpath, self.line_counts.get(rel, 0))
                files[fpath] = self._new_file_record(rel, lc)
            files[fpath]["classes"].add(ci.name)

        # modules with no functions/classes (skip excluded)
        for mname, mi in result.modules.items():
            fpath = mi.file
            if _is_excluded(fpath):
                continue
            if fpath not in files:
                rel = _rel_path(fpath, project_path)
                lc = self.line_counts.get(fpath, self.line_counts.get(rel, 0))
                files[fpath] = self._new_file_record(rel, lc)

        # fan-in + finalize
        self._compute_fan_in(files, result)

        for fpath in files:
            files[fpath]["class_count"] = len(files[fpath]["classes"])
            del files[fpath]["classes"]

        return files

    @staticmethod
    def _new_file_record(rel: str, line_count: int) -> Dict[str, Any]:
        """Create a fresh file metrics record."""
        return {
            "rel": rel, "lines": line_count,
            "classes": set(), "methods": 0,
            "cc_scores": [], "max_cc": 0.0,
            "fan_in": 0,
        }

    @staticmethod
    def _compute_fan_in(files: Dict, result: AnalysisResult) -> None:
        """Compute fan-in per file (how many other files call into this file)."""
        importers: Dict[str, set] = defaultdict(set)

        for fname, fi in result.functions.items():
            CoreMetricsComputer._process_function_calls(fi, result, importers)

        for fpath in files:
            files[fpath]["fan_in"] = len(importers.get(fpath, set()))

    @staticmethod
    def _process_function_calls(fi: FunctionInfo, result: AnalysisResult, importers: Dict[str, set]) -> None:
        """Process calls for a single function to compute fan-in."""
        src_file = fi.file

        # Forward: who calls me? (called_by)
        CoreMetricsComputer._process_called_by(fi, result, src_file, importers)

        # Reverse: who do I call? → target file gets fan-in
        CoreMetricsComputer._process_callee_calls(fi, result, src_file, importers)

    @staticmethod
    def _process_called_by(fi: FunctionInfo, result: AnalysisResult, src_file: str, importers: Dict[str, set]) -> None:
        """Process called_by relationships."""
        for callee in fi.called_by:
            callee_info = result.functions.get(callee)
            if callee_info and callee_info.file != src_file:
                importers[src_file].add(callee_info.file)

    @staticmethod
    def _process_callee_calls(fi: FunctionInfo, result: AnalysisResult, src_file: str, importers: Dict[str, set]) -> None:
        """Process callee relationships."""
        for callee in fi.calls:
            callee_info = result.functions.get(callee)
            if callee_info and callee_info.file != src_file:
                importers[callee_info.file].add(src_file)
            else:
                # Suffix match for unqualified names
                CoreMetricsComputer._handle_suffix_match(callee, result, src_file, importers)

    @staticmethod
    def _handle_suffix_match(callee: str, result: AnalysisResult, src_file: str, importers: Dict[str, set]) -> None:
        """Handle suffix matching for unqualified names."""
        for qn, ci in result.functions.items():
            if qn.endswith(f".{callee}") and ci.file != src_file:
                importers[ci.file].add(src_file)
                break

    def compute_package_metrics(
        self, files: Dict[str, Dict], result: AnalysisResult
    ) -> Dict[str, Dict[str, Any]]:
        """Package-level aggregation."""
        pkgs: Dict[str, Dict[str, Any]] = {}
        for fpath, fm in files.items():
            pkg = _package_of(fm["rel"])
            if pkg not in pkgs:
                pkgs[pkg] = {
                    "files": [], "total_lines": 0,
                    "cc_scores": [], "fan_in": 0, "fan_out": 0,
                }
            pkgs[pkg]["files"].append(fm["rel"])
            pkgs[pkg]["total_lines"] += fm["lines"]
            pkgs[pkg]["cc_scores"].extend(fm["cc_scores"])
            pkgs[pkg]["fan_in"] += fm["fan_in"]
        for pkg, pd in pkgs.items():
            scores = pd["cc_scores"]
            pd["avg_cc"] = round(sum(scores) / len(scores), 1) if scores else 0.0
            pd["file_count"] = len(pd["files"])
        return pkgs

    def compute_function_metrics(self, result: AnalysisResult) -> List[Dict[str, Any]]:
        """Compute per-function metrics including CC, nodes, exits, traits."""
        funcs = []
        for qname, fi in result.functions.items():
            if _is_excluded(fi.file):
                continue
            cc = fi.complexity.get("cyclomatic_complexity", 0)
            # count CFG nodes for this function
            node_count = len(fi.cfg_nodes) if fi.cfg_nodes else 0
            # count exits
            exits = 0
            for nid in (fi.cfg_nodes or []):
                nd = result.nodes.get(nid)
                if nd and getattr(nd, "type", "") in ("EXIT", "RETURN"):
                    exits += 1
            # traits
            from .helpers import _traits_from_cfg
            traits = _traits_from_cfg(fi, result)
            fan_out = len(set(fi.calls))
            fan_in = len(set(fi.called_by))

            funcs.append({
                "name": fi.name,
                "qualified": qname,
                "cc": cc,
                "nodes": node_count,
                "exits": exits,
                "traits": traits,
                "file": fi.file,
                "rel_file": _rel_path(fi.file, result.project_path),
                "module": fi.module,
                "class_name": fi.class_name,
                "fan_out": fan_out,
                "fan_in": fan_in,
                "reachability": fi.reachability,
            })
        funcs.sort(key=lambda x: x["cc"], reverse=True)
        return funcs

    def compute_class_metrics(self, result: AnalysisResult) -> List[Dict[str, Any]]:
        """Compute per-class metrics including method counts and CC."""
        classes = []
        for qname, ci in result.classes.items():
            if _is_excluded(ci.file):
                continue
            method_ccs = []
            method_names = []
            for mq in ci.methods:
                fi = result.functions.get(mq)
                if fi:
                    method_ccs.append(fi.complexity.get("cyclomatic_complexity", 0))
                    method_names.append(fi.name)
            mc = len(method_names)
            avg_cc = round(sum(method_ccs) / len(method_ccs), 1) if method_ccs else 0.0
            max_cc = max(method_ccs) if method_ccs else 0.0

            classes.append({
                "name": ci.name,
                "qualified": qname,
                "file": ci.file,
                "rel_file": _rel_path(ci.file, result.project_path),
                "module": ci.module,
                "methods": method_names,
                "method_count": mc,
                "avg_cc": avg_cc,
                "max_cc": max_cc,
            })
        classes.sort(key=lambda x: x["method_count"], reverse=True)
        return classes

    def compute_coupling_matrix(
        self, result: AnalysisResult
    ) -> Tuple[Dict[Tuple[str, str], int], Dict[str, Dict[str, int]]]:
        """Build package-to-package coupling from cross-module function calls."""
        # Build module lookup: qualified_func_name -> module_name (skip excluded)
        func_to_module = self._build_function_to_module_map(result)

        # Derive coupling from actual cross-module calls (skip excluded)
        matrix = self._build_coupling_matrix(result, func_to_module)

        # compute fan-in / fan-out per package
        pkg_fan = self._compute_package_fan(matrix)

        return dict(matrix), pkg_fan

    def _build_function_to_module_map(self, result: AnalysisResult) -> Dict[str, str]:
        """Build module lookup: qualified_func_name -> module_name (skip excluded)."""
        func_to_module: Dict[str, str] = {}
        for qname, fi in result.functions.items():
            if not _is_excluded(fi.file):
                func_to_module[qname] = fi.module
        return func_to_module

    def _build_coupling_matrix(self, result: AnalysisResult, func_to_module: Dict[str, str]) -> Dict[Tuple[str, str], int]:
        """Build coupling matrix from cross-module calls."""
        matrix: Dict[Tuple[str, str], int] = defaultdict(int)

        for qname, fi in result.functions.items():
            if _is_excluded(fi.file):
                continue
            src_mod = fi.module
            src_pkg = _package_of_module(src_mod)

            for callee in fi.calls:
                callee_mod = self._resolve_callee_module(callee, func_to_module, src_pkg)
                if callee_mod and callee_mod != src_mod:
                    dst_pkg = _package_of_module(callee_mod)
                    if dst_pkg and dst_pkg != src_pkg:
                        matrix[(src_pkg, dst_pkg)] += 1

        return matrix

    def _resolve_callee_module(self, callee: str, func_to_module: Dict[str, str], src_pkg: str) -> Optional[str]:
        """Resolve callee to a known function module."""
        callee_mod = func_to_module.get(callee)
        if callee_mod:
            return callee_mod

        # Try suffix match — collect all candidates
        candidates = [
            (qn, mod) for qn, mod in func_to_module.items()
            if qn.endswith(f".{callee}")
        ]

        if len(candidates) == 1:
            return candidates[0][1]
        elif candidates:
            # Prefer callee in same package as caller
            same_pkg = [
                (qn, mod) for qn, mod in candidates
                if _package_of_module(mod) == src_pkg
            ]
            if same_pkg:
                return same_pkg[0][1]
            else:
                # Pick first cross-package candidate
                return candidates[0][1]

        return None

    def _compute_package_fan(self, matrix: Dict[Tuple[str, str], int]) -> Dict[str, Dict[str, int]]:
        """Compute fan-in / fan-out per package."""
        pkg_fan: Dict[str, Dict[str, int]] = {}
        all_pkgs = set()
        for (s, d) in matrix:
            all_pkgs.add(s)
            all_pkgs.add(d)
        for pkg in all_pkgs:
            fi = sum(v for (s, d), v in matrix.items() if d == pkg)
            fo = sum(v for (s, d), v in matrix.items() if s == pkg)
            pkg_fan[pkg] = {"fan_in": fi, "fan_out": fo}
        return pkg_fan
