"""C# analyzer (regex-based)."""

import re
from typing import Dict

from code2llm.core.lang.base import analyze_c_family

# C#-specific patterns
_CSHARP_PATTERNS = {
    'import': re.compile(r'^\s*using\s+([\w.]+)\s*;'),
    'class': re.compile(
        r'^\s*(?:public\s+|private\s+|internal\s+|protected\s+)?'
        r'(?:abstract\s+|sealed\s+)?'
        r'class\s+(\w+)'
        r'(?:\s*:\s*(\w+))?'
    ),
    'interface': re.compile(
        r'^\s*(?:public\s+|private\s+|internal\s+)?interface\s+(\w+)'
    ),
    'function': re.compile(
        r'^\s*(?:public\s+|private\s+|protected\s+|internal\s+)?'
        r'(?:static\s+|virtual\s+|override\s+|abstract\s+)?'
        r'(?:async\s+)?'
        r'(?:[\w<>,\[\]]+\s+)?'
        r'(\w+)\s*\([^)]*\)'
    ),
}

_CSHARP_CONFIG = {
    'index_files': (),
    'brace_track': True,
    'reserved': {'if', 'for', 'while', 'switch', 'return', 'catch', 'class', 'namespace'},
}


def analyze_csharp(content: str, file_path: str, module_name: str,
                   ext: str, stats: Dict) -> Dict:
    """Analyze C# files using shared C-family extraction."""
    return analyze_c_family(
        content, file_path, module_name, stats,
        _CSHARP_PATTERNS, _CSHARP_CONFIG,
    )
