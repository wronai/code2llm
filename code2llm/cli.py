#!/usr/bin/env python3
"""
code2llm - CLI for Python code flow analysis

Analyze control flow, data flow, and call graphs of Python codebases.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .core.config import Config, ANALYSIS_MODES
from .core.analyzer import ProjectAnalyzer
from .cli_exports import (
    _export_evolution, _export_data_structures, _export_context_fallback,
    _export_readme, _export_code2logic, _export_prompt_txt, _run_exports,
    _export_simple_formats, _export_yaml, _export_mermaid, _export_refactor_prompts,
)



def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog='code2llm',
        description='Analyze Python code control flow, data flow, and call graphs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  code2llm ./                                       # Default: TOON diagnostics + README
  code2llm ./ -f all -o ./docs                      # All formats to ./docs/
  code2llm ./ -f toon,map,flow                      # Diagnostics + structure + data-flow
  code2llm ./ -f context                            # LLM narrative (context.md)
  code2llm ./ --streaming --strategy deep -f all    # Deep streaming analysis, all outputs
  code2llm ./ --strategy quick -f toon              # Fast overview
  code2llm ./ --refactor                            # AI refactoring prompts
  code2llm ./ --refactor --smell god_function       # Filter by smell type
  code2llm ./ -f yaml --split-output                # Split YAML into multiple files
  code2llm ./ -f yaml --separate-orphans            # Separate orphaned functions
  code2llm ./ -f mermaid --no-png                   # Mermaid diagrams without PNG
  code2llm ./ -m static -v -o ./analysis            # Static mode, verbose
  code2llm ./ --no-readme                           # Disable README generation
  code2llm llm-flow                                 # Generate LLM flow summary
  code2llm llm-context ./                           # Generate LLM context only

Format Options (-f):
  toon      — Health diagnostics (analysis.toon) [default]
  map       — Structural map (map.toon) — modules, imports, signatures
  flow      — Data-flow analysis (flow.toon) — pipelines, contracts, types
  context   — LLM narrative (context.md) — architecture summary
  code2logic — Generate project logic (project.toon) via external code2logic
  yaml      — Standard YAML format
  json      — Machine-readable JSON
  mermaid   — Flowchart diagrams (flow.mmd, calls.mmd, compact_flow.mmd)
  evolution — Refactoring queue (evolution.toon)
  all       — Generate all formats

Strategy Options (--strategy):
  quick     — Fast overview, fewer files analyzed
  standard  — Balanced analysis [default]
  deep      — Complete analysis, all files
        '''
    )
    
    # Add backward compatibility source argument first
    parser.add_argument(
        'source',
        nargs='?',
        help='Path to Python source file or directory'
    )
    
    parser.add_argument(
        '-m', '--mode',
        choices=list(ANALYSIS_MODES.keys()),
        default='hybrid',
        help=f'Analysis mode (default: hybrid)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='./code2llm_output',
        help='Output directory (default: ./code2llm_output)'
    )
    
    parser.add_argument(
        '-f', '--format',
        default='toon',
        help='Output formats: toon,map,flow,context,code2logic,yaml,json,mermaid,evolution,png,all (default: toon)'
    )
    
    parser.add_argument(
        '--full',
        action='store_true',
        help='Include all fields in output (including empty/null values)'
    )
    
    parser.add_argument(
        '--no-patterns',
        action='store_true',
        help='Disable pattern detection'
    )
    
    parser.add_argument(
        '--max-depth',
        type=int,
        default=10,
        help='Maximum analysis depth (default: 10)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--no-png',
        action='store_true',
        help='Skip automatic PNG generation from Mermaid files'
    )
    
    parser.add_argument(
        '--strategy',
        choices=['quick', 'standard', 'deep'],
        default='standard',
        help='Analysis strategy: quick (fast overview), standard (balanced), deep (complete)'
    )
    
    parser.add_argument(
        '--streaming',
        action='store_true',
        help='Use streaming analysis with progress reporting'
    )
    
    parser.add_argument(
        '--incremental',
        action='store_true',
        help='Only analyze changed files (requires previous run)'
    )
    
    parser.add_argument(
        '--max-memory',
        type=int,
        default=1000,
        help='Max memory in MB (default: 1000)'
    )
    
    parser.add_argument(
        '--split-output',
        action='store_true',
        help='Split YAML output into multiple files (summary, functions, classes, modules, entry_points)'
    )
    
    parser.add_argument(
        '--separate-orphans',
        action='store_true',
        help='Separate consolidated project from orphaned/isolated functions into different folders'
    )
    
    parser.add_argument(
        '--data-flow',
        action='store_true',
        help='Export data flow analysis (pipelines, state patterns, dependencies, events)'
    )
    
    parser.add_argument(
        '--data-structures',
        action='store_true',
        help='Export data structure analysis (types, flows, optimization opportunities)'
    )
    
    parser.add_argument(
        '--refactor',
        action='store_true',
        help='Enable AI-driven refactoring analysis and prompt generation'
    )
    
    parser.add_argument(
        '--smell',
        help='Filter refactoring by specific code smell (e.g., god_function, feature_envy)'
    )
    
    parser.add_argument(
        '--llm-format',
        choices=['claude', 'gpt', 'markdown'],
        default='markdown',
        help='Format for refactoring prompts (default: markdown)'
    )
    
    parser.add_argument(
        '--readme',
        action='store_true',
        default=True,
        help='Generate README.md with documentation of all output files (default: enabled)'
    )
    
    parser.add_argument(
        '--chunk',
        action='store_true',
        help='Automatically split large repositories into smaller subprojects'
    )
    
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=256,
        help='Maximum output size per chunk in KB (default: 256)'
    )
    
    parser.add_argument(
        '--max-files-per-chunk',
        type=int,
        default=50,
        help='Maximum files per chunk for large repos (default: 50)'
    )
    
    parser.add_argument(
        '--auto-chunk-threshold',
        type=int,
        default=100,
        help='File count threshold to auto-enable chunking (default: 100)'
    )
    
    parser.add_argument(
        '--skip-subprojects',
        nargs='+',
        default=[],
        help='Skip specific subprojects (e.g., --skip-subprojects tests examples)'
    )
    
    parser.add_argument(
        '--only-subproject',
        help='Analyze only specific subproject (e.g., --only-subproject src)'
    )
    
    return parser


def _handle_special_commands() -> Optional[int]:
    """Handle special sub-commands (llm-flow, llm-context)."""
    if len(sys.argv) > 1 and sys.argv[1] == 'llm-flow':
        from .generators.llm_flow import main as llm_flow_main
        return llm_flow_main(sys.argv[2:])
    if len(sys.argv) > 1 and sys.argv[1] == 'llm-context':
        return generate_llm_context(sys.argv[2:])
    return None


def _validate_and_setup(args) -> tuple[Path, Path]:
    """Validate source path and setup output directory."""
    if not args.source:
        print("Error: missing required argument: source", file=sys.stderr)
        print("Usage: code2llm <source> [options]", file=sys.stderr)
        print("   or: code2llm llm-flow [options]", file=sys.stderr)
        sys.exit(2)

    source_path = Path(args.source)
    if not source_path.exists():
        print(f"Error: Source path not found: {source_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    return source_path, output_dir


def _print_start_info(args, source_path: Path, output_dir: Path) -> None:
    """Print analysis start information if verbose."""
    if args.verbose:
        print(f"Analyzing: {source_path}")
        print(f"Mode: {args.mode}")
        print(f"Output: {output_dir}")


def main():
    """Main CLI entry point."""
    # Handle special sub-commands first
    special_result = _handle_special_commands()
    if special_result is not None:
        return special_result

    # Parse arguments
    parser = create_parser()
    args = parser.parse_args()

    source_path, output_dir = _validate_and_setup(args)
    _print_start_info(args, source_path, output_dir)

    # Analyze → Export
    result = _run_analysis(args, source_path, output_dir)
    _run_exports(args, result, output_dir, source_path=source_path)

    if args.verbose:
        print(f"\nAll outputs saved to: {output_dir}")

    return 0


def _run_analysis(args, source_path: Path, output_dir: Path):
    """Run code analysis with configured strategy.

    Returns AnalysisResult or exits on error.
    For large repos, may analyze in chunks and merge results.
    """
    from .core.large_repo import (
        HierarchicalRepoSplitter, should_use_chunking, get_analysis_plan
    )
    
    # Check if we should use chunked analysis
    # Auto-chunk when estimated output > chunk_size (default 256KB = ~85 files)
    use_chunking = (
        args.chunk or 
        should_use_chunking(source_path, args.chunk_size)
    )
    
    if use_chunking:
        if args.verbose:
            print(f"Large repository detected - using chunked analysis")
        # Set chunk flag so export knows to use chunked mode
        args.chunk = True
        return _run_chunked_analysis(args, source_path, output_dir)
    
    # Standard single-analysis flow
    config = Config(
        mode=args.mode,
        max_depth_enumeration=args.max_depth,
        detect_state_machines=not args.no_patterns,
        detect_recursion=not args.no_patterns,
        output_dir=str(output_dir)
    )

    try:
        if args.streaming or args.strategy in ['quick', 'deep']:
            result = _run_streaming_analysis(args, config, source_path)
        else:
            analyzer = ProjectAnalyzer(config)
            result = analyzer.analyze_project(str(source_path))

        if args.verbose:
            print(f"\nAnalysis complete:")
            print(f"  - Functions: {len(result.functions)}")
            print(f"  - Classes: {len(result.classes)}")
            print(f"  - CFG nodes: {len(result.nodes)}")
            print(f"  - CFG edges: {len(result.edges)}")

        return result

    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        sys.exit(1)


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
    
    # Get hierarchical analysis plan
    subprojects = splitter.get_analysis_plan(source_path)
    
    if args.verbose:
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
    
    # Filter subprojects if requested
    if args.only_subproject:
        subprojects = [sp for sp in subprojects if sp.name == args.only_subproject or sp.name.startswith(args.only_subproject + '.')]
        if not subprojects:
            print(f"Error: Subproject '{args.only_subproject}' not found", file=sys.stderr)
            sys.exit(1)
    
    if args.skip_subprojects:
        subprojects = [sp for sp in subprojects if not any(sp.name.startswith(skip) for skip in args.skip_subprojects)]
    
    # Analyze each subproject
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
    
    # Create merged summary
    merged_result = _merge_chunked_results(all_results, source_path)
    
    if args.verbose:
        print(f"\nChunked analysis complete:")
        print(f"  - Chunks analyzed: {len(all_results)}")
        print(f"  - Total functions: {len(merged_result.functions)}")
        print(f"  - Total classes: {len(merged_result.classes)}")
    
    return merged_result


def _analyze_subproject(args, subproject, output_dir: Path):
    """Analyze and export a single subproject."""
    from .core.analyzer import ProjectAnalyzer
    from .core.config import Config
    from .cli_exports import _export_simple_formats, _export_evolution, _export_chunked_prompt_txt, _export_code2logic
    
    config = Config(
        mode=args.mode,
        max_depth_enumeration=args.max_depth,
        detect_state_machines=not args.no_patterns,
        detect_recursion=not args.no_patterns,
        output_dir=str(output_dir),
        verbose=args.verbose
    )
    
    analyzer = ProjectAnalyzer(config)
    
    try:
        # Analyze subproject
        result = analyzer.analyze_project(str(subproject.path))
        
        # Export results for this subproject
        formats = [f.strip() for f in args.format.split(',')]
        if 'all' in formats:
            formats = ['toon', 'context', 'evolution', 'code2logic']
        
        # Export simple formats (toon, context)
        _export_simple_formats(args, result, output_dir, formats)
        
        # Export evolution
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
        
        # Prefix with subproject name to avoid collisions
        prefix = f"{name}."
        
        # Merge functions
        for func_name, func_info in result.functions.items():
            new_name = f"{prefix}{func_name}" if '.' not in func_name else func_name
            merged.functions[new_name] = func_info
        
        # Merge classes
        for class_name, class_info in result.classes.items():
            new_name = f"{prefix}{class_name}" if '.' not in class_name else class_name
            merged.classes[new_name] = class_info
        
        # Merge modules
        for mod_name, mod_info in result.modules.items():
            new_name = f"{prefix}{mod_name}" if '.' not in mod_name else mod_name
            merged.modules[new_name] = mod_info
        
        # Merge nodes and edges (simplified - just count)
        merged.nodes.update(result.nodes)
        merged.edges.extend(result.edges)
    
    return merged


def _run_streaming_analysis(args, config, source_path: Path):
    """Run streaming analysis with progress reporting."""
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

    # Adjust strategy for memory limit
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


if __name__ == '__main__':
    sys.exit(main())
