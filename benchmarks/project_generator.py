"""Generator projektu testowego dla benchmarków.

Tworzy strukturę plików z znanymi problemami do weryfikacji
jakości formatów wyjściowych code2llm.
"""

import textwrap
from pathlib import Path


def create_core_py(project: Path) -> None:
    """Utwórz core.py z god function, hub type, high fan-out i side-effect."""
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
            """Side effect: mutates global cache."""
            global _cache
            _cache[key] = result

        def get_cached(key: str) -> Optional[Result]:
            return _cache.get(key)

        def process_everything(data: list, config: Config) -> Result:
            """God function — does too many things."""
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
            """Dead code — never called."""
            return x * 2 + 1

        def main(config: Config) -> None:
            """High fan-out entry point."""
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


def create_etl_py(project: Path) -> None:
    """Utwórz etl.py z funkcjami pipeline ETL."""
    (project / "etl.py").write_text(textwrap.dedent("""\
        from typing import List, Dict
        from core import Config, Result

        def extract_data(config: Config) -> List[dict]:
            """ETL stage 1: extract from source."""
            # IO: reads from file
            with open(config.output_path + "/input.json") as f:
                import json
                return json.load(f)

        def transform_data(data: List[dict], config: Config) -> List[dict]:
            """ETL stage 2: pure transformation."""
            return [
                {k: v.upper() if isinstance(v, str) else v for k, v in item.items()}
                for item in data
                if item.get("active", True)
            ]

        def load_data(data: List[dict], config: Config) -> Result:
            """ETL stage 3: load to output."""
            # IO: writes to file
            import json
            with open(config.output_path + "/output.json", "w") as f:
                json.dump(data, f)
            return Result(data=data, metadata={"loaded": str(len(data))})
    """))


def create_validation_py(project: Path) -> None:
    """Utwórz validation.py z pipeline'em walidacji."""
    (project / "validation.py").write_text(textwrap.dedent("""\
        from typing import List, Dict, Optional
        from core import Result

        def parse_input(raw_data) -> Dict:
            """Parse raw input into structured format."""
            if isinstance(raw_data, str):
                import json
                return json.loads(raw_data)
            return {"items": raw_data}

        def validate_schema(data: Dict) -> Dict:
            """Validate data schema — pure function."""
            errors = []
            if "items" not in data:
                errors.append("missing 'items' key")
            if errors:
                data["schema_errors"] = errors
            return data

        def validate_rules(data: Dict) -> Dict:
            """Validate business rules — pure function."""
            errors = data.get("schema_errors", [])
            items = data.get("items", [])
            for i, item in enumerate(items):
                if not isinstance(item, dict):
                    errors.append(f"item {i} is not a dict")
            if errors:
                data["rule_errors"] = errors
            return data

        def format_errors(data: Dict) -> Optional[Result]:
            """Format validation errors into Result."""
            all_errors = data.get("schema_errors", []) + data.get("rule_errors", [])
            if all_errors:
                return Result(errors=all_errors)
            return None
    """))


def create_utils_py(project: Path) -> None:
    """Utwórz utils.py z duplikatem klasy Validator."""
    (project / "utils.py").write_text(textwrap.dedent("""\
        from core import Result, Config

        class Validator:
            """Duplicate of core Validator — should be merged."""
            def __init__(self, config: Config):
                self.config = config

            def validate(self, data: list) -> Result:
                if not data:
                    return Result(errors=["empty"])
                return Result(data=data)

        def report(result: Result, config: Config) -> None:
            """Consume Result to generate report."""
            if result.is_ok():
                print(f"OK: {len(result.data)} items")
            else:
                print(f"ERRORS: {result.errors}")

        def process_data(data, config):
            """No type annotations — bad practice."""
            v = Validator(config)
            return v.validate(data)
    """))


def add_validator_to_core(project: Path) -> None:
    """Dodaj klasę Validator do core.py (tworzy duplikat)."""
    with open(project / "core.py", "a") as f:
        f.write(textwrap.dedent("""
        class Validator:
            """Validator — also exists in utils.py."""
            def __init__(self, config: Config):
                self.config = config

            def validate(self, data: list) -> Result:
                if not data:
                    return Result(errors=["empty"])
                return Result(data=data)
        """))


def create_ground_truth_project(base_dir: Path) -> Path:
    """Utwórz projekt testowy ze znanymi, mierzalnymi problemami."""
    project = base_dir / "sample_project"
    project.mkdir(parents=True, exist_ok=True)

    create_core_py(project)
    create_etl_py(project)
    create_validation_py(project)
    create_utils_py(project)
    add_validator_to_core(project)

    return project
