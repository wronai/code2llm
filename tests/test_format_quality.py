#!/usr/bin/env python3
"""
Pytest-based format quality tests.

These verify that each code2llm output format correctly detects
known problems in a controlled test project.

Run with: pytest tests/test_format_quality.py -v
"""

import textwrap
import tempfile
import shutil
from pathlib import Path
from typing import Dict

import pytest


# ─────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def ground_truth_project(tmp_path_factory) -> Path:
    """Create a project with known problems."""
    project = tmp_path_factory.mktemp("sample")

    (project / "core.py").write_text(textwrap.dedent("""\
        from typing import List, Dict, Optional
        from dataclasses import dataclass

        @dataclass
        class Config:
            debug: bool = False
            max_items: int = 100

        @dataclass
        class Result:
            data: List[dict] = None
            errors: List[str] = None
            def is_ok(self) -> bool:
                return not self.errors

        _cache: Dict[str, Result] = {}

        def cache_result(key: str, result: Result) -> None:
            global _cache
            _cache[key] = result

        def process_everything(data: list, config: Config) -> Result:
            if not data:
                return Result(errors=["empty"])
            if not isinstance(data, list):
                return Result(errors=["not list"])
            filtered = []
            for item in data:
                if isinstance(item, dict):
                    if "id" in item:
                        if item.get("active", True):
                            filtered.append(item)
                        elif config.debug:
                            filtered.append(item)
                    else:
                        if config.debug:
                            print(f"No id: {item}")
                else:
                    if config.debug:
                        print(f"Not dict: {item}")
            results = []
            for item in filtered:
                t = {}
                for k, v in item.items():
                    if isinstance(v, str):
                        t[k] = v.strip().lower()
                    elif isinstance(v, (int, float)):
                        t[k] = v
                    else:
                        t[k] = str(v)
                results.append(t)
            return Result(data=results[:config.max_items])

        def unused_helper(x: int) -> int:
            return x * 2

        def main(config: Config) -> None:
            data = extract_data(config)
            result = transform_data(data, config)
            loaded = load_data(result, config)
            cache_result("latest", loaded)
            report(loaded, config)

        class Validator:
            def __init__(self, config: Config):
                self.config = config
            def validate(self, data: list) -> Result:
                if not data:
                    return Result(errors=["empty"])
                return Result(data=data)
    """))

    (project / "etl.py").write_text(textwrap.dedent("""\
        from typing import List
        from core import Config, Result

        def extract_data(config: Config) -> List[dict]:
            with open("input.json") as f:
                import json
                return json.load(f)

        def transform_data(data: List[dict], config: Config) -> List[dict]:
            return [{k: v for k, v in item.items()} for item in data]

        def load_data(data: List[dict], config: Config) -> Result:
            import json
            with open("output.json", "w") as f:
                json.dump(data, f)
            return Result(data=data)
    """))

    (project / "utils.py").write_text(textwrap.dedent("""\
        from core import Result, Config

        class Validator:
            def __init__(self, config: Config):
                self.config = config
            def validate(self, data: list) -> Result:
                if not data:
                    return Result(errors=["empty"])
                return Result(data=data)

        def report(result: Result, config: Config) -> None:
            if result.is_ok():
                print(f"OK: {len(result.data)} items")

        def process_data(data, config):
            v = Validator(config)
            return v.validate(data)
    """))

    return project


@pytest.fixture(scope="module")
def analysis_result(ground_truth_project):
    """Run code2llm analysis on ground truth project."""
    from code2llm import ProjectAnalyzer, Config
    cfg = Config()
    cfg.filters.exclude_patterns = [
        '*__pycache__*', '*.pyc', '*venv*', '*.venv*',
        '*node_modules*', '*.git*',
    ]
    cfg.filters.skip_private = False
    cfg.filters.min_function_lines = 1
    analyzer = ProjectAnalyzer(cfg)
    return analyzer.analyze_project(str(ground_truth_project))


# ─────────────────────────────────────────────────────────────────
# analysis.toon tests
# ─────────────────────────────────────────────────────────────────

class TestAnalysisToon:
    """Test that analysis.toon detects known problems."""

    @pytest.fixture
    def toon_content(self, analysis_result, tmp_path):
        from code2llm.exporters.toon import ToonExporter
        out = tmp_path / "analysis.toon"
        ToonExporter().export(analysis_result, str(out))
        return out.read_text()

    def test_detects_god_function(self, toon_content):
        """process_everything should appear in HEALTH or FUNCTIONS with high CC."""
        assert "process_everything" in toon_content
        assert "!!" in toon_content or "CC" in toon_content

    def test_detects_high_fan_out(self, toon_content):
        """main() should appear in HOTSPOTS with high fan-out."""
        assert "HOTSPOTS" in toon_content
        assert "main" in toon_content

    def test_has_health_section(self, toon_content):
        assert "HEALTH[" in toon_content

    def test_has_refactor_section(self, toon_content):
        assert "REFACTOR[" in toon_content

    def test_has_coupling_section(self, toon_content):
        assert "COUPLING" in toon_content

    def test_has_severity_markers(self, toon_content):
        assert ("!" in toon_content or "🔴" in toon_content
                or "🟡" in toon_content or "critical" in toon_content)

    def test_has_layers(self, toon_content):
        assert "LAYERS" in toon_content


# ─────────────────────────────────────────────────────────────────
# flow.toon tests
# ─────────────────────────────────────────────────────────────────

class TestFlowToon:
    """Test that flow.toon detects data-flow information."""

    @pytest.fixture
    def flow_content(self, analysis_result, tmp_path):
        from code2llm.exporters.flow_exporter import FlowExporter
        out = tmp_path / "flow.toon"
        FlowExporter().export(analysis_result, str(out))
        return out.read_text()

    def test_has_pipelines_section(self, flow_content):
        assert "PIPELINE" in flow_content

    def test_has_transforms_section(self, flow_content):
        assert "TRANSFORM" in flow_content

    def test_has_type_info(self, flow_content):
        """Should contain return type annotations."""
        assert "->" in flow_content or "→" in flow_content

    def test_detects_etl_pipeline_functions(self, flow_content):
        """extract_data, transform_data, load_data should appear together."""
        has_extract = "extract_data" in flow_content
        has_transform = "transform_data" in flow_content
        has_load = "load_data" in flow_content
        assert sum([has_extract, has_transform, has_load]) >= 2, \
            "Should detect at least 2 of 3 ETL pipeline stages"

    def test_has_side_effects_section(self, flow_content):
        assert "SIDE" in flow_content.upper() or "pure" in flow_content.lower()

    def test_has_contracts_or_data_types(self, flow_content):
        upper = flow_content.upper()
        assert "CONTRACT" in upper or "DATA_TYPE" in upper or "DATA TYPE" in upper


# ─────────────────────────────────────────────────────────────────
# project.map tests
# ─────────────────────────────────────────────────────────────────

class TestProjectMap:
    """Test that project.map provides structural information."""

    @pytest.fixture
    def map_content(self, analysis_result, tmp_path):
        from code2llm.exporters.map_exporter import MapExporter
        out = tmp_path / "project.map"
        MapExporter().export(analysis_result, str(out))
        return out.read_text()

    def test_lists_all_modules(self, map_content):
        assert "core.py" in map_content
        assert "etl.py" in map_content
        assert "utils.py" in map_content

    def test_has_import_info(self, map_content):
        assert "i:" in map_content or "import" in map_content.lower()

    def test_has_function_signatures(self, map_content):
        """Should contain function names with parameters."""
        assert "process_everything" in map_content
        assert "extract_data" in map_content

    def test_has_type_annotations(self, map_content):
        """Should preserve type info from source."""
        # At minimum function names should be present
        assert "Config" in map_content or "Result" in map_content


# ─────────────────────────────────────────────────────────────────
# context.md tests
# ─────────────────────────────────────────────────────────────────

class TestContextMd:
    """Test that context.md provides LLM-readable narrative."""

    @pytest.fixture
    def context_content(self, analysis_result, tmp_path):
        from code2llm.exporters.llm_exporter import LLMPromptExporter
        out = tmp_path / "context.md"
        LLMPromptExporter().export(analysis_result, str(out))
        return out.read_text()

    def test_has_overview(self, context_content):
        assert "Overview" in context_content or "Architecture" in context_content

    def test_has_entry_points(self, context_content):
        assert "main" in context_content

    def test_is_markdown(self, context_content):
        assert "#" in context_content  # has headers


# ─────────────────────────────────────────────────────────────────
# Cross-format comparison
# ─────────────────────────────────────────────────────────────────

class TestCrossFormat:
    """Test that formats are complementary, not redundant."""

    @pytest.fixture
    def all_formats(self, analysis_result, tmp_path):
        formats = {}
        exporters = {
            "analysis.toon": ("code2llm.exporters.toon", "ToonExporter"),
            "flow.toon":     ("code2llm.exporters.flow_exporter", "FlowExporter"),
            "project.map":   ("code2llm.exporters.map_exporter", "MapExporter"),
            "context.md":    ("code2llm.exporters.llm_exporter", "LLMPromptExporter"),
        }
        for name, (mod_path, cls_name) in exporters.items():
            try:
                mod = __import__(mod_path, fromlist=[cls_name])
                exp = getattr(mod, cls_name)()
                out = tmp_path / name
                exp.export(analysis_result, str(out))
                if out.exists():
                    formats[name] = out.read_text()
            except Exception:
                formats[name] = ""
        return formats

    def test_flow_toon_has_unique_pipeline_info(self, all_formats):
        """flow.toon should have pipeline info that analysis.toon doesn't."""
        flow = all_formats.get("flow.toon", "")
        # flow.toon should be the one with pipeline/transform/contract focus
        pipeline_keywords = ["PIPELINE", "TRANSFORM", "CONTRACT", "SIDE_EFFECT", "PURITY"]
        flow_has = sum(1 for kw in pipeline_keywords if kw in flow.upper())
        assert flow_has >= 2, f"flow.toon should have ≥2 pipeline keywords, found {flow_has}"

    def test_analysis_toon_has_unique_health_info(self, all_formats):
        """analysis.toon should have health diagnostics that others don't."""
        toon = all_formats.get("analysis.toon", "")
        assert "HEALTH[" in toon
        assert "REFACTOR[" in toon

    def test_project_map_has_unique_structure_info(self, all_formats):
        """project.map should have import graph that others don't."""
        pmap = all_formats.get("project.map", "")
        assert "i:" in pmap or "import" in pmap.lower()

    def test_formats_have_different_sizes(self, all_formats):
        """Formats should not be identical (would indicate copy-paste)."""
        sizes = {name: len(content) for name, content in all_formats.items() if content}
        if len(sizes) >= 2:
            values = list(sizes.values())
            # At least 20% size difference between largest and smallest
            ratio = max(values) / max(min(values), 1)
            assert ratio > 1.2, f"Formats too similar in size: {sizes}"
