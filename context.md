# System Architecture Analysis

## Overview

- **Project**: .
- **Analysis Mode**: static
- **Total Functions**: 750
- **Total Classes**: 99
- **Modules**: 90
- **Entry Points**: 0

## Architecture by Module

### examples.functional_refactoring_example
- **Functions**: 50
- **Classes**: 15
- **File**: `functional_refactoring_example.py`

### code2llm.cli_exports
- **Functions**: 28
- **File**: `cli_exports.py`

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

## Key Classes

### code2llm.exporters.toon.metrics.MetricsComputer
> Computes all metrics for TOON export.
- **Methods**: 27
- **Key Methods**: code2llm.exporters.toon.metrics.MetricsComputer.__init__, code2llm.exporters.toon.metrics.MetricsComputer.compute_all_metrics, code2llm.exporters.toon.metrics.MetricsComputer._compute_file_metrics, code2llm.exporters.toon.metrics.MetricsComputer._new_file_record, code2llm.exporters.toon.metrics.MetricsComputer._compute_fan_in, code2llm.exporters.toon.metrics.MetricsComputer._process_function_calls, code2llm.exporters.toon.metrics.MetricsComputer._process_called_by, code2llm.exporters.toon.metrics.MetricsComputer._process_callee_calls, code2llm.exporters.toon.metrics.MetricsComputer._handle_suffix_match, code2llm.exporters.toon.metrics.MetricsComputer._compute_package_metrics

### code2llm.exporters.toon.renderer.ToonRenderer
> Renders all sections for TOON export.
- **Methods**: 21
- **Key Methods**: code2llm.exporters.toon.renderer.ToonRenderer.render_header, code2llm.exporters.toon.renderer.ToonRenderer.render_health, code2llm.exporters.toon.renderer.ToonRenderer.render_refactor, code2llm.exporters.toon.renderer.ToonRenderer.render_coupling, code2llm.exporters.toon.renderer.ToonRenderer._select_top_packages, code2llm.exporters.toon.renderer.ToonRenderer._render_coupling_header, code2llm.exporters.toon.renderer.ToonRenderer._render_coupling_rows, code2llm.exporters.toon.renderer.ToonRenderer._build_coupling_row, code2llm.exporters.toon.renderer.ToonRenderer._coupling_row_tag, code2llm.exporters.toon.renderer.ToonRenderer._render_coupling_summary

### code2llm.analysis.type_inference.TypeInferenceEngine
> Extract and infer type information from Python source files.

Operates on source files referenced by
- **Methods**: 18
- **Key Methods**: code2llm.analysis.type_inference.TypeInferenceEngine.__init__, code2llm.analysis.type_inference.TypeInferenceEngine.enrich_function, code2llm.analysis.type_inference.TypeInferenceEngine.get_arg_types, code2llm.analysis.type_inference.TypeInferenceEngine.get_return_type, code2llm.analysis.type_inference.TypeInferenceEngine.get_typed_signature, code2llm.analysis.type_inference.TypeInferenceEngine.extract_all_types, code2llm.analysis.type_inference.TypeInferenceEngine._get_ast, code2llm.analysis.type_inference.TypeInferenceEngine._find_function_node, code2llm.analysis.type_inference.TypeInferenceEngine._extract_from_node, code2llm.analysis.type_inference.TypeInferenceEngine._extract_args

### code2llm.core.large_repo.HierarchicalRepoSplitter
> Splits large repositories using hierarchical approach.

Strategy:
1. First pass: level 1 folders
2. 
- **Methods**: 18
- **Key Methods**: code2llm.core.large_repo.HierarchicalRepoSplitter.__init__, code2llm.core.large_repo.HierarchicalRepoSplitter.get_analysis_plan, code2llm.core.large_repo.HierarchicalRepoSplitter._split_hierarchically, code2llm.core.large_repo.HierarchicalRepoSplitter._merge_small_l1_dirs, code2llm.core.large_repo.HierarchicalRepoSplitter._get_level1_dirs, code2llm.core.large_repo.HierarchicalRepoSplitter._split_level2_consolidated, code2llm.core.large_repo.HierarchicalRepoSplitter._categorize_subdirs, code2llm.core.large_repo.HierarchicalRepoSplitter._process_large_dirs, code2llm.core.large_repo.HierarchicalRepoSplitter._process_level1_files, code2llm.core.large_repo.HierarchicalRepoSplitter._merge_small_dirs

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

### code2llm.analysis.side_effects.SideEffectDetector
> Detect side effects in Python functions via AST analysis.

Scans function bodies for IO operations, 
- **Methods**: 15
- **Key Methods**: code2llm.analysis.side_effects.SideEffectDetector.__init__, code2llm.analysis.side_effects.SideEffectDetector.analyze_function, code2llm.analysis.side_effects.SideEffectDetector.analyze_all, code2llm.analysis.side_effects.SideEffectDetector.get_purity_score, code2llm.analysis.side_effects.SideEffectDetector._scan_node, code2llm.analysis.side_effects.SideEffectDetector._check_calls, code2llm.analysis.side_effects.SideEffectDetector._check_assignments, code2llm.analysis.side_effects.SideEffectDetector._check_globals, code2llm.analysis.side_effects.SideEffectDetector._check_yield, code2llm.analysis.side_effects.SideEffectDetector._check_delete

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

### code2llm.exporters.context_exporter.ContextExporter
> Export LLM-ready analysis summary with architecture and flows.

Output: context.md — architecture na
- **Methods**: 14
- **Key Methods**: code2llm.exporters.context_exporter.ContextExporter.export, code2llm.exporters.context_exporter.ContextExporter._get_overview, code2llm.exporters.context_exporter.ContextExporter._get_architecture_by_module, code2llm.exporters.context_exporter.ContextExporter._get_important_entries, code2llm.exporters.context_exporter.ContextExporter._get_key_entry_points, code2llm.exporters.context_exporter.ContextExporter._get_process_flows, code2llm.exporters.context_exporter.ContextExporter._get_key_classes, code2llm.exporters.context_exporter.ContextExporter._get_data_transformations, code2llm.exporters.context_exporter.ContextExporter._get_behavioral_patterns, code2llm.exporters.context_exporter.ContextExporter._get_api_surface
- **Inherits**: Exporter

### code2llm.exporters.flow_exporter.FlowExporter
> Export to flow.toon — data-flow focused format.

Sections: PIPELINES, TRANSFORMS, CONTRACTS, DATA_TY
- **Methods**: 14
- **Key Methods**: code2llm.exporters.flow_exporter.FlowExporter.__init__, code2llm.exporters.flow_exporter.FlowExporter.export, code2llm.exporters.flow_exporter.FlowExporter._build_context, code2llm.exporters.flow_exporter.FlowExporter._pipeline_to_dict, code2llm.exporters.flow_exporter.FlowExporter._compute_transforms, code2llm.exporters.flow_exporter.FlowExporter._transform_label, code2llm.exporters.flow_exporter.FlowExporter._compute_type_usage, code2llm.exporters.flow_exporter.FlowExporter._normalize_type, code2llm.exporters.flow_exporter.FlowExporter._type_label, code2llm.exporters.flow_exporter.FlowExporter._classify_side_effects
- **Inherits**: Exporter

### code2llm.analysis.pipeline_detector.PipelineDetector
> Detect pipelines in a codebase using networkx graph analysis.

Builds a call graph as a DiGraph, fin
- **Methods**: 13
- **Key Methods**: code2llm.analysis.pipeline_detector.PipelineDetector.__init__, code2llm.analysis.pipeline_detector.PipelineDetector.detect, code2llm.analysis.pipeline_detector.PipelineDetector._build_graph, code2llm.analysis.pipeline_detector.PipelineDetector._find_pipeline_paths, code2llm.analysis.pipeline_detector.PipelineDetector._longest_path_from, code2llm.analysis.pipeline_detector.PipelineDetector._longest_path_in_dag, code2llm.analysis.pipeline_detector.PipelineDetector._build_pipelines, code2llm.analysis.pipeline_detector.PipelineDetector._build_stages, code2llm.analysis.pipeline_detector.PipelineDetector._classify_domain, code2llm.analysis.pipeline_detector.PipelineDetector._derive_pipeline_name

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

### code2llm.exporters.map_exporter.MapExporter
> Export to map.toon — structural map with modules, imports, signatures.

Keys: M=modules, D=details, 
- **Methods**: 13
- **Key Methods**: code2llm.exporters.map_exporter.MapExporter.export, code2llm.exporters.map_exporter.MapExporter._render_header, code2llm.exporters.map_exporter.MapExporter._render_module_list, code2llm.exporters.map_exporter.MapExporter._render_details, code2llm.exporters.map_exporter.MapExporter._rank_modules, code2llm.exporters.map_exporter.MapExporter._render_map_module, code2llm.exporters.map_exporter.MapExporter._render_map_class, code2llm.exporters.map_exporter.MapExporter._function_signature, code2llm.exporters.map_exporter.MapExporter._is_excluded, code2llm.exporters.map_exporter.MapExporter._rel_path
- **Inherits**: Exporter

### examples.streaming-analyzer.sample_project.database.DatabaseConnection
> Simple database connection simulator.
- **Methods**: 13
- **Key Methods**: examples.streaming-analyzer.sample_project.database.DatabaseConnection.__init__, examples.streaming-analyzer.sample_project.database.DatabaseConnection._load_data, examples.streaming-analyzer.sample_project.database.DatabaseConnection._save_data, examples.streaming-analyzer.sample_project.database.DatabaseConnection.get_user, examples.streaming-analyzer.sample_project.database.DatabaseConnection.get_user_settings, examples.streaming-analyzer.sample_project.database.DatabaseConnection.get_user_logs, examples.streaming-analyzer.sample_project.database.DatabaseConnection.update_user_settings, examples.streaming-analyzer.sample_project.database.DatabaseConnection.update_user_profile, examples.streaming-analyzer.sample_project.database.DatabaseConnection.delete_user, examples.streaming-analyzer.sample_project.database.DatabaseConnection.clear_user_data

### code2llm.analysis.dfg.DFGExtractor
> Extract Data Flow Graph from AST.
- **Methods**: 12
- **Key Methods**: code2llm.analysis.dfg.DFGExtractor.__init__, code2llm.analysis.dfg.DFGExtractor.extract, code2llm.analysis.dfg.DFGExtractor.visit_FunctionDef, code2llm.analysis.dfg.DFGExtractor.visit_Assign, code2llm.analysis.dfg.DFGExtractor.visit_AugAssign, code2llm.analysis.dfg.DFGExtractor.visit_For, code2llm.analysis.dfg.DFGExtractor.visit_Call, code2llm.analysis.dfg.DFGExtractor._extract_targets, code2llm.analysis.dfg.DFGExtractor._get_names, code2llm.analysis.dfg.DFGExtractor._extract_names
- **Inherits**: ast.NodeVisitor

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

### code2llm.cli_exports._export_simple_formats
> Export toon, map, flow, context, yaml, json formats.
- **Output to**: format_map.items, code2llm.cli_exports._export_yaml, JSONExporter, exporter.export, exporter_cls

### demo_langs.valid.sample.UserService.process_users
- **Output to**: print

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

### code2llm.analysis.data_analysis.DataAnalyzer._identify_process_patterns
- **Output to**: result.functions.items, patterns.items, sorted, func.name.lower, indicators.items

### benchmarks.benchmark_format_quality._generate_format_outputs
> Generate all format outputs and evaluate them.
- **Output to**: format_configs.items, __import__, getattr, exporter_cls, time.time

### code2llm.core.large_repo.HierarchicalRepoSplitter._process_large_dirs
> Process large directories with file-level chunking.
- **Output to**: self._chunk_by_files, chunks.extend

### code2llm.core.large_repo.HierarchicalRepoSplitter._process_level1_files
> Process Python files directly in level1 directory.
- **Output to**: len, chunks.append, self._chunk_by_files, chunks.extend, str

### code2llm.core.toon_size_manager._parse_modules
> Parse module sections from TOON content.

Returns list of (module_name, start_line, end_line).
- **Output to**: content.split, enumerate, modules.append, line.startswith, line.endswith

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

### code2llm.analysis.cfg.CFGExtractor._format_except
> Format except handler.
- **Output to**: self._expr_to_str

### code2llm.exporters.context_exporter.ContextExporter._get_process_flows
- **Output to**: set, set, seen_base_names.add, self._trace_flow, ep_name.split

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `validate_toon.main` - 45 calls
- `code2llm.generators.llm_task.normalize_llm_task` - 43 calls
- `code2llm.generators.llm_flow.render_llm_flow_md` - 42 calls
- `benchmarks.benchmark_performance.main` - 41 calls
- `validate_toon.analyze_class_differences` - 39 calls
- `code2llm.core.analyzer.ProjectAnalyzer.analyze_project` - 38 calls
- `code2llm.exporters.toon.ToonExporter.export` - 35 calls
- `benchmarks.benchmark_evolution.run_benchmark` - 34 calls
- `code2llm.cli.create_parser` - 31 calls
- `benchmarks.benchmark_performance.create_test_project` - 29 calls
- `code2llm.nlp.pipeline.NLPPipeline.process` - 29 calls
- `validate_toon.compare_modules` - 26 calls
- `code2llm.core.streaming_analyzer.StreamingAnalyzer.analyze_streaming` - 26 calls
- `code2llm.exporters.mermaid_exporter.MermaidExporter.export_compact` - 26 calls
- `benchmarks.benchmark_evolution.parse_evolution_metrics` - 25 calls
- `code2llm.exporters.mermaid_exporter.MermaidExporter.export_call_graph` - 25 calls
- `code2llm.exporters.context_exporter.ContextExporter.export` - 25 calls
- `validate_toon.compare_functions` - 24 calls
- `code2llm.generators.mermaid.generate_single_png` - 24 calls
- `scripts.benchmark_badges.main` - 23 calls
- `code2llm.exporters.flow_exporter.FlowExporter.export` - 23 calls
- `benchmarks.format_evaluator.evaluate_format` - 22 calls
- `benchmarks.benchmark_format_quality.run_benchmark` - 22 calls
- `code2llm.cli.generate_llm_context` - 21 calls
- `code2llm.core.analyzer.ProjectAnalyzer.analyze_files` - 20 calls
- `code2llm.exporters.evolution_exporter.EvolutionExporter.export` - 20 calls
- `validate_toon.compare_classes` - 19 calls
- `scripts.benchmark_badges.parse_evolution_metrics` - 19 calls
- `code2llm.exporters.yaml_exporter.YAMLExporter.export_grouped` - 19 calls
- `code2llm.core.streaming.prioritizer.SmartPrioritizer.prioritize_files` - 19 calls
- `code2llm.core.streaming.scanner.StreamingScanner.quick_scan_file` - 19 calls
- `examples.streaming-analyzer.demo.demo_incremental_analysis` - 19 calls
- `code2llm.exporters.flow_renderer.FlowRenderer.render_pipelines` - 18 calls
- `code2llm.generators.llm_flow.main` - 18 calls
- `validate_toon.validate_toon_completeness` - 17 calls
- `examples.litellm.run.main` - 17 calls
- `examples.streaming-analyzer.demo.main` - 17 calls
- `examples.functional_refactoring_example.generate` - 16 calls
- `examples.streaming-analyzer.demo.demo_custom_progress` - 16 calls
- `scripts.benchmark_badges.generate_performance_badges` - 15 calls

## System Interactions

How components interact:

```mermaid
graph TD
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.