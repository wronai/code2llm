# code2llm + Claude Code

Refactoring workflow using `code2llm` analysis with **Claude Code** (Anthropic's CLI agent).

## Prerequisites

```bash
pip install code2llm
npm install -g @anthropic-ai/claude-code
```

# Analyze your project
code2llm /path/to/project -f evolution -o output/

# View refactoring priorities
cat output/evolution.toon
```

# Let Claude Code refactor the highest-impact function
claude -p "Read the following evolution analysis and refactor the #1 priority function. 
Split it into smaller helpers while keeping all tests passing.

$(cat output/evolution.toon)"
```

# refactor_loop.sh — automated refactoring with before/after tracking

for i in {1..5}; do
    echo "=== Iteration $i ==="
    
    # Benchmark before
    python -m benchmarks.benchmark_evolution /path/to/project
    
    # Get top target
    TARGET=$(grep -m1 'SPLIT-FUNC' output/evolution.toon | awk '{print $3}')
    
    if [ -z "$TARGET" ]; then
        echo "No more functions to split!"
        break
    fi
    
    echo "Splitting: $TARGET"
    
    # Claude Code refactors
    claude -p "Split the function '$TARGET' in this Python project into 
    smaller focused helper methods. Each helper should have CC≤10.
    Keep all existing tests passing.
    
    Context from evolution analysis:
    $(cat output/evolution.toon)"
    
    # Re-run tests
    python -m pytest tests/ -q
    
    # Re-benchmark
    code2llm /path/to/project -f evolution -o output/ --no-png
done
```

# Generate comprehensive analysis
code2llm /path/to/project -f all -o output/

# Ask Claude to review architecture
claude -p "Review this codebase architecture and suggest improvements.

Architecture map:
$(cat output/project.map)

Health diagnostics:
$(cat output/analysis.toon)

Data flow:
$(cat output/flow.toon)

Refactoring priorities:
$(cat output/evolution.toon)"
```

## Output Files

| File | Purpose | Best for |
|------|---------|----------|
| `evolution.toon` | Refactoring priorities | Automated splitting |
| `analysis.toon` | Health diagnostics | Code review |
| `flow.toon` | Data flow analysis | Architecture understanding |
| `context.md` | LLM narrative | Full context for Claude |
| `project.map` | Structural map | Quick orientation |

## Tips

- Start with `evolution.toon` — it ranks targets by impact
- Use `--no-png` to skip Mermaid rendering (faster)
- Pipe `context.md` for the richest context (~59% coverage)
- Run `benchmark_evolution.py` before/after to track progress
