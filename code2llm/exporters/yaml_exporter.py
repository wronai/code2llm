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
        connected, edges = self._collect_edges(result, max_calls_per_func, max_edges)
        nodes = self._build_nodes(result, connected)
        modules = self._group_by_module(result, connected)
        
        calls_data = self._build_calls_data(result, nodes, edges, modules)
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(calls_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def _collect_edges(self, result: AnalysisResult, max_calls: int, max_edges: int) -> Tuple[Set[str], List[Dict]]:
        """Collect connected nodes and edges from function calls."""
        connected: Set[str] = set()
        edges: List[Dict] = []
        seen_pairs: Set[Tuple[str, str]] = set()

        for func_name, fi in result.functions.items():
            if len(edges) >= max_edges:
                break
            self._process_function_calls(
                func_name, fi, result.functions, max_calls, max_edges,
                connected, edges, seen_pairs
            )

        return connected, edges

    def _process_function_calls(
        self, func_name: str, fi: FunctionInfo, functions: Dict[str, FunctionInfo],
        max_calls: int, max_edges: int, connected: Set[str], edges: List[Dict],
        seen_pairs: Set[Tuple[str, str]]
    ) -> None:
        """Process calls for a single function."""
        for callee in fi.calls[:max_calls]:
            if len(edges) >= max_edges:
                break
            resolved = self._resolve_callee(callee, functions)
            if self._should_add_edge(func_name, resolved, seen_pairs):
                connected.add(func_name)
                connected.add(resolved)
                seen_pairs.add((func_name, resolved))
                edges.append(self._create_edge(func_name, resolved, callee))

    @staticmethod
    def _should_add_edge(func_name: str, resolved: Optional[str], seen_pairs: Set[Tuple[str, str]]) -> bool:
        """Check if edge should be added (valid callee and not duplicate)."""
        if not resolved or resolved == func_name:
            return False
        return (func_name, resolved) not in seen_pairs

    @staticmethod
    def _create_edge(caller: str, resolved: str, callee: str) -> Dict:
        """Create edge dict with call type classification."""
        return {
            'caller': caller,
            'callee': resolved,
            'call_type': 'direct' if callee == resolved.split('.')[-1] else 'resolved'
        }

    def _build_nodes(self, result: AnalysisResult, connected: Set[str]) -> Dict[str, Dict]:
        """Build node data for all connected functions."""
        nodes: Dict[str, Dict] = {}
        for fn in connected:
            fi = result.functions.get(fn)
            if fi:
                nodes[fn] = self._create_node(fi, fn, result)
        return nodes

    def _create_node(self, fi: FunctionInfo, fn: str, result: AnalysisResult) -> Dict:
        """Create node dict with function metadata."""
        return {
            'name': fi.name,
            'module': fi.module,
            'line': fi.line,
            'cyclomatic_complexity': self._get_cc(fi),
            'calls_out': len(fi.calls),
            'calls_in': self._count_calls_in(fn, result),
        }

    def _count_calls_in(self, fn: str, result: AnalysisResult) -> int:
        """Count how many functions call the given function."""
        count = 0
        for f in result.functions.values():
            for c in f.calls:
                resolved = self._resolve_callee(c, result.functions)
                if resolved == fn:
                    count += 1
                    break
        return count

    @staticmethod
    def _group_by_module(result: AnalysisResult, connected: Set[str]) -> Dict[str, List[str]]:
        """Group connected functions by their module."""
        modules: Dict[str, List[str]] = defaultdict(list)
        for fn in connected:
            fi = result.functions.get(fn)
            if fi:
                modules[fi.module].append(fn)
        return {mod: sorted(funcs) for mod, funcs in sorted(modules.items())}

    def _build_calls_data(self, result: AnalysisResult, nodes: Dict, edges: List, modules: Dict) -> Dict:
        """Build the final calls.yaml data structure."""
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
            'modules': modules,
        }
        
        if result.entry_points:
            calls_data['entry_points'] = sorted(result.entry_points)
        
        return calls_data

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

    def export_calls_toon(self, result: AnalysisResult, output_path: str, max_calls_per_func: int = 10, max_edges: int = 500) -> None:
        """Export call graph as toon.yaml format (human-readable).

        Generates a human-readable toon format with:
        - Header with project stats
        - HUBS: high-degree functions (many calls in/out)
        - CHAINS: call chains/paths
        - MODULES: functions grouped by module with call relationships
        """
        connected, edges = self._collect_edges(result, max_calls_per_func, max_edges)
        nodes = self._build_nodes(result, connected)
        modules = self._group_by_module(result, connected)

        # Build toon format sections
        lines = []
        lines.extend(self._render_calls_header(result, nodes, edges, modules))
        lines.append("")
        lines.extend(self._render_hubs(nodes))
        lines.append("")
        lines.extend(self._render_modules(modules, nodes, edges))
        lines.append("")
        lines.extend(self._render_edges(edges))

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')

    def _render_calls_header(self, result: AnalysisResult, nodes: Dict, edges: List, modules: Dict) -> List[str]:
        """Render header section for calls.toon.yaml."""
        nfuncs = len(result.functions)
        all_cc = [self._get_cc(fi) for fi in result.functions.values()]
        avg_cc = round(sum(all_cc) / len(all_cc), 1) if all_cc else 0.0

        return [
            f"# code2llm call graph | {result.project_path}",
            f"# nodes: {len(nodes)} | edges: {len(edges)} | modules: {len(modules)}",
            f"# CC̄={avg_cc}",
        ]

    def _render_hubs(self, nodes: Dict) -> List[str]:
        """Render high-degree hub functions (sorted by total calls)."""
        hubs = sorted(
            [(name, data) for name, data in nodes.items()],
            key=lambda x: x[1]['calls_in'] + x[1]['calls_out'],
            reverse=True
        )[:20]

        lines = ['HUBS[20]:']
        for name, data in hubs:
            total_calls = data['calls_in'] + data['calls_out']
            lines.append(f"  {name}")
            lines.append(f"    CC={data['cyclomatic_complexity']}  in:{data['calls_in']}  out:{data['calls_out']}  total:{total_calls}")
        return lines

    def _render_modules(self, modules: Dict, nodes: Dict, edges: List) -> List[str]:
        """Render modules section with functions and call relationships."""
        lines = ['MODULES:']
        for module, funcs in sorted(modules.items()):
            lines.append(f"  {module}  [{len(funcs)} funcs]")
            for func in funcs[:10]:  # Show up to 10 funcs per module
                if func in nodes:
                    data = nodes[func]
                    lines.append(f"    {data['name']}  CC={data['cyclomatic_complexity']}  out:{data['calls_out']}")
        return lines

    def _render_edges(self, edges: List) -> List[str]:
        """Render call edges section."""
        lines = ['EDGES:']
        for edge in edges[:50]:  # Show up to 50 edges
            lines.append(f"  {edge['caller']} → {edge['callee']}")
        return lines
