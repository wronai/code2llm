"""C/C++ analyzer (regex-based)."""

import re
from typing import Dict

from ...models import ClassInfo, FunctionInfo, ModuleInfo
from .base import calculate_complexity_regex, extract_calls_regex


def analyze_cpp(content: str, file_path: str, module_name: str,
                ext: str, stats: Dict) -> Dict:
    """Analyze C/C++ files using regex-based parsing."""
    result = {
        'module': ModuleInfo(name=module_name, file=file_path, is_package=False),
        'functions': {},
        'classes': {},
        'nodes': {},
        'edges': [],
    }

    lines = content.split('\n')

    # Patterns for C/C++
    include_pattern = re.compile(r'^\s*#include\s+["<]([^">]+)[">]')
    class_pattern = re.compile(r'^\s*(?:class|struct)\s+(\w+)')
    func_pattern = re.compile(
        r'^\s*(?:inline\s+|static\s+|virtual\s+|explicit\s+|constexpr\s+)?'
        r'[\w<>,:*&\s]+\s+'  # return type with templates/pointers/refs
        r'(\w+)\s*\([^)]*\)'  # function name and params
    )
    namespace_pattern = re.compile(r'^\s*namespace\s+(\w+)')

    current_class = None
    current_namespace = None
    brace_depth = 0
    class_brace_depth = 0
    in_block_comment = False
    in_line_comment = False

    for line_no, line in enumerate(lines, 1):
        raw_line = line
        line = line.strip()
        
        # Handle block comments (/* ... */) and line comments
        if not in_block_comment:
            if '/*' in raw_line:
                in_block_comment = True
                # Remove everything after /* start
                raw_line = raw_line.split('/*')[0]
                line = raw_line.strip()
            elif line.startswith('//'):
                # Single line comment, skip entirely
                continue
        else:
            if '*/' in raw_line:
                # End of block comment
                in_block_comment = False
                # Remove everything before */ end
                raw_line = raw_line.split('*/')[1]
                line = raw_line.strip()
            else:
                # Still in block comment, skip this line
                continue
        
        if not line:
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

        # Includes
        include_match = include_pattern.match(line)
        if include_match:
            result['module'].imports.append(include_match.group(1))
            continue

        # Namespaces
        ns_match = namespace_pattern.match(line)
        if ns_match:
            current_namespace = ns_match.group(1)
            continue

        # Classes/structs
        class_match = class_pattern.match(line)
        if class_match:
            class_name = class_match.group(1)
            # Qualify with namespace if present
            if current_namespace:
                qualified_name = f"{module_name}.{current_namespace}.{class_name}"
            else:
                qualified_name = f"{module_name}.{class_name}"
            result['classes'][qualified_name] = ClassInfo(
                name=class_name, qualified_name=qualified_name,
                file=file_path, line=line_no, module=module_name,
                bases=[], methods=[], docstring="",
            )
            result['module'].classes.append(qualified_name)
            stats['classes_found'] += 1
            current_class = qualified_name
            class_brace_depth = brace_depth
            continue

        # Functions
        func_match = func_pattern.match(line)
        if func_match:
            func_name = func_match.group(1)
            # Skip keywords that look like functions, plus common license terms
            if func_name in ('if', 'for', 'while', 'switch', 'catch', 'return',
                             'sizeof', 'decltype', 'typeof', 'new', 'delete',
                             'Copyright', 'License', 'TORT', 'WITHOUT', 'WARRANTY',
                             'Permission', 'Redistribution', 'Conditions', 'Disclaimer'):
                continue

            if current_class:
                qualified_name = f"{current_class}.{func_name}"
                result['classes'][current_class].methods.append(qualified_name)
                is_method = True
                class_name = current_class.split('.')[-1]
            else:
                if current_namespace:
                    qualified_name = f"{module_name}.{current_namespace}.{func_name}"
                else:
                    qualified_name = f"{module_name}.{func_name}"
                is_method = False
                class_name = None

            result['functions'][qualified_name] = FunctionInfo(
                name=func_name, qualified_name=qualified_name,
                file=file_path, line=line_no, column=0,
                module=module_name, class_name=class_name,
                is_method=is_method, is_private=func_name.startswith('_'),
                is_property=False, docstring="", args=[], decorators=[],
            )
            result['module'].functions.append(qualified_name)
            stats['functions_found'] += 1

    # Regex-based complexity estimation and call extraction
    calculate_complexity_regex(content, result, lang='c_family')
    extract_calls_regex(content, module_name, result)

    stats['files_processed'] += 1
    return result
