import re
from typing import Dict, Optional, Tuple
from code2llm.core.models import ClassInfo
from code2llm.core.lang.base import calculate_complexity_regex, extract_calls_regex, _extract_declarations

def _parse_php_metadata(content: str, module_name: str, result: Dict) -> Tuple[Optional[str], bool]:
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
        if not in_php: continue
        ns_match = re.match(r'^namespace\s+([\\\w]+)', line)
        if ns_match:
            current_namespace = ns_match.group(1)
            continue
        use_match = re.match(r'^use\s+([\\\w]+)', line)
        if use_match:
            result['module'].imports.append(use_match.group(1))
    return current_namespace, in_php

def _adjust_qualified_names(result: Dict, module_name: str, namespace: str) -> None:
    ns_prefix = f".{namespace}"
    for key in ['classes', 'functions']:
        new_items = {}
        for qname, item in list(result[key].items()):
            new_qname = qname.replace(f"{module_name}.", f"{module_name}{ns_prefix}.", 1)
            item.qualified_name = new_qname
            new_items[new_qname] = item
        result[key] = new_items
        result['module'].__setattr__(key, list(new_items.keys()))

def _extract_php_traits(content: str, file_path: str, module_name: str, namespace: Optional[str], result: Dict, stats: Dict) -> None:
    trait_pattern = re.compile(r'^\s*trait\s+(\w+)')
    for line_no, line in enumerate(content.split('\n'), 1):
        tm = trait_pattern.match(line.strip())
        if tm:
            tname = tm.group(1)
            qual = f"{module_name}.{namespace + '.' if namespace else ''}{tname}"
            result['classes'][qual] = ClassInfo(name=tname, qualified_name=qual, file=file_path, line=line_no, module=module_name, bases=[], methods=[], docstring="")
            result['module'].classes.append(qual)
            stats['classes_found'] += 1

def analyze_php(content: str, file_path: str, module_name: str, ext: str, stats: Dict) -> Dict:
    patterns = {
        'import': re.compile(r'^(?:include|require|include_once|require_once)\s*["\']([^"\']+)["\']'),
        'class': re.compile(r'(?:abstract\s+|final\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w,\s\\]+))?'),
        'interface': re.compile(r'interface\s+(\w+)'),
        'function': re.compile(r'(?:public\s+|private\s+|protected\s+)?(?:static\s+)?function\s+(\w+)\s*\('),
    }
    lang_config = {'index_files': (), 'brace_track': True, 'reserved': {'if', 'for', 'while', 'switch', 'return', 'catch', 'echo', 'print'}}
    result = _extract_declarations(content, file_path, module_name, patterns, stats, lang_config)
    namespace, _ = _parse_php_metadata(content, module_name, result)
    if namespace:
        _adjust_qualified_names(result, module_name, namespace)
    _extract_php_traits(content, file_path, module_name, namespace, result, stats)
    calculate_complexity_regex(content, result, lang='c_family')
    extract_calls_regex(content, module_name, result)
    stats['files_processed'] += 1
    return result