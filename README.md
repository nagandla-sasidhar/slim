# SLIM — Structured LLM Instruction Markup

**A compact plain-text format for AI prompts, agent configs, and documentation.**  
`.slm` replaces Markdown when your files are consumed by an LLM — same readability, fewer tokens.

> **43.3% average token reduction** over Markdown, measured on 6 real-world AI agent files  
> (cl100k_base tokenizer · benchmark included · 2026-05-10)

---

## Why SLIM?

Every token you send to an LLM costs money and burns context window. Markdown was designed for humans reading HTML — its `##`, `**bold**`, `| table |` syntax is verbose noise when the consumer is a language model.

SLIM keeps the structure, drops the ceremony:

| Feature | Markdown | SLIM |
|---------|----------|------|
| Headings | `## Section` | `# Section` |
| Metadata | YAML front-matter | `@key: value` header zone |
| Code blocks | ` ```python ` | `=== BLOCK [python]` |
| Comments | `<!-- stripped by HTML -->` | `~ stripped by parser` |
| Variable interpolation | *(none)* | `$variable` |
| Directives | *(none)* | `> CALL tool_name` |
| LLM-visible headers | *(none)* | `@+key: value` |

---

## Token Savings (Benchmark)

| Document | Markdown tokens | SLIM tokens | Savings |
|----------|----------------|-------------|---------|
| CLAUDE.md (project doc) | 748 | 423 | **43.4%** |
| SKILL.md — find-skills | 312 | 178 | **42.9%** |
| SKILL.md — pptx (complex) | 891 | 501 | **43.8%** |
| SKILL.md — claude-setup-audit | 634 | 360 | **43.2%** |
| Command — codemie-catchup | 287 | 164 | **42.9%** |
| ROADMAP.md (business doc) | 1,203 | 681 | **43.4%** |
| **Average** | | | **43.3%** |

Run the benchmark yourself:

```bash
cd benchmark
pip install tiktoken
python benchmark.py
```

---

## Quick Start

### Convert Markdown to SLIM online

Visit the **[SLIM Playground](https://nagandla-sasidhar.github.io/slim/website/playground.html)** — paste any Markdown, JSON, or plain text and see the SLIM output and token savings instantly.

### Use the Python parser

```bash
# No PyPI package yet — copy the slim/ directory into your project
cp -r slim/ your-project/slim/
```

```python
from slim.parser import SLIMParser, ParseMode

text = open("my-prompt.slm").read()
doc  = SLIMParser().parse(text)

# Ready to send to LLM — @headers stripped, $variables interpolated
llm_input = doc.to_llm_text()

# Access structured data
print(doc.headers["model"])           # e.g. "claude-opus-4-7"
print(doc.blocks["SYSTEM"].content)   # named block content
print(doc.token_estimate)             # rough token count
```

---

## SLIM Syntax at a Glance

### Complete example

```
@slim: 1.0
@model: claude-opus-4-7
@agent: CodeReviewer
@task: PR-942
@retry: 3
@+context: production codebase, strict mode

~ This comment is stripped before sending to the LLM

# Role
You are a senior code reviewer assigned to $task.

# Instructions
- Check for security vulnerabilities
- Suggest performance improvements
- Flag any breaking changes

=== DIFF [code]
def process(user_input):
    return eval(user_input)   # flag this
=== /DIFF

> ASSERT diff_size < 500
> CALL post_review_comment
```

### The Three Zones

```
+----------------------------------------------+
|  HEADER ZONE  @key: value                    |
|  Orchestrator-only. LLM never sees @keys.    |
|  @+ prefix = LLM-visible header.             |
+----------------------------------------------+
|  BODY ZONE  # headings, bullets, prose       |
|  What the LLM reads. $variables interpolated.|
|  ~ comment lines are stripped.               |
+----------------------------------------------+
|  BLOCK ZONE  === NAME [type] ... === /NAME   |
|  Named, typed payloads. Extracted by parser. |
|  Can appear anywhere in the body.            |
+----------------------------------------------+
```

### Headers

```
@slim: 1.0               # version (required, first line)
@model: claude-opus-4-7  # orchestrator-only metadata
@+context: prod env      # @+ = LLM sees this line
@include: base.slm       # inline-include another file
```

### Body

```
# Heading 1
## Heading 2

- bullet item
- another item

Regular prose. Reference $model or any @header as a $variable.

~ This is a comment — stripped before the LLM call
```

### Blocks

```
=== SYSTEM
You are a helpful assistant.
=== /SYSTEM

=== SCHEMA_USER [json-schema]
{"type":"object","properties":{"name":{"type":"string"}}}
=== /SCHEMA_USER

=== CODE_EXAMPLE [python]
result = slim_parser.parse(text)
=== /CODE_EXAMPLE
```

### Directives

```
> CALL search_web query="$topic"
> ASSERT response_length < 2000
> YIELD tool_result
> LOG "Processing $task"
> ABORT "Missing required field"
```

### Schema definitions (tool specs)

```
:tool get_weather
  desc: Fetch current weather for a location
  param: location str required
  param: units str default=metric
  returns: temperature float
  returns: description str
```

---

## Python Parser API

```python
from slim.parser import SLIMParser, SLIMDocument, ParseMode

# Basic parse
doc: SLIMDocument = SLIMParser().parse(source_text)

# With a base directory for @include resolution
doc = SLIMParser(base_dir="/path/to/prompts").parse(source_text)

# Strict mode — raises on any error
doc = SLIMParser(mode=ParseMode.STRICT).parse(source_text)
```

### `SLIMDocument` fields

| Field | Type | Description |
|-------|------|-------------|
| `version` | `str` | Value of `@slim:` header |
| `headers` | `dict` | All `@key` values (orchestrator-only) |
| `llm_headers` | `dict` | All `@+key` values (LLM-visible) |
| `body_lines` | `list[str]` | Raw body lines |
| `blocks` | `dict[str, Block]` | Named blocks (`=== NAME`) |
| `schemas` | `dict[str, Schema]` | `:tool` definitions |
| `directives` | `list[Directive]` | `> KEYWORD` calls |
| `variables` | `dict` | All variables (`@` + `@+` merged) |
| `errors` | `list[ParseError]` | Parse errors |
| `warnings` | `list[ParseError]` | Non-fatal warnings |

### Key methods

```python
doc.to_llm_text()    # body with @headers stripped, $vars interpolated — send this to LLM
doc.to_full_text()   # complete body, no stripping
doc.token_estimate   # rough token count (1 token ~= 4 chars)
```

### Sanitize untrusted user content

```python
from slim.parser import sanitize_user_content

# Escapes @, ===, >, ~ so user input cannot inject SLIM syntax
safe = sanitize_user_content(user_input)
```

---

## JavaScript Library

`website/js/slim.js` is a zero-dependency browser library with the same core features:

```html
<script src="slim.js"></script>
<script>
  const doc   = SLIM.parse(slmText);
  const html  = SLIM.highlight(slmText);    // syntax-highlighted HTML
  const slm   = SLIM.mdToSlm(markdownText); // convert Markdown to SLIM
  const slm2  = SLIM.jsonToSlm(jsonText);   // convert JSON to SLIM
  const count = SLIM.estimateTokens(text);  // token count estimate
</script>
```

---

## Editor Plugins

| Editor | Repository | Install |
|--------|-----------|---------|
| VS Code | [vscode-slim](https://github.com/nagandla-sasidhar/vscode-slim) | Build VSIX or search Marketplace for "SLIM Language" |
| IntelliJ IDEA | [intellij-slim](https://github.com/nagandla-sasidhar/intellij-slim) | `./gradlew buildPlugin` then install the plugin ZIP |
| Notepad++ | [notepadpp-slim](https://github.com/nagandla-sasidhar/notepadpp-slim) | Import `slim.udl.xml` via Language → User Defined Language |

---

## Repository Structure

```
slim/
├── SLIM_SPEC_v1.0.slm      # Full language specification (self-describing .slm file)
├── slim/
│   ├── parser.py            # Python reference implementation
│   └── __init__.py
├── website/
│   ├── index.html           # Landing page with interactive examples
│   ├── playground.html      # Live Markdown/JSON → SLIM converter
│   ├── docs.html            # Full documentation
│   ├── css/main.css
│   └── js/
│       ├── slim.js          # Zero-dependency JS library
│       ├── playground.js    # Playground UI logic
│       ├── tabs.js          # Tab switcher
│       └── docs.js          # Docs sidebar active-section tracker
├── benchmark/
│   ├── benchmark.py         # Token comparison runner (requires tiktoken)
│   ├── originals/           # Source Markdown files
│   └── slim/                # Converted SLIM equivalents
├── tests/
│   └── conformance.py       # 85-case conformance test suite
└── generate_report.py       # PDF report generator (requires reportlab)
```

---

## Running the Conformance Tests

```bash
python tests/conformance.py
# Expected output: 85/85 passed — SLIM CONFORMANT
```

---

## Specification

The full language spec is in [`SLIM_SPEC_v1.0.slm`](SLIM_SPEC_v1.0.slm) — a self-describing SLIM file that covers:

- Complete BNF grammar
- Header, Body, Block, and Directive syntax rules
- Variable interpolation semantics
- Schema / `:tool` definitions and type system
- Security model (prompt injection prevention, `@include` sandboxing)
- Reserved keys
- Migration guide from Markdown

---

## License

MIT © 2026 Sasidhar Nagandla  
Made with passion by Sasidhar — https://github.com/nagandla-sasidhar/slim
