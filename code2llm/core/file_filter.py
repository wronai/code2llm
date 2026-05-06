"""Fast file filtering with pattern matching."""

import fnmatch
import re
from pathlib import Path
from .config import FilterConfig
from .gitignore import load_gitignore_patterns
from .source_classifier import (
    ARCHIVE_DIR_NAMES,
    GENERATED_OUTPUT_DIR_NAMES,
    is_generated_artifact,
)


_SKIP_DIR_NAMES = frozenset({
    '.git', '.svn', '.hg',
    '.vscode', '.idea', '.github',
    '__pycache__', '.venv', 'venv', 'env', 'fresh_env', 'test-env',
    '.tox', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.pyqual',
    'node_modules',
    'build', 'dist', 'target', 'out',
    '.eggs', 'egg-info',
    'htmlcov', '.coverage', '.cache',
    'lib', 'lib64', 'site-packages', 'include', 'bin', 'share',
    '.code2llm_cache',
    'tests', 'test',
    'coverage', '.nyc_output',
    # Backup and auto-generated directories that often contain venvs
    '.algitex', '.backup', 'backups', '.bak', 'bak',
    # Additional venv patterns
    'virtualenv', '.virtualenv', 'envs', '.envs', 'venv-', '.venv-',
    # CI/CD and deployment artifacts
    '.terraform', '.serverless', '.netlify', '.vercel',
}) | ARCHIVE_DIR_NAMES | GENERATED_OUTPUT_DIR_NAMES


class FastFileFilter:
    """Fast file filtering with pattern matching."""
    
    def __init__(self, config: FilterConfig, project_path: Path = None):
        self.config = config
        self.project_path = project_path

        # Split patterns into fast substring checks vs pre-compiled regex
        self._simple_excludes = []
        self._regex_excludes = []
        for p in config.exclude_patterns:
            p_lower = p.lower()
            if any(c in p_lower for c in ('*', '?', '[')):
                self._regex_excludes.append(re.compile(fnmatch.translate(p_lower)))
            else:
                self._simple_excludes.append(p_lower)

        self._simple_includes = []
        self._regex_includes = []
        for p in config.include_patterns:
            p_lower = p.lower()
            if any(c in p_lower for c in ('*', '?', '[')):
                self._regex_includes.append(re.compile(fnmatch.translate(p_lower)))
            else:
                self._simple_includes.append(p_lower)

        # Load gitignore patterns if enabled and project path is provided
        self._gitignore_parser = None
        if config.gitignore_enabled and project_path:
            self._gitignore_parser = load_gitignore_patterns(project_path)
    
    def should_skip_dir(self, dirname: str) -> bool:
        """Fast O(1) check: skip this directory entirely during tree walk?"""
        lower = dirname.lower()
        return lower.startswith('.') or lower in _SKIP_DIR_NAMES

    def _passes_gitignore(self, file_path: str) -> bool:
        """Check if file passes gitignore patterns (True = pass, False = excluded)."""
        if not self._gitignore_parser or not self.project_path:
            return True
        return not self._gitignore_parser.is_ignored(Path(file_path), self.project_path)

    def _passes_excludes(self, path_lower: str, basename_lower: str) -> bool:
        """Check if file passes exclude patterns (True = pass, False = excluded)."""
        # Fast substring excludes
        for pattern in self._simple_excludes:
            if pattern in path_lower:
                return False

        # Pre-compiled wildcard excludes
        for regex in self._regex_excludes:
            if regex.match(path_lower) or regex.match(basename_lower):
                return False

        return True

    def _passes_includes(self, path_lower: str) -> bool:
        """Check if file passes include patterns (True = include, False = exclude)."""
        if not self._simple_includes and not self._regex_includes:
            return True  # No includes defined = include all

        return (
            any(p in path_lower for p in self._simple_includes) or
            any(r.match(path_lower) for r in self._regex_includes)
        )

    def should_process(self, file_path: str) -> bool:
        """Check if file should be processed."""
        path_lower = file_path.lower()
        basename_lower = Path(file_path).name.lower()

        if is_generated_artifact(file_path, self.project_path):
            return False

        return (
            self._passes_gitignore(file_path) and
            self._passes_excludes(path_lower, basename_lower) and
            self._passes_includes(path_lower)
        )
    
    def _passes_line_count(self, line_count: int) -> bool:
        """Check if function passes line count threshold."""
        return line_count >= self.config.min_function_lines

    def _passes_visibility(self, is_private: bool, is_property: bool, is_accessor: bool) -> bool:
        """Check if function passes visibility filters."""
        if self.config.skip_private and is_private:
            return False
        if self.config.skip_properties and is_property:
            return False
        if self.config.skip_accessors and is_accessor:
            return False
        return True

    def should_skip_function(self, line_count: int, is_private: bool = False,
                            is_property: bool = False, is_accessor: bool = False) -> bool:
        """Check if function should be skipped."""
        return not (
            self._passes_line_count(line_count) and
            self._passes_visibility(is_private, is_property, is_accessor)
        )
