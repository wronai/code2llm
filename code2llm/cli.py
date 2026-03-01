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
from .exporters import (
    YAMLExporter, JSONExporter, MermaidExporter,
    ContextExporter, LLMPromptExporter,
    ToonExporter, MapExporter, FlowExporter,
    EvolutionExporter, READMEExporter,
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
        help='Output formats: toon,map,flow,context,yaml,json,mermaid,evolution,png,all (default: toon)'
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
        '--no-readme',
        action='store_true',
        help='Disable automatic README.md generation'
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
    _run_exports(args, result, output_dir)

    if args.verbose:
        print(f"\nAll outputs saved to: {output_dir}")

    return 0


def _run_analysis(args, source_path: Path, output_dir: Path):
    """Run code analysis with configured strategy.

    Returns AnalysisResult or exits on error.
    """
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


def _run_exports(args, result, output_dir: Path):
    """Export analysis results in requested formats."""
    formats = [f.strip() for f in args.format.split(',')]

    if 'all' in formats:
        formats = ['toon', 'map', 'flow', 'context', 'yaml', 'json', 'mermaid', 'evolution']

    try:
        # Simple format exports
        _export_simple_formats(args, result, output_dir, formats)

        # Mermaid (complex — 3 files + PNG)
        if 'mermaid' in formats:
            _export_mermaid(args, result, output_dir)

        # Evolution
        if 'evolution' in formats:
            exporter = EvolutionExporter()
            filepath = output_dir / 'evolution.toon'
            exporter.export(result, str(filepath))
            if args.verbose:
                print(f"  - EVOLUTION (refactoring queue): {filepath}")

        # Data structures (optional flag)
        if args.data_structures:
            exporter = YAMLExporter()
            struct_path = output_dir / 'data_structures.yaml'
            exporter.export_data_structures(result, str(struct_path), compact=True)
            if args.verbose:
                print(f"  - Data structures: {struct_path}")

        # Backward compat: always generate context.md
        if 'context' not in formats:
            exporter = ContextExporter()
            filepath = output_dir / 'context.md'
            exporter.export(result, str(filepath))
            if args.verbose:
                print(f"  - CONTEXT (LLM narrative): {filepath}")

        # AI-driven refactoring prompts
        if args.refactor:
            _export_refactor_prompts(args, result, output_dir)

        # README documentation (default enabled)
        if args.readme and not args.no_readme:
            exporter = READMEExporter()
            filepath = output_dir / 'README.md'
            exporter.export(result, str(filepath))
            if args.verbose:
                print(f"  - README (documentation): {filepath}")

    except Exception as e:
        print(f"Error during export: {e}", file=sys.stderr)
        sys.exit(1)


def _export_simple_formats(args, result, output_dir: Path, formats):
    """Export toon, map, flow, context, yaml, json formats."""
    format_map = {
        'toon': ('analysis.toon', ToonExporter, 'TOON (diagnostics)'),
        'map': ('map.toon', MapExporter, 'MAP (structure)'),
        'flow': ('flow.toon', FlowExporter, 'FLOW (data-flow)'),
        'context': ('context.md', ContextExporter, 'CONTEXT (LLM narrative)'),
    }

    for fmt, (filename, exporter_cls, label) in format_map.items():
        if fmt in formats:
            exporter = exporter_cls()
            filepath = output_dir / filename
            exporter.export(result, str(filepath))
            if args.verbose:
                print(f"  - {label}: {filepath}")

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


def _export_mermaid(args, result, output_dir: Path):
    """Export Mermaid diagrams + optional PNG generation."""
    exporter = MermaidExporter()
    exporter.export(result, str(output_dir / 'flow.mmd'))
    exporter.export_call_graph(result, str(output_dir / 'calls.mmd'))
    exporter.export_compact(result, str(output_dir / 'compact_flow.mmd'))
    if args.verbose:
        print(f"  - Mermaid: {output_dir / '*.mmd'}")

    if not args.no_png:
        try:
            from .generators.mermaid import generate_pngs
            png_count = generate_pngs(output_dir, output_dir)
            if args.verbose and png_count > 0:
                print(f"  - PNG: {png_count} files generated")
        except ImportError:
            try:
                import subprocess
                script_path = Path(__file__).parent.parent / 'mermaid_to_png.py'
                if script_path.exists():
                    png_result = subprocess.run([
                        'python', str(script_path),
                        '--batch', str(output_dir), str(output_dir)
                    ], capture_output=True, text=True, timeout=60)
                    if png_result.returncode == 0 and args.verbose:
                        print(f"  - PNG: {output_dir / '*.png'}")
            except Exception:
                if args.verbose:
                    print(f"  - PNG: Skipped (install with: make install-mermaid)")
    elif args.verbose:
        print(f"  - PNG: Skipped (--no-png)")


def _export_refactor_prompts(args, result, output_dir: Path):
    """Generate AI-driven refactoring prompts."""
    from .refactor.prompt_engine import PromptEngine
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
