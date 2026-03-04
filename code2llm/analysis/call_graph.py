"""Call graph extractor using AST."""

import ast
from typing import Optional, Set, List, Dict
import astroid

from ..core.config import Config
from ..core.models import AnalysisResult, FlowEdge


class CallGraphExtractor(ast.NodeVisitor):
    """Extract call graph from AST."""
    
    def __init__(self, config: Config):
        self.config = config
        self.result = AnalysisResult()
        self.module_name = ""
        self.file_path = ""
        
        # Context
        self.function_stack = []
        self.class_stack = []
        self.imports = {}
        self.astroid_tree = None
        
    def extract(self, tree: ast.AST, module_name: str, file_path: str) -> AnalysisResult:
        """Extract call graph from AST."""
        self.result = AnalysisResult()
        self.module_name = module_name
        self.file_path = file_path
        self.function_stack = []
        self.class_stack = []
        self.imports = {}
        
        # Suppress stderr at OS level to avoid syntax error messages from astroid/C parser
        import os
        null_fd = os.open(os.devnull, os.O_WRONLY)
        old_stderr_fd = os.dup(2)
        os.dup2(null_fd, 2)
        
        try:
            # Try to get astroid tree for better resolution
            self.astroid_tree = astroid.MANAGER.ast_from_file(file_path)
        except Exception:
            self.astroid_tree = None
        finally:
            os.dup2(old_stderr_fd, 2)
            os.close(null_fd)
            os.close(old_stderr_fd)
            
        self.visit(tree)
        self._calculate_metrics()
        return self.result

    def _calculate_metrics(self):
        """Calculate fan-in and fan-out metrics."""
        # First, populate called_by for all functions
        for caller_name, caller_info in self.result.functions.items():
            for callee_name in caller_info.calls:
                if callee_name in self.result.functions:
                    self.result.functions[callee_name].called_by.append(caller_name)

        # Then calculate metrics
        for func_name, func_info in self.result.functions.items():
            fan_out = len(set(func_info.calls))
            fan_in = len(set(func_info.called_by))
            
            self.result.metrics[func_name] = {
                "fan_in": fan_in,
                "fan_out": fan_out,
                "complexity": getattr(func_info, 'complexity', 1) # Placeholder for now
            }
        
    def visit_Import(self, node: ast.Import):
        """Track imports."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports[name] = alias.name
            self.result.imports[name] = alias.name
            
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Track from imports."""
        module = node.module or ""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            full_name = f"{module}.{alias.name}" if module else alias.name
            self.imports[name] = full_name
            self.result.imports[name] = full_name
            
    def visit_ClassDef(self, node: ast.ClassDef):
        """Visit class definition."""
        self.class_stack.append(node.name)
        
        # Store class info
        self.result.classes[node.name] = {
            'file': self.file_path,
            'line': node.lineno,
            'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
            'bases': [self._expr_to_str(b) for b in node.bases]
        }
        
        for stmt in node.body:
            self.visit(stmt)
            
        self.class_stack.pop()
        
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definition and track calls within it."""
        func_name = self._qualified_name(node.name)
        self.function_stack.append(func_name)
        
        # Visit body to find calls
        for stmt in node.body:
            self.visit(stmt)
            
        self.function_stack.pop()
        
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Visit async function."""
        self.visit_FunctionDef(node)
        
    def visit_Call(self, node: ast.Call):
        """Track function calls."""
        if not self.function_stack:
            self.generic_visit(node)
            return
            
        caller = self.function_stack[-1]
        callee = self._resolve_call(node.func)
        
        # If ast-based resolution failed or returned None.sth, try astroid
        if (not callee or 'None.' in callee) and self.astroid_tree:
            astroid_callee = self._resolve_with_astroid(node)
            if astroid_callee:
                callee = astroid_callee
        
        if callee and caller in self.result.functions:
            self.result.functions[caller].calls.append(callee)
            
            # Create call edge
            edge = FlowEdge(
                source=-1,  # Will be resolved
                target=-1,
                edge_type="call",
                metadata={'caller': caller, 'callee': callee}
            )
            self.result.call_edges.append(edge)
            
        self.generic_visit(node)
        
    def _qualified_name(self, name: str) -> str:
        """Get fully qualified name."""
        parts = [self.module_name]
        if self.class_stack:
            parts.append(self.class_stack[-1])
        parts.append(name)
        return '.'.join(parts)
        
    def _resolve_call(self, node: ast.AST) -> Optional[str]:
        """Resolve a call to its full name."""
        if isinstance(node, ast.Name):
            # Simple function call
            if node.id in self.imports:
                return self.imports[node.id]
            return f"{self.module_name}.{node.id}"
            
        elif isinstance(node, ast.Attribute):
            # Method or module.function call
            parts = []
            current = node
            
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
                
            if isinstance(current, ast.Name):
                parts.append(current.id)
                parts.reverse()
                
                # Check if root is an import
                root = parts[0]
                if root in self.imports:
                    return f"{self.imports[root]}.{'.'.join(parts[1:])}"
                    
                # Check for self/cls
                if root in ('self', 'cls') and self.class_stack:
                    return f"{self.module_name}.{self.class_stack[-1]}.{'.'.join(parts[1:])}"
                    
                return f"{self.module_name}.{'.'.join(parts)}"
                
        return None

    def _resolve_with_astroid(self, node: ast.Call) -> Optional[str]:
        """Use astroid to infer the call target."""
        if not self.astroid_tree:
            return None
            
        try:
            # Find the corresponding astroid node by line/col
            # This is a bit slow but robust
            for astroid_node in self.astroid_tree.nodes_of_class(astroid.Call):
                if astroid_node.lineno == node.lineno and astroid_node.col_offset == node.col_offset:
                    # Infer the targets
                    inferred = astroid_node.func.infer()
                    for target in inferred:
                        if hasattr(target, 'qname'):
                            return target.qname()
                    break
        except Exception:
            pass
        return None
        
    def _expr_to_str(self, node: ast.AST) -> str:
        """Convert AST expression to string."""
        if node is None:
            return ""
        try:
            return ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
        except:
            return str(node)
