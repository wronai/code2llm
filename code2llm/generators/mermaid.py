"""
Mermaid PNG Generator for code2llm
Integrates with CLI to auto-generate PNG from Mermaid files.
"""

import os
import sys
import subprocess
import tempfile
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional


def validate_mermaid_file(mmd_path: Path) -> List[str]:
    """Validate Mermaid file and return list of errors."""
    if not mmd_path.exists():
        return [f"File not found: {mmd_path}"]

    try:
        content = mmd_path.read_text(encoding='utf-8')
        lines = content.strip().split('\n')
        errors = []

        # Check for proper graph declaration
        if not lines or not any(line.strip().startswith(('graph', 'flowchart')) for line in lines):
            errors.append("Missing graph declaration (should start with 'graph' or 'flowchart')")

        _check_bracket_balance(lines, errors)
        _check_node_ids(lines, errors)

        return errors

    except Exception as e:
        return [f"Error reading file: {e}"]


def _strip_label_segments(s: str) -> str:
    """Remove label segments that frequently contain Mermaid syntax chars."""
    import re
    s = re.sub(r"\|[^|]*\|", "||", s)
    s = re.sub(r"\[\"[^\"]*\"\]", "[]", s)
    s = re.sub(r"\(\"[^\"]*\"\)", "()", s)
    s = re.sub(r"\{\"[^\"]*\"\}", "{}", s)
    s = re.sub(r"\[/[^\]]*?/\]", "[]", s)
    s = re.sub(r"\(/[^)]*?/\)", "()", s)
    return s


def _is_balanced_node_line(line: str) -> bool:
    """Check if a line has balanced brackets — likely a node definition."""
    return (('[' in line and ']' in line) or
            ('(' in line and ')' in line) or
            ('{' in line and '}' in line))


def _check_bracket_balance(lines: List[str], errors: List[str]) -> None:
    """Check for unmatched brackets/parentheses outside label segments."""
    bracket_stack = []
    paren_stack = []

    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('%%'):
            continue
        if _is_balanced_node_line(line):
            continue
        check_line = _strip_label_segments(line)
        _scan_brackets(check_line, line_num, bracket_stack, paren_stack, errors)

    for expected, line_num in bracket_stack:
        errors.append(f"Line {line_num}: Unclosed '[' (missing '{expected}')")
    for expected, line_num in paren_stack:
        errors.append(f"Line {line_num}: Unclosed '(' (missing '{expected}')")


def _scan_brackets(text: str, line_num: int, bracket_stack: list,
                   paren_stack: list, errors: List[str]) -> None:
    """Process bracket/paren chars in a single line."""
    for char in text:
        if char == '[':
            bracket_stack.append((']', line_num))
        elif char == ']':
            if not bracket_stack or bracket_stack[-1][0] != ']':
                errors.append(f"Line {line_num}: Unmatched ']'")
            else:
                bracket_stack.pop()
        elif char == '(':
            paren_stack.append((')', line_num))
        elif char == ')':
            if not paren_stack or paren_stack[-1][0] != ')':
                errors.append(f"Line {line_num}: Unmatched ')'")
            else:
                paren_stack.pop()


def _check_node_ids(lines: List[str], errors: List[str]) -> None:
    """Check for invalid node IDs."""
    import re
    node_pattern = re.compile(r'^\s*([A-Z]\d+|[Ff]\d+_\w+)\s*["\'\[\{]')

    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('%%'):
            continue
        if line.startswith('subgraph ') or line == 'end':
            continue
        if _is_balanced_node_line(line):
            continue

        if any(char in line for char in ['[', '(', '{']):
            if not node_pattern.match(line):
                match = re.match(r'^\s*([A-Za-z0-9_]+)', line)
                if match:
                    node_id = match.group(1)
                    if not re.match(r'^[A-Z]\d+$|^[Ff]\d+_\w+$', node_id):
                        errors.append(f"Line {line_num}: Invalid node ID '{node_id}' (should be like 'N1' or 'F123_name')")


# ------------------------------------------------------------------ #
# fix_mermaid_file helpers
# ------------------------------------------------------------------ #

def _sanitize_label_text(txt: str) -> str:
    """Replace Mermaid syntax chars in labels with HTML entities."""
    return (
        txt.replace('&', '&amp;')
        .replace('"', '&quot;')
        .replace('[', '&#91;')
        .replace(']', '&#93;')
        .replace('(', '&#40;')
        .replace(')', '&#41;')
        .replace('{', '&#123;')
        .replace('}', '&#125;')
        .replace('|', '&#124;')
    )


def _sanitize_node_id(node_id: str) -> str:
    """Make a Mermaid-safe node identifier."""
    import re
    node_id = (node_id or '').strip()
    node_id = re.split(r"[\[\]\(\)\{\}\"\|\s]", node_id, maxsplit=1)[0]
    node_id = re.sub(r"[^A-Za-z0-9_]", "_", node_id)
    return node_id or "N"


def fix_mermaid_file(mmd_path: Path) -> bool:
    """Attempt to fix common Mermaid syntax errors."""
    try:
        content = mmd_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        fixed_lines = []

        for line in lines:
            line = _fix_edge_line(line)
            line = _fix_subgraph_line(line)
            result = _fix_class_line(line)
            if result is not None:
                fixed_lines.extend(result)
            else:
                fixed_lines.append(line)

        fixed_content = '\n'.join(fixed_lines)
        if fixed_content != content:
            mmd_path.write_text(fixed_content, encoding='utf-8')
            return True

    except Exception as e:
        print(f"Error fixing {mmd_path}: {e}")

    return False


def _fix_edge_line(line: str) -> str:
    """Fix edge labels and endpoint issues."""
    import re

    if '-->' not in line:
        return line

    # Fix edge labels with pipe issues
    line = _fix_edge_label_pipes(line)

    # Fix stray trailing '|' after node IDs
    line = re.sub(r"(\b[A-Za-z]\w*)\|\s*$", r"\1", line)

    # Sanitize edge label content inside |...|
    def _sanitize_edge_label(m):
        return f"|{_sanitize_label_text(m.group(1))}|"

    if '|' in line:
        line = re.sub(r"\|([^|]{1,200})\|", _sanitize_edge_label, line)

    # Sanitize edge endpoints (lines without labels)
    if '|' not in line:
        m = re.match(r"^(\s*)([^\s-]+)\s*-->\s*([^\s]+)\s*$", line)
        if m:
            indent, src, dst = m.groups()
            line = f"{indent}{_sanitize_node_id(src)} --> {_sanitize_node_id(dst)}"

    return line


def _fix_edge_label_pipes(line: str) -> str:
    """Fix edge labels with pipe/parenthesis issues."""
    if '|' not in line or '-->|' not in line:
        return line
    parts = line.split('-->|', 1)
    if len(parts) != 2:
        return line
    label_and_target = parts[1]
    if '|' not in label_and_target:
        return line
    parts2 = label_and_target.split('|', 1)
    if len(parts2) != 2:
        return line
    label_content, target = parts2
    label_content = label_content.strip('|')
    if label_content.endswith('('):
        label_content = label_content[:-1]
    elif label_content.count('(') > label_content.count(')'):
        missing = label_content.count('(') - label_content.count(')')
        label_content += ')' * missing
    return f"{parts[0]}-->|{label_content}|{target}"


def _fix_subgraph_line(line: str) -> str:
    """Fix malformed subgraph IDs."""
    if line.strip().startswith('subgraph '):
        subgraph_part = line.strip()[9:].split('(', 1)
        if len(subgraph_part) == 2:
            subgraph_id, rest = subgraph_part
            subgraph_id = subgraph_id.replace('.', '_').replace('-', '_').replace(':', '_')
            line = f"    subgraph {subgraph_id}({rest}"
    return line


def _fix_class_line(line: str):
    """Fix class definitions with too many nodes. Returns list of lines or None."""
    if line.strip().startswith('class ') and ',' in line:
        class_parts = line.split(' ', 1)
        if len(class_parts) == 2:
            nodes_and_class = class_parts[1]
            nodes, class_name = nodes_and_class.rsplit(' ', 1)
            node_list = nodes.split(',')
            if len(node_list) > 10:
                result = []
                for i in range(0, len(node_list), 10):
                    chunk = ','.join(node_list[i:i+10])
                    result.append(f"    class {chunk} {class_name}")
                return result
    return None


def _prepare_and_render(mmd_file: Path, output_dir: Path, timeout: int) -> bool:
    """Validate, optionally fix, then render a single .mmd file to PNG."""
    output_file = output_dir / f"{mmd_file.stem}.png"
    errors = validate_mermaid_file(mmd_file)
    if errors:
        print(f"  Fixing {mmd_file.name}: {len(errors)} issues")
        fix_mermaid_file(mmd_file)
        errors = validate_mermaid_file(mmd_file)
        if errors:
            print(f"    Still has errors: {errors[:3]}")
            return False
    return generate_single_png(mmd_file, output_file, timeout)


def generate_pngs(input_dir: Path, output_dir: Path, timeout: int = 60, max_workers: int = 4) -> int:
    """Generate PNG files from all .mmd files in input_dir (parallel)."""
    mmd_files = list(input_dir.glob('*.mmd'))
    if not mmd_files:
        return 0

    success_count = 0
    with ThreadPoolExecutor(max_workers=min(max_workers, len(mmd_files))) as pool:
        futures = {pool.submit(_prepare_and_render, f, output_dir, timeout): f for f in mmd_files}
        for future in as_completed(futures):
            if future.result():
                success_count += 1
    return success_count


def generate_single_png(mmd_file: Path, output_file: Path, timeout: int = 60) -> bool:
    """Generate PNG from single Mermaid file using available renderers."""
    
    # Create output directory
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Mermaid's default maxTextSize is often too low for large projects,
    # resulting in placeholder PNGs that say "Maximum text size in diagram exceeded".
    # Provide a temporary config with a higher limit.
    try:
        max_text_size = int(os.getenv('CODE2FLOW_MERMAID_MAX_TEXT_SIZE', '2000000'))
    except Exception:
        max_text_size = 2000000

    try:
        max_edges = int(os.getenv('CODE2FLOW_MERMAID_MAX_EDGES', '20000'))
    except Exception:
        max_edges = 20000

    cfg_path: Optional[str] = None
    try:
        cfg = {
            "maxTextSize": max_text_size,
            "maxEdges": max_edges,
            "theme": "default",
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_cfg:
            tmp_cfg.write(json.dumps(cfg))
            cfg_path = tmp_cfg.name

        # Try different renderers in order of preference
        renderers = [
            (
                'mmdc',
                [
                    'mmdc',
                    '-i',
                    str(mmd_file),
                    '-o',
                    str(output_file),
                    '-t',
                    'default',
                    '-b',
                    'white',
                    '-c',
                    cfg_path,
                    '-w',
                    '2400',
                    '-H',
                    '1800',
                ],
            ),
            (
                'npx',
                [
                    'npx',
                    '-y',
                    '@mermaid-js/mermaid-cli',
                    '-i',
                    str(mmd_file),
                    '-o',
                    str(output_file),
                    '-t',
                    'default',
                    '-b',
                    'white',
                    '-c',
                    cfg_path,
                    '-w',
                    '2400',
                    '-H',
                    '1800',
                ],
            ),
            ('puppeteer', None),  # Special handling
        ]
    except Exception:
        # If creating config fails for any reason, fall back to renderer defaults.
        renderers = [
            ('mmdc', ['mmdc', '-i', str(mmd_file), '-o', str(output_file), '-t', 'default', '-b', 'white', '-w', '2400', '-H', '1800']),
            ('npx', ['npx', '-y', '@mermaid-js/mermaid-cli', '-i', str(mmd_file), '-o', str(output_file), '-w', '2400', '-H', '1800']),
            ('puppeteer', None),
        ]
    
    try:
        for renderer_name, cmd in renderers:
            try:
                if renderer_name == 'puppeteer':
                    # Special puppeteer handling
                    if generate_with_puppeteer(
                        mmd_file,
                        output_file,
                        timeout,
                        max_text_size=max_text_size,
                        max_edges=max_edges,
                    ):
                        return True
                    continue
                
                # Run command
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
                
                if result.returncode == 0:
                    return True
                else:
                    print(f"    {renderer_name} failed: {result.stderr.strip()}")
                    
            except subprocess.TimeoutExpired:
                print(f"    {renderer_name} timed out")
            except FileNotFoundError:
                print(f"    {renderer_name} not available")
            except Exception as e:
                print(f"    {renderer_name} error: {e}")
        
        return False
    finally:
        if cfg_path:
            try:
                os.unlink(cfg_path)
            except Exception:
                pass


def generate_with_puppeteer(
    mmd_file: Path,
    output_file: Path,
    timeout: int = 60,
    max_text_size: int = 2000000,
    max_edges: int = 20000,
) -> bool:
    """Generate PNG using Puppeteer with HTML template."""
    try:
        mmd_content = mmd_file.read_text(encoding='utf-8')
        
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        body {{ margin: 0; padding: 20px; background: white; font-family: Arial, sans-serif; }}
        .mermaid {{ max-width: none; }}
    </style>
</head>
<body>
    <div class="mermaid">
{mmd_content}
    </div>
    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'default', maxTextSize: {max_text_size}, maxEdges: {max_edges} }});
    </script>
</body>
</html>
"""
        
        # Create temporary HTML
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as tmp_html:
            tmp_html.write(html_template)
            tmp_html_path = tmp_html.name
        
        try:
            # Use puppeteer screenshot
            cmd = [
                'npx', '-y', 'puppeteer',
                'screenshot',
                '--url', f'file://{tmp_html_path}',
                '--output', str(output_file),
                '--wait-for', '.mermaid',
                '--full-page'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            
            return result.returncode == 0
            
        finally:
            os.unlink(tmp_html_path)
            
    except Exception as e:
        print(f"    Puppeteer error: {e}")
        return False


if __name__ == '__main__':
    # CLI interface for testing
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate PNG from Mermaid files')
    parser.add_argument('input_dir', help='Directory with .mmd files')
    parser.add_argument('output_dir', help='Output directory for PNG files')
    
    args = parser.parse_args()
    
    input_path = Path(args.input_dir)
    output_path = Path(args.output_dir)
    
    count = generate_pngs(input_path, output_path)
    print(f"Generated {count} PNG files")
