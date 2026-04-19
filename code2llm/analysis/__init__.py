"""Analysis package for code2llm."""

__all__ = [
    'CFGExtractor',
    'DFGExtractor',
    'CallGraphExtractor',
    'CouplingAnalyzer',
    'SmellDetector',
    'DataAnalyzer',
    'TypeInferenceEngine',
    'SideEffectDetector',
    'PipelineDetector',
    'PipelineResolver',
    'PipelineClassifier',
]


def __getattr__(name):
    """Lazy import analysis modules on first access."""
    _imports = {
        'CFGExtractor': '.cfg',
        'DFGExtractor': '.dfg',
        'CallGraphExtractor': '.call_graph',
        'CouplingAnalyzer': '.coupling',
        'SmellDetector': '.smells',
        'DataAnalyzer': '.data_analysis',
        'TypeInferenceEngine': '.type_inference',
        'SideEffectDetector': '.side_effects',
        'PipelineDetector': '.pipeline_detector',
        'PipelineResolver': '.pipeline_resolver',
        'PipelineClassifier': '.pipeline_classifier',
    }
    if name in _imports:
        import importlib
        module = importlib.import_module(_imports[name], __package__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
