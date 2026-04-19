# System Architecture Analysis

## Overview

- **Project**: .
- **Primary Language**: python
- **Languages**: python: 142, shell: 9, typescript: 1
- **Analysis Mode**: static
- **Total Functions**: 1115
- **Total Classes**: 121
- **Modules**: 152
- **Entry Points**: 0

## Architecture by Module

### examples.functional_refactoring_example
- **Functions**: 50
- **Classes**: 15
- **File**: `functional_refactoring_example.py`

### code2llm.exporters.toon.metrics
- **Functions**: 27
- **Classes**: 1
- **File**: `metrics.py`

### code2llm.exporters.toon.renderer
- **Functions**: 26
- **Classes**: 1
- **File**: `renderer.py`

### code2llm.exporters.map_exporter
- **Functions**: 25
- **Classes**: 1
- **File**: `map_exporter.py`

### code2llm.exporters.yaml_exporter
- **Functions**: 24
- **Classes**: 1
- **File**: `yaml_exporter.py`

### code2llm.generators.llm_flow
- **Functions**: 24
- **Classes**: 1
- **File**: `llm_flow.py`

### code2llm.core.large_repo
- **Functions**: 20
- **Classes**: 2
- **File**: `large_repo.py`

### code2llm.nlp.pipeline
- **Functions**: 20
- **Classes**: 3
- **File**: `pipeline.py`

### root.validate_toon
- **Functions**: 19
- **File**: `validate_toon.py`

### code2llm.exporters.mermaid_exporter
- **Functions**: 19
- **Classes**: 1
- **File**: `mermaid_exporter.py`

### batch_1.validate_toon
- **Functions**: 19
- **File**: `validate_toon.py`

### test_python_only_examples_tests.validate_toon
- **Functions**: 19
- **File**: `validate_toon.py`

### code2llm.analysis.data_analysis
- **Functions**: 18
- **Classes**: 1
- **File**: `data_analysis.py`

### code2llm.analysis.pipeline_detector
- **Functions**: 18
- **Classes**: 3
- **File**: `pipeline_detector.py`

### code2llm.core.persistent_cache
- **Functions**: 18
- **Classes**: 1
- **File**: `persistent_cache.py`

### code2llm.core.file_analyzer
- **Functions**: 18
- **Classes**: 1
- **File**: `file_analyzer.py`

### code2llm.cli_exports.prompt
- **Functions**: 18
- **File**: `prompt.py`

### code2llm.analysis.type_inference
- **Functions**: 17
- **Classes**: 1
- **File**: `type_inference.py`

### code2llm.analysis.cfg
- **Functions**: 17
- **Classes**: 1
- **File**: `cfg.py`

### code2llm.exporters.evolution_exporter
- **Functions**: 17
- **Classes**: 1
- **File**: `evolution_exporter.py`

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
- **Methods**: 26
- **Key Methods**: code2llm.exporters.toon.renderer.ToonRenderer.render_header, code2llm.exporters.toon.renderer.ToonRenderer._detect_language_label, code2llm.exporters.toon.renderer.ToonRenderer.render_health, code2llm.exporters.toon.renderer.ToonRenderer.render_refactor, code2llm.exporters.toon.renderer.ToonRenderer.render_coupling, code2llm.exporters.toon.renderer.ToonRenderer._select_top_packages, code2llm.exporters.toon.renderer.ToonRenderer._render_coupling_header, code2llm.exporters.toon.renderer.ToonRenderer._render_coupling_rows, code2llm.exporters.toon.renderer.ToonRenderer._build_coupling_row, code2llm.exporters.toon.renderer.ToonRenderer._coupling_row_tag

### code2llm.exporters.map_exporter.MapExporter
> Export to map.toon.yaml — structural map with a compact project header.

Keys: M=modules, D=details,
- **Methods**: 25
- **Key Methods**: code2llm.exporters.map_exporter.MapExporter.export, code2llm.exporters.map_exporter.MapExporter.export_to_yaml, code2llm.exporters.map_exporter.MapExporter._build_module_entry, code2llm.exporters.map_exporter.MapExporter._build_module_exports, code2llm.exporters.map_exporter.MapExporter._build_module_classes_data, code2llm.exporters.map_exporter.MapExporter._build_module_functions_data, code2llm.exporters.map_exporter.MapExporter._render_header, code2llm.exporters.map_exporter.MapExporter._render_stats_line, code2llm.exporters.map_exporter.MapExporter._render_alerts_line, code2llm.exporters.map_exporter.MapExporter._render_hotspots_line
- **Inherits**: BaseExporter

### code2llm.exporters.yaml_exporter.YAMLExporter
> Export to YAML format.
- **Methods**: 24
- **Key Methods**: code2llm.exporters.yaml_exporter.YAMLExporter.__init__, code2llm.exporters.yaml_exporter.YAMLExporter.export, code2llm.exporters.yaml_exporter.YAMLExporter.export_grouped, code2llm.exporters.yaml_exporter.YAMLExporter.export_data_flow, code2llm.exporters.yaml_exporter.YAMLExporter.export_data_structures, code2llm.exporters.yaml_exporter.YAMLExporter.export_separated, code2llm.exporters.yaml_exporter.YAMLExporter.export_split, code2llm.exporters.yaml_exporter.YAMLExporter.export_calls, code2llm.exporters.yaml_exporter.YAMLExporter._collect_edges, code2llm.exporters.yaml_exporter.YAMLExporter._process_function_calls
- **Inherits**: BaseExporter

### code2llm.exporters.mermaid_exporter.MermaidExporter
> Export call graph to Mermaid format.
- **Methods**: 19
- **Key Methods**: code2llm.exporters.mermaid_exporter.MermaidExporter.export, code2llm.exporters.mermaid_exporter.MermaidExporter._render_subgraphs, code2llm.exporters.mermaid_exporter.MermaidExporter._render_edges, code2llm.exporters.mermaid_exporter.MermaidExporter._render_cc_styles, code2llm.exporters.mermaid_exporter.MermaidExporter._get_cc, code2llm.exporters.mermaid_exporter.MermaidExporter.export_call_graph, code2llm.exporters.mermaid_exporter.MermaidExporter.export_compact, code2llm.exporters.mermaid_exporter.MermaidExporter._should_skip_module, code2llm.exporters.mermaid_exporter.MermaidExporter._is_entry_point, code2llm.exporters.mermaid_exporter.MermaidExporter._find_critical_path
- **Inherits**: BaseExporter

### code2llm.core.large_repo.HierarchicalRepoSplitter
> Splits large repositories using hierarchical approach.

Strategy:
1. First pass: level 1 folders
2. 
- **Methods**: 18
- **Key Methods**: code2llm.core.large_repo.HierarchicalRepoSplitter.__init__, code2llm.core.large_repo.HierarchicalRepoSplitter.get_analysis_plan, code2llm.core.large_repo.HierarchicalRepoSplitter._split_hierarchically, code2llm.core.large_repo.HierarchicalRepoSplitter._merge_small_l1_dirs, code2llm.core.large_repo.HierarchicalRepoSplitter._split_level2_consolidated, code2llm.core.large_repo.HierarchicalRepoSplitter._categorize_subdirs, code2llm.core.large_repo.HierarchicalRepoSplitter._process_large_dirs, code2llm.core.large_repo.HierarchicalRepoSplitter._process_level1_files, code2llm.core.large_repo.HierarchicalRepoSplitter._merge_small_dirs, code2llm.core.large_repo.HierarchicalRepoSplitter._chunk_by_files

### code2llm.analysis.type_inference.TypeInferenceEngine
> Extract and infer type information from Python source files.

Operates on source files referenced by
- **Methods**: 17
- **Key Methods**: code2llm.analysis.type_inference.TypeInferenceEngine.__init__, code2llm.analysis.type_inference.TypeInferenceEngine.enrich_function, code2llm.analysis.type_inference.TypeInferenceEngine.get_arg_types, code2llm.analysis.type_inference.TypeInferenceEngine.get_return_type, code2llm.analysis.type_inference.TypeInferenceEngine.get_typed_signature, code2llm.analysis.type_inference.TypeInferenceEngine.extract_all_types, code2llm.analysis.type_inference.TypeInferenceEngine._extract_from_node, code2llm.analysis.type_inference.TypeInferenceEngine._extract_args, code2llm.analysis.type_inference.TypeInferenceEngine._annotation_to_str, code2llm.analysis.type_inference.TypeInferenceEngine._ann_constant

### code2llm.analysis.pipeline_detector.PipelineDetector
> Detect pipelines in a codebase using networkx graph analysis.

Builds a call graph as a DiGraph, fin
- **Methods**: 17
- **Key Methods**: code2llm.analysis.pipeline_detector.PipelineDetector.__init__, code2llm.analysis.pipeline_detector.PipelineDetector.detect, code2llm.analysis.pipeline_detector.PipelineDetector._build_graph, code2llm.analysis.pipeline_detector.PipelineDetector._find_pipeline_paths, code2llm.analysis.pipeline_detector.PipelineDetector._longest_path_from, code2llm.analysis.pipeline_detector.PipelineDetector._longest_path_in_dag, code2llm.analysis.pipeline_detector.PipelineDetector._build_pipelines, code2llm.analysis.pipeline_detector.PipelineDetector._build_stages, code2llm.analysis.pipeline_detector.PipelineDetector._classify_domain, code2llm.analysis.pipeline_detector.PipelineDetector._derive_pipeline_name

### code2llm.analysis.cfg.CFGExtractor
> Extract Control Flow Graph from AST.
- **Methods**: 17
- **Key Methods**: code2llm.analysis.cfg.CFGExtractor.__init__, code2llm.analysis.cfg.CFGExtractor.extract, code2llm.analysis.cfg.CFGExtractor.new_node, code2llm.analysis.cfg.CFGExtractor.connect, code2llm.analysis.cfg.CFGExtractor.visit_FunctionDef, code2llm.analysis.cfg.CFGExtractor.visit_AsyncFunctionDef, code2llm.analysis.cfg.CFGExtractor.visit_If, code2llm.analysis.cfg.CFGExtractor.visit_For, code2llm.analysis.cfg.CFGExtractor.visit_While, code2llm.analysis.cfg.CFGExtractor.visit_Try
- **Inherits**: ast.NodeVisitor

### code2llm.core.file_analyzer.FileAnalyzer
> Analyzes a single file.
- **Methods**: 17
- **Key Methods**: code2llm.core.file_analyzer.FileAnalyzer.__init__, code2llm.core.file_analyzer.FileAnalyzer._route_to_language_analyzer, code2llm.core.file_analyzer.FileAnalyzer.analyze_file, code2llm.core.file_analyzer.FileAnalyzer._analyze_python, code2llm.core.file_analyzer.FileAnalyzer._analyze_ast, code2llm.core.file_analyzer.FileAnalyzer._calculate_complexity, code2llm.core.file_analyzer.FileAnalyzer._perform_deep_analysis, code2llm.core.file_analyzer.FileAnalyzer._process_class, code2llm.core.file_analyzer.FileAnalyzer._process_function, code2llm.core.file_analyzer.FileAnalyzer._build_cfg

### code2llm.exporters.evolution_exporter.EvolutionExporter
> Export evolution.toon.yaml — prioritized refactoring queue.
- **Methods**: 17
- **Key Methods**: code2llm.exporters.evolution_exporter.EvolutionExporter._is_excluded, code2llm.exporters.evolution_exporter.EvolutionExporter.export, code2llm.exporters.evolution_exporter.EvolutionExporter.export_to_yaml, code2llm.exporters.evolution_exporter.EvolutionExporter._build_context, code2llm.exporters.evolution_exporter.EvolutionExporter._compute_func_data, code2llm.exporters.evolution_exporter.EvolutionExporter._scan_file_sizes, code2llm.exporters.evolution_exporter.EvolutionExporter._aggregate_file_stats, code2llm.exporters.evolution_exporter.EvolutionExporter._make_relative_path, code2llm.exporters.evolution_exporter.EvolutionExporter._filter_god_modules, code2llm.exporters.evolution_exporter.EvolutionExporter._compute_god_modules
- **Inherits**: BaseExporter

### code2llm.analysis.data_analysis.DataAnalyzer
> Analyze data flows, structures, and optimization opportunities.
- **Methods**: 16
- **Key Methods**: code2llm.analysis.data_analysis.DataAnalyzer.analyze_data_flow, code2llm.analysis.data_analysis.DataAnalyzer.analyze_data_structures, code2llm.analysis.data_analysis.DataAnalyzer._find_data_pipelines, code2llm.analysis.data_analysis.DataAnalyzer._find_state_patterns, code2llm.analysis.data_analysis.DataAnalyzer._find_data_dependencies, code2llm.analysis.data_analysis.DataAnalyzer._find_event_flows, code2llm.analysis.data_analysis.DataAnalyzer._detect_types_from_name, code2llm.analysis.data_analysis.DataAnalyzer._create_type_entry, code2llm.analysis.data_analysis.DataAnalyzer._update_type_stats, code2llm.analysis.data_analysis.DataAnalyzer._analyze_data_types

### code2llm.nlp.pipeline.NLPPipeline
> Main NLP processing pipeline (4a-4e).
- **Methods**: 16
- **Key Methods**: code2llm.nlp.pipeline.NLPPipeline.__init__, code2llm.nlp.pipeline.NLPPipeline.process, code2llm.nlp.pipeline.NLPPipeline._step_normalize, code2llm.nlp.pipeline.NLPPipeline._step_match_intent, code2llm.nlp.pipeline.NLPPipeline._step_resolve_entities, code2llm.nlp.pipeline.NLPPipeline._infer_entity_types, code2llm.nlp.pipeline.NLPPipeline._calculate_overall_confidence, code2llm.nlp.pipeline.NLPPipeline._calculate_entity_confidence, code2llm.nlp.pipeline.NLPPipeline._apply_fallback, code2llm.nlp.pipeline.NLPPipeline._format_action

### code2llm.exporters.context_exporter.ContextExporter
> Export LLM-ready analysis summary with architecture and flows.

Output: context.md — architecture na
- **Methods**: 15
- **Key Methods**: code2llm.exporters.context_exporter.ContextExporter.export, code2llm.exporters.context_exporter.ContextExporter._get_overview, code2llm.exporters.context_exporter.ContextExporter._detect_languages, code2llm.exporters.context_exporter.ContextExporter._get_architecture_by_module, code2llm.exporters.context_exporter.ContextExporter._get_important_entries, code2llm.exporters.context_exporter.ContextExporter._get_key_entry_points, code2llm.exporters.context_exporter.ContextExporter._get_process_flows, code2llm.exporters.context_exporter.ContextExporter._get_key_classes, code2llm.exporters.context_exporter.ContextExporter._get_data_transformations, code2llm.exporters.context_exporter.ContextExporter._get_behavioral_patterns
- **Inherits**: BaseExporter

### code2llm.core.persistent_cache.PersistentCache
> Content-addressed persistent cache stored in ~/.code2llm/.

Thread-safety: manifest writes are prote
- **Methods**: 14
- **Key Methods**: code2llm.core.persistent_cache.PersistentCache.__init__, code2llm.core.persistent_cache.PersistentCache.content_hash, code2llm.core.persistent_cache.PersistentCache.get_file_result, code2llm.core.persistent_cache.PersistentCache.put_file_result, code2llm.core.persistent_cache.PersistentCache.get_changed_files, code2llm.core.persistent_cache.PersistentCache.get_export_cache_dir, code2llm.core.persistent_cache.PersistentCache.create_export_cache_dir, code2llm.core.persistent_cache.PersistentCache.mark_export_complete, code2llm.core.persistent_cache.PersistentCache.save, code2llm.core.persistent_cache.PersistentCache.cache_size_mb

### code2llm.nlp.entity_resolution.EntityResolver
> Resolve entities (functions, classes, etc.) from queries.
- **Methods**: 14
- **Key Methods**: code2llm.nlp.entity_resolution.EntityResolver.__init__, code2llm.nlp.entity_resolution.EntityResolver.resolve, code2llm.nlp.entity_resolution.EntityResolver._extract_candidates, code2llm.nlp.entity_resolution.EntityResolver._extract_from_patterns, code2llm.nlp.entity_resolution.EntityResolver._disambiguate, code2llm.nlp.entity_resolution.EntityResolver._resolve_hierarchical, code2llm.nlp.entity_resolution.EntityResolver._resolve_aliases, code2llm.nlp.entity_resolution.EntityResolver._name_similarity, code2llm.nlp.entity_resolution.EntityResolver.load_from_analysis, code2llm.nlp.entity_resolution.EntityResolver.step_3a_extract_entities

### code2llm.exporters.html_dashboard.HTMLDashboardGenerator
> Generate dashboard.html from project.yaml data.
- **Methods**: 14
- **Key Methods**: code2llm.exporters.html_dashboard.HTMLDashboardGenerator.generate, code2llm.exporters.html_dashboard.HTMLDashboardGenerator._render, code2llm.exporters.html_dashboard.HTMLDashboardGenerator._health_verdict, code2llm.exporters.html_dashboard.HTMLDashboardGenerator._build_evolution_section, code2llm.exporters.html_dashboard.HTMLDashboardGenerator._build_language_breakdown, code2llm.exporters.html_dashboard.HTMLDashboardGenerator._build_module_lines_chart, code2llm.exporters.html_dashboard.HTMLDashboardGenerator._build_module_funcs_chart, code2llm.exporters.html_dashboard.HTMLDashboardGenerator._build_top_modules_html, code2llm.exporters.html_dashboard.HTMLDashboardGenerator._build_alerts_html, code2llm.exporters.html_dashboard.HTMLDashboardGenerator._build_hotspots_html

### code2llm.exporters.flow_exporter.FlowExporter
> Export to flow.toon — data-flow focused format.

Sections: PIPELINES, TRANSFORMS, CONTRACTS, DATA_TY
- **Methods**: 14
- **Key Methods**: code2llm.exporters.flow_exporter.FlowExporter.__init__, code2llm.exporters.flow_exporter.FlowExporter.export, code2llm.exporters.flow_exporter.FlowExporter._build_context, code2llm.exporters.flow_exporter.FlowExporter._pipeline_to_dict, code2llm.exporters.flow_exporter.FlowExporter._compute_transforms, code2llm.exporters.flow_exporter.FlowExporter._transform_label, code2llm.exporters.flow_exporter.FlowExporter._compute_type_usage, code2llm.exporters.flow_exporter.FlowExporter._normalize_type, code2llm.exporters.flow_exporter.FlowExporter._type_label, code2llm.exporters.flow_exporter.FlowExporter._classify_side_effects
- **Inherits**: BaseExporter

### examples.streaming-analyzer.sample_project.database.DatabaseConnection
> Simple database connection simulator.
- **Methods**: 13
- **Key Methods**: examples.streaming-analyzer.sample_project.database.DatabaseConnection.__init__, examples.streaming-analyzer.sample_project.database.DatabaseConnection._load_data, examples.streaming-analyzer.sample_project.database.DatabaseConnection._save_data, examples.streaming-analyzer.sample_project.database.DatabaseConnection.get_user, examples.streaming-analyzer.sample_project.database.DatabaseConnection.get_user_settings, examples.streaming-analyzer.sample_project.database.DatabaseConnection.get_user_logs, examples.streaming-analyzer.sample_project.database.DatabaseConnection.update_user_settings, examples.streaming-analyzer.sample_project.database.DatabaseConnection.update_user_profile, examples.streaming-analyzer.sample_project.database.DatabaseConnection.delete_user, examples.streaming-analyzer.sample_project.database.DatabaseConnection.clear_user_data

### code2llm.analysis.side_effects.SideEffectDetector
> Detect side effects in Python functions via AST analysis.

Scans function bodies for IO operations, 
- **Methods**: 13
- **Key Methods**: code2llm.analysis.side_effects.SideEffectDetector.__init__, code2llm.analysis.side_effects.SideEffectDetector.analyze_function, code2llm.analysis.side_effects.SideEffectDetector.analyze_all, code2llm.analysis.side_effects.SideEffectDetector.get_purity_score, code2llm.analysis.side_effects.SideEffectDetector._scan_node, code2llm.analysis.side_effects.SideEffectDetector._check_calls, code2llm.analysis.side_effects.SideEffectDetector._check_assignments, code2llm.analysis.side_effects.SideEffectDetector._check_globals, code2llm.analysis.side_effects.SideEffectDetector._check_yield, code2llm.analysis.side_effects.SideEffectDetector._check_delete

## Data Transformation Functions

Key functions that process and transform data:

### test_langs.valid.sample.ProcessUsers
- **Output to**: test_langs.valid.sample.func, test_langs.valid.sample.Printf

### test_langs.valid.sample.UserService.processUsers
- **Output to**: test_langs.valid.sample.println, test_langs.valid.sample.User.getName

### test_langs.valid.sample.process_users

### validate_toon.validate_toon_completeness
> Validate toon format structure.
- **Output to**: print, print, bool, bool, bool

### examples.streaming-analyzer.sample_project.auth.AuthManager.validate_session
> Validate session and return user ID.
- **Output to**: self.sessions.get

### examples.streaming-analyzer.sample_project.api.APIHandler.process_request
> Process API request.
- **Output to**: self._check_rate_limit, self._get_stats, self._get_user_info, self._health_check

### examples.streaming-analyzer.sample_project.api.APIHandler.format_response
> Format API response.
- **Output to**: json.dumps

### examples.streaming-analyzer.sample_project.utils.validate_input
> Validate input data.
- **Output to**: isinstance, isinstance

### examples.streaming-analyzer.sample_project.utils.format_output
> Format output data.
- **Output to**: isinstance, json.dumps, isinstance, json.dumps, str

### examples.streaming-analyzer.sample_project.utils.transform_data
> Transform data fields.
- **Output to**: item.copy, transformations.items, transformed.append, None.upper, None.lower

### benchmarks.benchmark_evolution.parse_evolution_metrics
> Extract metrics from evolution.toon content.
- **Output to**: toon_content.splitlines, re.search, line.strip, line.startswith, int

### examples.streaming-analyzer.sample_project.main.Application.process_request
> Process a user request with complex logic.
- **Output to**: request.action.startswith, examples.streaming-analyzer.sample_project.utils.validate_input, print, self.auth.authenticate, print

### benchmarks.format_evaluator.evaluate_format
> Oceń pojedynczy format względem ground truth.
- **Output to**: FormatScore, benchmarks.format_evaluator._detect_problems, sum, benchmarks.format_evaluator._detect_pipelines, sum

### scripts.bump_version.parse_version
> Parse version string into tuple of (major, minor, patch)
- **Output to**: version_str.split, tuple, int

### scripts.bump_version.format_version
> Format version tuple as string

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

### test_python_only.valid.sample.UserService.process_users
- **Output to**: print

### code2llm.cli_parser.create_parser
> Create CLI argument parser.
- **Output to**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument

### benchmarks.benchmark_format_quality._generate_format_outputs
> Generate all format outputs and evaluate them.
- **Output to**: format_configs.items, __import__, getattr, exporter_cls, time.time

### code2llm.cli_commands.validate_and_setup
> Validate source path and setup output directory.
- **Output to**: Path, Path, output_dir.mkdir, print, print

### code2llm.cli_commands.validate_chunked_output
> Validate generated chunked output.

Checks:
1. All chunks have required files (analysis.toon, contex
- **Output to**: code2llm.cli_commands._get_chunk_dirs, code2llm.cli_commands._validate_chunks, code2llm.cli_commands._print_validation_summary, output_dir.exists, print

### code2llm.cli_commands._validate_chunks
> Validate all chunks and return issues and valid chunks.
- **Output to**: print, print, sorted, print, code2llm.cli_commands._validate_single_chunk

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `code2llm.core.analyzer.ProjectAnalyzer.analyze_project` - 56 calls
- `code2llm.cli_parser.create_parser` - 43 calls
- `code2llm.generators.llm_task.normalize_llm_task` - 43 calls
- `code2llm.generators.llm_flow.render_llm_flow_md` - 42 calls
- `benchmarks.benchmark_performance.main` - 41 calls
- `validate_toon.analyze_class_differences` - 39 calls
- `benchmarks.benchmark_evolution.run_benchmark` - 34 calls
- `code2llm.cli_commands.handle_cache_command` - 33 calls
- `code2llm.core.lang.rust.analyze_rust` - 31 calls
- `benchmarks.benchmark_optimizations.benchmark_cold_vs_warm` - 30 calls
- `benchmarks.benchmark_performance.create_test_project` - 29 calls
- `code2llm.nlp.pipeline.NLPPipeline.process` - 29 calls
- `validate_toon.compare_modules` - 26 calls
- `code2llm.core.streaming_analyzer.StreamingAnalyzer.analyze_streaming` - 26 calls
- `code2llm.exporters.mermaid_exporter.MermaidExporter.export_compact` - 26 calls
- `benchmarks.benchmark_evolution.parse_evolution_metrics` - 25 calls
- `code2llm.exporters.mermaid_exporter.MermaidExporter.export_call_graph` - 25 calls
- `code2llm.exporters.toon.ToonExporter.export` - 25 calls
- `validate_toon.compare_functions` - 24 calls
- `code2llm.exporters.context_exporter.ContextExporter.export` - 24 calls
- `code2llm.generators.mermaid.generate_single_png` - 24 calls
- `scripts.benchmark_badges.main` - 23 calls
- `benchmarks.format_evaluator.evaluate_format` - 22 calls
- `benchmarks.benchmark_format_quality.run_benchmark` - 22 calls
- `code2llm.exporters.evolution_exporter.EvolutionExporter.export` - 22 calls
- `code2llm.exporters.evolution_exporter.EvolutionExporter.export_to_yaml` - 22 calls
- `code2llm.exporters.flow_exporter.FlowExporter.export` - 22 calls
- `code2llm.cli_commands.generate_llm_context` - 21 calls
- `code2llm.core.analyzer.ProjectAnalyzer.analyze_files` - 20 calls
- `code2llm.core.lang.generic.analyze_generic` - 20 calls
- `code2llm.exporters.project_yaml.hotspots.build_refactoring` - 20 calls
- `examples.streaming-analyzer.demo.demo_incremental_analysis` - 19 calls
- `validate_toon.compare_classes` - 19 calls
- `scripts.benchmark_badges.parse_evolution_metrics` - 19 calls
- `code2llm.core.streaming.prioritizer.SmartPrioritizer.prioritize_files` - 19 calls
- `code2llm.core.streaming.scanner.StreamingScanner.quick_scan_file` - 19 calls
- `code2llm.core.lang.ruby.analyze_ruby` - 19 calls
- `code2llm.exporters.map_exporter.MapExporter.export_to_yaml` - 19 calls
- `code2llm.exporters.yaml_exporter.YAMLExporter.export_grouped` - 19 calls
- `code2llm.exporters.yaml_exporter.YAMLExporter.export_calls_toon` - 19 calls

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