"""Ruby analyzer (regex-based)."""

import re
from typing import Dict

from code2llm.core.models import ClassInfo, FunctionInfo, ModuleInfo
from code2llm.core.lang.base import extract_calls_regex, _extract_declarations


def _extract_ruby_body(content: str, start_line: int) -> str:
    """Extract Ruby function body from def to corresponding end."""
    lines = content.split('\n')
    if start_line < 1 or start_line > len(lines):
        return ''

    def_line_idx = start_line - 1
    while def_line_idx < len(lines):
        if re.match(r'^\s*def\s+', lines[def_line_idx]):
            break
        def_line_idx += 1

    if def_line_idx >= len(lines):
        return ''

    def_indent = len(lines[def_line_idx]) - len(lines[def_line_idx].lstrip())
    body_lines = []
    nested_depth = 1
    i = def_line_idx + 1

    while i < len(lines) and nested_depth > 0:
        line = lines[i]
        stripped = line.strip()

        if line.startswith('end') and len(line) == 3 or line.startswith('end '):
            nested_depth -= 1
            if nested_depth == 0:
                break
        elif re.match(r'^\s*(def|if|unless|while|until|for|case|begin|class|module)\b', line):
            nested_depth += 1

        body_lines.append(line)
        i += 1

    return '\n'.join(body_lines)


_RUBY_CC_PATTERN = re.compile(
    r'\b(?:if|unless|while|until|for|case|when)\b|&&|\|\||\?\s*[^:]*\s*:'
)


def analyze_ruby(content: str, file_path: str, module_name: str,
                 ext: str, stats: Dict) -> Dict:
    """Analyze Ruby files using shared extraction."""
    
    patterns = {
        'import': re.compile(r'^\s*require\s*["\']([^"\']+)["\']'),
        'class': re.compile(r'^\s*class\s+(\w+)(?:\s*<\s*(\w+))?'),
        'function': re.compile(r'^\s*def\s+(?:self\.)?(\w+[?!]?)'),
    }
    
    lang_config = {
        'index_files': (),
        'brace_track': False,  # Ruby uses 'end' keywords, not braces
        'reserved': {'if', 'unless', 'while', 'until', 'for', 'class', 'module'},
    }
    
    result = _extract_declarations(
        content, file_path, module_name,
        patterns, stats, lang_config
    )
    
    # Ruby-specific: handle module nesting
    lines = content.split('\n')
    current_module = None
    module_depth = 0
    
    for line_no, line in enumerate(lines, 1):
        raw_line = line
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Track module scope
        mod_match = re.match(r'^\s*module\s+(\w+)', line)
        if mod_match:
            current_module = mod_match.group(1)
            # Count control structures for depth
            control_starts = len(re.findall(r'\b(def|class|module|if|unless|while|until|for|begin|case)\b', line))
            module_depth = control_starts
            continue
        
        # Track end to exit module scope
        if line.startswith('end'):
            if current_module and module_depth > 0:
                module_depth -= 1
                if module_depth == 0:
                    current_module = None
    
    # Adjust qualified names for modules
    if current_module:
        mod_prefix = f".{current_module}"
        new_classes = {}
        for qname, cls in list(result['classes'].items()):
            new_qname = qname.replace(f"{module_name}.", f"{module_name}{mod_prefix}.", 1)
            cls.qualified_name = new_qname
            new_classes[new_qname] = cls
        result['classes'] = new_classes
        result['module'].classes = list(new_classes.keys())
        
        new_functions = {}
        for qname, func in list(result['functions'].items()):
            new_qname = qname.replace(f"{module_name}.", f"{module_name}{mod_prefix}.", 1)
            func.qualified_name = new_qname
            new_functions[new_qname] = func
        result['functions'] = new_functions
        result['module'].functions = list(new_functions.keys())
    
    # Ruby-specific complexity calculation
    for func_info in result['functions'].values():
        body = _extract_ruby_body(content, func_info.line)
        if not body:
            cc = 1
        else:
            cc = 1 + len(_RUBY_CC_PATTERN.findall(body))
        rank = 'A' if cc <= 5 else ('B' if cc <= 10 else ('C' if cc <= 20 else 'D'))
        func_info.complexity = {
            'cyclomatic_complexity': cc,
            'cc_rank': rank,
        }
    
    extract_calls_regex(content, module_name, result)
    
    stats['files_processed'] += 1
    return result
