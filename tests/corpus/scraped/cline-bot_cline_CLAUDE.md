# Cline — Autonomous Coding Agent for VS Code

## CLAUDE.md

Cline (formerly Claude Dev) is an autonomous coding agent extension for VS Code. This file guides AI assistants contributing to the Cline codebase.

## Architecture

Cline runs as a VS Code extension with two processes:
- **Extension host process** — core agent logic (TypeScript/Node.js)
- **Webview process** — the chat UI (React)

Communication between them uses VS Code's webview message API.

## Repository Structure

```
src/
  agent/
    v1/
      index.ts           Main agent loop
      tools/             Tool implementations
        execute_command.ts
        read_file.ts
        write_to_file.ts
        browser_action.ts
        ...
  shared/                Types shared between extension and webview
  providers/
    ClaudeDevProvider.ts  VS Code provider (sidebar activation)
webview-ui/
  src/
    App.tsx              Chat UI root
    components/
    context/
    utils/
```

## Agent Loop

The core loop in `src/agent/v1/index.ts`:

1. Send user message + context to Claude API (streaming)
2. Parse `<tool_use>` blocks from the response
3. Execute each tool, collect `<tool_result>`
4. Feed results back to the API as `tool_result` content blocks
5. Repeat until no tool calls remain
6. Display final response to user

## Tool Implementations

Each tool is a separate file in `src/agent/v1/tools/`. Tools receive a `ToolInput` object and return a `ToolResponse`.

When adding a new tool:
1. Add the function definition to the system prompt template in `src/prompts/system.ts`
2. Create the tool file in `src/agent/v1/tools/`
3. Register it in `src/agent/v1/tools/index.ts`
4. Add it to the tool input TypeScript union type

## Building and Running

```bash
npm install
npm run compile          # one-time build
npm run watch            # watch mode

# In VS Code: press F5 to launch Extension Development Host
```

## Webview development

```bash
cd webview-ui
npm install
npm run dev              # vite dev server for webview (requires extension host)
```

## Key Behaviors

- **Diff view**: file edits are shown in VS Code's diff editor before being applied
- **Streaming**: Claude's response streams in real-time; tool calls are extracted as they stream
- **Auto-approval**: configurable — users can allow Cline to run commands and write files without per-action approval

## Do Not

- Do not break streaming — users see output in real-time, any buffering is a regression
- Do not add new dependencies to `package.json` without checking bundle size impact
- Do not access VS Code APIs from `webview-ui/` — it runs in a sandboxed iframe
