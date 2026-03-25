"""Rust analyzer (regex-based)."""

import re
from pathlib import Path
from typing import Dict

from code2llm.core.models import ClassInfo, FunctionInfo, ModuleInfo
from code2llm.core.lang.base import calculate_complexity_regex, extract_calls_regex


def analyze_rust(content: str, file_path: str, module_name: str,
                 ext: str, stats: Dict) -> Dict:
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
            stats['functions_found'] += 1

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
            stats['classes_found'] += 1

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
                bases=[], methods=[], docstring="",
            )
            result['module'].classes.append(qualified_name)
            stats['classes_found'] += 1

    # Regex-based complexity estimation and call extraction
    calculate_complexity_regex(content, result, lang='rust')
    extract_calls_regex(content, module_name, result)

    stats['files_processed'] += 1
    return result
