# Copilot Instructions — Aider

Aider is AI pair programming in your terminal. You can use aider to start a new project or work with an existing git repo.

## For Copilot: Working in the aider repo

### Language

Python 3.10+. Type hints on all public APIs. Docstrings for public classes and methods.

### Testing

```bash
python -m pytest tests/
python -m pytest tests/basic/test_coder.py  # single file
```

### Architecture

Aider's `Coder` class is the central abstraction. Different edit formats are different `Coder` subclasses:

| Class | Module | Format |
|-------|--------|--------|
| `EditBlockCoder` | `coders/editblock_coder.py` | SEARCH/REPLACE blocks |
| `WholeFileCoder` | `coders/wholefile_coder.py` | Full file contents |
| `UnifiedDiffCoder` | `coders/udiff_coder.py` | Unified diff format |
| `ArchitectCoder` | `coders/architect_coder.py` | Two-pass planning |

### LLM providers

Aider uses LiteLLM to abstract LLM providers. Model-specific behavior (context window size, edit format to use) is in `aider/models.py`.

### Repo map

`RepoMap` in `aider/repomap.py` builds a compact representation of the codebase using tree-sitter. It's used to give the LLM context about the project structure.

### What to avoid

- Do not modify the benchmark scripts in `benchmark/` — these are used for measuring regression
- Do not change the SEARCH/REPLACE format in `EditBlockCoder` — it's versioned behavior
- When fixing bugs, add a regression test

### Commit messages

Aider uses its own commit message format internally. For contributions from humans (or Copilot), use Conventional Commits.
