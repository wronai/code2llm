# TODO - code2llm Project

## ✅ Completed — Rebranding (v0.3.8)

- [x] **Project Rebranding to code2llm**
  - [x] Package name: `code2flow-toon` → `code2llm`
  - [x] Documentation updates (README.md, API.md)
  - [x] CLI commands: `code2flow` → `code2llm`
  - [x] Makefile targets updated
  - [x] setup.py and pyproject.toml updated
  - [x] CHANGELOG.md and ROADMAP.md updated

## ✅ Completed — Sprint 1 (v0.3.0)

- [x] **Format Taxonomy Refactoring**
  - [x] Rename `project.toon` → `project.map` (new `MapExporter`)
  - [x] Rename `llm_prompt.md` → `context.md` (updated CLI output)
  - [x] New `FlowExporter` → `flow.toon` (data-flow: PIPELINES, TRANSFORMS, CONTRACTS, DATA_TYPES)
  - [x] Update CLI: `--format map,toon,flow,context,all`
  - [x] 4 files, 4 purposes: map (structure), toon (health), flow (data-flow), context (LLM)

## ✅ Completed — Sprint 2 (v0.3.1)

- [x] **Type inference from AST** (`analysis/type_inference.py`)
  - [x] Parse `->` return annotations
  - [x] Parse arguments with type hints
  - [x] Fallback: infer from names (`parse_*` → str input, `to_dict` → dict output)
  - [x] Batch mode: `extract_all_types()` for all project functions

- [x] **CONTRACTS section enhancement**
  - [x] Per-pipeline: IN types, OUT type for each stage
  - [x] Side-effect detection via AST: `self.`, `.write`, `open()`, `global`, `cache`
  - [x] Purity scoring: pure / IO / cache / mutation
  - [x] INVARIANT inference (normalize → `len(output) <= len(input)`)
  - [x] SMELL markers for CC ≥ 15

- [x] **DATA_TYPES section enhancement**
  - [x] Count consumed/produced per type (AST-based)
  - [x] Auto-detect hub-types (consumed ≥ 10)
  - [x] Hub-type split recommendations with named sub-interfaces
  - [x] Source counts: `[N annotated, M inferred / T functions]`

- [x] **SideEffectDetector** (`analysis/side_effects.py`)
  - [x] AST scan: `open()`, `write()`, `self.x = ...`, `global`, `del`
  - [x] Classification: IO / Cache / Mutation / Pure
  - [x] Heuristic fallback when source unavailable

- [x] **26 new tests** (`tests/test_sprint2_flow.py`)

## ✅ Completed — Sprint 3 (v0.3.2)

- [x] **Pipeline detection with networkx** (`analysis/pipeline_detector.py`)
  - [x] `networkx.DiGraph` call graph, `dag_longest_path` + DFS fallback
  - [x] Domain classification: NLP, Analysis, Export, Refactor, Core, IO
  - [x] Entry/exit point labeling (▶/■ markers)
  - [x] `Pipeline` and `PipelineStage` dataclasses

- [x] **SIDE_EFFECTS analysis** (done in Sprint 2, integrated in Sprint 3)
  - [x] AST scan: `open()`, `write()`, `self.cache`, `global`
  - [x] Classification: IO / Cache / Mutation / Pure
  - [x] Pipeline purity aggregation per pipeline

- [x] **Integration: flow.toon ← analysis.toon**
  - [x] CC metrics inline in pipeline stages
  - [x] Bottleneck identification per pipeline
  - [x] `!!` markers for CC ≥ 15
  - [x] Domain summary in PIPELINES header
  - [x] Entry→exit type flow per pipeline

- [x] **22 new tests** (`tests/test_sprint3_pipelines.py`)
  - [x] ≥3 pipelines with ≥3 stages each (success metric ✅)

## 🎯 Sprint 4 — Self-test + benchmark v2 (v0.3.3)

### High Priority

- [ ] **Self-analysis**
  - Run code2flow on itself with new flow.toon
  - Verify: detect NLP, Analysis, Export, Refactor pipelines
  - Verify: AnalysisResult marked as hub-type

- [ ] **Benchmark v2**
  - Run benchmark with 4 formats (map, toon, flow, context)
  - Target: flow.toon ≥ 8.0/10 in Data Flow (currently: 5.5)
  - Target: combined score ≥ 8.5/10

### Medium Priority

- [ ] **Semantic Code Search** (Phase 1.1)
  - Integrate sentence transformers for semantic embeddings
  - Build vector index for similarity search

- [ ] **Advanced Pattern Detection** (Phase 1.2)
  - Factory, Singleton, Observer, Strategy patterns

- [ ] **Interactive Web UI** (Phase 1.3)
  - Streamlit-based web interface
  - Interactive graph visualization (D3.js/Plotly)

### Low Priority

- [ ] **VS Code Extension** (Phase 2.1)
- [ ] **Real-time Analysis** (Phase 2.2)
- [ ] **Git Integration** (Phase 2.3)
- [ ] **JavaScript/TypeScript Support** (Phase 3.1)
- [ ] **Security Analysis** (Phase 4.1)

## 📝 Notes

- Format taxonomy based on TODO/action_plan_v3.md benchmark results
- Each format has one purpose: map=structure, toon=health, flow=data-flow, context=LLM
- This TODO list is managed by Goal — use `goal -t` for auto-detection

Last updated: 2026-03-01