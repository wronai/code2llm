"""CLI argument parser for code2llm."""

import argparse

from .core.config import ANALYSIS_MODES


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog='code2llm',
        description='Analyze Python code control flow, data flow, and call graphs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  code2llm ./                                       # Default: TOON diagnostics + README
  code2llm ./ -f all -o ./docs                      # All core formats to ./docs/
  code2llm ./ -f toon,map,evolution                 # Consolidated diagnostics + structure + roadmap
  code2llm ./ -f context                            # LLM narrative (context.md)
  code2llm ./ --streaming --strategy deep -f all    # Deep streaming analysis, all core outputs
  code2llm ./ --strategy quick -f toon              # Fast overview
  code2llm ./ --refactor                            # AI refactoring prompts
  code2llm ./ --refactor --smell god_function       # Filter by smell type
  code2llm ./ -f yaml --split-output                # Split YAML into multiple files
  code2llm ./ -f yaml --separate-orphans            # Separate orphaned functions
  code2llm ./ -f mermaid --no-png                   # Mermaid diagrams without PNG
  code2llm ./ -m static -v -o ./analysis            # Static mode, verbose
  code2llm ./ --no-readme                           # Disable README generation
  code2llm ./ -f project-yaml                       # Legacy project.yaml export (opt-in)
  code2llm report --format toon                     # Generate analysis_view.toon from existing project.yaml
  code2llm report --format all                      # All legacy views from existing project.yaml
  code2llm llm-flow                                 # Generate LLM flow summary
  code2llm llm-context ./                           # Generate LLM context only

Format Options (-f):
  toon         — Health diagnostics (analysis.toon) [default]
  map          — Structural map (map.toon.yaml) — modules, imports, exports, signatures, project header
  evolution    — Refactoring queue (evolution.toon.yaml)
  context      — LLM narrative (context.md) — architecture summary
  yaml         — Standard YAML format (legacy / explicit opt-in)
  json         — Machine-readable JSON (legacy / explicit opt-in)
  mermaid      — Flowchart diagrams (flow.mmd, calls.mmd, compact_flow.mmd)
  flow         — Data-flow analysis (flow.toon) — legacy, explicit opt-in
  code2logic   — Generate project logic (legacy project.toon) via external code2logic
  project-yaml — Legacy project.yaml export (single source of truth) + generated views
  all          — Generate core formats (analysis.toon, map.toon.yaml, evolution.toon.yaml, context, mermaid)

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
        help='Output formats: toon,map,flow,context,code2logic,yaml,json,mermaid,evolution,png,project-yaml,all (default: toon)'
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
        '--no-chunk',
        action='store_true',
        help='Disable chunked analysis even for large repositories'
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
    
    parser.add_argument(
        '--exclude',
        nargs='+',
        default=[],
        help='Exclude specific directories or patterns (e.g., --exclude vendor build test)'
    )
    
    parser.add_argument(
        '--no-gitignore',
        action='store_true',
        help='Disable .gitignore support (include all files)'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate generated chunked output - check all chunks have required files'
    )

    # Flow diagram options (Plan R1)
    parser.add_argument(
        '--flow-detail',
        action='store_true',
        help='Export detailed flow diagram (flow_detailed.mmd) with per-module view (~150 nodes)'
    )

    parser.add_argument(
        '--flow-full',
        action='store_true',
        help='Export full flow diagram (flow_full.mmd) with all nodes (debug view)'
    )

    parser.add_argument(
        '--flow-include-examples',
        action='store_true',
        help='Include examples/, benchmarks/, demo_langs/, tests/ in flow diagrams'
    )

    # Toon YAML export option
    parser.add_argument(
        '--toon-yaml',
        action='store_true',
        help='Export TOON format as YAML (analysis.toon.yaml) instead of plain text'
    )

    return parser
