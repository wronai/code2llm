"""Optimized project analyzer with caching and parallel processing."""

import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .config import Config, FAST_CONFIG, ALL_EXTENSIONS, LANGUAGE_EXTENSIONS
from .models import AnalysisResult, FlowEdge, FlowNode, Pattern
from ..analysis.call_graph import CallGraphExtractor

from .core import FileCache, FastFileFilter, FileAnalyzer, RefactoringAnalyzer, _analyze_single_file


class ProjectAnalyzer:
    """Main analyzer with parallel processing."""
    
    def __init__(self, config: Optional[Config] = None, project_path: Optional[Path] = None):
        self.config = config or FAST_CONFIG
        self.project_path = project_path
        self.cache = FileCache(
            self.config.performance.cache_dir,
            self.config.performance.cache_ttl_hours
        ) if self.config.performance.enable_cache else None
        self.file_filter = FastFileFilter(self.config.filters, project_path)
        self.refactoring_analyzer = RefactoringAnalyzer(self.config, self.file_filter)
    
    def analyze_project(self, project_path: str) -> AnalysisResult:
        """Analyze entire project."""
        start_time = time.time()
        
        project_path = Path(project_path).resolve()
        if not project_path.exists():
            raise FileNotFoundError(f"Project path does not exist: {project_path}")
        
        # Update project path for gitignore support if not set during init
        if not self.project_path:
            self.project_path = project_path
            self.file_filter = FastFileFilter(self.config.filters, project_path)
        
        # Collect Python files
        files = self._collect_files(project_path)
        
        if self.config.verbose:
            print(f"Found {len(files)} files to analyze")
            print(f"  - Parallel: {self.config.performance.parallel_enabled}, Workers: {self.config.performance.parallel_workers}")
        
        # Analyze files
        if self.config.performance.parallel_enabled and len(files) > 1:
            results = self._analyze_parallel(files)
        else:
            results = self._analyze_sequential(files)
        
        # Merge results
        merged = self._merge_results(results, str(project_path))
        
        # Build call graph
        self._build_call_graph(merged)
        
        if not self.config.performance.skip_pattern_detection:
            self._detect_patterns(merged)
            
        # Refactoring analysis
        if self.config.verbose:
            print(f"  - Running refactoring analysis...", flush=True)
        self.refactoring_analyzer.perform_refactoring_analysis(merged)
        if self.config.verbose:
            print(f"  - Refactoring analysis complete", flush=True)
        
        # Calculate stats
        elapsed = time.time() - start_time
        merged.stats = {
            'files_processed': len(files),
            'functions_found': len(merged.functions),
            'classes_found': len(merged.classes),
            'nodes_created': len(merged.nodes),
            'edges_created': len(merged.edges),
            'patterns_detected': len(merged.patterns),
            'analysis_time_seconds': round(elapsed, 2),
            'cache_hits': sum(r.get('cache_hits', 0) for r in results),
        }
        
        if self.config.verbose:
            print(f"Analysis complete in {elapsed:.2f}s")
            print(f"  Functions: {len(merged.functions)}")
            print(f"  Classes: {len(merged.classes)}")
            print(f"  CFG Nodes: {len(merged.nodes)}")
            print(f"  Patterns: {len(merged.patterns)}")
        
        return merged
    
    def _collect_files(self, project_path: Path) -> List[Tuple[str, str]]:
        """Collect all source files with their module names for all supported languages."""
        files = []
        
        # Collect files for all supported extensions
        for ext in ALL_EXTENSIONS:
            for src_file in project_path.rglob(f"*{ext}"):
                file_str = str(src_file)
                if not self.file_filter.should_process(file_str):
                    continue
                
                # Calculate module name
                rel_path = src_file.relative_to(project_path)
                parts = list(rel_path.parts)[:-1]  # Remove filename
                
                # Handle init files for various languages
                is_init = src_file.name in ('__init__.py', 'index.js', 'index.ts', 'mod.rs', 'lib.rs')
                if is_init:
                    module_name = '.'.join(parts) if parts else project_path.name
                else:
                    module_name = '.'.join(parts + [src_file.stem])
                
                files.append((file_str, module_name))
        
        return files
    
    def _analyze_parallel(self, files: List[Tuple[str, str]]) -> List[Dict]:
        """Analyze files in parallel."""
        results = []
        workers = min(self.config.performance.parallel_workers, len(files))
        
        # Convert config to dict for pickle compatibility
        config_dict = {
            'mode': self.config.mode,
            'max_depth_enumeration': self.config.max_depth_enumeration,
            'detect_state_machines': self.config.detect_state_machines,
            'detect_recursion': self.config.detect_recursion,
            'output_dir': self.config.output_dir,
        }
        
        with ProcessPoolExecutor(max_workers=workers) as executor:
            # Submit all jobs
            future_to_file = {
                executor.submit(_analyze_single_file, (file_path, module_name, config_dict)): (file_path, module_name)
                for file_path, module_name in files
            }
            
            # Collect results as they complete
            completed = 0
            for future in as_completed(future_to_file):
                file_path, module_name = future_to_file[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    if self.config.verbose:
                        print(f"Error analyzing {file_path}: {e}")
                completed += 1
                if self.config.verbose and completed % 10 == 0:
                    print(f"  - Progress: {completed}/{len(files)} files analyzed ({completed*100//len(files)}%)", flush=True)
        
        return results
    
    def _analyze_sequential(self, files: List[Tuple[str, str]]) -> List[Dict]:
        """Analyze files sequentially."""
        results = []
        analyzer = FileAnalyzer(self.config, self.cache)
        total = len(files)
        
        for i, (file_path, module_name) in enumerate(files, 1):
            try:
                result = analyzer.analyze_file(file_path, module_name)
                if result:
                    results.append(result)
            except Exception as e:
                if self.config.verbose:
                    print(f"Error analyzing {file_path}: {e}")
            if self.config.verbose and (i % 10 == 0 or i == total):
                print(f"  - Progress: {i}/{total} files analyzed ({i*100//total}%)", flush=True)
        
        return results
    
    def _merge_results(self, results: List[Dict], project_path: str) -> AnalysisResult:
        """Merge results from multiple files."""
        merged = AnalysisResult(project_path=project_path)
        
        for result in results:
            # Merge module info
            if 'module' in result:
                module_name = result['module'].name
                merged.modules[module_name] = result['module']
            
            # Merge functions
            for func_name, func_info in result.get('functions', {}).items():
                merged.functions[func_name] = func_info
            
            # Merge classes
            for class_name, class_info in result.get('classes', {}).items():
                merged.classes[class_name] = class_info
            
            # Merge nodes
            for node_id, node_info in result.get('nodes', {}).items():
                merged.nodes[node_id] = node_info
            
            # Merge edges
            merged.edges.extend(result.get('edges', []))
            
            # Merge mutations and data flows
            if 'mutations' in result:
                merged.mutations.extend(result['mutations'])
            if 'data_flows' in result:
                merged.data_flows.update(result['data_flows'])
        
        return merged
    
    def _build_call_graph(self, result: AnalysisResult) -> None:
        """Build call graph and find entry points."""
        if self.config.verbose:
            print(f"  - Building call graph for {len(result.functions)} functions...", flush=True)
        
        # Build lookup maps for O(1) resolution
        # Map simple name -> list of full names (for overloaded methods)
        simple_to_full: Dict[str, List[str]] = {}
        for known_name in result.functions:
            simple_name = known_name.split('.')[-1]
            if simple_name not in simple_to_full:
                simple_to_full[simple_name] = []
            simple_to_full[simple_name].append(known_name)
        
        # Map calls between functions
        for func_name, func in result.functions.items():
            for idx, called in enumerate(func.calls):
                # Try exact match first, then suffix match
                if called in result.functions:
                    resolved = called
                elif called in simple_to_full:
                    # Use first match if multiple (common case: single match)
                    candidates = simple_to_full[called]
                    # Prefer exact module match if available
                    resolved = None
                    for cand in candidates:
                        if func_name.rsplit('.', 1)[0] == cand.rsplit('.', 1)[0]:
                            resolved = cand
                            break
                    if resolved is None:
                        resolved = candidates[0]
                else:
                    continue  # Unknown function
                
                func.calls[idx] = resolved
                result.functions[resolved].called_by.append(func_name)
        
        # Find entry points (not called by anything)
        for func_name, func in result.functions.items():
            if not func.called_by:
                result.entry_points.append(func_name)
        
        if self.config.verbose:
            print(f"  - Call graph complete: {len(result.entry_points)} entry points found", flush=True)
    
    def analyze_files(self, files: List[Tuple[str, str]], project_path: str) -> AnalysisResult:
        """Analyze specific list of files (for chunked analysis).
        
        Args:
            files: List of (file_path, module_name) tuples
            project_path: Base project path for the result
        """
        start_time = time.time()
        
        if self.config.verbose:
            print(f"Analyzing {len(files)} specific files")
        
        # Analyze files
        if self.config.performance.parallel_enabled and len(files) > 1:
            results = self._analyze_parallel(files)
        else:
            results = self._analyze_sequential(files)
        
        # Merge results
        merged = self._merge_results(results, project_path)
        
        # Build call graph
        self._build_call_graph(merged)
        
        if not self.config.performance.skip_pattern_detection:
            self._detect_patterns(merged)
        
        # Refactoring analysis
        self.refactoring_analyzer.perform_refactoring_analysis(merged)
        
        # Calculate stats
        elapsed = time.time() - start_time
        merged.stats = {
            'files_processed': len(files),
            'functions_found': len(merged.functions),
            'classes_found': len(merged.classes),
            'nodes_created': len(merged.nodes),
            'edges_created': len(merged.edges),
            'patterns_detected': len(merged.patterns),
            'analysis_time_seconds': round(elapsed, 2),
            'cache_hits': sum(r.get('cache_hits', 0) for r in results),
        }
        
        return merged
    
    def _detect_patterns(self, result: AnalysisResult) -> None:
        """Detect behavioral patterns."""
        # Detect recursion
        for func_name, func in result.functions.items():
            if func_name in func.calls:
                result.patterns.append(Pattern(
                    name=f"recursion_{func.name}",
                    type="recursion",
                    confidence=0.9,
                    functions=[func_name],
                    entry_points=[func_name],
                ))
        
        # Detect state machines (simple heuristic)
        for class_name, cls in result.classes.items():
            state_methods = [m for m in cls.methods if any(
                s in m.lower() for s in ['state', 'transition', 'enter', 'exit', 'connect', 'disconnect']
            )]
            if len(state_methods) >= 2:
                cls.is_state_machine = True
                result.patterns.append(Pattern(
                    name=f"state_machine_{cls.name}",
                    type="state_machine",
                    confidence=0.7,
                    functions=cls.methods,
                    entry_points=cls.methods[:1],
                ))


# Re-export for backward compatibility
from .core import FileCache, FastFileFilter, FileAnalyzer
