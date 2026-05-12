# Sweep — AI Junior Developer

## Agent Instructions

Sweep is an AI assistant that resolves GitHub issues by writing code and opening pull requests.

## How Sweep Works

When a GitHub issue is labeled with `sweep`, Sweep:

1. Reads the issue title and body
2. Searches the codebase for relevant files
3. Plans the changes needed
4. Writes code changes
5. Runs the test suite
6. Opens a pull request with the changes

## Rules for This Repository

### What Sweep can change

- Source files in `src/`
- Test files in `tests/`
- Documentation in `docs/` (Markdown only)

### What Sweep should never change

- `requirements.txt` or `pyproject.toml` — dependency changes need human review
- Database migration files
- Environment configuration files (`.env*`, `config/*.yaml`)
- CI/CD pipeline files

### Code Style

This project uses Black (line-length=88) and isort. Sweep should generate code that passes:

```bash
black --check src/ tests/
isort --check-only src/ tests/
flake8 src/ tests/
```

### Tests

Every code change must have tests. Sweep should:
1. Add tests for new functionality
2. Update tests when behavior changes
3. Never delete existing tests (unless the code being tested is deleted)

Minimum test coverage for new code: 80%.

### Commit Messages

Follow Conventional Commits: `fix:`, `feat:`, `refactor:`, `test:`.

Include the issue number: `fix: handle None in parse_response (#123)`.

### Pull Request Template

PR title: `Sweep: {issue_title} (#{issue_number})`

PR body must include:
- Summary of changes
- Testing done
- Link to the issue

## Issue Writing Tips

For best results, Sweep issues should:
- Describe the desired behavior, not the implementation
- Include a minimal reproduction if it's a bug
- Specify which files are likely affected if known
- Include example inputs and expected outputs
