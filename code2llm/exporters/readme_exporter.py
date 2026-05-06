"""README Exporter for code2llm — backward compatibility shim.

Generates comprehensive README.md documentation for analysis output files.

Implementation has been split into:
  - readme/insights.py - Health metrics extraction
  - readme/files.py - File existence checking
  - readme/sections.py - Dynamic table builders
  - readme/content.py - Main README template
"""

from pathlib import Path
from typing import Any, Optional

from .base import BaseExporter, export_format
from .readme import (
    extract_insights,
    get_existing_files,
    build_core_files_section,
    build_llm_files_section,
    build_viz_files_section,
    generate_readme_content,
)


@export_format("readme", description="README documentation format", extension=".md")
class READMEExporter(BaseExporter):
    """Export README.md with documentation of all generated files."""
    
    def export(self, analysis_result: Any, output_path: str, **kwargs) -> Optional[Path]:
        """Generate README.md documentation."""
        output_dir = Path(output_path).parent
        project_path = analysis_result.project_path if hasattr(analysis_result, 'project_path') else './'

        # Collect statistics
        total_functions = len(analysis_result.functions) if hasattr(analysis_result, 'functions') else 0
        total_classes = len(analysis_result.classes) if hasattr(analysis_result, 'classes') else 0
        total_modules = len(analysis_result.modules) if hasattr(analysis_result, 'modules') else 0

        # Read existing files to extract insights
        insights = extract_insights(output_dir)

        # Check which files actually exist
        existing_files = get_existing_files(output_dir)

        # Build dynamic file sections
        core_files_section = build_core_files_section(existing_files, insights)
        llm_files_section = build_llm_files_section(existing_files)
        viz_files_section = build_viz_files_section(existing_files)

        readme_content = generate_readme_content(
            project_path=project_path,
            output_dir=output_dir,
            total_functions=total_functions,
            total_classes=total_classes,
            total_modules=total_modules,
            insights=insights,
            core_files_section=core_files_section,
            llm_files_section=llm_files_section,
            viz_files_section=viz_files_section,
        )

        path = self._ensure_dir(output_path)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        return path
