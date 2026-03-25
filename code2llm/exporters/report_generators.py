"""Report generators — produce views from project.yaml (single source of truth).

Thin re-export module. Actual generators live in separate files:
  toon_view.py      → ToonViewGenerator     → project.toon (legacy)
  context_view.py   → ContextViewGenerator  → context.md
  article_view.py   → ArticleViewGenerator  → status.md
  html_dashboard.py → HTMLDashboardGenerator → dashboard.html
"""

import yaml
from typing import Any, Dict

from .toon_view import ToonViewGenerator
from .context_view import ContextViewGenerator
from .article_view import ArticleViewGenerator
from .html_dashboard import HTMLDashboardGenerator


def load_project_yaml(path: str) -> Dict[str, Any]:
    """Load and validate project.yaml."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict) or "version" not in data:
        raise ValueError(f"Invalid project.yaml: missing 'version' key in {path}")
    return data


__all__ = [
    "load_project_yaml",
    "ToonViewGenerator",
    "ContextViewGenerator",
    "ArticleViewGenerator",
    "HTMLDashboardGenerator",
]
