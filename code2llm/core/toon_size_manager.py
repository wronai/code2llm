"""TOON file size management - splits large output files into chunks.

Handles the 256KB size limit for generated TOON files.
"""

import os
from pathlib import Path
from typing import List, Tuple


MAX_TOON_SIZE_KB = 256
MAX_TOON_SIZE_BYTES = MAX_TOON_SIZE_KB * 1024


def get_file_size_kb(filepath: Path) -> float:
    """Get file size in KB."""
    return os.path.getsize(filepath) / 1024


def should_split_toon(filepath: Path, max_kb: int = MAX_TOON_SIZE_KB) -> bool:
    """Check if TOON file exceeds size limit."""
    return get_file_size_kb(filepath) > max_kb


def split_toon_file(
    source_file: Path,
    output_dir: Path,
    max_kb: int = MAX_TOON_SIZE_KB,
    prefix: str = "project"
) -> List[Path]:
    """Split large TOON file into chunks under size limit.
    
    Strategy:
    1. Split by modules (M: sections)
    2. If module still too big, split by file groups
    3. Keep header in each part for context
    
    Returns list of created chunk files.
    """
    max_bytes = max_kb * 1024
    content = source_file.read_text(encoding='utf-8')
    
    # Check if we need to split
    if len(content.encode('utf-8')) <= max_bytes:
        return [source_file]
    
    # Parse modules from TOON content
    modules = _parse_modules(content)
    
    if not modules:
        # No clear module structure - split by line count
        return _split_by_lines(source_file, output_dir, max_kb, prefix)
    
    # Split by modules
    return _split_by_modules(source_file, output_dir, modules, max_kb, prefix)


def _parse_modules(content: str) -> List[Tuple[str, int, int]]:
    """Parse module sections from TOON content.
    
    Returns list of (module_name, start_line, end_line).
    """
    lines = content.split('\n')
    modules = []
    current_module = None
    start_line = 0
    
    for i, line in enumerate(lines):
        # TOON format: M[module_name]:
        if line.startswith('M[') and line.endswith(':'):
            # Save previous module
            if current_module:
                modules.append((current_module, start_line, i))
            # Start new module
            current_module = line[2:-2]  # Extract from M[...]:
            start_line = i
    
    # Add last module
    if current_module:
        modules.append((current_module, start_line, len(lines)))
    
    return modules


def _split_by_modules(
    source_file: Path,
    output_dir: Path,
    modules: List[Tuple[str, int, int]],
    max_kb: int,
    prefix: str
) -> List[Path]:
    """Split TOON file by module sections."""
    content = source_file.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # Extract header (first section before M[)
    header_lines = []
    for i, line in enumerate(lines):
        if line.startswith('M['):
            break
        header_lines.append(line)
    
    header = '\n'.join(header_lines)
    max_bytes = max_kb * 1024
    
    chunks = []
    current_chunk = [header]
    current_size = len(header.encode('utf-8'))
    chunk_num = 1
    
    for module_name, start, end in modules:
        module_content = '\n'.join(lines[start:end])
        module_bytes = len(module_content.encode('utf-8'))
        
        # If single module exceeds limit, it goes in its own chunk
        if module_bytes > max_bytes:
            # Flush current chunk if not empty
            if len(current_chunk) > 1:  # More than just header
                chunk_file = _write_chunk(output_dir, prefix, chunk_num, '\n'.join(current_chunk))
                chunks.append(chunk_file)
                chunk_num += 1
                current_chunk = [header]
                current_size = len(header.encode('utf-8'))
            
            # Write oversized module as separate chunk
            chunk_file = _write_chunk(output_dir, prefix, chunk_num, 
                                      header + '\n' + module_content)
            chunks.append(chunk_file)
            chunk_num += 1
            current_chunk = [header]
            current_size = len(header.encode('utf-8'))
        
        elif current_size + module_bytes > max_bytes:
            # Flush current chunk
            chunk_file = _write_chunk(output_dir, prefix, chunk_num, '\n'.join(current_chunk))
            chunks.append(chunk_file)
            chunk_num += 1
            
            # Start new chunk with this module
            current_chunk = [header, module_content]
            current_size = len(header.encode('utf-8')) + module_bytes
        else:
            # Add to current chunk
            current_chunk.append(module_content)
            current_size += module_bytes
    
    # Flush remaining chunk
    if len(current_chunk) > 1:
        chunk_file = _write_chunk(output_dir, prefix, chunk_num, '\n'.join(current_chunk))
        chunks.append(chunk_file)
    
    return chunks


def _split_by_lines(
    source_file: Path,
    output_dir: Path,
    max_kb: int,
    prefix: str
) -> List[Path]:
    """Fallback: split by line count when no module structure."""
    content = source_file.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # Extract header
    header_lines = []
    content_start = 0
    for i, line in enumerate(lines):
        if line.startswith('M[') or line.startswith('D[') or line.startswith('#'):
            content_start = i
            break
        header_lines.append(line)
    
    header = '\n'.join(header_lines)
    max_bytes = max_kb * 1024
    header_bytes = len(header.encode('utf-8'))
    
    chunks = []
    current_lines = [header]
    current_size = header_bytes
    chunk_num = 1
    
    for line in lines[content_start:]:
        line_bytes = len((line + '\n').encode('utf-8'))
        
        if current_size + line_bytes > max_bytes:
            # Write current chunk
            chunk_file = _write_chunk(output_dir, prefix, chunk_num, '\n'.join(current_lines))
            chunks.append(chunk_file)
            chunk_num += 1
            current_lines = [header, line]
            current_size = header_bytes + line_bytes
        else:
            current_lines.append(line)
            current_size += line_bytes
    
    # Write final chunk
    if len(current_lines) > 1:
        chunk_file = _write_chunk(output_dir, prefix, chunk_num, '\n'.join(current_lines))
        chunks.append(chunk_file)
    
    return chunks


def _write_chunk(output_dir: Path, prefix: str, chunk_num: int, content: str) -> Path:
    """Write a chunk file."""
    if chunk_num == 1:
        chunk_file = output_dir / f"{prefix}.toon"
    else:
        chunk_file = output_dir / f"{prefix}_part{chunk_num}.toon"
    
    chunk_file.write_text(content, encoding='utf-8')
    return chunk_file


def manage_toon_size(
    source_file: Path,
    output_dir: Path,
    max_kb: int = MAX_TOON_SIZE_KB,
    prefix: str = "project",
    verbose: bool = False
) -> List[Path]:
    """Main entry point: check and split TOON file if needed.
    
    Returns list of final TOON file(s).
    """
    size_kb = get_file_size_kb(source_file)
    
    if size_kb <= max_kb:
        if verbose:
            print(f"  - {prefix}.toon: {size_kb:.1f}KB (within {max_kb}KB limit)")
        return [source_file]
    
    if verbose:
        print(f"  - {prefix}.toon: {size_kb:.1f}KB → splitting into chunks (>{max_kb}KB limit)")
    
    # Remove original and create chunks
    chunks = split_toon_file(source_file, output_dir, max_kb, prefix)
    
    if len(chunks) > 1:
        source_file.unlink()  # Remove oversized original
        if verbose:
            for chunk in chunks:
                chunk_kb = get_file_size_kb(chunk)
                print(f"    → {chunk.name}: {chunk_kb:.1f}KB")
    
    return chunks
