"""
md_to_slm.py — Python port of the JavaScript slim.js mdToSlm converter.

Faithfully mirrors:
  - _stripInline(s)   → strip_inline(s: str) -> str
  - mdToSlm(markdown) → md_to_slm(markdown: str) -> str
  - estimateTokens(t) → estimate_tokens(text: str) -> int

Token estimator uses tiktoken when available, otherwise falls back to
the same char/4 heuristic used in the JS implementation.
"""

import re

# ---------------------------------------------------------------------------
# Token estimator
# ---------------------------------------------------------------------------

try:
    import tiktoken as _tiktoken
    _ENC = _tiktoken.get_encoding("cl100k_base")

    def estimate_tokens(text: str) -> int:
        """Return token count using tiktoken cl100k_base encoding."""
        if not isinstance(text, str):
            return 0
        tokens = _ENC.encode(text)
        return max(1, len(tokens))

except Exception:  # tiktoken not installed or encoding unavailable
    _ENC = None

    def estimate_tokens(text: str) -> int:  # type: ignore[misc]
        """Fallback: 1 token ≈ 4 characters (matches JS estimateTokens)."""
        if not isinstance(text, str):
            return 0
        return max(1, round(len(text) / 4))


# ---------------------------------------------------------------------------
# strip_inline — exact Python port of JS _stripInline
# ---------------------------------------------------------------------------

def strip_inline(s: str) -> str:
    """
    Remove inline Markdown decorators that cost tokens but add no semantic
    value for LLMs. Mirrors JS _stripInline exactly.

    Transformations (in order):
      1. Bold+italic ***text*** / ___text___  → text
      2. Bold         **text** / __text__     → text
      3. Italic       *text*  (guard lone *)  → text
      4. Italic       _text_  (word boundary) → text
      5. Strikethrough ~~text~~               → text
      6. Inline images ![alt](url)            → alt text only
      7. Links [text](url)                    → text
      8. Reference-style links [text][ref]    → text
      9. HTML tags <br/>, <b>, </b>, …       → ''
     10. Collapse multiple spaces, strip ends
    """
    # 1. Bold+italic: ***text*** / ___text___
    s = re.sub(r'\*{3}(.+?)\*{3}', r'\1', s)
    s = re.sub(r'_{3}(.+?)_{3}', r'\1', s)

    # 2. Bold: **text** / __text__
    s = re.sub(r'\*{2}(.+?)\*{2}', r'\1', s)
    s = re.sub(r'_{2}(.+?)_{2}', r'\1', s)

    # 3. Italic: *text* — guard against list bullets (lone * at start)
    #    JS: /(?<!\*)\*(?!\s)([^*\n]+?)(?<!\s)\*(?!\*)/g
    #    Python lookbehind must be fixed-width — (?<!\*) is fine.
    s = re.sub(r'(?<!\*)\*(?!\s)([^*\n]+?)(?<!\s)\*(?!\*)', r'\1', s)

    # 4. Italic: _text_ — only when not inside a word (keeps variable_names safe)
    #    JS: /(?<![a-zA-Z0-9_])_(?!\s)([^_\n]+?)(?<!\s)_(?![a-zA-Z0-9_])/g
    s = re.sub(r'(?<![a-zA-Z0-9_])_(?!\s)([^_\n]+?)(?<!\s)_(?![a-zA-Z0-9_])', r'\1', s)

    # 5. Strikethrough: ~~text~~
    s = re.sub(r'~~(.+?)~~', r'\1', s)

    # 6. Inline images mid-line: ![alt](url) → alt text only
    s = re.sub(r'!\[([^\]]*)\]\([^)]*\)', lambda m: m.group(1), s)

    # 7. Links: [text](url) → text
    s = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', s)

    # 8. Reference-style links: [text][ref] → text
    s = re.sub(r'\[([^\]]*)\]\[[^\]]*\]', r'\1', s)

    # 9. HTML tags: <br />, <b>, </b>, <details>, etc.
    s = re.sub(r'</?[a-zA-Z][^>]*>', '', s)

    # 10. Collapse multiple spaces left by removals, strip ends
    s = re.sub(r'  +', ' ', s).strip()

    return s


# ---------------------------------------------------------------------------
# md_to_slm — exact Python port of JS mdToSlm
# ---------------------------------------------------------------------------

def md_to_slm(markdown: str) -> str:
    """
    Convert Markdown to SLIM format.

    Processing pipeline:
      - YAML front-matter  → @headers
      - Code fences        → kept verbatim (converting would ADD tokens)
      - HTML comments      → ~ comment lines (or stripped if empty)
      - Blank lines        → collapse multiple into one
      - Horizontal rules   → stripped (pure decoration)
      - Setext headings    → converted to ATX style (# / ##)
      - Link ref defs      → stripped (definitions already inlined)
      - Badge image lines  → stripped
      - Table separator    → stripped
      - Table cells        → compacted padding + strip_inline
      - All other lines    → strip_inline applied, preserving indentation
    """
    if not isinstance(markdown, str):
        return ''

    lines = markdown.split('\n')
    # Only emit @slim: 1.0 when source has YAML frontmatter.
    # Plain files have no metadata to convey and pay a pure token penalty for the header.
    has_yaml = bool(lines) and lines[0].strip() == '---'
    slm_headers = ['@slim: 1.0'] if has_yaml else []
    i = 0

    # ── YAML front-matter → @headers ──────────────────────────────
    if lines and lines[0].strip() == '---':
        i = 1
        while i < len(lines) and lines[i].strip() != '---':
            ci = lines[i].find(':')
            if ci > 0:
                key = lines[i][:ci].strip().lower()
                key = re.sub(r'[^a-z0-9_-]', '_', key)
                val = lines[i][ci + 1:].strip().strip('"\'')
                if key and val:
                    slm_headers.append(f'@{key}: {val}')
            i += 1
        i += 1  # skip closing ---

    body = []
    in_code = False
    code_fence = ''

    while i < len(lines):
        raw = lines[i]
        t = raw.strip()

        # ── Code fences: keep verbatim ──────────────────────────────
        if not in_code and re.match(r'^(`{3,}|~{3,})', t):
            in_code = True
            m = re.match(r'^(`+|~+)', t)
            code_fence = m.group(1) if m else '```'
            body.append(raw.rstrip())
            i += 1
            continue

        if in_code:
            if t.startswith(code_fence):
                in_code = False
            body.append(raw.rstrip())
            i += 1
            continue

        # ── HTML comments → ~ or strip ─────────────────────────────
        if t.startswith('<!--') and t.endswith('-->'):
            c = t[4:-3].strip()
            if c:
                body.append(f'~ {c}')
            i += 1
            continue

        if t.startswith('<!--'):
            while i < len(lines) and '-->' not in lines[i]:
                i += 1
            i += 1
            continue

        # ── Blank lines: strip entirely — LLMs parse structure from headings/bullets,
        # not visual whitespace. Removing blank lines is the single biggest token win
        # on plain-prose agent files that have no other Markdown decoration to strip.
        if t == '':
            i += 1
            continue

        # ── Horizontal rules → strip ─────────────────────────────────
        if re.match(r'^[-*_]{3,}\s*$', t):
            i += 1
            continue

        # ── Setext-style headings → ATX style ────────────────────────
        next_t = (lines[i + 1] if i + 1 < len(lines) else '').strip()
        if next_t and re.match(r'^=+$', next_t) and len(t) > 0:
            body.append('# ' + strip_inline(t))
            i += 2
            continue
        if next_t and re.match(r'^-{2,}$', next_t) and len(t) > 0:
            body.append('## ' + strip_inline(t))
            i += 2
            continue

        # ── Link reference definitions → strip ───────────────────────
        if re.match(r'^\[[^\]]+\]:\s*https?://\S+', t):
            i += 1
            continue

        # ── Standalone badge / image lines → strip ────────────────────
        if re.match(r'^!\[[^\]]*\]\([^)]*\)\s*$', t):
            i += 1
            continue

        # ── Table separator rows |---|---| → strip ────────────────────
        if re.match(r'^\|[\s\-:|]+\|$', t) and not re.search(r'[a-zA-Z0-9]', t):
            i += 1
            continue

        # ── Compact table cell padding ────────────────────────────────
        if t.startswith('|') and t.endswith('|'):
            compact = re.sub(r'\|\s+', '| ', t)
            compact = re.sub(r'\s+\|', ' |', compact)
            indent_m = re.match(r'^(\s*)', raw)
            indent = indent_m.group(1) if indent_m else ''
            body.append(indent + strip_inline(compact))
            i += 1
            continue

        # ── List item markers → strip (keeps indent; LLMs infer list structure) ──
        list_m = re.match(r'^(\s*)([-*+])\s+(.*)', raw)
        if list_m:
            content = strip_inline(list_m.group(3))
            if content:
                body.append(list_m.group(1) + content)
            i += 1
            continue

        ordered_m = re.match(r'^(\s*)\d+\.\s+(.*)', raw)
        if ordered_m:
            content = strip_inline(ordered_m.group(2))
            if content:
                body.append(ordered_m.group(1) + content)
            i += 1
            continue

        # ── All other lines: strip inline decorators ─────────────────
        indent_m = re.match(r'^(\s*)', raw)
        indent = indent_m.group(1) if indent_m else ''
        cleaned = strip_inline(t)
        if cleaned:
            body.append(indent + cleaned)
        i += 1

    # Strip trailing blank lines
    while body and body[-1] == '':
        body.pop()

    header_part = '\n'.join(slm_headers) + '\n\n' if slm_headers else ''
    return header_part + '\n'.join(body).rstrip() + '\n'


def slim_to_llm_text(slm: str) -> str:
    """Return only the body zone — what the LLM actually receives.

    Strips the @header zone (orchestrator-only metadata: @slim, @model, etc.).
    The header zone ends at the first blank line; every line in it starts with '@'.
    If there is no header zone, the full text is returned unchanged.
    """
    if not slm:
        return slm
    parts = slm.split('\n\n', 1)
    header_candidate = parts[0]
    if all(ln == '' or ln.startswith('@') for ln in header_candidate.split('\n')):
        return parts[1] if len(parts) > 1 else ''
    return slm


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys

    tests_passed = 0
    tests_failed = 0

    def check(label: str, got, expected):
        global tests_passed, tests_failed
        if got == expected:
            print(f'  PASS  {label}')
            tests_passed += 1
        else:
            print(f'  FAIL  {label}')
            print(f'        expected: {expected!r}')
            print(f'        got:      {got!r}')
            tests_failed += 1

    print('--- strip_inline tests ---')

    # 1. Bold removal
    check('bold **text**', strip_inline('Hello **world**'), 'Hello world')

    # 2. Italic removal (not a list bullet)
    check('italic *text*', strip_inline('This is *great*'), 'This is great')

    # 3. Italic underscore: variable_name must survive
    check('variable_name safe', strip_inline('Use variable_name here'), 'Use variable_name here')

    # 4. Italic underscore: standalone _word_
    check('italic _word_', strip_inline('This is _important_'), 'This is important')

    # 5. Link stripping
    check('link stripped', strip_inline('[MDN](https://developer.mozilla.org)'), 'MDN')

    # 6. Bold+italic combined
    check('bold+italic ***text***', strip_inline('***bold italic*** word'), 'bold italic word')

    # 7. HTML tag stripped
    check('html tag stripped', strip_inline('Line <br/> break'), 'Line break')

    # 8. Strikethrough removed
    check('strikethrough', strip_inline('~~old~~ new'), 'old new')

    # 9. Inline image → alt text
    check('inline image', strip_inline('See ![logo](http://x.com/a.png) here'), 'See logo here')

    # 10. Reference-style link
    check('ref link', strip_inline('[text][ref-id]'), 'text')

    print()
    print('--- md_to_slm tests ---')

    # 1. YAML front-matter converted to @headers
    md1 = '---\ntitle: My Doc\nauthor: Alice\n---\n\n# Hello\n'
    slm1 = md_to_slm(md1)
    check('yaml frontmatter', '@title: My Doc' in slm1 and '@author: Alice' in slm1, True)

    # 2. Code fence preserved verbatim
    md2 = 'Some text\n\n```python\nx = **bold**\n```\n'
    slm2 = md_to_slm(md2)
    check('code fence verbatim', '```python\nx = **bold**\n```' in slm2, True)

    # 3. Horizontal rule stripped
    md3 = 'Before\n\n---\n\nAfter\n'
    slm3 = md_to_slm(md3)
    check('hr stripped', '---' not in slm3.replace('@slim: 1.0', ''), True)

    # 4. Badge image line stripped
    md4 = '# Title\n\n![CI](https://img.shields.io/badge/status-stable-green)\n\nText\n'
    slm4 = md_to_slm(md4)
    check('badge stripped', 'shields.io' not in slm4, True)

    # 5. Setext heading converted to ATX
    md5 = 'My Section\n==========\n\nContent here.\n'
    slm5 = md_to_slm(md5)
    check('setext h1 -> ATX', '# My Section' in slm5, True)

    # 6. No @slim header on plain (no-YAML) file
    md6 = '# Simple Agent\n\n- Do task A\n- Do task B\n'
    slm6 = md_to_slm(md6)
    check('no header on plain file', '@slim' not in slm6, True)

    # 7. Blank lines stripped
    md7 = '# Section\n\n- item 1\n\n- item 2\n\n- item 3\n'
    slm7 = md_to_slm(md7)
    check('blank lines stripped', '\n\n' not in slm7, True)

    # 8. YAML file still gets header
    md8 = '---\nmodel: gpt-4\n---\n\n# Instructions\n\nDo something.\n'
    slm8 = md_to_slm(md8)
    check('yaml file keeps @slim header', '@slim: 1.0' in slm8, True)

    # 9. Unordered bullet markers stripped
    md9 = '# Section\n\n- Do task A\n- Do task B\n'
    slm9 = md_to_slm(md9)
    check('bullet markers stripped', '- Do task A' not in slm9 and 'Do task A' in slm9, True)

    # 10. Nested bullets: indentation preserved, marker stripped
    md10 = '# Section\n\n- Top level\n  - Nested item\n'
    slm10 = md_to_slm(md10)
    check('nested bullet indentation preserved', '  Nested item' in slm10, True)

    # 11. Ordered list markers stripped
    md11 = '1. First step\n2. Second step\n3. Third step\n'
    slm11 = md_to_slm(md11)
    check('ordered list markers stripped', '1. First step' not in slm11 and 'First step' in slm11, True)

    print()
    print('--- estimate_tokens test ---')
    tok = estimate_tokens('Hello world, this is a test string.')
    using = 'tiktoken' if _ENC else 'char/4 fallback'
    check(f'estimate_tokens > 0 (using {using})', tok > 0, True)

    print()
    total = tests_passed + tests_failed
    status = 'ALL PASSED' if tests_failed == 0 else 'SOME FAILED'
    print(f'Results: {tests_passed}/{total} passed -- {status}')
    sys.exit(0 if tests_failed == 0 else 1)
