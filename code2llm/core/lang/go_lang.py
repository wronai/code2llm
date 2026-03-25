"""Go analyzer (regex-based)."""

import re
from pathlib import Path
from typing import Dict

from code2llm.core.models import ClassInfo, FunctionInfo, ModuleInfo
from code2llm.core.lang.base import calculate_complexity_regex, extract_calls_regex


def analyze_go(content: str, file_path: str, module_name: str,
               ext: str, stats: Dict) -> Dict:
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
            stats['functions_found'] += 1

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
            stats['classes_found'] += 1

        # Interfaces
        interface_match = interface_pattern.match(line)
        if interface_match:
            class_name = interface_match.group(1)
            qualified_name = f"{module_name}.{class_name}"
            result['classes'][qualified_name] = ClassInfo(
                name=class_name, qualified_name=qualified_name,
                file=file_path, line=line_no, module=module_name,
                bases=[], methods=[], docstring="",
            )
            result['module'].classes.append(qualified_name)
            stats['classes_found'] += 1

    # Regex-based complexity estimation and call extraction
    calculate_complexity_regex(content, result, lang='go')
    extract_calls_regex(content, module_name, result)

    stats['files_processed'] += 1
    return result
