"""
benchmark_runner.py — SLIM format benchmark runner.

For each .md file in tests/corpus/generated/ and tests/corpus/scraped/:
  1. Convert with md_to_slm()
  2. Count tokens three ways:
       - original  : raw Markdown input
       - slim_raw  : full SLIM output (includes @header zone)
       - llm_facing: SLIM body only — what the LLM actually receives
  3. Grade savings on LLM-facing reduction (the real API cost benefit)
  4. Analyse problem files (ZERO/WORSE) for surviving Markdown patterns
  5. Write a findings report to tests/corpus/results/findings_YYYYMMDD.md
"""

import os
import re
import sys
import time
import statistics
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Allow running from anywhere by resolving the project root
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent       # tests/
PROJECT_ROOT = SCRIPT_DIR.parent                   # TAML/

# Add tests/ to path so we can import md_to_slm
sys.path.insert(0, str(SCRIPT_DIR))

from md_to_slm import md_to_slm, slim_to_llm_text, estimate_tokens, _ENC  # type: ignore[attr-defined]

CORPUS_DIRS = [
    SCRIPT_DIR / 'corpus' / 'generated',
    SCRIPT_DIR / 'corpus' / 'scraped',
]
RESULTS_DIR = SCRIPT_DIR / 'corpus' / 'results'

# ---------------------------------------------------------------------------
# Grade thresholds (%)
# ---------------------------------------------------------------------------
def grade(pct: float) -> str:
    if pct >= 30:
        return 'GREAT'
    if pct >= 10:
        return 'OK'
    if pct >= 1:
        return 'LOW'
    if pct == 0:
        return 'ZERO'
    return 'WORSE'


# ---------------------------------------------------------------------------
# Pattern detection helpers
# ---------------------------------------------------------------------------

PATTERN_CHECKS = {
    'YAML frontmatter':    lambda t: bool(re.match(r'^---\s*$', t.split('\n')[0])),
    'Code fences':         lambda t: bool(re.search(r'^(`{3,}|~{3,})', t, re.MULTILINE)),
    'Inline bold/italic':  lambda t: bool(re.search(r'\*{1,3}.+?\*{1,3}|_{1,3}.+?_{1,3}', t)),
    'Links':               lambda t: bool(re.search(r'\[[^\]]*\]\([^)]*\)', t)),
    'HTML tags':           lambda t: bool(re.search(r'</?[a-zA-Z][^>]*>', t)),
    'Tables':              lambda t: bool(re.search(r'^\|.+\|$', t, re.MULTILINE)),
    'Setext headings':     lambda t: bool(re.search(r'^[^\n]+\n[=\-]{2,}$', t, re.MULTILINE)),
    'Horizontal rules':    lambda t: bool(re.search(r'^[-*_]{3,}\s*$', t, re.MULTILINE)),
    'Badge images':        lambda t: bool(re.search(r'!\[[^\]]*\]\(https?://[^)]*shield', t)),
}

SURVIVED_CHECKS = {
    'Bold/italic survived':     lambda slm: bool(re.search(r'\*{2,}.+?\*{2,}|_{2,}.+?_{2,}', slm)),
    'Links survived':           lambda slm: bool(re.search(r'\[[^\]]*\]\(https?://[^)]*\)', slm)),
    'HTML tags survived':       lambda slm: bool(re.search(r'</?[a-zA-Z][^>]*>', slm)),
    'Code fence expanded':      lambda slm: bool(re.search(r'^===\s+CODE', slm, re.MULTILINE)),
}


def detect_patterns(original: str) -> list:
    found = []
    for name, fn in PATTERN_CHECKS.items():
        try:
            if fn(original):
                found.append(name)
        except Exception:
            pass
    return found


def detect_survived(slm_output: str) -> list:
    survived = []
    for name, fn in SURVIVED_CHECKS.items():
        try:
            if fn(slm_output):
                survived.append(name)
        except Exception:
            pass
    return survived


# ---------------------------------------------------------------------------
# Main benchmark logic
# ---------------------------------------------------------------------------

def run_benchmark(max_retries: int = 3, retry_wait: int = 30):
    for attempt in range(1, max_retries + 1):
        md_files = []
        for d in CORPUS_DIRS:
            if d.exists():
                md_files.extend(sorted(d.glob('*.md')))
            else:
                print(f'[WARNING] Corpus directory not found: {d}')

        if md_files:
            break

        if attempt < max_retries:
            print(f'[INFO] No corpus files found (attempt {attempt}/{max_retries}). '
                  f'Retrying in {retry_wait}s...')
            time.sleep(retry_wait)
        else:
            print('[ERROR] No corpus .md files found after all retries. Exiting.')
            sys.exit(0)

    print(f'\n[INFO] Found {len(md_files)} corpus file(s).')
    print(f'[INFO] Token counting: {"tiktoken cl100k_base" if _ENC else "char/4 fallback"}')
    print(f'[INFO] Savings measured on LLM-facing text (body only, @headers stripped)\n')

    # ── Per-file processing ─────────────────────────────────────────────────
    rows = []
    problem_files = {}

    for path in md_files:
        original  = path.read_text(encoding='utf-8', errors='replace')
        slim_full = md_to_slm(original)
        llm_text  = slim_to_llm_text(slim_full)

        tok_orig  = estimate_tokens(original)
        tok_slim  = estimate_tokens(slim_full)
        tok_llm   = estimate_tokens(llm_text)

        # Primary metric: how much smaller is the LLM call vs the original?
        saved = tok_orig - tok_llm
        pct   = round(saved / tok_orig * 100, 1) if tok_orig > 0 else 0.0
        g     = grade(pct)

        rows.append({
            'file':      path.name,
            'path':      path,
            'tok_orig':  tok_orig,
            'tok_slim':  tok_slim,
            'tok_llm':   tok_llm,
            'saved':     saved,
            'pct':       pct,
            'grade':     g,
            'original':  original,
            'slim_full': slim_full,
            'llm_text':  llm_text,
        })

        if g in ('ZERO', 'WORSE'):
            patterns_found = detect_patterns(original)
            survived       = detect_survived(slim_full)
            problem_files[path.name] = {
                'pct':      pct,
                'grade':    g,
                'patterns': patterns_found,
                'survived': survived,
                'original': original,
                'converted': slim_full,
            }

    # ── Print table ─────────────────────────────────────────────────────────
    col_file = max(len(r['file']) for r in rows) + 2
    col_file = max(col_file, 30)

    header = (f"{'File':<{col_file}} | {'Orig':>5} | {'SLIM':>5} | "
              f"{'LLM':>5} | {'Saved':>5} | {'%':>6} | Grade")
    sep    = '-' * len(header)

    print(header)
    print(sep)
    for r in rows:
        print(f"{r['file']:<{col_file}} | {r['tok_orig']:>5} | {r['tok_slim']:>5} | "
              f"{r['tok_llm']:>5} | {r['saved']:>5} | {r['pct']:>5.1f}% | {r['grade']}")

    # ── Aggregate stats ──────────────────────────────────────────────────────
    pcts      = [r['pct'] for r in rows]
    avg_pct   = round(sum(pcts) / len(pcts), 1)
    med_pct   = round(statistics.median(pcts), 1)
    target_met = avg_pct >= 30.0

    # Subset averages
    has_yaml_rows  = [r for r in rows if r['original'].lstrip().startswith('---')]
    plain_rows     = [r for r in rows if not r['original'].lstrip().startswith('---')]
    yaml_avg  = round(sum(r['pct'] for r in has_yaml_rows)  / len(has_yaml_rows),  1) if has_yaml_rows  else None
    plain_avg = round(sum(r['pct'] for r in plain_rows) / len(plain_rows), 1) if plain_rows else None

    grade_counts = {'GREAT': 0, 'OK': 0, 'LOW': 0, 'ZERO': 0, 'WORSE': 0}
    for r in rows:
        grade_counts[r['grade']] += 1

    print()
    print(f'Total files:         {len(rows)}')
    print(f'Average savings:     {avg_pct}%  (LLM-facing)')
    print(f'Median savings:      {med_pct}%')
    if yaml_avg is not None:
        print(f'  YAML files ({len(has_yaml_rows):>2}):  {yaml_avg}%  avg')
    if plain_avg is not None:
        print(f'  Plain files ({len(plain_rows):>2}):  {plain_avg}%  avg')
    print(f'Target (>=30%):      {"MET ✓" if target_met else "NOT MET"}')
    print()
    for g_name, cnt in grade_counts.items():
        print(f'  {g_name:<6}: {cnt}')

    # ── Pattern analysis ─────────────────────────────────────────────────────
    pattern_freq = {}
    for info in problem_files.values():
        for p in info['patterns']:
            pattern_freq[p] = pattern_freq.get(p, 0) + 1
        for s in info['survived']:
            key = f'[survived] {s}'
            pattern_freq[key] = pattern_freq.get(key, 0) + 1

    top3 = sorted(pattern_freq.items(), key=lambda x: -x[1])[:3]

    if top3:
        print()
        print('Top problem patterns (ZERO/WORSE files):')
        for name, cnt in top3:
            print(f'  {cnt}x  {name}')

    # ── Write findings report ─────────────────────────────────────────────────
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime('%Y%m%d')
    report_path = RESULTS_DIR / f'findings_{today}.md'

    _write_report(
        path=report_path,
        rows=rows,
        avg_pct=avg_pct,
        med_pct=med_pct,
        yaml_avg=yaml_avg,
        plain_avg=plain_avg,
        has_yaml_count=len(has_yaml_rows),
        plain_count=len(plain_rows),
        target_met=target_met,
        grade_counts=grade_counts,
        problem_files=problem_files,
        pattern_freq=pattern_freq,
        col_file=col_file,
        header=header,
        sep=sep,
    )

    print(f'\n[INFO] Findings report written to: {report_path}')
    return rows, avg_pct, target_met, top3, report_path


def _write_report(*, path, rows, avg_pct, med_pct, yaml_avg, plain_avg,
                  has_yaml_count, plain_count, target_met,
                  grade_counts, problem_files, pattern_freq,
                  col_file, header, sep):
    today_pretty = datetime.now().strftime('%Y-%m-%d')

    lines = []
    lines.append(f'# Benchmark Findings -- {today_pretty}')
    lines.append('')
    lines.append('## Summary')
    lines.append('')
    lines.append(f'- Files tested: {len(rows)}')
    lines.append(f'- **Metric: LLM-facing tokens** (body only — @headers stripped before LLM call)')
    lines.append(f'- Average savings: {avg_pct}%')
    lines.append(f'- Median savings: {med_pct}%')
    if yaml_avg is not None:
        lines.append(f'- YAML-frontmatter files ({has_yaml_count}): {yaml_avg}% avg')
    if plain_avg is not None:
        lines.append(f'- Plain-prose files ({plain_count}): {plain_avg}% avg')
    lines.append(f'- Target (>=30%): **{"MET" if target_met else "NOT MET"}**')
    lines.append(f'- Token counting: {"tiktoken cl100k_base" if _ENC else "char/4 fallback"}')
    lines.append('')
    lines.append('### Grade breakdown')
    lines.append('')
    for g_name, cnt in grade_counts.items():
        lines.append(f'- {g_name}: {cnt}')

    lines.append('')
    lines.append('## Results Table')
    lines.append('')
    lines.append('Columns: Orig = original tokens | SLIM = full SLIM output | '
                 'LLM = what gets sent to the model | Saved = Orig - LLM')
    lines.append('')
    lines.append('```')
    lines.append(header)
    lines.append(sep)
    for r in rows:
        lines.append(
            f"{r['file']:<{col_file}} | {r['tok_orig']:>5} | {r['tok_slim']:>5} | "
            f"{r['tok_llm']:>5} | {r['saved']:>5} | {r['pct']:>5.1f}% | {r['grade']}"
        )
    lines.append('```')

    lines.append('')
    lines.append('## Problem Patterns (files graded ZERO or WORSE)')
    lines.append('')

    if not problem_files:
        lines.append('None -- all files achieved at least 1% savings.')
    else:
        for fname, info in problem_files.items():
            lines.append(f'### {fname}')
            lines.append('')
            lines.append(f'- Grade: {info["grade"]} ({info["pct"]}% savings)')
            if info['patterns']:
                lines.append(f'- Markdown patterns present: {", ".join(info["patterns"])}')
            else:
                lines.append('- No recognizable Markdown patterns detected.')
            if info['survived']:
                lines.append(f'- Patterns surviving conversion: {", ".join(info["survived"])}')
            else:
                lines.append('- No problematic pattern survivals detected.')

            orig_lines = info['original'].split('\n')[:15]
            conv_lines = info['converted'].split('\n')[:15]
            lines.append('')
            lines.append('<details><summary>Original (first 15 lines)</summary>')
            lines.append('')
            lines.append('```markdown')
            lines.extend(orig_lines)
            lines.append('```')
            lines.append('')
            lines.append('</details>')
            lines.append('')
            lines.append('<details><summary>Converted (first 15 lines)</summary>')
            lines.append('')
            lines.append('```')
            lines.extend(conv_lines)
            lines.append('```')
            lines.append('')
            lines.append('</details>')
            lines.append('')

    if pattern_freq:
        lines.append('### Pattern frequency across ZERO/WORSE files')
        lines.append('')
        for name, cnt in sorted(pattern_freq.items(), key=lambda x: -x[1]):
            lines.append(f'- {cnt}x  {name}')
        lines.append('')

    lines.append('## Proposed Fixes')
    lines.append('')

    suggestions = []

    if pattern_freq.get('[survived] Links survived', 0) > 0:
        suggestions.append(
            '**Links surviving in body**: Verify `strip_inline` regex handles all link variants.'
        )
    if pattern_freq.get('[survived] Bold/italic survived', 0) > 0:
        suggestions.append(
            '**Bold/italic surviving**: Ensure `strip_inline` is called on every non-code line.'
        )
    if pattern_freq.get('[survived] HTML tags survived', 0) > 0:
        suggestions.append(
            '**HTML tags surviving**: Regex may miss multi-line or unusual HTML tag forms.'
        )

    plain_zero = sum(
        1 for info in problem_files.values()
        if not info['patterns'] and info['grade'] in ('ZERO', 'WORSE')
    )
    if plain_zero > 0:
        suggestions.append(
            f'**Plain-prose files with zero savings ({plain_zero} files)**: '
            'These files have no Markdown decoration to strip. '
            'Further savings require stripping structural markers (`- ` bullets, `##` headings) '
            'which is a lossy transform — suitable for a future "ultra compact" mode.'
        )

    if not suggestions:
        suggestions.append(
            'No critical failures detected. Focus on expanding coverage of richly-decorated '
            'Markdown files (YAML + bold + links + tables) for the best benchmark numbers.'
        )

    for s in suggestions:
        lines.append(f'1. {s}')
        lines.append('')

    path.write_text('\n'.join(lines), encoding='utf-8')


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    run_benchmark()
