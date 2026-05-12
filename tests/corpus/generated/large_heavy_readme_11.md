---
title: "Nexus Agent SDK"
description: "Multi-modal AI agent framework for production workflows"
version: "3.1.0"
badges:
  - ci: passing
  - coverage: 89%
  - license: MIT
---

# Nexus Agent SDK

[![CI](https://img.shields.io/github/actions/workflow/status/acme/nexus-agent/ci.yml?branch=main)](https://github.com/acme/nexus-agent/actions)
[![Coverage](https://img.shields.io/codecov/c/github/acme/nexus-agent)](https://codecov.io/gh/acme/nexus-agent)
[![PyPI](https://img.shields.io/pypi/v/nexus-agent)](https://pypi.org/project/nexus-agent/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Nexus Agent SDK** is an open-source framework for building *production-grade* AI agents with **tool use**, **memory**, and **multi-step reasoning**. It wraps [OpenAI](https://platform.openai.com/docs/api-reference), [Anthropic](https://docs.anthropic.com/), and [Gemini](https://ai.google.dev/docs) behind a unified interface.

---

## Installation

```bash
pip install nexus-agent
# or with extras
pip install "nexus-agent[redis,postgres,opentelemetry]"
```

## Quick Start

```python
from nexus_agent import Agent, tool

@tool
def get_weather(city: str) -> dict:
    """Return current weather for a city."""
    # highlight-next-line
    return weather_api.fetch(city)

agent = Agent(
    name="WeatherBot",
    model="claude-3-7-sonnet",
    tools=[get_weather],
    system="You are a helpful weather assistant.",
)

response = agent.run("What's the weather in Tokyo?")
print(response.text)
```

---

## Core Concepts

### Agents

An `Agent` is the top-level orchestrator. It holds:

- A **model** (LLM backend)
- A list of **tools** (callable functions)
- A **memory** store (optional)
- A **system prompt**

### Tools

Tools are Python functions decorated with `@tool`. The decorator extracts the **docstring** as the tool description and the **type hints** as the parameter schema.

| Decorator Option | Type | Default | Description |
|-----------------|------|---------|-------------|
| `name` | `str` | function name | Override tool name shown to model |
| `description` | `str` | docstring | Override tool description |
| `schema` | `dict` | inferred | Override JSON schema for params |
| `timeout` | `int` | `30` | Max seconds before tool is cancelled |

### Memory

Nexus supports three memory backends:

1. **InMemory** — ephemeral, session-scoped, zero config
2. **Redis** — persistent, fast, requires `redis` extra
3. **Postgres** — persistent, queryable, requires `postgres` extra

```python
from nexus_agent.memory import RedisMemory

agent = Agent(
    name="CustomerSupport",
    model="gpt-4o",
    memory=RedisMemory(url="redis://localhost:6379", ttl=3600),
)
```

---

## Configuration Reference

### Agent Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | `str` | yes | Display name for the agent |
| `model` | `str` | yes | Model ID, e.g. `"claude-3-7-sonnet"` |
| `tools` | `list[Tool]` | no | List of tool instances |
| `memory` | `Memory` | no | Memory backend instance |
| `system` | `str` | no | System prompt |
| `max_turns` | `int` | no | Max agentic loop iterations (default `10`) |
| `temperature` | `float` | no | Sampling temperature (default `0.0`) |

### Environment Variables

| Variable | Description |
|----------|-------------|
| `NEXUS_MODEL_PROVIDER` | Default provider: `openai`, `anthropic`, `google` |
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `GOOGLE_API_KEY` | Google AI API key |
| `NEXUS_LOG_LEVEL` | Log verbosity: `DEBUG`, `INFO`, `WARN`, `ERROR` |

---

## Advanced Usage

### Parallel Tool Calls

```python
agent = Agent(
    ...,
    parallel_tool_calls=True,  # default True for supported models
)
```

When **`parallel_tool_calls=True`**, the agent may invoke multiple tools in a single turn. Results are merged before the next LLM call.

### Streaming

```python
for chunk in agent.stream("Summarize the last 10 issues"):
    print(chunk.text, end="", flush=True)
```

### Human-in-the-Loop

```python
from nexus_agent.hooks import before_tool_call

@before_tool_call("terraform_apply")
def confirm_apply(call):
    answer = input(f"Apply {call.args}? [y/N] ")
    if answer.lower() != "y":
        raise ToolAborted("User declined")
```

---

## Observability

Nexus integrates with [OpenTelemetry](https://opentelemetry.io/docs/). Install the extra and configure your exporter:

```bash
pip install "nexus-agent[opentelemetry]"
```

```python
from nexus_agent.telemetry import configure_otel
configure_otel(endpoint="http://otel-collector:4317")
```

Spans are emitted for:
- Each `agent.run()` call
- Each **tool invocation** (with input/output as span attributes)
- Each **LLM call** (with token counts)

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). Run the test suite with:

```bash
make test
make lint
```

<details>
<summary>Running integration tests</summary>

Integration tests require Docker Compose:

```bash
docker compose -f tests/docker-compose.yml up -d
pytest tests/integration/
docker compose -f tests/docker-compose.yml down
```

</details>

---

## License

MIT — see [LICENSE](./LICENSE).
