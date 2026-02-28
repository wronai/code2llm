"""Optimized project analyzer with caching and parallel processing."""

import ast
import hashlib
import json
import os
import pickle
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from radon.complexity import cc_visit, cc_rank
import fnmatch
import networkx as nx
import vulture

from .config import Config, FAST_CONFIG, FilterConfig
from .models import (
    AnalysisResult, ClassInfo, FlowEdge, FlowNode,
    FunctionInfo, ModuleInfo, Pattern
)
from ..analysis.dfg import DFGExtractor
from ..analysis.call_graph import CallGraphExtractor
from ..analysis.coupling import CouplingAnalyzer
from ..analysis.smells import SmellDetector


class FileCache:
    """Cache for parsed AST files."""
    
    def __init__(self, cache_dir: str = ".code2flow_cache", ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_hours * 3600
    
    def _get_cache_key(self, file_path: str, content: str) -> str:
        """Generate cache key from file path and content hash."""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:16]
        return f"{Path(file_path).stem}_{content_hash}"
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path."""
        return self.cache_dir / f"{cache_key}.pkl"
    
    def get(self, file_path: str, content: str) -> Optional[Tuple[ast.AST, str]]:
        """Get cached AST if available and not expired."""
        cache_key = self._get_cache_key(file_path, content)
        cache_path = self._get_cache_path(cache_key)
        
        if not cache_path.exists():
            return None
        
        # Check TTL
        age = time.time() - cache_path.stat().st_mtime
        if age > self.ttl_seconds:
            cache_path.unlink()
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return None
    
    def put(self, file_path: str, content: str, data: Tuple[ast.AST, str]) -> None:
        """Store AST in cache."""
        cache_key = self._get_cache_key(file_path, content)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception:
            pass
    
    def clear(self) -> None:
        """Clear all cached files."""
        for f in self.cache_dir.glob("*.pkl"):
            f.unlink()


class FastFileFilter:
    """Fast file filtering with pattern matching."""
    
    def __init__(self, config: FilterConfig):
        self.config = config
        self._exclude_patterns = [p.lower() for p in config.exclude_patterns]
        self._include_patterns = [p.lower() for p in config.include_patterns]
    
    def should_process(self, file_path: str) -> bool:
        """Check if file should be processed."""
        path_lower = file_path.lower()
        
        # Check exclude patterns
        for pattern in self._exclude_patterns:
            if fnmatch.fnmatch(path_lower, pattern) or pattern in path_lower:
                return False
        
        # Check include patterns (if any)
        if self._include_patterns:
            return any(
                fnmatch.fnmatch(path_lower, p) or p in path_lower
                for p in self._include_patterns
            )
        
        return True
    
    def should_skip_function(self, name: str, line_count: int, is_private: bool = False, 
                            is_property: bool = False, is_accessor: bool = False) -> bool:
        """Check if function should be skipped."""
        if line_count < self.config.min_function_lines:
            return True
        if self.config.skip_private and is_private:
            return True
        if self.config.skip_properties and is_property:
            return True
        if self.config.skip_accessors and is_accessor:
            return True
        return False


class FileAnalyzer:
    """Analyzes a single file."""
    
    def __init__(self, config: Config, cache: Optional[FileCache] = None):
        self.config = config
        self.cache = cache
        self.stats = {
            'files_processed': 0,
            'functions_found': 0,
            'classes_found': 0,
            'nodes_created': 0,
            'cache_hits': 0,
        }
    
    def analyze_file(self, file_path: str, module_name: str) -> Dict:
        """Analyze a single Python file."""
        path = Path(file_path)
        if not path.exists():
            return {}
        
        try:
            content = path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return {}
        
        # Try cache
        if self.cache and self.config.performance.enable_cache:
            cached = self.cache.get(file_path, content)
            if cached:
                self.stats['cache_hits'] += 1
                ast_tree, _ = cached
            else:
                try:
                    ast_tree = ast.parse(content)
                    self.cache.put(file_path, content, (ast_tree, content))
                except SyntaxError:
                    return {}
        else:
            try:
                ast_tree = ast.parse(content)
            except SyntaxError:
                return {}
        
        result = self._analyze_ast(ast_tree, file_path, module_name, content)
        self.stats['files_processed'] += 1
        return result
    
    def _analyze_ast(self, tree: ast.AST, file_path: str, module_name: str, content: str) -> Dict:
        """Analyze AST and extract structure."""
        result = {
            'module': ModuleInfo(
                name=module_name,
                file=file_path,
                is_package=Path(file_path).name == '__init__.py'
            ),
            'functions': {},
            'classes': {},
            'nodes': {},
            'edges': [],
        }
        
        lines = content.split('\n')
        
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                self._process_class(node, file_path, module_name, result, lines)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._process_function(node, file_path, module_name, result, lines, None)
        
        # Calculate complexity with radon
        try:
            complexity_results = cc_visit(content)
            for entry in complexity_results:
                # Radon returns a list of objects (Function, Class, Method)
                name = getattr(entry, 'name', '')
                classname = getattr(entry, 'classname', None)
                
                if classname:
                    full_name = f"{module_name}.{classname}.{name}"
                else:
                    full_name = f"{module_name}.{name}"
                
                if full_name in result['functions']:
                    result['functions'][full_name].complexity = {
                        'cyclomatic_complexity': entry.complexity,
                        'cc_rank': cc_rank(entry.complexity)
                    }
                elif full_name in result['classes']:
                    # We can store class complexity too if needed
                    result['classes'][full_name].is_state_machine = result['classes'][full_name].is_state_machine or (entry.complexity > 20)
        except Exception as e:
            if self.config.verbose:
                print(f"Error calculating complexity for {file_path}: {e}")
        
        # New: Deep Analysis for refactoring
        try:
            dfg_ext = DFGExtractor(self.config)
            dfg_res = dfg_ext.extract(tree, module_name, file_path)
            result['mutations'] = dfg_res.mutations
            result['data_flows'] = dfg_res.data_flows
            
            # Update function calls from CG extractor which is more robust
            cg_ext = CallGraphExtractor(self.config)
            cg_res = cg_ext.extract(tree, module_name, file_path)
            for func_name, cg_func in cg_res.functions.items():
                if func_name in result['functions']:
                    result['functions'][func_name].calls.extend(list(cg_func.calls))
        except Exception as e:
            if self.config.verbose:
                print(f"Error in deep analysis for {file_path}: {e}")

        self.stats['files_processed'] += 1
        return result
    
    def _process_class(self, node: ast.ClassDef, file_path: str, module_name: str, 
                       result: Dict, lines: List[str]) -> None:
        """Process class definition."""
        class_name = node.name
        qualified_name = f"{module_name}.{class_name}"
        
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                method_name = item.name
                qualified_method = f"{qualified_name}.{method_name}"
                methods.append(qualified_method)
                self._process_function(item, file_path, module_name, result, lines, class_name)
        
        result['classes'][qualified_name] = ClassInfo(
            name=class_name,
            qualified_name=qualified_name,
            file=file_path,
            line=node.lineno,
            module=module_name,
            bases=[self._get_base_name(b) for b in node.bases],
            methods=methods,
            docstring=ast.get_docstring(node),
        )
        result['module'].classes.append(qualified_name)
        self.stats['classes_found'] += 1
    
    def _process_function(self, node: ast.FunctionDef, file_path: str, module_name: str,
                          result: Dict, lines: List[str], class_name: Optional[str]) -> None:
        """Process function definition with limited CFG depth."""
        func_name = node.name
        if class_name:
            qualified_name = f"{module_name}.{class_name}.{func_name}"
        else:
            qualified_name = f"{module_name}.{func_name}"
        
        # Check filtering - use FastFileFilter for function-level filtering
        line_count = (node.end_lineno - node.lineno + 1) if node.end_lineno else 1
        is_private = func_name.startswith('_')
        is_property = any(
            isinstance(d, ast.Name) and d.id == 'property' 
            for d in node.decorator_list
        )
        
        filter_obj = FastFileFilter(self.config.filters)
        if filter_obj.should_skip_function(func_name, line_count, is_private, is_property):
            return
        
        # Create function info
        func_info = FunctionInfo(
            name=func_name,
            qualified_name=qualified_name,
            file=file_path,
            line=node.lineno,
            column=node.col_offset,
            module=module_name,
            class_name=class_name,
            is_method=class_name is not None,
            is_private=is_private,
            is_property=is_property,
            docstring=ast.get_docstring(node),
            args=[arg.arg for arg in node.args.args],
            decorators=[self._get_decorator_name(d) for d in node.decorator_list],
        )
        
        # Build simplified CFG with depth limit
        if not self.config.performance.skip_data_flow:
            self._build_cfg(node, qualified_name, func_info, result)
        
        # Find calls
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                called_name = self._get_call_name(child.func)
                if called_name:
                    func_info.calls.append(called_name)
        
        result['functions'][qualified_name] = func_info
        result['module'].functions.append(qualified_name)
        self.stats['functions_found'] += 1
    
    def _build_cfg(self, node: ast.FunctionDef, func_name: str, 
                   func_info: FunctionInfo, result: Dict) -> None:
        """Build simplified control flow graph with depth limit."""
        max_depth = self.config.depth.max_cfg_depth
        
        entry_id = f"{func_name}_entry"
        exit_id = f"{func_name}_exit"
        
        # Create entry/exit nodes
        result['nodes'][entry_id] = FlowNode(
            id=entry_id, type='ENTRY', label='entry', function=func_name
        )
        result['nodes'][exit_id] = FlowNode(
            id=exit_id, type='EXIT', label='exit', function=func_name
        )
        
        func_info.cfg_nodes.extend([entry_id, exit_id])
        
        func_info.cfg_entry = entry_id
        func_info.cfg_exit = exit_id
        
        # Build CFG with depth limiting
        self._process_cfg_block(node.body, entry_id, exit_id, func_name, 
                               func_info, result, depth=0, max_depth=max_depth)
        
        self.stats['nodes_created'] += len(result['nodes'])
    
    def _process_cfg_block(self, body: List[ast.stmt], entry: str, exit: str,
                            func_name: str, func_info: FunctionInfo, result: Dict, depth: int, max_depth: int) -> str:
        """Process a block of statements for CFG with depth limiting."""
        if depth >= max_depth:
            # Connect directly to exit if depth exceeded
            result['edges'].append(FlowEdge(source=entry, target=exit))
            return exit
        
        current = entry
        for stmt in body:
            if isinstance(stmt, ast.If):
                # Create branch node
                node_id = f"{func_name}_if_{stmt.lineno}"
                result['nodes'][node_id] = FlowNode(
                    id=node_id, type='IF', label='if', function=func_name,
                    line=stmt.lineno
                )
                func_info.cfg_nodes.append(node_id)
                result['edges'].append(FlowEdge(source=current, target=node_id))
                
                # Process branches
                then_exit = self._process_cfg_block(
                    stmt.body, node_id, exit, func_name, func_info, result, depth + 1, max_depth
                )
                if stmt.orelse:
                    else_exit = self._process_cfg_block(
                        stmt.orelse, node_id, exit, func_name, func_info, result, depth + 1, max_depth
                    )
                else:
                    else_exit = node_id
                
                # Merge point
                current = f"{func_name}_merge_{stmt.lineno}"
                result['nodes'][current] = FlowNode(
                    id=current, type='FUNC', label='merge', function=func_name
                )
                func_info.cfg_nodes.append(current)
                result['edges'].append(FlowEdge(source=then_exit, target=current))
                if else_exit != node_id:
                    result['edges'].append(FlowEdge(source=else_exit, target=current))
            
            elif isinstance(stmt, (ast.For, ast.While)):
                node_id = f"{func_name}_loop_{stmt.lineno}"
                loop_type = 'FOR' if isinstance(stmt, ast.For) else 'WHILE'
                result['nodes'][node_id] = FlowNode(
                    id=node_id, type=loop_type, label=loop_type.lower(), 
                    function=func_name, line=stmt.lineno
                )
                func_info.cfg_nodes.append(node_id)
                result['edges'].append(FlowEdge(source=current, target=node_id))
                
                # Limit loop body depth even more
                self._process_cfg_block(
                    stmt.body, node_id, node_id, func_name, func_info, result, depth + 2, max_depth
                )
                current = node_id
            
            elif isinstance(stmt, ast.Return):
                node_id = f"{func_name}_return_{stmt.lineno}"
                result['nodes'][node_id] = FlowNode(
                    id=node_id, type='RETURN', label='return', 
                    function=func_name, line=stmt.lineno
                )
                func_info.cfg_nodes.append(node_id)
                result['edges'].append(FlowEdge(source=current, target=node_id))
                result['edges'].append(FlowEdge(source=node_id, target=exit))
                return exit
        
        if current != exit:
            result['edges'].append(FlowEdge(source=current, target=exit))
        
        return exit
    
    def _get_base_name(self, node: ast.expr) -> str:
        """Extract base class name."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_base_name(node.value)}.{node.attr}"
        return str(node)
    
    def _get_decorator_name(self, node: ast.expr) -> str:
        """Extract decorator name."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            return node.func.id
        return ""
    
    def _get_call_name(self, node: ast.expr) -> Optional[str]:
        """Extract function name from call."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_call_name(node.value)}.{node.attr}"
        return None


def _analyze_single_file(args):
    """Analyze single file - module level function for pickle compatibility."""
    file_path, module_name, config_dict = args
    from .config import Config
    config = Config(**config_dict)
    analyzer = FileAnalyzer(config, None)
    return analyzer.analyze_file(file_path, module_name)


class ProjectAnalyzer:
    """Main analyzer with parallel processing."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or FAST_CONFIG
        self.cache = FileCache(
            self.config.performance.cache_dir,
            self.config.performance.cache_ttl_hours
        ) if self.config.performance.enable_cache else None
        self.file_filter = FastFileFilter(self.config.filters)
    
    def analyze_project(self, project_path: str) -> AnalysisResult:
        """Analyze entire project."""
        start_time = time.time()
        
        project_path = Path(project_path).resolve()
        if not project_path.exists():
            raise FileNotFoundError(f"Project path does not exist: {project_path}")
        
        # Collect Python files
        files = self._collect_files(project_path)
        
        if self.config.verbose:
            print(f"Found {len(files)} files to analyze")
        
        # Analyze files
        if self.config.performance.parallel_enabled and len(files) > 1:
            results = self._analyze_parallel(files)
        else:
            results = self._analyze_sequential(files)
        
        # Merge results
        merged = self._merge_results(results, str(project_path))
        
        # Build call graph
        self._build_call_graph(merged)
        
        if not self.config.performance.skip_pattern_detection:
            self._detect_patterns(merged)
            
        # New: Refactoring analysis
        self._perform_refactoring_analysis(merged)
        
        # Calculate stats
        elapsed = time.time() - start_time
        merged.stats = {
            'files_processed': len(files),
            'functions_found': len(merged.functions),
            'classes_found': len(merged.classes),
            'nodes_created': len(merged.nodes),
            'edges_created': len(merged.edges),
            'patterns_detected': len(merged.patterns),
            'analysis_time_seconds': round(elapsed, 2),
            'cache_hits': sum(r.get('cache_hits', 0) for r in results),
        }
        
        if self.config.verbose:
            print(f"Analysis complete in {elapsed:.2f}s")
            print(f"  Functions: {len(merged.functions)}")
            print(f"  Classes: {len(merged.classes)}")
            print(f"  CFG Nodes: {len(merged.nodes)}")
            print(f"  Patterns: {len(merged.patterns)}")
        
        return merged
    
    def _collect_files(self, project_path: Path) -> List[Tuple[str, str]]:
        """Collect all Python files with their module names."""
        files = []
        
        for py_file in project_path.rglob("*.py"):
            file_str = str(py_file)
            if not self.file_filter.should_process(file_str):
                continue
            
            # Calculate module name
            rel_path = py_file.relative_to(project_path)
            parts = list(rel_path.parts)[:-1]  # Remove .py
            if py_file.name == '__init__.py':
                module_name = '.'.join(parts) if parts else project_path.name
            else:
                module_name = '.'.join(parts + [py_file.stem])
            
            files.append((file_str, module_name))
        
        return files
    
    def _analyze_parallel(self, files: List[Tuple[str, str]]) -> List[Dict]:
        """Analyze files in parallel."""
        results = []
        workers = min(self.config.performance.parallel_workers, len(files))
        
        # Convert config to dict for pickle compatibility
        config_dict = {
            'mode': self.config.mode,
            'max_depth_enumeration': self.config.max_depth_enumeration,
            'detect_state_machines': self.config.detect_state_machines,
            'detect_recursion': self.config.detect_recursion,
            'output_dir': self.config.output_dir,
        }
        
        # Prepare args with config dict
        args_list = [(f[0], f[1], config_dict) for f in files]
        
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(_analyze_single_file, a): a for a in args_list}
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    if self.config.verbose:
                        print(f"Error analyzing {futures[future]}: {e}")
        
        return results
    
    def _analyze_sequential(self, files: List[Tuple[str, str]]) -> List[Dict]:
        """Analyze files sequentially."""
        results = []
        analyzer = FileAnalyzer(self.config, self.cache)
        
        for file_path, module_name in files:
            result = analyzer.analyze_file(file_path, module_name)
            if result:
                results.append(result)
        
        return results
    
    def _merge_results(self, results: List[Dict], project_path: str) -> AnalysisResult:
        """Merge all file analysis results."""
        merged = AnalysisResult(
            project_path=project_path,
            analysis_mode=self.config.mode,
        )
        
        for r in results:
            if 'module' in r:
                mod = r['module']
                merged.modules[mod.name] = mod
            if 'functions' in r:
                merged.functions.update(r['functions'])
            if 'classes' in r:
                merged.classes.update(r['classes'])
            if 'nodes' in r:
                merged.nodes.update(r['nodes'])
            if 'edges' in r:
                merged.edges.extend(r['edges'])
            if 'mutations' in r:
                merged.mutations.extend(r['mutations'])
            if 'data_flows' in r:
                merged.data_flows.update(r['data_flows'])
        
        return merged
    
    def _build_call_graph(self, result: AnalysisResult) -> None:
        """Build call graph and find entry points."""
        # Map calls between functions
        for func_name, func in result.functions.items():
            for called in func.calls:
                # Try to resolve to a known function
                for known_name in result.functions:
                    if known_name.endswith(f".{called}") or known_name == called:
                        func.calls[func.calls.index(called)] = known_name
                        result.functions[known_name].called_by.append(func_name)
                        break
        
        # Find entry points (not called by anything)
        for func_name, func in result.functions.items():
            if not func.called_by:
                result.entry_points.append(func_name)
    
    def _detect_patterns(self, result: AnalysisResult) -> None:
        """Detect behavioral patterns."""
        # Detect recursion
        for func_name, func in result.functions.items():
            if func_name in func.calls:
                result.patterns.append(Pattern(
                    name=f"recursion_{func.name}",
                    type="recursion",
                    confidence=0.9,
                    functions=[func_name],
                    entry_points=[func_name],
                ))
        
        # Detect state machines (simple heuristic)
        for class_name, cls in result.classes.items():
            state_methods = [m for m in cls.methods if any(
                s in m.lower() for s in ['state', 'transition', 'enter', 'exit', 'connect', 'disconnect']
            )]
            if len(state_methods) >= 2:
                cls.is_state_machine = True
                result.patterns.append(Pattern(
                    name=f"state_machine_{cls.name}",
                    type="state_machine",
                    confidence=0.7,
                    functions=cls.methods,
                    entry_points=cls.methods[:1],
                ))

    def _perform_refactoring_analysis(self, result: AnalysisResult) -> None:
        """Perform deep analysis and detect code smells."""
        if self.config.verbose:
            print("Performing refactoring analysis...")
            
        # 1. Calculate metrics (fan-in/fan-out)
        cg_ext = CallGraphExtractor(self.config)
        cg_ext.result = result
        cg_ext._calculate_metrics()
        
        # 2. Build networkx graph for project-level analysis
        G = nx.DiGraph()
        for func_name, func_info in result.functions.items():
            G.add_node(func_name)
            for callee in func_info.calls:
                G.add_edge(func_name, callee)
        
        # 3. Calculate Betweenness Centrality (Bottlenecks)
        if len(G) > 0:
            try:
                centrality = nx.betweenness_centrality(G)
                for func_name, score in centrality.items():
                    if func_name in result.functions:
                        result.functions[func_name].centrality = score
            except Exception as e:
                if self.config.verbose:
                    print(f"Error calculating centrality: {e}")
            
            # 4. Detect Circular Dependencies
            try:
                cycles = list(nx.simple_cycles(G))
                if cycles:
                    result.metrics["project"] = result.metrics.get("project", {})
                    result.metrics["project"]["circular_dependencies"] = cycles
            except Exception as e:
                if self.config.verbose:
                    print(f"Error detecting cycles: {e}")

            # 5. Community Detection (Module groups)
            try:
                from networkx.algorithms import community
                # Using Louvain if available, otherwise greedy modularity
                if hasattr(community, 'louvain_communities'):
                    communities = community.louvain_communities(G.to_undirected())
                else:
                    communities = community.greedy_modularity_communities(G.to_undirected())
                
                result.coupling["communities"] = [list(c) for c in communities]
            except Exception as e:
                if self.config.verbose:
                    print(f"Error in community detection: {e}")
        
        # 6. Analyze coupling
        coupling_analyzer = CouplingAnalyzer(result)
        coupling_analyzer.analyze()
        
        # 7. Detect code smells
        smell_detector = SmellDetector(result)
        smell_detector.detect()
        
        # 8. Dead code detection with vulture
        self._detect_dead_code(result)
        
        if self.config.verbose:
            print(f"  Detected {len(result.smells)} code smells")

    def _detect_dead_code(self, result: AnalysisResult) -> None:
        """Use vulture to find dead code and update reachability."""
        if self.config.verbose:
            print("Detecting dead code with vulture...")
            
        try:
            v = vulture.Vulture(verbose=False)
            
            # vulture.scan takes the code content as a string
            for py_file in Path(result.project_path).rglob("*.py"):
                if not self.file_filter.should_process(str(py_file)):
                    continue
                try:
                    content = py_file.read_text(encoding='utf-8', errors='ignore')
                    v.scan(content, filename=str(py_file))
                except Exception:
                    continue
                    
            dead_code = v.get_unused_code()
            
            if self.config.verbose:
                print(f"  Vulture found {len(dead_code)} unused items")
            
            # Map unused code to our functions/classes
            for item in dead_code:
                if self.config.verbose:
                    item_lineno = getattr(item, 'lineno', getattr(item, 'first_lineno', 0))
                    print(f"  Vulture item: {item.filename}:{item_lineno} ({item.typ})")
                    
                # Match by file and line
                item_path = Path(item.filename).resolve()
                item_lineno = getattr(item, 'lineno', getattr(item, 'first_lineno', 0))
                for func_name, func_info in result.functions.items():
                    func_path = Path(func_info.file).resolve()
                    if func_path == item_path and func_info.line == item_lineno:
                        func_info.reachability = "unreachable"
                        
                for class_name, class_info in result.classes.items():
                    if Path(class_info.file).resolve() == Path(item.filename).resolve() and class_info.line == item.lineno:
                        class_info.reachability = "unreachable" # (if we add reachability to ClassInfo too)
                        
            # Mark others as reachable if they are NOT orphans
            for func_name, func_info in result.functions.items():
                if func_info.reachability == "unknown":
                    if func_info.called_by or func_name in result.entry_points:
                        func_info.reachability = "reachable"
        except Exception as e:
            if self.config.verbose:
                print(f"Error in dead code detection: {e}")
