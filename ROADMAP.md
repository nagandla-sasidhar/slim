# SLIM Format — Roadmap

## Shipped

| Item | Status |
|---|---|
| SLIM v2.0 spec (`::SECTION`, `@key`, `@+key`, `~ comment`, `$var`) | ✅ |
| Python reference parser (`slim-parser` on PyPI) | ✅ |
| Markdown → SLIM converter | ✅ |
| YAML → SLIM converter | ✅ |
| Token benchmark (43.3% avg savings, 6 real files) | ✅ |
| Claude Code plugin — `/slim` skill (Anthropic verified) | ✅ |
| VS Code extension — syntax highlighting (Microsoft verified) | ✅ |
| IntelliJ IDEA plugin — syntax highlighting + folding | ✅ |
| Notepad++ UDL — syntax highlighting + folding | ✅ |
| Antigravity CLI plugin — `/slim` skill | ✅ |
| slimformat.org — website, playground, docs, install page | ✅ |

---

## Planned

### GitHub Copilot Chat Extension
Bring `/slim` as a chat participant inside GitHub Copilot (`@slim`) — convert, validate, and report token savings directly from VS Code Copilot chat without leaving the editor.
- **Why:** VS Code extension currently provides syntax highlighting only; Copilot chat requires a separate chat participant extension using `vscode.chat.createChatParticipant` API
- **Scope:** New VS Code extension published alongside `slim-format.slim-language`

### Docs/PDF → SLIM Converter
Convert popular document formats (PDF, DOCX, Google Docs) to SLIM — massive token savings when feeding reference material into LLM context.
- **Why:** RAG pipelines and long-context workflows routinely inject entire documents; stripping formatting before injection saves significant tokens at scale
- **Scope:** CLI tool + Python library + playground integration

### TypeScript Parser
Reference implementation in TypeScript — enables browser-side parsing and native integration in Node.js LLM pipelines.
- **Why:** Most LLM orchestration frameworks (LangChain.js, Vercel AI SDK) are TypeScript-first
- **Scope:** Port of Python parser with full test suite parity

### JetBrains Marketplace Publish
Publish the IntelliJ plugin to JetBrains Marketplace for one-click install.
- **Scope:** Marketplace account setup, plugin signing, submission

### SLIM Interaction Logger
Structured `.jsonl` logger for Claude API integrations — captures real token counts from API responses, parse errors, unresolved variables, and savings per call.
- **Scope:** `slim_logger.py` wrapper + `slim_tail.py` live viewer
