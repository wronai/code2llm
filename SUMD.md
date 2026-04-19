# code2llm

High-performance Python code flow analysis with optimized TOON format - CFG, DFG, call graphs, and intelligent code queries

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Dependencies](#dependencies)
- [Source Map](#source-map)
- [Intent](#intent)

## Metadata

- **name**: `code2llm`
- **version**: `0.5.120`
- **python_requires**: `>=3.13`
- **license**: MIT
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Taskfile.yml, Makefile, src/

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

## Source Map

- test_langs/valid/sample.py
- test_langs/invalid/sample_bad.py
- examples/litellm/run.py
- examples/functional_refactoring_example.py
- examples/streaming-analyzer/demo.py
- examples/streaming-analyzer/sample_project/auth.py
- examples/streaming-analyzer/sample_project/__init__.py
- examples/streaming-analyzer/sample_project/api.py
- examples/streaming-analyzer/sample_project/database.py
- examples/streaming-analyzer/sample_project/utils.py
- examples/streaming-analyzer/sample_project/main.py
- examples/streaming-analyzer/test_example.py
- benchmarks/test_performance.py
- benchmarks/benchmark_evolution.py
- benchmarks/reporting.py
- benchmarks/format_evaluator.py
- benchmarks/benchmark_format_quality.py
- benchmarks/benchmark_performance.py
- benchmarks/project_generator.py
- benchmarks/benchmark_optimizations.py
- benchmarks/benchmark_constants.py
- tests/test_multilanguage_e2e.py
- tests/test_nonpython_cc_calls.py
- tests/test_edge_cases.py
- tests/test_flow_exporter.py
- tests/test_pipeline_detector.py
- tests/test_advanced_analysis.py
- tests/test_refactoring_engine.py
- tests/test_nlp_pipeline.py
- tests/test_calls_toon_export.py
- tests/test_prompt_engine.py
- tests/test_prompt_txt.py
- tests/test_toon_v2.py
- tests/test_persistent_cache.py
- tests/test_format_quality.py
- tests/test_deep_analysis.py
- tests/test_project_toon_export.py
- tests/test_analyzer.py
- scripts/benchmark_badges.py
- scripts/bump_version.py
- badges/server.py
- setup.py
- validate_toon.py
- test_python_only/valid/__init__.py
- test_python_only/valid/sample.py
- test_python_only/invalid/__init__.py
- test_python_only/invalid/sample_bad.py
- code2llm/cli.py
- code2llm/cli_analysis.py
- code2llm/analysis/data_analysis.py
