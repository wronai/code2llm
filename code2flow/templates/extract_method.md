# Refaktoryzacja: Wyodrębnienie Metody (Extract Method)

Dla funkcji: `{{ target_function }}` w pliku `{{ source_file }}`

## Analiza Problemu
{{ reason }}

## Kontekst Techniczny
- **Metryki**: {{ metrics | dictsort | map('join', ': ') | join(', ') if metrics else 'N/A' }}
- **Mutacje Danych**: {{ mutations_context }}
- **Dostępność (Reachability)**: {{ reachability }}

## Zadanie
{{ instruction }}

## Kod do Refaktoryzacji (L{{ start_line }}-{{ end_line }})
```python
{{ source_code }}
```

## Wytyczne
1. Nie zmieniaj funkcjonalności zewnętrznej.
2. Zadbaj o poprawne przekazywanie parametrów do nowych metod.
3. Jeśli funkcja mutuje stan, zastanów się, czy nie lepiej zwrócić nowe wartości.
4. Zachowaj docstringi i typowanie (jeśli obecne).
