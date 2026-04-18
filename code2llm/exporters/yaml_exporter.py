"""YAML Exporter for code2llm."""

import yaml
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from .base import Exporter
from code2llm.core.models import AnalysisResult, FunctionInfo
from code2llm.analysis.data_analysis import DataAnalyzer


class YAMLExporter(Exporter):
    """Export to YAML format."""
    
    def __init__(self):
        self.analyzer = DataAnalyzer()
    
    def export(self, result: AnalysisResult, output_path: str, compact: bool = True, include_defaults: bool = False) -> None:
        """Export to YAML file."""
        data = result.to_dict(compact=compact and not include_defaults)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    def export_grouped(self, result: AnalysisResult, output_path: str) -> None:
        """Export with grouped CFG flows by function."""
        from collections import defaultdict
        func_flows = defaultdict(list)
        for node_id, node in result.nodes.items():
            if hasattr(node, 'function') and node.function:
                func_flows[node.function].append({
                    'id': node_id,
                    'type': getattr(node, 'type', 'unknown'),
                    'label': getattr(node, 'label', ''),
                    'line': getattr(node, 'line', None),
                })
        
        grouped_data = {
            'project': result.project_path,
            'summary': {'functions': len(result.functions), 'classes': len(result.classes)},
            'control_flows': {}
        }
        for func_name, nodes in sorted(func_flows.items()):
            if len(nodes) < 2: continue
            sorted_nodes = sorted(nodes, key=lambda n: (n['line'] or 0, n['id']))
            grouped_data['control_flows'][func_name] = {
                'node_count': len(nodes),
                'flow_sequence': [{'step': i+1, 'type': n['type'], 'label': n['label'][:50], 'line': n['line']} for i, n in enumerate(sorted_nodes)]
            }
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(grouped_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def export_data_flow(self, result: AnalysisResult, output_path: str, compact: bool = True) -> None:
        """Export detailed data flow analysis."""
        flow_data = self.analyzer.analyze_data_flow(result)
        flow_data.update({'project_path': result.project_path, 'analysis_type': 'data_flow'})
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(flow_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def export_data_structures(self, result: AnalysisResult, output_path: str, compact: bool = True) -> None:
        """Export data structure analysis."""
        structure_data = self.analyzer.analyze_data_structures(result)
        structure_data.update({'project_path': result.project_path, 'analysis_type': 'data_structures'})
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(structure_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def export_separated(self, result: AnalysisResult, output_dir: str, compact: bool = True) -> None:
        """Export separated consolidated and orphan functions."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Simple separation logic: functions reachable from entry points vs others
        connected = {}
        orphans = {}
        
        # Reachability is already in FunctionInfo (Sprint 3)
        for name, func in result.functions.items():
            if func.reachability == "reachable" or name in result.entry_points:
                connected[name] = func.to_dict(compact)
            else:
                orphans[name] = func.to_dict(compact)
        
        with open(output_path / 'consolidated.yaml', 'w', encoding='utf-8') as f:
            yaml.dump({'functions': connected}, f, default_flow_style=False, allow_unicode=True)
            
        with open(output_path / 'orphans.yaml', 'w', encoding='utf-8') as f:
            yaml.dump({'functions': orphans}, f, default_flow_style=False, allow_unicode=True)

    def export_split(self, result: AnalysisResult, output_dir: str, include_defaults: bool = False) -> None:
        """Export results split by module."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        modules = defaultdict(lambda: {'functions': {}, 'classes': {}})
        for name, func in result.functions.items():
            modules[func.module]['functions'][name] = func.to_dict(not include_defaults)
        for name, cls in result.classes.items():
            modules[cls.module]['classes'][name] = cls.to_dict(not include_defaults)
            
        for mod_name, content in modules.items():
            safe_name = mod_name.replace('.', '_') or 'root'
            with open(output_path / f'{safe_name}.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(content, f, default_flow_style=False, allow_unicode=True)

    def export_calls(self, result: AnalysisResult, output_path: str, max_calls_per_func: int = 10, max_edges: int = 500) -> None:
        """Export call graph as structured YAML (calls.yaml).
        
        Generates a structured representation of the call graph with:
        - nodes: all functions that participate in calls (with metadata)
        - edges: caller -> callee relationships
        - modules: grouping of functions by module
        - stats: summary statistics
        """
        # Collect connected nodes and edges
        connected: Set[str] = set()
        edges: List[Dict] = []
        seen_pairs: Set[Tuple[str, str]] = set()
        
        for func_name, fi in result.functions.items():
            for callee in fi.calls[:max_calls_per_func]:
                resolved = self._resolve_callee(callee, result.functions)
                if resolved and resolved != func_name:
                    connected.add(func_name)
                    connected.add(resolved)
                    pair = (func_name, resolved)
                    if pair not in seen_pairs:
                        seen_pairs.add(pair)
                        edges.append({
                            'caller': func_name,
                            'callee': resolved,
                            'call_type': 'direct' if callee == resolved.split('.')[-1] else 'resolved'
                        })
                        if len(edges) >= max_edges:
                            break
            if len(edges) >= max_edges:
                break
        
        # Build nodes data
        nodes: Dict[str, Dict] = {}
        for fn in connected:
            fi = result.functions.get(fn)
            if fi:
                cc = self._get_cc(fi)
                nodes[fn] = {
                    'name': fi.name,
                    'module': fi.module,
                    'line': fi.line,
                    'cyclomatic_complexity': cc,
                    'calls_out': len(fi.calls),
                    'calls_in': sum(1 for f in result.functions.values() if fn in [self._resolve_callee(c, result.functions) for c in f.calls]),
                }
        
        # Group by module
        modules: Dict[str, List[str]] = defaultdict(list)
        for fn in connected:
            fi = result.functions.get(fn)
            if fi:
                modules[fi.module].append(fn)
        
        # Build output structure
        calls_data = {
            'project': result.project_path,
            'generated_from': 'code2llm call graph analysis',
            'stats': {
                'total_nodes': len(nodes),
                'total_edges': len(edges),
                'modules_count': len(modules),
            },
            'nodes': nodes,
            'edges': edges,
            'modules': {mod: sorted(funcs) for mod, funcs in sorted(modules.items())},
        }
        
        # Add entry points if available
        if result.entry_points:
            calls_data['entry_points'] = sorted(result.entry_points)
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(calls_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    @staticmethod
    def _resolve_callee(callee: str, funcs: Dict[str, FunctionInfo]) -> Optional[str]:
        """Resolve callee to a known qualified name."""
        if callee in funcs:
            return callee
        candidates = [qn for qn in funcs if qn.endswith(f".{callee}")]
        if len(candidates) == 1:
            return candidates[0]
        return None

    @staticmethod
    def _get_cc(fi: FunctionInfo) -> int:
        """Extract cyclomatic complexity from FunctionInfo."""
        if isinstance(fi.complexity, dict):
            return fi.complexity.get('cyclomatic_complexity', 0)
        return fi.complexity or 0
