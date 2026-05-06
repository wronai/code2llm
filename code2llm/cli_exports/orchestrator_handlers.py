"""Export handlers — specific format export implementations.

This module contains all the individual export handler functions
that were extracted from orchestrator.py to reduce its size.
"""

import time
from pathlib import Path
from typing import Any, Dict, List

from code2llm.exporters import (
    get_exporter,
    YAMLExporter,
    MermaidExporter,
    ToonViewGenerator,
    IndexHTMLGenerator,
)
from code2llm.exporters.project_yaml.evolution import load_previous_evolution
from .orchestrator_constants import FORMAT_LABELS


def _export_mermaid(args, result, output_dir: Path):
    """Export mermaid diagrams."""
    from .orchestrator import _inject_generation_time

    exporter = MermaidExporter()
    include_examples = getattr(args, 'flow_include_examples', False)

    # Core diagrams
    mmd_files = ['flow.mmd', 'calls.mmd', 'compact_flow.mmd']
    t0 = time.monotonic()
    exporter.export_flow_compact(result, str(output_dir / 'flow.mmd'), include_examples)
    exporter.export_call_graph(result, str(output_dir / 'calls.mmd'))
    exporter.export_compact(result, str(output_dir / 'compact_flow.mmd'))

    # Optional detailed diagrams
    if getattr(args, 'flow_detail', False):
        exporter.export_flow_detailed(result, str(output_dir / 'flow_detailed.mmd'), include_examples)
        mmd_files.append('flow_detailed.mmd')
    if getattr(args, 'flow_full', False):
        exporter.export_flow_full(result, str(output_dir / 'flow_full.mmd'), include_examples)
        mmd_files.append('flow_full.mmd')
    elapsed_mmd = time.monotonic() - t0

    # Inject timing into each .mmd file
    for mf in mmd_files:
        _inject_generation_time(output_dir / mf, elapsed_mmd)

    # Also export calls.yaml/toon
    yaml_exporter = YAMLExporter()
    t0 = time.monotonic()
    yaml_exporter.export_calls(result, str(output_dir / 'calls.yaml'))
    yaml_exporter.export_calls_toon(result, str(output_dir / 'calls.toon.yaml'))
    elapsed_calls = time.monotonic() - t0
    _inject_generation_time(output_dir / 'calls.toon.yaml', elapsed_calls)

    if args.verbose:
        files = mmd_files + ['calls.yaml']
        print(f"  - Mermaid: {output_dir}/*.mmd ({', '.join(files)}) ({elapsed_mmd:.2f}s)")

    # PNG generation
    _export_mermaid_pngs(args, output_dir)


def _export_mermaid_pngs(args, output_dir: Path):
    """Generate PNGs from mermaid files."""
    if getattr(args, 'no_png', False):
        return
    try:
        from ..generators.mermaid import generate_pngs
        png_count = generate_pngs(output_dir, output_dir)
        if args.verbose and png_count > 0:
            print(f"  - PNG: {png_count} files generated")
    except ImportError:
        if args.verbose:
            print(f"  - PNG: Skipped (install with: make install-mermaid)")


def _export_calls(args, result, output_dir: Path, formats: List[str]):
    """Export calls.yaml and calls.toon.yaml."""
    yaml_exporter = YAMLExporter()
    if 'calls' in formats:
        yaml_exporter.export_calls(result, str(output_dir / 'calls.yaml'))
        if args.verbose:
            print(f"  - CALLS (call graph YAML): {output_dir / 'calls.yaml'}")
    if 'calls_toon' in formats:
        yaml_exporter.export_calls_toon(result, str(output_dir / 'calls.toon.yaml'))
        if args.verbose:
            print(f"  - CALLS (toon format): {output_dir / 'calls.toon.yaml'}")


def _export_context_fallback(args, result, output_dir: Path):
    """Export context.md as fallback."""
    exporter_cls = get_exporter('context')
    if exporter_cls:
        exporter = exporter_cls()
        exporter.export(result, str(output_dir / 'context.md'))
        if args.verbose:
            print(f"  - CONTEXT (LLM narrative): {output_dir / 'context.md'}")


def _export_data_structures(args, result, output_dir: Path):
    """Export data_structures.yaml."""
    yaml_exporter = YAMLExporter()
    yaml_exporter.export_data_structures(result, str(output_dir / 'data_structures.yaml'), compact=True)
    if args.verbose:
        print(f"  - Data structures: {output_dir / 'data_structures.yaml'}")


def _export_project_toon(args, result, output_dir: Path):
    """Export project.toon.yaml from project.yaml data."""
    from ..exporters.project_yaml_exporter import ProjectYAMLExporter
    from .orchestrator import _inject_generation_time

    project_yaml_exporter = ProjectYAMLExporter()
    prev_evolution = load_previous_evolution(output_dir / 'project.yaml')
    data = project_yaml_exporter._build_project_yaml(result, prev_evolution)

    generator = ToonViewGenerator()
    filepath = output_dir / 'project.toon.yaml'
    t0 = time.monotonic()
    generator.generate(data, str(filepath))
    elapsed = time.monotonic() - t0
    _inject_generation_time(filepath, elapsed)

    if args.verbose:
        print(f"  - PROJECT-TOON (project overview): {filepath} ({elapsed:.2f}s)")


def _export_readme(args, result, output_dir: Path):
    """Export README.md."""
    if getattr(args, 'no_readme', False):
        return
    from .orchestrator import _inject_generation_time
    exporter_cls = get_exporter('readme')
    if exporter_cls:
        exporter = exporter_cls()
        filepath = output_dir / 'README.md'
        t0 = time.monotonic()
        exporter.export(result, str(filepath))
        elapsed = time.monotonic() - t0
        _inject_generation_time(filepath, elapsed)
        if args.verbose:
            print(f"  - README (documentation): {filepath} ({elapsed:.2f}s)")


def _export_index_html(args, output_dir: Path):
    """Generate index.html for browsing files."""
    if 'all' not in getattr(args, 'format', ''):
        return
    try:
        from .orchestrator import _inject_generation_time
        generator = IndexHTMLGenerator(output_dir)
        t0 = time.monotonic()
        index_path = generator.generate()
        elapsed = time.monotonic() - t0
        _inject_generation_time(index_path, elapsed)
        if args.verbose:
            print(f"  - INDEX (file browser): {index_path} ({elapsed:.2f}s)")
    except Exception as e:
        if args.verbose:
            print(f"  - INDEX generation failed: {e}", file=__import__('sys').stderr)


__all__ = [
    '_export_mermaid',
    '_export_mermaid_pngs',
    '_export_calls',
    '_export_context_fallback',
    '_export_data_structures',
    '_export_project_toon',
    '_export_readme',
    '_export_index_html',
]
