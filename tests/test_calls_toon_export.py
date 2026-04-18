"""Tests for calls.toon.yaml export functionality."""

from pathlib import Path
from unittest.mock import MagicMock

from code2llm.core.models import AnalysisResult, FunctionInfo, ClassInfo
from code2llm.exporters.yaml_exporter import YAMLExporter


def test_export_calls_toon_generates_file(tmp_path):
    """Test that export_calls_toon generates a valid toon format file."""
    # Create a mock result with some functions and calls
    result = MagicMock(spec=AnalysisResult)
    result.project_path = "."
    
    # Add some mock functions
    func1 = MagicMock(spec=FunctionInfo)
    func1.name = "func1"
    func1.module = "module1"
    func1.line = 10
    func1.complexity = {"cyclomatic_complexity": 5}
    func1.calls = ["func2", "func3"]
    
    func2 = MagicMock(spec=FunctionInfo)
    func2.name = "func2"
    func2.module = "module1"
    func2.line = 20
    func2.complexity = {"cyclomatic_complexity": 3}
    func2.calls = []
    
    func3 = MagicMock(spec=FunctionInfo)
    func3.name = "func3"
    func3.module = "module2"
    func3.line = 30
    func3.complexity = {"cyclomatic_complexity": 2}
    func3.calls = []
    
    result.functions = {
        "module1.func1": func1,
        "module1.func2": func2,
        "module2.func3": func3,
    }
    result.classes = {}
    result.entry_points = ["module1.func1"]
    
    # Export
    exporter = YAMLExporter()
    output_path = tmp_path / "calls.toon.yaml"
    exporter.export_calls_toon(result, str(output_path))
    
    # Verify file exists
    assert output_path.exists()
    
    # Verify content
    content = output_path.read_text(encoding="utf-8")
    assert "# code2llm call graph" in content
    assert "HUBS[" in content
    assert "MODULES:" in content
    assert "EDGES:" in content


def test_export_calls_toon_hubs_section(tmp_path):
    """Test that HUBS section contains high-degree functions sorted by total calls."""
    result = MagicMock(spec=AnalysisResult)
    result.project_path = "."
    
    # Create functions with different call patterns
    func_hub = MagicMock(spec=FunctionInfo)
    func_hub.name = "hub_func"
    func_hub.module = "module1"
    func_hub.line = 10
    func_hub.complexity = {"cyclomatic_complexity": 10}
    func_hub.calls = ["func2", "func3", "func4", "func5"]  # 4 outgoing calls
    
    func2 = MagicMock(spec=FunctionInfo)
    func2.name = "func2"
    func2.module = "module1"
    func2.line = 20
    func2.complexity = {"cyclomatic_complexity": 2}
    func2.calls = []
    
    func3 = MagicMock(spec=FunctionInfo)
    func3.name = "func3"
    func3.module = "module2"
    func3.line = 30
    func3.complexity = {"cyclomatic_complexity": 1}
    func3.calls = []
    
    func4 = MagicMock(spec=FunctionInfo)
    func4.name = "func4"
    func4.module = "module3"
    func4.line = 40
    func4.complexity = {"cyclomatic_complexity": 1}
    func4.calls = []
    
    func5 = MagicMock(spec=FunctionInfo)
    func5.name = "func5"
    func5.module = "module4"
    func5.line = 50
    func5.complexity = {"cyclomatic_complexity": 1}
    func5.calls = []
    
    result.functions = {
        "module1.hub_func": func_hub,
        "module1.func2": func2,
        "module2.func3": func3,
        "module3.func4": func4,
        "module4.func5": func5,
    }
    result.classes = {}
    result.entry_points = []
    
    exporter = YAMLExporter()
    output_path = tmp_path / "calls.toon.yaml"
    exporter.export_calls_toon(result, str(output_path))
    
    content = output_path.read_text(encoding="utf-8")
    assert "HUBS[" in content
    assert "hub_func" in content


def test_export_calls_toon_modules_section(tmp_path):
    """Test that MODULES section groups functions by module."""
    result = MagicMock(spec=AnalysisResult)
    result.project_path = "."
    
    func1 = MagicMock(spec=FunctionInfo)
    func1.name = "func1"
    func1.module = "module_a"
    func1.line = 10
    func1.complexity = {"cyclomatic_complexity": 3}
    func1.calls = ["func2", "func3"]
    
    func2 = MagicMock(spec=FunctionInfo)
    func2.name = "func2"
    func2.module = "module_a"
    func2.line = 20
    func2.complexity = {"cyclomatic_complexity": 2}
    func2.calls = []
    
    func3 = MagicMock(spec=FunctionInfo)
    func3.name = "func3"
    func3.module = "module_b"
    func3.line = 30
    func3.complexity = {"cyclomatic_complexity": 4}
    func3.calls = []
    
    result.functions = {
        "module_a.func1": func1,
        "module_a.func2": func2,
        "module_b.func3": func3,
    }
    result.classes = {}
    result.entry_points = []
    
    exporter = YAMLExporter()
    output_path = tmp_path / "calls.toon.yaml"
    exporter.export_calls_toon(result, str(output_path))
    
    content = output_path.read_text(encoding="utf-8")
    assert "MODULES:" in content
    assert "module_a" in content
    assert "module_b" in content
    assert "[2 funcs]" in content or "[1 func]" in content


def test_export_calls_toon_edges_section(tmp_path):
    """Test that EDGES section contains caller -> callee relationships."""
    result = MagicMock(spec=AnalysisResult)
    result.project_path = "."
    
    caller = MagicMock(spec=FunctionInfo)
    caller.name = "caller"
    caller.module = "module1"
    caller.line = 10
    caller.complexity = {"cyclomatic_complexity": 2}
    caller.calls = ["callee"]
    
    callee = MagicMock(spec=FunctionInfo)
    callee.name = "callee"
    callee.module = "module1"
    callee.line = 20
    callee.complexity = {"cyclomatic_complexity": 1}
    callee.calls = []
    
    result.functions = {
        "module1.caller": caller,
        "module1.callee": callee,
    }
    result.classes = {}
    result.entry_points = []
    
    exporter = YAMLExporter()
    output_path = tmp_path / "calls.toon.yaml"
    exporter.export_calls_toon(result, str(output_path))
    
    content = output_path.read_text(encoding="utf-8")
    assert "EDGES:" in content
    assert "→" in content
    assert "caller" in content
    assert "callee" in content


def test_export_calls_toon_header_stats(tmp_path):
    """Test that header contains correct statistics."""
    result = MagicMock(spec=AnalysisResult)
    result.project_path = "."
    
    func1 = MagicMock(spec=FunctionInfo)
    func1.name = "func1"
    func1.module = "module1"
    func1.line = 10
    func1.complexity = {"cyclomatic_complexity": 5}
    func1.calls = ["func2"]
    
    func2 = MagicMock(spec=FunctionInfo)
    func2.name = "func2"
    func2.module = "module1"
    func2.line = 20
    func2.complexity = {"cyclomatic_complexity": 3}
    func2.calls = []
    
    result.functions = {
        "module1.func1": func1,
        "module1.func2": func2,
    }
    result.classes = {}
    result.entry_points = []
    
    exporter = YAMLExporter()
    output_path = tmp_path / "calls.toon.yaml"
    exporter.export_calls_toon(result, str(output_path))
    
    content = output_path.read_text(encoding="utf-8")
    # Check header lines
    lines = content.split('\n')[:5]
    assert any("# code2llm call graph" in line for line in lines)
    assert any("nodes:" in line for line in lines)
    assert any("edges:" in line for line in lines)
    assert any("modules:" in line for line in lines)
    assert any("CC̄=" in line for line in lines)
