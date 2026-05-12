# Devin Agent — Task Instructions

## Overview

This AGENT.md configures Devin's behavior for this repository. Devin is an autonomous software engineering agent. It can read and write files, run commands, browse the web, and interact with external services.

## Repository

This is a Go microservices repository. Services live in `services/`. Shared libraries are in `pkg/`. Infrastructure code is in `infra/`.

## How Devin Should Work on This Codebase

### Before starting any task

1. Read the relevant service's README in `services/<name>/README.md`
2. Run `make test` to confirm the baseline test suite passes
3. Check open issues for any related work to avoid duplication

### Code conventions

- Use Go 1.22 features where appropriate
- Follow `gofmt` + `golangci-lint` — run `make lint` before committing
- Error wrapping: `fmt.Errorf("doing X: %w", err)` always
- Context is the first parameter of every function that does I/O
- Tests live alongside source: `foo.go` + `foo_test.go`

### Service boundaries

Services communicate only via gRPC (internal) or HTTP/JSON (external). Do not add direct database access from one service to another service's database. Shared data models are in `pkg/proto/`.

### Migrations

Database migrations use `golang-migrate`. Migration files are in `services/<name>/migrations/`. Always write both up and down migrations. Never modify a migration that has been applied to production.

### CI/CD

The CI pipeline runs on GitHub Actions. Do not modify `.github/workflows/` without explicit instruction. Devin can read pipeline results but should not change pipeline configuration.

## What Devin Can Do Autonomously

- Write code, tests, and documentation
- Run `make test`, `make lint`, `make build`
- Create feature branches and commits
- Open draft pull requests

## What Requires Human Approval

- Merging to `main`
- Deploying to any environment
- Modifying CI/CD configuration
- Adding or upgrading dependencies
- Changing gRPC proto files (requires coordination across services)

## Escalation

If Devin encounters an error it cannot resolve after three attempts, it should:
1. Document what it tried in a comment on the issue
2. Tag the issue with `needs-human`
3. Stop working on that task
