"""CLI subcommands and validation for code2llm."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .cli_exports import _run_report
from .core.config import DEFAULT_CACHE_MAX_AGE_DAYS, KB


def handle_special_commands() -> Optional[int]:
    """Handle special sub-commands (llm-flow, llm-context, report, cache)."""
    if len(sys.argv) > 1 and sys.argv[1] == 'llm-flow':
        from .generators.llm_flow import main as llm_flow_main
        return llm_flow_main(sys.argv[2:])
    if len(sys.argv) > 1 and sys.argv[1] == 'llm-context':
        return generate_llm_context(sys.argv[2:])
    if len(sys.argv) > 1 and sys.argv[1] == 'report':
        return handle_report_command(sys.argv[2:])
    if len(sys.argv) > 1 and sys.argv[1] == 'cache':
        return handle_cache_command(sys.argv[2:])
    return None


def handle_cache_command(args_list) -> int:
    """Manage persistent cache (~/.code2llm/).

    Usage:
        code2llm cache status          # show size, projects, last used
        code2llm cache clear           # clear cache for current directory
        code2llm cache clear --all     # clear entire ~/.code2llm/
        code2llm cache gc              # manual garbage collection
    """
    import os
    import time
    from .core.persistent_cache import PersistentCache, get_all_projects, clear_all, _DEFAULT_ROOT

    parser = argparse.ArgumentParser(prog='code2llm cache')
    parser.add_argument('action', choices=['status', 'clear', 'gc'], help='Cache action')
    parser.add_argument('--all', action='store_true', dest='all_projects',
                        help='Apply to all cached projects (clear only)')
    parser.add_argument('--max-age', type=int, default=DEFAULT_CACHE_MAX_AGE_DAYS, metavar='DAYS',
                        help=f'Max age in days for gc (default: {DEFAULT_CACHE_MAX_AGE_DAYS})')
    args = parser.parse_args(args_list)

    if args.action == 'status':
        projects = get_all_projects()
        root = _DEFAULT_ROOT
        total_mb = sum(p.get('cache_size_bytes', 0) for p in projects) / (KB * KB)
        print(f"Cache: {root}")
        print(f"  Projects: {len(projects)}   Total: {total_mb:.1f} MB")
        for p in projects:
            size_mb = p.get('cache_size_bytes', 0) / (KB * KB)
            updated = p.get('updated_at', 0)
            age_min = int((time.time() - updated) / 60) if updated else 0
            age_str = f"{age_min}m ago" if age_min < 120 else f"{age_min//60}h ago"
            exports = p.get('exports', 0)
            files = p.get('files_cached', 0)
            print(f"\n  {p.get('project', '?')}")
            print(f"    Files: {files}   Exports: {exports}   Size: {size_mb:.1f} MB   Last: {age_str}")
        return 0

    if args.action == 'clear':
        if args.all_projects:
            clear_all()
            print("Cleared entire cache.")
        else:
            project_dir = os.path.realpath('.')
            c = PersistentCache(project_dir)
            c.clear()
            print(f"Cleared cache for {project_dir}")
        return 0

    if args.action == 'gc':
        projects = get_all_projects()
        total_removed = 0
        for p in projects:
            project_dir = p.get('project')
            if project_dir and Path(project_dir).exists():
                c = PersistentCache(project_dir)
                removed = c.gc(max_age_days=args.max_age)
                total_removed += removed
        print(f"GC complete: {total_removed} stale entries removed.")
        return 0

    return 0


def handle_report_command(args_list) -> int:
    """Generate views from an existing project.yaml (legacy).

    Usage:
        code2llm report --format toon    # → project.toon.yaml (legacy)
        code2llm report --format context # → context.md
        code2llm report --format article # → status.md
        code2llm report --format html    # → dashboard.html
        code2llm report --format all     # → all views
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog='code2llm report',
        description='Generate views from an existing project.yaml (legacy, single source of truth)',
    )
    parser.add_argument(
        '--input', '-i',
        default='./project.yaml',
        help='Path to legacy project.yaml (default: ./project.yaml)',
    )
    parser.add_argument(
        '--format', '-f',
        dest='report_format',
        default='all',
        help='Output format: toon, context, article, html, all (default: all)',
    )
    parser.add_argument(
        '-o', '--output',
        default='.',
        help='Output directory (default: current directory)',
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output',
    )

    args = parser.parse_args(args_list)

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: project.yaml not found: {input_path}", file=sys.stderr)
        print("If you still need it, use the legacy 'code2llm <source> -f project-yaml' export.", file=sys.stderr)
        return 1

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.verbose:
        print(f"Generating views from: {input_path}")
        print(f"Output directory: {output_dir}")

    _run_report(args, str(input_path), output_dir)

    if args.verbose:
        print(f"\nAll views saved to: {output_dir}")

    return 0


def validate_and_setup(args) -> tuple[Path, Path]:
    """Validate source path and setup output directory."""
    if not args.source:
        print("Error: missing required argument: source", file=sys.stderr)
        print("Usage: code2llm <source> [options]", file=sys.stderr)
        print("   or: code2llm llm-flow [options]", file=sys.stderr)
        sys.exit(2)

    source_path = Path(args.source).resolve()
    if not source_path.exists():
        print(f"Error: Source path not found: {source_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    return source_path, output_dir


def print_start_info(args, source_path: Path, output_dir: Path) -> None:
    """Print analysis start information if verbose."""
    if args.verbose:
        print(f"Analyzing: {source_path}")
        print(f"Mode: {args.mode}")
        print(f"Output: {output_dir}")


def validate_chunked_output(output_dir: Path, args) -> bool:
    """Validate generated chunked output.

    Checks:
    1. All chunks have required files (analysis.toon, context.md, evolution.toon.yaml)
    2. Files are not empty
    3. Report summary

    Returns True if valid, False otherwise.
    """
    if not output_dir.exists():
        print(f"✗ Output directory does not exist: {output_dir}", file=sys.stderr)
        return False

    chunk_dirs = _get_chunk_dirs(output_dir)
    if not chunk_dirs:
        print(f"✗ No chunk directories found in: {output_dir}", file=sys.stderr)
        return False

    required_files = ['analysis.toon.yaml', 'context.md', 'evolution.toon.yaml']
    issues, valid_chunks = _validate_chunks(chunk_dirs, required_files)

    _print_validation_summary(chunk_dirs, valid_chunks, issues)
    return len(issues) == 0


def _get_chunk_dirs(output_dir: Path) -> list[Path]:
    """Find all chunk directories in output directory."""
    return [d for d in output_dir.iterdir() if d.is_dir()]


def _validate_chunks(chunk_dirs: list[Path], required_files: list[str]) -> tuple:
    """Validate all chunks and return issues and valid chunks."""
    issues = []
    valid_chunks = []

    print(f"\n🔍 Validating {len(chunk_dirs)} chunks")
    print("-" * 50)

    for chunk_dir in sorted(chunk_dirs):
        chunk_issues = _validate_single_chunk(chunk_dir, required_files)

        if chunk_issues:
            issues.append((chunk_dir.name, chunk_issues))
            _print_chunk_errors(chunk_dir.name, chunk_issues)
        else:
            sizes = _get_file_sizes(chunk_dir, required_files)
            valid_chunks.append(chunk_dir.name)
            print(f"✓ {chunk_dir.name} ({sizes})")

    print("-" * 50)
    return issues, valid_chunks


def _validate_single_chunk(chunk_dir: Path, required_files: list[str]) -> list[str]:
    """Validate a single chunk directory. Returns list of issues."""
    chunk_issues = []

    for req_file in required_files:
        file_path = chunk_dir / req_file
        if not file_path.exists():
            chunk_issues.append(f"  missing {req_file}")
        elif file_path.stat().st_size == 0:
            chunk_issues.append(f"  empty {req_file}")

    return chunk_issues


def _get_file_sizes(chunk_dir: Path, required_files: list[str]) -> str:
    """Get formatted file sizes for a chunk."""
    sizes = []
    for req_file in required_files:
        size = (chunk_dir / req_file).stat().st_size
        sizes.append(f"{req_file}:{size//KB}KB" if size > KB else f"{req_file}:{size}B")
    return ", ".join(sizes)


def _print_chunk_errors(chunk_name: str, chunk_issues: list[str]) -> None:
    """Print errors for a chunk."""
    print(f"✗ {chunk_name}")
    for issue in chunk_issues:
        print(f"    {issue}")


def _print_validation_summary(chunk_dirs: list, valid_chunks: list, issues: list) -> None:
    """Print validation summary report."""
    print(f"\n📊 Validation Summary:")
    print(f"  Total chunks: {len(chunk_dirs)}")
    print(f"  Valid: {len(valid_chunks)}")
    print(f"  Issues: {len(issues)}")

    if issues:
        print(f"\n⚠️  {len(issues)} chunk(s) have issues:")
        for chunk_name, _ in issues:
            print(f"    - {chunk_name}")
    else:
        print(f"\n✅ All {len(valid_chunks)} chunks are valid!")


def generate_llm_context(args_list):
    """Quick command to generate LLM context only."""
    import argparse
    
    parser = argparse.ArgumentParser(
        prog='code2llm llm-context',
        description='Generate LLM-friendly context for a project'
    )
    parser.add_argument('source', help='Path to Python project')
    parser.add_argument('-o', '--output', default='./llm_context.md', help='Output file path')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args(args_list)
    
    from pathlib import Path
    from . import ProjectAnalyzer, FAST_CONFIG
    from .exporters import ContextExporter
    
    source_path = Path(args.source)
    if not source_path.exists():
        print(f"Error: Source path not found: {source_path}", file=sys.stderr)
        return 1
    
    if args.verbose:
        print(f"Generating LLM context for: {source_path}")
    
    # Use fast config with parallel disabled for stability
    FAST_CONFIG.performance.parallel_enabled = False
    
    analyzer = ProjectAnalyzer(FAST_CONFIG)
    result = analyzer.analyze_project(str(source_path))
    
    exporter = ContextExporter()
    exporter.export(result, args.output)
    
    # Print summary
    print(f"\n✓ LLM context generated: {args.output}")
    print(f"  Functions: {len(result.functions)}")
    print(f"  Classes: {len(result.classes)}")
    print(f"  Modules: {len(result.modules)}")
    
    return 0
