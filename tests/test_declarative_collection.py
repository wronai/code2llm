"""Tests for IaC / declarative / documentation file collection.

The persistent cache can only invalidate the export when a file appears
in the manifest. For content-addressed invalidation to work on IaC
manifests, pyproject.toml, Dockerfile, README.md, etc., those files must
be picked up by ProjectAnalyzer._collect_files.

These tests pin the contract end-to-end:
  1. Declarative files are discovered by _collect_files.
  2. Editing them changes the persistent-cache run hash (invalidation).
  3. Dockerfile/Makefile are matched by filename, not extension.
"""

from pathlib import Path

import pytest

from code2llm.core.analyzer import ProjectAnalyzer
from code2llm.core.config import (
    ALL_EXTENSIONS, ALL_FILENAMES, DECLARATIVE_EXTENSIONS, Config,
    LANGUAGE_FILENAMES,
)
from code2llm.core.file_analyzer import FileAnalyzer
from code2llm.core.persistent_cache import PersistentCache


@pytest.fixture()
def iac_project(tmp_path):
    """Synthetic project with a representative mix of declarative files."""
    p = tmp_path / "proj"
    p.mkdir()
    (p / "Dockerfile").write_text("FROM python:3.13\nCOPY . /app\n")
    (p / "Makefile").write_text("build:\n\tpython -m build\n")
    (p / "main.tf").write_text('resource "aws_s3_bucket" "b" {}\n')
    (p / "infra.bicep").write_text("param location string = 'eastus'\n")
    (p / "k8s.yaml").write_text("apiVersion: v1\nkind: Pod\n")
    (p / "pyproject.toml").write_text('[project]\nname = "x"\n')
    (p / "package.json").write_text('{"name": "x"}\n')
    (p / "README.md").write_text("# Project\n")
    (p / "schema.proto").write_text("syntax = \"proto3\";\n")
    (p / "app.doql").write_text("query foo { bar }\n")
    # A non-declarative ignored file (binary-ish) to confirm we don't over-match
    (p / "logo.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    return p


def test_all_extensions_includes_declarative():
    """DECLARATIVE_EXTENSIONS must be merged into ALL_EXTENSIONS."""
    assert ".tf" in ALL_EXTENSIONS
    assert ".yaml" in ALL_EXTENSIONS
    assert ".md" in ALL_EXTENSIONS
    assert ".toml" in ALL_EXTENSIONS
    assert ".doql" in ALL_EXTENSIONS


def test_all_filenames_includes_dockerfile_and_makefile():
    assert "Dockerfile" in ALL_FILENAMES
    assert "Makefile" in ALL_FILENAMES
    assert "Jenkinsfile" in ALL_FILENAMES


def test_collect_files_discovers_iac(iac_project):
    cfg = Config()
    cfg.performance.parallel_enabled = False
    a = ProjectAnalyzer(cfg, iac_project)
    files = a._collect_files(iac_project)
    found = {Path(fp).name for fp, _ in files}

    # Every declarative fixture file must be picked up.
    expected = {
        "Dockerfile", "Makefile",
        "main.tf", "infra.bicep", "k8s.yaml",
        "pyproject.toml", "package.json",
        "README.md", "schema.proto", "app.doql",
    }
    missing = expected - found
    assert not missing, f"declarative files not collected: {missing}"

    # The PNG must NOT be collected (we didn't add image extensions).
    assert "logo.png" not in found


def test_modifying_declarative_file_invalidates_cache(iac_project, tmp_path):
    """Editing pyproject.toml must change the persistent-cache run hash."""
    cache_root = tmp_path / "cache_root"

    # Hook ProjectAnalyzer to use our isolated cache root.
    from code2llm.core import analyzer as analyzer_mod
    orig = analyzer_mod.PersistentCache

    class _PC(orig):
        def __init__(self, pd):
            super().__init__(pd, cache_root=str(cache_root), auto_cleanup=False)

    analyzer_mod.PersistentCache = _PC
    try:
        cfg = Config()
        cfg.performance.parallel_enabled = False
        a = ProjectAnalyzer(cfg, iac_project)
        a.analyze_project(str(iac_project))

        pc1 = PersistentCache(
            str(iac_project), cache_root=str(cache_root), auto_cleanup=False
        )
        assert "pyproject.toml" in pc1._manifest["files"], (
            "declarative files must be tracked in the manifest so that "
            "content-addressed invalidation works"
        )
        h1 = pc1._compute_run_hash({"fmt": "toon"})

        # Modify pyproject.toml
        (iac_project / "pyproject.toml").write_text('[project]\nname = "y"\n')

        a2 = ProjectAnalyzer(cfg, iac_project)
        a2.analyze_project(str(iac_project))

        pc2 = PersistentCache(
            str(iac_project), cache_root=str(cache_root), auto_cleanup=False
        )
        h2 = pc2._compute_run_hash({"fmt": "toon"})
        assert h1 != h2, (
            "editing pyproject.toml must invalidate the export cache "
            "(run hash must change)"
        )
    finally:
        analyzer_mod.PersistentCache = orig


def test_dockerfile_edit_invalidates_cache(iac_project, tmp_path):
    """Dockerfile is matched by filename, not extension — must also invalidate."""
    cache_root = tmp_path / "cache_root"

    from code2llm.core import analyzer as analyzer_mod
    orig = analyzer_mod.PersistentCache

    class _PC(orig):
        def __init__(self, pd):
            super().__init__(pd, cache_root=str(cache_root), auto_cleanup=False)

    analyzer_mod.PersistentCache = _PC
    try:
        cfg = Config()
        cfg.performance.parallel_enabled = False
        ProjectAnalyzer(cfg, iac_project).analyze_project(str(iac_project))
        pc1 = PersistentCache(
            str(iac_project), cache_root=str(cache_root), auto_cleanup=False
        )
        assert "Dockerfile" in pc1._manifest["files"]
        h1 = pc1._compute_run_hash({"fmt": "toon"})

        (iac_project / "Dockerfile").write_text("FROM python:3.14\n")
        ProjectAnalyzer(cfg, iac_project).analyze_project(str(iac_project))

        pc2 = PersistentCache(
            str(iac_project), cache_root=str(cache_root), auto_cleanup=False
        )
        h2 = pc2._compute_run_hash({"fmt": "toon"})
        assert h1 != h2
    finally:
        analyzer_mod.PersistentCache = orig


def test_dockerfile_variants_matched_by_prefix(tmp_path):
    """Dockerfile.dev, Dockerfile.prod etc. are discovered via prefix match."""
    p = tmp_path / "proj"
    p.mkdir()
    (p / "Dockerfile.dev").write_text("FROM python:3.13-slim\n")
    (p / "Dockerfile.prod").write_text("FROM python:3.13\n")
    (p / "Dockerfile.test").write_text("FROM alpine\n")
    (p / "Makefile.am").write_text("all:\n\techo am\n")
    # non-matching negative control
    (p / "Dockerfiles").write_text("not a real file")  # same prefix but no dot
    (p / "my.Dockerfile").write_text("FROM scratch\n")  # reverse — not a variant

    cfg = Config()
    cfg.performance.parallel_enabled = False
    a = ProjectAnalyzer(cfg, p)
    files = a._collect_files(p)
    names = {Path(fp).name for fp, _ in files}

    assert "Dockerfile.dev" in names
    assert "Dockerfile.prod" in names
    assert "Dockerfile.test" in names
    assert "Makefile.am" in names
    # "Dockerfiles" (no dot) must NOT match the prefix rule
    assert "Dockerfiles" not in names


def test_lockfiles_excluded_by_default(iac_project, tmp_path):
    """package-lock.json etc. should NOT enter the manifest (too noisy)."""
    (iac_project / "package-lock.json").write_text('{"lockfileVersion": 3}\n')
    (iac_project / "poetry.lock").write_text("[[package]]\n")
    (iac_project / "Cargo.lock").write_text("[[package]]\n")

    cfg = Config()
    cfg.performance.parallel_enabled = False
    a = ProjectAnalyzer(cfg, iac_project)
    files = a._collect_files(iac_project)
    names = {Path(fp).name for fp, _ in files}

    assert "package-lock.json" not in names
    assert "poetry.lock" not in names
    assert "Cargo.lock" not in names
    # But the non-lock package.json stays.
    assert "package.json" in names


def test_generated_analysis_artifacts_are_excluded_by_default(tmp_path):
    """code2llm outputs must not be fed back into the next analysis run."""
    p = tmp_path / "proj"
    p.mkdir()
    (p / "app.py").write_text("def run():\n    return 1\n")
    out = p / "project"
    out.mkdir()
    (out / "analysis.toon.yaml").write_text("# code2llm\nHEALTH[0]: ok\n")
    (out / "map.toon.yaml").write_text("# generated map\n")
    (out / "index.html").write_text("<title>code2llm Analysis Results</title>\n")
    batch = out / "batch_1"
    batch.mkdir()
    (batch / "context.md").write_text("# System Architecture Analysis\n<!-- generated in 0.01s -->\n")
    (p / ".code2llm_incremental.json").write_text("{}\n")
    (p / "SUMD.md").write_text("# generated summary\n")
    (p / "defscan-classes-py.md").write_text("class Noise:\n    pass\n")

    cfg = Config()
    cfg.performance.parallel_enabled = False
    files = ProjectAnalyzer(cfg, p)._collect_files(p)
    names = {str(Path(fp).relative_to(p)) for fp, _ in files}

    assert "app.py" in names
    assert "project/analysis.toon.yaml" not in names
    assert "project/map.toon.yaml" not in names
    assert "project/index.html" not in names
    assert "project/batch_1/context.md" not in names
    assert ".code2llm_incremental.json" not in names
    assert "SUMD.md" not in names
    assert "defscan-classes-py.md" not in names


def test_code2llmignore_is_applied(tmp_path):
    """Project-local .code2llmignore should refine analysis scope."""
    p = tmp_path / "proj"
    p.mkdir()
    (p / ".code2llmignore").write_text("docs/\n")
    (p / "app.py").write_text("def run():\n    return 1\n")
    docs = p / "docs"
    docs.mkdir()
    (docs / "README.md").write_text("# Docs\n")

    cfg = Config()
    cfg.performance.parallel_enabled = False
    files = ProjectAnalyzer(cfg, p)._collect_files(p)
    names = {Path(fp).name for fp, _ in files}

    assert "app.py" in names
    assert "README.md" not in names


def test_markdown_and_config_do_not_emit_fake_symbols(iac_project):
    """Tracked docs/config invalidate cache but should not create classes/functions."""
    cfg = Config()
    analyzer = FileAnalyzer(cfg)

    markdown = analyzer.analyze_file(str(iac_project / "README.md"), "README")
    yaml_result = analyzer.analyze_file(str(iac_project / "k8s.yaml"), "k8s")

    assert markdown["functions"] == {}
    assert markdown["classes"] == {}
    assert yaml_result["functions"] == {}
    assert yaml_result["classes"] == {}
    assert markdown["module"].source_kind == "docs"
    assert yaml_result["module"].source_kind == "config"
