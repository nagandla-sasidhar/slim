# Cursor — AI Code Editor

## CLAUDE.md for Cursor Development

This file guides AI assistants working on the Cursor codebase.

## Tech Stack

- **Frontend**: Electron + React + TypeScript
- **Backend**: Node.js services, some Rust for performance-critical paths
- **AI layer**: Custom LLM proxy with streaming support
- **Database**: SQLite (local) + PostgreSQL (remote sync)
- **Build**: Turborepo + esbuild + Rust cargo

## Repository Structure

```
apps/
  cursor/         Main Electron app
  cursor-server/  Remote collaboration server
packages/
  ai/             LLM client, streaming, tool use
  editor/         CodeMirror extensions and patches
  ui/             Shared component library
  sync/           CRDT-based document sync
rust/
  parser/         Tree-sitter based code parser
  indexer/        Fast local code indexer
```

## Key Principles

**Performance first.** Cursor is a code editor — latency is perceptible. Every keystroke handler must complete in under 16ms. LLM calls are always async and never block the editor.

**Offline-capable.** Features degrade gracefully without network. Core editing never requires a network call.

**Privacy by default.** Code is not sent to any server without explicit user action. Telemetry is opt-in.

## Development Commands

```bash
# Install all deps
pnpm install

# Start dev mode (hot reload)
pnpm dev

# Run all tests
pnpm test

# Build production release
pnpm build:prod

# Run the Rust indexer tests
cargo test -p indexer
```

## AI Feature Development Guidelines

When working on AI features:

1. All LLM calls go through `packages/ai/src/client.ts` — never call provider APIs directly from app code
2. Use the `StreamingResponse` type for any response that streams tokens
3. Tool calls must be validated with Zod schemas before execution
4. Rate limiting is handled by the AI package — do not add your own

## Do Not Touch Without Discussion

- `packages/sync/` — CRDT logic is subtle, changes can cause data loss
- `apps/cursor/src/editor/patches/` — CodeMirror patches require careful testing
- Electron IPC channels defined in `apps/cursor/src/ipc/channels.ts` — adding/removing breaks protocol
