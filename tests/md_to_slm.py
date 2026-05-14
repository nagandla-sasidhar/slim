"""
md_to_slm.py — Python reference converter: Markdown → SLIM v2.

Faithfully mirrors the JavaScript slim.js mdToSlm converter.

Public API:
  strip_inline(s)             → remove Markdown formatting markers
  md_to_slm(markdown)         → convert Markdown string to SLIM v2
  slim_to_llm_text(slm)       → strip @header zone; return LLM-facing text
  sanitize_user_content(s)    → escape SLIM control chars in user-provided strings
  estimate_tokens(text)       → approximate token count (tiktoken or char/4)
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
        return max(1, len(_ENC.encode(text)))

except Exception:
    _ENC = None

    def estimate_tokens(text: str) -> int:  # type: ignore[misc]
        """Fallback: 1 token ≈ 4 characters (matches JS estimateTokens)."""
        if not isinstance(text, str):
            return 0
        return max(1, round(len(text) / 4))


# ---------------------------------------------------------------------------
# strip_inline
# ---------------------------------------------------------------------------

def strip_inline(s: str) -> str:
    """Remove inline Markdown decorators that cost tokens but add no LLM value."""
    s = re.sub(r'\*{3}(.+?)\*{3}', r'\1', s)
    s = re.sub(r'_{3}(.+?)_{3}', r'\1', s)
    s = re.sub(r'\*{2}(.+?)\*{2}', r'\1', s)
    s = re.sub(r'_{2}(.+?)_{2}', r'\1', s)
    s = re.sub(r'(?<!\*)\*(?!\s)([^*\n]+?)(?<!\s)\*(?!\*)', r'\1', s)
    s = re.sub(r'(?<![a-zA-Z0-9_])_(?!\s)([^_\n]+?)(?<!\s)_(?![a-zA-Z0-9_])', r'\1', s)
    s = re.sub(r'~~(.+?)~~', r'\1', s)
    s = re.sub(r'!\[([^\]]*)\]\([^)]*\)', lambda m: m.group(1), s)
    s = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', s)
    s = re.sub(r'\[([^\]]*)\]\[[^\]]*\]', r'\1', s)
    s = re.sub(r'</?[a-zA-Z][^>]*>', '', s)
    s = re.sub(r'  +', ' ', s).strip()
    return s


# ---------------------------------------------------------------------------
# md_to_slm
# ---------------------------------------------------------------------------

def md_to_slm(markdown: str) -> str:
    """Convert Markdown to SLIM v2 format.

    Key transformations:
      YAML front-matter  → @key: value headers
      Code fences        → ::CODE_N type sections (verbatim, no close tag)
      HTML comments      → ~ comment lines
      Horizontal rules   → stripped (pure decoration)
      Setext headings    → ATX style (# / ##)
      Table separators   → stripped
      List markers       → stripped (indent preserved)
      Inline formatting  → stripped via strip_inline
      Blank lines        → stripped (LLMs parse structure from headings)
    """
    if not isinstance(markdown, str):
        return ''

    lines = markdown.split('\n')
    has_yaml = bool(lines) and lines[0].strip() == '---'
    slm_headers = ['@slim: 2.0'] if has_yaml else []
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
    code_count = 0

    while i < len(lines):
        raw = lines[i]
        t = raw.strip()

        # ── Code fences → ::CODE_N type (verbatim, no close tag) ──────
        if re.match(r'^(`{3,}|~{3,})', t):
            m = re.match(r'^(`+|~+)(.*)', t)
            fence = m.group(1) if m else '```'
            lang = m.group(2).strip() if m else ''
            code_count += 1
            sec_name = f'CODE_{code_count}'
            body.append(f'::{sec_name}' + (f' {lang}' if lang else ' raw'))
            i += 1
            while i < len(lines):
                inner = lines[i]
                inner_t = inner.strip()
                if inner_t.startswith(fence):
                    i += 1
                    break
                # Escape :: at line start inside verbatim content
                line = ('\\' + inner if re.match(r'^::', inner) else inner)
                body.append(line.rstrip())
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

        # ── Blank lines → strip ──────────────────────────────────────
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
            indent = re.match(r'^(\s*)', raw).group(1)
            body.append(indent + strip_inline(compact))
            i += 1
            continue

        # ── List item markers → strip (indent preserved) ──────────────
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
        indent = re.match(r'^(\s*)', raw).group(1)
        cleaned = strip_inline(t)
        if cleaned:
            body.append(indent + cleaned)
        i += 1

    while body and body[-1] == '':
        body.pop()

    header_part = '\n'.join(slm_headers) + '\n\n' if slm_headers else ''
    return header_part + '\n'.join(body).rstrip() + '\n'


# ---------------------------------------------------------------------------
# slim_to_llm_text
# ---------------------------------------------------------------------------

def slim_to_llm_text(slm: str) -> str:
    """Return only the content zone — what the LLM actually receives.

    Strips the @header zone (orchestrator-only metadata).
    The header zone ends at the first blank line when every preceding line
    starts with '@'. Returns the full string unchanged if no header zone found.
    """
    if not slm:
        return slm
    parts = slm.split('\n\n', 1)
    header_candidate = parts[0]
    if all(ln == '' or ln.startswith('@') for ln in header_candidate.split('\n')):
        return parts[1] if len(parts) > 1 else ''
    return slm


# ---------------------------------------------------------------------------
# sanitize_user_content
# ---------------------------------------------------------------------------

def sanitize_user_content(s: str) -> str:
    """Escape SLIM v2 control characters in user-provided strings.

    Safe to embed in any SLIM section. Escapes:
      @  $  >  ~  anywhere in the string
      ::  only at the start of a line (mid-line :: is safe)
    """
    if not isinstance(s, str):
        return ''
    s = s.replace('\\', '\\\\')
    for ch in ['@', '$', '>', '~']:
        s = s.replace(ch, '\\' + ch)
    lines = s.split('\n')
    lines = ['\\' + line if line.startswith('::') else line for line in lines]
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Self-tests  (25 cases)
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

    check('bold **text**',          strip_inline('Hello **world**'),                      'Hello world')
    check('italic *text*',          strip_inline('This is *great*'),                      'This is great')
    check('variable_name safe',     strip_inline('Use variable_name here'),               'Use variable_name here')
    check('italic _word_',          strip_inline('This is _important_'),                  'This is important')
    check('link stripped',          strip_inline('[MDN](https://developer.mozilla.org)'), 'MDN')
    check('bold+italic ***text***', strip_inline('***bold italic*** word'),               'bold italic word')
    check('html tag stripped',      strip_inline('Line <br/> break'),                     'Line break')
    check('strikethrough',          strip_inline('~~old~~ new'),                          'old new')
    check('inline image',           strip_inline('See ![logo](http://x.com/a.png) here'), 'See logo here')
    check('ref link',               strip_inline('[text][ref-id]'),                       'text')

    print()
    print('--- md_to_slm tests ---')

    # 1. YAML front-matter converted to @headers
    md1 = '---\ntitle: My Doc\nauthor: Alice\n---\n\n# Hello\n'
    slm1 = md_to_slm(md1)
    check('yaml frontmatter', '@title: My Doc' in slm1 and '@author: Alice' in slm1, True)

    # 2. Code fence → ::CODE_1 section (verbatim — bold NOT stripped inside)
    md2 = 'Some text\n\n```python\nx = **bold**\n```\n'
    slm2 = md_to_slm(md2)
    check('code fence -> v2 section', '::CODE_1 python' in slm2 and 'x = **bold**' in slm2, True)

    # 3. Horizontal rule stripped
    md3 = 'Before\n\n---\n\nAfter\n'
    slm3 = md_to_slm(md3)
    check('hr stripped', '---' not in slm3, True)

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

    # 8. YAML file gets @slim: 2.0 header
    md8 = '---\nmodel: gpt-4\n---\n\n# Instructions\n\nDo something.\n'
    slm8 = md_to_slm(md8)
    check('yaml file gets @slim: 2.0', '@slim: 2.0' in slm8, True)

    # 9. Unordered bullet markers stripped
    md9 = '# Section\n\n- Do task A\n- Do task B\n'
    slm9 = md_to_slm(md9)
    check('bullet markers stripped', '- Do task A' not in slm9 and 'Do task A' in slm9, True)

    # 10. Nested bullets: indentation preserved, marker stripped
    md10 = '# Section\n\n- Top level\n  - Nested item\n'
    slm10 = md_to_slm(md10)
    check('nested bullet indent preserved', '  Nested item' in slm10, True)

    # 11. Ordered list markers stripped
    md11 = '1. First step\n2. Second step\n3. Third step\n'
    slm11 = md_to_slm(md11)
    check('ordered list markers stripped', '1. First step' not in slm11 and 'First step' in slm11, True)

    # 12. Multiple code blocks get sequential section names
    md12 = '```python\nfoo()\n```\n\nSome text\n\n```js\nbar()\n```\n'
    slm12 = md_to_slm(md12)
    check('multiple code blocks sequential names',
          '::CODE_1 python' in slm12 and '::CODE_2 js' in slm12, True)

    # 13. Code fence with no language gets raw type
    md13 = '```\nplain content\n```\n'
    slm13 = md_to_slm(md13)
    check('no-lang fence gets raw type', '::CODE_1 raw' in slm13, True)

    print()
    print('--- sanitize_user_content tests ---')

    # 14. :: at line start is escaped
    check(':: at line start escaped',
          sanitize_user_content('::inject section'), '\\::inject section')

    # 15. Mid-line :: is NOT escaped
    check('mid-line :: not escaped',
          sanitize_user_content('Use :: for namespaces'), 'Use :: for namespaces')

    # 16. @ and $ are escaped everywhere
    s16 = sanitize_user_content('@model: evil\n$var injection')
    check('@ and $ escaped', '\\@model' in s16 and '\\$var' in s16, True)

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
