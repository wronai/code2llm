"""Tests for Sprint 3: networkx-based PipelineDetector with domain grouping,
entry/exit labeling, and purity aggregation.

Success metrics from action_plan_v3:
- Auto-detected ≥3 pipelines with ≥3 stages each
- Side-effect detection accuracy ≥70%
- Pipeline purity scoring matches manual analysis
"""
import textwrap
import pytest
from pathlib import Path

from code2flow.core.models import AnalysisResult, FunctionInfo, ModuleInfo
from code2flow.analysis.pipeline_detector import (
    PipelineDetector, Pipeline, PipelineStage,
)
from code2flow.analysis.side_effects import SideEffectDetector
from code2flow.analysis.type_inference import TypeInferenceEngine
from code2flow.exporters.flow_exporter import FlowExporter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fi(name, module="mod", args=None, calls=None, cc=3, class_name=None,
        file="/test/src.py", line=1):
    """Shorthand FunctionInfo builder."""
    return FunctionInfo(
        name=name,
        qualified_name=f"{module}.{class_name + '.' if class_name else ''}{name}",
        file=file,
        line=line,
        module=module,
        class_name=class_name,
        is_method=class_name is not None,
        args=args or [],
        calls=calls or [],
        complexity={"cyclomatic_complexity": cc},
    )


def _build_chain_funcs(chain_spec, module="mod", file="/test/src.py"):
    """Build a dict of FunctionInfo forming a call chain.

    chain_spec: list of (name, cc) tuples.
    Each function calls the next one in the list.
    """
    funcs = {}
    names = [name for name, _ in chain_spec]
    for i, (name, cc) in enumerate(chain_spec):
        calls = [f"{module}.{names[i+1]}"] if i < len(chain_spec) - 1 else []
        fi = _fi(name, module=module, calls=calls, cc=cc, file=file)
        funcs[fi.qualified_name] = fi
    return funcs


# ---------------------------------------------------------------------------
# PipelineDetector unit tests
# ---------------------------------------------------------------------------

class TestPipelineDetector:

    def test_detects_simple_chain(self):
        """A linear chain A->B->C->D should produce 1 pipeline with 4 stages."""
        funcs = _build_chain_funcs([
            ("entry", 2), ("process", 5), ("transform", 3), ("output", 1),
        ])
        detector = PipelineDetector()
        pipelines = detector.detect(funcs)

        assert len(pipelines) >= 1
        longest = pipelines[0]
        assert longest.total_stages >= 3

    def test_entry_exit_labeling(self):
        """First stage should be marked entry, last stage marked exit."""
        funcs = _build_chain_funcs([
            ("start", 1), ("middle", 2), ("end", 1),
        ])
        detector = PipelineDetector()
        pipelines = detector.detect(funcs)

        assert len(pipelines) >= 1
        p = pipelines[0]
        assert p.stages[0].is_entry is True
        assert p.stages[-1].is_exit is True
        # Middle stages should not be entry/exit
        if len(p.stages) > 2:
            assert p.stages[1].is_entry is False
            assert p.stages[1].is_exit is False

    def test_purity_aggregation(self, tmp_path):
        """Pipeline purity should count pure stages correctly."""
        src = tmp_path / "purity_test.py"
        src.write_text(textwrap.dedent("""\
            def pure_func(x: str) -> str:
                return x.upper()

            def io_func(path: str) -> None:
                with open(path) as f:
                    f.read()

            def another_pure(x: int) -> int:
                return x + 1
        """))
        funcs = {
            "m.pure_func": _fi("pure_func", module="m",
                                calls=["m.io_func"], file=str(src), line=1),
            "m.io_func": _fi("io_func", module="m",
                              calls=["m.another_pure"], file=str(src), line=4),
            "m.another_pure": _fi("another_pure", module="m",
                                   calls=[], file=str(src), line=8),
        }
        detector = PipelineDetector()
        pipelines = detector.detect(funcs)

        assert len(pipelines) >= 1
        p = pipelines[0]
        assert p.total_stages == 3
        # 2 pure, 1 IO
        assert p.pure_count == 2

    def test_bottleneck_detection(self):
        """Bottleneck should be the stage with highest CC."""
        funcs = _build_chain_funcs([
            ("a", 2), ("b", 18), ("c", 5),
        ])
        detector = PipelineDetector()
        pipelines = detector.detect(funcs)

        assert len(pipelines) >= 1
        bn = pipelines[0].bottleneck
        assert bn is not None
        assert bn.name == "b"
        assert bn.cc == 18

    def test_pipeline_to_dict(self):
        """Pipeline.to_dict() should produce a valid dict."""
        funcs = _build_chain_funcs([
            ("x", 1), ("y", 2), ("z", 3),
        ])
        detector = PipelineDetector()
        pipelines = detector.detect(funcs)

        assert len(pipelines) >= 1
        d = pipelines[0].to_dict()
        assert "name" in d
        assert "domain" in d
        assert "stages" in d
        assert isinstance(d["stages"], list)
        assert d["total_stages"] >= 3

    def test_no_pipelines_from_isolated_functions(self):
        """Functions with no calls should not form pipelines."""
        funcs = {
            "m.a": _fi("a", calls=[]),
            "m.b": _fi("b", calls=[]),
            "m.c": _fi("c", calls=[]),
        }
        detector = PipelineDetector()
        pipelines = detector.detect(funcs)

        assert len(pipelines) == 0

    def test_empty_input(self):
        detector = PipelineDetector()
        pipelines = detector.detect({})
        assert pipelines == []


# ---------------------------------------------------------------------------
# Domain classification tests
# ---------------------------------------------------------------------------

class TestDomainClassification:

    def test_nlp_domain(self):
        funcs = _build_chain_funcs([
            ("normalize_query", 2), ("match_intent", 5), ("resolve_entity", 3),
        ], module="code2flow.nlp")
        detector = PipelineDetector()
        pipelines = detector.detect(funcs)

        assert len(pipelines) >= 1
        assert pipelines[0].domain == "NLP"

    def test_analysis_domain(self):
        funcs = _build_chain_funcs([
            ("analyze_file", 4), ("compute_metrics", 6), ("build_call_graph", 3),
        ], module="code2flow.analysis")
        detector = PipelineDetector()
        pipelines = detector.detect(funcs)

        assert len(pipelines) >= 1
        assert pipelines[0].domain == "Analysis"

    def test_export_domain(self):
        funcs = _build_chain_funcs([
            ("export_toon", 3), ("render_header", 2), ("format_output", 2),
        ], module="code2flow.exporters")
        detector = PipelineDetector()
        pipelines = detector.detect(funcs)

        assert len(pipelines) >= 1
        assert pipelines[0].domain == "Export"

    def test_unknown_domain(self):
        funcs = _build_chain_funcs([
            ("foo", 1), ("bar", 1), ("baz", 1),
        ], module="mylib.stuff")
        detector = PipelineDetector()
        pipelines = detector.detect(funcs)

        if pipelines:
            assert pipelines[0].domain == "Unknown"


# ---------------------------------------------------------------------------
# Multiple pipelines (success metric: ≥3 pipelines with ≥3 stages)
# ---------------------------------------------------------------------------

class TestMultiplePipelines:

    def test_three_independent_pipelines(self):
        """Three independent chains should produce ≥3 pipelines."""
        funcs = {}
        # NLP pipeline
        funcs.update(_build_chain_funcs([
            ("normalize", 2), ("tokenize", 3), ("match_intent", 5),
        ], module="nlp"))
        # Analysis pipeline
        funcs.update(_build_chain_funcs([
            ("analyze_file", 4), ("compute_metrics", 6), ("build_graph", 3),
        ], module="analysis"))
        # Export pipeline
        funcs.update(_build_chain_funcs([
            ("export_data", 3), ("render_toon", 2), ("format_output", 2),
        ], module="exporters"))

        detector = PipelineDetector()
        pipelines = detector.detect(funcs)

        assert len(pipelines) >= 3
        for p in pipelines:
            assert p.total_stages >= 3

    def test_four_pipelines_with_domains(self):
        """Four domain pipelines including Refactor."""
        funcs = {}
        funcs.update(_build_chain_funcs([
            ("normalize", 2), ("tokenize", 3), ("match_intent", 5),
        ], module="nlp"))
        funcs.update(_build_chain_funcs([
            ("analyze_file", 4), ("compute_metrics", 6), ("build_graph", 3),
        ], module="analysis"))
        funcs.update(_build_chain_funcs([
            ("export_data", 3), ("render_toon", 2), ("format_output", 2),
        ], module="exporters"))
        funcs.update(_build_chain_funcs([
            ("detect_smell", 5), ("suggest_fix", 4), ("apply_patch", 3),
        ], module="refactor"))

        detector = PipelineDetector()
        pipelines = detector.detect(funcs)

        assert len(pipelines) >= 4
        domains = {p.domain for p in pipelines}
        assert "NLP" in domains
        assert "Analysis" in domains
        assert "Export" in domains
        assert "Refactor" in domains


# ---------------------------------------------------------------------------
# FlowExporter integration (Sprint 3)
# ---------------------------------------------------------------------------

class TestFlowExporterSprint3:

    @pytest.fixture
    def multi_pipeline_result(self):
        """AnalysisResult with multiple pipelines across domains."""
        result = AnalysisResult(project_path="/test/project")

        # NLP pipeline
        for name, cc, calls in [
            ("normalize", 2, ["nlp.tokenize"]),
            ("tokenize", 3, ["nlp.match_intent"]),
            ("match_intent", 5, []),
        ]:
            fi = _fi(name, module="nlp", calls=calls, cc=cc)
            result.functions[fi.qualified_name] = fi

        # Analysis pipeline
        for name, cc, calls in [
            ("analyze_file", 4, ["analysis.compute_metrics"]),
            ("compute_metrics", 6, ["analysis.build_graph"]),
            ("build_graph", 3, []),
        ]:
            fi = _fi(name, module="analysis", calls=calls, cc=cc)
            result.functions[fi.qualified_name] = fi

        # Export pipeline
        for name, cc, calls in [
            ("export_data", 3, ["exporters.render_toon"]),
            ("render_toon", 2, ["exporters.format_output"]),
            ("format_output", 2, []),
        ]:
            fi = _fi(name, module="exporters", calls=calls, cc=cc)
            result.functions[fi.qualified_name] = fi

        return result

    def test_output_has_domain_tags(self, multi_pipeline_result, tmp_path):
        exporter = FlowExporter()
        output = tmp_path / "flow.toon"
        exporter.export(multi_pipeline_result, str(output))
        content = output.read_text()

        assert "PIPELINES[" in content
        # Should contain domain tags
        assert "[NLP]" in content or "[Analysis]" in content or "[Export]" in content

    def test_output_has_entry_exit_markers(self, multi_pipeline_result, tmp_path):
        exporter = FlowExporter()
        output = tmp_path / "flow.toon"
        exporter.export(multi_pipeline_result, str(output))
        content = output.read_text()

        # ▶ for entry, ■ for exit
        assert "\u25b6" in content  # entry marker
        assert "\u25a0" in content  # exit marker

    def test_output_has_pipeline_purity(self, multi_pipeline_result, tmp_path):
        exporter = FlowExporter()
        output = tmp_path / "flow.toon"
        exporter.export(multi_pipeline_result, str(output))
        content = output.read_text()

        assert "PIPELINE PURITY:" in content
        assert "% pure" in content

    def test_output_has_all_sections(self, multi_pipeline_result, tmp_path):
        exporter = FlowExporter()
        output = tmp_path / "flow.toon"
        exporter.export(multi_pipeline_result, str(output))
        content = output.read_text()

        assert "PIPELINES[" in content
        assert "CONTRACTS:" in content
        assert "DATA_TYPES" in content
        assert "SIDE_EFFECTS:" in content

    def test_contracts_show_domain_pipeline(self, multi_pipeline_result, tmp_path):
        exporter = FlowExporter()
        output = tmp_path / "flow.toon"
        exporter.export(multi_pipeline_result, str(output))
        content = output.read_text()

        assert "Pipeline:" in content
        assert "IN:" in content
        assert "OUT:" in content


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestPipelineEdgeCases:

    def test_cyclic_calls(self):
        """Cycles should not crash the detector."""
        funcs = {
            "m.a": _fi("a", calls=["m.b"]),
            "m.b": _fi("b", calls=["m.c"]),
            "m.c": _fi("c", calls=["m.a"]),  # cycle back to a
        }
        detector = PipelineDetector()
        pipelines = detector.detect(funcs)
        # Should not crash; may or may not find a pipeline
        assert isinstance(pipelines, list)

    def test_self_recursive(self):
        """Self-recursive functions should not create infinite loops."""
        funcs = {
            "m.rec": _fi("rec", calls=["m.rec", "m.base"]),
            "m.base": _fi("base", calls=[]),
        }
        detector = PipelineDetector()
        pipelines = detector.detect(funcs)
        assert isinstance(pipelines, list)

    def test_diamond_dependency(self):
        """Diamond: A->B, A->C, B->D, C->D should find a path."""
        funcs = {
            "m.a": _fi("a", calls=["m.b", "m.c"]),
            "m.b": _fi("b", calls=["m.d"]),
            "m.c": _fi("c", calls=["m.d"]),
            "m.d": _fi("d", calls=[]),
        }
        detector = PipelineDetector()
        pipelines = detector.detect(funcs)

        assert len(pipelines) >= 1
        assert pipelines[0].total_stages >= 3

    def test_very_long_chain(self):
        """A chain of 15 functions should produce a long pipeline."""
        spec = [(f"step_{i}", i % 5 + 1) for i in range(15)]
        funcs = _build_chain_funcs(spec)
        detector = PipelineDetector()
        pipelines = detector.detect(funcs)

        assert len(pipelines) >= 1
        assert pipelines[0].total_stages >= 10
