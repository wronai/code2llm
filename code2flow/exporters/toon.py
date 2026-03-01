"""Toon Exporter v2 — scannable plain-text format for code2flow.

Structure communicates health: sorting by severity, inline markers,
coupling matrix, duplicate detection, filtered functions.
"""

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from ..core.models import AnalysisResult, FunctionInfo, ClassInfo, ModuleInfo


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------
CC_CRITICAL = 10
CC_HIGH = 5
CC_WARNING = 15
GOD_MODULE_LINES = 500
GOD_MODULE_CLASSES = 4

# Limits for output size
MAX_HEALTH_ISSUES = 20
MAX_COUPLING_PACKAGES = 15
MAX_FUNCTIONS_SHOWN = 50

# Patterns to exclude (venv, site-packages, etc.)
EXCLUDE_PATTERNS = {
    'venv', '.venv', 'env', '.env', 'publish-env', 'test-env',
    'site-packages', 'node_modules', '__pycache__', '.git',
    'dist', 'build', 'egg-info', '.tox', '.mypy_cache',
}


class ToonExporter:
    """Export to toon v2 plain-text format — scannable, sorted by severity."""

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    def export(self, result: AnalysisResult, output_path: str, **kwargs) -> None:
        """Export analysis result to toon v2 format."""
        ctx = self._build_context(result)

        sections: List[str] = []
        sections.extend(self._render_header(ctx))
        sections.append("")
        sections.extend(self._render_health(ctx))
        sections.append("")
        sections.extend(self._render_refactor(ctx))
        sections.append("")
        sections.extend(self._render_coupling(ctx))
        sections.append("")
        sections.extend(self._render_layers(ctx))
        sections.append("")
        sections.extend(self._render_duplicates(ctx))
        sections.append("")
        sections.extend(self._render_functions(ctx))
        sections.append("")
        sections.extend(self._render_hotspots(ctx))
        sections.append("")
        sections.extend(self._render_classes(ctx))
        sections.append("")
        sections.extend(self._render_details(ctx))

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(sections) + "\n")

    # ------------------------------------------------------------------
    # context builder — pre-compute all metrics once
    # ------------------------------------------------------------------
    def _is_excluded(self, path: str) -> bool:
        """Check if path should be excluded (venv, site-packages, etc.)."""
        path_lower = path.lower().replace('\\', '/')
        for pattern in EXCLUDE_PATTERNS:
            if f'/{pattern}/' in path_lower or path_lower.startswith(f'{pattern}/'):
                return True
            if pattern in path_lower.split('/'):
                return True
        return False

    def _build_context(self, result: AnalysisResult) -> Dict[str, Any]:
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

    # ------------------------------------------------------------------
    # compute helpers
    # ------------------------------------------------------------------
    def _compute_file_metrics(self, result: AnalysisResult) -> Dict[str, Dict[str, Any]]:
        """Per-file metrics derived from AnalysisResult."""
        files: Dict[str, Dict[str, Any]] = {}

        # read line counts from disk if project_path available
        line_counts: Dict[str, int] = {}
        project_path = result.project_path
        if project_path:
            pp = Path(project_path)
            if pp.is_dir():
                for py in pp.rglob("*.py"):
                    try:
                        lc = len(py.read_text(encoding="utf-8", errors="ignore").splitlines())
                        rel = str(py.relative_to(pp))
                        line_counts[str(py)] = lc
                        line_counts[rel] = lc
                    except Exception:
                        pass

        # aggregate from functions (skip excluded paths)
        for qname, fi in result.functions.items():
            fpath = fi.file
            if self._is_excluded(fpath):
                continue
            if fpath not in files:
                rel = self._rel_path(fpath, project_path)
                lc = line_counts.get(fpath, line_counts.get(rel, 0))
                files[fpath] = {
                    "rel": rel, "lines": lc,
                    "classes": set(), "methods": 0,
                    "cc_scores": [], "max_cc": 0.0,
                    "fan_in": 0,
                }
            cc = fi.complexity.get("cyclomatic_complexity", 0)
            files[fpath]["cc_scores"].append(cc)
            files[fpath]["max_cc"] = max(files[fpath]["max_cc"], cc)
            files[fpath]["methods"] += 1
            if fi.class_name:
                files[fpath]["classes"].add(fi.class_name)

        # aggregate from classes without functions (skip excluded)
        for qname, ci in result.classes.items():
            fpath = ci.file
            if self._is_excluded(fpath):
                continue
            if fpath not in files:
                rel = self._rel_path(fpath, project_path)
                lc = line_counts.get(fpath, line_counts.get(rel, 0))
                files[fpath] = {
                    "rel": rel, "lines": lc,
                    "classes": set(), "methods": 0,
                    "cc_scores": [], "max_cc": 0.0,
                    "fan_in": 0,
                }
            files[fpath]["classes"].add(ci.name)

        # modules with no functions/classes (e.g. __init__.py) (skip excluded)
        for mname, mi in result.modules.items():
            fpath = mi.file
            if self._is_excluded(fpath):
                continue
            if fpath not in files:
                rel = self._rel_path(fpath, project_path)
                lc = line_counts.get(fpath, line_counts.get(rel, 0))
                files[fpath] = {
                    "rel": rel, "lines": lc,
                    "classes": set(), "methods": 0,
                    "cc_scores": [], "max_cc": 0.0,
                    "fan_in": 0,
                }

        # compute fan-in per file (how many other files import from this file)
        importers: Dict[str, Set[str]] = defaultdict(set)
        for fname, fi in result.functions.items():
            for callee in fi.called_by:
                callee_info = result.functions.get(callee)
                if callee_info and callee_info.file != fi.file:
                    importers[fi.file].add(callee_info.file)
        for fpath in files:
            files[fpath]["fan_in"] = len(importers.get(fpath, set()))

        # convert class sets to counts
        for fpath in files:
            files[fpath]["class_count"] = len(files[fpath]["classes"])
            del files[fpath]["classes"]

        return files

    def _compute_package_metrics(
        self, files: Dict[str, Dict], result: AnalysisResult
    ) -> Dict[str, Dict[str, Any]]:
        """Package-level aggregation."""
        pkgs: Dict[str, Dict[str, Any]] = {}
        for fpath, fm in files.items():
            pkg = self._package_of(fm["rel"])
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
            if self._is_excluded(fi.file):
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
            traits = self._traits_from_cfg(fi, result)
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
                "rel_file": self._rel_path(fi.file, result.project_path),
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
            if self._is_excluded(ci.file):
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
                "rel_file": self._rel_path(ci.file, result.project_path),
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
        matrix: Dict[Tuple[str, str], int] = defaultdict(int)
        pkg_fan: Dict[str, Dict[str, int]] = {}

        # Build module lookup: qualified_func_name -> module_name (skip excluded)
        func_to_module: Dict[str, str] = {}
        for qname, fi in result.functions.items():
            if not self._is_excluded(fi.file):
                func_to_module[qname] = fi.module

        # Derive coupling from actual cross-module calls (skip excluded)
        for qname, fi in result.functions.items():
            if self._is_excluded(fi.file):
                continue
            src_mod = fi.module
            src_pkg = self._package_of_module(src_mod)
            for callee in fi.calls:
                # Resolve callee to a known function
                callee_mod = func_to_module.get(callee)
                if not callee_mod:
                    # Try suffix match
                    for known_qname, known_mod in func_to_module.items():
                        if known_qname.endswith(f".{callee}"):
                            callee_mod = known_mod
                            break
                if callee_mod and callee_mod != src_mod:
                    dst_pkg = self._package_of_module(callee_mod)
                    if dst_pkg and dst_pkg != src_pkg:
                        matrix[(src_pkg, dst_pkg)] += 1

        # compute fan-in / fan-out per package
        all_pkgs = set()
        for (s, d) in matrix:
            all_pkgs.add(s)
            all_pkgs.add(d)
        for pkg in all_pkgs:
            fi = sum(v for (s, d), v in matrix.items() if d == pkg)
            fo = sum(v for (s, d), v in matrix.items() if s == pkg)
            pkg_fan[pkg] = {"fan_in": fi, "fan_out": fo}

        return dict(matrix), pkg_fan

    def _detect_duplicates(self, result: AnalysisResult) -> List[Dict[str, Any]]:
        """Detect duplicate classes by comparing method-name sets."""
        dupes: List[Dict[str, Any]] = []
        # Filter out excluded classes first
        class_list = [(q, c) for q, c in result.classes.items() if not self._is_excluded(c.file)]

        for i, (qa, ca) in enumerate(class_list):
            methods_a = set(m.split(".")[-1] for m in ca.methods)
            if len(methods_a) < 3:
                continue
            for j in range(i + 1, len(class_list)):
                qb, cb = class_list[j]
                if ca.name != cb.name:
                    continue
                methods_b = set(m.split(".")[-1] for m in cb.methods)
                if len(methods_b) < 3:
                    continue
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
                    dupes.append({
                        "class_name": ca.name,
                        "qualA": qa, "qualB": qb,
                        "fileA": self._rel_path(ca.file, result.project_path),
                        "fileB": self._rel_path(cb.file, result.project_path),
                        "methodsA": sorted(methods_a),
                        "methodsB": sorted(methods_b),
                        "countA": len(methods_a),
                        "countB": len(methods_b),
                        "diff": diff,
                    })
        return dupes

    def _compute_health(self, ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compute health issues sorted by severity."""
        issues: List[Dict[str, Any]] = []
        result: AnalysisResult = ctx["result"]

        # duplicates
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

        # god modules (large files with many classes)
        for fpath, fm in ctx["files"].items():
            if fm["lines"] >= GOD_MODULE_LINES and fm["class_count"] >= GOD_MODULE_CLASSES:
                issues.append({
                    "severity": "red",
                    "code": "GOD",
                    "message": f"{fm['rel']} = {fm['lines']}L, {fm['class_count']} classes, {fm['methods']}m, max CC={fm['max_cc']}",
                    "impact": "split needed",
                })

        # from existing smells
        for smell in result.smells:
            stype = smell.type
            if stype == "god_function":
                cc_val = smell.context.get("complexity", 0)
                if cc_val >= CC_WARNING:
                    fname = smell.context.get("function", smell.name)
                    short = fname.split(".")[-1] if "." in fname else fname
                    issues.append({
                        "severity": "yellow",
                        "code": "CC",
                        "message": f"{short} CC={cc_val} (limit:{CC_WARNING})",
                        "impact": "split method",
                    })
            elif stype == "circular_dependency":
                issues.append({
                    "severity": "red",
                    "code": "CYCLE",
                    "message": smell.description,
                    "impact": "break cycle",
                })
            elif stype == "bottleneck":
                issues.append({
                    "severity": "yellow",
                    "code": "BTL",
                    "message": smell.description,
                    "impact": "decouple",
                })

        # high CC functions not caught by smells
        high_cc = [f for f in ctx["func_metrics"] if f["cc"] >= CC_WARNING]
        existing_cc_msgs = {i["message"] for i in issues if i["code"] == "CC"}
        for fm in high_cc:
            short = fm["name"]
            msg = f"{short} CC={fm['cc']} (limit:{CC_WARNING})"
            if msg not in existing_cc_msgs:
                issues.append({
                    "severity": "yellow",
                    "code": "CC",
                    "message": msg,
                    "impact": "split method",
                })

        # sort: red first, then yellow, limit to MAX_HEALTH_ISSUES
        sev_order = {"red": 0, "yellow": 1, "green": 2}
        issues.sort(key=lambda x: sev_order.get(x["severity"], 9))
        return issues[:MAX_HEALTH_ISSUES]

    def _compute_hotspots(self, result: AnalysisResult) -> List[Dict[str, Any]]:
        """Top functions by fan-out."""
        spots = []
        for qname, fi in result.functions.items():
            if self._is_excluded(fi.file):
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
                    "description": self._hotspot_description(fi, fan_out),
                })
        spots.sort(key=lambda x: x["fan_out"], reverse=True)
        return spots[:10]

    def _get_cycles(self, result: AnalysisResult) -> List[List[str]]:
        proj = result.metrics.get("project", {})
        return proj.get("circular_dependencies", [])

    # ------------------------------------------------------------------
    # render sections
    # ------------------------------------------------------------------
    def _render_header(self, ctx: Dict[str, Any]) -> List[str]:
        result: AnalysisResult = ctx["result"]
        nfiles = len(ctx["files"])
        total_lines = sum(fm["lines"] for fm in ctx["files"].values())
        nfuncs = len(result.functions)
        all_cc = [f["cc"] for f in ctx["func_metrics"]]
        avg_cc = round(sum(all_cc) / len(all_cc), 1) if all_cc else 0.0
        critical = len([f for f in ctx["func_metrics"] if f["cc"] >= CC_CRITICAL])
        ndups = len(ctx["duplicates"])
        ncycles = len(ctx["cycles"])

        lines = [
            f"# code2flow | {nfiles}f {total_lines}L | py:{nfiles} | {ctx['timestamp']}",
            f"# CC\u0304={avg_cc} | critical:{critical}/{nfuncs} | dups:{ndups} | cycles:{ncycles}",
        ]
        return lines

    def _render_health(self, ctx: Dict[str, Any]) -> List[str]:
        issues = ctx["health"]
        if not issues:
            return ["HEALTH[0]: ok"]
        lines = [f"HEALTH[{len(issues)}]:"]
        for issue in issues:
            icon = "\U0001f534" if issue["severity"] == "red" else "\U0001f7e1"
            lines.append(f"  {icon} {issue['code']:5s} {issue['message']}")
        return lines

    def _render_refactor(self, ctx: Dict[str, Any]) -> List[str]:
        """Generate numbered refactoring steps from health issues."""
        steps: List[str] = []

        # duplicates → remove
        if ctx["duplicates"]:
            n = len(ctx["duplicates"])
            steps.append(f"rm duplicates  (-{n} dup classes)")

        # god modules → split
        god_issues = [h for h in ctx["health"] if h["code"] == "GOD"]
        for gi in god_issues:
            steps.append(f"split {gi['message'].split('=')[0].strip()}  (god module)")

        # high CC → split methods
        cc_issues = [h for h in ctx["health"] if h["code"] == "CC"]
        if cc_issues:
            steps.append(f"split {len(cc_issues)} high-CC methods  (CC>{CC_WARNING})")

        # cycles → break
        if ctx["cycles"]:
            steps.append(f"break {len(ctx['cycles'])} circular dependencies")

        if not steps:
            return ["REFACTOR[0]: none needed"]
        lines = [f"REFACTOR[{len(steps)}]:"]
        for i, step in enumerate(steps, 1):
            lines.append(f"  {i}. {step}")
        return lines

    def _render_coupling(self, ctx: Dict[str, Any]) -> List[str]:
        matrix = ctx["coupling_matrix"]
        pkg_fan = ctx["pkg_fan"]
        if not matrix:
            return ["COUPLING: no cross-package imports detected"]

        all_pkgs = sorted({p for pair in matrix for p in pair})
        if not all_pkgs:
            return ["COUPLING: n/a"]

        # Limit to top packages by fan-in + fan-out
        pkg_activity = [(p, pkg_fan.get(p, {}).get("fan_in", 0) + pkg_fan.get(p, {}).get("fan_out", 0)) for p in all_pkgs]
        pkg_activity.sort(key=lambda x: x[1], reverse=True)
        top_pkgs = [p for p, _ in pkg_activity[:MAX_COUPLING_PACKAGES]]

        if not top_pkgs:
            return ["COUPLING: n/a"]

        # header
        col_w = max(len(p) for p in top_pkgs)
        col_w = max(col_w, 6)
        hdr_label = "COUPLING:"
        pad = max(len(p) for p in top_pkgs) + 2
        hdr = f"{'':>{pad}}  " + "  ".join(f"{p:>{col_w}}" for p in top_pkgs)
        lines = [hdr_label, hdr]

        for src in top_pkgs:
            row_parts = []
            for dst in top_pkgs:
                if src == dst:
                    row_parts.append(f"{'──':>{col_w}}")
                else:
                    val = matrix.get((src, dst), 0)
                    cell = str(val) if val else ""
                    # show ←N for fan-in direction
                    if not val:
                        rev = matrix.get((dst, src), 0)
                        cell = f"←{rev}" if rev else ""
                    row_parts.append(f"{cell:>{col_w}}")
            tag = ""
            fi = pkg_fan.get(src, {}).get("fan_in", 0)
            fo = pkg_fan.get(src, {}).get("fan_out", 0)
            if fi >= 5:
                tag = "  hub"
            elif fo >= 8:
                tag = "  !! fan-out"
            lines.append(f"  {src:>{pad-2}}  " + "  ".join(row_parts) + tag)

        # summary
        ncycles = len(ctx["cycles"])
        lines.append(f"  CYCLES: {'none' if ncycles == 0 else ncycles}")
        hubs = [p for p, d in pkg_fan.items() if d.get("fan_in", 0) >= 5]
        if hubs:
            for h in hubs:
                lines.append(f"  HUB: {h}/ (fan-in={pkg_fan[h]['fan_in']})")
        smelly = [p for p, d in pkg_fan.items() if d.get("fan_out", 0) >= 8]
        if smelly:
            for s in smelly:
                lines.append(f"  SMELL: {s}/ fan-out={pkg_fan[s]['fan_out']} → split needed")

        return lines

    def _render_layers(self, ctx: Dict[str, Any]) -> List[str]:
        """Render LAYERS section — files grouped by package with metrics."""
        files = ctx["files"]
        packages = ctx["packages"]
        pkg_fan = ctx["pkg_fan"]
        dup_files = self._dup_file_set(ctx)

        # group files by package, sort packages by avg_cc desc
        pkg_order = sorted(
            packages.keys(),
            key=lambda p: packages[p].get("avg_cc", 0),
            reverse=True,
        )

        lines = ["LAYERS:"]
        for pkg in pkg_order:
            pd = packages[pkg]
            fi = pkg_fan.get(pkg, {}).get("fan_in", 0)
            fo = pkg_fan.get(pkg, {}).get("fan_out", 0)
            markers = ""
            if fo >= 8:
                markers = "  !! split"
            # any dup classes?
            pkg_dups = any(
                d["fileA"].startswith(pkg + "/") or d["fileB"].startswith(pkg + "/")
                for d in ctx["duplicates"]
            )
            if pkg_dups:
                markers += "  ×DUP"

            lines.append(
                f"  {pkg + '/':30s}  CC\u0304={pd['avg_cc']:<5}  "
                f"\u2190in:{fi}  \u2192out:{fo}{markers}"
            )

            # files in this package sorted by lines desc
            pkg_files = [
                (fpath, fm) for fpath, fm in files.items()
                if fm["rel"].startswith(pkg + "/") or (pkg == "." and "/" not in fm["rel"])
            ]
            pkg_files.sort(key=lambda x: x[1]["lines"], reverse=True)

            for fpath, fm in pkg_files:
                rel = fm["rel"]
                short = rel.split("/")[-1] if "/" in rel else rel
                # remove .py suffix for compactness
                if short.endswith(".py"):
                    short = short[:-3]
                lc = fm["lines"]
                cc_count = fm["class_count"]
                mc = fm["methods"]
                mcc = fm["max_cc"]
                fin = fm["fan_in"]

                severity = ""
                if lc >= GOD_MODULE_LINES or mcc >= CC_WARNING:
                    severity = "!! "
                elif mcc >= CC_CRITICAL:
                    severity = "!  "

                dup_mark = ""
                if rel in dup_files:
                    dup_mark = "  ×DUP"

                lines.append(
                    f"  \u2502 {severity}{short:24s} {lc:>5}L  {cc_count}C  {mc:>3}m"
                    f"  CC={mcc:<5}  \u2190{fin}{dup_mark}"
                )
            lines.append(f"  \u2502")

        # zero-line files
        zero = [(fpath, fm) for fpath, fm in files.items() if fm["lines"] == 0]
        if zero:
            lines.append("  \u2500\u2500 zero \u2500\u2500")
            for fpath, fm in sorted(zero, key=lambda x: x[1]["rel"]):
                lines.append(f"     {fm['rel']:40s}  0L")

        return lines

    def _render_duplicates(self, ctx: Dict[str, Any]) -> List[str]:
        dupes = ctx["duplicates"]
        if not dupes:
            return ["DUPLICATES[0]: none"]
        lines = [f"DUPLICATES[{len(dupes)}]:"]
        for d in dupes:
            lines.append(f"  {d['class_name']}  {d['fileA']} \u2194 {d['fileB']}")
            lines.append(f"    A: {d['countA']}m  {' '.join(d['methodsA'][:8])}")
            lines.append(f"    B: {d['countB']}m  {' '.join(d['methodsB'][:8])}")
            recommend = ""
            if d["diff"] == "IDENTICAL":
                recommend = " \u2192 rm B"
            elif d["diff"].startswith("A has"):
                recommend = " \u2192 keep A"
            elif d["diff"].startswith("B has"):
                recommend = " \u2192 keep B"
            lines.append(f"    DIFF: {d['diff']}{recommend}")
        return lines

    def _render_functions(self, ctx: Dict[str, Any]) -> List[str]:
        """Render FUNCTIONS section — only CC >= threshold."""
        all_funcs = ctx["func_metrics"]
        critical = [f for f in all_funcs if f["cc"] >= CC_CRITICAL]
        total = len(all_funcs)
        dup_classes = {d["class_name"] for d in ctx["duplicates"]}

        if not critical:
            return [f"FUNCTIONS (CC\u2265{CC_CRITICAL}, 0 of {total}): none"]

        lines = [f"FUNCTIONS (CC\u2265{CC_CRITICAL}, {len(critical)} of {total}):"]
        shown = critical[:MAX_FUNCTIONS_SHOWN]
        for fm in shown:
            display = fm["name"]
            if fm["class_name"]:
                display = f"{fm['class_name']}.{fm['name']}"

            traits = "+".join(fm["traits"]) if fm["traits"] else ""
            exits_s = f"{fm['exits']}exit" if fm["exits"] else ""

            markers = ""
            if fm["class_name"] and fm["class_name"] in dup_classes:
                markers += "  ×DUP"
            if fm["cc"] >= CC_WARNING:
                markers += "  !! split"

            lines.append(
                f"  {fm['cc']:>5.1f}  {display:40s}  {fm['nodes']:>3}n"
                f"  {exits_s:>6s}  {traits}{markers}"
            )

        # summary distribution
        cc_bins = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for f in all_funcs:
            if f["cc"] >= CC_CRITICAL:
                cc_bins["critical"] += 1
            elif f["cc"] >= CC_HIGH:
                cc_bins["high"] += 1
            elif f["cc"] >= 2:
                cc_bins["medium"] += 1
            else:
                cc_bins["low"] += 1

        pct_crit = round(cc_bins["critical"] / total * 100) if total else 0
        pct_high = round((cc_bins["critical"] + cc_bins["high"]) / total * 100) if total else 0

        lines.append("")
        lines.append("  summary:")
        lines.append(
            f"    critical(\u2265{CC_CRITICAL}): {cc_bins['critical']}"
            f" | high({CC_HIGH}-{CC_CRITICAL}): {cc_bins['high']}"
            f" | medium(2-{CC_HIGH}): {cc_bins['medium']}"
            f" | low(<2): {cc_bins['low']}"
        )
        lines.append(f"    {pct_crit}% CC\u2265{CC_CRITICAL}  {pct_high}% CC\u2265{CC_HIGH}")

        return lines

    def _render_hotspots(self, ctx: Dict[str, Any]) -> List[str]:
        spots = ctx["hotspots"]
        if not spots:
            return ["HOTSPOTS: none"]
        lines = ["HOTSPOTS:"]
        for i, s in enumerate(spots, 1):
            lines.append(
                f"  #{i:<2} {s['name']:35s}  fan={s['fan_out']:<3}"
                f"  \"{s['description']}\""
            )
        return lines

    def _render_classes(self, ctx: Dict[str, Any]) -> List[str]:
        """Render CLASSES section with visual bar chart proportional to method count."""
        classes = ctx["class_metrics"]
        if not classes:
            return ["CLASSES: none"]

        max_methods = max(c["method_count"] for c in classes) if classes else 1
        bar_max = 24

        lines = ["CLASSES:"]
        for cm in classes:
            name = cm["name"]
            mc = cm["method_count"]
            avg_cc = cm["avg_cc"]
            max_cc = cm["max_cc"]

            bar_len = int((mc / max_methods) * bar_max) if max_methods > 0 else 0
            bar = "\u2588" * bar_len

            markers = ""
            if max_cc >= CC_WARNING:
                markers += "  !!"
            dup_count = sum(1 for d in ctx["duplicates"] if d["class_name"] == name)
            if dup_count > 0:
                markers += f"  \u00d7{dup_count}"

            lines.append(
                f"  {name:30s} {bar:<{bar_max}}  {mc:>2}m  CC\u0304={avg_cc:<4}  max={max_cc:<4}{markers}"
            )

        return lines

    def _render_details(self, ctx: Dict[str, Any]) -> List[str]:
        """Render D: section — per-module details sorted by max CC desc."""
        result: AnalysisResult = ctx["result"]
        files = ctx["files"]
        dup_classes = {d["class_name"] for d in ctx["duplicates"]}

        # sort modules by max CC desc
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

        lines = ["D:"]
        for mname, mi, max_cc in mod_items:
            rel = self._rel_path(mi.file, result.project_path)
            lines.append(f"  {rel}:")

            # imports
            if mi.imports:
                imp_str = ",".join(sorted(mi.imports))
                lines.append(f"    i: {imp_str}")

            # exports (classes + top-level functions)
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

            # classes with methods - show flow signature
            for cq in mi.classes:
                ci = result.classes.get(cq)
                if not ci:
                    continue

                dup_mark = "  ×DUP" if ci.name in dup_classes else ""
                doc = ""
                if ci.docstring:
                    doc = f"  # {ci.docstring[:60]}..."
                lines.append(f"    {ci.name}{dup_mark}{doc}")

                # flow signature: show call chain for each method
                method_items = []
                for mq in ci.methods:
                    fi = result.functions.get(mq)
                    if fi:
                        cc = fi.complexity.get("cyclomatic_complexity", 0)
                        arity = len(fi.args) - (1 if fi.is_method else 0)
                        method_items.append((fi, cc, arity))

                # find root method (usually __init__ or first method)
                root_method = None
                for fi, cc, arity in method_items:
                    if fi.name == "__init__":
                        root_method = fi
                        break
                if not root_method and method_items:
                    root_method = method_items[0][0]

                # build call chain
                if root_method:
                    self._render_call_chain(root_method, method_items, result, lines, "      ")

            # standalone functions
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

        return lines

    # ------------------------------------------------------------------
    # utility helpers
    # ------------------------------------------------------------------
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

    def _package_of(self, rel_path: str) -> str:
        """Extract top-level package/directory from relative path."""
        parts = Path(rel_path).parts
        if len(parts) >= 2:
            return parts[0]
        # root-level .py files → group under "."
        return "."

    def _package_of_module(self, module_name: str) -> str:
        parts = module_name.split(".")
        if len(parts) >= 2:
            return parts[0]
        # single-part module names are root-level scripts
        return parts[0] if parts else ""

    def _traits_from_cfg(self, fi: FunctionInfo, result: AnalysisResult) -> List[str]:
        traits = []
        node_types = set()
        for nid in (fi.cfg_nodes or []):
            nd = result.nodes.get(nid)
            if nd:
                node_types.add(getattr(nd, "type", ""))
        if node_types & {"FOR", "WHILE"}:
            traits.append("loops")
        if "IF" in node_types:
            traits.append("cond")
        if "RETURN" in node_types:
            traits.append("ret")
        return traits

    def _dup_file_set(self, ctx: Dict[str, Any]) -> Set[str]:
        s: Set[str] = set()
        for d in ctx["duplicates"]:
            s.add(d["fileA"])
            s.add(d["fileB"])
        return s

    def _hotspot_description(self, fi: FunctionInfo, fan_out: int) -> str:
        if fi.name == "to_dict":
            return f"{fan_out} conditional field serializations"
        if "format" in fi.name.lower() or "dispatch" in fi.name.lower():
            return f"{fan_out}-way dispatch"
        if "export" in fi.name.lower():
            return f"export with {fan_out} outputs"
        if "analyze" in fi.name.lower() or "process" in fi.name.lower():
            return f"analysis pipeline, {fan_out} stages"
        if fi.class_name:
            return f"{fi.class_name} method, fan-out={fan_out}"
        return f"calls {fan_out} functions"

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

