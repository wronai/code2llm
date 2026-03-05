"""
code2llm - Optimized Python Code Flow Analysis Tool

A high-performance tool for analyzing Python code control flow, data flow,
and call graphs with caching and parallel processing.

Includes NLP Processing Pipeline for query normalization, intent matching,
and entity resolution with multilingual support.
"""

__version__ = "0.5.36"
__author__ = "STTS Project"

# Core analysis components (lightweight, always needed)
from .core.config import Config, FAST_CONFIG
from .core.models import AnalysisResult, FunctionInfo, ClassInfo, Pattern

__all__ = [
    # Core
    "ProjectAnalyzer",
    "Config",
    "FAST_CONFIG",
    "AnalysisResult",
    "FunctionInfo",
    "ClassInfo",
    "Pattern",
    # NLP Pipeline
    "NLPPipeline",
    "QueryNormalizer",
    "IntentMatcher",
    "EntityResolver",
    "NLPConfig",
    "FAST_NLP_CONFIG",
    "PRECISE_NLP_CONFIG",
]


def __getattr__(name):
    """Lazy import heavy modules on first access."""
    if name == "ProjectAnalyzer":
        from .core.analyzer import ProjectAnalyzer
        return ProjectAnalyzer
    
    _nlp_names = {
        "NLPPipeline", "QueryNormalizer", "IntentMatcher",
        "EntityResolver", "NLPConfig", "FAST_NLP_CONFIG", "PRECISE_NLP_CONFIG",
    }
    if name in _nlp_names:
        from . import nlp
        return getattr(nlp, name)
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
