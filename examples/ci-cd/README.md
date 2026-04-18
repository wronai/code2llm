# code2llm + CI/CD Pipeline

Automatyczne sprawdzanie jakości kodu w CI/CD z `code2llm`.

# .github/workflows/code-quality.yml
name: Code Quality Check

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install code2llm
        run: pip install code2llm

      - name: Run analysis
        run: code2llm . -f evolution -o /tmp/analysis --no-png

      - name: Check max-CC threshold
        run: |
          MAX_CC=$(grep "max-CC:" /tmp/analysis/evolution.toon | grep -oP '\d+' | head -1)
          echo "max-CC = $MAX_CC"
          if [ "$MAX_CC" -gt 30 ]; then
            echo "::error::max-CC=$MAX_CC exceeds threshold 30"
            cat /tmp/analysis/evolution.toon
            exit 1
          fi

      - name: Check god modules
        run: |
          GOD=$(grep "god-modules:" /tmp/analysis/evolution.toon | grep -oP '\d+' | head -1)
          echo "god-modules = $GOD"
          if [ "$GOD" -gt 5 ]; then
            echo "::warning::$GOD god modules detected"
          fi

      - name: Upload analysis
        uses: actions/upload-artifact@v4
        with:
          name: code-analysis
          path: /tmp/analysis/
```

# .git/hooks/pre-commit

echo "Running code2llm quality check..."
code2llm . -f evolution -o /tmp/pre-commit-analysis --no-png 2>/dev/null

MAX_CC=$(grep "max-CC:" /tmp/pre-commit-analysis/evolution.toon 2>/dev/null | grep -oP '\d+' | head -1)

if [ -n "$MAX_CC" ] && [ "$MAX_CC" -gt 40 ]; then
    echo "❌ max-CC=$MAX_CC — refactoring needed before commit"
    grep "NEXT\[" /tmp/pre-commit-analysis/evolution.toon -A 5
    exit 1
fi

echo "✅ Code quality OK (max-CC=${MAX_CC:-unknown})"
rm -rf /tmp/pre-commit-analysis
```

## Makefile target

```makefile
.PHONY: quality benchmark

quality:
	code2llm . -f evolution -o /tmp/quality --no-png
	@echo "=== Top refactoring targets ==="
	@grep "SPLIT" /tmp/quality/evolution.toon | head -5
	@echo "=== Metrics ==="
	@grep "CC̄\|max-CC\|high-CC\|god-modules" /tmp/quality/evolution.toon

benchmark:
	python benchmarks/benchmark_evolution.py .
```
