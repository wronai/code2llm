"""Map exporter utilities — path handling, line counting, language detection."""

from functools import lru_cache
from pathlib import Path
from typing import Dict, Set
from collections import defaultdict

from code2llm.core.config import LANGUAGE_EXTENSIONS
from code2llm.core.models import AnalysisResult


@lru_cache(maxsize=4096)
def rel_path(fpath: str, project_path: str) -> str:
    """Get relative path from project root."""
    if not project_path or not fpath:
        return fpath or ""
    try:
        return str(Path(fpath).relative_to(Path(project_path).resolve()))
    except (ValueError, RuntimeError):
        try:
            return str(Path(fpath).relative_to(Path(project_path)))
        except (ValueError, RuntimeError):
            return fpath


@lru_cache(maxsize=4096)
def file_line_count(fpath: str) -> int:
    """Count lines in a file."""
    try:
        return len(Path(fpath).read_text(encoding="utf-8", errors="ignore").splitlines())
    except Exception:
        return 0


def count_total_lines(result: AnalysisResult, is_excluded_path) -> int:
    """Count total lines across all modules."""
    total = 0
    seen: Set[str] = set()
    for mi in result.modules.values():
        if mi.file and mi.file not in seen and not is_excluded_path(mi.file):
            seen.add(mi.file)
            total += file_line_count(mi.file)
    return total


def detect_languages(result: AnalysisResult, is_excluded_path) -> Dict[str, int]:
    """Detect all supported programming languages in the project."""
    langs: Dict[str, int] = defaultdict(int)
    for mi in result.modules.values():
        if is_excluded_path(mi.file):
            continue
        # Check all supported language extensions
        detected = False
        for lang, extensions in LANGUAGE_EXTENSIONS.items():
            if any(mi.file.endswith(ext) for ext in extensions):
                langs[lang] += 1
                detected = True
                break
        if not detected:
            # Fallback: try to detect from file extension
            ext = Path(mi.file).suffix.lower()
            if ext:
                langs[ext.lstrip('.')] += 1
    return dict(langs)


__all__ = [
    'rel_path',
    'file_line_count',
    'count_total_lines',
    'detect_languages',
]
