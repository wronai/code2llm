"""Base Exporter class for code2llm."""

from abc import ABC, abstractmethod
from code2llm.core.models import AnalysisResult


class Exporter(ABC):
    """Abstract base class for all exporters."""
    
    @abstractmethod
    def export(self, result: AnalysisResult, output_path: str, **kwargs) -> None:
        """Export analysis result to the specified path."""
        pass
