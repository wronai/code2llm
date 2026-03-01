"""Stałe dane dla benchmarku jakości formatów.

Zawiera znane problemy, pipeline'y i typy hub używane jako ground truth
w benchmarkach jakości formatów.
"""

# Znane problemy w projekcie testowym
KNOWN_PROBLEMS = {
    "god_function":     "process_everything in core.py has CC≥15",
    "hub_type":         "Result is consumed by ≥5 functions",
    "duplicate_class":  "Validator exists in both core.py and utils.py",
    "impure_pipeline":  "transform pipeline has IO in the middle",
    "dead_code":        "unused_helper is never called",
    "high_fan_out":     "main() calls ≥8 functions",
    "missing_types":    "process_data has no type annotations",
    "side_effect":      "cache_result mutates global state",
}

# Znane pipeline'y w projekcie testowym
KNOWN_PIPELINES = {
    "ETL":        ["extract_data", "transform_data", "load_data"],
    "Validation": ["parse_input", "validate_schema", "validate_rules", "format_errors"],
}

# Znane typy hub w projekcie testowym
KNOWN_HUB_TYPES = {
    "Result":  {"consumed_by": 6, "produced_by": 2},
    "Config":  {"consumed_by": 4, "produced_by": 1},
}
