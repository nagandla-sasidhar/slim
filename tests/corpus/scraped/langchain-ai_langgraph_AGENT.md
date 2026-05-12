# LangGraph ReAct Agent

This directory contains a ReAct (Reasoning + Acting) agent built with LangGraph.

## Architecture

The agent uses a cyclic graph with two nodes:

```
[START] → agent → tools → agent → [END]
                    ↑         ↓
                    └─────────┘
                  (loop until no tool call)
```

The `agent` node calls the LLM. If the LLM returns tool calls, the graph routes to the `tools` node. The `tools` node executes all tool calls in parallel and returns results. The loop continues until the LLM returns a final answer with no tool calls.

## State

The agent state is a `TypedDict` with a single `messages` key that uses the `add_messages` reducer:

```python
from typing import Annotated
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
```

## Tools

Tools are standard LangChain tools decorated with `@tool`. The agent is initialized with a bound model:

```python
model_with_tools = model.bind_tools(tools)
```

## Checkpointing

The graph uses a `MemorySaver` for in-memory checkpointing during development. For production, replace with `AsyncPostgresSaver` or `AsyncSqliteSaver`:

```python
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

async with AsyncPostgresSaver.from_conn_string(DB_URL) as checkpointer:
    graph = workflow.compile(checkpointer=checkpointer)
```

## Streaming

Use `astream_events` for fine-grained streaming:

```python
async for event in graph.astream_events(input, version="v2"):
    if event["event"] == "on_chat_model_stream":
        print(event["data"]["chunk"].content, end="")
```

## Human-in-the-loop

Add `interrupt_before=["tools"]` to the compile call to pause before every tool execution and allow a human to review and approve.

## Running

```bash
pip install -e .
python agent.py
```

Set `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` to enable LangSmith tracing.
