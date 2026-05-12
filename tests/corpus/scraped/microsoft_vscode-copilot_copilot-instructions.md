# GitHub Copilot Instructions

This file contains workspace-level instructions for GitHub Copilot Chat and Copilot Edits.

## Project: VS Code Extension

This is a TypeScript VS Code extension. Follow these conventions when generating code.

### TypeScript conventions

- Use strict TypeScript (`"strict": true` in tsconfig.json)
- Prefer `const` over `let`, never use `var`
- Use `async/await` over Promise chains
- Export types separately from values: `export type { Foo }` not `export { Foo }`

### VS Code API usage

- Check the minimum engine version in `package.json` before using new VS Code APIs
- Use `vscode.workspace.fs` for file operations, not Node.js `fs` module
- Dispose disposables in the `context.subscriptions` array
- Use `vscode.window.withProgress` for long-running operations

### Testing

Tests use Mocha + the VS Code test runner. Test files live in `src/test/` and follow the naming convention `*.test.ts`.

To run tests:
```
npm run test
```

### Extension manifest

When adding new commands, add them to:
1. `package.json` under `contributes.commands`
2. The appropriate menu in `contributes.menus`
3. The `activate` function in `src/extension.ts`

### Error handling

All VS Code commands should be wrapped in try/catch. Surface errors to the user via `vscode.window.showErrorMessage`. Log detailed errors to the output channel.

## What Copilot should not change

- Do not modify `package.json` `engines.vscode` without asking
- Do not add dependencies without checking existing similar functionality
- Do not remove existing telemetry calls
