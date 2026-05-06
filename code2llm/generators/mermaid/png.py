"""Mermaid PNG generation — render .mmd files to PNG images."""

import os
import subprocess
import tempfile
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional

from code2llm.core.config import (
    DEFAULT_PNG_TIMEOUT,
    DEFAULT_MERMAID_MAX_TEXT_SIZE,
    DEFAULT_MERMAID_MAX_EDGES,
)
from .validation import validate_mermaid_file
from .fix import fix_mermaid_file


def _is_png_fresh(mmd_file: Path, output_dir: Path) -> bool:
    """Check if PNG exists and is newer than MMD source."""
    png_file = output_dir / f"{mmd_file.stem}.png"
    if not png_file.exists():
        return False
    # PNG is fresh if newer than MMD
    return png_file.stat().st_mtime >= mmd_file.stat().st_mtime


def _prepare_and_render(mmd_file: Path, output_dir: Path, timeout: int) -> bool:
    """Validate, optionally fix, then render a single .mmd file to PNG."""
    output_file = output_dir / f"{mmd_file.stem}.png"
    
    # Skip if PNG is already fresh
    if _is_png_fresh(mmd_file, output_dir):
        return True
    
    errors = validate_mermaid_file(mmd_file)
    if errors:
        print(f"  Fixing {mmd_file.name}: {len(errors)} issues")
        fix_mermaid_file(mmd_file)
        errors = validate_mermaid_file(mmd_file)
        if errors:
            print(f"    Still has errors: {errors[:3]}")
            return False
    return generate_single_png(mmd_file, output_file, timeout)


def generate_pngs(
    input_dir: Path, output_dir: Path, timeout: int = DEFAULT_PNG_TIMEOUT, max_workers: int = 0
) -> int:
    """Generate PNG files from all .mmd files in input_dir (parallel).

    Args:
        max_workers: Number of parallel workers (0 = auto-detect from CPU count)
    """
    mmd_files = list(input_dir.glob('*.mmd'))
    if not mmd_files:
        return 0

    # Auto-detect workers if not specified
    if max_workers <= 0:
        max_workers = os.cpu_count() or 4

    success_count = 0
    with ThreadPoolExecutor(max_workers=min(max_workers, len(mmd_files))) as pool:
        futures = {pool.submit(_prepare_and_render, f, output_dir, timeout): f for f in mmd_files}
        for future in as_completed(futures):
            if future.result():
                success_count += 1
    return success_count


def _setup_puppeteer_config() -> tuple[int, int, Optional[str], Optional[str]]:
    """Setup puppeteer config file and return (max_text_size, max_edges, cfg_path, puppeteer_cfg_path)."""
    try:
        max_text_size = int(os.getenv('CODE2FLOW_MERMAID_MAX_TEXT_SIZE', str(DEFAULT_MERMAID_MAX_TEXT_SIZE)))
    except Exception:
        max_text_size = DEFAULT_MERMAID_MAX_TEXT_SIZE

    try:
        max_edges = int(os.getenv('CODE2FLOW_MERMAID_MAX_EDGES', str(DEFAULT_MERMAID_MAX_EDGES)))
    except Exception:
        max_edges = DEFAULT_MERMAID_MAX_EDGES

    cfg_path: Optional[str] = None
    puppeteer_cfg_path: Optional[str] = None
    try:
        cfg = {
            "maxTextSize": max_text_size,
            "maxEdges": max_edges,
            "theme": "default",
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_cfg:
            tmp_cfg.write(json.dumps(cfg))
            cfg_path = tmp_cfg.name
    except Exception:
        pass  # cfg_path remains None, renderers will use defaults

    # Puppeteer launch config — --no-sandbox required for many Linux environments
    try:
        puppeteer_cfg = {
            "args": ["--no-sandbox", "--disable-setuid-sandbox"],
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_pcfg:
            tmp_pcfg.write(json.dumps(puppeteer_cfg))
            puppeteer_cfg_path = tmp_pcfg.name
    except Exception:
        pass

    return max_text_size, max_edges, cfg_path, puppeteer_cfg_path


def _build_renderers(
    mmd_file: Path,
    output_file: Path,
    cfg_path: Optional[str],
    puppeteer_cfg_path: Optional[str] = None,
) -> List[tuple]:
    """Build renderer command list based on config availability."""
    base_mmdc = ['mmdc', '-i', str(mmd_file), '-o', str(output_file), '-t', 'default', '-b', 'white', '-w', '2400', '-H', '1800']
    base_npx = ['npx', '-y', '@mermaid-js/mermaid-cli', '-i', str(mmd_file), '-o', str(output_file), '-t', 'default', '-b', 'white', '-w', '2400', '-H', '1800']

    if cfg_path:
        base_mmdc.extend(['-c', cfg_path])
        base_npx.extend(['-c', cfg_path])

    if puppeteer_cfg_path:
        base_mmdc.extend(['-p', puppeteer_cfg_path])
        base_npx.extend(['-p', puppeteer_cfg_path])

    return [
        ('mmdc', base_mmdc),
        ('npx', base_npx),
        ('puppeteer', None),
    ]


def _run_mmdc_subprocess(
    renderers: List[tuple],
    mmd_file: Path,
    output_file: Path,
    timeout: int,
    max_text_size: int,
    max_edges: int,
) -> bool:
    """Run mmdc/npx/puppeteer renderers and return success status."""
    for renderer_name, cmd in renderers:
        try:
            if renderer_name == 'puppeteer':
                if generate_with_puppeteer(
                    mmd_file, output_file, timeout,
                    max_text_size=max_text_size, max_edges=max_edges,
                ):
                    return True
                continue

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


def generate_single_png(mmd_file: Path, output_file: Path, timeout: int = DEFAULT_PNG_TIMEOUT) -> bool:
    """Generate PNG from single Mermaid file using available renderers."""
    # Create output directory
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Setup config and renderers
    max_text_size, max_edges, cfg_path, puppeteer_cfg_path = _setup_puppeteer_config()
    renderers = _build_renderers(mmd_file, output_file, cfg_path, puppeteer_cfg_path)

    # Run renderers
    try:
        return _run_mmdc_subprocess(
            renderers, mmd_file, output_file, timeout, max_text_size, max_edges
        )
    finally:
        for p in (cfg_path, puppeteer_cfg_path):
            if p:
                try:
                    os.unlink(p)
                except Exception:
                    pass


def generate_with_puppeteer(
    mmd_file: Path,
    output_file: Path,
    timeout: int = DEFAULT_PNG_TIMEOUT,
    max_text_size: int = DEFAULT_MERMAID_MAX_TEXT_SIZE,
    max_edges: int = DEFAULT_MERMAID_MAX_EDGES,
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
                '--full-page',
                '--no-sandbox',
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            
            return result.returncode == 0
            
        finally:
            os.unlink(tmp_html_path)
            
    except Exception as e:
        print(f"    Puppeteer error: {e}")
        return False


__all__ = [
    'generate_pngs',
    'generate_single_png',
    'generate_with_puppeteer',
    '_is_png_fresh',
    '_prepare_and_render',
    '_setup_puppeteer_config',
    '_build_renderers',
    '_run_mmdc_subprocess',
]
