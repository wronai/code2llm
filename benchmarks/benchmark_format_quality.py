#!/usr/bin/env python3
"""
Format Quality Benchmark — measures how USEFUL each output format is
for data-flow refactoring decisions.

This is NOT a speed benchmark. It measures INFORMATION QUALITY:
- Can the format detect known problems in a test project?
- Does it show data flow pipelines?
- Does it identify hub types?
- Does it provide actionable refactoring steps?

Run with: python benchmarks/benchmark_format_quality.py
"""

import ast
import json
import os
import re
import shutil
import tempfile
import textwrap
import time
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


# ─────────────────────────────────────────────────────────────────
# Test project with KNOWN problems for ground-truth comparison
# ─────────────────────────────────────────────────────────────────

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

KNOWN_PIPELINES = {
    "ETL":        ["extract_data", "transform_data", "load_data"],
    "Validation": ["parse_input", "validate_schema", "validate_rules", "format_errors"],
}

KNOWN_HUB_TYPES = {
    "Result":  {"consumed_by": 6, "produced_by": 2},
    "Config":  {"consumed_by": 4, "produced_by": 1},
}


def create_ground_truth_project(base_dir: Path) -> Path:
    """Create a project with known, measurable problems."""
    project = base_dir / "sample_project"
    project.mkdir(parents=True, exist_ok=True)

    # ── core.py: God function + hub type + high fan-out + side-effect ──
    (project / "core.py").write_text(textwrap.dedent("""\
        from typing import List, Dict, Optional
        from dataclasses import dataclass

        @dataclass
        class Config:
            debug: bool = False
            max_items: int = 100
            output_path: str = "./out"

        @dataclass
        class Result:
            data: List[dict] = None
            errors: List[str] = None
            metadata: Dict[str, str] = None
            
            def is_ok(self) -> bool:
                return not self.errors

        _cache: Dict[str, Result] = {}

        def cache_result(key: str, result: Result) -> None:
            \"\"\"Side effect: mutates global cache.\"\"\"
            global _cache
            _cache[key] = result

        def get_cached(key: str) -> Optional[Result]:
            return _cache.get(key)

        def process_everything(data: list, config: Config) -> Result:
            \"\"\"God function — does too many things.\"\"\"
            # validate
            if not data:
                return Result(errors=["empty data"])
            if not isinstance(data, list):
                return Result(errors=["not a list"])
            # filter
            filtered = []
            for item in data:
                if isinstance(item, dict):
                    if "id" in item:
                        if item.get("active", True):
                            filtered.append(item)
                        elif config.debug:
                            filtered.append(item)
                    else:
                        if config.debug:
                            print(f"No id: {item}")
                else:
                    if config.debug:
                        print(f"Not dict: {item}")
            # transform
            results = []
            for item in filtered:
                transformed = {}
                for key, value in item.items():
                    if isinstance(value, str):
                        transformed[key] = value.strip().lower()
                    elif isinstance(value, (int, float)):
                        transformed[key] = value
                    else:
                        transformed[key] = str(value)
                results.append(transformed)
            # aggregate
            if len(results) > config.max_items:
                results = results[:config.max_items]
            metadata = {"count": str(len(results)), "source": "process_everything"}
            return Result(data=results, metadata=metadata)

        def unused_helper(x: int) -> int:
            \"\"\"Dead code — never called.\"\"\"
            return x * 2 + 1

        def main(config: Config) -> None:
            \"\"\"High fan-out entry point.\"\"\"
            data = extract_data(config)
            validated = parse_input(data)
            schema_ok = validate_schema(validated)
            rules_ok = validate_rules(schema_ok)
            errors = format_errors(rules_ok)
            transformed = transform_data(validated, config)
            result = load_data(transformed, config)
            cache_result("latest", result)
            report(result, config)
    """))

    # ── etl.py: Pipeline functions ──
    (project / "etl.py").write_text(textwrap.dedent("""\
        from typing import List, Dict
        from core import Config, Result

        def extract_data(config: Config) -> List[dict]:
            \"\"\"ETL stage 1: extract from source.\"\"\"
            # IO: reads from file
            with open(config.output_path + "/input.json") as f:
                import json
                return json.load(f)

        def transform_data(data: List[dict], config: Config) -> List[dict]:
            \"\"\"ETL stage 2: pure transformation.\"\"\"
            return [
                {k: v.upper() if isinstance(v, str) else v for k, v in item.items()}
                for item in data
                if item.get("active", True)
            ]

        def load_data(data: List[dict], config: Config) -> Result:
            \"\"\"ETL stage 3: load to output.\"\"\"
            # IO: writes to file
            import json
            with open(config.output_path + "/output.json", "w") as f:
                json.dump(data, f)
            return Result(data=data, metadata={"loaded": str(len(data))})
    """))

    # ── validation.py: Validation pipeline ──
    (project / "validation.py").write_text(textwrap.dedent("""\
        from typing import List, Dict, Optional
        from core import Result

        def parse_input(raw_data) -> Dict:
            \"\"\"Parse raw input into structured format.\"\"\"
            if isinstance(raw_data, str):
                import json
                return json.loads(raw_data)
            return {"items": raw_data}

        def validate_schema(data: Dict) -> Dict:
            \"\"\"Validate data schema — pure function.\"\"\"
            errors = []
            if "items" not in data:
                errors.append("missing 'items' key")
            if errors:
                data["schema_errors"] = errors
            return data

        def validate_rules(data: Dict) -> Dict:
            \"\"\"Validate business rules — pure function.\"\"\"
            errors = data.get("schema_errors", [])
            items = data.get("items", [])
            for i, item in enumerate(items):
                if not isinstance(item, dict):
                    errors.append(f"item {i} is not a dict")
            if errors:
                data["rule_errors"] = errors
            return data

        def format_errors(data: Dict) -> Optional[Result]:
            \"\"\"Format validation errors into Result.\"\"\"
            all_errors = data.get("schema_errors", []) + data.get("rule_errors", [])
            if all_errors:
                return Result(errors=all_errors)
            return None
    """))

    # ── utils.py: Contains DUPLICATE Validator class ──
    (project / "utils.py").write_text(textwrap.dedent("""\
        from core import Result, Config

        class Validator:
            \"\"\"Duplicate of core Validator — should be merged.\"\"\"
            def __init__(self, config: Config):
                self.config = config

            def validate(self, data: list) -> Result:
                if not data:
                    return Result(errors=["empty"])
                return Result(data=data)

        def report(result: Result, config: Config) -> None:
            \"\"\"Consume Result to generate report.\"\"\"
            if result.is_ok():
                print(f"OK: {len(result.data)} items")
            else:
                print(f"ERRORS: {result.errors}")

        def process_data(data, config):
            \"\"\"No type annotations — bad practice.\"\"\"
            v = Validator(config)
            return v.validate(data)
    """))

    # Add Validator to core.py too (for duplicate detection)
    with open(project / "core.py", "a") as f:
        f.write(textwrap.dedent("""
        class Validator:
            \"\"\"Validator — also exists in utils.py.\"\"\"
            def __init__(self, config: Config):
                self.config = config

            def validate(self, data: list) -> Result:
                if not data:
                    return Result(errors=["empty"])
                return Result(data=data)
        """))

    return project


# ─────────────────────────────────────────────────────────────────
# Evaluation: parse each format and check what it detected
# ─────────────────────────────────────────────────────────────────

@dataclass
class FormatScore:
    name: str
    file_path: Optional[Path] = None
    size_bytes: int = 0
    generation_time: float = 0.0

    # Problem detection (out of KNOWN_PROBLEMS)
    problems_detected: Dict[str, bool] = field(default_factory=dict)
    
    # Pipeline detection (out of KNOWN_PIPELINES)
    pipelines_detected: Dict[str, bool] = field(default_factory=dict)
    
    # Hub type detection (out of KNOWN_HUB_TYPES)
    hub_types_detected: Dict[str, bool] = field(default_factory=dict)
    
    # Structural completeness
    has_call_chains: bool = False
    has_type_info: bool = False
    has_coupling_info: bool = False
    has_severity_markers: bool = False
    has_refactor_steps: bool = False
    has_side_effects: bool = False
    has_purity_info: bool = False
    has_contracts: bool = False
    
    # Computed scores
    problem_score: float = 0.0      # 0-100%
    pipeline_score: float = 0.0     # 0-100%
    hub_type_score: float = 0.0     # 0-100%
    structural_score: float = 0.0   # 0-100%
    total_score: float = 0.0        # 0-100%


def evaluate_format(name: str, content: str, path: Optional[Path] = None) -> FormatScore:
    """Evaluate a single format against ground truth."""
    score = FormatScore(name=name, file_path=path)
    if path and path.exists():
        score.size_bytes = path.stat().st_size
    
    cl = content.lower()
    
    # ── Problem detection ──
    score.problems_detected = {
        "god_function":    bool(re.search(r'god|!! split|CC[=≥]\s*(1[5-9]|[2-9]\d)', content)),
        "hub_type":        bool(re.search(r'hub.?type|consumed.?\d|HUB|fan.?in.?\d', content, re.I)),
        "duplicate_class": bool(re.search(r'DUP|duplicate|×DUP|identical', content, re.I)),
        "impure_pipeline": bool(re.search(r'impure|IO|side.?effect.*pipeline|purity.*0', content, re.I)),
        "dead_code":       bool(re.search(r'dead.?code|unused|unreachable|never.?called', content, re.I)),
        "high_fan_out":    bool(re.search(r'fan.?out|fan=\d|hotspot|fan-out', content, re.I)),
        "missing_types":   bool(re.search(r'missing.?type|no.?annotation|untyped', content, re.I)),
        "side_effect":     bool(re.search(r'side.?effect|mutation|mutate|global|cache_result', content, re.I)),
    }
    detected = sum(score.problems_detected.values())
    score.problem_score = detected / len(KNOWN_PROBLEMS) * 100

    # ── Pipeline detection ──
    for pipeline_name, stages in KNOWN_PIPELINES.items():
        # Check if ≥2 consecutive stages appear in order
        found_stages = sum(1 for s in stages if s in cl)
        # Check if they appear as a connected chain (→ or similar)
        chain_pattern = r'→|──>|->|calls|chain'
        has_chain = bool(re.search(chain_pattern, content))
        score.pipelines_detected[pipeline_name] = (found_stages >= 2) and has_chain
    
    detected_p = sum(score.pipelines_detected.values())
    score.pipeline_score = detected_p / len(KNOWN_PIPELINES) * 100
    
    # ── Hub type detection ──
    for type_name in KNOWN_HUB_TYPES:
        # Check if type appears with consumption/production counts
        type_pattern = rf'{type_name}.*consumed|{type_name}.*fan|{type_name}.*←\d|{type_name}.*hub'
        score.hub_types_detected[type_name] = bool(re.search(type_pattern, content, re.I))
    
    detected_h = sum(score.hub_types_detected.values())
    score.hub_type_score = detected_h / len(KNOWN_HUB_TYPES) * 100
    
    # ── Structural completeness ──
    score.has_call_chains     = bool(re.search(r'→|calls:|──>|call.?chain|call.?graph', content, re.I))
    score.has_type_info       = bool(re.search(r'->\s*(str|int|dict|list|Result|Config|None)', content))
    score.has_coupling_info   = bool(re.search(r'COUPLING|fan-in|fan-out|import.*graph|←in', content, re.I))
    score.has_severity_markers = bool(re.search(r'!!|🔴|🟡|critical|HEALTH', content))
    score.has_refactor_steps  = bool(re.search(r'REFACTOR|split|extract|merge.*class', content, re.I))
    score.has_side_effects    = bool(re.search(r'SIDE.?EFFECT|pure|impure|IO|mutation', content, re.I))
    score.has_purity_info     = bool(re.search(r'purity|pure.*\d|PURITY', content, re.I))
    score.has_contracts       = bool(re.search(r'CONTRACT|IN:|OUT:|input.*→.*output|invariant', content, re.I))
    
    structural_features = [
        score.has_call_chains, score.has_type_info, score.has_coupling_info,
        score.has_severity_markers, score.has_refactor_steps,
        score.has_side_effects, score.has_purity_info, score.has_contracts,
    ]
    score.structural_score = sum(structural_features) / len(structural_features) * 100
    
    # ── Total (weighted) ──
    score.total_score = (
        score.problem_score * 0.30 +      # 30% — finding problems
        score.pipeline_score * 0.25 +      # 25% — data flow pipelines
        score.hub_type_score * 0.20 +      # 20% — type analysis
        score.structural_score * 0.25      # 25% — format completeness
    )
    
    return score


# ─────────────────────────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────────────────────────

def run_benchmark() -> Dict:
    """Run the full format quality benchmark."""
    
    print("=" * 70)
    print("FORMAT QUALITY BENCHMARK")
    print("Measures: how well each format supports data-flow refactoring")
    print("=" * 70)
    
    # 1. Create ground-truth project
    tmp = Path(tempfile.mkdtemp())
    project_path = create_ground_truth_project(tmp)
    print(f"\n✓ Created ground-truth project: {project_path}")
    print(f"  Known problems: {len(KNOWN_PROBLEMS)}")
    print(f"  Known pipelines: {len(KNOWN_PIPELINES)}")
    print(f"  Known hub types: {len(KNOWN_HUB_TYPES)}")
    
    # 2. Run code2flow and generate all formats
    output_dir = tmp / "output"
    output_dir.mkdir()
    
    scores: Dict[str, FormatScore] = {}
    
    try:
        from code2flow import ProjectAnalyzer, Config
        from code2flow.core.models import AnalysisResult
        
        # Analyze project — use relaxed Config (FAST_CONFIG excludes *test*)
        print(f"\n→ Running code2flow analysis...")
        start = time.time()
        cfg = Config()
        cfg.filters.exclude_patterns = [
            '*__pycache__*', '*.pyc', '*venv*', '*.venv*',
            '*node_modules*', '*.git*',
        ]
        cfg.filters.skip_private = False
        cfg.filters.min_function_lines = 1
        analyzer = ProjectAnalyzer(cfg)
        result = analyzer.analyze_project(str(project_path))
        analysis_time = time.time() - start
        print(f"  Analysis: {analysis_time:.2f}s, {result.get_function_count()} functions")
        
        # Generate each format
        format_configs = {
            "analysis.toon": ("code2flow.exporters.toon", "ToonExporter"),
            "flow.toon":     ("code2flow.exporters.flow_exporter", "FlowExporter"),
            "project.map":   ("code2flow.exporters.map_exporter", "MapExporter"),
            "context.md":    ("code2flow.exporters.llm_exporter", "LLMPromptExporter"),
        }
        
        for filename, (module_path, class_name) in format_configs.items():
            try:
                mod = __import__(module_path, fromlist=[class_name])
                exporter_cls = getattr(mod, class_name)
                exporter = exporter_cls()
                
                out_path = output_dir / filename
                start = time.time()
                exporter.export(result, str(out_path))
                gen_time = time.time() - start
                
                if out_path.exists():
                    content = out_path.read_text(errors="replace")
                    s = evaluate_format(filename, content, out_path)
                    s.generation_time = gen_time
                    scores[filename] = s
                    print(f"  ✓ {filename}: {out_path.stat().st_size:,} bytes, {gen_time:.2f}s")
                else:
                    print(f"  ✗ {filename}: file not created")
                    scores[filename] = FormatScore(name=filename)
            except Exception as e:
                print(f"  ✗ {filename}: {e}")
                scores[filename] = FormatScore(name=filename)
        
    except ImportError as e:
        print(f"\n⚠ code2flow not installed: {e}")
        print("  Running in OFFLINE mode with sample data...")
        # Create minimal fallback scores for when code2flow isn't installed
        for name in ["analysis.toon", "flow.toon", "project.map", "context.md"]:
            scores[name] = FormatScore(name=name)
    
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    
    # 3. Print results
    print_results(scores)
    
    # 4. Save report
    report = build_report(scores)
    return report


def print_results(scores: Dict[str, FormatScore]):
    """Print formatted benchmark results."""
    
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    # Header
    print(f"\n{'Format':<18} {'Problems':>9} {'Pipelines':>10} {'Hub Types':>10} {'Structure':>10} {'TOTAL':>8} {'Size':>8}")
    print("─" * 75)
    
    sorted_scores = sorted(scores.values(), key=lambda s: s.total_score, reverse=True)
    medals = ["🥇", "🥈", "🥉", "  "]
    
    for i, s in enumerate(sorted_scores):
        medal = medals[min(i, 3)]
        size_str = f"{s.size_bytes:,}" if s.size_bytes else "N/A"
        print(f"{medal} {s.name:<15} {s.problem_score:>8.0f}% {s.pipeline_score:>9.0f}%"
              f" {s.hub_type_score:>9.0f}% {s.structural_score:>9.0f}%"
              f" {s.total_score:>7.1f}% {size_str:>8}")
    
    # Detail: which problems each format detected
    print(f"\n{'Problem':<20}", end="")
    for s in sorted_scores:
        print(f" {s.name:^16}", end="")
    print()
    print("─" * (20 + 17 * len(sorted_scores)))
    
    for problem_key, description in KNOWN_PROBLEMS.items():
        label = problem_key.replace("_", " ")[:19]
        print(f"{label:<20}", end="")
        for s in sorted_scores:
            detected = s.problems_detected.get(problem_key, False)
            print(f" {'  ✓  detected':^16}" if detected else f" {'  ✗  missed':^16}", end="")
        print()
    
    # Pipeline detail
    print(f"\n{'Pipeline':<20}", end="")
    for s in sorted_scores:
        print(f" {s.name:^16}", end="")
    print()
    print("─" * (20 + 17 * len(sorted_scores)))
    
    for pipeline_name in KNOWN_PIPELINES:
        print(f"{pipeline_name:<20}", end="")
        for s in sorted_scores:
            detected = s.pipelines_detected.get(pipeline_name, False)
            print(f" {'  ✓  detected':^16}" if detected else f" {'  ✗  missed':^16}", end="")
        print()
    
    # Structural features
    print(f"\n{'Feature':<20}", end="")
    for s in sorted_scores:
        print(f" {s.name:^16}", end="")
    print()
    print("─" * (20 + 17 * len(sorted_scores)))
    
    features = [
        ("Call chains", "has_call_chains"),
        ("Type info", "has_type_info"),
        ("Coupling", "has_coupling_info"),
        ("Severity markers", "has_severity_markers"),
        ("Refactor steps", "has_refactor_steps"),
        ("Side effects", "has_side_effects"),
        ("Purity info", "has_purity_info"),
        ("Contracts", "has_contracts"),
    ]
    for label, attr in features:
        print(f"{label:<20}", end="")
        for s in sorted_scores:
            val = getattr(s, attr)
            print(f" {'  ✓':^16}" if val else f" {'  ✗':^16}", end="")
        print()
    
    # Gap analysis
    print("\n" + "=" * 70)
    print("GAP ANALYSIS — what each format misses")
    print("=" * 70)
    
    for s in sorted_scores:
        missed = [k for k, v in s.problems_detected.items() if not v]
        if missed:
            print(f"\n  {s.name} ({s.total_score:.0f}%) — missed {len(missed)} problems:")
            for m in missed:
                print(f"    ✗ {m}: {KNOWN_PROBLEMS[m]}")


def build_report(scores: Dict[str, FormatScore]) -> Dict:
    """Build JSON report for saving."""
    return {
        "benchmark_type": "format_quality",
        "timestamp": datetime.now().isoformat(),
        "ground_truth": {
            "problems": len(KNOWN_PROBLEMS),
            "pipelines": len(KNOWN_PIPELINES),
            "hub_types": len(KNOWN_HUB_TYPES),
        },
        "results": {
            name: {
                "total_score": s.total_score,
                "problem_score": s.problem_score,
                "pipeline_score": s.pipeline_score,
                "hub_type_score": s.hub_type_score,
                "structural_score": s.structural_score,
                "size_bytes": s.size_bytes,
                "generation_time": s.generation_time,
                "problems_detected": s.problems_detected,
                "pipelines_detected": s.pipelines_detected,
                "hub_types_detected": s.hub_types_detected,
            }
            for name, s in scores.items()
        },
        "ranking": [
            {"rank": i + 1, "format": s.name, "score": s.total_score}
            for i, s in enumerate(
                sorted(scores.values(), key=lambda x: x.total_score, reverse=True)
            )
        ],
    }


def save_report(report: Dict, filename: str = None) -> str:
    """Save benchmark report to reports folder."""
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"format_quality_{timestamp}.json"
    
    report_path = reports_dir / filename
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n[Report saved to: {report_path}]")
    return str(report_path)


if __name__ == "__main__":
    report = run_benchmark()
    save_report(report)
