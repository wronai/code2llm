import pytest
import ast
from code2llm.core.config import Config
from code2llm.analysis.call_graph import CallGraphExtractor
from code2llm.analysis.dfg import DFGExtractor
from code2llm.analysis.smells import SmellDetector
from code2llm.refactor.prompt_engine import PromptEngine

def test_metrics_calculation():
    code = """
def a():
    b()
    c()
def b():
    pass
def c():
    b()
"""
    tree = ast.parse(code)
    config = Config()
    extractor = CallGraphExtractor(config)
    result = extractor.extract(tree, "test", "test.py")
    
    # Manual population of functions (since cg_extractor assumes they are in result.functions)
    # ProjectAnalyzer normally does this merge. For unit test, we simulate:
    from code2llm.core.models import FunctionInfo
    result.functions = {
        "test.a": FunctionInfo(name="a", qualified_name="test.a", file="test.py", line=2, calls=["test.b", "test.c"]),
        "test.b": FunctionInfo(name="b", qualified_name="test.b", file="test.py", line=5, calls=[]),
        "test.c": FunctionInfo(name="c", qualified_name="test.c", file="test.py", line=7, calls=["test.b"]),
    }
    
    extractor._calculate_metrics()
    
    assert result.metrics["test.b"]["fan_in"] == 2 # Called by a and c
    assert result.metrics["test.a"]["fan_out"] == 2 # Calls b and c

def test_mutation_tracking():
    code = """
def update_data(obj):
    obj.value = 10
    obj.list.append(5)
    x = 1
    x += 1
"""
    tree = ast.parse(code)
    config = Config()
    extractor = DFGExtractor(config)
    result = extractor.extract(tree, "test", "test.py")
    
    mutations = result.mutations
    types = [m.type for m in mutations]
    assert "assign" in types
    assert "aug_assign" in types
    assert "method_call" in types # .append()

def test_smell_detection():
    from code2llm.core.models import AnalysisResult, FunctionInfo, Mutation
    result = AnalysisResult(project_path=".", analysis_mode="static")
    result.functions = {
        "test.god_func": FunctionInfo(name="god_func", qualified_name="test.god_func", file="test.py", line=10)
    }
    result.metrics = {
        "test.god_func": {"fan_out": 10, "fan_in": 1}
    }
    
    detector = SmellDetector(result)
    smells = detector.detect()
    
    assert any(s.type == "god_function" for s in smells)

if __name__ == "__main__":
    pytest.main([__file__])
