#!/usr/bin/env python3
"""
Format Quality Benchmark — measures how USEFUL each output format is
for data-flow refactoring decisions.

This is NOT a speed benchmark. It measures INFORMATION QUALITY:
- Can the format detect known problems in a test project?
- Does it show data flow pipelines?
- Does it identify hub types?
- Does it provide actionable refactoring steps?

Run with: python benchmarks/benchmark_format_quality.py
"""

import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmarks.benchmark_constants import KNOWN_PROBLEMS, KNOWN_PIPELINES, KNOWN_HUB_TYPES
from benchmarks.format_evaluator import FormatScore, evaluate_format
from benchmarks.project_generator import create_ground_truth_project
from benchmarks.reporting import build_report, print_results, save_report


def _print_benchmark_header() -> None:
    """Print benchmark header with description."""
    print("=" * 70)
    print("FORMAT QUALITY BENCHMARK")
    print("Measures: how well each format supports data-flow refactoring")
    print("=" * 70)


def _print_ground_truth_info(project_path: Path) -> None:
    """Print information about created ground-truth project."""
    print(f"\n✓ Created ground-truth project: {project_path}")
    print(f"  Known problems: {len(KNOWN_PROBLEMS)}")
    print(f"  Known pipelines: {len(KNOWN_PIPELINES)}")
    print(f"  Known hub types: {len(KNOWN_HUB_TYPES)}")


def _generate_format_outputs(result, output_dir: Path) -> Dict[str, FormatScore]:
    """Generate all format outputs and evaluate them."""
    scores: Dict[str, FormatScore] = {}

    format_configs = {
        "analysis.toon": ("code2llm.exporters.toon", "ToonExporter"),
        "flow.toon":     ("code2llm.exporters.flow_exporter", "FlowExporter"),
        "project.map":   ("code2llm.exporters.map_exporter", "MapExporter"),
        "context.md":    ("code2llm.exporters.llm_exporter", "LLMPromptExporter"),
    }

    for filename, (module_path, class_name) in format_configs.items():
        try:
            mod = __import__(module_path, fromlist=[class_name])
            exporter_cls = getattr(mod, class_name)
            exporter = exporter_cls()

            out_path = output_dir / filename
            start = time.time()
            exporter.export(result, str(out_path))
            gen_time = time.time() - start

            if out_path.exists():
                content = out_path.read_text(errors="replace")
                s = evaluate_format(filename, content, out_path)
                s.generation_time = gen_time
                scores[filename] = s
                print(f"  ✓ {filename}: {out_path.stat().st_size:,} bytes, {gen_time:.2f}s")
            else:
                print(f"  ✗ {filename}: file not created")
                scores[filename] = FormatScore(name=filename)
        except Exception as e:
            print(f"  ✗ {filename}: {e}")
            scores[filename] = FormatScore(name=filename)

    return scores


def _create_offline_scores() -> Dict[str, FormatScore]:
    """Create minimal fallback scores when code2llm isn't installed."""
    return {
        name: FormatScore(name=name)
        for name in ["analysis.toon", "flow.toon", "project.map", "context.md"]
    }


def run_benchmark() -> Dict:
    """Run the full format quality benchmark."""
    _print_benchmark_header()

    # 1. Create ground-truth project
    tmp = Path(tempfile.mkdtemp())
    project_path = create_ground_truth_project(tmp)
    _print_ground_truth_info(project_path)

    # 2. Run code2llm and generate all formats
    output_dir = tmp / "output"
    output_dir.mkdir()

    scores: Dict[str, FormatScore] = {}

    try:
        from code2llm import ProjectAnalyzer, Config

        print(f"\n→ Running code2llm analysis...")
        start = time.time()
        cfg = Config()
        cfg.filters.exclude_patterns = [
            '*__pycache__*', '*.pyc', '*venv*', '*.venv*',
            '*node_modules*', '*.git*',
        ]
        cfg.filters.skip_private = False
        cfg.filters.min_function_lines = 1
        analyzer = ProjectAnalyzer(cfg)
        result = analyzer.analyze_project(str(project_path))
        analysis_time = time.time() - start
        print(f"  Analysis: {analysis_time:.2f}s, {result.get_function_count()} functions")

        scores = _generate_format_outputs(result, output_dir)

    except ImportError as e:
        print(f"\n⚠ code2llm not installed: {e}")
        print("  Running in OFFLINE mode with sample data...")
        scores = _create_offline_scores()

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 3. Print results
    print_results(scores)

    # 4. Save report
    return build_report(scores)


if __name__ == "__main__":
    report = run_benchmark()
    save_report(report)
