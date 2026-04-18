# code2llm — Przykłady użycia CLI

Kompletna dokumentacja formatów i komend code2llm.

## Instalacja

```bash
pip install -e .
# lub
pip install code2llm
```

## Formaty wyjściowe

| Format | Plik | Cel | Komenda |
|--------|------|-----|---------|
| `toon` | `analysis.toon` | Diagnostyka zdrowia kodu | `code2llm . -f toon` |
| `flow` | `flow.toon` | Przepływ danych, pipelines | `code2llm . -f flow` |
| `map` | `project.map` | Mapa strukturalna | `code2llm . -f map` |
| `context` | `context.md` | Narracja dla LLM | `code2llm . -f context` |
| `evolution` | `evolution.toon` | Kolejka refaktoryzacji | `code2llm . -f evolution` |
| `yaml` | `analysis.yaml` | Strukturalne dane | `code2llm . -f yaml` |
| `json` | `analysis.json` | Dane maszynowe | `code2llm . -f json` |
| `mermaid` | `flow.mmd` etc. | Diagramy | `code2llm . -f mermaid` |
| `all` | Wszystkie powyższe | Pełna analiza | `code2llm . -f all` |

---

### 1. Szybka analiza zdrowia kodu (domyślne)
```bash
code2llm /path/to/project
### 2. Generowanie wszystkich formatów
```bash
code2llm /path/to/project -f all -o output/
### 3. Metryki ewolucji (co refaktoryzować najpierw?)
```bash
code2llm /path/to/project -f evolution -o output/ --no-png
cat output/evolution.toon
```

Wynik:
```
NEXT[10] (ranked by impact):
  [1] !! SPLIT-FUNC    main  CC=61  fan=44
      WHY: CC=61 exceeds 15
      EFFORT: ~1h  IMPACT: 2684
```

### 4. Diagnostyka zdrowia
```bash
code2llm . -f toon -o output/
grep "^HEALTH" output/analysis.toon
grep "🔴" output/analysis.toon   # god modules
grep "🟡 CC" output/analysis.toon # high complexity
```

### 5. Mapa strukturalna (szybki przegląd)
```bash
code2llm . -f map -o output/
cat output/project.map
```

### 6. Kontekst dla LLM (do wklejenia w prompt)
```bash
code2llm . -f context -o output/
cat output/context.md | pbcopy   # macOS
cat output/context.md | xclip    # Linux
```

### 7. Analiza przepływu danych
```bash
code2llm . -f flow -o output/
cat output/flow.toon
### Fast mode (5-10x szybciej)
```bash
code2llm /path/to/project --fast
```

### Streaming (małe zużycie RAM)
```bash
code2llm /path/to/project --streaming
```

### Verbose (szczegółowy output)
```bash
code2llm /path/to/project -f all -v
```

### Bez PNG (szybciej, nie wymaga mmdc)
```bash
code2llm /path/to/project -f all --no-png
```

---

# 1. Benchmark BEFORE
python benchmarks/benchmark_evolution.py /path/to/project

# 3. Benchmark AFTER (porównanie automatyczne)
python benchmarks/benchmark_evolution.py /path/to/project
```

Wynik:
```
============================================================
  CODE2LLM EVOLUTION BENCHMARK
============================================================

  Metric                   Before      After      Delta
  ---------------------- ---------- ---------- ----------
  CC̄ (average)                 5.1        4.8     -0.3 ↓
  max-CC                        63         35      -28 ↓
  high-CC (≥15)                 27         19       -8 ↓
```

---

# ci_quality_check.sh

code2llm ./src -f evolution -o /tmp/analysis --no-png

# Sprawdź max-CC
MAX_CC=$(grep "max-CC:" /tmp/analysis/evolution.toon | grep -oP '\d+' | head -1)
if [ "$MAX_CC" -gt 30 ]; then
    echo "❌ max-CC=$MAX_CC exceeds threshold 30"
    exit 1
fi
echo "✅ max-CC=$MAX_CC — code quality OK"
```

---

## Przykłady integracji z LLM

Patrz osobne projekty:
- [Claude Code](../claude-code/README.md) — automatyczna refaktoryzacja
- [Shell LLM](../shell-llm/README.md) — aider, llm, sgpt, fabric
- [LiteLLM](../litellm/README.md) — Python skrypt z API
