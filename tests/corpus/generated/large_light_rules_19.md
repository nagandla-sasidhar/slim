# CLAUDE.md — Open Source Library Project

## Project Overview

This is the rule file for Claude when assisting with contributions to this open-source library. The library provides a lightweight HTTP client for Python with automatic retry, timeout, and connection pooling.

## Repository Layout

The repository is organized as follows. Source code lives in src/httpclient/. Tests live in tests/. Documentation source is in docs/ and builds to docs/_build/. Examples are in examples/.

The main module is src/httpclient/client.py. The connection pool is in src/httpclient/pool.py. Retry logic is in src/httpclient/retry.py. Type stubs are in src/httpclient/py.typed and the accompanying .pyi files.

## Development Setup

The project uses pyproject.toml for all configuration. Development dependencies are in the dev extras group. Use a virtual environment. The Makefile has targets for common tasks.

## Coding Rules

Follow the existing code style exactly. The project uses black for formatting with a 100-character line length. Imports are sorted with isort using the black profile. Type annotations are required on every public function and class.

Private functions start with a single underscore. Internal-only modules start with an underscore in their filename. Nothing that starts with an underscore is considered part of the public API.

Error types are defined in src/httpclient/exceptions.py. Do not raise built-in exceptions directly. Wrap them in the library's exception hierarchy so callers can catch httpclient-specific errors without importing Python internals.

## Public API Rules

The public API is whatever is exported from src/httpclient/__init__.py. If you add a new public symbol, add it to __all__ in __init__.py. If you add a new public symbol, document it in docs/api.rst.

Backward compatibility is taken seriously. Once a symbol is public, it cannot be removed without a deprecation cycle. Deprecation means adding a DeprecationWarning in the current minor version, removing in the next major version.

Default argument values for public functions are part of the API contract. Changing a default is a breaking change. Adding a new optional argument with a sensible default is not breaking.

## Testing Requirements

Every bug fix must include a regression test that fails before the fix and passes after. Test names must describe the scenario being tested, not the function being tested.

Test files mirror the source structure. Tests for src/httpclient/retry.py go in tests/test_retry.py. Tests for integration scenarios go in tests/integration/.

Use pytest fixtures for common setup. Do not use unittest.TestCase. Use pytest-parametrize for testing multiple cases of the same logic.

The test suite must pass with no warnings. If a warning is expected in a test, use pytest.warns to assert it explicitly.

## Documentation Rules

Every public function, class, and method has a docstring. Docstrings follow Google style. The first line is a single sentence summary ending with a period. Parameters, Returns, and Raises sections follow when applicable.

Do not document private functions unless the logic is genuinely complex. In that case, use an inline comment rather than a docstring.

When you change behavior, update the changelog in CHANGELOG.md. Use the Keep a Changelog format.

## Pull Request Guidelines

Pull requests should be focused. One logical change per PR. If the PR touches both a bug fix and a refactor, split them.

The PR title follows Conventional Commits. The PR description explains the why, not just the what. It includes a testing section describing how to verify the change.

Do not add yourself to CONTRIBUTORS.md. That is maintained automatically from the git log.

## Release Process

Releases are managed by the maintainers. Do not bump the version number in a PR unless you are a maintainer and have been asked to do a release. The release process uses bump2version and GitHub Actions.

## Things Claude Should Not Do

Do not add new dependencies to the project without a discussion in an issue first. The library aims to have zero runtime dependencies. Adding even a well-known dependency requires a strong justification.

Do not modify pyproject.toml [build-system] or [tool.setuptools] sections. These are set up precisely for the packaging toolchain.

Do not modify or delete .github/workflows/ files without explicitly being asked to.
