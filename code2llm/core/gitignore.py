"""Gitignore support for code2llm file filtering."""

from pathlib import Path
from typing import List
import re


class _GitIgnoreEntry:
    """Single parsed gitignore rule."""
    __slots__ = ('regex', 'is_negated', 'is_anchored')

    def __init__(self, regex: re.Pattern, is_negated: bool, is_anchored: bool):
        self.regex = regex
        self.is_negated = is_negated
        self.is_anchored = is_anchored


class GitIgnoreParser:
    """Parse and apply .gitignore patterns to file paths."""
    
    def __init__(self, gitignore_path: Path = None):
        """Initialize parser with optional .gitignore file path."""
        self.patterns: List[re.Pattern] = []
        self.dir_patterns: List[re.Pattern] = []
        self.negated_patterns: List[re.Pattern] = []
        self._entries: List[_GitIgnoreEntry] = []
        
        if gitignore_path and gitignore_path.exists():
            self._load_gitignore(gitignore_path)
    
    def _load_gitignore(self, gitignore_path: Path) -> None:
        """Load and parse .gitignore file."""
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.rstrip()
                    if not line or line.startswith('#'):
                        continue
                    entry = self._parse_entry(line)
                    if entry:
                        self._entries.append(entry)
                        # Keep legacy lists populated for backward compat
                        if entry.is_negated:
                            self.negated_patterns.append(entry.regex)
                        else:
                            self.patterns.append(entry.regex)
        except (OSError, UnicodeDecodeError):
            pass

    def _parse_entry(self, raw: str) -> '_GitIgnoreEntry':
        """Parse a single gitignore line into a _GitIgnoreEntry."""
        is_negated = raw.startswith('!')
        pattern = raw[1:] if is_negated else raw

        is_dir_only = pattern.endswith('/')
        if is_dir_only:
            pattern = pattern[:-1]

        # A pattern is "anchored" (must match from root) if:
        #   - it starts with / (explicit root anchor), or
        #   - it contains / somewhere in the middle (path separator present)
        if pattern.startswith('/'):
            pattern = pattern[1:]
            is_anchored = True
        else:
            is_anchored = '/' in pattern  # e.g. "src/*.py" is anchored

        regex_str = self._pattern_to_regex(pattern, is_anchored)
        try:
            compiled = re.compile(regex_str)
            return _GitIgnoreEntry(compiled, is_negated, is_anchored)
        except re.error:
            return None

    @staticmethod
    def _pattern_to_regex(pattern: str, is_anchored: bool) -> str:
        """Convert a gitignore glob pattern to a full-match regex string.

        Key gitignore rules implemented:
        - '*'  does NOT match '/'  → '[^/]*'
        - '?'  does NOT match '/'  → '[^/]'
        - '**' matches anything    → '.*'
        - Unanchored patterns are matched against any path component boundary.
        """
        # Split on '**' first so we can treat it specially
        parts = pattern.split('**')
        converted = []
        for i, part in enumerate(parts):
            # Escape, then restore *, ?, [...]
            esc = re.escape(part)
            esc = esc.replace(r'\*', '[^/]*')
            esc = esc.replace(r'\?', '[^/]')
            esc = re.sub(r'\\(\[.*?\])', r'\1', esc)
            converted.append(esc)
        # Join '**' segments with '.*' (matches across dirs)
        regex_body = '.*'.join(converted)

        if is_anchored:
            # Must match from the start of the relative path
            return f'^{regex_body}(/.*)?$'
        else:
            # Match against any path component: at start OR after a '/'
            return f'(^|/){regex_body}(/.*)?$'

    def is_ignored(self, file_path: Path, project_root: Path) -> bool:
        """Check if file should be ignored based on gitignore patterns."""
        try:
            rel_path = file_path.relative_to(project_root)
            path_str = str(rel_path).replace('\\', '/')
        except ValueError:
            return False

        # DEBUG
        if 'vendor' in path_str:
            print(f"DEBUG is_ignored: path_str={path_str}, entries={len(self._entries)}")

        ignored = False
        for entry in self._entries:
            if entry.regex.search(path_str):
                # DEBUG
                if 'vendor' in path_str:
                    print(f"DEBUG is_ignored: MATCHED pattern={entry.regex.pattern}, is_negated={entry.is_negated}")
                ignored = not entry.is_negated

        # DEBUG
        if 'vendor' in path_str:
            print(f"DEBUG is_ignored: result={ignored}")

        return ignored


def load_gitignore_patterns(project_path: Path) -> GitIgnoreParser:
    """Load gitignore patterns from project directory.
    
    Searches up the directory tree from project_path until it finds a .gitignore file
    or reaches the filesystem root. This ensures that gitignore rules are properly applied
    even when analyzing subdirectories of a larger project.
    """
    current_path = project_path.resolve()
    
    while current_path != current_path.parent:  # Stop at filesystem root
        gitignore_path = current_path / '.gitignore'
        if gitignore_path.exists():
            return GitIgnoreParser(gitignore_path)
        current_path = current_path.parent
    
    # Check filesystem root as last resort
    gitignore_path = current_path / '.gitignore'
    return GitIgnoreParser(gitignore_path)
