"""Helper utilities for TOON exporter."""

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Set

from code2llm.core.models import AnalysisResult, FunctionInfo

# Re-export is_excluded_path from flow_constants to eliminate duplication
from ..flow_constants import is_excluded_path as _is_excluded


def _rel_path(fpath: str, project_path: str) -> str:
    if not project_path or not fpath:
        return fpath or ""
    try:
        return str(Path(fpath).relative_to(Path(project_path).resolve()))
    except (ValueError, RuntimeError):
        try:
            return str(Path(fpath).relative_to(Path(project_path)))
        except (ValueError, RuntimeError):
            return fpath


def _package_of(rel_path: str) -> str:
    """Extract top-level package/directory from relative path."""
    parts = Path(rel_path).parts
    if len(parts) >= 2:
        return parts[0]
    # root-level .py files → group under "."
    return "."


def _package_of_module(module_name: str) -> str:
    """Return subpackage for coupling analysis.

    For 'code2llm.exporters.toon' returns 'code2llm.exporters'
    so cross-subpackage coupling is detected.
    """
    parts = module_name.split(".")
    if len(parts) >= 3:
        return ".".join(parts[:2])  # e.g. code2llm.exporters
    if len(parts) == 2:
        return parts[0]
    return parts[0] if parts else ""


def _traits_from_cfg(fi: FunctionInfo, result: AnalysisResult) -> list:
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


def _dup_file_set(ctx: Dict[str, Any]) -> Set[str]:
    s: Set[str] = set()
    for d in ctx["duplicates"]:
        s.add(d["fileA"])
        s.add(d["fileB"])
    return s


def _hotspot_description(fi: FunctionInfo, fan_out: int) -> str:
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


def _scan_line_counts(project_path, result=None) -> Dict[str, int]:
    """Get line counts for project files.

    Fast path: derive from AnalysisResult modules (already parsed, no extra I/O).
    Slow fallback: single os.walk pass reading files from disk.
    """
    line_counts: Dict[str, int] = {}
    if not project_path:
        return line_counts
    pp = Path(project_path)
    if not pp.is_dir():
        return line_counts

    # Fast path: use already-analyzed file data when available
    if result is not None:
        for mname, mi in getattr(result, 'modules', {}).items():
            fpath = mi.file
            if not fpath:
                continue
            try:
                lc = len(Path(fpath).read_text(encoding="utf-8", errors="ignore").splitlines())
                rel = str(Path(fpath).relative_to(pp))
                line_counts[str(fpath)] = lc
                line_counts[rel] = lc
            except Exception:
                pass
        return line_counts

    # Slow fallback: single walk instead of 73 rglob calls
    from ...core.config import ALL_EXTENSIONS
    ext_set = set(ALL_EXTENSIONS)
    for root, dirs, files in Path(project_path).walk() if hasattr(Path, 'walk') else _walk_compat(pp):
        # Prune excluded directories
        dirs[:] = [d for d in dirs if d not in {
            'venv', '.venv', 'node_modules', '__pycache__', '.git',
            'dist', 'build', '.tox', '.mypy_cache', 'egg-info',
        }]
        for fname in files:
            ext = Path(fname).suffix
            if ext not in ext_set:
                continue
            src_file = root / fname
            try:
                lc = len(src_file.read_text(encoding="utf-8", errors="ignore").splitlines())
                rel = str(src_file.relative_to(pp))
                line_counts[str(src_file)] = lc
                line_counts[rel] = lc
            except Exception:
                pass
    return line_counts


def _walk_compat(path):
    """os.walk compatibility wrapper for Path (Python < 3.12)."""
    import os
    for root, dirs, files in os.walk(path):
        yield Path(root), dirs, files
