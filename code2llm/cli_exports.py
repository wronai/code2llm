"""Export functions for CLI - extracted from cli.py to reduce module complexity."""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from .exporters import (
    YAMLExporter, JSONExporter, MermaidExporter,
    ContextExporter, ToonExporter, MapExporter, FlowExporter,
    EvolutionExporter, READMEExporter,
)


def _export_evolution(args, result, output_dir: Path):
    """Export evolution.toon format."""
    if 'evolution' not in [f.strip() for f in args.format.split(',')] and 'all' not in [f.strip() for f in args.format.split(',')]:
        return
    exporter = EvolutionExporter()
    filepath = output_dir / 'evolution.toon'
    exporter.export(result, str(filepath))
    if args.verbose:
        print(f"  - EVOLUTION (refactoring queue): {filepath}")


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
    exporter.export(result, str(filepath))
    if args.verbose:
        print(f"  - CONTEXT (LLM narrative): {filepath}")


def _export_readme(args, result, output_dir: Path):
    """Export README.md documentation."""
    if not args.readme or args.no_readme:
        return
    exporter = READMEExporter()
    filepath = output_dir / 'README.md'
    exporter.export(result, str(filepath))
    if args.verbose:
        print(f"  - README (documentation): {filepath}")


def _export_code2logic(args, source_path: Path, output_dir: Path, formats: list[str]) -> None:
    """Generate project.toon using external code2logic tool."""
    if not _should_run_code2logic(formats):
        return

    _check_code2logic_installed()
    cmd = _build_code2logic_cmd(args, source_path, output_dir)
    res = _run_code2logic(cmd, args.verbose)
    
    if res.returncode != 0:
        _handle_code2logic_error(res, cmd)

    found = _find_code2logic_output(output_dir, res)
    target = output_dir / 'project.toon'
    final_files = _normalize_code2logic_output(found, target, args)

    if args.verbose:
        if len(final_files) == 1:
            print(f"  - CODE2LOGIC (project logic): {final_files[0]}")
        else:
            print(f"  - CODE2LOGIC (project logic): {len(final_files)} parts")
            for f in final_files:
                size_kb = os.path.getsize(f) / 1024
                print(f"    → {f.name}: {size_kb:.1f}KB")


def _should_run_code2logic(formats: list[str]) -> bool:
    """Check if code2logic format is requested."""
    return 'code2logic' in formats or 'all' in formats


def _check_code2logic_installed() -> None:
    """Verify code2logic is available in PATH."""
    if shutil.which('code2logic') is None:
        print("Error: requested format 'code2logic' but 'code2logic' executable was not found in PATH.", file=sys.stderr)
        print("Install it with: pip install code2logic --upgrade", file=sys.stderr)
        sys.exit(1)


def _build_code2logic_cmd(args, source_path: Path, output_dir: Path) -> list[str]:
    """Build command for code2logic execution."""
    cmd = [
        'code2logic', str(source_path),
        '-f', 'toon',
        '--compact',
        '--name', 'project',
        '-o', str(output_dir),
    ]
    if not args.verbose:
        cmd.append('-q')
    return cmd


def _run_code2logic(cmd: list[str], verbose: bool):
    """Execute code2logic command."""
    try:
        if verbose:
            return subprocess.run(cmd, capture_output=True, text=True)
        else:
            return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
    except Exception as e:
        print(f"Error running code2logic: {e}", file=sys.stderr)
        sys.exit(1)


def _handle_code2logic_error(res, cmd: list[str]) -> None:
    """Handle code2logic execution error."""
    # Re-run with output capture if not verbose
    if not res.stdout and not res.stderr:
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
        except Exception as e:
            print(f"Error running code2logic: {e}", file=sys.stderr)
            sys.exit(1)
    
    if res.stdout:
        print(res.stdout, file=sys.stderr)
    if res.stderr:
        print(res.stderr, file=sys.stderr)
    print(f"Error: code2logic failed (exit code {res.returncode}).", file=sys.stderr)
    sys.exit(res.returncode)


def _find_code2logic_output(output_dir: Path, res) -> Path:
    """Find code2logic output file in possible locations."""
    candidate_paths = [
        output_dir / 'project.toon',
        output_dir / 'project' / 'project.toon',
        output_dir / 'project.toon.txt',
    ]
    found = next((p for p in candidate_paths if p.exists()), None)
    
    if found is None:
        # Show output for debugging
        if res.stdout:
            print(res.stdout, file=sys.stderr)
        if res.stderr:
            print(res.stderr, file=sys.stderr)
        print("Error: code2logic completed but project.toon was not found in the output directory.", file=sys.stderr)
        sys.exit(1)
    
    return found


def _normalize_code2logic_output(found: Path, target: Path, args) -> List[Path]:
    """Normalize output location to target path and check size limits."""
    if found != target:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(found, target)
        found = target
    
    # Check and split if exceeds 256KB limit
    from .core.toon_size_manager import manage_toon_size
    return manage_toon_size(
        found,
        target.parent,
        max_kb=256,
        prefix="project",
        verbose=getattr(args, 'verbose', False)
    )


def _export_prompt_txt(args, output_dir: Path, formats: list[str], source_path: Optional[Path] = None) -> None:
    """Generate prompt.txt useful to send to an LLM."""
    # Keep it conservative: generate when code2logic is requested.
    if 'code2logic' not in formats and 'all' not in formats:
        return

    prompt_path = output_dir / 'prompt.txt'
    
    # Determine project name and relative output path for display
    if source_path:
        project_path = source_path.name if source_path.name else str(source_path)
        try:
            output_rel_path = str(output_dir.relative_to(source_path))
        except ValueError:
            output_rel_path = str(output_dir)
    else:
        cwd = Path.cwd()
        project_path = cwd.name
        try:
            output_rel_path = str(output_dir.relative_to(cwd))
        except ValueError:
            output_rel_path = str(output_dir)

    files = [
        ('analysis.toon', 'Health diagnostics - complexity metrics, god modules, coupling issues, refactoring priorities'),
        ('context.md', 'LLM narrative - architecture summary, key entry points, process flows, public API surface'),
        ('evolution.toon', 'Refactoring queue - ranked actions by impact/effort, risks, metrics targets, history'),
        ('project.toon', 'Project logic - compact module view from code2logic, file sizes, dependencies overview'),
        ('README.md', 'Documentation - complete guide to all generated files, usage examples, interpretation'),
    ]
    
    existing = [(name, desc) for name, desc in files if (output_dir / name).exists()]
    missing = [name for name, desc in files if (output_dir / name).exists() is False]

    lines: list[str] = []
    lines.append("You are an AI assistant helping me understand and improve a codebase.")
    lines.append("Use the attached/generated files as the authoritative context.")
    lines.append("")
    lines.append(f"we are in project path: {project_path}")
    lines.append("")
    lines.append("Files for analysis:")
    
    for name, desc in existing:
        file_path = f"{output_rel_path}/{name}"
        lines.append(f"- {file_path}  ({desc})")
    
    if missing:
        lines.append("")
        lines.append("Missing files (not generated in this run):")
        for name in missing:
            file_path = f"{output_rel_path}/{name}"
            lines.append(f"- {file_path}")
    
    lines.append("")
    lines.append("Task:")
    lines.append("- Summarize the architecture and main flows.")
    lines.append("- Identify the highest-risk areas and propose a refactoring plan.")
    lines.append("- If you suggest changes, keep behavior backward compatible and provide concrete steps.")
    lines.append("")
    lines.append("Constraints:")
    lines.append("- Prefer minimal, incremental changes.")
    lines.append("- If uncertain, ask clarifying questions.")

    prompt_path.write_text("\n".join(lines) + "\n", encoding='utf-8')
    if args.verbose:
        print(f"  - PROMPT: {prompt_path}")


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


def _run_exports(args, result, output_dir: Path, source_path: Optional[Path] = None):
    """Export analysis results in requested formats.
    
    For chunked analysis, exports to subproject subdirectories.
    """
    formats = [f.strip() for f in args.format.split(',')]
    if 'all' in formats:
        formats = ['toon', 'map', 'flow', 'context', 'code2logic', 'yaml', 'json', 'mermaid', 'evolution']

    # Check if this is a chunked analysis (has subproject subdirs)
    is_chunked = args.chunk if hasattr(args, 'chunk') else False
    
    try:
        if is_chunked and source_path:
            # For chunked analysis, export each subproject separately
            _export_chunked_results(args, result, output_dir, source_path, formats)
        else:
            # Standard single export
            _export_single_project(args, result, output_dir, formats, source_path)

    except Exception as e:
        print(f"Error during export: {e}", file=sys.stderr)
        sys.exit(1)


def _export_single_project(args, result, output_dir: Path, formats: list, source_path: Optional[Path] = None):
    """Export single project results."""
    _export_simple_formats(args, result, output_dir, formats)
    
    if 'mermaid' in formats:
        _export_mermaid(args, result, output_dir)
    
    _export_evolution(args, result, output_dir)
    _export_data_structures(args, result, output_dir)
    _export_context_fallback(args, result, output_dir, formats)

    if source_path is not None:
        _export_code2logic(args, source_path, output_dir, formats)
        _export_prompt_txt(args, output_dir, formats, source_path)
    
    if hasattr(args, 'refactor') and args.refactor:
        _export_refactor_prompts(args, result, output_dir)
    
    _export_readme(args, result, output_dir)


def _export_chunked_results(args, result, output_dir: Path, source_path: Path, formats: list):
    """Export chunked analysis results to subproject directories."""
    from .core.large_repo import HierarchicalRepoSplitter
    
    splitter = HierarchicalRepoSplitter(size_limit_kb=args.chunk_size)
    subprojects = splitter.get_analysis_plan(source_path)
    
    # Filter subprojects same as in analysis
    if hasattr(args, 'only_subproject') and args.only_subproject:
        subprojects = [sp for sp in subprojects if sp.name == args.only_subproject or sp.name.startswith(args.only_subproject + '.')]
    
    if hasattr(args, 'skip_subprojects') and args.skip_subprojects:
        subprojects = [sp for sp in subprojects if not any(sp.name.startswith(skip) for skip in args.skip_subprojects)]
    
    # Export each subproject to its own directory
    for sp in subprojects:
        sp_output_dir = output_dir / sp.name.replace('.', '_')
        if not sp_output_dir.exists():
            continue
        
        # Check for subproject result files
        for ext in ['.toon', '.yaml', '.json']:
            result_file = sp_output_dir / f'analysis{ext}'
            if result_file.exists():
                if args.verbose:
                    level_name = {0: 'root', 1: 'L1', 2: 'L2'}.get(sp.level, f'L{sp.level}')
                    print(f"  - Exported [{level_name}] {sp.name}")
                break
    
    # Also create merged summary in root output dir
    _export_simple_formats(args, result, output_dir, ['toon', 'context'])
    _export_evolution(args, result, output_dir)
    
    if source_path is not None:
        _export_code2logic(args, source_path, output_dir, formats)
        _export_prompt_txt(args, output_dir, formats, source_path)
    
    _export_readme(args, result, output_dir)
