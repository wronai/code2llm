"""Analysis of coupling between modules."""
from typing import Dict, List, Set, Any
from ..core.models import AnalysisResult

class CouplingAnalyzer:
    """Analyze coupling between modules."""
    
    def __init__(self, result: AnalysisResult):
        self.result = result
        
    def analyze(self) -> Dict[str, Any]:
        """Perform coupling analysis."""
        coupling_data = {
            "module_interactions": self._analyze_module_interactions(),
            "data_leakage": self._detect_data_leakage(),
            "shared_state": self._detect_shared_state()
        }
        self.result.coupling = coupling_data
        return coupling_data
        
    def _analyze_module_interactions(self) -> Dict[str, Set[str]]:
        """Track which modules call which other modules."""
        interactions = {}
        for func_name, func_info in self.result.functions.items():
            caller_mod = func_info.module or func_name.split('.')[0]
            if caller_mod not in interactions:
                interactions[caller_mod] = set()
                
            for callee in func_info.calls:
                callee_mod = callee.split('.')[0]
                if callee_mod != caller_mod:
                    interactions[caller_mod].add(callee_mod)
                    
        # Convert sets to lists for JSON serialization
        return {k: list(v) for k, v in interactions.items()}
        
    def _detect_data_leakage(self) -> List[Dict[str, Any]]:
        """Detect when a module mutates data defined in another module."""
        leakages = []
        # Heuristic: if a function in module A mutates an object passed from module B
        # This is simplified: we look for mutations where the scope module 
        # is different from the variable's likely origin.
        for mutation in self.result.mutations:
            scope_parts = mutation.scope.split('.')
            mut_mod = scope_parts[0]
            
            # If the variable name looks like it belongs to another module (e.g. 'other_mod.data')
            if '.' in mutation.variable:
                origin_mod = mutation.variable.split('.')[0]
                if origin_mod != mut_mod and origin_mod in self.result.modules:
                    leakages.append({
                        "variable": mutation.variable,
                        "mutator_module": mut_mod,
                        "origin_module": origin_mod,
                        "line": mutation.line,
                        "file": mutation.file
                    })
        return leakages

    def _detect_shared_state(self) -> List[Dict[str, Any]]:
        """Detect modules that access/mutate the same global/shared variables."""
        shared = []
        variable_accessors = {} # var -> set(modules)
        
        for mutation in self.result.mutations:
            mut_mod = mutation.scope.split('.')[0]
            if mutation.variable not in variable_accessors:
                variable_accessors[mutation.variable] = set()
            variable_accessors[mutation.variable].add(mut_mod)
            
        for var, mods in variable_accessors.items():
            if len(mods) > 1:
                shared.append({
                    "variable": var,
                    "modules": list(mods)
                })
        return shared
