"""File analyzer for analyzing individual source files across multiple languages."""

import ast
from pathlib import Path
from typing import Dict, List, Optional

from radon.complexity import cc_visit, cc_rank

from .config import Config
from .models import ClassInfo, FlowEdge, FlowNode, FunctionInfo, ModuleInfo
from code2llm.analysis.dfg import DFGExtractor
from code2llm.analysis.call_graph import CallGraphExtractor
from .file_filter import FastFileFilter
from .source_classifier import classify_source_path
from .lang import (
    analyze_typescript_js, analyze_go, analyze_rust, analyze_java,
    analyze_cpp, analyze_csharp, analyze_php, analyze_ruby, analyze_generic,
)


class FileAnalyzer:
    """Analyzes a single file."""
    
    def __init__(self, config: Config, cache=None):
        self.config = config
        self.cache = cache
        self._file_filter = FastFileFilter(config.filters)
        self.stats = {
            'files_processed': 0,
            'functions_found': 0,
            'classes_found': 0,
            'nodes_created': 0,
            'cache_hits': 0,
        }
    
    def _route_to_language_analyzer(self, content: str, file_path: str,
                                    module_name: str, ext: str) -> Dict:
        """Dispatch file content to the correct language analyzer."""
        if ext == '.py':
            return self._analyze_python(content, file_path, module_name)
        if ext in ('.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs'):
            return analyze_typescript_js(content, file_path, module_name, ext, self.stats)
        if ext == '.go':
            return analyze_go(content, file_path, module_name, ext, self.stats)
        if ext == '.rs':
            return analyze_rust(content, file_path, module_name, ext, self.stats)
        if ext == '.java':
            return analyze_java(content, file_path, module_name, ext, self.stats)
        if ext in ('.c', '.cpp', '.cc', '.h', '.hpp', '.hh', '.cxx', '.hxx'):
            return analyze_cpp(content, file_path, module_name, ext, self.stats)
        if ext in ('.cs', '.csharp'):
            return analyze_csharp(content, file_path, module_name, ext, self.stats)
        if ext == '.php':
            return analyze_php(content, file_path, module_name, ext, self.stats)
        if ext in ('.rb', '.ruby'):
            return analyze_ruby(content, file_path, module_name, ext, self.stats)
        return analyze_generic(content, file_path, module_name, ext, self.stats)

    def analyze_file(self, file_path: str, module_name: str) -> Dict:
        """Analyze a single source file based on its language."""
        path = Path(file_path)
        if not path.exists():
            return {}

        if self.cache and self.config.performance.enable_cache:
            cached = self.cache.get_fast(file_path)
            if cached:
                self.stats['cache_hits'] += 1
                if 'file' not in cached:
                    cached['file'] = file_path
                return cached

        ext = path.suffix.lower()
        try:
            content = path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return {}

        result = self._route_to_language_analyzer(content, file_path, module_name, ext)
        if result and result.get('module'):
            result['module'].line_count = len(content.splitlines())
            result['module'].source_kind = classify_source_path(file_path)

        # Tag result with its source file so downstream callers
        # (e.g. PersistentCache in ProjectAnalyzer._store_to_persistent_cache)
        # can match results back to file paths. Without this, the persistent
        # manifest never gets populated and the export-level cache key
        # collapses to md5("{}")[:12], causing stale exports to be reused.
        if result:
            result['file'] = file_path

        if self.cache and self.config.performance.enable_cache and result:
            self.cache.put_fast(file_path, result)

        return result
    
    def _analyze_python(self, content: str, file_path: str, module_name: str) -> Dict:
        """Analyze Python file using AST."""
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
        
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                self._process_class(node, file_path, module_name, result)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._process_function(node, file_path, module_name, result, None)
        
        # Calculate complexity with radon
        self._calculate_complexity(content, file_path, result)
        
        # Deep Analysis for refactoring (skip when data flow not needed)
        if not self.config.performance.skip_data_flow:
            self._perform_deep_analysis(tree, module_name, file_path, result)

        self.stats['files_processed'] += 1
        return result

    def _calculate_complexity(self, content: str, file_path: str, result: Dict) -> None:
        """Calculate cyclomatic complexity using radon."""
        try:
            complexity_results = cc_visit(content)
            for entry in complexity_results:
                # Radon returns a list of objects (Function, Class, Method)
                name = getattr(entry, 'name', '')
                classname = getattr(entry, 'classname', None)
                
                if classname:
                    full_name = f"{result['module'].name}.{classname}.{name}"
                else:
                    full_name = f"{result['module'].name}.{name}"
                
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

    def _perform_deep_analysis(self, tree: ast.AST, module_name: str, file_path: str, result: Dict) -> None:
        """Perform deep analysis including DFG and call graph extraction."""
        try:
            dfg_ext = DFGExtractor(self.config)
            dfg_res = dfg_ext.extract(tree, module_name, file_path)
            result['mutations'] = dfg_res.mutations
            result['data_flows'] = dfg_res.data_flows
            
            # Update function calls from CG extractor which is more robust.
            # Use set-based merge to avoid duplicate call entries (ast.walk
            # in _process_function already extracts calls).
            cg_ext = CallGraphExtractor(self.config)
            cg_res = cg_ext.extract(tree, module_name, file_path)
            for func_name, cg_func in cg_res.functions.items():
                if func_name in result['functions']:
                    existing = set(result['functions'][func_name].calls)
                    for c in cg_func.calls:
                        if c not in existing:
                            result['functions'][func_name].calls.append(c)
                            existing.add(c)
        except Exception as e:
            if self.config.verbose:
                print(f"Error in deep analysis for {file_path}: {e}")
    
    def _process_class(self, node: ast.ClassDef, file_path: str, module_name: str, 
                       result: Dict) -> None:
        """Process class definition."""
        class_name = node.name
        qualified_name = f"{module_name}.{class_name}"
        
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                method_name = item.name
                qualified_method = f"{qualified_name}.{method_name}"
                methods.append(qualified_method)
                self._process_function(item, file_path, module_name, result, class_name)
        
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
                          result: Dict, class_name: Optional[str]) -> None:
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
        
        if self._file_filter.should_skip_function(line_count, is_private, is_property):
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
                current = self._process_if_stmt(stmt, current, exit, func_name, func_info, result, depth, max_depth)
            elif isinstance(stmt, (ast.For, ast.While)):
                current = self._process_loop_stmt(stmt, current, func_name, func_info, result, depth, max_depth)
            elif isinstance(stmt, ast.Return):
                return self._process_return_stmt(stmt, current, exit, func_name, func_info, result)
        
        if current != exit:
            result['edges'].append(FlowEdge(source=current, target=exit))
        
        return exit

    def _process_if_stmt(self, stmt: ast.If, current: str, exit: str, func_name: str, 
                         func_info: FunctionInfo, result: Dict, depth: int, max_depth: int) -> str:
        """Process if statement for CFG."""
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
        
        return current

    def _process_loop_stmt(self, stmt: ast.For | ast.While, current: str, func_name: str,
                           func_info: FunctionInfo, result: Dict, depth: int, max_depth: int) -> str:
        """Process loop statement for CFG."""
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
        return node_id

    def _process_return_stmt(self, stmt: ast.Return, current: str, exit: str, func_name: str,
                             func_info: FunctionInfo, result: Dict) -> str:
        """Process return statement for CFG."""
        node_id = f"{func_name}_return_{stmt.lineno}"
        result['nodes'][node_id] = FlowNode(
            id=node_id, type='RETURN', label='return', 
            function=func_name, line=stmt.lineno
        )
        func_info.cfg_nodes.append(node_id)
        result['edges'].append(FlowEdge(source=current, target=node_id))
        result['edges'].append(FlowEdge(source=node_id, target=exit))
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
    from code2llm.core.config import Config
    config = Config(**config_dict)
    analyzer = FileAnalyzer(config, None)
    return analyzer.analyze_file(file_path, module_name)
