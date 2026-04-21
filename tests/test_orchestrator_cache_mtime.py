"""Regression test: cache-restored export files must have a fresh mtime.

Previously `_copy_cached_export` used `shutil.copy2` which preserves the
original mtime, making users believe the current `code2llm` run did not
produce any output (the files looked stale). The orchestrator now
touches every restored file so its mtime reflects the current run.
"""

import os
import time
from pathlib import Path

import pytest

from code2llm.cli_exports.orchestrator import _copy_cached_export


def _write(path: Path, content: str, mtime: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    os.utime(path, (mtime, mtime))


def test_copy_cached_export_refreshes_mtime(tmp_path: Path) -> None:
    cache_dir = tmp_path / "cache"
    output_dir = tmp_path / "out"

    old_mtime = time.time() - 60 * 60 * 24  # 24h ago

    _write(cache_dir / "analysis.toon.yaml", "x: 1\n", old_mtime)
    _write(cache_dir / "sub" / "inner.md", "# hi\n", old_mtime)

    before = time.time() - 1
    _copy_cached_export(cache_dir, output_dir, verbose=False)
    after = time.time() + 1

    for rel in ("analysis.toon.yaml", "sub/inner.md"):
        dest = output_dir / rel
        assert dest.exists(), f"missing {rel}"
        mtime = dest.stat().st_mtime
        assert before <= mtime <= after, (
            f"{rel} mtime {mtime} not in current run window "
            f"[{before}, {after}] (old_mtime={old_mtime})"
        )


def test_copy_cached_export_preserves_contents(tmp_path: Path) -> None:
    cache_dir = tmp_path / "cache"
    output_dir = tmp_path / "out"

    _write(cache_dir / "analysis.toon.yaml", "content: cached\n", time.time() - 10)
    _copy_cached_export(cache_dir, output_dir, verbose=False)

    assert (output_dir / "analysis.toon.yaml").read_text(encoding="utf-8") == "content: cached\n"
