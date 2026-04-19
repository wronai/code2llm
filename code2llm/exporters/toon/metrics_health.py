"""Health metrics computation for TOON export.

Health issue detection: duplicates, god modules, code smells, high CC.
"""

from typing import Any, Dict, List

from code2llm.core.models import AnalysisResult


class HealthMetricsComputer:
    """Computes health issues and quality alerts."""

    def __init__(self):
        pass

    def compute_health(self, ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
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
