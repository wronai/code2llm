"""Export orchestration — registry-based dispatch for cleaner code.

Refactored to use EXPORT_REGISTRY for core format dispatch.
Maintains backward compatibility with all existing --format values.
"""

import os
import shutil
import sys
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

# Optional progress bar support
try:
    from tqdm import tqdm
    _HAS_TQDM = True
except ImportError:
    _HAS_TQDM = False

from code2llm.exporters import (
    get_exporter,
    EXPORT_REGISTRY,
    YAMLExporter,
    MermaidExporter,
    ToonViewGenerator,
    IndexHTMLGenerator,
)
from code2llm.exporters.project_yaml.evolution import load_previous_evolution
from code2llm.core.persistent_cache import PersistentCache
from code2llm.core.config import DEFAULT_PROGRESS_BAR_THRESHOLD
from .orchestrator_constants import (
    FORMAT_FILENAMES,
    FORMAT_DRY_RUN_FILES,
    FORMAT_LABELS,
)
from .orchestrator_handlers import (
    _export_mermaid,
    _export_calls,
    _export_context_fallback,
    _export_data_structures,
    _export_project_toon,
    _export_readme,
    _export_index_html,
)
from .orchestrator_chunked import (
    _get_filtered_subprojects,
    _process_subproject,
)


def _build_export_config(args, formats: List[str]) -> Dict[str, Any]:
    """Build config dict for export caching."""
    return {
        'formats': sorted(formats),
        'png': getattr(args, 'png', False),
        'no_png': getattr(args, 'no_png', False),
        'flow_include_examples': getattr(args, 'flow_include_examples', False),
        'full': getattr(args, 'full', False),
        'refactor': getattr(args, 'refactor', False),
        'data_structures': getattr(args, 'data_structures', False),
    }


def _collect_dry_run_files(formats: List[str], output_dir: Path) -> List[Path]:
    """Return the list of files that would be written for the given formats."""
    output_files: List[Path] = []
    for fmt in formats:
        for name in FORMAT_DRY_RUN_FILES.get(fmt, []):
            output_files.append(output_dir / name)
    output_files.append(output_dir / 'project.toon.yaml')
    output_files.append(output_dir / 'prompt.txt')
    return output_files


def _show_dry_run_plan(formats: List[str], output_dir: Path, is_chunked: bool, result) -> None:
    """Display what would be exported in dry-run mode."""
    print("\n📋 DRY-RUN: Would export the following:\n")

    output_files = _collect_dry_run_files(formats, output_dir)

    size_hint = ""
    func_count = len(getattr(result, 'functions', []))
    if func_count > 0:
        size_hint = f" (~{func_count * 50 // 1024}KB est.)"

    for f in sorted(set(output_files)):
        print(f"  📄 {f}{size_hint}")

    stats = getattr(result, 'stats', {})
    if stats:
        print(f"\n📊 Based on analysis:")
        print(f"  - Functions: {stats.get('functions_found', 'N/A')}")
        print(f"  - Classes: {stats.get('classes_found', 'N/A')}")
        print(f"  - Files: {stats.get('files_processed', 'N/A')}")

    print(f"\n✅ Dry-run complete. Use without --dry-run to export.\n")


def _run_exports(args, result, output_dir: Path, source_path: Optional[Path] = None):
    """Export analysis results in requested formats.

    Uses EXPORT_REGISTRY for core format dispatch.
    For chunked analysis, exports to subproject subdirectories.
    Supports export-level caching for repeated runs.
    """
    requested_formats = [f.strip() for f in args.format.split(',')]
    formats = _expand_all_formats(requested_formats, getattr(args, 'png', False))
    is_chunked = getattr(args, 'chunk', False)
    dry_run = getattr(args, 'dry_run', False)

    # Dry-run: show what would be exported without writing
    if dry_run:
        _show_dry_run_plan(formats, output_dir, is_chunked, result)
        return

    # Skip cache for chunked or when explicitly disabled
    skip_cache = is_chunked or getattr(args, 'no_cache', False)

    if not skip_cache and source_path:
        cache = PersistentCache(str(source_path))
        config_dict = _build_export_config(args, formats)
        cached_export_dir = cache.get_export_cache_dir(config_dict)

        if cached_export_dir:
            if args.verbose:
                print(f"  Using cached export from: {cached_export_dir}")
            # Copy cached files to output_dir
            _copy_cached_export(cached_export_dir, output_dir, verbose=args.verbose)
            return

    try:
        if is_chunked and source_path:
            _export_chunked(args, result, output_dir, source_path, formats, requested_formats)
        else:
            _export_single(args, result, output_dir, formats, requested_formats, source_path)

        # Mark export as complete in cache
        if not skip_cache and source_path:
            cache = PersistentCache(str(source_path))
            config_dict = _build_export_config(args, formats)
            export_cache_dir = cache.create_export_cache_dir(config_dict)
            _copy_to_cache(output_dir, export_cache_dir, verbose=args.verbose)
            cache.mark_export_complete(export_cache_dir)
            cache.save()
            if args.verbose:
                print(f"  Export cached at: {export_cache_dir}")

    except Exception as e:
        print(f"Error during export: {e}", file=sys.stderr)
        sys.exit(1)


def _copy_cached_export(cached_dir: Path, output_dir: Path, verbose: bool = False) -> None:
    """Copy files from cached export to output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    items = [item for item in cached_dir.iterdir() if item.name != '_complete']

    # Progress bar for large cache restores
    use_tqdm = _HAS_TQDM and not verbose and len(items) > DEFAULT_PROGRESS_BAR_THRESHOLD
    item_iterator = tqdm(items, desc="Restoring from cache") if use_tqdm else items

    for item in item_iterator:
        dest = output_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)
        # Refresh mtime so the user can tell these files were produced by
        # the current run, even though the contents came from cache.
        _touch_recursive(dest)


def _touch_recursive(path: Path) -> None:
    """Update mtime/atime to now for `path` (and all contents if it is a dir)."""
    try:
        os.utime(path, None)
    except OSError:
        return
    if path.is_dir():
        for sub in path.rglob('*'):
            try:
                os.utime(sub, None)
            except OSError:
                continue


def _copy_to_cache(output_dir: Path, cache_dir: Path, verbose: bool = False) -> None:
    """Copy export files to cache directory."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    if not output_dir.exists():
        return

    items = list(output_dir.iterdir())
    # Progress bar for large cache saves
    use_tqdm = _HAS_TQDM and not verbose and len(items) > DEFAULT_PROGRESS_BAR_THRESHOLD
    item_iterator = tqdm(items, desc="Saving to cache") if use_tqdm else items

    for item in item_iterator:
        dest = cache_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)


def _expand_all_formats(requested: List[str], include_png: bool = False) -> List[str]:
    """Expand 'all' to concrete format list."""
    if 'all' not in requested:
        return requested[:]
    formats = ['toon', 'map', 'context', 'evolution', 'mermaid']
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
    # Use progress bar when many formats and not in verbose mode
    use_tqdm = (
        _HAS_TQDM and
        not args.verbose and
        len(formats) > DEFAULT_PROGRESS_BAR_THRESHOLD
    )

    format_iterator = formats
    if use_tqdm:
        format_iterator = tqdm(formats, desc="Exporting formats")

    for fmt in format_iterator:
        exporter_cls = get_exporter(fmt)
        if exporter_cls is None:
            continue

        filename = FORMAT_FILENAMES.get(fmt, f'{fmt}.export')
        label = FORMAT_LABELS.get(fmt, fmt.upper())
        filepath = output_dir / filename

        exporter = exporter_cls()
        kwargs = _get_format_kwargs(fmt, args)

        try:
            t0 = time.monotonic()
            exporter.export(result, str(filepath), **kwargs)
            elapsed = time.monotonic() - t0
            _inject_generation_time(filepath, elapsed)
            if args.verbose:
                print(f"  - {label}: {filepath} ({elapsed:.2f}s)")
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


def _export_chunked(
    args, result, output_dir: Path, source_path: Path,
    formats: List[str], requested_formats: List[str]
):
    """Export chunked analysis results."""
    from .orchestrator_chunked import _export_chunked as _chunked_impl
    _chunked_impl(args, result, output_dir, source_path, formats, requested_formats)


def _inject_generation_time(filepath: Path, elapsed: float) -> None:
    """Inject generation time comment into the second line of an exported file."""
    try:
        path = Path(filepath)
        if not path.exists():
            return
        suffix = path.suffix.lower()
        name = path.name.lower()

        # Only inject into text-based files
        if suffix not in ('.yaml', '.yml', '.md', '.txt', '.mmd', '.html', '.json', '.export'):
            return

        content = path.read_text(encoding='utf-8')
        if not content:
            return

        tag = f"generated in {elapsed:.2f}s"

        if suffix in ('.yaml', '.yml', '.mmd', '.export', '.txt') or name.endswith('.toon.yaml'):
            # YAML/Mermaid/text: insert '# generated in X.XXs' after first line
            lines = content.split('\n', 1)
            if len(lines) == 2:
                content = f"{lines[0]}\n# {tag}\n{lines[1]}"
            else:
                content = f"{lines[0]}\n# {tag}\n"
        elif suffix == '.md':
            # Markdown: insert HTML comment after first line
            lines = content.split('\n', 1)
            if len(lines) == 2:
                content = f"{lines[0]}\n<!-- {tag} -->\n{lines[1]}"
            else:
                content = f"{lines[0]}\n<!-- {tag} -->\n"
        elif suffix == '.html':
            # HTML: insert comment after <!DOCTYPE or <html>
            content = content.replace('\n', f'\n<!-- {tag} -->\n', 1)
        elif suffix == '.json':
            # JSON doesn't support comments — skip
            return
        else:
            return

        path.write_text(content, encoding='utf-8')
    except Exception:
        pass  # Never fail the export pipeline for a comment


# Backward-compatible aliases
_export_single_project = _export_single
_export_chunked_results = _export_chunked
