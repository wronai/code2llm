"""Optimized streaming analyzer with prioritization and progress tracking.

Key optimizations:
1. Lazy CFG generation - only build when needed
2. Memory-bounded analysis with streaming output
3. Smart file prioritization (entry points, public API first)
4. Incremental analysis with change detection
5. Progress reporting with ETA
"""

import time
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

from .config import Config, FAST_CONFIG
from .streaming import (
    ScanStrategy, STRATEGY_STANDARD, StreamingFileCache,
    SmartPrioritizer, FilePriority, StreamingScanner, IncrementalAnalyzer
)


class StreamingAnalyzer:
    """Memory-efficient streaming analyzer with progress tracking."""
    
    def __init__(
        self,
        config: Optional[Config] = None,
        strategy: Optional[ScanStrategy] = None
    ):
        self.config = config or FAST_CONFIG
        self.strategy = strategy or STRATEGY_STANDARD
        
        # Streaming cache with memory bounds
        self.cache = StreamingFileCache(
            max_size=self.strategy.max_files_in_memory,
            cache_dir=self.config.performance.cache_dir
        ) if self.config.performance.enable_cache else None
        
        self.prioritizer = SmartPrioritizer(self.strategy)
        self.scanner = StreamingScanner(self.strategy, self.cache)
        
        # Progress tracking
        self._progress_callback: Optional[callable] = None
        self._cancelled = False
    
    def set_progress_callback(self, callback: callable) -> None:
        """Set callback for progress updates."""
        self._progress_callback = callback
    
    def cancel(self) -> None:
        """Cancel ongoing analysis."""
        self._cancelled = True
    
    def analyze_streaming(
        self,
        project_path: str,
        _output_callback: Optional[callable] = None
    ) -> Iterator[Dict]:
        """Analyze project with streaming output (yields partial results)."""
        start_time = time.time()
        project_path = Path(project_path).resolve()
        
        # Phase 1: Collect and prioritize files
        raw_files = self.scanner.collect_files(project_path)
        prioritized = self.prioritizer.prioritize_files(raw_files, project_path)
        
        total_files = len(prioritized)
        processed = 0
        
        self._report_progress(
            phase="collect",
            current=0,
            total=total_files,
            message=f"Found {total_files} files to analyze"
        )
        
        # Phase 2: Quick scan (functions/classes only)
        quick_results = []
        for priority in prioritized:
            if self._cancelled:
                break
            
            result = self.scanner.quick_scan_file(priority)
            if result:
                quick_results.append(result)
                processed += 1
                
                # Yield incremental result
                yield {
                    'type': 'file_complete',
                    'file': priority.file_path,
                    'priority': priority.priority_score,
                    'functions': len(result.get('functions', {})),
                    'classes': len(result.get('classes', {})),
                    'progress': processed / total_files,
                    'eta_seconds': self._estimate_eta(start_time, processed, total_files)
                }
                
                self._report_progress(
                    phase="quick_scan",
                    current=processed,
                    total=total_files,
                    message=f"Scanned {priority.module_name} (priority: {priority.priority_score:.1f})"
                )
        
        # Phase 3: Build call graph (memory efficient)
        if self.strategy.phase_2_call_graph and not self._cancelled:
            call_graph = self.scanner.build_call_graph_streaming(quick_results)
            
            yield {
                'type': 'call_graph_complete',
                'functions': len(call_graph),
                'edges': sum(len(calls) for calls in call_graph.values())
            }
        
        # Phase 4: Deep analysis for important files (selective CFG)
        if self.strategy.phase_3_deep_analysis and not self._cancelled:
            important_files = self.scanner.select_important_files(prioritized, quick_results)
            
            deep_processed = 0
            for priority in important_files[:50]:  # Limit to top 50
                if self._cancelled:
                    break
                
                result = self.scanner.deep_analyze_file(priority)
                if result:
                    deep_processed += 1
                    yield {
                        'type': 'deep_complete',
                        'file': priority.file_path,
                        'nodes': len(result.get('nodes', {})),
                        'progress': deep_processed / len(important_files)
                    }
        
        # Final summary
        yield {
            'type': 'complete',
            'total_files': total_files,
            'processed_files': processed,
            'elapsed_seconds': time.time() - start_time
        }
    
    def _estimate_eta(
        self,
        start_time: float,
        processed: int,
        total: int
    ) -> float:
        """Estimate remaining time."""
        if processed == 0:
            return 0.0
        
        elapsed = time.time() - start_time
        rate = processed / elapsed
        remaining = total - processed
        
        return remaining / rate if rate > 0 else 0.0
    
    def _report_progress(
        self,
        phase: str,
        current: int,
        total: int,
        message: str
    ) -> None:
        """Report progress via callback."""
        if self._progress_callback:
            self._progress_callback({
                'phase': phase,
                'current': current,
                'total': total,
                'percentage': (current / total * 100) if total > 0 else 0,
                'message': message
            })


# Re-export for backward compatibility
from .streaming import (
    ScanStrategy, STRATEGY_QUICK, STRATEGY_STANDARD, STRATEGY_DEEP,
    StreamingFileCache, SmartPrioritizer, FilePriority, IncrementalAnalyzer
)
