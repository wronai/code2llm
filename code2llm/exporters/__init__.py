"""Exporters package for code2llm.

Available exporters:
  - ToonExporter      → analysis.toon       (health diagnostics)
  - MapExporter       → map.toon.yaml       (structural map + project header)
  - FlowExporter      → flow.toon           (data-flow: pipelines, contracts, types)
  - EvolutionExporter → evolution.toon.yaml (ranked refactoring queue)
  - ContextExporter   → context.md          (LLM narrative)
  - READMEExporter    → README.md           (documentation of all files)
  - YAMLExporter      → analysis.yaml
  - JSONExporter      → analysis.json
  - MermaidExporter   → *.mmd

Registry API:
  - BaseExporter          → Abstract base class for all exporters
  - export_format         → Decorator for auto-registration
  - EXPORT_REGISTRY       → Dict mapping format names to exporter classes
  - get_exporter(name)    → Get exporter by format name
  - list_exporters()      → List all registered exporters

Backward-compat alias: LLMPromptExporter = ContextExporter, Exporter = BaseExporter
"""

# Base classes and registry (must be first for dependency order)
from .base import (
    BaseExporter,
    Exporter,  # backward compat alias
    export_format,
    EXPORT_REGISTRY,
    get_exporter,
    list_exporters,
)

# Standard exporters (auto-registered via @export_format decorator)
from .json_exporter import JSONExporter
from .yaml_exporter import YAMLExporter
from .mermaid_exporter import MermaidExporter
from .context_exporter import ContextExporter
from .llm_exporter import LLMPromptExporter  # backward compat
from .toon import ToonExporter
from .map_exporter import MapExporter
from .flow_exporter import FlowExporter
from .evolution_exporter import EvolutionExporter
from .readme_exporter import READMEExporter
from .project_yaml_exporter import ProjectYAMLExporter

# View generators (work from project.yaml data)
from .report_generators import (
    ToonViewGenerator, ContextViewGenerator,
    ArticleViewGenerator, HTMLDashboardGenerator,
    load_project_yaml,
)
from .index_generator import IndexHTMLGenerator

__all__ = [
    # Base classes and registry
    'BaseExporter',
    'Exporter',
    'export_format',
    'EXPORT_REGISTRY',
    'get_exporter',
    'list_exporters',
    # Standard exporters
    'JSONExporter',
    'YAMLExporter',
    'MermaidExporter',
    'ContextExporter',
    'LLMPromptExporter',
    'ToonExporter',
    'MapExporter',
    'FlowExporter',
    'EvolutionExporter',
    'READMEExporter',
    'ProjectYAMLExporter',
    # View generators
    'ToonViewGenerator',
    'ContextViewGenerator',
    'ArticleViewGenerator',
    'HTMLDashboardGenerator',
    'IndexHTMLGenerator',
    'load_project_yaml',
]