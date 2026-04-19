"""JSON Exporter for code2llm."""

import json
from pathlib import Path
from typing import Optional
from .base import BaseExporter, export_format
from code2llm.core.models import AnalysisResult


@export_format("json", description="JSON format", extension=".json")
class JSONExporter(BaseExporter):
    """Export to JSON format."""

    def export(
        self,
        result: AnalysisResult,
        output_path: str,
        compact: bool = True,
        include_defaults: bool = False,
        **kwargs
    ) -> Optional[Path]:
        """Export to JSON file."""
        data = result.to_dict(compact=compact and not include_defaults)
        path = self._ensure_dir(output_path)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2 if not compact else None, ensure_ascii=False)
        return path
