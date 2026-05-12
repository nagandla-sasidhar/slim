# Aider — AI Pair Programming in Your Terminal

## CLAUDE.md

This file is for AI assistants contributing to the aider codebase itself.

## What is aider?

Aider lets you pair program with LLMs in your terminal. You can work with code in your local git repo. Aider makes it easy to share relevant context with the LLM and apply the changes it suggests back to your codebase.

## Codebase Overview

```
aider/
  coders/         Different edit formats (diff, whole-file, udiff, etc.)
  models/         LLM provider integrations
  io.py           Terminal I/O, input handling, syntax highlighting
  repo.py         Git repo interaction
  commands.py     Slash command implementations
  linter.py       Per-language linting integration
tests/
  basic/          Unit tests
  browser/        Browser-mode tests
benchmark/        Aider self-improvement benchmark
```

## Development

```bash
# Install dev mode
pip install -e ".[dev]"

# Run tests
python -m pytest tests/

# Run a single test
python -m pytest tests/basic/test_coder.py::TestCoder::test_get_files_content

# Run the benchmark
python -m benchmark.benchmark
```

## Coding Conventions

- Python 3.10+ features are fine — f-strings, match statements, type hints
- Use `self.io.tool_output()` for output, not `print()`
- Errors go to `self.io.tool_error()`
- New slash commands go in `aider/commands.py` following the existing `cmd_*` pattern
- New coder edit formats inherit from `Coder` in `aider/coders/base_coder.py`

## Testing Philosophy

Write tests that test behavior, not implementation. Use `tempfile.TemporaryDirectory` for tests that need a real filesystem. Mock the LLM with recorded responses in `tests/fixtures/`.

## Commit Style

aider uses Conventional Commits. Use `feat:`, `fix:`, `refactor:`, `test:`, `docs:`.

aider's benchmark script measures performance on coding tasks. When making changes to edit formats or model handling, run the benchmark before and after.
