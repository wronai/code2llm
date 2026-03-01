"""Analysis package for code2llm."""

from .cfg import CFGExtractor
from .dfg import DFGExtractor
from .call_graph import CallGraphExtractor
from .coupling import CouplingAnalyzer
from .smells import SmellDetector
from .data_analysis import DataAnalyzer
from .type_inference import TypeInferenceEngine
from .side_effects import SideEffectDetector
from .pipeline_detector import PipelineDetector

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
]
