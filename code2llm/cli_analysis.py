"""Analysis execution — chunked, streaming, and standard analysis flows.

Extracted from cli.py to isolate analysis orchestration from CLI parsing.
"""

import sys
from pathlib import Path
from typing import List, Optional, Tuple


def _run_analysis(args, source_path: Path, output_dir: Path):
    """Run code analysis with configured strategy.

    Returns AnalysisResult or exits on error.
    For large repos, may analyze in chunks and merge results.
    """
    from .core.large_repo import should_use_chunking

    # --no-chunk explicitly disables chunking
    use_chunking = (
        not args.no_chunk and
        (args.chunk or should_use_chunking(source_path, args.chunk_size))
    )

    if use_chunking:
        if args.verbose:
            print(f"Large repository detected - using chunked analysis")
        args.chunk = True
        return _run_chunked_analysis(args, source_path, output_dir)

    return _run_standard_analysis(args, source_path, output_dir)


def _run_standard_analysis(args, source_path: Path, output_dir: Path):
    """Standard single-project analysis flow."""
    from .core.config import Config
    from .core.analyzer import ProjectAnalyzer

    config = _build_config(args, output_dir)

    try:
        if args.streaming or args.strategy in ['quick', 'deep']:
            result = _run_streaming_analysis(args, config, source_path)
        else:
            analyzer = ProjectAnalyzer(config, source_path)
            result = analyzer.analyze_project(str(source_path))

        if args.verbose:
            _print_analysis_summary(result)

        return result

    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        sys.exit(1)


def _build_config(args, output_dir: Path):
    """Build analysis Config from CLI args."""
    from .core.config import Config, FilterConfig
    
    # Start with default filter config
    filter_config = FilterConfig()
    
    # Apply custom exclude patterns if provided
    if hasattr(args, 'exclude') and args.exclude:
        default_patterns = filter_config.exclude_patterns
        custom_patterns = [f"*{pattern}*" if not pattern.startswith('*') and not pattern.endswith('*') else pattern 
                          for pattern in args.exclude]
        filter_config.exclude_patterns = list(set(default_patterns + custom_patterns))
    
    # Apply gitignore setting
    if hasattr(args, 'no_gitignore') and args.no_gitignore:
        filter_config.gitignore_enabled = False
    
    return Config(
        mode=args.mode,
        max_depth_enumeration=args.max_depth,
        detect_state_machines=not args.no_patterns,
        detect_recursion=not args.no_patterns,
        output_dir=str(output_dir),
        filters=filter_config
    )


def _print_analysis_summary(result) -> None:
    """Print analysis completion summary."""
    print(f"\nAnalysis complete:")
    print(f"  - Functions: {len(result.functions)}")
    print(f"  - Classes: {len(result.classes)}")
    print(f"  - CFG nodes: {len(result.nodes)}")
    print(f"  - CFG edges: {len(result.edges)}")


# ------------------------------------------------------------------
# Chunked analysis
# ------------------------------------------------------------------
def _run_chunked_analysis(args, source_path: Path, output_dir: Path):
    """Analyze large repository using hierarchical chunking.

    Strategy:
    1. Level 1 folders first
    2. If >256KB, split to level 2 subfolders
    3. If still too big, use file chunking
    """
    from .core.large_repo import HierarchicalRepoSplitter

    splitter = HierarchicalRepoSplitter(
        size_limit_kb=args.chunk_size,
        max_files_per_chunk=args.max_files_per_chunk
    )

    subprojects = splitter.get_analysis_plan(source_path)

    if args.verbose:
        _print_chunked_plan(subprojects)

    subprojects = _filter_subprojects(args, subprojects)

    all_results = _analyze_all_subprojects(args, subprojects, output_dir)

    merged_result = _merge_chunked_results(all_results, source_path)

    if args.verbose:
        print(f"\nChunked analysis complete:")
        print(f"  - Chunks analyzed: {len(all_results)}")
        print(f"  - Total functions: {len(merged_result.functions)}")
        print(f"  - Total classes: {len(merged_result.classes)}")

    return merged_result


def _print_chunked_plan(subprojects) -> None:
    """Print hierarchical analysis plan summary."""
    print(f"Hierarchical analysis plan ({len(subprojects)} chunks):")
    level_counts = {}
    for sp in subprojects:
        level_counts[sp.level] = level_counts.get(sp.level, 0) + 1

    for level in sorted(level_counts.keys()):
        level_name = {0: 'root', 1: 'level-1', 2: 'level-2', 3: 'file-chunks'}.get(level, f'level-{level}')
        print(f"  {level_name}: {level_counts[level]} chunks")

    print("\nChunks:")
    for sp in subprojects:
        level_indicator = "  " * sp.level
        size_info = f"~{sp.estimated_size_kb}KB"
        print(f"{level_indicator}{sp.name}: {sp.file_count} files ({size_info})")


def _filter_subprojects(args, subprojects) -> list:
    """Apply --only-subproject and --skip-subprojects filters."""
    if args.only_subproject:
        subprojects = [
            sp for sp in subprojects
            if sp.name == args.only_subproject
            or sp.name.startswith(args.only_subproject + '.')
        ]
        if not subprojects:
            print(f"Error: Subproject '{args.only_subproject}' not found", file=sys.stderr)
            sys.exit(1)

    if args.skip_subprojects:
        subprojects = [
            sp for sp in subprojects
            if not any(sp.name.startswith(skip) for skip in args.skip_subprojects)
        ]

    return subprojects


def _analyze_all_subprojects(args, subprojects, output_dir: Path) -> list:
    """Analyze each subproject and collect results."""
    all_results = []
    for i, subproject in enumerate(subprojects, 1):
        if args.verbose:
            level_name = {0: 'root', 1: 'L1', 2: 'L2', 3: 'chunk'}.get(subproject.level, f'L{subproject.level}')
            print(f"\n[{i}/{len(subprojects)}] Analyzing [{level_name}]: {subproject.name}")

        sp_output_dir = output_dir / subproject.name.replace('.', '_')
        sp_output_dir.mkdir(parents=True, exist_ok=True)

        result = _analyze_subproject(args, subproject, sp_output_dir)
        if result:
            all_results.append((subproject.name, result, sp_output_dir))
    return all_results


def _analyze_subproject(args, subproject, output_dir: Path):
    """Analyze and export a single subproject."""
    from .core.analyzer import ProjectAnalyzer
    from .core.config import Config, FilterConfig
    from .cli_exports import _export_simple_formats, _export_evolution

    # Start with default filter config
    filter_config = FilterConfig()
    
    # Apply custom exclude patterns if provided
    if hasattr(args, 'exclude') and args.exclude:
        default_patterns = filter_config.exclude_patterns
        custom_patterns = [f"*{pattern}*" if not pattern.startswith('*') and not pattern.endswith('*') else pattern 
                          for pattern in args.exclude]
        filter_config.exclude_patterns = list(set(default_patterns + custom_patterns))
    
    # Apply gitignore setting
    if hasattr(args, 'no_gitignore') and args.no_gitignore:
        filter_config.gitignore_enabled = False

    config = Config(
        mode=args.mode,
        max_depth_enumeration=args.max_depth,
        detect_state_machines=not args.no_patterns,
        detect_recursion=not args.no_patterns,
        output_dir=str(output_dir),
        verbose=args.verbose,
        filters=filter_config
    )

    analyzer = ProjectAnalyzer(config, subproject.path)

    try:
        result = analyzer.analyze_project(str(subproject.path))

        formats = [f.strip() for f in args.format.split(',')]
        if 'all' in formats:
            formats = ['toon', 'context', 'evolution', 'code2logic']

        _export_simple_formats(args, result, output_dir, formats)

        if 'evolution' in formats or 'all' in formats:
            _export_evolution(args, result, output_dir)

        if args.verbose:
            print(f"    ✓ Exported {subproject.name}: {len(result.functions)} functions")

        return result
    except Exception as e:
        print(f"Warning: Failed to analyze {subproject.name}: {e}", file=sys.stderr)
        return None


def _merge_chunked_results(all_results, source_path: Path):
    """Merge results from multiple subproject analyses."""
    from .core.models import AnalysisResult

    merged = AnalysisResult(project_path=str(source_path))

    for name, result, output_dir in all_results:
        if not result:
            continue

        prefix = f"{name}."

        for func_name, func_info in result.functions.items():
            new_name = f"{prefix}{func_name}" if '.' not in func_name else func_name
            merged.functions[new_name] = func_info

        for class_name, class_info in result.classes.items():
            new_name = f"{prefix}{class_name}" if '.' not in class_name else class_name
            merged.classes[new_name] = class_info

        for mod_name, mod_info in result.modules.items():
            new_name = f"{prefix}{mod_name}" if '.' not in mod_name else mod_name
            merged.modules[new_name] = mod_info

        merged.nodes.update(result.nodes)
        merged.edges.extend(result.edges)

    return merged


# ------------------------------------------------------------------
# Streaming analysis
# ------------------------------------------------------------------
def _run_streaming_analysis(args, config, source_path: Path):
    """Run streaming analysis with progress reporting."""
    from .core.analyzer import ProjectAnalyzer
    from .core.streaming_analyzer import (
        StreamingAnalyzer, STRATEGY_QUICK,
        STRATEGY_STANDARD, STRATEGY_DEEP
    )

    strategy_map = {
        'quick': STRATEGY_QUICK,
        'standard': STRATEGY_STANDARD,
        'deep': STRATEGY_DEEP
    }
    strategy = strategy_map.get(args.strategy, STRATEGY_STANDARD)

    strategy.max_files_in_memory = min(
        strategy.max_files_in_memory,
        args.max_memory // 10
    )

    analyzer = StreamingAnalyzer(config, strategy)

    if args.verbose:
        def on_progress(update):
            pct = update.get('percentage', 0)
            print(f"\r[{pct:.0f}%] {update.get('message', '')}", end='', flush=True)
        analyzer.set_progress_callback(on_progress)

    print(f"Analyzing with {args.strategy} strategy...")
    for update in analyzer.analyze_streaming(str(source_path)):
        if update['type'] == 'complete':
            if args.verbose:
                print()
            print(f"Completed in {update.get('elapsed_seconds', 0):.1f}s")

    # Re-run standard analyzer for full results
    # TODO: Modify streaming to accumulate results properly
    analyzer = ProjectAnalyzer(config)
    return analyzer.analyze_project(str(source_path))
