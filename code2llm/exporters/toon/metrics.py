"""Metrics computation for TOON exporter."""

from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Tuple, Set, Optional

from ...core.models import AnalysisResult, FunctionInfo, ClassInfo

from .helpers import _is_excluded, _rel_path, _package_of, _package_of_module, _scan_line_counts


class MetricsComputer:
    """Computes all metrics for TOON export."""
    
    def __init__(self):
        self.result = None
        self.project_path = None
        self.line_counts = {}
    
    def compute_all_metrics(self, result: AnalysisResult) -> Dict[str, Any]:
        """Compute all metrics and return context dict."""
        self.result = result
        self.project_path = result.project_path
        self.line_counts = _scan_line_counts(self.project_path)
        
        ctx: Dict[str, Any] = {}
        ctx["result"] = result
        ctx["timestamp"] = datetime.now().strftime("%Y-%m-%d")

        # file-level metrics  {rel_path: {lines, classes, methods, max_cc, …}}
        ctx["files"] = self._compute_file_metrics(result)
        # package-level metrics  {pkg: {files, total_lines, avg_cc, fan_in, fan_out}}
        ctx["packages"] = self._compute_package_metrics(ctx["files"], result)
        # per-function CC list  [{name, qualified, cc, nodes, exits, traits, file, module, class_name}]
        ctx["func_metrics"] = self._compute_function_metrics(result)
        # per-class metrics  [{name, qualified, file, module, methods, method_count, avg_cc, max_cc}]
        ctx["class_metrics"] = self._compute_class_metrics(result)
        # coupling matrix  {(src_pkg, dst_pkg): count}
        ctx["coupling_matrix"], ctx["pkg_fan"] = self._compute_coupling_matrix(result)
        # duplicates  [{classA, classB, fileA, fileB, methodsA, methodsB, diff}]
        ctx["duplicates"] = self._detect_duplicates(result)
        # health issues  [{severity, code, message, impact}]
        ctx["health"] = self._compute_health(ctx)
        # hotspots  [{name, fan_out, description}]
        ctx["hotspots"] = self._compute_hotspots(result)
        # cycles
        ctx["cycles"] = self._get_cycles(result)

        return ctx

    def _compute_file_metrics(self, result: AnalysisResult) -> Dict[str, Dict[str, Any]]:
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
            MetricsComputer._process_function_calls(fi, result, importers)
        
        for fpath in files:
            files[fpath]["fan_in"] = len(importers.get(fpath, set()))

    @staticmethod
    def _process_function_calls(fi: FunctionInfo, result: AnalysisResult, importers: Dict[str, set]) -> None:
        """Process calls for a single function to compute fan-in."""
        src_file = fi.file
        
        # Forward: who calls me? (called_by)
        MetricsComputer._process_called_by(fi, result, src_file, importers)
        
        # Reverse: who do I call? → target file gets fan-in
        MetricsComputer._process_callee_calls(fi, result, src_file, importers)

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
                MetricsComputer._handle_suffix_match(callee, result, src_file, importers)

    @staticmethod
    def _handle_suffix_match(callee: str, result: AnalysisResult, src_file: str, importers: Dict[str, set]) -> None:
        """Handle suffix matching for unqualified names."""
        for qn, ci in result.functions.items():
            if qn.endswith(f".{callee}") and ci.file != src_file:
                importers[ci.file].add(src_file)
                break

    def _compute_package_metrics(
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

    def _compute_function_metrics(self, result: AnalysisResult) -> List[Dict[str, Any]]:
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

    def _compute_class_metrics(self, result: AnalysisResult) -> List[Dict[str, Any]]:
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

    def _compute_coupling_matrix(
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

    def _detect_duplicates(self, result: AnalysisResult) -> List[Dict[str, Any]]:
        """Detect duplicate classes by comparing method-name sets."""
        dupes: List[Dict[str, Any]] = []
        # Filter out excluded classes first
        class_list = [(q, c) for q, c in result.classes.items() if not _is_excluded(c.file)]

        for i, (qa, ca) in enumerate(class_list):
            dupes.extend(self._check_class_for_duplicates(i, qa, ca, class_list, result))
        
        return dupes

    def _check_class_for_duplicates(self, i: int, qa: str, ca: ClassInfo, class_list: List, result: AnalysisResult) -> List[Dict[str, Any]]:
        """Check a single class for duplicates."""
        methods_a = {m.split(".")[-1] for m in ca.methods}
        if len(methods_a) < 3:
            return []
            
        dupes = []
        for j in range(i + 1, len(class_list)):
            qb, cb = class_list[j]
            if ca.name != cb.name:
                continue
                
            methods_b = {m.split(".")[-1] for m in cb.methods}
            if len(methods_b) < 3:
                continue
                
            duplicate_info = self._calculate_duplicate_info(qa, ca, qb, cb, methods_a, methods_b, result)
            if duplicate_info:
                dupes.append(duplicate_info)
        
        return dupes

    def _calculate_duplicate_info(self, qa: str, ca: ClassInfo, qb: str, cb: ClassInfo, methods_a: Set[str], methods_b: Set[str], result: AnalysisResult) -> Optional[Dict[str, Any]]:
        """Calculate duplicate information between two classes."""
        overlap = methods_a & methods_b
        union = methods_a | methods_b
        if len(overlap) / len(union) >= 0.6:
            only_a = methods_a - methods_b
            only_b = methods_b - methods_a
            
            if methods_a == methods_b:
                diff = "IDENTICAL"
            elif len(methods_a) >= len(methods_b):
                diff = f"A has +{','.join(sorted(only_a))}" if only_a else "A=B"
            else:
                diff = f"B has +{','.join(sorted(only_b))}" if only_b else "A=B"
                
            return {
                "class_name": ca.name,
                "qualA": qa, "qualB": qb,
                "fileA": _rel_path(ca.file, result.project_path),
                "fileB": _rel_path(cb.file, result.project_path),
                "methodsA": sorted(methods_a),
                "methodsB": sorted(methods_b),
                "countA": len(methods_a),
                "countB": len(methods_b),
                "diff": diff,
            }
        return None

    def _compute_health(self, ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compute health issues sorted by severity."""
        issues: List[Dict[str, Any]] = []
        result: AnalysisResult = ctx["result"]

        self._check_duplicates_health(ctx, issues)
        self._check_god_modules_health(ctx, issues)
        self._check_smells_health(result, issues)
        self._check_high_cc_health(ctx, issues)

        # sort: red first, then yellow, limit
        sev_order = {"red": 0, "yellow": 1, "green": 2}
        issues.sort(key=lambda x: sev_order.get(x["severity"], 9))
        return issues[:20]  # MAX_HEALTH_ISSUES

    def _check_duplicates_health(self, ctx, issues):
        """Check for duplicate classes."""
        ndups = len(ctx["duplicates"])
        if ndups > 0:
            dup_lines = sum(
                ctx["files"].get(d.get("fileA_abs", ""), {}).get("lines", 0)
                for d in ctx["duplicates"]
            )
            issues.append({
                "severity": "red",
                "code": "DUP",
                "message": f"{ndups} classes duplicated ({dup_lines}L wasted)" if dup_lines else f"{ndups} classes duplicated",
                "impact": f"-{ndups} dup classes",
            })

    def _check_god_modules_health(self, ctx, issues):
        """Check for god modules (large files with many classes)."""
        GOD_MODULE_LINES = 500
        GOD_MODULE_CLASSES = 4
        for fpath, fm in ctx["files"].items():
            if fm["lines"] >= GOD_MODULE_LINES and fm["class_count"] >= GOD_MODULE_CLASSES:
                issues.append({
                    "severity": "red",
                    "code": "GOD",
                    "message": f"{fm['rel']} = {fm['lines']}L, {fm['class_count']} classes, {fm['methods']}m, max CC={fm['max_cc']}",
                    "impact": "split needed",
                })

    def _check_smells_health(self, result, issues):
        """Check for code smells: CC, cycles, bottlenecks."""
        CC_WARNING = 15
        for smell in result.smells:
            stype = smell.type
            if stype == "god_function":
                cc_val = smell.context.get("complexity", 0)
                if cc_val >= CC_WARNING:
                    fname = smell.context.get("function", smell.name)
                    short = fname.split(".")[-1] if "." in fname else fname
                    issues.append({
                        "severity": "yellow", "code": "CC",
                        "message": f"{short} CC={cc_val} (limit:{CC_WARNING})",
                        "impact": "split method",
                    })
            elif stype == "circular_dependency":
                issues.append({
                    "severity": "red", "code": "CYCLE",
                    "message": smell.description, "impact": "break cycle",
                })
            elif stype == "bottleneck":
                issues.append({
                    "severity": "yellow", "code": "BTL",
                    "message": smell.description, "impact": "decouple",
                })

    def _check_high_cc_health(self, ctx, issues):
        """Check for high CC functions not already caught by smells."""
        CC_WARNING = 15
        high_cc = [f for f in ctx["func_metrics"] if f["cc"] >= CC_WARNING]
        existing_cc_msgs = {i["message"] for i in issues if i["code"] == "CC"}
        for fm in high_cc:
            short = fm["name"]
            msg = f"{short} CC={fm['cc']} (limit:{CC_WARNING})"
            if msg not in existing_cc_msgs:
                issues.append({
                    "severity": "yellow", "code": "CC",
                    "message": msg, "impact": "split method",
                })

    def _compute_hotspots(self, result: AnalysisResult) -> List[Dict[str, Any]]:
        """Top functions by fan-out."""
        from .helpers import _hotspot_description
        spots = []
        for qname, fi in result.functions.items():
            if _is_excluded(fi.file):
                continue
            fan_out = len(set(fi.calls))
            if fan_out >= 5:
                display = fi.name
                if fi.class_name:
                    display = f"{fi.class_name}.{fi.name}"
                spots.append({
                    "name": display,
                    "qualified": qname,
                    "fan_out": fan_out,
                    "description": _hotspot_description(fi, fan_out),
                })
        spots.sort(key=lambda x: x["fan_out"], reverse=True)
        return spots[:10]

    def _get_cycles(self, result: AnalysisResult) -> List[List[str]]:
        proj = result.metrics.get("project", {})
        return proj.get("circular_dependencies", [])
