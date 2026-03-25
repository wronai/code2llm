"""PHP analyzer (regex-based)."""

import re
from typing import Dict

from code2llm.core.models import ClassInfo, FunctionInfo, ModuleInfo
from code2llm.core.lang.base import calculate_complexity_regex, extract_calls_regex, _extract_declarations


def analyze_php(content: str, file_path: str, module_name: str,
                ext: str, stats: Dict) -> Dict:
    """Analyze PHP files using shared extraction."""
    
    # PHP-specific patterns
    patterns = {
        'import': re.compile(r'^(?:include|require|include_once|require_once)\s*["\']([^"\']+)["\']'),
        'class': re.compile(
            r'(?:abstract\s+|final\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w,\s\\]+))?'
        ),
        'interface': re.compile(r'interface\s+(\w+)'),
        'function': re.compile(
            r'(?:public\s+|private\s+|protected\s+)?(?:static\s+)?function\s+(\w+)\s*\('
        ),
    }
    
    # Language configuration
    lang_config = {
        'index_files': (),
        'brace_track': True,
        'reserved': {'if', 'for', 'while', 'switch', 'return', 'catch', 'echo', 'print'},
    }
    
    # Use shared extraction
    result = _extract_declarations(
        content, file_path, module_name,
        patterns, stats, lang_config
    )
    
    # PHP-specific: handle namespaces and adjust qualified names
    lines = content.split('\n')
    current_namespace = None
    in_php = False
    
    for line in lines:
        line = line.strip()
        if line.startswith('<?php') or line.startswith('<?'):
            in_php = True
            continue
        if line == '?>':
            in_php = False
            continue
        if not in_php:
            continue
        
        ns_match = re.match(r'^namespace\s+([\\\w]+)', line)
        if ns_match:
            current_namespace = ns_match.group(1)
            continue
        
        use_match = re.match(r'^use\s+([\\\w]+)', line)
        if use_match:
            result['module'].imports.append(use_match.group(1))
            continue
    
    # Adjust qualified names for namespaces
    if current_namespace:
        ns_prefix = f".{current_namespace}"
        new_classes = {}
        for qname, cls in list(result['classes'].items()):
            new_qname = qname.replace(f"{module_name}.", f"{module_name}{ns_prefix}.", 1)
            cls.qualified_name = new_qname
            new_classes[new_qname] = cls
        result['classes'] = new_classes
        result['module'].classes = list(new_classes.keys())
        
        new_functions = {}
        for qname, func in list(result['functions'].items()):
            new_qname = qname.replace(f"{module_name}.", f"{module_name}{ns_prefix}.", 1)
            func.qualified_name = new_qname
            new_functions[new_qname] = func
        result['functions'] = new_functions
        result['module'].functions = list(new_functions.keys())
    
    # Handle traits as classes
    trait_pattern = re.compile(r'^\s*trait\s+(\w+)')
    for line_no, line in enumerate(lines, 1):
        tm = trait_pattern.match(line.strip())
        if tm:
            tname = tm.group(1)
            if current_namespace:
                qual = f"{module_name}.{current_namespace}.{tname}"
            else:
                qual = f"{module_name}.{tname}"
            result['classes'][qual] = ClassInfo(
                name=tname, qualified_name=qual,
                file=file_path, line=line_no, module=module_name,
                bases=[], methods=[], docstring="",
            )
            result['module'].classes.append(qual)
            stats['classes_found'] += 1
    
    calculate_complexity_regex(content, result, lang='c_family')
    extract_calls_regex(content, module_name, result)
    
    stats['files_processed'] += 1
    return result
