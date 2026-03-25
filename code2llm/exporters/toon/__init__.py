"""TOON exporter - split into modular components."""

import yaml
from pathlib import Path
from typing import Any, Dict, List

from code2llm.core.models import AnalysisResult

from .metrics import MetricsComputer
from .renderer import ToonRenderer
from .helpers import _is_excluded, _rel_path, _package_of, _package_of_module, _traits_from_cfg, _dup_file_set, _hotspot_description, _scan_line_counts

# Re-export constants for backward compatibility
EXCLUDE_PATTERNS = {
    'venv', '.venv', 'env', '.env', 'publish-env', 'test-env',
    'site-packages', 'node_modules', '__pycache__', '.git',
    'dist', 'build', 'egg-info', '.tox', '.mypy_cache',
    'TODO', 'examples',
}

MAX_HEALTH_ISSUES = 20
MAX_COUPLING_PACKAGES = 15
MAX_FUNCTIONS_SHOWN = 50


class ToonExporter:
    """Export to toon v2 plain-text format — scannable, sorted by severity."""

    def __init__(self):
        self.metrics_computer = MetricsComputer()
        self.renderer = ToonRenderer()

    def export(self, result: AnalysisResult, output_path: str, **kwargs) -> None:
        """Export analysis result to toon v2 format."""
        ctx = self.metrics_computer.compute_all_metrics(result)

        sections: List[str] = []
        sections.extend(self.renderer.render_header(ctx))
        sections.append("")
        sections.extend(self.renderer.render_health(ctx))
        sections.append("")
        sections.extend(self.renderer.render_refactor(ctx))
        sections.append("")
        sections.extend(self.renderer.render_pipelines(ctx))
        sections.append("")
        sections.extend(self.renderer.render_layers(ctx))
        sections.append("")
        sections.extend(self.renderer.render_coupling(ctx))
        sections.append("")
        sections.extend(self.renderer.render_external(ctx))

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(sections) + "\n")

    def export_to_yaml(self, result: AnalysisResult, output_path: str, **kwargs) -> None:
        """Export analysis result to toon.yaml format (structured YAML)."""
        ctx = self.metrics_computer.compute_all_metrics(result)

        # Build structured YAML data mirroring TOON sections
        data: Dict[str, Any] = {
            "format": "toon-v2-yaml",
            "timestamp": ctx.get("timestamp", ""),
            "header": self._build_header_dict(ctx),
            "health": self._build_health_dict(ctx),
            "refactor": self._build_refactor_dict(ctx),
            "pipelines": self._build_pipelines_dict(ctx),
            "layers": self._build_layers_dict(ctx),
            "coupling": self._build_coupling_dict(ctx),
            "external": self._build_external_dict(ctx),
        }

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def _build_header_dict(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Build header section as dict."""
        result = ctx["result"]
        nfiles = len(ctx["files"])
        total_lines = sum(fm["lines"] for fm in ctx["files"].values())
        nfuncs = len(result.functions)
        all_cc = [f["cc"] for f in ctx["func_metrics"]]
        avg_cc = round(sum(all_cc) / len(all_cc), 1) if all_cc else 0.0
        critical = len([f for f in ctx["func_metrics"] if f["cc"] >= 15])

        return {
            "files": nfiles,
            "lines": total_lines,
            "functions": nfuncs,
            "avg_cc": avg_cc,
            "critical_count": critical,
            "duplicates": len(ctx["duplicates"]),
            "cycles": len(ctx["cycles"]),
        }

    def _build_health_dict(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Build health section as dict."""
        issues = ctx["health"]
        return {
            "count": len(issues),
            "status": "ok" if not issues else "issues_found",
            "issues": [
                {
                    "severity": issue["severity"],
                    "code": issue["code"],
                    "message": issue["message"],
                }
                for issue in issues[:20]
            ],
        }

    def _build_refactor_dict(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Build refactor section as dict."""
        steps = []
        if ctx["duplicates"]:
            steps.append({"action": "remove_duplicates", "count": len(ctx["duplicates"])})

        god_issues = [h for h in ctx["health"] if h["code"] == "GOD"]
        for gi in god_issues:
            steps.append({"action": "split_module", "target": gi["message"].split("=")[0].strip()})

        cc_issues = [h for h in ctx["health"] if h["code"] == "CC"]
        if cc_issues:
            steps.append({"action": "split_methods", "count": len(cc_issues), "reason": "high_cc"})

        if ctx["cycles"]:
            steps.append({"action": "break_cycles", "count": len(ctx["cycles"])})

        return {"steps": steps}

    def _build_pipelines_dict(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Build pipelines section as dict."""
        pipelines = ctx.get("pipelines", [])
        return {
            "count": len(pipelines),
            "pipelines": [
                {
                    "name": p["name"],
                    "functions": p.get("functions", []),
                    "entry": p.get("entry", ""),
                    "exit": p.get("exit", ""),
                }
                for p in pipelines[:10]
            ],
        }

    def _build_layers_dict(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Build layers section as dict."""
        layers = ctx.get("layers", [])
        return {
            "count": len(layers),
            "layers": [
                {
                    "name": layer["name"],
                    "modules": layer.get("modules", []),
                }
                for layer in layers[:10]
            ],
        }

    def _build_coupling_dict(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Build coupling section as dict."""
        coupling = ctx.get("coupling", [])
        return {
            "count": len(coupling),
            "packages": [
                {
                    "package": c["package"],
                    "outbound": c.get("outbound", 0),
                    "inbound": c.get("inbound", 0),
                    "strength": c.get("strength", "low"),
                }
                for c in coupling[:15]
            ],
        }

    def _build_external_dict(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Build external section as dict."""
        external = ctx.get("external", [])
        return {
            "count": len(external),
            "libraries": [
                {
                    "name": lib["name"],
                    "type": lib.get("type", "unknown"),
                    "usage_count": lib.get("usage_count", 0),
                }
                for lib in external[:20]
            ],
        }

    # Backward compatibility methods
    def _is_excluded(self, path: str) -> bool:
        """Check if path should be excluded (venv, site-packages, etc.)."""
        return _is_excluded(path)
