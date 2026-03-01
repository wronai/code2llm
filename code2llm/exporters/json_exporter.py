"""JSON Exporter for code2llm."""

import json
from pathlib import Path
from .base import Exporter
from ..core.models import AnalysisResult


class JSONExporter(Exporter):
    """Export to JSON format."""
    
    def export(self, result: AnalysisResult, output_path: str, compact: bool = True, include_defaults: bool = False) -> None:
        """Export to JSON file."""
        data = result.to_dict(compact=compact and not include_defaults)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2 if not compact else None, ensure_ascii=False)
