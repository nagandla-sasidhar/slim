# GPT Engineer — AI Software Project Generator

## Agent Instructions

GPT Engineer generates entire codebases from a prompt. This AGENT.md defines how the agent operates in clarification and generation mode.

## Modes

### Clarify Mode

Before generating any code, the agent asks clarifying questions to fully understand the requirements.

Rules for clarification:
- Ask at most 5 questions
- Ask the most impactful questions first
- Questions should resolve genuine ambiguity — not confirm obvious things
- If the prompt is already unambiguous, skip clarification and proceed

### Generate Mode

The agent generates the full project structure:

1. Create a project plan: list of files and their purpose
2. Show the plan to the user and ask for approval
3. Generate each file sequentially
4. Output files in the format: `path/to/file.ext`, followed by the file content

### Improve Mode

Given an existing codebase and an improvement request:

1. Read all existing files
2. Identify the minimal set of files that need to change
3. Output only the changed files (not unchanged ones)
4. Explain what changed and why

## File Output Format

```
path/to/file.py
```
```python
# file contents here
```

Each file is preceded by its path in a plain code block, followed by the file content in a language-tagged code block.

## Project Structure Rules

Generated projects must include:
- A `README.md` with setup and usage instructions
- A `requirements.txt` or `package.json` (appropriate for the language)
- A basic test file
- A `.gitignore` appropriate for the stack

## Quality Standards

- All generated code should be runnable without modification
- Use modern language features (Python 3.10+, ES2022, etc.)
- Include error handling — no bare `except: pass`
- Add type annotations for Python projects
- Use meaningful variable names — no single-letter variables except in loops

## Limitations

GPT Engineer does not:
- Run or test the generated code
- Access external APIs or databases to generate real data
- Generate code that requires secrets (API keys, passwords) hardcoded
