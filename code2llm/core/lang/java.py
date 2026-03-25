"""Java analyzer (regex-based)."""

import re
from typing import Dict

from code2llm.core.models import ClassInfo, FunctionInfo, ModuleInfo
from code2llm.core.lang.base import calculate_complexity_regex, extract_calls_regex, _extract_declarations


def analyze_java(content: str, file_path: str, module_name: str,
                 ext: str, stats: Dict) -> Dict:
    """Analyze Java files using shared extraction."""
    
    patterns = {
        'import': re.compile(r'^\s*import\s+([\w.]+)\s*;'),
        'class': re.compile(
            r'^\s*(?:public\s+|private\s+|protected\s+)?'
            r'(?:abstract\s+|final\s+)?'
            r'class\s+(\w+)'
            r'(?:\s+extends\s+(\w+))?'
            r'(?:\s+implements\s+([\w,\s]+))?'
        ),
        'interface': re.compile(
            r'^\s*(?:public\s+|private\s+|protected\s+)?'
            r'interface\s+(\w+)'
        ),
        'function': re.compile(
            r'^\s*(?:public\s+|private\s+|protected\s+)?'
            r'(?:static\s+|final\s+|abstract\s+|synchronized\s+)?'
            r'(?:[\w<>,\[\]]+\s+)?'  # return type with generics
            r'(\w+)\s*\([^)]*\)'  # name and params
        ),
    }
    
    lang_config = {
        'index_files': (),
        'brace_track': True,
        'reserved': {'if', 'for', 'while', 'switch', 'return', 'catch', 'class', 'interface'},
    }
    
    result = _extract_declarations(
        content, file_path, module_name,
        patterns, stats, lang_config
    )
    
    calculate_complexity_regex(content, result, lang='c_family')
    extract_calls_regex(content, module_name, result)
    
    stats['files_processed'] += 1
    return result
