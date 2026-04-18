## 📁 Generated Files Overview

When you run `code2llm ./ -f all`, the following files are created:

### 🎯 Core Analysis Files

| File | Format | Purpose | Key Insights |
|------|--------|---------|--------------|
| `analysis.toon` | **TOON** | **🔥 Health diagnostics** - Complexity, god modules, coupling | 52 critical functions, 0 god modules |
| `evolution.toon` | **TOON** | **📋 Refactoring queue** - Prioritized improvements | 0 refactoring actions needed |
| `project.toon` | **TOON** | **🧠 Project logic** - Compact module view from code2logic | Generated via code2logic integration |

# LLM-ready context only
code2llm ./ -f context
```

# Fast analysis for large projects
code2llm ./ -f toon --strategy quick

# Memory-limited analysis
code2llm ./ -f all --max-memory 500

# Skip PNG generation (faster)
code2llm ./ -f all --no-png
```

# Get refactoring recommendations
code2llm ./ -f evolution

# Focus on specific code smells
code2llm ./ -f toon --refactor --smell god_function

# Data flow analysis
code2llm ./ -f flow --data-flow
```

# View health issues
cat analysis.toon | head -30

# Check refactoring priorities
grep "REFACTOR" analysis.toon
```

### `evolution.toon` - Refactoring Queue
**Purpose**: Step-by-step refactoring plan
**Key sections**:
- **NEXT**: Immediate actions to take
- **RISKS**: Potential breaking changes
- **METRICS-TARGET**: Success criteria

**Example usage**:
```bash
# Track progress
grep "NEXT" evolution.toon
```

# Find data pipelines
grep "PIPELINES" flow.toon

# Identify side effects
grep "SIDE_EFFECTS" flow.toon
```

# See project structure
cat map.toon | head -50

# Find public APIs
grep "SIGNATURES" map.toon
```

# View compact project structure
cat project.toon | head -30

# Find largest files
grep -E "^  .*[0-9]{3,}$" project.toon | sort -t',' -k2 -n -r | head -10
```

# Copy to clipboard and paste into ChatGPT/Claude
cat prompt.txt | pbcopy  # macOS
cat prompt.txt | xclip -sel clip  # Linux
```

# Copy to clipboard for LLM
cat context.md | pbcopy  # macOS
cat context.md | xclip -sel clip  # Linux

# View diagrams
open flow.png  # macOS
xdg-open flow.png  # Linux

# Quick health check
code2llm ./ -f toon
cat analysis.toon | grep -E "(HEALTH|REFACTOR)"
```

# Get refactoring queue
code2llm ./ -f evolution
cat evolution.toon

# Focus on specific issues
code2llm ./ -f toon --refactor --smell god_function
```

# Generate context for AI
code2llm ./ -f context
cat context.md

# Generate all docs for team
code2llm ./ -f all -o ./docs/

# Create visual diagrams
open docs/flow.png
```

### Module Health
- **GOD Module**: Too large (>500 lines, >20 methods)
- **HUB**: High fan-out (calls many modules)
- **FAN-IN**: High incoming dependencies
- **CYCLES**: Circular dependencies

### Data Flow Indicators
- **PIPELINE**: Sequential data processing
- **CONTRACT**: Clear input/output specification
- **SIDE_EFFECT**: External state modification

# Analyze code quality in CI
code2llm ./ -f toon -o ./analysis
if grep -q "🔴 GOD" ./analysis/analysis.toon; then
    echo "❌ God modules detected"
    exit 1
fi
```

# .git/hooks/pre-commit
code2llm ./ -f toon -o ./temp_analysis
if grep -q "🔴" ./temp_analysis/analysis.toon; then
    echo "⚠️  Critical issues found. Review before committing."
fi
rm -rf ./temp_analysis
```

# Generate docs for README
code2llm ./ -f context -o ./docs/
echo "## Architecture" >> README.md
cat docs/context.md >> README.md
```

# Deep analysis with all insights
code2llm ./ -m hybrid -f all --max-depth 15 -v

# Performance-optimized
code2llm ./ -m static -f toon --strategy quick

# Refactoring-focused
code2llm ./ -f toon,evolution --refactor
```

# Separate output directories
code2llm ./ -f all -o ./analysis-$(date +%Y%m%d)

# Split YAML into multiple files
code2llm ./ -f yaml --split-output

