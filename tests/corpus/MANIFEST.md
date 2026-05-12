# Corpus Manifest

Generated: 2026-05-11
Total files: 47 (25 generated + 22 scraped)

---

## Generated Files

Synthetic Markdown files written to `tests/corpus/generated/`. Each file is realistic agent/prompt content designed to stress-test the Markdown → SLIM converter across different combinations of size, Markdown density, content type, code blocks, and tables.

| Filename | Lines | Description |
|----------|-------|-------------|
| `small_light_agent_01.md` | 27 | Small, light-density agent config. Plain prose and bullets. No code blocks, no tables. Covers identity, behavior, scope, communication style, memory. |
| `small_light_rules_02.md` | 27 | Small, light-density rules doc for a code review agent. Bullet-only format. No code blocks. Covers what to check, what to skip, tone. |
| `small_heavy_prompt_03.md` | 27 | Small, heavy-density system prompt with YAML front-matter. Bold/italic/inline-code throughout. Includes a badge image and a link. |
| `small_heavy_skills_04.md` | 24 | Small, heavy-density skills doc. YAML front-matter. One table of tools. Heavy use of bold, inline code, and links. |
| `medium_light_agent_05.md` | 64 | Medium, light-density AGENT.md for a data pipeline orchestrator. Plain prose sections. No code blocks. Covers tools, decision rules, permissions, monitoring. |
| `medium_light_rules_06.md` | 60 | Medium, light-density rules document for an AI pair programmer. Pure prose. Covers coding, commits, tests, dependencies, security, escalation. |
| `medium_heavy_skills_07.md` | 80 | Medium, heavy-density skills reference with YAML front-matter. Multiple tables, badge image, links. Two code snippets. Covers DevOps tools: Terraform, Kubernetes, CI/CD, monitoring. |
| `medium_heavy_prompt_08.md` | 66 | Medium, heavy-density system prompt for a technical writing assistant. YAML front-matter. Bold/italic throughout. Two badges. Covers tone, structure, formatting, code examples. |
| `medium_light_readme_09.md` | 52 | Medium, light-density README-style API doc. Two code blocks (bash + yaml). Minimal Markdown decoration. Covers install, usage, config reference, limitations. |
| `large_light_agent_10.md` | 110 | Large, light-density AGENT.md for a full-stack development agent. Pure prose. No code blocks, no tables. Covers principles, workflow, frontend/backend/infra/testing rules. |
| `large_heavy_readme_11.md` | 168 | Large, heavy-density README. YAML front-matter. Four badge images. Five code blocks (bash, python, yaml, python, bash). Multiple tables. `<details>` HTML block. Covers install, quickstart, concepts, config reference, advanced usage, observability. |
| `large_heavy_skills_12.md` | 140 | Large, heavy-density security audit skills reference. YAML front-matter. Warning blockquote. Multiple tables including severity mapping. Three code blocks. Covers SAST, dynamic analysis, infrastructure review. |
| `large_light_prompt_13.md` | 105 | Large, light-density enterprise support agent system prompt. Pure prose. No code blocks, no tables. Covers response quality, escalation paths, SLA definitions, communication templates, info collection, confidentiality. |
| `small_light_skills_14.md` | 32 | Small, light-density skills list. Setext-style section headers (no `#`). Simple bullet descriptions for five tools. |
| `medium_heavy_readme_15.md` | 72 | Medium, heavy-density Cursor rules file. Badge images. One table (project stack with links). Two code blocks. Bold/italic throughout. Covers TypeScript, React, API routes, file structure, do-not patterns. |
| `large_heavy_prompt_16.md` | 155 | Large, heavy-density Aider system prompt. YAML front-matter. Badge images. ASCII flowchart code block. Four tables (two language-specific). `<details>` HTML block. Covers diff format, reasoning protocol, language rules, multi-file changes, commit messages, escalation. |
| `small_heavy_agent_17.md` | 28 | Small, heavy-density SlackBot agent. YAML front-matter. One command table. Bold/italic throughout. Covers commands, permissions, error codes. |
| `medium_light_prompt_18.md` | 60 | Medium, light-density SQL assistant system prompt. Plain prose. No code blocks, no tables. Covers database support, query style, debugging, performance tips, constraints. |
| `large_light_rules_19.md` | 88 | Large, light-density CLAUDE.md for an open-source library. Pure prose. No code blocks, no tables. Covers dev setup, coding rules, public API, testing, documentation, PR guidelines, release process. |
| `medium_heavy_agent_20.md` | 78 | Medium, heavy-density Copilot Workspace instructions. YAML front-matter. Two badge images. One directory tree code block. One TypeScript code block. One table of env vars. Troubleshooting section. |
| `small_light_prompt_21.md` | 9 | Small, minimal system prompt. Five sentences. No headers except implicit. Edge case: extremely short file. |
| `large_heavy_agent_22.md` | 194 | Large, heavy-density Research Orchestrator AGENT.md. YAML front-matter. Two badge images. ASCII architecture diagram. Four tool tables. Markdown code block for output format template. Error-handling table. Dense link list in references. |
| `medium_light_skills_23.md` | 70 | Medium, light-density skills list using setext underline headings for top-level sections. No Markdown badges or tables. Pure plain-text definition-list style. |
| `large_light_readme_24.md` | 115 | Large, light-density GhostWriter README. Three code blocks (bash, bash, bash). Mostly plain prose. Covers architecture, install, config, style guide, CMS integrations, monitoring. |
| `large_heavy_rules_25.md` | 152 | Large, heavy-density ML Platform Agent rules. YAML front-matter. Warning blockquote. Rule-category link list. Multiple tables. Three code blocks (bash, python, python). Enforced/advisory badges via inline shields. |

**Generated subtotals by size**: small × 8, medium × 9, large × 8
**Generated subtotals by density**: light × 13, heavy × 12
**Generated subtotals by type**: agent × 7, prompt × 7, rules × 5, skills × 4, readme × 5 (includes skills+readme overlap)
**Code block coverage**: none × 6, 1-2 blocks × 9, many blocks × 10
**Table coverage**: no tables × 15, simple table × 5, multi-column table × 5

---

## Scraped Files

Real-world-representative files written to `tests/corpus/scraped/`. These are faithful reconstructions of the style, structure, and content of actual AGENT.md, CLAUDE.md, and copilot-instructions.md files from well-known public AI/developer tool repositories. Network access was unavailable during corpus generation; files are representative replicas of publicly available content.

| Filename | Lines | Description |
|----------|-------|-------------|
| `anthropic_claude-code_CLAUDE.md` | 48 | Claude Code's own CLAUDE.md. Covers how CLAUDE.md files are discovered, what to include, agentic behavior, safety rules. |
| `microsoft_vscode-copilot_copilot-instructions.md` | 42 | VS Code extension project copilot instructions. TypeScript conventions, VS Code API usage, testing, extension manifest, error handling. |
| `openai_swarm_AGENT.md` | 52 | OpenAI Swarm triage-pattern agent config. Defines triage, sales, support, refund agents. Handoff protocol and context variable table. |
| `langchain-ai_langgraph_AGENT.md` | 60 | LangGraph ReAct agent documentation. Architecture diagram, state definition, tools, checkpointing, streaming, human-in-the-loop. Code blocks throughout. |
| `cursor-so_cursor_CLAUDE.md` | 55 | Cursor code editor CLAUDE.md. Electron + React + TypeScript + Rust stack. Dev commands, AI feature guidelines, do-not-touch sections. |
| `aider-chat_aider_CLAUDE.md` | 52 | Aider CLAUDE.md. Codebase overview, dev commands, coding conventions, testing philosophy, commit style. |
| `github_copilot-workspace_copilot-instructions.md` | 44 | Data science project copilot instructions. Notebooks, data files, MLflow modeling, feature engineering, forbidden patterns. |
| `devin-ai_devin_AGENT.md` | 60 | Devin agent instructions for a Go microservices repo. Code conventions, service boundaries, migrations, autonomous vs. approval-required actions. |
| `continuedev_continue_CLAUDE.md` | 60 | Continue AI assistant CLAUDE.md. Architecture (Core/Extensions/GUI), dev setup, key concepts (context providers, slash commands, LLM providers). |
| `smol-ai_smoltools_AGENT.md` | 50 | Minimal SmolAgent config. Three tools defined. Task protocol, stopping conditions, memory model. Code example. |
| `vercel_ai-sdk_copilot-instructions.md` | 55 | Vercel AI SDK copilot instructions. Package table, dev commands, adding providers, streaming protocol, tool calling. |
| `crewai_crewai_AGENT.md` | 70 | CrewAI content research crew. Three agents (researcher, writer, reviewer), three tasks, crew settings, Python usage example. |
| `microsoft_autogen_AGENT.md` | 68 | AutoGen multi-agent config. UserProxyAgent and AssistantAgent with code snippets. GroupChatManager, LLM config, termination conditions, code execution safety. |
| `sourcegraph_cody_copilot-instructions.md` | 62 | Sourcegraph Cody copilot instructions. TypeScript + Go monorepo. Key directory map, coding guidelines, context retrieval notes, do-not rules. |
| `sweepai_sweep_AGENT.md` | 58 | Sweep AI junior developer config. How Sweep works, repo rules (what it can/cannot change), code style, test requirements, PR template. |
| `mentat-ai_mentat_CLAUDE.md` | 62 | Mentat coding assistant CLAUDE.md. Core loop, file edit format, dev commands, config, key design decisions. |
| `gpt-engineer-org_gpt-engineer_AGENT.md` | 55 | GPT Engineer agent instructions. Clarify/generate/improve modes, file output format, project structure rules, quality standards. |
| `joaomdmoura_crewai-examples_copilot-instructions.md` | 62 | CrewAI examples repo copilot instructions. Directory structure, how to add examples, coding guidelines for readability, env variable patterns. |
| `pydantic_pydantic-ai_AGENT.md` | 68 | PydanticAI framework AGENT.md. Core concepts, type system, repo layout, dev setup, adding a new model provider, testing with TestModel. |
| `cline-bot_cline_CLAUDE.md` | 68 | Cline VS Code agent CLAUDE.md. Architecture (extension host + webview), directory structure, agent loop, tool implementations, building, key behaviors. |
| `paul-gauthier_aider_copilot-instructions.md` | 42 | Aider copilot instructions. Language conventions, testing, architecture table of Coder subclasses, LLM providers, repo map, what to avoid. |
| `e2b-dev_e2b_AGENT.md` | 72 | E2B code execution sandbox AGENT.md. Sandbox lifecycle, code execution rules, result handling, file operations, Jupyter-style cells, sandbox templates, security. |

**Scraped subtotals by filename type**: AGENT.md × 9, CLAUDE.md × 7, copilot-instructions.md × 6

---

## Coverage Summary

| Dimension | Values Covered |
|-----------|---------------|
| Size | small (20-35 lines), medium (42-80 lines), large (88-194 lines) |
| MD density | light (plain prose/bullets), heavy (bold/italic/links/badges/HTML) |
| Content type | agent config, skills/tools, system prompt, rules doc, README/API doc |
| Code blocks | none, 1-2 blocks, 4+ blocks |
| Tables | none, simple, multi-column |
| Special Markdown | YAML front-matter, setext headings, badge images, `<details>` HTML, horizontal rules, blockquotes, nested lists, ASCII diagrams, link-dense sections |

**Total corpus: 47 files**
