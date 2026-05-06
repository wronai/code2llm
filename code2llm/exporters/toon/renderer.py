"""Rendering functions for TOON exporter."""

from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

from code2llm.core.models import AnalysisResult
from code2llm.core.config import LANGUAGE_EXTENSIONS

from .helpers import _dup_file_set


# Constants
CC_CRITICAL = 15
CC_HIGH = 10
CC_WARNING = 15
GOD_MODULE_LINES = 500
MAX_HEALTH_ISSUES = 20
MAX_COUPLING_PACKAGES = 15
MAX_FUNCTIONS_SHOWN = 50


class ToonRenderer:
    """Renders all sections for TOON export."""
    
    def render_header(self, ctx: Dict[str, Any]) -> List[str]:
        """Render header section."""
        result: AnalysisResult = ctx["result"]
        nfiles = len(ctx["files"])
        total_lines = sum(fm["lines"] for fm in ctx["files"].values())
        nfuncs = len(result.functions)
        all_cc = [f["cc"] for f in ctx["func_metrics"]]
        avg_cc = round(sum(all_cc) / len(all_cc), 1) if all_cc else 0.0
        critical = len([f for f in ctx["func_metrics"] if f["cc"] >= CC_CRITICAL])
        ndups = len(ctx["duplicates"])
        ncycles = len(ctx["cycles"])

        lang_label = self._detect_language_label(result)

        lines = [
            f"# code2llm | {nfiles}f {total_lines}L | {lang_label} | {ctx['timestamp']}",
            f"# CC̄={avg_cc} | critical:{critical}/{nfuncs} | dups:{ndups} | cycles:{ncycles}",
        ]
        return lines

    @staticmethod
    def _detect_language_label(result: AnalysisResult) -> str:
        """Build language breakdown label like 'typescript:463,javascript:10,rust:1'."""
        from .helpers import _is_excluded
        langs: Dict[str, int] = defaultdict(int)
        for mi in result.modules.values():
            if _is_excluded(mi.file):
                continue
            detected = False
            for lang, extensions in LANGUAGE_EXTENSIONS.items():
                if any(mi.file.endswith(ext) for ext in extensions):
                    langs[lang] += 1
                    detected = True
                    break
            if not detected:
                ext = Path(mi.file).suffix.lower()
                if ext:
                    langs[ext.lstrip('.')] += 1
        if not langs:
            return "unknown"
        sorted_langs = sorted(langs.items(), key=lambda x: -x[1])
        return ",".join(f"{lang}:{count}" for lang, count in sorted_langs)

    def render_health(self, ctx: Dict[str, Any]) -> List[str]:
        """Render health section."""
        issues = ctx["health"]
        if not issues:
            return ["HEALTH[0]: ok"]
        lines = [f"HEALTH[{len(issues)}]:"]
        for issue in issues:
            icon = "\U0001f534" if issue["severity"] == "red" else "\U0001f7e1"
            lines.append(f"  {icon} {issue['code']:5s} {issue['message']}")
        return lines

    def render_refactor(self, ctx: Dict[str, Any]) -> List[str]:
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

    def render_coupling(self, ctx: Dict[str, Any]) -> List[str]:
        """Render coupling section."""
        matrix = ctx["coupling_matrix"]
        pkg_fan = ctx["pkg_fan"]
        if not matrix:
            return ["COUPLING: no cross-package imports detected"]

        top_pkgs = self._select_top_packages(matrix, pkg_fan)
        if not top_pkgs:
            return ["COUPLING: n/a"]

        lines = self._render_coupling_header(top_pkgs)
        self._render_coupling_rows(top_pkgs, matrix, pkg_fan, lines)
        self._render_coupling_summary(ctx, pkg_fan, lines)
        return lines

    def _select_top_packages(self, matrix: Dict, pkg_fan: Dict) -> List[str]:
        """Select top packages by activity (fan-in + fan-out)."""
        all_pkgs = sorted({p for pair in matrix for p in pair})
        if not all_pkgs:
            return []
        pkg_activity = [(p, pkg_fan.get(p, {}).get("fan_in", 0) + pkg_fan.get(p, {}).get("fan_out", 0)) for p in all_pkgs]
        pkg_activity.sort(key=lambda x: x[1], reverse=True)
        return [p for p, _ in pkg_activity[:MAX_COUPLING_PACKAGES]]

    def _render_coupling_header(self, top_pkgs: List[str]) -> List[str]:
        """Render coupling matrix header row."""
        col_w = max(max(len(p) for p in top_pkgs), 6)
        pad = max(len(p) for p in top_pkgs) + 2
        hdr = f"{'':>{pad}}  " + "  ".join(f"{p:>{col_w}}" for p in top_pkgs)
        return ["COUPLING:", hdr]

    def _render_coupling_rows(self, top_pkgs: List[str], matrix: Dict, pkg_fan: Dict, lines: List[str]) -> None:
        """Render one matrix row per source package."""
        col_w = max(max(len(p) for p in top_pkgs), 6)
        pad = max(len(p) for p in top_pkgs) + 2
        for src in top_pkgs:
            row_parts = self._build_coupling_row(src, top_pkgs, matrix, col_w)
            tag = self._coupling_row_tag(src, pkg_fan)
            lines.append(f"  {src:>{pad-2}}  " + "  ".join(row_parts) + tag)

    @staticmethod
    def _build_coupling_row(src: str, top_pkgs: List[str], matrix: Dict, col_w: int) -> List[str]:
        """Build cell values for a single coupling matrix row."""
        row_parts = []
        for dst in top_pkgs:
            if src == dst:
                row_parts.append(f"{'──':>{col_w}}")
            else:
                val = matrix.get((src, dst), 0)
                cell = str(val) if val else ""
                if not val:
                    rev = matrix.get((dst, src), 0)
                    cell = f"←{rev}" if rev else ""
                row_parts.append(f"{cell:>{col_w}}")
        return row_parts

    @staticmethod
    def _coupling_row_tag(src: str, pkg_fan: Dict) -> str:
        """Determine row tag (hub / fan-out warning)."""
        fi = pkg_fan.get(src, {}).get("fan_in", 0)
        fo = pkg_fan.get(src, {}).get("fan_out", 0)
        if fi >= 5:
            return "  hub"
        if fo >= 8:
            return "  !! fan-out"
        return ""

    @staticmethod
    def _render_coupling_summary(ctx: Dict[str, Any], pkg_fan: Dict, lines: List[str]) -> None:
        """Render coupling summary: cycles, hubs, smells."""
        ncycles = len(ctx["cycles"])
        lines.append(f"  CYCLES: {'none' if ncycles == 0 else ncycles}")
        for h, d in pkg_fan.items():
            if d.get("fan_in", 0) >= 5:
                lines.append(f"  HUB: {h}/ (fan-in={d['fan_in']})")
        for s, d in pkg_fan.items():
            if d.get("fan_out", 0) >= 8:
                lines.append(f"  SMELL: {s}/ fan-out={d['fan_out']} → split needed")

    def render_layers(self, ctx: Dict[str, Any]) -> List[str]:
        """Render LAYERS section — files grouped by package with metrics."""
        files = ctx["files"]
        packages = ctx["packages"]
        pkg_fan = ctx["pkg_fan"]
        dup_files = _dup_file_set(ctx)

        pkg_order = sorted(
            packages.keys(),
            key=lambda p: packages[p].get("avg_cc", 0),
            reverse=True,
        )

        lines = ["LAYERS:"]
        for pkg in pkg_order:
            self._render_layer_package(pkg, packages[pkg], pkg_fan, ctx, lines)
            self._render_layer_files(pkg, files, dup_files, lines)
            lines.append(f"  │")

        self._render_zero_line_files(files, lines)
        return lines

    def _render_layer_package(self, pkg: str, pd: Dict, pkg_fan: Dict, ctx: Dict, lines: List[str]) -> None:
        """Render a single package header line in LAYERS."""
        fi = pkg_fan.get(pkg, {}).get("fan_in", 0)
        fo = pkg_fan.get(pkg, {}).get("fan_out", 0)
        markers = "  !! split" if fo >= 8 else ""
        pkg_dups = any(
            d["fileA"].startswith(pkg + "/") or d["fileB"].startswith(pkg + "/")
            for d in ctx["duplicates"]
        )
        if pkg_dups:
            markers += "  ×DUP"
        lines.append(
            f"  {pkg + '/':30s}  CC̄={pd['avg_cc']:<5}  "
            f"←in:{fi}  →out:{fo}{markers}"
        )

    def _render_layer_files(self, pkg: str, files: Dict, dup_files: set, lines: List[str]) -> None:
        """Render file rows for a single package in LAYERS."""
        pkg_files = [
            (fpath, fm) for fpath, fm in files.items()
            if fm["rel"].startswith(pkg + "/") or (pkg == "." and "/" not in fm["rel"])
        ]
        pkg_files.sort(key=lambda x: x[1]["lines"], reverse=True)
        for fpath, fm in pkg_files:
            lines.append(self._format_layer_file_row(fm, dup_files))

    @staticmethod
    def _format_layer_file_row(fm: Dict, dup_files: set) -> str:
        """Format a single file row in LAYERS section."""
        rel = fm["rel"]
        short = rel.split("/")[-1] if "/" in rel else rel
        if short.endswith(".py"):
            short = short[:-3]
        lc, mcc, fin = fm["lines"], fm["max_cc"], fm["fan_in"]
        severity = "!! " if (lc >= GOD_MODULE_LINES or mcc >= CC_WARNING) else ("!  " if mcc >= CC_CRITICAL else "")
        dup_mark = "  ×DUP" if rel in dup_files else ""
        return (
            f"  │ {severity}{short:24s} {lc:>5}L  {fm['class_count']}C  {fm['methods']:>3}m"
            f"  CC={mcc:<5}  ←{fin}{dup_mark}"
        )

    @staticmethod
    def _render_zero_line_files(files: Dict, lines: List[str]) -> None:
        """Render zero-line files at the end of LAYERS."""
        zero = [(fpath, fm) for fpath, fm in files.items() if fm["lines"] == 0]
        if zero:
            lines.append("  ── zero ──")
            for fpath, fm in sorted(zero, key=lambda x: x[1]["rel"]):
                lines.append(f"     {fm['rel']:40s}  0L")

    def render_duplicates(self, ctx: Dict[str, Any]) -> List[str]:
        """Render duplicates section."""
        dupes = ctx["duplicates"]
        if not dupes:
            return ["DUPLICATES[0]: none"]
        lines = [f"DUPLICATES[{len(dupes)}]:"]
        for d in dupes:
            lines.append(f"  {d['class_name']}  {d['fileA']} ↔ {d['fileB']}")
            lines.append(f"    A: {d['countA']}m  {' '.join(d['methodsA'][:8])}")
            lines.append(f"    B: {d['countB']}m  {' '.join(d['methodsB'][:8])}")
            recommend = ""
            if d["diff"] == "IDENTICAL":
                recommend = " → rm B"
            elif d["diff"].startswith("A has"):
                recommend = " → keep A"
            elif d["diff"].startswith("B has"):
                recommend = " → keep B"
            lines.append(f"    DIFF: {d['diff']}{recommend}")
        return lines

    def render_functions(self, ctx: Dict[str, Any]) -> List[str]:
        """Render FUNCTIONS section — only CC >= threshold."""
        all_funcs = ctx["func_metrics"]
        critical = [f for f in all_funcs if f["cc"] >= CC_CRITICAL]
        total = len(all_funcs)
        dup_classes = {d["class_name"] for d in ctx["duplicates"]}

        if not critical:
            return [f"FUNCTIONS (CC≥{CC_CRITICAL}, 0 of {total}): none"]

        lines = [f"FUNCTIONS (CC≥{CC_CRITICAL}, {len(critical)} of {total}):"]
        for fm in critical[:MAX_FUNCTIONS_SHOWN]:
            lines.append(self._format_function_row(fm, dup_classes))

        self._render_cc_summary(all_funcs, total, lines)
        return lines

    @staticmethod
    def _format_function_row(fm: Dict, dup_classes: set) -> str:
        """Format a single function row."""
        display = f"{fm['class_name']}.{fm['name']}" if fm["class_name"] else fm["name"]
        traits = "+".join(fm["traits"]) if fm["traits"] else ""
        exits_s = f"{fm['exits']}exit" if fm["exits"] else ""
        markers = ""
        if fm["class_name"] and fm["class_name"] in dup_classes:
            markers += "  ×DUP"
        if fm["cc"] >= CC_WARNING:
            markers += "  !! split"
        return (
            f"  {fm['cc']:>5.1f}  {display:40s}  {fm['nodes']:>3}n"
            f"  {exits_s:>6s}  {traits}{markers}"
        )

    @staticmethod
    def _render_cc_summary(all_funcs: List[Dict], total: int, lines: List[str]) -> None:
        """Render CC distribution summary."""
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
            f"    critical(≥{CC_CRITICAL}): {cc_bins['critical']}"
            f" | high({CC_HIGH}-{CC_CRITICAL}): {cc_bins['high']}"
            f" | medium(2-{CC_HIGH}): {cc_bins['medium']}"
            f" | low(<2): {cc_bins['low']}"
        )
        lines.append(f"    {pct_crit}% CC≥{CC_CRITICAL}  {pct_high}% CC≥{CC_HIGH}")

    def render_hotspots(self, ctx: Dict[str, Any]) -> List[str]:
        """Render hotspots section."""
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

    def render_classes(self, ctx: Dict[str, Any]) -> List[str]:
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
            bar = "█" * bar_len

            markers = ""
            if max_cc >= CC_WARNING:
                markers += "  !!"
            dup_count = sum(1 for d in ctx["duplicates"] if d["class_name"] == name)
            if dup_count > 0:
                markers += f"  ×{dup_count}"

            lines.append(
                f"  {name:30s} {bar:<{bar_max}}  {mc:>2}m  CC̄={avg_cc:<4}  max={max_cc:<4}{markers}"
            )

        return lines

    def render_pipelines(self, ctx: Dict[str, Any]) -> List[str]:
        """Render PIPELINES section - data flow pipelines from entry points."""
        result: AnalysisResult = ctx["result"]
        
        # Find entry points and their downstream pipelines
        pipelines = []
        for func_name, func_info in result.functions.items():
            # Entry points: functions with no callers but have calls
            if not func_info.called_by and func_info.calls:
                chain = self._trace_pipeline(func_name, result, depth=0)
                if chain:
                    pipelines.append({
                        "entry": func_name.split(".")[-1],
                        "chain": chain,
                        "purity": self._calculate_purity(chain, result),
                    })
        
        if not pipelines:
            return ["PIPELINES[0]: none detected"]
        
        lines = [f"PIPELINES[{len(pipelines)}]:"]
        for i, pipe in enumerate(pipelines[:5], 1):  # Max 5 pipelines
            purity_pct = int(pipe["purity"] * 100)
            chain_str = " → ".join(pipe["chain"][:4])  # Show first 4 steps
            if len(pipe["chain"]) > 4:
                chain_str += f" → ...({len(pipe['chain']) - 4} more)"
            lines.append(f"  [{i}] Src [{pipe['entry']}]: {chain_str}")
            lines.append(f"      PURITY: {purity_pct}% pure")
        
        return lines
    
    def _trace_pipeline(self, start_func: str, result: AnalysisResult, depth: int) -> List[str]:
        """Trace a pipeline starting from an entry point."""
        if depth > 10:  # Prevent infinite recursion
            return []
        
        chain = []
        current = start_func
        visited = set()
        
        while current and current not in visited and len(chain) < 20:
            visited.add(current)
            func_info = result.functions.get(current)
            if not func_info:
                break
            
            chain.append(current.split(".")[-1])
            
            # Follow the first call that's not a builtin
            next_func = None
            for callee in func_info.calls:
                if callee in result.functions:
                    next_func = callee
                    break
            
            current = next_func
        
        return chain
    
    def _calculate_purity(self, chain: List[str], result: AnalysisResult) -> float:
        """Calculate purity ratio (functions without side effects)."""
        if not chain:
            return 0.0
        
        pure_count = 0
        for func_name in chain:
            full_name = None
            for qname, fi in result.functions.items():
                if fi.name == func_name:
                    full_name = qname
                    break
            
            if full_name:
                func_info = result.functions.get(full_name)
                if func_info and not getattr(func_info, 'has_side_effects', False):
                    pure_count += 1
        
        return pure_count / len(chain)

    def render_external(self, ctx: Dict[str, Any]) -> List[str]:
        """Render EXTERNAL section - cross-references to other tools."""
        lines = ["EXTERNAL:"]
        lines.append("  validation: run `vallm batch .` → validation.toon")
        lines.append("  duplication: run `redup scan .` → duplication.toon")
        return lines
