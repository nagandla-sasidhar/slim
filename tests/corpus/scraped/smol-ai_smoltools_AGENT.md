# SmolAgent — Minimal AI Agent

## Agent Configuration

This is a minimal AI agent designed to be easily hackable and extensible.

## Philosophy

Small is better. This agent does one thing well: it takes a task, breaks it into steps, executes the steps, and returns the result. No fancy orchestration. No complicated state machines.

## Tools

The agent has access to exactly three tools by default:

**run_bash(command: str) -> str**
Run a bash command and return stdout + stderr. Timeout: 30s.

**read_file(path: str) -> str**
Read a file from the working directory. Returns the file contents.

**write_file(path: str, content: str) -> bool**
Write content to a file. Creates intermediate directories. Returns true on success.

Additional tools can be registered with `agent.add_tool(func)`. The function's docstring becomes the tool description.

## Task Protocol

Given a task:
1. Think about what steps are needed
2. Execute steps one at a time
3. After each step, verify the result
4. If a step fails, try an alternative approach (max 3 retries)
5. If all retries fail, return what was accomplished and what failed

## Stopping Conditions

The agent stops when:
- The task is complete (self-assessed)
- The maximum number of steps is reached (default: 20)
- An unrecoverable error occurs
- The user sends a stop signal

## Memory

The agent has no persistent memory. Each run starts fresh. To add memory, pass a `context` string when creating the task.

## Example Usage

```python
from smol_agent import Agent

agent = Agent(model="gpt-4o-mini")
result = agent.run("Write a Python function to parse CSV and return a list of dicts")
print(result)
```
