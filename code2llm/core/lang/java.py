"""Java analyzer (regex-based)."""

import re
from typing import Dict

from code2llm.core.lang.base import analyze_c_family

# Java-specific patterns
_JAVA_PATTERNS = {
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
        r'(?:[\w<>,\[\]]+\s+)?'
        r'(\w+)\s*\([^)]*\)'
    ),
}

_JAVA_CONFIG = {
    'index_files': (),
    'brace_track': True,
    'reserved': {'if', 'for', 'while', 'switch', 'return', 'catch', 'class', 'interface'},
}


def analyze_java(content: str, file_path: str, module_name: str,
                 ext: str, stats: Dict) -> Dict:
    """Analyze Java files using shared C-family extraction."""
    return analyze_c_family(
        content, file_path, module_name, stats,
        _JAVA_PATTERNS, _JAVA_CONFIG,
    )
