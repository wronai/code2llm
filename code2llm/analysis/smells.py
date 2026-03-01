"""Detection of code smells using analysis metrics."""
from typing import List, Dict, Any
from ..core.models import AnalysisResult, CodeSmell

class SmellDetector:
    """Detect code smells from analysis results."""
    
    def __init__(self, result: AnalysisResult):
        self.result = result
        
    def detect(self) -> List[CodeSmell]:
        """Record and return detected code smells."""
        smells = []
        smells.extend(self._detect_god_functions())
        smells.extend(self._detect_god_modules())
        smells.extend(self._detect_feature_envy())
        smells.extend(self._detect_data_clumps())
        smells.extend(self._detect_shotgun_surgery())
        smells.extend(self._detect_bottlenecks())
        smells.extend(self._detect_circular_dependencies())
        
        self.result.smells = smells
        return smells
        
    def _detect_god_functions(self) -> List[CodeSmell]:
        """Detect high fan-out / large functions."""
        smells = []
        for func_name, func_info in self.result.functions.items():
            metrics = self.result.metrics.get(func_name, {})
            fan_out = metrics.get('fan_out', 0)
            mutation_count = len([m for m in self.result.mutations if m.scope == func_name])
            
            # Use cyclomatic complexity (now mapped to 'cc' in FunctionInfo.complexity)
            complexity = func_info.complexity.get('cyclomatic_complexity', 1)
            
            if fan_out > 10 or mutation_count > 6 or complexity > 12:
                severity = (fan_out / 20) * 0.3 + (mutation_count / 15) * 0.3 + (complexity / 30) * 0.4
                severity = min(1.0, severity)
                
                smells.append(CodeSmell(
                    name=f"God Function: {func_info.name}",
                    type="god_function",
                    file=func_info.file,
                    line=func_info.line,
                    severity=severity,
                    description=f"Function '{func_info.name}' is oversized: CC={complexity}, fan-out={fan_out}, mutations={mutation_count}.",
                    context={"fan_out": fan_out, "mutations": mutation_count, "complexity": complexity, "function": func_name}
                ))
        return smells

    def _detect_god_modules(self) -> List[CodeSmell]:
        """Detect oversized modules/packages."""
        smells = []
        for mod_name, mod in self.result.modules.items():
            f_count = len(mod.functions)
            c_count = len(mod.classes)
            
            if f_count > 40 or c_count > 10:
                severity = (f_count / 100) * 0.5 + (c_count / 25) * 0.5
                severity = min(1.0, severity)
                
                smells.append(CodeSmell(
                    name=f"God Module: {mod_name}",
                    type="god_function", # Map to extract_method for simplicity or add god_module template
                    file=mod.file,
                    line=1,
                    severity=severity,
                    description=f"Module '{mod_name}' is too large ({f_count} functions, {c_count} classes). Consider splitting into sub-modules.",
                    context={"functions": f_count, "classes": c_count}
                ))
        return smells
        
    def _detect_feature_envy(self) -> List[CodeSmell]:
        """Detect functions that use other objects more than their own."""
        smells = []
        # Simplified: look for functions mutating many variables in OTHER modules
        for func_name, func_info in self.result.functions.items():
            mut_mod = func_name.split('.')[0]
            foreign_mutations = []
            
            for mutation in self.result.mutations:
                if mutation.scope == func_name:
                    if '.' in mutation.variable:
                        origin_mod = mutation.variable.split('.')[0]
                        if origin_mod != mut_mod:
                            foreign_mutations.append(mutation.variable)
                            
            if len(set(foreign_mutations)) >= 3:
                smells.append(CodeSmell(
                    name=f"Feature Envy: {func_info.name}",
                    type="feature_envy",
                    file=func_info.file,
                    line=func_info.line,
                    severity=0.7,
                    description=f"Function '{func_info.name}' mutates multiple variables in other modules: {', '.join(set(foreign_mutations))}.",
                    context={"foreign_mutations": list(set(foreign_mutations))}
                ))
        return smells

    def _detect_data_clumps(self) -> List[CodeSmell]:
        """Detect 3+ variables frequently passed together."""
        smells = []
        # Simplified: find functions with same 3+ arguments
        arg_sets = {} # frozenset(args) -> List[func_names]
        for func_name, func_info in self.result.functions.items():
            if len(func_info.args) >= 3:
                args = frozenset(func_info.args)
                if args not in arg_sets:
                    arg_sets[args] = []
                arg_sets[args].append(func_name)
                
        for args, funcs in arg_sets.items():
            if len(funcs) >= 2:
                for func_name in funcs:
                    func_info = self.result.functions[func_name]
                    smells.append(CodeSmell(
                        name=f"Data Clump: {', '.join(args)}",
                        type="data_clump",
                        file=func_info.file,
                        line=func_info.line,
                        severity=0.6,
                        description=f"Arguments ({', '.join(args)}) are used together in multiple functions: {', '.join(funcs)}.",
                        context={"clump": list(args), "related_functions": funcs}
                    ))
        return smells

    def _detect_shotgun_surgery(self) -> List[CodeSmell]:
        """Detect variables whose mutation requires changes across many functions."""
        smells = []
        var_mutators = {} # variable -> set(functions)
        
        for mutation in self.result.mutations:
            if mutation.variable not in var_mutators:
                var_mutators[mutation.variable] = set()
            var_mutators[mutation.variable].add(mutation.scope)
            
        for var, funcs in var_mutators.items():
            if len(funcs) >= 5:
                # Find a representative function to report the smell
                func_name = list(funcs)[0]
                func_info = self.result.functions.get(func_name)
                if not func_info: continue
                
                smells.append(CodeSmell(
                    name=f"Shotgun Surgery: {var}",
                    type="shotgun_surgery",
                    file=func_info.file,
                    line=func_info.line,
                    severity=0.8,
                    description=f"Mutation of variable '{var}' spans {len(funcs)} functions. Changing this logic requires work in many places.",
                    context={"variable": var, "affected_functions": list(funcs)}
                ))
        return smells
    def _detect_bottlenecks(self) -> List[CodeSmell]:
        """Detect functions with high Betweenness Centrality."""
        smells = []
        # Central functions that many independent paths traverse
        for func_name, func_info in self.result.functions.items():
            if func_info.centrality > 0.1: # Heuristic threshold
                smells.append(CodeSmell(
                    name=f"Structural Bottleneck: {func_info.name}",
                    type="bottleneck",
                    file=func_info.file,
                    line=func_info.line,
                    severity=min(1.0, func_info.centrality * 5),
                    description=f"Function '{func_info.name}' is a structural bottleneck (centrality={round(func_info.centrality, 3)}). Significant logic flows through this function.",
                    context={"centrality": func_info.centrality}
                ))
        return smells

    def _detect_circular_dependencies(self) -> List[CodeSmell]:
        """Detect circular dependencies in call graph."""
        smells = []
        cycles = self.result.metrics.get("project", {}).get("circular_dependencies", [])
        
        for cycle in cycles:
            if len(cycle) >= 2:
                # Report on the first function in the cycle
                func_name = cycle[0]
                func_info = self.result.functions.get(func_name)
                if not func_info: continue
                
                smells.append(CodeSmell(
                    name=f"Circular Dependency: {' -> '.join(cycle)}",
                    type="circular_dependency",
                    file=func_info.file,
                    line=func_info.line,
                    severity=0.8,
                    description=f"Circular dependency detected: {' -> '.join(cycle)}. This indicates high coupling and may lead to infinite recursion or initialization issues.",
                    context={"cycle": cycle}
                ))
        return smells
