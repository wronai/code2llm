"""File Scanner — scans output directory and collects file metadata."""

from pathlib import Path
from typing import Any, Dict, List


# File type detection and icons
FILE_TYPES: Dict[str, Dict[str, str]] = {
    '.toon': {'icon': '📊', 'type': 'toon', 'name': 'TOON'},
    '.md': {'icon': '📝', 'type': 'markdown', 'name': 'Markdown'},
    '.yaml': {'icon': '⚙️', 'type': 'yaml', 'name': 'YAML'},
    '.yml': {'icon': '⚙️', 'type': 'yaml', 'name': 'YAML'},
    '.json': {'icon': '📋', 'type': 'json', 'name': 'JSON'},
    '.mmd': {'icon': '📈', 'type': 'mermaid', 'name': 'Mermaid'},
    '.txt': {'icon': '📄', 'type': 'text', 'name': 'Text'},
    '.html': {'icon': '🌐', 'type': 'html', 'name': 'HTML'},
    '.py': {'icon': '🐍', 'type': 'code', 'name': 'Python'},
    '.js': {'icon': '📜', 'type': 'code', 'name': 'JavaScript'},
    '.ts': {'icon': '📘', 'type': 'code', 'name': 'TypeScript'},
    '.go': {'icon': '🐹', 'type': 'code', 'name': 'Go'},
    '.rs': {'icon': '🦀', 'type': 'code', 'name': 'Rust'},
    '.java': {'icon': '☕', 'type': 'code', 'name': 'Java'},
    '.png': {'icon': '🖼️', 'type': 'image', 'name': 'Image'},
    '.jpg': {'icon': '🖼️', 'type': 'image', 'name': 'Image'},
    '.jpeg': {'icon': '🖼️', 'type': 'image', 'name': 'Image'},
    '.gif': {'icon': '🖼️', 'type': 'image', 'name': 'Image'},
    '.svg': {'icon': '🖼️', 'type': 'image', 'name': 'Image'},
    '.webp': {'icon': '🖼️', 'type': 'image', 'name': 'Image'},
}


class FileScanner:
    """Scan output directory and collect file metadata."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir.resolve()

    def scan(self) -> List[Dict[str, Any]]:
        """Scan output directory for all generated files."""
        files = []

        for path in self.output_dir.rglob('*'):
            if not path.is_file():
                continue
            if path.name == 'index.html':
                continue

            rel_path = path.relative_to(self.output_dir)
            ext = path.suffix.lower()
            file_info = FILE_TYPES.get(
                ext,
                {'icon': '📄', 'type': 'unknown', 'name': ext[1:].upper() if ext else 'File'}
            )

            # Read file content for preview
            content = self._read_file_content(path, file_info['type'])

            files.append({
                'name': path.name,
                'rel_path': str(rel_path),
                'path': str(rel_path).replace('/', ' / '),
                'size': self._format_size(path.stat().st_size),
                'icon': file_info['icon'],
                'type': file_info['type'],
                'type_name': file_info['name'],
                'content': content,
                'is_subdir': '/' in str(rel_path),
            })

        # Sort: root files first, then by type and name
        files.sort(key=lambda f: (f['is_subdir'], f['type'], f['name']))
        return files

    def _read_file_content(self, path: Path, file_type: str) -> str:
        """Read and escape file content for display."""
        try:
            if file_type in ('toon', 'markdown', 'yaml', 'json', 'text', 'mermaid', 'code'):
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    # Limit size
                    if len(content) > 100000:
                        content = content[:100000] + '\n\n... [truncated - file too large]'
                    # Don't escape markdown - it will be rendered as HTML
                    if file_type == 'markdown':
                        return content
                    return self._escape_html(content)
            return '[Binary file]'
        except Exception as e:
            return f'[Error reading file: {e}]'

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;'))

    def _format_size(self, size: int) -> str:
        """Format file size for display."""
        if size < 1024:
            return f'{size}B'
        elif size < 1024 * 1024:
            return f'{size / 1024:.1f}KB'
        else:
            return f'{size / (1024 * 1024):.1f}MB'


def get_file_types() -> Dict[str, Dict[str, str]]:
    """Get file type configuration mapping."""
    return dict(FILE_TYPES)


def get_default_file_info(ext: str) -> Dict[str, str]:
    """Get default file info for unknown extension."""
    return {'icon': '📄', 'type': 'unknown', 'name': ext[1:].upper() if ext else 'File'}
