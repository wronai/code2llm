"""Export orchestration — _run_exports, single-project and chunked export flows."""

import sys
from pathlib import Path
from typing import Optional

from .formats import (
    _export_simple_formats,
    _export_mermaid,
    _export_calls,
    _export_evolution,
    _export_data_structures,
    _export_context_fallback,
    _export_project_toon,
    _export_readme,
    _export_refactor_prompts,
    _export_index_html,
)
from .code2logic import _export_code2logic
from .prompt import _export_prompt_txt, _export_chunked_prompt_txt


def _run_exports(args, result, output_dir: Path, source_path: Optional[Path] = None):
    """Export analysis results in requested formats.

    For chunked analysis, exports to subproject subdirectories.
    """
    requested_formats = [f.strip() for f in args.format.split(',')]
    formats = requested_formats[:]
    if 'all' in formats:
        formats = ['toon', 'map', 'context', 'mermaid', 'evolution']

    is_chunked = args.chunk if hasattr(args, 'chunk') else False

    try:
        if is_chunked and source_path:
            _export_chunked_results(args, result, output_dir, source_path, formats, requested_formats)
        else:
            _export_single_project(args, result, output_dir, formats, requested_formats, source_path)
    except Exception as e:
        print(f"Error during export: {e}", file=sys.stderr)
        sys.exit(1)


def _export_single_project(
    args,
    result,
    output_dir: Path,
    formats: list,
    requested_formats: Optional[list] = None,
    source_path: Optional[Path] = None,
):
    """Export single project results."""
    if requested_formats is None:
        requested_formats = formats

    _export_simple_formats(args, result, output_dir, formats)

    if 'mermaid' in formats:
        _export_mermaid(args, result, output_dir)

    if 'calls' in formats:
        _export_calls(args, result, output_dir)

    _export_evolution(args, result, output_dir)
    _export_data_structures(args, result, output_dir)
    _export_context_fallback(args, result, output_dir, formats)

    if 'all' in requested_formats:
        _export_project_toon(args, result, output_dir)

    if source_path is not None:
        _export_code2logic(args, source_path, output_dir, formats)
        _export_prompt_txt(args, output_dir, requested_formats, source_path)

    if hasattr(args, 'refactor') and args.refactor:
        _export_refactor_prompts(args, result, output_dir)

    _export_readme(args, result, output_dir)
    
    # Generate index.html for browsing all files (only when 'all' formats used)
    _export_index_html(args, output_dir)


def _export_chunked_results(
    args,
    result,
    output_dir: Path,
    source_path: Path,
    formats: list,
    requested_formats: Optional[list] = None,
):
    """Export chunked analysis results to subproject directories."""
    if requested_formats is None:
        requested_formats = formats

    subprojects = _get_filtered_subprojects(args, source_path)

    for sp in subprojects:
        _process_subproject_result(args, sp, output_dir)

    # Also create merged summary in root output dir
    _export_simple_formats(args, result, output_dir, ['toon', 'context'])
    _export_evolution(args, result, output_dir)

    if 'all' in requested_formats:
        _export_project_toon(args, result, output_dir)

    if source_path is not None:
        _export_code2logic(args, source_path, output_dir, formats)
        _export_chunked_prompt_txt(args, output_dir, requested_formats, source_path, subprojects)

    _export_readme(args, result, output_dir)

    # Generate index.html for browsing all files (only when 'all' formats used)
    _export_index_html(args, output_dir)


def _get_filtered_subprojects(args, source_path: Path):
    """Get subprojects list with filtering applied."""
    from ..core.large_repo import HierarchicalRepoSplitter

    splitter = HierarchicalRepoSplitter(size_limit_kb=args.chunk_size)
    subprojects = splitter.get_analysis_plan(source_path)

    if hasattr(args, 'only_subproject') and args.only_subproject:
        subprojects = [
            sp for sp in subprojects
            if sp.name == args.only_subproject or sp.name.startswith(args.only_subproject + '.')
        ]

    if hasattr(args, 'skip_subprojects') and args.skip_subprojects:
        subprojects = [
            sp for sp in subprojects
            if not any(sp.name.startswith(skip) for skip in args.skip_subprojects)
        ]

    return subprojects


def _process_subproject_result(args, sp, output_dir: Path) -> None:
    """Process a single subproject result file."""
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
