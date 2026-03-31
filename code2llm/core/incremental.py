"""Incremental analysis — hash-based skip for unchanged files.

On repeated runs, files whose mtime+size match the cached state are skipped,
and their previous analysis results are reused. This dramatically speeds up
CI/CD and iterative development workflows.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

CACHE_FILE = ".code2llm_incremental.json"


def _file_signature(filepath: str) -> Tuple[int, int]:
    """Return (mtime_ns, size) for a file — fast freshness check."""
    try:
        s = os.stat(filepath)
        return (s.st_mtime_ns, s.st_size)
    except OSError:
        return (0, 0)


class IncrementalAnalyzer:
    """Track file signatures to skip unchanged files on subsequent runs.

    Usage::

        inc = IncrementalAnalyzer(project_dir)

        for filepath in files:
            if inc.needs_analysis(filepath):
                result = analyze(filepath)
                inc.update(filepath, result)
            else:
                result = inc.get_cached_result(filepath)

        inc.save()  # persist state for next run
    """

    def __init__(self, project_dir: str):
        self._project_dir = Path(project_dir).resolve()
        self._cache_path = self._project_dir / CACHE_FILE
        self._state: Dict[str, Dict[str, Any]] = self._load_cache()
        self._dirty = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def needs_analysis(self, filepath: str) -> bool:
        """Return True if file has changed since last cached analysis."""
        key = self._normalize_key(filepath)
        sig = _file_signature(filepath)

        cached = self._state.get(key)
        if not cached:
            return True

        cached_sig = (cached.get("mtime_ns", 0), cached.get("size", 0))
        return sig != cached_sig

    def get_cached_result(self, filepath: str) -> Optional[Dict]:
        """Return previously cached analysis result, or None."""
        key = self._normalize_key(filepath)
        cached = self._state.get(key)
        if cached:
            return cached.get("result")
        return None

    def update(self, filepath: str, result: Dict) -> None:
        """Store analysis result and file signature for future runs."""
        key = self._normalize_key(filepath)
        sig = _file_signature(filepath)

        self._state[key] = {
            "mtime_ns": sig[0],
            "size": sig[1],
            "result": result,
        }
        self._dirty = True

    def invalidate(self, filepath: str) -> None:
        """Remove cached state for a file (e.g. after deletion)."""
        key = self._normalize_key(filepath)
        if key in self._state:
            del self._state[key]
            self._dirty = True

    def save(self) -> None:
        """Persist incremental state to disk."""
        if not self._dirty:
            return

        try:
            # Write atomically via temp file
            tmp_path = self._cache_path.with_suffix(".tmp")
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self._state, f, indent=2, default=str)
            tmp_path.replace(self._cache_path)
            self._dirty = False
            logger.debug("Saved incremental cache: %d files", len(self._state))
        except OSError as e:
            logger.warning("Cannot save incremental cache: %s", e)

    def clear(self) -> None:
        """Clear all cached state (force full re-analysis)."""
        self._state.clear()
        self._dirty = True
        if self._cache_path.exists():
            try:
                self._cache_path.unlink()
            except OSError:
                pass

    @property
    def cached_count(self) -> int:
        """Number of files in cache."""
        return len(self._state)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _load_cache(self) -> Dict[str, Dict[str, Any]]:
        """Load previous cache from disk, or return empty dict."""
        if not self._cache_path.exists():
            return {}

        try:
            with open(self._cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except (OSError, json.JSONDecodeError) as e:
            logger.debug("Cannot load incremental cache: %s", e)

        return {}

    def _normalize_key(self, filepath: str) -> str:
        """Normalize filepath to relative path from project root."""
        try:
            return str(Path(filepath).resolve().relative_to(self._project_dir))
        except ValueError:
            # File outside project — use absolute path
            return str(Path(filepath).resolve())
