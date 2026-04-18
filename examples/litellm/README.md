# code2llm + LiteLLM

Python automation: analyze code with `code2llm`, then use **LiteLLM** to get refactoring advice from any LLM provider.

## Prerequisites

```bash
pip install code2llm litellm
```

Set your API key:
```bash
export OPENAI_API_KEY="sk-..."
# or
export ANTHROPIC_API_KEY="sk-ant-..."
# Analyze + get AI advice in one command
python examples/litellm/run.py /path/to/project
```

## Files

| File | Description |
|------|-------------|
| `run.py` | Main script — analyze + LLM advice |
| `README.md` | This file |

## How It Works

1. **Analyze**: Runs `code2llm` to generate `evolution.toon` + `context.md`
2. **Read**: Parses the analysis outputs
3. **Ask LLM**: Sends analysis to LiteLLM for refactoring recommendations
4. **Report**: Prints structured advice with before/after prediction
