/**
 * SLIM — JavaScript Parser & Converter v1.0
 * Structured LLM Instruction Markup
 *
 * © 2026 Sasidhar Nagandla. MIT License.
 * Made with passion by Sasidhar — https://github.com/slim-format/slim
 */
(function (root, factory) {
  if (typeof module !== 'undefined' && module.exports) module.exports = factory();
  else root.SLIM = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const DIRECTIVE_KEYWORDS = new Set(['CALL','ASSERT','YIELD','EMIT','LOG','ABORT','WAIT','RETRY']);
  const HEADER_KEY_RE  = /^@(\+?)([a-z][a-z0-9_-]*)$/;
  const DIRECTIVE_RE   = /^>\s+([A-Z]+)(.*)$/;
  const BLOCK_OPEN_RE  = /^===\s+([A-Z][A-Z0-9_]*)(?:\s+\[([^\]]+)\])?$/;
  const BLOCK_CLOSE_RE = /^===\s+\/([A-Z][A-Z0-9_]*)$/;

  // Hard limits to prevent resource exhaustion (Finding 6 / DoS guard)
  const MAX_INPUT_CHARS  = 1 * 1024 * 1024; // 1 MB
  const MAX_LINES        = 50_000;
  const MAX_COERCE_DEPTH = 5;

  // ── HTML escape helper (used by highlight) ───────────────────
  function escHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // ── Type coercion ────────────────────────────────────────────
  // depth guard prevents unbounded recursion on deeply nested comma lists
  function coerce(v, _depth) {
    _depth = (_depth || 0);
    if (typeof v !== 'string') return v;
    v = v.trim();
    if (v.length > 1024) return v;                                 // length guard (Finding 12)
    if (v.toLowerCase() === 'true')  return true;
    if (v.toLowerCase() === 'false') return false;
    if (['null','none'].includes(v.toLowerCase())) return null;
    if (/^-?\d+$/.test(v))       return parseInt(v, 10);
    if (/^-?\d+\.\d+$/.test(v))  return parseFloat(v);
    if (v.startsWith('"') && v.endsWith('"')) return v.slice(1, -1);
    if (_depth < MAX_COERCE_DEPTH && v.includes(','))
      return v.split(',').map(p => p.trim()).filter(Boolean).map(p => coerce(p, _depth + 1));
    return v;
  }

  // ── Variable interpolation ───────────────────────────────────
  // Uses hasOwnProperty to avoid prototype chain leakage (Finding 15)
  function interpolate(text, vars) {
    return text.replace(/\$([a-zA-Z][a-zA-Z0-9_]*)(\.[a-zA-Z0-9_.[\]]*)?/g, (m, key, tail) => {
      if (!Object.prototype.hasOwnProperty.call(vars, key)) return m;
      const val = vars[key];
      return (Array.isArray(val) ? val.join(', ') : String(val)) + (tail || '');
    });
  }

  // ── Block extractor ──────────────────────────────────────────
  function extractBlocks(lines, offset) {
    const blocks = Object.create(null), out = [], errors = [];
    let i = 0;
    while (i < lines.length) {
      const stripped = lines[i].trim();
      const mO = BLOCK_OPEN_RE.exec(stripped);
      if (mO) {
        const name = mO[1], typeTag = mO[2] || null, start = offset + i;
        const content = []; i++; let closed = false;
        while (i < lines.length) {
          const inner = lines[i].trim();
          const mC = BLOCK_CLOSE_RE.exec(inner);
          if (mC && mC[1].toUpperCase() === name) { closed = true; break; }
          content.push(lines[i].replace(/\s+$/, ''));
          i++;
        }
        if (!closed) { errors.push({ line: start, message: `Unclosed block: ${name}` }); i++; continue; }
        blocks[name] = {
          name, typeTag, lineStart: start,
          content: content.map(l => l.trim().startsWith('\\===') ? l.replace('\\===', '===') : l).join('\n')
        };
        out.push(`=== ${name}`); i++; continue;
      }
      out.push(lines[i].replace(/\s+$/, '')); i++;
    }
    return { blocks, outLines: out, errors };
  }

  // ── Main parser ──────────────────────────────────────────────
  function parse(text) {
    // Input size guard — prevents memory/CPU exhaustion (Finding 6)
    if (typeof text !== 'string') return _emptyDoc();
    if (text.length > MAX_INPUT_CHARS)
      return _emptyDoc([{ line: 0, message: `Input too large (max ${MAX_INPUT_CHARS / 1024}KB)` }]);

    const lines = text.split('\n');
    if (lines.length > MAX_LINES)
      return _emptyDoc([{ line: 0, message: `Too many lines (max ${MAX_LINES})` }]);

    const errors = [], warnings = [];
    // Object.create(null) severs prototype chain — prevents prototype pollution (Finding 7)
    const headers = Object.create(null), llmHeaders = Object.create(null);
    let i = 0, inHeader = true;

    while (i < lines.length && inHeader) {
      const stripped = lines[i].trim();
      if (stripped === '' || stripped === '---') { i++; continue; }
      const ci = stripped.indexOf(': ');
      const m = HEADER_KEY_RE.exec(ci >= 0 ? stripped.substring(0, ci) : stripped);
      if (m && ci >= 0) {
        const plus = m[1] === '+', key = m[2];
        let val = stripped.substring(ci + 2);
        while (i + 1 < lines.length && lines[i + 1].startsWith('  ')) { i++; val += ' ' + lines[i].trim(); }
        if (plus) llmHeaders[key] = coerce(val);
        else      headers[key]    = coerce(val);
      } else { inHeader = false; continue; }
      i++;
    }

    let bodyLines = lines.slice(i);
    const { blocks, outLines, errors: bErrs } = extractBlocks(bodyLines, i);
    bodyLines = outLines; errors.push(...bErrs);

    const directives = [];
    for (let ln = 0; ln < bodyLines.length; ln++) {
      const m = DIRECTIVE_RE.exec(bodyLines[ln].trim());
      if (m && DIRECTIVE_KEYWORDS.has(m[1]))
        directives.push({ keyword: m[1], args: m[2].trim(), line: i + ln });
    }

    // Merge with Object.assign to a null-prototype object (Finding 7)
    const variables = Object.assign(Object.create(null), headers, llmHeaders);
    return {
      version: String(Object.prototype.hasOwnProperty.call(headers, 'slim') ? headers['slim'] : '1.0'),
      headers, llmHeaders, bodyLines, blocks, directives, variables, errors, warnings,
      toLlmText() {
        const out = [];
        for (const k of Object.keys(llmHeaders)) out.push(`@+${k}: ${llmHeaders[k]}`);
        if (out.length) out.push('');
        for (const l of bodyLines) { if (!l.trim().startsWith('~')) out.push(l); }
        return interpolate(out.join('\n'), variables);
      },
      get tokenEstimate() { return Math.max(1, Math.round(this.toLlmText().length / 4)); }
    };
  }

  function _emptyDoc(errors) {
    const h = Object.create(null), lh = Object.create(null), v = Object.create(null);
    return {
      version: '1.0', headers: h, llmHeaders: lh, bodyLines: [], blocks: Object.create(null),
      directives: [], variables: v, errors: errors || [], warnings: [],
      toLlmText() { return ''; },
      get tokenEstimate() { return 0; }
    };
  }

  // ── Sanitizer ────────────────────────────────────────────────
  function sanitizeUserContent(text) {
    if (typeof text !== 'string') return '';
    text = text.replace(/\\/g, '\\\\');
    for (const s of ['===', '@', '$', '>', '~'])
      text = text.replace(new RegExp(s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), `\\${s}`);
    return text;
  }

  // ── Token estimator (1 token ≈ 4 chars) ─────────────────────
  function estimateTokens(text) {
    if (typeof text !== 'string') return 0;
    return Math.max(1, Math.round(text.length / 4));
  }

  // ── Markdown → SLIM converter ────────────────────────────────
  function mdToSlm(markdown) {
    if (typeof markdown !== 'string') return '@slim: 1.0\n';
    const lines = markdown.split('\n');
    const slmHeaders = ['@slim: 1.0'];
    let i = 0;

    // YAML frontmatter
    if (lines[0] && lines[0].trim() === '---') {
      i = 1;
      while (i < lines.length && lines[i].trim() !== '---') {
        const ci = lines[i].indexOf(':');
        if (ci > 0) {
          const key = lines[i].substring(0, ci).trim().toLowerCase().replace(/[^a-z0-9_-]/g, '_');
          const val = lines[i].substring(ci + 1).trim().replace(/^["']|["']$/g, '');
          if (key && val) slmHeaders.push(`@${key}: ${val}`);
        }
        i++;
      }
      i++;
    }

    const body = [];
    let inCode = false, blockName = '', codeIdx = 0;
    const used = new Set();

    while (i < lines.length) {
      const line = lines[i], t = line.trim();

      if (!inCode && t.startsWith('```')) {
        const lang = t.slice(3).trim();
        const base = (lang || 'CODE').toUpperCase().replace(/[^A-Z0-9_]/g, '_') || 'CODE';
        let name = base; codeIdx++;
        let sfx = 2; while (used.has(name)) name = `${base}_${sfx++}`;
        used.add(name); blockName = name; inCode = true;
        body.push(`=== ${name}` + (lang ? ` [${lang}]` : ''));
        i++; continue;
      }
      if (inCode) {
        if (t === '```') { body.push(`=== /${blockName}`); inCode = false; }
        else body.push(line.replace(/\s+$/, ''));
        i++; continue;
      }
      // Single-line HTML comment
      if (t.startsWith('<!--') && t.endsWith('-->')) {
        const c = t.slice(4, -3).trim();
        if (c) body.push(`~ ${c}`);
        i++; continue;
      }
      // Multi-line HTML comment — skip entire block, no-op
      if (t.startsWith('<!--')) {
        while (i < lines.length && !lines[i].includes('-->')) i++;
        i++; continue;
      }
      body.push(line.replace(/\s+$/, ''));
      i++;
    }

    return slmHeaders.join('\n') + '\n\n' + body.join('\n').trimEnd() + '\n';
  }

  // ── JSON → SLIM converter ────────────────────────────────────
  function jsonToSlm(jsonText) {
    if (typeof jsonText !== 'string') return '@slim: 1.0\n';
    let obj;
    try { obj = JSON.parse(jsonText); }
    catch (e) { return `@slim: 1.0\n\n~ JSON parse error: ${escHtml(String(e.message))}\n`; }

    if (typeof obj !== 'object' || obj === null || Array.isArray(obj))
      return `@slim: 1.0\n\n~ JSON root must be an object\n`;

    const headers = ['@slim: 1.0'];
    const blocks = [];

    // Use Object.keys (not for...in) to avoid prototype chain enumeration (Finding 7)
    for (const key of Object.keys(obj)) {
      // Neutralise __proto__, constructor, toString etc. (Finding 7)
      if (!key || key === '__proto__' || key === 'constructor' || key === 'prototype') continue;
      const safeKey = key.toLowerCase().replace(/[^a-z0-9_-]/g, '_').replace(/^-+|-+$/g, '') || 'key';
      const val = obj[key];
      if (typeof val === 'string' || typeof val === 'number' || typeof val === 'boolean' || val === null) {
        headers.push(`@${safeKey}: ${val}`);
      } else {
        const bName = key.toUpperCase().replace(/[^A-Z0-9_]/g, '_').replace(/^_+|_+$/g, '') || 'BLOCK';
        const content = typeof val === 'object' ? JSON.stringify(val, null, 2) : String(val);
        blocks.push(`=== ${bName} [json]\n${content}\n=== /${bName}`);
      }
    }

    return headers.join('\n') + '\n\n' + blocks.join('\n\n') + '\n';
  }

  // ── SLIM syntax highlighter (returns HTML) ───────────────────
  // All regex replacements use function callbacks — never string $1 back-references
  // This eliminates replacement-string metachar injection (Finding 1)
  function highlight(slmText) {
    if (typeof slmText !== 'string') return '';
    return slmText
      .split('\n')
      .map(line => {
        // HTML-escape the full line first — this is the security boundary
        const esc = escHtml(line);
        const t = line.trim();

        if (t.startsWith('~'))
          return `<span class="sl-comment">${esc}</span>`;

        if (/^@\+[a-z]/.test(t))
          // Function callback: k and p are substrings of esc (already HTML-safe)
          return esc.replace(/^(@\+[a-z][a-z0-9_-]*)(:)/, (_, k, p) =>
            `<span class="sl-llm-key">${k}</span><span class="sl-punct">${p}</span>`);

        if (/^@[a-z]/.test(t))
          return esc.replace(/^(@[a-z][a-z0-9_-]*)(:)/, (_, k, p) =>
            `<span class="sl-key">${k}</span><span class="sl-punct">${p}</span>`);

        if (/^===/.test(t))
          return `<span class="sl-block">${esc}</span>`;

        if (/^>\s+[A-Z]/.test(t))
          return `<span class="sl-directive">${esc}</span>`;

        if (/^#/.test(t))
          return `<span class="sl-heading">${esc}</span>`;

        // Function callback for variable spans — v is a substring of esc
        return esc.replace(/(\$[a-zA-Z][a-zA-Z0-9_]*)/g, (_, v) =>
          `<span class="sl-var">${v}</span>`);
      })
      .join('\n');
  }

  return { parse, mdToSlm, jsonToSlm, sanitizeUserContent, estimateTokens, highlight };
});
