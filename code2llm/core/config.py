"""Configuration and constants for code2llm."""

import os
import psutil
from dataclasses import dataclass, field
from typing import List, Set
from enum import Enum


def _get_optimal_workers(default: int = 4, max_per_gb: float = 2.0) -> int:
    """Calculate optimal parallel workers based on CPU and available RAM.

    Args:
        default: Default workers if detection fails
        max_per_gb: Max workers per GB of RAM

    Returns:
        Optimal worker count (at least 1)
    """
    try:
        cpu_count = os.cpu_count() or default
        available_ram_gb = psutil.virtual_memory().available / (1024 ** 3)
        # Limit workers by RAM (assume each worker needs ~500MB)
        ram_limited = int(available_ram_gb * max_per_gb)
        # Take minimum of CPU and RAM limits, but at least 1
        return max(1, min(cpu_count, ram_limited))
    except Exception:
        return default


# Performance limits (named constants for magic numbers)
DEFAULT_MAX_NODES_PER_FILE = 1000
DEFAULT_MAX_TOTAL_NODES = 10000
DEFAULT_MAX_EDGES = 50000
DEFAULT_CACHE_TTL_HOURS = 24
DEFAULT_MAX_MEMORY_MB = 2048
DEFAULT_PROGRESS_BAR_THRESHOLD = 50  # File count threshold for progress bar

# Complexity thresholds
CC_LOW_THRESHOLD = 5      # Rank A
CC_MEDIUM_THRESHOLD = 10  # Rank B
CC_HIGH_THRESHOLD = 20    # Rank C
CC_CRITICAL_THRESHOLD = 50  # For warnings

# Size limits
KB = 1024
MB = 1024 * 1024
MAX_FILE_SIZE_KB = 256
CHUNK_SIZE_KB = 256

# Timeouts
DEFAULT_PNG_TIMEOUT = 60
DEFAULT_MERMAID_MAX_TEXT_SIZE = 2_000_000
DEFAULT_MERMAID_MAX_EDGES = 20_000

# Cache settings
DEFAULT_CACHE_MAX_AGE_DAYS = 30


class AnalysisMode(str, Enum):
    """Available analysis modes."""
    STATIC = "static"
    DYNAMIC = "dynamic"
    HYBRID = "hybrid"
    BEHAVIORAL = "behavioral"
    REVERSE = "reverse"


@dataclass
class PerformanceConfig:
    """Performance optimization settings."""
    enable_cache: bool = True
    cache_dir: str = ".code2llm_cache"
    cache_ttl_hours: int = DEFAULT_CACHE_TTL_HOURS
    parallel_workers: int = 0  # 0 = auto-detect based on CPU/RAM
    parallel_enabled: bool = True
    max_memory_mb: int = DEFAULT_MAX_MEMORY_MB
    max_nodes_per_file: int = DEFAULT_MAX_NODES_PER_FILE
    max_total_nodes: int = DEFAULT_MAX_TOTAL_NODES
    max_edges: int = DEFAULT_MAX_EDGES
    fast_mode: bool = False
    skip_data_flow: bool = False
    skip_pattern_detection: bool = False
    skip_refactoring_analysis: bool = False
    skip_dead_code_detection: bool = True
    skip_centrality: bool = False
    skip_community_detection: bool = False

    def get_workers(self) -> int:
        """Get effective worker count (auto-detect if set to 0)."""
        if self.parallel_workers <= 0:
            return _get_optimal_workers(default=4)
        return self.parallel_workers

    def apply_fast_mode(self) -> None:
        """Apply fast_mode overrides — skip expensive analyses."""
        if not self.fast_mode:
            return
        self.skip_data_flow = True
        self.skip_pattern_detection = True
        self.skip_dead_code_detection = True
        self.skip_centrality = True
        self.skip_community_detection = True


@dataclass
class FilterConfig:
    """Filtering options to reduce analysis scope."""
    exclude_tests: bool = True
    exclude_patterns: List[str] = field(default_factory=lambda: [
        "*__pycache__*", "*.pyc", "*/venv/*", "*/.venv/*",
        "*node_modules*", "*/.git/*", "*/build/*", "*/dist/*",
        "*_test.py", "test_*.py", "conftest.py",
        "*/tests/*", "*/test/*",
        "*demo_langs/invalid*",
        # Lockfiles and generated artefacts — declarative but noisy and
        # auto-generated, keep them out of the manifest by default.
        "*package-lock.json", "*yarn.lock", "*pnpm-lock.yaml",
        "*poetry.lock", "*Pipfile.lock", "*Cargo.lock", "*composer.lock",
        "*.terraform.lock.hcl", "*.tfstate", "*.tfstate.backup",
        "*.min.js", "*.min.css", "*.map",
    ])
    include_patterns: List[str] = field(default_factory=list)
    min_function_lines: int = 1
    skip_private: bool = False
    skip_properties: bool = True
    skip_accessors: bool = True
    gitignore_enabled: bool = True


@dataclass
class DepthConfig:
    """Depth limiting for control flow analysis."""
    max_cfg_depth: int = 5
    max_call_depth: int = 3
    max_data_flow_depth: int = 2
    max_interprocedural_depth: int = 2


@dataclass
class OutputConfig:
    """Output formatting options."""
    compact: bool = True
    include_source: bool = False
    max_label_length: int = 50
    group_by_module: bool = True


@dataclass
class Config:
    """Analysis configuration with performance optimizations."""
    
    # Analysis mode
    mode: str = "hybrid"
    
    # Sub-configs for performance
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    filters: FilterConfig = field(default_factory=FilterConfig)
    depth: DepthConfig = field(default_factory=DepthConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    
    # Legacy path limits (for compatibility)
    max_paths_per_function: int = 20
    max_depth_enumeration: int = 10
    max_depth_interprocedural: int = 3
    max_total_paths: int = 1000
    
    # Output settings
    output_formats: List[str] = field(default_factory=lambda: ["yaml", "mermaid", "png"])
    output_dir: str = "output"
    
    # Visualization
    fig_size: tuple = (16, 12)
    dpi: int = 300
    layout: str = "sfdp"  # dot, neato, fdp, sfdp, circo, twopi
    
    # Pattern detection
    detect_state_machines: bool = True
    detect_recursion: bool = True
    detect_loops: bool = True
    
    # Dynamic analysis
    trace_runtime: bool = False
    skip_packages: Set[str] = field(default_factory=lambda: {
        'site-packages', 'dist-packages', 'venv', '.venv'
    })
    
    # Logging
    verbose: bool = False
    quiet: bool = False


# Predefined fast configuration
FAST_CONFIG = Config(
    mode="static",
    performance=PerformanceConfig(
        fast_mode=True,
        skip_data_flow=True,
        skip_pattern_detection=True,
        parallel_enabled=True,
        parallel_workers=0,  # auto-detect
        max_nodes_per_file=500,
        max_total_nodes=5000,
    ),
    filters=FilterConfig(
        exclude_tests=True,
        skip_private=True,
        skip_properties=True,
        skip_accessors=True,
        min_function_lines=1,
    ),
    depth=DepthConfig(
        max_cfg_depth=3,
        max_call_depth=2,
        max_data_flow_depth=1,
        max_interprocedural_depth=1,
    ),
    output=OutputConfig(compact=True, include_source=False),
    layout="dot",
)


# Analysis modes descriptions
ANALYSIS_MODES = {
    'static': 'AST-based control and data flow analysis',
    'dynamic': 'Runtime execution tracing',
    'hybrid': 'Combined static + dynamic analysis',
    'behavioral': 'Behavioral pattern extraction',
    'reverse': 'Reverse engineering ready output'
}


# Supported language extensions
LANGUAGE_EXTENSIONS = {
    'python': ['.py'],
    'typescript': ['.ts', '.tsx'],
    'javascript': ['.js', '.jsx', '.mjs', '.cjs'],
    'go': ['.go'],
    'rust': ['.rs'],
    'java': ['.java'],
    'cpp': ['.cpp', '.cc', '.cxx', '.hpp', '.hh', '.h'],
    'c': ['.c', '.h'],
    'csharp': ['.cs'],
    'ruby': ['.rb'],
    'php': ['.php'],
    'swift': ['.swift'],
    'kotlin': ['.kt', '.kts'],
    'scala': ['.scala'],
    'r': ['.r', '.R'],
    'matlab': ['.m'],
    'shell': ['.sh', '.bash', '.zsh'],
    'dart': ['.dart'],
    'elixir': ['.ex', '.exs'],
    'clojure': ['.clj', '.cljs'],
    'haskell': ['.hs'],
    'lua': ['.lua'],
    'perl': ['.pl', '.pm'],
    'raku': ['.raku', '.rakumod'],
}

# Declarative / IaC / config / docs extensions.
# These are NOT analyzed for call graphs or CC — they're routed to the
# generic analyzer. The point is to include them in the content-addressed
# manifest so the export cache is invalidated when they change (e.g.
# editing Dockerfile, terraform .tf, k8s manifests, pyproject.toml,
# README.md, openapi.yaml, ...).
DECLARATIVE_EXTENSIONS = {
    # Infrastructure as Code
    'terraform':   ['.tf', '.tfvars', '.hcl'],
    'bicep':       ['.bicep'],
    'nix':         ['.nix'],
    # (K8s/Helm/Ansible/Pulumi/CloudFormation/docker-compose all use
    #  yaml/json, matched below.)
    # Config / serialization
    'yaml':        ['.yaml', '.yml'],
    'toml':        ['.toml'],
    'ini':         ['.ini', '.cfg', '.conf', '.properties'],
    'xml':         ['.xml'],
    'json_config': ['.json', '.json5', '.jsonc'],
    'env':         ['.env'],
    # Schema / IDL
    'proto':       ['.proto'],
    'graphql':     ['.graphql', '.gql'],
    'avro':        ['.avsc'],
    'prisma':      ['.prisma'],
    # Documentation
    'markdown':    ['.md', '.mdx', '.markdown'],
    'rst':         ['.rst'],
    'asciidoc':    ['.adoc', '.asciidoc'],
    'text':        ['.txt'],
    # Project DSLs (user-specific, low-friction to include)
    'dsl':         ['.doql', '.dsl'],
}

# Declarative files matched by FILENAME (no extension, or compound names).
# Case-insensitive matched against os.path.basename().
LANGUAGE_FILENAMES = {
    'dockerfile': ['Dockerfile', 'Containerfile'],
    'makefile':   ['Makefile', 'GNUmakefile', 'BSDmakefile'],
    'jenkins':    ['Jenkinsfile'],
    'vagrant':    ['Vagrantfile'],
    'rakefile':   ['Rakefile'],
    'gemfile':    ['Gemfile'],
    'procfile':   ['Procfile'],
    'caddyfile':  ['Caddyfile'],
    'pipfile':    ['Pipfile'],
    'brewfile':   ['Brewfile'],
}

# Filename PREFIXES that indicate a declarative file even with arbitrary
# suffix — e.g. `Dockerfile.dev`, `Dockerfile.prod`, `Makefile.am`.
# The match is case-insensitive against the basename; a '.' suffix is
# required so we don't accidentally match e.g. `Dockerfiles/`.
LANGUAGE_FILENAME_PREFIXES = ('Dockerfile.', 'Containerfile.', 'Makefile.')

# All supported extensions flat list (programming languages + declarative)
ALL_EXTENSIONS = (
    [ext for exts in LANGUAGE_EXTENSIONS.values() for ext in exts]
    + [ext for exts in DECLARATIVE_EXTENSIONS.values() for ext in exts]
)

# Flat set of recognised filenames (case-insensitive compare at collection time).
ALL_FILENAMES = frozenset(
    name for names in LANGUAGE_FILENAMES.values() for name in names
)

# Node types
NODE_TYPES = {
    'FUNC': 'Function definition',
    'CALL': 'Function call',
    'IF': 'Conditional branch',
    'FOR': 'For loop',
    'WHILE': 'While loop',
    'ASSIGN': 'Variable assignment',
    'RETURN': 'Return statement',
    'ENTRY': 'Entry point',
    'EXIT': 'Exit point',
}


# Colors for visualization
NODE_COLORS = {
    'FUNC': '#4CAF50',
    'CALL': '#2196F3',
    'IF': '#FF9800',
    'FOR': '#9C27B0',
    'WHILE': '#9C27B0',
    'ASSIGN': '#607D8B',
    'RETURN': '#E91E63',
    'ENTRY': '#00BCD4',
    'EXIT': '#F44336',
}
