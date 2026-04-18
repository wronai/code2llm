# code2llm — DevOps Workflow

Praktyczne skrypty bash do codziennej pracy z kodem: generowanie raportów, metryki w commitach, automatyczne aktualizacje README.

# Jednolinijkowa analiza — od razu widać zdrowie projektu
code2llm . -f evolution -o /tmp/q --no-png && head -20 /tmp/q/evolution.toon
```

---

## 1. Raport metryk do README

Automatyczne generowanie sekcji metryk do README:

```bash
#!/bin/bash
# Generuje metryki i wstawia do README.md

set -e
PROJECT="${1:-.}"
OUTPUT="/tmp/code2llm_metrics"

# Generuj analizę
code2llm "$PROJECT" -f evolution -o "$OUTPUT" --no-png 2>/dev/null

# Parsuj metryki
CC_AVG=$(grep "CC̄:" "$OUTPUT/evolution.toon" | grep -oP '[\d.]+' | head -1)
MAX_CC=$(grep "max-CC:" "$OUTPUT/evolution.toon" | grep -oP '\d+' | head -1)
HIGH_CC=$(grep "high-CC" "$OUTPUT/evolution.toon" | grep -oP '\d+' | head -1)
GOD=$(grep "god-modules:" "$OUTPUT/evolution.toon" | grep -oP '\d+' | head -1)
FUNCS=$(grep -oP '\d+ func' "$OUTPUT/evolution.toon" | grep -oP '\d+' | head -1)
DATE=$(date +%Y-%m-%d)

# Generuj badge-style sekcję
cat > /tmp/metrics_section.md <<EOF
## 📊 Code Quality Metrics

| Metric | Value | Status |
|--------|-------|--------|
| CC̄ (avg complexity) | **${CC_AVG:-?}** | $([ "${CC_AVG%.*}" -le 5 ] 2>/dev/null && echo "✅" || echo "⚠️") |
| max-CC | **${MAX_CC:-?}** | $([ "${MAX_CC:-99}" -le 20 ] && echo "✅" || echo "⚠️") |
| High-CC functions (≥15) | **${HIGH_CC:-?}** | $([ "${HIGH_CC:-99}" -le 10 ] && echo "✅" || echo "⚠️") |
| God modules | **${GOD:-?}** | $([ "${GOD:-99}" -eq 0 ] && echo "✅" || echo "⚠️") |
| Total functions | **${FUNCS:-?}** | — |

*Last updated: ${DATE} by code2llm v0.5.1*
EOF

# Wstaw do README (między markerami)
if grep -q "<!-- METRICS_START -->" README.md 2>/dev/null; then
    sed -i '/<!-- METRICS_START -->/,/<!-- METRICS_END -->/!b;//!d;/<!-- METRICS_START -->/r /tmp/metrics_section.md' README.md
    echo "✅ README.md metrics updated"
else
    echo "⚠ Add markers to README.md:"
    echo "  <!-- METRICS_START -->"
    echo "  <!-- METRICS_END -->"
    echo ""
    echo "Generated metrics:"
    cat /tmp/metrics_section.md
fi
```

### Użycie:
```bash
chmod +x scripts/update_readme_metrics.sh
./scripts/update_readme_metrics.sh .
```

---

## 2. Metryki w commit message

Automatyczne dodawanie metryk do commit message:

```bash
#!/bin/bash
# Commituje zmiany z metrykami code2llm w wiadomości

set -e
MSG="${1:-refactor: improve code quality}"
OUTPUT="/tmp/code2llm_commit"

# Generuj metryki
code2llm . -f evolution -o "$OUTPUT" --no-png 2>/dev/null

CC_AVG=$(grep "CC̄:" "$OUTPUT/evolution.toon" | grep -oP '[\d.]+' | head -1)
MAX_CC=$(grep "max-CC:" "$OUTPUT/evolution.toon" | grep -oP '\d+' | head -1)
HIGH_CC=$(grep "high-CC" "$OUTPUT/evolution.toon" | grep -oP '\d+' | head -1)

# Commit z metrykami
git add -A
git commit -m "$MSG

code2llm metrics:
  CC̄=${CC_AVG:-?} | max-CC=${MAX_CC:-?} | high-CC(≥15)=${HIGH_CC:-?}"

echo "✅ Committed with metrics"
```

### Użycie:
```bash
./scripts/commit_with_metrics.sh "refactor: split main() into helpers"
```

Wynik w `git log`:
```
refactor: split main() into helpers

code2llm metrics:
  CC̄=4.8 | max-CC=35 | high-CC(≥15)=19
```

---

# Przed pracą — szybki przegląd co polepszać
code2llm . -f evolution -o /tmp/q --no-png
grep "NEXT\[" /tmp/q/evolution.toon -A 3

# Po pracy — porównanie before/after
python benchmarks/benchmark_evolution.py .

# Raport do README
./scripts/update_readme_metrics.sh .

# Commit z metrykami
./scripts/commit_with_metrics.sh "refactor: split _render_coupling CC=28→14"
```

---

## 4. Makefile — all-in-one

```makefile
.PHONY: metrics quality benchmark report commit-metrics

# Szybki podgląd zdrowia
metrics:
	@code2llm . -f evolution -o /tmp/q --no-png 2>/dev/null
	@echo "=== NEXT targets ==="
	@grep "SPLIT" /tmp/q/evolution.toon | head -5
	@echo "=== Metrics ==="
	@grep "CC̄\|max-CC\|high-CC\|god-modules" /tmp/q/evolution.toon

# Pełny benchmark z historią
benchmark:
	python benchmarks/benchmark_evolution.py .

# Aktualizuj README
report:
	./scripts/update_readme_metrics.sh .

# Commit z metrykami
commit-metrics:
	./scripts/commit_with_metrics.sh "$(MSG)"
```

Użycie:
```bash
make metrics           # szybki check
make benchmark         # before/after
make report            # README update
make commit-metrics MSG="refactor: split god modules"
```

---

# Automatycznie dopisuje metryki do KAŻDEGO commita

OUTPUT="/tmp/code2llm_hook"
code2llm . -f evolution -o "$OUTPUT" --no-png 2>/dev/null

if [ -f "$OUTPUT/evolution.toon" ]; then
    CC_AVG=$(grep "CC̄:" "$OUTPUT/evolution.toon" | grep -oP '[\d.]+' | head -1)
    MAX_CC=$(grep "max-CC:" "$OUTPUT/evolution.toon" | grep -oP '\d+' | head -1)
    echo "" >> "$1"
    echo "metrics: CC̄=${CC_AVG} max-CC=${MAX_CC}" >> "$1"
fi
```

Instalacja:
```bash
cp scripts/prepare-commit-msg .git/hooks/
chmod +x .git/hooks/prepare-commit-msg
```

---

# Porównaj metryki między dwoma branchami

BRANCH1="${1:-main}"
BRANCH2="${2:-HEAD}"

echo "=== $BRANCH1 ==="
git stash
git checkout "$BRANCH1" 2>/dev/null
code2llm . -f evolution -o /tmp/branch1 --no-png 2>/dev/null
grep "CC̄\|max-CC\|high-CC" /tmp/branch1/evolution.toon

echo ""
echo "=== $BRANCH2 ==="
git checkout "$BRANCH2" 2>/dev/null
git stash pop 2>/dev/null
code2llm . -f evolution -o /tmp/branch2 --no-png 2>/dev/null
grep "CC̄\|max-CC\|high-CC" /tmp/branch2/evolution.toon
```
