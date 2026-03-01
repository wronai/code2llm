"""Stałe dla FlowExporter.

Zawiera progi, wzorce wykluczeń i rekomendacje dotyczące podziału typów hub.
"""

# Progi dla wykrywania problemów
CC_HIGH = 15
FAN_OUT_THRESHOLD = 10
HUB_TYPE_THRESHOLD = 10

# Wzorce do wykluczenia (venv, cache, etc.)
EXCLUDE_PATTERNS = {
    'venv', '.venv', 'env', '.env', 'publish-env', 'test-env',
    'site-packages', 'node_modules', '__pycache__', '.git',
    'dist', 'build', 'egg-info', '.tox', '.mypy_cache',
}

# Rekomendacje podziału typów hub: typ -> sugerowane pod-interfejsy
HUB_SPLIT_RECOMMENDATIONS = {
    "AnalysisResult": [
        "StructureResult (modules, classes, functions)",
        "MetricsResult (complexity, coupling)",
        "FlowResult (call_graph, cfg, dfg)",
    ],
    "dict": ["replace with typed alternatives (dataclass/TypedDict)"],
    "str": [],  # primitive, expected to be ubiquitous
    "list": [],
    "Any": [],
}
