"""Generic analyzer for unsupported languages."""

import re
from typing import Dict

from code2llm.core.models import ClassInfo, FunctionInfo, ModuleInfo


def analyze_generic(content: str, file_path: str, module_name: str,
                    ext: str, stats: Dict) -> Dict:
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
                stats['classes_found'] += 1
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
                    stats['functions_found'] += 1
                break

    stats['files_processed'] += 1
    return result
