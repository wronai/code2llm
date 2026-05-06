#!/usr/bin/env python3
"""
Streaming Analyzer Demo

This script demonstrates how to use the streaming analyzer with different strategies
and configurations for real-time code analysis.
"""

import sys
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from code2llm.core.streaming_analyzer import (
    StreamingAnalyzer, 
    STRATEGY_QUICK, 
    STRATEGY_STANDARD, 
    STRATEGY_DEEP,
    StreamingIncrementalAnalyzer
)


def demo_quick_strategy():
    """Demonstrate quick strategy analysis."""
    print("\n🚀 Quick Strategy Demo")
    print("=" * 50)
    
    analyzer = StreamingAnalyzer(strategy=STRATEGY_QUICK)
    
    def progress_callback(update):
        percentage = update.get('percentage', 0)
        message = update.get('message', '')
        print(f"\r[{percentage:.0f}%] {message}", end='', flush=True)
    
    analyzer.set_progress_callback(progress_callback)
    
    start_time = time.time()
    results = list(analyzer.analyze_streaming("sample_project"))
    elapsed = time.time() - start_time
    
    print(f"\n✅ Quick analysis completed in {elapsed:.2f}s")
    
    # Show final result
    final = results[-1]
    if final['type'] == 'complete':
        print(f"   Files processed: {final['processed_files']}")
        print(f"   Total files: {final['total_files']}")


def demo_standard_strategy():
    """Demonstrate standard strategy analysis."""
    print("\n⚖️ Standard Strategy Demo")
    print("=" * 50)
    
    analyzer = StreamingAnalyzer(strategy=STRATEGY_STANDARD)
    
    file_count = 0
    function_count = 0
    class_count = 0
    
    for update in analyzer.analyze_streaming("sample_project"):
        if update['type'] == 'file_complete':
            file_count += 1
            function_count += update['functions']
            class_count += update['classes']
            print(f"📄 {Path(update['file']).name}: "
                  f"{update['functions']} functions, {update['classes']} classes")
        
        elif update['type'] == 'call_graph_complete':
            print(f"🔗 Call graph built: {update['functions']} functions, "
                  f"{update['edges']} edges")
        
        elif update['type'] == 'complete':
            print(f"✅ Standard analysis completed in {update['elapsed_seconds']:.2f}s")
            print(f"   Total: {file_count} files, {function_count} functions, {class_count} classes")


def demo_deep_strategy():
    """Demonstrate deep strategy analysis."""
    print("\n🔬 Deep Strategy Demo")
    print("=" * 50)
    
    analyzer = StreamingAnalyzer(strategy=STRATEGY_DEEP)
    
    node_count = 0
    deep_files = 0
    
    for update in analyzer.analyze_streaming("sample_project"):
        if update['type'] == 'file_complete':
            print(f"📄 Scanned: {Path(update['file']).name}")
        
        elif update['type'] == 'deep_complete':
            deep_files += 1
            node_count += update['nodes']
            print(f"🔍 Deep analysis: {Path(update['file']).name} "
                  f"({update['nodes']} CFG nodes)")
        
        elif update['type'] == 'complete':
            print(f"✅ Deep analysis completed in {update['elapsed_seconds']:.2f}s")
            print(f"   Deep files: {deep_files}, Total CFG nodes: {node_count}")


def demo_incremental_analysis():
    """Demonstrate incremental analysis."""
    print("\n🔄 Incremental Analysis Demo")
    print("=" * 50)
    
    incremental = StreamingIncrementalAnalyzer()
    
    # First run - all files are "changed"
    print("🔍 First analysis run...")
    changed, unchanged = incremental.get_changed_files("sample_project")
    
    print(f"   Changed files: {len(changed)}")
    print(f"   Unchanged files: {len(unchanged)}")
    
    if changed:
        analyzer = StreamingAnalyzer(strategy=STRATEGY_QUICK)
        for update in analyzer.analyze_streaming("sample_project"):
            if update['type'] == 'complete':
                print(f"   Completed in {update['elapsed_seconds']:.2f}s")
                break
    
    # Second run - should detect no changes
    print("\n🔍 Second analysis run (no changes)...")
    changed, unchanged = incremental.get_changed_files("sample_project")
    
    print(f"   Changed files: {len(changed)}")
    print(f"   Unchanged files: {len(unchanged)}")
    
    if not changed:
        print("   ✅ No changes detected - analysis skipped!")


def demo_memory_limited():
    """Demonstrate memory-limited analysis."""
    print("\n💾 Memory-Limited Analysis Demo")
    print("=" * 50)
    
    from code2llm.core.streaming_analyzer import ScanStrategy
    
    # Create memory-constrained strategy
    limited_strategy = ScanStrategy(
        name="memory_limited",
        description="Low memory analysis",
        phase_1_quick_scan=True,
        phase_2_call_graph=False,  # Skip call graph to save memory
        phase_3_deep_analysis=False,  # Skip deep analysis
        max_files_in_memory=2,  # Very low memory limit
        skip_private_functions=True,
    )
    
    analyzer = StreamingAnalyzer(strategy=limited_strategy)
    
    for update in analyzer.analyze_streaming("sample_project"):
        if update['type'] == 'file_complete':
            print(f"📄 {Path(update['file']).name} (low memory mode)")
        
        elif update['type'] == 'complete':
            print(f"✅ Memory-limited analysis completed in {update['elapsed_seconds']:.2f}s")
            break


def demo_custom_progress():
    """Demonstrate custom progress tracking."""
    print("\n📊 Custom Progress Tracking Demo")
    print("=" * 50)
    
    analyzer = StreamingAnalyzer(strategy=STRATEGY_STANDARD)
    
    # Custom progress tracker
    class ProgressTracker:
        def __init__(self):
            self.start_time = time.time()
            self.files_processed = 0
            self.total_functions = 0
        
        def __call__(self, update):
            phase = update.get('phase', '')
            current = update.get('current', 0)
            total = update.get('total', 0)
            message = update.get('message', '')
            
            if phase == "quick_scan":
                self.files_processed = current
                elapsed = time.time() - self.start_time
                rate = self.files_processed / elapsed if elapsed > 0 else 0
                eta = (total - current) / rate if rate > 0 else 0
                
                print(f"\r🔄 Scanning: {current}/{total} files "
                      f"({rate:.1f} files/s, ETA: {eta:.1f}s)", end='', flush=True)
            
            elif phase == "collect":
                print(f"\n📁 Found {total} files to analyze")
    
    tracker = ProgressTracker()
    analyzer.set_progress_callback(tracker)
    
    for update in analyzer.analyze_streaming("sample_project"):
        if update['type'] == 'complete':
            elapsed = time.time() - tracker.start_time
            print(f"\n✅ Completed in {elapsed:.2f}s "
                  f"({tracker.files_processed} files)")
            break


def main():
    """Run all demos."""
    print("🎯 Streaming Analyzer Demo Suite")
    print("=" * 60)
    print("This demo showcases different streaming analyzer strategies")
    print("and configurations for real-time Python code analysis.\n")
    
    # Change to the demo directory
    demo_dir = Path(__file__).parent
    import os
    os.chdir(demo_dir)
    
    # Run all demos
    demos = [
        demo_quick_strategy,
        demo_standard_strategy,
        demo_deep_strategy,
        demo_incremental_analysis,
        demo_memory_limited,
        demo_custom_progress,
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"❌ Demo failed: {e}")
        
        print("\n" + "-" * 50)
    
    print("\n🎉 All demos completed!")
    print("\nNext steps:")
    print("1. Try the CLI commands:")
    print("   code2llm examples/streaming-analyzer/sample_project --strategy quick")
    print("   code2llm examples/streaming-analyzer/sample_project --strategy standard -v")
    print("   code2llm examples/streaming-analyzer/sample_project --strategy deep")
    print("\n2. Check the output files in code2llm_output/")
    print("3. Read the full README.md for more examples")


if __name__ == "__main__":
    main()
