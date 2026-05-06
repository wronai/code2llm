import pytest
import os
from pathlib import Path
from code2llm.core.analyzer import ProjectAnalyzer, FileAnalyzer
from code2llm.core.config import Config
from code2llm.core.models import AnalysisResult

def test_astroid_resolution_mock(tmp_path):
    # Create two files. A.py calls B.func() via an instance.
    b_py = tmp_path / "B.py"
    b_py.write_text("""
class B:
    def target_method(self):
        return 42
""")
    
    a_py = tmp_path / "A.py"
    a_py.write_text("""
from B import B
def caller_func():
    obj = B()
    obj.target_method()
""")
    
    config = Config()
    config.filters.exclude_tests = False
    config.filters.exclude_patterns = []
    analyzer = ProjectAnalyzer(config)
    
    # Analyze project
    # Note: We need to make sure the tmp_path is in sys.path for astroid to find B
    import sys
    sys.path.append(str(tmp_path))
    
    try:
        result = analyzer.analyze_project(str(tmp_path))
        print(f"DEBUG: Found files: {[os.path.basename(f) for f, _ in analyzer._collect_files(tmp_path)]}")
        print(f"DEBUG: Result functions: {list(result.functions.keys())}")
        
        # Look for caller_func regardless of exact module prefix
        func_a_name = next((k for k in result.functions if "caller_func" in k), None)
        assert func_a_name is not None, f"caller_func not found. Available: {list(result.functions.keys())}"
        func_a = result.functions[func_a_name]
        
        # Check if target_method is in calls
        print(f"DEBUG: Calls from {func_a_name}: {func_a.calls}")
        assert any("target_method" in c for c in func_a.calls)
    finally:
        sys.path.remove(str(tmp_path))

def test_vulture_dead_code(tmp_path):
    import os
    p = tmp_path / "app.py"
    p.write_text("""
def used_func():
    return 1

def unused_func():
    return 2

used_func()
""")
    
    config = Config()
    config.verbose = True
    config.filters.exclude_tests = False
    config.filters.exclude_patterns = []
    config.performance.skip_dead_code_detection = False
    analyzer = ProjectAnalyzer(config)
    result = analyzer.analyze_project(str(tmp_path))
    print(f"DEBUG: Dead code test functions: {list(result.functions.keys())}")
    
    unused_key = next((k for k in result.functions if "unused_func" in k), None)
    used_key = next((k for k in result.functions if "used_func" in k), None)
    
    assert unused_key is not None
    assert used_key is not None
    assert result.functions[unused_key].reachability == "unreachable"
    assert result.functions[used_key].reachability == "reachable"
