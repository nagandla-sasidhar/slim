# Copilot Instructions — Sourcegraph Cody

## What is Cody?

Cody is an AI coding assistant that uses Sourcegraph's code intelligence (precise code navigation, code search) to provide context-aware completions and chat.

## Working in This Repo

This is a TypeScript + Go monorepo.

- Frontend (VS Code extension, web UI): TypeScript/React in `client/`
- Backend (context fetching, LLM proxy): Go in `internal/`
- Agent logic: TypeScript in `lib/shared/`

### Key directories

```
client/
  cody-shared/      Shared TypeScript logic (no UI)
  vscode/           VS Code extension
  web/              Web UI
internal/
  completions/      LLM provider integrations (Go)
  codycontext/      Context retrieval (Go)
  embeddings/       Vector search (Go)
lib/
  shared/           Agent, prompting, context management (TypeScript)
```

## Coding Guidelines

### TypeScript

- Functional components only (React)
- Use `vitest` for unit tests
- Import paths: use `@sourcegraph/cody-shared` not relative `../../` imports
- All LLM interactions go through `lib/shared/src/llm/`

### Go

- `gofmt` + `golangci-lint` enforced in CI
- HTTP handlers use the standard `net/http` library — no Gin or Echo
- Database access uses `internal/database/` — no raw SQL outside that package
- gRPC services defined in `proto/` — regenerate with `make proto`

## Context Retrieval

Cody's key differentiator is context. When modifying context retrieval:

1. Understand the `ContextItem` type in `lib/shared/src/codebase-context/`
2. Context providers are registered in `getDefaultContextProviders()`
3. Test context quality with the eval harness in `lib/shared/src/eval/`

## Copilot Should Know

- Cody supports multiple LLM providers: Anthropic, OpenAI, Google, Ollama
- Provider selection logic is in `client/cody-shared/src/models/`
- The main system prompt is assembled in `lib/shared/src/chat/prompts.ts`
- Cody uses "enhanced context" — ranked, deduplicated context from multiple sources

## Do Not

- Do not add Sourcegraph-specific APIs to `cody-shared` — it must work standalone
- Do not add hardcoded model names — use the model registry
- Do not ship changes that degrade autocomplete latency by more than 20ms
