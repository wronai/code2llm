"""Validate consistency between project.yaml and its generated views.

Quick sanity check that key metrics in project.yaml match the
generated project.toon.yaml output.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Tuple


def validate_project_yaml(output_dir: Path, verbose: bool = False) -> Tuple[bool, List[str]]:
    """Validate project.yaml against generated views in output_dir.

    Returns (is_valid, list_of_issues).
    """
    issues: List[str] = []

    yaml_path = output_dir / "project.yaml"
    toon_path = output_dir / "project.toon.yaml"

    if not yaml_path.exists():
        issues.append(f"project.yaml not found in {output_dir}")
        return False, issues

    # Load project.yaml
    try:
        import yaml as _yaml
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = _yaml.safe_load(f)
    except Exception as e:
        issues.append(f"Failed to parse project.yaml: {e}")
        return False, issues

    # Validate structure
    issues.extend(_check_required_keys(data))

    # Validate views exist
    expected_views = ["project.toon.yaml", "dashboard.html"]
    for view in expected_views:
        if not (output_dir / view).exists():
            issues.append(f"Expected view {view} not found")

    # Cross-check project.toon.yaml if it exists
    if toon_path.exists():
        issues.extend(_cross_check_toon(data, toon_path))

    if verbose and not issues:
        print("  ✓ project.yaml validation passed")
    elif verbose and issues:
        print(f"  ⚠ project.yaml validation: {len(issues)} issue(s)")
        for issue in issues:
            print(f"    - {issue}")

    return len(issues) == 0, issues


def _check_required_keys(data: Dict[str, Any]) -> List[str]:
    """Check that required top-level keys exist in project.yaml."""
    issues = []
    required = ["version", "project", "health", "modules"]
    for key in required:
        if key not in data:
            issues.append(f"Missing required key: {key}")

    proj = data.get("project", {})
    if proj:
        stats = proj.get("stats", {})
        for stat_key in ["files", "lines", "functions", "classes"]:
            if stat_key not in stats:
                issues.append(f"Missing project.stats.{stat_key}")

    health = data.get("health", {})
    if health:
        for h_key in ["cc_avg", "critical_count"]:
            if h_key not in health:
                issues.append(f"Missing health.{h_key}")

    return issues


def _cross_check_toon(data: Dict[str, Any], toon_path: Path) -> List[str]:
    """Cross-check project.yaml metrics against project.toon.yaml header."""
    issues = []
    try:
        content = toon_path.read_text(encoding="utf-8")
    except Exception:
        return [f"Cannot read {toon_path.name}"]

    # Parse first line: "# name | N func | Nf | NL | date"
    first_line = content.split("\n", 1)[0] if content else ""

    proj = data.get("project", {})
    stats = proj.get("stats", {})
    yaml_funcs = stats.get("functions", 0)
    yaml_lines = stats.get("lines", 0)

    # Extract func count from toon header
    m = re.search(r"(\d+)\s*func", first_line)
    if m:
        toon_funcs = int(m.group(1))
        if toon_funcs != yaml_funcs:
            issues.append(
                f"Function count mismatch: project.yaml={yaml_funcs}, "
                f"project.toon.yaml={toon_funcs}"
            )

    # Extract lines count from toon header
    m = re.search(r"(\d+)L", first_line)
    if m:
        toon_lines = int(m.group(1))
        if toon_lines != yaml_lines:
            issues.append(
                f"Lines count mismatch: project.yaml={yaml_lines}, "
                f"project.toon.yaml={toon_lines}"
            )

    return issues
