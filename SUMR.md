# code2llm - Generated Analysis Files

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Quality Pipeline (`pyqual.yaml`)](#quality-pipeline-pyqualyaml)
- [Dependencies](#dependencies)
- [Source Map](#source-map)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `code2llm`
- **version**: `0.5.114`
- **python_requires**: `>=3.8`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, requirements.txt, Taskfile.yml, Makefile, app.doql.css, pyqual.yaml, goal.yaml, .env.example, src(5 mod), project/(6 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.css`)

```css markpact:doql path=app.doql.css
app {
  name: "code2llm";
  version: "0.5.104";
}

entity[name="FlowNode"] {

}

entity[name="FlowEdge"] {

}

entity[name="FunctionInfo"] {

}

entity[name="ClassInfo"] {

}

entity[name="ModuleInfo"] {

}

entity[name="Pattern"] {

}

entity[name="CodeSmell"] {

}

entity[name="Mutation"] {

}

entity[name="DataFlow"] {

}

interface[type="cli"] {
  framework: argparse;
}
interface[type="cli"] page[name="code2llm"] {

}

workflow[name="install"] {
  trigger: "manual";
  step-1: run cmd=$(PYTHON) -m pip install -e .;
  step-2: run cmd=echo "✓ code2llm installed with TOON format support";
}

workflow[name="dev-install"] {
  trigger: "manual";
  step-1: run cmd=$(PYTHON) -m pip install -e ".[dev]";
  step-2: run cmd=echo "✓ code2llm installed with dev dependencies";
}

workflow[name="test"] {
  trigger: "manual";
  step-1: run cmd=$(PYTHON) -m pytest tests/ -v --tb=short 2>/dev/null || echo "No tests yet - create tests/ directory";
}

workflow[name="test-cov"] {
  trigger: "manual";
  step-1: run cmd=$(PYTHON) -m pytest tests/ --cov=code2llm --cov-report=html --cov-report=term 2>/dev/null || echo "No tests yet";
}

workflow[name="test-toon"] {
  trigger: "manual";
  step-1: run cmd=echo "🎯 Testing TOON format...";
  step-2: run cmd=$(PYTHON) -m code2llm ./ -v -o ./test_toon -m hybrid -f toon;
  step-3: run cmd=$(PYTHON) validate_toon.py test_toon/analysis.toon;
  step-4: run cmd=echo "✓ TOON format test complete";
}

workflow[name="validate-toon"] {
  trigger: "manual";
  step-1: depend target=test-toon;
}

workflow[name="test-all-formats"] {
  trigger: "manual";
  step-1: run cmd=echo "📊 Testing all output formats...";
  step-2: run cmd=$(PYTHON) -m code2llm ./ -v -o ./test_all -m hybrid -f all;
  step-3: run cmd=$(PYTHON) validate_toon.py test_all/analysis.toon;
  step-4: run cmd=echo "✓ All formats test complete";
}

workflow[name="test-comprehensive"] {
  trigger: "manual";
  step-1: run cmd=echo "🚀 Running comprehensive test suite...";
  step-2: run cmd=bash project.sh;
  step-3: run cmd=echo "✓ Comprehensive tests complete";
}

workflow[name="lint"] {
  trigger: "manual";
  step-1: run cmd=$(PYTHON) -m flake8 code2llm/ --max-line-length=100 --ignore=E203,W503 2>/dev/null || echo "flake8 not installed";
  step-2: run cmd=$(PYTHON) -m black --check code2llm/ 2>/dev/null || echo "black not installed";
  step-3: run cmd=echo "✓ Linting complete";
}

workflow[name="format"] {
  trigger: "manual";
  step-1: run cmd=$(PYTHON) -m black code2llm/ --line-length=100 2>/dev/null || echo "black not installed, run: pip install black";
  step-2: run cmd=echo "✓ Code formatted";
}

workflow[name="typecheck"] {
  trigger: "manual";
  step-1: run cmd=$(PYTHON) -m mypy code2llm/ --ignore-missing-imports 2>/dev/null || echo "mypy not installed";
}

workflow[name="check"] {
  trigger: "manual";
  step-1: run cmd=echo "✓ All checks passed";
}

workflow[name="run"] {
  trigger: "manual";
  step-1: run cmd=$(PYTHON) -m code2llm ../python/stts_core -v -o ./output;
}

workflow[name="analyze"] {
  trigger: "manual";
  step-1: run cmd=echo "🎯 Running TOON format analysis on current project...";
  step-2: run cmd=$(PYTHON) -m code2llm ./ -v -o ./analysis -m hybrid -f toon;
  step-3: run cmd=$(PYTHON) validate_toon.py analysis/analysis.toon;
  step-4: run cmd=echo "✓ TOON analysis complete - check analysis/analysis.toon";
}

workflow[name="analyze-all"] {
  trigger: "manual";
  step-1: run cmd=echo "📊 Running analysis with all formats...";
  step-2: run cmd=$(PYTHON) -m code2llm ./ -v -o ./analysis_all -m hybrid -f all;
  step-3: run cmd=$(PYTHON) validate_toon.py analysis_all/analysis.toon;
  step-4: run cmd=echo "✓ All formats analysis complete - check analysis_all/";
}

workflow[name="toon-demo"] {
  trigger: "manual";
  step-1: run cmd=echo "🎯 Quick TOON format demo...";
  step-2: run cmd=$(PYTHON) -m code2llm ./ -v -o ./demo -m hybrid -f toon;
  step-3: run cmd=echo "📁 Generated: demo/analysis.toon";
  step-4: run cmd=echo "📊 Size: $$(du -h demo/analysis.toon | cut -f1)";
  step-5: run cmd=echo "🔍 Preview:";
  step-6: run cmd=head -20 demo/analysis.toon;
}

workflow[name="toon-compare"] {
  trigger: "manual";
  step-1: run cmd=echo "📊 Comparing TOON vs YAML formats...";
  step-2: run cmd=$(PYTHON) -m code2llm ./ -v -o ./compare -m hybrid -f toon,yaml;
  step-3: run cmd=echo "📁 Files generated:";
  step-4: run cmd=echo "  - TOON:  compare/analysis.toon  ($$(du -h compare/analysis.toon | cut -f1))";
  step-5: run cmd=echo "  - YAML:  compare/analysis.yaml  ($$(du -h compare/analysis.yaml | cut -f1))";
  step-6: run cmd=echo "  - Ratio: $$(echo "scale=1; $$(du -k compare/analysis.yaml | cut -f1) / $$(du -k compare/analysis.toon | cut -f1)" | bc)x smaller";
  step-7: run cmd=$(PYTHON) validate_toon.py compare/analysis.yaml compare/analysis.toon;
}

workflow[name="toon-validate"] {
  trigger: "manual";
  step-1: run cmd=echo "🔍 Validating TOON format structure...";
  step-2: run cmd=$(PYTHON) validate_toon.py analysis/analysis.toon 2>/dev/null || $(PYTHON) validate_toon.py test_toon/analysis.toon 2>/dev/null || echo "Run 'make test-toon' first";
}

workflow[name="build"] {
  trigger: "manual";
  step-1: run cmd=rm -rf build/ dist/ *.egg-info;
  step-2: run cmd=$(PYTHON) -m build;
  step-3: run cmd=echo "✓ Build complete - check dist/";
}

workflow[name="publish-test"] {
  trigger: "manual";
  step-1: run cmd=echo "🚀 Publishing to TestPyPI...";
  step-2: run cmd=$(PYTHON) -m venv publish-test-env;
  step-3: run cmd=publish-test-env/bin/pip install twine;
  step-4: run cmd=publish-test-env/bin/python -m twine upload --repository testpypi dist/*;
  step-5: run cmd=rm -rf publish-test-env;
  step-6: run cmd=echo "✓ Published to TestPyPI";
}

workflow[name="bump-patch"] {
  trigger: "manual";
  step-1: run cmd=echo "🔢 Bumping patch version...";
  step-2: run cmd=$(PYTHON) scripts/bump_version.py patch 2>/dev/null || echo "Create scripts/bump_version.py or edit pyproject.toml manually";
}

workflow[name="bump-minor"] {
  trigger: "manual";
  step-1: run cmd=echo "🔢 Bumping minor version...";
  step-2: run cmd=$(PYTHON) scripts/bump_version.py minor 2>/dev/null || echo "Create scripts/bump_version.py or edit pyproject.toml manually";
}

workflow[name="bump-major"] {
  trigger: "manual";
  step-1: run cmd=echo "🔢 Bumping major version...";
  step-2: run cmd=$(PYTHON) scripts/bump_version.py major 2>/dev/null || echo "Create scripts/bump_version.py or edit pyproject.toml manually";
}

workflow[name="publish"] {
  trigger: "manual";
  step-1: run cmd=echo "🚀 Publishing to PyPI...";
  step-2: run cmd=echo "🔢 Bumping patch version...";
  step-3: run cmd=$(MAKE) bump-patch;
  step-4: run cmd=echo "🔨 Rebuilding package with new version...";
  step-5: run cmd=$(MAKE) build;
  step-6: run cmd=echo "📦 Publishing to PyPI...";
  step-7: run cmd=$(PYTHON) -m venv publish-env;
  step-8: run cmd=publish-env/bin/pip install twine;
  step-9: run cmd=publish-env/bin/python -m twine upload dist/*;
  step-10: run cmd=rm -rf publish-env;
  step-11: run cmd=echo "✓ Published to PyPI";
}

workflow[name="mermaid-png"] {
  trigger: "manual";
  step-1: run cmd=$(PYTHON) mermaid_to_png.py --batch output output;
}

workflow[name="install-mermaid"] {
  trigger: "manual";
  step-1: run cmd=npm install -g @mermaid-js/mermaid-cli;
}

workflow[name="check-mermaid"] {
  trigger: "manual";
  step-1: run cmd=echo "Checking available Mermaid renderers...";
  step-2: run cmd=which mmdc > /dev/null && echo "✓ mmdc (mermaid-cli)" || echo "✗ mmdc (run: npm install -g @mermaid-js/mermaid-cli)";
  step-3: run cmd=which npx > /dev/null && echo "✓ npx (for @mermaid-js/mermaid-cli)" || echo "✗ npx (install Node.js)";
  step-4: run cmd=which puppeteer > /dev/null && echo "✓ puppeteer" || echo "✗ puppeteer (run: npm install -g puppeteer)";
}

workflow[name="clean"] {
  trigger: "manual";
  step-1: run cmd=rm -rf build/ dist/ *.egg-info;
  step-2: run cmd=rm -rf .pytest_cache .coverage htmlcov/;
  step-3: run cmd=rm -rf code2llm/__pycache__ code2llm/*/__pycache__;
  step-4: run cmd=rm -rf test_* demo compare analysis analysis_all output_* 2>/dev/null || true;
  step-5: run cmd=find . -name "*.pyc" -delete 2>/dev/null || true;
  step-6: run cmd=find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true;
  step-7: run cmd=echo "✓ Cleaned build artifacts and test outputs";
}

workflow[name="clean-png"] {
  trigger: "manual";
  step-1: run cmd=rm -f output/*.png;
  step-2: run cmd=echo "✓ Cleaned PNG files";
}

workflow[name="quickstart"] {
  trigger: "manual";
  step-1: run cmd=echo "🚀 Quick Start with code2llm TOON format:";
  step-2: run cmd=echo "";
  step-3: run cmd=echo "1. Install:        make install";
  step-4: run cmd=echo "2. Test TOON:      make test-toon";
  step-5: run cmd=echo "3. Analyze:        make analyze";
  step-6: run cmd=echo "4. Compare:        make toon-compare";
  step-7: run cmd=echo "5. All formats:    make test-all-formats";
  step-8: run cmd=echo "";
  step-9: run cmd=echo "📖 For more: make help";
}

workflow[name="health"] {
  trigger: "manual";
  step-1: run cmd=docker compose ps;
  step-2: run cmd=docker compose exec app echo "Health check passed";
}

workflow[name="import-makefile-hint"] {
  trigger: "manual";
  step-1: run cmd=echo 'Run: taskfile import Makefile to import existing targets.';
}

workflow[name="help"] {
  trigger: "manual";
  step-1: run cmd=echo "code2llm - Python Code Flow Analysis Tool with LLM Integration and TOON;
  step-2: run cmd=echo "";
  step-3: run cmd=echo \"\U0001F680 Installation:\; 
  step-4: run cmd=echo "  make install       - Install package";
  step-5: run cmd=echo "  make dev-install   - Install with development dependencies";
  step-6: run cmd=echo "";
  step-7: run cmd=echo \"\U0001F9EA Testing:\; 
  step-8: run cmd=echo "  make test          - Run test suite";
  step-9: run cmd=echo "  make test-toon     - Test TOON format only";
  step-10: run cmd=echo "  make validate-toon - Validate TOON format output";
  step-11: run cmd=echo "  make test-all-formats - Test all output formats";
  step-12: run cmd=echo "";
  step-13: run cmd=echo \"\U0001F527 Code Quality:\; 
  step-14: run cmd=echo "  make lint          - Run linters (flake8, black --check)";
  step-15: run cmd=echo "  make format        - Format code with black";
  step-16: run cmd=echo "  make typecheck     - Run mypy type checking";
  step-17: run cmd=echo "  make check         - Run all quality checks";
  step-18: run cmd=echo "";
  step-19: run cmd=echo \"\U0001F4CA Analysis:\; 
  step-20: run cmd=echo "  make analyze       - Run analysis on current project (TOON format)";
  step-21: run cmd=echo "  make run           - Run with example arguments";
  step-22: run cmd=echo "  make analyze-all   - Run analysis with all formats";
  step-23: run cmd=echo "";
  step-24: run cmd=echo \"\U0001F3AF TOON Format:\; 
  step-25: run cmd=echo "  make toon-demo     - Quick TOON format demo";
  step-26: run cmd=echo "  make toon-compare  - Compare TOON vs YAML formats";
  step-27: run cmd=echo "  make toon-validate - Validate TOON format structure";
  step-28: run cmd=echo "";
  step-29: run cmd=echo \"\U0001F4E6 Building & Release:\; 
  step-30: run cmd=echo "  make build         - Build distribution packages";
  step-31: run cmd=echo "  make publish       - Publish to PyPI (with version bump)";
  step-32: run cmd=echo "  make publish-test  - Publish to TestPyPI";
  step-33: run cmd=echo "  make bump-patch    - Bump patch version";
  step-34: run cmd=echo "  make bump-minor    - Bump minor version";
  step-35: run cmd=echo "  make bump-major    - Bump major version";
  step-36: run cmd=echo "";
  step-37: run cmd=echo \"\U0001F3A8 Visualization:\; 
  step-38: run cmd=echo "  make mermaid-png   - Generate PNG from all Mermaid files";
  step-39: run cmd=echo "  make install-mermaid - Install Mermaid CLI renderer";
  step-40: run cmd=echo "  make check-mermaid - Check available Mermaid renderers";
  step-41: run cmd=echo "";
  step-42: run cmd=echo \"\U0001F9F9 Maintenance:\; 
  step-43: run cmd=echo "  make clean         - Remove build artifacts";
  step-44: run cmd=echo "  make clean-png     - Clean PNG files";
  step-45: run cmd=echo "";
}

deploy {
  target: makefile;
}

environment[name="local"] {
  runtime: makefile;
  env_file: ".env";
}

workflow[name="all"] {
  trigger: "manual";
  step-1: run cmd=taskfile run install;
  step-2: run cmd=taskfile run lint;
  step-3: run cmd=taskfile run test;
}

workflow[name="fmt"] {
  trigger: "manual";
  step-1: run cmd=ruff format .;
}

/* auto-added stub: define where entities are persisted */
database[name="default"] {
  engine: "sqlite";
  path: "data/app.db";
}
```

### Source Modules

- `code2llm.api`
- `code2llm.cli`
- `code2llm.cli_analysis`
- `code2llm.cli_commands`
- `code2llm.cli_parser`

## Quality Pipeline (`pyqual.yaml`)

```yaml markpact:pyqual path=pyqual.yaml
pipeline:
  name: code2llm-quality

  metrics:
    cc_max: 15
    critical_max: 0

  custom_tools:
    - name: code2llm_code2llm
      binary: code2llm
      command: >-
        code2llm {workdir} -f toon -o ./project --no-chunk
        --exclude .git .venv .venv_test build dist __pycache__ .pytest_cache .code2llm_cache .benchmarks .mypy_cache .ruff_cache node_modules
      output: ""
      allow_failure: false

    - name: vallm_code2llm
      binary: vallm
      command: >-
        vallm batch {workdir} --recursive --format toon --output ./project
        --exclude .git,.venv,.venv_test,build,dist,__pycache__,.pytest_cache,.code2llm_cache,.benchmarks,.mypy_cache,.ruff_cache,node_modules
      output: ""
      allow_failure: false

  stages:
    - name: analyze
      tool: code2llm_code2llm
      optional: true
      timeout: 0

    - name: validate
      tool: vallm_code2llm
      optional: true
      timeout: 0

    - name: lint
      tool: ruff
      optional: true

    - name: fix
      tool: prefact
      optional: true
      when: metrics_fail
      timeout: 900

    - name: test
      run: python3 -m pytest -q
      when: always

  loop:
    max_iterations: 3
    on_fail: report

  env:
    LLM_MODEL: openrouter/qwen/qwen3-coder-next
```

## Dependencies

### Runtime

```text markpact:deps python
networkx>=2.6
matplotlib>=3.4
pyyaml>=5.4
numpy>=1.20
jinja2>=3.0
radon>=5.1
astroid>=3.0
code2logic
vulture>=2.10
tiktoken>=0.5
tree-sitter>=0.21
tree-sitter-python>=0.21
tree-sitter-javascript>=0.21
tree-sitter-typescript>=0.21
tree-sitter-go>=0.21
tree-sitter-rust>=0.21
tree-sitter-java>=0.21
tree-sitter-c>=0.21
tree-sitter-cpp>=0.22
tree-sitter-c-sharp>=0.21
tree-sitter-php>=0.22
tree-sitter-ruby>=0.21
```

### Development

```text markpact:deps python scope=dev
pytest>=6.2
pytest-cov>=2.12
pytest-xdist>=3.0
black>=21.0
flake8>=3.9
mypy>=0.910
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
```

## Source Map

*Top 5 modules by symbol density — signatures for LLM orientation.*

### `code2llm.cli_commands` (`code2llm/cli_commands.py`)

```python
def handle_special_commands()  # CC=7, fan=4
def handle_report_command(args_list)  # CC=4, fan=9
def validate_and_setup(args)  # CC=3, fan=5
def print_start_info(args, source_path, output_dir)  # CC=2, fan=1
def validate_chunked_output(output_dir, args)  # CC=3, fan=6
def _get_chunk_dirs(output_dir)  # CC=3, fan=2
def _validate_chunks(chunk_dirs, required_files)  # CC=3, fan=7
def _validate_single_chunk(chunk_dir, required_files)  # CC=4, fan=3
def _get_file_sizes(chunk_dir, required_files)  # CC=3, fan=3
def _print_chunk_errors(chunk_name, chunk_issues)  # CC=2, fan=1
def _print_validation_summary(chunk_dirs, valid_chunks, issues)  # CC=3, fan=2
def generate_llm_context(args_list)  # CC=3, fan=12
```

### `code2llm.cli_analysis` (`code2llm/cli_analysis.py`)

```python
def _run_analysis(args, source_path, output_dir)  # CC=5, fan=4
def _run_standard_analysis(args, source_path, output_dir)  # CC=5, fan=8
def _build_config(args, output_dir)  # CC=8, fan=8
def _print_analysis_summary(result)  # CC=1, fan=2
def _run_chunked_analysis(args, source_path, output_dir)  # CC=3, fan=8
def _print_chunked_plan(subprojects)  # CC=4, fan=5
def _filter_subprojects(args, subprojects)  # CC=10, fan=4 ⚠
def _analyze_all_subprojects(args, subprojects, output_dir)  # CC=4, fan=8
def _analyze_subproject(args, subproject, output_dir)  # CC=14, fan=16 ⚠
def _merge_chunked_results(all_results, source_path)  # CC=9, fan=5
def _run_streaming_analysis(args, config, source_path)  # CC=7, fan=9
```

### `code2llm.api` (`code2llm/api.py`)

```python
def analyze(project_path, config)  # CC=2, fan=2
def analyze_file(file_path, config)  # CC=1, fan=4
```

### `code2llm.cli_parser` (`code2llm/cli_parser.py`)

```python
def get_version()  # CC=2, fan=5
def create_parser()  # CC=1, fan=5
```

### `code2llm.cli` (`code2llm/cli.py`)

```python
def main()  # CC=7, fan=9
```

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/code2llm
# nodes: 357 | edges: 383 | modules: 66
# CC̄=4.1

HUBS[20]:
  code2llm.generators.llm_task.normalize_llm_task
    CC=14  in:1  out:43  total:44
  code2llm.generators.llm_flow.render_llm_flow_md
    CC=10  in:1  out:42  total:43
  code2llm.cli_parser.create_parser
    CC=1  in:1  out:40  total:41
  benchmarks.benchmark_performance.main
    CC=1  in:0  out:41  total:41
  validate_toon.analyze_class_differences
    CC=6  in:1  out:39  total:40
  code2llm.generators.llm_flow._summarize_functions
    CC=14  in:1  out:35  total:36
  benchmarks.benchmark_evolution.run_benchmark
    CC=9  in:0  out:34  total:34
  code2llm.core.lang.rust.analyze_rust
    CC=9  in:1  out:31  total:32
  code2llm.core.lang.base._extract_declarations
    CC=9  in:4  out:28  total:32
  benchmarks.benchmark_optimizations.benchmark_cold_vs_warm
    CC=7  in:1  out:30  total:31
  benchmarks.benchmark_performance.create_test_project
    CC=5  in:1  out:29  total:30
  code2llm.core.toon_size_manager._split_by_modules
    CC=10  in:1  out:27  total:28
  code2llm.cli_exports.formats._export_mermaid
    CC=6  in:1  out:27  total:28
  code2llm.cli_exports.formats._export_simple_formats
    CC=13  in:3  out:24  total:27
  code2llm.core.lang.go_lang._analyze_go_regex
    CC=10  in:1  out:26  total:27
  validate_toon.compare_modules
    CC=5  in:1  out:26  total:27
  code2llm.exporters.toon.metrics.MetricsComputer._compute_file_metrics
    CC=12  in:0  out:25  total:25
  validate_toon.compare_functions
    CC=6  in:1  out:24  total:25
  code2llm.exporters.project_yaml.core.ProjectYAMLExporter._build_project_yaml
    CC=12  in:0  out:25  total:25
  code2llm.generators.mermaid.generate_single_png
    CC=13  in:1  out:24  total:25

MODULES:
  benchmarks.benchmark_evolution  [3 funcs]
    load_previous  CC=3  out:3
    run_benchmark  CC=9  out:34
    save_current  CC=1  out:3
  benchmarks.benchmark_format_quality  [3 funcs]
    _print_benchmark_header  CC=1  out:4
    _print_ground_truth_info  CC=1  out:7
    run_benchmark  CC=2  out:22
  benchmarks.benchmark_optimizations  [5 funcs]
    benchmark_cold_vs_warm  CC=7  out:30
    clear_caches  CC=3  out:7
    main  CC=3  out:13
    print_summary  CC=1  out:18
    run_analysis  CC=1  out:7
  benchmarks.benchmark_performance  [2 funcs]
    create_test_project  CC=5  out:29
    main  CC=1  out:41
  benchmarks.format_evaluator  [5 funcs]
    _check_structural_features  CC=1  out:16
    _detect_hub_types  CC=2  out:2
    _detect_pipelines  CC=5  out:5
    _detect_problems  CC=1  out:16
    evaluate_format  CC=4  out:22
  benchmarks.project_generator  [6 funcs]
    add_validator_to_core  CC=1  out:3
    create_core_py  CC=1  out:2
    create_etl_py  CC=1  out:2
    create_ground_truth_project  CC=1  out:6
    create_utils_py  CC=1  out:2
    create_validation_py  CC=1  out:2
  benchmarks.reporting  [8 funcs]
    _print_gap_analysis  CC=6  out:9
    _print_header  CC=1  out:3
    _print_pipelines_detail  CC=5  out:11
    _print_problems_detail  CC=5  out:13
    _print_scores_table  CC=3  out:7
    _print_structural_features  CC=5  out:11
    build_report  CC=3  out:8
    print_results  CC=1  out:6
  code2llm.analysis.data_analysis  [3 funcs]
    _find_data_pipelines  CC=7  out:7
    _categorize_functions  CC=8  out:8
    _make_stage  CC=2  out:0
  code2llm.analysis.side_effects  [2 funcs]
    __init__  CC=2  out:1
    analyze_function  CC=3  out:6
  code2llm.analysis.type_inference  [2 funcs]
    __init__  CC=2  out:1
    enrich_function  CC=3  out:4
  code2llm.analysis.utils.ast_helpers  [2 funcs]
    find_function_node  CC=8  out:4
    get_ast  CC=2  out:2
  code2llm.api  [2 funcs]
    analyze  CC=2  out:2
    analyze_file  CC=1  out:4
  code2llm.cli  [1 funcs]
    main  CC=7  out:11
  code2llm.cli_analysis  [11 funcs]
    _analyze_all_subprojects  CC=4  out:8
    _analyze_subproject  CC=14  out:19
    _build_config  CC=8  out:9
    _filter_subprojects  CC=10  out:5
    _merge_chunked_results  CC=9  out:7
    _print_analysis_summary  CC=1  out:9
    _print_chunked_plan  CC=4  out:9
    _run_analysis  CC=5  out:4
    _run_chunked_analysis  CC=3  out:13
    _run_standard_analysis  CC=5  out:8
  code2llm.cli_commands  [12 funcs]
    _get_chunk_dirs  CC=3  out:2
    _get_file_sizes  CC=3  out:3
    _print_chunk_errors  CC=2  out:2
    _print_validation_summary  CC=3  out:12
    _validate_chunks  CC=3  out:11
    _validate_single_chunk  CC=4  out:4
    generate_llm_context  CC=3  out:21
    handle_report_command  CC=4  out:17
    handle_special_commands  CC=7  out:6
    print_start_info  CC=2  out:3
  code2llm.cli_exports.code2logic  [8 funcs]
    _build_code2logic_cmd  CC=2  out:3
    _check_code2logic_installed  CC=2  out:4
    _export_code2logic  CC=6  out:13
    _find_code2logic_output  CC=6  out:6
    _handle_code2logic_error  CC=6  out:7
    _normalize_code2logic_output  CC=2  out:4
    _run_code2logic  CC=3  out:4
    _should_run_code2logic  CC=2  out:0
  code2llm.cli_exports.formats  [14 funcs]
    _export_calls  CC=2  out:4
    _export_calls_toon  CC=2  out:4
    _export_context_fallback  CC=4  out:4
    _export_data_structures  CC=3  out:4
    _export_evolution  CC=6  out:8
    _export_index_html  CC=5  out:4
    _export_mermaid  CC=6  out:27
    _export_mermaid_pngs  CC=11  out:11
    _export_project_toon  CC=2  out:8
    _export_project_yaml  CC=2  out:5
  code2llm.cli_exports.orchestrator  [5 funcs]
    _export_chunked_results  CC=6  out:10
    _export_single_project  CC=9  out:14
    _get_filtered_subprojects  CC=11  out:7
    _process_subproject_result  CC=5  out:5
    _run_exports  CC=7  out:7
  code2llm.cli_exports.prompt  [18 funcs]
    _analyze_generated_files  CC=14  out:11
    _build_dynamic_focus_areas  CC=9  out:17
    _build_dynamic_tasks  CC=8  out:16
    _build_main_files_section  CC=1  out:1
    _build_missing_files_section  CC=6  out:5
    _build_optional_files_section  CC=2  out:1
    _build_priority_order  CC=9  out:21
    _build_prompt_file_lines  CC=4  out:5
    _build_prompt_footer  CC=5  out:7
    _build_prompt_header  CC=1  out:0
  code2llm.cli_parser  [1 funcs]
    create_parser  CC=1  out:40
  code2llm.core.ast_registry  [1 funcs]
    get_global  CC=2  out:1
  code2llm.core.file_analyzer  [1 funcs]
    _route_to_language_analyzer  CC=10  out:10
  code2llm.core.file_filter  [1 funcs]
    __init__  CC=9  out:13
  code2llm.core.gitignore  [1 funcs]
    load_gitignore_patterns  CC=3  out:4
  code2llm.core.incremental  [3 funcs]
    needs_analysis  CC=2  out:5
    update  CC=1  out:2
    _file_signature  CC=2  out:1
  code2llm.core.lang.base  [10 funcs]
    _extract_declarations  CC=9  out:28
    _match_method_name  CC=14  out:9
    _process_class_method  CC=2  out:7
    _process_functions  CC=9  out:2
    _process_standalone_function  CC=10  out:11
    _resolve_call  CC=7  out:7
    analyze_c_family  CC=5  out:6
    calculate_complexity_regex  CC=6  out:5
    extract_calls_regex  CC=9  out:11
    extract_function_body  CC=10  out:4
  code2llm.core.lang.cpp  [1 funcs]
    analyze_cpp  CC=1  out:1
  code2llm.core.lang.csharp  [1 funcs]
    analyze_csharp  CC=1  out:1
  code2llm.core.lang.generic  [1 funcs]
    analyze_generic  CC=12  out:20
  code2llm.core.lang.go_lang  [2 funcs]
    _analyze_go_regex  CC=10  out:26
    analyze_go  CC=4  out:6
  code2llm.core.lang.java  [1 funcs]
    analyze_java  CC=1  out:1
  code2llm.core.lang.php  [4 funcs]
    _adjust_qualified_names  CC=3  out:6
    _extract_php_traits  CC=4  out:8
    _parse_php_metadata  CC=8  out:9
    analyze_php  CC=2  out:10
  code2llm.core.lang.ruby  [2 funcs]
    _adjust_ruby_module_qualnames  CC=4  out:10
    analyze_ruby  CC=14  out:19
  code2llm.core.lang.rust  [1 funcs]
    analyze_rust  CC=9  out:31
  code2llm.core.lang.ts_extractors  [5 funcs]
    _extract_classes_ts  CC=1  out:6
    _extract_functions_ts  CC=1  out:9
    _find_name_node  CC=7  out:0
    _get_node_text  CC=1  out:1
    extract_declarations_ts  CC=1  out:5
  code2llm.core.lang.ts_parser  [9 funcs]
    __init__  CC=1  out:1
    parse  CC=3  out:3
    supports  CC=2  out:1
    _get_language  CC=7  out:6
    _get_parser  CC=4  out:3
    _init_tree_sitter  CC=2  out:1
    get_parser  CC=2  out:1
    is_available  CC=1  out:1
    parse_source  CC=1  out:3
  code2llm.core.lang.typescript  [3 funcs]
    analyze_typescript_js  CC=1  out:5
    get_typescript_lang_config  CC=1  out:0
    get_typescript_patterns  CC=1  out:8
  code2llm.core.large_repo  [15 funcs]
    _calculate_priority  CC=1  out:1
    _categorize_subdirs  CC=7  out:10
    _collect_files_in_dir  CC=1  out:1
    _collect_files_recursive  CC=1  out:1
    _collect_root_files  CC=1  out:1
    _contains_python_files  CC=1  out:1
    _count_py_files  CC=1  out:1
    _get_level1_dirs  CC=1  out:1
    _merge_small_l1_dirs  CC=7  out:19
    _process_level1_files  CC=5  out:13
  code2llm.core.repo_files  [8 funcs]
    _get_gitignore_parser  CC=2  out:2
    calculate_priority  CC=7  out:1
    collect_files_in_dir  CC=6  out:10
    collect_root_files  CC=3  out:5
    contains_python_files  CC=3  out:4
    count_py_files  CC=3  out:4
    get_level1_dirs  CC=8  out:9
    should_skip_file  CC=7  out:4
  code2llm.core.toon_size_manager  [8 funcs]
    _parse_modules  CC=6  out:7
    _split_by_lines  CC=8  out:20
    _split_by_modules  CC=10  out:27
    _write_chunk  CC=2  out:1
    get_file_size_kb  CC=1  out:1
    manage_toon_size  CC=8  out:11
    should_split_toon  CC=1  out:1
    split_toon_file  CC=3  out:6
  code2llm.exporters.map_exporter  [4 funcs]
    _is_excluded  CC=6  out:4
    _load_evolution_trend  CC=5  out:2
    _read_previous_cc_avg  CC=6  out:6
    _rel_path  CC=6  out:9
  code2llm.exporters.mermaid_exporter  [3 funcs]
    export_flow_compact  CC=1  out:9
    export_flow_detailed  CC=1  out:13
    export_flow_full  CC=1  out:13
  code2llm.exporters.mermaid_flow_helpers  [12 funcs]
    _append_entry_styles  CC=3  out:3
    _append_flow_node  CC=4  out:6
    _classify_architecture_module  CC=4  out:3
    _entry_points  CC=3  out:2
    _filtered_functions  CC=4  out:4
    _group_architecture_functions  CC=2  out:3
    _group_functions_by_module  CC=2  out:4
    _render_architecture_view  CC=6  out:13
    _render_flow_edges  CC=10  out:9
    _render_flow_styles  CC=6  out:10
  code2llm.exporters.project_yaml.core  [3 funcs]
    _build_project_yaml  CC=12  out:25
    _detect_primary_language  CC=9  out:11
    export  CC=1  out:6
  code2llm.exporters.project_yaml.evolution  [2 funcs]
    build_evolution  CC=3  out:4
    load_previous_evolution  CC=6  out:5
  code2llm.exporters.project_yaml.health  [3 funcs]
    build_alerts  CC=13  out:11
    build_health  CC=7  out:13
    count_duplicates  CC=5  out:8
  code2llm.exporters.project_yaml.hotspots  [3 funcs]
    build_hotspots  CC=5  out:7
    build_refactoring  CC=13  out:20
    hotspot_note  CC=7  out:5
  code2llm.exporters.project_yaml.modules  [7 funcs]
    build_class_export  CC=11  out:10
    build_exports  CC=2  out:3
    build_function_exports  CC=7  out:6
    build_modules  CC=5  out:11
    compute_inbound_deps  CC=5  out:3
    compute_module_entry  CC=4  out:12
    group_by_file  CC=5  out:8
  code2llm.exporters.report_generators  [1 funcs]
    load_project_yaml  CC=3  out:4
  code2llm.exporters.toon.helpers  [6 funcs]
    _dup_file_set  CC=2  out:3
    _hotspot_description  CC=8  out:5
    _package_of  CC=2  out:2
    _package_of_module  CC=4  out:4
    _scan_line_counts  CC=6  out:9
    _traits_from_cfg  CC=7  out:7
  code2llm.exporters.toon.metrics  [16 funcs]
    _build_coupling_matrix  CC=8  out:6
    _build_function_to_module_map  CC=3  out:2
    _calculate_duplicate_info  CC=6  out:14
    _compute_class_metrics  CC=7  out:14
    _compute_fan_in  CC=3  out:6
    _compute_file_metrics  CC=12  out:25
    _compute_function_metrics  CC=8  out:14
    _compute_hotspots  CC=5  out:7
    _compute_package_metrics  CC=5  out:9
    _detect_duplicates  CC=4  out:5
  code2llm.exporters.toon.module_detail  [1 funcs]
    _render_module_detail  CC=3  out:10
  code2llm.exporters.toon.renderer  [2 funcs]
    _detect_language_label  CC=10  out:12
    render_layers  CC=2  out:8
  code2llm.exporters.validate_project  [2 funcs]
    _check_required_keys  CC=9  out:6
    validate_project_yaml  CC=11  out:17
  code2llm.generators.llm_flow  [19 funcs]
    _as_dict  CC=2  out:1
    _as_list  CC=2  out:1
    _collect_entrypoints  CC=5  out:6
    _collect_functions  CC=7  out:10
    _collect_nodes  CC=5  out:5
    _deduplicate_entrypoints  CC=5  out:4
    _extract_entrypoint_info  CC=4  out:6
    _group_nodes_by_file  CC=3  out:5
    _is_entrypoint_file  CC=2  out:2
    _node_counts_by_function  CC=4  out:4
  code2llm.generators.llm_task  [12 funcs]
    _apply_bullet_sections  CC=6  out:10
    _apply_simple_sections  CC=5  out:4
    _create_empty_task_data  CC=1  out:0
    _ensure_list  CC=3  out:1
    _parse_acceptance_tests  CC=3  out:4
    _parse_bullets  CC=4  out:5
    _parse_sections  CC=7  out:8
    _strip_bom  CC=2  out:1
    load_input  CC=6  out:11
    main  CC=4  out:13
  code2llm.generators.mermaid  [15 funcs]
    _check_bracket_balance  CC=7  out:8
    _check_node_ids  CC=12  out:12
    _fix_class_line  CC=6  out:11
    _fix_edge_label_pipes  CC=8  out:10
    _fix_edge_line  CC=5  out:9
    _fix_subgraph_line  CC=3  out:8
    _is_balanced_node_line  CC=6  out:0
    _sanitize_label_text  CC=1  out:9
    _sanitize_node_id  CC=3  out:3
    _scan_brackets  CC=10  out:6
  code2llm.nlp.entity_resolution  [1 funcs]
    resolve  CC=13  out:8
  code2llm.parsers.toon_parser  [6 funcs]
    _detect_section  CC=3  out:2
    _parse_header_line  CC=2  out:2
    _parse_stats_line  CC=5  out:5
    is_toon_file  CC=4  out:5
    load_toon  CC=2  out:4
    parse_toon_content  CC=8  out:9
  demo_langs.valid.sample  [12 funcs]
    AddUser  CC=1  out:2
    GetUser  CC=3  out:1
    NewUserService  CC=1  out:1
    User  CC=1  out:0
    getId  CC=1  out:0
    getName  CC=1  out:0
    addUser  CC=1  out:1
    getUser  CC=3  out:1
    main  CC=2  out:6
    processUsers  CC=2  out:2
  examples.litellm.run  [3 funcs]
    get_refactoring_advice  CC=2  out:5
    main  CC=1  out:17
    run_analysis  CC=4  out:8
  examples.streaming-analyzer.sample_project.main  [2 funcs]
    handle_get_request  CC=4  out:6
    process_request  CC=6  out:11
  examples.streaming-analyzer.sample_project.utils  [2 funcs]
    format_output  CC=3  out:5
    validate_input  CC=4  out:2
  scripts.benchmark_badges  [3 funcs]
    create_html  CC=4  out:3
    get_shield_url  CC=1  out:3
    main  CC=5  out:23
  scripts.bump_version  [7 funcs]
    bump_version  CC=4  out:5
    format_version  CC=1  out:0
    get_current_version  CC=3  out:9
    main  CC=3  out:11
    parse_version  CC=2  out:3
    update_pyproject_toml  CC=1  out:5
    update_version_file  CC=1  out:3
  validate_toon  [19 funcs]
    _compare_all_aspects  CC=1  out:5
    _print_comparison_summary  CC=5  out:5
    _run_comparison_mode  CC=7  out:12
    _run_single_file_mode  CC=6  out:12
    analyze_class_differences  CC=6  out:39
    compare_basic_stats  CC=4  out:11
    compare_classes  CC=1  out:19
    compare_functions  CC=6  out:24
    compare_modules  CC=5  out:26
    extract_classes_from_toon  CC=3  out:4

EDGES:
  examples.litellm.run.main → examples.litellm.run.run_analysis
  examples.litellm.run.main → examples.litellm.run.get_refactoring_advice
  validate_toon.load_file → code2llm.parsers.toon_parser.is_toon_file
  validate_toon.load_file → validate_toon.load_yaml
  validate_toon.load_file → code2llm.parsers.toon_parser.load_toon
  validate_toon.compare_functions → validate_toon.extract_functions_from_yaml
  validate_toon.compare_functions → validate_toon.extract_functions_from_toon
  validate_toon.compare_classes → validate_toon.extract_classes_from_yaml
  validate_toon.compare_classes → validate_toon.extract_classes_from_toon
  validate_toon.compare_classes → validate_toon.analyze_class_differences
  validate_toon.compare_modules → validate_toon.extract_modules_from_yaml
  validate_toon.compare_modules → validate_toon.extract_modules_from_toon
  validate_toon._run_single_file_mode → validate_toon.load_file
  validate_toon._run_single_file_mode → validate_toon.validate_toon_completeness
  validate_toon._run_comparison_mode → validate_toon.load_yaml
  validate_toon._run_comparison_mode → validate_toon.load_file
  validate_toon._run_comparison_mode → validate_toon._compare_all_aspects
  validate_toon._run_comparison_mode → validate_toon._print_comparison_summary
  validate_toon._compare_all_aspects → validate_toon.compare_basic_stats
  validate_toon._compare_all_aspects → validate_toon.compare_functions
  validate_toon._compare_all_aspects → validate_toon.compare_classes
  validate_toon._compare_all_aspects → validate_toon.compare_modules
  validate_toon._compare_all_aspects → validate_toon.validate_toon_completeness
  validate_toon.main → validate_toon._run_single_file_mode
  validate_toon.main → validate_toon._run_comparison_mode
  benchmarks.benchmark_evolution.run_benchmark → benchmarks.benchmark_evolution.load_previous
  benchmarks.benchmark_evolution.run_benchmark → benchmarks.benchmark_evolution.save_current
  benchmarks.reporting.print_results → benchmarks.reporting._print_header
  benchmarks.reporting.print_results → benchmarks.reporting._print_scores_table
  benchmarks.reporting.print_results → benchmarks.reporting._print_problems_detail
  benchmarks.reporting.print_results → benchmarks.reporting._print_pipelines_detail
  benchmarks.reporting.print_results → benchmarks.reporting._print_structural_features
  benchmarks.reporting.print_results → benchmarks.reporting._print_gap_analysis
  examples.streaming-analyzer.sample_project.main.Application.process_request → examples.streaming-analyzer.sample_project.utils.validate_input
  examples.streaming-analyzer.sample_project.main.Application.handle_get_request → examples.streaming-analyzer.sample_project.utils.format_output
  benchmarks.format_evaluator.evaluate_format → benchmarks.format_evaluator._detect_problems
  benchmarks.format_evaluator.evaluate_format → benchmarks.format_evaluator._detect_pipelines
  benchmarks.format_evaluator.evaluate_format → benchmarks.format_evaluator._detect_hub_types
  benchmarks.format_evaluator.evaluate_format → benchmarks.format_evaluator._check_structural_features
  benchmarks.project_generator.create_ground_truth_project → benchmarks.project_generator.create_core_py
  benchmarks.project_generator.create_ground_truth_project → benchmarks.project_generator.create_etl_py
  benchmarks.project_generator.create_ground_truth_project → benchmarks.project_generator.create_validation_py
  benchmarks.project_generator.create_ground_truth_project → benchmarks.project_generator.create_utils_py
  benchmarks.project_generator.create_ground_truth_project → benchmarks.project_generator.add_validator_to_core
  benchmarks.benchmark_optimizations.clear_caches → code2llm.core.ast_registry.ASTRegistry.get_global
  benchmarks.benchmark_optimizations.benchmark_cold_vs_warm → benchmarks.benchmark_optimizations.clear_caches
  benchmarks.benchmark_optimizations.benchmark_cold_vs_warm → benchmarks.benchmark_optimizations.run_analysis
  benchmarks.benchmark_optimizations.main → benchmarks.benchmark_optimizations.benchmark_cold_vs_warm
  benchmarks.benchmark_optimizations.main → benchmarks.benchmark_optimizations.print_summary
  scripts.bump_version.bump_version → scripts.bump_version.get_current_version
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 144f 23470L | python:131,shell:9,typescript:1,java:1 | 2026-04-19
# CC̄=4.2 | critical:0/1078 | dups:1 | cycles:0

HEALTH[1]:
  🔴 DUP   1 class duplicated

REFACTOR[1]:
  1. rm duplicates  (-1 dup class)

PIPELINES[693]:
  [1] Src [NewUserService]: NewUserService
      PURITY: 100% pure
  [2] Src [AddUser]: AddUser
      PURITY: 100% pure
  [3] Src [GetUser]: GetUser
      PURITY: 100% pure
  [4] Src [ProcessUsers]: ProcessUsers
      PURITY: 100% pure
  [5] Src [main]: main
      PURITY: 100% pure

LAYERS:
  code2llm/                       CC̄=4.4    ←in:0  →out:5
  │ !! index_generator            790L  1C    7m  CC=5      ←0
  │ !! pipeline_detector          506L  3C   18m  CC=13     ←0
  │ !! html_dashboard             504L  1C   14m  CC=7      ←0
  │ !! metrics                    501L  1C   27m  CC=12     ←0
  │ readme_exporter            496L  1C    7m  CC=13     ←0
  │ large_repo                 488L  2C   20m  CC=9      ←1
  │ mermaid                    485L  0C   16m  CC=13     ←1
  │ mermaid_exporter           480L  1C   19m  CC=13     ←0
  │ prompt                     475L  0C   18m  CC=14     ←1
  │ llm_flow                   472L  1C   24m  CC=14     ←0
  │ evolution_exporter         471L  1C   17m  CC=11     ←0
  │ renderer                   471L  1C   26m  CC=11     ←0
  │ base                       454L  0C   14m  CC=14     ←8
  │ map_exporter               439L  1C   25m  CC=13     ←7
  │ file_analyzer              396L  1C   18m  CC=12     ←0
  │ flow_exporter              391L  1C   14m  CC=10     ←0
  │ pipeline                   388L  3C   20m  CC=10     ←0
  │ analyzer                   355L  1C    9m  CC=14     ←0
  │ entity_resolution          326L  3C   16m  CC=13     ←1
  │ yaml_exporter              326L  1C   24m  CC=8      ←0
  │ cli_analysis               323L  0C   11m  CC=14     ←1
  │ formats                    318L  0C   15m  CC=13     ←3
  │ cli_parser                 297L  0C    2m  CC=2      ←1
  │ intent_matching            297L  3C   15m  CC=7      ←0
  │ side_effects               294L  2C   15m  CC=14     ←0
  │ cfg                        293L  1C   17m  CC=5      ←0
  │ type_inference             290L  1C   17m  CC=9      ←0
  │ data_analysis              286L  1C   18m  CC=14     ←0
  │ llm_task                   284L  0C   15m  CC=14     ←0
  │ toon_size_manager          265L  0C    8m  CC=10     ←1
  │ mermaid_flow_helpers       262L  0C   12m  CC=10     ←1
  │ cli_commands               250L  0C   12m  CC=7      ←1
  │ context_exporter           248L  1C   15m  CC=10     ←0
  │ dfg                        224L  1C   12m  CC=7      ←0
  │ call_graph                 211L  1C   13m  CC=9      ←0
  │ config                     211L  6C    0m  CC=0.0    ←0
  │ scanner                    201L  1C    6m  CC=14     ←0
  │ refactoring                196L  1C   11m  CC=9      ←0
  │ __init__                   196L  1C   11m  CC=9      ←0
  │ models                     194L  11C    6m  CC=8      ←0
  │ smells                     192L  1C    9m  CC=7      ←0
  │ flow_renderer              188L  1C    6m  CC=14     ←0
  │ streaming_analyzer         181L  1C    6m  CC=12     ←0
  │ ts_extractors              180L  0C    5m  CC=7      ←2
  │ repo_files                 174L  0C    8m  CC=8      ←1
  │ config                     174L  5C    2m  CC=1      ←0
  │ detector                   168L  1C    8m  CC=9      ←0
  │ article_view               163L  1C    9m  CC=7      ←0
  │ module_detail              162L  1C    9m  CC=7      ←0
  │ orchestrator               160L  0C    5m  CC=11     ←1
  │ ts_parser                  158L  1C    9m  CC=7      ←2
  │ toon_view                  157L  1C    9m  CC=6      ←0
  │ export_pipeline            153L  2C    5m  CC=4      ←0
  │ modules                    151L  0C    7m  CC=11     ←1
  │ incremental                150L  1C   10m  CC=4      ←0
  │ prompt_engine              150L  1C    7m  CC=12     ←0
  │ toon_parser                147L  0C   10m  CC=8      ←1
  │ ruby                       143L  0C    3m  CC=14     ←1
  │ context_view               140L  1C    8m  CC=11     ←0
  │ gitignore                  138L  2C    7m  CC=7      ←2
  │ prioritizer                131L  2C    4m  CC=9      ←0
  │ code2logic                 127L  0C    8m  CC=6      ←1
  │ normalization              122L  2C   13m  CC=6      ←0
  │ helpers                    120L  0C    8m  CC=8      ←3
  │ validate_project           118L  0C    3m  CC=11     ←1
  │ core                       118L  1C    3m  CC=12     ←0
  │ hotspots                   106L  0C    3m  CC=13     ←1
  │ file_cache                 103L  1C    9m  CC=5      ←0
  │ health                     103L  0C    3m  CC=13     ←1
  │ ast_registry               102L  1C    9m  CC=5      ←4
  │ go_lang                    102L  0C    2m  CC=10     ←1
  │ file_filter                100L  1C    4m  CC=14     ←0
  │ rust                        94L  0C    1m  CC=9      ←1
  │ coupling                    77L  1C    5m  CC=7      ←0
  │ incremental                 75L  1C    5m  CC=5      ←0
  │ api                         73L  0C    2m  CC=2      ←0
  │ generic                     71L  0C    1m  CC=12     ←1
  │ cli                         69L  0C    1m  CC=7      ←0
  │ strategies                  68L  1C    0m  CC=0.0    ←0
  │ php                         66L  0C    4m  CC=8      ←1
  │ __init__                    55L  0C    0m  CC=0.0    ←0
  │ ast_helpers                 54L  0C    3m  CC=8      ←2
  │ __init__                    53L  0C    1m  CC=6      ←0
  │ typescript                  53L  0C    3m  CC=1      ←1
  │ __init__                    52L  0C    1m  CC=3      ←0
  │ cache                       51L  1C    5m  CC=4      ←0
  │ __init__                    48L  0C    0m  CC=0.0    ←0
  │ evolution                   46L  0C    2m  CC=6      ←2
  │ java                        43L  0C    1m  CC=1      ←1
  │ csharp                      42L  0C    1m  CC=1      ←1
  │ cpp                         35L  0C    1m  CC=1      ←1
  │ report_generators           34L  0C    1m  CC=3      ←1
  │ __init__                    33L  0C    1m  CC=2      ←0
  │ flow_constants              29L  0C    0m  CC=0.0    ←0
  │ __init__                    23L  0C    0m  CC=0.0    ←0
  │ json_exporter               17L  1C    1m  CC=3      ←0
  │ project_yaml_exporter       15L  0C    0m  CC=0.0    ←0
  │ __init__                    15L  0C    0m  CC=0.0    ←0
  │ constants                   15L  0C    0m  CC=0.0    ←0
  │ base                        13L  1C    1m  CC=1      ←0
  │ llm_exporter                12L  0C    0m  CC=0.0    ←0
  │ __init__                    12L  0C    0m  CC=0.0    ←0
  │ __init__                    11L  0C    0m  CC=0.0    ←0
  │ __init__                     7L  0C    0m  CC=0.0    ←0
  │ __main__                     6L  0C    0m  CC=0.0    ←0
  │ __init__                     5L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  scripts/                        CC̄=3.9    ←in:0  →out:0
  │ benchmark_badges           392L  0C    9m  CC=13     ←0
  │ bump_version                96L  0C    7m  CC=4      ←0
  │
  ./                              CC̄=3.6    ←in:0  →out:0
  │ validate_toon              390L  0C   19m  CC=7      ←0
  │ setup                       67L  0C    1m  CC=2      ←0
  │ orchestrator.sh             58L  0C    0m  CC=0.0    ←0
  │ project.sh                  49L  0C    0m  CC=0.0    ←0
  │ project2.sh                 35L  0C    0m  CC=0.0    ←0
  │
  benchmarks/                     CC̄=3.0    ←in:0  →out:1
  │ benchmark_performance      306L  0C    7m  CC=6      ←0
  │ project_generator          233L  0C    6m  CC=1      ←1
  │ reporting                  179L  0C    9m  CC=6      ←1
  │ benchmark_optimizations    157L  0C    5m  CC=7      ←0
  │ benchmark_format_quality   143L  0C    5m  CC=4      ←0
  │ format_evaluator           138L  1C    5m  CC=5      ←1
  │ benchmark_evolution        137L  0C    4m  CC=13     ←0
  │ benchmark_constants         29L  0C    0m  CC=0.0    ←0
  │
  badges/                         CC̄=2.7    ←in:0  →out:0
  │ server                     110L  0C    3m  CC=4      ←0
  │
  test_python_only/               CC̄=1.8    ←in:0  →out:0
  │ sample                      40L  2C    5m  CC=3      ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │
  demo_langs/                     CC̄=1.5    ←in:0  →out:0  ×DUP
  │ sample.java                 47L  2C    7m  CC=3      ←1  ×DUP
  │ sample.rs                   47L  1C    4m  CC=2      ←0
  │ sample.go                   46L  0C    4m  CC=3      ←0
  │ sample.php                  44L  1C    1m  CC=1      ←0
  │ sample                      40L  1C    5m  CC=3      ←0
  │ sample.ts                   26L  1C    1m  CC=1      ←0
  │
  test_langs/                     CC̄=1.4    ←in:0  →out:0  ×DUP
  │ sample.java                 47L  2C    7m  CC=3      ←3  ×DUP
  │ sample.rs                   47L  1C    4m  CC=2      ←0
  │ sample.go                   46L  0C    4m  CC=3      ←0
  │ sample.php                  44L  1C    1m  CC=1      ←0
  │ sample                      40L  2C    5m  CC=3      ←0
  │ sample.ts                   26L  1C    1m  CC=1      ←0
  │ sample_bad.go               24L  0C    2m  CC=1      ←0
  │ sample_bad.php              22L  1C    1m  CC=1      ←0
  │ sample_bad.ts               20L  2C    3m  CC=1      ←0
  │ sample_bad.java             18L  1C    1m  CC=1      ←0
  │ sample_bad.rs               18L  1C    2m  CC=1      ←0
  │
  ── zero ──
     code2llm/patterns/__init__.py             0L
     code2llm/refactor/__init__.py             0L

COUPLING:
                            code2llm.cli_exports           code2llm.core                code2llm      code2llm.exporters       code2llm.analysis        code2llm.parsers        test_langs.valid           validate_toon              benchmarks     code2llm.generators            code2llm.nlp        demo_langs.valid  test_python_only.valid
    code2llm.cli_exports                      ──                       1                      ←4                       4                                                                                                                                               1                                                                        
           code2llm.core                      ←1                      ──                      ←1                                              ←3                                                                                              ←1                                                                                                  hub
                code2llm                       4                       1                      ──                                                                                                                                                                                                                                                
      code2llm.exporters                      ←4                                                                      ──                                                                                                                                                                       1                                                
       code2llm.analysis                                               3                                                                      ──                                                                                                                                                                                                
        code2llm.parsers                                                                                                                                              ──                                              ←2                                                                                                                        
        test_langs.valid                                                                                                                                                                      ──                                                                                                                      ←1                      ←1
           validate_toon                                                                                                                                               2                                              ──                                                                                                                        
              benchmarks                                               1                                                                                                                                                                      ──                                                                                                
     code2llm.generators                      ←1                                                                                                                                                                                                                      ──                                                                        
            code2llm.nlp                                                                                              ←1                                                                                                                                                                      ──                                                
        demo_langs.valid                                                                                                                                                                       1                                                                                                                      ──                        
  test_python_only.valid                                                                                                                                                                       1                                                                                                                                              ──
  CYCLES: none
  HUB: code2llm.core/ (fan-in=6)

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 12 groups | 133f 24336L | 2026-04-19

SUMMARY:
  files_scanned: 133
  total_lines:   24336
  dup_groups:    12
  dup_fragments: 29
  saved_lines:   369
  scan_ms:       5385

HOTSPOTS[7] (files with most duplication):
  benchmarks/project_generator.py  dup=187L  groups=1  frags=4  (0.8%)
  validate_toon.py  dup=40L  groups=2  frags=4  (0.2%)
  code2llm/cli_exports/formats.py  dup=22L  groups=1  frags=2  (0.1%)
  code2llm/analysis/call_graph.py  dup=18L  groups=3  frags=3  (0.1%)
  code2llm/analysis/cfg.py  dup=18L  groups=3  frags=3  (0.1%)
  code2llm/exporters/flow_exporter.py  dup=10L  groups=1  frags=1  (0.0%)
  code2llm/exporters/map_exporter.py  dup=10L  groups=1  frags=1  (0.0%)

DUPLICATES[12] (ranked by impact):
  [362da81ebf98419f] !! STRU  create_core_py  L=88 N=4 saved=264 sim=1.00
      benchmarks/project_generator.py:11-98  (create_core_py)
      benchmarks/project_generator.py:101-130  (create_etl_py)
      benchmarks/project_generator.py:133-173  (create_validation_py)
      benchmarks/project_generator.py:176-203  (create_utils_py)
  [cda17a98c0c13954]   STRU  _expr_to_str  L=8 N=3 saved=16 sim=1.00
      code2llm/analysis/call_graph.py:204-211  (_expr_to_str)
      code2llm/analysis/cfg.py:277-284  (_expr_to_str)
      code2llm/analysis/dfg.py:209-216  (_expr_to_str)
  [710a483fb398e4ca]   STRU  analyze_cpp  L=7 N=3 saved=14 sim=1.00
      code2llm/core/lang/cpp.py:29-35  (analyze_cpp)
      code2llm/core/lang/csharp.py:36-42  (analyze_csharp)
      code2llm/core/lang/java.py:37-43  (analyze_java)
  [4910811602b5abf2]   STRU  _export_calls  L=13 N=2 saved=13 sim=1.00
      code2llm/cli_exports/formats.py:218-230  (_export_calls)
      code2llm/cli_exports/formats.py:233-241  (_export_calls_toon)
  [702f10bd42911198]   STRU  extract_functions_from_toon  L=11 N=2 saved=11 sim=1.00
      validate_toon.py:42-52  (extract_functions_from_toon)
      validate_toon.py:64-74  (extract_classes_from_toon)
  [422d78dbe06f5996]   EXAC  generate  L=5 N=3 saved=10 sim=1.00
      code2llm/exporters/article_view.py:14-18  (generate)
      code2llm/exporters/context_view.py:13-17  (generate)
      code2llm/exporters/toon_view.py:27-31  (generate)
  [bcb3f9f38c88d7ef]   EXAC  _is_excluded  L=10 N=2 saved=10 sim=1.00
      code2llm/exporters/flow_exporter.py:382-391  (_is_excluded)
      code2llm/exporters/map_exporter.py:314-323  (_is_excluded)
  [e359910cdf520aea]   STRU  extract_classes_from_yaml  L=9 N=2 saved=9 sim=1.00
      validate_toon.py:54-62  (extract_classes_from_yaml)
      validate_toon.py:120-128  (extract_modules_from_yaml)
  [9e673b6a7113c738]   EXAC  dump_yaml  L=8 N=2 saved=8 sim=1.00
      code2llm/generators/llm_flow.py:405-412  (dump_yaml)
      code2llm/generators/llm_task.py:233-240  (dump_yaml)
  [8ce608e75583dc78]   EXAC  _qualified_name  L=7 N=2 saved=7 sim=1.00
      code2llm/analysis/call_graph.py:141-147  (_qualified_name)
      code2llm/analysis/cfg.py:262-268  (_qualified_name)
  [54d9f117655e9665]   EXAC  _get_cache_key  L=4 N=2 saved=4 sim=1.00
      code2llm/core/file_cache.py:28-31  (_get_cache_key)
      code2llm/core/streaming/cache.py:19-22  (_get_cache_key)
  [c427db29782c2b80]   EXAC  visit_AsyncFunctionDef  L=3 N=2 saved=3 sim=1.00
      code2llm/analysis/call_graph.py:108-110  (visit_AsyncFunctionDef)
      code2llm/analysis/cfg.py:106-108  (visit_AsyncFunctionDef)

REFACTOR[12] (ranked by priority):
  [1] ○ extract_module     → benchmarks/utils/create_core_py.py
      WHY: 4 occurrences of 88-line block across 1 files — saves 264 lines
      FILES: benchmarks/project_generator.py
  [2] ○ extract_function   → code2llm/analysis/utils/_expr_to_str.py
      WHY: 3 occurrences of 8-line block across 3 files — saves 16 lines
      FILES: code2llm/analysis/call_graph.py, code2llm/analysis/cfg.py, code2llm/analysis/dfg.py
  [3] ○ extract_function   → code2llm/core/lang/utils/analyze_cpp.py
      WHY: 3 occurrences of 7-line block across 3 files — saves 14 lines
      FILES: code2llm/core/lang/cpp.py, code2llm/core/lang/csharp.py, code2llm/core/lang/java.py
  [4] ○ extract_function   → code2llm/cli_exports/utils/_export_calls.py
      WHY: 2 occurrences of 13-line block across 1 files — saves 13 lines
      FILES: code2llm/cli_exports/formats.py
  [5] ○ extract_function   → utils/extract_functions_from_toon.py
      WHY: 2 occurrences of 11-line block across 1 files — saves 11 lines
      FILES: validate_toon.py
  [6] ○ extract_function   → code2llm/exporters/utils/generate.py
      WHY: 3 occurrences of 5-line block across 3 files — saves 10 lines
      FILES: code2llm/exporters/article_view.py, code2llm/exporters/context_view.py, code2llm/exporters/toon_view.py
  [7] ○ extract_function   → code2llm/exporters/utils/_is_excluded.py
      WHY: 2 occurrences of 10-line block across 2 files — saves 10 lines
      FILES: code2llm/exporters/flow_exporter.py, code2llm/exporters/map_exporter.py
  [8] ○ extract_function   → utils/extract_classes_from_yaml.py
      WHY: 2 occurrences of 9-line block across 1 files — saves 9 lines
      FILES: validate_toon.py
  [9] ○ extract_function   → code2llm/generators/utils/dump_yaml.py
      WHY: 2 occurrences of 8-line block across 2 files — saves 8 lines
      FILES: code2llm/generators/llm_flow.py, code2llm/generators/llm_task.py
  [10] ○ extract_function   → code2llm/analysis/utils/_qualified_name.py
      WHY: 2 occurrences of 7-line block across 2 files — saves 7 lines
      FILES: code2llm/analysis/call_graph.py, code2llm/analysis/cfg.py
  [11] ○ extract_function   → code2llm/core/utils/_get_cache_key.py
      WHY: 2 occurrences of 4-line block across 2 files — saves 4 lines
      FILES: code2llm/core/file_cache.py, code2llm/core/streaming/cache.py
  [12] ○ extract_function   → code2llm/analysis/utils/visit_AsyncFunctionDef.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: code2llm/analysis/call_graph.py, code2llm/analysis/cfg.py

QUICK_WINS[10] (low risk, high savings — do first):
  [1] extract_module     saved=264L  → benchmarks/utils/create_core_py.py
      FILES: project_generator.py
  [2] extract_function   saved=16L  → code2llm/analysis/utils/_expr_to_str.py
      FILES: call_graph.py, cfg.py, dfg.py
  [3] extract_function   saved=14L  → code2llm/core/lang/utils/analyze_cpp.py
      FILES: cpp.py, csharp.py, java.py
  [4] extract_function   saved=13L  → code2llm/cli_exports/utils/_export_calls.py
      FILES: formats.py
  [5] extract_function   saved=11L  → utils/extract_functions_from_toon.py
      FILES: validate_toon.py
  [6] extract_function   saved=10L  → code2llm/exporters/utils/generate.py
      FILES: article_view.py, context_view.py, toon_view.py
  [7] extract_function   saved=10L  → code2llm/exporters/utils/_is_excluded.py
      FILES: flow_exporter.py, map_exporter.py
  [8] extract_function   saved=9L  → utils/extract_classes_from_yaml.py
      FILES: validate_toon.py
  [9] extract_function   saved=8L  → code2llm/generators/utils/dump_yaml.py
      FILES: llm_flow.py, llm_task.py
  [10] extract_function   saved=7L  → code2llm/analysis/utils/_qualified_name.py
      FILES: call_graph.py, cfg.py

EFFORT_ESTIMATE (total ≈ 16.7h):
  hard   create_core_py                      saved=264L  ~792min
  medium _expr_to_str                        saved=16L  ~32min
  easy   analyze_cpp                         saved=14L  ~28min
  easy   _export_calls                       saved=13L  ~26min
  easy   extract_functions_from_toon         saved=11L  ~22min
  easy   generate                            saved=10L  ~20min
  easy   _is_excluded                        saved=10L  ~20min
  easy   extract_classes_from_yaml           saved=9L  ~18min
  easy   dump_yaml                           saved=8L  ~16min
  easy   _qualified_name                     saved=7L  ~14min
  ... +2 more (~14min)

METRICS-TARGET:
  dup_groups:  12 → 0
  saved_lines: 369 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 859 func | 94f | 2026-04-19

NEXT[3] (ranked by impact):
  [1] !! SPLIT           code2llm/analysis/pipeline_detector.py
      WHY: 506L, 3 classes, max CC=13
      EFFORT: ~4h  IMPACT: 6578

  [2] !! SPLIT           code2llm/exporters/index_generator.py
      WHY: 790L, 1 classes, max CC=5
      EFFORT: ~4h  IMPACT: 3950

  [3] !! SPLIT           code2llm/exporters/html_dashboard.py
      WHY: 504L, 1 classes, max CC=7
      EFFORT: ~4h  IMPACT: 3528


RISKS[3]:
  ⚠ Splitting code2llm/exporters/index_generator.py may break 7 import paths
  ⚠ Splitting code2llm/analysis/pipeline_detector.py may break 18 import paths
  ⚠ Splitting code2llm/exporters/html_dashboard.py may break 14 import paths

METRICS-TARGET:
  CC̄:          4.4 → ≤3.1
  max-CC:      14 → ≤7
  god-modules: 4 → 0
  high-CC(≥15): 0 → ≤0
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  prev CC̄=4.3 → now CC̄=4.4
```

### Validation (`project/validation.toon.yaml`)

```toon markpact:analysis path=project/validation.toon.yaml
# vallm batch | 224f | 105✓ 5⚠ 65✗ | 2026-03-31

SUMMARY:
  scanned: 224  passed: 105 (46.9%)  warnings: 5  errors: 65  unsupported: 54

WARNINGS[5]{path,score}:
  code2llm/generators/mermaid.py,0.97
    issues[1]{rule,severity,message,line}:
      complexity.lizard_length,warning,generate_single_png: 102 lines exceeds limit 100,287
  tests/test_format_quality.py,0.97
    issues[1]{rule,severity,message,line}:
      complexity.lizard_length,warning,ground_truth_project: 116 lines exceeds limit 100,25
  validate_toon.py,0.97
    issues[2]{rule,severity,message,line}:
      complexity.cyclomatic,warning,main has cyclomatic complexity 17 (max: 15),297
      complexity.lizard_cc,warning,main: CC=17 exceeds limit 15,297
  code2llm/analysis/data_analysis.py,0.98
    issues[1]{rule,severity,message,line}:
      complexity.maintainability,warning,Low maintainability index: 7.1 (threshold: 20),
  code2llm/generators/llm_flow.py,0.98
    issues[1]{rule,severity,message,line}:
      complexity.maintainability,warning,Low maintainability index: 15.9 (threshold: 20),

ERRORS[65]{path,score}:
  demo_langs/invalid/sample_bad.go,0.00
    issues[1]{rule,severity,message,line}:
      syntax.tree_sitter,error,tree-sitter found 3 parse error(s) in go,
  demo_langs/invalid/sample_bad.java,0.00
    issues[1]{rule,severity,message,line}:
      syntax.tree_sitter,error,tree-sitter found 7 parse error(s) in java,
  demo_langs/invalid/sample_bad.php,0.00
    issues[1]{rule,severity,message,line}:
      syntax.tree_sitter,error,tree-sitter found 10 parse error(s) in php,
  demo_langs/invalid/sample_bad.py,0.00
    issues[1]{rule,severity,message,line}:
      syntax.parse,error,SyntaxError: expected ':',7
  demo_langs/invalid/sample_bad.rs,0.00
    issues[1]{rule,severity,message,line}:
      syntax.tree_sitter,error,tree-sitter found 7 parse error(s) in rust,
  demo_langs/invalid/sample_bad.ts,0.00
    issues[1]{rule,severity,message,line}:
      syntax.tree_sitter,error,tree-sitter found 3 parse error(s) in typescript,
  test_langs/invalid/sample_bad.go,0.00
    issues[1]{rule,severity,message,line}:
      syntax.tree_sitter,error,tree-sitter found 3 parse error(s) in go,
  test_langs/invalid/sample_bad.java,0.00
    issues[1]{rule,severity,message,line}:
      syntax.tree_sitter,error,tree-sitter found 7 parse error(s) in java,
  test_langs/invalid/sample_bad.php,0.00
    issues[1]{rule,severity,message,line}:
      syntax.tree_sitter,error,tree-sitter found 10 parse error(s) in php,
  test_langs/invalid/sample_bad.py,0.00
    issues[1]{rule,severity,message,line}:
      syntax.parse,error,SyntaxError: invalid syntax,3
  test_langs/invalid/sample_bad.rs,0.00
    issues[1]{rule,severity,message,line}:
      syntax.tree_sitter,error,tree-sitter found 7 parse error(s) in rust,
  test_langs/invalid/sample_bad.ts,0.00
    issues[1]{rule,severity,message,line}:
      syntax.tree_sitter,error,tree-sitter found 3 parse error(s) in typescript,
  test_python_only/invalid/sample_bad.py,0.00
    issues[1]{rule,severity,message,line}:
      syntax.parse,error,SyntaxError: invalid syntax,3
  code2llm/__init__.py,0.57
    issues[3]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'core.config' not found,15
      python.import.resolvable,error,Module 'core.models' not found,16
      python.import.resolvable,error,Module 'core.analyzer' not found,41
  code2llm/core/lang/__init__.py,0.57
    issues[9]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'typescript' not found,3
      python.import.resolvable,error,Module 'go_lang' not found,4
      python.import.resolvable,error,Module 'rust' not found,5
      python.import.resolvable,error,Module 'java' not found,6
      python.import.resolvable,error,Module 'cpp' not found,7
      python.import.resolvable,error,Module 'csharp' not found,8
      python.import.resolvable,error,Module 'php' not found,9
      python.import.resolvable,error,Module 'ruby' not found,10
      python.import.resolvable,error,Module 'generic' not found,11
  code2llm/core/streaming/__init__.py,0.57
    issues[5]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'strategies' not found,3
      python.import.resolvable,error,Module 'cache' not found,4
      python.import.resolvable,error,Module 'prioritizer' not found,5
      python.import.resolvable,error,Module 'scanner' not found,6
      python.import.resolvable,error,Module 'incremental' not found,7
  code2llm/exporters/__init__.py,0.57
    issues[14]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'base' not found,17
      python.import.resolvable,error,Module 'json_exporter' not found,18
      python.import.resolvable,error,Module 'yaml_exporter' not found,19
      python.import.resolvable,error,Module 'mermaid_exporter' not found,20
      python.import.resolvable,error,Module 'context_exporter' not found,21
      python.import.resolvable,error,Module 'llm_exporter' not found,22
      python.import.resolvable,error,Module 'toon' not found,23
      python.import.resolvable,error,Module 'map_exporter' not found,24
      python.import.resolvable,error,Module 'flow_exporter' not found,25
      python.import.resolvable,error,Module 'evolution_exporter' not found,26
      python.import.resolvable,error,Module 'readme_exporter' not found,27
      python.import.resolvable,error,Module 'project_yaml_exporter' not found,28
      python.import.resolvable,error,Module 'report_generators' not found,29
      python.import.resolvable,error,Module 'index_generator' not found,34
  code2llm/exporters/llm_exporter.py,0.57
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'context_exporter' not found,7
  code2llm/exporters/toon.py,0.57
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'toon' not found,8
  code2llm/generators/__init__.py,0.57
    issues[2]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'llm_flow' not found,6
      python.import.resolvable,error,Module 'mermaid' not found,7
  code2llm/core/__init__.py,0.63
    issues[6]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'models' not found,4
      python.import.resolvable,error,Module 'analyzer' not found,32
      python.import.resolvable,error,Module 'file_analyzer' not found,35
      python.import.resolvable,error,Module 'refactoring' not found,38
      python.import.resolvable,error,Module 'file_cache' not found,41
      python.import.resolvable,error,Module 'file_filter' not found,42
  code2llm/cli.py,0.66
    issues[4]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'cli_parser' not found,10
      python.import.resolvable,error,Module 'cli_commands' not found,11
      python.import.resolvable,error,Module 'cli_exports' not found,18
      python.import.resolvable,error,Module 'cli_analysis' not found,24
  code2llm/cli_analysis.py,0.66
    issues[11]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'core.large_repo' not found,17
      python.import.resolvable,error,Module 'core.config' not found,36
      python.import.resolvable,error,Module 'core.analyzer' not found,37
      python.import.resolvable,error,Module 'core.config' not found,60
      python.import.resolvable,error,Module 'core.large_repo' not found,106
      python.import.resolvable,error,Module 'core.analyzer' not found,191
      python.import.resolvable,error,Module 'core.config' not found,192
      python.import.resolvable,error,Module 'cli_exports' not found,193
      python.import.resolvable,error,Module 'core.models' not found,244
      python.import.resolvable,error,Module 'core.analyzer' not found,277
      python.import.resolvable,error,Module 'core.streaming_analyzer' not found,278
  code2llm/nlp/__init__.py,0.66
    issues[4]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'pipeline' not found,9
      python.import.resolvable,error,Module 'normalization' not found,10
      python.import.resolvable,error,Module 'intent_matching' not found,11
      python.import.resolvable,error,Module 'entity_resolution' not found,12
  code2llm/cli_exports/__init__.py,0.68
    issues[3]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'formats' not found,6
      python.import.resolvable,error,Module 'prompt' not found,18
      python.import.resolvable,error,Module 'orchestrator' not found,25
  code2llm/exporters/report_generators.py,0.71
    issues[4]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'toon_view' not found,13
      python.import.resolvable,error,Module 'context_view' not found,14
      python.import.resolvable,error,Module 'article_view' not found,15
      python.import.resolvable,error,Module 'html_dashboard' not found,16
  code2llm/api.py,0.74
    issues[3]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'core.config' not found,10
      python.import.resolvable,error,Module 'core.models' not found,11
      python.import.resolvable,error,Module 'core.analyzer' not found,37
  code2llm/core/lang/base.py,0.76
    issues[4]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'models' not found,146
      python.import.resolvable,error,Module 'models' not found,254
      python.import.resolvable,error,Module 'models' not found,305
      python.import.resolvable,error,Module 'models' not found,363
  examples/streaming-analyzer/sample_project/main.py,0.76
    issues[4]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'auth' not found,7
      python.import.resolvable,error,Module 'database' not found,8
      python.import.resolvable,error,Module 'api' not found,9
      python.import.resolvable,error,Module 'utils' not found,10
  code2llm/core/analyzer.py,0.77
    issues[8]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'models' not found,10
      python.import.resolvable,error,Module 'file_cache' not found,13
      python.import.resolvable,error,Module 'file_filter' not found,14
      python.import.resolvable,error,Module 'file_analyzer' not found,15
      python.import.resolvable,error,Module 'refactoring' not found,16
      python.import.resolvable,error,Module 'file_cache' not found,353
      python.import.resolvable,error,Module 'file_filter' not found,354
      python.import.resolvable,error,Module 'file_analyzer' not found,355
  code2llm/cli_parser.py,0.79
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'core.config' not found,5
  code2llm/nlp/pipeline.py,0.81
    issues[4]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'normalization' not found,15
      python.import.resolvable,error,Module 'intent_matching' not found,16
      python.import.resolvable,error,Module 'entity_resolution' not found,17
      python.import.resolvable,error,Module 'intent_matching' not found,308
  code2llm/cli_exports/orchestrator.py,0.82
    issues[3]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'formats' not found,7
      python.import.resolvable,error,Module 'prompt' not found,19
      python.import.resolvable,error,Module 'core.large_repo' not found,117
  code2llm/core/streaming/scanner.py,0.82
    issues[3]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'cache' not found,9
      python.import.resolvable,error,Module 'prioritizer' not found,10
      python.import.resolvable,error,Module 'strategies' not found,11
  code2llm/exporters/toon/__init__.py,0.82
    issues[3]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'metrics' not found,9
      python.import.resolvable,error,Module 'renderer' not found,10
      python.import.resolvable,error,Module 'helpers' not found,11
  code2llm/exporters/toon/metrics.py,0.82
    issues[3]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'helpers' not found,9
      python.import.resolvable,error,Module 'helpers' not found,480
      python.import.resolvable,error,Module 'helpers' not found,198
  code2llm/core/large_repo.py,0.83
    issues[2]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'repo_files' not found,14
      python.import.resolvable,error,Module 'repo_files' not found,323
  code2llm/exporters/flow_renderer.py,0.83
    issues[2]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'flow_constants' not found,9
      python.import.resolvable,error,Module 'core.models' not found,19
  benchmarks/benchmark_format_quality.py,0.84
    issues[4]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'benchmarks.benchmark_constants' not found,24
      python.import.resolvable,error,Module 'benchmarks.format_evaluator' not found,25
      python.import.resolvable,error,Module 'benchmarks.project_generator' not found,26
      python.import.resolvable,error,Module 'benchmarks.reporting' not found,27
  code2llm/core/refactoring.py,0.85
    issues[5]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'models' not found,7
      python.import.resolvable,error,Module 'file_filter' not found,8
      python.import.resolvable,error,Module 'analysis.call_graph' not found,24
      python.import.resolvable,error,Module 'analysis.coupling' not found,125
      python.import.resolvable,error,Module 'analysis.smells' not found,131
  benchmarks/reporting.py,0.86
    issues[2]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'benchmark_constants' not found,12
      python.import.resolvable,error,Module 'format_evaluator' not found,13
  code2llm/cli_exports/formats.py,0.86
    issues[3]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'refactor.prompt_engine' not found,250
      python.import.resolvable,error,Module 'exporters.validate_project' not found,151
      python.import.resolvable,error,Module 'generators.mermaid' not found,196
  code2llm/core/streaming_analyzer.py,0.86
    issues[2]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'streaming' not found,16
      python.import.resolvable,error,Module 'streaming' not found,178
  code2llm/exporters/toon/module_detail.py,0.86
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'helpers' not found,7
  examples/streaming-analyzer/sample_project/api.py,0.86
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'database' not found,5
  code2llm/cli_commands.py,0.87
    issues[3]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'cli_exports' not found,8
      python.import.resolvable,error,Module 'exporters' not found,195
      python.import.resolvable,error,Module 'generators.llm_flow' not found,14
  code2llm/exporters/mermaid_exporter.py,0.88
    issues[2]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'base' not found,18
      python.import.resolvable,error,Module 'mermaid_flow_helpers' not found,20
  code2llm/exporters/toon/renderer.py,0.88
    issues[2]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'helpers' not found,10
      python.import.resolvable,error,Module 'helpers' not found,49
  code2llm/analysis/pipeline_detector.py,0.89
    issues[2]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'side_effects' not found,21
      python.import.resolvable,error,Module 'type_inference' not found,22
  code2llm/core/file_analyzer.py,0.89
    issues[3]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'models' not found,11
      python.import.resolvable,error,Module 'file_filter' not found,17
      python.import.resolvable,error,Module 'lang' not found,18
  code2llm/core/repo_files.py,0.89
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'gitignore' not found,7
  code2llm/exporters/flow_exporter.py,0.89
    issues[3]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'base' not found,19
      python.import.resolvable,error,Module 'flow_constants' not found,20
      python.import.resolvable,error,Module 'flow_renderer' not found,21
  code2llm/exporters/json_exporter.py,0.89
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'base' not found,5
  code2llm/exporters/toon/helpers.py,0.89
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'core.config' not found,101
  code2llm/exporters/project_yaml_exporter.py,0.90
    issues[2]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'base' not found,18
      python.import.resolvable,error,Module 'toon.helpers' not found,20
  benchmarks/format_evaluator.py,0.91
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'benchmark_constants' not found,12
  code2llm/core/file_filter.py,0.91
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'gitignore' not found,7
  code2llm/exporters/readme_exporter.py,0.91
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'base' not found,12
  examples/functional_refactoring_example.py,0.91
    issues[5]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'entities.preparer' not found,354
      python.import.resolvable,error,Module 'templates.loader' not found,355
      python.import.resolvable,error,Module 'templates.renderer' not found,356
      python.import.resolvable,error,Module 'domain.command_generation.generator' not found,560
      python.import.resolvable,error,Module 'infrastructure.caching.evolutionary_cache' not found,561
  code2llm/core/streaming/prioritizer.py,0.93
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'strategies' not found,9
  code2llm/exporters/context_exporter.py,0.93
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'base' not found,10
  code2llm/cli_exports/code2logic.py,0.94
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'core.toon_size_manager' not found,120
  code2llm/exporters/evolution_exporter.py,0.94
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'base' not found,16
  code2llm/exporters/yaml_exporter.py,0.94
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'base' not found,6
  code2llm/exporters/map_exporter.py,0.95
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'base' not found,18

UNSUPPORTED[4]{bucket,count}:
  *.md,39
  *.txt,5
  *.example,1
  other,9
```

## Intent

High-performance Python code flow analysis with optimized TOON format - CFG, DFG, call graphs, and intelligent code queries
