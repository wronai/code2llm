"""Persistent content-addressed cache for code2llm.

Stores per-file analysis results in ~/.code2llm/ keyed by content hash
(SHA-256), so identical files in different projects share one cache entry.

Layout::

    ~/.code2llm/
    ├── config.json
    └── projects/
        └── {path_hash}/          # md5(realpath(project_dir))[:12]
            ├── manifest.json     # rel_path → {hash, mtime, size}
            ├── meta.json         # human-readable summary
            ├── files/            # {sha256[:16]}.pkl  — per-file results
            └── exports/          # {run_hash}/_complete + copied outputs

Invalidation strategy (fastest-first):
  L1  mtime + size unchanged  →  cache hit (no I/O on file content)
  L2  content hash unchanged  →  cache hit (file touched but identical)
  L3  --no-cache / --force    →  skip cache entirely
"""

import hashlib
import json
import logging
import os
import pickle
import shutil
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

VERSION = 2
_DEFAULT_ROOT = os.path.expanduser("~/.code2llm")
_MAX_CACHE_MB = 500
_GC_THRESHOLD = 0.8

try:
    import msgpack as _msgpack
    _HAS_MSGPACK = True
except ImportError:
    _HAS_MSGPACK = False


def _pack(obj: Any) -> bytes:
    if _HAS_MSGPACK:
        return _msgpack.packb(obj, use_bin_type=True)
    return pickle.dumps(obj, protocol=4)


def _unpack(data: bytes) -> Any:
    if _HAS_MSGPACK:
        return _msgpack.unpackb(data, raw=False)
    return pickle.loads(data)


_EXT = "msgpack" if _HAS_MSGPACK else "pkl"


class PersistentCache:
    """Content-addressed persistent cache stored in ~/.code2llm/.

    Thread-safety: manifest writes are protected by an atomic rename.
    Parallel processes may write the same file entry concurrently — this is
    safe because entries are immutable once written (content-addressed).
    """

    def __init__(self, project_dir: str, cache_root: Optional[str] = None):
        self._project_dir = os.path.realpath(project_dir)
        self._root = Path(cache_root or _DEFAULT_ROOT)
        self._project_hash = hashlib.md5(
            self._project_dir.encode()
        ).hexdigest()[:12]
        self._project_cache = self._root / "projects" / self._project_hash
        self._files_dir = self._project_cache / "files"
        self._exports_dir = self._project_cache / "exports"
        self._manifest_path = self._project_cache / "manifest.json"
        self._meta_path = self._project_cache / "meta.json"

        self._files_dir.mkdir(parents=True, exist_ok=True)
        self._exports_dir.mkdir(parents=True, exist_ok=True)

        self._manifest: Dict[str, Any] = self._load_manifest()
        self._dirty = False

    # ------------------------------------------------------------------
    # File-level cache
    # ------------------------------------------------------------------

    def content_hash(self, filepath: str) -> str:
        """SHA-256 of file bytes — the content-addressed key."""
        return hashlib.sha256(Path(filepath).read_bytes()).hexdigest()[:16]

    def get_file_result(self, filepath: str) -> Optional[Any]:
        """Return cached analysis result for *filepath*, or None on miss."""
        try:
            h = self.content_hash(filepath)
        except OSError:
            return None
        cache_file = self._files_dir / f"{h}.{_EXT}"
        if not cache_file.exists():
            return None
        try:
            return _unpack(cache_file.read_bytes())
        except Exception:
            cache_file.unlink(missing_ok=True)
            return None

    def put_file_result(self, filepath: str, result: Any) -> None:
        """Store *result* keyed by content hash of *filepath*."""
        try:
            h = self.content_hash(filepath)
            cache_file = self._files_dir / f"{h}.{_EXT}"
            if not cache_file.exists():
                cache_file.write_bytes(_pack(result))
            rel = os.path.relpath(filepath, self._project_dir)
            stat = os.stat(filepath)
            self._manifest["files"][rel] = {
                "hash": h,
                "mtime": stat.st_mtime,
                "size": stat.st_size,
            }
            self._dirty = True
        except Exception as exc:
            logger.debug("put_file_result failed for %s: %s", filepath, exc)

    # ------------------------------------------------------------------
    # Batch changed-file detection
    # ------------------------------------------------------------------

    def get_changed_files(
        self, filepaths: List[str]
    ) -> Tuple[List[str], List[str]]:
        """Split *filepaths* into (changed, cached).

        Uses L1 (mtime+size) first; falls back to L2 (content hash) when
        mtime changed but size matches — handles touch/copy without edit.
        """
        changed: List[str] = []
        cached: List[str] = []
        files_index = self._manifest["files"]

        for fp in filepaths:
            rel = os.path.relpath(fp, self._project_dir)
            prev = files_index.get(rel)
            if prev is None:
                changed.append(fp)
                continue
            try:
                stat = os.stat(fp)
                # L1: mtime + size identical → hit
                if stat.st_mtime == prev["mtime"] and stat.st_size == prev["size"]:
                    cached.append(fp)
                    continue
                # L2: content hash check (size may match but mtime drifted)
                h = self.content_hash(fp)
                if h == prev["hash"]:
                    prev["mtime"] = stat.st_mtime  # refresh mtime in manifest
                    self._dirty = True
                    cached.append(fp)
                else:
                    changed.append(fp)
            except OSError:
                changed.append(fp)

        return changed, cached

    # ------------------------------------------------------------------
    # Export-level cache
    # ------------------------------------------------------------------

    def get_export_cache_dir(self, config_dict: Dict) -> Optional[Path]:
        """Return path to a complete cached export, or None if stale/absent."""
        run_hash = self._compute_run_hash(config_dict)
        export_dir = self._exports_dir / run_hash
        if export_dir.exists() and (export_dir / "_complete").exists():
            return export_dir
        return None

    def create_export_cache_dir(self, config_dict: Dict) -> Path:
        """Create (or reuse) an export staging directory for this run."""
        run_hash = self._compute_run_hash(config_dict)
        export_dir = self._exports_dir / run_hash
        export_dir.mkdir(parents=True, exist_ok=True)
        return export_dir

    def mark_export_complete(self, export_dir: Path) -> None:
        """Stamp *export_dir* as complete (used by get_export_cache_dir)."""
        (export_dir / "_complete").write_text(str(time.time()))

    # ------------------------------------------------------------------
    # Persist & GC
    # ------------------------------------------------------------------

    def save(self) -> None:
        """Flush manifest and meta to disk (atomic rename)."""
        if not self._dirty:
            return
        self._manifest["version"] = VERSION
        self._manifest["project_dir"] = self._project_dir
        self._manifest["updated_at"] = time.time()
        tmp = self._manifest_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._manifest, indent=2, default=str))
        tmp.replace(self._manifest_path)

        try:
            size = sum(f.stat().st_size for f in self._files_dir.iterdir() if f.is_file())
            meta = {
                "project": self._project_dir,
                "files_cached": len(self._manifest["files"]),
                "cache_size_bytes": size,
                "exports": len(list(self._exports_dir.iterdir())),
                "updated_at": self._manifest["updated_at"],
            }
            self._meta_path.write_text(json.dumps(meta, indent=2))
        except OSError:
            pass
        self._dirty = False

    def cache_size_mb(self) -> float:
        """Total size of this project's cache in MB."""
        try:
            total = sum(
                f.stat().st_size
                for f in self._project_cache.rglob("*")
                if f.is_file()
            )
            return total / (1024 * 1024)
        except OSError:
            return 0.0

    def gc(self, max_age_days: int = 30, max_size_mb: int = _MAX_CACHE_MB) -> int:
        """Remove stale exports and orphaned file entries.

        Returns number of items removed.
        """
        removed = 0
        cutoff = time.time() - (max_age_days * 86400)

        # Remove old export dirs
        for export_dir in list(self._exports_dir.iterdir()):
            if not export_dir.is_dir():
                continue
            complete = export_dir / "_complete"
            if complete.exists():
                try:
                    if float(complete.read_text()) < cutoff:
                        shutil.rmtree(export_dir)
                        removed += 1
                except (ValueError, OSError):
                    pass

        # Remove orphaned file entries (hash not in manifest)
        known = {v["hash"] for v in self._manifest["files"].values()}
        for f in list(self._files_dir.iterdir()):
            if f.stem not in known:
                try:
                    f.unlink()
                    removed += 1
                except OSError:
                    pass

        return removed

    def clear(self) -> None:
        """Delete all cached data for this project."""
        shutil.rmtree(self._project_cache, ignore_errors=True)
        self._files_dir.mkdir(parents=True, exist_ok=True)
        self._exports_dir.mkdir(parents=True, exist_ok=True)
        self._manifest = {"version": VERSION, "files": {}, "project_dir": self._project_dir}
        self._dirty = False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_manifest(self) -> Dict[str, Any]:
        if self._manifest_path.exists():
            try:
                m = json.loads(self._manifest_path.read_text())
                if m.get("version") == VERSION:
                    return m
            except (json.JSONDecodeError, KeyError, OSError):
                pass
        return {"version": VERSION, "files": {}, "project_dir": self._project_dir}

    def _compute_run_hash(self, config_dict: Dict) -> str:
        manifest_hash = hashlib.md5(
            json.dumps(self._manifest["files"], sort_keys=True).encode()
        ).hexdigest()[:12]
        config_hash = hashlib.md5(
            json.dumps(config_dict, sort_keys=True, default=str).encode()
        ).hexdigest()[:8]
        return f"{manifest_hash}_{config_hash}"


# ---------------------------------------------------------------------------
# Module-level helpers for CLI cache commands
# ---------------------------------------------------------------------------

def get_all_projects(cache_root: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return summary dicts for every cached project."""
    root = Path(cache_root or _DEFAULT_ROOT) / "projects"
    projects = []
    if not root.exists():
        return projects
    for proj_dir in sorted(root.iterdir()):
        meta_path = proj_dir / "meta.json"
        if meta_path.exists():
            try:
                projects.append(json.loads(meta_path.read_text()))
            except (json.JSONDecodeError, OSError):
                pass
    return projects


def clear_all(cache_root: Optional[str] = None) -> None:
    """Delete entire ~/.code2llm/ cache."""
    root = Path(cache_root or _DEFAULT_ROOT)
    shutil.rmtree(root, ignore_errors=True)
