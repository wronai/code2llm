# Prompt: Implementacja grupowych eksportów sumd i sumr

## Cel
Rozszerzenie `code2llm` o możliwość generowania **tylko wybranych grup plików** (`sumd` lub `sumr`) oraz automatyczne generowanie **list plików (manifestów)** dla każdej grupy przed ich dołączeniem.

## Definicje

### `sumd` - Summary Documentation
**Cel**: Pliki do dokumentacji i zrozumienia architektury projektu.

**Pliki wchodzące w skład `sumd`**:
- `context.md` — narracja LLM, podsumowanie architektury
- `README.md` — dokumentacja projektu
- `project.toon.yaml` — kompaktowy przegląd projektu

### `sumr` - Summary Refactoring
**Cel**: Pliki do analizy i planowania refaktoryzacji.

**Pliki wchodzące w skład `sumr`**:
- `analysis.toon.yaml` (lub `analysis.toon`) — metryki złożoności, god modules, coupling
- `evolution.toon.yaml` — kolejka refaktoryzacji, priorytety
- `map.toon.yaml` — mapa strukturalna, importy/eksporty, sygnatury

## Wymagania funkcjonalne

### 1. Nowe opcje formatu (`-f`, `--format`)
Dodać obsługę nowych wartości formatu:
- `sumd` — generuje tylko pliki grupy dokumentacyjnej
- `sumr` — generuje tylko pliki grupy refaktoryzacyjnej
- `sumd+sumr` lub `sumall` — generuje obie grupy (ekwiwalent obecnego `all` bez niektórych plików)

### 2. Automatyczna lista plików (manifest)
Przed wygenerowaniem plików dla danej grupy, code2llm powinien:
1. Przeanalizować co będzie generowane
2. Wygenerować **listę plików** dla danej grupy w formacie:
   - `sumd_files.txt` — lista plików sumd
   - `sumr_files.txt` — lista plików sumr

Format listy:
```
# sumd files for project: {project_name}
# Generated: {timestamp}
# Total: {count} files

{output_dir}/context.md [{size}]
{output_dir}/README.md [{size}]
{output_dir}/project.toon.yaml [{size}]
```

### 3. Świeża generacja
**Każde uruchomienie z flagą `sumd` lub `sumr` musi**:
- Wygenerować pliki na nowo (ignorować cache)
- Wygenerować aktualną listę plików
- Nie używać starych plików z poprzednich uruchomień

### 4. Integracja z prompt.txt
Gdy generowane są `sumd` lub `sumr`, `prompt.txt` powinien:
- Zawierać sekcję "Documentation Files (sumd)" lub "Refactoring Files (sumr)"
- Odnosić się do odpowiedniej listy plików
- Wyraźnie rozdzielać te dwie grupy

## Pliki do modyfikacji

### 1. `code2llm/cli_parser.py`
Dodać nowe opcje formatu w `create_parser()`:
```python
# W opisie formatów:
sumd         — Documentation files only (context.md, README.md, project.toon.yaml)
sumr         — Refactoring files only (analysis.toon, evolution.toon.yaml, map.toon.yaml)
sumall       — Both sumd and sumr groups
```

### 2. `code2llm/cli_exports/formats.py`
Dodać nowe funkcje eksportu:
```python
def _export_sumd(args, result, output_dir: Path):
    """Export documentation group (sumd) files."""
    # 1. Generate fresh files
    # 2. Generate sumd_files.txt manifest
    pass

def _export_sumr(args, result, output_dir: Path):
    """Export refactoring group (sumr) files."""
    # 1. Generate fresh files
    # 2. Generate sumr_files.txt manifest
    pass
```

### 3. `code2llm/cli_exports/prompt.py`
Zmodyfikować `_MAIN_FILES` i dodać obsługę grup:
```python
_SUMD_FILES = [
    ('context.md', 'LLM narrative - architecture summary and project context', ('context.md',)),
    ('README.md', 'Generated documentation - overview and usage guide', ('README.md',)),
    ('project.toon.yaml', 'Compact project overview - generated from project.yaml data', ('project.toon.yaml',)),
]

_SUMR_FILES = [
    ('analysis.toon.yaml', 'Health diagnostics - complexity metrics, god modules, coupling issues', ('analysis.toon', 'analysis.toon.yaml')),
    ('evolution.toon.yaml', 'Refactoring queue - ranked actions by impact/effort', ('evolution.toon.yaml',)),
    ('map.toon.yaml', 'Structural map - files, sizes, imports, exports, signatures', ('map.toon.yaml',)),
]
```

Dodać funkcję generującą manifest:
```python
def _generate_file_manifest(output_dir: Path, group_name: str, files: list) -> Path:
    """Generate {group}_files.txt manifest listing all files in group."""
    pass
```

### 4. Główna logika w `cli.py` lub `__main__.py`
Dodać routing dla nowych formatów:
```python
formats = [f.strip() for f in args.format.split(',')]

if 'sumd' in formats:
    _export_sumd(args, result, output_dir)
if 'sumr' in formats:
    _export_sumr(args, result, output_dir)
if 'sumall' in formats:
    _export_sumd(args, result, output_dir)
    _export_sumr(args, result, output_dir)
```

## Przykłady użycia (CLI)

```bash
# Generuj tylko pliki dokumentacyjne
code2llm ./ -f sumd -o ./docs

# Generuj tylko pliki do refaktoryzacji
code2llm ./ -f sumr -o ./refactor

# Generuj obie grupy z osobnymi manifestami
code2llm ./ -f sumall -o ./project

# Kombinacja z innymi formatami
code2llm ./ -f sumr,mermaid -o ./analysis

# Standardowe 'all' pozostaje bez zmian (generuje wszystko + prompt.txt)
code2llm ./ -f all -o ./project
```

## Struktura wyjściowa

Po uruchomieniu `code2llm ./ -f sumall -o ./output`:
```
./output/
├── sumd_files.txt          # Lista plików dokumentacyjnych
├── sumr_files.txt          # Lista plików refaktoryzacyjnych
├── context.md              # [sumd]
├── README.md               # [sumd]
├── project.toon.yaml       # [sumd]
├── analysis.toon.yaml      # [sumr]
├── evolution.toon.yaml     # [sumr]
├── map.toon.yaml           # [sumr]
└── prompt.txt              # Generowany jeśli format zawiera 'all' lub 'code2logic'
```

## Edge Cases

1. **Brak plików do wygenerowania** — manifest powinien zawierać komentarz `# No files generated`
2. **Częściowa generacja** — jeśli któryś plik nie może być wygenerowany, powinien być oznaczony w manifeście jako `[MISSING]`
3. **Nadpisywanie** — zawsze generuj świeże pliki i manifesty (overwrite=True)
4. **Chunked mode** — w trybie chunkowania, manifesty powinny być generowane dla każdego chunka osobno

## Kryteria akceptacji

- [ ] `code2llm ./ -f sumd` generuje tylko `context.md`, `README.md`, `project.toon.yaml` + `sumd_files.txt`
- [ ] `code2llm ./ -f sumr` generuje tylko `analysis.toon.yaml`, `evolution.toon.yaml`, `map.toon.yaml` + `sumr_files.txt`
- [ ] Manifesty zawierają pełne ścieżki, rozmiary i timestamp
- [ ] Każde uruchomienie generuje świeże pliki (nie używa cache dla tych grup)
- [ ] `prompt.txt` (gdy generowany) wyraźnie oznacza które pliki należą do sumd/sumr
- [ ] Wszystkie istniejące testy przechodzą
- [ ] Nowe testy dla grup sumd/sumr są dodane i przechodzą
