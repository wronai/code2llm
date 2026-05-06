"""File collection and filtering utilities for repository analysis."""

from pathlib import Path
from typing import List, Tuple, Optional

from functools import lru_cache
from .gitignore import load_gitignore_patterns, GitIgnoreParser
from .source_classifier import (
    ARCHIVE_DIR_NAMES,
    GENERATED_OUTPUT_DIR_NAMES,
    is_generated_artifact,
)

# Directories to skip during analysis
SKIP_DIRS = {
    '.git', '.github', '.vscode', '.idea',
    '__pycache__', 'node_modules', '.venv', 'venv', 'fresh_env', 'test-env',
    '.tox', '.pytest_cache', '.mypy_cache',
    'build', 'dist', 'egg-info', '.eggs',
    'htmlcov', '.coverage', '.cache',
    'lib', 'lib64', 'site-packages', 'include', 'bin', 'share',  # venv internals
} | ARCHIVE_DIR_NAMES | GENERATED_OUTPUT_DIR_NAMES

# Patterns that indicate a file should be skipped
SKIP_PATTERNS = [
    'conftest',
    '__pycache__', '.venv', 'venv', 'fresh_env', 'test-env',
    'node_modules', '.git',
    '/lib/', '/lib64/', '/site-packages/',  # venv internals
    '/include/', '/bin/python', '/share/',
    '/tests/', '/test/',  # test directories (but not projects named *test*)
]


@lru_cache(maxsize=16)
def _get_gitignore_parser(project_path: Path) -> Optional[GitIgnoreParser]:
    """Load gitignore parser for project if available (cached per path)."""
    try:
        return load_gitignore_patterns(project_path)
    except Exception:
        return None


def should_skip_file(file_str: str, project_path: Optional[Path] = None, 
                     gitignore_parser: Optional[GitIgnoreParser] = None) -> bool:
    """Check if file should be skipped."""
    lower_path = file_str.lower()
    if any(pattern in lower_path for pattern in SKIP_PATTERNS):
        return True
    if is_generated_artifact(file_str, project_path):
        return True
    
    # Check gitignore if parser provided
    if gitignore_parser and project_path:
        try:
            if gitignore_parser.is_ignored(Path(file_str), project_path):
                return True
        except Exception:
            pass
    
    return False


def collect_files_in_dir(
    dir_path: Path,
    project_path: Path
) -> List[Tuple[str, str]]:
    """Collect Python files recursively in a directory."""
    files = []
    gitignore_parser = _get_gitignore_parser(project_path)

    for py_file in dir_path.rglob("*.py"):
        file_str = str(py_file)

        if should_skip_file(file_str, project_path, gitignore_parser):
            continue

        # Calculate module name
        try:
            rel_path = py_file.relative_to(project_path)
            parts = list(rel_path.parts)[:-1]

            if py_file.name == '__init__.py':
                module_name = '.'.join(parts) if parts else dir_path.name
            else:
                module_name = '.'.join(parts + [py_file.stem])

            files.append((file_str, module_name))
        except ValueError:
            # File not relative to project_path
            files.append((file_str, py_file.stem))

    return files


def collect_root_files(project_path: Path) -> List[Tuple[str, str]]:
    """Collect Python files at root level."""
    files = []
    gitignore_parser = _get_gitignore_parser(project_path)

    for py_file in project_path.glob("*.py"):
        file_str = str(py_file)

        if should_skip_file(file_str, project_path, gitignore_parser):
            continue

        module_name = py_file.stem
        files.append((file_str, module_name))

    return files


def count_py_files(path: Path) -> int:
    """Count Python files (excluding tests/cache and gitignore patterns)."""
    count = 0
    gitignore_parser = _get_gitignore_parser(path)
    for py_file in path.rglob("*.py"):
        if not should_skip_file(str(py_file), path, gitignore_parser):
            count += 1
    return count


def contains_python_files(dir_path: Path) -> bool:
    """Check if directory contains any Python files."""
    gitignore_parser = _get_gitignore_parser(dir_path)
    for py_file in dir_path.rglob("*.py"):
        if not should_skip_file(str(py_file), dir_path, gitignore_parser):
            return True
    return False


def get_level1_dirs(project_path: Path) -> List[Path]:
    """Get all level 1 directories (excluding hidden/cache)."""
    dirs = []

    for entry in project_path.iterdir():
        if not entry.is_dir():
            continue

        dir_name = entry.name.lower()

        # Skip wheel packages (e.g., networkx-3.6.1-py3-none-any)
        if '-py3-none-any' in dir_name or dir_name.endswith('.dist-info'):
            continue

        if dir_name.startswith('.') or dir_name in SKIP_DIRS:
            continue

        # Check if directory contains Python files
        if contains_python_files(entry):
            dirs.append(entry)

    return sorted(dirs, key=lambda d: d.name.lower())


def calculate_priority(name: str, level: int) -> int:
    """Calculate priority based on name and nesting level.
    
    Higher priority = analyzed first
    """
    name_lower = name.lower()
    base_priority = 50

    # Core code
    if name_lower in {'src', 'source', 'lib', 'core', 'app', 'application'}:
        base_priority = 100
    elif name_lower in {'api', 'cli', 'cmd', 'commands', 'server', 'backend'}:
        base_priority = 80
    elif name_lower in {'utils', 'util', 'tools', 'scripts'}:
        base_priority = 60
    elif name_lower in {'docs', 'doc', 'documentation'}:
        base_priority = 40
    elif name_lower in {'examples', 'example', 'demo', 'demos', 'samples'}:
        base_priority = 30
    elif name_lower in {'tests', 'test', 'testing'}:
        base_priority = 20

    # Deeper nesting = slightly lower priority
    level_penalty = level * 5

    return base_priority - level_penalty
