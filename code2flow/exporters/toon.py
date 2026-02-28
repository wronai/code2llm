"""Toon Exporter - Optimized compact format for code2flow."""

import yaml
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict

from ..core.models import AnalysisResult


class ToonExporter:
    """Export to optimized toon format with enhanced sorting and compression."""
    
    def __init__(self):
        self.complexity_weights = {
            'FOR': 2, 'WHILE': 2,      # Loops are most complex
            'IF': 1,                   # Conditions add complexity
            'method_call': 1,          # Method calls add complexity
            'assign': 0.5,             # Assignments add minor complexity
            'RETURN': 0.5              # Returns add minor complexity
        }
    
    def export(self, result: AnalysisResult, output_path: str, **kwargs) -> None:
        """Export analysis result to toon format."""
        toon_data = self._build_toon_data(result)
        
        # Optimize sorting and structure
        toon_data = self._optimize_structure(toon_data)
        
        # Save with optimized YAML settings
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(toon_data, f, 
                     default_flow_style=True, 
                     sort_keys=False,
                     allow_unicode=True,
                     width=120)  # Wider width for better readability
    
    def _build_toon_data(self, result: AnalysisResult) -> Dict[str, Any]:
        """Build comprehensive toon format from analysis result."""
        # Initialize structure
        toon_data = {
            'meta': {
                'project': result.project_path,
                'mode': result.analysis_mode,
                'generated': self._get_timestamp(),
                'version': '2.0'
            },
            'stats': result.stats,
            'functions': [],
            'classes': [],
            'modules': [],
            'patterns': [],
            'call_graph': [],
            'insights': {}
        }
        
        # Process functions with optimized analysis
        function_analysis = self._analyze_functions(result)
        toon_data['functions'] = function_analysis['functions']
        
        # Build classes and modules from function data
        toon_data['classes'] = self._build_classes(function_analysis['functions'])
        toon_data['modules'] = self._build_modules(function_analysis['functions'])
        
        # Extract patterns and call graph
        toon_data['patterns'] = self._extract_patterns(result)
        toon_data['call_graph'] = self._build_call_graph(result)
        
        # Generate insights
        toon_data['insights'] = self._generate_insights(toon_data)
        
        return toon_data
    
    def _analyze_functions(self, result: AnalysisResult) -> Dict[str, Any]:
        """Analyze functions with optimized complexity calculation."""
        function_nodes = defaultdict(list)
        
        # Group nodes by function
        for node_id, node_data in result.nodes.items():
            func_name = getattr(node_data, 'function', '')
            if func_name:
                function_nodes[func_name].append(node_data)
        
        functions = []
        complexity_distribution = defaultdict(int)
        
        for func_name, nodes in function_nodes.items():
            # Calculate complexity using weighted system
            complexity_score = self._calculate_complexity(nodes)
            complexity_distribution[self._get_complexity_tier(complexity_score)] += 1
            
            # Skip detailed entry if complexity is low (CC < 3.0),
            # but still keep it in distribution/averages
            if complexity_score < 3.0:
                continue

            # Extract function characteristics in compact trait format
            traits = self._extract_traits(nodes)
            
            # Build function entry
            func_entry = {
                'name': func_name.split('.')[-1] if '.' in func_name else func_name,
                'module': func_name.rsplit('.', 1)[0] if '.' in func_name else 'root',
                'complexity': complexity_score,
                'tier': self._get_complexity_tier(complexity_score),
                'nodes': len(nodes),
                'traits': traits,
                'exits': len([n for n in nodes if getattr(n, 'type', '') in ['EXIT', 'RETURN']])
            }
            
            functions.append(func_entry)
        
        return {
            'functions': functions,
            'complexity_distribution': dict(complexity_distribution)
        }
    
    def _calculate_complexity(self, nodes) -> float:
        """Calculate weighted complexity score."""
        complexity = 0.0
        
        for node in nodes:
            node_type = getattr(node, 'type', 'FUNC')
            complexity += self.complexity_weights.get(node_type, 0)
        
        # Add size-based complexity
        if len(nodes) > 20:
            complexity += 2
        elif len(nodes) > 10:
            complexity += 1
        
        return round(complexity, 2)
    
    def _get_complexity_tier(self, score: float) -> str:
        """Get complexity tier from score."""
        if score >= 5:
            return 'critical'
        elif score >= 3:
            return 'high'
        elif score >= 1.5:
            return 'medium'
        elif score > 0:
            return 'low'
        else:
            return 'basic'
    
    def _extract_traits(self, nodes) -> list:
        """Extract function traits in compact list format."""
        node_types = set(getattr(node, 'type', 'FUNC') for node in nodes)
        traits = []
        
        if any(t in ['FOR', 'WHILE'] for t in node_types): traits.append('loops')
        if 'IF' in node_types: traits.append('conditions')
        if 'RETURN' in node_types: traits.append('returns')
        if 'assign' in node_types: traits.append('assigns')
        if 'method_call' in node_types: traits.append('calls')
        
        return traits
    
    def _build_classes(self, functions: list) -> list:
        """Build class information from function data."""
        class_map = {}
        
        for func in functions:
            module_parts = func['module'].split('.')
            
            # Look for class patterns (module.ClassName)
            if len(module_parts) >= 2 and module_parts[-1][0].isupper():
                class_name = module_parts[-1]
                module_name = '.'.join(module_parts[:-1])
                
                class_key = f"{module_name}.{class_name}"
                
                if class_key not in class_map:
                    class_map[class_key] = {
                        'name': class_name,
                        'module': module_name,
                        'methods': [],
                        'method_count': 0,
                        'complexity_scores': [],
                        'total_nodes': 0
                    }
                
                class_map[class_key]['methods'].append(func['name'])
                class_map[class_key]['method_count'] += 1
                class_map[class_key]['complexity_scores'].append(func['complexity'])
                class_map[class_key]['total_nodes'] += func['nodes']
        
        # Calculate class-level metrics
        classes = []
        for class_data in class_map.values():
            if class_data['method_count'] > 0:
                class_data['avg_complexity'] = round(
                    sum(class_data['complexity_scores']) / len(class_data['complexity_scores']), 2
                )
                class_data['max_complexity'] = max(class_data['complexity_scores'])
                class_data['complex_methods'] = len([
                    c for c in class_data['complexity_scores'] if c >= 3
                ])
                
                # Remove temporary arrays
                del class_data['complexity_scores']
                classes.append(class_data)
        
        return classes
    
    def _build_modules(self, functions: list) -> list:
        """Build module information from function data."""
        module_map = {}
        
        for func in functions:
            module = func['module']
            
            if module not in module_map:
                module_map[module] = {
                    'name': module,
                    'functions': [],
                    'function_count': 0,
                    'complexity_scores': [],
                    'total_nodes': 0,
                    'tiers': defaultdict(int)
                }
            
            module_map[module]['functions'].append(func['name'])
            module_map[module]['function_count'] += 1
            module_map[module]['complexity_scores'].append(func['complexity'])
            module_map[module]['total_nodes'] += func['nodes']
            module_map[module]['tiers'][func['tier']] += 1
        
        # Calculate module-level metrics
        modules = []
        for module_data in module_map.values():
            if module_data['function_count'] > 0:
                scores = module_data['complexity_scores']
                module_data['avg_complexity'] = round(sum(scores) / len(scores), 2)
                module_data['max_complexity'] = max(scores)
                module_data['complex_functions'] = len([c for c in scores if c >= 3])
                module_data['critical_functions'] = len([c for c in scores if c >= 5])
                
                # Convert tiers to regular dict
                module_data['complexity_distribution'] = dict(module_data['tiers'])
                del module_data['tiers']
                del module_data['complexity_scores']
                
                modules.append(module_data)
        
        return modules
    
    def _extract_patterns(self, result: AnalysisResult) -> list:
        """Extract code patterns with enhanced analysis."""
        pattern_counts = defaultdict(lambda: {'functions': [], 'count': 0})
        
        for node_id, node_data in result.nodes.items():
            node_type = getattr(node_data, 'type', 'FUNC')
            
            if node_type in ['god_function', 'feature_envy', 'shotgun_surgery', 'data_clump', 'state_machine']:
                func_name = getattr(node_data, 'function', '')
                if func_name:
                    pattern_counts[node_type]['functions'].append(func_name)
                    pattern_counts[node_type]['count'] += 1
        
        # Build pattern list with severity assessment
        patterns = []
        severity_map = {
            'god_function': 'critical',
            'shotgun_surgery': 'high',
            'feature_envy': 'medium',
            'data_clump': 'medium',
            'state_machine': 'low'
        }
        
        for pattern_type, data in pattern_counts.items():
            if data['count'] > 0:
                patterns.append({
                    'type': pattern_type,
                    'severity': severity_map.get(pattern_type, 'unknown'),
                    'count': data['count'],
                    'functions': data['functions'][:10],  # Limit for readability
                    'percentage': round((data['count'] / len(result.functions)) * 100, 1)
                })
        
        return sorted(patterns, key=lambda x: x['count'], reverse=True)
    
    def _build_call_graph(self, result: AnalysisResult) -> list:
        """Build optimized call graph with importance scoring."""
        call_counts = defaultdict(lambda: {'calls': [], 'call_count': 0, 'targets': set()})
        
        # Analyze edges
        for edge in result.edges:
            source = getattr(edge, 'source', '')
            target = getattr(edge, 'target', '')
            
            if source and target:
                call_counts[source]['calls'].append(target)
                call_counts[source]['call_count'] += 1
                call_counts[source]['targets'].add(target)
        
        # Build call graph with importance metrics
        call_graph = []
        for caller, data in call_counts.items():
            if data['call_count'] >= 2:  # Only include significant callers
                entry = {
                    'function': caller.split('.')[-1] if '.' in caller else caller,
                    'module': caller.rsplit('.', 1)[0] if '.' in caller else 'root',
                    'calls_count': data['call_count'],
                    'unique_targets': len(data['targets']),
                    'targets': list(data['targets'])[:5],  # Top 5 targets
                    'importance': self._calculate_importance(data['call_count'], len(data['targets']))
                }
                call_graph.append(entry)
        
        return sorted(call_graph, key=lambda x: x['importance'], reverse=True)
    
    def _calculate_importance(self, call_count: int, target_count: int) -> float:
        """Calculate importance score for call graph entry."""
        # Importance based on call volume and diversity
        return round((call_count * 0.7 + target_count * 0.3), 2)
    
    def _generate_insights(self, toon_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights and recommendations."""
        functions = toon_data['functions']
        classes = toon_data['classes']
        modules = toon_data['modules']
        patterns = toon_data['patterns']
        
        insights = {
            'complexity_summary': {
                'critical_functions': len([f for f in functions if f['tier'] == 'critical']),
                'high_complexity': len([f for f in functions if f['tier'] == 'high']),
                'avg_complexity': round(sum(f['complexity'] for f in functions) / len(functions), 2)
            },
            'top_complex_modules': sorted(
                modules, 
                key=lambda x: x['avg_complexity'], 
                reverse=True
            )[:5],
            'pattern_summary': {
                'total_patterns': len(patterns),
                'critical_patterns': len([p for p in patterns if p['severity'] == 'critical']),
                'high_severity_patterns': len([p for p in patterns if p['severity'] == 'high'])
            },
            'recommendations': self._generate_recommendations(toon_data)
        }
        
        return insights
    
    def _generate_recommendations(self, toon_data: Dict[str, Any]) -> list:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Complexity recommendations
        critical_funcs = len([f for f in toon_data['functions'] if f['tier'] == 'critical'])
        if critical_funcs > 0:
            recommendations.append({
                'type': 'complexity',
                'priority': 'high',
                'message': f"Refactor {critical_funcs} critical functions to improve maintainability"
            })
        
        # Pattern recommendations
        critical_patterns = [p for p in toon_data['patterns'] if p['severity'] == 'critical']
        if critical_patterns:
            recommendations.append({
                'type': 'patterns',
                'priority': 'critical',
                'message': f"Address {len(critical_patterns)} critical code patterns"
            })
        
        # Module recommendations
        complex_modules = [m for m in toon_data['modules'] if m['avg_complexity'] > 4]
        if complex_modules:
            recommendations.append({
                'type': 'modules',
                'priority': 'medium',
                'message': f"Consider splitting {len(complex_modules)} highly complex modules"
            })
        
        return recommendations
    
    def _optimize_structure(self, toon_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize data structure for better performance and readability."""
        # Sort functions by complexity (highest first)
        toon_data['functions'].sort(key=lambda x: (x['complexity'], x['module'], x['name']), reverse=True)
        
        # Sort classes by method count and complexity
        toon_data['classes'].sort(key=lambda x: (x['method_count'], x['avg_complexity']), reverse=True)
        
        # Sort modules by complexity and function count
        toon_data['modules'].sort(key=lambda x: (x['avg_complexity'], x['function_count']), reverse=True)
        
        # Limit call graph to top entries for readability
        if len(toon_data['call_graph']) > 50:
            toon_data['call_graph'] = toon_data['call_graph'][:50]
        
        return toon_data
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
