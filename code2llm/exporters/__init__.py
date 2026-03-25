"""Exporters package for code2llm.

Available exporters:
  - ToonExporter      → analysis.toon  (health diagnostics)
  - MapExporter       → map.toon       (structural map + project header)
  - FlowExporter      → flow.toon      (data-flow: pipelines, contracts, types)
  - EvolutionExporter  → evolution.toon (ranked refactoring queue)
  - ContextExporter   → context.md     (LLM narrative)
  - READMEExporter    → README.md      (documentation of all files)
  - YAMLExporter      → analysis.yaml
  - JSONExporter      → analysis.json
  - MermaidExporter   → *.mmd

Backward-compat alias: LLMPromptExporter = ContextExporter
"""

from .base import Exporter
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
from .report_generators import (
    ToonViewGenerator, ContextViewGenerator,
    ArticleViewGenerator, HTMLDashboardGenerator,
    load_project_yaml,
)
from .index_generator import IndexHTMLGenerator

__all__ = [
    'Exporter',
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
    'ToonViewGenerator',
    'ContextViewGenerator',
    'ArticleViewGenerator',
    'HTMLDashboardGenerator',
    'IndexHTMLGenerator',
    'load_project_yaml',
]