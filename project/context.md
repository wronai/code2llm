# System Architecture Analysis

## Overview

- **Project**: /home/tom/github/wronai/code2llm
- **Primary Language**: python
- **Languages**: python: 114, shell: 2, php: 1
- **Analysis Mode**: static
- **Total Functions**: 934
- **Total Classes**: 106
- **Modules**: 117
- **Entry Points**: 695

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

### code2llm.generators.llm_flow
- **Functions**: 24
- **Classes**: 1
- **File**: `llm_flow.py`

### code2llm.exporters.map_exporter
- **Functions**: 21
- **Classes**: 1
- **File**: `map_exporter.py`

### code2llm.core.large_repo
- **Functions**: 20
- **Classes**: 2
- **File**: `large_repo.py`

### code2llm.nlp.pipeline
- **Functions**: 20
- **Classes**: 3
- **File**: `pipeline.py`

### code2llm.analysis.type_inference
- **Functions**: 19
- **Classes**: 1
- **File**: `type_inference.py`

### code2llm.analysis.data_analysis
- **Functions**: 18
- **Classes**: 1
- **File**: `data_analysis.py`

### code2llm.analysis.pipeline_detector
- **Functions**: 18
- **Classes**: 3
- **File**: `pipeline_detector.py`

### code2llm.exporters.project_yaml_exporter
- **Functions**: 18
- **Classes**: 1
- **File**: `project_yaml_exporter.py`

### code2llm.exporters.mermaid_exporter
- **Functions**: 18
- **Classes**: 1
- **File**: `mermaid_exporter.py`

### code2llm.cli_exports.prompt
- **Functions**: 18
- **File**: `prompt.py`

### code2llm.analysis.side_effects
- **Functions**: 17
- **Classes**: 2
- **File**: `side_effects.py`

### code2llm.core.file_analyzer
- **Functions**: 17
- **Classes**: 1
- **File**: `file_analyzer.py`

### code2llm.analysis.cfg
- **Functions**: 17
- **Classes**: 1
- **File**: `cfg.py`

### code2llm.exporters.evolution_exporter
- **Functions**: 17
- **Classes**: 1
- **File**: `evolution_exporter.py`

### code2llm.nlp.entity_resolution
- **Functions**: 16
- **Classes**: 3
- **File**: `entity_resolution.py`

### code2llm.generators.mermaid
- **Functions**: 16
- **File**: `mermaid.py`

### validate_toon
- **Functions**: 15
- **File**: `validate_toon.py`

## Key Entry Points

Main execution flows into the system:

### code2llm.exporters.mermaid_exporter.MermaidExporter.export_flow_detailed
> Export detailed per-module view (~150 nodes).

Shows all significant functions per module with CC annotations.
- **Calls**: lines.append, lines.append, lines.append, lines.append, lines.append, lines.append, defaultdict, filtered_funcs.items

### code2llm.exporters.mermaid_exporter.MermaidExporter.export_flow_full
> Export full debug view with all nodes (original flow.mmd).

This is the original export() behavior with optional filtering.
- **Calls**: lines.append, lines.append, lines.append, lines.append, lines.append, lines.append, filtered_funcs.items, sorted

### validate_toon.main
> Main validation function.
- **Calls**: len, Path, print, print, validate_toon.load_file, validate_toon.validate_toon_completeness, print, print

### benchmarks.benchmark_performance.main
> Run benchmark suite.
- **Calls**: print, print, print, print, benchmarks.benchmark_performance.create_test_project, print, print, print

### code2llm.core.analyzer.ProjectAnalyzer.analyze_project
> Analyze entire project.
- **Calls**: time.time, None.resolve, self._collect_files, self._merge_results, self._build_call_graph, self.refactoring_analyzer.perform_refactoring_analysis, project_path.exists, FileNotFoundError

### code2llm.exporters.mermaid_exporter.MermaidExporter.export_flow_compact
> Export compact architectural view (~50 nodes).

Shows entry points, high-level modules, and critical path.
- **Calls**: lines.append, lines.append, lines.append, lines.append, self._find_critical_path, arch_modules.items, self._write, self._module_of

### benchmarks.benchmark_evolution.run_benchmark
> Run evolution analysis and print before/after table.
- **Calls**: benchmarks.benchmark_evolution.load_previous, print, print, print, print, print, metrics_labels.items, print

### code2llm.exporters.map_exporter.MapExporter.export_to_yaml
> Export analysis result to map.toon.yaml format (structured YAML).
- **Calls**: self._detect_languages, self._count_total_lines, sorted, None.parent.mkdir, result.modules.items, self._is_excluded, self._rel_path, self._file_line_count

### code2llm.nlp.pipeline.NLPPipeline.process
> Process query through full pipeline (4a-4e).
- **Calls**: time.time, time.time, self._step_normalize, stages.append, time.time, self._step_match_intent, stages.append, time.time

### code2llm.refactor.prompt_engine.PromptEngine._build_context_for_smell
> Prepare context data for the Jinja2 template.
- **Calls**: self._get_source_context, self.result.metrics.get, self.result.metrics.get, self._get_instruction_for_smell, None.replace, None.join, None.join, smell.name.split

### code2llm.exporters.context_view.ContextViewGenerator._render_architecture
- **Calls**: sorted, m.get, None.append, dir_groups.keys, sum, sum, lines.append, lines.append

### code2llm.core.streaming_analyzer.StreamingAnalyzer.analyze_streaming
> Analyze project with streaming output (yields partial results).
- **Calls**: time.time, None.resolve, self.scanner.collect_files, self.prioritizer.prioritize_files, len, self._report_progress, self.scanner.quick_scan_file, self.scanner.build_call_graph_streaming

### code2llm.exporters.mermaid_exporter.MermaidExporter.export_compact
> Export module-level graph: one node per module, weighted edges.
- **Calls**: defaultdict, defaultdict, result.functions.items, defaultdict, result.functions.items, set, sorted, sorted

### code2llm.exporters.toon.ToonExporter.export
> Export analysis result to toon v2 format.
- **Calls**: self.metrics_computer.compute_all_metrics, sections.extend, sections.append, sections.extend, sections.append, sections.extend, sections.append, sections.extend

### code2llm.exporters.project_yaml_exporter.ProjectYAMLExporter._build_project_yaml
- **Calls**: code2llm.exporters.toon.helpers._scan_line_counts, self._build_modules, self._build_health, self._build_hotspots, self._build_refactoring, self._build_evolution, sum, line_counts.items

### code2llm.exporters.mermaid_exporter.MermaidExporter.export_call_graph
> Export simplified call graph — only connected nodes.
- **Calls**: set, result.functions.items, sorted, set, self._write, self._module_of, result.functions.get, modules.items

### code2llm.exporters.context_exporter.ContextExporter.export
> Generate comprehensive LLM prompt with architecture description.
- **Calls**: lines.extend, lines.extend, self._get_important_entries, lines.extend, lines.extend, lines.extend, lines.extend, lines.extend

### code2llm.exporters.html_dashboard.HTMLDashboardGenerator._assemble_html
- **Calls**: self._render_evolution_section, self._render_evolution_script, None.join, proj.get, proj.get, proj.get, stats.get, stats.get

### code2llm.exporters.toon.metrics.MetricsComputer._compute_file_metrics
> Per-file metrics derived from AnalysisResult.
- **Calls**: result.functions.items, result.classes.items, result.modules.items, self._compute_fan_in, code2llm.exporters.map_exporter.MapExporter._is_excluded, fi.complexity.get, None.append, max

### code2llm.exporters.toon_view.ToonViewGenerator._render_modules
- **Calls**: defaultdict, sorted, m.get, None.suffix.lower, _LANG_EXT_MAP.get, lines.append, None.suffix.lower, _LANG_EXT_MAP.get

### scripts.benchmark_badges.main
> Main function to generate badges.
- **Calls**: Path, output_dir.mkdir, os.walk, None.glob, None.glob, scripts.benchmark_badges.create_html, output_path.write_text, print

### code2llm.exporters.evolution_exporter.EvolutionExporter.export
> Generate evolution.toon.
- **Calls**: self._build_context, sections.extend, sections.append, sections.extend, sections.append, sections.extend, sections.append, sections.extend

### code2llm.exporters.flow_exporter.FlowExporter.export
> Export analysis result to flow.toon format.
- **Calls**: self._build_context, sections.extend, sections.append, sections.extend, sections.append, sections.extend, sections.append, sections.extend

### benchmarks.benchmark_format_quality.run_benchmark
> Run the full format quality benchmark.
- **Calls**: benchmarks.benchmark_format_quality._print_benchmark_header, Path, benchmarks.project_generator.create_ground_truth_project, benchmarks.benchmark_format_quality._print_ground_truth_info, output_dir.mkdir, benchmarks.reporting.print_results, benchmarks.reporting.build_report, tempfile.mkdtemp

### code2llm.nlp.intent_matching.IntentMatcher._calculate_similarity
> Calculate string similarity using configured algorithm.
- **Calls**: None.ratio, None.ratio, a.lower, b.lower, None.ratio, SequenceMatcher, SequenceMatcher, None.join

### code2llm.exporters.evolution_exporter.EvolutionExporter.export_to_yaml
> Generate evolution.toon.yaml (structured YAML).
- **Calls**: self._build_context, actions.sort, None.parent.mkdir, actions.append, risks.append, open, yaml.dump, actions.append

### code2llm.analysis.pipeline_detector.PipelineDetector._find_pipeline_paths
> Find longest paths in the call graph as pipeline candidates.

Strategy:
1. Find all source nodes (in-degree 0) as potential entry points
2. Find all s
- **Calls**: set, nx.weakly_connected_components, self._longest_path_from, len, graph.subgraph, self._longest_path_in_dag, graph.nodes, sorted

### code2llm.exporters.mermaid_exporter.MermaidExporter._find_critical_path
> Find the longest path from entry points (critical path).
- **Calls**: defaultdict, result.functions.items, set, result.functions.items, set, set, set, any

### code2llm.core.analyzer.ProjectAnalyzer.analyze_files
> Analyze specific list of files (for chunked analysis).

Args:
    files: List of (file_path, module_name) tuples
    project_path: Base project path f
- **Calls**: time.time, self._merge_results, self._build_call_graph, self.refactoring_analyzer.perform_refactoring_analysis, print, self._analyze_parallel, self._analyze_sequential, self._detect_patterns

### code2llm.exporters.project_yaml_exporter.ProjectYAMLExporter._build_refactoring
- **Calls**: result.functions.items, result.metrics.get, proj_metrics.get, priorities.sort, code2llm.exporters.map_exporter.MapExporter._is_excluded, fi.complexity.get, priorities.append, code2llm.exporters.map_exporter.MapExporter._rel_path

## Process Flows

Key execution flows identified:

### Flow 1: export_flow_detailed
```
export_flow_detailed [code2llm.exporters.mermaid_exporter.MermaidExporter]
```

### Flow 2: export_flow_full
```
export_flow_full [code2llm.exporters.mermaid_exporter.MermaidExporter]
```

### Flow 3: main
```
main [validate_toon]
  └─> load_file
      └─> load_yaml
      └─ →> is_toon_file
      └─ →> load_toon
```

### Flow 4: analyze_project
```
analyze_project [code2llm.core.analyzer.ProjectAnalyzer]
```

### Flow 5: export_flow_compact
```
export_flow_compact [code2llm.exporters.mermaid_exporter.MermaidExporter]
```

### Flow 6: run_benchmark
```
run_benchmark [benchmarks.benchmark_evolution]
  └─> load_previous
```

### Flow 7: export_to_yaml
```
export_to_yaml [code2llm.exporters.map_exporter.MapExporter]
```

### Flow 8: process
```
process [code2llm.nlp.pipeline.NLPPipeline]
```

### Flow 9: _build_context_for_smell
```
_build_context_for_smell [code2llm.refactor.prompt_engine.PromptEngine]
```

### Flow 10: _render_architecture
```
_render_architecture [code2llm.exporters.context_view.ContextViewGenerator]
```

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
- **Methods**: 21
- **Key Methods**: code2llm.exporters.map_exporter.MapExporter.export, code2llm.exporters.map_exporter.MapExporter.export_to_yaml, code2llm.exporters.map_exporter.MapExporter._render_header, code2llm.exporters.map_exporter.MapExporter._render_stats_line, code2llm.exporters.map_exporter.MapExporter._render_alerts_line, code2llm.exporters.map_exporter.MapExporter._render_hotspots_line, code2llm.exporters.map_exporter.MapExporter._render_module_list, code2llm.exporters.map_exporter.MapExporter._render_details, code2llm.exporters.map_exporter.MapExporter._rank_modules, code2llm.exporters.map_exporter.MapExporter._render_map_module
- **Inherits**: Exporter

### code2llm.analysis.type_inference.TypeInferenceEngine
> Extract and infer type information from Python source files.

Operates on source files referenced by
- **Methods**: 19
- **Key Methods**: code2llm.analysis.type_inference.TypeInferenceEngine.__init__, code2llm.analysis.type_inference.TypeInferenceEngine.enrich_function, code2llm.analysis.type_inference.TypeInferenceEngine.get_arg_types, code2llm.analysis.type_inference.TypeInferenceEngine.get_return_type, code2llm.analysis.type_inference.TypeInferenceEngine.get_typed_signature, code2llm.analysis.type_inference.TypeInferenceEngine.extract_all_types, code2llm.analysis.type_inference.TypeInferenceEngine._get_ast, code2llm.analysis.type_inference.TypeInferenceEngine._find_function_node, code2llm.analysis.type_inference.TypeInferenceEngine._extract_from_node, code2llm.analysis.type_inference.TypeInferenceEngine._extract_args

### code2llm.core.large_repo.HierarchicalRepoSplitter
> Splits large repositories using hierarchical approach.

Strategy:
1. First pass: level 1 folders
2. 
- **Methods**: 18
- **Key Methods**: code2llm.core.large_repo.HierarchicalRepoSplitter.__init__, code2llm.core.large_repo.HierarchicalRepoSplitter.get_analysis_plan, code2llm.core.large_repo.HierarchicalRepoSplitter._split_hierarchically, code2llm.core.large_repo.HierarchicalRepoSplitter._merge_small_l1_dirs, code2llm.core.large_repo.HierarchicalRepoSplitter._split_level2_consolidated, code2llm.core.large_repo.HierarchicalRepoSplitter._categorize_subdirs, code2llm.core.large_repo.HierarchicalRepoSplitter._process_large_dirs, code2llm.core.large_repo.HierarchicalRepoSplitter._process_level1_files, code2llm.core.large_repo.HierarchicalRepoSplitter._merge_small_dirs, code2llm.core.large_repo.HierarchicalRepoSplitter._chunk_by_files

### code2llm.exporters.project_yaml_exporter.ProjectYAMLExporter
> Export unified project.yaml — single source of truth for diagnostics.

Combines data from analysis.t
- **Methods**: 18
- **Key Methods**: code2llm.exporters.project_yaml_exporter.ProjectYAMLExporter.export, code2llm.exporters.project_yaml_exporter.ProjectYAMLExporter._build_project_yaml, code2llm.exporters.project_yaml_exporter.ProjectYAMLExporter._build_health, code2llm.exporters.project_yaml_exporter.ProjectYAMLExporter._build_alerts, code2llm.exporters.project_yaml_exporter.ProjectYAMLExporter._count_duplicates, code2llm.exporters.project_yaml_exporter.ProjectYAMLExporter._build_modules, code2llm.exporters.project_yaml_exporter.ProjectYAMLExporter._group_by_file, code2llm.exporters.project_yaml_exporter.ProjectYAMLExporter._compute_module_entry, code2llm.exporters.project_yaml_exporter.ProjectYAMLExporter._compute_inbound_deps, code2llm.exporters.project_yaml_exporter.ProjectYAMLExporter._build_exports
- **Inherits**: Exporter

### code2llm.exporters.mermaid_exporter.MermaidExporter
> Export call graph to Mermaid format.
- **Methods**: 18
- **Key Methods**: code2llm.exporters.mermaid_exporter.MermaidExporter.export, code2llm.exporters.mermaid_exporter.MermaidExporter._render_subgraphs, code2llm.exporters.mermaid_exporter.MermaidExporter._render_edges, code2llm.exporters.mermaid_exporter.MermaidExporter._render_cc_styles, code2llm.exporters.mermaid_exporter.MermaidExporter._get_cc, code2llm.exporters.mermaid_exporter.MermaidExporter.export_call_graph, code2llm.exporters.mermaid_exporter.MermaidExporter.export_compact, code2llm.exporters.mermaid_exporter.MermaidExporter._should_skip_module, code2llm.exporters.mermaid_exporter.MermaidExporter._is_entry_point, code2llm.exporters.mermaid_exporter.MermaidExporter._find_critical_path
- **Inherits**: Exporter

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

### code2llm.exporters.evolution_exporter.EvolutionExporter
> Export evolution.toon.yaml — prioritized refactoring queue.
- **Methods**: 17
- **Key Methods**: code2llm.exporters.evolution_exporter.EvolutionExporter._is_excluded, code2llm.exporters.evolution_exporter.EvolutionExporter.export, code2llm.exporters.evolution_exporter.EvolutionExporter.export_to_yaml, code2llm.exporters.evolution_exporter.EvolutionExporter._build_context, code2llm.exporters.evolution_exporter.EvolutionExporter._compute_func_data, code2llm.exporters.evolution_exporter.EvolutionExporter._scan_file_sizes, code2llm.exporters.evolution_exporter.EvolutionExporter._aggregate_file_stats, code2llm.exporters.evolution_exporter.EvolutionExporter._make_relative_path, code2llm.exporters.evolution_exporter.EvolutionExporter._filter_god_modules, code2llm.exporters.evolution_exporter.EvolutionExporter._compute_god_modules
- **Inherits**: Exporter

### code2llm.analysis.data_analysis.DataAnalyzer
> Analyze data flows, structures, and optimization opportunities.
- **Methods**: 16
- **Key Methods**: code2llm.analysis.data_analysis.DataAnalyzer.analyze_data_flow, code2llm.analysis.data_analysis.DataAnalyzer.analyze_data_structures, code2llm.analysis.data_analysis.DataAnalyzer._find_data_pipelines, code2llm.analysis.data_analysis.DataAnalyzer._find_state_patterns, code2llm.analysis.data_analysis.DataAnalyzer._find_data_dependencies, code2llm.analysis.data_analysis.DataAnalyzer._find_event_flows, code2llm.analysis.data_analysis.DataAnalyzer._detect_types_from_name, code2llm.analysis.data_analysis.DataAnalyzer._create_type_entry, code2llm.analysis.data_analysis.DataAnalyzer._update_type_stats, code2llm.analysis.data_analysis.DataAnalyzer._analyze_data_types

### code2llm.core.file_analyzer.FileAnalyzer
> Analyzes a single file.
- **Methods**: 16
- **Key Methods**: code2llm.core.file_analyzer.FileAnalyzer.__init__, code2llm.core.file_analyzer.FileAnalyzer.analyze_file, code2llm.core.file_analyzer.FileAnalyzer._analyze_python, code2llm.core.file_analyzer.FileAnalyzer._analyze_ast, code2llm.core.file_analyzer.FileAnalyzer._calculate_complexity, code2llm.core.file_analyzer.FileAnalyzer._perform_deep_analysis, code2llm.core.file_analyzer.FileAnalyzer._process_class, code2llm.core.file_analyzer.FileAnalyzer._process_function, code2llm.core.file_analyzer.FileAnalyzer._build_cfg, code2llm.core.file_analyzer.FileAnalyzer._process_cfg_block

### code2llm.nlp.pipeline.NLPPipeline
> Main NLP processing pipeline (4a-4e).
- **Methods**: 16
- **Key Methods**: code2llm.nlp.pipeline.NLPPipeline.__init__, code2llm.nlp.pipeline.NLPPipeline.process, code2llm.nlp.pipeline.NLPPipeline._step_normalize, code2llm.nlp.pipeline.NLPPipeline._step_match_intent, code2llm.nlp.pipeline.NLPPipeline._step_resolve_entities, code2llm.nlp.pipeline.NLPPipeline._infer_entity_types, code2llm.nlp.pipeline.NLPPipeline._calculate_overall_confidence, code2llm.nlp.pipeline.NLPPipeline._calculate_entity_confidence, code2llm.nlp.pipeline.NLPPipeline._apply_fallback, code2llm.nlp.pipeline.NLPPipeline._format_action

### code2llm.analysis.side_effects.SideEffectDetector
> Detect side effects in Python functions via AST analysis.

Scans function bodies for IO operations, 
- **Methods**: 15
- **Key Methods**: code2llm.analysis.side_effects.SideEffectDetector.__init__, code2llm.analysis.side_effects.SideEffectDetector.analyze_function, code2llm.analysis.side_effects.SideEffectDetector.analyze_all, code2llm.analysis.side_effects.SideEffectDetector.get_purity_score, code2llm.analysis.side_effects.SideEffectDetector._scan_node, code2llm.analysis.side_effects.SideEffectDetector._check_calls, code2llm.analysis.side_effects.SideEffectDetector._check_assignments, code2llm.analysis.side_effects.SideEffectDetector._check_globals, code2llm.analysis.side_effects.SideEffectDetector._check_yield, code2llm.analysis.side_effects.SideEffectDetector._check_delete

### code2llm.exporters.context_exporter.ContextExporter
> Export LLM-ready analysis summary with architecture and flows.

Output: context.md — architecture na
- **Methods**: 15
- **Key Methods**: code2llm.exporters.context_exporter.ContextExporter.export, code2llm.exporters.context_exporter.ContextExporter._get_overview, code2llm.exporters.context_exporter.ContextExporter._detect_languages, code2llm.exporters.context_exporter.ContextExporter._get_architecture_by_module, code2llm.exporters.context_exporter.ContextExporter._get_important_entries, code2llm.exporters.context_exporter.ContextExporter._get_key_entry_points, code2llm.exporters.context_exporter.ContextExporter._get_process_flows, code2llm.exporters.context_exporter.ContextExporter._get_key_classes, code2llm.exporters.context_exporter.ContextExporter._get_data_transformations, code2llm.exporters.context_exporter.ContextExporter._get_behavioral_patterns
- **Inherits**: Exporter

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
- **Inherits**: Exporter

### code2llm.analysis.call_graph.CallGraphExtractor
> Extract call graph from AST.
- **Methods**: 13
- **Key Methods**: code2llm.analysis.call_graph.CallGraphExtractor.__init__, code2llm.analysis.call_graph.CallGraphExtractor.extract, code2llm.analysis.call_graph.CallGraphExtractor._calculate_metrics, code2llm.analysis.call_graph.CallGraphExtractor.visit_Import, code2llm.analysis.call_graph.CallGraphExtractor.visit_ImportFrom, code2llm.analysis.call_graph.CallGraphExtractor.visit_ClassDef, code2llm.analysis.call_graph.CallGraphExtractor.visit_FunctionDef, code2llm.analysis.call_graph.CallGraphExtractor.visit_AsyncFunctionDef, code2llm.analysis.call_graph.CallGraphExtractor.visit_Call, code2llm.analysis.call_graph.CallGraphExtractor._qualified_name
- **Inherits**: ast.NodeVisitor

### code2llm.nlp.normalization.QueryNormalizer
> Normalize queries for consistent processing.
- **Methods**: 13
- **Key Methods**: code2llm.nlp.normalization.QueryNormalizer.__init__, code2llm.nlp.normalization.QueryNormalizer.normalize, code2llm.nlp.normalization.QueryNormalizer._unicode_normalize, code2llm.nlp.normalization.QueryNormalizer._lowercase, code2llm.nlp.normalization.QueryNormalizer._remove_punctuation, code2llm.nlp.normalization.QueryNormalizer._normalize_whitespace, code2llm.nlp.normalization.QueryNormalizer._remove_stopwords, code2llm.nlp.normalization.QueryNormalizer._tokenize, code2llm.nlp.normalization.QueryNormalizer.step_1a_lowercase, code2llm.nlp.normalization.QueryNormalizer.step_1b_remove_punctuation

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

### code2llm.cli_parser.create_parser
> Create CLI argument parser.
- **Output to**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument

### demo_langs.valid.sample.UserService.process_users
- **Output to**: print

### code2llm.cli_commands.validate_and_setup
> Validate source path and setup output directory.
- **Output to**: Path, Path, output_dir.mkdir, print, print

### code2llm.cli_commands.validate_chunked_output
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
- **Output to**: code2llm.core.repo_files._get_gitignore_parser, len, chunks.append, self._chunk_by_files, chunks.extend

### code2llm.core.repo_files._get_gitignore_parser
> Load gitignore parser for project if available.
- **Output to**: code2llm.core.gitignore.load_gitignore_patterns

### code2llm.core.gitignore.GitIgnoreParser._parse_pattern
> Parse a single gitignore pattern into regex.
- **Output to**: pattern.startswith, pattern.endswith, pattern.startswith, self._wildcard_to_regex, re.compile

### code2llm.core.toon_size_manager._parse_modules
> Parse module sections from TOON content.

Returns list of (module_name, start_line, end_line).
- **Output to**: content.split, enumerate, modules.append, line.startswith, line.endswith

### code2llm.core.file_filter.FastFileFilter.should_process
> Check if file should be processed.
- **Output to**: file_path.lower, Path, self._gitignore_parser.is_ignored, any, fnmatch.fnmatch

### code2llm.core.file_analyzer.FileAnalyzer._process_class
> Process class definition.
- **Output to**: ClassInfo, None.classes.append, isinstance, isinstance, methods.append

### code2llm.core.file_analyzer.FileAnalyzer._process_function
> Process function definition with limited CFG depth.
- **Output to**: func_name.startswith, any, self._file_filter.should_skip_function, FunctionInfo, ast.walk

### code2llm.core.file_analyzer.FileAnalyzer._process_cfg_block
> Process a block of statements for CFG with depth limiting.
- **Output to**: None.append, isinstance, None.append, FlowEdge, self._process_if_stmt

### code2llm.core.file_analyzer.FileAnalyzer._process_if_stmt
> Process if statement for CFG.
- **Output to**: FlowNode, func_info.cfg_nodes.append, None.append, self._process_cfg_block, FlowNode

## Behavioral Patterns

### recursion__is_excluded
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: code2llm.exporters.toon.ToonExporter._is_excluded

### state_machine_IncrementalAnalyzer
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: code2llm.core.streaming.incremental.IncrementalAnalyzer.__init__, code2llm.core.streaming.incremental.IncrementalAnalyzer._load_state, code2llm.core.streaming.incremental.IncrementalAnalyzer._save_state, code2llm.core.streaming.incremental.IncrementalAnalyzer.get_changed_files, code2llm.core.streaming.incremental.IncrementalAnalyzer._get_module_name

### state_machine_DatabaseConnection
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: examples.streaming-analyzer.sample_project.database.DatabaseConnection.__init__, examples.streaming-analyzer.sample_project.database.DatabaseConnection._load_data, examples.streaming-analyzer.sample_project.database.DatabaseConnection._save_data, examples.streaming-analyzer.sample_project.database.DatabaseConnection.get_user, examples.streaming-analyzer.sample_project.database.DatabaseConnection.get_user_settings

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `code2llm.exporters.mermaid_exporter.MermaidExporter.export_flow_detailed` - 51 calls
- `code2llm.exporters.mermaid_exporter.MermaidExporter.export_flow_full` - 46 calls
- `validate_toon.main` - 45 calls
- `code2llm.generators.llm_task.normalize_llm_task` - 43 calls
- `code2llm.generators.llm_flow.render_llm_flow_md` - 42 calls
- `benchmarks.benchmark_performance.main` - 41 calls
- `validate_toon.analyze_class_differences` - 39 calls
- `code2llm.core.analyzer.ProjectAnalyzer.analyze_project` - 39 calls
- `code2llm.cli_parser.create_parser` - 38 calls
- `code2llm.exporters.mermaid_exporter.MermaidExporter.export_flow_compact` - 37 calls
- `benchmarks.benchmark_evolution.run_benchmark` - 34 calls
- `code2llm.cli_commands.validate_chunked_output` - 34 calls
- `code2llm.exporters.map_exporter.MapExporter.export_to_yaml` - 33 calls
- `code2llm.core.lang.php.analyze_php` - 33 calls
- `code2llm.core.lang.rust.analyze_rust` - 31 calls
- `benchmarks.benchmark_performance.create_test_project` - 29 calls
- `code2llm.nlp.pipeline.NLPPipeline.process` - 29 calls
- `code2llm.core.lang.go_lang.analyze_go` - 28 calls
- `code2llm.core.lang.ruby.analyze_ruby` - 28 calls
- `validate_toon.compare_modules` - 26 calls
- `code2llm.core.streaming_analyzer.StreamingAnalyzer.analyze_streaming` - 26 calls
- `code2llm.exporters.mermaid_exporter.MermaidExporter.export_compact` - 26 calls
- `code2llm.exporters.toon.ToonExporter.export` - 26 calls
- `benchmarks.benchmark_evolution.parse_evolution_metrics` - 25 calls
- `code2llm.exporters.mermaid_exporter.MermaidExporter.export_call_graph` - 25 calls
- `code2llm.exporters.context_exporter.ContextExporter.export` - 25 calls
- `validate_toon.compare_functions` - 24 calls
- `code2llm.generators.mermaid.generate_single_png` - 24 calls
- `scripts.benchmark_badges.main` - 23 calls
- `code2llm.exporters.evolution_exporter.EvolutionExporter.export` - 23 calls
- `code2llm.exporters.flow_exporter.FlowExporter.export` - 23 calls
- `benchmarks.format_evaluator.evaluate_format` - 22 calls
- `benchmarks.benchmark_format_quality.run_benchmark` - 22 calls
- `code2llm.exporters.evolution_exporter.EvolutionExporter.export_to_yaml` - 22 calls
- `code2llm.cli_commands.generate_llm_context` - 21 calls
- `code2llm.core.analyzer.ProjectAnalyzer.analyze_files` - 20 calls
- `code2llm.core.lang.generic.analyze_generic` - 20 calls
- `validate_toon.compare_classes` - 19 calls
- `scripts.benchmark_badges.parse_evolution_metrics` - 19 calls
- `code2llm.exporters.yaml_exporter.YAMLExporter.export_grouped` - 19 calls

## System Interactions

How components interact:

```mermaid
graph TD
    export_flow_detailed --> append
    export_flow_full --> append
    main --> len
    main --> Path
    main --> print
    main --> load_file
    main --> create_test_project
    analyze_project --> time
    analyze_project --> resolve
    analyze_project --> _collect_files
    analyze_project --> _merge_results
    analyze_project --> _build_call_graph
    export_flow_compact --> append
    export_flow_compact --> _find_critical_path
    run_benchmark --> load_previous
    run_benchmark --> print
    export_to_yaml --> _detect_languages
    export_to_yaml --> _count_total_lines
    export_to_yaml --> sorted
    export_to_yaml --> mkdir
    export_to_yaml --> items
    process --> time
    process --> _step_normalize
    process --> append
    _build_context_for_s --> _get_source_context
    _build_context_for_s --> get
    _build_context_for_s --> _get_instruction_for
    _build_context_for_s --> replace
    _render_architecture --> sorted
    _render_architecture --> get
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.