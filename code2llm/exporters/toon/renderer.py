"""Rendering functions for TOON exporter."""

from typing import Any, Dict, List

from ...core.models import AnalysisResult, FunctionInfo

from .helpers import _dup_file_set, _package_of


# Constants
CC_CRITICAL = 10
CC_HIGH = 5
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

        lines = [
            f"# code2llm | {nfiles}f {total_lines}L | py:{nfiles} | {ctx['timestamp']}",
            f"# CC̄={avg_cc} | critical:{critical}/{nfuncs} | dups:{ndups} | cycles:{ncycles}",
        ]
        return lines

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

    def render_layers(self, ctx: Dict[str, Any]) -> List[str]:
        """Render LAYERS section — files grouped by package with metrics."""
        files = ctx["files"]
        packages = ctx["packages"]
        pkg_fan = ctx["pkg_fan"]
        dup_files = _dup_file_set(ctx)

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
                f"  {pkg + '/':30s}  CC̄={pd['avg_cc']:<5}  "
                f"←in:{fi}  →out:{fo}{markers}"
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
                    f"  │ {severity}{short:24s} {lc:>5}L  {cc_count}C  {mc:>3}m"
                    f"  CC={mcc:<5}  ←{fin}{dup_mark}"
                )
            lines.append(f"  │")

        # zero-line files
        zero = [(fpath, fm) for fpath, fm in files.items() if fm["lines"] == 0]
        if zero:
            lines.append("  ── zero ──")
            for fpath, fm in sorted(zero, key=lambda x: x[1]["rel"]):
                lines.append(f"     {fm['rel']:40s}  0L")

        return lines

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
            f"    critical(≥{CC_CRITICAL}): {cc_bins['critical']}"
            f" | high({CC_HIGH}-{CC_CRITICAL}): {cc_bins['high']}"
            f" | medium(2-{CC_HIGH}): {cc_bins['medium']}"
            f" | low(<2): {cc_bins['low']}"
        )
        lines.append(f"    {pct_crit}% CC≥{CC_CRITICAL}  {pct_high}% CC≥{CC_HIGH}")

        return lines

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
