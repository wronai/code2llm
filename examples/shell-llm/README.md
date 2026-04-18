# code2llm + Shell-Based LLM Tools

Integrate `code2llm` output with popular shell-based LLM tools: **aider**, **llm** (Simon Willison), **sgpt**, and **fabric**.

## Prerequisites

```bash
pip install code2llm

# Install one or more LLM tools:
pip install aider-chat    # aider
pip install llm            # Simon Willison's llm
pip install shell-gpt      # sgpt
pip install fabric-ai      # fabric
```

# Generate all formats
code2llm /path/to/project -f all -o output/ --no-png

# Or specific format
code2llm /path/to/project -f evolution -o output/ --no-png
```

---

## aider — AI Pair Programming

Aider can read code2llm output as context:

```bash
# Add analysis as read-only context
aider --read output/analysis.toon --read output/evolution.toon

# Split a specific function using evolution.toon guidance
aider --message "Read output/evolution.toon and split the #1 SPLIT-FUNC target 
into smaller helpers with CC≤10. Keep all tests passing." \
  --read output/evolution.toon
```

---

# Summarize architecture
cat output/context.md | llm "Summarize this codebase architecture in 5 bullet points"

# Get refactoring advice
cat output/evolution.toon | llm "What are the top 3 most impactful refactoring steps?"

# Explain a specific module
cat output/analysis.toon | llm "Explain the health issues in this codebase"

# Compare formats
diff <(cat output/analysis.toon) <(cat output/flow.toon) | llm "What does each format reveal?"
```

# Use Claude
cat output/evolution.toon | llm -m claude-3.5-sonnet "Prioritize these refactoring tasks"

# Use GPT-4
cat output/context.md | llm -m gpt-4 "Review this architecture"

# Use local Ollama model
cat output/analysis.toon | llm -m ollama/llama3 "Summarize health issues"
```

---

# Code review from analysis
sgpt --code "Refactor based on this analysis: $(cat output/evolution.toon)"

# Architecture summary
sgpt "Summarize: $(cat output/context.md | head -100)"

# Generate tests for weak spots
sgpt --code "Write tests for the highest-CC functions: $(grep 'CC=' output/analysis.toon | head -10)"
```

---

# Summarize with fabric pattern
cat output/context.md | fabric -p summarize

# Extract action items
cat output/evolution.toon | fabric -p extract_actions

# Create improvement plan
cat output/analysis.toon | fabric -p improve_code
```

---

# benchmark_and_refactor.sh

PROJECT="/path/to/project"

# Step 1: Benchmark BEFORE
echo "=== BEFORE ==="
python benchmarks/benchmark_evolution.py "$PROJECT"

# Step 3: Run tests
python -m pytest tests/ -q

# Step 4: Benchmark AFTER
echo "=== AFTER ==="
python benchmarks/benchmark_evolution.py "$PROJECT"
```

## Comparison Matrix

| Tool | Strengths | Best For |
|------|-----------|----------|
| **aider** | Edits files in-place, git-aware | Automated refactoring |
| **llm** | Simple piping, many models | Quick analysis, summaries |
| **sgpt** | Code generation focus | Generating patches |
| **fabric** | Pattern-based prompts | Structured workflows |
