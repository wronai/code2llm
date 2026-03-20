"""Gitignore support for code2llm file filtering."""

from pathlib import Path
from typing import List, Set
import re


class GitIgnoreParser:
    """Parse and apply .gitignore patterns to file paths."""
    
    def __init__(self, gitignore_path: Path = None):
        """Initialize parser with optional .gitignore file path."""
        self.patterns: List[re.Pattern] = []
        self.dir_patterns: List[re.Pattern] = []
        self.negated_patterns: List[re.Pattern] = []
        
        if gitignore_path and gitignore_path.exists():
            self._load_gitignore(gitignore_path)
    
    def _load_gitignore(self, gitignore_path: Path) -> None:
        """Load and parse .gitignore file."""
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.rstrip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse pattern
                    pattern = self._parse_pattern(line)
                    if pattern:
                        self.patterns.append(pattern)
        except (OSError, UnicodeDecodeError):
            # Silently ignore gitignore parsing errors
            pass
    
    def _parse_pattern(self, pattern: str) -> re.Pattern:
        """Parse a single gitignore pattern into regex."""
        is_negated = pattern.startswith('!')
        if is_negated:
            pattern = pattern[1:]
        
        is_dir_only = pattern.endswith('/')
        if is_dir_only:
            pattern = pattern[:-1]
        
        # Handle absolute patterns (starting with /)
        if pattern.startswith('/'):
            pattern = pattern[1:]
            # Match from beginning of path
            regex_pattern = f'^{self._wildcard_to_regex(pattern)}'
        else:
            # Match anywhere in path
            regex_pattern = self._wildcard_to_regex(pattern)
        
        # Match directory or file
        if is_dir_only:
            regex_pattern += f'(/.*)?$'
        else:
            regex_pattern += f'(/.*)?$'
        
        try:
            compiled = re.compile(regex_pattern)
            if is_negated:
                self.negated_patterns.append(compiled)
            elif is_dir_only:
                self.dir_patterns.append(compiled)
                # Also add to main patterns for directory matching
                return compiled
            else:
                return compiled
        except re.error:
            # Skip invalid regex patterns
            pass
        
        return None
    
    def _wildcard_to_regex(self, pattern: str) -> str:
        """Convert gitignore wildcards to regex."""
        # Escape regex special characters except *, ?, []
        escaped = re.escape(pattern)
        
        # Unescape gitignore wildcards
        escaped = escaped.replace(r'\*', '.*')  # * matches any sequence
        escaped = escaped.replace(r'\?', '.')   # ? matches any single character
        
        # Handle character classes [abc]
        escaped = re.sub(r'\\(\[.*?\])', r'\1', escaped)
        
        return escaped
    
    def is_ignored(self, file_path: Path, project_root: Path) -> bool:
        """Check if file should be ignored based on gitignore patterns."""
        # Convert to relative path from project root
        try:
            rel_path = file_path.relative_to(project_root)
            path_str = str(rel_path).replace('\\', '/')  # Use forward slashes
        except ValueError:
            # File is outside project root, don't ignore
            return False
        
        # Check negated patterns first (they override)
        for pattern in self.negated_patterns:
            if pattern.search(path_str):
                return False
        
        # Check regular patterns
        for pattern in self.patterns:
            if pattern and pattern.search(path_str):
                return True
        
        # Check directory patterns
        for pattern in self.dir_patterns:
            if pattern and pattern.search(path_str):
                return True
        
        return False


def load_gitignore_patterns(project_path: Path) -> GitIgnoreParser:
    """Load gitignore patterns from project directory."""
    gitignore_path = project_path / '.gitignore'
    return GitIgnoreParser(gitignore_path)
