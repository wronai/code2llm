"""Evolution exporter exclusion logic — path filtering."""

from functools import lru_cache

from .constants import EXCLUDE_PATTERNS


@lru_cache(maxsize=4096)
def is_excluded(path: str) -> bool:
    """Check if path should be excluded (venv, site-packages, etc.)."""
    if not path:
        return False
    parts = set(path.lower().replace('\\', '/').split('/'))
    return bool(parts & EXCLUDE_PATTERNS)


__all__ = ['is_excluded']
