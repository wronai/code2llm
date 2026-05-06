"""Core analysis components for code2llm."""

from .config import Config, FAST_CONFIG, PerformanceConfig, FilterConfig
from .models import (
    AnalysisResult, FlowNode, FlowEdge, 
    FunctionInfo, ClassInfo, ModuleInfo, Pattern
)

__all__ = [
    'ProjectAnalyzer',
    'StreamingAnalyzer',
    'StreamingIncrementalAnalyzer',
    'ScanStrategy',
    'SmartPrioritizer',
    'STRATEGY_QUICK',
    'STRATEGY_STANDARD',
    'STRATEGY_DEEP',
    'FileCache',
    'FastFileFilter',
    'Config',
    'FAST_CONFIG',
    'AnalysisResult',
    'FunctionInfo',
    'ClassInfo',
    'ModuleInfo',
]


def __getattr__(name):
    """Lazy import heavy modules on first access."""
    if name == 'ProjectAnalyzer':
        from .analyzer import ProjectAnalyzer
        return ProjectAnalyzer
    if name == 'FileAnalyzer':
        from .file_analyzer import FileAnalyzer
        return FileAnalyzer
    if name == 'RefactoringAnalyzer':
        from .refactoring import RefactoringAnalyzer
        return RefactoringAnalyzer
    if name in {'FileCache', 'FastFileFilter'}:
        from .file_cache import FileCache
        from .file_filter import FastFileFilter
        return locals()[name]
    
    _streaming_names = {
        'StreamingAnalyzer', 'StreamingIncrementalAnalyzer', 'ScanStrategy',
        'SmartPrioritizer', 'STRATEGY_QUICK', 'STRATEGY_STANDARD', 'STRATEGY_DEEP',
    }
    if name in _streaming_names:
        from . import streaming_analyzer as _mod
        return getattr(_mod, name)
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")