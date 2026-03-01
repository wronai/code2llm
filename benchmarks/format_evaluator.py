"""Funkcje oceny jakości formatów wyjściowych.

Zawiera logikę oceny formatów pod kątem wykrywania problemów,
pipeline'ów, typów hub i kompletności strukturalnej.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .benchmark_constants import KNOWN_PROBLEMS, KNOWN_PIPELINES, KNOWN_HUB_TYPES


@dataclass
class FormatScore:
    """Wynik oceny pojedynczego formatu."""
    name: str
    file_path: Optional[Path] = None
    size_bytes: int = 0
    generation_time: float = 0.0

    # Wykryte problemy
    problems_detected: Dict[str, bool] = field(default_factory=dict)
    # Wykryte pipeline'y
    pipelines_detected: Dict[str, bool] = field(default_factory=dict)
    # Wykryte typy hub
    hub_types_detected: Dict[str, bool] = field(default_factory=dict)

    # Kompletność strukturalna
    has_call_chains: bool = False
    has_type_info: bool = False
    has_coupling_info: bool = False
    has_severity_markers: bool = False
    has_refactor_steps: bool = False
    has_side_effects: bool = False
    has_purity_info: bool = False
    has_contracts: bool = False

    # Wyniki obliczone
    problem_score: float = 0.0      # 0-100%
    pipeline_score: float = 0.0     # 0-100%
    hub_type_score: float = 0.0       # 0-100%
    structural_score: float = 0.0     # 0-100%
    total_score: float = 0.0          # 0-100%


def _detect_problems(content: str) -> Dict[str, bool]:
    """Wykryj znane problemy w treści formatu."""
    return {
        "god_function":    bool(re.search(r'god|!! split|CC[=≥]\s*(1[5-9]|[2-9]\d)', content)),
        "hub_type":        bool(re.search(r'hub.?type|consumed.?\d|HUB|fan.?in.?\d', content, re.I)),
        "duplicate_class": bool(re.search(r'DUP|duplicate|×DUP|identical', content, re.I)),
        "impure_pipeline": bool(re.search(r'impure|IO|side.?effect.*pipeline|purity.*0', content, re.I)),
        "dead_code":       bool(re.search(r'dead.?code|unused|unreachable|never.?called', content, re.I)),
        "high_fan_out":    bool(re.search(r'fan.?out|fan=\d|hotspot|fan-out', content, re.I)),
        "missing_types":   bool(re.search(r'missing.?type|no.?annotation|untyped', content, re.I)),
        "side_effect":     bool(re.search(r'side.?effect|mutation|mutate|global|cache_result', content, re.I)),
    }


def _detect_pipelines(content: str) -> Dict[str, bool]:
    """Wykryj znane pipeline'y w treści formatu."""
    cl = content.lower()
    result = {}

    for pipeline_name, stages in KNOWN_PIPELINES.items():
        # Sprawdź czy ≥2 kolejne etapy pojawiają się w odpowiedniej kolejności
        found_stages = sum(1 for s in stages if s in cl)
        # Sprawdź czy pojawiają się jako połączony łańcuch
        chain_pattern = r'→|──>|->|calls|chain'
        has_chain = bool(re.search(chain_pattern, content))
        result[pipeline_name] = (found_stages >= 2) and has_chain

    return result


def _detect_hub_types(content: str) -> Dict[str, bool]:
    """Wykryj znane typy hub w treści formatu."""
    result = {}
    for type_name in KNOWN_HUB_TYPES:
        type_pattern = rf'{type_name}.*consumed|{type_name}.*fan|{type_name}.*←\d|{type_name}.*hub'
        result[type_name] = bool(re.search(type_pattern, content, re.I))
    return result


def _check_structural_features(content: str) -> Dict[str, bool]:
    """Sprawdź cechy kompletności strukturalnej."""
    return {
        "has_call_chains":     bool(re.search(r'→|calls:|──>|call.?chain|call.?graph', content, re.I)),
        "has_type_info":       bool(re.search(r'->\s*(str|int|dict|list|Result|Config|None)', content)),
        "has_coupling_info":   bool(re.search(r'COUPLING|fan-in|fan-out|import.*graph|←in', content, re.I)),
        "has_severity_markers": bool(re.search(r'!!|🔴|🟡|critical|HEALTH', content)),
        "has_refactor_steps":  bool(re.search(r'REFACTOR|split|extract|merge.*class', content, re.I)),
        "has_side_effects":    bool(re.search(r'SIDE.?EFFECT|pure|impure|IO|mutation', content, re.I)),
        "has_purity_info":     bool(re.search(r'purity|pure.*\d|PURITY', content, re.I)),
        "has_contracts":       bool(re.search(r'CONTRACT|IN:|OUT:|input.*→.*output|invariant', content, re.I)),
    }


def evaluate_format(name: str, content: str, path: Optional[Path] = None) -> FormatScore:
    """Oceń pojedynczy format względem ground truth."""
    score = FormatScore(name=name, file_path=path)
    if path and path.exists():
        score.size_bytes = path.stat().st_size

    # Wykrywanie problemów
    score.problems_detected = _detect_problems(content)
    detected = sum(score.problems_detected.values())
    score.problem_score = detected / len(KNOWN_PROBLEMS) * 100

    # Wykrywanie pipeline'ów
    score.pipelines_detected = _detect_pipelines(content)
    detected_p = sum(score.pipelines_detected.values())
    score.pipeline_score = detected_p / len(KNOWN_PIPELINES) * 100

    # Wykrywanie typów hub
    score.hub_types_detected = _detect_hub_types(content)
    detected_h = sum(score.hub_types_detected.values())
    score.hub_type_score = detected_h / len(KNOWN_HUB_TYPES) * 100

    # Kompletność strukturalna
    features = _check_structural_features(content)
    for key, value in features.items():
        setattr(score, key, value)

    structural_features = list(features.values())
    score.structural_score = sum(structural_features) / len(structural_features) * 100

    # Całkowity wynik (ważony)
    score.total_score = (
        score.problem_score * 0.30 +
        score.pipeline_score * 0.25 +
        score.hub_type_score * 0.20 +
        score.structural_score * 0.25
    )

    return score
