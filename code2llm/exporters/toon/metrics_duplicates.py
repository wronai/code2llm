"""Duplicate detection metrics for TOON export.

Detects duplicate classes by comparing method-name sets.
"""

from typing import Any, Dict, List, Optional, Set

from code2llm.core.models import AnalysisResult, ClassInfo

from .helpers import _is_excluded, _rel_path


class DuplicatesMetricsComputer:
    """Detects duplicate classes in the codebase."""

    def __init__(self, project_path: str):
        self.project_path = project_path

    def detect_duplicates(self, result: AnalysisResult) -> List[Dict[str, Any]]:
        """Detect duplicate classes by comparing method-name sets."""
        dupes: List[Dict[str, Any]] = []
        # Filter out excluded classes first
        class_list = [(q, c) for q, c in result.classes.items() if not _is_excluded(c.file)]

        for i, (qa, ca) in enumerate(class_list):
            dupes.extend(self._check_class_for_duplicates(i, qa, ca, class_list, result))

        return dupes

    def _check_class_for_duplicates(self, i: int, qa: str, ca: ClassInfo, class_list: List, result: AnalysisResult) -> List[Dict[str, Any]]:
        """Check a single class for duplicates."""
        methods_a = {m.split(".")[-1] for m in ca.methods}
        if len(methods_a) < 3:
            return []

        dupes = []
        for j in range(i + 1, len(class_list)):
            qb, cb = class_list[j]
            if ca.name != cb.name:
                continue

            methods_b = {m.split(".")[-1] for m in cb.methods}
            if len(methods_b) < 3:
                continue

            duplicate_info = self._calculate_duplicate_info(qa, ca, qb, cb, methods_a, methods_b, result)
            if duplicate_info:
                dupes.append(duplicate_info)

        return dupes

    def _calculate_duplicate_info(self, qa: str, ca: ClassInfo, qb: str, cb: ClassInfo, methods_a: Set[str], methods_b: Set[str], result: AnalysisResult) -> Optional[Dict[str, Any]]:
        """Calculate duplicate information between two classes."""
        overlap = methods_a & methods_b
        union = methods_a | methods_b
        if len(overlap) / len(union) >= 0.6:
            only_a = methods_a - methods_b
            only_b = methods_b - methods_a

            if methods_a == methods_b:
                diff = "IDENTICAL"
            elif len(methods_a) >= len(methods_b):
                diff = f"A has +{','.join(sorted(only_a))}" if only_a else "A=B"
            else:
                diff = f"B has +{','.join(sorted(only_b))}" if only_b else "A=B"

            return {
                "class_name": ca.name,
                "qualA": qa, "qualB": qb,
                "fileA": _rel_path(ca.file, result.project_path),
                "fileB": _rel_path(cb.file, result.project_path),
                "methodsA": sorted(methods_a),
                "methodsB": sorted(methods_b),
                "countA": len(methods_a),
                "countB": len(methods_b),
                "diff": diff,
            }
        return None
