# code2flow

**Python Code Flow Analysis Tool** - Static analysis for control flow graphs (CFG), data flow graphs (DFG), and call graph extraction with optimized TOON format.

![img.png](img.png)

## 🚀 New: TOON Format

**TOON** is the new default output format - optimized for performance and readability:

- **🎯 10x smaller** than standard YAML (204KB vs 2.5MB)
- **⚡ Faster processing** with intelligent sorting
- **📊 Enhanced insights** with complexity analysis
- **🔍 Smart recommendations** for refactoring
- **📋 Complete validation** with built-in testing

```bash
# Default: TOON format only
code2flow /path/to/project

# Generate all formats
code2flow /path/to/project -f all

# TOON + YAML (for comparison)
code2flow /path/to/project -f toon,yaml
```

## Performance Optimization

For large projects (>1000 functions), use **Fast Mode**:

```bash
# Ultra-fast analysis (5-10x faster)
code2flow /path/to/project --fast

# Custom performance settings
code2flow /path/to/project \
    --parallel-workers 8 \
    --max-depth 3 \
    --skip-data-flow \
    --cache-dir ./.cache
```

### Performance Tips

| Technique | Speedup | Use Case |
|-----------|---------|----------|
| `--fast` mode | 5-10x | Initial exploration |
| Parallel workers | 2-4x | Multi-core machines |
| Caching | 3-5x | Repeated analysis |
| Depth limiting | 2-3x | Large codebases |
| Skip private methods | 1.5-2x | Public API analysis |

### Benchmarks

| Project Size | Functions | Time (fast) | Time (full) |
|--------------|-----------|-------------|-------------|
| Small (<100) | ~50 | 0.5s | 2s |
| Medium (1K) | ~500 | 3s | 15s |
| Large (10K) | ~2000 | 15s | 120s |

## Features

- **🎯 TOON Format**: Optimized compact output (default)
- **Control Flow Graph (CFG)**: Extract execution paths from Python AST
- **Data Flow Graph (DFG)**: Track variable definitions and dependencies  
- **Call Graph Analysis**: Map function calls and dependencies
- **Pattern Detection**: Identify design patterns and code smells
- **Multiple Output Formats**: TOON, YAML, JSON, Mermaid diagrams, PNG visualizations
- **LLM-Ready Output**: Generate prompts for reverse engineering
- **Smart Validation**: Built-in format validation and testing

## Installation

```bash
# Install from source
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

## Quick Start

```bash
# Analyze a Python project (default: TOON format)
code2flow /path/to/project

# With verbose output
code2flow /path/to/project -v

# Generate all formats
code2flow /path/to/project -f all

# Use different analysis modes
code2flow /path/to/project -m static    # Fast static analysis only
code2flow /path/to/project -m hybrid     # Combined analysis (default)
```

## Usage

### Output Formats

```bash
# Default: TOON format only
code2flow /path/to/project

# All formats (toon,yaml,json,mermaid,png)
code2flow /path/to/project -f all

# Custom combinations
code2flow /path/to/project -f toon,yaml
code2flow /path/to/project -f json,png
code2flow /path/to/project -f mermaid,png
```

### Analysis Modes

```bash
# Static analysis only (fastest)
code2flow /path/to/project -m static

# Dynamic analysis with tracing
code2flow /path/to/project -m dynamic

# Hybrid analysis (recommended)
code2flow /path/to/project -m hybrid

# Behavioral pattern focus
code2flow /path/to/project -m behavioral

# Reverse engineering ready
code2flow /path/to/project -m reverse
```

### Custom Output

```bash
code2flow /path/to/project -o my_analysis
```

## Output Files

| File | Description | Size |
|------|-------------|------|
| `analysis.toon` | **🎯 Optimized TOON format** (default) | ~200KB |
| `analysis.yaml` | Complete structured analysis data | ~2.5MB |
| `analysis.json` | JSON format for programmatic use | ~2.6MB |
| `flow.mmd` | Full Mermaid flowchart (all nodes) | ~9KB |
| `compact_flow.mmd` | Compact flowchart - deduplicated nodes | ~9KB |
| `calls.mmd` | Function call graph | ~9KB |
| `cfg.png` | Control flow visualization | ~7MB |
| `call_graph.png` | Call graph visualization | ~3.7MB |
| `llm_prompt.md` | LLM-ready analysis summary | ~35KB |

## 🎯 TOON Format Structure

The TOON format provides optimized, human-readable output:

```yaml
meta:
  project: /path/to/project
  mode: hybrid
  generated: '2026-02-28T22:13:30'
  version: '2.0'

stats:
  files_processed: 42
  functions_found: 443
  classes_found: 77
  nodes_created: 2734
  edges_created: 3223

functions:
  - name: export
    module: code2flow.exporters.base.LLMPromptExporter
    complexity: 45.0
    tier: critical
    nodes: 52
    has_loops: true
    has_conditions: true
    has_returns: false

insights:
  complexity_summary:
    critical_functions: 115
    high_complexity: 64
    avg_complexity: 3.17
  recommendations:
    - type: complexity
      priority: high
      message: "Refactor 115 critical functions"
```

### Complexity Tiers

- **🔴 Critical** (≥5.0): Immediate refactoring needed
- **🟠 High** (≥3.0): Consider refactoring
- **🟡 Medium** (≥1.5): Monitor complexity
- **🟢 Low** (>0): Acceptable complexity
- **⚪ Basic** (0): Simple functions

## Validation & Testing

Built-in validation ensures output quality:

```bash
# Validate TOON format
python validate_toon.py analysis.toon

# Compare TOON vs YAML
python validate_toon.py analysis.yaml analysis.toon

# Run comprehensive tests
bash project.sh
```

### Test Results

- **✅ Functions**: 100% data consistency (443/443)
- **✅ Statistics**: Perfect correlation
- **✅ Structure**: All required sections present
- **✅ Insights**: Actionable recommendations generated

## Understanding the Output

### LLM Prompt Structure
The generated prompt includes:
- System overview with metrics
- Call graph structure
- Behavioral patterns with confidence scores
- Data flow insights
- State machine definitions
- Reverse engineering guidelines

### Behavioral Patterns
Each pattern includes:
- **Name**: Descriptive identifier
- **Type**: sequential, conditional, iterative, recursive, state_machine
- **Entry/Exit points**: Key functions
- **Decision points**: Conditional logic locations
- **Data transformations**: Variable dependencies
- **Confidence**: Pattern detection certainty

### Reverse Engineering Guidelines
The analysis provides specific guidance for:
1. Preserving call graph structure
2. Implementing identified patterns
3. Maintaining data dependencies
4. Recreating state machines
5. Preserving decision logic

## Advanced Features

### State Machine Detection
Automatically identifies:
- State variables
- Transition methods
- Source and destination states
- State machine hierarchy

### Data Flow Tracking
Maps:
- Variable dependencies
- Data transformations
- Information flow paths
- Side effects

### Dynamic Tracing
When using dynamic mode:
- Function entry/exit timing
- Call stack reconstruction
- Exception tracking
- Performance profiling

## Integration with LLMs

The generated `llm_prompt.md` is designed to be:
- **Comprehensive**: Contains all necessary system information
- **Structured**: Organized for easy parsing
- **Actionable**: Includes specific implementation guidance
- **Language-agnostic**: Describes behavior, not implementation

Example usage with an LLM:
```
"Based on the TOON analysis provided, implement this system in Go,
preserving all behavioral patterns and data flow characteristics."
```

## Format Comparison

| Feature | TOON | YAML | JSON |
|---------|------|------|------|
| **Size** | 🎯 200KB | 2.5MB | 2.6MB |
| **Readability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Processing Speed** | ⚡ Fast | 🐌 Slow | 🐌 Slow |
| **Human-Friendly** | ✅ Yes | ❌ No | ❌ No |
| **Machine-Readable** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Insights** | ✅ Built-in | ❌ No | ❌ No |

## Limitations

- Dynamic analysis requires test files
- Complex inheritance hierarchies may need manual review
- External library calls are treated as black boxes
- Runtime reflection and metaprogramming not fully captured

## Contributing

The analyzer is designed to be extensible. Key areas for enhancement:
- Additional pattern types
- Language-specific optimizations
- Improved visualization
- Real-time analysis mode
- TOON format enhancements

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

## Author

Created by **Tom Sapletta** - [tom@sapletta.com](mailto:tom@sapletta.com)
