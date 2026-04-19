"""Export orchestration — registry-based dispatch for cleaner code.

Refactored to use EXPORT_REGISTRY for core format dispatch.
Maintains backward compatibility with all existing --format values.
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

from code2llm.exporters import (
    get_exporter,
    EXPORT_REGISTRY,
    YAMLExporter,
    MermaidExporter,
    ToonViewGenerator,
    IndexHTMLGenerator,
)
from code2llm.exporters.project_yaml.evolution import load_previous_evolution


# Format output filenames
FORMAT_FILENAMES: Dict[str, str] = {
    'toon': 'analysis.toon.yaml',
    'map': 'map.toon.yaml',
    'flow': 'flow.toon.yaml',
    'context': 'context.md',
    'yaml': 'analysis.yaml',
    'json': 'analysis.json',
    'evolution': 'evolution.toon.yaml',
    'readme': 'README.md',
    'project-yaml': 'project.yaml',
}

# Human-readable labels
FORMAT_LABELS: Dict[str, str] = {
    'toon': 'TOON (diagnostics)',
    'map': 'MAP (structure)',
    'flow': 'FLOW (data-flow)',
    'context': 'CONTEXT (LLM narrative)',
    'yaml': 'YAML',
    'json': 'JSON',
    'evolution': 'EVOLUTION (refactoring queue)',
    'readme': 'README (documentation)',
    'project-yaml': 'PROJECT-YAML (single source of truth)',
}


def _run_exports(args, result, output_dir: Path, source_path: Optional[Path] = None):
    """Export analysis results in requested formats.

    Uses EXPORT_REGISTRY for core format dispatch.
    For chunked analysis, exports to subproject subdirectories.
    """
    requested_formats = [f.strip() for f in args.format.split(',')]
    formats = _expand_all_formats(requested_formats, getattr(args, 'png', False))
    is_chunked = getattr(args, 'chunk', False)

    try:
        if is_chunked and source_path:
            _export_chunked(args, result, output_dir, source_path, formats, requested_formats)
        else:
            _export_single(args, result, output_dir, formats, requested_formats, source_path)
    except Exception as e:
        print(f"Error during export: {e}", file=sys.stderr)
        sys.exit(1)


def _expand_all_formats(requested: List[str], include_png: bool = False) -> List[str]:
    """Expand 'all' to concrete format list."""
    if 'all' not in requested:
        return requested[:]
    formats = ['toon', 'map', 'context', 'evolution']
    if include_png:
        formats.append('mermaid')
    return formats


def _export_single(
    args, result, output_dir: Path,
    formats: List[str], requested_formats: List[str],
    source_path: Optional[Path] = None
):
    """Export single project results."""
    # Core formats via registry
    _export_registry_formats(args, result, output_dir, formats)

    # Special/conditional formats
    if 'mermaid' in formats:
        _export_mermaid(args, result, output_dir)
    if 'calls' in formats or 'calls_toon' in formats:
        _export_calls(args, result, output_dir, formats)

    # Evolution always exported for 'all' or 'evolution' (handled by registry)
    # Context fallback only if not explicitly requested
    if 'context' not in formats and 'all' not in requested_formats:
        _export_context_fallback(args, result, output_dir)

    # project.toon.yaml for 'all' mode
    if 'all' in requested_formats:
        _export_project_toon(args, result, output_dir)

    # Optional exports
    if source_path is not None:
        from .code2logic import _export_code2logic
        from .prompt import _export_prompt_txt
        _export_code2logic(args, source_path, output_dir, formats)
        _export_prompt_txt(args, output_dir, requested_formats, source_path)

    if getattr(args, 'refactor', False):
        from .formats import _export_refactor_prompts
        _export_refactor_prompts(args, result, output_dir)

    if getattr(args, 'data_structures', False):
        _export_data_structures(args, result, output_dir)

    # Always export README and index
    _export_readme(args, result, output_dir)
    _export_index_html(args, output_dir)


def _export_registry_formats(args, result, output_dir: Path, formats: List[str]):
    """Export core formats via EXPORT_REGISTRY lookup."""
    for fmt in formats:
        exporter_cls = get_exporter(fmt)
        if exporter_cls is None:
            continue

        filename = FORMAT_FILENAMES.get(fmt, f'{fmt}.export')
        label = FORMAT_LABELS.get(fmt, fmt.upper())
        filepath = output_dir / filename

        exporter = exporter_cls()
        kwargs = _get_format_kwargs(fmt, args)

        try:
            exporter.export(result, str(filepath), **kwargs)
            if args.verbose:
                print(f"  - {label}: {filepath}")
        except Exception as e:
            if args.verbose:
                print(f"  - {label} export failed: {e}", file=sys.stderr)


def _get_format_kwargs(fmt: str, args) -> Dict[str, Any]:
    """Get format-specific kwargs for export."""
    kwargs: Dict[str, Any] = {}
    if fmt in ('yaml', 'json'):
        kwargs['compact'] = not args.full
        kwargs['include_defaults'] = args.full
    return kwargs


def _export_mermaid(args, result, output_dir: Path):
    """Export mermaid diagrams."""
    exporter = MermaidExporter()
    include_examples = getattr(args, 'flow_include_examples', False)

    # Core diagrams
    exporter.export_flow_compact(result, str(output_dir / 'flow.mmd'), include_examples)
    exporter.export_call_graph(result, str(output_dir / 'calls.mmd'))
    exporter.export_compact(result, str(output_dir / 'compact_flow.mmd'))

    # Optional detailed diagrams
    if getattr(args, 'flow_detail', False):
        exporter.export_flow_detailed(result, str(output_dir / 'flow_detailed.mmd'), include_examples)
    if getattr(args, 'flow_full', False):
        exporter.export_flow_full(result, str(output_dir / 'flow_full.mmd'), include_examples)

    # Also export calls.yaml/toon
    yaml_exporter = YAMLExporter()
    yaml_exporter.export_calls(result, str(output_dir / 'calls.yaml'))
    yaml_exporter.export_calls_toon(result, str(output_dir / 'calls.toon.yaml'))

    if args.verbose:
        files = ['flow.mmd', 'calls.mmd', 'compact_flow.mmd', 'calls.yaml']
        if getattr(args, 'flow_detail', False):
            files.append('flow_detailed.mmd')
        if getattr(args, 'flow_full', False):
            files.append('flow_full.mmd')
        print(f"  - Mermaid: {output_dir}/*.mmd ({', '.join(files)})")

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

    project_yaml_exporter = ProjectYAMLExporter()
    prev_evolution = load_previous_evolution(output_dir / 'project.yaml')
    data = project_yaml_exporter._build_project_yaml(result, prev_evolution)

    generator = ToonViewGenerator()
    generator.generate(data, str(output_dir / 'project.toon.yaml'))

    if args.verbose:
        print(f"  - PROJECT-TOON (project overview): {output_dir / 'project.toon.yaml'}")


def _export_readme(args, result, output_dir: Path):
    """Export README.md."""
    if getattr(args, 'no_readme', False):
        return
    exporter_cls = get_exporter('readme')
    if exporter_cls:
        exporter = exporter_cls()
        exporter.export(result, str(output_dir / 'README.md'))
        if args.verbose:
            print(f"  - README (documentation): {output_dir / 'README.md'}")


def _export_index_html(args, output_dir: Path):
    """Generate index.html for browsing files."""
    if 'all' not in getattr(args, 'format', ''):
        return
    try:
        generator = IndexHTMLGenerator(output_dir)
        index_path = generator.generate()
        if args.verbose:
            print(f"  - INDEX (file browser): {index_path}")
    except Exception as e:
        if args.verbose:
            print(f"  - INDEX generation failed: {e}", file=sys.stderr)


def _export_chunked(
    args, result, output_dir: Path, source_path: Path,
    formats: List[str], requested_formats: List[str]
):
    """Export chunked analysis results."""
    subprojects = _get_filtered_subprojects(args, source_path)

    for sp in subprojects:
        _process_subproject(args, sp, output_dir)

    # Merged summary
    _export_registry_formats(args, result, output_dir, ['toon', 'context', 'evolution'])

    if 'calls' in formats or 'calls_toon' in formats:
        _export_calls(args, result, output_dir, formats)
    if 'all' in requested_formats:
        _export_project_toon(args, result, output_dir)

    if source_path is not None:
        from .code2logic import _export_code2logic
        from .prompt import _export_chunked_prompt_txt
        _export_code2logic(args, source_path, output_dir, formats)
        _export_chunked_prompt_txt(args, output_dir, requested_formats, source_path, subprojects)

    _export_readme(args, result, output_dir)
    _export_index_html(args, output_dir)


def _get_filtered_subprojects(args, source_path: Path):
    """Get filtered subprojects list."""
    from ..core.large_repo import HierarchicalRepoSplitter

    splitter = HierarchicalRepoSplitter(size_limit_kb=args.chunk_size)
    subprojects = splitter.get_analysis_plan(source_path)

    if getattr(args, 'only_subproject', None):
        subprojects = [
            sp for sp in subprojects
            if sp.name == args.only_subproject or sp.name.startswith(args.only_subproject + '.')
        ]
    if getattr(args, 'skip_subprojects', None):
        subprojects = [
            sp for sp in subprojects
            if not any(sp.name.startswith(skip) for skip in args.skip_subprojects)
        ]
    return subprojects


def _process_subproject(args, sp, output_dir: Path):
    """Process a single subproject result."""
    sp_output_dir = output_dir / sp.name.replace('.', '_')
    if not sp_output_dir.exists():
        return
    for ext in ['.toon', '.yaml', '.json']:
        result_file = sp_output_dir / f'analysis{ext}'
        if result_file.exists():
            if args.verbose:
                level_name = {0: 'root', 1: 'L1', 2: 'L2'}.get(sp.level, f'L{sp.level}')
                print(f"  - Exported [{level_name}] {sp.name}")
            break


# Backward-compatible aliases
_export_single_project = _export_single
_export_chunked_results = _export_chunked
