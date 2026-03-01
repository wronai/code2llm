"""Backward-compatibility shim: LLMPromptExporter → ContextExporter.

The canonical implementation is now in context_exporter.py.
This module re-exports the old name for backward compatibility.
"""

from .context_exporter import ContextExporter

# Backward-compat alias
LLMPromptExporter = ContextExporter

__all__ = ["LLMPromptExporter", "ContextExporter"]
