"""Large repository analyzer with hierarchical chunking.

Splitting strategy:
1. Check total project size
2. Split by level 1 folders first
3. If level 1 folder >256KB, split by level 2 subfolders
4. If still too big, use file count chunking
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class SubProject:
    """Represents a sub-project within a larger repository."""
    name: str
    path: Path
    relative_path: str
    files: List[Tuple[str, str]] = field(default_factory=list)  # (file_path, module_name)
    level: int = 1  # Nesting level (1=root dirs, 2=subdirs)
    priority: int = 0
    
    @property
    def estimated_size_kb(self) -> int:
        """Estimate output size based on file count."""
        # Rough estimate: ~3KB per file in TOON format
        file_count = len(self.files)
        return max(1, file_count * 3)
    
    @property
    def file_count(self) -> int:
        return len(self.files)


class HierarchicalRepoSplitter:
    """Splits large repositories using hierarchical approach.
    
    Strategy:
    1. First pass: level 1 folders
    2. If any level 1 folder > limit, split into level 2 subfolders
    3. Continue until all chunks under limit
    """
    
    # Size limits
    DEFAULT_SIZE_LIMIT_KB = 256
    MAX_FILES_PER_CHUNK = 50
    
    def __init__(
        self,
        size_limit_kb: int = DEFAULT_SIZE_LIMIT_KB,
        max_files_per_chunk: int = MAX_FILES_PER_CHUNK
    ):
        self.size_limit_kb = size_limit_kb
        self.max_files_per_chunk = max_files_per_chunk
        
    def get_analysis_plan(self, project_path: Path) -> List[SubProject]:
        """Get complete hierarchical analysis plan.
        
        Returns list of subprojects respecting size limits.
        """
        # First, check total project
        total_files = self._count_py_files(project_path)
        total_estimated_kb = total_files * 3
        
        if total_estimated_kb <= self.size_limit_kb:
            # Small project - analyze as single unit
            files = self._collect_files_recursive(project_path, project_path)
            return [SubProject(
                name='root',
                path=project_path,
                relative_path='.',
                files=files,
                level=0,
                priority=100
            )]
        
        # Large project - need hierarchical splitting
        return self._split_hierarchically(project_path)
    
    def _split_hierarchically(self, project_path: Path) -> List[SubProject]:
        """Split project hierarchically by level 1, then level 2 if needed."""
        subprojects = []
        
        # First pass: level 1 directories
        level1_dirs = self._get_level1_dirs(project_path)
        
        for dir_path in level1_dirs:
            files = self._collect_files_in_dir(dir_path, project_path)
            if not files:
                continue
                
            estimated_kb = len(files) * 3
            
            if estimated_kb <= self.size_limit_kb:
                # Level 1 dir fits in limit
                subprojects.append(SubProject(
                    name=dir_path.name,
                    path=dir_path,
                    relative_path=str(dir_path.relative_to(project_path)),
                    files=files,
                    level=1,
                    priority=self._calculate_priority(dir_path.name, 1)
                ))
            else:
                # Level 1 too big - split into level 2
                level2_chunks = self._split_level2(dir_path, project_path)
                subprojects.extend(level2_chunks)
        
        # Add root-level files
        root_files = self._collect_root_files(project_path)
        if root_files:
            subprojects.append(SubProject(
                name='root',
                path=project_path,
                relative_path='.',
                files=root_files,
                level=0,
                priority=100
            ))
        
        # Sort by priority (highest first)
        subprojects.sort(key=lambda x: x.priority, reverse=True)
        
        return subprojects
    
    def _get_level1_dirs(self, project_path: Path) -> List[Path]:
        """Get all level 1 directories (excluding hidden/cache)."""
        dirs = []
        
        for entry in project_path.iterdir():
            if not entry.is_dir():
                continue
            
            dir_name = entry.name.lower()
            
            # Skip hidden and cache directories
            skip_dirs = {
                '.git', '.github', '.vscode', '.idea',
                '__pycache__', 'node_modules', '.venv', 'venv',
                '.tox', '.pytest_cache', '.mypy_cache',
                'build', 'dist', 'egg-info', '.eggs',
                'htmlcov', '.coverage', '.cache'
            }
            
            if dir_name.startswith('.') or dir_name in skip_dirs:
                continue
            
            # Check if directory contains Python files
            if self._contains_python_files(entry):
                dirs.append(entry)
        
        return sorted(dirs, key=lambda d: d.name.lower())
    
    def _split_level2(self, level1_path: Path, project_path: Path) -> List[SubProject]:
        """Split level 1 directory into level 2 subdirectories."""
        chunks = []
        
        # Get level 2 subdirectories
        level2_dirs = [d for d in level1_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
        
        # Sort by priority
        level2_dirs.sort(key=lambda d: self._calculate_priority(d.name, 2), reverse=True)
        
        for dir_path in level2_dirs:
            files = self._collect_files_in_dir(dir_path, project_path)
            if not files:
                continue
            
            estimated_kb = len(files) * 3
            
            if estimated_kb <= self.size_limit_kb:
                # Level 2 dir fits
                chunks.append(SubProject(
                    name=f"{level1_path.name}.{dir_path.name}",
                    path=dir_path,
                    relative_path=str(dir_path.relative_to(project_path)),
                    files=files,
                    level=2,
                    priority=self._calculate_priority(dir_path.name, 2)
                ))
            else:
                # Level 2 still too big - chunk by file count
                file_chunks = self._chunk_by_files(
                    files, level1_path.name, dir_path.name, 
                    dir_path, project_path
                )
                chunks.extend(file_chunks)
        
        # Add any files directly in level1 (not in subdirs)
        level1_direct_files = [
            (str(f), f"{level1_path.name}.{f.stem}")
            for f in level1_path.glob("*.py")
            if not self._should_skip_file(str(f))
        ]
        
        if level1_direct_files:
            estimated_kb = len(level1_direct_files) * 3
            
            if estimated_kb <= self.size_limit_kb:
                chunks.append(SubProject(
                    name=f"{level1_path.name}._root",
                    path=level1_path,
                    relative_path=str(level1_path.relative_to(project_path)),
                    files=level1_direct_files,
                    level=2,
                    priority=self._calculate_priority(level1_path.name, 2) - 10
                ))
            else:
                file_chunks = self._chunk_by_files(
                    level1_direct_files, level1_path.name, "_root",
                    level1_path, project_path
                )
                chunks.extend(file_chunks)
        
        return chunks
    
    def _chunk_by_files(
        self,
        files: List[Tuple[str, str]],
        level1_name: str,
        level2_name: str,
        path: Path,
        project_path: Path
    ) -> List[SubProject]:
        """Chunk large file list by max_files_per_chunk."""
        chunks = []
        chunk_num = 1
        
        remaining_files = files.copy()
        
        while remaining_files:
            chunk_files = remaining_files[:self.max_files_per_chunk]
            remaining_files = remaining_files[self.max_files_per_chunk:]
            
            chunks.append(SubProject(
                name=f"{level1_name}.{level2_name}_part{chunk_num}",
                path=path,
                relative_path=str(path.relative_to(project_path)),
                files=chunk_files,
                level=3,
                priority=30 - chunk_num  # Lower priority for chunked parts
            ))
            chunk_num += 1
        
        return chunks
    
    def _collect_files_in_dir(
        self,
        dir_path: Path,
        project_path: Path
    ) -> List[Tuple[str, str]]:
        """Collect Python files recursively in a directory."""
        files = []
        
        for py_file in dir_path.rglob("*.py"):
            file_str = str(py_file)
            
            if self._should_skip_file(file_str):
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
    
    def _collect_files_recursive(
        self,
        dir_path: Path,
        project_path: Path
    ) -> List[Tuple[str, str]]:
        """Collect all Python files recursively."""
        return self._collect_files_in_dir(dir_path, project_path)
    
    def _collect_root_files(self, project_path: Path) -> List[Tuple[str, str]]:
        """Collect Python files at root level."""
        files = []
        
        for py_file in project_path.glob("*.py"):
            file_str = str(py_file)
            
            if self._should_skip_file(file_str):
                continue
            
            module_name = py_file.stem
            files.append((file_str, module_name))
        
        return files
    
    def _count_py_files(self, path: Path) -> int:
        """Count Python files (excluding tests/cache)."""
        count = 0
        for py_file in path.rglob("*.py"):
            if not self._should_skip_file(str(py_file)):
                count += 1
        return count
    
    def _contains_python_files(self, dir_path: Path) -> bool:
        """Check if directory contains any Python files."""
        for py_file in dir_path.rglob("*.py"):
            if not self._should_skip_file(str(py_file)):
                return True
        return False
    
    def _should_skip_file(self, file_str: str) -> bool:
        """Check if file should be skipped."""
        lower_path = file_str.lower()
        skip_patterns = [
            'test', '_test', 'conftest',
            '__pycache__', '.venv', 'venv',
            'node_modules', '.git',
        ]
        return any(pattern in lower_path for pattern in skip_patterns)
    
    def _calculate_priority(self, name: str, level: int) -> int:
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


def should_use_chunking(project_path: Path, size_threshold_kb: int = 256) -> bool:
    """Check if repository should use chunked analysis.
    
    Estimates size based on file count.
    """
    splitter = HierarchicalRepoSplitter(size_limit_kb=size_threshold_kb)
    total_files = splitter._count_py_files(project_path)
    estimated_kb = total_files * 3
    return estimated_kb > size_threshold_kb


def get_analysis_plan(project_path: Path, size_limit_kb: int = 256) -> List[SubProject]:
    """Get analysis plan for project (auto-detect if chunking needed)."""
    splitter = HierarchicalRepoSplitter(size_limit_kb=size_limit_kb)
    return splitter.get_analysis_plan(project_path)


# Backward compatibility
LargeRepoSplitter = HierarchicalRepoSplitter
