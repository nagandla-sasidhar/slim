# Mentat — AI Coding Assistant

## CLAUDE.md

Mentat is a command-line AI coding assistant that can edit multiple files simultaneously. This file helps AI assistants working on Mentat itself.

## Project Structure

```
mentat/
  __init__.py
  agent_handler.py      Manages the agent loop
  code_context.py       Builds context from files
  code_editor.py        Applies changes to files
  conversation.py       Handles conversation history
  parsers/
    file_edit_parser.py   Parses file edits from LLM output
    streaming_printer.py  Handles streaming output
  session.py            Top-level session management
tests/
  benchmarks/           Mentat's self-evaluation benchmark
  conftest.py
  test_*.py
```

## Core Loop

```
User input
    ↓
Build context (relevant files, git diff, etc.)
    ↓
Send to LLM
    ↓
Stream + display response
    ↓
Parse file edits from response
    ↓
Show diff to user
    ↓
User approves/rejects
    ↓
Apply edits to disk
```

## File Edit Format

Mentat uses a custom format for file edits:

```
@ path/to/file.py
starting_line_number-ending_line_number
new content
line 2
@ end_of_edit
```

When the LLM creates a new file, `starting_line_number` is `0` and `ending_line_number` is `0`.

## Development

```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run
python -m mentat [files...]

# Test
pytest

# Benchmark
python -m tests.benchmarks.run_benchmark
```

## Configuration

User config is in `~/.mentat/config.yaml`. Project config can be in `.mentat.yaml` in the repo root. Project config overrides user config.

## Key Design Decisions

- File edits are streamed and displayed in real-time before being applied
- Users always approve or reject edits before they are written to disk
- Context is built per-conversation, not per-message — expensive but accurate
- The benchmark suite measures Mentat's ability to complete real-world tasks from GitHub issues
