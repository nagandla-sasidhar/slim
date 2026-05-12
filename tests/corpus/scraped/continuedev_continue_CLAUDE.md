# Continue — AI Code Assistant

## Project CLAUDE.md

Continue is an open-source AI code assistant for VS Code and JetBrains. This file helps AI assistants contribute to the Continue codebase.

## Architecture

Continue has three main components:

**Core** (`core/`) — TypeScript/Node.js. Contains the LLM providers, context providers, slash commands, and the main Continue protocol. This runs in the extension's backend process.

**Extensions** — Two IDE extensions:
- `extensions/vscode/` — VS Code extension (TypeScript)  
- `extensions/intellij/` — JetBrains plugin (Kotlin)

**GUI** (`gui/`) — React app running in the sidebar webview.

Communication between Core and GUI uses a message-passing protocol defined in `core/protocol/`.

## Development Setup

```bash
# Install dependencies
npm install

# Build core
cd core && npm run build

# Start VS Code extension dev mode
cd extensions/vscode && npm run dev

# Run tests
npm test --workspaces
```

## Key Concepts

**Context Providers** — plugins that add context to LLM prompts. Examples: `@codebase`, `@docs`, `@web`. New context providers go in `core/context/providers/`.

**Slash Commands** — inline commands triggered by `/`. New slash commands go in `core/commands/slash/`.

**LLM Providers** — integrations with different LLM APIs. All providers extend `BaseLLM` in `core/llm/baseLLM.ts`.

**Config** — User configuration is in `~/.continue/config.json`. The schema is in `core/config/types.ts`.

## Adding a New LLM Provider

1. Create `core/llm/llms/MyProvider.ts` extending `BaseLLM`
2. Implement `_streamComplete` and optionally `_streamChat`
3. Add the provider to `core/llm/llms/index.ts`
4. Add a config template in `core/llm/templates/`
5. Add tests in `core/llm/__tests__/`
6. Document in `docs/docs/reference/Model Providers/`

## Testing

Unit tests use Jest. Integration tests that need a real LLM are in `core/test/integration/` and are skipped in CI unless `INTEGRATION_TESTS=true`.

## Do Not

- Do not add provider-specific logic into the core protocol — keep providers isolated
- Do not store conversation history in the extension process — it belongs in Core
- Do not access the file system directly from the GUI — use IPC
