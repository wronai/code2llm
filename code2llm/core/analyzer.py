"""Optimized project analyzer with caching and parallel processing."""

import logging
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

from .config import Config, FAST_CONFIG, ALL_EXTENSIONS, LANGUAGE_EXTENSIONS
from .models import AnalysisResult, FlowEdge, FlowNode, Pattern
from code2llm.analysis.call_graph import CallGraphExtractor

from .file_cache import FileCache
from .file_filter import FastFileFilter
from .file_analyzer import FileAnalyzer, _analyze_single_file
from .persistent_cache import PersistentCache
from .refactoring import RefactoringAnalyzer


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
        project_path = self._resolve_project_path(project_path)
        files = self._collect_files(project_path)

        if self.config.verbose:
            print(f"Found {len(files)} files to analyze")
            print(f"  - Parallel: {self.config.performance.parallel_enabled}, Workers: {self.config.performance.parallel_workers}")

        pcache, cached_results, files_to_analyze = self._load_from_persistent_cache(files, project_path)
        fresh_results = self._run_analysis(files_to_analyze)
        self._store_to_persistent_cache(pcache, files_to_analyze, fresh_results)

        merged = self._merge_results(cached_results + fresh_results, str(project_path))
        self._build_call_graph(merged)
        if not self.config.performance.skip_pattern_detection:
            self._detect_patterns(merged)
        if self.config.verbose:
            print(f"  - Running refactoring analysis...", flush=True)
        self.refactoring_analyzer.perform_refactoring_analysis(merged)
        if self.config.verbose:
            print(f"  - Refactoring analysis complete", flush=True)
        merged.stats = self._build_stats(files, cached_results + fresh_results, merged, start_time)
        if self.config.verbose:
            self._print_summary(merged)
        return merged

    def _resolve_project_path(self, project_path: str) -> Path:
        """Resolve and validate project path; initialise file_filter if needed."""
        p = Path(project_path).resolve()
        if not p.exists():
            raise FileNotFoundError(f"Project path does not exist: {p}")
        if not self.project_path:
            self.project_path = p
            self.file_filter = FastFileFilter(self.config.filters, p)
        return p

    def _load_from_persistent_cache(
        self, files: List[Tuple[str, str]], project_path: Path
    ) -> Tuple[Optional["PersistentCache"], List[Dict], List[Tuple[str, str]]]:
        """Split files into cached/changed; return (pcache, cached_results, files_to_analyze)."""
        if getattr(self.config, 'no_cache', False):
            return None, [], files
        try:
            pcache = PersistentCache(str(project_path))
            file_paths = [fp for fp, _ in files]
            changed_paths, cached_paths = pcache.get_changed_files(file_paths)
            path_to_module = dict(files)
            cached_results: List[Dict] = []
            for fp in cached_paths:
                r = pcache.get_file_result(fp)
                if r is not None:
                    cached_results.append(r)
                else:
                    changed_paths.append(fp)
            files_to_analyze = [(fp, path_to_module[fp]) for fp in changed_paths]
            if self.config.verbose:
                print(f"  - Persistent cache: {len(cached_results)} hits, {len(files_to_analyze)} to analyze")
            return pcache, cached_results, files_to_analyze
        except Exception as exc:
            logger.debug("PersistentCache init failed, falling back: %s", exc)
            return None, [], files

    def _run_analysis(self, files_to_analyze: List[Tuple[str, str]]) -> List[Dict]:
        """Analyze files in parallel or sequentially depending on config."""
        if not files_to_analyze:
            return []
        if self.config.performance.parallel_enabled and len(files_to_analyze) > 1:
            return self._analyze_parallel(files_to_analyze)
        return self._analyze_sequential(files_to_analyze)

    def _store_to_persistent_cache(
        self,
        pcache: Optional["PersistentCache"],
        files_to_analyze: List[Tuple[str, str]],
        fresh_results: List[Dict],
    ) -> None:
        """Persist fresh analysis results to cache; no-op when pcache is None."""
        if pcache is None or not fresh_results:
            return
        path_to_result = {r.get('file', ''): r for r in fresh_results if r}
        for fp, _ in files_to_analyze:
            if fp in path_to_result:
                try:
                    pcache.put_file_result(fp, path_to_result[fp])
                except Exception as exc:
                    logger.debug("put_file_result failed: %s", exc)
        try:
            pcache.save()
        except Exception as exc:
            logger.debug("PersistentCache save failed: %s", exc)

    def _build_stats(self, files: List, results: List[Dict], merged: AnalysisResult, start_time: float) -> Dict:
        """Build analysis stats dict."""
        return {
            'files_processed': len(files),
            'functions_found': len(merged.functions),
            'classes_found': len(merged.classes),
            'nodes_created': len(merged.nodes),
            'edges_created': len(merged.edges),
            'patterns_detected': len(merged.patterns),
            'analysis_time_seconds': round(time.time() - start_time, 2),
            'cache_hits': sum(r.get('cache_hits', 0) for r in results),
        }

    def _print_summary(self, merged: AnalysisResult) -> None:
        """Print verbose analysis summary."""
        print(f"Analysis complete in {merged.stats.get('analysis_time_seconds', 0):.2f}s")
        print(f"  Functions: {len(merged.functions)}")
        print(f"  Classes: {len(merged.classes)}")
        print(f"  CFG Nodes: {len(merged.nodes)}")
        print(f"  Patterns: {len(merged.patterns)}")
    
    def _collect_files(self, project_path: Path) -> List[Tuple[str, str]]:
        """Collect all source files with their module names for all supported languages.
        
        Uses a single os.walk traversal with early directory pruning instead of
        separate rglob calls per extension (~40x speedup on large repos).
        """
        files = []
        ext_set = set(ALL_EXTENSIONS)  # O(1) lookup
        init_names = frozenset({'__init__.py', 'index.js', 'index.ts', 'mod.rs', 'lib.rs'})
        seen = set()  # guard against duplicate paths (e.g. .h in both c and cpp lists)
        project_str = str(project_path)

        for dirpath, dirnames, filenames in os.walk(project_str, topdown=True):
            # Prune skipped directories in-place so os.walk won't descend into them
            dirnames[:] = [
                d for d in dirnames
                if not self.file_filter.should_skip_dir(d)
            ]

            for filename in filenames:
                suffix = os.path.splitext(filename)[1].lower()
                if suffix not in ext_set:
                    continue

                file_str = os.path.join(dirpath, filename)
                if file_str in seen:
                    continue
                seen.add(file_str)

                if not self.file_filter.should_process(file_str):
                    continue

                # Calculate module name from relative path
                rel = os.path.relpath(file_str, project_str)
                parts = rel.replace('\\', '/').split('/')
                dir_parts = parts[:-1]  # everything before filename

                if filename in init_names:
                    module_name = '.'.join(dir_parts) if dir_parts else project_path.name
                else:
                    stem = os.path.splitext(filename)[0]
                    module_name = '.'.join(dir_parts + [stem]) if dir_parts else stem

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
    
    def _build_simple_name_map(self, result: AnalysisResult) -> Dict[str, List[str]]:
        """Build lookup map: simple name -> list of full qualified names."""
        simple_to_full: Dict[str, List[str]] = {}
        for known_name in result.functions:
            simple_name = known_name.split('.')[-1]
            if simple_name not in simple_to_full:
                simple_to_full[simple_name] = []
            simple_to_full[simple_name].append(known_name)
        return simple_to_full

    def _resolve_call(self, called: str, func_name: str,
                     result: AnalysisResult,
                     simple_to_full: Dict[str, List[str]]) -> str | None:
        """Resolve a function call to its fully qualified name."""
        # Try exact match first
        if called in result.functions:
            return called

        # Try simple name lookup
        if called not in simple_to_full:
            return None  # Unknown function

        candidates = simple_to_full[called]

        # Prefer exact module match if available
        func_module = func_name.rsplit('.', 1)[0]
        for cand in candidates:
            cand_module = cand.rsplit('.', 1)[0]
            if func_module == cand_module:
                return cand

        # Fall back to first candidate
        return candidates[0]

    def _collect_call_edges(self, result: AnalysisResult,
                           simple_to_full: Dict[str, List[str]]) -> None:
        """Collect and resolve all call graph edges."""
        for func_name, func in result.functions.items():
            for idx, called in enumerate(func.calls):
                resolved = self._resolve_call(called, func_name, result, simple_to_full)
                if resolved is None:
                    continue

                func.calls[idx] = resolved
                result.functions[resolved].called_by.append(func_name)

    def _find_entry_points(self, result: AnalysisResult) -> None:
        """Find entry points (functions not called by any other function)."""
        for func_name, func in result.functions.items():
            if not func.called_by:
                result.entry_points.append(func_name)

    def _build_call_graph(self, result: AnalysisResult) -> None:
        """Build call graph and find entry points."""
        if self.config.verbose:
            print(f"  - Building call graph for {len(result.functions)} functions...", flush=True)

        # Build lookup maps for O(1) resolution
        simple_to_full = self._build_simple_name_map(result)

        # Map calls between functions
        self._collect_call_edges(result, simple_to_full)

        # Find entry points
        self._find_entry_points(result)

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
from .file_cache import FileCache
from .file_filter import FastFileFilter
from .file_analyzer import FileAnalyzer
