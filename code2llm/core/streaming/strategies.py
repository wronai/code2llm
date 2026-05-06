"""Scanning strategies for streaming analyzer."""

from dataclasses import dataclass


@dataclass
class ScanStrategy:
    """Scanning methodology configuration."""
    name: str
    description: str
    
    # Analysis phases
    phase_1_quick_scan: bool = True  # Only functions/classes, no CFG
    phase_2_call_graph: bool = True  # Build call relationships
    phase_3_deep_analysis: bool = False  # Full CFG only for important files
    phase_4_patterns: bool = False  # Pattern detection
    
    # Memory limits
    max_files_in_memory: int = 100
    max_nodes_per_function: int = 50
    max_total_nodes: int = 10000
    
    # Prioritization
    prioritize_entry_points: bool = True
    prioritize_public_api: bool = True
    skip_private_functions: bool = True
    skip_test_files: bool = True
    
    # Output
    streaming_output: bool = True
    incremental_save: bool = True


# Predefined strategies
STRATEGY_QUICK = ScanStrategy(
    name="quick",
    description="Fast overview - functions/classes only, no CFG",
    phase_1_quick_scan=True,
    phase_2_call_graph=True,
    phase_3_deep_analysis=False,
    phase_4_patterns=False,
    max_files_in_memory=200,
    skip_private_functions=True,
)

STRATEGY_STANDARD = ScanStrategy(
    name="standard",
    description="Balanced analysis with selective CFG",
    phase_1_quick_scan=True,
    phase_2_call_graph=True,
    phase_3_deep_analysis=True,
    phase_4_patterns=True,
    max_files_in_memory=100,
    max_nodes_per_function=30,
    prioritize_entry_points=True,
)

STRATEGY_DEEP = ScanStrategy(
    name="deep",
    description="Complete analysis with full CFG for all files",
    phase_1_quick_scan=True,
    phase_2_call_graph=True,
    phase_3_deep_analysis=True,
    phase_4_patterns=True,
    max_files_in_memory=50,
    max_nodes_per_function=100,
    prioritize_entry_points=True,
)
