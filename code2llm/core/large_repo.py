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
        # Rough estimate: ~1KB per file in TOON format
        file_count = len(self.files)
        return max(1, file_count * 1)
    
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
    MAX_FILES_PER_CHUNK = 120  # ~360KB at 3KB per file
    TARGET_CHUNKS = 7  # Target number of chunks for large repos
    MERGE_MARGIN_KB = 192  # Allow up to 448KB per chunk (256+192)
    
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
        """Split project hierarchically with aggressive consolidation to ~7 chunks."""
        subprojects = []
        
        # Get level 1 directories
        level1_dirs = self._get_level1_dirs(project_path)
        
        # Calculate total size
        total_kb = 0
        dir_sizes = {}
        for dir_path in level1_dirs:
            files = self._collect_files_in_dir(dir_path, project_path)
            estimated_kb = len(files) * 3
            dir_sizes[dir_path] = (files, estimated_kb)
            total_kb += estimated_kb
        
        # Strategy: If total fits in ~7 chunks, try to consolidate
        target_per_chunk = max(self.size_limit_kb, total_kb // self.TARGET_CHUNKS)
        
        # First pass: collect small L1 dirs for potential merging
        small_l1_dirs = []  # dirs that fit within margin
        large_l1_dirs = []  # dirs that need splitting
        
        for dir_path in level1_dirs:
            files, estimated_kb = dir_sizes[dir_path]
            if not files:
                continue
            
            if estimated_kb <= self.size_limit_kb + self.MERGE_MARGIN_KB:
                small_l1_dirs.append((dir_path, files, estimated_kb))
            else:
                large_l1_dirs.append((dir_path, files, estimated_kb))
        
        # Merge small L1 directories into consolidated chunks
        if small_l1_dirs:
            subprojects.extend(self._merge_small_l1_dirs(small_l1_dirs, project_path))
        
        # Process large L1 directories
        for dir_path, files, estimated_kb in large_l1_dirs:
            level2_chunks = self._split_level2_consolidated(dir_path, project_path, target_per_chunk)
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
    
    def _merge_small_l1_dirs(
        self, 
        small_l1_dirs: List[Tuple[Path, List, int]], 
        project_path: Path
    ) -> List[SubProject]:
        """Merge small L1 directories into consolidated chunks up to size limit."""
        chunks = []
        
        # Sort by priority (highest first)
        sorted_dirs = sorted(
            small_l1_dirs, 
            key=lambda x: self._calculate_priority(x[0].name, 1), 
            reverse=True
        )
        
        current_chunk_files = []
        current_chunk_names = []
        current_size = 0
        
        effective_limit = self.size_limit_kb + 128  # Use 384KB as effective limit
        
        for dir_path, files, estimated_kb in sorted_dirs:
            # Check if adding this dir would exceed limit
            if current_chunk_files and (current_size + estimated_kb > effective_limit):
                # Flush current chunk
                chunk_name = '_'.join(current_chunk_names) if len(current_chunk_names) <= 3 else f"batch_{len(chunks)+1}"
                
                chunks.append(SubProject(
                    name=chunk_name,
                    path=project_path,
                    relative_path=str(project_path.relative_to(project_path)),
                    files=current_chunk_files.copy(),
                    level=1,
                    priority=50  # Medium priority for merged batch
                ))
                
                # Start new chunk
                current_chunk_files = []
                current_chunk_names = []
                current_size = 0
            
            # Add to current chunk
            current_chunk_files.extend(files)
            current_chunk_names.append(dir_path.name)
            current_size += estimated_kb
        
        # Flush remaining chunk
        if current_chunk_files:
            chunk_name = '_'.join(current_chunk_names) if len(current_chunk_names) <= 3 else f"batch_{len(chunks)+1}"
            
            chunks.append(SubProject(
                name=chunk_name,
                path=project_path,
                relative_path=str(project_path.relative_to(project_path)),
                files=current_chunk_files,
                level=1,
                priority=50
            ))
        
        return chunks
    
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
                '__pycache__', 'node_modules', '.venv', 'venv', 'fresh_env', 'test-env',
                '.tox', '.pytest_cache', '.mypy_cache',
                'build', 'dist', 'egg-info', '.eggs',
                'htmlcov', '.coverage', '.cache',
                'lib', 'lib64', 'site-packages', 'include', 'bin', 'share',  # venv internals
            }
            
            # Skip wheel packages (e.g., networkx-3.6.1-py3-none-any)
            if '-py3-none-any' in dir_name or dir_name.endswith('.dist-info'):
                continue
            
            if dir_name.startswith('.') or dir_name in skip_dirs:
                continue
            
            # Check if directory contains Python files
            if self._contains_python_files(entry):
                dirs.append(entry)
        
        return sorted(dirs, key=lambda d: d.name.lower())
    
    def _split_level2_consolidated(self, level1_path: Path, project_path: Path, target_chunk_kb: int) -> List[SubProject]:
        """Split level 1 directory with aggressive consolidation.
        
        Strategy: Create chunks of ~target_chunk_kb size (up to 384KB with margin).
        """
        all_files = self._collect_files_in_dir(level1_path, project_path)
        if not all_files:
            return []
        
        total_kb = len(all_files) * 3
        
        # If all files fit with large margin, return single chunk
        if total_kb <= self.size_limit_kb + self.MERGE_MARGIN_KB:
            return [SubProject(
                name=level1_path.name,
                path=level1_path,
                relative_path=str(level1_path.relative_to(project_path)),
                files=all_files,
                level=1,
                priority=self._calculate_priority(level1_path.name, 1)
            )]
        
        # Need to split - aim for chunks of target size (up to 320KB)
        chunks = []
        chunk_num = 1
        current_files = []
        current_size = 0
        
        # Sort files by path for consistent ordering
        all_files.sort(key=lambda x: x[0])
        
        # Effective limit: 320KB (256 + 64 safety margin within the 128 total margin)
        effective_limit = self.size_limit_kb + 64
        
        for file_path, module_name in all_files:
            file_kb = 3  # Estimate 3KB per file
            
            # If adding this file would exceed effective limit and we have files, flush chunk
            if current_files and (current_size + file_kb > effective_limit):
                chunk_name = f"{level1_path.name}_part{chunk_num}" if chunk_num > 1 else level1_path.name
                chunks.append(SubProject(
                    name=chunk_name,
                    path=level1_path,
                    relative_path=str(level1_path.relative_to(project_path)),
                    files=current_files.copy(),
                    level=2,
                    priority=self._calculate_priority(level1_path.name, 1) - chunk_num
                ))
                chunk_num += 1
                current_files = []
                current_size = 0
            
            current_files.append((file_path, module_name))
            current_size += file_kb
        
        # Flush remaining files
        if current_files:
            chunk_name = f"{level1_path.name}_part{chunk_num}" if chunk_num > 1 else level1_path.name
            chunks.append(SubProject(
                name=chunk_name,
                path=level1_path,
                relative_path=str(level1_path.relative_to(project_path)),
                files=current_files,
                level=2,
                priority=self._calculate_priority(level1_path.name, 1) - chunk_num
            ))
        
        return chunks
    
    def _categorize_subdirs(
        self, level1_path: Path, project_path: Path
    ) -> Tuple[List, List]:
        """Categorize subdirectories into small and large based on size."""
        level2_dirs = [d for d in level1_path.iterdir() 
                      if d.is_dir() and not d.name.startswith('.')]
        level2_dirs.sort(key=lambda d: self._calculate_priority(d.name, 2), reverse=True)
        
        small_dirs = []
        large_dirs = []
        
        for dir_path in level2_dirs:
            files = self._collect_files_in_dir(dir_path, project_path)
            if not files:
                continue
            
            estimated_kb = len(files) * 3
            priority = self._calculate_priority(dir_path.name, 2)
            
            if estimated_kb > self.size_limit_kb:
                large_dirs.append((dir_path, files, estimated_kb, priority))
            else:
                small_dirs.append((dir_path, files, estimated_kb, priority))
        
        return small_dirs, large_dirs
    
    def _process_large_dirs(
        self, large_dirs: List, level1_path: Path, project_path: Path
    ) -> List[SubProject]:
        """Process large directories with file-level chunking."""
        chunks = []
        for dir_path, files, estimated_kb, priority in large_dirs:
            file_chunks = self._chunk_by_files(
                files, level1_path.name, dir_path.name, 
                dir_path, project_path
            )
            chunks.extend(file_chunks)
        return chunks
    
    def _process_level1_files(self, level1_path: Path, project_path: Path) -> List[SubProject]:
        """Process Python files directly in level1 directory."""
        chunks = []
        
        level1_direct_files = [
            (str(f), f"{level1_path.name}.{f.stem}")
            for f in level1_path.glob("*.py")
            if not self._should_skip_file(str(f))
        ]
        
        if not level1_direct_files:
            return chunks
        
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
    
    def _merge_small_dirs(
        self,
        small_dirs: List[Tuple[Path, List, int, int]],
        level1_path: Path,
        project_path: Path
    ) -> List[SubProject]:
        """Merge small subdirectories into combined chunks up to size limit."""
        chunks = []
        
        # Sort by priority (highest first)
        small_dirs.sort(key=lambda x: x[3], reverse=True)
        
        current_chunk_files = []
        current_chunk_names = []
        current_size = 0
        
        for dir_path, files, estimated_kb, priority in small_dirs:
            # Check if adding this dir would exceed limit
            if current_chunk_files and (current_size + estimated_kb > self.size_limit_kb):
                # Flush current chunk
                chunk_name = f"{level1_path.name}.{'_'.join(current_chunk_names)}"
                if len(current_chunk_names) > 3:
                    chunk_name = f"{level1_path.name}.batch_{len(chunks)+1}"
                
                chunks.append(SubProject(
                    name=chunk_name,
                    path=level1_path,
                    relative_path=str(level1_path.relative_to(project_path)),
                    files=current_chunk_files.copy(),
                    level=2,
                    priority=priority
                ))
                
                # Start new chunk
                current_chunk_files = []
                current_chunk_names = []
                current_size = 0
            
            # Add to current chunk
            current_chunk_files.extend(files)
            current_chunk_names.append(dir_path.name)
            current_size += estimated_kb
        
        # Flush remaining chunk
        if current_chunk_files:
            chunk_name = f"{level1_path.name}.{'_'.join(current_chunk_names)}"
            if len(current_chunk_names) > 3:
                chunk_name = f"{level1_path.name}.batch_{len(chunks)+1}"
            
            chunks.append(SubProject(
                name=chunk_name,
                path=level1_path,
                relative_path=str(level1_path.relative_to(project_path)),
                files=current_chunk_files,
                level=2,
                priority=30  # Default priority for merged batch
            ))
        
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
            '__pycache__', '.venv', 'venv', 'fresh_env', 'test-env',
            'node_modules', '.git',
            '/lib/', '/lib64/', '/site-packages/',  # venv internals
            '/include/', '/bin/python', '/share/',
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
