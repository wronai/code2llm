"""Funkcje raportowania wyników benchmarku.

Zawiera funkcje do formatowanego wyświetlania wyników benchmarku
oraz zapisywania raportów JSON.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from .benchmark_constants import KNOWN_PROBLEMS, KNOWN_PIPELINES
from .format_evaluator import FormatScore


def _print_header() -> None:
    """Wydrukuj nagłówek sekcji wyników."""
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)


def _print_scores_table(scores: Dict[str, FormatScore]) -> None:
    """Wydrukuj tabelę wyników formatów."""
    # Nagłówek
    print(f"\n{'Format':<18} {'Problems':>9} {'Pipelines':>10} {'Hub Types':>10} {'Structure':>10} {'TOTAL':>8} {'Size':>8}")
    print("─" * 75)

    sorted_scores = sorted(scores.values(), key=lambda s: s.total_score, reverse=True)
    medals = ["🥇", "🥈", "🥉", "  "]

    for i, s in enumerate(sorted_scores):
        medal = medals[min(i, 3)]
        size_str = f"{s.size_bytes:,}" if s.size_bytes else "N/A"
        print(f"{medal} {s.name:<15} {s.problem_score:>8.0f}% {s.pipeline_score:>9.0f}%"
              f" {s.hub_type_score:>9.0f}% {s.structural_score:>9.0f}%"
              f" {s.total_score:>7.1f}% {size_str:>8}")


def _print_problems_detail(scores: Dict[str, FormatScore]) -> None:
    """Wydrukuj szczegóły wykrytych problemów."""
    sorted_scores = sorted(scores.values(), key=lambda s: s.total_score, reverse=True)

    print(f"\n{'Problem':<20}", end="")
    for s in sorted_scores:
        print(f" {s.name:^16}", end="")
    print()
    print("─" * (20 + 17 * len(sorted_scores)))

    for problem_key, description in KNOWN_PROBLEMS.items():
        label = problem_key.replace("_", " ")[:19]
        print(f"{label:<20}", end="")
        for s in sorted_scores:
            detected = s.problems_detected.get(problem_key, False)
            print(f" {'  ✓  detected':^16}" if detected else f" {'  ✗  missed':^16}", end="")
        print()


def _print_pipelines_detail(scores: Dict[str, FormatScore]) -> None:
    """Wydrukuj szczegóły wykrytych pipeline'ów."""
    sorted_scores = sorted(scores.values(), key=lambda s: s.total_score, reverse=True)

    print(f"\n{'Pipeline':<20}", end="")
    for s in sorted_scores:
        print(f" {s.name:^16}", end="")
    print()
    print("─" * (20 + 17 * len(sorted_scores)))

    for pipeline_name in KNOWN_PIPELINES:
        print(f"{pipeline_name:<20}", end="")
        for s in sorted_scores:
            detected = s.pipelines_detected.get(pipeline_name, False)
            print(f" {'  ✓  detected':^16}" if detected else f" {'  ✗  missed':^16}", end="")
        print()


def _print_structural_features(scores: Dict[str, FormatScore]) -> None:
    """Wydrukuj cechy strukturalne formatów."""
    sorted_scores = sorted(scores.values(), key=lambda s: s.total_score, reverse=True)

    print(f"\n{'Feature':<20}", end="")
    for s in sorted_scores:
        print(f" {s.name:^16}", end="")
    print()
    print("─" * (20 + 17 * len(sorted_scores)))

    features = [
        ("Call chains", "has_call_chains"),
        ("Type info", "has_type_info"),
        ("Coupling", "has_coupling_info"),
        ("Severity markers", "has_severity_markers"),
        ("Refactor steps", "has_refactor_steps"),
        ("Side effects", "has_side_effects"),
        ("Purity info", "has_purity_info"),
        ("Contracts", "has_contracts"),
    ]
    for label, attr in features:
        print(f"{label:<20}", end="")
        for s in sorted_scores:
            val = getattr(s, attr)
            print(f" {'  ✓':^16}" if val else f" {'  ✗':^16}", end="")
        print()


def _print_gap_analysis(scores: Dict[str, FormatScore]) -> None:
    """Wydrukuj analizę luk w formatach."""
    print("\n" + "=" * 70)
    print("GAP ANALYSIS — what each format misses")
    print("=" * 70)

    sorted_scores = sorted(scores.values(), key=lambda s: s.total_score, reverse=True)

    for s in sorted_scores:
        missed = [k for k, v in s.problems_detected.items() if not v]
        if missed:
            print(f"\n  {s.name} ({s.total_score:.0f}%) — missed {len(missed)} problems:")
            for m in missed:
                print(f"    ✗ {m}: {KNOWN_PROBLEMS[m]}")


def print_results(scores: Dict[str, FormatScore]) -> None:
    """Wydrukuj sformatowane wyniki benchmarku."""
    _print_header()
    _print_scores_table(scores)
    _print_problems_detail(scores)
    _print_pipelines_detail(scores)
    _print_structural_features(scores)
    _print_gap_analysis(scores)


def build_report(scores: Dict[str, FormatScore]) -> Dict:
    """Zbuduj raport JSON do zapisu."""
    return {
        "benchmark_type": "format_quality",
        "timestamp": datetime.now().isoformat(),
        "ground_truth": {
            "problems": len(KNOWN_PROBLEMS),
            "pipelines": len(KNOWN_PIPELINES),
            "hub_types": 2,
        },
        "results": {
            name: {
                "total_score": s.total_score,
                "problem_score": s.problem_score,
                "pipeline_score": s.pipeline_score,
                "hub_type_score": s.hub_type_score,
                "structural_score": s.structural_score,
                "size_bytes": s.size_bytes,
                "generation_time": s.generation_time,
                "problems_detected": s.problems_detected,
                "pipelines_detected": s.pipelines_detected,
                "hub_types_detected": s.hub_types_detected,
            }
            for name, s in scores.items()
        },
        "ranking": [
            {"rank": i + 1, "format": s.name, "score": s.total_score}
            for i, s in enumerate(
                sorted(scores.values(), key=lambda x: x.total_score, reverse=True)
            )
        ],
    }


def save_report(report: Dict, filename: str = None) -> str:
    """Zapisz raport benchmarku do folderu reports."""
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"format_quality_{timestamp}.json"

    report_path = reports_dir / filename
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n[Report saved to: {report_path}]")
    return str(report_path)
