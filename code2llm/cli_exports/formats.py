"""Format export functions — toon, map, context, yaml, json, mermaid, evolution, and legacy project-yaml/flow exports."""

import sys
import time
from pathlib import Path

from code2llm.exporters import (
    YAMLExporter, JSONExporter, MermaidExporter,
    ContextExporter, ToonExporter, MapExporter, FlowExporter,
    EvolutionExporter, READMEExporter, ProjectYAMLExporter,
    ToonViewGenerator, ContextViewGenerator,
    ArticleViewGenerator, HTMLDashboardGenerator,
    load_project_yaml, IndexHTMLGenerator,
)
from .orchestrator import _inject_generation_time as _inject_time


def _export_evolution(args, result, output_dir: Path):
    """Export evolution.toon.yaml format (plain text TOON)."""
    if 'evolution' not in [f.strip() for f in args.format.split(',')] and 'all' not in [f.strip() for f in args.format.split(',')]:
        return
    exporter = EvolutionExporter()
    filepath = output_dir / 'evolution.toon.yaml'
    t0 = time.monotonic()
    exporter.export(result, str(filepath))
    elapsed = time.monotonic() - t0
    _inject_time(filepath, elapsed)
    if args.verbose:
        print(f"  - EVOLUTION (refactoring queue): {filepath} ({elapsed:.2f}s)")


def _export_data_structures(args, result, output_dir: Path):
    """Export data structures YAML."""
    if not args.data_structures:
        return
    exporter = YAMLExporter()
    struct_path = output_dir / 'data_structures.yaml'
    exporter.export_data_structures(result, str(struct_path), compact=True)
    if args.verbose:
        print(f"  - Data structures: {struct_path}")


def _export_context_fallback(args, result, output_dir: Path, formats: list):
    """Export context.md if not in formats."""
    if 'context' in formats or 'all' in formats:
        return
    exporter = ContextExporter()
    filepath = output_dir / 'context.md'
    t0 = time.monotonic()
    exporter.export(result, str(filepath))
    elapsed = time.monotonic() - t0
    _inject_time(filepath, elapsed)
    if args.verbose:
        print(f"  - CONTEXT (LLM narrative): {filepath} ({elapsed:.2f}s)")


def _export_readme(args, result, output_dir: Path):
    """Export README.md documentation."""
    if not args.readme or getattr(args, 'no_readme', False):
        return
    exporter = READMEExporter()
    filepath = output_dir / 'README.md'
    t0 = time.monotonic()
    exporter.export(result, str(filepath))
    elapsed = time.monotonic() - t0
    _inject_time(filepath, elapsed)
    if args.verbose:
        print(f"  - README (documentation): {filepath} ({elapsed:.2f}s)")


def _export_project_yaml(args, result, output_dir: Path):
    """Export unified project.yaml — single source of truth."""
    exporter = ProjectYAMLExporter()
    filepath = output_dir / 'project.yaml'
    t0 = time.monotonic()
    exporter.export(result, str(filepath))
    elapsed = time.monotonic() - t0
    _inject_time(filepath, elapsed)
    if getattr(args, 'verbose', False):
        print(f"  - PROJECT-YAML (single source of truth): {filepath} ({elapsed:.2f}s)")
    return filepath


def _export_project_toon(args, result, output_dir: Path):
    """Export project.toon.yaml directly from the current analysis result."""
    from ..exporters.project_yaml.evolution import load_previous_evolution

    project_yaml_exporter = ProjectYAMLExporter()
    prev_evolution = load_previous_evolution(output_dir / 'project.yaml')
    data = project_yaml_exporter._build_project_yaml(result, prev_evolution)

    exporter = ToonViewGenerator()
    filepath = output_dir / 'project.toon.yaml'
    t0 = time.monotonic()
    exporter.generate(data, str(filepath))
    elapsed = time.monotonic() - t0
    _inject_time(filepath, elapsed)

    if getattr(args, 'verbose', False):
        print(f"  - PROJECT-TOON (project overview): {filepath} ({elapsed:.2f}s)")

    return filepath


def _run_report(args, project_yaml_path: str, output_dir: Path) -> None:
    """Generate views from project.yaml.

    Supported formats: toon, context, article, html, all.
    """
    data = load_project_yaml(project_yaml_path)
    report_formats = [f.strip() for f in args.report_format.split(',')]
    if 'all' in report_formats:
        report_formats = ['toon', 'context', 'article', 'html']

    generator_map = {
        'toon': ('project.toon.yaml', ToonViewGenerator(), 'TOON view'),
        'context': ('context.md', ContextViewGenerator(), 'Context view'),
        'article': ('status.md', ArticleViewGenerator(), 'Article view'),
        'html': ('dashboard.html', HTMLDashboardGenerator(), 'HTML dashboard'),
    }

    for fmt in report_formats:
        if fmt not in generator_map:
            print(f"Warning: unknown report format '{fmt}', skipping", file=sys.stderr)
            continue
        filename, generator, label = generator_map[fmt]
        filepath = output_dir / filename
        generator.generate(data, str(filepath))
        if getattr(args, 'verbose', False):
            print(f"  - {label}: {filepath}")


def _export_simple_formats(args, result, output_dir: Path, formats):
    """Export toon, map, flow, context, yaml, json, project-yaml formats."""
    format_map = {
        'toon': (ToonExporter, 'analysis.toon.yaml', 'TOON (diagnostics)'),
        'map': (MapExporter, 'map.toon.yaml', 'MAP (structure)'),
        'flow': (FlowExporter, 'flow.toon.yaml', 'FLOW (data-flow)'),
        'context': (ContextExporter, 'context.md', 'CONTEXT (LLM narrative)'),
    }

    for fmt, (exporter_cls, filename, label) in format_map.items():
        if fmt in formats:
            exporter = exporter_cls()
            # Export as plain text TOON format with .toon.yaml extension
            filepath = output_dir / filename
            t0 = time.monotonic()
            exporter.export(result, str(filepath))
            elapsed = time.monotonic() - t0
            _inject_time(filepath, elapsed)
            if args.verbose:
                print(f"  - {label}: {filepath} ({elapsed:.2f}s)")

    # Unified project.yaml (single source of truth)
    if 'project-yaml' in formats:
        yaml_path = _export_project_yaml(args, result, output_dir)
        # Auto-generate all views from project.yaml
        data = load_project_yaml(str(yaml_path))
        view_map = {
            'project.toon.yaml': ToonViewGenerator(),
            'context.md': ContextViewGenerator(),
            'dashboard.html': HTMLDashboardGenerator(),
        }
        for filename, generator in view_map.items():
            filepath = output_dir / filename
            generator.generate(data, str(filepath))
            if args.verbose:
                print(f"  - Generated view: {filepath}")

        # Auto-validate consistency
        from ..exporters.validate_project import validate_project_yaml
        is_valid, issues = validate_project_yaml(output_dir, verbose=args.verbose)
        if not is_valid and not args.verbose:
            print(f"  ⚠ project.yaml validation: {len(issues)} issue(s)", file=sys.stderr)
            for issue in issues:
                print(f"    - {issue}", file=sys.stderr)

    if 'yaml' in formats:
        _export_yaml(args, result, output_dir)

    if 'json' in formats:
        exporter = JSONExporter()
        filepath = output_dir / 'analysis.json'
        exporter.export(result, str(filepath), include_defaults=args.full)
        if args.verbose:
            print(f"  - JSON: {filepath}")


def _export_yaml(args, result, output_dir: Path):
    """Export YAML with optional split/separated modes."""
    exporter = YAMLExporter()
    if args.separate_orphans:
        sep_dir = output_dir / 'separated'
        exporter.export_separated(result, str(sep_dir), compact=True)
        if args.verbose:
            print(f"  - YAML (separated): {sep_dir}/")
    elif args.split_output:
        split_dir = output_dir / 'split'
        exporter.export_split(result, str(split_dir), include_defaults=args.full)
        if args.verbose:
            print(f"  - YAML (split): {split_dir}/")
    else:
        filepath = output_dir / 'analysis.yaml'
        exporter.export(result, str(filepath), include_defaults=args.full)
        if args.verbose:
            print(f"  - YAML: {filepath}")


def _export_mermaid_pngs(args, output_dir: Path) -> None:
    """Attempt PNG generation from .mmd files, with graceful fallback."""
    if args.no_png:
        if args.verbose:
            print(f"  - PNG: Skipped (--no-png)")
        return
    try:
        from ..generators.mermaid import generate_pngs
        png_count = generate_pngs(output_dir, output_dir)
        if args.verbose and png_count > 0:
            print(f"  - PNG: {png_count} files generated")
    except ImportError:
        try:
            import subprocess
            script_path = Path(__file__).parent.parent.parent / 'mermaid_to_png.py'
            if script_path.exists():
                png_result = subprocess.run(
                    ['python', str(script_path), '--batch', str(output_dir), str(output_dir)],
                    capture_output=True, text=True, timeout=60,
                )
                if png_result.returncode == 0 and args.verbose:
                    print(f"  - PNG: {output_dir / '*.png'}")
        except Exception:
            if args.verbose:
                print(f"  - PNG: Skipped (install with: make install-mermaid)")


def _export_calls_format(args, result, output_dir: Path, toon: bool = False) -> None:
    """Shared helper: export call graph in YAML or toon format."""
    yaml_exporter = YAMLExporter()
    if toon:
        yaml_exporter.export_calls_toon(result, str(output_dir / 'calls.toon.yaml'))
        if args.verbose:
            print(f"  - CALLS (toon format): {output_dir / 'calls.toon.yaml'}")
    else:
        yaml_exporter.export_calls(result, str(output_dir / 'calls.yaml'))
        if args.verbose:
            print(f"  - CALLS (call graph YAML): {output_dir / 'calls.yaml'}")


def _export_calls(args, result, output_dir: Path):
    """Export standalone calls.yaml (structured call graph YAML)."""
    _export_calls_format(args, result, output_dir, toon=False)


def _export_calls_toon(args, result, output_dir: Path):
    """Export calls.toon.yaml (call graph in human-readable toon format)."""
    _export_calls_format(args, result, output_dir, toon=True)


def _export_mermaid(args, result, output_dir: Path):
    """Export Mermaid diagrams + optional PNG generation.
    
    Plan R1: 3-level flow diagrams
    - flow.mmd (compact, ~50 nodes) - architectural view [default]
    - flow_detailed.mmd (~150 nodes) - per-module view [with --flow-detail]
    - flow_full.mmd (all nodes) - debug view [with --flow-full]
    """
    exporter = MermaidExporter()
    include_examples = getattr(args, 'flow_include_examples', False)

    exporter.export_flow_compact(result, str(output_dir / 'flow.mmd'), include_examples)
    if getattr(args, 'flow_detail', False):
        exporter.export_flow_detailed(result, str(output_dir / 'flow_detailed.mmd'), include_examples)
    if getattr(args, 'flow_full', False):
        exporter.export_flow_full(result, str(output_dir / 'flow_full.mmd'), include_examples)

    exporter.export_call_graph(result, str(output_dir / 'calls.mmd'))
    exporter.export_compact(result, str(output_dir / 'compact_flow.mmd'))

    # Export calls.yaml (structured call graph data) and calls.toon.yaml (human-readable)
    yaml_exporter = YAMLExporter()
    yaml_exporter.export_calls(result, str(output_dir / 'calls.yaml'))
    yaml_exporter.export_calls_toon(result, str(output_dir / 'calls.toon.yaml'))

    if args.verbose:
        files = ['flow.mmd']
        if getattr(args, 'flow_detail', False):
            files.append('flow_detailed.mmd')
        if getattr(args, 'flow_full', False):
            files.append('flow_full.mmd')
        files.extend(['calls.mmd', 'compact_flow.mmd', 'calls.yaml'])
        print(f"  - Mermaid: {output_dir}/*.mmd ({', '.join(files)})")

    _export_mermaid_pngs(args, output_dir)


def _export_refactor_prompts(args, result, output_dir: Path):
    """Generate AI-driven refactoring prompts."""
    from ..refactor.prompt_engine import PromptEngine
    prompt_engine = PromptEngine(result)
    prompts = prompt_engine.generate_prompts()

    if prompts:
        prompts_dir = output_dir / 'prompts'
        prompts_dir.mkdir(parents=True, exist_ok=True)

        if args.smell:
            prompts = {k: v for k, v in prompts.items() if args.smell in k.lower()}

        for filename, content in prompts.items():
            prompt_path = prompts_dir / filename
            prompt_path.write_text(content)

        if args.verbose:
            print(f"  - Refactoring prompts: {prompts_dir}/ ({len(prompts)} files)")
    else:
        if args.verbose:
            print("  - Refactoring: No code smells detected.")


def _export_index_html(args, output_dir: Path) -> None:
    """Generate index.html for browsing all generated files."""
    # Only generate index.html when 'all' formats is used
    if 'all' not in args.format:
        return
    
    try:
        generator = IndexHTMLGenerator(output_dir)
        index_path = generator.generate()
        if args.verbose:
            print(f"  - INDEX (file browser): {index_path}")
    except Exception as e:
        if args.verbose:
            print(f"  - INDEX generation failed: {e}", file=sys.stderr)
