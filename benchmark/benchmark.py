"""
SLIM Token Benchmark
Compares token counts between original Markdown files and their SLIM equivalents.
Tokenizer: cl100k_base (GPT-4 / Claude approximate)
"""

import tiktoken
import os
from pathlib import Path

enc = tiktoken.get_encoding("cl100k_base")

ORIGINALS = Path("originals")
SLIM_DIR = Path("slim")

PAIRS = [
    ("01-claude-md.md",          "01-claude-md.slm",          "CLAUDE.md (project doc)"),
    ("02-find-skills.md",        "02-find-skills.slm",        "SKILL.md — find-skills"),
    ("03-pptx-skill.md",         "03-pptx-skill.slm",         "SKILL.md — pptx (complex)"),
    ("04-claude-setup-audit.md", "04-claude-setup-audit.slm", "SKILL.md — claude-setup-audit"),
    ("05-codemie-catchup.md",    "05-codemie-catchup.slm",    "Command — codemie-catchup"),
    ("06-roadmap.md",            "06-roadmap.slm",            "ROADMAP.md (business doc)"),
]

def count_tokens(path):
    text = Path(path).read_text(encoding="utf-8")
    return len(enc.encode(text)), len(text)

def count_stripped_tokens(path):
    """Count SLIM tokens with @ headers stripped (orchestrator-only, never sent to LLM)."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    in_header = True
    filtered = []
    for line in lines:
        if in_header:
            if line.startswith("@+") or line.startswith("---"):
                filtered.append(line)  # @+ lines stay
            elif line.startswith("@"):
                pass  # strip pure @ headers
            elif line.strip() == "" or line.startswith("#"):
                in_header = False
                filtered.append(line)
            else:
                in_header = False
                filtered.append(line)
        else:
            filtered.append(line)
    # Also strip ~ comment lines anywhere in file
    filtered = [l for l in filtered if not l.strip().startswith("~")]
    text = "\n".join(filtered)
    return len(enc.encode(text)), len(text)

print("=" * 90)
print(f"{'Document':<40} {'MD tokens':>10} {'SLIM tokens':>12} {'SLIM stripped':>14} {'Saved%':>8}")
print("=" * 90)

total_md = 0
total_slim = 0
total_stripped = 0

for md_file, slm_file, label in PAIRS:
    md_path = ORIGINALS / md_file
    slm_path = SLIM_DIR / slm_file

    if not md_path.exists() or not slm_path.exists():
        print(f"  MISSING: {md_file} or {slm_file}")
        continue

    md_tokens, md_chars = count_tokens(md_path)
    slm_tokens, slm_chars = count_tokens(slm_path)
    stripped_tokens, stripped_chars = count_stripped_tokens(slm_path)

    pct_full = round((1 - slm_tokens / md_tokens) * 100, 1)
    pct_stripped = round((1 - stripped_tokens / md_tokens) * 100, 1)

    total_md += md_tokens
    total_slim += slm_tokens
    total_stripped += stripped_tokens

    print(f"  {label:<38} {md_tokens:>10,} {slm_tokens:>12,} {stripped_tokens:>14,} {pct_stripped:>7.1f}%")

print("-" * 90)
avg_full_pct = round((1 - total_slim / total_md) * 100, 1)
avg_stripped_pct = round((1 - total_stripped / total_md) * 100, 1)
print(f"  {'TOTAL':<38} {total_md:>10,} {total_slim:>12,} {total_stripped:>14,} {avg_stripped_pct:>7.1f}%")
print("=" * 90)
print(f"\n  Tokenizer: cl100k_base (GPT-4 / Claude approximate)")
print(f"  'SLIM stripped' = @ headers removed (never sent to LLM) + ~ comments removed")
print(f"  Average saving vs Markdown: {avg_full_pct}% (full SLIM) | {avg_stripped_pct}% (SLIM stripped)")
print()

# Per-file detail
print("\nDETAILED BREAKDOWN:")
print("-" * 90)
for md_file, slm_file, label in PAIRS:
    md_path = ORIGINALS / md_file
    slm_path = SLIM_DIR / slm_file
    if not md_path.exists() or not slm_path.exists():
        continue
    md_tokens, md_chars = count_tokens(md_path)
    slm_tokens, slm_chars = count_tokens(slm_path)
    stripped_tokens, _ = count_stripped_tokens(slm_path)
    print(f"\n  {label}")
    print(f"    Original MD  : {md_tokens:,} tokens  ({md_chars:,} chars)")
    print(f"    SLIM full    : {slm_tokens:,} tokens  ({slm_chars:,} chars)  [{round((1-slm_tokens/md_tokens)*100,1)}% saved]")
    print(f"    SLIM stripped: {stripped_tokens:,} tokens  [{round((1-stripped_tokens/md_tokens)*100,1)}% saved vs MD]")
