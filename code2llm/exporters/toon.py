"""Toon Exporter v2 — scannable plain-text format for code2llm.

Structure communicates health: sorting by severity, inline markers,
coupling matrix, duplicate detection, filtered functions.
"""

# Re-export the modular ToonExporter for backward compatibility
from .toon import ToonExporter

# Keep this file for backward compatibility - the actual implementation is now in .toon/
