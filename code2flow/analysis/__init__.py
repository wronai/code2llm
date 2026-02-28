"""Analysis package for code2flow."""

from .cfg import CFGExtractor
from .dfg import DFGExtractor
from .call_graph import CallGraphExtractor
from .coupling import CouplingAnalyzer
from .smells import SmellDetector
from .data_analysis import DataAnalyzer

__all__ = [
    'CFGExtractor',
    'DFGExtractor',
    'CallGraphExtractor',
    'CouplingAnalyzer',
    'SmellDetector',
    'DataAnalyzer'
]
