"""Data Analysis logic for code2flow - extracted from YAMLExporter."""

from typing import Any, Dict, List
from ..core.models import AnalysisResult


class DataAnalyzer:
    """Analyze data flows, structures, and optimization opportunities."""
    
    def analyze_data_flow(self, result: AnalysisResult) -> Dict[str, Any]:
        """Perform detailed data flow analysis."""
        return {
            'data_pipelines': self._find_data_pipelines(result),
            'state_patterns': self._find_state_patterns(result),
            'data_dependencies': self._find_data_dependencies(result),
            'event_flows': self._find_event_flows(result),
        }
        
    def analyze_data_structures(self, result: AnalysisResult) -> Dict[str, Any]:
        """Analyze data structures and optimization opportunities."""
        data_types = self._analyze_data_types(result)
        data_flow_graph = self._build_data_flow_graph(result)
        process_patterns = self._identify_process_patterns(result)
        optimization_analysis = self._analyze_optimization_opportunities(result, data_types, data_flow_graph)
        
        return {
            'data_types': data_types,
            'data_flow_graph': data_flow_graph,
            'process_patterns': process_patterns,
            'optimization_analysis': optimization_analysis,
        }

    def _find_data_pipelines(self, result: AnalysisResult) -> list:
        """Find data transformation pipelines in the codebase."""
        pipelines = []
        input_indicators = ['parse', 'load', 'read', 'fetch', 'get', 'input', 'receive', 'extract']
        transform_indicators = ['transform', 'convert', 'process', 'validate', 'filter', 'map', 'reduce', 'compute']
        output_indicators = ['serialize', 'format', 'write', 'save', 'send', 'output', 'render', 'encode']
        
        input_funcs = []
        transform_funcs = []
        output_funcs = []
        
        for func_name, func in result.functions.items():
            name_lower = func.name.lower()
            if any(ind in name_lower for ind in input_indicators):
                input_funcs.append((func_name, func))
            elif any(ind in name_lower for ind in transform_indicators):
                transform_funcs.append((func_name, func))
            elif any(ind in name_lower for ind in output_indicators):
                output_funcs.append((func_name, func))
        
        for in_name, in_func in input_funcs[:20]:
            for t_name, t_func in transform_funcs[:30]:
                if t_name in in_func.calls:
                    for out_name, out_func in output_funcs[:20]:
                        if out_name in t_func.calls:
                            pipelines.append({
                                'pipeline_id': f"pipeline_{len(pipelines)+1}",
                                'stages': [
                                    {'stage': 'input', 'function': in_name, 'description': in_func.docstring[:100] if in_func.docstring else 'N/A'},
                                    {'stage': 'transform', 'function': t_name, 'description': t_func.docstring[:100] if t_func.docstring else 'N/A'},
                                    {'stage': 'output', 'function': out_name, 'description': out_func.docstring[:100] if out_func.docstring else 'N/A'},
                                ],
                                'data_flow': f"{in_name} → {t_name} → {out_name}",
                            })
                            if len(pipelines) >= 15:
                                return pipelines
        return pipelines

    def _find_state_patterns(self, result: AnalysisResult) -> list:
        """Find state management patterns."""
        patterns = []
        state_indicators = ['state', 'status', 'mode', 'phase', 'lifecycle', 'session', 'context']
        transition_indicators = ['transition', 'change', 'update', 'set_state', 'switch']
        
        for func_name, func in result.functions.items():
            name_lower = func.name.lower()
            if any(ind in name_lower for ind in state_indicators + transition_indicators):
                affected_states = []
                for call in list(func.calls)[:10]:
                    call_func = result.functions.get(call)
                    if call_func and any(ind in call_func.name.lower() for ind in state_indicators):
                        affected_states.append(call)
                patterns.append({
                    'function': func_name,
                    'type': 'state_manager' if 'set' in name_lower or 'update' in name_lower else 'state_reader',
                    'affects_states': affected_states[:5],
                    'description': func.docstring[:150] if func.docstring else 'N/A',
                })
                if len(patterns) >= 20: break
        return patterns

    def _find_data_dependencies(self, result: AnalysisResult) -> list:
        """Find cross-module data dependencies."""
        module_data_flow = {}
        for func_name, func in result.functions.items():
            func_module = func_name.rsplit('.', 1)[0] if '.' in func_name else 'root'
            for called in list(func.calls)[:15]:
                called_module = called.rsplit('.', 1)[0] if '.' in called else 'root'
                if func_module != called_module and called in result.functions:
                    key = (func_module, called_module)
                    if key not in module_data_flow:
                        module_data_flow[key] = {'from_module': func_module, 'to_module': called_module, 'data_functions': [], 'call_count': 0}
                    module_data_flow[key]['data_functions'].append({'caller': func_name, 'callee': called})
                    module_data_flow[key]['call_count'] += 1
        deps = sorted(module_data_flow.values(), key=lambda x: x['call_count'], reverse=True)
        for dep in deps: dep['data_functions'] = dep['data_functions'][:10]
        return deps[:15]

    def _find_event_flows(self, result: AnalysisResult) -> list:
        """Find event-driven patterns."""
        flows = []
        event_indicators = ['event', 'emit', 'trigger', 'notify', 'callback', 'handler', 'listen', 'subscribe']
        hook_indicators = ['hook', 'on_', 'before_', 'after_', 'pre_', 'post_']
        for func_name, func in result.functions.items():
            name_lower = func.name.lower()
            if any(ind in name_lower for ind in event_indicators) or any(name_lower.startswith(ind) for ind in hook_indicators):
                handlers = []
                for called in list(func.calls)[:10]:
                    called_func = result.functions.get(called)
                    if called_func and any(ind in called_func.name.lower() for ind in event_indicators + ['handle', 'process']):
                        handlers.append(called)
                flows.append({
                    'event_source': func_name,
                    'type': 'emitter' if 'emit' in name_lower or 'trigger' in name_lower else 'handler',
                    'handlers': handlers[:5],
                    'description': func.docstring[:150] if func.docstring else 'N/A',
                })
                if len(flows) >= 20: break
        return flows

    def _analyze_data_types(self, result: AnalysisResult) -> list:
        """Analyze data types and usage."""
        data_types = {}
        type_indicators = {
            'list': ['list', 'array', 'items', 'elements', 'collection', 'sequence'],
            'dict': ['dict', 'map', 'mapping', 'key_value', 'record', 'object'],
            'str': ['string', 'text', 'content', 'message'],
            'int': ['int', 'count', 'index', 'number', 'id'],
            'float': ['float', 'decimal', 'score', 'probability'],
            'bool': ['bool', 'flag', 'is_', 'has_'],
            'tuple': ['tuple', 'pair'],
            'set': ['set', 'unique'],
        }
        for func_name, func in result.functions.items():
            name_lower = func.name.lower()
            doc = func.docstring.lower() if func.docstring else ''
            detected = [t for t, inds in type_indicators.items() if any(ind in name_lower or ind in doc for ind in inds)]
            params = self._infer_parameter_types(func)
            returns = self._infer_return_types(func)
            if detected or params or returns:
                type_key = ",".join(sorted(set(detected + params + returns)))
                if type_key not in data_types:
                    data_types[type_key] = {'type_name': type_key, 'detected_types': list(set(detected)), 'parameter_types': list(set(params)), 'return_types': list(set(returns)), 'functions': [], 'usage_count': 0, 'cross_module_usage': 0}
                data_types[type_key]['functions'].append(func_name)
                data_types[type_key]['usage_count'] += 1
                mod = func_name.rsplit('.', 1)[0] if '.' in func_name else 'root'
                for called in list(func.calls)[:10]:
                    if (called.rsplit('.', 1)[0] if '.' in called else 'root') != mod:
                        data_types[type_key]['cross_module_usage'] += 1
                        break
        return sorted(data_types.values(), key=lambda x: x['usage_count'], reverse=True)

    def _infer_parameter_types(self, func) -> list:
        params = []
        name = func.name.lower()
        if 'list' in name or 'items' in name: params.append('list')
        if 'dict' in name or 'map' in name: params.append('dict')
        if 'text' in name or 'string' in name: params.append('str')
        if 'count' in name or 'index' in name: params.append('int')
        return params

    def _infer_return_types(self, func) -> list:
        returns = []
        name = func.name.lower()
        if name.startswith(('get_', 'find_')): returns.append('dict')
        if name.startswith(('is_', 'has_')): returns.append('bool')
        if name.startswith(('count_', 'len_')): returns.append('int')
        if name.startswith(('list_', 'get_all_')): returns.append('list')
        return returns

    def _build_data_flow_graph(self, result: AnalysisResult) -> dict:
        nodes = {}
        edges = []
        for func_name, func in result.functions.items():
            nodes[func_name] = {
                'id': func_name, 'name': func.name.split('.')[-1],
                'module': func_name.rsplit('.', 1)[0] if '.' in func_name else 'root',
                'data_types': self._get_function_data_types(func),
                'in_degree': len(func.called_by), 'out_degree': len(func.calls),
                'is_hub': len(func.calls) > 5 or len(func.called_by) > 5,
            }
        for func_name, func in result.functions.items():
            for called in list(func.calls)[:15]:
                if called in result.functions:
                    edges.append({'from': func_name, 'to': called, 'data_flow': True, 'weight': 1})
        return {'nodes': nodes, 'edges': edges, 'stats': {'total_nodes': len(nodes), 'total_edges': len(edges), 'hub_nodes': sum(1 for n in nodes.values() if n['is_hub'])}}

    def _get_function_data_types(self, func) -> list:
        types = []
        name = func.name.lower()
        if 'list' in name or 'items' in name: types.append('list')
        if 'dict' in name or 'map' in name: types.append('dict')
        if 'text' in name or 'string' in name: types.append('str')
        if 'count' in name or 'index' in name: types.append('int')
        if func.docstring:
            doc = func.docstring.lower()
            if 'list' in doc: types.append('list')
            if 'dict' in doc: types.append('dict')
            if 'string' in doc or 'text' in doc: types.append('str')
        return list(set(types))

    def _identify_process_patterns(self, result: AnalysisResult) -> list:
        patterns = {'filter': [], 'map': [], 'reduce': [], 'aggregate': [], 'transform': [], 'validate': []}
        indicators = {
            'filter': ['filter', 'select', 'where', 'find'], 'map': ['map', 'transform', 'process'],
            'reduce': ['reduce', 'sum', 'count', 'aggregate'], 'aggregate': ['group', 'bucket', 'cluster'],
            'transform': ['transform', 'convert', 'normalize'], 'validate': ['validate', 'check', 'verify'],
        }
        for func_name, func in result.functions.items():
            name = func.name.lower()
            doc = func.docstring.lower() if func.docstring else ''
            for p_type, inds in indicators.items():
                if any(ind in name or ind in doc for ind in inds):
                    patterns[p_type].append({'function': func_name, 'description': func.docstring[:100] if func.docstring else 'N/A', 'data_flow': f"{len(func.called_by)} → {func_name} → {len(func.calls)}"})
                    break
        res = []
        for p_type, funcs in patterns.items():
            res.append({'pattern_type': p_type, 'functions': funcs[:10], 'count': len(funcs)})
        return sorted(res, key=lambda x: x['count'], reverse=True)

    def _analyze_optimization_opportunities(self, result: AnalysisResult, data_types: list, dfg: dict) -> dict:
        opt = {'potential_score': 0.0, 'type_consolidation': [], 'process_consolidation': [], 'hub_optimization': [], 'recommendations': []}
        similar = {}
        for dt in data_types:
            sig = ",".join(sorted(dt['detected_types']))
            if sig not in similar: similar[sig] = []
            similar[sig].append(dt)
        for sig, sims in similar.items():
            if len(sims) > 1:
                usage = sum(s['usage_count'] for s in sims)
                if usage > 10: opt['type_consolidation'].append({'type_signature': sig, 'similar_types': [s['type_name'] for s in sims], 'total_usage': usage, 'potential_reduction': len(sims)-1})
        for p in self._identify_process_patterns(result):
            if p['count'] > 5: opt['process_consolidation'].append({'pattern_type': p['pattern_type'], 'function_count': p['count'], 'potential_reduction': p['count'] // 3})
        for hub in [n for n in dfg['nodes'].values() if n['is_hub']][:10]:
            opt['hub_optimization'].append({'function': hub['id'], 'connections': hub['in_degree'] + hub['out_degree'], 'optimization_type': 'split' if hub['out_degree'] > 10 else 'cache'})
        opt['potential_score'] = (len(opt['type_consolidation']) * 10 + len(opt['process_consolidation']) * 15 + len(opt['hub_optimization']) * 5) / 100.0
        return opt
