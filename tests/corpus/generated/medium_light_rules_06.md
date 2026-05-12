# Rules Document: AI Pair Programmer

## Purpose

This document defines the rules for the AI Pair Programmer integrated into our development workflow. All team members using the AI assistant should understand these rules.

## Coding Standards

The agent follows the project's ESLint and Prettier configuration exactly. It does not suggest changes that would fail linting. When generating new files, it reads the nearest config file to determine formatting rules.

## Branch and Commit Behavior

The agent never commits directly to main or develop. All changes go through a feature branch. Commit messages follow the Conventional Commits standard: feat, fix, docs, test, refactor, chore. The agent writes the commit message body when the change is non-trivial.

## Test Requirements

Every new function the agent writes gets a corresponding unit test. Tests go in the __tests__ directory mirroring the source tree. The agent uses the testing framework already in use in the project rather than introducing a new one.

## Dependencies

The agent does not add new dependencies without asking first. If a task can be done with built-in language features or existing dependencies, it does that. When a new dependency is genuinely needed, it explains why and names at least two alternatives.

## Security Rules

- Never log secrets, tokens, or passwords
- Never commit .env files or hardcoded credentials
- Sanitize all user input before using it in SQL or shell commands
- Use parameterized queries, never string interpolation in SQL
- Validate file paths to prevent directory traversal

## Communication

When the agent is not sure what the user wants, it asks one question, not multiple. It rephrases the request to confirm understanding before generating large amounts of code.

## Review Workflow

After producing a large block of code, the agent summarizes what it did in three bullets so the developer can quickly verify it matches intent. It asks for approval before opening pull requests or running tests.

## Escalation

If a task requires root access, production credentials, or modifying shared infrastructure, the agent halts and asks the user to perform that step manually.
