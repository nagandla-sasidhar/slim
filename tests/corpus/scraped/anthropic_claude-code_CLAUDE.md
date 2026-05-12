# Claude Code

Claude Code is an agentic coding tool made by Anthropic.

## How to use Claude Code

Claude Code reads `CLAUDE.md` files from the following locations:
- `~/.claude/CLAUDE.md` (user-level)
- `<repo-root>/CLAUDE.md` (project-level)
- Subdirectory `CLAUDE.md` files within the project

All discovered files are concatenated and included in Claude's context.

## Writing effective CLAUDE.md files

Keep them focused. Claude Code's context window is finite. Write what matters for the current project: project structure, coding conventions, commands to know, and things Claude should or shouldn't do.

### Bash commands

Include the commands developers actually run:

```bash
# Build
npm run build

# Test
npm test
npm run test:watch

# Lint
npm run lint
npm run lint:fix
```

### Project-specific rules

Tell Claude about conventions that aren't obvious from the code:

- Which test framework is in use
- Where to put new files
- Naming conventions
- Things to never do (e.g., never use `var`, always use `pnpm` not `npm`)

### MCP servers

If the project uses MCP servers, document them here so Claude knows how to invoke them.

## Agentic behavior

Claude Code can run autonomously on tasks. It will:
- Read and edit files
- Run bash commands
- Search the codebase
- Make git commits

It will pause and ask for confirmation when it needs to run something potentially destructive or when it is uncertain about intent.

## Safety

Claude Code will never:
- Exfiltrate code to untrusted systems
- Introduce backdoors or security vulnerabilities intentionally
- Ignore explicit user instructions

## Feedback

Report issues at https://github.com/anthropics/claude-code/issues
