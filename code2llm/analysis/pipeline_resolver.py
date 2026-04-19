"""Pipeline Resolver — callee resolution for pipeline detection.

Handles resolution of function calls to qualified names,
including self.method resolution within the same class.
"""

from typing import Dict, List, Optional, Tuple

from code2llm.core.models import FunctionInfo


class PipelineResolver:
    """Resolves callee names to qualified function names."""

    def resolve(
        self,
        callee: str,
        funcs: Dict[str, FunctionInfo],
        caller: Optional[FunctionInfo] = None,
    ) -> Optional[str]:
        """Resolve callee name to qualified name.

        Handles:
        - Direct qualified matches
        - self.method → same-class method resolution
        - Unqualified names with same-class preference

        Returns None for ambiguous matches (multiple candidates)
        to avoid creating phantom pipeline edges.
        """
        # Direct match
        if callee in funcs:
            return callee

        bare, is_self_call = self._strip_self_prefix(callee)

        # Try same-class resolution first
        if result := self._try_same_class_resolution(bare, caller, funcs):
            return result

        # Suffix match
        candidates = self._get_suffix_candidates(bare, funcs)
        if len(candidates) == 1:
            return candidates[0]

        # Prefer same-class candidates for method calls
        return self._select_same_class_candidate(candidates, caller, is_self_call)

    def _strip_self_prefix(self, callee: str) -> Tuple[str, bool]:
        """Strip self. prefix and return bare name + flag."""
        if callee.startswith("self."):
            return callee[5:], True
        return callee, False

    def _try_same_class_resolution(
        self,
        bare: str,
        caller: Optional[FunctionInfo],
        funcs: Dict[str, FunctionInfo],
    ) -> Optional[str]:
        """Try to resolve method in the same class as caller."""
        if caller and caller.class_name:
            class_prefix = f"{caller.module}.{caller.class_name}."
            class_candidate = class_prefix + bare
            if class_candidate in funcs:
                return class_candidate
        return None

    def _get_suffix_candidates(
        self, bare: str, funcs: Dict[str, FunctionInfo]
    ) -> List[str]:
        """Find candidates matching by suffix."""
        return [qn for qn in funcs if qn.endswith(f".{bare}")]

    def _select_same_class_candidate(
        self,
        candidates: List[str],
        caller: Optional[FunctionInfo],
        is_self_call: bool,
    ) -> Optional[str]:
        """Select candidate from same class if applicable."""
        if not candidates or not (is_self_call or (caller and caller.class_name)):
            return None

        same_class = [
            qn for qn in candidates
            if caller and caller.class_name and f".{caller.class_name}." in qn
        ]
        if len(same_class) == 1:
            return same_class[0]
        return None
