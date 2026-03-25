"""C++ analyzer (regex-based)."""

import re
from typing import Dict

from code2llm.core.models import ClassInfo, FunctionInfo, ModuleInfo
from code2llm.core.lang.base import calculate_complexity_regex, extract_calls_regex, _extract_declarations


def analyze_cpp(content: str, file_path: str, module_name: str,
                ext: str, stats: Dict) -> Dict:
    """Analyze C++ files using shared extraction."""
    
    patterns = {
        'import': re.compile(r'^\s*#include\s*["<]([^">]+)[">]'),
        'class': re.compile(
            r'^\s*(?:class|struct)\s+(\w+)'
            r'(?:\s*:\s*(?:public|private|protected)\s+(\w+))?'
        ),
        'function': re.compile(
            r'^\s*(?:virtual\s+|static\s+|inline\s+)?'
            r'(?:[\w:*&<>\s]+\s+)?'  # return type
            r'(\w+)\s*\([^)]*\)'  # name and params
        ),
    }
    
    lang_config = {
        'index_files': (),
        'brace_track': True,
        'reserved': {'if', 'for', 'while', 'switch', 'return', 'catch', 'class'},
    }
    
    result = _extract_declarations(
        content, file_path, module_name,
        patterns, stats, lang_config
    )
    
    calculate_complexity_regex(content, result, lang='c_family')
    extract_calls_regex(content, module_name, result)
    
    stats['files_processed'] += 1
    return result
