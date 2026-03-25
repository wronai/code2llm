"""Prompt generation — prompt.txt for LLM consumption (regular and chunked)."""

import sys
from pathlib import Path
from typing import List, Optional, Tuple


def _export_prompt_txt(args, output_dir: Path, formats: list[str], source_path: Optional[Path] = None) -> None:
    """Generate prompt.txt useful to send to an LLM."""
    if 'code2logic' not in formats and 'all' not in formats:
        return

    project_path, output_rel_path = _get_prompt_paths(source_path, output_dir)
    lines = _build_prompt_header(project_path)
    lines.extend(_build_main_files_section(output_dir, output_rel_path))

    missing = _get_missing_files(output_dir)
    if missing:
        lines.append("")
        lines.append("Missing files (not generated in this run):")
        for name in missing:
            lines.append(f"- {output_rel_path}/{name}")

    # Analyze generated files and build dynamic footer
    file_analysis = _analyze_generated_files(output_dir)
    lines.extend(_build_prompt_footer(chunked=False, file_analysis=file_analysis))

    prompt_path = output_dir / 'prompt.txt'
    prompt_path.write_text("\n".join(lines) + "\n", encoding='utf-8')
    if args.verbose:
        print(f"  - PROMPT: {prompt_path}")


def _export_chunked_prompt_txt(args, output_dir: Path, formats: list[str], source_path: Optional[Path] = None, subprojects: list = None) -> None:
    """Generate prompt.txt for chunked analysis with all subproject files."""
    if 'code2logic' not in formats and 'all' not in formats:
        return

    project_path, output_rel_path = _get_prompt_paths(source_path, output_dir)
    lines = _build_prompt_header(project_path)
    lines.extend(_build_main_files_section(output_dir, output_rel_path))

    if subprojects:
        lines.extend(_build_subprojects_section(subprojects, output_dir, output_rel_path))

    lines.extend(_build_missing_files_section(output_dir, output_rel_path))
    
    # Analyze generated files and build dynamic footer
    file_analysis = _analyze_generated_files(output_dir, subprojects=subprojects)
    lines.extend(_build_prompt_footer(chunked=True, file_analysis=file_analysis))

    prompt_path = output_dir / 'prompt.txt'
    prompt_path.write_text("\n".join(lines) + "\n", encoding='utf-8')
    if args.verbose:
        print(f"  - PROMPT (chunked): {prompt_path}")


# ------------------------------------------------------------------
# helpers
# ------------------------------------------------------------------
def _get_prompt_paths(source_path: Optional[Path], output_dir: Path) -> Tuple[str, str]:
    """Determine project name and relative output path."""
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
    return project_path, output_rel_path


_MAIN_FILES = [
    ('analysis.toon', 'Health diagnostics - complexity metrics, god modules, coupling issues, refactoring priorities'),
    ('map.toon', 'Structural map - files, sizes, imports, exports, signatures, project header'),
    ('context.md', 'LLM narrative - architecture summary, key entry points, process flows, public API surface'),
    ('evolution.toon', 'Refactoring queue - ranked actions by impact/effort, risks, metrics targets, history'),
    ('README.md', 'Documentation - complete guide to all generated files, usage examples, interpretation'),
]


def _build_prompt_header(project_path: str) -> List[str]:
    """Build header section of prompt."""
    return [
        "You are an AI assistant helping me understand and improve a codebase.",
        "Use the attached/generated files as the authoritative context.",
        "",
        f"we are in project path: {project_path}",
        "",
        "Files for analysis:",
    ]


def _build_main_files_section(output_dir: Path, output_rel_path: str) -> List[str]:
    """Build main files section with size metrics."""
    lines = []
    for name, desc in _MAIN_FILES:
        file_path = output_dir / name
        if file_path.exists():
            size_bytes = file_path.stat().st_size
            size_str = _format_size(size_bytes)
            lines.append(f"- {output_rel_path}/{name}  ({desc}) [{size_str}]")
    return lines


def _format_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes // 1024}KB"
    else:
        return f"{size_bytes // (1024 * 1024)}MB"


def _get_missing_files(output_dir: Path) -> List[str]:
    """Return names of expected main files that are missing."""
    return [name for name, _ in _MAIN_FILES if not (output_dir / name).exists()]


def _build_subprojects_section(subprojects: list, output_dir: Path, output_rel_path: str) -> List[str]:
    """Build subprojects section with detailed file info."""
    lines = [
        "",
        "Subproject Analysis Files (hierarchical chunking for large repository):",
    ]

    for sp in subprojects:
        sp_dir = output_dir / sp.name.replace('.', '_')
        if not sp_dir.exists():
            continue

        level_name = {0: 'root', 1: 'L1', 2: 'L2', 3: 'chunk'}.get(sp.level, f'L{sp.level}')
        sp_files = []
        total_size = 0
        for f in ['analysis.toon', 'context.md', 'evolution.toon']:
            f_path = sp_dir / f
            if f_path.exists():
                size = f_path.stat().st_size
                total_size += size
                sp_files.append(f"{f} [{_format_size(size)}]")

        if sp_files:
            size_str = _format_size(total_size)
            file_list = ', '.join(sp_files)
            lines.append(f"- {output_rel_path}/{sp.name.replace('.', '_')}/  [{level_name}] Total: {size_str} - Contains: {file_list}")

    return lines


def _build_missing_files_section(output_dir: Path, output_rel_path: str) -> List[str]:
    """Build missing files section."""
    missing = _get_missing_files(output_dir)
    if not missing:
        return []
    lines = ["", "Missing files (not generated in this run):"]
    for name in missing:
        lines.append(f"- {output_rel_path}/{name}")
    return lines


def _analyze_generated_files(output_dir: Path, subprojects: list = None) -> dict:
    """Analyze which files were generated and determine appropriate focus areas."""
    analysis = {
        'has_analysis_toon': (output_dir / 'analysis.toon').exists(),
        'has_map_toon': (output_dir / 'map.toon').exists(),
        'has_context_md': (output_dir / 'context.md').exists(),
        'has_evolution_toon': (output_dir / 'evolution.toon').exists(),
        'has_readme': (output_dir / 'README.md').exists(),
        'has_yaml': (output_dir / 'analysis.yaml').exists(),
        'has_json': (output_dir / 'analysis.json').exists(),
        'has_mermaid': (output_dir / 'flow.mmd').exists() or (output_dir / 'calls.mmd').exists(),
        'is_chunked': subprojects is not None and len(subprojects) > 0,
        'file_count': 0,
    }
    
    # Count total files
    for key, exists in analysis.items():
        if key.startswith('has_') and exists:
            analysis['file_count'] += 1
    
    return analysis


def _build_dynamic_focus_areas(file_analysis: dict) -> List[str]:
    """Build focus areas based on generated files."""
    focus_areas = []
    
    if file_analysis['has_analysis_toon']:
        focus_areas.append("1. **Code Health Analysis** - Review complexity metrics, god modules, coupling issues from analysis.toon")

    if file_analysis['has_map_toon']:
        focus_areas.append("2. **Structural Map** - Use map.toon to inspect imports, exports, signatures, and the project header")
    
    if file_analysis['has_evolution_toon']:
        focus_areas.append("3. **Refactoring Priorities** - Examine ranked refactoring actions and risk assessment from evolution.toon")
    
    if file_analysis['has_context_md']:
        focus_areas.append("4. **Architecture Overview** - Understand main flows, entry points, and public API from context.md")
    
    if file_analysis['has_yaml'] or file_analysis['has_json']:
        focus_areas.append("5. **Structured Data** - Use machine-readable formats for automated analysis and metrics extraction")
    
    if file_analysis['has_mermaid']:
        focus_areas.append("6. **Visual Flow** - Review control flow diagrams and call graphs for architectural insights")
    
    if file_analysis['is_chunked']:
        focus_areas.append("7. **Large Repository Patterns** - Identify cross-chunk dependencies and consolidation opportunities")
    
    if not focus_areas:
        focus_areas.append("1. **General Code Review** - Provide overall architecture assessment and improvement recommendations")
    
    return focus_areas


def _build_dynamic_tasks(file_analysis: dict) -> List[str]:
    """Build tasks based on available files."""
    tasks = [
        "- Summarize the architecture, main flows, and structural dependencies.",
        "- Identify the highest-risk areas and propose a refactoring plan.",
        "- If you suggest changes, keep behavior backward compatible and provide concrete steps.",
    ]
    
    if file_analysis['has_analysis_toon']:
        tasks.append("- Highlight critical functions (CC ≥ 10) and top problem areas from analysis.toon.")

    if file_analysis['has_map_toon']:
        tasks.append("- Cross-check imports, exports, and signatures against map.toon before proposing splits.")
    
    if file_analysis['has_evolution_toon']:
        tasks.append("- Prioritize refactoring actions by impact/effort ratio from evolution.toon.")
    
    if file_analysis['has_context_md']:
        tasks.append("- Validate entry points and public API surface match the architecture described.")

    if file_analysis['is_chunked']:
        tasks.append("- Analyze cross-chunk dependencies and suggest consolidation strategies.")
    
    return tasks


def _build_prompt_footer(chunked: bool = False, file_analysis: dict = None) -> List[str]:
    """Build dynamic footer section of prompt based on generated files."""
    if file_analysis is None:
        file_analysis = {}
    
    lines = [""]
    
    # Dynamic tasks
    lines.append("Task:")
    tasks = _build_dynamic_tasks(file_analysis)
    for task in tasks:
        lines.append(task)
    
    # Dynamic focus areas
    focus_areas = _build_dynamic_focus_areas(file_analysis)
    if focus_areas:
        lines.append("")
        lines.append("Focus Areas for Analysis:")
        for area in focus_areas:
            lines.append(area)
    
    # File-specific recommendations
    if file_analysis['file_count'] > 0:
        lines.append("")
        lines.append("Analysis Strategy:")
        if file_analysis['has_analysis_toon'] and file_analysis['has_map_toon']:
            lines.append("- Start with analysis.toon for health metrics, then map.toon for structure and signatures")
            if file_analysis['has_evolution_toon']:
                lines.append("- Finish with evolution.toon for action priorities and next steps")
        elif file_analysis['has_context_md']:
            lines.append("- Use context.md as the primary reference for architectural understanding")
        
        if file_analysis['has_yaml']:
            lines.append("- Reference analysis.yaml for precise metrics and programmatic data")
    
    # Constraints
    lines.append("")
    lines.append("Constraints:")
    lines.append("- Prefer minimal, incremental changes.")
    lines.append("- Maintain full backward compatibility.")
    lines.append("- Base recommendations on concrete metrics from the provided files.")
    lines.append("- If uncertain, ask clarifying questions.")
    
    if chunked:
        lines.extend([
            "",
            "Note: This repository was analyzed using hierarchical chunking due to its size.",
            "      Start with the main files (analysis.toon, context.md) for overview,",
            "      then examine specific subproject directories as needed.",
        ])
    
    return lines
