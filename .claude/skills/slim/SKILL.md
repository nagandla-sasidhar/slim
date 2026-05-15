---
name: slim
description: Use this skill when the user asks to convert a file to SLIM format, write a new SLIM document, validate or review an existing .slm file, check SLIM v2 syntax, or asks questions like "convert this to SLIM", "make this SLIM", "is this valid SLIM", "write a SLIM prompt", "create a SLIM agent config", or "review this .slm file". Also use when the user pastes Markdown/JSON/YAML/plain text and wants it optimised for LLM token usage.
version: 1.0.0
---

# SLIM Format Skill

SLIM (Structured LLM Instruction Markup) v2.0 is a token-efficient format for AI documents.
Website: https://slimformat.org | Repo: https://github.com/nagandla-sasidhar/TAML | Playground: https://slimformat.org/playground.html

## Core Syntax (v2.0)

```
@slim: 2.0               ← required first line
@key: value              ← orchestrator-only header (stripped before LLM)
@+key: value             ← LLM-visible header (appears in LLM text)
~ comment                ← always stripped
$var                     ← variable reference (interpolated at runtime)

::SECTION_NAME type      ← named section, no close tag (type is optional)
  content here           ← verbatim until blank line or next ::
:::NESTED_NAME type      ← nested section (one extra colon)
::CODE_1 lang            ← code block; increment _N for each additional block
```

## Header zone rules
- `@slim: 2.0` must be the first non-blank line
- `@key` = orchestrator metadata (model, retry, timeout, task IDs) — LLM never sees it
- `@+key` = LLM-visible info (name, description, purpose, context)
- Do NOT use `@+version` or `@+tags` — the LLM gains no value from these
- Headers end at the first `::` section or blank line after headers

## Section rules
- `::NAME` opens a section; the previous section implicitly closes
- No close tag — blank line or next `::` ends the content block
- Type hint is optional but valuable: `::CONTEXT markdown`, `::CODE python`, `::SCHEMA json`
- `:::NAME` for nested sections inside a parent section
- Section names: UPPERCASE by convention (CONTEXT, INSTRUCTIONS, EXAMPLES, SCHEMA, OUTPUT)

## Token-saving conversions from Markdown
| Markdown | SLIM |
|---|---|
| `---\nkey: val\n---` YAML front-matter | `@key: val` headers |
| `# Heading` | `::HEADING` section or `@+name: Heading` |
| `**bold**`, `*italic*` | plain text (meaning preserved) |
| `- item` bullet | plain indented line |
| `\`\`\`lang ... \`\`\`` | `::CODE_N lang` section |
| `<!-- comment -->` | `~ comment` |

## Token-saving conversions from YAML
| YAML | SLIM |
|---|---|
| `key: scalar` root scalar | `@key: scalar` header |
| `key:` block (array or object) | `::KEY` section |
| `- item` list entry | plain line (marker stripped) |
| `# comment` | `~ comment` |
| Quoted values `"val"` / `'val'` | unquoted plain value |
| Inline comment `key: val # note` | value without comment |

## How to convert YAML (step by step)

1. Skip `---` document separators
2. Root scalar `key: value` → `@key: value` header; strip inline `# comments` and quotes
3. Root block `key:` (array or object) → `::KEY` section; collect indented children, strip `- ` list markers
4. `# comment` lines → `~ comment`
5. Nested sub-keys inside a block → preserve as `subkey: value` lines in the section body
6. Report token savings

## How to convert Markdown (step by step)

1. **Read the source file** — identify: YAML front-matter, headings, bullets, code blocks, bold/italic
2. **Write header zone** — `@slim: 2.0`, then map YAML keys to `@key`/`@+key`
3. **Map headings → sections** — each `#` heading becomes `::HEADING_NAME`
4. **Strip inline formatting** — remove `**`, `*`, backtick pairs; preserve meaning
5. **Strip bullets** — remove `- ` / `* ` prefixes; keep indentation for hierarchy
6. **Wrap code blocks** — ` ```lang...``` ` → `::CODE_1 lang` (increment counter per block)
7. **Convert comments** — `<!-- ... -->` → `~ ...`
8. **Count tokens** — use `estimateTokens()` or tiktoken; report % saved

## Validation checklist for reviewing .slm files

- [ ] First line is `@slim: 2.0`
- [ ] No `@slim: 1.0` (old version)
- [ ] No `=== BLOCK [type] ... === /BLOCK` (old v1 syntax)
- [ ] `@+` used only for keys the LLM actually needs to know
- [ ] No `@+version` or `@+tags` (LLM doesn't benefit)
- [ ] Section names are UPPERCASE
- [ ] No close tags (no `:::` without an opener, no `=== /`)
- [ ] Variables (`$var`) have corresponding `@+var:` or `@var:` headers
- [ ] Code blocks use `::CODE_N lang` not fenced backticks

## Common section names by use case

**Agent config**: `::ROLE`, `::INSTRUCTIONS`, `::CONSTRAINTS`, `::CONTEXT`, `::EXAMPLES`, `::OUTPUT`
**System prompt**: `::SYSTEM`, `::PERSONA`, `::CAPABILITIES`, `::RESTRICTIONS`, `::FORMAT`
**RAG document**: `::SUMMARY`, `::CONTENT`, `::METADATA`, `::REFERENCES`
**API schema**: `::REQUEST`, `::RESPONSE`, `::ERRORS`, `::EXAMPLES`

## Example — minimal agent config

```
@slim: 2.0
@model: claude-opus-4-7
@task: $task_id
@+name: CodeReviewer
@+purpose: Review pull requests for security and quality issues

::INSTRUCTIONS
Review the diff in $context.
Focus on: security vulnerabilities, breaking changes, performance regressions.
Be concise. Flag critical issues first.

::CONSTRAINTS
Never approve a PR with an unaddressed critical security issue.
Keep each comment under 80 words.
```

## Example — YAML agent config → SLIM

Input YAML:
```yaml
# Agent config
name: DataAnalyst
model: claude-opus-4-7
temperature: 0.3
instructions:
  - Always cite data sources
  - Flag data quality issues
constraints:
  - Never fabricate data points
  - Keep reports under 500 words
```

Output SLIM:
```
@slim: 2.0
@name: DataAnalyst
@model: claude-opus-4-7
@temperature: 0.3

~ Agent config

::INSTRUCTIONS
Always cite data sources
Flag data quality issues

::CONSTRAINTS
Never fabricate data points
Keep reports under 500 words
```

## Reporting token savings

After converting, always report:
- Input tokens (original) — estimate as char_count / 4
- LLM-facing tokens (SLIM output, header zone excluded) — same estimation
- Savings % = (input - llm_facing) / input × 100
- For precise counts use tiktoken (Python) or the playground at https://slimformat.org/playground.html
