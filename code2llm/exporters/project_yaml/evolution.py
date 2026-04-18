"""Evolution history builder for project.yaml."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import yaml


def build_evolution(
    health: Dict[str, Any],
    total_lines: int,
    prev_evolution: List[Dict],
) -> List[Dict[str, Any]]:
    """Build append-only evolution history."""
    today = datetime.now().strftime("%Y-%m-%d")

    new_entry = {
        "date": today,
        "cc_avg": health["cc_avg"],
        "critical": health["critical_count"],
        "lines": total_lines,
        "note": "Automated analysis",
    }

    # Avoid duplicate entries for same date
    evolution = [e for e in prev_evolution if e.get("date") != today]
    evolution.append(new_entry)

    return evolution


def load_previous_evolution(output_path: Path) -> List[Dict]:
    """Load previous evolution entries from existing project.yaml."""
    if not output_path.exists():
        return []
    try:
        with open(output_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if isinstance(data, dict) and "evolution" in data:
            evo = data["evolution"]
            if isinstance(evo, list):
                return evo
    except Exception:
        pass
    return []
