"""File analyzer for analyzing individual source files across multiple languages."""

import ast
import re
from pathlib import Path
from typing import Dict, List, Optional

from radon.complexity import cc_visit, cc_rank

from ..config import Config, LANGUAGE_EXTENSIONS
from ..models import (
    AnalysisResult, ClassInfo, FlowEdge, FlowNode,
    FunctionInfo, ModuleInfo
)
from ...analysis.dfg import DFGExtractor
from ...analysis.call_graph import CallGraphExtractor
from .file_filter import FastFileFilter


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
    
    def analyze_file(self, file_path: str, module_name: str) -> Dict:
        """Analyze a single source file based on its language."""
        path = Path(file_path)
        if not path.exists():
            return {}
        
        # Detect language from extension
        ext = path.suffix.lower()
        
        try:
            content = path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return {}
        
        # Route to appropriate analyzer based on language
        if ext == '.py':
            return self._analyze_python(content, file_path, module_name)
        elif ext in ('.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs'):
            return self._analyze_typescript_js(content, file_path, module_name, ext)
        elif ext == '.go':
            return self._analyze_go(content, file_path, module_name)
        elif ext == '.rs':
            return self._analyze_rust(content, file_path, module_name)
        elif ext == '.java':
            return self._analyze_java(content, file_path, module_name)
        else:
            # For unsupported languages, do basic structural analysis
            return self._analyze_generic(content, file_path, module_name, ext)
    
    def _analyze_python(self, content: str, file_path: str, module_name: str) -> Dict:
        """Analyze Python file using AST."""
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
        
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                self._process_class(node, file_path, module_name, result)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._process_function(node, file_path, module_name, result, None)
        
        # Calculate complexity with radon
        self._calculate_complexity(content, file_path, result)
        
        # Deep Analysis for refactoring
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

    # ------------------------------------------------------------------
    # Universal regex-based complexity & call extraction (non-Python)
    # ------------------------------------------------------------------

    # Branching keywords per language family
    _CC_PATTERNS = {
        'c_family': re.compile(
            r'\b(?:if|else\s+if|for|while|do|switch|case|catch|&&|\|\||\?\?|\?\.)\b'
            r'|\?\s*[^:]*\s*:'  # ternary
        ),
        'go': re.compile(
            r'\b(?:if|for|switch|case|select|go|defer)\b'
            r'|&&|\|\|'
        ),
        'rust': re.compile(
            r'\b(?:if|else\s+if|for|while|loop|match|=>)\b'
            r'|&&|\|\||\?'
        ),
    }

    @staticmethod
    def _extract_function_body(content: str, start_line: int) -> str:
        """Extract the body of a function between braces from a start line (1-indexed)."""
        lines = content.split('\n')
        if start_line < 1 or start_line > len(lines):
            return ''
        depth = 0
        body_lines = []
        started = False
        for line in lines[start_line - 1:]:
            for ch in line:
                if ch == '{':
                    depth += 1
                    started = True
                elif ch == '}':
                    depth -= 1
            if started:
                body_lines.append(line)
            if started and depth <= 0:
                break
        return '\n'.join(body_lines)

    def _calculate_complexity_regex(self, content: str, result: Dict,
                                    lang: str = 'c_family') -> None:
        """Estimate cyclomatic complexity for every function using regex keyword counting."""
        pattern = self._CC_PATTERNS.get(lang, self._CC_PATTERNS['c_family'])
        for func_info in result['functions'].values():
            body = self._extract_function_body(content, func_info.line)
            if not body:
                cc = 1
            else:
                cc = 1 + len(pattern.findall(body))
            rank = 'A' if cc <= 5 else ('B' if cc <= 10 else ('C' if cc <= 20 else 'D'))
            func_info.complexity = {
                'cyclomatic_complexity': cc,
                'cc_rank': rank,
            }

    _CALL_PATTERN_C_FAMILY = re.compile(
        r'(?<!\bfunction\b\s)'            # not a function declaration
        r'(?<!\bclass\b\s)'               # not a class declaration
        r'\b([a-zA-Z_]\w*)\s*\('          # simple call: foo(
        r'|'
        r'(?:this|self)\s*\.\s*(\w+)\s*\('  # this.method( / self.method(
        r'|'
        r'\b(\w+)\s*\.\s*(\w+)\s*\('      # obj.method(
    )

    def _extract_calls_regex(self, content: str, module_name: str, result: Dict) -> None:
        """Extract function calls from function bodies using regex."""
        # Build set of known function simple names for resolution
        known_simple: Dict[str, List[str]] = {}
        for qname in result['functions']:
            simple = qname.rsplit('.', 1)[-1]
            known_simple.setdefault(simple, []).append(qname)

        for func_qname, func_info in result['functions'].items():
            body = self._extract_function_body(content, func_info.line)
            if not body:
                continue
            calls_seen = set()
            for m in self._CALL_PATTERN_C_FAMILY.finditer(body):
                simple_call = m.group(1) or m.group(2) or m.group(4)
                if not simple_call:
                    continue
                # Skip language keywords
                if simple_call in ('if', 'for', 'while', 'switch', 'catch',
                                   'return', 'throw', 'new', 'typeof', 'instanceof',
                                   'import', 'export', 'require', 'console',
                                   'super', 'class', 'function', 'async', 'await',
                                   'delete', 'void', 'case', 'default'):
                    continue
                # Resolve to known qualified name
                if simple_call in known_simple:
                    candidates = known_simple[simple_call]
                    # Prefer same-module match
                    resolved = None
                    my_module = func_qname.rsplit('.', 1)[0]
                    for cand in candidates:
                        if cand.rsplit('.', 1)[0] == my_module:
                            resolved = cand
                            break
                    if resolved is None:
                        resolved = candidates[0]
                    if resolved != func_qname and resolved not in calls_seen:
                        func_info.calls.append(resolved)
                        calls_seen.add(resolved)
                else:
                    # External call — store as module.name for downstream
                    ext_name = f"{module_name}.{simple_call}"
                    if ext_name not in calls_seen:
                        func_info.calls.append(ext_name)
                        calls_seen.add(ext_name)

    def _perform_deep_analysis(self, tree: ast.AST, module_name: str, file_path: str, result: Dict) -> None:
        """Perform deep analysis including DFG and call graph extraction."""
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

    # ------------------------------------------------------------------
    # TypeScript/JavaScript analysis (regex-based)
    # ------------------------------------------------------------------
    def _analyze_typescript_js(self, content: str, file_path: str, module_name: str, ext: str) -> Dict:
        """Analyze TypeScript/JavaScript files using regex-based parsing."""
        result = {
            'module': ModuleInfo(
                name=module_name,
                file=file_path,
                is_package=Path(file_path).name in ('index.ts', 'index.js', 'index.tsx', 'index.jsx')
            ),
            'functions': {},
            'classes': {},
            'nodes': {},
            'edges': [],
        }
        
        lines = content.split('\n')
        
        # Patterns for TypeScript/JavaScript
        import_pattern = re.compile(r"^\s*import\s+.*?\s+from\s+['\"]([^'\"]+)['\"]")
        class_pattern = re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?")
        func_pattern = re.compile(r"^\s*(?:export\s+)?(?:async\s+)?(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?[\(\w])")
        interface_pattern = re.compile(r"^\s*(?:export\s+)?interface\s+(\w+)")
        # Class method patterns: shorthand methods, getters, setters, arrow props
        method_pattern = re.compile(
            r"^\s*(?:(?:public|private|protected|static|readonly|abstract|async|override)\s+)*"
            r"(?:get\s+|set\s+)?"
            r"(\w+)\s*(?:<[^>]*>)?\s*\([^)]*\)"
        )
        arrow_prop_pattern = re.compile(
            r"^\s*(?:(?:public|private|protected|static|readonly)\s+)*"
            r"(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|[a-zA-Z_]\w*)\s*=>"
        )
        
        current_class = None
        class_brace_depth = 0
        brace_depth = 0
        
        for line_no, line in enumerate(lines, 1):
            raw_line = line
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('/*') or line.startswith('*'):
                # Still track braces in comments? No — skip them
                continue
            
            # Track brace depth for class scope
            for ch in raw_line:
                if ch == '{':
                    brace_depth += 1
                elif ch == '}':
                    brace_depth -= 1
            
            # End of class scope
            if current_class and brace_depth < class_brace_depth:
                current_class = None
                class_brace_depth = 0
            
            # Imports
            import_match = import_pattern.match(line)
            if import_match:
                result['module'].imports.append(import_match.group(1))
                continue
            
            # Classes
            class_match = class_pattern.match(line)
            if class_match:
                class_name = class_match.group(1)
                qualified_name = f"{module_name}.{class_name}"
                bases = []
                if class_match.group(2):
                    bases.append(class_match.group(2).strip())
                if class_match.group(3):
                    bases.extend([b.strip() for b in class_match.group(3).split(',')])
                
                result['classes'][qualified_name] = ClassInfo(
                    name=class_name,
                    qualified_name=qualified_name,
                    file=file_path,
                    line=line_no,
                    module=module_name,
                    bases=bases,
                    methods=[],
                    docstring="",
                )
                result['module'].classes.append(qualified_name)
                self.stats['classes_found'] += 1
                current_class = qualified_name
                class_brace_depth = brace_depth
                continue
            
            # Interfaces (treat as classes)
            interface_match = interface_pattern.match(line)
            if interface_match:
                class_name = interface_match.group(1)
                qualified_name = f"{module_name}.{class_name}"
                result['classes'][qualified_name] = ClassInfo(
                    name=class_name,
                    qualified_name=qualified_name,
                    file=file_path,
                    line=line_no,
                    module=module_name,
                    bases=[],
                    methods=[],
                    docstring="",
                )
                result['module'].classes.append(qualified_name)
                self.stats['classes_found'] += 1
                continue
            
            # Standalone functions (function declarations & const/let/var arrows)
            func_match = func_pattern.match(line)
            if func_match and not current_class:
                func_name = func_match.group(1) or func_match.group(2)
                if func_name:
                    qualified_name = f"{module_name}.{func_name}"
                    result['functions'][qualified_name] = FunctionInfo(
                        name=func_name,
                        qualified_name=qualified_name,
                        file=file_path,
                        line=line_no,
                        column=0,
                        module=module_name,
                        class_name=None,
                        is_method=False,
                        is_private=func_name.startswith('_'),
                        is_property=False,
                        docstring="",
                        args=[],
                        decorators=[],
                    )
                    result['module'].functions.append(qualified_name)
                    self.stats['functions_found'] += 1
                    continue
            
            # Class members: methods (shorthand syntax) & arrow property methods
            if current_class:
                _matched_method = False
                # Arrow property: myMethod = (args) => { ... }
                arrow_match = arrow_prop_pattern.match(line)
                if arrow_match:
                    method_name = arrow_match.group(1)
                    if method_name not in ('constructor', 'if', 'for', 'while', 'switch', 'return'):
                        _matched_method = True
                
                # Shorthand method: myMethod(args) { ... }
                if not _matched_method:
                    meth_match = method_pattern.match(line)
                    if meth_match:
                        method_name = meth_match.group(1)
                        if method_name not in ('if', 'for', 'while', 'switch', 'return',
                                               'catch', 'class', 'import', 'export', 'new'):
                            _matched_method = True
                
                # Also catch const/let/var arrows inside class (rare but valid)
                if not _matched_method and func_match:
                    fname = func_match.group(1) or func_match.group(2)
                    if fname:
                        method_name = fname
                        _matched_method = True
                
                if _matched_method:
                    qualified_name = f"{current_class}.{method_name}"
                    result['classes'][current_class].methods.append(qualified_name)
                    result['functions'][qualified_name] = FunctionInfo(
                        name=method_name,
                        qualified_name=qualified_name,
                        file=file_path,
                        line=line_no,
                        column=0,
                        module=module_name,
                        class_name=current_class.split('.')[-1],
                        is_method=True,
                        is_private=method_name.startswith('_') or method_name.startswith('#'),
                        is_property=False,
                        docstring="",
                        args=[],
                        decorators=[],
                    )
                    result['module'].functions.append(qualified_name)
                    self.stats['functions_found'] += 1
        
        # Regex-based complexity estimation and call extraction
        self._calculate_complexity_regex(content, result, lang='c_family')
        self._extract_calls_regex(content, module_name, result)
        
        self.stats['files_processed'] += 1
        return result

    # ------------------------------------------------------------------
    # Go analysis (regex-based)
    # ------------------------------------------------------------------
    def _analyze_go(self, content: str, file_path: str, module_name: str) -> Dict:
        """Analyze Go files using regex-based parsing."""
        result = {
            'module': ModuleInfo(name=module_name, file=file_path, is_package=False),
            'functions': {},
            'classes': {},
            'nodes': {},
            'edges': [],
        }
        
        lines = content.split('\n')
        
        import_pattern = re.compile(r'^\s*import\s+(?:\(\s*["\']([^"\']+)["\']|["\']([^"\']+)["\'])')
        func_pattern = re.compile(r'^\s*func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(')
        struct_pattern = re.compile(r'^\s*type\s+(\w+)\s+struct')
        interface_pattern = re.compile(r'^\s*type\s+(\w+)\s+interface')
        
        for line_no, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            
            # Imports
            import_match = import_pattern.match(line)
            if import_match:
                imp = import_match.group(1) or import_match.group(2)
                if imp:
                    result['module'].imports.append(imp)
            
            # Functions
            func_match = func_pattern.match(line)
            if func_match:
                func_name = func_match.group(1)
                qualified_name = f"{module_name}.{func_name}"
                result['functions'][qualified_name] = FunctionInfo(
                    name=func_name, qualified_name=qualified_name,
                    file=file_path, line=line_no, column=0,
                    module=module_name, class_name=None,
                    is_method=False, is_private=func_name.startswith('_'),
                    is_property=False, docstring="", args=[], decorators=[],
                )
                result['module'].functions.append(qualified_name)
                self.stats['functions_found'] += 1
            
            # Structs (treated as classes)
            struct_match = struct_pattern.match(line)
            if struct_match:
                class_name = struct_match.group(1)
                qualified_name = f"{module_name}.{class_name}"
                result['classes'][qualified_name] = ClassInfo(
                    name=class_name, qualified_name=qualified_name,
                    file=file_path, line=line_no, module=module_name,
                    bases=[], methods=[], docstring="",
                )
                result['module'].classes.append(qualified_name)
                self.stats['classes_found'] += 1
            
            # Interfaces
            interface_match = interface_pattern.match(line)
            if interface_match:
                class_name = interface_match.group(1)
                qualified_name = f"{module_name}.{class_name}"
                result['classes'][qualified_name] = ClassInfo(
                    name=class_name, qualified_name=qualified_name,
                    file=file_path, line=line_no, module=module_name,
                    bases=[], methods=[], docstring="", is_interface=True,
                )
                result['module'].classes.append(qualified_name)
                self.stats['classes_found'] += 1
        
        # Regex-based complexity estimation and call extraction
        self._calculate_complexity_regex(content, result, lang='go')
        self._extract_calls_regex(content, module_name, result)
        
        self.stats['files_processed'] += 1
        return result

    # ------------------------------------------------------------------
    # Rust analysis (regex-based)
    # ------------------------------------------------------------------
    def _analyze_rust(self, content: str, file_path: str, module_name: str) -> Dict:
        """Analyze Rust files using regex-based parsing."""
        result = {
            'module': ModuleInfo(name=module_name, file=file_path, is_package=Path(file_path).name == 'mod.rs'),
            'functions': {},
            'classes': {},
            'nodes': {},
            'edges': [],
        }
        
        lines = content.split('\n')
        
        use_pattern = re.compile(r'^\s*use\s+([\w:]+)')
        fn_pattern = re.compile(r'^\s*(?:pub\s+)?fn\s+(\w+)\s*\(')
        struct_pattern = re.compile(r'^\s*(?:pub\s+)?struct\s+(\w+)')
        impl_pattern = re.compile(r'^\s*impl\s+(?:<[^>]+>\s+)?(\w+)')
        trait_pattern = re.compile(r'^\s*(?:pub\s+)?trait\s+(\w+)')
        
        current_impl = None
        
        for line_no, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            
            # Imports
            use_match = use_pattern.match(line)
            if use_match:
                result['module'].imports.append(use_match.group(1))
            
            # Functions
            fn_match = fn_pattern.match(line)
            if fn_match:
                func_name = fn_match.group(1)
                qualified_name = f"{module_name}.{func_name}"
                result['functions'][qualified_name] = FunctionInfo(
                    name=func_name, qualified_name=qualified_name,
                    file=file_path, line=line_no, column=0,
                    module=module_name, class_name=current_impl,
                    is_method=current_impl is not None,
                    is_private=not line.startswith('pub'),
                    is_property=False, docstring="", args=[], decorators=[],
                )
                result['module'].functions.append(qualified_name)
                self.stats['functions_found'] += 1
            
            # Structs
            struct_match = struct_pattern.match(line)
            if struct_match:
                class_name = struct_match.group(1)
                qualified_name = f"{module_name}.{class_name}"
                result['classes'][qualified_name] = ClassInfo(
                    name=class_name, qualified_name=qualified_name,
                    file=file_path, line=line_no, module=module_name,
                    bases=[], methods=[], docstring="",
                )
                result['module'].classes.append(qualified_name)
                self.stats['classes_found'] += 1
            
            # impl blocks
            impl_match = impl_pattern.match(line)
            if impl_match:
                current_impl = impl_match.group(1)
            
            # Traits (interfaces)
            trait_match = trait_pattern.match(line)
            if trait_match:
                class_name = trait_match.group(1)
                qualified_name = f"{module_name}.{class_name}"
                result['classes'][qualified_name] = ClassInfo(
                    name=class_name, qualified_name=qualified_name,
                    file=file_path, line=line_no, module=module_name,
                    bases=[], methods=[], docstring="", is_interface=True,
                )
                result['module'].classes.append(qualified_name)
                self.stats['classes_found'] += 1
        
        # Regex-based complexity estimation and call extraction
        self._calculate_complexity_regex(content, result, lang='rust')
        self._extract_calls_regex(content, module_name, result)
        
        self.stats['files_processed'] += 1
        return result

    # ------------------------------------------------------------------
    # Java analysis (regex-based)
    # ------------------------------------------------------------------
    def _analyze_java(self, content: str, file_path: str, module_name: str) -> Dict:
        """Analyze Java files using regex-based parsing."""
        result = {
            'module': ModuleInfo(name=module_name, file=file_path, is_package=False),
            'functions': {},
            'classes': {},
            'nodes': {},
            'edges': [],
        }
        
        lines = content.split('\n')
        
        import_pattern = re.compile(r'^\s*import\s+([\w.]+)')
        class_pattern = re.compile(r'^\s*(?:public\s+|private\s+|protected\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?')
        interface_pattern = re.compile(r'^\s*(?:public\s+)?interface\s+(\w+)')
        method_pattern = re.compile(r'^\s*(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:final\s+)?(?:abstract\s+)?[\w<>,\[\]]+\s+(\w+)\s*\([^)]*\)\s*\{?')
        
        current_class = None
        
        for line_no, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('/*') or line.startswith('*'):
                continue
            
            # Imports
            import_match = import_pattern.match(line)
            if import_match:
                result['module'].imports.append(import_match.group(1))
            
            # Classes
            class_match = class_pattern.match(line)
            if class_match:
                class_name = class_match.group(1)
                qualified_name = f"{module_name}.{class_name}"
                bases = []
                if class_match.group(2):
                    bases.append(class_match.group(2).strip())
                if class_match.group(3):
                    bases.extend([b.strip() for b in class_match.group(3).split(',')])
                
                result['classes'][qualified_name] = ClassInfo(
                    name=class_name, qualified_name=qualified_name,
                    file=file_path, line=line_no, module=module_name,
                    bases=bases, methods=[], docstring="",
                )
                result['module'].classes.append(qualified_name)
                self.stats['classes_found'] += 1
                current_class = qualified_name
            
            # Interfaces
            interface_match = interface_pattern.match(line)
            if interface_match:
                class_name = interface_match.group(1)
                qualified_name = f"{module_name}.{class_name}"
                result['classes'][qualified_name] = ClassInfo(
                    name=class_name, qualified_name=qualified_name,
                    file=file_path, line=line_no, module=module_name,
                    bases=[], methods=[], docstring="", is_interface=True,
                )
                result['module'].classes.append(qualified_name)
                self.stats['classes_found'] += 1
            
            # Methods
            method_match = method_pattern.match(line)
            if method_match:
                method_name = method_match.group(1)
                if current_class and not method_name[0].isupper():  # Skip constructors
                    qualified_name = f"{current_class}.{method_name}"
                    result['functions'][qualified_name] = FunctionInfo(
                        name=method_name, qualified_name=qualified_name,
                        file=file_path, line=line_no, column=0,
                        module=module_name, class_name=current_class.split('.')[-1],
                        is_method=True, is_private=False,
                        is_property=False, docstring="", args=[], decorators=[],
                    )
                    result['module'].functions.append(qualified_name)
                    result['classes'][current_class].methods.append(qualified_name)
                    self.stats['functions_found'] += 1
        
        # Regex-based complexity estimation and call extraction
        self._calculate_complexity_regex(content, result, lang='c_family')
        self._extract_calls_regex(content, module_name, result)
        
        self.stats['files_processed'] += 1
        return result

    # ------------------------------------------------------------------
    # Generic analysis for other languages
    # ------------------------------------------------------------------
    def _analyze_generic(self, content: str, file_path: str, module_name: str, ext: str) -> Dict:
        """Basic structural analysis for unsupported languages."""
        result = {
            'module': ModuleInfo(name=module_name, file=file_path, is_package=False),
            'functions': {},
            'classes': {},
            'nodes': {},
            'edges': [],
        }
        
        # Count lines as basic metric
        lines = content.split('\n')
        non_empty = len([l for l in lines if l.strip()])
        
        # Try to detect function-like patterns
        func_patterns = [
            re.compile(r'^\s*(?:def|function|func|fn|sub)\s+(\w+)'),
            re.compile(r'^\s*(\w+)\s*\([^)]*\)\s*\{?\s*$'),
        ]
        
        class_patterns = [
            re.compile(r'^\s*(?:class|struct|type)\s+(\w+)'),
        ]
        
        for line_no, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('//'):
                continue
            
            for pattern in class_patterns:
                match = pattern.match(line)
                if match:
                    class_name = match.group(1)
                    qualified_name = f"{module_name}.{class_name}"
                    result['classes'][qualified_name] = ClassInfo(
                        name=class_name, qualified_name=qualified_name,
                        file=file_path, line=line_no, module=module_name,
                        bases=[], methods=[], docstring="",
                    )
                    result['module'].classes.append(qualified_name)
                    self.stats['classes_found'] += 1
                    break
            
            for pattern in func_patterns:
                match = pattern.match(line)
                if match:
                    func_name = match.group(1)
                    if func_name not in ('if', 'for', 'while', 'switch', 'catch', 'return'):
                        qualified_name = f"{module_name}.{func_name}"
                        result['functions'][qualified_name] = FunctionInfo(
                            name=func_name, qualified_name=qualified_name,
                            file=file_path, line=line_no, column=0,
                            module=module_name, class_name=None,
                            is_method=False, is_private=func_name.startswith('_'),
                            is_property=False, docstring="", args=[], decorators=[],
                        )
                        result['module'].functions.append(qualified_name)
                        self.stats['functions_found'] += 1
                    break
        
        self.stats['files_processed'] += 1
        return result


def _analyze_single_file(args):
    """Analyze single file - module level function for pickle compatibility."""
    file_path, module_name, config_dict = args
    from ..config import Config
    config = Config(**config_dict)
    analyzer = FileAnalyzer(config, None)
    return analyzer.analyze_file(file_path, module_name)
