# Copilot Instructions — Vercel AI SDK

## Repository Overview

The Vercel AI SDK is a TypeScript library for building AI-powered applications with streaming support. It works with Next.js, Nuxt, SvelteKit, and other frameworks.

## Package Structure

This is a monorepo with the following packages:

| Package | Path | Description |
|---------|------|-------------|
| `ai` | `packages/ai/` | Core SDK — providers, streaming, tools |
| `@ai-sdk/openai` | `packages/openai/` | OpenAI provider |
| `@ai-sdk/anthropic` | `packages/anthropic/` | Anthropic provider |
| `@ai-sdk/google` | `packages/google/` | Google AI provider |
| `@ai-sdk/react` | `packages/react/` | React hooks (`useChat`, `useCompletion`) |
| `@ai-sdk/svelte` | `packages/svelte/` | Svelte stores |
| `@ai-sdk/vue` | `packages/vue/` | Vue composables |

## Development

```bash
pnpm install
pnpm build
pnpm test
```

Run a specific package's tests:
```bash
pnpm --filter ai test
pnpm --filter @ai-sdk/openai test
```

## Contributing Code

### Adding a new provider

1. Copy `packages/openai/` as a starting point
2. Implement `LanguageModelV1` interface from `@ai-sdk/provider`
3. Implement `EmbeddingModelV1` if the provider supports embeddings
4. Add integration tests using `@ai-sdk/provider-utils/test`
5. Export from `packages/ai/src/index.ts`

### Streaming protocol

The AI SDK uses a custom streaming protocol (`AIStreamProtocol`). Text chunks are prefixed with `0:`, tool calls with `9:`, tool results with `a:`. Understand this protocol before modifying any streaming code.

### Tool calling

Tools must follow the `CoreTool` schema. Parameters are validated with Zod at runtime. Never pass unvalidated tool parameters to any external system.

## Copilot Guidance

When generating code for this repo:

- Use the `experimental_` prefix for unstable APIs
- All new APIs must be exported from the root `ai` package
- Every new feature needs an example in `examples/`
- Breaking changes need a migration guide in `docs/`
- Never add framework-specific code to `packages/ai/` — it must be framework-agnostic
