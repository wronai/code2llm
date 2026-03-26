"""Tests for automatic project.toon.yaml export in all-format runs."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from code2llm.cli_exports.formats import _export_project_toon
from code2llm.cli_exports.orchestrator import _export_single_project


def test_export_project_toon_writes_file(tmp_path):
    args = SimpleNamespace(verbose=False)
    result = MagicMock()

    fake_data = {
        "project": {
            "name": "sample",
            "stats": {"functions": 1, "files": 1, "lines": 10, "classes": 0},
            "language": "python",
            "analyzed_at": "2026-03-26T12:34:56Z",
        },
        "health": {
            "cc_avg": 1.0,
            "critical_count": 0,
            "critical_limit": 10,
            "duplicates": 0,
            "cycles": 0,
            "alerts": [],
        },
        "modules": [
            {"path": "sample.py", "lines": 10, "classes": 0, "methods": 1, "cc_max": 1, "inbound_deps": 0},
        ],
        "hotspots": [],
        "refactoring": {},
        "evolution": [],
    }

    with patch("code2llm.cli_exports.formats.ProjectYAMLExporter._load_previous_evolution", return_value=[]), \
         patch("code2llm.cli_exports.formats.ProjectYAMLExporter._build_project_yaml", return_value=fake_data):
        output_path = _export_project_toon(args, result, tmp_path)

    assert output_path == tmp_path / "project.toon.yaml"
    assert output_path.exists()

    content = output_path.read_text(encoding="utf-8")
    assert content.startswith("# sample | 1 func | 1f | 10L | python | 2026-03-26")
    assert "HEALTH:" in content
    assert "MODULES[1]" in content


def test_export_single_project_all_triggers_project_toon(tmp_path):
    args = SimpleNamespace(verbose=False, refactor=False)
    result = MagicMock()
    source_path = Path("/tmp/source")

    with patch("code2llm.cli_exports.orchestrator._export_simple_formats"), \
         patch("code2llm.cli_exports.orchestrator._export_mermaid"), \
         patch("code2llm.cli_exports.orchestrator._export_evolution"), \
         patch("code2llm.cli_exports.orchestrator._export_data_structures"), \
         patch("code2llm.cli_exports.orchestrator._export_context_fallback"), \
         patch("code2llm.cli_exports.orchestrator._export_project_toon") as project_toon_mock, \
         patch("code2llm.cli_exports.orchestrator._export_code2logic"), \
         patch("code2llm.cli_exports.orchestrator._export_prompt_txt"), \
         patch("code2llm.cli_exports.orchestrator._export_readme"), \
         patch("code2llm.cli_exports.orchestrator._export_index_html"):
        _export_single_project(
            args,
            result,
            tmp_path,
            ['toon', 'map', 'context', 'mermaid', 'evolution'],
            requested_formats=['all'],
            source_path=source_path,
        )

    project_toon_mock.assert_called_once_with(args, result, tmp_path)
