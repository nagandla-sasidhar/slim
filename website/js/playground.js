/**
 * SLIM Playground — UI Logic v1.0
 *
 * © 2026 Sasidhar Nagandla. MIT License.
 * Made with passion by Sasidhar — https://slimformat.org
 */
(function () {
  'use strict';

  // Maximum file size accepted for upload / drag-and-drop (Finding 5)
  const MAX_FILE_BYTES = 1 * 1024 * 1024; // 1 MB

  // Allowed MIME types for drag-and-drop (Finding 11)
  const ALLOWED_MIME_PREFIXES = ['text/', 'application/json', ''];

  // ── State ──────────────────────────────────────────────────
  let currentFormat = 'markdown';
  let debounceTimer = null;
  // Stores the plain-text of the last successful conversion (safe copy for download/copy)
  let lastSlmText   = '';

  // ── DOM refs ───────────────────────────────────────────────
  const inputEl     = document.getElementById('input');
  const outputEl    = document.getElementById('output');
  const outputPre   = document.getElementById('output-pre');
  const beforeTok   = document.getElementById('tok-before');
  const afterTok    = document.getElementById('tok-after');
  const savedTok    = document.getElementById('tok-saved');
  const savedPct    = document.getElementById('tok-pct');
  const statsSaved  = document.getElementById('stats-saved');
  const errorBanner = document.getElementById('error-banner');
  const copyBtn     = document.getElementById('btn-copy');
  const dlBtn       = document.getElementById('btn-download');
  const fileInput   = document.getElementById('file-input');
  const formatBtns  = document.querySelectorAll('.fmt-btn');
  const exampleSel  = document.getElementById('example-select');

  // ── Examples ───────────────────────────────────────────────
  const EXAMPLES = {
    md_agent: {
      label: 'Agent config (Markdown)',
      format: 'markdown',
      text: `---
model: claude-opus-4-7
agent: CodeReviewer
task: PR-942
retry: 3
timeout: 30
---

<!-- Agent system prompt -->
# Role
You are a senior code reviewer assigned to $task.

# Instructions
- Check for security vulnerabilities
- Suggest performance improvements
- Flag any breaking changes
- Be concise and direct

\`\`\`python
def review(diff):
    return analyze(diff, strict=True)
\`\`\`
`
    },
    md_prompt: {
      label: 'Prompt template (Markdown)',
      format: 'markdown',
      text: `---
version: 1.0
author: team-ai
purpose: customer support bot
language: en
---

# System Prompt

You are a helpful customer support assistant for Acme Corp.

## Capabilities
- Answer questions about products and pricing
- Help with order tracking and returns
- Escalate complex issues to human agents

## Tone Guidelines
- Be friendly but professional
- Keep responses concise (under 150 words)
- Always acknowledge the customer's frustration first

## What NOT to do
- Never promise refunds without manager approval
- Never share other customers' data
- Never make up information you don't know
`
    },
    md_readme: {
      label: 'README / docs (Markdown)',
      format: 'markdown',
      text: `# MyLibrary

A fast, lightweight utility library for Node.js.

## Installation

\`\`\`bash
npm install mylibrary
\`\`\`

## Quick Start

\`\`\`javascript
const lib = require('mylibrary');
const result = lib.process({ input: 'hello' });
console.log(result);
\`\`\`

## API Reference

### \`process(options)\`

| Option | Type | Default | Description |
| input  | string | required | The input to process |
| mode   | string | 'fast' | Processing mode |
| debug  | bool | false | Enable debug output |

Returns a Promise that resolves to the processed result.

## License
MIT
`
    },
    json_config: {
      label: 'Config (JSON)',
      format: 'json',
      text: `{
  "model": "claude-opus-4-7",
  "temperature": 0.7,
  "max_tokens": 4096,
  "system_prompt": "You are a helpful assistant.",
  "tools": ["search", "calculator", "code_runner"],
  "retry": 3,
  "timeout": 30
}`
    },
    plain_notes: {
      label: 'Plain text notes',
      format: 'plain',
      text: `Project Meeting Notes — 2024-01-15

Attendees: Alice, Bob, Carol

Decisions Made:
- Migrate to new API by Q2
- Hire two senior engineers
- Deprecate legacy endpoints in March

Action Items:
- Alice: Draft migration plan by Jan 22
- Bob: Review performance benchmarks
- Carol: Update documentation

Next meeting: Jan 22 at 2pm EST
`
    }
  };

  // ── Convert ────────────────────────────────────────────────
  function convert() {
    const input = inputEl.value.trim();
    if (!input) {
      setOutput('', 0, 0);
      clearError();
      return;
    }

    let slmText = '';
    let errors = [];

    try {
      if (currentFormat === 'markdown') {
        slmText = SLIM.mdToSlm(input);
      } else if (currentFormat === 'json') {
        slmText = SLIM.jsonToSlm(input);
      } else {
        slmText = '@slim: 2.0\n\n' + input;
      }

      const doc = SLIM.parse(slmText);
      errors = doc.errors || [];
    } catch (e) {
      // Use textContent-only path — error messages never reach innerHTML (Finding 9)
      showError('Conversion error: ' + String(e.message).slice(0, 200));
      return;
    }

    if (errors.length) {
      // Safe: errorBanner uses textContent (Finding 9)
      showError(errors.map(e => `Line ${e.line}: ${String(e.message).slice(0, 100)}`).join(' · '));
    } else {
      clearError();
    }

    const beforeTokens = SLIM.estimateTokens(input);
    // Measure LLM-facing tokens only — @header zone is stripped by orchestrator before the call.
    // This is the real API cost metric; comparing full SLIM output would understate savings.
    const afterTokens  = SLIM.estimateTokens(SLIM.slimToLlmText(slmText));
    setOutput(slmText, beforeTokens, afterTokens);
  }

  function setOutput(text, before, after) {
    // Store the plain text for copy/download — never used as HTML (Finding 1)
    lastSlmText = text || '';

    if (text) {
      // SLIM.highlight() uses function callbacks and HTML-escapes all content.
      // Setting innerHTML here is safe: highlight() is the sole HTML boundary.
      outputPre.innerHTML = SLIM.highlight(text);
    } else {
      // Static string — no user content involved
      outputPre.innerHTML = '<span class="pl-empty">// converted SLIM will appear here</span>';
    }

    if (before > 0) {
      const saved = Math.max(0, before - after);
      const pct   = Math.round((saved / before) * 100);
      beforeTok.textContent = before.toLocaleString();
      afterTok.textContent  = after.toLocaleString();
      savedTok.textContent  = saved.toLocaleString();
      savedPct.textContent  = pct + '%';
      statsSaved.textContent = pct + '% fewer tokens';
      statsSaved.className   = pct >= 30 ? 'badge-green' : pct >= 10 ? 'badge-yellow' : 'badge-gray';
    } else {
      resetStats();
    }
  }

  function resetStats() {
    beforeTok.textContent = '—';
    afterTok.textContent  = '—';
    savedTok.textContent  = '—';
    savedPct.textContent  = '—';
    statsSaved.textContent = 'paste input to see savings';
    statsSaved.className   = 'badge-gray';
  }

  function showError(msg) {
    // Always textContent — never innerHTML (Finding 9)
    errorBanner.textContent = '⚠ ' + msg;
    errorBanner.style.display = 'block';
  }

  function clearError() {
    errorBanner.style.display = 'none';
  }

  // ── File validation ────────────────────────────────────────
  // Returns an error string or null if valid (Findings 5 & 11)
  function validateFile(file) {
    if (file.size > MAX_FILE_BYTES)
      return `File too large (${Math.round(file.size / 1024)} KB). Maximum is 1 MB.`;
    // Allow text/* and application/json; empty type string = browser couldn't determine
    const mime = file.type || '';
    const allowed = ALLOWED_MIME_PREFIXES.some(p => mime.startsWith(p));
    if (!allowed)
      return `Unsupported file type: ${mime}`;
    return null;
  }

  // ── Copy ───────────────────────────────────────────────────
  copyBtn.addEventListener('click', () => {
    // Use lastSlmText (plain text) — not outputPre.innerText which parses HTML (Finding 1)
    if (!lastSlmText) return;
    navigator.clipboard.writeText(lastSlmText).then(() => {
      copyBtn.textContent = 'Copied!';
      setTimeout(() => { copyBtn.textContent = 'Copy'; }, 1800);
    }).catch(() => {
      showError('Clipboard access denied. Use Ctrl+C on the output.');
    });
  });

  // ── Download ───────────────────────────────────────────────
  dlBtn.addEventListener('click', () => {
    if (!lastSlmText) return;
    const blob = new Blob([lastSlmText], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'output.slm';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(a.href);
  });

  // ── File upload ────────────────────────────────────────────
  document.getElementById('btn-upload').addEventListener('click', () => fileInput.click());

  fileInput.addEventListener('change', e => {
    const file = e.target.files[0];
    if (!file) return;

    // Size + MIME validation (Findings 5 & 11)
    const err = validateFile(file);
    if (err) { showError(err); fileInput.value = ''; return; }

    const ext = file.name.split('.').pop().toLowerCase();
    if (ext === 'json') setFormat('json');
    else if (ext === 'md' || ext === 'markdown') setFormat('markdown');
    else setFormat('plain');

    const reader = new FileReader();
    reader.onload = ev => {
      inputEl.value = ev.target.result;
      convert();
    };
    reader.onerror = () => showError('Failed to read file.');
    reader.readAsText(file);
    fileInput.value = '';
  });

  // ── Drag & drop ────────────────────────────────────────────
  const dropZone = document.getElementById('drop-zone');
  ['dragenter','dragover'].forEach(evt => {
    dropZone.addEventListener(evt, e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
  });
  ['dragleave','drop'].forEach(evt => {
    dropZone.addEventListener(evt, e => { e.preventDefault(); dropZone.classList.remove('drag-over'); });
  });
  dropZone.addEventListener('drop', e => {
    const file = e.dataTransfer.files[0];
    if (!file) return;

    // Size + MIME validation for drag-and-drop (Findings 5 & 11)
    const err = validateFile(file);
    if (err) { showError(err); return; }

    const ext = file.name.split('.').pop().toLowerCase();
    if (ext === 'json') setFormat('json');
    else if (['md','markdown'].includes(ext)) setFormat('markdown');
    else setFormat('plain');

    const reader = new FileReader();
    reader.onload = ev => { inputEl.value = ev.target.result; convert(); };
    reader.onerror = () => showError('Failed to read file.');
    reader.readAsText(file);
  });

  // ── Format selector ────────────────────────────────────────
  function setFormat(fmt) {
    currentFormat = fmt;
    formatBtns.forEach(btn => btn.classList.toggle('active', btn.dataset.fmt === fmt));
  }

  formatBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      setFormat(btn.dataset.fmt);
      convert();
    });
  });

  // ── Examples ──────────────────────────────────────────────
  exampleSel.addEventListener('change', () => {
    const key = exampleSel.value;
    if (!key) return;
    // Only load from the hardcoded EXAMPLES object — no eval/dynamic dispatch
    if (!Object.prototype.hasOwnProperty.call(EXAMPLES, key)) return;
    const ex = EXAMPLES[key];
    setFormat(ex.format);
    inputEl.value = ex.text;
    convert();
    exampleSel.value = '';
  });

  // ── Live typing ────────────────────────────────────────────
  inputEl.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(convert, 280);
  });

  // ── Keyboard shortcut ──────────────────────────────────────
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') convert();
  });

  // ── Help overlay ───────────────────────────────────────────
  const helpClose = document.getElementById('btn-help-close');
  if (helpClose) {
    helpClose.addEventListener('click', () => {
      document.getElementById('help-overlay').style.display = 'none';
    });
  }

  // ── Init ───────────────────────────────────────────────────
  const ex = EXAMPLES['md_agent'];
  setFormat(ex.format);
  inputEl.value = ex.text;
  convert();

})();
