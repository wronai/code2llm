# Streaming Analyzer Examples

This directory demonstrates how to use the new streaming analyzer functionality with different strategies and configurations.

## 📁 Sample Project Structure

```
sample_project/
├── __init__.py          # Package initialization
├── main.py              # Main application with complex logic
├── auth.py              # Authentication module
├── database.py          # Database operations
├── api.py               # API handler
└── utils.py             # Utility functions
```

The sample project contains:
- **5 Python files** with various complexity levels
- **Multiple classes** and functions
- **Complex control flow** with conditionals and loops
- **Cross-module dependencies** for call graph analysis

# Quick overview - functions and classes only
code2llm examples/streaming-analyzer/sample_project --strategy quick -v
```

**Output:**
```
Analyzing with quick strategy...
[100%] Scanned sample_project.main (priority: 150.0)
Completed in 0.1s

Analysis complete:
  - Functions: 25
  - Classes: 4
  - CFG nodes: 0
  - CFG edges: 0
```

# Standard analysis with selective CFG
code2llm examples/streaming-analyzer/sample_project --strategy standard -v
```

**Output:**
```
Analyzing with standard strategy...
[20%] Scanned sample_project.main (priority: 150.0)
[40%] Scanned sample_project.database (priority: 80.0)
[60%] Scanned sample_project.auth (priority: 60.0)
[80%] Building call graph...
[100%] Deep analysis of important files...
Completed in 0.3s

Analysis complete:
  - Functions: 25
  - Classes: 4
  - CFG nodes: 45
  - CFG edges: 67
```

# Complete analysis with full CFG
code2llm examples/streaming-analyzer/sample_project --strategy deep -v
```

**Output:**
```
Analyzing with deep strategy...
[20%] Scanned sample_project.main (priority: 150.0)
[40%] Scanned sample_project.database (priority: 80.0)
[60%] Building call graph...
[80%] Deep analysis of all files...
[100%] Completed in 0.5s

Analysis complete:
  - Functions: 25
  - Classes: 4
  - CFG nodes: 89
  - CFG edges: 134
```

# Limit memory usage to 256MB
code2llm examples/streaming-analyzer/sample_project --strategy quick --max-memory 256 -v
```

# Use streaming without specific strategy
code2llm examples/streaming-analyzer/sample_project --streaming -v
```

## 📊 Strategy Comparison

| Strategy | Functions | Classes | CFG Nodes | Time | Memory |
|----------|-----------|---------|-----------|------|--------|
| Quick | 25 | 4 | 0 | 0.1s | Low |
| Standard | 25 | 4 | 45 | 0.3s | Medium |
| Deep | 25 | 4 | 89 | 0.5s | High |

### Basic Streaming Analysis

```python
from code2llm.core.streaming_analyzer import StreamingAnalyzer, STRATEGY_QUICK

# Create analyzer with quick strategy
analyzer = StreamingAnalyzer(strategy=STRATEGY_QUICK)

# Analyze with progress tracking
for update in analyzer.analyze_streaming("examples/streaming-analyzer/sample_project"):
    if update['type'] == 'file_complete':
        print(f"✓ {update['file']}: {update['functions']} functions")
    elif update['type'] == 'complete':
        print(f"Done in {update['elapsed_seconds']:.1f}s")
```

### Custom Progress Callback

```python
from code2llm.core.streaming_analyzer import StreamingAnalyzer

def progress_callback(update):
    percentage = update.get('percentage', 0)
    message = update.get('message', '')
    print(f"[{percentage:.0f}%] {message}")

analyzer = StreamingAnalyzer()
analyzer.set_progress_callback(progress_callback)

for update in analyzer.analyze_streaming("examples/streaming-analyzer/sample_project"):
    pass  # Progress is handled by callback
```

### Incremental Analysis

```python
from code2llm.core.streaming_analyzer import IncrementalAnalyzer, StreamingAnalyzer

# Detect changed files
incremental = IncrementalAnalyzer()
changed, unchanged = incremental.get_changed_files("examples/streaming-analyzer/sample_project")

if changed:
    print(f"Analyzing {len(changed)} changed files...")
    analyzer = StreamingAnalyzer()
    for update in analyzer.analyze_streaming([f[0] for f in changed]):
        if update['type'] == 'complete':
            print(f"Incremental analysis completed in {update['elapsed_seconds']:.1f}s")
else:
    print("No changes detected")
```

### Custom Strategy

```python
from code2llm.core.streaming_analyzer import StreamingAnalyzer, ScanStrategy

# Create custom strategy
custom_strategy = ScanStrategy(
    name="custom",
    description="Custom analysis for CI/CD",
    phase_1_quick_scan=True,
    phase_2_call_graph=True,
    phase_3_deep_analysis=False,  # Skip deep analysis
    max_files_in_memory=50,
    skip_private_functions=True,
    skip_test_files=True
)

analyzer = StreamingAnalyzer(strategy=custom_strategy)
for update in analyzer.analyze_streaming("examples/streaming-analyzer/sample_project"):
    if update['type'] == 'complete':
        print(f"Custom analysis completed")
```

## 🔍 Output Analysis

The streaming analyzer generates the same output files as the standard analyzer:

- `analysis.toon` - Health diagnostics and refactoring recommendations
- `context.md` - LLM-ready context documentation
- `README.md` - Project overview and statistics

### Key Insights from Sample Project

The streaming analyzer will identify:

1. **High Priority Files:**
   - `main.py` - Entry point with complex logic (priority: 150.0)
   - `database.py` - Central data management (priority: 80.0)

2. **Complex Functions:**
   - `Application.process_request()` - Multiple conditional branches
   - `DatabaseConnection._log_action()` - Complex data manipulation

3. **Call Graph Patterns:**
   - Main → Auth → Database flow
   - API handler dependencies
   - Utility function usage patterns

# Use quick strategy for initial exploration
code2llm /large/project --strategy quick

# Follow with standard strategy for detailed analysis
code2llm /large/project --strategy standard
```

# Use incremental analysis for fast CI
incremental = IncrementalAnalyzer()
changed, _ = incremental.get_changed_files(".")
if changed:
    analyzer = StreamingAnalyzer(strategy=STRATEGY_QUICK)
    # Analyze only changed files
```

# Limit memory usage
code2llm /project --strategy quick --max-memory 256
```

## 📈 Performance Tips

1. **Start with `quick` strategy** for overview
2. **Use `standard` for most use cases**
3. **Reserve `deep` for critical analysis**
4. **Enable verbose mode** to monitor progress
5. **Set memory limits** for constrained environments
6. **Use incremental analysis** for frequent runs
