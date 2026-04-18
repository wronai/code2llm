"""Project YAML Exporter — unified single source of truth for project diagnostics.

This package splits the original monolithic exporter into focused modules:
  - health: CC metrics, alerts, duplicates
  - modules: per-file metrics, exports
  - hotspots: high fan-out detection
  - evolution: append-only history log

Backward compatible: ProjectYAMLExporter can still be imported from here
or from the original location.
"""

from .core import ProjectYAMLExporter

__all__ = ["ProjectYAMLExporter"]
