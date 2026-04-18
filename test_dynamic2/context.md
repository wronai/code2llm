## Overview

- **Project**: .
- **Analysis Mode**: static
- **Total Functions**: 823
- **Total Classes**: 104
- **Modules**: 102
- **Entry Points**: 0

### examples.functional_refactoring_example
- **Functions**: 50
- **Classes**: 15
- **File**: `functional_refactoring_example.py`

### code2llm.exporters.toon.metrics
- **Functions**: 27
- **Classes**: 1
- **File**: `metrics.py`

### code2llm.generators.llm_flow
- **Functions**: 24
- **Classes**: 1
- **File**: `llm_flow.py`

### code2llm.exporters.toon.renderer
- **Functions**: 21
- **Classes**: 1
- **File**: `renderer.py`

### code2llm.core.large_repo
- **Functions**: 20
- **Classes**: 2
- **File**: `large_repo.py`

### code2llm.nlp.pipeline
- **Functions**: 20
- **Classes**: 3
- **File**: `pipeline.py`

### code2llm.analysis.type_inference
- **Functions**: 18
- **Classes**: 1
- **File**: `type_inference.py`

### code2llm.analysis.side_effects
- **Functions**: 17
- **Classes**: 2
- **File**: `side_effects.py`

### code2llm.analysis.cfg
- **Functions**: 17
- **Classes**: 1
- **File**: `cfg.py`

### code2llm.exporters.project_yaml_exporter
- **Functions**: 17
- **Classes**: 1
- **File**: `project_yaml_exporter.py`

### code2llm.analysis.data_analysis
- **Functions**: 16
- **Classes**: 1
- **File**: `data_analysis.py`

### code2llm.nlp.entity_resolution
- **Functions**: 16
- **Classes**: 3
- **File**: `entity_resolution.py`

### code2llm.generators.mermaid
- **Functions**: 16
- **File**: `mermaid.py`

### code2llm.core.core.file_analyzer
- **Functions**: 16
- **Classes**: 1
- **File**: `file_analyzer.py`

### root.validate_toon
- **Functions**: 15
- **File**: `validate_toon.py`

### code2llm.nlp.intent_matching
- **Functions**: 15
- **Classes**: 3
- **File**: `intent_matching.py`

### code2llm.exporters.evolution_exporter
- **Functions**: 15
- **Classes**: 1
- **File**: `evolution_exporter.py`

### code2llm.generators.llm_task
- **Functions**: 15
- **File**: `llm_task.py`

### batch_1.validate_toon
- **Functions**: 15
- **File**: `validate_toon.py`

### code2llm.analysis.pipeline_detector
- **Functions**: 14
- **Classes**: 3
- **File**: `pipeline_detector.py`

## Key Entry Points

Main execution flows into the system:

## Process Flows

Key execution flows identified:

### code2llm.exporters.toon.metrics.MetricsComputer
> Computes all metrics for TOON export.
- **Methods**: 27
- **Key Methods**: code2llm.exporters.toon.metrics.MetricsComputer.__init__, code2llm.exporters.toon.metrics.MetricsComputer.compute_all_metrics, code2llm.exporters.toon.metrics.MetricsComputer._compute_file_metrics, code2llm.exporters.toon.metrics.MetricsComputer._new_file_record, code2llm.exporters.toon.metrics.MetricsComputer._compute_fan_in, code2llm.exporters.toon.metrics.MetricsComputer._process_function_calls, code2llm.exporters.toon.metrics.MetricsComputer._process_called_by, code2llm.exporters.toon.metrics.MetricsComputer._process_callee_calls, code2llm.exporters.toon.metrics.MetricsComputer._handle_suffix_match, code2llm.exporters.toon.metrics.MetricsComputer._compute_package_metrics

### code2llm.exporters.toon.renderer.ToonRenderer
> Renders all sections for TOON export.
- **Methods**: 21
- **Key Methods**: code2llm.exporters.toon.renderer.ToonRenderer.render_header, code2llm.exporters.toon.renderer.ToonRenderer.render_health, code2llm.exporters.toon.renderer.ToonRenderer.render_refactor, code2llm.exporters.toon.renderer.ToonRenderer.render_coupling, code2llm.exporters.toon.renderer.ToonRenderer._select_top_packages, code2llm.exporters.toon.renderer.ToonRenderer._render_coupling_header, code2llm.exporters.toon.renderer.ToonRenderer._render_coupling_rows, code2llm.exporters.toon.renderer.ToonRenderer._build_coupling_row, code2llm.exporters.toon.renderer.ToonRenderer._coupling_row_tag, code2llm.exporters.toon.renderer.ToonRenderer._render_coupling_summary

### code2llm.analysis.cfg.CFGExtractor
> Extract Control Flow Graph from AST.
- **Methods**: 17
- **Key Methods**: code2llm.analysis.cfg.CFGExtractor.__init__, code2llm.analysis.cfg.CFGExtractor.extract, code2llm.analysis.cfg.CFGExtractor.new_node, code2llm.analysis.cfg.CFGExtractor.connect, code2llm.analysis.cfg.CFGExtractor.visit_FunctionDef, code2llm.analysis.cfg.CFGExtractor.visit_AsyncFunctionDef, code2llm.analysis.cfg.CFGExtractor.visit_If, code2llm.analysis.cfg.CFGExtractor.visit_For, code2llm.analysis.cfg.CFGExtractor.visit_While, code2llm.analysis.cfg.CFGExtractor.visit_Try
- **Inherits**: ast.NodeVisitor

### code2llm.analysis.data_analysis.DataAnalyzer
> Analyze data flows, structures, and optimization opportunities.
- **Methods**: 16
- **Key Methods**: code2llm.analysis.data_analysis.DataAnalyzer.analyze_data_flow, code2llm.analysis.data_analysis.DataAnalyzer.analyze_data_structures, code2llm.analysis.data_analysis.DataAnalyzer._find_data_pipelines, code2llm.analysis.data_analysis.DataAnalyzer._find_state_patterns, code2llm.analysis.data_analysis.DataAnalyzer._find_data_dependencies, code2llm.analysis.data_analysis.DataAnalyzer._find_event_flows, code2llm.analysis.data_analysis.DataAnalyzer._detect_types_from_name, code2llm.analysis.data_analysis.DataAnalyzer._create_type_entry, code2llm.analysis.data_analysis.DataAnalyzer._update_type_stats, code2llm.analysis.data_analysis.DataAnalyzer._analyze_data_types

### code2llm.nlp.pipeline.NLPPipeline
> Main NLP processing pipeline (4a-4e).
- **Methods**: 16
- **Key Methods**: code2llm.nlp.pipeline.NLPPipeline.__init__, code2llm.nlp.pipeline.NLPPipeline.process, code2llm.nlp.pipeline.NLPPipeline._step_normalize, code2llm.nlp.pipeline.NLPPipeline._step_match_intent, code2llm.nlp.pipeline.NLPPipeline._step_resolve_entities, code2llm.nlp.pipeline.NLPPipeline._infer_entity_types, code2llm.nlp.pipeline.NLPPipeline._calculate_overall_confidence, code2llm.nlp.pipeline.NLPPipeline._calculate_entity_confidence, code2llm.nlp.pipeline.NLPPipeline._apply_fallback, code2llm.nlp.pipeline.NLPPipeline._format_action

### code2llm.exporters.evolution_exporter.EvolutionExporter
> Export evolution.toon — prioritized refactoring queue.
- **Methods**: 15
- **Key Methods**: code2llm.exporters.evolution_exporter.EvolutionExporter._is_excluded, code2llm.exporters.evolution_exporter.EvolutionExporter.export, code2llm.exporters.evolution_exporter.EvolutionExporter._build_context, code2llm.exporters.evolution_exporter.EvolutionExporter._compute_func_data, code2llm.exporters.evolution_exporter.EvolutionExporter._scan_file_sizes, code2llm.exporters.evolution_exporter.EvolutionExporter._aggregate_file_stats, code2llm.exporters.evolution_exporter.EvolutionExporter._make_relative_path, code2llm.exporters.evolution_exporter.EvolutionExporter._filter_god_modules, code2llm.exporters.evolution_exporter.EvolutionExporter._compute_god_modules, code2llm.exporters.evolution_exporter.EvolutionExporter._compute_hub_types
- **Inherits**: Exporter

### code2llm.core.core.file_analyzer.FileAnalyzer
> Analyzes a single file.
- **Methods**: 15
- **Key Methods**: code2llm.core.core.file_analyzer.FileAnalyzer.__init__, code2llm.core.core.file_analyzer.FileAnalyzer.analyze_file, code2llm.core.core.file_analyzer.FileAnalyzer._analyze_ast, code2llm.core.core.file_analyzer.FileAnalyzer._calculate_complexity, code2llm.core.core.file_analyzer.FileAnalyzer._perform_deep_analysis, code2llm.core.core.file_analyzer.FileAnalyzer._process_class, code2llm.core.core.file_analyzer.FileAnalyzer._process_function, code2llm.core.core.file_analyzer.FileAnalyzer._build_cfg, code2llm.core.core.file_analyzer.FileAnalyzer._process_cfg_block, code2llm.core.core.file_analyzer.FileAnalyzer._process_if_stmt

### code2llm.nlp.entity_resolution.EntityResolver
> Resolve entities (functions, classes, etc.) from queries.
- **Methods**: 14
- **Key Methods**: code2llm.nlp.entity_resolution.EntityResolver.__init__, code2llm.nlp.entity_resolution.EntityResolver.resolve, code2llm.nlp.entity_resolution.EntityResolver._extract_candidates, code2llm.nlp.entity_resolution.EntityResolver._extract_from_patterns, code2llm.nlp.entity_resolution.EntityResolver._disambiguate, code2llm.nlp.entity_resolution.EntityResolver._resolve_hierarchical, code2llm.nlp.entity_resolution.EntityResolver._resolve_aliases, code2llm.nlp.entity_resolution.EntityResolver._name_similarity, code2llm.nlp.entity_resolution.EntityResolver.load_from_analysis, code2llm.nlp.entity_resolution.EntityResolver.step_3a_extract_entities

### code2llm.analysis.call_graph.CallGraphExtractor
> Extract call graph from AST.
- **Methods**: 13
- **Key Methods**: code2llm.analysis.call_graph.CallGraphExtractor.__init__, code2llm.analysis.call_graph.CallGraphExtractor.extract, code2llm.analysis.call_graph.CallGraphExtractor._calculate_metrics, code2llm.analysis.call_graph.CallGraphExtractor.visit_Import, code2llm.analysis.call_graph.CallGraphExtractor.visit_ImportFrom, code2llm.analysis.call_graph.CallGraphExtractor.visit_ClassDef, code2llm.analysis.call_graph.CallGraphExtractor.visit_FunctionDef, code2llm.analysis.call_graph.CallGraphExtractor.visit_AsyncFunctionDef, code2llm.analysis.call_graph.CallGraphExtractor.visit_Call, code2llm.analysis.call_graph.CallGraphExtractor._qualified_name
- **Inherits**: ast.NodeVisitor

### code2llm.nlp.intent_matching.IntentMatcher
> Match queries to intents using fuzzy and keyword matching.
- **Methods**: 13
- **Key Methods**: code2llm.nlp.intent_matching.IntentMatcher.__init__, code2llm.nlp.intent_matching.IntentMatcher.match, code2llm.nlp.intent_matching.IntentMatcher._fuzzy_match, code2llm.nlp.intent_matching.IntentMatcher._keyword_match, code2llm.nlp.intent_matching.IntentMatcher._apply_context, code2llm.nlp.intent_matching.IntentMatcher._combine_matches, code2llm.nlp.intent_matching.IntentMatcher._resolve_multi_intent, code2llm.nlp.intent_matching.IntentMatcher._calculate_similarity, code2llm.nlp.intent_matching.IntentMatcher.step_2a_fuzzy_match, code2llm.nlp.intent_matching.IntentMatcher.step_2b_semantic_match

### code2llm.nlp.normalization.QueryNormalizer
> Normalize queries for consistent processing.
- **Methods**: 13
- **Key Methods**: code2llm.nlp.normalization.QueryNormalizer.__init__, code2llm.nlp.normalization.QueryNormalizer.normalize, code2llm.nlp.normalization.QueryNormalizer._unicode_normalize, code2llm.nlp.normalization.QueryNormalizer._lowercase, code2llm.nlp.normalization.QueryNormalizer._remove_punctuation, code2llm.nlp.normalization.QueryNormalizer._normalize_whitespace, code2llm.nlp.normalization.QueryNormalizer._remove_stopwords, code2llm.nlp.normalization.QueryNormalizer._tokenize, code2llm.nlp.normalization.QueryNormalizer.step_1a_lowercase, code2llm.nlp.normalization.QueryNormalizer.step_1b_remove_punctuation

### examples.streaming-analyzer.sample_project.database.DatabaseConnection
> Simple database connection simulator.
- **Methods**: 13
- **Key Methods**: examples.streaming-analyzer.sample_project.database.DatabaseConnection.__init__, examples.streaming-analyzer.sample_project.database.DatabaseConnection._load_data, examples.streaming-analyzer.sample_project.database.DatabaseConnection._save_data, examples.streaming-analyzer.sample_project.database.DatabaseConnection.get_user, examples.streaming-analyzer.sample_project.database.DatabaseConnection.get_user_settings, examples.streaming-analyzer.sample_project.database.DatabaseConnection.get_user_logs, examples.streaming-analyzer.sample_project.database.DatabaseConnection.update_user_settings, examples.streaming-analyzer.sample_project.database.DatabaseConnection.update_user_profile, examples.streaming-analyzer.sample_project.database.DatabaseConnection.delete_user, examples.streaming-analyzer.sample_project.database.DatabaseConnection.clear_user_data

## Data Transformation Functions

Key functions that process and transform data:

### benchmarks.benchmark_evolution.parse_evolution_metrics
> Extract metrics from evolution.toon content.
- **Output to**: toon_content.splitlines, re.search, line.strip, line.startswith, int

### validate_toon.validate_toon_completeness
> Validate toon format structure.
- **Output to**: print, print, bool, bool, bool

### benchmarks.format_evaluator.evaluate_format
> Oceń pojedynczy format względem ground truth.
- **Output to**: FormatScore, benchmarks.format_evaluator._detect_problems, sum, benchmarks.format_evaluator._detect_pipelines, sum

### scripts.benchmark_badges.parse_evolution_metrics
> Extract metrics from evolution.toon content.
- **Output to**: toon_content.splitlines, re.search, line.strip, line.startswith, m.group

### scripts.benchmark_badges.parse_format_quality_report
> Parse format quality JSON report.
- **Output to**: report_path.exists, json.loads, data.get, report_path.read_text

### scripts.benchmark_badges.parse_performance_report
> Parse performance JSON report.
- **Output to**: report_path.exists, json.loads, report_path.read_text

### scripts.benchmark_badges.generate_format_quality_badges
> Generate badges from format quality scores.
- **Output to**: enumerate, badges.append, sorted, badges.append, format_scores.items

### scripts.bump_version.parse_version
> Parse version string into tuple of (major, minor, patch)
- **Output to**: version_str.split, tuple, int

### scripts.bump_version.format_version
> Format version tuple as string

### demo_langs.valid.sample.UserService.process_users
- **Output to**: print

### code2llm.analysis.data_analysis.DataAnalyzer._identify_process_patterns
- **Output to**: result.functions.items, patterns.items, sorted, func.name.lower, indicators.items

### benchmarks.benchmark_format_quality._generate_format_outputs
> Generate all format outputs and evaluate them.
- **Output to**: format_configs.items, __import__, getattr, exporter_cls, time.time

### code2llm.cli.create_parser
> Create CLI argument parser.
- **Output to**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument

### code2llm.cli._validate_and_setup
> Validate source path and setup output directory.
- **Output to**: Path, Path, output_dir.mkdir, print, print

### code2llm.cli._validate_chunked_output
> Validate generated chunked output.

Checks:
1. All chunks have required files (analysis.toon, contex
- **Output to**: print, print, sorted, print, print

### code2llm.analysis.cfg.CFGExtractor._format_except
> Format except handler.
- **Output to**: self._expr_to_str

### code2llm.core.toon_size_manager._parse_modules
> Parse module sections from TOON content.

Returns list of (module_name, start_line, end_line).
- **Output to**: content.split, enumerate, modules.append, line.startswith, line.endswith

### code2llm.core.large_repo.HierarchicalRepoSplitter._process_large_dirs
> Process large directories with file-level chunking.
- **Output to**: self._chunk_by_files, chunks.extend

### code2llm.core.large_repo.HierarchicalRepoSplitter._process_level1_files
> Process Python files directly in level1 directory.
- **Output to**: len, chunks.append, self._chunk_by_files, chunks.extend, str

### code2llm.nlp.pipeline.NLPPipeline.process
> Process query through full pipeline (4a-4e).
- **Output to**: time.time, time.time, self._step_normalize, stages.append, time.time

### code2llm.nlp.pipeline.NLPPipeline._format_action
> 4e. Format action recommendation.
- **Output to**: result.get_intent, result.get_entities

### code2llm.nlp.pipeline.NLPPipeline._format_response
> 4e. Format human-readable response.
- **Output to**: None.join, lines.append, lines.append, lines.append, result.get_intent

### code2llm.nlp.pipeline.NLPPipeline.step_4e_format
> Step 4e: Output formatting.
- **Output to**: self._format_response

### code2llm.exporters.validate_project.validate_project_yaml
> Validate project.yaml against generated views in output_dir.

Returns (is_valid, list_of_issues).
- **Output to**: issues.extend, toon_path.exists, yaml_path.exists, issues.append, code2llm.exporters.validate_project._check_required_keys

### code2llm.exporters.context_exporter.ContextExporter._get_process_flows
- **Output to**: set, set, seen_base_names.add, self._trace_flow, ep_name.split

## System Interactions

How components interact:

```mermaid
graph TD
```

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.