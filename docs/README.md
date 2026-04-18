<!-- code2docs:start --># code2llm

![version](https://img.shields.io/badge/version-0.1.0-blue) ![python](https://img.shields.io/badge/python-%3E%3D3.8-blue) ![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey) ![functions](https://img.shields.io/badge/functions-934-green)
> **934** functions | **106** classes | **123** files | CC̄ = 4.4

> Auto-generated project documentation from source code analysis.

**Author:** Tom Sapletta  
**License:** Apache-2.0[(LICENSE)](./LICENSE)  
**Repository:** [https://github.com/wronai/code2flow](https://github.com/wronai/code2flow)

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

## Generated Output

When you run `code2llm`, the following files are produced:

```
<project>/
├── README.md                 # Main project README (auto-generated sections)
├── docs/
│   ├── api.md               # Consolidated API reference
│   ├── modules.md           # Module documentation with metrics
│   ├── architecture.md      # Architecture overview with diagrams
│   ├── dependency-graph.md  # Module dependency graphs
│   ├── coverage.md          # Docstring coverage report
│   ├── getting-started.md   # Getting started guide
│   ├── configuration.md    # Configuration reference
│   └── api-changelog.md    # API change tracking
├── examples/
│   ├── quickstart.py       # Basic usage examples
│   └── advanced_usage.py   # Advanced usage examples
├── CONTRIBUTING.md         # Contribution guidelines
└── mkdocs.yml             # MkDocs site configuration
```

## Configuration

Create `code2llm.yaml` in your project root (or run `code2llm init`):

```yaml
project:
  name: my-project
  source: ./
  output: ./docs/

readme:
  sections:
    - overview
    - install
    - quickstart
    - api
    - structure
  badges:
    - version
    - python
    - coverage
  sync_markers: true

docs:
  api_reference: true
  module_docs: true
  architecture: true
  changelog: true

examples:
  auto_generate: true
  from_entry_points: true

sync:
  strategy: markers    # markers | full | git-diff
  watch: false
  ignore:
    - "tests/"
    - "__pycache__"
```

## Sync Markers

code2llm can update only specific sections of an existing README using HTML comment markers:

```markdown
<!-- code2llm:start -->
# Project Title
... auto-generated content ...
<!-- code2llm:end -->
```

Content outside the markers is preserved when regenerating. Enable this with `sync_markers: true` in your configuration.

## Architecture

```
code2llm/
    ├── benchmark_evolution├── setup    ├── reporting├── validate_toon    ├── format_evaluator    ├── project_generator    ├── benchmark_constants    ├── functional_refactoring_example    ├── benchmark_badges    ├── server    ├── cli    ├── bump_version├── code2llm/    ├── __main__    ├── api    ├── cli_parser    ├── cli_commands        ├── sample    ├── cli_analysis        ├── data_analysis        ├── pipeline_detector    ├── analysis/        ├── type_inference    ├── benchmark_format_quality    ├── benchmark_performance        ├── coupling        ├── side_effects        ├── smells        ├── config        ├── file_cache        ├── analyzer        ├── large_repo        ├── repo_files    ├── core/        ├── streaming_analyzer        ├── gitignore        ├── cfg        ├── toon_size_manager        ├── refactoring        ├── dfg        ├── file_filter        ├── call_graph    ├── nlp/        ├── config        ├── file_analyzer        ├── intent_matching        ├── normalization        ├── models        ├── entity_resolution        ├── base        ├── pipeline        ├── readme_exporter        ├── toon/    ├── exporters/        ├── json_exporter        ├── report_generators        ├── yaml_exporter        ├── project_yaml_exporter        ├── map_exporter        ├── context_view        ├── mermaid_exporter        ├── llm_exporter        ├── article_view        ├── flow_constants        ├── validate_project        ├── context_exporter        ├── evolution_exporter        ├── flow_renderer        ├── html_dashboard    ├── generators/        ├── toon_view        ├── index_generator        ├── flow_exporter        ├── llm_task        ├── code2logic    ├── cli_exports/        ├── mermaid        ├── formats    ├── refactor/        ├── llm_flow        ├── orchestrator        ├── toon_parser    ├── patterns/        ├── prompt_engine        ├── detector            ├── helpers        ├── prompt            ├── module_detail            ├── incremental        ├── streaming/            ├── strategies            ├── prioritizer            ├── cache            ├── scanner            ├── rust            ├── metrics            ├── cpp        ├── lang/            ├── renderer            ├── csharp            ├── go_lang            ├── java            ├── base            ├── generic            ├── typescript        ├── run            ├── auth        ├── sample_project/        ├── demo            ├── api            ├── utils            ├── database├── orchestrator├── project            ├── main            ├── ruby            ├── php```

### Classes

- **`FormatScore`** — Wynik oceny pojedynczego formatu.
- **`TemplateGenerator`** — Original - handles EVERYTHING: loading, matching, rendering, shell, docker, sql...
- **`CommandContext`** — Context for command generation.
- **`CommandResult`** — Result of command generation.
- **`EntityPreparer`** — Protocol for domain-specific entity preparation.
- **`ShellEntityPreparer`** — Prepares entities for shell commands.
- **`DockerEntityPreparer`** — Prepares entities for docker commands.
- **`SQLEntityPreparer`** — Prepares entities for SQL commands.
- **`KubernetesEntityPreparer`** — Prepares entities for kubernetes commands.
- **`EntityPreparationPipeline`** — Coordinates entity preparation across domains.
- **`Template`** — Command template.
- **`TemplateLoader`** — Loads templates from various sources.
- **`TemplateRenderer`** — Renders templates with entity substitution.
- **`CommandGenerator`** — Generates commands from natural language intents.
- **`CacheEntry`** — Single cache entry with evolution metadata.
- **`EvolutionaryCache`** — Cache that evolves based on usage patterns.
- **`User`** — —
- **`UserService`** — —
- **`DataAnalyzer`** — Analyze data flows, structures, and optimization opportunities.
- **`PipelineStage`** — A single stage in a detected pipeline.
- **`Pipeline`** — A detected pipeline with stages, purity info, and domain.
- **`PipelineDetector`** — Detect pipelines in a codebase using networkx graph analysis.
- **`TypeInferenceEngine`** — Extract and infer type information from Python source files.
- **`CouplingAnalyzer`** — Analyze coupling between modules.
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
- **`ProjectAnalyzer`** — Main analyzer with parallel processing.
- **`SubProject`** — Represents a sub-project within a larger repository.
- **`HierarchicalRepoSplitter`** — Splits large repositories using hierarchical approach.
- **`StreamingAnalyzer`** — Memory-efficient streaming analyzer with progress tracking.
- **`GitIgnoreParser`** — Parse and apply .gitignore patterns to file paths.
- **`CFGExtractor`** — Extract Control Flow Graph from AST.
- **`RefactoringAnalyzer`** — Performs refactoring analysis on code.
- **`DFGExtractor`** — Extract Data Flow Graph from AST.
- **`FastFileFilter`** — Fast file filtering with pattern matching.
- **`CallGraphExtractor`** — Extract call graph from AST.
- **`NormalizationConfig`** — Configuration for query normalization.
- **`IntentMatchingConfig`** — Configuration for intent matching.
- **`EntityResolutionConfig`** — Configuration for entity resolution.
- **`MultilingualConfig`** — Configuration for multilingual processing.
- **`NLPConfig`** — Main NLP pipeline configuration.
- **`FileAnalyzer`** — Analyzes a single file.
- **`IntentMatch`** — Single intent match result.
- **`IntentMatchingResult`** — Result of intent matching.
- **`IntentMatcher`** — Match queries to intents using fuzzy and keyword matching.
- **`NormalizationResult`** — Result of query normalization.
- **`QueryNormalizer`** — Normalize queries for consistent processing.
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
- **`Entity`** — Resolved entity.
- **`EntityResolutionResult`** — Result of entity resolution.
- **`EntityResolver`** — Resolve entities (functions, classes, etc.) from queries.
- **`Exporter`** — Abstract base class for all exporters.
- **`PipelineStage`** — Single pipeline stage result.
- **`NLPPipelineResult`** — Complete NLP pipeline result (4b-4e aggregation).
- **`NLPPipeline`** — Main NLP processing pipeline (4a-4e).
- **`READMEExporter`** — Export README.md with documentation of all generated files.
- **`JSONExporter`** — Export to JSON format.
- **`YAMLExporter`** — Export to YAML format.
- **`ProjectYAMLExporter`** — Export unified project.yaml — single source of truth for diagnostics.
- **`MapExporter`** — Export to map.toon.yaml — structural map with a compact project header.
- **`ContextViewGenerator`** — Generate context.md from project.yaml data.
- **`MermaidExporter`** — Export call graph to Mermaid format.
- **`ArticleViewGenerator`** — Generate status.md — publishable project health article.
- **`ContextExporter`** — Export LLM-ready analysis summary with architecture and flows.
- **`EvolutionExporter`** — Export evolution.toon.yaml — prioritized refactoring queue.
- **`FlowRenderer`** — Renderer dla sekcji formatu flow.toon.
- **`HTMLDashboardGenerator`** — Generate dashboard.html from project.yaml data.
- **`ToonViewGenerator`** — Generate project.toon.yaml from project.yaml data.
- **`IndexHTMLGenerator`** — Generate index.html for browsing all generated files.
- **`FlowExporter`** — Export to flow.toon — data-flow focused format.
- **`FuncSummary`** — —
- **`PromptEngine`** — Generate refactoring prompts from analysis results and detected smells.
- **`PatternDetector`** — Detect behavioral patterns in code.
- **`ToonExporter`** — Export to toon v2 plain-text format — scannable, sorted by severity.
- **`ModuleDetailRenderer`** — Renders detailed module information.
- **`IncrementalAnalyzer`** — Incremental analysis with change detection.
- **`ScanStrategy`** — Scanning methodology configuration.
- **`FilePriority`** — Priority scoring for file analysis order.
- **`SmartPrioritizer`** — Smart file prioritization for optimal analysis order.
- **`StreamingFileCache`** — Memory-efficient cache with LRU eviction.
- **`StreamingScanner`** — Handles file scanning operations.
- **`MetricsComputer`** — Computes all metrics for TOON export.
- **`ToonRenderer`** — Renders all sections for TOON export.
- **`AuthManager`** — Manages user authentication and authorization.
- **`APIHandler`** — Handles API requests and responses.
- **`DatabaseConnection`** — Simple database connection simulator.
- **`UserRequest`** — User request data structure.
- **`Application`** — Main application class with multiple responsibilities.

### Functions

- `parse_evolution_metrics(toon_content)` — Extract metrics from evolution.toon content.
- `load_previous(history_file)` — Load previous metrics from history file if present.
- `save_current(history_file, metrics)` — Save current metrics for next comparison.
- `run_benchmark(project_path)` — Run evolution analysis and print before/after table.
- `read_readme()` — —
- `print_results(scores)` — Wydrukuj sformatowane wyniki benchmarku.
- `build_report(scores)` — Zbuduj raport JSON do zapisu.
- `save_report(report, filename)` — Zapisz raport benchmarku do folderu reports.
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
- `evaluate_format(name, content, path)` — Oceń pojedynczy format względem ground truth.
- `create_core_py(project)` — Utwórz core.py z god function, hub type, high fan-out i side-effect.
- `create_etl_py(project)` — Utwórz etl.py z funkcjami pipeline ETL.
- `create_validation_py(project)` — Utwórz validation.py z pipeline'em walidacji.
- `create_utils_py(project)` — Utwórz utils.py z duplikatem klasy Validator.
- `add_validator_to_core(project)` — Dodaj klasę Validator do core.py (tworzy duplikat).
- `create_ground_truth_project(base_dir)` — Utwórz projekt testowy ze znanymi, mierzalnymi problemami.
- `generate(query, intent, dry_run, cache_dir)` — Generate command from natural language query.
- `get_shield_url(label, message, color)` — Generate a shields.io badge URL.
- `parse_evolution_metrics(toon_content)` — Extract metrics from evolution.toon content.
- `parse_format_quality_report(report_path)` — Parse format quality JSON report.
- `parse_performance_report(report_path)` — Parse performance JSON report.
- `generate_badges(metrics)` — Generate badge data from metrics.
- `generate_format_quality_badges(format_scores)` — Generate badges from format quality scores.
- `generate_performance_badges(performance_data)` — Generate badges from performance data.
- `create_html(badges, title)` — Create HTML page with badge table.
- `main()` — Main function to generate badges.
- `index()` — Serve the main badges page.
- `generate_badges()` — Generate badges by running the benchmark script.
- `get_badges()` — Get the generated badges HTML.
- `main()` — Main CLI entry point.
- `get_current_version()` — Get current version from pyproject.toml
- `parse_version(version_str)` — Parse version string into tuple of (major, minor, patch)
- `format_version(major, minor, patch)` — Format version tuple as string
- `bump_version(version_type)` — Bump version based on type (major, minor, patch)
- `update_pyproject_toml(new_version)` — Update version in pyproject.toml
- `update_version_file(new_version)` — Update VERSION file
- `main()` — —
- `analyze(project_path, config)` — Analyze a Python project and return structured results.
- `analyze_file(file_path, config)` — Analyze a single Python file.
- `create_parser()` — Create CLI argument parser.
- `handle_special_commands()` — Handle special sub-commands (llm-flow, llm-context, report).
- `handle_report_command(args_list)` — Generate views from an existing project.yaml (legacy).
- `validate_and_setup(args)` — Validate source path and setup output directory.
- `print_start_info(args, source_path, output_dir)` — Print analysis start information if verbose.
- `validate_chunked_output(output_dir, args)` — Validate generated chunked output.
- `generate_llm_context(args_list)` — Quick command to generate LLM context only.
- `run_benchmark()` — Run the full format quality benchmark.
- `save_report(results, filename)` — Save benchmark report to reports folder.
- `create_test_project(size)` — Create test project of specified size.
- `benchmark_original_analyzer(project_path, runs)` — Benchmark original ProjectAnalyzer.
- `benchmark_streaming_analyzer(project_path, runs)` — Benchmark new StreamingAnalyzer.
- `benchmark_with_strategies(project_path)` — Benchmark all strategies.
- `print_comparison(original, streaming)` — Print comparison table.
- `main()` — Run benchmark suite.
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
- `load_project_yaml(path)` — Load and validate project.yaml.
- `validate_project_yaml(output_dir, verbose)` — Validate project.yaml against generated views in output_dir.
- `normalize_llm_task(data)` — —
- `parse_llm_task_text(text)` — Parse LLM task text into structured data.
- `load_input(path)` — —
- `dump_yaml(data)` — —
- `create_parser()` — —
- `main(argv)` — —
- `validate_mermaid_file(mmd_path)` — Validate Mermaid file and return list of errors.
- `fix_mermaid_file(mmd_path)` — Attempt to fix common Mermaid syntax errors.
- `generate_pngs(input_dir, output_dir, timeout)` — Generate PNG files from all .mmd files in input_dir.
- `generate_single_png(mmd_file, output_file, timeout)` — Generate PNG from single Mermaid file using available renderers.
- `generate_with_puppeteer(mmd_file, output_file, timeout, max_text_size)` — Generate PNG using Puppeteer with HTML template.
- `generate_llm_flow(analysis, max_functions, limit_decisions, limit_calls)` — —
- `render_llm_flow_md(flow)` — —
- `dump_yaml(data)` — —
- `create_parser()` — —
- `main(argv)` — —
- `parse_toon_content(content)` — Parse TOON v2 plain-text format.
- `is_toon_file(filepath)` — Check if file is TOON format based on extension or content.
- `load_toon(filepath)` — Parse TOON plain-text format into structured data.
- `analyze_rust(content, file_path, module_name, ext)` — Analyze Rust files using regex-based parsing.
- `analyze_cpp(content, file_path, module_name, ext)` — Analyze C++ files using shared extraction.
- `analyze_csharp(content, file_path, module_name, ext)` — Analyze C# files using shared extraction.
- `analyze_go(content, file_path, module_name, ext)` — Analyze Go files using regex-based parsing.
- `analyze_java(content, file_path, module_name, ext)` — Analyze Java files using shared extraction.
- `extract_function_body(content, start_line)` — Extract the body of a function between braces from a start line (1-indexed).
- `calculate_complexity_regex(content, result, lang)` — Estimate cyclomatic complexity for every function using regex keyword counting.
- `extract_calls_regex(content, module_name, result)` — Extract function calls from function bodies using regex.
- `analyze_generic(content, file_path, module_name, ext)` — Basic structural analysis for unsupported languages.
- `analyze_typescript_js(content, file_path, module_name, ext)` — Analyze TypeScript/JavaScript files using shared extraction.
- `run_analysis(project_path)` — Run code2llm and return analysis outputs.
- `get_refactoring_advice(outputs, model)` — Send analysis to LLM and get refactoring advice.
- `main()` — —
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
- `NewUserService()` — —
- `AddUser()` — —
- `GetUser()` — —
- `ProcessUsers()` — —
- `main()` — Main entry point.
- `analyze_ruby(content, file_path, module_name, ext)` — Analyze Ruby files using shared extraction.
- `analyze_php(content, file_path, module_name, ext)` — Analyze PHP files using shared extraction.


## Project Structure

📄 `badges.server` (3 functions)
📄 `benchmarks.benchmark_constants`
📄 `benchmarks.benchmark_evolution` (4 functions)
📄 `benchmarks.benchmark_format_quality` (5 functions)
📄 `benchmarks.benchmark_performance` (7 functions)
📄 `benchmarks.format_evaluator` (5 functions, 1 classes)
📄 `benchmarks.project_generator` (6 functions)
📄 `benchmarks.reporting` (9 functions)
📦 `code2llm` (1 functions)
📄 `code2llm.__main__`
📦 `code2llm.analysis` (1 functions)
📄 `code2llm.analysis.call_graph` (13 functions, 1 classes)
📄 `code2llm.analysis.cfg` (17 functions, 1 classes)
📄 `code2llm.analysis.coupling` (5 functions, 1 classes)
📄 `code2llm.analysis.data_analysis` (18 functions, 1 classes)
📄 `code2llm.analysis.dfg` (12 functions, 1 classes)
📄 `code2llm.analysis.pipeline_detector` (18 functions, 3 classes)
📄 `code2llm.analysis.side_effects` (17 functions, 2 classes)
📄 `code2llm.analysis.smells` (9 functions, 1 classes)
📄 `code2llm.analysis.type_inference` (19 functions, 1 classes)
📄 `code2llm.api` (2 functions)
📄 `code2llm.cli` (1 functions)
📄 `code2llm.cli_analysis` (11 functions)
📄 `code2llm.cli_commands` (6 functions)
📦 `code2llm.cli_exports`
📄 `code2llm.cli_exports.code2logic` (8 functions)
📄 `code2llm.cli_exports.formats` (12 functions)
📄 `code2llm.cli_exports.orchestrator` (5 functions)
📄 `code2llm.cli_exports.prompt` (17 functions)
📄 `code2llm.cli_parser` (1 functions)
📦 `code2llm.core` (1 functions)
📄 `code2llm.core.analyzer` (9 functions, 1 classes)
📄 `code2llm.core.config` (6 classes)
📄 `code2llm.core.file_analyzer` (17 functions, 1 classes)
📄 `code2llm.core.file_cache` (6 functions, 1 classes)
📄 `code2llm.core.file_filter` (3 functions, 1 classes)
📄 `code2llm.core.gitignore` (6 functions, 1 classes)
📦 `code2llm.core.lang`
📄 `code2llm.core.lang.base` (9 functions)
📄 `code2llm.core.lang.cpp` (1 functions)
📄 `code2llm.core.lang.csharp` (1 functions)
📄 `code2llm.core.lang.generic` (1 functions)
📄 `code2llm.core.lang.go_lang` (1 functions)
📄 `code2llm.core.lang.java` (1 functions)
📄 `code2llm.core.lang.php` (1 functions)
📄 `code2llm.core.lang.ruby` (2 functions)
📄 `code2llm.core.lang.rust` (1 functions)
📄 `code2llm.core.lang.typescript` (1 functions)
📄 `code2llm.core.large_repo` (20 functions, 2 classes)
📄 `code2llm.core.models` (6 functions, 11 classes)
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
📄 `code2llm.exporters.article_view` (9 functions, 1 classes)
📄 `code2llm.exporters.base` (1 functions, 1 classes)
📄 `code2llm.exporters.context_exporter` (15 functions, 1 classes)
📄 `code2llm.exporters.context_view` (8 functions, 1 classes)
📄 `code2llm.exporters.evolution_exporter` (17 functions, 1 classes)
📄 `code2llm.exporters.flow_constants`
📄 `code2llm.exporters.flow_exporter` (14 functions, 1 classes)
📄 `code2llm.exporters.flow_renderer` (6 functions, 1 classes)
📄 `code2llm.exporters.html_dashboard` (14 functions, 1 classes)
📄 `code2llm.exporters.index_generator` (7 functions, 1 classes)
📄 `code2llm.exporters.json_exporter` (1 functions, 1 classes)
📄 `code2llm.exporters.llm_exporter`
📄 `code2llm.exporters.map_exporter` (21 functions, 1 classes)
📄 `code2llm.exporters.mermaid_exporter` (19 functions, 1 classes)
📄 `code2llm.exporters.project_yaml_exporter` (18 functions, 1 classes)
📄 `code2llm.exporters.readme_exporter` (7 functions, 1 classes)
📄 `code2llm.exporters.report_generators` (1 functions)
📦 `code2llm.exporters.toon` (11 functions, 1 classes)
📄 `code2llm.exporters.toon.helpers` (8 functions)
📄 `code2llm.exporters.toon.metrics` (27 functions, 1 classes)
📄 `code2llm.exporters.toon.module_detail` (9 functions, 1 classes)
📄 `code2llm.exporters.toon.renderer` (26 functions, 1 classes)
📄 `code2llm.exporters.toon_view` (9 functions, 1 classes)
📄 `code2llm.exporters.validate_project` (3 functions)
📄 `code2llm.exporters.yaml_exporter` (7 functions, 1 classes)
📦 `code2llm.generators`
📄 `code2llm.generators.llm_flow` (24 functions, 1 classes)
📄 `code2llm.generators.llm_task` (15 functions)
📄 `code2llm.generators.mermaid` (16 functions)
📦 `code2llm.nlp`
📄 `code2llm.nlp.config` (2 functions, 5 classes)
📄 `code2llm.nlp.entity_resolution` (16 functions, 3 classes)
📄 `code2llm.nlp.intent_matching` (15 functions, 3 classes)
📄 `code2llm.nlp.normalization` (13 functions, 2 classes)
📄 `code2llm.nlp.pipeline` (20 functions, 3 classes)
📄 `code2llm.parsers.toon_parser` (10 functions)
📦 `code2llm.patterns`
📄 `code2llm.patterns.detector` (8 functions, 1 classes)
📦 `code2llm.refactor`
📄 `code2llm.refactor.prompt_engine` (7 functions, 1 classes)
📄 `demo_langs.valid.sample` (4 functions, 2 classes)
📄 `examples.functional_refactoring_example` (50 functions, 15 classes)
📄 `examples.litellm.run` (3 functions)
📄 `examples.streaming-analyzer.demo` (7 functions)
📦 `examples.streaming-analyzer.sample_project`
📄 `examples.streaming-analyzer.sample_project.api` (7 functions, 1 classes)
📄 `examples.streaming-analyzer.sample_project.auth` (10 functions, 1 classes)
📄 `examples.streaming-analyzer.sample_project.database` (13 functions, 1 classes)
📄 `examples.streaming-analyzer.sample_project.main` (9 functions, 2 classes)
📄 `examples.streaming-analyzer.sample_project.utils` (5 functions)
📄 `orchestrator`
📄 `project`
📄 `scripts.benchmark_badges` (9 functions)
📄 `scripts.bump_version` (7 functions)
📄 `setup` (1 functions)
📄 `validate_toon` (15 functions)

## Requirements

- Python >= >=3.8
- networkx >=2.6- matplotlib >=3.4- pyyaml >=5.4- numpy >=1.20- jinja2 >=3.0- radon >=5.1- astroid >=3.0- code2logic- vulture >=2.10- tiktoken >=0.5- tree-sitter >=0.21- tree-sitter-python >=0.21

## Contributing

**Contributors:**
- Tom Softreck <tom@sapletta.com>
- Tom Sapletta <tom-sapletta-com@users.noreply.github.com>

We welcome contributions! Please see [CONTRIBUTING.md](https://github.com/wronai/code2llm/blob/main/CONTRIBUTING.md) for guidelines.

# Clone the repository
git clone https://github.com/wronai/code2flow
cd code2llm

# Install in development mode
pip install -e ".[dev]"

## Documentation

- 📖 [Full Documentation](https://github.com/wronai/code2flow/tree/main/docs) — API reference, module docs, architecture
- 🚀 [Getting Started](https://github.com/wronai/code2flow/blob/main/docs/getting-started.md) — Quick start guide
- 📚 [API Reference](https://github.com/wronai/code2flow/blob/main/docs/api.md) — Complete API documentation
- 🔧 [Configuration](https://github.com/wronai/code2flow/blob/main/docs/configuration.md) — Configuration options
- 💡 [Examples](./examples) — Usage examples and code samples

### Generated Files

| Output | Description | Link |
|--------|-------------|------|
| `README.md` | Project overview (this file) | — |
| `docs/api.md` | Consolidated API reference | [View](https://github.com/wronai/code2llm/blob/main/docs/api.md) |
| `docs/modules.md` | Module reference with metrics | [View](https://github.com/wronai/code2llm/blob/main/docs/modules.md) |
| `docs/architecture.md` | Architecture with diagrams | [View](https://github.com/wronai/code2llm/blob/main/docs/architecture.md) |
| `docs/dependency-graph.md` | Dependency graphs | [View](https://github.com/wronai/code2llm/blob/main/docs/dependency-graph.md) |
| `docs/coverage.md` | Docstring coverage report | [View](https://github.com/wronai/code2llm/blob/main/docs/coverage.md) |
| `docs/getting-started.md` | Getting started guide | [View](https://github.com/wronai/code2llm/blob/main/docs/getting-started.md) |
| `docs/configuration.md` | Configuration reference | [View](https://github.com/wronai/code2llm/blob/main/docs/configuration.md) |
| `docs/api-changelog.md` | API change tracking | [View](https://github.com/wronai/code2llm/blob/main/docs/api-changelog.md) |
| `CONTRIBUTING.md` | Contribution guidelines | [View](https://github.com/wronai/code2llm/blob/main/CONTRIBUTING.md) |
| `examples/` | Usage examples | [Browse](./examples) |
| `mkdocs.yml` | MkDocs configuration | — |

<!-- code2docs:end -->