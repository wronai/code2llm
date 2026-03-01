# System Architecture Analysis

## Overview

- **Project**: /home/tom/github/wronai/code2flow
- **Analysis Mode**: hybrid
- **Total Functions**: 406
- **Total Classes**: 76
- **Modules**: 43
- **Entry Points**: 360

## Architecture by Module

### examples.functional_refactoring_example
- **Functions**: 50
- **Classes**: 15
- **File**: `functional_refactoring_example.py`

### code2flow.core.analyzer
- **Functions**: 30
- **Classes**: 4
- **File**: `analyzer.py`

### code2flow.exporters.toon
- **Functions**: 29
- **Classes**: 1
- **File**: `toon.py`

### code2flow.core.streaming_analyzer
- **Functions**: 25
- **Classes**: 6
- **File**: `streaming_analyzer.py`

### code2flow.optimization.advanced_optimizer
- **Functions**: 22
- **Classes**: 1
- **File**: `advanced_optimizer.py`

### code2flow.llm_flow_generator
- **Functions**: 20
- **Classes**: 1
- **File**: `llm_flow_generator.py`

### code2flow.nlp.pipeline
- **Functions**: 20
- **Classes**: 3
- **File**: `pipeline.py`

### code2flow.analysis.cfg
- **Functions**: 17
- **Classes**: 1
- **File**: `cfg.py`

### code2flow.nlp.entity_resolution
- **Functions**: 16
- **Classes**: 3
- **File**: `entity_resolution.py`

### code2flow.nlp.intent_matching
- **Functions**: 15
- **Classes**: 3
- **File**: `intent_matching.py`

### validate_toon
- **Functions**: 14
- **File**: `validate_toon.py`

### code2flow.analysis.data_analysis
- **Functions**: 13
- **Classes**: 1
- **File**: `data_analysis.py`

### code2flow.analysis.call_graph
- **Functions**: 13
- **Classes**: 1
- **File**: `call_graph.py`

### code2flow.nlp.normalization
- **Functions**: 13
- **Classes**: 2
- **File**: `normalization.py`

### code2flow.analysis.dfg
- **Functions**: 12
- **Classes**: 1
- **File**: `dfg.py`

### code2flow.exporters.llm_exporter
- **Functions**: 12
- **Classes**: 1
- **File**: `llm_exporter.py`

### code2flow.llm_task_generator
- **Functions**: 10
- **File**: `llm_task_generator.py`

### code2flow.analysis.smells
- **Functions**: 9
- **Classes**: 1
- **File**: `smells.py`

### code2flow.patterns.detector
- **Functions**: 8
- **Classes**: 1
- **File**: `detector.py`

### code2flow.exporters.yaml_exporter
- **Functions**: 7
- **Classes**: 1
- **File**: `yaml_exporter.py`

## Key Entry Points

Main execution flows into the system:

### code2flow.cli.main
> Main CLI entry point.
- **Calls**: code2flow.llm_task_generator.create_parser, parser.parse_args, Path, Path, output_dir.mkdir, Config, llm_flow_main, code2flow.cli.generate_llm_context

### validate_toon.main
> Main validation function.
- **Calls**: len, Path, print, print, validate_toon.load_yaml, validate_toon.validate_toon_completeness, print, print

### benchmarks.benchmark_performance.main
> Run benchmark suite.
- **Calls**: print, print, print, print, benchmarks.benchmark_performance.create_test_project, print, print, print

### code2flow.exporters.toon.ToonExporter._compute_file_metrics
> Per-file metrics derived from AnalysisResult.
- **Calls**: result.functions.items, result.classes.items, result.modules.items, defaultdict, result.functions.items, Path, pp.is_dir, self._is_excluded

### code2flow.exporters.toon.ToonExporter.export
> Export analysis result to toon v2 format.
- **Calls**: self._build_context, sections.extend, sections.append, sections.extend, sections.append, sections.extend, sections.append, sections.extend

### code2flow.core.analyzer.ProjectAnalyzer.analyze_project
> Analyze entire project.
- **Calls**: time.time, None.resolve, self._collect_files, self._merge_results, self._build_call_graph, self._perform_refactoring_analysis, project_path.exists, FileNotFoundError

### code2flow.core.analyzer.FileAnalyzer._process_cfg_block
> Process a block of statements for CFG with depth limiting.
- **Calls**: None.append, isinstance, None.append, FlowEdge, FlowNode, func_info.cfg_nodes.append, None.append, self._process_cfg_block

### code2flow.exporters.toon.ToonExporter._render_coupling
- **Calls**: sorted, pkg_activity.sort, max, max, len, lines.append, max, None.join

### code2flow.nlp.pipeline.NLPPipeline.process
> Process query through full pipeline (4a-4e).
- **Calls**: time.time, time.time, self._step_normalize, stages.append, time.time, self._step_match_intent, stages.append, time.time

### code2flow.core.analyzer.ProjectAnalyzer._perform_refactoring_analysis
> Perform deep analysis and detect code smells.
- **Calls**: CallGraphExtractor, cg_ext._calculate_metrics, nx.DiGraph, result.functions.items, CouplingAnalyzer, coupling_analyzer.analyze, SmellDetector, smell_detector.detect

### code2flow.core.analyzer.ProjectAnalyzer._detect_dead_code
> Use vulture to find dead code and update reachability.
- **Calls**: print, vulture.Vulture, None.rglob, v.get_unused_code, result.functions.items, print, None.resolve, getattr

### code2flow.refactor.prompt_engine.PromptEngine._build_context_for_smell
> Prepare context data for the Jinja2 template.
- **Calls**: self._get_source_context, self.result.metrics.get, self.result.metrics.get, self._get_instruction_for_smell, None.replace, None.join, None.join, smell.name.split

### code2flow.exporters.toon.ToonExporter._render_details
> Render D: section — per-module details sorted by max CC desc.
- **Calls**: result.modules.items, mod_items.sort, mod_items.append, self._rel_path, lines.append, result.functions.get, None.join, lines.append

### code2flow.core.streaming_analyzer.StreamingAnalyzer.analyze_streaming
> Analyze project with streaming output (yields partial results).
- **Calls**: time.time, None.resolve, self._collect_files, self.prioritizer.prioritize_files, len, self._report_progress, self._quick_scan_file, self._build_call_graph_streaming

### code2flow.visualizers.graph.GraphVisualizer.visualize_cfg
> Create control flow visualization.
- **Calls**: plt.figure, self.graph.nodes, nx.draw_networkx_nodes, nx.draw_networkx_edges, self.graph.nodes, nx.draw_networkx_labels, plt.legend, plt.title

### code2flow.exporters.toon.ToonExporter._detect_duplicates
> Detect duplicate classes by comparing method-name sets.
- **Calls**: enumerate, set, range, result.classes.items, len, len, set, self._is_excluded

### code2flow.exporters.llm_exporter.LLMPromptExporter.export
> Generate comprehensive LLM prompt with architecture description.
- **Calls**: lines.extend, lines.extend, self._get_important_entries, lines.extend, lines.extend, lines.extend, lines.extend, lines.extend

### code2flow.cli.create_parser
> Create CLI argument parser.
- **Calls**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument

### code2flow.visualizers.graph.GraphVisualizer.visualize_call_graph
> Visualize call graph.
- **Calls**: nx.DiGraph, self.result.functions.items, plt.figure, nx.spring_layout, call_graph.nodes, nx.draw_networkx_nodes, nx.draw_networkx_edges, nx.draw_networkx_labels

### code2flow.exporters.toon.ToonExporter._render_layers
> Render LAYERS section — files grouped by package with metrics.
- **Calls**: self._dup_file_set, sorted, packages.keys, None.get, None.get, any, lines.append, pkg_files.sort

### code2flow.analysis.data_analysis.DataAnalyzer._analyze_data_types
> Analyze data types and usage.
- **Calls**: result.functions.items, sorted, func.name.lower, self._infer_parameter_types, self._infer_return_types, data_types.values, func.docstring.lower, None.join

### code2flow.nlp.intent_matching.IntentMatcher._calculate_similarity
> Calculate string similarity using configured algorithm.
- **Calls**: None.ratio, None.ratio, a.lower, b.lower, None.ratio, SequenceMatcher, SequenceMatcher, None.join

### code2flow.core.streaming_analyzer.StreamingAnalyzer._quick_scan_file
> Quick scan - extract functions and classes only (no CFG).
- **Calls**: content.split, ast.walk, None.read_text, self.cache.get, ModuleInfo, isinstance, ast.parse, ClassInfo

### code2flow.exporters.mermaid_exporter.MermaidExporter.export_call_graph
> Export simplified call graph.
- **Calls**: sorted, result.functions.items, None.parent.mkdir, func_name.split, None.append, modules.items, None.replace, lines.append

### code2flow.core.analyzer.FileAnalyzer._analyze_ast
> Analyze AST and extract structure.
- **Calls**: content.split, ModuleInfo, isinstance, cc_visit, DFGExtractor, dfg_ext.extract, CallGraphExtractor, cg_ext.extract

### code2flow.core.streaming_analyzer.SmartPrioritizer.prioritize_files
> Score and sort files by importance.
- **Calls**: self._build_import_graph, scored.sort, self._check_has_main, len, FilePriority, scored.append, reasons.append, reasons.append

### code2flow.exporters.yaml_exporter.YAMLExporter.export_grouped
> Export with grouped CFG flows by function.
- **Calls**: defaultdict, result.nodes.items, sorted, None.parent.mkdir, func_flows.items, sorted, open, yaml.dump

### code2flow.llm_flow_generator.main
- **Calls**: None.parse_args, Path, code2flow.llm_flow_generator._safe_read_yaml, code2flow.llm_flow_generator.generate_llm_flow, Path, output_path.parent.mkdir, output_path.write_text, input_path.exists

### code2flow.exporters.toon.ToonExporter._compute_coupling_matrix
> Build package-to-package coupling from cross-module function calls.
- **Calls**: defaultdict, result.functions.items, result.functions.items, set, self._is_excluded, self._package_of_module, all_pkgs.add, all_pkgs.add

### code2flow.exporters.llm_exporter.LLMPromptExporter._trace_flow
> Trace execution flow from a function with cycle detection.
- **Calls**: visited.add, sorted, None.join, set, func_name.split, None.append, calls_by_module.items, func_name.split

## Process Flows

Key execution flows identified:

### Flow 1: main
```
main [code2flow.cli]
  └─ →> create_parser
```

### Flow 2: _compute_file_metrics
```
_compute_file_metrics [code2flow.exporters.toon.ToonExporter]
```

### Flow 3: export
```
export [code2flow.exporters.toon.ToonExporter]
```

### Flow 4: analyze_project
```
analyze_project [code2flow.core.analyzer.ProjectAnalyzer]
```

### Flow 5: _process_cfg_block
```
_process_cfg_block [code2flow.core.analyzer.FileAnalyzer]
```

### Flow 6: _render_coupling
```
_render_coupling [code2flow.exporters.toon.ToonExporter]
```

### Flow 7: process
```
process [code2flow.nlp.pipeline.NLPPipeline]
```

### Flow 8: _perform_refactoring_analysis
```
_perform_refactoring_analysis [code2flow.core.analyzer.ProjectAnalyzer]
```

### Flow 9: _detect_dead_code
```
_detect_dead_code [code2flow.core.analyzer.ProjectAnalyzer]
```

### Flow 10: _build_context_for_smell
```
_build_context_for_smell [code2flow.refactor.prompt_engine.PromptEngine]
```

## Key Classes

### code2flow.exporters.toon.ToonExporter
> Export to toon v2 plain-text format — scannable, sorted by severity.
- **Methods**: 29
- **Key Methods**: code2flow.exporters.toon.ToonExporter.export, code2flow.exporters.toon.ToonExporter._is_excluded, code2flow.exporters.toon.ToonExporter._build_context, code2flow.exporters.toon.ToonExporter._compute_file_metrics, code2flow.exporters.toon.ToonExporter._compute_package_metrics, code2flow.exporters.toon.ToonExporter._compute_function_metrics, code2flow.exporters.toon.ToonExporter._compute_class_metrics, code2flow.exporters.toon.ToonExporter._compute_coupling_matrix, code2flow.exporters.toon.ToonExporter._detect_duplicates, code2flow.exporters.toon.ToonExporter._compute_health

### code2flow.optimization.advanced_optimizer.DataStructureOptimizer
> Advanced optimizer for data structures and flows.
- **Methods**: 22
- **Key Methods**: code2flow.optimization.advanced_optimizer.DataStructureOptimizer.__init__, code2flow.optimization.advanced_optimizer.DataStructureOptimizer._build_networkx_graph, code2flow.optimization.advanced_optimizer.DataStructureOptimizer.analyze_communities, code2flow.optimization.advanced_optimizer.DataStructureOptimizer.analyze_centrality, code2flow.optimization.advanced_optimizer.DataStructureOptimizer.analyze_type_patterns, code2flow.optimization.advanced_optimizer.DataStructureOptimizer.generate_refactoring_plan, code2flow.optimization.advanced_optimizer.DataStructureOptimizer.export_optimization_report, code2flow.optimization.advanced_optimizer.DataStructureOptimizer._get_community_patterns, code2flow.optimization.advanced_optimizer.DataStructureOptimizer._calculate_consolidation_potential, code2flow.optimization.advanced_optimizer.DataStructureOptimizer._generate_consolidation_recommendation

### code2flow.analysis.cfg.CFGExtractor
> Extract Control Flow Graph from AST.
- **Methods**: 17
- **Key Methods**: code2flow.analysis.cfg.CFGExtractor.__init__, code2flow.analysis.cfg.CFGExtractor.extract, code2flow.analysis.cfg.CFGExtractor.new_node, code2flow.analysis.cfg.CFGExtractor.connect, code2flow.analysis.cfg.CFGExtractor.visit_FunctionDef, code2flow.analysis.cfg.CFGExtractor.visit_AsyncFunctionDef, code2flow.analysis.cfg.CFGExtractor.visit_If, code2flow.analysis.cfg.CFGExtractor.visit_For, code2flow.analysis.cfg.CFGExtractor.visit_While, code2flow.analysis.cfg.CFGExtractor.visit_Try
- **Inherits**: ast.NodeVisitor

### code2flow.nlp.pipeline.NLPPipeline
> Main NLP processing pipeline (4a-4e).
- **Methods**: 16
- **Key Methods**: code2flow.nlp.pipeline.NLPPipeline.__init__, code2flow.nlp.pipeline.NLPPipeline.process, code2flow.nlp.pipeline.NLPPipeline._step_normalize, code2flow.nlp.pipeline.NLPPipeline._step_match_intent, code2flow.nlp.pipeline.NLPPipeline._step_resolve_entities, code2flow.nlp.pipeline.NLPPipeline._infer_entity_types, code2flow.nlp.pipeline.NLPPipeline._calculate_overall_confidence, code2flow.nlp.pipeline.NLPPipeline._calculate_entity_confidence, code2flow.nlp.pipeline.NLPPipeline._apply_fallback, code2flow.nlp.pipeline.NLPPipeline._format_action

### code2flow.nlp.entity_resolution.EntityResolver
> Resolve entities (functions, classes, etc.) from queries.
- **Methods**: 14
- **Key Methods**: code2flow.nlp.entity_resolution.EntityResolver.__init__, code2flow.nlp.entity_resolution.EntityResolver.resolve, code2flow.nlp.entity_resolution.EntityResolver._extract_candidates, code2flow.nlp.entity_resolution.EntityResolver._extract_from_patterns, code2flow.nlp.entity_resolution.EntityResolver._disambiguate, code2flow.nlp.entity_resolution.EntityResolver._resolve_hierarchical, code2flow.nlp.entity_resolution.EntityResolver._resolve_aliases, code2flow.nlp.entity_resolution.EntityResolver._name_similarity, code2flow.nlp.entity_resolution.EntityResolver.load_from_analysis, code2flow.nlp.entity_resolution.EntityResolver.step_3a_extract_entities

### code2flow.analysis.data_analysis.DataAnalyzer
> Analyze data flows, structures, and optimization opportunities.
- **Methods**: 13
- **Key Methods**: code2flow.analysis.data_analysis.DataAnalyzer.analyze_data_flow, code2flow.analysis.data_analysis.DataAnalyzer.analyze_data_structures, code2flow.analysis.data_analysis.DataAnalyzer._find_data_pipelines, code2flow.analysis.data_analysis.DataAnalyzer._find_state_patterns, code2flow.analysis.data_analysis.DataAnalyzer._find_data_dependencies, code2flow.analysis.data_analysis.DataAnalyzer._find_event_flows, code2flow.analysis.data_analysis.DataAnalyzer._analyze_data_types, code2flow.analysis.data_analysis.DataAnalyzer._infer_parameter_types, code2flow.analysis.data_analysis.DataAnalyzer._infer_return_types, code2flow.analysis.data_analysis.DataAnalyzer._build_data_flow_graph

### code2flow.analysis.call_graph.CallGraphExtractor
> Extract call graph from AST.
- **Methods**: 13
- **Key Methods**: code2flow.analysis.call_graph.CallGraphExtractor.__init__, code2flow.analysis.call_graph.CallGraphExtractor.extract, code2flow.analysis.call_graph.CallGraphExtractor._calculate_metrics, code2flow.analysis.call_graph.CallGraphExtractor.visit_Import, code2flow.analysis.call_graph.CallGraphExtractor.visit_ImportFrom, code2flow.analysis.call_graph.CallGraphExtractor.visit_ClassDef, code2flow.analysis.call_graph.CallGraphExtractor.visit_FunctionDef, code2flow.analysis.call_graph.CallGraphExtractor.visit_AsyncFunctionDef, code2flow.analysis.call_graph.CallGraphExtractor.visit_Call, code2flow.analysis.call_graph.CallGraphExtractor._qualified_name
- **Inherits**: ast.NodeVisitor

### code2flow.nlp.intent_matching.IntentMatcher
> Match queries to intents using fuzzy and keyword matching.
- **Methods**: 13
- **Key Methods**: code2flow.nlp.intent_matching.IntentMatcher.__init__, code2flow.nlp.intent_matching.IntentMatcher.match, code2flow.nlp.intent_matching.IntentMatcher._fuzzy_match, code2flow.nlp.intent_matching.IntentMatcher._keyword_match, code2flow.nlp.intent_matching.IntentMatcher._apply_context, code2flow.nlp.intent_matching.IntentMatcher._combine_matches, code2flow.nlp.intent_matching.IntentMatcher._resolve_multi_intent, code2flow.nlp.intent_matching.IntentMatcher._calculate_similarity, code2flow.nlp.intent_matching.IntentMatcher.step_2a_fuzzy_match, code2flow.nlp.intent_matching.IntentMatcher.step_2b_semantic_match

### code2flow.nlp.normalization.QueryNormalizer
> Normalize queries for consistent processing.
- **Methods**: 13
- **Key Methods**: code2flow.nlp.normalization.QueryNormalizer.__init__, code2flow.nlp.normalization.QueryNormalizer.normalize, code2flow.nlp.normalization.QueryNormalizer._unicode_normalize, code2flow.nlp.normalization.QueryNormalizer._lowercase, code2flow.nlp.normalization.QueryNormalizer._remove_punctuation, code2flow.nlp.normalization.QueryNormalizer._normalize_whitespace, code2flow.nlp.normalization.QueryNormalizer._remove_stopwords, code2flow.nlp.normalization.QueryNormalizer._tokenize, code2flow.nlp.normalization.QueryNormalizer.step_1a_lowercase, code2flow.nlp.normalization.QueryNormalizer.step_1b_remove_punctuation

### code2flow.analysis.dfg.DFGExtractor
> Extract Data Flow Graph from AST.
- **Methods**: 12
- **Key Methods**: code2flow.analysis.dfg.DFGExtractor.__init__, code2flow.analysis.dfg.DFGExtractor.extract, code2flow.analysis.dfg.DFGExtractor.visit_FunctionDef, code2flow.analysis.dfg.DFGExtractor.visit_Assign, code2flow.analysis.dfg.DFGExtractor.visit_AugAssign, code2flow.analysis.dfg.DFGExtractor.visit_For, code2flow.analysis.dfg.DFGExtractor.visit_Call, code2flow.analysis.dfg.DFGExtractor._extract_targets, code2flow.analysis.dfg.DFGExtractor._get_names, code2flow.analysis.dfg.DFGExtractor._extract_names
- **Inherits**: ast.NodeVisitor

### code2flow.exporters.llm_exporter.LLMPromptExporter
> Export LLM-ready analysis summary with architecture and flows.
- **Methods**: 12
- **Key Methods**: code2flow.exporters.llm_exporter.LLMPromptExporter.export, code2flow.exporters.llm_exporter.LLMPromptExporter._get_overview, code2flow.exporters.llm_exporter.LLMPromptExporter._get_architecture_by_module, code2flow.exporters.llm_exporter.LLMPromptExporter._get_important_entries, code2flow.exporters.llm_exporter.LLMPromptExporter._get_key_entry_points, code2flow.exporters.llm_exporter.LLMPromptExporter._get_process_flows, code2flow.exporters.llm_exporter.LLMPromptExporter._get_key_classes, code2flow.exporters.llm_exporter.LLMPromptExporter._get_data_transformations, code2flow.exporters.llm_exporter.LLMPromptExporter._get_behavioral_patterns, code2flow.exporters.llm_exporter.LLMPromptExporter._get_api_surface
- **Inherits**: Exporter

### code2flow.core.streaming_analyzer.StreamingAnalyzer
> Memory-efficient streaming analyzer with progress tracking.
- **Methods**: 11
- **Key Methods**: code2flow.core.streaming_analyzer.StreamingAnalyzer.__init__, code2flow.core.streaming_analyzer.StreamingAnalyzer.set_progress_callback, code2flow.core.streaming_analyzer.StreamingAnalyzer.cancel, code2flow.core.streaming_analyzer.StreamingAnalyzer.analyze_streaming, code2flow.core.streaming_analyzer.StreamingAnalyzer._quick_scan_file, code2flow.core.streaming_analyzer.StreamingAnalyzer._deep_analyze_file, code2flow.core.streaming_analyzer.StreamingAnalyzer._build_call_graph_streaming, code2flow.core.streaming_analyzer.StreamingAnalyzer._select_important_files, code2flow.core.streaming_analyzer.StreamingAnalyzer._collect_files, code2flow.core.streaming_analyzer.StreamingAnalyzer._estimate_eta

### examples.functional_refactoring_example.EvolutionaryCache
> Cache that evolves based on usage patterns.

Unlike simple LRU cache, this tracks success/failure ra
- **Methods**: 10
- **Key Methods**: examples.functional_refactoring_example.EvolutionaryCache.__init__, examples.functional_refactoring_example.EvolutionaryCache._load, examples.functional_refactoring_example.EvolutionaryCache._save, examples.functional_refactoring_example.EvolutionaryCache.get, examples.functional_refactoring_example.EvolutionaryCache.put, examples.functional_refactoring_example.EvolutionaryCache.report_success, examples.functional_refactoring_example.EvolutionaryCache.report_failure, examples.functional_refactoring_example.EvolutionaryCache._make_key, examples.functional_refactoring_example.EvolutionaryCache._calculate_score, examples.functional_refactoring_example.EvolutionaryCache._evict_worst

### code2flow.core.analyzer.FileAnalyzer
> Analyzes a single file.
- **Methods**: 10
- **Key Methods**: code2flow.core.analyzer.FileAnalyzer.__init__, code2flow.core.analyzer.FileAnalyzer.analyze_file, code2flow.core.analyzer.FileAnalyzer._analyze_ast, code2flow.core.analyzer.FileAnalyzer._process_class, code2flow.core.analyzer.FileAnalyzer._process_function, code2flow.core.analyzer.FileAnalyzer._build_cfg, code2flow.core.analyzer.FileAnalyzer._process_cfg_block, code2flow.core.analyzer.FileAnalyzer._get_base_name, code2flow.core.analyzer.FileAnalyzer._get_decorator_name, code2flow.core.analyzer.FileAnalyzer._get_call_name

### code2flow.core.analyzer.ProjectAnalyzer
> Main analyzer with parallel processing.
- **Methods**: 10
- **Key Methods**: code2flow.core.analyzer.ProjectAnalyzer.__init__, code2flow.core.analyzer.ProjectAnalyzer.analyze_project, code2flow.core.analyzer.ProjectAnalyzer._collect_files, code2flow.core.analyzer.ProjectAnalyzer._analyze_parallel, code2flow.core.analyzer.ProjectAnalyzer._analyze_sequential, code2flow.core.analyzer.ProjectAnalyzer._merge_results, code2flow.core.analyzer.ProjectAnalyzer._build_call_graph, code2flow.core.analyzer.ProjectAnalyzer._detect_patterns, code2flow.core.analyzer.ProjectAnalyzer._perform_refactoring_analysis, code2flow.core.analyzer.ProjectAnalyzer._detect_dead_code

### examples.functional_refactoring_example.TemplateGenerator
> Original - handles EVERYTHING: loading, matching, rendering, shell, docker, sql...
- **Methods**: 9
- **Key Methods**: examples.functional_refactoring_example.TemplateGenerator.__init__, examples.functional_refactoring_example.TemplateGenerator.generate, examples.functional_refactoring_example.TemplateGenerator._prepare_shell_entities, examples.functional_refactoring_example.TemplateGenerator._prepare_docker_entities, examples.functional_refactoring_example.TemplateGenerator._prepare_sql_entities, examples.functional_refactoring_example.TemplateGenerator._prepare_kubernetes_entities, examples.functional_refactoring_example.TemplateGenerator._apply_shell_find_flags, examples.functional_refactoring_example.TemplateGenerator._build_shell_find_name_flag, examples.functional_refactoring_example.TemplateGenerator._build_shell_find_size_flag

### code2flow.analysis.smells.SmellDetector
> Detect code smells from analysis results.
- **Methods**: 9
- **Key Methods**: code2flow.analysis.smells.SmellDetector.__init__, code2flow.analysis.smells.SmellDetector.detect, code2flow.analysis.smells.SmellDetector._detect_god_functions, code2flow.analysis.smells.SmellDetector._detect_god_modules, code2flow.analysis.smells.SmellDetector._detect_feature_envy, code2flow.analysis.smells.SmellDetector._detect_data_clumps, code2flow.analysis.smells.SmellDetector._detect_shotgun_surgery, code2flow.analysis.smells.SmellDetector._detect_bottlenecks, code2flow.analysis.smells.SmellDetector._detect_circular_dependencies

### code2flow.patterns.detector.PatternDetector
> Detect behavioral patterns in code.
- **Methods**: 8
- **Key Methods**: code2flow.patterns.detector.PatternDetector.__init__, code2flow.patterns.detector.PatternDetector.detect_patterns, code2flow.patterns.detector.PatternDetector._detect_recursion, code2flow.patterns.detector.PatternDetector._detect_state_machines, code2flow.patterns.detector.PatternDetector._detect_factory_pattern, code2flow.patterns.detector.PatternDetector._detect_singleton, code2flow.patterns.detector.PatternDetector._detect_strategy_pattern, code2flow.patterns.detector.PatternDetector._check_returns_classes

### examples.functional_refactoring_example.TemplateLoader
> Loads templates from various sources.
- **Methods**: 7
- **Key Methods**: examples.functional_refactoring_example.TemplateLoader.__init__, examples.functional_refactoring_example.TemplateLoader.load, examples.functional_refactoring_example.TemplateLoader._load_templates, examples.functional_refactoring_example.TemplateLoader._load_defaults, examples.functional_refactoring_example.TemplateLoader.get_template, examples.functional_refactoring_example.TemplateLoader.get_default, examples.functional_refactoring_example.TemplateLoader.find_alternative_template

### code2flow.exporters.yaml_exporter.YAMLExporter
> Export to YAML format.
- **Methods**: 7
- **Key Methods**: code2flow.exporters.yaml_exporter.YAMLExporter.__init__, code2flow.exporters.yaml_exporter.YAMLExporter.export, code2flow.exporters.yaml_exporter.YAMLExporter.export_grouped, code2flow.exporters.yaml_exporter.YAMLExporter.export_data_flow, code2flow.exporters.yaml_exporter.YAMLExporter.export_data_structures, code2flow.exporters.yaml_exporter.YAMLExporter.export_separated, code2flow.exporters.yaml_exporter.YAMLExporter.export_split
- **Inherits**: Exporter

## Data Transformation Functions

Key functions that process and transform data:

### validate_toon.validate_toon_completeness
> Validate toon format structure.
- **Output to**: print, print, toon_data.get, print, enumerate

### code2flow.mermaid_generator.validate_mermaid_file
> Validate Mermaid file and return list of errors.
- **Output to**: mmd_path.exists, mmd_path.read_text, None.split, enumerate, re.compile

### code2flow.llm_task_generator._parse_bullets
- **Output to**: raw.strip, s.startswith, items.append, items.append, None.strip

### code2flow.llm_task_generator.parse_llm_task_text
- **Output to**: code2flow.llm_task_generator._strip_bom, None.split, _SECTION_KEYS.items, sections.get, sections.get

### code2flow.llm_task_generator.create_parser
- **Output to**: argparse.ArgumentParser, p.add_argument, p.add_argument, p.add_argument

### code2flow.llm_flow_generator._parse_call_label
- **Output to**: None.strip, None.strip, None.replace, re.match, re.match

### code2flow.llm_flow_generator._parse_func_label
- **Output to**: None.strip, label.startswith, None.strip, len

### code2flow.llm_flow_generator.create_parser
- **Output to**: argparse.ArgumentParser, p.add_argument, p.add_argument, p.add_argument, p.add_argument

### code2flow.analysis.data_analysis.DataAnalyzer._identify_process_patterns
- **Output to**: result.functions.items, patterns.items, sorted, func.name.lower, indicators.items

### code2flow.cli.create_parser
> Create CLI argument parser.
- **Output to**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument

### code2flow.analysis.cfg.CFGExtractor._format_except
> Format except handler.
- **Output to**: self._expr_to_str

### code2flow.nlp.pipeline.NLPPipeline.process
> Process query through full pipeline (4a-4e).
- **Output to**: time.time, time.time, self._step_normalize, stages.append, time.time

### code2flow.nlp.pipeline.NLPPipeline._format_action
> 4e. Format action recommendation.
- **Output to**: result.get_intent, result.get_entities

### code2flow.nlp.pipeline.NLPPipeline._format_response
> 4e. Format human-readable response.
- **Output to**: None.join, lines.append, lines.append, lines.append, result.get_intent

### code2flow.nlp.pipeline.NLPPipeline.step_4e_format
> Step 4e: Output formatting.
- **Output to**: self._format_response

### code2flow.exporters.llm_exporter.LLMPromptExporter._get_process_flows
- **Output to**: set, set, seen_base_names.add, self._trace_flow, ep_name.split

### code2flow.exporters.llm_exporter.LLMPromptExporter._get_data_transformations
- **Output to**: lines.append, lines.append, result.functions.items, any, lines.append

### code2flow.core.analyzer.FastFileFilter.should_process
> Check if file should be processed.
- **Output to**: file_path.lower, any, fnmatch.fnmatch, fnmatch.fnmatch

### code2flow.core.analyzer.FileAnalyzer._process_class
> Process class definition.
- **Output to**: ClassInfo, None.classes.append, isinstance, isinstance, methods.append

### code2flow.core.analyzer.FileAnalyzer._process_function
> Process function definition with limited CFG depth.
- **Output to**: func_name.startswith, any, FastFileFilter, filter_obj.should_skip_function, FunctionInfo

### code2flow.core.analyzer.FileAnalyzer._process_cfg_block
> Process a block of statements for CFG with depth limiting.
- **Output to**: None.append, isinstance, None.append, FlowEdge, FlowNode

## Behavioral Patterns

### state_machine_IncrementalAnalyzer
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: code2flow.core.streaming_analyzer.IncrementalAnalyzer.__init__, code2flow.core.streaming_analyzer.IncrementalAnalyzer._load_state, code2flow.core.streaming_analyzer.IncrementalAnalyzer._save_state, code2flow.core.streaming_analyzer.IncrementalAnalyzer.get_changed_files, code2flow.core.streaming_analyzer.IncrementalAnalyzer._get_module_name

### state_machine_OptimizationImplementer
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: code2flow.optimization.implementation.OptimizationImplementer.__init__, code2flow.optimization.implementation.OptimizationImplementer.implement_unified_validation_framework, code2flow.optimization.implementation.OptimizationImplementer.implement_generic_filter_map_framework, code2flow.optimization.implementation.OptimizationImplementer.implement_hub_function_splitting, code2flow.optimization.implementation.OptimizationImplementer.generate_optimization_report

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `code2flow.cli.main` - 117 calls
- `code2flow.mermaid_generator.fix_mermaid_file` - 55 calls
- `validate_toon.main` - 45 calls
- `code2flow.llm_task_generator.normalize_llm_task` - 43 calls
- `code2flow.llm_flow_generator.render_llm_flow_md` - 42 calls
- `benchmarks.benchmark_performance.main` - 40 calls
- `validate_toon.analyze_class_differences` - 39 calls
- `code2flow.mermaid_generator.validate_mermaid_file` - 38 calls
- `code2flow.exporters.toon.ToonExporter.export` - 35 calls
- `code2flow.core.analyzer.ProjectAnalyzer.analyze_project` - 35 calls
- `code2flow.llm_task_generator.parse_llm_task_text` - 32 calls
- `benchmarks.benchmark_performance.create_test_project` - 29 calls
- `code2flow.nlp.pipeline.NLPPipeline.process` - 29 calls
- `validate_toon.compare_modules` - 26 calls
- `code2flow.core.streaming_analyzer.StreamingAnalyzer.analyze_streaming` - 26 calls
- `code2flow.visualizers.graph.GraphVisualizer.visualize_cfg` - 26 calls
- `code2flow.exporters.llm_exporter.LLMPromptExporter.export` - 25 calls
- `validate_toon.compare_functions` - 24 calls
- `code2flow.mermaid_generator.generate_single_png` - 24 calls
- `code2flow.cli.create_parser` - 23 calls
- `code2flow.visualizers.graph.GraphVisualizer.visualize_call_graph` - 23 calls
- `code2flow.cli.generate_llm_context` - 21 calls
- `code2flow.exporters.mermaid_exporter.MermaidExporter.export_call_graph` - 20 calls
- `validate_toon.compare_classes` - 19 calls
- `validate_toon.validate_toon_completeness` - 19 calls
- `code2flow.core.streaming_analyzer.SmartPrioritizer.prioritize_files` - 19 calls
- `code2flow.exporters.yaml_exporter.YAMLExporter.export_grouped` - 19 calls
- `code2flow.llm_flow_generator.main` - 18 calls
- `examples.functional_refactoring_example.generate` - 16 calls
- `code2flow.optimization.advanced_optimizer.DataStructureOptimizer.analyze_centrality` - 16 calls
- `code2flow.nlp.config.NLPConfig.from_yaml` - 15 calls
- `benchmarks.benchmark_performance.benchmark_original_analyzer` - 14 calls
- `code2flow.analysis.smells.SmellDetector.detect` - 14 calls
- `code2flow.llm_task_generator.main` - 13 calls
- `code2flow.optimization.advanced_optimizer.DataStructureOptimizer.analyze_communities` - 13 calls
- `code2flow.llm_flow_generator.generate_llm_flow` - 12 calls
- `benchmarks.benchmark_performance.benchmark_streaming_analyzer` - 12 calls
- `code2flow.analysis.dfg.DFGExtractor.visit_Call` - 12 calls
- `code2flow.core.streaming_analyzer.IncrementalAnalyzer.get_changed_files` - 12 calls
- `code2flow.nlp.normalization.QueryNormalizer.normalize` - 12 calls

## System Interactions

How components interact:

```mermaid
graph TD
    main --> create_parser
    main --> parse_args
    main --> Path
    main --> mkdir
    main --> len
    main --> print
    main --> load_yaml
    main --> create_test_project
    _compute_file_metric --> items
    _compute_file_metric --> defaultdict
    export --> _build_context
    export --> extend
    export --> append
    analyze_project --> time
    analyze_project --> resolve
    analyze_project --> _collect_files
    analyze_project --> _merge_results
    analyze_project --> _build_call_graph
    _process_cfg_block --> append
    _process_cfg_block --> isinstance
    _process_cfg_block --> FlowEdge
    _process_cfg_block --> FlowNode
    _render_coupling --> sorted
    _render_coupling --> sort
    _render_coupling --> max
    _render_coupling --> len
    process --> time
    process --> _step_normalize
    process --> append
    _perform_refactoring --> CallGraphExtractor
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.