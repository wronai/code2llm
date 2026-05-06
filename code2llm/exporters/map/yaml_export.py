"""Map exporter YAML export — export to map.toon.yaml (structured YAML format)."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import yaml

from code2llm.core.models import AnalysisResult

from .utils import file_line_count, detect_languages, count_total_lines, rel_path


def export_to_yaml(result: AnalysisResult, output_path: str, is_excluded_path) -> None:
    """Export analysis result to map.toon.yaml format (structured YAML)."""
    project_name = Path(result.project_path).name if result.project_path else "project"
    langs = detect_languages(result, is_excluded_path)

    included_funcs = [fi for fi in result.functions.values() if not is_excluded_path(fi.file)]
    included_files = [mi for mi in result.modules.values() if not is_excluded_path(mi.file)]
    total_lines = count_total_lines(result, is_excluded_path)

    modules_data = [
        _build_module_entry(mi, result, is_excluded_path)
        for _mname, mi in sorted(result.modules.items())
        if not is_excluded_path(mi.file)
    ]

    data = {
        "format": "map-toon-yaml",
        "project": project_name,
        "timestamp": datetime.now().strftime("%Y-%m-%d"),
        "stats": {
            "files": len(included_files),
            "lines": total_lines,
            "functions": len(included_funcs),
            "languages": langs,
        },
        "modules": modules_data,
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def _build_module_entry(mi: "ModuleInfo", result: AnalysisResult, is_excluded_path) -> Dict[str, Any]:
    """Build the YAML dict for a single module."""
    rel = rel_path(mi.file, result.project_path)
    lc = file_line_count(mi.file)
    return {
        "path": rel,
        "lines": lc,
        "imports": sorted(mi.imports) if mi.imports else [],
        "exports": _build_module_exports(mi, result),
        "classes": _build_module_classes_data(mi, result),
        "functions": _build_module_functions_data(mi, result),
    }


def _build_module_exports(mi: "ModuleInfo", result: AnalysisResult) -> List[Dict]:
    """Return export list (classes + standalone functions) for a module."""
    exports: List[Dict] = []
    for cq in mi.classes:
        ci = result.classes.get(cq)
        if ci:
            exports.append({"type": "class", "name": ci.name})
    for fq in mi.functions:
        fi = result.functions.get(fq)
        if fi and not fi.class_name:
            exports.append({"type": "function", "name": fi.name})
    return exports


def _build_module_classes_data(mi: "ModuleInfo", result: AnalysisResult) -> List[Dict]:
    """Return class list with method arities for a module."""
    classes_data: List[Dict] = []
    for cq in mi.classes:
        ci = result.classes.get(cq)
        if not ci:
            continue
        methods = []
        for mq in ci.methods:
            fi = result.functions.get(mq)
            if fi:
                arity = len(fi.args) - (1 if fi.is_method else 0)
                methods.append({"name": fi.name, "arity": arity})
        classes_data.append({"name": ci.name, "bases": ci.bases, "methods": methods})
    return classes_data


def _build_module_functions_data(mi: "ModuleInfo", result: AnalysisResult) -> List[Dict]:
    """Return standalone function list for a module."""
    functions_data: List[Dict] = []
    for fq in mi.functions:
        fi = result.functions.get(fq)
        if fi and not fi.class_name:
            functions_data.append({
                "name": fi.name,
                "args": [a for a in fi.args if a != "self"],
                "returns": fi.returns or None,
            })
    return functions_data


__all__ = ['export_to_yaml']
