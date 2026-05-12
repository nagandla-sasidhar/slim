# Pydantic AI — Agent Framework

## AGENT.md for PydanticAI Repository

PydanticAI is a Python agent framework built on Pydantic. This file helps AI assistants contribute to the framework.

## Core Concepts

**Agent** — the central object. Holds a model, system prompt, and tools. Calling `agent.run()` executes the agent loop.

**Tool** — a Python function decorated with `@agent.tool` or `@agent.tool_plain`. The function signature defines the tool's parameter schema automatically using Pydantic.

**Result** — agents return `RunResult[T]` where `T` is the structured output type (a Pydantic model or primitive).

**Deps** — dependency injection via `RunContext[DepsType]`. Tools receive context through the first parameter.

## Type System

PydanticAI uses Pydantic v2 for all schema validation. Tool parameters are derived from function signatures. Return types are validated against the agent's `result_type`.

```python
from pydantic import BaseModel
from pydantic_ai import Agent

class Weather(BaseModel):
    temperature: float
    condition: str
    city: str

agent = Agent("openai:gpt-4o", result_type=Weather)

@agent.tool_plain
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return fetch_from_api(city)
```

## Repository Layout

```
pydantic_ai_slim/   Core package (no optional deps)
  pydantic_ai/
    agent.py        Agent class
    models/         LLM provider implementations
    tools.py        Tool registration and execution
    result.py       RunResult and streaming types
pydantic_ai/        Metapackage with all extras
tests/
  test_agent.py
  test_tools.py
  models/           Per-provider tests
docs/               MkDocs documentation source
```

## Development Setup

```bash
uv sync --all-extras --dev
pytest
```

Run tests for a specific provider:
```bash
pytest tests/models/test_openai.py
```

## Adding a New Model Provider

1. Create `pydantic_ai_slim/pydantic_ai/models/my_provider.py`
2. Implement the `Model` abstract class
3. Implement streaming: `StreamTextResponse` and `StreamStructuredResponse`
4. Add the provider to `pydantic_ai_slim/pydantic_ai/models/__init__.py`
5. Add tests in `tests/models/test_my_provider.py`
6. Add documentation in `docs/models/my-provider.md`

## Testing

Use `TestModel` for unit tests — it doesn't make real LLM calls:

```python
from pydantic_ai.models.test import TestModel

def test_agent():
    agent = Agent(TestModel())
    result = agent.run_sync("hello")
    assert result.data == "success"
```

Use `pytest-recording` with VCR cassettes for integration tests.
