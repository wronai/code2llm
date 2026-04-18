# Refaktoryzacja: Przeniesienie Metody (Move Method)

Dla metody: `{{ target_function }}` z modułu `{{ source_module }}` do `{{ target_module }}`

## Kontekst Couplingu
- {{ foreign_mutations_context }}
- **Zależności Obce**: {{ foreign_mutations }}
- **Zależności Mutowane**: {{ dependencies }}

## Kod do Przeniesienia
```python
{{ source_code }}
```

## Wytyczne
1. Przenieś logikę do docelowego modułu/klasy.
2. W miejscu starej metody możesz zostawić delegację (jeśli konieczne) lub całkowicie ją usunąć, aktualizując wywołania.
3. Zadbaj o poprawne importy w nowym miejscu.
4. Upewnij się, że testy jednostkowe nadal pokrywają tę logikę.
