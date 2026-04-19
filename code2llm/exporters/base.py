"""Base Exporter class for code2llm.

Provides:
  - BaseExporter ABC with standardized export interface
  - EXPORT_REGISTRY for format registration
  - @export_format decorator for auto-registration
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Type, ClassVar
from code2llm.core.models import AnalysisResult


class BaseExporter(ABC):
    """Abstract base class for all code2llm exporters.

    All exporters must inherit from this class and implement:
      - export() method for AnalysisResult-based export
      - format_name class attribute for registry identification

    Example:
        @export_format("json")
        class JSONExporter(BaseExporter):
            format_name = "json"
            description = "Export to JSON format"

            def export(self, result, output_path, **kwargs):
                # implementation
                pass
    """

    format_name: ClassVar[str] = ""
    description: ClassVar[str] = ""
    file_extension: ClassVar[str] = ""
    supports_project_yaml: ClassVar[bool] = False  # True if can work from project.yaml data

    @abstractmethod
    def export(
        self,
        result: AnalysisResult,
        output_path: str,
        **kwargs: Any
    ) -> Optional[Path]:
        """Export analysis result to the specified path.

        Args:
            result: The AnalysisResult to export
            output_path: Target file path for the export
            **kwargs: Additional exporter-specific options

        Returns:
            Path to the exported file, or None if export failed
        """
        pass

    def generate(
        self,
        data: Dict[str, Any],
        output_path: str,
        **kwargs: Any
    ) -> Optional[Path]:
        """Generate output from project.yaml data (optional).

        Override this if the exporter can work from project.yaml data
        instead of a full AnalysisResult. Set supports_project_yaml=True.

        Args:
            data: Dict loaded from project.yaml
            output_path: Target file path for the export
            **kwargs: Additional exporter-specific options

        Returns:
            Path to the generated file, or None if generation failed
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support project.yaml generation"
        )

    def _ensure_dir(self, output_path: str) -> Path:
        """Ensure parent directory exists for output path."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def _write_text(self, output_path: str, content: str) -> Path:
        """Write text content to file, ensuring directory exists."""
        path = self._ensure_dir(output_path)
        path.write_text(content, encoding="utf-8")
        return path


# Backward compatibility alias
Exporter = BaseExporter


# Export registry: format_name -> exporter_class
EXPORT_REGISTRY: Dict[str, Type[BaseExporter]] = {}


def export_format(
    name: str,
    description: str = "",
    extension: str = "",
    supports_project_yaml: bool = False
):
    """Decorator to register an exporter with the EXPORT_REGISTRY.

    Args:
        name: Format identifier (e.g., "json", "yaml", "toon")
        description: Human-readable description of the format
        extension: Default file extension for this format
        supports_project_yaml: Whether this exporter can generate from project.yaml data

    Example:
        @export_format("json", description="JSON format", extension=".json")
        class JSONExporter(BaseExporter):
            def export(self, result, output_path, **kwargs):
                # implementation
                pass
    """
    def decorator(cls: Type[BaseExporter]) -> Type[BaseExporter]:
        cls.format_name = name
        cls.description = description or f"{name} format"
        cls.file_extension = extension
        cls.supports_project_yaml = supports_project_yaml
        EXPORT_REGISTRY[name] = cls
        return cls
    return decorator


def get_exporter(name: str) -> Optional[Type[BaseExporter]]:
    """Get exporter class by format name.

    Args:
        name: Format identifier from registry

    Returns:
        Exporter class or None if not found
    """
    return EXPORT_REGISTRY.get(name)


def list_exporters() -> Dict[str, Dict[str, Any]]:
    """List all registered exporters with metadata.

    Returns:
        Dict mapping format_name to exporter metadata
    """
    return {
        name: {
            "class": cls.__name__,
            "description": cls.description,
            "extension": cls.file_extension,
            "supports_project_yaml": cls.supports_project_yaml,
        }
        for name, cls in EXPORT_REGISTRY.items()
    }
