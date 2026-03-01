"""Tests for ToonExporter v2 format."""
import pytest
from pathlib import Path
from code2llm.core.models import AnalysisResult, FunctionInfo, ClassInfo, ModuleInfo
from code2llm.exporters.toon import ToonExporter, EXCLUDE_PATTERNS


@pytest.fixture
def sample_result():
    """Create a sample AnalysisResult for testing."""
    result = AnalysisResult(project_path="/test/project")
    
    # Add modules
    result.modules["test_module"] = ModuleInfo(
        name="test_module",
        file="/test/project/test_module.py",
        imports=["os", "sys"],
        functions=["test_module.func1", "test_module.func2"],
        classes=["test_module.MyClass"],
    )
    
    # Add functions
    result.functions["test_module.func1"] = FunctionInfo(
        name="func1",
        qualified_name="test_module.func1",
        file="/test/project/test_module.py",
        line=10,
        module="test_module",
        args=["x", "y"],
        complexity={"cyclomatic_complexity": 5},
        calls=["test_module.func2"],
    )
    
    result.functions["test_module.func2"] = FunctionInfo(
        name="func2",
        qualified_name="test_module.func2",
        file="/test/project/test_module.py",
        line=20,
        module="test_module",
        args=["z"],
        complexity={"cyclomatic_complexity": 12},  # critical
        calls=[],
    )
    
    # Add class
    result.classes["test_module.MyClass"] = ClassInfo(
        name="MyClass",
        qualified_name="test_module.MyClass",
        file="/test/project/test_module.py",
        line=30,
        module="test_module",
        methods=["test_module.MyClass.method1"],
    )
    
    result.functions["test_module.MyClass.method1"] = FunctionInfo(
        name="method1",
        qualified_name="test_module.MyClass.method1",
        file="/test/project/test_module.py",
        line=35,
        module="test_module",
        class_name="MyClass",
        is_method=True,
        args=["self", "x"],
        complexity={"cyclomatic_complexity": 8},
        calls=[],
    )
    
    return result


class TestToonExporterV2:
    """Test ToonExporter v2 format."""
    
    def test_export_creates_file(self, sample_result, tmp_path):
        """Test that export creates output file."""
        exporter = ToonExporter()
        output_file = tmp_path / "test.toon"
        exporter.export(sample_result, str(output_file))
        
        assert output_file.exists()
        content = output_file.read_text()
        assert len(content) > 0
    
    def test_header_format(self, sample_result, tmp_path):
        """Test header contains key metrics."""
        exporter = ToonExporter()
        output_file = tmp_path / "test.toon"
        exporter.export(sample_result, str(output_file))
        
        content = output_file.read_text()
        lines = content.split("\n")
        
        # Check header
        assert lines[0].startswith("# code2llm |")
        assert "CC" in lines[1]
        assert "critical:" in lines[1]
    
    def test_health_section(self, sample_result, tmp_path):
        """Test HEALTH section is present."""
        exporter = ToonExporter()
        output_file = tmp_path / "test.toon"
        exporter.export(sample_result, str(output_file))
        
        content = output_file.read_text()
        assert "HEALTH[" in content
    
    def test_refactor_section(self, sample_result, tmp_path):
        """Test REFACTOR section is present."""
        exporter = ToonExporter()
        output_file = tmp_path / "test.toon"
        exporter.export(sample_result, str(output_file))
        
        content = output_file.read_text()
        assert "REFACTOR[" in content
    
    def test_layers_section(self, sample_result, tmp_path):
        """Test LAYERS section shows package structure."""
        exporter = ToonExporter()
        output_file = tmp_path / "test.toon"
        exporter.export(sample_result, str(output_file))
        
        content = output_file.read_text()
        assert "LAYERS:" in content
        assert "test_module" in content
    
    def test_functions_section_filters_by_cc(self, sample_result, tmp_path):
        """Test FUNCTIONS section only shows CC >= 10."""
        exporter = ToonExporter()
        output_file = tmp_path / "test.toon"
        exporter.export(sample_result, str(output_file))
        
        content = output_file.read_text()
        assert "FUNCTIONS (CC≥10" in content
        # func2 has CC=12, should be shown
        assert "func2" in content
    
    def test_classes_section_with_bar_chart(self, sample_result, tmp_path):
        """Test CLASSES section has visual bar chart."""
        exporter = ToonExporter()
        output_file = tmp_path / "test.toon"
        exporter.export(sample_result, str(output_file))
        
        content = output_file.read_text()
        assert "CLASSES:" in content
        assert "MyClass" in content
        # Check for bar chart character
        assert "█" in content
    
    def test_hotspots_section(self, sample_result, tmp_path):
        """Test HOTSPOTS section shows fan-out."""
        exporter = ToonExporter()
        output_file = tmp_path / "test.toon"
        exporter.export(sample_result, str(output_file))
        
        content = output_file.read_text()
        assert "HOTSPOTS:" in content
    
    def test_details_section(self, sample_result, tmp_path):
        """Test D: section shows module details."""
        exporter = ToonExporter()
        output_file = tmp_path / "test.toon"
        exporter.export(sample_result, str(output_file))
        
        content = output_file.read_text()
        assert "D:" in content
    
    def test_excluded_paths_venv(self):
        """Test that venv paths are excluded."""
        exporter = ToonExporter()
        
        assert exporter._is_excluded("/project/venv/lib/module.py") is True
        assert exporter._is_excluded("/project/.venv/lib/module.py") is True
        assert exporter._is_excluded("/project/publish-env/lib/module.py") is True
    
    def test_excluded_paths_site_packages(self):
        """Test that site-packages are excluded."""
        exporter = ToonExporter()
        
        assert exporter._is_excluded("/usr/lib/python3.10/site-packages/pkg/module.py") is True
    
    def test_included_paths(self):
        """Test that normal project paths are included."""
        exporter = ToonExporter()
        
        assert exporter._is_excluded("/project/code2llm/analyzer.py") is False
        assert exporter._is_excluded("/project/tests/test_analyzer.py") is False
    
    def test_max_health_issues_limit(self, sample_result, tmp_path):
        """Test that HEALTH section respects MAX_HEALTH_ISSUES limit."""
        from code2llm.exporters.toon import MAX_HEALTH_ISSUES
        
        # Add many high CC functions
        for i in range(100):
            result = sample_result
            result.functions[f"test_module.func_high_{i}"] = FunctionInfo(
                name=f"func_high_{i}",
                qualified_name=f"test_module.func_high_{i}",
                file="/test/project/test_module.py",
                line=100 + i,
                module="test_module",
                complexity={"cyclomatic_complexity": 20},  # high CC
                calls=[],
            )
        
        exporter = ToonExporter()
        output_file = tmp_path / "test.toon"
        exporter.export(result, str(output_file))
        
        content = output_file.read_text()
        # Count health issues (lines starting with severity markers)
        health_lines = [l for l in content.split("\n") if l.strip().startswith(("🔴", "🟡", "🟢"))]
        assert len(health_lines) <= MAX_HEALTH_ISSUES
    
    def test_coupling_matrix_limited(self, sample_result, tmp_path):
        """Test that COUPLING matrix is limited to top packages."""
        from code2llm.exporters.toon import MAX_COUPLING_PACKAGES
        
        exporter = ToonExporter()
        output_file = tmp_path / "test.toon"
        exporter.export(sample_result, str(output_file))
        
        content = output_file.read_text()
        # If coupling section exists, check it's not too wide
        if "COUPLING:" in content and "no cross-package" not in content:
            # Count package columns in header
            coupling_start = content.index("COUPLING:")
            coupling_section = content[coupling_start:coupling_start+2000]
            lines = coupling_section.split("\n")
            # Header line has package names
            if len(lines) > 1:
                header_cols = [c for c in lines[1].split() if c and not c.isspace()]
                assert len(header_cols) <= MAX_COUPLING_PACKAGES + 1  # +1 for row label column
    
    def test_inline_markers(self, sample_result, tmp_path):
        """Test inline markers (!! for high CC, ×DUP for duplicates)."""
        # Add a function with CC >= CC_WARNING (15) to trigger !! marker
        sample_result.functions["test_module.func_critical"] = FunctionInfo(
            name="func_critical",
            qualified_name="test_module.func_critical",
            file="/test/project/test_module.py",
            line=50,
            module="test_module",
            complexity={"cyclomatic_complexity": 20},  # >= CC_WARNING (15)
            calls=[],
        )
        
        exporter = ToonExporter()
        output_file = tmp_path / "test.toon"
        exporter.export(sample_result, str(output_file))
        
        content = output_file.read_text()
        # func_critical has CC=20 which is >= CC_WARNING (15), should have !! marker
        assert "!!" in content  # severity marker for high CC


class TestToonExporterEdgeCases:
    """Test edge cases for ToonExporter."""
    
    def test_empty_result(self, tmp_path):
        """Test export with empty AnalysisResult."""
        result = AnalysisResult(project_path="/empty")
        exporter = ToonExporter()
        output_file = tmp_path / "empty.toon"
        exporter.export(result, str(output_file))
        
        assert output_file.exists()
        content = output_file.read_text()
        assert "HEALTH[0]" in content or "HEALTH[0]:" in content
    
    def test_single_function(self, tmp_path):
        """Test export with single function."""
        result = AnalysisResult(project_path="/single")
        result.functions["main"] = FunctionInfo(
            name="main",
            qualified_name="main",
            file="/single/main.py",
            line=1,
            module="main",
            complexity={"cyclomatic_complexity": 1},
            calls=[],
        )
        result.modules["main"] = ModuleInfo(
            name="main",
            file="/single/main.py",
            functions=["main"],
        )
        
        exporter = ToonExporter()
        output_file = tmp_path / "single.toon"
        exporter.export(result, str(output_file))
        
        content = output_file.read_text()
        assert "main" in content
