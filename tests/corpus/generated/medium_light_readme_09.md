# AutoTest Agent

AutoTest is an AI agent that reads your source code and automatically writes unit tests for uncovered functions.

## Getting Started

Install the agent:

```bash
pip install autotest-agent
autotest init
```

Configure your project by adding a section to your existing config:

```yaml
autotest:
  source_dir: src/
  test_dir: tests/
  framework: pytest
  coverage_target: 80
```

Run the agent:

```bash
autotest run --target src/utils.py
```

## How It Works

The agent reads source files and identifies functions that have no corresponding test. For each uncovered function, it:

1. Analyzes the function signature and docstring
2. Identifies likely input types and edge cases
3. Generates test cases covering happy path, edge cases, and error conditions
4. Writes the tests to the appropriate file in the test directory

## Supported Frameworks

- pytest (Python)
- Jest (JavaScript/TypeScript)
- JUnit 5 (Java)
- Go testing package

## Configuration Reference

source_dir: Directory to scan for untested code. Default is src/.

test_dir: Directory where tests are written. Default is tests/.

framework: Testing framework to use. Must match what is already in the project.

coverage_target: Minimum coverage percentage to aim for. Agent stops generating once this is reached. Default is 80.

exclude_patterns: List of glob patterns for files to skip. Default is empty.

max_tests_per_function: Cap on how many test cases to generate per function. Default is 5.

## Limitations

The agent does not run tests itself. Use your normal test runner. The agent does not understand external dependencies that require real network or database connections. For those, it generates tests with mocked dependencies and adds a comment indicating what the mock replaces.
