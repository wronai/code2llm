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
_DEFAULT_TTL_DAYS = 1.0
# Opt-out via env var: CODE2LLM_AUTO_CLEANUP=0 disables automatic TTL-based
# cleanup on PersistentCache initialisation. Override TTL via
# CODE2LLM_CACHE_TTL_DAYS (accepts fractional days, e.g. "0.5").
_ENV_AUTO_CLEANUP = "CODE2LLM_AUTO_CLEANUP"
_ENV_TTL_DAYS = "CODE2LLM_CACHE_TTL_DAYS"

def _pack(obj: Any) -> bytes:
    # Always pickle: analysis results contain dataclasses (ModuleInfo,
    # FunctionInfo, ...) and graph objects that msgpack cannot serialize
    # natively. Falling back to pickle unconditionally keeps the cache
    # correct; the speed/size delta is negligible for our payloads.
    return pickle.dumps(obj, protocol=4)


def _unpack(data: bytes) -> Any:
    return pickle.loads(data)


_EXT = "pkl"


class PersistentCache:
    """Content-addressed persistent cache stored in ~/.code2llm/.

    Thread-safety: manifest writes are protected by an atomic rename.
    Parallel processes may write the same file entry concurrently — this is
    safe because entries are immutable once written (content-addressed).
    """

    def __init__(
        self,
        project_dir: str,
        cache_root: Optional[str] = None,
        auto_cleanup: Optional[bool] = None,
        ttl_days: Optional[float] = None,
    ):
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

        # Resolve cleanup policy: explicit arg > env var > default.
        if auto_cleanup is None:
            auto_cleanup = os.environ.get(_ENV_AUTO_CLEANUP, "1") != "0"
        if ttl_days is None:
            try:
                ttl_days = float(os.environ.get(_ENV_TTL_DAYS, _DEFAULT_TTL_DAYS))
            except ValueError:
                ttl_days = _DEFAULT_TTL_DAYS
        if auto_cleanup:
            try:
                self.auto_cleanup(ttl_days=ttl_days)
            except Exception as exc:
                # Never let cleanup errors break analysis.
                logger.debug("auto_cleanup failed: %s", exc)

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

    def prune_missing(self, current_filepaths: List[str]) -> List[str]:
        """Remove manifest entries for files not present in *current_filepaths*.

        Keeps the manifest in sync with the real project state so that a
        deleted source file invalidates the export-level cache (the
        per-file cache key is content-addressed, but the export-level cache
        key is derived from the manifest and therefore must shrink when
        files disappear).

        Returns the list of relative paths that were removed.
        """
        current_rel = {
            os.path.relpath(fp, self._project_dir) for fp in current_filepaths
        }
        files_index = self._manifest["files"]
        stale = [rel for rel in files_index if rel not in current_rel]
        if not stale:
            return []
        for rel in stale:
            files_index.pop(rel, None)
        self._dirty = True
        return stale

    # ------------------------------------------------------------------
    # Export-level cache
    # ------------------------------------------------------------------

    def get_export_cache_dir(self, config_dict: Dict) -> Optional[Path]:
        """Return path to a complete cached export, or None if stale/absent.

        Safety: when the per-file manifest is empty we cannot reliably key
        the run (hash collapses to md5("{}")), so we refuse to return a
        cached export. This avoids propagating stale content from an earlier
        run after the per-file cache was cleared or never populated.
        """
        if not self._manifest.get("files"):
            return None
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

    def _cleanup_stale_exports(self, cutoff: float) -> int:
        """Remove export directories older than *cutoff*.

        Returns the number of removed export directories.
        """
        removed = 0
        if not self._exports_dir.exists():
            return removed
        for export_dir in list(self._exports_dir.iterdir()):
            if not export_dir.is_dir():
                continue
            complete = export_dir / "_complete"
            try:
                if complete.exists():
                    ts = float(complete.read_text())
                else:
                    ts = export_dir.stat().st_mtime
                if ts < cutoff:
                    shutil.rmtree(export_dir, ignore_errors=True)
                    removed += 1
            except (ValueError, OSError):
                pass
        return removed

    def _cleanup_orphaned_files(self, cutoff: float, known: set) -> int:
        """Remove orphaned file-level cache entries older than *cutoff*.

        *known* is a set of hash stems still referenced by the manifest.
        Returns the number of removed files.
        """
        removed = 0
        if not self._files_dir.exists():
            return removed
        for f in list(self._files_dir.iterdir()):
            if not f.is_file():
                continue
            if f.stem in known:
                continue  # still referenced
            try:
                if f.stat().st_mtime < cutoff:
                    f.unlink()
                    removed += 1
            except OSError:
                pass
        return removed

    def auto_cleanup(self, ttl_days: float = _DEFAULT_TTL_DAYS) -> Dict[str, int]:
        """Remove stale cache artefacts older than *ttl_days*.

        Runs automatically on `__init__` (opt-out via env var
        `CODE2LLM_AUTO_CLEANUP=0`). Prevents unbounded disk growth while
        keeping content-addressed file cache entries that are still
        referenced by the manifest.

        What is removed:
          - Export directories with a `_complete` stamp older than TTL,
            or export dirs never marked complete whose mtime is older
            than TTL (dead/abandoned runs).
          - File-level cache entries (`files/*.pkl`) whose mtime is older
            than TTL AND whose hash is no longer referenced by the
            manifest (orphaned). Referenced entries are kept regardless
            of age — they represent content still present in the project.

        Returns a dict summary `{"exports": n, "files": n}` for logging.
        """
        cutoff = time.time() - (ttl_days * 86400)
        known = {v.get("hash") for v in self._manifest.get("files", {}).values()}
        removed = {
            "exports": self._cleanup_stale_exports(cutoff),
            "files": self._cleanup_orphaned_files(cutoff, known),
        }

        if removed["exports"] or removed["files"]:
            logger.debug(
                "auto_cleanup: removed %d exports, %d orphan file entries "
                "(ttl=%.1fd, project=%s)",
                removed["exports"], removed["files"], ttl_days, self._project_dir,
            )
        return removed

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
