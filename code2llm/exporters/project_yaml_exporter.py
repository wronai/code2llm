"""Project YAML Exporter — unified single source of truth for project diagnostics.

BACKWARD COMPATIBILITY: This module now re-exports from project_yaml package.
The implementation has been split into focused modules:
  - project_yaml/core: main exporter class
  - project_yaml/health: CC metrics, alerts
  - project_yaml/modules: per-file metrics, exports
  - project_yaml/hotspots: high fan-out detection
  - project_yaml/evolution: append-only history
"""

# Re-export from new package location for backward compatibility
from .project_yaml import ProjectYAMLExporter

__all__ = ["ProjectYAMLExporter"]
