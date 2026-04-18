# code2llm Development Roadmap

This document outlines planned features, improvements, and milestones for the code2llm project with LLM integration focus.

## Current Status (v0.5.0)

✅ **Completed:**
- Core analysis engine with caching and parallel processing
- NLP Processing Pipeline (Query Normalization, Intent Matching, Entity Resolution)
- Multilingual support (EN/PL)
- Comprehensive test suite
- CLI with multiple output formats
- PyPI publication ready
- **TOON v2 Format** — health-first diagnostics (`analysis.toon`)
- **Format Taxonomy (v0.3.0)** — 4 purpose-built output formats:
  - `project.map` — structural map (modules, imports, signatures, types)
  - `analysis.toon` — health diagnostics (HEALTH, REFACTOR, COUPLING, LAYERS)
  - `flow.toon` — data-flow analysis (PIPELINES, TRANSFORMS, CONTRACTS, DATA_TYPES)
  - `context.md` — LLM narrative (architecture, patterns, API surface)
  - CLI: `--format map,toon,flow,context,all`
- **AST-based type inference + side-effect detection (v0.3.1)**:
  - `TypeInferenceEngine` — parses return annotations, argument types, name-based fallback
  - `SideEffectDetector` — AST scan for IO, cache, mutation, pure classification
  - Enhanced CONTRACTS: IN/OUT types, SIDE-EFFECT, INVARIANT, SMELL markers
  - Enhanced DATA_TYPES: source counts, hub-type split recommendations
- **networkx-based pipeline detection (v0.3.2)**:
  - `PipelineDetector` — DiGraph call graph, longest-path detection, cycle-safe
  - Domain classification: NLP, Analysis, Export, Refactor, Core, IO
  - Entry/exit labeling, purity aggregation, bottleneck identification
- **Format quality benchmark + rename (v0.3.3)**:
  - `benchmark_format_quality.py` — ground-truth project, 8 problems, 4-axis scoring
  - 24 format quality tests (`test_format_quality.py`)
  - `llm_exporter` → `context_exporter` rename with backward compat
- **Rename + structural cleanup (v0.4.0)**:
  - `code2flow` → `code2llm` — full package rename (folder, imports, CLI, docs)
  - CLI: all 7 exporters connected (Toon, Map, Flow, Context, YAML, JSON, Mermaid)
  - Removed dead code: `optimization/` (1590L), `visualizers/` (150L)
  - Moved root-level generators to `generators/` subpackage
  - Renamed sprint-based tests to feature-based names
  - Updated all documentation references
- **Bug fixes + EvolutionExporter (v0.5.0)**:
  - Fixed MermaidExporter: 3 distinct outputs (flow.mmd, calls.mmd, compact_flow.mmd)
  - Fixed SideEffectDetector: `dict.get()` false positive as IO
  - Fixed coupling matrix: candidate-based callee disambiguation
  - Fixed pipeline detection: safe ambiguous callee handling
  - New `EvolutionExporter` → `evolution.toon` — ranked refactoring queue
  - CLI: `--format evolution` (8 total output formats)

---

#### 1.1 Semantic Code Search
**Status:** Not Started | **Priority:** High | **Effort:** Medium

- [ ] Integrate sentence transformers for semantic embeddings
- [ ] Build vector index of codebase for similarity search
- [ ] Add `semantic_search()` method to ProjectAnalyzer
- [ ] Support queries like "find code that handles authentication"

**Technical Notes:**
- Use `sentence-transformers` library
- Store embeddings in cache alongside AST
- Consider HNSW for fast approximate search

#### 1.2 Advanced Pattern Detection
**Status:** Not Started | **Priority:** High | **Effort:** Medium

- [ ] Factory pattern detection
- [ ] Singleton pattern detection  
- [ ] Observer pattern detection
- [ ] Strategy pattern detection
- [ ] Template method pattern detection

**Implementation:**
```python
class PatternDetector:
    def detect_factory(self, classes: List[ClassInfo]) -> List[Pattern]
    def detect_singleton(self, classes: List[ClassInfo]) -> List[Pattern]
    def detect_observer(self, classes: List[ClassInfo]) -> List[Pattern]
```

#### 1.3 Interactive Web UI
**Status:** Not Started | **Priority:** High | **Effort:** Large

- [ ] Streamlit-based web interface
- [ ] Upload and analyze projects via browser
- [ ] Interactive graph visualization (D3.js/Plotly)
- [ ] Natural language query interface
- [ ] Export to PNG/SVG/PDF

**Components:**
- File upload with drag-and-drop
- Project browser with tree view
- Search interface with filters
- Graph visualization with zoom/pan

---

#### 2.1 VS Code Extension
**Status:** Not Started | **Priority:** Medium | **Effort:** Large

- [ ] Extension manifest and activation
- [ ] Sidebar panel for project structure
- [ ] Code lens for function call graphs
- [ ] Hover information with call statistics
- [ ] Command palette integration
- [ ] Settings synchronization

**Features:**
- Right-click "Show Call Graph"
- Inline hints for recursive functions
- Status bar with project metrics

#### 2.2 Real-time Analysis
**Status:** Not Started | **Priority:** Medium | **Effort:** Medium

- [ ] File watching with watchdog
- [ ] Incremental analysis (only changed files)
- [ ] Background analysis daemon
- [ ] WebSocket updates for UI

**Performance Targets:**
- < 100ms for incremental updates
- < 5s for full project re-analysis

#### 2.3 Git Integration
**Status:** Not Started | **Priority:** Medium | **Effort:** Medium

- [ ] Diff analysis between commits
- [ ] Show changed functions/classes
- [ ] Impact analysis for PRs
- [ ] Code churn visualization
- [ ] Contributor statistics

---

#### 3.1 JavaScript/TypeScript Support
**Status:** Not Started | **Priority:** Medium | **Effort:** Large

- [ ] JS/TS AST parsing with Babel
- [ ] CommonJS and ES module resolution
- [ ] TypeScript type information extraction
- [ ] JSX/TSX component analysis

**Architecture:**
```python
class LanguageAnalyzer(ABC):
    @abstractmethod
    def parse_file(self, path: str) -> AST
    @abstractmethod
    def extract_functions(self, ast: AST) -> List[FunctionInfo]
```

#### 3.2 Go Support
**Status:** Not Started | **Priority:** Low | **Effort:** Large

- [ ] Go AST parsing
- [ ] Goroutine and channel analysis
- [ ] Interface implementation tracking
- [ ] Package dependency analysis

#### 3.3 Rust Support
**Status:** Not Started | **Priority:** Low | **Effort:** Large

- [ ] Rust AST parsing
- [ ] Trait analysis
- [ ] Lifetime visualization
- [ ] Macro expansion tracking

---

#### 4.1 Security Analysis
**Status:** Not Started | **Priority:** Low | **Effort:** Medium

- [ ] Detect common vulnerabilities
- [ ] Hardcoded secret detection
- [ ] SQL injection pattern detection
- [ ] XSS vulnerability patterns
- [ ] Integration with CVE databases

#### 4.2 Performance Profiling Integration
**Status:** Not Started | **Priority:** Low | **Effort:** Medium

- [ ] Import cProfile/py-spy results
- [ ] Annotate call graph with timing
- [ ] Hot path identification
- [ ] Memory usage visualization

#### 4.3 Custom Pattern DSL
**Status:** Not Started | **Priority:** Low | **Effort:** Large

- [ ] YAML-based pattern definitions
- [ ] Pattern marketplace/registry
- [ ] User-contributed patterns
- [ ] Pattern testing framework

**Example Pattern Definition:**
```yaml
name: database_repository
pattern:
  class:
    inherits: BaseRepository
    methods:
      - name: get_
        return_type: Model
      - name: save_
        args: [Model]
```

---

#### 5.1 API Stability
**Status:** Not Started | **Priority:** High | **Effort:** Medium

- [ ] Stable public API guarantee
- [ ] Backward compatibility policy
- [ ] Deprecation warnings
- [ ] Migration guides

#### 5.2 Enterprise Features
**Status:** Not Started | **Priority:** Low | **Effort:** Large

- [ ] SAML/SSO authentication
- [ ] Role-based access control
- [ ] Audit logging
- [ ] On-premises deployment
- [ ] SCIM user provisioning

#### 5.3 Documentation & Community
**Status:** Not Started | **Priority:** Medium | **Effort:** Ongoing

- [ ] Video tutorial series
- [ ] Interactive documentation
- [ ] Community Discord/Slack
- [ ] Monthly community calls
- [ ] Case study library

---

### Code Quality
- [ ] Achieve 90%+ test coverage
- [ ] Add property-based testing (Hypothesis)
- [ ] Implement fuzzing for parsers
- [ ] Add mutation testing

### Performance
- [ ] Profile and optimize hot paths
- [ ] Implement LRU cache for analysis results
- [ ] Add memory usage benchmarks
- [ ] Optimize graph layout algorithms

### Documentation
- [ ] API reference with auto-generation
- [ ] Architecture decision records (ADRs)
- [ ] Contributing guidelines
- [ ] Code of conduct

---

### Good First Issues
1. Add more language stopwords to NLP config
2. Improve error messages in CLI
3. Add more output format examples
4. Create tutorial notebooks

### Medium Complexity
1. Implement new pattern detector
2. Add support for additional export formats
3. Improve parallel processing stability
4. Add fuzzy matching algorithms

### Advanced
1. Implement semantic search
2. Add new language support
3. Build web UI components
4. Create IDE plugins

---

### Potential Future Directions

1. **LLM Integration**
   - Code explanation generation
   - Automatic refactoring suggestions
   - Documentation generation

2. **Machine Learning**
   - Bug prediction models
   - Code smell detection
   - Performance bottleneck prediction

3. **Visualization**
   - 3D code structure visualization
   - VR/AR code exploration
   - Haptic feedback for code review

4. **Collaboration**
   - Real-time collaborative analysis
   - Comment and annotation system
   - Code review integration

---

## Release Schedule

| Version | Target Date | Focus | Status |
|---------|-------------|-------|--------|
| v0.2.5 | Mar 2026 | TOON v2 format implementation | ✅ Done |
| v0.3.0 | Mar 2026 | Format taxonomy (map, toon, flow, context) | ✅ Done |
| v0.3.1 | Mar 2026 | CONTRACTS + DATA_TYPES enhancement (AST type inference, side-effect detection) | ✅ Done |
| v0.3.2 | Mar 2026 | networkx pipeline detection, domain grouping, entry/exit labeling | ✅ Done |
| v0.3.3 | Mar 2026 | Format quality benchmark, llm_exporter → context_exporter rename | ✅ Done |
| v0.4.0 | Mar 2026 | Rename code2flow → code2llm, structural cleanup, dead code removal | ✅ Done |
| v0.5.0 | Mar 2026 | Bug fixes, EvolutionExporter, format quality | ✅ Done |
| v0.5.1 | Mar 2026 | Structural refactoring (9 function splits, CC̄ 5.1→4.8), examples, auto-benchmark | ✅ Done |
| v0.6.0 | Q3 2026 | IDE integration, semantic code search | 📋 Planned |
| v0.7.0 | Q4 2026 | JS/TS support | 📋 Planned |
| v0.8.0 | Q1 2027 | Enterprise features | 📋 Planned |
| v1.0.0 | Q2 2027 | Stable API, mature platform | 📋 Planned |

---

## How to Contribute

1. **Pick an issue** from the roadmap
2. **Discuss** approach in GitHub issue
3. **Implement** with tests
4. **Submit PR** with documentation
5. **Iterate** based on review

## Feedback

Have ideas or suggestions? Open a GitHub issue with the `roadmap` label.
