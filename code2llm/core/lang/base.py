"""Shared utilities for regex-based language analyzers."""

import re
from typing import Dict, List


# Branching keywords per language family
CC_PATTERNS = {
    'c_family': re.compile(
        r'\b(?:if|else\s+if|for|while|do|switch|case|catch)\b'
        r'|&&|\|\||\?\?|\?\.'  # logical operators (not word chars)
        r'|\?\s*[^:]*\s*:'  # ternary
    ),
    'go': re.compile(
        r'\b(?:if|for|switch|case|select|go|defer)\b'
        r'|&&|\|\|'
    ),
    'rust': re.compile(
        r'\b(?:if|else\s+if|for|while|loop|match)\b'
        r'|&&|\|\||\?'
    ),
}

CALL_PATTERN_C_FAMILY = re.compile(
    r'(?<!\bfunction\b\s)'            # not a function declaration
    r'(?<!\bclass\b\s)'               # not a class declaration
    r'\b([a-zA-Z_]\w*)\s*\('          # simple call: foo(
    r'|'
    r'(?:this|self)\s*\.\s*(\w+)\s*\('  # this.method( / self.method(
    r'|'
    r'\b(\w+)\s*\.\s*(\w+)\s*\('      # obj.method(
)


def extract_function_body(content: str, start_line: int) -> str:
    """Extract the body of a function between braces from a start line (1-indexed)."""
    lines = content.split('\n')
    if start_line < 1 or start_line > len(lines):
        return ''
    depth = 0
    body_lines = []
    started = False
    for line in lines[start_line - 1:]:
        for ch in line:
            if ch == '{':
                depth += 1
                started = True
            elif ch == '}':
                depth -= 1
        if started:
            body_lines.append(line)
        if started and depth <= 0:
            break
    return '\n'.join(body_lines)


def calculate_complexity_regex(content: str, result: Dict,
                               lang: str = 'c_family') -> None:
    """Estimate cyclomatic complexity for every function using regex keyword counting."""
    pattern = CC_PATTERNS.get(lang, CC_PATTERNS['c_family'])
    for func_info in result['functions'].values():
        body = extract_function_body(content, func_info.line)
        if not body:
            cc = 1
        else:
            cc = 1 + len(pattern.findall(body))
        rank = 'A' if cc <= 5 else ('B' if cc <= 10 else ('C' if cc <= 20 else 'D'))
        func_info.complexity = {
            'cyclomatic_complexity': cc,
            'cc_rank': rank,
        }


_CALL_KEYWORDS = frozenset({
    'if', 'for', 'while', 'switch', 'catch', 'return', 'throw', 'new',
    'typeof', 'instanceof', 'import', 'export', 'require', 'console',
    'super', 'class', 'function', 'async', 'await', 'delete', 'void',
    'case', 'default',
})


def _resolve_call(
    simple_call: str,
    func_qname: str,
    module_name: str,
    known_simple: Dict[str, List[str]],
    calls_seen: set,
    func_info,
) -> None:
    """Resolve a single call name and append to func_info.calls if novel."""
    if simple_call in known_simple:
        candidates = known_simple[simple_call]
        my_module = func_qname.rsplit('.', 1)[0]
        resolved = next(
            (c for c in candidates if c.rsplit('.', 1)[0] == my_module),
            candidates[0],
        )
        if resolved != func_qname and resolved not in calls_seen:
            func_info.calls.append(resolved)
            calls_seen.add(resolved)
    else:
        ext_name = f"{module_name}.{simple_call}"
        if ext_name not in calls_seen:
            func_info.calls.append(ext_name)
            calls_seen.add(ext_name)


def extract_calls_regex(content: str, module_name: str, result: Dict) -> None:
    """Extract function calls from function bodies using regex."""
    known_simple: Dict[str, List[str]] = {}
    for qname in result['functions']:
        simple = qname.rsplit('.', 1)[-1]
        known_simple.setdefault(simple, []).append(qname)

    for func_qname, func_info in result['functions'].items():
        body = extract_function_body(content, func_info.line)
        if not body:
            continue
        calls_seen: set = set()
        for m in CALL_PATTERN_C_FAMILY.finditer(body):
            simple_call = m.group(1) or m.group(2) or m.group(4)
            if not simple_call or simple_call in _CALL_KEYWORDS:
                continue
            _resolve_call(simple_call, func_qname, module_name, known_simple, calls_seen, func_info)


# Shared declaration extraction for language parsers
def _extract_declarations(
    content: str,
    file_path: str,
    module_name: str,
    patterns: Dict,
    stats: Dict,
    lang_config: Dict,
) -> Dict:
    """Shared extraction logic for language parsers.
    
    Args:
        content: File content
        file_path: Path to file  
        module_name: Module name
        patterns: Dict of compiled regex patterns
        stats: Statistics dict to update
        lang_config: Language-specific config dict
    """
    from ..models import ClassInfo, FunctionInfo, ModuleInfo
    from pathlib import Path
    
    result = {
        'module': ModuleInfo(
            name=module_name,
            file=file_path,
            is_package=Path(file_path).name in lang_config.get('index_files', [])
        ),
        'functions': {},
        'classes': {},
        'nodes': {},
        'edges': [],
    }
    
    lines = content.split('\n')
    current_class = None
    class_brace_depth = 0
    brace_depth = 0
    pending_decorators = []
    
    import_re = patterns.get('import')
    decorator_re = patterns.get('decorator')
    class_re = patterns.get('class')
    interface_re = patterns.get('interface')
    func_re = patterns.get('function')
    arrow_re = patterns.get('arrow_func')
    method_re = patterns.get('method')
    arrow_prop_re = patterns.get('arrow_prop')
    
    track_braces = lang_config.get('brace_track', True)
    reserved = lang_config.get('reserved', {'if', 'for', 'while', 'switch', 'return', 'catch'})
    
    for line_no, line in enumerate(lines, 1):
        raw_line = line
        line = line.strip()
        # Skip empty lines and comments, but NOT preprocessor directives like #include
        if not line:
            continue
        if line.startswith(('//', '/*', '*')):
            continue
        # Skip # comments (Python, Ruby, shell) but NOT #include/#define (C-family)
        if line.startswith('#') and not line.startswith('#include') and not line.startswith('#define'):
            continue
        
        # Update brace tracking
        brace_depth, current_class, class_brace_depth = _update_brace_tracking(
            raw_line, brace_depth, current_class, class_brace_depth, track_braces
        )
        
        # Process decorators
        pending_decorators = _process_decorators(decorator_re, line, pending_decorators)
        
        # Process imports
        if import_re:
            im = import_re.match(line)
            if im:
                result['module'].imports.append(im.group(1))
                continue
        
        # Process classes and interfaces
        current_class, class_brace_depth, pending_decorators = _process_classes(
            class_re, interface_re, line, line_no, file_path, module_name,
            result, stats, current_class, class_brace_depth, pending_decorators
        )
        
        # Process functions
        pending_decorators = _process_functions(
            func_re, arrow_re, method_re, arrow_prop_re, line, line_no,
            file_path, module_name, result, stats, current_class,
            pending_decorators, reserved
        )
        
        # Clear orphaned decorators
        pending_decorators = _clear_orphaned_decorators(
            line, pending_decorators, func_re, arrow_re, class_re, interface_re, method_re
        )
    
    return result


def _update_brace_tracking(raw_line, brace_depth, current_class, class_brace_depth, track_braces):
    """Update brace depth and track current class scope."""
    if track_braces:
        for ch in raw_line:
            if ch == '{':
                brace_depth += 1
            elif ch == '}':
                brace_depth -= 1
        if current_class and brace_depth < class_brace_depth:
            current_class = None
            class_brace_depth = 0
    return brace_depth, current_class, class_brace_depth


def _process_decorators(decorator_re, line, pending_decorators):
    """Process decorator patterns and update pending list."""
    if decorator_re:
        dm = decorator_re.match(line)
        if dm:
            pending_decorators.append(dm.group(1))
            return pending_decorators
    return pending_decorators


def _process_classes(class_re, interface_re, line, line_no, file_path, module_name,
                     result, stats, current_class, class_brace_depth, pending_decorators):
    """Process class and interface declarations."""
    from ..models import ClassInfo
    
    # Process classes
    if class_re:
        cm = class_re.match(line)
        if cm:
            cname = cm.group(1)
            bases = []
            if len(cm.groups()) > 1 and cm.group(2):
                bases.append(cm.group(2).strip())
            if len(cm.groups()) > 2 and cm.group(3):
                bases.extend([b.strip() for b in cm.group(3).split(',')])
            qual = f"{module_name}.{cname}"
            result['classes'][qual] = ClassInfo(
                name=cname, qualified_name=qual, file=file_path,
                line=line_no, module=module_name, bases=bases,
                methods=[], docstring="",
            )
            result['module'].classes.append(qual)
            stats['classes_found'] += 1
            current_class = qual
            class_brace_depth = class_brace_depth  # Will be updated by caller
            pending_decorators.clear()
            return current_class, class_brace_depth, pending_decorators
    
    # Process interfaces
    if interface_re:
        imt = interface_re.match(line)
        if imt:
            cname = imt.group(1)
            qual = f"{module_name}.{cname}"
            result['classes'][qual] = ClassInfo(
                name=cname, qualified_name=qual, file=file_path,
                line=line_no, module=module_name, bases=[],
                methods=[], docstring="",
            )
            result['module'].classes.append(qual)
            stats['classes_found'] += 1
            pending_decorators.clear()
    
    return current_class, class_brace_depth, pending_decorators


def _process_standalone_function(
    func_re, arrow_re, line, line_no, file_path, module_name,
    result, stats, pending_decorators, reserved,
):
    """Register a top-level (non-method) function declaration.

    Returns (registered: bool, pending_decorators).
    """
    from ..models import FunctionInfo

    fname = None
    if func_re:
        fm = func_re.match(line)
        if fm:
            fname = fm.group(1) or (fm.group(2) if len(fm.groups()) > 1 else None)
    if not fname and arrow_re:
        am = arrow_re.match(line)
        if am:
            fname = am.group(1)

    if fname and fname not in reserved:
        qual = f"{module_name}.{fname}"
        result['functions'][qual] = FunctionInfo(
            name=fname, qualified_name=qual, file=file_path,
            line=line_no, column=0, module=module_name,
            class_name=None, is_method=False,
            is_private=fname.startswith('_'),
            is_property=False, docstring="", args=[],
            decorators=pending_decorators[:],
        )
        result['module'].functions.append(qual)
        stats['functions_found'] += 1
        pending_decorators.clear()
        return True, pending_decorators

    return False, pending_decorators


def _match_method_name(arrow_prop_re, method_re, func_re, line, reserved):
    """Return matched method name from any of the three patterns, or None."""
    if arrow_prop_re:
        apm = arrow_prop_re.match(line)
        if apm:
            mname = apm.group(1)
            if mname not in reserved and mname != 'constructor':
                return mname
    if method_re:
        mm = method_re.match(line)
        if mm:
            mname = mm.group(1)
            if mname not in reserved:
                return mname
    if func_re:
        fm = func_re.match(line)
        if fm:
            fn = fm.group(1) or (fm.group(2) if len(fm.groups()) > 1 else None)
            if fn and fn not in reserved:
                return fn
    return None


def _process_class_method(
    method_re, arrow_prop_re, func_re, line, line_no, file_path, module_name,
    result, stats, current_class, pending_decorators, reserved,
):
    """Register a method declaration inside a class scope."""
    from ..models import FunctionInfo

    mname = _match_method_name(arrow_prop_re, method_re, func_re, line, reserved)
    if not mname:
        return pending_decorators

    qual = f"{current_class}.{mname}"
    result['classes'][current_class].methods.append(qual)
    result['functions'][qual] = FunctionInfo(
        name=mname, qualified_name=qual, file=file_path,
        line=line_no, column=0, module=module_name,
        class_name=current_class.split('.')[-1],
        is_method=True, is_private=mname.startswith(('_', '#')),
        is_property=False, docstring="", args=[],
        decorators=pending_decorators[:],
    )
    result['module'].functions.append(qual)
    stats['functions_found'] += 1
    pending_decorators.clear()
    return pending_decorators


def _process_functions(func_re, arrow_re, method_re, arrow_prop_re, line, line_no,
                       file_path, module_name, result, stats, current_class,
                       pending_decorators, reserved):
    """Process function and method declarations."""
    if not current_class and (func_re or arrow_re):
        registered, pending_decorators = _process_standalone_function(
            func_re, arrow_re, line, line_no, file_path, module_name,
            result, stats, pending_decorators, reserved,
        )
        if registered:
            return pending_decorators

    if current_class and (method_re or arrow_prop_re or func_re):
        pending_decorators = _process_class_method(
            method_re, arrow_prop_re, func_re, line, line_no, file_path,
            module_name, result, stats, current_class, pending_decorators, reserved,
        )

    return pending_decorators


def _clear_orphaned_decorators(line, pending_decorators, func_re, arrow_re, class_re, interface_re, method_re):
    """Clear decorators that don't precede any declaration."""
    if pending_decorators:
        all_patterns = [p for p in [func_re, arrow_re, class_re, interface_re, method_re] if p]
        if not any(p and p.match(line) for p in all_patterns):
            pending_decorators.clear()
    return pending_decorators


def analyze_c_family(
    content: str,
    file_path: str,
    module_name: str,
    stats: Dict,
    patterns: Dict,
    lang_config: Dict,
    cc_lang: str = 'c_family',
) -> Dict:
    """Shared analyzer for C-family languages (Java, C#, C++, etc.).

    Reduces boilerplate duplication across Java/C#/C++ analyzers.
    """
    result = _extract_declarations(
        content, file_path, module_name,
        patterns, stats, lang_config,
    )
    calculate_complexity_regex(content, result, lang=cc_lang)
    extract_calls_regex(content, module_name, result)
    stats['files_processed'] += 1
    return result
