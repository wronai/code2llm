"""Tests for PersistentCache."""

import json
import os
import time
import tempfile
from pathlib import Path

import pytest

from code2llm.core.persistent_cache import PersistentCache, get_all_projects, clear_all, VERSION


@pytest.fixture()
def tmp_project(tmp_path):
    """A temporary project directory with a few source files."""
    (tmp_path / "a.py").write_text("def foo(): pass\n")
    (tmp_path / "b.py").write_text("def bar(): pass\n")
    return tmp_path


@pytest.fixture()
def cache(tmp_project, tmp_path):
    """PersistentCache pointing at a separate temp cache root."""
    cache_root = tmp_path / "cache_root"
    return PersistentCache(str(tmp_project), cache_root=str(cache_root))


class TestContentHash:
    def test_same_content_same_hash(self, tmp_project, cache):
        fp = str(tmp_project / "a.py")
        assert cache.content_hash(fp) == cache.content_hash(fp)

    def test_different_content_different_hash(self, tmp_project, cache):
        a = str(tmp_project / "a.py")
        b = str(tmp_project / "b.py")
        assert cache.content_hash(a) != cache.content_hash(b)


class TestFileResultRoundtrip:
    def test_put_then_get(self, tmp_project, cache):
        fp = str(tmp_project / "a.py")
        payload = {"functions": {"foo": {"cc": 1}}, "file": fp}
        cache.put_file_result(fp, payload)
        retrieved = cache.get_file_result(fp)
        assert retrieved == payload

    def test_get_missing_returns_none(self, tmp_project, cache):
        fp = str(tmp_project / "a.py")
        assert cache.get_file_result(fp) is None

    def test_manifest_updated_after_put(self, tmp_project, cache):
        fp = str(tmp_project / "a.py")
        cache.put_file_result(fp, {"file": fp})
        rel = os.path.relpath(fp, str(tmp_project))
        assert rel in cache._manifest["files"]


class TestGetChangedFiles:
    def test_new_files_are_changed(self, tmp_project, cache):
        files = [str(tmp_project / "a.py"), str(tmp_project / "b.py")]
        changed, cached = cache.get_changed_files(files)
        assert set(changed) == set(files)
        assert cached == []

    def test_cached_file_not_changed(self, tmp_project, cache):
        fp = str(tmp_project / "a.py")
        cache.put_file_result(fp, {"file": fp})
        changed, cached = cache.get_changed_files([fp])
        assert changed == []
        assert cached == [fp]

    def test_modified_file_is_changed(self, tmp_project, cache):
        fp = str(tmp_project / "a.py")
        cache.put_file_result(fp, {"file": fp})
        # Modify content
        time.sleep(0.01)
        Path(fp).write_text("def foo(): return 42\n")
        changed, cached = cache.get_changed_files([fp])
        assert fp in changed
        assert fp not in cached


class TestExportCache:
    def test_missing_export_returns_none(self, cache):
        assert cache.get_export_cache_dir({"fmt": "toon"}) is None

    def test_complete_export_returned(self, cache):
        cfg = {"fmt": "toon", "verbose": False}
        d = cache.create_export_cache_dir(cfg)
        assert cache.get_export_cache_dir(cfg) is None  # not complete yet
        cache.mark_export_complete(d)
        assert cache.get_export_cache_dir(cfg) == d

    def test_different_config_different_dir(self, cache):
        d1 = cache.create_export_cache_dir({"fmt": "toon"})
        d2 = cache.create_export_cache_dir({"fmt": "json"})
        assert d1 != d2


class TestSaveAndReload:
    def test_save_creates_manifest(self, tmp_project, cache):
        fp = str(tmp_project / "a.py")
        cache.put_file_result(fp, {"file": fp})
        cache.save()
        assert cache._manifest_path.exists()

    def test_reload_preserves_entries(self, tmp_project, tmp_path):
        cache_root = tmp_path / "cache_root"
        fp = str(tmp_project / "a.py")
        c1 = PersistentCache(str(tmp_project), cache_root=str(cache_root))
        c1.put_file_result(fp, {"file": fp, "data": 42})
        c1.save()

        c2 = PersistentCache(str(tmp_project), cache_root=str(cache_root))
        result = c2.get_file_result(fp)
        assert result == {"file": fp, "data": 42}

    def test_version_mismatch_resets_manifest(self, tmp_project, tmp_path):
        cache_root = tmp_path / "cache_root"
        proj_hash = __import__('hashlib').md5(
            os.path.realpath(str(tmp_project)).encode()
        ).hexdigest()[:12]
        manifest_path = cache_root / "projects" / proj_hash / "manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps({"version": 0, "files": {"stale": {}}}))

        c = PersistentCache(str(tmp_project), cache_root=str(cache_root))
        assert c._manifest.get("version") == VERSION
        assert c._manifest["files"] == {}


class TestGC:
    def test_gc_removes_old_exports(self, tmp_project, cache):
        cfg = {"fmt": "toon"}
        d = cache.create_export_cache_dir(cfg)
        # Backdate _complete timestamp
        (d / "_complete").write_text(str(time.time() - 40 * 86400))
        removed = cache.gc(max_age_days=30)
        assert removed >= 1
        assert not d.exists()

    def test_gc_keeps_recent_exports(self, tmp_project, cache):
        cfg = {"fmt": "toon"}
        d = cache.create_export_cache_dir(cfg)
        cache.mark_export_complete(d)
        removed = cache.gc(max_age_days=30)
        assert removed == 0
        assert d.exists()


class TestClear:
    def test_clear_empties_manifest(self, tmp_project, cache):
        fp = str(tmp_project / "a.py")
        cache.put_file_result(fp, {"file": fp})
        cache.clear()
        assert cache._manifest["files"] == {}
        assert cache.get_file_result(fp) is None


class TestModuleLevelHelpers:
    def test_get_all_projects_empty(self, tmp_path):
        projects = get_all_projects(cache_root=str(tmp_path))
        assert projects == []

    def test_get_all_projects_after_save(self, tmp_project, tmp_path):
        cache_root = tmp_path / "root"
        c = PersistentCache(str(tmp_project), cache_root=str(cache_root))
        fp = str(tmp_project / "a.py")
        c.put_file_result(fp, {"file": fp})
        c.save()
        projects = get_all_projects(cache_root=str(cache_root))
        assert len(projects) == 1
        assert projects[0]["project"] == os.path.realpath(str(tmp_project))

    def test_clear_all(self, tmp_project, tmp_path):
        cache_root = tmp_path / "root"
        c = PersistentCache(str(tmp_project), cache_root=str(cache_root))
        c.put_file_result(str(tmp_project / "a.py"), {"x": 1})
        c.save()
        clear_all(cache_root=str(cache_root))
        assert not cache_root.exists()
