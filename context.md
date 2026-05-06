# System Architecture Analysis

## Overview

- **Project**: /home/tom/github/semcod/code2llm
- **Primary Language**: python
- **Languages**: python: 343, md: 66, yaml: 46, txt: 8, shell: 7
- **Analysis Mode**: static
- **Total Functions**: 3625
- **Total Classes**: 250
- **Modules**: 492
- **Entry Points**: 0

## Architecture by Module

### map.toon
- **Functions**: 6780
- **File**: `map.toon.yaml`

### root.SUMD
- **Functions**: 554
- **File**: `SUMD.md`

### batch_1.SUMD
- **Functions**: 554
- **File**: `SUMD.md`

### project.map.toon
- **Functions**: 523
- **File**: `map.toon.yaml`

### root.SUMR
- **Functions**: 29
- **File**: `SUMR.md`

### batch_1.SUMR
- **Functions**: 29
- **File**: `SUMR.md`

### code2llm.analysis.data_analysis
- **Functions**: 28
- **Classes**: 3
- **File**: `data_analysis.py`

### analysis.data_analysis
- **Functions**: 28
- **Classes**: 3
- **File**: `data_analysis.py`

### code2llm.exporters.toon.renderer
- **Functions**: 26
- **Classes**: 1
- **File**: `renderer.py`

### exporters.toon.renderer
- **Functions**: 26
- **Classes**: 1
- **File**: `renderer.py`

### code2llm.exporters.yaml_exporter
- **Functions**: 25
- **Classes**: 1
- **File**: `yaml_exporter.py`

### exporters.yaml_exporter
- **Functions**: 25
- **Classes**: 1
- **File**: `yaml_exporter.py`

### code2llm.core.persistent_cache
- **Functions**: 22
- **Classes**: 1
- **File**: `persistent_cache.py`

### code2llm.core.analyzer
- **Functions**: 22
- **Classes**: 1
- **File**: `analyzer.py`

### core.persistent_cache
- **Functions**: 22
- **Classes**: 1
- **File**: `persistent_cache.py`

### root.validate_toon
- **Functions**: 21
- **File**: `validate_toon.py`

### docs.API
- **Functions**: 21
- **Classes**: 6
- **File**: `API.md`

### batch_1.validate_toon
- **Functions**: 21
- **File**: `validate_toon.py`

### code2llm.core.large_repo
- **Functions**: 20
- **Classes**: 2
- **File**: `large_repo.py`

### code2llm.nlp.pipeline
- **Functions**: 20
- **Classes**: 3
- **File**: `pipeline.py`

## Key Entry Points

Main execution flows into the system:

## Process Flows

Key execution flows identified:

## Key Classes

### code2llm.exporters.toon.renderer.ToonRenderer
> Renders all sections for TOON export.
- **Methods**: 26
- **Key Methods**: code2llm.exporters.toon.renderer.ToonRenderer.render_header, code2llm.exporters.toon.renderer.ToonRenderer._detect_language_label, code2llm.exporters.toon.renderer.ToonRenderer.render_health, code2llm.exporters.toon.renderer.ToonRenderer.render_refactor, code2llm.exporters.toon.renderer.ToonRenderer.render_coupling, code2llm.exporters.toon.renderer.ToonRenderer._select_top_packages, code2llm.exporters.toon.renderer.ToonRenderer._render_coupling_header, code2llm.exporters.toon.renderer.ToonRenderer._render_coupling_rows, code2llm.exporters.toon.renderer.ToonRenderer._build_coupling_row, code2llm.exporters.toon.renderer.ToonRenderer._coupling_row_tag

### exporters.toon.renderer.ToonRenderer
> Renders all sections for TOON export.
- **Methods**: 26
- **Key Methods**: exporters.toon.renderer.ToonRenderer.render_header, exporters.toon.renderer.ToonRenderer._detect_language_label, exporters.toon.renderer.ToonRenderer.render_health, exporters.toon.renderer.ToonRenderer.render_refactor, exporters.toon.renderer.ToonRenderer.render_coupling, exporters.toon.renderer.ToonRenderer._select_top_packages, exporters.toon.renderer.ToonRenderer._render_coupling_header, exporters.toon.renderer.ToonRenderer._render_coupling_rows, exporters.toon.renderer.ToonRenderer._build_coupling_row, exporters.toon.renderer.ToonRenderer._coupling_row_tag

### code2llm.exporters.yaml_exporter.YAMLExporter
> Export to YAML format.
- **Methods**: 25
- **Key Methods**: code2llm.exporters.yaml_exporter.YAMLExporter.__init__, code2llm.exporters.yaml_exporter.YAMLExporter._get_name_index, code2llm.exporters.yaml_exporter.YAMLExporter.export, code2llm.exporters.yaml_exporter.YAMLExporter.export_grouped, code2llm.exporters.yaml_exporter.YAMLExporter.export_data_flow, code2llm.exporters.yaml_exporter.YAMLExporter.export_data_structures, code2llm.exporters.yaml_exporter.YAMLExporter.export_separated, code2llm.exporters.yaml_exporter.YAMLExporter.export_split, code2llm.exporters.yaml_exporter.YAMLExporter.export_calls, code2llm.exporters.yaml_exporter.YAMLExporter._collect_edges
- **Inherits**: BaseExporter

### exporters.yaml_exporter.YAMLExporter
> Export to YAML format.
- **Methods**: 25
- **Key Methods**: exporters.yaml_exporter.YAMLExporter.__init__, exporters.yaml_exporter.YAMLExporter._get_name_index, exporters.yaml_exporter.YAMLExporter.export, exporters.yaml_exporter.YAMLExporter.export_grouped, exporters.yaml_exporter.YAMLExporter.export_data_flow, exporters.yaml_exporter.YAMLExporter.export_data_structures, exporters.yaml_exporter.YAMLExporter.export_separated, exporters.yaml_exporter.YAMLExporter.export_split, exporters.yaml_exporter.YAMLExporter.export_calls, exporters.yaml_exporter.YAMLExporter._collect_edges
- **Inherits**: BaseExporter

### code2llm.core.analyzer.ProjectAnalyzer
> Main analyzer with parallel processing.
- **Methods**: 22
- **Key Methods**: code2llm.core.analyzer.ProjectAnalyzer.__init__, code2llm.core.analyzer.ProjectAnalyzer.analyze_project, code2llm.core.analyzer.ProjectAnalyzer._resolve_project_path, code2llm.core.analyzer.ProjectAnalyzer._load_from_persistent_cache, code2llm.core.analyzer.ProjectAnalyzer._run_analysis, code2llm.core.analyzer.ProjectAnalyzer._store_to_persistent_cache, code2llm.core.analyzer.ProjectAnalyzer._build_stats, code2llm.core.analyzer.ProjectAnalyzer._print_summary, code2llm.core.analyzer.ProjectAnalyzer._post_process, code2llm.core.analyzer.ProjectAnalyzer._should_collect_file

### code2llm.core.large_repo.HierarchicalRepoSplitter
> Splits large repositories using hierarchical approach.

Strategy:
1. First pass: level 1 folders
2. 
- **Methods**: 18
- **Key Methods**: code2llm.core.large_repo.HierarchicalRepoSplitter.__init__, code2llm.core.large_repo.HierarchicalRepoSplitter.get_analysis_plan, code2llm.core.large_repo.HierarchicalRepoSplitter._split_hierarchically, code2llm.core.large_repo.HierarchicalRepoSplitter._merge_small_l1_dirs, code2llm.core.large_repo.HierarchicalRepoSplitter._split_level2_consolidated, code2llm.core.large_repo.HierarchicalRepoSplitter._categorize_subdirs, code2llm.core.large_repo.HierarchicalRepoSplitter._process_large_dirs, code2llm.core.large_repo.HierarchicalRepoSplitter._process_level1_files, code2llm.core.large_repo.HierarchicalRepoSplitter._merge_small_dirs, code2llm.core.large_repo.HierarchicalRepoSplitter._chunk_by_files

### code2llm.core.persistent_cache.PersistentCache
> Content-addressed persistent cache stored in ~/.code2llm/.

Thread-safety: manifest writes are prote
- **Methods**: 18
- **Key Methods**: code2llm.core.persistent_cache.PersistentCache.__init__, code2llm.core.persistent_cache.PersistentCache.content_hash, code2llm.core.persistent_cache.PersistentCache.get_file_result, code2llm.core.persistent_cache.PersistentCache.put_file_result, code2llm.core.persistent_cache.PersistentCache.get_changed_files, code2llm.core.persistent_cache.PersistentCache.prune_missing, code2llm.core.persistent_cache.PersistentCache.get_export_cache_dir, code2llm.core.persistent_cache.PersistentCache.create_export_cache_dir, code2llm.core.persistent_cache.PersistentCache.mark_export_complete, code2llm.core.persistent_cache.PersistentCache.save

### core.large_repo.HierarchicalRepoSplitter
> Splits large repositories using hierarchical approach.

Strategy:
1. First pass: level 1 folders
2. 
- **Methods**: 18
- **Key Methods**: core.large_repo.HierarchicalRepoSplitter.__init__, core.large_repo.HierarchicalRepoSplitter.get_analysis_plan, core.large_repo.HierarchicalRepoSplitter._split_hierarchically, core.large_repo.HierarchicalRepoSplitter._merge_small_l1_dirs, core.large_repo.HierarchicalRepoSplitter._split_level2_consolidated, core.large_repo.HierarchicalRepoSplitter._categorize_subdirs, core.large_repo.HierarchicalRepoSplitter._process_large_dirs, core.large_repo.HierarchicalRepoSplitter._process_level1_files, core.large_repo.HierarchicalRepoSplitter._merge_small_dirs, core.large_repo.HierarchicalRepoSplitter._chunk_by_files

### core.persistent_cache.PersistentCache
> Content-addressed persistent cache stored in ~/.code2llm/.

Thread-safety: manifest writes are prote
- **Methods**: 18
- **Key Methods**: core.persistent_cache.PersistentCache.__init__, core.persistent_cache.PersistentCache.content_hash, core.persistent_cache.PersistentCache.get_file_result, core.persistent_cache.PersistentCache.put_file_result, core.persistent_cache.PersistentCache.get_changed_files, core.persistent_cache.PersistentCache.prune_missing, core.persistent_cache.PersistentCache.get_export_cache_dir, core.persistent_cache.PersistentCache.create_export_cache_dir, core.persistent_cache.PersistentCache.mark_export_complete, core.persistent_cache.PersistentCache.save

### code2llm.analysis.type_inference.TypeInferenceEngine
> Extract and infer type information from Python source files.

Operates on source files referenced by
- **Methods**: 17
- **Key Methods**: code2llm.analysis.type_inference.TypeInferenceEngine.__init__, code2llm.analysis.type_inference.TypeInferenceEngine.enrich_function, code2llm.analysis.type_inference.TypeInferenceEngine.get_arg_types, code2llm.analysis.type_inference.TypeInferenceEngine.get_return_type, code2llm.analysis.type_inference.TypeInferenceEngine.get_typed_signature, code2llm.analysis.type_inference.TypeInferenceEngine.extract_all_types, code2llm.analysis.type_inference.TypeInferenceEngine._extract_from_node, code2llm.analysis.type_inference.TypeInferenceEngine._extract_args, code2llm.analysis.type_inference.TypeInferenceEngine._annotation_to_str, code2llm.analysis.type_inference.TypeInferenceEngine._ann_constant

### code2llm.core.file_analyzer.FileAnalyzer
> Analyzes a single file.
- **Methods**: 17
- **Key Methods**: code2llm.core.file_analyzer.FileAnalyzer.__init__, code2llm.core.file_analyzer.FileAnalyzer._route_to_language_analyzer, code2llm.core.file_analyzer.FileAnalyzer.analyze_file, code2llm.core.file_analyzer.FileAnalyzer._analyze_python, code2llm.core.file_analyzer.FileAnalyzer._analyze_ast, code2llm.core.file_analyzer.FileAnalyzer._calculate_complexity, code2llm.core.file_analyzer.FileAnalyzer._perform_deep_analysis, code2llm.core.file_analyzer.FileAnalyzer._process_class, code2llm.core.file_analyzer.FileAnalyzer._process_function, code2llm.core.file_analyzer.FileAnalyzer._build_cfg

### analysis.type_inference.TypeInferenceEngine
> Extract and infer type information from Python source files.

Operates on source files referenced by
- **Methods**: 17
- **Key Methods**: analysis.type_inference.TypeInferenceEngine.__init__, analysis.type_inference.TypeInferenceEngine.enrich_function, analysis.type_inference.TypeInferenceEngine.get_arg_types, analysis.type_inference.TypeInferenceEngine.get_return_type, analysis.type_inference.TypeInferenceEngine.get_typed_signature, analysis.type_inference.TypeInferenceEngine.extract_all_types, analysis.type_inference.TypeInferenceEngine._extract_from_node, analysis.type_inference.TypeInferenceEngine._extract_args, analysis.type_inference.TypeInferenceEngine._annotation_to_str, analysis.type_inference.TypeInferenceEngine._ann_constant

### code2llm.analysis.data_analysis.DataAnalyzer
> Analyze data flows, structures, and optimization opportunities.
- **Methods**: 16
- **Key Methods**: code2llm.analysis.data_analysis.DataAnalyzer.analyze_data_flow, code2llm.analysis.data_analysis.DataAnalyzer.analyze_data_structures, code2llm.analysis.data_analysis.DataAnalyzer._find_data_pipelines, code2llm.analysis.data_analysis.DataAnalyzer._find_state_patterns, code2llm.analysis.data_analysis.DataAnalyzer._find_data_dependencies, code2llm.analysis.data_analysis.DataAnalyzer._find_event_flows, code2llm.analysis.data_analysis.DataAnalyzer._detect_types_from_name, code2llm.analysis.data_analysis.DataAnalyzer._create_type_entry, code2llm.analysis.data_analysis.DataAnalyzer._update_type_stats, code2llm.analysis.data_analysis.DataAnalyzer._analyze_data_types

### code2llm.analysis.cfg.CFGExtractor
> Extract Control Flow Graph from AST.
- **Methods**: 16
- **Key Methods**: code2llm.analysis.cfg.CFGExtractor.__init__, code2llm.analysis.cfg.CFGExtractor.extract, code2llm.analysis.cfg.CFGExtractor.new_node, code2llm.analysis.cfg.CFGExtractor.connect, code2llm.analysis.cfg.CFGExtractor.visit_FunctionDef, code2llm.analysis.cfg.CFGExtractor.visit_AsyncFunctionDef, code2llm.analysis.cfg.CFGExtractor.visit_If, code2llm.analysis.cfg.CFGExtractor.visit_For, code2llm.analysis.cfg.CFGExtractor.visit_While, code2llm.analysis.cfg.CFGExtractor.visit_Try
- **Inherits**: ast.NodeVisitor

### code2llm.nlp.pipeline.NLPPipeline
> Main NLP processing pipeline (4a-4e).
- **Methods**: 16
- **Key Methods**: code2llm.nlp.pipeline.NLPPipeline.__init__, code2llm.nlp.pipeline.NLPPipeline.process, code2llm.nlp.pipeline.NLPPipeline._step_normalize, code2llm.nlp.pipeline.NLPPipeline._step_match_intent, code2llm.nlp.pipeline.NLPPipeline._step_resolve_entities, code2llm.nlp.pipeline.NLPPipeline._infer_entity_types, code2llm.nlp.pipeline.NLPPipeline._calculate_overall_confidence, code2llm.nlp.pipeline.NLPPipeline._calculate_entity_confidence, code2llm.nlp.pipeline.NLPPipeline._apply_fallback, code2llm.nlp.pipeline.NLPPipeline._format_action

### code2llm.exporters.toon.metrics_core.CoreMetricsComputer
> Computes core structural and complexity metrics.
- **Methods**: 16
- **Key Methods**: code2llm.exporters.toon.metrics_core.CoreMetricsComputer.__init__, code2llm.exporters.toon.metrics_core.CoreMetricsComputer.compute_file_metrics, code2llm.exporters.toon.metrics_core.CoreMetricsComputer._new_file_record, code2llm.exporters.toon.metrics_core.CoreMetricsComputer._compute_fan_in, code2llm.exporters.toon.metrics_core.CoreMetricsComputer._process_function_calls, code2llm.exporters.toon.metrics_core.CoreMetricsComputer._process_called_by, code2llm.exporters.toon.metrics_core.CoreMetricsComputer._process_callee_calls, code2llm.exporters.toon.metrics_core.CoreMetricsComputer._handle_suffix_match, code2llm.exporters.toon.metrics_core.CoreMetricsComputer.compute_package_metrics, code2llm.exporters.toon.metrics_core.CoreMetricsComputer.compute_function_metrics

### analysis.data_analysis.DataAnalyzer
> Analyze data flows, structures, and optimization opportunities.
- **Methods**: 16
- **Key Methods**: analysis.data_analysis.DataAnalyzer.analyze_data_flow, analysis.data_analysis.DataAnalyzer.analyze_data_structures, analysis.data_analysis.DataAnalyzer._find_data_pipelines, analysis.data_analysis.DataAnalyzer._find_state_patterns, analysis.data_analysis.DataAnalyzer._find_data_dependencies, analysis.data_analysis.DataAnalyzer._find_event_flows, analysis.data_analysis.DataAnalyzer._detect_types_from_name, analysis.data_analysis.DataAnalyzer._create_type_entry, analysis.data_analysis.DataAnalyzer._update_type_stats, analysis.data_analysis.DataAnalyzer._analyze_data_types

### analysis.cfg.CFGExtractor
> Extract Control Flow Graph from AST.
- **Methods**: 16
- **Key Methods**: analysis.cfg.CFGExtractor.__init__, analysis.cfg.CFGExtractor.extract, analysis.cfg.CFGExtractor.new_node, analysis.cfg.CFGExtractor.connect, analysis.cfg.CFGExtractor.visit_FunctionDef, analysis.cfg.CFGExtractor.visit_AsyncFunctionDef, analysis.cfg.CFGExtractor.visit_If, analysis.cfg.CFGExtractor.visit_For, analysis.cfg.CFGExtractor.visit_While, analysis.cfg.CFGExtractor.visit_Try
- **Inherits**: ast.NodeVisitor

### nlp.pipeline.NLPPipeline
> Main NLP processing pipeline (4a-4e).
- **Methods**: 16
- **Key Methods**: nlp.pipeline.NLPPipeline.__init__, nlp.pipeline.NLPPipeline.process, nlp.pipeline.NLPPipeline._step_normalize, nlp.pipeline.NLPPipeline._step_match_intent, nlp.pipeline.NLPPipeline._step_resolve_entities, nlp.pipeline.NLPPipeline._infer_entity_types, nlp.pipeline.NLPPipeline._calculate_overall_confidence, nlp.pipeline.NLPPipeline._calculate_entity_confidence, nlp.pipeline.NLPPipeline._apply_fallback, nlp.pipeline.NLPPipeline._format_action

### exporters.toon.metrics_core.CoreMetricsComputer
> Computes core structural and complexity metrics.
- **Methods**: 16
- **Key Methods**: exporters.toon.metrics_core.CoreMetricsComputer.__init__, exporters.toon.metrics_core.CoreMetricsComputer.compute_file_metrics, exporters.toon.metrics_core.CoreMetricsComputer._new_file_record, exporters.toon.metrics_core.CoreMetricsComputer._compute_fan_in, exporters.toon.metrics_core.CoreMetricsComputer._process_function_calls, exporters.toon.metrics_core.CoreMetricsComputer._process_called_by, exporters.toon.metrics_core.CoreMetricsComputer._process_callee_calls, exporters.toon.metrics_core.CoreMetricsComputer._handle_suffix_match, exporters.toon.metrics_core.CoreMetricsComputer.compute_package_metrics, exporters.toon.metrics_core.CoreMetricsComputer.compute_function_metrics

## Data Transformation Functions

Key functions that process and transform data:

### SUMR.validate_and_setup

### SUMR.validate_chunked_output

### SUMR._validate_chunks

### SUMR._validate_single_chunk

### SUMR.create_parser

### validate_toon.validate_toon_completeness
> Validate toon format structure.
- **Output to**: SUMD.print, SUMD.print, bool, bool, bool

### map.toon._process_decorators

### map.toon._process_classes

### map.toon._process_standalone_function

### map.toon._process_class_method

### map.toon._process_functions

### map.toon._format_size

### map.toon._expand_all_formats

### map.toon._export_registry_formats

### map.toon._get_format_kwargs

### map.toon._parse_bullets

### map.toon._parse_sections

### map.toon._parse_acceptance_tests

### map.toon.parse_llm_task_text

### map.toon.create_parser

### map.toon.parse_evolution_metrics

### map.toon.parse_format_quality_report

### map.toon.parse_performance_report

### map.toon.generate_format_quality_badges

### map.toon._export_simple_formats

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `pipeline.run_pipeline` - 68 calls
- `code2llm.cli_parser.create_parser` - 46 calls
- `code2llm.generators.llm_task.normalize_llm_task` - 43 calls
- `generators.llm_task.normalize_llm_task` - 43 calls
- `code2llm.generators.llm_flow.generator.render_llm_flow_md` - 42 calls
- `generators.llm_flow.generator.render_llm_flow_md` - 42 calls
- `benchmarks.benchmark_performance.main` - 41 calls
- `validate_toon.analyze_class_differences` - 39 calls
- `benchmarks.benchmark_evolution.run_benchmark` - 34 calls
- `code2llm.cli_commands.handle_cache_command` - 33 calls
- `cli_commands.handle_cache_command` - 33 calls
- `code2llm.core.lang.rust.analyze_rust` - 31 calls
- `core.lang.rust.analyze_rust` - 31 calls
- `benchmarks.benchmark_optimizations.benchmark_cold_vs_warm` - 30 calls
- `benchmarks.benchmark_performance.create_test_project` - 29 calls
- `code2llm.nlp.pipeline.NLPPipeline.process` - 29 calls
- `nlp.pipeline.NLPPipeline.process` - 29 calls
- `code2llm.exporters.mermaid.compact.export_compact` - 27 calls
- `exporters.mermaid.compact.export_compact` - 27 calls
- `validate_toon.compare_modules` - 26 calls
- `code2llm.core.streaming_analyzer.StreamingAnalyzer.analyze_streaming` - 26 calls
- `code2llm.exporters.mermaid.calls.export_calls` - 26 calls
- `core.streaming_analyzer.StreamingAnalyzer.analyze_streaming` - 26 calls
- `exporters.mermaid.calls.export_calls` - 26 calls
- `benchmarks.benchmark_evolution.parse_evolution_metrics` - 25 calls
- `code2llm.exporters.toon.ToonExporter.export` - 25 calls
- `code2llm.exporters.toon.metrics_core.CoreMetricsComputer.compute_file_metrics` - 25 calls
- `exporters.toon.ToonExporter.export` - 25 calls
- `exporters.toon.metrics_core.CoreMetricsComputer.compute_file_metrics` - 25 calls
- `validate_toon.compare_functions` - 24 calls
- `code2llm.exporters.context_exporter.ContextExporter.export` - 24 calls
- `code2llm.exporters.evolution.yaml_export.export_to_yaml` - 24 calls
- `exporters.context_exporter.ContextExporter.export` - 24 calls
- `exporters.evolution.yaml_export.export_to_yaml` - 24 calls
- `scripts.benchmark_badges.main` - 23 calls
- `benchmarks.format_evaluator.evaluate_format` - 22 calls
- `benchmarks.benchmark_format_quality.run_benchmark` - 22 calls
- `code2llm.exporters.evolution_exporter.EvolutionExporter.export` - 22 calls
- `code2llm.exporters.flow_exporter.FlowExporter.export` - 22 calls
- `code2llm.core.analyzer.ProjectAnalyzer.analyze_project` - 22 calls

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