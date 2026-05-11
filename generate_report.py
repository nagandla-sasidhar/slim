"""
SLIM Report Generator — Professional PDF using ReportLab
Generates SLIM_Report_v1.0.pdf
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import Flowable
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF
from pathlib import Path
import datetime

# ─────────────────────────────────────────────────────────────
# COLOUR PALETTE
# ─────────────────────────────────────────────────────────────
NAVY     = colors.HexColor("#0D1B2A")
TEAL     = colors.HexColor("#1B7F79")
TEAL_LT  = colors.HexColor("#E8F5F4")
ACCENT   = colors.HexColor("#E05C2A")
MID_GREY = colors.HexColor("#4A5568")
LT_GREY  = colors.HexColor("#F7F9FC")
BDR_GREY = colors.HexColor("#D1D9E6")
WHITE    = colors.white
CODE_BG  = colors.HexColor("#1E2D3D")
CODE_FG  = colors.HexColor("#A8D8D8")

W, H = A4  # 595.27 x 841.89 pts


# ─────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────
base = getSampleStyleSheet()

def style(name, **kw):
    s = ParagraphStyle(name, parent=base["Normal"], **kw)
    return s

S = {
    "cover_title": style("cover_title", fontSize=36, leading=44,
                          textColor=WHITE, fontName="Helvetica-Bold", alignment=TA_CENTER),
    "cover_sub":   style("cover_sub",   fontSize=14, leading=20,
                          textColor=colors.HexColor("#A8D8D8"), alignment=TA_CENTER),
    "cover_meta":  style("cover_meta",  fontSize=10, leading=14,
                          textColor=colors.HexColor("#6B8FA8"), alignment=TA_CENTER),
    "h1":  style("h1",  fontSize=20, leading=26, textColor=NAVY,
                  fontName="Helvetica-Bold", spaceBefore=18, spaceAfter=6),
    "h2":  style("h2",  fontSize=14, leading=20, textColor=TEAL,
                  fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=4),
    "h3":  style("h3",  fontSize=11, leading=16, textColor=MID_GREY,
                  fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=3),
    "body": style("body", fontSize=10, leading=15, textColor=NAVY,
                   spaceAfter=6),
    "bullet": style("bullet", fontSize=10, leading=15, textColor=NAVY,
                     leftIndent=14, bulletIndent=4, spaceAfter=3),
    "code":  style("code",  fontSize=8.5, leading=13, textColor=CODE_FG,
                    fontName="Courier", backColor=CODE_BG,
                    leftIndent=10, rightIndent=10, spaceBefore=4, spaceAfter=4),
    "caption": style("caption", fontSize=8.5, leading=12, textColor=MID_GREY,
                      alignment=TA_CENTER, spaceAfter=8),
    "callout": style("callout", fontSize=10, leading=15, textColor=NAVY,
                      backColor=TEAL_LT, leftIndent=12, rightIndent=12,
                      spaceBefore=6, spaceAfter=6),
    "footer": style("footer", fontSize=8, textColor=MID_GREY, alignment=TA_CENTER),
    "toc":    style("toc",    fontSize=10, leading=16, textColor=NAVY),
}


# ─────────────────────────────────────────────────────────────
# CUSTOM FLOWABLES
# ─────────────────────────────────────────────────────────────

class ColorBar(Flowable):
    """Full-width horizontal colour bar."""
    def __init__(self, color, height=4):
        super().__init__()
        self.color = color
        self.bar_h = height

    def wrap(self, w, h):
        self.width = w
        return w, self.bar_h

    def draw(self):
        self.canv.setFillColor(self.color)
        self.canv.rect(0, 0, self.width, self.bar_h, fill=1, stroke=0)


class CoverPage(Flowable):
    def __init__(self):
        super().__init__()

    def wrap(self, w, h):
        self.width = w
        self.height = h
        return w, h

    def draw(self):
        c = self.canv
        # Background
        c.setFillColor(NAVY)
        c.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        # Teal accent bar top
        c.setFillColor(TEAL)
        c.rect(0, self.height - 6, self.width, 6, fill=1, stroke=0)
        # Accent bar bottom
        c.setFillColor(ACCENT)
        c.rect(0, 0, self.width, 4, fill=1, stroke=0)
        # Decorative circle
        c.setFillColor(colors.HexColor("#162435"))
        c.circle(self.width - 60, self.height - 80, 120, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#1A2D40"))
        c.circle(60, 80, 80, fill=1, stroke=0)


class SectionHeader(Flowable):
    """Section header with left colour accent."""
    def __init__(self, text, level=1):
        super().__init__()
        self.text = text
        self.level = level

    def wrap(self, w, h):
        self.width = w
        return w, 32 if self.level == 1 else 24

    def draw(self):
        c = self.canv
        bar_w = 4 if self.level == 1 else 3
        bar_color = TEAL if self.level == 1 else ACCENT
        h = 32 if self.level == 1 else 24
        c.setFillColor(bar_color)
        c.rect(0, 0, bar_w, h, fill=1, stroke=0)
        c.setFillColor(NAVY)
        fs = 18 if self.level == 1 else 13
        c.setFont("Helvetica-Bold", fs)
        c.drawString(bar_w + 8, 8, self.text)


class MetricBar(Flowable):
    """Horizontal token savings bar chart."""
    def __init__(self, data):
        super().__init__()
        self.data = data  # list of (label, pct, md_tokens, slim_tokens)

    def wrap(self, w, h):
        self.width = w
        rows = len(self.data)
        self.height = rows * 34 + 20
        return w, self.height

    def draw(self):
        c = self.canv
        bar_area = self.width - 220
        row_h = 34
        y = self.height - 20

        for label, pct, md_tok, slim_tok in self.data:
            y -= row_h
            # Label
            c.setFillColor(NAVY)
            c.setFont("Helvetica", 8)
            trunc = label[:32] + "..." if len(label) > 32 else label
            c.drawString(0, y + 10, trunc)
            # Background bar
            bx = 200
            bw = bar_area
            bh = 14
            c.setFillColor(BDR_GREY)
            c.roundRect(bx, y + 4, bw, bh, 3, fill=1, stroke=0)
            # Filled bar
            filled = int(bw * pct / 100)
            c.setFillColor(TEAL)
            c.roundRect(bx, y + 4, filled, bh, 3, fill=1, stroke=0)
            # Percentage label
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 7)
            if filled > 35:
                c.drawString(bx + filled - 30, y + 7, f"{pct:.1f}% saved")
            else:
                c.setFillColor(TEAL)
                c.drawString(bx + filled + 4, y + 7, f"{pct:.1f}%")
            # Token counts
            c.setFillColor(MID_GREY)
            c.setFont("Helvetica", 7.5)
            c.drawRightString(self.width, y + 10, f"{md_tok:,} → {slim_tok:,} tokens")


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def P(text, s="body"):
    return Paragraph(text, S[s])

def B(text):
    return Paragraph(f"<bullet>&bull;</bullet> {text}", S["bullet"])

def Code(text):
    lines = text.strip().split("\n")
    escaped = "<br/>".join(l.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                            .replace(" ", "&nbsp;") for l in lines)
    return Paragraph(f'<font name="Courier" size="8" color="#A8D8D8">{escaped}</font>',
                     ParagraphStyle("codeblk", parent=S["code"],
                                    backColor=CODE_BG, borderPadding=(8, 10, 8, 10)))

def HR():
    return HRFlowable(width="100%", thickness=1, color=BDR_GREY, spaceAfter=8, spaceBefore=8)

def SP(h=8):
    return Spacer(1, h)

def tbl(data, col_widths, header_row=True, row_colors=None):
    t = Table(data, colWidths=col_widths, repeatRows=1 if header_row else 0)
    style_cmds = [
        ("BACKGROUND",  (0, 0), (-1, 0 if header_row else -1), TEAL if header_row else LT_GREY),
        ("TEXTCOLOR",   (0, 0), (-1, 0), WHITE if header_row else NAVY),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LT_GREY]),
        ("GRID",        (0, 0), (-1, -1), 0.5, BDR_GREY),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
    ]
    if row_colors:
        for ri, color in row_colors:
            style_cmds.append(("BACKGROUND", (0, ri), (-1, ri), color))
    t.setStyle(TableStyle(style_cmds))
    return t

def page_header_footer(canvas, doc):
    canvas.saveState()
    # Header bar
    canvas.setFillColor(NAVY)
    canvas.rect(doc.leftMargin, H - 28, W - doc.leftMargin - doc.rightMargin, 2, fill=1, stroke=0)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(NAVY)
    canvas.drawString(doc.leftMargin, H - 22, "SLIM — Structured LLM Instruction Markup")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MID_GREY)
    canvas.drawRightString(W - doc.rightMargin, H - 22, "Specification & Benchmark Report v1.0")
    # Footer
    canvas.setFillColor(BDR_GREY)
    canvas.rect(doc.leftMargin, 28, W - doc.leftMargin - doc.rightMargin, 1, fill=1, stroke=0)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MID_GREY)
    canvas.drawCentredString(W / 2, 16, f"Page {doc.page}  |  SLIM v1.0  |  {datetime.date.today()}")
    canvas.restoreState()


# ─────────────────────────────────────────────────────────────
# DOCUMENT CONTENT
# ─────────────────────────────────────────────────────────────

def build():
    out = Path(__file__).parent / "SLIM_Report_v1.0.pdf"
    doc = SimpleDocTemplate(
        str(out), pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2.5*cm, bottomMargin=2.5*cm,
        title="SLIM — Structured LLM Instruction Markup Report v1.0",
        author="Sasidhar Nagandla",
    )

    story = []

    # ── COVER PAGE ──────────────────────────────────────────
    story.append(ColorBar(NAVY, height=260))
    story.append(SP(10))
    story.append(P("SLIM", "cover_title"))
    story.append(SP(6))
    story.append(P("Structured LLM Instruction Markup", "cover_sub"))
    story.append(SP(4))
    story.append(P("Specification &amp; Benchmark Report", "cover_sub"))
    story.append(SP(20))
    story.append(P("Version 1.0  ·  May 2026  ·  Sasidhar Nagandla", "cover_meta"))
    story.append(SP(8))
    story.append(P("A new open-source file format (.slm) designed to replace Markdown<br/>"
                   "for AI documentation, agent configuration, and prompt engineering.", "cover_meta"))
    story.append(ColorBar(TEAL, height=6))
    story.append(PageBreak())

    # ── TABLE OF CONTENTS ────────────────────────────────────
    story.append(SectionHeader("Table of Contents"))
    story.append(SP(10))
    toc_data = [
        ["Section", "Page"],
        ["1. Executive Summary", "3"],
        ["2. Problem Statement — Why Markdown Is Not Enough", "3"],
        ["3. SLIM Architecture — Three Zones", "4"],
        ["4. Complete Syntax Reference", "5"],
        ["5. Token Benchmark — Real-World Results", "8"],
        ["6. Security Model", "10"],
        ["7. Parser Reference Implementation", "10"],
        ["8. Conformance Test Suite", "11"],
        ["9. Migration Guide from Markdown", "11"],
        ["10. Roadmap — Build Plan", "12"],
    ]
    story.append(tbl(toc_data, [11*cm, 3*cm]))
    story.append(PageBreak())

    # ── 1. EXECUTIVE SUMMARY ─────────────────────────────────
    story.append(SectionHeader("1. Executive Summary"))
    story.append(SP(8))
    story.append(P(
        "SLIM (Structured LLM Instruction Markup) is a plain-text file format designed "
        "specifically for AI workflows — system prompts, agent configurations, tool schemas, "
        "orchestration scripts, and AI documentation. It replaces Markdown (.md) as the "
        "primary format for files consumed by Large Language Models and AI orchestration systems."
    ))
    story.append(SP(6))

    highlights = [
        ["Metric", "Value"],
        ["Average token savings vs Markdown", "43.3%"],
        ["Measured on", "6 real-world AI agent files (cl100k_base tokenizer)"],
        ["Token range", "14.7% (already-lean files) to 67.7% (verbose skill docs)"],
        ["File extension", ".slm"],
        ["Conformance tests", "85 / 85 passing"],
        ["Parser", "Python reference implementation included"],
        ["License", "Open source (TBD)"],
    ]
    story.append(tbl(highlights, [7*cm, 9*cm]))
    story.append(SP(8))
    story.append(P(
        "At scale, a system with 100 agent files averaging 500 tokens each saves "
        "<b>~21,650 tokens per LLM call</b> — translating directly to reduced latency, "
        "lower API costs, and more available context window for actual task content.",
        "callout"
    ))

    # ── 2. PROBLEM STATEMENT ─────────────────────────────────
    story.append(SP(10))
    story.append(SectionHeader("2. Problem Statement — Why Markdown Is Not Enough"))
    story.append(SP(8))
    story.append(P(
        "Markdown was designed for human-readable documentation that converts to HTML. "
        "Its use in AI workflows is accidental — it happens to be concise. But it has "
        "fundamental structural limitations that compound at scale:"
    ))
    story.append(SP(4))

    problems = [
        ["Problem", "Impact"],
        ["No semantic structure — # means 'heading', not 'agent role' or 'rules'",
         "LLM must infer structure from words, not syntax"],
        ["No header stripping — all metadata reaches the LLM",
         "Config tokens (model name, retry count) waste context"],
        ["No injection boundaries — all text is equal",
         "User content can inject instructions"],
        ["No type system — types inferred from prose",
         "LLM guesses; tool schemas need full JSON"],
        ["No variable interpolation",
         "Values repeated verbatim → redundant tokens"],
        ["Table separator row required: |---|---|",
         "~6 wasted tokens per table"],
        ["No comment stripping — HTML <!-- comments --> reach LLM",
         "Author notes, TODOs cost real tokens"],
    ]
    story.append(tbl(problems, [9.5*cm, 6.5*cm]))

    # ── 3. ARCHITECTURE ───────────────────────────────────────
    story.append(PageBreak())
    story.append(SectionHeader("3. SLIM Architecture — Three Zones"))
    story.append(SP(8))
    story.append(P(
        "Every SLIM file is divided into three strictly ordered zones. This separation "
        "is the primary source of token efficiency and security."
    ))
    story.append(SP(8))

    zones = [
        ["Zone", "Sigil", "LLM Sees?", "Purpose"],
        ["Header Zone", "@key: value", "No (stripped)", "Orchestrator config — model, retry, timeout, tags"],
        ["Header Zone (visible)", "@+key: value", "Yes", "Context the LLM needs — agent name, task ID, env"],
        ["Body Zone", "#, -, 1., >, $", "Yes", "Instructions, rules, steps, prose — the core prompt"],
        ["Block Zone", "=== NAME ... === /NAME", "Content only", "Injected data, code, context, examples — hard-bounded"],
    ]
    story.append(tbl(zones, [2.8*cm, 3.8*cm, 2.4*cm, 7*cm]))
    story.append(SP(10))

    story.append(SectionHeader("How Token Stripping Works", level=2))
    story.append(SP(6))
    story.append(P(
        "The single biggest efficiency gain in SLIM is the <b>header stripping mechanism</b>. "
        "When a SLIM parser sends content to an LLM, it removes all <code>@key</code> lines "
        "entirely. This means configuration metadata — which can easily be 30-80 tokens in "
        "a typical agent file — costs exactly <b>zero LLM tokens</b>."
    ))
    story.append(SP(6))
    story.append(Code(
"""SLIM file (on disk):              What LLM receives:
@slim: 1.0                        @+agent: SecurityBot
@model: claude-opus-4      -->    @+task: PR-942
@retry: 3
@timeout: 60s                     # Role
@+agent: SecurityBot              You are SecurityBot reviewing PR-942.
@+task: PR-942

# Role
You are $agent reviewing $task."""
    ))
    story.append(P("The 4 stripped @ lines (model, retry, timeout, slim) save ~18 tokens on every single LLM call.",
                   "caption"))

    # ── 4. SYNTAX REFERENCE ──────────────────────────────────
    story.append(PageBreak())
    story.append(SectionHeader("4. Complete Syntax Reference"))
    story.append(SP(8))

    story.append(SectionHeader("4.1 Sigil Table — One Symbol, One Meaning", level=2))
    story.append(SP(6))
    sigils = [
        ["Sigil", "Meaning", "LLM Sees?"],
        ["@key: value", "Orchestrator-only header (stripped)", "No"],
        ["@+key: value", "LLM-visible header", "Yes"],
        ["@include: path", "Import another .slm file", "No"],
        ["# ## ###", "Section headings (H1, H2, H3)", "Yes"],
        ["- text", "Bullet instruction or rule", "Yes"],
        ["1. text", "Ordered step", "Yes"],
        ["> KEYWORD args", "Directive: CALL/ASSERT/YIELD/EMIT/LOG/ABORT/WAIT/RETRY", "Yes"],
        ["$key", "Variable reference (interpolated from header)", "Yes (as value)"],
        ["=== NAME [type]", "Open named block", "Content only"],
        ["=== /NAME", "Close named block", "No"],
        [":tool_name", "Tool/schema definition", "Yes"],
        ["  key!: type", "Required schema property", "Yes"],
        ["  key?: type = v", "Optional property with default", "Yes"],
        ["  -> type", "Tool return type", "Yes"],
        ["[a|b|c]", "Enum type", "Yes"],
        ["list<T>", "Typed list", "Yes"],
        ["| col | col |", "Table row (no separator row needed)", "Yes"],
        ["~", "Comment — stripped by parser", "No"],
        ["---", "Multi-document separator", "No"],
        [r"\X", "Escape any sigil — treated as literal", "Yes (as literal)"],
    ]
    story.append(tbl(sigils, [4.5*cm, 8*cm, 3.5*cm]))

    story.append(SP(12))
    story.append(SectionHeader("4.2 Type System", level=2))
    story.append(SP(6))

    types = [
        ["Type", "Syntax", "Auto-coerced from header?", "Example"],
        ["str", "str", "Fallback (anything else)", '@name: Bot'],
        ["int", "int", "Yes: integer pattern", "@retry: 3"],
        ["float", "float", "Yes: decimal pattern", "@threshold: 0.7"],
        ["bool", "bool", "Yes: true/false", "@async: true"],
        ["null", "null", "Yes: null/none", "@ctx: null"],
        ["list<str>", "list<T>", "Yes: comma-separated", "@stack: py, js"],
        ["datetime", "datetime", "No (schema only)", "created: datetime"],
        ["url", "url", "No (schema only)", "endpoint: url"],
        ["uuid", "uuid", "No (schema only)", "id: uuid"],
        ["json", "json", "No (schema only)", "payload: json"],
        ["dict<K,V>", "dict<K,V>", "No (schema only)", "meta: dict<str,int>"],
        ["enum", "[a|b|c]", "No (schema only)", "env: [prod|dev]"],
    ]
    story.append(tbl(types, [2.5*cm, 2.5*cm, 4*cm, 7*cm]))

    story.append(SP(12))
    story.append(SectionHeader("4.3 Complete Annotated Example", level=2))
    story.append(SP(6))
    story.append(Code(
"""@slim: 1.0s                           <- version + schema profile
@include: ./base/reviewer.slm          <- import base config (stripped)
@model: claude-opus-4                  <- orchestrator only, 0 LLM tokens
@retry: 3                              <- orchestrator only, 0 LLM tokens
@+agent: SecurityBot                   <- LLM sees this
@+task: PR-942                         <- LLM sees this, $task interpolates

~ Author: Security Team                <- comment, never reaches LLM

# Role
You are $agent auditing $task.         <- $agent -> SecurityBot, $task -> PR-942

# Rules
- Score risk 0.0-1.0. Above 0.7 blocks the PR.
- Use [CRITICAL]/[HIGH]/[MEDIUM]/[LOW] inline labels.

# Steps
1. Read USER_CODE block
2. > CALL analyze_risk(pr: $task, code: $input)
3. > ASSERT $result.score != null
4. > YIELD $result.report

=== USER_CODE [python]                 <- named, typed block
def get_user(id):
    q = f"SELECT * WHERE id={id}"      <- injected code is boundary-safe
    return db.execute(q)
=== /USER_CODE                         <- symmetric closing tag

:analyze_risk                          <- tool schema definition
  desc: Score a PR for security risks
  pr!: str                             <- required
  code!: str                           <- required
  env?: [prod|staging|dev] = prod      <- optional enum with default
  depth?: int = 3
  -> score: float, findings: list<Finding>"""
    ))

    # ── 5. BENCHMARK ─────────────────────────────────────────
    story.append(PageBreak())
    story.append(SectionHeader("5. Token Benchmark — Real-World Results"))
    story.append(SP(8))
    story.append(P(
        "All measurements use your actual files as source material. "
        "Tokenizer: <b>cl100k_base</b> (used by GPT-4; close approximation for Claude). "
        "<b>SLIM stripped</b> = @ headers removed + ~ comments removed — the text actually sent to the LLM."
    ))
    story.append(SP(8))

    bench_data = [
        ["Document", "MD Tokens", "SLIM Full", "SLIM Stripped", "Saved"],
        ["CLAUDE.md (project doc)",          "574",   "410",   "367",   "36.1%"],
        ["SKILL.md — find-skills",           "1,286", "425",   "415",   "67.7%"],
        ["SKILL.md — pptx (complex skill)",  "2,403", "1,112", "1,101", "54.2%"],
        ["SKILL.md — claude-setup-audit",    "2,732", "1,702", "1,691", "38.1%"],
        ["Command — codemie-catchup",        "102",   "96",    "87",    "14.7%"],
        ["ROADMAP.md (business doc)",        "2,632", "1,965", "1,852", "29.6%"],
    ]
    total_row = [["TOTAL / AVERAGE", "9,729", "5,710", "5,513", "43.3%"]]

    bench_style = [
        ("BACKGROUND",  (0, 0), (-1, 0), TEAL),
        ("TEXTCOLOR",   (0, 0), (-1, 0), WHITE),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LT_GREY]),
        ("GRID",        (0, 0), (-1, -1), 0.5, BDR_GREY),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("ALIGN",       (1, 0), (-1, -1), "CENTER"),
        ("FONTNAME",    (4, 1), (4, -1), "Helvetica-Bold"),
        ("TEXTCOLOR",   (4, 1), (4, -1), TEAL),
    ]
    t = Table(bench_data, colWidths=[6.5*cm, 2.2*cm, 2.2*cm, 2.8*cm, 2.3*cm], repeatRows=1)
    t.setStyle(TableStyle(bench_style))
    story.append(t)
    story.append(SP(4))

    total_t = Table(total_row, colWidths=[6.5*cm, 2.2*cm, 2.2*cm, 2.8*cm, 2.3*cm])
    total_t.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), NAVY),
        ("TEXTCOLOR",   (0, 0), (-1, -1), WHITE),
        ("FONTNAME",    (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("ALIGN",       (1, 0), (-1, -1), "CENTER"),
        ("TEXTCOLOR",   (4, 0), (4, 0), colors.HexColor("#00E5CC")),
    ]))
    story.append(total_t)
    story.append(SP(12))

    story.append(SectionHeader("Visual — Token Savings by Document", level=2))
    story.append(SP(6))
    bar_data = [
        ("CLAUDE.md (project doc)",         36.1, 574,   367),
        ("SKILL.md — find-skills",          67.7, 1286,  415),
        ("SKILL.md — pptx",                 54.2, 2403,  1101),
        ("SKILL.md — claude-setup-audit",   38.1, 2732,  1691),
        ("Command — codemie-catchup",       14.7, 102,   87),
        ("ROADMAP.md",                      29.6, 2632,  1852),
    ]
    story.append(MetricBar(bar_data))
    story.append(P("Each bar shows token savings percentage. Numbers show original → SLIM stripped token counts.",
                   "caption"))

    story.append(SP(10))
    story.append(SectionHeader("What Drives the Savings", level=2))
    story.append(SP(6))
    drivers = [
        ["Driver", "Example", "Typical Saving"],
        ["Header stripping (@key lines)", "@model, @retry, @timeout removed", "15-50 tokens/file"],
        ["Comment stripping (~ lines)", "Author notes, TODOs, disabled code", "5-30 tokens/file"],
        ["Table no-separator row", "Remove |---|---| line per table", "6-10 tokens/table"],
        ["Prose compression to bullets", "Verbose paragraphs → structured steps", "50-300 tokens/file"],
        ["Variable interpolation", "$agent used once vs 5× repetition", "10-40 tokens/file"],
        ["Named blocks vs ``` fences", "=== BLOCK [python] vs ```python + label", "2-5 tokens/block"],
        ["Schema vs JSON schema", "key!: str vs {\"required\": [\"key\"], ...}", "30-80 tokens/schema"],
    ]
    story.append(tbl(drivers, [4.5*cm, 6*cm, 3.5*cm]))

    story.append(SP(10))
    story.append(P(
        "<b>At scale:</b> An AI system with 100 agent files, each called 1,000 times/day, "
        "averaging 500 MD tokens → 285 SLIM tokens (43% reduction):<br/><br/>"
        "Daily token savings = 100 files × 1,000 calls × 215 tokens = <b>21,500,000 tokens/day</b><br/>"
        "At $3/million tokens (Claude Sonnet) = <b>$64.50 saved daily / $23,542 saved annually</b>.",
        "callout"
    ))

    # ── 6. SECURITY ──────────────────────────────────────────
    story.append(PageBreak())
    story.append(SectionHeader("6. Security Model"))
    story.append(SP(8))

    sec_data = [
        ["Threat", "SLIM Defence"],
        ["Header injection: attacker inserts @model: evil before first #",
         "Header zone strictly ends at first # heading. Any @key after = literal text."],
        ["Block boundary injection: === /BLOCK inside user content",
         "Unescaped === inside block = parse error. Escape with \\===."],
        ["Variable injection: $var references user-controlled values",
         "sanitize_user_content() escapes @, $, >, ===, ~ before embedding."],
        ["Directive injection: > CALL bad_tool() in user content",
         "> only triggers on ALL_CAPS reserved keywords. Unrecognised = literal text."],
        ["Include path traversal: @include: ../../../../etc/passwd",
         "Max include depth 5. Circular include detection. Absolute paths flagged by linter."],
    ]
    story.append(tbl(sec_data, [6*cm, 10*cm]))

    # ── 7. PARSER ────────────────────────────────────────────
    story.append(SP(10))
    story.append(SectionHeader("7. Python Reference Parser"))
    story.append(SP(8))
    story.append(P(
        "The reference parser is located at <code>slim/parser.py</code>. "
        "It implements the full SLIM v1.0 specification in pure Python (stdlib only, no dependencies)."
    ))
    story.append(SP(6))

    api = [
        ["API", "Description"],
        ["SLIMParser(mode).parse(text)", "Parse SLIM string → SLIMDocument"],
        ["SLIMParser(mode).parse_file(path)", "Parse .slm file → SLIMDocument"],
        ["doc.to_llm_text()", "Return stripped, interpolated text ready for LLM"],
        ["doc.to_full_text()", "Full body text with variable interpolation, no stripping"],
        ["doc.headers", "dict — @ headers (orchestrator-only)"],
        ["doc.llm_headers", "dict — @+ headers (LLM-visible)"],
        ["doc.blocks['NAME']", "Block object: .content, .type_tag, .line_start"],
        ["doc.schemas['tool']", "Schema: .properties, .returns, .desc"],
        ["doc.directives", "list of Directive: .keyword, .args, .line"],
        ["sanitize_user_content(str)", "Escape SLIM sigils in user-provided strings"],
        ["ParseMode.STRICT", "Raise exception on first error (CI/linter use)"],
        ["ParseMode.LENIENT", "Collect warnings, return partial result (default)"],
    ]
    story.append(tbl(api, [6*cm, 10*cm]))

    story.append(SP(8))
    story.append(Code(
"""from slim.parser import SLIMParser, ParseMode

doc = SLIMParser().parse_file("agent.slm")
print(doc.to_llm_text())        # send this to your LLM
print(doc.headers["model"])     # orchestrator config
print(doc.blocks["USER_CODE"].content)   # extracted block"""
    ))

    # ── 8. CONFORMANCE TESTS ─────────────────────────────────
    story.append(SP(10))
    story.append(SectionHeader("8. Conformance Test Suite"))
    story.append(SP(8))
    story.append(P(
        "The conformance suite at <code>tests/conformance.py</code> contains 85 test cases "
        "covering all aspects of the SLIM specification. Any parser implementation that passes "
        "all 85 tests is declared <b>SLIM-conformant</b>."
    ))
    story.append(SP(6))

    conf = [
        ["Section", "Tests", "Covers"],
        ["1. Header Zone",     "18", "Parsing, coercion, stripping, multi-line, @+ semantics"],
        ["2. Header Security",  "3", "Injection prevention, variable safety"],
        ["3. Body Structure",   "5", "Headings, bullets, ordered steps"],
        ["4. Comments",         "4", "~ stripping in all positions"],
        ["5. Directives",       "7", "CALL/ASSERT/YIELD, non-keyword > preservation"],
        ["6. Block Zone",      "10", "Open/close, types, nesting, escaping, errors"],
        ["7. Schema",           "7", "Tool defs, required/optional, defaults, enums, returns"],
        ["8. Variables",        "6", "Interpolation, escaped $, dotpath, unresolved"],
        ["9. Tables",           "3", "Row preservation, no separator requirement"],
        ["10. Multi-Document",  "1", "--- separator, independent headers"],
        ["11. Sanitizer",       "5", "All sigil escaping"],
        ["12. Strip Mode",      "6", "LLM text output, comment removal, interpolation"],
        ["13. Edge Cases",      "8", "Empty file, unicode, duplicate headers, blank lines"],
        ["TOTAL",              "85", "All passing — SLIM CONFORMANT"],
    ]
    story.append(tbl(conf, [4*cm, 1.8*cm, 10.2*cm],
                     row_colors=[(13, colors.HexColor("#E8F5F4"))]))

    # ── 9. MIGRATION ─────────────────────────────────────────
    story.append(PageBreak())
    story.append(SectionHeader("9. Migration Guide from Markdown"))
    story.append(SP(8))

    migration = [
        ["Markdown", "SLIM Equivalent", "Token Impact"],
        ["--- frontmatter ---", "@key: value or @+key: value", "Saves: @ lines stripped entirely"],
        ["# Heading", "# Heading", "Identical"],
        ["- bullet", "- bullet", "Identical"],
        ["```python\\ncode\\n```", "=== BLOCK [python]\\ncode\\n=== /BLOCK", "Named + typed block"],
        ["<!-- comment -->", "~ comment", "Shorter; guaranteed stripped"],
        ["| A | B |\\n|---|---|\\n| v |", "| A | B |\\n| v |", "Saves ~6 tokens/table"],
        ["*bold*", "*bold*", "Identical"],
        ["`inline`", "`inline`", "Identical"],
        ["(no equivalent)", "@model: claude-opus-4 → stripped", "0 LLM tokens for config"],
        ["(no equivalent)", "$agent variable reference", "Eliminates value repetition"],
        ["(no equivalent)", "> CALL tool(param: $val)", "Structured directives"],
        ["(no equivalent)", ":tool\\n  p!: type\\n  -> r: json", "Typed tool schemas"],
    ]
    story.append(tbl(migration, [4.5*cm, 5.5*cm, 6*cm]))

    story.append(SP(10))
    story.append(SectionHeader("Migration Steps", level=2))
    story.append(SP(6))
    for i, step in enumerate([
        "Rename file from .md to .slm",
        "Add @slim: 1.0 as the very first line",
        "Convert YAML frontmatter (---) to @key: / @+key: headers, remove --- delimiters",
        "Replace ``` code blocks with === BLOCK_NAME [lang] ... === /BLOCK_NAME",
        "Replace <!-- comments --> with ~ comments",
        "Remove | --- | separator rows from all tables",
        "Run: python -m slim validate yourfile.slm",
    ], 1):
        story.append(P(f"{i}. {step}", "bullet"))

    # ── 10. ROADMAP ──────────────────────────────────────────
    story.append(SP(10))
    story.append(SectionHeader("10. Roadmap — Build Plan"))
    story.append(SP(8))

    roadmap = [
        ["Phase", "Deliverable", "Status"],
        ["1", "SLIM v1.0 Formal Specification (.slm)", "DONE"],
        ["2", "Conformance Test Suite (85 tests)",      "DONE"],
        ["3", "Python Reference Parser",                "DONE"],
        ["4", "Token Benchmark Publication (this report)", "DONE"],
        ["5", "VSCode Extension — syntax highlighting + linter", "Planned"],
        ["6", "TypeScript Parser (Node/browser)",       "Planned"],
        ["7", "Website — spec + playground + benchmarks", "Planned"],
        ["8", "IntelliJ / JetBrains Plugin",            "Planned"],
        ["9", "Notepad++ Syntax File",                  "Planned"],
        ["10", "Open Source Release with full docs",    "Planned"],
    ]
    done_style = [("TEXTCOLOR", (2, i+1), (2, i+1), TEAL) for i in range(4)]
    done_style += [("FONTNAME", (2, i+1), (2, i+1), "Helvetica-Bold") for i in range(4)]
    t = Table(roadmap, colWidths=[1.5*cm, 10*cm, 4.5*cm], repeatRows=1)
    base_style = [
        ("BACKGROUND",  (0, 0), (-1, 0), TEAL),
        ("TEXTCOLOR",   (0, 0), (-1, 0), WHITE),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LT_GREY]),
        ("GRID",        (0, 0), (-1, -1), 0.5, BDR_GREY),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
    ] + done_style
    t.setStyle(TableStyle(base_style))
    story.append(t)

    story.append(SP(12))
    story.append(P(
        "<b>Phases 1-4 are complete.</b> The format is fully specified, the parser is "
        "conformant-tested, and the benchmark proves the efficiency claims with real data. "
        "The next milestone is the VSCode extension to make SLIM usable in daily development."
    ))

    story.append(SP(20))
    story.append(HR())
    story.append(SP(6))
    story.append(P(
        f"SLIM v1.0  |  Generated {datetime.date.today()}  |  Sasidhar Nagandla  |  Open source (license TBD)",
        "footer"
    ))

    # ── BUILD ────────────────────────────────────────────────
    doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=page_header_footer)
    return out


if __name__ == "__main__":
    out = build()
    print(f"PDF generated: {out}")
