# code2llm - Generated Analysis Files

High-performance Python code flow analysis with optimized TOON format - CFG, DFG, call graphs, and intelligent code queries

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Workflows](#workflows)
- [Quality Pipeline (`pyqual.yaml`)](#quality-pipeline-pyqualyaml)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Environment Variables (`.env.example`)](#environment-variables-envexample)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Makefile Targets](#makefile-targets)
- [Code Analysis](#code-analysis)
- [Source Map](#source-map)
- [Call Graph](#call-graph)
- [Intent](#intent)

## Metadata

- **name**: `code2llm`
- **version**: `0.5.114`
- **python_requires**: `>=3.8`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, requirements.txt, Taskfile.yml, Makefile, app.doql.css, pyqual.yaml, goal.yaml, .env.example, src(5 mod), project/(2 analysis files)

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

## Interfaces

### CLI Entry Points

- `code2llm`

## Workflows

### Taskfile Tasks (`Taskfile.yml`)

```yaml markpact:taskfile path=Taskfile.yml
version: '1'
name: code2llm
description: Minimal Taskfile
variables:
  APP_NAME: code2llm
environments:
  local:
    container_runtime: docker
    compose_command: docker compose
pipeline:
  python_version: "3.12"
  runner_image: ubuntu-latest
  branches: [main]
  cache: [~/.cache/pip]
  artifacts: [dist/]

  stages:
    - name: lint
      tasks: [lint]

    - name: test
      tasks: [test]

    - name: build
      tasks: [build]
      when: "branch:main"

tasks:
  install:
    desc: Install Python dependencies (editable)
    cmds:
    - pip install -e .[dev]
  test:
    desc: Run pytest suite
    cmds:
    - pytest -q
  build:
    desc: Build wheel + sdist
    cmds:
    - python -m build
  clean:
    desc: Remove build artefacts
    cmds:
    - rm -rf build/ dist/ *.egg-info
  help:
    desc: '[imported from Makefile] help'
    cmds:
    - echo "code2llm - Python Code Flow Analysis Tool with LLM Integration and TOON
      Format"
    - echo ""
    - "echo \"\U0001F680 Installation:\""
    - echo "  make install       - Install package"
    - echo "  make dev-install   - Install with development dependencies"
    - echo ""
    - "echo \"\U0001F9EA Testing:\""
    - echo "  make test          - Run test suite"
    - echo "  make test-toon     - Test TOON format only"
    - echo "  make validate-toon - Validate TOON format output"
    - echo "  make test-all-formats - Test all output formats"
    - echo ""
    - "echo \"\U0001F527 Code Quality:\""
    - echo "  make lint          - Run linters (flake8, black --check)"
    - echo "  make format        - Format code with black"
    - echo "  make typecheck     - Run mypy type checking"
    - echo "  make check         - Run all quality checks"
    - echo ""
    - "echo \"\U0001F4CA Analysis:\""
    - echo "  make analyze       - Run analysis on current project (TOON format)"
    - echo "  make run           - Run with example arguments"
    - echo "  make analyze-all   - Run analysis with all formats"
    - echo ""
    - "echo \"\U0001F3AF TOON Format:\""
    - echo "  make toon-demo     - Quick TOON format demo"
    - echo "  make toon-compare  - Compare TOON vs YAML formats"
    - echo "  make toon-validate - Validate TOON format structure"
    - echo ""
    - "echo \"\U0001F4E6 Building & Release:\""
    - echo "  make build         - Build distribution packages"
    - echo "  make publish       - Publish to PyPI (with version bump)"
    - echo "  make publish-test  - Publish to TestPyPI"
    - echo "  make bump-patch    - Bump patch version"
    - echo "  make bump-minor    - Bump minor version"
    - echo "  make bump-major    - Bump major version"
    - echo ""
    - "echo \"\U0001F3A8 Visualization:\""
    - echo "  make mermaid-png   - Generate PNG from all Mermaid files"
    - echo "  make install-mermaid - Install Mermaid CLI renderer"
    - echo "  make check-mermaid - Check available Mermaid renderers"
    - echo ""
    - "echo \"\U0001F9F9 Maintenance:\""
    - echo "  make clean         - Remove build artifacts"
    - echo "  make clean-png     - Clean PNG files"
    - echo ""
  dev-install:
    desc: '[imported from Makefile] dev-install'
    cmds:
    - $(PYTHON) -m pip install -e ".[dev]"
    - "echo \"\u2713 code2llm installed with dev dependencies\""
  test-cov:
    desc: '[imported from Makefile] test-cov'
    cmds:
    - $(PYTHON) -m pytest tests/ --cov=code2llm --cov-report=html --cov-report=term
      2>/dev/null || echo "No tests yet"
  test-toon:
    desc: '[imported from Makefile] test-toon'
    cmds:
    - "echo \"\U0001F3AF Testing TOON format...\""
    - $(PYTHON) -m code2llm ./ -v -o ./test_toon -m hybrid -f toon
    - $(PYTHON) validate_toon.py test_toon/analysis.toon
    - "echo \"\u2713 TOON format test complete\""
  validate-toon:
    desc: '[imported from Makefile] validate-toon'
    deps:
    - test-toon
  test-all-formats:
    desc: '[imported from Makefile] test-all-formats'
    cmds:
    - "echo \"\U0001F4CA Testing all output formats...\""
    - $(PYTHON) -m code2llm ./ -v -o ./test_all -m hybrid -f all
    - $(PYTHON) validate_toon.py test_all/analysis.toon
    - "echo \"\u2713 All formats test complete\""
  test-comprehensive:
    desc: '[imported from Makefile] test-comprehensive'
    cmds:
    - "echo \"\U0001F680 Running comprehensive test suite...\""
    - bash project.sh
    - "echo \"\u2713 Comprehensive tests complete\""
  lint:
    desc: '[imported from Makefile] lint'
    cmds:
    - $(PYTHON) -m flake8 code2llm/ --max-line-length=100 --ignore=E203,W503 2>/dev/null
      || echo "flake8 not installed"
    - $(PYTHON) -m black --check code2llm/ 2>/dev/null || echo "black not installed"
    - "echo \"\u2713 Linting complete\""
  format:
    desc: '[imported from Makefile] format'
    cmds:
    - '$(PYTHON) -m black code2llm/ --line-length=100 2>/dev/null || echo "black not
      installed, run: pip install black"'
    - "echo \"\u2713 Code formatted\""
  typecheck:
    desc: '[imported from Makefile] typecheck'
    cmds:
    - $(PYTHON) -m mypy code2llm/ --ignore-missing-imports 2>/dev/null || echo "mypy
      not installed"
  check:
    desc: '[imported from Makefile] check'
    cmds:
    - "echo \"\u2713 All checks passed\""
    deps:
    - lint
    - typecheck
    - test
  run:
    desc: '[imported from Makefile] run'
    cmds:
    - $(PYTHON) -m code2llm ../python/stts_core -v -o ./output
  analyze:
    desc: '[imported from Makefile] analyze'
    cmds:
    - "echo \"\U0001F3AF Running TOON format analysis on current project...\""
    - $(PYTHON) -m code2llm ./ -v -o ./analysis -m hybrid -f toon
    - $(PYTHON) validate_toon.py analysis/analysis.toon
    - "echo \"\u2713 TOON analysis complete - check analysis/analysis.toon\""
  analyze-all:
    desc: '[imported from Makefile] analyze-all'
    cmds:
    - "echo \"\U0001F4CA Running analysis with all formats...\""
    - $(PYTHON) -m code2llm ./ -v -o ./analysis_all -m hybrid -f all
    - $(PYTHON) validate_toon.py analysis_all/analysis.toon
    - "echo \"\u2713 All formats analysis complete - check analysis_all/\""
  toon-demo:
    desc: '[imported from Makefile] toon-demo'
    cmds:
    - "echo \"\U0001F3AF Quick TOON format demo...\""
    - $(PYTHON) -m code2llm ./ -v -o ./demo -m hybrid -f toon
    - "echo \"\U0001F4C1 Generated: demo/analysis.toon\""
    - "echo \"\U0001F4CA Size: $$(du -h demo/analysis.toon | cut -f1)\""
    - "echo \"\U0001F50D Preview:\""
    - head -20 demo/analysis.toon
  toon-compare:
    desc: '[imported from Makefile] toon-compare'
    cmds:
    - "echo \"\U0001F4CA Comparing TOON vs YAML formats...\""
    - $(PYTHON) -m code2llm ./ -v -o ./compare -m hybrid -f toon,yaml
    - "echo \"\U0001F4C1 Files generated:\""
    - 'echo "  - TOON:  compare/analysis.toon  ($$(du -h compare/analysis.toon | cut
      -f1))"'
    - 'echo "  - YAML:  compare/analysis.yaml  ($$(du -h compare/analysis.yaml | cut
      -f1))"'
    - 'echo "  - Ratio: $$(echo "scale=1; $$(du -k compare/analysis.yaml | cut -f1)
      / $$(du -k compare/analysis.toon | cut -f1)" | bc)x smaller"'
    - $(PYTHON) validate_toon.py compare/analysis.yaml compare/analysis.toon
  toon-validate:
    desc: '[imported from Makefile] toon-validate'
    cmds:
    - "echo \"\U0001F50D Validating TOON format structure...\""
    - $(PYTHON) validate_toon.py analysis/analysis.toon 2>/dev/null || $(PYTHON) validate_toon.py
      test_toon/analysis.toon 2>/dev/null || echo "Run 'make test-toon' first"
  publish-test:
    desc: '[imported from Makefile] publish-test'
    cmds:
    - "echo \"\U0001F680 Publishing to TestPyPI...\""
    - $(PYTHON) -m venv publish-test-env
    - publish-test-env/bin/pip install twine
    - publish-test-env/bin/python -m twine upload --repository testpypi dist/*
    - rm -rf publish-test-env
    - "echo \"\u2713 Published to TestPyPI\""
    deps:
    - build
  bump-patch:
    desc: '[imported from Makefile] bump-patch'
    cmds:
    - "echo \"\U0001F522 Bumping patch version...\""
    - $(PYTHON) scripts/bump_version.py patch 2>/dev/null || echo "Create scripts/bump_version.py
      or edit pyproject.toml manually"
  bump-minor:
    desc: '[imported from Makefile] bump-minor'
    cmds:
    - "echo \"\U0001F522 Bumping minor version...\""
    - $(PYTHON) scripts/bump_version.py minor 2>/dev/null || echo "Create scripts/bump_version.py
      or edit pyproject.toml manually"
  bump-major:
    desc: '[imported from Makefile] bump-major'
    cmds:
    - "echo \"\U0001F522 Bumping major version...\""
    - $(PYTHON) scripts/bump_version.py major 2>/dev/null || echo "Create scripts/bump_version.py
      or edit pyproject.toml manually"
  publish:
    desc: '[imported from Makefile] publish'
    cmds:
    - "echo \"\U0001F680 Publishing to PyPI...\""
    - "echo \"\U0001F522 Bumping patch version...\""
    - $(MAKE) bump-patch
    - "echo \"\U0001F528 Rebuilding package with new version...\""
    - $(MAKE) build
    - "echo \"\U0001F4E6 Publishing to PyPI...\""
    - $(PYTHON) -m venv publish-env
    - publish-env/bin/pip install twine
    - publish-env/bin/python -m twine upload dist/*
    - rm -rf publish-env
    - "echo \"\u2713 Published to PyPI\""
    deps:
    - build
  mermaid-png:
    desc: '[imported from Makefile] mermaid-png'
    cmds:
    - $(PYTHON) mermaid_to_png.py --batch output output
  install-mermaid:
    desc: '[imported from Makefile] install-mermaid'
    cmds:
    - npm install -g @mermaid-js/mermaid-cli
  check-mermaid:
    desc: '[imported from Makefile] check-mermaid'
    cmds:
    - echo "Checking available Mermaid renderers..."
    - "which mmdc > /dev/null && echo \"\u2713 mmdc (mermaid-cli)\" || echo \"\u2717\
      \ mmdc (run: npm install -g @mermaid-js/mermaid-cli)\""
    - "which npx > /dev/null && echo \"\u2713 npx (for @mermaid-js/mermaid-cli)\"\
      \ || echo \"\u2717 npx (install Node.js)\""
    - "which puppeteer > /dev/null && echo \"\u2713 puppeteer\" || echo \"\u2717 puppeteer\
      \ (run: npm install -g puppeteer)\""
  clean-png:
    desc: '[imported from Makefile] clean-png'
    cmds:
    - rm -f output/*.png
    - "echo \"\u2713 Cleaned PNG files\""
  quickstart:
    desc: '[imported from Makefile] quickstart'
    cmds:
    - "echo \"\U0001F680 Quick Start with code2llm TOON format:\""
    - echo ""
    - 'echo "1. Install:        make install"'
    - 'echo "2. Test TOON:      make test-toon"'
    - 'echo "3. Analyze:        make analyze"'
    - 'echo "4. Compare:        make toon-compare"'
    - 'echo "5. All formats:    make test-all-formats"'
    - echo ""
    - "echo \"\U0001F4D6 For more: make help\""
  health:
    desc: '[from doql] workflow: health'
    cmds:
    - docker compose ps
    - docker compose exec app echo "Health check passed"
  import-makefile-hint:
    desc: '[from doql] workflow: import-makefile-hint'
    cmds:
    - 'echo ''Run: taskfile import Makefile to import existing targets.'''
  all:
    desc: Run install, lint, test
    cmds:
    - taskfile run install
    - taskfile run lint
    - taskfile run test
  fmt:
    desc: Auto-format with ruff
    cmds:
    - ruff format .
```

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

## Configuration

```yaml
project:
  name: code2llm
  version: 0.5.114
  env: local
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

## Deployment

```bash markpact:run
pip install code2llm

# development install
pip install -e .[dev]
```

### Requirements Files

#### `requirements.txt`

- `networkx>=3.0`
- `matplotlib>=3.6.0`
- `numpy>=1.21.0`
- `pyyaml>=6.0`
- `scipy>=1.7.0`
- `radon>=5.1`
- `psutil>=5.8.0`
- `astroid>=3.0`
- `code2logic`

## Environment Variables (`.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `CODE2FLOW_CALLS_SPLIT` | `1` | Enable/disable splitting |
| `CODE2FLOW_CALLS_KEEP_MAIN` | `0` | Keep writing the full calls.mmd in addition to parts |
| `CODE2FLOW_CALLS_MIN_NODES` | `30` | Minimum number of functions per part |
| `CODE2FLOW_CALLS_MAX_NODES` | `250` | Maximum number of functions per part |
| `CODE2FLOW_CALLS_MAX_PARTS` | `20` | Maximum number of parts to generate |
| `CODE2FLOW_CALLS_INCLUDE_SINGLETONS` | `0` | Include singleton components (1 function with no edges) |
| `CODE2FLOW_MERMAID_MAX_EDGES` | `20000` | Increase if Mermaid CLI reports edge/text limits. |
| `CODE2FLOW_MERMAID_MAX_TEXT_SIZE` | `2000000` |  |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`code2flow`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `setup.py:version`, `code2llm/__init__.py:__version__`

## Makefile Targets

- `PYTHON`
- `help` — Default target
- `install`
- `dev-install`
- `test`
- `test-cov`
- `test-toon`
- `validate-toon`
- `test-all-formats`
- `test-comprehensive`
- `lint`
- `format`
- `typecheck`
- `check`
- `run`
- `analyze`
- `analyze-all`
- `toon-demo`
- `toon-compare`
- `toon-validate`
- `build`
- `publish-test`
- `bump-patch`
- `bump-minor`
- `bump-major`
- `publish`
- `mermaid-png`
- `install-mermaid`
- `check-mermaid`
- `clean`
- `clean-png`
- `quickstart`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# code2llm | 125f 22873L | shell:3,python:121,java:1 | 2026-04-19
# stats: 938 func | 0 cls | 125 mod | CC̄=4.3 | critical:0 | cycles:0
# alerts[5]: fan-out analyze_rust=24; fan-out _summarize_functions=21; fan-out _analyze_go_regex=20; fan-out ProjectAnalyzer.analyze_project=19; fan-out ProjectYAMLExporter._build_project_yaml=18
# hotspots[5]: analyze_rust fan=24; _summarize_functions fan=21; _analyze_go_regex fan=20; ProjectAnalyzer.analyze_project fan=19; run_benchmark fan=18
# evolution: CC̄ 4.3→4.3 (flat 0.0)
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[125]:
  badges/server.py,110
  benchmarks/benchmark_constants.py,29
  benchmarks/benchmark_evolution.py,137
  benchmarks/benchmark_format_quality.py,143
  benchmarks/benchmark_optimizations.py,157
  benchmarks/benchmark_performance.py,306
  benchmarks/format_evaluator.py,138
  benchmarks/project_generator.py,233
  benchmarks/reporting.py,179
  code2llm/__init__.py,52
  code2llm/__main__.py,6
  code2llm/analysis/__init__.py,33
  code2llm/analysis/call_graph.py,211
  code2llm/analysis/cfg.py,293
  code2llm/analysis/coupling.py,77
  code2llm/analysis/data_analysis.py,286
  code2llm/analysis/dfg.py,224
  code2llm/analysis/pipeline_detector.py,506
  code2llm/analysis/side_effects.py,294
  code2llm/analysis/smells.py,192
  code2llm/analysis/type_inference.py,290
  code2llm/analysis/utils/__init__.py,5
  code2llm/analysis/utils/ast_helpers.py,54
  code2llm/api.py,73
  code2llm/cli.py,69
  code2llm/cli_analysis.py,323
  code2llm/cli_commands.py,250
  code2llm/cli_exports/__init__.py,48
  code2llm/cli_exports/code2logic.py,127
  code2llm/cli_exports/formats.py,318
  code2llm/cli_exports/orchestrator.py,160
  code2llm/cli_exports/prompt.py,475
  code2llm/cli_parser.py,297
  code2llm/core/__init__.py,53
  code2llm/core/analyzer.py,355
  code2llm/core/ast_registry.py,102
  code2llm/core/config.py,211
  code2llm/core/export_pipeline.py,153
  code2llm/core/file_analyzer.py,396
  code2llm/core/file_cache.py,103
  code2llm/core/file_filter.py,100
  code2llm/core/gitignore.py,138
  code2llm/core/incremental.py,150
  code2llm/core/lang/__init__.py,11
  code2llm/core/lang/base.py,454
  code2llm/core/lang/cpp.py,35
  code2llm/core/lang/csharp.py,42
  code2llm/core/lang/generic.py,71
  code2llm/core/lang/go_lang.py,102
  code2llm/core/lang/java.py,43
  code2llm/core/lang/php.py,66
  code2llm/core/lang/ruby.py,143
  code2llm/core/lang/rust.py,94
  code2llm/core/lang/ts_extractors.py,180
  code2llm/core/lang/ts_parser.py,158
  code2llm/core/lang/typescript.py,53
  code2llm/core/large_repo.py,488
  code2llm/core/models.py,194
  code2llm/core/refactoring.py,196
  code2llm/core/repo_files.py,174
  code2llm/core/streaming/__init__.py,7
  code2llm/core/streaming/cache.py,51
  code2llm/core/streaming/incremental.py,75
  code2llm/core/streaming/prioritizer.py,131
  code2llm/core/streaming/scanner.py,201
  code2llm/core/streaming/strategies.py,68
  code2llm/core/streaming_analyzer.py,181
  code2llm/core/toon_size_manager.py,265
  code2llm/exporters/__init__.py,55
  code2llm/exporters/article_view.py,163
  code2llm/exporters/base.py,13
  code2llm/exporters/context_exporter.py,248
  code2llm/exporters/context_view.py,140
  code2llm/exporters/evolution_exporter.py,471
  code2llm/exporters/flow_constants.py,29
  code2llm/exporters/flow_exporter.py,391
  code2llm/exporters/flow_renderer.py,188
  code2llm/exporters/html_dashboard.py,504
  code2llm/exporters/index_generator.py,790
  code2llm/exporters/json_exporter.py,17
  code2llm/exporters/llm_exporter.py,12
  code2llm/exporters/map_exporter.py,439
  code2llm/exporters/mermaid_exporter.py,480
  code2llm/exporters/mermaid_flow_helpers.py,262
  code2llm/exporters/project_yaml/__init__.py,15
  code2llm/exporters/project_yaml/constants.py,15
  code2llm/exporters/project_yaml/core.py,118
  code2llm/exporters/project_yaml/evolution.py,46
  code2llm/exporters/project_yaml/health.py,103
  code2llm/exporters/project_yaml/hotspots.py,106
  code2llm/exporters/project_yaml/modules.py,151
  code2llm/exporters/project_yaml_exporter.py,15
  code2llm/exporters/readme_exporter.py,496
  code2llm/exporters/report_generators.py,34
  code2llm/exporters/toon/__init__.py,196
  code2llm/exporters/toon/helpers.py,120
  code2llm/exporters/toon/metrics.py,501
  code2llm/exporters/toon/module_detail.py,162
  code2llm/exporters/toon/renderer.py,471
  code2llm/exporters/toon_view.py,157
  code2llm/exporters/validate_project.py,118
  code2llm/exporters/yaml_exporter.py,326
  code2llm/generators/__init__.py,12
  code2llm/generators/llm_flow.py,472
  code2llm/generators/llm_task.py,284
  code2llm/generators/mermaid.py,485
  code2llm/nlp/__init__.py,23
  code2llm/nlp/config.py,174
  code2llm/nlp/entity_resolution.py,326
  code2llm/nlp/intent_matching.py,297
  code2llm/nlp/normalization.py,122
  code2llm/nlp/pipeline.py,388
  code2llm/parsers/toon_parser.py,147
  code2llm/patterns/__init__.py,0
  code2llm/patterns/detector.py,168
  code2llm/refactor/__init__.py,0
  code2llm/refactor/prompt_engine.py,150
  demo_langs/valid/sample.java,47
  orchestrator.sh,58
  project.sh,49
  project2.sh,35
  scripts/benchmark_badges.py,392
  scripts/bump_version.py,96
  setup.py,67
  validate_toon.py,390
D:
  code2llm/cli_analysis.py:
    e: _run_analysis,_run_standard_analysis,_build_config,_print_analysis_summary,_run_chunked_analysis,_print_chunked_plan,_filter_subprojects,_analyze_all_subprojects,_analyze_subproject,_merge_chunked_results,_run_streaming_analysis
    _run_analysis(args;source_path;output_dir)
    _run_standard_analysis(args;source_path;output_dir)
    _build_config(args;output_dir)
    _print_analysis_summary(result)
    _run_chunked_analysis(args;source_path;output_dir)
    _print_chunked_plan(subprojects)
    _filter_subprojects(args;subprojects)
    _analyze_all_subprojects(args;subprojects;output_dir)
    _analyze_subproject(args;subproject;output_dir)
    _merge_chunked_results(all_results;source_path)
    _run_streaming_analysis(args;config;source_path)
  code2llm/analysis/data_analysis.py:
    e: DataAnalyzer,_categorize_functions,_make_stage
    DataAnalyzer: analyze_data_flow(1),analyze_data_structures(1),_find_data_pipelines(1),_find_state_patterns(1),_find_data_dependencies(1),_find_event_flows(1),_detect_types_from_name(2),_create_type_entry(4),_update_type_stats(4),_analyze_data_types(1),_infer_parameter_types(1),_infer_return_types(1),_build_data_flow_graph(1),_get_function_data_types(1),_identify_process_patterns(1),_analyze_optimization_opportunities(3)  # Analyze data flows, structures, and optimization opportuniti...
    _categorize_functions(result)
    _make_stage(label;func_name;func)
  code2llm/analysis/side_effects.py:
    e: SideEffectInfo,SideEffectDetector
    SideEffectInfo: __init__(2),to_dict(0)  # Side-effect analysis result for a single function...
    SideEffectDetector: __init__(1),analyze_function(1),analyze_all(1),get_purity_score(1),_scan_node(2),_check_calls(2),_check_assignments(2),_check_globals(2),_check_yield(2),_check_delete(2),_classify(1),_heuristic_classify(2),_get_call_name(1)  # Detect side effects in Python functions via AST analysis.

S...
  code2llm/core/analyzer.py:
    e: ProjectAnalyzer
    ProjectAnalyzer: __init__(2),analyze_project(1),_collect_files(1),_analyze_parallel(1),_analyze_sequential(1),_merge_results(2),_build_call_graph(1),analyze_files(2),_detect_patterns(1)  # Main analyzer with parallel processing...
  code2llm/core/file_filter.py:
    e: FastFileFilter
    FastFileFilter: __init__(2),should_skip_dir(1),should_process(1),should_skip_function(4)  # Fast file filtering with pattern matching...
  code2llm/core/streaming/scanner.py:
    e: StreamingScanner
    StreamingScanner: __init__(2),quick_scan_file(1),deep_analyze_file(1),build_call_graph_streaming(1),select_important_files(2),collect_files(1)  # Handles file scanning operations...
  code2llm/core/lang/ruby.py:
    e: _extract_ruby_body,_adjust_ruby_module_qualnames,analyze_ruby
    _extract_ruby_body(content;start_line)
    _adjust_ruby_module_qualnames(result;module_name;current_module)
    analyze_ruby(content;file_path;module_name;ext;stats)
  code2llm/core/lang/base.py:
    e: extract_function_body,calculate_complexity_regex,_resolve_call,extract_calls_regex,_extract_declarations,_update_brace_tracking,_process_decorators,_process_classes,_process_standalone_function,_match_method_name,_process_class_method,_process_functions,_clear_orphaned_decorators,analyze_c_family
    extract_function_body(content;start_line)
    calculate_complexity_regex(content;result;lang)
    _resolve_call(simple_call;func_qname;module_name;known_simple;calls_seen;func_info)
    extract_calls_regex(content;module_name;result)
    _extract_declarations(content;file_path;module_name;patterns;stats;lang_config)
    _update_brace_tracking(raw_line;brace_depth;current_class;class_brace_depth;track_braces)
    _process_decorators(decorator_re;line;pending_decorators)
    _process_classes(class_re;interface_re;line;line_no;file_path;module_name;result;stats;current_class;class_brace_depth;pending_decorators)
    _process_standalone_function(func_re;arrow_re;line;line_no;file_path;module_name;result;stats;pending_decorators;reserved)
    _match_method_name(arrow_prop_re;method_re;func_re;line;reserved)
    _process_class_method(method_re;arrow_prop_re;func_re;line;line_no;file_path;module_name;result;stats;current_class;pending_decorators;reserved)
    _process_functions(func_re;arrow_re;method_re;arrow_prop_re;line;line_no;file_path;module_name;result;stats;current_class;pending_decorators;reserved)
    _clear_orphaned_decorators(line;pending_decorators;func_re;arrow_re;class_re;interface_re;method_re)
    analyze_c_family(content;file_path;module_name;stats;patterns;lang_config;cc_lang;ext)
  code2llm/exporters/flow_renderer.py:
    e: FlowRenderer
    FlowRenderer: render_header(0),render_pipelines(0),render_transforms(0),render_contracts(0),render_data_types(0),render_side_effects(0)  # Renderer dla sekcji formatu flow.toon...
  code2llm/generators/llm_task.py:
    e: _strip_bom,_ensure_list,_deep_get,normalize_llm_task,_parse_bullets,_parse_sections,_create_empty_task_data,_apply_simple_sections,_apply_bullet_sections,_parse_acceptance_tests,parse_llm_task_text,load_input,dump_yaml,create_parser,main
    _strip_bom(text)
    _ensure_list(value)
    _deep_get(d;path)
    normalize_llm_task(data)
    _parse_bullets(lines)
    _parse_sections(lines)
    _create_empty_task_data()
    _apply_simple_sections(sections;data)
    _apply_bullet_sections(sections;data)
    _parse_acceptance_tests(sections)
    parse_llm_task_text(text)
    load_input(path)
    dump_yaml(data)
    create_parser()
    main(argv)
  code2llm/generators/llm_flow.py:
    e: FuncSummary,_strip_bom,_safe_read_yaml,_as_dict,_as_list,_shorten,_parse_call_label,_parse_func_label,_collect_nodes,_group_nodes_by_file,_is_entrypoint_file,_extract_entrypoint_info,_deduplicate_entrypoints,_collect_entrypoints,_collect_functions,_node_counts_by_function,_pick_relevant_functions,_summarize_functions,_build_call_graph,_reachable,generate_llm_flow,render_llm_flow_md,dump_yaml,create_parser,main
    FuncSummary:
    _strip_bom(text)
    _safe_read_yaml(path)
    _as_dict(d)
    _as_list(v)
    _shorten(s;max_len)
    _parse_call_label(label)
    _parse_func_label(label)
    _collect_nodes(analysis)
    _group_nodes_by_file(nodes)
    _is_entrypoint_file(filepath)
    _extract_entrypoint_info(node;filepath)
    _deduplicate_entrypoints(entrypoints)
    _collect_entrypoints(nodes)
    _collect_functions(nodes)
    _node_counts_by_function(nodes)
    _pick_relevant_functions()
    _summarize_functions(nodes;limit_decisions;limit_calls)
    _build_call_graph(func_summaries;known_functions)
    _reachable(g;roots;max_nodes)
    generate_llm_flow(analysis;max_functions;limit_decisions;limit_calls)
    render_llm_flow_md(flow)
    dump_yaml(data)
    create_parser()
    main(argv)
  code2llm/cli_exports/prompt.py:
    e: _export_prompt_txt,_export_chunked_prompt_txt,_get_prompt_paths,_build_prompt_header,_find_existing_prompt_file,_build_prompt_file_lines,_build_main_files_section,_build_optional_files_section,_format_size,_get_missing_files,_build_subprojects_section,_build_missing_files_section,_analyze_generated_files,_build_dynamic_focus_areas,_build_dynamic_tasks,_build_priority_order,_build_strategy_section,_build_prompt_footer
    _export_prompt_txt(args;output_dir;formats;source_path)
    _export_chunked_prompt_txt(args;output_dir;formats;source_path;subprojects)
    _get_prompt_paths(source_path;output_dir)
    _build_prompt_header(project_path)
    _find_existing_prompt_file(output_dir;candidates)
    _build_prompt_file_lines(output_dir;output_rel_path;files)
    _build_main_files_section(output_dir;output_rel_path)
    _build_optional_files_section(output_dir;output_rel_path)
    _format_size(size_bytes)
    _get_missing_files(output_dir)
    _build_subprojects_section(subprojects;output_dir;output_rel_path)
    _build_missing_files_section(output_dir;output_rel_path)
    _analyze_generated_files(output_dir;subprojects)
    _build_dynamic_focus_areas(file_analysis)
    _build_dynamic_tasks(file_analysis)
    _build_priority_order(file_analysis)
    _build_strategy_section(file_analysis)
    _build_prompt_footer(chunked;file_analysis)
  benchmarks/benchmark_evolution.py:
    e: parse_evolution_metrics,load_previous,save_current,run_benchmark
    parse_evolution_metrics(toon_content)
    load_previous(history_file)
    save_current(history_file;metrics)
    run_benchmark(project_path)
  scripts/benchmark_badges.py:
    e: get_shield_url,parse_evolution_metrics,parse_format_quality_report,parse_performance_report,generate_badges,generate_format_quality_badges,generate_performance_badges,create_html,main
    get_shield_url(label;message;color)
    parse_evolution_metrics(toon_content)
    parse_format_quality_report(report_path)
    parse_performance_report(report_path)
    generate_badges(metrics)
    generate_format_quality_badges(format_scores)
    generate_performance_badges(performance_data)
    create_html(badges;title)
    main()
  code2llm/analysis/pipeline_detector.py:
    e: PipelineStage,Pipeline,PipelineDetector
    PipelineStage:  # A single stage in a detected pipeline...
    Pipeline: to_dict(0)  # A detected pipeline with stages, purity info, and domain...
    PipelineDetector: __init__(2),detect(2),_build_graph(1),_find_pipeline_paths(1),_longest_path_from(3),_longest_path_in_dag(1),_build_pipelines(3),_build_stages(3),_classify_domain(2),_derive_pipeline_name(3),_get_entry_type(1),_get_exit_type(1),_resolve_callee(3),_strip_self_prefix(1),_try_same_class_resolution(3),_get_suffix_candidates(2),_select_same_class_candidate(3)  # Detect pipelines in a codebase using networkx graph analysis...
  code2llm/nlp/entity_resolution.py:
    e: Entity,EntityResolutionResult,EntityResolver
    Entity:  # Resolved entity...
    EntityResolutionResult: get_by_type(1),get_best_match(0)  # Result of entity resolution...
    EntityResolver: __init__(2),resolve(3),_extract_candidates(2),_extract_from_patterns(2),_disambiguate(2),_resolve_hierarchical(1),_resolve_aliases(1),_name_similarity(2),load_from_analysis(1),step_3a_extract_entities(2),step_3b_match_threshold(1),step_3c_disambiguate(2),step_3d_hierarchical_resolve(1),step_3e_alias_resolve(1)  # Resolve entities (functions, classes, etc.) from queries...
  code2llm/exporters/readme_exporter.py:
    e: READMEExporter
    READMEExporter(BaseExporter): export(2),_extract_insights(2),_generate_readme_content(6),_get_existing_files(1),_build_core_files_section(2),_build_llm_files_section(1),_build_viz_files_section(1)  # Export README.md with documentation of all generated files...
  code2llm/exporters/map_exporter.py:
    e: MapExporter
    MapExporter(Exporter): export(2),export_to_yaml(2),_build_module_entry(2),_build_module_exports(2),_build_module_classes_data(2),_build_module_functions_data(2),_render_header(2),_render_stats_line(4),_render_alerts_line(1),_render_hotspots_line(1),_render_module_list(1),_render_details(1),_rank_modules(1),_render_map_module(3),_render_map_class(3),_function_signature(1),_is_excluded(1),_rel_path(2),_file_line_count(1),_count_total_lines(1),_detect_languages(1),_build_alerts(0),_build_hotspots(0),_load_evolution_trend(1),_read_previous_cc_avg(0)  # Export to map.toon.yaml — structural map with a compact proj...
  code2llm/exporters/mermaid_exporter.py:
    e: MermaidExporter
    MermaidExporter(Exporter): export(2),_render_subgraphs(2),_render_edges(3),_render_cc_styles(2),_get_cc(0),export_call_graph(2),export_compact(2),_should_skip_module(2),_is_entry_point(3),_find_critical_path(2),export_flow_compact(3),export_flow_detailed(3),export_flow_full(3),_readable_id(1),_safe_module(1),_sanitize_identifier(1),_module_of(1),_resolve(2),_write(2)  # Export call graph to Mermaid format...
  code2llm/exporters/project_yaml/health.py:
    e: build_health,build_alerts,count_duplicates
    build_health(result;modules)
    build_alerts(result)
    count_duplicates(result)
  code2llm/exporters/project_yaml/hotspots.py:
    e: build_hotspots,hotspot_note,build_refactoring
    build_hotspots(result)
    hotspot_note(fi;fan_out)
    build_refactoring(result;modules;hotspots)
  code2llm/generators/mermaid.py:
    e: validate_mermaid_file,_strip_label_segments,_is_balanced_node_line,_check_bracket_balance,_scan_brackets,_check_node_ids,_sanitize_label_text,_sanitize_node_id,fix_mermaid_file,_fix_edge_line,_fix_edge_label_pipes,_fix_subgraph_line,_fix_class_line,generate_pngs,generate_single_png,generate_with_puppeteer
    validate_mermaid_file(mmd_path)
    _strip_label_segments(s)
    _is_balanced_node_line(line)
    _check_bracket_balance(lines;errors)
    _scan_brackets(text;line_num;bracket_stack;paren_stack;errors)
    _check_node_ids(lines;errors)
    _sanitize_label_text(txt)
    _sanitize_node_id(node_id)
    fix_mermaid_file(mmd_path)
    _fix_edge_line(line)
    _fix_edge_label_pipes(line)
    _fix_subgraph_line(line)
    _fix_class_line(line)
    generate_pngs(input_dir;output_dir;timeout)
    generate_single_png(mmd_file;output_file;timeout)
    generate_with_puppeteer(mmd_file;output_file;timeout;max_text_size;max_edges)
  code2llm/cli_exports/formats.py:
    e: _export_evolution,_export_data_structures,_export_context_fallback,_export_readme,_export_project_yaml,_export_project_toon,_run_report,_export_simple_formats,_export_yaml,_export_mermaid_pngs,_export_calls,_export_calls_toon,_export_mermaid,_export_refactor_prompts,_export_index_html
    _export_evolution(args;result;output_dir)
    _export_data_structures(args;result;output_dir)
    _export_context_fallback(args;result;output_dir;formats)
    _export_readme(args;result;output_dir)
    _export_project_yaml(args;result;output_dir)
    _export_project_toon(args;result;output_dir)
    _run_report(args;project_yaml_path;output_dir)
    _export_simple_formats(args;result;output_dir;formats)
    _export_yaml(args;result;output_dir)
    _export_mermaid_pngs(args;output_dir)
    _export_calls(args;result;output_dir)
    _export_calls_toon(args;result;output_dir)
    _export_mermaid(args;result;output_dir)
    _export_refactor_prompts(args;result;output_dir)
    _export_index_html(args;output_dir)
  code2llm/core/streaming_analyzer.py:
    e: StreamingAnalyzer
    StreamingAnalyzer: __init__(2),set_progress_callback(1),cancel(0),analyze_streaming(2),_estimate_eta(3),_report_progress(4)  # Memory-efficient streaming analyzer with progress tracking...
  code2llm/core/file_analyzer.py:
    e: FileAnalyzer,_analyze_single_file
    FileAnalyzer: __init__(2),_route_to_language_analyzer(4),analyze_file(2),_analyze_python(3),_analyze_ast(4),_calculate_complexity(3),_perform_deep_analysis(4),_process_class(4),_process_function(5),_build_cfg(4),_process_cfg_block(8),_process_if_stmt(8),_process_loop_stmt(7),_process_return_stmt(6),_get_base_name(1),_get_decorator_name(1),_get_call_name(1)  # Analyzes a single file...
    _analyze_single_file(args)
  code2llm/core/lang/generic.py:
    e: analyze_generic
    analyze_generic(content;file_path;module_name;ext;stats)
  code2llm/exporters/toon/metrics.py:
    e: MetricsComputer
    MetricsComputer: __init__(0),compute_all_metrics(1),_compute_file_metrics(1),_new_file_record(1),_compute_fan_in(1),_process_function_calls(2),_process_called_by(3),_process_callee_calls(3),_handle_suffix_match(3),_compute_package_metrics(2),_compute_function_metrics(1),_compute_class_metrics(1),_compute_coupling_matrix(1),_build_function_to_module_map(1),_build_coupling_matrix(2),_resolve_callee_module(3),_compute_package_fan(1),_detect_duplicates(1),_check_class_for_duplicates(5),_calculate_duplicate_info(7),_compute_health(1),_check_duplicates_health(2),_check_god_modules_health(2),_check_smells_health(2),_check_high_cc_health(2),_compute_hotspots(1),_get_cycles(1)  # Computes all metrics for TOON export...
  code2llm/exporters/project_yaml/core.py:
    e: ProjectYAMLExporter
    ProjectYAMLExporter(Exporter): export(2),_build_project_yaml(2),_detect_primary_language(1)  # Export unified project.yaml — single source of truth for dia...
  code2llm/refactor/prompt_engine.py:
    e: PromptEngine
    PromptEngine: __init__(2),generate_prompts(0),_generate_prompt_for_smell(1),_get_template_for_type(1),_build_context_for_smell(1),_get_source_context(3),_get_instruction_for_smell(1)  # Generate refactoring prompts from analysis results and detec...
  code2llm/exporters/context_view.py:
    e: ContextViewGenerator
    ContextViewGenerator: generate(2),_render(1),_render_overview(1),_render_architecture(0),_render_exports(0),_render_hotspots(0),_render_refactoring(0),_render_guidelines(-1)  # Generate context.md from project.yaml data...
  code2llm/exporters/validate_project.py:
    e: validate_project_yaml,_check_required_keys,_cross_check_toon
    validate_project_yaml(output_dir;verbose)
    _check_required_keys(data)
    _cross_check_toon(data;toon_path)
  code2llm/exporters/evolution_exporter.py:
    e: EvolutionExporter
    EvolutionExporter(Exporter): _is_excluded(1),export(2),export_to_yaml(2),_build_context(1),_compute_func_data(1),_scan_file_sizes(1),_aggregate_file_stats(2),_make_relative_path(2),_filter_god_modules(2),_compute_god_modules(1),_compute_hub_types(1),_render_header(1),_render_next(1),_render_risks(1),_render_metrics_target(1),_render_patterns(1),_render_history(2)  # Export evolution.toon.yaml — prioritized refactoring queue...
  code2llm/exporters/project_yaml/modules.py:
    e: build_modules,group_by_file,compute_module_entry,compute_inbound_deps,build_exports,build_class_export,build_function_exports
    build_modules(result;line_counts)
    group_by_file(result)
    compute_module_entry(fpath;result;line_counts;file_funcs;file_classes)
    compute_inbound_deps(funcs;fpath;result)
    build_exports(funcs;classes;result)
    build_class_export(ci;result)
    build_function_exports(funcs;classes)
  code2llm/exporters/toon/renderer.py:
    e: ToonRenderer
    ToonRenderer: render_header(1),_detect_language_label(0),render_health(1),render_refactor(1),render_coupling(1),_select_top_packages(2),_render_coupling_header(1),_render_coupling_rows(4),_build_coupling_row(3),_coupling_row_tag(1),_render_coupling_summary(2),render_layers(1),_render_layer_package(5),_render_layer_files(4),_format_layer_file_row(1),_render_zero_line_files(1),render_duplicates(1),render_functions(1),_format_function_row(1),_render_cc_summary(2),render_hotspots(1),render_classes(1),render_pipelines(1),_trace_pipeline(3),_calculate_purity(2),render_external(1)  # Renders all sections for TOON export...
  code2llm/cli_exports/orchestrator.py:
    e: _run_exports,_export_single_project,_export_chunked_results,_get_filtered_subprojects,_process_subproject_result
    _run_exports(args;result;output_dir;source_path)
    _export_single_project(args;result;output_dir;formats;requested_formats;source_path)
    _export_chunked_results(args;result;output_dir;source_path;formats;requested_formats)
    _get_filtered_subprojects(args;source_path)
    _process_subproject_result(args;sp;output_dir)
  code2llm/core/toon_size_manager.py:
    e: get_file_size_kb,should_split_toon,split_toon_file,_parse_modules,_split_by_modules,_split_by_lines,_write_chunk,manage_toon_size
    get_file_size_kb(filepath)
    should_split_toon(filepath;max_kb)
    split_toon_file(source_file;output_dir;max_kb;prefix)
    _parse_modules(content)
    _split_by_modules(source_file;output_dir;modules;max_kb;prefix)
    _split_by_lines(source_file;output_dir;max_kb;prefix)
    _write_chunk(output_dir;prefix;chunk_num;content)
    manage_toon_size(source_file;output_dir;max_kb;prefix;verbose)
  code2llm/core/lang/go_lang.py:
    e: _analyze_go_regex,analyze_go
    _analyze_go_regex(content;file_path;module_name;stats)
    analyze_go(content;file_path;module_name;ext;stats)
  code2llm/nlp/pipeline.py:
    e: PipelineStage,NLPPipelineResult,NLPPipeline
    PipelineStage:  # Single pipeline stage result...
    NLPPipelineResult: is_successful(0),get_intent(0),get_entities(0),to_dict(0)  # Complete NLP pipeline result (4b-4e aggregation)...
    NLPPipeline: __init__(1),process(2),_step_normalize(2),_step_match_intent(1),_step_resolve_entities(3),_infer_entity_types(1),_calculate_overall_confidence(1),_calculate_entity_confidence(1),_apply_fallback(1),_format_action(1),_format_response(1),step_4a_orchestrate(1),step_4b_aggregate(1),step_4c_confidence(1),step_4d_fallback(1),step_4e_format(1)  # Main NLP processing pipeline (4a-4e)...
  code2llm/exporters/mermaid_flow_helpers.py:
    e: _filtered_functions,_entry_points,_group_functions_by_module,_classify_architecture_module,_group_architecture_functions,_select_key_functions,_append_flow_node,_render_module_subgraphs,_render_flow_edges,_append_entry_styles,_render_flow_styles,_render_architecture_view
    _filtered_functions(result;module_of;should_skip_module;include_examples)
    _entry_points(filtered_funcs;result;is_entry_point)
    _group_functions_by_module(funcs;module_of)
    _classify_architecture_module(func_name;module)
    _group_architecture_functions(funcs;module_of)
    _select_key_functions(func_names;funcs;entry_points;critical_path;get_cc;threshold)
    _append_flow_node(lines;func_name;fi;short_len;entry_points;readable_id;get_cc;high_threshold;med_threshold)
    _render_module_subgraphs(lines;modules;entry_points;short_len;readable_id;safe_module;get_cc;sort_funcs;max_funcs;high_threshold;med_threshold)
    _render_flow_edges(lines;funcs;readable_id;resolve;calls_per_function;limit)
    _append_entry_styles(lines;entry_points;readable_id;entry_limit)
    _render_flow_styles(lines;funcs;entry_points;readable_id;get_cc;high_threshold;med_threshold;high_limit;med_limit;entry_limit)
    _render_architecture_view(lines;filtered_funcs;entry_points;critical_path;module_of;readable_id;get_cc)
  code2llm/exporters/context_exporter.py:
    e: ContextExporter
    ContextExporter(Exporter): export(2),_get_overview(1),_detect_languages(0),_get_architecture_by_module(1),_get_important_entries(1),_get_key_entry_points(1),_get_process_flows(2),_get_key_classes(1),_get_data_transformations(1),_get_behavioral_patterns(1),_get_api_surface(1),_get_system_interactions(1),_group_calls_by_module(2),_format_sub_flow(3),_trace_flow(5)  # Export LLM-ready analysis summary with architecture and flow...
  code2llm/exporters/flow_exporter.py:
    e: FlowExporter
    FlowExporter(Exporter): __init__(0),export(2),_build_context(1),_pipeline_to_dict(1),_compute_transforms(1),_transform_label(2),_compute_type_usage(2),_normalize_type(1),_type_label(3),_classify_side_effects(2),_compute_contracts(4),_build_stage_contract(4),_infer_invariant(2),_is_excluded(1)  # Export to flow.toon — data-flow focused format.

Sections: P...
  code2llm/analysis/type_inference.py:
    e: TypeInferenceEngine
    TypeInferenceEngine: __init__(1),enrich_function(1),get_arg_types(1),get_return_type(1),get_typed_signature(1),extract_all_types(1),_extract_from_node(2),_extract_args(1),_annotation_to_str(1),_ann_constant(1),_ann_name(1),_ann_attribute(1),_ann_subscript(1),_ann_tuple(1),_ann_binop(1),_infer_from_name(1),_infer_arg_type(1)  # Extract and infer type information from Python source files...
  code2llm/core/large_repo.py:
    e: SubProject,HierarchicalRepoSplitter,should_use_chunking,get_analysis_plan
    SubProject:  # Represents a sub-project within a larger repository...
    HierarchicalRepoSplitter: __init__(2),get_analysis_plan(1),_split_hierarchically(1),_merge_small_l1_dirs(2),_split_level2_consolidated(3),_categorize_subdirs(2),_process_large_dirs(3),_process_level1_files(2),_merge_small_dirs(3),_chunk_by_files(5),_collect_files_in_dir(2),_collect_files_recursive(2),_collect_root_files(1),_count_py_files(1),_contains_python_files(1),_should_skip_file(1),_calculate_priority(2),_get_level1_dirs(1)  # Splits large repositories using hierarchical approach.

Stra...
    should_use_chunking(project_path;size_threshold_kb)
    get_analysis_plan(project_path;size_limit_kb)
  code2llm/analysis/call_graph.py:
    e: CallGraphExtractor
    CallGraphExtractor(ast.NodeVisitor): __init__(1),extract(3),_calculate_metrics(0),visit_Import(1),visit_ImportFrom(1),visit_ClassDef(1),visit_FunctionDef(1),visit_AsyncFunctionDef(1),visit_Call(1),_qualified_name(1),_resolve_call(1),_resolve_with_astroid(1),_expr_to_str(1)  # Extract call graph from AST...
  code2llm/core/refactoring.py:
    e: RefactoringAnalyzer
    RefactoringAnalyzer: __init__(2),perform_refactoring_analysis(1),_build_call_graph(1),_calculate_centrality(2),_detect_cycles(2),_detect_communities(2),_analyze_coupling(1),_detect_smells(1),_detect_dead_code(1),_map_dead_code_to_items(2),_mark_reachable_items(1)  # Performs refactoring analysis on code...
  code2llm/core/streaming/prioritizer.py:
    e: FilePriority,SmartPrioritizer
    FilePriority:  # Priority scoring for file analysis order...
    SmartPrioritizer: __init__(1),prioritize_files(2),_build_import_graph(1),_check_has_main(1)  # Smart file prioritization for optimal analysis order...
  code2llm/core/lang/rust.py:
    e: analyze_rust
    analyze_rust(content;file_path;module_name;ext;stats)
  code2llm/exporters/toon/__init__.py:
    e: ToonExporter
    ToonExporter: __init__(0),export(2),export_to_yaml(2),_build_header_dict(1),_build_health_dict(1),_build_refactor_dict(1),_build_pipelines_dict(1),_build_layers_dict(1),_build_coupling_dict(1),_build_external_dict(1),_is_excluded(1)  # Export to toon v2 plain-text format — scannable, sorted by s...
  code2llm/patterns/detector.py:
    e: PatternDetector
    PatternDetector: __init__(1),detect_patterns(1),_detect_recursion(1),_detect_state_machines(1),_detect_factory_pattern(1),_detect_singleton(1),_detect_strategy_pattern(1),_check_returns_classes(2)  # Detect behavioral patterns in code...
  code2llm/analysis/utils/ast_helpers.py:
    e: get_ast,find_function_node,expr_to_str
    get_ast(filepath;registry)
    find_function_node(tree;name;line)
    expr_to_str(node)
  code2llm/core/repo_files.py:
    e: _get_gitignore_parser,should_skip_file,collect_files_in_dir,collect_root_files,count_py_files,contains_python_files,get_level1_dirs,calculate_priority
    _get_gitignore_parser(project_path)
    should_skip_file(file_str;project_path;gitignore_parser)
    collect_files_in_dir(dir_path;project_path)
    collect_root_files(project_path)
    count_py_files(path)
    contains_python_files(dir_path)
    get_level1_dirs(project_path)
    calculate_priority(name;level)
  code2llm/core/models.py:
    e: BaseModel,FlowNode,FlowEdge,FunctionInfo,ClassInfo,ModuleInfo,Pattern,CodeSmell,Mutation,DataFlow,AnalysisResult
    BaseModel: to_dict(1),_filter_compact(1)  # Base class for models with automated serialization...
    FlowNode(BaseModel):  # Represents a node in the control flow graph...
    FlowEdge(BaseModel):  # Represents an edge in the control flow graph...
    FunctionInfo(BaseModel):  # Information about a function/method...
    ClassInfo(BaseModel):  # Information about a class...
    ModuleInfo(BaseModel):  # Information about a module/package...
    Pattern(BaseModel):  # Detected behavioral pattern...
    CodeSmell(BaseModel):  # Represents a detected code smell...
    Mutation(BaseModel):  # Represents a mutation of a variable/object...
    DataFlow(BaseModel):  # Represents data flow for a variable...
    AnalysisResult(BaseModel): get_function_count(0),get_class_count(0),get_node_count(0),get_edge_count(0)  # Complete analysis result for a project...
  code2llm/core/lang/php.py:
    e: _parse_php_metadata,_adjust_qualified_names,_extract_php_traits,analyze_php
    _parse_php_metadata(content;module_name;result)
    _adjust_qualified_names(result;module_name;namespace)
    _extract_php_traits(content;file_path;module_name;namespace;result;stats)
    analyze_php(content;file_path;module_name;ext;stats)
  code2llm/exporters/yaml_exporter.py:
    e: YAMLExporter
    YAMLExporter(Exporter): __init__(0),export(4),export_grouped(2),export_data_flow(3),export_data_structures(3),export_separated(3),export_split(3),export_calls(4),_collect_edges(3),_process_function_calls(8),_should_add_edge(2),_create_edge(2),_build_nodes(2),_create_node(3),_count_calls_in(2),_group_by_module(1),_build_calls_data(4),_resolve_callee(1),_get_cc(0),export_calls_toon(4),_render_calls_header(4),_render_hubs(1),_render_modules(3),_render_edges(1)  # Export to YAML format...
  code2llm/exporters/toon/helpers.py:
    e: _is_excluded,_rel_path,_package_of,_package_of_module,_traits_from_cfg,_dup_file_set,_hotspot_description,_scan_line_counts
    _is_excluded(path)
    _rel_path(fpath;project_path)
    _package_of(rel_path)
    _package_of_module(module_name)
    _traits_from_cfg(fi;result)
    _dup_file_set(ctx)
    _hotspot_description(fi;fan_out)
    _scan_line_counts(project_path)
  code2llm/parsers/toon_parser.py:
    e: _parse_header_line,_parse_stats_line,_parse_health_line,_parse_functions_line,_parse_classes_line,_parse_hotspots_line,_detect_section,parse_toon_content,is_toon_file,load_toon
    _parse_header_line(line;data)
    _parse_stats_line(line;data)
    _parse_health_line(line_stripped;data)
    _parse_functions_line(line_stripped;data)
    _parse_classes_line(line_stripped;data)
    _parse_hotspots_line(line_stripped;data)
    _detect_section(line)
    parse_toon_content(content)
    is_toon_file(filepath)
    load_toon(filepath)
  validate_toon.py:
    e: load_yaml,load_file,extract_functions_from_yaml,extract_functions_from_toon,extract_classes_from_yaml,extract_classes_from_toon,analyze_class_differences,extract_modules_from_yaml,extract_modules_from_toon,compare_basic_stats,compare_functions,compare_classes,compare_modules,validate_toon_completeness,_run_single_file_mode,_run_comparison_mode,_compare_all_aspects,_print_comparison_summary,main
    load_yaml(filepath)
    load_file(filepath)
    extract_functions_from_yaml(yaml_data)
    extract_functions_from_toon(toon_data)
    extract_classes_from_yaml(yaml_data)
    extract_classes_from_toon(toon_data)
    analyze_class_differences(yaml_data;toon_data)
    extract_modules_from_yaml(yaml_data)
    extract_modules_from_toon(toon_data)
    compare_basic_stats(yaml_data;toon_data)
    compare_functions(yaml_data;toon_data)
    compare_classes(yaml_data;toon_data)
    compare_modules(yaml_data;toon_data)
    validate_toon_completeness(toon_data)
    _run_single_file_mode(file_path)
    _run_comparison_mode(yaml_path;toon_path)
    _compare_all_aspects(yaml_data;toon_data)
    _print_comparison_summary(results)
    main()
  benchmarks/benchmark_optimizations.py:
    e: clear_caches,run_analysis,benchmark_cold_vs_warm,print_summary,main
    clear_caches(project_path)
    run_analysis(project_path;config)
    benchmark_cold_vs_warm(project_path;runs)
    print_summary(results)
    main()
  code2llm/cli.py:
    e: main
    main()
  code2llm/cli_commands.py:
    e: handle_special_commands,handle_report_command,validate_and_setup,print_start_info,validate_chunked_output,_get_chunk_dirs,_validate_chunks,_validate_single_chunk,_get_file_sizes,_print_chunk_errors,_print_validation_summary,generate_llm_context
    handle_special_commands()
    handle_report_command(args_list)
    validate_and_setup(args)
    print_start_info(args;source_path;output_dir)
    validate_chunked_output(output_dir;args)
    _get_chunk_dirs(output_dir)
    _validate_chunks(chunk_dirs;required_files)
    _validate_single_chunk(chunk_dir;required_files)
    _get_file_sizes(chunk_dir;required_files)
    _print_chunk_errors(chunk_name;chunk_issues)
    _print_validation_summary(chunk_dirs;valid_chunks;issues)
    generate_llm_context(args_list)
  code2llm/analysis/coupling.py:
    e: CouplingAnalyzer
    CouplingAnalyzer: __init__(1),analyze(0),_analyze_module_interactions(0),_detect_data_leakage(0),_detect_shared_state(0)  # Analyze coupling between modules...
  code2llm/analysis/smells.py:
    e: SmellDetector
    SmellDetector: __init__(1),detect(0),_detect_god_functions(0),_detect_god_modules(0),_detect_feature_envy(0),_detect_data_clumps(0),_detect_shotgun_surgery(0),_detect_bottlenecks(0),_detect_circular_dependencies(0)  # Detect code smells from analysis results...
  code2llm/analysis/dfg.py:
    e: DFGExtractor
    DFGExtractor(ast.NodeVisitor): __init__(1),extract(3),visit_FunctionDef(1),visit_Assign(1),visit_AugAssign(1),visit_For(1),visit_Call(1),_extract_targets(1),_get_names(1),_extract_names(1),_expr_to_str(1),_build_data_flow_edges(0)  # Extract Data Flow Graph from AST...
  code2llm/core/gitignore.py:
    e: _GitIgnoreEntry,GitIgnoreParser,load_gitignore_patterns
    _GitIgnoreEntry: __init__(3)  # Single parsed gitignore rule...
    GitIgnoreParser: __init__(1),_load_gitignore(1),_parse_entry(1),_pattern_to_regex(1),is_ignored(2)  # Parse and apply .gitignore patterns to file paths...
    load_gitignore_patterns(project_path)
  code2llm/core/lang/ts_extractors.py:
    e: _get_node_text,_find_name_node,_extract_functions_ts,_extract_classes_ts,extract_declarations_ts
    _get_node_text(node;source_bytes)
    _find_name_node(node)
    _extract_functions_ts(tree;source_bytes;lang;module_name;file_path)
    _extract_classes_ts(tree;source_bytes;lang;module_name;file_path)
    extract_declarations_ts(tree;source_bytes;ext;file_path;module_name)
  code2llm/core/lang/ts_parser.py:
    e: TreeSitterParser,_init_tree_sitter,_get_language,_get_parser,get_parser,parse_source,is_available
    TreeSitterParser: __init__(0),parse(2),supports(1)  # Unified tree-sitter parser for all supported languages.

Usa...
    _init_tree_sitter()
    _get_language(ext)
    _get_parser(ext)
    get_parser()
    parse_source(content;ext)
    is_available()
  code2llm/nlp/intent_matching.py:
    e: IntentMatch,IntentMatchingResult,IntentMatcher
    IntentMatch:  # Single intent match result...
    IntentMatchingResult: get_best_intent(0),get_confidence(0)  # Result of intent matching...
    IntentMatcher: __init__(2),match(2),_fuzzy_match(1),_keyword_match(1),_apply_context(3),_combine_matches(1),_resolve_multi_intent(1),_calculate_similarity(2),step_2a_fuzzy_match(2),step_2b_semantic_match(2),step_2c_keyword_match(2),step_2d_context_score(2),step_2e_resolve_intents(1)  # Match queries to intents using fuzzy and keyword matching...
  code2llm/exporters/article_view.py:
    e: ArticleViewGenerator
    ArticleViewGenerator: generate(2),_render(1),_render_frontmatter(0),_render_health_summary(1),_render_alerts(0),_render_hotspots(0),_render_roadmap(0),_render_evolution(0),_render_footer(-1)  # Generate status.md — publishable project health article...
  code2llm/exporters/html_dashboard.py:
    e: HTMLDashboardGenerator
    HTMLDashboardGenerator: generate(2),_render(1),_health_verdict(0),_build_evolution_section(0),_build_language_breakdown(0),_build_module_lines_chart(0),_build_module_funcs_chart(0),_build_top_modules_html(0),_build_alerts_html(0),_build_hotspots_html(0),_build_refactoring_html(0),_assemble_html(0),_render_evolution_section(0),_render_evolution_script(0)  # Generate dashboard.html from project.yaml data...
  code2llm/exporters/toon/module_detail.py:
    e: ModuleDetailRenderer
    ModuleDetailRenderer: render_details(1),_rank_modules_by_cc(1),_render_module_detail(4),_get_module_exports(2),_render_module_classes(4),_get_method_items(2),_find_root_method(1),_render_standalone_funcs(3),_render_call_chain(5)  # Renders detailed module information...
  benchmarks/reporting.py:
    e: _print_header,_print_scores_table,_print_problems_detail,_print_pipelines_detail,_print_structural_features,_print_gap_analysis,print_results,build_report,save_report
    _print_header()
    _print_scores_table(scores)
    _print_problems_detail(scores)
    _print_pipelines_detail(scores)
    _print_structural_features(scores)
    _print_gap_analysis(scores)
    print_results(scores)
    build_report(scores)
    save_report(report;filename)
  benchmarks/benchmark_performance.py:
    e: save_report,create_test_project,benchmark_original_analyzer,benchmark_streaming_analyzer,benchmark_with_strategies,print_comparison,main
    save_report(results;filename)
    create_test_project(size)
    benchmark_original_analyzer(project_path;runs)
    benchmark_streaming_analyzer(project_path;runs)
    benchmark_with_strategies(project_path)
    print_comparison(original;streaming)
    main()
  code2llm/core/__init__.py:
    e: __getattr__
    __getattr__(name)
  code2llm/nlp/normalization.py:
    e: NormalizationResult,QueryNormalizer
    NormalizationResult:  # Result of query normalization...
    QueryNormalizer: __init__(1),normalize(2),_unicode_normalize(1),_lowercase(1),_remove_punctuation(1),_normalize_whitespace(1),_remove_stopwords(2),_tokenize(1),step_1a_lowercase(1),step_1b_remove_punctuation(1),step_1c_normalize_whitespace(1),step_1d_unicode_normalize(1),step_1e_remove_stopwords(2)  # Normalize queries for consistent processing...
  code2llm/exporters/toon_view.py:
    e: ToonViewGenerator
    ToonViewGenerator: generate(2),_render(1),_render_header(0),_render_health(0),_render_alerts(0),_render_modules(0),_render_hotspots(0),_render_refactoring(0),_render_evolution(0)  # Generate project.toon.yaml from project.yaml data...
  code2llm/exporters/project_yaml/evolution.py:
    e: build_evolution,load_previous_evolution
    build_evolution(health;total_lines;prev_evolution)
    load_previous_evolution(output_path)
  code2llm/cli_exports/code2logic.py:
    e: _export_code2logic,_should_run_code2logic,_check_code2logic_installed,_build_code2logic_cmd,_run_code2logic,_handle_code2logic_error,_find_code2logic_output,_normalize_code2logic_output
    _export_code2logic(args;source_path;output_dir;formats)
    _should_run_code2logic(formats)
    _check_code2logic_installed()
    _build_code2logic_cmd(args;source_path;output_dir)
    _run_code2logic(cmd;verbose)
    _handle_code2logic_error(res;cmd)
    _find_code2logic_output(output_dir;res)
    _normalize_code2logic_output(found;target;args)
  benchmarks/format_evaluator.py:
    e: FormatScore,_detect_problems,_detect_pipelines,_detect_hub_types,_check_structural_features,evaluate_format
    FormatScore:  # Wynik oceny pojedynczego formatu...
    _detect_problems(content)
    _detect_pipelines(content)
    _detect_hub_types(content)
    _check_structural_features(content)
    evaluate_format(name;content;path)
  code2llm/core/file_cache.py:
    e: FileCache
    FileCache: __init__(2),_get_cache_key_stat(1),_get_cache_key(2),_get_cache_path(1),get(2),put(3),get_fast(1),put_fast(2),clear(0)  # Cache for parsed AST files...
  code2llm/core/ast_registry.py:
    e: ASTRegistry
    ASTRegistry: __init__(0),get_global(0),reset_global(0),get_ast(1),get_source(1),invalidate(1),clear(0),__len__(0),__repr__(0)  # Parse each file exactly once; share the AST across all analy...
  code2llm/analysis/cfg.py:
    e: CFGExtractor
    CFGExtractor(ast.NodeVisitor): __init__(1),extract(3),new_node(2),connect(4),visit_FunctionDef(1),visit_AsyncFunctionDef(1),visit_If(1),visit_For(1),visit_While(1),visit_Try(1),visit_Assign(1),visit_Return(1),visit_Expr(1),_qualified_name(1),_extract_condition(1),_expr_to_str(1),_format_except(1)  # Extract Control Flow Graph from AST...
  code2llm/core/streaming/incremental.py:
    e: IncrementalAnalyzer
    IncrementalAnalyzer: __init__(1),_load_state(0),_save_state(1),get_changed_files(1),_get_module_name(2)  # Incremental analysis with change detection...
  code2llm/exporters/index_generator.py:
    e: IndexHTMLGenerator
    IndexHTMLGenerator: __init__(1),generate(0),_scan_files(0),_read_file_content(2),_escape_html(1),_format_size(1),_render(1)  # Generate index.html for browsing all generated files...
  scripts/bump_version.py:
    e: get_current_version,parse_version,format_version,bump_version,update_pyproject_toml,update_version_file,main
    get_current_version()
    parse_version(version_str)
    format_version(major;minor;patch)
    bump_version(version_type)
    update_pyproject_toml(new_version)
    update_version_file(new_version)
    main()
  badges/server.py:
    e: index,generate_badges,get_badges
    index()
    generate_badges()
    get_badges()
  benchmarks/benchmark_format_quality.py:
    e: _print_benchmark_header,_print_ground_truth_info,_generate_format_outputs,_create_offline_scores,run_benchmark
    _print_benchmark_header()
    _print_ground_truth_info(project_path)
    _generate_format_outputs(result;output_dir)
    _create_offline_scores()
    run_benchmark()
  code2llm/core/incremental.py:
    e: IncrementalAnalyzer,_file_signature
    IncrementalAnalyzer: __init__(1),needs_analysis(1),get_cached_result(1),update(2),invalidate(1),save(0),clear(0),_load_cache(0),_normalize_key(1)  # Track file signatures to skip unchanged files on subsequent ...
    _file_signature(filepath)
  code2llm/core/export_pipeline.py:
    e: SharedExportContext,ExportPipeline
    SharedExportContext: __init__(1),_compute_metrics_summary(0),_compute_cc_distribution(0)  # Pre-computed context shared across all exporters.

Lazy-comp...
    ExportPipeline: __init__(1),run(2)  # Run multiple exporters with a single shared context.

Usage:...
  code2llm/core/streaming/cache.py:
    e: StreamingFileCache
    StreamingFileCache: __init__(2),_get_cache_key(2),_evict_if_needed(0),get(2),put(3)  # Memory-efficient cache with LRU eviction...
  code2llm/__init__.py:
    e: __getattr__
    __getattr__(name)
  code2llm/exporters/json_exporter.py:
    e: JSONExporter
    JSONExporter(Exporter): export(4)  # Export to JSON format...
  code2llm/exporters/report_generators.py:
    e: load_project_yaml
    load_project_yaml(path)
  demo_langs/valid/sample.java:
    e: User,UserService
    User: User(-1),getId(-1),getName(-1)
    UserService: addUser(-1),getUser(-1),processUsers(-1),main(-1)
  setup.py:
    e: read_readme
    read_readme()
  code2llm/api.py:
    e: analyze,analyze_file
    analyze(project_path;config)
    analyze_file(file_path;config)
  code2llm/cli_parser.py:
    e: get_version,create_parser
    get_version()
    create_parser()
  code2llm/analysis/__init__.py:
    e: __getattr__
    __getattr__(name)
  benchmarks/project_generator.py:
    e: create_core_py,create_etl_py,create_validation_py,create_utils_py,add_validator_to_core,create_ground_truth_project
    create_core_py(project)
    create_etl_py(project)
    create_validation_py(project)
    create_utils_py(project)
    add_validator_to_core(project)
    create_ground_truth_project(base_dir)
  code2llm/core/lang/cpp.py:
    e: analyze_cpp
    analyze_cpp(content;file_path;module_name;ext;stats)
  code2llm/core/lang/csharp.py:
    e: analyze_csharp
    analyze_csharp(content;file_path;module_name;ext;stats)
  code2llm/core/lang/java.py:
    e: analyze_java
    analyze_java(content;file_path;module_name;ext;stats)
  code2llm/core/lang/typescript.py:
    e: get_typescript_patterns,get_typescript_lang_config,analyze_typescript_js
    get_typescript_patterns()
    get_typescript_lang_config()
    analyze_typescript_js(content;file_path;module_name;ext;stats)
  code2llm/nlp/config.py:
    e: NormalizationConfig,IntentMatchingConfig,EntityResolutionConfig,MultilingualConfig,NLPConfig
    NormalizationConfig:  # Configuration for query normalization...
    IntentMatchingConfig:  # Configuration for intent matching...
    EntityResolutionConfig:  # Configuration for entity resolution...
    MultilingualConfig:  # Configuration for multilingual processing...
    NLPConfig: from_yaml(1),to_yaml(1)  # Main NLP pipeline configuration...
  code2llm/exporters/base.py:
    e: Exporter
    Exporter(ABC): export(2)  # Abstract base class for all exporters...
  orchestrator.sh:
  project2.sh:
  project.sh:
  benchmarks/benchmark_constants.py:
  code2llm/__main__.py:
  code2llm/analysis/utils/__init__.py:
  code2llm/core/config.py:
    e: AnalysisMode,PerformanceConfig,FilterConfig,DepthConfig,OutputConfig,Config
    AnalysisMode(str,Enum):  # Available analysis modes...
    PerformanceConfig:  # Performance optimization settings...
    FilterConfig:  # Filtering options to reduce analysis scope...
    DepthConfig:  # Depth limiting for control flow analysis...
    OutputConfig:  # Output formatting options...
    Config:  # Analysis configuration with performance optimizations...
  code2llm/core/streaming/__init__.py:
  code2llm/core/streaming/strategies.py:
    e: ScanStrategy
    ScanStrategy:  # Scanning methodology configuration...
  code2llm/core/lang/__init__.py:
  code2llm/nlp/__init__.py:
  code2llm/exporters/project_yaml_exporter.py:
  code2llm/exporters/__init__.py:
  code2llm/exporters/llm_exporter.py:
  code2llm/exporters/flow_constants.py:
  code2llm/exporters/project_yaml/__init__.py:
  code2llm/exporters/project_yaml/constants.py:
  code2llm/generators/__init__.py:
  code2llm/cli_exports/__init__.py:
  code2llm/refactor/__init__.py:
  code2llm/patterns/__init__.py:
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

## Call Graph

*357 nodes · 383 edges · 66 modules · CC̄=4.1*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `normalize_llm_task` *(in code2llm.generators.llm_task)* | 14 ⚠ | 1 | 43 | **44** |
| `render_llm_flow_md` *(in code2llm.generators.llm_flow)* | 10 ⚠ | 1 | 42 | **43** |
| `create_parser` *(in code2llm.cli_parser)* | 1 | 1 | 40 | **41** |
| `main` *(in benchmarks.benchmark_performance)* | 1 | 0 | 41 | **41** |
| `analyze_class_differences` *(in validate_toon)* | 6 | 1 | 39 | **40** |
| `_summarize_functions` *(in code2llm.generators.llm_flow)* | 14 ⚠ | 1 | 35 | **36** |
| `run_benchmark` *(in benchmarks.benchmark_evolution)* | 9 | 0 | 34 | **34** |
| `analyze_rust` *(in code2llm.core.lang.rust)* | 9 | 1 | 31 | **32** |

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

## Intent

High-performance Python code flow analysis with optimized TOON format - CFG, DFG, call graphs, and intelligent code queries
