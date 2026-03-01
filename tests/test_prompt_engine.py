import pytest
from code2llm.refactor.prompt_engine import PromptEngine
from code2llm.core.models import AnalysisResult, CodeSmell, FunctionInfo

def test_tiktoken_truncation():
    result = AnalysisResult()
    # Create a dummy smell
    smell = CodeSmell(
        name="Test Smell",
        type="god_function",
        file="fake.py",
        line=1,
        severity=1.0,
        description="A very long description " * 100
    )
    result.smells = [smell]
    
    engine = PromptEngine(result)
    # Mock source context to be very large
    engine._get_source_context = lambda f, l: "print('Hello world')\n" * 1000
    
    prompts = engine.generate_prompts()
    assert len(prompts) == 1
    filename = list(prompts.keys())[0]
    prompt = prompts[filename]
    
    # Check if truncated
    if engine.encoding:
        assert "... (prompt truncated due to length) ..." in prompt
        tokens = engine.encoding.encode(prompt)
        assert len(tokens) <= 4000

def test_template_rendering_with_metrics():
    result = AnalysisResult()
    func_name = "complex_func"
    result.functions[func_name] = FunctionInfo(
        name=func_name,
        qualified_name=f"mod.{func_name}",
        file="mod.py",
        line=10,
        reachability="reachable"
    )
    result.functions[func_name].complexity = {"cyclomatic": 20, "rank": "F"}
    
    smell = CodeSmell(
        name=f"God Function: {func_name}",
        type="god_function",
        file="mod.py",
        line=10,
        severity=0.9,
        description="Function is too complex."
    )
    result.smells = [smell]
    result.metrics[func_name] = {
        "fan_in": 2, 
        "fan_out": 15,
        "complexity": {"cyclomatic": 20, "rank": "F"}
    }
    
    engine = PromptEngine(result)
    engine._get_source_context = lambda f, l: "def complex_func():\n    pass"
    
    prompts = engine.generate_prompts()
    prompt_content = list(prompts.values())[0]
    
    # Template renders metrics as raw dict keys via Jinja2 dictsort
    assert "complexity" in prompt_content
    assert "fan_out" in prompt_content
    assert "reachable" in prompt_content
    assert "Wyekstrahuj mniejsze, spójne metody" in prompt_content

def test_tree_sitter_init():
    result = AnalysisResult()
    engine = PromptEngine(result)
    # Check if parser is initialized (might be None if libs missing, but shouldn't crash)
    assert hasattr(engine, 'parser')
