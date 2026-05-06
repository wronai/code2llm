"""Tree-sitter based declaration extractors — fast CST traversal.

Each language has specific node types for functions, classes, methods.
This module provides unified extraction using tree-sitter queries.
"""

from typing import Dict, Optional, Any
from pathlib import Path

from code2llm.core.models import ClassInfo, FunctionInfo, ModuleInfo


# Node type mappings per language
FUNCTION_TYPES = {
    'python': ('function_definition', 'async_function_definition'),
    'javascript': ('function_declaration', 'function_expression', 'arrow_function', 'method_definition'),
    'typescript': ('function_declaration', 'function_expression', 'arrow_function', 'method_definition'),
    'go': ('function_declaration', 'method_declaration'),
    'rust': ('function_item', 'impl_item'),
    'java': ('method_declaration', 'constructor_declaration'),
    'c': ('function_definition',),
    'cpp': ('function_definition', 'template_function'),
    'csharp': ('method_declaration', 'constructor_declaration'),
    'php': ('function_definition', 'method_declaration'),
    'ruby': ('method', 'singleton_method'),
}

CLASS_TYPES = {
    'python': ('class_definition',),
    'javascript': ('class_declaration', 'class_expression'),
    'typescript': ('class_declaration', 'class_expression', 'interface_declaration'),
    'go': ('type_declaration',),
    'rust': ('struct_item', 'enum_item', 'impl_item', 'trait_item'),
    'java': ('class_declaration', 'interface_declaration', 'enum_declaration'),
    'c': ('struct_specifier',),
    'cpp': ('class_specifier', 'struct_specifier'),
    'csharp': ('class_declaration', 'interface_declaration', 'struct_declaration'),
    'php': ('class_declaration', 'interface_declaration', 'trait_declaration'),
    'ruby': ('class', 'module'),
}

EXT_TO_LANG = {
    '.py': 'python',
    '.js': 'javascript', '.jsx': 'javascript', '.mjs': 'javascript', '.cjs': 'javascript',
    '.ts': 'typescript', '.tsx': 'typescript',
    '.go': 'go',
    '.rs': 'rust',
    '.java': 'java',
    '.c': 'c', '.h': 'c',
    '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp', '.hpp': 'cpp', '.hxx': 'cpp',
    '.cs': 'csharp',
    '.php': 'php',
    '.rb': 'ruby',
}


def _get_node_text(node, source_bytes: bytes) -> str:
    """Extract text content of a node."""
    return source_bytes[node.start_byte:node.end_byte].decode('utf-8', errors='replace')


def _find_name_node(node) -> Optional[Any]:
    """Find the name/identifier child of a node."""
    for child in node.children:
        if child.type in ('identifier', 'name', 'property_identifier', 'type_identifier'):
            return child
        # For method definitions, look for property_identifier
        if child.type == 'property_identifier':
            return child
    # Fallback: look in named children
    for child in node.children:
        if 'name' in child.type or 'identifier' in child.type:
            return child
    return None


def _extract_functions_ts(tree, source_bytes: bytes, lang: str, 
                          module_name: str, file_path: str) -> Dict[str, FunctionInfo]:
    """Extract functions using tree-sitter traversal."""
    functions = {}
    func_types = FUNCTION_TYPES.get(lang, ())
    
    def visit(node, class_context: Optional[str] = None):
        if node.type in func_types:
            name_node = _find_name_node(node)
            if name_node:
                name = _get_node_text(name_node, source_bytes)
                if class_context:
                    qname = f"{module_name}.{class_context}.{name}"
                else:
                    qname = f"{module_name}.{name}"
                
                # Count lines
                start_line = node.start_point[0] + 1
                end_line = node.end_point[0] + 1
                line_count = end_line - start_line + 1
                
                functions[qname] = FunctionInfo(
                    name=name,
                    qualified_name=qname,
                    file=file_path,
                    line=start_line,
                    end_line=end_line,
                    line_count=line_count,
                    is_method=class_context is not None,
                    class_name=class_context,
                )
        
        # Recurse, tracking class context
        new_class = None
        class_types = CLASS_TYPES.get(lang, ())
        if node.type in class_types:
            name_node = _find_name_node(node)
            if name_node:
                new_class = _get_node_text(name_node, source_bytes)
        
        for child in node.children:
            visit(child, new_class or class_context)
    
    visit(tree.root_node)
    return functions


def _extract_classes_ts(tree, source_bytes: bytes, lang: str,
                        module_name: str, file_path: str) -> Dict[str, ClassInfo]:
    """Extract classes using tree-sitter traversal."""
    classes = {}
    class_types = CLASS_TYPES.get(lang, ())
    
    def visit(node):
        if node.type in class_types:
            name_node = _find_name_node(node)
            if name_node:
                name = _get_node_text(name_node, source_bytes)
                qname = f"{module_name}.{name}"
                start_line = node.start_point[0] + 1
                end_line = node.end_point[0] + 1
                
                classes[qname] = ClassInfo(
                    name=name,
                    qualified_name=qname,
                    file=file_path,
                    line=start_line,
                    end_line=end_line,
                )
        
        for child in node.children:
            visit(child)
    
    visit(tree.root_node)
    return classes


def extract_declarations_ts(
    tree,
    source_bytes: bytes,
    ext: str,
    file_path: str,
    module_name: str,
) -> Dict:
    """Extract all declarations from a tree-sitter tree.
    
    Returns dict compatible with regex-based _extract_declarations.
    """
    lang = EXT_TO_LANG.get(ext, 'generic')
    
    functions = _extract_functions_ts(tree, source_bytes, lang, module_name, file_path)
    classes = _extract_classes_ts(tree, source_bytes, lang, module_name, file_path)
    
    return {
        'module': ModuleInfo(
            name=module_name,
            file=file_path,
            is_package=Path(file_path).name in ('__init__.py', 'index.js', 'index.ts', 'mod.rs', 'lib.rs'),
        ),
        'functions': functions,
        'classes': classes,
        'nodes': {},
        'edges': [],
    }
