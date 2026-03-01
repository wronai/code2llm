import pytest
import ast
from code2llm.core.analyzer import ProjectAnalyzer
from code2llm.core.config import Config
from code2llm.core.models import AnalysisResult

def test_radon_complexity():
    content = """
def simple_func(x):
    return x + 1

def complex_func(x):
    if x > 0:
        if x > 10:
            return x * 2
        else:
            return x + 1
    else:
        for i in range(10):
            print(i)
        return 0
"""
    from code2llm.core.analyzer import FileAnalyzer
    config = Config()
    config.verbose = True
    analyzer = FileAnalyzer(config)
    
    # We need to mock some parts to test _analyze_ast directly
    tree = ast.parse(content)
    result = analyzer._analyze_ast(tree, "test.py", "test_mod", content)
    
    simple = result['functions'].get("test_mod.simple_func")
    complex_f = result['functions'].get("test_mod.complex_func")
    
    assert simple is not None
    assert complex_f is not None
    
    assert simple.complexity['cyclomatic'] == 1
    assert complex_f.complexity['cyclomatic'] > 1
    assert complex_f.complexity['cyclomatic'] > simple.complexity['cyclomatic']

def test_graph_metrics():
    # Create a dummy AnalysisResult with a call graph
    result = AnalysisResult()
    
    # A -> B -> C
    # A -> D -> C
    # B is a bottleneck if A wants to reach C? 
    # Actually Betweenness Centrality on:
    # A -> B, B -> C, A -> D, D -> C
    
    from code2llm.core.models import FunctionInfo
    
    func_names = ["A", "B", "C", "D"]
    for name in func_names:
        result.functions[name] = FunctionInfo(name=name, qualified_name=name, file="test.py", line=1)
    
    result.functions["A"].calls = ["B", "D"]
    result.functions["B"].calls = ["C"]
    result.functions["D"].calls = ["C"]
    
    config = Config()
    analyzer = ProjectAnalyzer(config)
    analyzer._perform_refactoring_analysis(result)
    
    # Check centrality
    # B and D should have some centrality
    assert result.functions["B"].centrality > 0
    assert result.functions["D"].centrality > 0
    
    # Check for smells if any (threshold is 0.1, might be lower for this tiny graph)
    # Let's adjust threshold in test or check if it's set
    
def test_circular_dependency():
    result = AnalysisResult()
    from code2llm.core.models import FunctionInfo
    
    # A -> B -> A
    result.functions["A"] = FunctionInfo(name="A", qualified_name="A", file="test.py", line=1)
    result.functions["B"] = FunctionInfo(name="B", qualified_name="B", file="test.py", line=1)
    result.functions["A"].calls = ["B"]
    result.functions["B"].calls = ["A"]
    
    config = Config()
    analyzer = ProjectAnalyzer(config)
    analyzer._perform_refactoring_analysis(result)
    
    project_metrics = result.metrics.get("project", {})
    assert "circular_dependencies" in project_metrics
    cycles = project_metrics["circular_dependencies"]
    assert any("A" in cycle and "B" in cycle for cycle in cycles)
    
    # Check if smell is detected
    smells = [s for s in result.smells if s.type == "circular_dependency"]
    assert len(smells) > 0
