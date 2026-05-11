"""
SLIM Parser — Reference Implementation v1.0
Structured LLM Instruction Markup

© 2026 Sasidhar Nagandla. MIT License.
Made with passion by Sasidhar — https://slimformat.org

Usage:
    from slim.parser import SLIMParser, ParseMode

    doc = SLIMParser().parse(text)
    llm_input = doc.to_llm_text()   # stripped, interpolated, ready to send
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Enums & Constants
# ---------------------------------------------------------------------------

class ParseMode(Enum):
    STRICT = "strict"
    LENIENT = "lenient"


DIRECTIVE_KEYWORDS = frozenset(
    ["CALL", "ASSERT", "YIELD", "EMIT", "LOG", "ABORT", "WAIT", "RETRY"]
)

RESERVED_HEADER_KEYS = frozenset(
    ["slim", "agent", "model", "mode", "retry", "timeout", "tags", "include", "version"]
)

BLOCK_NAME_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
HEADER_KEY_RE = re.compile(r"^@(\+?)([a-z][a-z0-9_-]*)$")
DIRECTIVE_RE  = re.compile(r"^>\s+([A-Z]+)(.*)$")
VARIABLE_RE   = re.compile(r"\$([a-zA-Z][a-zA-Z0-9_]*)(\.[a-zA-Z0-9_.[\]]*)?")


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class Header:
    key: str
    value: Any
    llm_visible: bool   # True for @+key, False for @key


@dataclass
class Block:
    name: str
    type_tag: str | None
    content: str
    line_start: int


@dataclass
class Directive:
    keyword: str
    args: str
    line: int


@dataclass
class SchemaProperty:
    name: str
    type_str: str
    required: bool
    default: Any | None


@dataclass
class Schema:
    name: str
    desc: str
    properties: list[SchemaProperty]
    returns: list[SchemaProperty]


@dataclass
class ParseError:
    line: int
    message: str


@dataclass
class SLIMDocument:
    version: str
    headers: dict[str, Any]          # @ headers (orchestrator-only)
    llm_headers: dict[str, Any]       # @+ headers (LLM-visible)
    body_lines: list[str]             # raw body lines (post-header)
    blocks: dict[str, Block]          # named blocks
    schemas: dict[str, Schema]        # :tool definitions
    directives: list[Directive]       # > KEYWORD calls
    variables: dict[str, Any]         # all defined variables (@ + @+)
    errors: list[ParseError]
    warnings: list[ParseError]

    def to_llm_text(self) -> str:
        """
        Returns the body text ready to send to the LLM:
        - @+ header lines included
        - @ header lines stripped
        - ~ comment lines stripped
        - $variable references interpolated
        """
        lines = []

        # Include @+ headers as key: value lines
        for key, value in self.llm_headers.items():
            lines.append(f"@+{key}: {value}")

        if self.llm_headers:
            lines.append("")  # blank line separator

        # Process body lines
        for line in self.body_lines:
            stripped = line.strip()
            if stripped.startswith("~"):
                continue  # strip comments
            lines.append(line)

        text = "\n".join(lines)
        return self._interpolate(text)

    def to_full_text(self) -> str:
        """Returns complete body text including all blocks, no stripping."""
        text = "\n".join(self.body_lines)
        return self._interpolate(text)

    def _interpolate(self, text: str) -> str:
        def replace_var(m: re.Match) -> str:
            key = m.group(1)
            tail = m.group(2) or ""
            if key in self.variables:
                val = self.variables[key]
                if isinstance(val, list):
                    return ", ".join(str(v) for v in val) + tail
                return str(val) + tail
            return m.group(0)  # leave unresolved references as-is
        return VARIABLE_RE.sub(replace_var, text)

    @property
    def token_estimate(self) -> int:
        """Rough token count of LLM text (1 token ≈ 4 chars)."""
        return len(self.to_llm_text()) // 4


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

# Hard limits to prevent resource exhaustion (DoS guard)
MAX_INPUT_BYTES = 10 * 1024 * 1024   # 10 MB
MAX_LINES       = 200_000


class SLIMParser:
    def __init__(self, mode: ParseMode = ParseMode.LENIENT, base_dir: Path | None = None):
        self.mode = mode
        self.base_dir = (base_dir or Path(".")).resolve()
        self._include_stack: list[Path] = []

    def parse(self, text: str, source_path: Path | None = None) -> SLIMDocument:
        # Input size guard — prevents memory/CPU exhaustion (Finding 6)
        if not isinstance(text, str):
            raise TypeError("parse() expects a str")
        encoded_len = len(text.encode("utf-8", errors="replace"))
        if encoded_len > MAX_INPUT_BYTES:
            raise ValueError(f"Input too large ({encoded_len} bytes, max {MAX_INPUT_BYTES})")
        lines = text.splitlines()
        if len(lines) > MAX_LINES:
            raise ValueError(f"Too many lines ({len(lines)}, max {MAX_LINES})")
        errors: list[ParseError] = []
        warnings: list[ParseError] = []

        headers: dict[str, Any] = {}
        llm_headers: dict[str, Any] = {}
        body_lines: list[str] = []
        blocks: dict[str, Block] = {}
        schemas: dict[str, Schema] = {}
        directives: list[Directive] = []

        # ---- Phase 1: Parse header zone ----
        i = 0
        in_header = True
        while i < len(lines) and in_header:
            line = lines[i]
            stripped = line.strip()

            if stripped == "" or stripped == "---":
                i += 1
                continue

            m = HEADER_KEY_RE.match(stripped.split(":")[0] if ":" in stripped else stripped)
            if m and ": " in stripped:
                plus = m.group(1) == "+"
                key = m.group(2)
                value_str = stripped[stripped.index(": ") + 2:]

                # Handle multi-line continuation
                while i + 1 < len(lines) and lines[i + 1].startswith("  "):
                    i += 1
                    value_str += " " + lines[i].strip()

                value = self._coerce(value_str)

                if key == "include":
                    included = self._resolve_include(value_str, source_path, errors, warnings)
                    if included:
                        headers.update(included.headers)
                        llm_headers.update(included.llm_headers)
                else:
                    if plus:
                        llm_headers[key] = value
                    else:
                        headers[key] = value
            else:
                in_header = False
                continue

            i += 1

        # ---- Phase 2: Collect body lines ----
        body_lines = lines[i:]

        # ---- Phase 3: Extract blocks ----
        blocks, body_lines, block_errors = self._extract_blocks(body_lines, i)
        errors.extend(block_errors)

        # ---- Phase 4: Extract schemas ----
        schemas, schema_errors = self._extract_schemas(body_lines)
        errors.extend(schema_errors)

        # ---- Phase 5: Extract directives ----
        for ln, line in enumerate(body_lines):
            m = DIRECTIVE_RE.match(line.strip())
            if m:
                kw = m.group(1)
                if kw in DIRECTIVE_KEYWORDS:
                    directives.append(Directive(keyword=kw, args=m.group(2).strip(), line=i + ln))
                # else: not a directive, literal text

        variables = {**headers, **llm_headers}

        return SLIMDocument(
            version=str(headers.get("slim", "1.0")),
            headers=headers,
            llm_headers=llm_headers,
            body_lines=body_lines,
            blocks=blocks,
            schemas=schemas,
            directives=directives,
            variables=variables,
            errors=errors,
            warnings=warnings,
        )

    def parse_file(self, path: str | Path) -> SLIMDocument:
        p = Path(path)
        return self.parse(p.read_text(encoding="utf-8"), source_path=p)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _coerce(self, value: str, _depth: int = 0) -> Any:
        if not isinstance(value, str):
            return value
        v = value.strip()
        # Length guard — prevents ReDoS on pathological inputs (Finding 12)
        if len(v) > 2048:
            return v
        if v.lower() in ("true",):  return True
        if v.lower() in ("false",): return False
        if v.lower() in ("null", "none"): return None
        # Use len() pre-check to avoid regex scanning huge strings (Finding 12)
        if len(v) <= 20 and re.fullmatch(r"-?\d+", v):      return int(v)
        if len(v) <= 30 and re.fullmatch(r"-?\d+\.\d+", v): return float(v)
        if v.startswith('"') and v.endswith('"'): return v[1:-1]
        # Depth guard — prevents unbounded recursion on nested comma lists (Finding 6)
        if _depth < 5 and "," in v:
            parts = [p.strip() for p in v.split(",") if p.strip()]
            return [self._coerce(p, _depth + 1) for p in parts]
        return v

    def _extract_blocks(
        self, lines: list[str], line_offset: int
    ) -> tuple[dict[str, Block], list[str], list[ParseError]]:
        blocks: dict[str, Block] = {}
        out_lines: list[str] = []
        errors: list[ParseError] = []

        BLOCK_OPEN_RE  = re.compile(r"^===\s+([A-Z][A-Z0-9_]*)(?:\s+\[([^\]]+)\])?$")
        BLOCK_CLOSE_RE = re.compile(r"^===\s+/([A-Z][A-Z0-9_]*)$")

        i = 0
        while i < len(lines):
            stripped = lines[i].strip()

            m_open = BLOCK_OPEN_RE.match(stripped)
            if m_open:
                name = m_open.group(1)
                type_tag = m_open.group(2)
                start_line = line_offset + i
                content_lines: list[str] = []
                i += 1

                while i < len(lines):
                    inner = lines[i].strip()
                    m_close = BLOCK_CLOSE_RE.match(inner)
                    if m_close and m_close.group(1).upper() == name.upper():
                        break
                    # Check for unescaped boundary inside block
                    if inner.startswith("===") and not inner.startswith("\\==="):
                        msg = f"Unescaped '===' inside block {name}"
                        if self.mode == ParseMode.STRICT:
                            errors.append(ParseError(line_offset + i, msg))
                        else:
                            errors.append(ParseError(line_offset + i, msg))
                    content_lines.append(lines[i].rstrip())
                    i += 1
                else:
                    errors.append(ParseError(start_line, f"Unclosed block: {name}"))
                    i += 1
                    continue

                # Unescape \=== → === in content
                content = "\n".join(
                    l[1:] if l.strip().startswith("\\===") else l
                    for l in content_lines
                )
                blocks[name] = Block(name=name, type_tag=type_tag, content=content, line_start=start_line)
                out_lines.append(f"=== {name}")   # keep reference in body
                i += 1
                continue

            out_lines.append(lines[i].rstrip())
            i += 1

        return blocks, out_lines, errors

    def _extract_schemas(
        self, lines: list[str]
    ) -> tuple[dict[str, Schema], list[ParseError]]:
        schemas: dict[str, Schema] = {}
        errors: list[ParseError] = []
        i = 0

        while i < len(lines):
            line = lines[i]
            if re.match(r"^:[a-z][a-z0-9_-]*\s*$", line.strip()):
                name = line.strip()[1:]
                desc = ""
                props: list[SchemaProperty] = []
                returns: list[SchemaProperty] = []
                i += 1

                while i < len(lines) and (lines[i].startswith("  ") or lines[i].strip() == ""):
                    pline = lines[i]
                    ps = pline.strip()
                    if not ps or ps.startswith("~"):
                        i += 1
                        continue
                    if ps.startswith("desc:"):
                        desc = ps[5:].strip()
                    elif ps.startswith("->"):
                        ret_str = ps[2:].strip()
                        for part in ret_str.split(","):
                            part = part.strip()
                            if ":" in part:
                                rname, rtype = part.split(":", 1)
                                returns.append(SchemaProperty(
                                    name=rname.strip(), type_str=rtype.strip(),
                                    required=True, default=None
                                ))
                    else:
                        # property: name!: type or name?: type = default
                        m = re.match(r"([a-z_][a-z0-9_]*)([!?]?):\s*(.+)", ps)
                        if m:
                            pname  = m.group(1)
                            suffix = m.group(2)
                            rest   = m.group(3).strip()
                            default = None
                            required = suffix == "!"
                            if "=" in rest and suffix != "!":
                                type_part, default_part = rest.split("=", 1)
                                rest    = type_part.strip()
                                default = self._coerce(default_part.strip())
                            props.append(SchemaProperty(
                                name=pname, type_str=rest,
                                required=required, default=default
                            ))
                    i += 1

                schemas[name] = Schema(name=name, desc=desc, properties=props, returns=returns)
                continue
            i += 1

        return schemas, errors

    def _resolve_include(
        self,
        path_str: str,
        source_path: Path | None,
        errors: list[ParseError],
        warnings: list[ParseError],
    ) -> SLIMDocument | None:
        if len(self._include_stack) >= 5:
            errors.append(ParseError(0, f"Max include depth exceeded: {path_str}"))
            return None

        base = source_path.parent if source_path else self.base_dir
        try:
            target = (base / path_str).resolve()
        except (ValueError, OSError):
            errors.append(ParseError(0, f"Invalid include path: {path_str}"))
            return None

        # Path traversal guard — target must remain inside base_dir (Finding 2)
        allowed_root = self.base_dir.resolve()
        try:
            target.relative_to(allowed_root)
        except ValueError:
            errors.append(ParseError(0, f"Include path escapes base directory: {path_str}"))
            return None

        if target in self._include_stack:
            errors.append(ParseError(0, f"Circular include detected: {path_str}"))
            return None
        if not target.exists():
            warnings.append(ParseError(0, f"Include not found: {path_str}"))
            return None
        if not target.is_file():
            errors.append(ParseError(0, f"Include path is not a file: {path_str}"))
            return None

        self._include_stack.append(target)
        doc = self.parse(target.read_text(encoding="utf-8"), source_path=target)
        self._include_stack.pop()
        return doc


# ---------------------------------------------------------------------------
# Sanitizer
# ---------------------------------------------------------------------------

def sanitize_user_content(text: str) -> str:
    """
    Escape SLIM sigils in user-provided strings before embedding in a SLIM file.
    Prevents header injection, block injection, directive injection.
    """
    text = text.replace("\\", "\\\\")
    for sigil in ["===", "@", "$", ">", "~"]:
        text = text.replace(sigil, f"\\{sigil}")
    return text


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python parser.py <file.slm> [--strict] [--llm]")
        sys.exit(1)

    path = sys.argv[1]
    strict = "--strict" in sys.argv
    llm_only = "--llm" in sys.argv
    mode = ParseMode.STRICT if strict else ParseMode.LENIENT

    doc = SLIMParser(mode=mode).parse_file(path)

    if doc.errors:
        print("ERRORS:")
        for e in doc.errors:
            print(f"  Line {e.line}: {e.message}")
        if strict:
            sys.exit(1)

    if doc.warnings:
        print("WARNINGS:")
        for w in doc.warnings:
            print(f"  Line {w.line}: {w.message}")

    if llm_only:
        print(doc.to_llm_text())
    else:
        print(f"Version  : {doc.version}")
        print(f"Headers  : {json.dumps(doc.headers, default=str)}")
        print(f"LLM Hdrs : {json.dumps(doc.llm_headers, default=str)}")
        print(f"Blocks   : {list(doc.blocks.keys())}")
        print(f"Schemas  : {list(doc.schemas.keys())}")
        print(f"Directives: {[(d.keyword, d.args) for d in doc.directives]}")
        print(f"~Token est: {doc.token_estimate}")
        print()
        print("--- LLM TEXT ---")
        print(doc.to_llm_text())
