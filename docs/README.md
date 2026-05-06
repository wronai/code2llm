<!-- code2docs:start --># code2llm

![version](https://img.shields.io/badge/version-0.1.0-blue) ![python](https://img.shields.io/badge/python-%3E%3D3.8-blue) ![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey) ![functions](https://img.shields.io/badge/functions-2864-green)
> **2864** functions | **155** classes | **336** files | CC̄ = 3.9

> Auto-generated project documentation from source code analysis.

**Author:** Tom Sapletta  
**License:** Apache-2.0[(LICENSE)](./LICENSE)  
**Repository:** [https://github.com/wronai/code2flow](https://github.com/wronai/code2flow)

## Installation

### From PyPI

```bash
pip install code2llm
```

### From Source

```bash
git clone https://github.com/wronai/code2flow
cd code2llm
pip install -e .
```

### Optional Extras

```bash
pip install code2llm[dev]    # development tools
```

## Quick Start

### CLI Usage

```bash
# Generate full documentation for your project
code2llm ./my-project

# Only regenerate README
code2llm ./my-project --readme-only

# Preview what would be generated (no file writes)
code2llm ./my-project --dry-run

# Check documentation health
code2llm check ./my-project

# Sync — regenerate only changed modules
code2llm sync ./my-project
```

### Python API

```python
from code2llm import generate_readme, generate_docs, Code2DocsConfig

# Quick: generate README
generate_readme("./my-project")

# Full: generate all documentation
config = Code2DocsConfig(project_name="mylib", verbose=True)
docs = generate_docs("./my-project", config=config)
```




## Architecture

```
code2llm/
    ├── toon
├── redsl
├── orchestrator
├── goal
├── planfile
├── Makefile
    ├── toon
├── setup
├── validate_toon
├── pyqual
├── requirements
├── pyproject
├── calls
├── pipeline
├── project2
├── prefact
├── Taskfile
    ├── toon
├── project
    ├── toon
    ├── toon
    ├── prompt
        ├── sample
        ├── sample_bad
    ├── prompt
    ├── functional_refactoring_example
        ├── toon
        ├── run
        ├── run-doql
        ├── fluent-bit
        ├── docker-compose
        ├── prometheus
            ├── Main
            ├── main
            ├── main
            ├── requirements
            ├── worker
            ├── Cargo
                ├── main
            ├── index
        ├── node/
            ├── app
        ├── cli
        ├── generator
    ├── functional_refactoring/
        ├── entity_preparers
        ├── template_engine
        ├── models
        ├── cache
        ├── demo
            ├── auth
        ├── sample_project/
            ├── api
            ├── database
            ├── utils
            ├── main
    ├── benchmark_evolution
    ├── reporting
    ├── format_evaluator
    ├── benchmark_format_quality
    ├── benchmark_performance
    ├── project_generator
    ├── benchmark_optimizations
    ├── benchmark_constants
        ├── toon
    ├── prompt
        ├── toon
        ├── toon
    ├── benchmark_badges
    ├── bump_version
    ├── server
        ├── toon
    ├── prompt
        ├── toon
    ├── refactor-prompt
            ├── toon
            ├── toon
            ├── toon
            ├── toon
            ├── toon
            ├── toon
            ├── toon
            ├── toon
            ├── toon
            ├── toon
        ├── toon
    ├── calls
    ├── valid/
        ├── sample
    ├── calls
        ├── toon
    ├── cli
    ├── cli_analysis
├── code2llm/
    ├── __main__
    ├── api
    ├── cli_parser
        ├── code2llm_incremental
    ├── cli_commands
        ├── data_analysis
        ├── pipeline_detector
        ├── type_inference
    ├── analysis/
        ├── pipeline_resolver
        ├── dfg
        ├── call_graph
        ├── pipeline_classifier
        ├── coupling
        ├── cfg
        ├── side_effects
        ├── smells
            ├── ast_helpers
        ├── utils/
        ├── config
        ├── file_cache
        ├── ast_registry
        ├── incremental
        ├── analyzer
        ├── large_repo
        ├── repo_files
    ├── core/
        ├── streaming_analyzer
        ├── gitignore
        ├── toon_size_manager
        ├── models
        ├── refactoring
        ├── file_analyzer
        ├── persistent_cache
        ├── file_filter
        ├── export_pipeline
            ├── incremental
            ├── strategies
        ├── streaming/
            ├── prioritizer
            ├── scanner
            ├── cache
            ├── rust
            ├── ruby
            ├── base
            ├── cpp
        ├── lang/
            ├── ts_extractors
            ├── ts_parser
            ├── php
            ├── csharp
            ├── go_lang
            ├── java
            ├── generic
            ├── typescript
        ├── config
    ├── nlp/
        ├── intent_matching
        ├── entity_resolution
        ├── pipeline
        ├── normalization
        ├── readme_exporter
        ├── base
        ├── map_exporter
        ├── project_yaml_exporter
        ├── mermaid_flow_helpers
        ├── mermaid_exporter
        ├── toon/
        ├── dashboard_renderer
    ├── exporters/
        ├── json_exporter
        ├── report_generators
        ├── yaml_exporter
        ├── context_view
        ├── article_view
        ├── dashboard_data
        ├── evolution_exporter
        ├── context_exporter
        ├── llm_exporter
        ├── validate_project
        ├── flow_constants
        ├── html_dashboard
        ├── flow_renderer
        ├── toon_view
        ├── flow_exporter
        ├── index_generator/
            ├── content
            ├── files
        ├── readme/
            ├── insights
            ├── sections
            ├── helpers
            ├── metrics_duplicates
            ├── metrics
            ├── module_detail
            ├── metrics_health
            ├── metrics_core
            ├── renderer
            ├── evolution
        ├── project_yaml/
            ├── health
            ├── modules
            ├── hotspots
            ├── core
            ├── constants
            ├── render
            ├── yaml_export
        ├── evolution/
            ├── exclusion
            ├── constants
            ├── computation
            ├── alerts
            ├── module_list
            ├── details
            ├── header
            ├── yaml_export
        ├── map/
            ├── utils
            ├── scanner
            ├── renderer
            ├── compact
            ├── classic
        ├── mermaid/
            ├── flow_detailed
            ├── calls
            ├── flow_compact
            ├── utils
            ├── flow_full
        ├── _utils
    ├── generators/
        ├── llm_flow/
        ├── llm_task
        ├── mermaid/
            ├── cli
            ├── parsing
            ├── analysis
            ├── generator
            ├── utils
            ├── nodes
            ├── validation
            ├── png
            ├── fix
        ├── formats
        ├── code2logic
        ├── orchestrator_chunked
    ├── cli_exports/
        ├── orchestrator_handlers
        ├── prompt
        ├── orchestrator_constants
        ├── orchestrator
    ├── refactor/
        ├── prompt_engine
        ├── toon_parser
        ├── detector
        ├── sample
├── prompt_sumd_sumr_feature
├── TODO
├── redsl_refactor_report
├── context
├── ROADMAP
├── redsl_refactor_plan
    ├── README
├── README
├── REFACTORING_PLAN
    ├── API
    ├── context
        ├── context
    ├── context
        ├── context
        ├── context
        ├── context
        ├── README
        ├── DEPENDENCY_ANALYSIS
    ├── README
    ├── LLM_USAGE
        ├── README
        ├── README
        ├── SUMMARY
        ├── ANALYSIS
    ├── README
        ├── README
├── CHANGELOG
    ├── METHODOLOGY
        ├── README
    ├── PROJECT_SUMMARY
        ├── README
    ├── README
    ├── COMPARISON_AND_OPTIMIZATION
        ├── context
        ├── context
    ├── README
    ├── context
        ├── toon
        ├── toon
        ├── context
        ├── context
    ├── README
        ├── toon
    ├── context
    ├── README
        ├── toon
        ├── context
    ├── context
        ├── context
        ├── README
    ├── README
    ├── context
    ├── context
        ├── move_method
        ├── extract_method
        ├── context
├── SUMR
├── SUMD
    ├── calls
        ├── toon
```

## API Overview

### Classes

- **`User`** — —
- **`UserService`** — —
- **`Product`** — —
- **`ProductRepository`** — —
- **`User`** — —
- **`UserService`** — —
- **`TemplateGenerator`** — Original - handles EVERYTHING: loading, matching, rendering, shell, docker, sql...
- **`Main`** — —
- **`CustomHandler`** — —
- **`Response`** — —
- **`Response`** — —
- **`CommandGenerator`** — Generates commands from natural language intents.
- **`EntityPreparer`** — Protocol for domain-specific entity preparation.
- **`ShellEntityPreparer`** — Prepares entities for shell commands.
- **`DockerEntityPreparer`** — Prepares entities for docker commands.
- **`SQLEntityPreparer`** — Prepares entities for SQL commands.
- **`KubernetesEntityPreparer`** — Prepares entities for kubernetes commands.
- **`EntityPreparationPipeline`** — Coordinates entity preparation across domains.
- **`Template`** — Command template.
- **`TemplateLoader`** — Loads templates from various sources.
- **`TemplateRenderer`** — Renders templates with entity substitution.
- **`CommandContext`** — Context for command generation.
- **`CommandResult`** — Result of command generation.
- **`CacheEntry`** — Single cache entry with evolution metadata.
- **`EvolutionaryCache`** — Cache that evolves based on usage patterns.
- **`AuthManager`** — Manages user authentication and authorization.
- **`APIHandler`** — Handles API requests and responses.
- **`DatabaseConnection`** — Simple database connection simulator.
- **`UserRequest`** — User request data structure.
- **`Application`** — Main application class with multiple responsibilities.
- **`FormatScore`** — Wynik oceny pojedynczego formatu.
- **`User`** — —
- **`UserService`** — —
- **`DataAnalyzer`** — Analyze data flows, structures, and optimization opportunities.
- **`DataFlowAnalyzer`** — Analyze data flows: pipelines, state patterns, dependencies, and event flows.
- **`OptimizationAdvisor`** — Analyze optimization opportunities: data types and process patterns.
- **`PipelineStage`** — A single stage in a detected pipeline.
- **`Pipeline`** — A detected pipeline with stages, purity info, and domain.
- **`PipelineDetector`** — Detect pipelines in a codebase using networkx graph analysis.
- **`TypeInferenceEngine`** — Extract and infer type information from Python source files.
- **`PipelineResolver`** — Resolves callee names to qualified function names.
- **`DFGExtractor`** — Extract Data Flow Graph from AST.
- **`CallGraphExtractor`** — Extract call graph from AST.
- **`PipelineClassifier`** — Classify pipelines by domain and derive human-readable names.
- **`CouplingAnalyzer`** — Analyze coupling between modules.
- **`CFGExtractor`** — Extract Control Flow Graph from AST.
- **`SideEffectInfo`** — Side-effect analysis result for a single function.
- **`SideEffectDetector`** — Detect side effects in Python functions via AST analysis.
- **`SmellDetector`** — Detect code smells from analysis results.
- **`AnalysisMode`** — Available analysis modes.
- **`PerformanceConfig`** — Performance optimization settings.
- **`FilterConfig`** — Filtering options to reduce analysis scope.
- **`DepthConfig`** — Depth limiting for control flow analysis.
- **`OutputConfig`** — Output formatting options.
- **`Config`** — Analysis configuration with performance optimizations.
- **`FileCache`** — Cache for parsed AST files.
- **`ASTRegistry`** — Parse each file exactly once; share the AST across all analysis consumers.
- **`IncrementalAnalyzer`** — Track file signatures to skip unchanged files on subsequent runs.
- **`ProjectAnalyzer`** — Main analyzer with parallel processing.
- **`SubProject`** — Represents a sub-project within a larger repository.
- **`HierarchicalRepoSplitter`** — Splits large repositories using hierarchical approach.
- **`StreamingAnalyzer`** — Memory-efficient streaming analyzer with progress tracking.
- **`GitIgnoreParser`** — Parse and apply .gitignore patterns to file paths.
- **`BaseModel`** — Base class for models with automated serialization.
- **`FlowNode`** — Represents a node in the control flow graph.
- **`FlowEdge`** — Represents an edge in the control flow graph.
- **`FunctionInfo`** — Information about a function/method.
- **`ClassInfo`** — Information about a class.
- **`ModuleInfo`** — Information about a module/package.
- **`Pattern`** — Detected behavioral pattern.
- **`CodeSmell`** — Represents a detected code smell.
- **`Mutation`** — Represents a mutation of a variable/object.
- **`DataFlow`** — Represents data flow for a variable.
- **`AnalysisResult`** — Complete analysis result for a project.
- **`RefactoringAnalyzer`** — Performs refactoring analysis on code.
- **`FileAnalyzer`** — Analyzes a single file.
- **`PersistentCache`** — Content-addressed persistent cache stored in ~/.code2llm/.
- **`FastFileFilter`** — Fast file filtering with pattern matching.
- **`SharedExportContext`** — Pre-computed context shared across all exporters.
- **`ExportPipeline`** — Run multiple exporters with a single shared context.
- **`StreamingIncrementalAnalyzer`** — Incremental analysis with change detection for streaming analyzer.
- **`ScanStrategy`** — Scanning methodology configuration.
- **`FilePriority`** — Priority scoring for file analysis order.
- **`SmartPrioritizer`** — Smart file prioritization for optimal analysis order.
- **`StreamingScanner`** — Handles file scanning operations.
- **`StreamingFileCache`** — Memory-efficient cache with LRU eviction.
- **`RubyParser`** — Ruby language parser - registered via @register_language in __init__.py.
- **`LanguageParser`** — Abstract base class for language-specific parsers.
- **`TreeSitterParser`** — Unified tree-sitter parser for all supported languages.
- **`NormalizationConfig`** — Configuration for query normalization.
- **`IntentMatchingConfig`** — Configuration for intent matching.
- **`EntityResolutionConfig`** — Configuration for entity resolution.
- **`MultilingualConfig`** — Configuration for multilingual processing.
- **`NLPConfig`** — Main NLP pipeline configuration.
- **`IntentMatch`** — Single intent match result.
- **`IntentMatchingResult`** — Result of intent matching.
- **`IntentMatcher`** — Match queries to intents using fuzzy and keyword matching.
- **`Entity`** — Resolved entity.
- **`EntityResolutionResult`** — Result of entity resolution.
- **`EntityResolver`** — Resolve entities (functions, classes, etc.) from queries.
- **`NlpPipelineStage`** — Single NLP pipeline stage result.
- **`NLPPipelineResult`** — Complete NLP pipeline result (4b-4e aggregation).
- **`NLPPipeline`** — Main NLP processing pipeline (4a-4e).
- **`NormalizationResult`** — Result of query normalization.
- **`QueryNormalizer`** — Normalize queries for consistent processing.
- **`READMEExporter`** — Export README.md with documentation of all generated files.
- **`BaseExporter`** — Abstract base class for all code2llm exporters.
- **`ViewGeneratorMixin`** — Mixin providing the shared ``generate`` implementation for view generators.
- **`MapExporter`** — Export to map.toon.yaml — structural map with a compact project header.
- **`MermaidExporter`** — Export call graph to Mermaid format.
- **`DashboardRenderer`** — Render HTML dashboard from prepared data structures.
- **`JSONExporter`** — Export to JSON format.
- **`YAMLExporter`** — Export to YAML format.
- **`ContextViewGenerator`** — Generate context.md from project.yaml data.
- **`ArticleViewGenerator`** — Generate status.md — publishable project health article.
- **`DashboardDataBuilder`** — Build dashboard data structures from project analysis results.
- **`EvolutionExporter`** — Export evolution.toon.yaml — prioritized refactoring queue.
- **`ContextExporter`** — Export LLM-ready analysis summary with architecture and flows.
- **`HTMLDashboardGenerator`** — Generate dashboard.html from project.yaml data.
- **`FlowRenderer`** — Renderer dla sekcji formatu flow.toon.
- **`ToonViewGenerator`** — Generate project.toon.yaml from project.yaml data.
- **`FlowExporter`** — Export to flow.toon — data-flow focused format.
- **`DuplicatesMetricsComputer`** — Detects duplicate classes in the codebase.
- **`ToonExporter`** — Export to toon v2 plain-text format — scannable, sorted by severity.
- **`MetricsComputer`** — Computes all metrics for TOON export.
- **`ModuleDetailRenderer`** — Renders detailed module information.
- **`HealthMetricsComputer`** — Computes health issues and quality alerts.
- **`CoreMetricsComputer`** — Computes core structural and complexity metrics.
- **`ToonRenderer`** — Renders all sections for TOON export.
- **`ProjectYAMLExporter`** — Export unified project.yaml — single source of truth for diagnostics.
- **`IndexHTMLGenerator`** — Generate index.html for browsing all generated files.
- **`FileScanner`** — Scan output directory and collect file metadata.
- **`HTMLRenderer`** — Render the index.html page with CSS and JavaScript.
- **`FuncSummary`** — —
- **`PromptEngine`** — Generate refactoring prompts from analysis results and detected smells.
- **`PatternDetector`** — Detect behavioral patterns in code.
- **`User`** — —
- **`UserService`** — —
- **`Order`** — —
- **`OrderService`** — —
- **`PatternDetector`** — —
- **`LanguageAnalyzer`** — —
- **`ProjectAnalyzer`** — —
- **`AnalysisResult`** — —
- **`NLPPipeline`** — —
- **`QueryNormalizer`** — —
- **`IntentMatcher`** — —
- **`EntityResolver`** — —
- **`StreamingAnalyzer`** — —
- **`TemplateGenerator`** — —
- **`CommandGenerator`** — —
- **`IntentMatcher`** — —
- **`CommandCache`** — —
- **`SchemaValidator`** — —

### Functions

- `read_version()` — —
- `read_readme()` — —
- `load_yaml(filepath)` — Load YAML file safely.
- `load_file(filepath)` — Load file - auto-detect TOON vs YAML format.
- `extract_functions_from_yaml(yaml_data)` — Extract function list from standard YAML format.
- `extract_functions_from_toon(toon_data)` — Extract function list from parsed TOON data.
- `extract_classes_from_yaml(yaml_data)` — Extract class list from standard YAML format.
- `extract_classes_from_toon(toon_data)` — Extract class list from parsed TOON data.
- `analyze_class_differences(yaml_data, toon_data)` — Analyze why classes differ between formats.
- `extract_modules_from_yaml(yaml_data)` — Extract module list from standard YAML format.
- `extract_modules_from_toon(toon_data)` — Extract module list from parsed TOON data.
- `compare_basic_stats(yaml_data, toon_data)` — Compare basic statistics.
- `compare_functions(yaml_data, toon_data)` — Compare function lists.
- `compare_classes(yaml_data, toon_data)` — Compare class lists with detailed analysis.
- `compare_modules(yaml_data, toon_data)` — Compare module lists with detailed analysis.
- `validate_toon_completeness(toon_data)` — Validate toon format structure.
- `main()` — Main validation function.
- `run_pipeline(project_dir, output_dir)` — Run unified pipeline in single process.
- `print()` — —
- `analyze_ruby()` — —
- `extract_function_body()` — —
- `calculate_complexity_regex()` — —
- `extract_calls_regex()` — —
- `analyze_c_family()` — —
- `normalize_llm_task()` — —
- `parse_llm_task_text()` — —
- `load_input()` — —
- `create_parser()` — —
- `main()` — —
- `parse_evolution_metrics()` — —
- `load_previous()` — —
- `save_current()` — —
- `run_benchmark()` — —
- `get_shield_url()` — —
- `parse_format_quality_report()` — —
- `parse_performance_report()` — —
- `generate_badges()` — —
- `generate_format_quality_badges()` — —
- `generate_performance_badges()` — —
- `create_html()` — —
- `load_project_yaml()` — —
- `extract_insights()` — —
- `build_health()` — —
- `build_alerts()` — —
- `count_duplicates()` — —
- `build_hotspots()` — —
- `hotspot_note()` — —
- `build_refactoring()` — —
- `render_details()` — —
- `export_compact()` — —
- `export_calls()` — —
- `handle_special_commands()` — —
- `handle_cache_command()` — —
- `handle_report_command()` — —
- `validate_and_setup()` — —
- `print_start_info()` — —
- `validate_chunked_output()` — —
- `generate_llm_context()` — —
- `analyze_generic()` — —
- `validate_mermaid_file()` — —
- `validate_project_yaml()` — —
- `build_modules()` — —
- `group_by_file()` — —
- `compute_module_entry()` — —
- `compute_inbound_deps()` — —
- `build_exports()` — —
- `build_class_export()` — —
- `build_function_exports()` — —
- `export_to_yaml()` — —
- `should_skip_module()` — —
- `is_entry_point()` — —
- `build_callers_graph()` — —
- `find_leaves()` — —
- `find_critical_path()` — —
- `export_flow_compact()` — —
- `get_file_size_kb()` — —
- `should_split_toon()` — —
- `split_toon_file()` — —
- `manage_toon_size()` — —
- `get_all_projects()` — —
- `clear_all()` — —
- `analyze_go()` — —
- `render_header()` — —
- `render_next()` — —
- `render_risks()` — —
- `render_metrics_target()` — —
- `render_patterns()` — —
- `render_history()` — —
- `compute_func_data()` — —
- `scan_file_sizes()` — —
- `aggregate_file_stats()` — —
- `make_relative_path()` — —
- `filter_god_modules()` — —
- `compute_god_modules()` — —
- `compute_hub_types()` — —
- `build_context()` — —
- `generate_llm_flow()` — —
- `render_llm_flow_md()` — —
- `run_pipeline()` — —
- `should_use_chunking()` — —
- `get_analysis_plan()` — —
- `analyze_rust()` — —
- `get_ast()` — —
- `find_function_node()` — —
- `ast_unparse()` — —
- `qualified_name()` — —
- `expr_to_str()` — —
- `should_skip_file()` — —
- `collect_files_in_dir()` — —
- `collect_root_files()` — —
- `count_py_files()` — —
- `contains_python_files()` — —
- `get_level1_dirs()` — —
- `calculate_priority()` — —
- `analyze_php()` — —
- `load_evolution_trend()` — —
- `rel_path()` — —
- `file_line_count()` — —
- `count_total_lines()` — —
- `detect_languages()` — —
- `export_classic()` — —
- `generate_pngs()` — —
- `generate_single_png()` — —
- `generate_with_puppeteer()` — —
- `fix_mermaid_file()` — —
- `parse_toon_content()` — —
- `is_toon_file()` — —
- `load_toon()` — —
- `load_yaml()` — —
- `load_file()` — —
- `extract_functions_from_yaml()` — —
- `extract_functions_from_toon()` — —
- `extract_classes_from_yaml()` — —
- `extract_classes_from_toon()` — —
- `analyze_class_differences()` — —
- `extract_modules_from_yaml()` — —
- `extract_modules_from_toon()` — —
- `compare_basic_stats()` — —
- `compare_functions()` — —
- `compare_classes()` — —
- `compare_modules()` — —
- `validate_toon_completeness()` — —
- `validate_input()` — —
- `format_output()` — —
- `calculate_metrics()` — —
- `filter_data()` — —
- `transform_data()` — —
- `clear_caches()` — —
- `run_analysis()` — —
- `benchmark_cold_vs_warm()` — —
- `print_summary()` — —
- `load_gitignore_patterns()` — —
- `extract_declarations_ts()` — —
- `get_parser()` — —
- `parse_source()` — —
- `is_available()` — —
- `build_core_files_section()` — —
- `build_llm_files_section()` — —
- `build_viz_files_section()` — —
- `generate()` — —
- `print_results()` — —
- `build_report()` — —
- `save_report()` — —
- `create_test_project()` — —
- `benchmark_original_analyzer()` — —
- `benchmark_streaming_analyzer()` — —
- `benchmark_with_strategies()` — —
- `print_comparison()` — —
- `is_excluded_path()` — —
- `build_evolution()` — —
- `load_previous_evolution()` — —
- `readable_id()` — —
- `safe_module()` — —
- `module_of()` — —
- `build_name_index()` — —
- `resolve_callee()` — —
- `write_file()` — —
- `get_cc()` — —
- `demo_quick_strategy()` — —
- `demo_standard_strategy()` — —
- `demo_deep_strategy()` — —
- `demo_incremental_analysis()` — —
- `demo_memory_limited()` — —
- `demo_custom_progress()` — —
- `evaluate_format()` — —
- `make_cache_key()` — —
- `is_excluded()` — —
- `get_file_types()` — —
- `get_default_file_info()` — —
- `get_refactoring_advice()` — —
- `get_current_version()` — —
- `parse_version()` — —
- `format_version()` — —
- `bump_version()` — —
- `update_pyproject_toml()` — —
- `update_version_file()` — —
- `index()` — —
- `get_badges()` — —
- `render_module_list()` — —
- `http()` — —
- `os()` — —
- `PORT()` — —
- `SERVICE_NAME()` — —
- `DB_HOST()` — —
- `server()` — —
- `read_version()` — —
- `read_readme()` — —
- `healthHandler()` — —
- `apiHandler()` — —
- `analyze()` — —
- `analyze_file()` — —
- `get_version()` — —
- `export_format()` — —
- `get_exporter()` — —
- `list_exporters()` — —
- `get_existing_files()` — —
- `process_message()` — —
- `sendResponse()` — —
- `create_core_py()` — —
- `create_etl_py()` — —
- `create_validation_py()` — —
- `create_utils_py()` — —
- `add_validator_to_core()` — —
- `create_ground_truth_project()` — —
- `analyze_cpp()` — —
- `register_language()` — —
- `list_parsers()` — —
- `analyze_csharp()` — —
- `analyze_java()` — —
- `get_typescript_patterns()` — —
- `get_typescript_lang_config()` — —
- `analyze_typescript_js()` — —
- `generate_index_html()` — —
- `generate_readme_content()` — —
- `export_flow_detailed()` — —
- `export_flow_full()` — —
- `dump_yaml()` — —
- `print()` — —
- `detect_factory()` — —
- `detect_singleton()` — —
- `detect_observer()` — —
- `parse_file()` — —
- `extract_functions()` — —
- `analyze_project()` — —
- `get_function_count()` — —
- `get_class_count()` — —
- `to_dict()` — —
- `process()` — —
- `normalize()` — —
- `step_1a_lowercase()` — —
- `step_1b_remove_punctuation()` — —
- `step_1c_normalize_whitespace()` — —
- `step_1d_unicode_normalize()` — —
- `step_1e_remove_stopwords()` — —
- `match()` — —
- `step_2a_fuzzy_match()` — —
- `step_2c_keyword_match()` — —
- `step_2d_context_score()` — —
- `resolve()` — —
- `load_from_analysis()` — —
- `repair_command()` — —
- `get_file_hash()` — —
- `parse_file_cached()` — —
- `generate_command()` — —
- `render_template()` — —
- `optimize_output()` — —
- `cache_result()` — —
- `load_patterns()` — —
- `fuzzy_match()` — —
- `validate_schema()` — —
- `render()` — —
- `fuzzy_find()` — —
- `get()` — —
- `put()` — —
- `validate()` — —
- `on_progress()` — —
- `get_cfg()` — —
- `generate_readme()` — —
- `progress_callback()` — —
- `supported_extensions()` — —
- `save_test_report()` — —
- `run_cli()` — —
- `test_imports()` — —
- `test_basic_analysis()` — —
- `test_radon_complexity()` — —
- `test_graph_metrics()` — —
- `test_circular_dependency()` — —
- `project()` — —
- `test_first_run_populates_manifest()` — —
- `test_run_hash_changes_when_file_modified()` — —
- `test_run_hash_changes_when_file_deleted()` — —
- `test_run_hash_stable_when_nothing_changes()` — —
- `test_export_calls_toon_generates_file()` — —
- `test_export_calls_toon_hubs_section()` — —
- `test_export_calls_toon_modules_section()` — —
- `test_export_calls_toon_edges_section()` — —
- `test_export_calls_toon_header_stats()` — —
- `iac_project()` — —
- `test_all_extensions_includes_declarative()` — —
- `test_all_filenames_includes_dockerfile_and_makefile()` — —
- `test_collect_files_discovers_iac()` — —
- `test_modifying_declarative_file_invalidates_cache()` — —
- `test_dockerfile_edit_invalidates_cache()` — —
- `test_dockerfile_variants_matched_by_prefix()` — —
- `test_lockfiles_excluded_by_default()` — —
- `test_astroid_resolution_mock()` — —
- `test_vulture_dead_code()` — —
- `analyzer()` — —
- `test_analyze_file_tags_result_with_path()` — —
- `test_nonexistent_file_returns_empty()` — —
- `test_cached_result_also_tagged()` — —
- `typed_source()` — —
- `untyped_source()` — —
- `ground_truth_project()` — —
- `analysis_result()` — —
- `test_copy_cached_export_refreshes_mtime()` — —
- `test_copy_cached_export_preserves_contents()` — —
- `tmp_project()` — —
- `cache()` — —
- `test_export_project_toon_writes_file()` — —
- `test_export_single_project_all_triggers_project_toon()` — —
- `test_tiktoken_truncation()` — —
- `test_template_rendering_with_metrics()` — —
- `test_tree_sitter_init()` — —
- `test_metrics_calculation()` — —
- `test_mutation_tracking()` — —
- `test_smell_detection()` — —
- `sample_result()` — —
- `NewUserService()` — —
- `AddUser()` — —
- `GetUser()` — —
- `ProcessUsers()` — —
- `NewUserService()` — —
- `AddUser()` — —
- `run_analysis(project_path)` — Run code2llm and return analysis outputs.
- `get_refactoring_advice(outputs, model)` — Send analysis to LLM and get refactoring advice.
- `main()` — —
- `healthHandler()` — —
- `apiHandler()` — —
- `main()` — —
- `process_message(ch, method, properties, body)` — —
- `main()` — —
- `sendResponse()` — —
- `http()` — —
- `os()` — —
- `PORT()` — —
- `SERVICE_NAME()` — —
- `DB_HOST()` — —
- `server()` — —
- `generate(query, intent, dry_run, cache_dir)` — Generate command from natural language query.
- `demo_quick_strategy()` — Demonstrate quick strategy analysis.
- `demo_standard_strategy()` — Demonstrate standard strategy analysis.
- `demo_deep_strategy()` — Demonstrate deep strategy analysis.
- `demo_incremental_analysis()` — Demonstrate incremental analysis.
- `demo_memory_limited()` — Demonstrate memory-limited analysis.
- `demo_custom_progress()` — Demonstrate custom progress tracking.
- `main()` — Run all demos.
- `validate_input(data)` — Validate input data.
- `format_output(data)` — Format output data.
- `calculate_metrics(data)` — Calculate metrics from data list.
- `filter_data(data, criteria)` — Filter data based on criteria.
- `transform_data(data, transformations)` — Transform data fields.
- `main()` — Main entry point.
- `parse_evolution_metrics(toon_content)` — Extract metrics from evolution.toon content.
- `load_previous(history_file)` — Load previous metrics from history file if present.
- `save_current(history_file, metrics)` — Save current metrics for next comparison.
- `run_benchmark(project_path)` — Run evolution analysis and print before/after table.
- `print_results(scores)` — Wydrukuj sformatowane wyniki benchmarku.
- `build_report(scores)` — Zbuduj raport JSON do zapisu.
- `save_report(report, filename)` — Zapisz raport benchmarku do folderu reports.
- `evaluate_format(name, content, path)` — Oceń pojedynczy format względem ground truth.
- `run_benchmark()` — Run the full format quality benchmark.
- `save_report(results, filename)` — Save benchmark report to reports folder.
- `create_test_project(size)` — Create test project of specified size.
- `benchmark_original_analyzer(project_path, runs)` — Benchmark original ProjectAnalyzer.
- `benchmark_streaming_analyzer(project_path, runs)` — Benchmark new StreamingAnalyzer.
- `benchmark_with_strategies(project_path)` — Benchmark all strategies.
- `print_comparison(original, streaming)` — Print comparison table.
- `main()` — Run benchmark suite.
- `create_core_py(project)` — Utwórz core.py z god function, hub type, high fan-out i side-effect.
- `create_etl_py(project)` — Utwórz etl.py z funkcjami pipeline ETL.
- `create_validation_py(project)` — Utwórz validation.py z pipeline'em walidacji.
- `create_utils_py(project)` — Utwórz utils.py z duplikatem klasy Validator.
- `add_validator_to_core(project)` — Dodaj klasę Validator do core.py (tworzy duplikat).
- `create_ground_truth_project(base_dir)` — Utwórz projekt testowy ze znanymi, mierzalnymi problemami.
- `clear_caches(project_path)` — Clear all caches for clean benchmark.
- `run_analysis(project_path, config)` — Run analysis and return (time_seconds, file_count).
- `benchmark_cold_vs_warm(project_path, runs)` — Compare cold (no cache) vs warm (cached) runs.
- `print_summary(results)` — Print benchmark summary with speedup calculations.
- `main()` — —
- `get_shield_url(label, message, color)` — Generate a shields.io badge URL.
- `parse_evolution_metrics(toon_content)` — Extract metrics from evolution.toon content.
- `parse_format_quality_report(report_path)` — Parse format quality JSON report.
- `parse_performance_report(report_path)` — Parse performance JSON report.
- `generate_badges(metrics)` — Generate badge data from metrics.
- `generate_format_quality_badges(format_scores)` — Generate badges from format quality scores.
- `generate_performance_badges(performance_data)` — Generate badges from performance data.
- `create_html(badges, title)` — Create HTML page with badge table.
- `main()` — Main function to generate badges.
- `get_current_version()` — Get current version from pyproject.toml
- `parse_version(version_str)` — Parse version string into tuple of (major, minor, patch)
- `format_version(major, minor, patch)` — Format version tuple as string
- `bump_version(version_type)` — Bump version based on type (major, minor, patch)
- `update_pyproject_toml(new_version)` — Update version in pyproject.toml
- `update_version_file(new_version)` — Update VERSION file
- `main()` — —
- `index()` — Serve the main badges page.
- `generate_badges()` — Generate badges by running the benchmark script.
- `get_badges()` — Get the generated badges HTML.
- `analyze()` — —
- `supported_extensions()` — —
- `main()` — —
- `main()` — Main CLI entry point.
- `analyze(project_path, config)` — Analyze a Python project and return structured results.
- `analyze_file(file_path, config)` — Analyze a single Python file.
- `get_version()` — Read version from VERSION file.
- `create_parser()` — Create CLI argument parser.
- `handle_special_commands()` — Handle special sub-commands (llm-flow, llm-context, report, cache).
- `handle_cache_command(args_list)` — Manage persistent cache (~/.code2llm/).
- `handle_report_command(args_list)` — Generate views from an existing project.yaml (legacy).
- `validate_and_setup(args)` — Validate source path and setup output directory.
- `print_start_info(args, source_path, output_dir)` — Print analysis start information if verbose.
- `validate_chunked_output(output_dir, args)` — Validate generated chunked output.
- `generate_llm_context(args_list)` — Quick command to generate LLM context only.
- `get_ast(filepath, registry)` — Return parsed AST for *filepath* using the shared registry.
- `find_function_node(tree, name, line)` — Locate a function/async-function node by name and line number.
- `ast_unparse(node, default_none)` — Convert an AST node to its source string via ast.unparse (Python 3.9+).
- `qualified_name(module_name, class_stack, name)` — Build a fully-qualified dotted name from module, optional class scope, and name.
- `expr_to_str(node)` — Convert an AST expression to a dotted string (for call-name extraction).
- `make_cache_key(file_path, content)` — Generate a cache key from file stem and MD5 of content.
- `should_use_chunking(project_path, size_threshold_kb)` — Check if repository should use chunked analysis.
- `get_analysis_plan(project_path, size_limit_kb)` — Get analysis plan for project (auto-detect if chunking needed).
- `should_skip_file(file_str, project_path, gitignore_parser)` — Check if file should be skipped.
- `collect_files_in_dir(dir_path, project_path)` — Collect Python files recursively in a directory.
- `collect_root_files(project_path)` — Collect Python files at root level.
- `count_py_files(path)` — Count Python files (excluding tests/cache and gitignore patterns).
- `contains_python_files(dir_path)` — Check if directory contains any Python files.
- `get_level1_dirs(project_path)` — Get all level 1 directories (excluding hidden/cache).
- `calculate_priority(name, level)` — Calculate priority based on name and nesting level.
- `load_gitignore_patterns(project_path)` — Load gitignore patterns from project directory.
- `get_file_size_kb(filepath)` — Get file size in KB.
- `should_split_toon(filepath, max_kb)` — Check if TOON file exceeds size limit.
- `split_toon_file(source_file, output_dir, max_kb, prefix)` — Split large TOON file into chunks under size limit.
- `manage_toon_size(source_file, output_dir, max_kb, prefix)` — Main entry point: check and split TOON file if needed.
- `get_all_projects(cache_root)` — Return summary dicts for every cached project.
- `clear_all(cache_root)` — Delete entire ~/.code2llm/ cache.
- `analyze_rust(content, file_path, module_name, ext)` — Analyze Rust files using regex-based parsing.
- `analyze_ruby(content, file_path, module_name, ext)` — Analyze Ruby files using shared extraction.
- `extract_function_body(content, start_line)` — Extract the body of a function between braces from a start line (1-indexed).
- `calculate_complexity_regex(content, result, lang)` — Estimate cyclomatic complexity for every function using regex keyword counting.
- `extract_calls_regex(content, module_name, result)` — Extract function calls from function bodies using regex.
- `analyze_c_family(content, file_path, module_name, stats)` — Shared analyzer for C-family languages (Java, C#, C++, etc.).
- `analyze_cpp(content, file_path, module_name, ext)` — Analyze C++ files using shared C-family extraction.
- `register_language()` — Decorator to register a language parser.
- `get_parser(extension)` — Get parser for a file extension.
- `list_parsers()` — List all registered parsers.
- `extract_declarations_ts(tree, source_bytes, ext, file_path)` — Extract all declarations from a tree-sitter tree.
- `get_parser()` — Get global TreeSitterParser instance.
- `parse_source(content, ext)` — Convenience function: parse string content for given extension.
- `is_available()` — Check if tree-sitter is available.
- `analyze_php(content, file_path, module_name, ext)` — —
- `analyze_csharp(content, file_path, module_name, ext)` — Analyze C# files using shared C-family extraction.
- `analyze_go(content, file_path, module_name, ext)` — Analyze Go files. Uses tree-sitter when available, regex fallback.
- `analyze_java(content, file_path, module_name, ext)` — Analyze Java files using shared C-family extraction.
- `analyze_generic(content, file_path, module_name, ext)` — Basic structural analysis for unsupported languages.
- `get_typescript_patterns()` — Returns regex patterns for TypeScript/JavaScript parsing.
- `get_typescript_lang_config()` — Returns language configuration for TypeScript/JavaScript.
- `analyze_typescript_js(content, file_path, module_name, ext)` — Analyze TypeScript/JavaScript files using shared extraction.
- `export_format(name, description, extension, supports_project_yaml)` — Decorator to register an exporter with the EXPORT_REGISTRY.
- `get_exporter(name)` — Get exporter class by format name.
- `list_exporters()` — List all registered exporters with metadata.
- `load_project_yaml(path)` — Load and validate project.yaml with detailed error reporting.
- `validate_project_yaml(output_dir, verbose)` — Validate project.yaml against generated views in output_dir.
- `is_excluded_path(path)` — Return True if *path* matches any standard exclusion pattern (venv, cache, etc.).
- `generate_readme_content(project_path, output_dir, total_functions, total_classes)` — Generate the complete README.md content.
- `get_existing_files(output_dir)` — Check which files exist in the output directory.
- `extract_insights(output_dir)` — Extract insights from existing analysis files.
- `build_core_files_section(existing, insights)` — Build the Core Analysis Files section dynamically.
- `build_llm_files_section(existing)` — Build the LLM-Ready Documentation section dynamically.
- `build_viz_files_section(existing)` — Build the Visualizations section dynamically.
- `build_evolution(health, total_lines, prev_evolution)` — Build append-only evolution history.
- `load_previous_evolution(output_path)` — Load previous evolution entries from existing project.yaml.
- `build_health(result, modules)` — Build health section with CC metrics, alerts, and issues.
- `build_alerts(result)` — Build list of health alerts for high CC and high fan-out.
- `count_duplicates(result)` — Count duplicate class names in different files.
- `build_modules(result, line_counts)` — Build module list with per-file metrics.
- `group_by_file(result)` — Group functions and classes by file path.
- `compute_module_entry(fpath, result, line_counts, file_funcs)` — Build a single module dict for the given file.
- `compute_inbound_deps(funcs, fpath, result)` — Count unique files that call into this module.
- `build_exports(funcs, classes, result)` — Build export list (classes + standalone functions) for a module.
- `build_class_export(ci, result)` — Build export entry for a single class.
- `build_function_exports(funcs, classes)` — Build export entries for standalone (non-method) functions.
- `build_hotspots(result)` — Build hotspots list (high fan-out functions).
- `hotspot_note(fi, fan_out)` — Generate descriptive note for a hotspot.
- `build_refactoring(result, modules, hotspots)` — Build prioritized refactoring actions.
- `render_header(ctx)` — Render header line.
- `render_next(ctx)` — Render NEXT — ranked refactoring queue.
- `render_risks(ctx)` — Render RISKS — potential breaking changes.
- `render_metrics_target(ctx)` — Render METRICS-TARGET — baseline vs goals.
- `render_patterns(ctx)` — Render PATTERNS — shared language parser extraction patterns.
- `render_history(ctx, output_path)` — Render HISTORY — load previous evolution.toon.yaml if exists.
- `export_to_yaml(result, output_path)` — Generate evolution.toon.yaml (structured YAML).
- `is_excluded(path)` — Check if path should be excluded (venv, site-packages, etc.).
- `compute_func_data(result)` — Compute per-function metrics, excluding venv.
- `scan_file_sizes(project_path, result)` — Return per-file line counts, preferring already-analyzed module data.
- `aggregate_file_stats(result, file_lines)` — Aggregate function and class data per file.
- `make_relative_path(fpath, project_path)` — Convert absolute path to relative path.
- `filter_god_modules(file_stats, project_path)` — Filter files to god modules (≥500 lines).
- `compute_god_modules(result)` — Identify god modules (≥500 lines) from project files.
- `compute_hub_types(result)` — Identify hub types consumed by many functions.
- `build_context(result)` — Build context dict with all computed metrics.
- `build_alerts(funcs)` — Build a compact list of top alerts for the header.
- `build_hotspots(funcs)` — Build a compact list of top fan-out hotspots for the header.
- `load_evolution_trend(evolution_path, current_cc)` — Summarize the latest CC trend from the previous evolution.toon.yaml file.
- `render_module_list(result, is_excluded_path)` — Render M[] — module list with line counts.
- `render_details(result, is_excluded_path)` — Render D: — details per module.
- `render_header(result, output_path, is_excluded_path)` — Render header lines with project stats and alerts.
- `export_to_yaml(result, output_path, is_excluded_path)` — Export analysis result to map.toon.yaml format (structured YAML).
- `rel_path(fpath, project_path)` — Get relative path from project root.
- `file_line_count(fpath)` — Count lines in a file.
- `count_total_lines(result, is_excluded_path)` — Count total lines across all modules.
- `detect_languages(result, is_excluded_path)` — Detect all supported programming languages in the project.
- `generate_index_html(output_dir)` — Generate index.html in the specified directory.
- `get_file_types()` — Get file type configuration mapping.
- `get_default_file_info(ext)` — Get default file info for unknown extension.
- `export_compact(result, output_path)` — Export module-level graph: one node per module, weighted edges.
- `export_classic(result, output_path)` — Export full flow diagram with CC-based node shapes and styling.
- `export_flow_detailed(result, output_path, include_examples)` — Export detailed per-module view (~150 nodes).
- `export_calls(result, output_path)` — Export simplified call graph — only connected nodes.
- `should_skip_module(module, include_examples)` — Check if module should be skipped (examples, benchmarks, etc.).
- `is_entry_point(func_name, fi, result)` — Detect if function is an entry point (main, cli, api entry).
- `build_callers_graph(result, name_index)` — Build reverse graph: map each function to its callers.
- `find_leaves(result, name_index)` — Find leaf nodes (functions that don't call other project functions).
- `find_critical_path(result, entry_points)` — Find the longest path from entry points (critical path).
- `export_flow_compact(result, output_path, include_examples)` — Export compact architectural view (~50 nodes).
- `readable_id(name)` — Create human-readable Mermaid-safe unique node ID.
- `safe_module(name)` — Create safe subgraph name.
- `module_of(func_name)` — Extract module from qualified name.
- `build_name_index(funcs)` — Build index mapping simple names to qualified names for O(1) lookup.
- `resolve_callee(callee, funcs, name_index)` — Resolve callee to a known qualified name.
- `write_file(path, lines)` — Write lines to file.
- `get_cc(fi)` — Extract cyclomatic complexity from FunctionInfo.
- `export_flow_full(result, output_path, include_examples)` — Export full debug view with all nodes (original flow.mmd).
- `dump_yaml(data)` — Shared YAML serialiser (sort_keys=False, unicode, width=100).
- `normalize_llm_task(data)` — —
- `parse_llm_task_text(text)` — Parse LLM task text into structured data.
- `load_input(path)` — Load input file with detailed YAML/JSON error reporting.
- `create_parser()` — —
- `main(argv)` — —
- `run_cli()` — Run the CLI interface for generating PNGs from Mermaid files.
- `create_parser()` — —
- `main(argv)` — —
- `generate_llm_flow(analysis, max_functions, limit_decisions, limit_calls)` — —
- `render_llm_flow_md(flow)` — —
- `validate_mermaid_file(mmd_path)` — Validate Mermaid file and return list of errors.
- `generate_pngs(input_dir, output_dir, timeout, max_workers)` — Generate PNG files from all .mmd files in input_dir (parallel).
- `generate_single_png(mmd_file, output_file, timeout)` — Generate PNG from single Mermaid file using available renderers.
- `generate_with_puppeteer(mmd_file, output_file, timeout, max_text_size)` — Generate PNG using Puppeteer with HTML template.
- `fix_mermaid_file(mmd_path)` — Attempt to fix common Mermaid syntax errors.
- `parse_toon_content(content)` — Parse TOON v2 plain-text format.
- `is_toon_file(filepath)` — Check if file is TOON format based on extension or content.
- `load_toon(filepath)` — Parse TOON plain-text format into structured data.
- `main()` — —
- `detect_factory()` — —
- `detect_singleton()` — —
- `detect_observer()` — —
- `parse_file()` — —
- `extract_functions()` — —
- `print()` — —
- `analyze_project()` — —
- `get_function_count()` — —
- `get_class_count()` — —
- `to_dict()` — —
- `process()` — —
- `normalize()` — —
- `step_1a_lowercase()` — —
- `step_1b_remove_punctuation()` — —
- `step_1c_normalize_whitespace()` — —
- `step_1d_unicode_normalize()` — —
- `step_1e_remove_stopwords()` — —
- `match()` — —
- `step_2a_fuzzy_match()` — —
- `step_2c_keyword_match()` — —
- `step_2d_context_score()` — —
- `resolve()` — —
- `load_from_analysis()` — —
- `generate_readme()` — —
- `on_progress()` — —
- `print()` — —
- `get_cfg()` — —
- `repair_command()` — —
- `print()` — —
- `print()` — —
- `get_file_hash()` — —
- `parse_file_cached()` — —
- `generate_command()` — —
- `render_template()` — —
- `optimize_output()` — —
- `cache_result()` — —
- `load_patterns()` — —
- `fuzzy_match()` — —
- `validate_schema()` — —
- `generate()` — —
- `render()` — —
- `match()` — —
- `fuzzy_find()` — —
- `get()` — —
- `put()` — —
- `validate()` — —
- `print()` — —
- `progress_callback()` — —
- `print()` — —
- `handle_special_commands()` — —
- `handle_cache_command()` — —
- `handle_report_command()` — —
- `validate_and_setup()` — —
- `print_start_info()` — —
- `validate_chunked_output()` — —
- `generate_llm_context()` — —
- `analyze()` — —
- `analyze_file()` — —
- `get_version()` — —
- `create_parser()` — —
- `main()` — —
- `print()` — —
- `index()` — —
- `generate_badges()` — —
- `get_badges()` — —
- `parse_evolution_metrics()` — —
- `load_previous()` — —
- `save_current()` — —
- `run_benchmark()` — —
- `clear_caches()` — —
- `run_analysis()` — —
- `benchmark_cold_vs_warm()` — —
- `print_summary()` — —
- `main()` — —
- `save_report()` — —
- `create_test_project()` — —
- `benchmark_original_analyzer()` — —
- `benchmark_streaming_analyzer()` — —
- `benchmark_with_strategies()` — —
- `print_comparison()` — —
- `evaluate_format()` — —
- `create_core_py()` — —
- `create_etl_py()` — —
- `create_validation_py()` — —
- `create_utils_py()` — —
- `add_validator_to_core()` — —
- `create_ground_truth_project()` — —
- `print_results()` — —
- `build_report()` — —
- `save_test_report()` — —
- `get_ast()` — —
- `find_function_node()` — —
- `ast_unparse()` — —
- `qualified_name()` — —
- `expr_to_str()` — —
- `analyze()` — —
- `analyze_file()` — —
- `handle_special_commands()` — —
- `handle_cache_command()` — —
- `handle_report_command()` — —
- `validate_and_setup()` — —
- `print_start_info()` — —
- `validate_chunked_output()` — —
- `generate_llm_context()` — —
- `get_version()` — —
- `create_parser()` — —
- `make_cache_key()` — —
- `load_gitignore_patterns()` — —
- `register_language()` — —
- `get_parser()` — —
- `list_parsers()` — —
- `extract_function_body()` — —
- `calculate_complexity_regex()` — —
- `extract_calls_regex()` — —
- `analyze_c_family()` — —
- `analyze_cpp()` — —
- `analyze_csharp()` — —
- `analyze_generic()` — —
- `analyze_go()` — —
- `analyze_java()` — —
- `analyze_php()` — —
- `analyze_ruby()` — —
- `analyze_rust()` — —
- `extract_declarations_ts()` — —
- `parse_source()` — —
- `is_available()` — —
- `get_typescript_patterns()` — —
- `get_typescript_lang_config()` — —
- `analyze_typescript_js()` — —
- `should_use_chunking()` — —
- `get_analysis_plan()` — —
- `get_all_projects()` — —
- `clear_all()` — —
- `should_skip_file()` — —
- `collect_files_in_dir()` — —
- `collect_root_files()` — —
- `count_py_files()` — —
- `contains_python_files()` — —
- `get_level1_dirs()` — —
- `calculate_priority()` — —
- `get_file_size_kb()` — —
- `should_split_toon()` — —
- `split_toon_file()` — —
- `manage_toon_size()` — —
- `export_format()` — —
- `get_exporter()` — —
- `list_exporters()` — —
- `compute_func_data()` — —
- `scan_file_sizes()` — —
- `aggregate_file_stats()` — —
- `make_relative_path()` — —
- `filter_god_modules()` — —
- `compute_god_modules()` — —
- `compute_hub_types()` — —
- `build_context()` — —
- `is_excluded()` — —
- `render_header()` — —
- `render_next()` — —
- `render_risks()` — —
- `render_metrics_target()` — —
- `render_patterns()` — —
- `render_history()` — —
- `export_to_yaml()` — —
- `is_excluded_path()` — —
- `generate_index_html()` — —
- `get_file_types()` — —
- `get_default_file_info()` — —
- `build_alerts()` — —
- `build_hotspots()` — —
- `load_evolution_trend()` — —
- `render_details()` — —
- `render_module_list()` — —
- `rel_path()` — —
- `file_line_count()` — —
- `count_total_lines()` — —
- `detect_languages()` — —
- `export_calls()` — —
- `export_classic()` — —
- `export_compact()` — —
- `should_skip_module()` — —
- `is_entry_point()` — —
- `build_callers_graph()` — —
- `find_leaves()` — —
- `find_critical_path()` — —
- `export_flow_compact()` — —
- `export_flow_detailed()` — —
- `export_flow_full()` — —
- `readable_id()` — —
- `safe_module()` — —
- `module_of()` — —
- `build_name_index()` — —
- `resolve_callee()` — —
- `write_file()` — —
- `get_cc()` — —
- `build_evolution()` — —
- `load_previous_evolution()` — —
- `build_health()` — —
- `count_duplicates()` — —
- `hotspot_note()` — —
- `build_refactoring()` — —
- `build_modules()` — —
- `group_by_file()` — —
- `compute_module_entry()` — —
- `compute_inbound_deps()` — —
- `build_exports()` — —
- `build_class_export()` — —
- `build_function_exports()` — —
- `generate_readme_content()` — —
- `get_existing_files()` — —
- `extract_insights()` — —
- `build_core_files_section()` — —
- `build_llm_files_section()` — —
- `build_viz_files_section()` — —
- `load_project_yaml()` — —
- `validate_project_yaml()` — —
- `dump_yaml()` — —
- `generate_llm_flow()` — —
- `render_llm_flow_md()` — —
- `normalize_llm_task()` — —
- `parse_llm_task_text()` — —
- `load_input()` — —
- `fix_mermaid_file()` — —
- `generate_pngs()` — —
- `generate_single_png()` — —
- `generate_with_puppeteer()` — —
- `validate_mermaid_file()` — —
- `run_cli()` — —
- `parse_toon_content()` — —
- `is_toon_file()` — —
- `load_toon()` — —
- `process_message()` — —
- `generate()` — —
- `get_refactoring_advice()` — —
- `demo_quick_strategy()` — —
- `demo_standard_strategy()` — —
- `demo_deep_strategy()` — —
- `demo_incremental_analysis()` — —
- `demo_memory_limited()` — —
- `demo_custom_progress()` — —
- `validate_input()` — —
- `format_output()` — —
- `calculate_metrics()` — —
- `filter_data()` — —
- `transform_data()` — —
- `test_imports()` — —
- `test_basic_analysis()` — —
- `run_pipeline()` — —
- `get_shield_url()` — —
- `parse_format_quality_report()` — —
- `parse_performance_report()` — —
- `generate_format_quality_badges()` — —
- `generate_performance_badges()` — —
- `create_html()` — —
- `get_current_version()` — —
- `parse_version()` — —
- `format_version()` — —
- `bump_version()` — —
- `update_pyproject_toml()` — —
- `update_version_file()` — —
- `read_version()` — —
- `read_readme()` — —
- `test_radon_complexity()` — —
- `test_graph_metrics()` — —
- `test_circular_dependency()` — —
- `project()` — —
- `test_first_run_populates_manifest()` — —
- `test_run_hash_changes_when_file_modified()` — —
- `test_run_hash_changes_when_file_deleted()` — —
- `test_run_hash_stable_when_nothing_changes()` — —
- `test_export_calls_toon_generates_file()` — —
- `test_export_calls_toon_hubs_section()` — —
- `test_export_calls_toon_modules_section()` — —
- `test_export_calls_toon_edges_section()` — —
- `test_export_calls_toon_header_stats()` — —
- `iac_project()` — —
- `test_all_extensions_includes_declarative()` — —
- `test_all_filenames_includes_dockerfile_and_makefile()` — —
- `test_collect_files_discovers_iac()` — —
- `test_modifying_declarative_file_invalidates_cache()` — —
- `test_dockerfile_edit_invalidates_cache()` — —
- `test_dockerfile_variants_matched_by_prefix()` — —
- `test_lockfiles_excluded_by_default()` — —
- `test_astroid_resolution_mock()` — —
- `test_vulture_dead_code()` — —
- `analyzer()` — —
- `test_analyze_file_tags_result_with_path()` — —
- `test_nonexistent_file_returns_empty()` — —
- `test_cached_result_also_tagged()` — —
- `typed_source()` — —
- `untyped_source()` — —
- `ground_truth_project()` — —
- `analysis_result()` — —
- `test_copy_cached_export_refreshes_mtime()` — —
- `test_copy_cached_export_preserves_contents()` — —
- `tmp_project()` — —
- `cache()` — —
- `test_export_project_toon_writes_file()` — —
- `test_export_single_project_all_triggers_project_toon()` — —
- `test_tiktoken_truncation()` — —
- `test_template_rendering_with_metrics()` — —
- `test_tree_sitter_init()` — —
- `test_metrics_calculation()` — —
- `test_mutation_tracking()` — —
- `test_smell_detection()` — —
- `sample_result()` — —
- `load_yaml()` — —
- `load_file()` — —
- `extract_functions_from_yaml()` — —
- `extract_functions_from_toon()` — —
- `extract_classes_from_yaml()` — —
- `extract_classes_from_toon()` — —
- `analyze_class_differences()` — —
- `extract_modules_from_yaml()` — —
- `extract_modules_from_toon()` — —
- `compare_basic_stats()` — —
- `compare_functions()` — —
- `compare_classes()` — —
- `compare_modules()` — —
- `validate_toon_completeness()` — —
- `compute_func_data()` — —
- `scan_file_sizes()` — —
- `aggregate_file_stats()` — —
- `make_relative_path()` — —
- `filter_god_modules()` — —
- `compute_god_modules()` — —
- `compute_hub_types()` — —
- `build_context()` — —
- `analyze_ruby()` — —
- `extract_function_body()` — —
- `calculate_complexity_regex()` — —
- `extract_calls_regex()` — —
- `analyze_c_family()` — —
- `normalize_llm_task()` — —
- `parse_llm_task_text()` — —
- `load_input()` — —
- `create_parser()` — —
- `main()` — —
- `parse_evolution_metrics()` — —
- `load_previous()` — —
- `save_current()` — —
- `run_benchmark()` — —
- `get_shield_url()` — —
- `parse_format_quality_report()` — —
- `parse_performance_report()` — —
- `generate_badges()` — —
- `generate_format_quality_badges()` — —
- `generate_performance_badges()` — —
- `create_html()` — —
- `load_project_yaml()` — —
- `extract_insights()` — —
- `build_health()` — —
- `build_alerts()` — —
- `count_duplicates()` — —
- `build_hotspots()` — —
- `hotspot_note()` — —
- `build_refactoring()` — —
- `render_details()` — —
- `export_compact()` — —
- `export_calls()` — —
- `handle_special_commands()` — —
- `handle_cache_command()` — —
- `handle_report_command()` — —
- `validate_and_setup()` — —
- `print_start_info()` — —
- `validate_chunked_output()` — —
- `generate_llm_context()` — —
- `analyze_generic()` — —
- `validate_mermaid_file()` — —
- `validate_project_yaml()` — —
- `build_modules()` — —
- `group_by_file()` — —
- `compute_module_entry()` — —
- `compute_inbound_deps()` — —
- `build_exports()` — —
- `build_class_export()` — —
- `build_function_exports()` — —
- `export_to_yaml()` — —
- `get_file_size_kb()` — —
- `should_split_toon()` — —
- `split_toon_file()` — —
- `manage_toon_size()` — —
- `get_all_projects()` — —
- `clear_all()` — —
- `analyze_go()` — —
- `render_header()` — —
- `render_next()` — —
- `render_risks()` — —
- `render_metrics_target()` — —
- `render_patterns()` — —
- `render_history()` — —
- `generate_llm_flow()` — —
- `render_llm_flow_md()` — —
- `run_pipeline()` — —
- `should_use_chunking()` — —
- `get_analysis_plan()` — —
- `analyze_rust()` — —
- `should_skip_module()` — —
- `is_entry_point()` — —
- `build_callers_graph()` — —
- `find_leaves()` — —
- `find_critical_path()` — —
- `export_flow_compact()` — —
- `get_ast()` — —
- `find_function_node()` — —
- `ast_unparse()` — —
- `qualified_name()` — —
- `expr_to_str()` — —
- `should_skip_file()` — —
- `collect_files_in_dir()` — —
- `collect_root_files()` — —
- `count_py_files()` — —
- `contains_python_files()` — —
- `get_level1_dirs()` — —
- `calculate_priority()` — —
- `analyze_php()` — —
- `load_evolution_trend()` — —
- `rel_path()` — —
- `file_line_count()` — —
- `count_total_lines()` — —
- `detect_languages()` — —
- `export_classic()` — —
- `generate_pngs()` — —
- `generate_single_png()` — —
- `generate_with_puppeteer()` — —
- `fix_mermaid_file()` — —
- `parse_toon_content()` — —
- `is_toon_file()` — —
- `load_toon()` — —
- `load_yaml()` — —
- `load_file()` — —
- `extract_functions_from_yaml()` — —
- `extract_functions_from_toon()` — —
- `extract_classes_from_yaml()` — —
- `extract_classes_from_toon()` — —
- `analyze_class_differences()` — —
- `extract_modules_from_yaml()` — —
- `extract_modules_from_toon()` — —
- `compare_basic_stats()` — —
- `compare_functions()` — —
- `compare_classes()` — —
- `compare_modules()` — —
- `validate_toon_completeness()` — —
- `validate_input()` — —
- `format_output()` — —
- `calculate_metrics()` — —
- `filter_data()` — —
- `transform_data()` — —
- `clear_caches()` — —
- `run_analysis()` — —
- `benchmark_cold_vs_warm()` — —
- `print_summary()` — —
- `load_gitignore_patterns()` — —
- `extract_declarations_ts()` — —
- `get_parser()` — —
- `parse_source()` — —
- `is_available()` — —
- `build_core_files_section()` — —
- `build_llm_files_section()` — —
- `build_viz_files_section()` — —
- `generate()` — —
- `print_results()` — —
- `build_report()` — —
- `save_report()` — —
- `create_test_project()` — —
- `benchmark_original_analyzer()` — —
- `benchmark_streaming_analyzer()` — —
- `benchmark_with_strategies()` — —
- `print_comparison()` — —
- `build_evolution()` — —
- `load_previous_evolution()` — —
- `readable_id()` — —
- `safe_module()` — —
- `module_of()` — —
- `build_name_index()` — —
- `resolve_callee()` — —
- `write_file()` — —
- `get_cc()` — —
- `demo_quick_strategy()` — —
- `demo_standard_strategy()` — —
- `demo_deep_strategy()` — —
- `demo_incremental_analysis()` — —
- `demo_memory_limited()` — —
- `demo_custom_progress()` — —
- `evaluate_format()` — —
- `make_cache_key()` — —
- `get_file_types()` — —
- `get_default_file_info()` — —
- `get_refactoring_advice()` — —
- `get_current_version()` — —
- `parse_version()` — —
- `format_version()` — —
- `bump_version()` — —
- `update_pyproject_toml()` — —
- `update_version_file()` — —
- `index()` — —
- `get_badges()` — —
- `render_module_list()` — —
- `http()` — —
- `os()` — —
- `PORT()` — —
- `SERVICE_NAME()` — —
- `DB_HOST()` — —
- `server()` — —
- `read_version()` — —
- `read_readme()` — —
- `healthHandler()` — —
- `apiHandler()` — —
- `analyze()` — —
- `analyze_file()` — —
- `get_version()` — —
- `export_format()` — —
- `get_exporter()` — —
- `list_exporters()` — —
- `is_excluded_path()` — —
- `get_existing_files()` — —
- `is_excluded()` — —
- `process_message()` — —
- `sendResponse()` — —
- `create_core_py()` — —
- `create_etl_py()` — —
- `create_validation_py()` — —
- `create_utils_py()` — —
- `add_validator_to_core()` — —
- `create_ground_truth_project()` — —
- `analyze_cpp()` — —
- `register_language()` — —
- `list_parsers()` — —
- `analyze_csharp()` — —
- `analyze_java()` — —
- `get_typescript_patterns()` — —
- `get_typescript_lang_config()` — —
- `analyze_typescript_js()` — —
- `generate_index_html()` — —
- `generate_readme_content()` — —
- `export_flow_detailed()` — —
- `export_flow_full()` — —
- `dump_yaml()` — —
- `print()` — —
- `detect_factory()` — —
- `detect_singleton()` — —
- `detect_observer()` — —
- `parse_file()` — —
- `extract_functions()` — —
- `analyze_project()` — —
- `get_function_count()` — —
- `get_class_count()` — —
- `to_dict()` — —
- `process()` — —
- `normalize()` — —
- `step_1a_lowercase()` — —
- `step_1b_remove_punctuation()` — —
- `step_1c_normalize_whitespace()` — —
- `step_1d_unicode_normalize()` — —
- `step_1e_remove_stopwords()` — —
- `match()` — —
- `step_2a_fuzzy_match()` — —
- `step_2c_keyword_match()` — —
- `step_2d_context_score()` — —
- `resolve()` — —
- `load_from_analysis()` — —
- `repair_command()` — —
- `get_file_hash()` — —
- `parse_file_cached()` — —
- `generate_command()` — —
- `render_template()` — —
- `optimize_output()` — —
- `cache_result()` — —
- `load_patterns()` — —
- `fuzzy_match()` — —
- `validate_schema()` — —
- `render()` — —
- `fuzzy_find()` — —
- `get()` — —
- `put()` — —
- `validate()` — —
- `on_progress()` — —
- `get_cfg()` — —
- `generate_readme()` — —
- `progress_callback()` — —
- `supported_extensions()` — —
- `save_test_report()` — —
- `run_cli()` — —
- `test_imports()` — —
- `test_basic_analysis()` — —
- `test_radon_complexity()` — —
- `test_graph_metrics()` — —
- `test_circular_dependency()` — —
- `project()` — —
- `test_first_run_populates_manifest()` — —
- `test_run_hash_changes_when_file_modified()` — —
- `test_run_hash_changes_when_file_deleted()` — —
- `test_run_hash_stable_when_nothing_changes()` — —
- `test_export_calls_toon_generates_file()` — —
- `test_export_calls_toon_hubs_section()` — —
- `test_export_calls_toon_modules_section()` — —
- `test_export_calls_toon_edges_section()` — —
- `test_export_calls_toon_header_stats()` — —
- `iac_project()` — —
- `test_all_extensions_includes_declarative()` — —
- `test_all_filenames_includes_dockerfile_and_makefile()` — —
- `test_collect_files_discovers_iac()` — —
- `test_modifying_declarative_file_invalidates_cache()` — —
- `test_dockerfile_edit_invalidates_cache()` — —
- `test_dockerfile_variants_matched_by_prefix()` — —
- `test_lockfiles_excluded_by_default()` — —
- `test_astroid_resolution_mock()` — —
- `test_vulture_dead_code()` — —
- `analyzer()` — —
- `test_analyze_file_tags_result_with_path()` — —
- `test_nonexistent_file_returns_empty()` — —
- `test_cached_result_also_tagged()` — —
- `typed_source()` — —
- `untyped_source()` — —
- `ground_truth_project()` — —
- `analysis_result()` — —
- `test_copy_cached_export_refreshes_mtime()` — —
- `test_copy_cached_export_preserves_contents()` — —
- `tmp_project()` — —
- `cache()` — —
- `test_export_project_toon_writes_file()` — —
- `test_export_single_project_all_triggers_project_toon()` — —
- `test_tiktoken_truncation()` — —
- `test_template_rendering_with_metrics()` — —
- `test_tree_sitter_init()` — —
- `test_metrics_calculation()` — —
- `test_mutation_tracking()` — —
- `test_smell_detection()` — —
- `sample_result()` — —


## Project Structure

📄 `CHANGELOG`
📄 `Makefile`
📄 `README`
📄 `REFACTORING_PLAN`
📄 `ROADMAP` (5 functions, 2 classes)
📄 `SUMD` (556 functions)
📄 `SUMR` (31 functions)
📄 `TODO`
📄 `Taskfile` (2 functions)
📄 `analysis.toon`
📄 `badges.server` (3 functions)
📄 `batch_1.analysis.toon`
📄 `benchmarks.benchmark_constants`
📄 `benchmarks.benchmark_evolution` (4 functions)
📄 `benchmarks.benchmark_format_quality` (5 functions)
📄 `benchmarks.benchmark_optimizations` (5 functions)
📄 `benchmarks.benchmark_performance` (7 functions)
📄 `benchmarks.format_evaluator` (5 functions, 1 classes)
📄 `benchmarks.project_generator` (6 functions)
📄 `benchmarks.reporting` (9 functions)
📄 `calls`
📄 `calls_output.README`
📄 `calls_output.analysis.toon`
📄 `calls_output.calls`
📄 `calls_output.context`
📦 `code2llm` (1 functions)
📄 `code2llm..code2llm_incremental`
📄 `code2llm.__main__`
📦 `code2llm.analysis` (1 functions)
📄 `code2llm.analysis.call_graph` (12 functions, 1 classes)
📄 `code2llm.analysis.cfg` (16 functions, 1 classes)
📄 `code2llm.analysis.coupling` (5 functions, 1 classes)
📄 `code2llm.analysis.data_analysis` (28 functions, 3 classes)
📄 `code2llm.analysis.dfg` (12 functions, 1 classes)
📄 `code2llm.analysis.pipeline_classifier` (5 functions, 1 classes)
📄 `code2llm.analysis.pipeline_detector` (9 functions, 3 classes)
📄 `code2llm.analysis.pipeline_resolver` (5 functions, 1 classes)
📄 `code2llm.analysis.side_effects` (15 functions, 2 classes)
📄 `code2llm.analysis.smells` (9 functions, 1 classes)
📄 `code2llm.analysis.type_inference` (17 functions, 1 classes)
📦 `code2llm.analysis.utils`
📄 `code2llm.analysis.utils.ast_helpers` (5 functions)
📄 `code2llm.api` (2 functions)
📄 `code2llm.cli` (1 functions)
📄 `code2llm.cli_analysis` (11 functions)
📄 `code2llm.cli_commands` (13 functions)
📦 `code2llm.cli_exports`
📄 `code2llm.cli_exports.code2logic` (8 functions)
📄 `code2llm.cli_exports.formats` (16 functions)
📄 `code2llm.cli_exports.orchestrator` (13 functions)
📄 `code2llm.cli_exports.orchestrator_chunked` (3 functions)
📄 `code2llm.cli_exports.orchestrator_constants`
📄 `code2llm.cli_exports.orchestrator_handlers` (8 functions)
📄 `code2llm.cli_exports.prompt` (18 functions)
📄 `code2llm.cli_parser` (2 functions)
📦 `code2llm.core` (1 functions)
📄 `code2llm.core.analyzer` (22 functions, 1 classes)
📄 `code2llm.core.ast_registry` (9 functions, 1 classes)
📄 `code2llm.core.config` (3 functions, 6 classes)
📄 `code2llm.core.export_pipeline` (5 functions, 2 classes)
📄 `code2llm.core.file_analyzer` (18 functions, 1 classes)
📄 `code2llm.core.file_cache` (10 functions, 1 classes)
📄 `code2llm.core.file_filter` (9 functions, 1 classes)
📄 `code2llm.core.gitignore` (7 functions, 2 classes)
📄 `code2llm.core.incremental` (10 functions, 1 classes)
📦 `code2llm.core.lang` (5 functions, 1 classes)
📄 `code2llm.core.lang.base` (14 functions)
📄 `code2llm.core.lang.cpp` (1 functions)
📄 `code2llm.core.lang.csharp` (1 functions)
📄 `code2llm.core.lang.generic` (1 functions)
📄 `code2llm.core.lang.go_lang` (2 functions)
📄 `code2llm.core.lang.java` (1 functions)
📄 `code2llm.core.lang.php` (4 functions)
📄 `code2llm.core.lang.ruby` (4 functions, 1 classes)
📄 `code2llm.core.lang.rust` (1 functions)
📄 `code2llm.core.lang.ts_extractors` (5 functions)
📄 `code2llm.core.lang.ts_parser` (9 functions, 1 classes)
📄 `code2llm.core.lang.typescript` (3 functions)
📄 `code2llm.core.large_repo` (20 functions, 2 classes)
📄 `code2llm.core.models` (6 functions, 11 classes)
📄 `code2llm.core.persistent_cache` (22 functions, 1 classes)
📄 `code2llm.core.refactoring` (11 functions, 1 classes)
📄 `code2llm.core.repo_files` (8 functions)
📦 `code2llm.core.streaming`
📄 `code2llm.core.streaming.cache` (5 functions, 1 classes)
📄 `code2llm.core.streaming.incremental` (5 functions, 1 classes)
📄 `code2llm.core.streaming.prioritizer` (4 functions, 2 classes)
📄 `code2llm.core.streaming.scanner` (6 functions, 1 classes)
📄 `code2llm.core.streaming.strategies` (1 classes)
📄 `code2llm.core.streaming_analyzer` (6 functions, 1 classes)
📄 `code2llm.core.toon_size_manager` (8 functions)
📦 `code2llm.exporters`
📄 `code2llm.exporters.article_view` (8 functions, 1 classes)
📄 `code2llm.exporters.base` (8 functions, 2 classes)
📄 `code2llm.exporters.context_exporter` (15 functions, 1 classes)
📄 `code2llm.exporters.context_view` (7 functions, 1 classes)
📄 `code2llm.exporters.dashboard_data` (9 functions, 1 classes)
📄 `code2llm.exporters.dashboard_renderer` (4 functions, 1 classes)
📦 `code2llm.exporters.evolution`
📄 `code2llm.exporters.evolution.computation` (8 functions)
📄 `code2llm.exporters.evolution.constants`
📄 `code2llm.exporters.evolution.exclusion` (1 functions)
📄 `code2llm.exporters.evolution.render` (6 functions)
📄 `code2llm.exporters.evolution.yaml_export` (1 functions)
📄 `code2llm.exporters.evolution_exporter` (3 functions, 1 classes)
📄 `code2llm.exporters.flow_constants` (1 functions)
📄 `code2llm.exporters.flow_exporter` (14 functions, 1 classes)
📄 `code2llm.exporters.flow_renderer` (6 functions, 1 classes)
📄 `code2llm.exporters.html_dashboard` (3 functions, 1 classes)
📦 `code2llm.exporters.index_generator` (5 functions, 1 classes)
📄 `code2llm.exporters.index_generator.renderer` (1 functions, 1 classes)
📄 `code2llm.exporters.index_generator.scanner` (7 functions, 1 classes)
📄 `code2llm.exporters.json_exporter` (1 functions, 1 classes)
📄 `code2llm.exporters.llm_exporter`
📦 `code2llm.exporters.map`
📄 `code2llm.exporters.map.alerts` (4 functions)
📄 `code2llm.exporters.map.details` (5 functions)
📄 `code2llm.exporters.map.header` (4 functions)
📄 `code2llm.exporters.map.module_list` (1 functions)
📄 `code2llm.exporters.map.utils` (4 functions)
📄 `code2llm.exporters.map.yaml_export` (5 functions)
📄 `code2llm.exporters.map_exporter` (2 functions, 1 classes)
📦 `code2llm.exporters.mermaid`
📄 `code2llm.exporters.mermaid.calls` (1 functions)
📄 `code2llm.exporters.mermaid.classic` (4 functions)
📄 `code2llm.exporters.mermaid.compact` (1 functions)
📄 `code2llm.exporters.mermaid.flow_compact` (9 functions)
📄 `code2llm.exporters.mermaid.flow_detailed` (1 functions)
📄 `code2llm.exporters.mermaid.flow_full` (1 functions)
📄 `code2llm.exporters.mermaid.utils` (8 functions)
📄 `code2llm.exporters.mermaid_exporter` (1 classes)
📄 `code2llm.exporters.mermaid_flow_helpers` (12 functions)
📦 `code2llm.exporters.project_yaml`
📄 `code2llm.exporters.project_yaml.constants`
📄 `code2llm.exporters.project_yaml.core` (3 functions, 1 classes)
📄 `code2llm.exporters.project_yaml.evolution` (2 functions)
📄 `code2llm.exporters.project_yaml.health` (3 functions)
📄 `code2llm.exporters.project_yaml.hotspots` (3 functions)
📄 `code2llm.exporters.project_yaml.modules` (7 functions)
📄 `code2llm.exporters.project_yaml_exporter`
📦 `code2llm.exporters.readme`
📄 `code2llm.exporters.readme.content` (1 functions)
📄 `code2llm.exporters.readme.files` (1 functions)
📄 `code2llm.exporters.readme.insights` (1 functions)
📄 `code2llm.exporters.readme.sections` (3 functions)
📄 `code2llm.exporters.readme_exporter` (1 functions, 1 classes)
📄 `code2llm.exporters.report_generators` (1 functions)
📦 `code2llm.exporters.toon` (11 functions, 1 classes)
📄 `code2llm.exporters.toon.helpers` (8 functions)
📄 `code2llm.exporters.toon.metrics` (4 functions, 1 classes)
📄 `code2llm.exporters.toon.metrics_core` (13 functions, 1 classes)
📄 `code2llm.exporters.toon.metrics_duplicates` (4 functions, 1 classes)
📄 `code2llm.exporters.toon.metrics_health` (6 functions, 1 classes)
📄 `code2llm.exporters.toon.module_detail` (9 functions, 1 classes)
📄 `code2llm.exporters.toon.renderer` (26 functions, 1 classes)
📄 `code2llm.exporters.toon_view` (8 functions, 1 classes)
📄 `code2llm.exporters.validate_project` (3 functions)
📄 `code2llm.exporters.yaml_exporter` (25 functions, 1 classes)
📦 `code2llm.generators`
📄 `code2llm.generators._utils` (1 functions)
📦 `code2llm.generators.llm_flow`
📄 `code2llm.generators.llm_flow.analysis` (5 functions, 1 classes)
📄 `code2llm.generators.llm_flow.cli` (2 functions)
📄 `code2llm.generators.llm_flow.generator` (2 functions)
📄 `code2llm.generators.llm_flow.nodes` (7 functions)
📄 `code2llm.generators.llm_flow.parsing` (2 functions)
📄 `code2llm.generators.llm_flow.utils` (5 functions)
📄 `code2llm.generators.llm_task` (16 functions)
📦 `code2llm.generators.mermaid`
📄 `code2llm.generators.mermaid.fix` (7 functions)
📄 `code2llm.generators.mermaid.png` (8 functions)
📄 `code2llm.generators.mermaid.validation` (6 functions)
📦 `code2llm.nlp`
📄 `code2llm.nlp.config`
📄 `code2llm.nlp.entity_resolution` (16 functions, 3 classes)
📄 `code2llm.nlp.intent_matching` (15 functions, 3 classes)
📄 `code2llm.nlp.normalization` (13 functions, 2 classes)
📄 `code2llm.nlp.pipeline` (20 functions, 3 classes)
📄 `code2llm.parsers.toon_parser` (10 functions)
📄 `code2llm.patterns.detector` (8 functions, 1 classes)
📦 `code2llm.refactor`
📄 `code2llm.refactor.prompt_engine` (7 functions, 1 classes)
📄 `code2llm.templates.extract_method`
📄 `code2llm.templates.move_method`
📄 `code2llm_part2.analysis.toon`
📄 `context`
📄 `demo_langs.valid.sample` (7 functions, 2 classes)
📄 `docs.API` (21 functions, 6 classes)
📄 `docs.COMPARISON_AND_OPTIMIZATION` (20 functions, 5 classes)
📄 `docs.LLM_USAGE`
📄 `docs.METHODOLOGY` (6 functions, 1 classes)
📄 `docs.PROJECT_SUMMARY` (4 functions)
📄 `docs.README` (1 functions)
📄 `evolution.toon`
📄 `examples.analysis.toon`
📄 `examples.basic-usage.README`
📄 `examples.ci-cd.README`
📄 `examples.claude-code.README`
📄 `examples.devops-workflow.README`
📄 `examples.docker-doql-example.ANALYSIS`
📄 `examples.docker-doql-example.DEPENDENCY_ANALYSIS`
📄 `examples.docker-doql-example.SUMMARY`
📄 `examples.docker-doql-example.app.main` (2 functions, 1 classes)
📄 `examples.docker-doql-example.docker-compose`
📄 `examples.docker-doql-example.fluent-bit`
📄 `examples.docker-doql-example.go.main` (3 functions, 1 classes)
📄 `examples.docker-doql-example.java.Main` (9 functions, 1 classes)
📦 `examples.docker-doql-example.node` (6 functions)
📄 `examples.docker-doql-example.php.index` (1 functions)
📄 `examples.docker-doql-example.prometheus`
📄 `examples.docker-doql-example.ruby.app`
📄 `examples.docker-doql-example.run-doql`
📄 `examples.docker-doql-example.rust.Cargo`
📄 `examples.docker-doql-example.rust.src.main` (1 classes)
📄 `examples.docker-doql-example.worker.requirements`
📄 `examples.docker-doql-example.worker.worker` (2 functions)
📦 `examples.functional_refactoring`
📄 `examples.functional_refactoring.cache` (10 functions, 2 classes)
📄 `examples.functional_refactoring.cli` (1 functions)
📄 `examples.functional_refactoring.entity_preparers` (18 functions, 6 classes)
📄 `examples.functional_refactoring.generator` (2 functions, 1 classes)
📄 `examples.functional_refactoring.models` (2 classes)
📄 `examples.functional_refactoring.template_engine` (10 functions, 3 classes)
📄 `examples.functional_refactoring_example` (9 functions, 1 classes)
📄 `examples.litellm.README`
📄 `examples.litellm.run` (3 functions)
📄 `examples.shell-llm.README`
📄 `examples.streaming-analyzer.README` (7 functions)
📄 `examples.streaming-analyzer.demo` (7 functions)
📦 `examples.streaming-analyzer.sample_project`
📄 `examples.streaming-analyzer.sample_project.api` (7 functions, 1 classes)
📄 `examples.streaming-analyzer.sample_project.auth` (10 functions, 1 classes)
📄 `examples.streaming-analyzer.sample_project.database` (13 functions, 1 classes)
📄 `examples.streaming-analyzer.sample_project.main` (9 functions, 2 classes)
📄 `examples.streaming-analyzer.sample_project.utils` (5 functions)
📄 `goal`
📄 `map.toon` (23564 functions)
📄 `orchestrator`
📄 `pipeline` (2 functions)
📄 `planfile`
📄 `prefact`
📄 `project`
📄 `project.README`
📄 `project.analysis.toon`
📄 `project.batch_1.analysis.toon`
📄 `project.batch_1.context`
📄 `project.batch_1.evolution.toon`
📄 `project.calls`
📄 `project.calls.toon`
📄 `project.code2llm_part2.analysis.toon`
📄 `project.context`
📄 `project.duplication.toon`
📄 `project.evolution.toon`
📄 `project.examples.analysis.toon`
📄 `project.map.toon` (72666 functions)
📄 `project.project.toon`
📄 `project.prompt`
📄 `project.refactor-prompt` (2 functions)
📄 `project.root.analysis.toon`
📄 `project.root.context`
📄 `project.test_python_only_examples.analysis.toon`
📄 `project.test_python_only_examples.context`
📄 `project.test_python_only_examples_tests.analysis.toon`
📄 `project.validation.toon`
📄 `project2`
📄 `project_calls_test.README`
📄 `project_calls_test.calls`
📄 `project_calls_test.context`
📄 `prompt_sumd_sumr_feature` (7 functions)
📄 `pyproject`
📄 `pyqual`
📄 `redsl`
📄 `redsl_refactor_plan`
📄 `redsl_refactor_plan.toon`
📄 `redsl_refactor_report`
📄 `redsl_refactor_report.toon`
📄 `requirements`
📄 `root.analysis.toon`
📄 `scripts.benchmark_badges` (9 functions)
📄 `scripts.bump_version` (7 functions)
📄 `setup` (2 functions)
📄 `test_dynamic.README`
📄 `test_dynamic.batch_1.context`
📄 `test_dynamic.context`
📄 `test_dynamic.root.context`
📄 `test_dynamic2.README`
📄 `test_dynamic2.batch_1.context`
📄 `test_dynamic2.context`
📄 `test_dynamic2.prompt`
📄 `test_dynamic2.root.context`
📄 `test_langs.invalid.sample_bad` (3 functions, 2 classes)
📄 `test_langs.valid.sample` (4 functions, 2 classes)
📄 `test_metrics.README`
📄 `test_metrics.batch_1.context`
📄 `test_metrics.context`
📄 `test_metrics.prompt`
📄 `test_metrics.root.context`
📄 `test_prompt.README`
📄 `test_prompt.batch_1.context`
📄 `test_prompt.context`
📄 `test_prompt.prompt`
📄 `test_prompt.root.context`
📦 `test_python_only.valid`
📄 `test_python_only.valid.sample` (5 functions, 2 classes)
📄 `test_python_only_examples_tests.analysis.toon`
📄 `testql-scenarios.generated-api-smoke.testql.toon`
📄 `testql-scenarios.generated-cli-tests.testql.toon`
📄 `testql-scenarios.generated-from-pytests.testql.toon`
📄 `validate_toon` (21 functions)

## Requirements

- Python >= >=3.8
- networkx >=2.6- matplotlib >=3.4- pyyaml >=5.4- numpy >=1.20- jinja2 >=3.0- radon >=5.1- astroid >=3.0- code2logic- vulture >=2.10- tiktoken >=0.5- tree-sitter >=0.21- tree-sitter-python >=0.21- tree-sitter-javascript >=0.21- tree-sitter-typescript >=0.21- tree-sitter-go >=0.21- tree-sitter-rust >=0.21- tree-sitter-java >=0.21- tree-sitter-c >=0.21- tree-sitter-cpp >=0.22- tree-sitter-c-sharp >=0.21- tree-sitter-php >=0.22- tree-sitter-ruby >=0.21

## Contributing

**Contributors:**
- Tom Softreck <tom@sapletta.com>
- Tom Sapletta <tom-sapletta-com@users.noreply.github.com>

We welcome contributions! Open an issue or pull request to get started.
### Development Setup

```bash
# Clone the repository
git clone https://github.com/wronai/code2flow
cd code2llm

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## Documentation

- 💡 [Examples](./examples) — Usage examples and code samples

### Generated Files

| Output | Description | Link |
|--------|-------------|------|
| `README.md` | Project overview (this file) | — |
| `examples` | Usage examples and code samples | [View](./examples) |

<!-- code2docs:end -->