## [0.3.8] - 2026-03-01

### Summary

feat(rebrand): rename project from code2flow-toon to code2llm with LLM integration focus

### Changed

- **Package name**: `code2flow-toon` → `code2llm`
- **Documentation**: Updated all references to use new project name
- **Commands**: All CLI commands now use `code2llm`
- **Setup**: Updated setup.py and pyproject.toml with new name
- **Makefile**: All targets updated to use `code2llm` commands

## [0.3.2] - 2026-03-01

### Summary

feat(pipelines): networkx-based pipeline detection with domain grouping and entry/exit labeling

### Added

- **PipelineDetector** (`analysis/pipeline_detector.py`)
  - Builds directed call graph with `networkx.DiGraph`
  - Finds longest paths via `dag_longest_path` + DFS fallback for cycles
  - Classifies pipelines by domain: NLP, Analysis, Export, Refactor, Core, IO
  - Labels entry/exit points per pipeline
  - Aggregates purity per pipeline using `SideEffectDetector`
  - `Pipeline` and `PipelineStage` dataclasses with `to_dict()` support

- **22 new tests** (`tests/test_sprint3_pipelines.py`)
  - PipelineDetector: chain detection, entry/exit, purity, bottleneck, edge cases
  - Domain classification: NLP, Analysis, Export, Unknown
  - Multiple pipelines: ≥3 pipelines with ≥3 stages each (success metric ✅)
  - FlowExporter integration: domain tags, entry/exit markers, purity summary
  - Edge cases: cycles, self-recursion, diamond dependencies, long chains

### Changed

- **FlowExporter** now uses `PipelineDetector` instead of custom DFS
  - Replaced `_detect_pipelines`, `_trace_chain`, `_pipeline_name` with networkx
  - PIPELINES header shows domain summary: `PIPELINES[3] (Analysis:1, Export:1, NLP:1)`
  - Pipeline stages show ▶ (entry) and ■ (exit) markers
  - Pipeline header shows entry→exit type flow: `NLP [NLP]: str → IntentMatch`

- **Version bump** to 0.3.2

---

## [0.3.1] - 2026-03-01

### Summary

feat(flow): AST-based type inference + side-effect detection for enhanced CONTRACTS and DATA_TYPES

### Added

- **TypeInferenceEngine** (`analysis/type_inference.py`)
  - Parses `->` return annotations from source AST
  - Extracts argument type hints (`arg: Type`)
  - Fallback: infers types from function name patterns (`parse_*` → str→dict)
  - Batch mode: `extract_all_types()` for all project functions

- **SideEffectDetector** (`analysis/side_effects.py`)
  - AST scan: detects `open()`, `write()`, `self.x = ...`, `global`, `del`
  - Classification: IO / Cache / Mutation / Pure
  - `SideEffectInfo` with detailed breakdown and summary
  - Heuristic fallback when source files unavailable

- **26 new tests** (`tests/test_sprint2_flow.py`)
  - TypeInferenceEngine: annotation extraction, defaults, signatures, batch
  - SideEffectDetector: IO, pure, mutation, summary, batch, heuristic
  - FlowExporter integration: contracts IN/OUT, data types, edge cases

### Changed

- **Enhanced CONTRACTS section** in `flow.toon`
  - Per-stage: IN types, OUT type, SIDE-EFFECT summary
  - INVARIANT inference (normalize → `len(output) <= len(input)`)
  - SMELL markers for CC ≥ 15

- **Enhanced DATA_TYPES section** in `flow.toon`
  - Source counts: `[N annotated, M inferred / T functions]`
  - Hub-type split recommendations with named sub-interfaces
  - e.g. `AnalysisResult → split into: StructureResult, MetricsResult, FlowResult`

- **FlowExporter** now uses `TypeInferenceEngine` and `SideEffectDetector`
  - Typed signatures from AST (not just arg names)
  - Purity scoring from AST body scan (not just name heuristics)

- **Version bump** to 0.3.1

---

## [0.3.0] - 2026-03-01

### Summary

refactor(exporters): format taxonomy — 4 files, 4 purposes (map, toon, flow, context)

### Added

- **MapExporter** (`project.map`) — structural map format
  - Modules, imports, signatures, type information
  - Formerly `project.toon` — renamed for clarity
  - Purpose: "what exists and how it's connected"

- **FlowExporter** (`flow.toon`) — **NEW** data-flow format
  - PIPELINES: auto-detected call chains with purity scoring
  - TRANSFORMS: high fan-out functions sorted by fan-out
  - CONTRACTS: per-pipeline input→output with CC and purity
  - DATA_TYPES: consumed/produced counts, hub-type detection
  - SIDE_EFFECTS: IO/Cache/Mutation/Pure classification
  - Purpose: "how data flows through the system"

- **New CLI format options**
  - `--format map` — generate project.map (structural map)
  - `--format flow` — generate flow.toon (data-flow analysis)
  - `--format context` — generate context.md (LLM narrative)
  - `--format all` — now generates all 8 formats (toon, map, flow, context, yaml, json, mermaid, png)

### Changed

- **Renamed `llm_prompt.md` → `context.md`** — LLM narrative context
  - LLMPromptExporter now outputs `context.md` by default
  - Purpose: "understand the system to rebuild it"

- **Format taxonomy** based on benchmark analysis (TODO/action_plan_v3.md)
  - `project.map` — structure (modules, imports, signatures)
  - `analysis.toon` — health diagnostics (CC, coupling, smells)
  - `flow.toon` — data flow (pipelines, contracts, hub-types)
  - `context.md` — LLM narrative (architecture, patterns, API)

- **Version bump** to 0.3.0

### Docs

- Updated README.md with new format taxonomy and examples
- Updated TODO.md with Sprint 2-4 roadmap from action_plan_v3
- Updated CHANGELOG.md, ROADMAP.md, REFACTORING_PLAN.md

---

## [0.2.5] - 2026-03-01

### Summary

feat(toon): implement TOON v2 format with health-first design

### Added

- **TOON v2 Format** - complete reimplementation of the exporter
  - HEALTH section: issues sorted by severity (🔴/🟡), limited to 20 items
  - REFACTOR section: actionable steps with concrete recommendations
  - COUPLING matrix: package-level fan-in/fan-out analysis, limited to 15 packages
  - LAYERS section: package hierarchy with inline markers
  - DUPLICATES detection: find classes with identical method sets (≥60% overlap)
  - FUNCTIONS section: filtered by CC≥10, limited to 50 items
  - HOTSPOTS ranking: top 10 functions by fan-out with descriptions
  - CLASSES section: visual bar charts (████), max CC markers
  - D: details section: per-module call flow signatures

- **Smart Filtering**
  - EXCLUDE_PATTERNS: venv, site-packages, node_modules, .git, etc.
  - Automatic exclusion of virtual environments
  - Configurable limits: MAX_HEALTH_ISSUES, MAX_COUPLING_PACKAGES, MAX_FUNCTIONS_SHOWN

- **Inline Markers**
  - `!!` for CC≥15 (critical)
  - `!` for CC≥10 (high)
  - `×DUP` for duplicate classes
  - `hub` for high fan-in packages
  - `SMELL` for high fan-out packages

### Test

- add tests/test_toon_v2.py with 17 comprehensive tests
- all tests passing (17/17)

### Docs

- update README.md with TOON v2 format documentation


## [0.2.4] - 2026-02-28

### Summary

docs(docs): deep code analysis engine with 5 supporting modules

### Docs

- docs: update README


## [0.2.3] - 2026-02-28

### Summary

refactor(docs): intelligent code analysis pipeline

### Docs

- docs: update llm_prompt.md
- docs: update 01_god_function_god_function_normalize_llm_task.md
- docs: update 02_god_function_god_function_parse_llm_task_text.md
- docs: update 03_god_function_god_function_main.md
- docs: update 04_god_function_god_function_validate_mermaid_file.md
- docs: update 05_god_function_god_function_fix_mermaid_file.md
- docs: update 06_god_function_god_function_generate_pngs.md
- docs: update 07_god_function_god_function_generate_single_png.md
- docs: update 08_god_function_god_function_strip_label_segments.md
- docs: update 09_god_function_god_function___init__.md
- ... and 676 more

### Test

- update tests/test_sprint5.py

### Config

- config: update goal.yaml

### Other

- update TICKET
- config: update analysis.yaml
- update final_prompts/call_graph.png
- update final_prompts/calls.mmd
- update final_prompts/cfg.png
- update final_prompts/compact_flow.mmd
- update final_prompts/flow.mmd
- scripts: update project.sh
- update project.toon
- config: update analysis.yaml
- ... and 5 more


## [0.2.2] - 2026-02-28

### Summary

feat(goal): deep code analysis engine with 7 supporting modules

### Ci

- config: update publish.yml

### Config

- config: update goal.yaml

### Other

- scripts: update project.sh


## [0.2.1] - 2026-02-28

### Summary

refactor(docs): code analysis engine

### Docs

- docs: update TODO.md
- docs: update context.md
- docs: update context_final.md
- docs: update context_fixed.md
- docs: update fast_analysis_report.md

### Config

- config: update goal.yaml

### Other

- update debug/.code2flow_cache/__init___067a3ea9a806bdcd.pkl
- update debug/.code2flow_cache/__init___06ee3b304cbac344.pkl
- update debug/.code2flow_cache/__init___07004ae5fc0b63a4.pkl
- update debug/.code2flow_cache/__init___092c164e1ea3ed2a.pkl
- update debug/.code2flow_cache/__init___1306939d2650ad0a.pkl
- update debug/.code2flow_cache/__init___1435b739d4a93c01.pkl
- update debug/.code2flow_cache/__init___1a3f34073e505d94.pkl
- update debug/.code2flow_cache/__init___20b71d7ad5e01760.pkl
- update debug/.code2flow_cache/__init___385814d063e205eb.pkl
- update debug/.code2flow_cache/__init___563e1960e3f8fe02.pkl
- ... and 222 more


# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-02-28

### Added

#### Core Analysis Engine
- **Optimized ProjectAnalyzer** with caching and parallel processing
  - FileCache with TTL support for AST parsing results
  - Parallel file analysis using ProcessPoolExecutor
  - Configurable performance settings (FAST_CONFIG, DETAILED_CONFIG)
  - Memory-efficient depth limiting for CFG generation

- **Enhanced Filtering**
  - FastFileFilter with glob pattern matching
  - Exclude test files, private methods, properties
  - Min function lines threshold
  - Configurable include/exclude patterns

- **Comprehensive Code Model**
  - FlowNode, FlowEdge for CFG representation
  - FunctionInfo, ClassInfo, ModuleInfo with metadata
  - Pattern detection (recursion, state machines)
  - Compact JSON/YAML output with optional full details

#### NLP Processing Pipeline
- **Query Normalization (1a-1e)**
  - Unicode NFKC normalization
  - Lowercase conversion
  - Punctuation removal
  - Whitespace normalization
  - Stopword removal (multilingual)

- **Intent Matching (2a-2e)**
  - Fuzzy matching with configurable algorithms
  - Keyword matching with weighted scoring
  - Context window scoring for disambiguation
  - Multi-intent resolution strategies (best_match, combine, sequential)

- **Entity Resolution (3a-3e)**
  - Type-based entity extraction (function, class, module, variable, file)
  - Name matching with similarity threshold
  - Context-aware disambiguation
  - Hierarchical resolution (Class.method -> method)
  - Alias resolution (short -> qualified names)

- **Pipeline Integration (4a-4e)**
  - Orchestration with stage tracking
  - Result aggregation and confidence scoring
  - Fallback handling for low-confidence queries
  - Formatted output with action recommendations

- **Multilingual Support**
  - English and Polish query support
  - Cross-language fuzzy matching
  - Language-specific stopwords
  - YAML-driven configuration

#### Export Formats
- **JSON Exporter** - Machine-readable analysis output
- **YAML Exporter** - Human-readable with compact/full modes
- **Mermaid Exporter** - Flowchart and call graph visualization
- **LLMPromptExporter** - LLM-ready analysis summaries
- **GraphVisualizer** - NetworkX/matplotlib PNG generation

#### CLI Enhancements
- Improved argument parsing with subcommands
- Automatic PNG generation from Mermaid files
- LLM flow generation command
- Verbose output with progress reporting
- Multiple output format support

#### Testing & Quality
- **Comprehensive Test Suite**
  - Unit tests for all core components
  - Edge case tests (empty projects, syntax errors, unicode)
  - Performance benchmarks
  - Integration tests (NLP + Analysis workflow)
  - NLP pipeline tests (steps 1a-4e validation)

- **Benchmarking**
  - Performance tests for large projects
  - Cache effectiveness measurement
  - Parallel vs sequential comparison
  - Memory usage validation

#### Documentation
- Complete API documentation
- Usage examples and tutorials
- Performance optimization guide
- Multilingual query examples
- Configuration reference

### Changed
- Refactored monolithic flow.py into modular package structure
- Improved error handling throughout codebase
- Enhanced type hints for better IDE support
- Updated setup.py for PyPI publication readiness

### Fixed
- Import errors in CLI module
- Attribute mismatches between models and exporters
- Parallel processing pickle compatibility issues
- FlowEdge attribute access (condition -> conditions)

## [0.1.0] - 2025-02-20

### Added
- Initial project structure
- Basic AST-based code analysis
- Control flow graph generation
- Call graph extraction
- Pattern detection (recursion, loops)
- Mermaid diagram export
- Command-line interface
- Initial test suite

---

## Future Roadmap

### Planned for 0.3.0
- [ ] Semantic code search using embeddings
- [ ] Advanced pattern detection (factory, singleton, observer)
- [ ] Interactive web UI (Streamlit/Gradio)
- [ ] VS Code extension
- [ ] Support for additional languages (JavaScript, TypeScript)

### Planned for 0.4.0
- [ ] Real-time code analysis via file watching
- [ ] Integration with Git for diff analysis
- [ ] Custom pattern definition via YAML
- [ ] Plugin system for third-party extensions
- [ ] Docker container for easy deployment

### Planned for 1.0.0
- [ ] Complete API stability
- [ ] Comprehensive security audit
- [ ] Enterprise features (SSO, audit logs)
- [ ] Performance optimizations for 100k+ LOC projects
- [ ] Full documentation with video tutorials

## Contributing

Please report issues and suggest features via GitHub Issues.

## Credits

Developed by the STTS Project team.
