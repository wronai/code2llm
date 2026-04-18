"""Core ProjectYAMLExporter class — orchestrates all builders."""

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import yaml

from code2llm.core.models import AnalysisResult
from code2llm.core.config import LANGUAGE_EXTENSIONS
from code2llm.exporters.base import Exporter

from code2llm.exporters.toon.helpers import _is_excluded, _scan_line_counts, _rel_path
from .constants import GOD_MODULE_LINES
from .health import build_health
from .modules import build_modules
from .hotspots import build_hotspots, build_refactoring
from .evolution import build_evolution, load_previous_evolution


class ProjectYAMLExporter(Exporter):
    """Export unified project.yaml — single source of truth for diagnostics.

    Combines data from analysis.toon, project.toon.yaml, context.md, and evolution.toon.yaml
    into one machine-parseable YAML file.
    """

    def export(self, result: AnalysisResult, output_path: str, **kwargs) -> None:
        """Generate project.yaml from AnalysisResult.

        If the file already exists, the evolution section is appended (not replaced).
        """
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        # Load previous evolution entries if file exists
        prev_evolution = load_previous_evolution(output)

        data = self._build_project_yaml(result, prev_evolution)

        with open(output, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def _build_project_yaml(
        self, result: AnalysisResult, prev_evolution: List[Dict]
    ) -> Dict[str, Any]:
        """Build complete project.yaml structure."""
        line_counts = _scan_line_counts(result.project_path)
        # Filter out venv/site-packages/etc — only count lines of non-excluded files
        filtered_lines = {
            k: v for k, v in line_counts.items()
            if not _is_excluded(k)
        }
        total_lines = sum(filtered_lines.values()) // 2  # keys stored twice (abs + rel)

        modules = build_modules(result, line_counts)
        health = build_health(result, modules)
        hotspots = build_hotspots(result)
        refactoring = build_refactoring(result, modules, hotspots)
        evolution = build_evolution(health, total_lines, prev_evolution)

        return {
            "version": "1",
            "project": {
                "name": Path(result.project_path).name if result.project_path else "unknown",
                "repo": result.project_path or "",
                "language": self._detect_primary_language(result),
                "analyzed_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "tool": "code2llm",
                "stats": {
                    "files": len(set(
                        fi.file for fi in result.functions.values()
                        if not _is_excluded(fi.file)
                    )) or len(result.modules),
                    "lines": total_lines,
                    "functions": len([
                        f for f in result.functions.values()
                        if not _is_excluded(f.file)
                    ]),
                    "classes": len([
                        c for c in result.classes.values()
                        if not _is_excluded(c.file)
                    ]),
                },
            },
            "health": health,
            "modules": modules,
            "hotspots": hotspots,
            "refactoring": refactoring,
            "evolution": evolution,
        }

    def _detect_primary_language(self, result: AnalysisResult) -> str:
        """Detect the primary language of the project based on file counts."""
        lang_counts: Dict[str, int] = defaultdict(int)

        # Count files by language
        for mi in result.modules.values():
            if _is_excluded(mi.file):
                continue
            detected = False
            for lang, extensions in LANGUAGE_EXTENSIONS.items():
                if any(mi.file.endswith(ext) for ext in extensions):
                    lang_counts[lang] += 1
                    detected = True
                    break
            if not detected:
                # Fallback to extension
                ext = Path(mi.file).suffix.lstrip('.').lower()
                if ext:
                    lang_counts[ext] += 1

        if not lang_counts:
            return "unknown"

        # Return the most common language
        return max(lang_counts.items(), key=lambda x: x[1])[0]
