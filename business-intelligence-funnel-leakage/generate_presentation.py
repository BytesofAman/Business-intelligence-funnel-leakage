"""
generate_presentation.py
Cross-Channel Marketing Funnel Leakage Intelligence
Academic PPTX Generator — G H Raisoni College of Engineering and Management
TAE-II Winter 2026 | Business Intelligence | B.Tech CSE – Data Science

Design system: Matches the CAP Theorem reference presentation (P07_CAP_Theorem.pdf)
  - Slide size: 13.33" × 7.5" (standard 16:9 widescreen)
  - Footer: Full-width purple band (RGB 102, 47, 145) at bottom 0.78"
  - Font: Calibri (closest to Carlito from original)
  - Brand purple: #662F91

Author:  Aman Yadav  (P-07)
Guide:   Mrs. Vaishali Kapure
"""

import os
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

# ---------------------------------------------------------------------------
# PATH CONSTANTS
# ---------------------------------------------------------------------------
PROJECT_DIR = Path(__file__).parent
PRESENTATION_DIR = PROJECT_DIR / "presentation"
PRESENTATION_DIR.mkdir(exist_ok=True)

OUTPUT_PATH = PRESENTATION_DIR / "Cross_Channel_Marketing_Funnel_Leakage_Intelligence.pptx"

LOGO_LEFT  = PROJECT_DIR / "Im5.jpg"    # GH Raisoni College logo
LOGO_RIGHT = PROJECT_DIR / "Im10.jpg"   # Raisoni Education logo
FOOTER_IMG = PROJECT_DIR / "Im8.jpg"    # Footer branding image

# ---------------------------------------------------------------------------
# DESIGN CONSTANTS
# ---------------------------------------------------------------------------
PURPLE     = RGBColor(102, 47, 145)    # #662F91 — brand purple
L_PURPLE   = RGBColor(180, 120, 220)   # light purple accent
WHITE      = RGBColor(255, 255, 255)
BLACK      = RGBColor(0,   0,   0)
DARK_GRAY  = RGBColor(50,  50,  50)
TEAL       = RGBColor(44,  125, 160)
GREEN      = RGBColor(60,  122,  80)
ORANGE     = RGBColor(200,  90,  20)
RED        = RGBColor(180,  30,  30)

SLIDE_W   = Inches(13.33)
SLIDE_H   = Inches(7.50)
FOOTER_H  = Inches(0.78)
FOOTER_TOP = Inches(7.50 - 0.78)       # = Inches(6.72)

TITLE_TOP    = Inches(0.22)
TITLE_LEFT   = Inches(0.50)
TITLE_WIDTH  = Inches(12.33)
TITLE_HEIGHT = Inches(0.70)

BODY_TOP    = Inches(1.25)
BODY_LEFT   = Inches(0.55)
BODY_WIDTH  = Inches(12.23)
BODY_HEIGHT = Inches(5.20)

HEADER_LINE_TOP = Inches(1.05)   # thin separator under title


# ---------------------------------------------------------------------------
# HELPER — create presentation object
# ---------------------------------------------------------------------------
def make_prs():
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs


# ---------------------------------------------------------------------------
# HELPER — add shape with solid fill
# ---------------------------------------------------------------------------
def add_rect(slide, left, top, width, height, fill_color=None, line_color=None, line_width_pt=0):
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        left, top, width, height
    )
    shape.line.fill.background()
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    else:
        shape.fill.background()
    if line_color and line_width_pt > 0:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(line_width_pt)
    else:
        shape.line.fill.background()
    return shape


# ---------------------------------------------------------------------------
# HELPER — add text box
# ---------------------------------------------------------------------------
def add_text(slide, text, left, top, width, height,
             font_name="Calibri", font_size=18, bold=False, italic=False,
             color=None, align=PP_ALIGN.LEFT, word_wrap=True):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    txBox.word_wrap = word_wrap
    tf = txBox.text_frame
    tf.word_wrap = word_wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = color
    return txBox


# ---------------------------------------------------------------------------
# HELPER — add paragraph to existing text frame
# ---------------------------------------------------------------------------
def add_paragraph(tf, text, font_size=16, bold=False, italic=False,
                  color=None, bullet=True, level=0, font_name="Calibri",
                  space_before_pt=4, align=PP_ALIGN.LEFT):
    from pptx.oxml.ns import qn
    from lxml import etree
    p = tf.add_paragraph()
    p.alignment = align
    p.level = level
    p.space_before = Pt(space_before_pt)
    run = p.add_run()
    run.text = text
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = color
    if bullet and text:
        pPr = p._pPr
        if pPr is None:
            pPr = p._p.get_or_add_pPr()
        buChar = etree.SubElement(pPr, qn('a:buChar'))
        buChar.set('char', '•')
        buFont = etree.SubElement(pPr, qn('a:buFont'))
        buFont.set('typeface', 'Calibri')
    return p


# ---------------------------------------------------------------------------
# HELPER — draw footer (purple band + branding image)
# ---------------------------------------------------------------------------
def add_footer(slide):
    # Purple rectangle
    add_rect(slide,
             left=Inches(0), top=FOOTER_TOP,
             width=SLIDE_W, height=FOOTER_H,
             fill_color=PURPLE)
    # Footer branding image (if available)
    if FOOTER_IMG.exists():
        slide.shapes.add_picture(
            str(FOOTER_IMG),
            left=Inches(2.96), top=Inches(6.84),
            width=Inches(7.50), height=Inches(0.42)
        )
    else:
        # Fallback text
        add_text(slide,
                 "G H Raisoni College of Engineering and Management, Wagholi, Pune – 412207",
                 left=Inches(1.5), top=Inches(6.84),
                 width=Inches(10.33), height=Inches(0.40),
                 font_size=10, color=WHITE, align=PP_ALIGN.CENTER)


# ---------------------------------------------------------------------------
# HELPER — draw header separator line
# ---------------------------------------------------------------------------
def add_header_line(slide):
    add_rect(slide,
             left=TITLE_LEFT, top=HEADER_LINE_TOP,
             width=TITLE_WIDTH, height=Inches(0.035),
             fill_color=PURPLE)


# ---------------------------------------------------------------------------
# HELPER — add slide title
# ---------------------------------------------------------------------------
def add_title(slide, title_text):
    tb = add_text(slide, title_text,
                  left=TITLE_LEFT, top=TITLE_TOP,
                  width=TITLE_WIDTH, height=TITLE_HEIGHT,
                  font_size=26, bold=True, color=PURPLE)
    add_header_line(slide)
    return tb


# ---------------------------------------------------------------------------
# HELPER — blank slide
# ---------------------------------------------------------------------------
def blank_slide(prs):
    blank_layout = prs.slide_layouts[6]  # completely blank
    slide = prs.slides.add_slide(blank_layout)
    return slide


# ===========================================================================
# SLIDE 1 — Title & Executive Summary
# ===========================================================================
def slide_01_title(prs):
    slide = blank_slide(prs)

    # White background
    add_rect(slide, 0, 0, SLIDE_W, SLIDE_H, fill_color=WHITE)

    # --- logos ---
    if LOGO_LEFT.exists():
        slide.shapes.add_picture(str(LOGO_LEFT),
                                 left=Inches(0.30), top=Inches(0.18),
                                 width=Inches(2.20), height=Inches(1.27))
    if LOGO_RIGHT.exists():
        slide.shapes.add_picture(str(LOGO_RIGHT),
                                 left=Inches(11.40), top=Inches(0.30),
                                 width=Inches(1.60), height=Inches(0.54))

    # --- institution header ---
    add_text(slide,
             "G H Raisoni College of Engineering and Management, Wagholi, Pune – 412207",
             left=Inches(2.60), top=Inches(0.18),
             width=Inches(8.60), height=Inches(0.38),
             font_size=11, bold=True, color=DARK_GRAY, align=PP_ALIGN.CENTER)
    add_text(slide,
             "(An Empowered Autonomous Institute Affiliated to SPPU) | NAAC Accredited A+",
             left=Inches(2.60), top=Inches(0.52),
             width=Inches(8.60), height=Inches(0.30),
             font_size=9, bold=False, color=DARK_GRAY, align=PP_ALIGN.CENTER)
    add_text(slide,
             "Department of CSE (Data Science) | B.Tech – Data Science",
             left=Inches(2.60), top=Inches(0.78),
             width=Inches(8.60), height=Inches(0.30),
             font_size=9, bold=False, color=DARK_GRAY, align=PP_ALIGN.CENTER)

    # --- purple separator ---
    add_rect(slide,
             left=Inches(0.40), top=Inches(1.18),
             width=Inches(12.53), height=Inches(0.045),
             fill_color=PURPLE)

    # --- main title (dark purple, large) ---
    add_text(slide,
             "Cross-Channel Marketing Funnel Leakage Intelligence:",
             left=Inches(0.60), top=Inches(1.38),
             width=Inches(12.13), height=Inches(0.72),
             font_size=34, bold=True, color=PURPLE, align=PP_ALIGN.CENTER)
    add_text(slide,
             "A Business Intelligence Approach for Customer Journey Optimization",
             left=Inches(0.60), top=Inches(2.05),
             width=Inches(12.13), height=Inches(0.55),
             font_size=22, bold=False, color=PURPLE, align=PP_ALIGN.CENTER)

    # --- subtitle tagline ---
    add_text(slide,
             "Cross-Channel Attribution  •  Funnel Drop-Off Analysis  •  Marketing Budget Optimization",
             left=Inches(0.60), top=Inches(2.70),
             width=Inches(12.13), height=Inches(0.42),
             font_size=14, bold=False, color=DARK_GRAY, align=PP_ALIGN.CENTER, italic=True)

    # --- thin separator ---
    add_rect(slide,
             left=Inches(2.50), top=Inches(3.22),
             width=Inches(8.33), height=Inches(0.030),
             fill_color=L_PURPLE)

    # --- info block ---
    info_top = Inches(3.38)
    info_left = Inches(0.80)
    info_w = Inches(11.73)
    labels = [
        ("Subject:", "Business Intelligence  |  TAE-II — Winter 2026  (2023 Pattern)"),
        ("Student:", "Aman Yadav  (Roll No. P-07)"),
        ("Guide:", "Mrs. Vaishali Kapure"),
        ("Assessment:", "Term Assessment Examination – II (TAE-II)"),
    ]
    for i, (lbl, val) in enumerate(labels):
        row_top = info_top + Inches(i * 0.52)
        add_text(slide, lbl,
                 left=info_left, top=row_top,
                 width=Inches(1.60), height=Inches(0.44),
                 font_size=13, bold=True, color=PURPLE)
        add_text(slide, val,
                 left=Inches(2.50), top=row_top,
                 width=Inches(10.0), height=Inches(0.44),
                 font_size=13, bold=False, color=DARK_GRAY)

    add_footer(slide)
    return slide


# ===========================================================================
# SLIDE 2 — Contents & Business Problem
# ===========================================================================
def slide_02_contents(prs):
    slide = blank_slide(prs)
    add_rect(slide, 0, 0, SLIDE_W, SLIDE_H, fill_color=WHITE)
    add_title(slide, "Contents & The Approved Business Problem")

    # Contents column
    left_col = Inches(0.55)
    right_col = Inches(6.90)
    col_w    = Inches(5.90)

    # Left: table of contents
    tb = slide.shapes.add_textbox(left_col, BODY_TOP, col_w, Inches(5.10))
    tb.word_wrap = True
    tf = tb.text_frame
    tf.word_wrap = True

    contents = [
        "1.  Business Problem & Motivation",
        "2.  Project Objectives & Scope",
        "3.  7-Stage Conversion Funnel",
        "4.  End-to-End System Architecture",
        "5.  Multi-Source Data Ingestion",
        "6.  Automated ETL Pipeline",
        "7.  Data Cleansing & Normalization",
        "8.  34-Point Data Quality Engine",
        "9.  Dimensional Data Warehouse",
        "10. SQL Analytics Engine",
        "11. Power BI Architecture & DAX",
        "12. Dashboard — Executive Overview",
        "13. Dashboard — Funnel Leakage",
        "14. Dashboard — Channel Attribution",
        "15. Dashboard — Customer Segmentation",
        "16. Strategic Recommendations",
        "17. Limitations & Future Scope",
    ]

    p0 = tf.paragraphs[0]
    p0.alignment = PP_ALIGN.LEFT
    r0 = p0.add_run()
    r0.text = "Agenda"
    r0.font.name = "Calibri"
    r0.font.size = Pt(16)
    r0.font.bold = True
    r0.font.color.rgb = PURPLE

    for item in contents:
        add_paragraph(tf, item, font_size=12, bullet=False,
                      color=DARK_GRAY, space_before_pt=3)

    # Right: Business Problem
    add_rect(slide, right_col, BODY_TOP, col_w, Inches(5.10),
             fill_color=RGBColor(245, 240, 255), line_color=PURPLE, line_width_pt=1)

    add_text(slide, "The Business Problem",
             left=right_col + Inches(0.15), top=BODY_TOP + Inches(0.12),
             width=Inches(5.60), height=Inches(0.38),
             font_size=15, bold=True, color=PURPLE)

    problems = [
        ("Marketing Fragmentation",
         "Siloed tracking across Google, Meta, Email, and CRM systems creates blind spots in the customer journey."),
        ("The Visibility Void",
         "Marketing managers cannot reconstruct continuous user paths from impression to purchase."),
        ("Cost of Ignorance",
         "Ad budgets are wasted on channels that drive clicks but fail to convert — with no systematic detection."),
    ]

    prob_top = BODY_TOP + Inches(0.62)
    for i, (heading, body) in enumerate(problems):
        box_top = prob_top + Inches(i * 1.48)
        add_rect(slide, right_col + Inches(0.12), box_top,
                 Inches(5.65), Inches(1.32),
                 fill_color=WHITE, line_color=L_PURPLE, line_width_pt=0.75)
        add_text(slide, f"⚠  {heading}",
                 left=right_col + Inches(0.22), top=box_top + Inches(0.08),
                 width=Inches(5.45), height=Inches(0.35),
                 font_size=12, bold=True, color=PURPLE)
        add_text(slide, body,
                 left=right_col + Inches(0.22), top=box_top + Inches(0.42),
                 width=Inches(5.45), height=Inches(0.80),
                 font_size=11, color=DARK_GRAY)

    add_footer(slide)
    return slide


# ===========================================================================
# SLIDE 3 — Project Objectives & 7-Stage Conversion Funnel
# ===========================================================================
def slide_03_objectives_funnel(prs):
    slide = blank_slide(prs)
    add_rect(slide, 0, 0, SLIDE_W, SLIDE_H, fill_color=WHITE)
    add_title(slide, "Project Objectives & The 7-Stage Conversion Funnel")

    # --- Objectives (top half) ---
    obj_top = BODY_TOP
    objectives = [
        "Ingest and cleanse 57,000+ multi-touch customer journey interactions from GA4 event exports.",
        "Construct an enterprise Star Schema data warehouse on MySQL with 6 conformed dimensions.",
        "Build an automated modular Python ETL pipeline with zero-silent-drop validation (34/34 checks).",
        "Deploy an interactive 4-page Power BI executive dashboard with verified DAX KPI metrics.",
    ]
    obj_tb = slide.shapes.add_textbox(BODY_LEFT, obj_top, BODY_WIDTH, Inches(2.10))
    obj_tb.word_wrap = True
    tf = obj_tb.text_frame
    tf.word_wrap = True
    p0 = tf.paragraphs[0]
    p0.alignment = PP_ALIGN.LEFT
    r0 = p0.add_run()
    r0.text = "Project Objectives"
    r0.font.name = "Calibri"
    r0.font.size = Pt(16)
    r0.font.bold = True
    r0.font.color.rgb = PURPLE

    for obj in objectives:
        add_paragraph(tf, obj, font_size=13, bullet=True, color=DARK_GRAY, space_before_pt=5)

    # --- Funnel diagram (bottom) ---
    funnel_top = BODY_TOP + Inches(2.30)
    funnel_label_top = funnel_top - Inches(0.30)
    add_text(slide, "The 7-Stage Continuous Conversion Funnel",
             left=BODY_LEFT, top=funnel_label_top,
             width=BODY_WIDTH, height=Inches(0.30),
             font_size=14, bold=True, color=PURPLE)

    stages = [
        ("IMPRESSION",   RGBColor(91,  44, 135)),
        ("CLICK",        RGBColor(102, 47, 145)),
        ("LANDING PAGE", RGBColor(120, 80, 165)),
        ("PRODUCT VIEW", RGBColor(44, 125, 160)),
        ("CART",         RGBColor(60, 122,  80)),
        ("CHECKOUT",     RGBColor(200, 140,  20)),
        ("PURCHASE",     RGBColor(180,  30,  30)),
    ]

    box_w   = Inches(1.58)
    box_h   = Inches(0.80)
    arrow_w = Inches(0.22)
    total_w = len(stages) * float(box_w) + (len(stages) - 1) * float(arrow_w)
    start_x = (float(SLIDE_W) - total_w) / 2

    for i, (label, color) in enumerate(stages):
        bx = start_x + i * (float(box_w) + float(arrow_w))
        # Box
        add_rect(slide,
                 left=Emu(int(bx)), top=funnel_top,
                 width=box_w, height=box_h,
                 fill_color=color)
        add_text(slide, label,
                 left=Emu(int(bx)), top=funnel_top + Inches(0.15),
                 width=box_w, height=Inches(0.50),
                 font_size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        # Arrow (except after last)
        if i < len(stages) - 1:
            ax = bx + float(box_w)
            add_text(slide, "▶",
                     left=Emu(int(ax)), top=funnel_top + Inches(0.22),
                     width=arrow_w, height=Inches(0.36),
                     font_size=14, color=PURPLE, align=PP_ALIGN.CENTER)

    # Drop-off note
    add_text(slide,
             "Key Finding: 54.3% drop-off between Landing Page → Product View is the primary bottleneck",
             left=BODY_LEFT, top=funnel_top + Inches(0.95),
             width=BODY_WIDTH, height=Inches(0.35),
             font_size=12, italic=True, color=RED, align=PP_ALIGN.CENTER)

    add_footer(slide)
    return slide


# ===========================================================================
# SLIDE 4 — End-to-End System Architecture
# ===========================================================================
def slide_04_architecture(prs):
    slide = blank_slide(prs)
    add_rect(slide, 0, 0, SLIDE_W, SLIDE_H, fill_color=WHITE)
    add_title(slide, "End-to-End BI System Architecture")

    tiers = [
        ("TIER 1", "Raw Data Ingestion",
         "GA4 Event Exports  •  Campaign CSVs  •  Ad Spend Data\nAPI Adapters: Google Ads, Meta, HubSpot, Email (schema-extensible)",
         RGBColor(91, 44, 135)),
        ("TIER 2", "Automated Python ETL",
         "extract.py  →  transform.py  →  validate.py  →  load.py\nOrchestrated by run_pipeline.py  |  34-Point Quality Engine",
         TEAL),
        ("TIER 3", "Dimensional Data Warehouse",
         "MySQL  |  Star Schema  |  Fact_FunnelEvent + 6 Conformed Dimensions\nSQL Analytical Views: vw_funnel_summary, vw_channel_performance, etc.",
         GREEN),
        ("TIER 4", "Analytical Reporting Layer",
         "Power BI Desktop  |  DirectQuery / Import  |  4 Dashboard Pages\nDAX KPIs: Revenue $355K, Spend $243K, ROAS, CPA, Funnel Conversion Rates",
         ORANGE),
    ]

    tier_w  = Inches(11.50)
    tier_h  = Inches(1.08)
    tier_l  = Inches(0.92)
    tier_start = BODY_TOP

    for i, (tier_num, tier_name, tier_body, color) in enumerate(tiers):
        ty = tier_start + Inches(i * 1.22)
        # Left label tab
        add_rect(slide, tier_l, ty, Inches(1.20), tier_h, fill_color=color)
        add_text(slide, tier_num,
                 left=tier_l, top=ty + Inches(0.08),
                 width=Inches(1.20), height=Inches(0.38),
                 font_size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        # Main box
        add_rect(slide, tier_l + Inches(1.20), ty,
                 Inches(10.30), tier_h,
                 fill_color=RGBColor(248, 245, 255),
                 line_color=color, line_width_pt=1.2)
        add_text(slide, tier_name,
                 left=tier_l + Inches(1.32), top=ty + Inches(0.06),
                 width=Inches(9.90), height=Inches(0.38),
                 font_size=14, bold=True, color=color)
        add_text(slide, tier_body,
                 left=tier_l + Inches(1.32), top=ty + Inches(0.46),
                 width=Inches(9.90), height=Inches(0.56),
                 font_size=11, color=DARK_GRAY)
        # Down-arrow between tiers
        if i < len(tiers) - 1:
            add_text(slide, "▼",
                     left=Inches(6.80), top=ty + tier_h,
                     width=Inches(0.60), height=Inches(0.14),
                     font_size=13, color=PURPLE, align=PP_ALIGN.CENTER)

    add_footer(slide)
    return slide


# ===========================================================================
# SLIDE 5 — Multi-Source Data Ingestion & ETL Pipeline
# ===========================================================================
def slide_05_ingestion_etl(prs):
    slide = blank_slide(prs)
    add_rect(slide, 0, 0, SLIDE_W, SLIDE_H, fill_color=WHITE)
    add_title(slide, "Multi-Source Data Ingestion & Automated ETL Pipeline")

    # Left column: Data Sources
    lc = Inches(0.55)
    lw = Inches(5.80)
    rc = Inches(6.85)
    rw = Inches(5.93)

    add_text(slide, "Data Sources",
             left=lc, top=BODY_TOP,
             width=lw, height=Inches(0.38),
             font_size=15, bold=True, color=PURPLE)

    sources = [
        ("GA4 Event Exports",       "57,083 rows | 6,803 unique users | 15,000 sessions",    RGBColor(91, 44, 135)),
        ("Campaign Master Data",    "7 campaigns across 5 channels",                          TEAL),
        ("Daily Ad Spend",          "1,830 rows | $243,209.53 total spend",                   GREEN),
        ("API Adapters (Future)",   "Google Ads, Meta, HubSpot, Email — schema reserved",     ORANGE),
    ]

    src_top = BODY_TOP + Inches(0.50)
    for i, (name, detail, color) in enumerate(sources):
        sy = src_top + Inches(i * 1.12)
        add_rect(slide, lc, sy, lw, Inches(1.00),
                 fill_color=RGBColor(248, 245, 255),
                 line_color=color, line_width_pt=1.5)
        add_rect(slide, lc, sy, Inches(0.18), Inches(1.00), fill_color=color)
        add_text(slide, name,
                 left=lc + Inches(0.28), top=sy + Inches(0.06),
                 width=Inches(5.40), height=Inches(0.38),
                 font_size=13, bold=True, color=color)
        add_text(slide, detail,
                 left=lc + Inches(0.28), top=sy + Inches(0.48),
                 width=Inches(5.40), height=Inches(0.42),
                 font_size=11, color=DARK_GRAY)

    # Right column: ETL Modules
    add_text(slide, "ETL Pipeline Modules",
             left=rc, top=BODY_TOP,
             width=rw, height=Inches(0.38),
             font_size=15, bold=True, color=PURPLE)

    modules = [
        ("extract.py",       "Reads GA4 CSV, campaign & spend data; applies schema enforcement"),
        ("transform.py",     "Flattens nested events, standardizes timestamps, maps channel taxonomy"),
        ("validate.py",      "Executes 34-point QA: PK uniqueness, FK integrity, stage validity"),
        ("load.py",          "Bulk-inserts 57K+ rows into MySQL star schema via parameterized SQL"),
        ("run_pipeline.py",  "Orchestrates phases 1–4 with logging, error trapping & summary report"),
    ]

    mod_top = BODY_TOP + Inches(0.50)
    mod_h   = Inches(0.90)
    mod_gap = Inches(0.02)

    for i, (mod_name, mod_desc) in enumerate(modules):
        my = mod_top + Inches(i * (float(mod_h) + float(mod_gap)))
        add_rect(slide, rc, my, rw, mod_h,
                 fill_color=RGBColor(245, 240, 255),
                 line_color=PURPLE, line_width_pt=0.75)
        add_text(slide, f"  {i+1}.  {mod_name}",
                 left=rc + Inches(0.08), top=my + Inches(0.06),
                 width=Inches(5.70), height=Inches(0.36),
                 font_size=13, bold=True, color=PURPLE)
        add_text(slide, mod_desc,
                 left=rc + Inches(0.08), top=my + Inches(0.46),
                 width=Inches(5.70), height=Inches(0.36),
                 font_size=11, color=DARK_GRAY)
        if i < len(modules) - 1:
            add_text(slide, "↓",
                     left=rc + Inches(2.70), top=my + mod_h,
                     width=Inches(0.50), height=mod_gap + Inches(0.10),
                     font_size=11, color=PURPLE, align=PP_ALIGN.CENTER)

    add_footer(slide)
    return slide


# ===========================================================================
# SLIDE 6 — Data Cleansing & 34-Point Quality Engine
# ===========================================================================
def slide_06_quality(prs):
    slide = blank_slide(prs)
    add_rect(slide, 0, 0, SLIDE_W, SLIDE_H, fill_color=WHITE)
    add_title(slide, "Data Cleansing, Normalization & 34-Point Quality Engine")

    # Top: cleansing steps
    add_text(slide, "Data Cleansing & Normalization",
             left=BODY_LEFT, top=BODY_TOP,
             width=Inches(6.00), height=Inches(0.38),
             font_size=15, bold=True, color=PURPLE)

    cleansing = [
        "Flatten nested GA4 JSON event schemas into tabular columnar format",
        "Convert Unix microsecond timestamps → UTC ISO 8601 → local timezone",
        "Prune orphan events (sessions with no landing page / pre-funnel entry)",
        "Map raw traffic_source_medium values → 5 conformed channel categories",
        "Proportional daily ad spend allocation per campaign preventing double-counting",
        "Deduplicate event_id primary keys (100% uniqueness enforced post-transform)",
    ]

    cln_tb = slide.shapes.add_textbox(BODY_LEFT, BODY_TOP + Inches(0.45),
                                       Inches(6.00), Inches(2.30))
    cln_tb.word_wrap = True
    ctf = cln_tb.text_frame
    ctf.word_wrap = True
    p0 = ctf.paragraphs[0]
    p0.space_before = Pt(0)
    p0.add_run()  # empty first paragraph

    for step in cleansing:
        add_paragraph(ctf, step, font_size=12, bullet=True,
                      color=DARK_GRAY, space_before_pt=5)

    # Divider
    add_rect(slide, Inches(6.70), BODY_TOP, Inches(0.04), Inches(5.00),
             fill_color=L_PURPLE)

    # Right: Quality engine
    add_text(slide, "34-Point Automated Quality Engine",
             left=Inches(6.90), top=BODY_TOP,
             width=Inches(5.88), height=Inches(0.38),
             font_size=15, bold=True, color=PURPLE)

    checks = [
        ("Column Completeness",     "Required columns present in all tables"),
        ("Primary Key Uniqueness",  "Event_ID / User_ID / Session_ID — zero duplicates"),
        ("Foreign Key Integrity",   "All FK references resolve to dimension tables"),
        ("Funnel Stage Validity",   "Events belong to valid IMPRESSION–PURCHASE stages"),
        ("Date Range Integrity",    "All dates within Jan–Dec 2024 boundary"),
        ("Revenue Non-Negative",    "Revenue ≥ 0 for purchase events only"),
        ("Spend Allocation",        "Total allocated spend = total raw spend ±$0.01"),
        ("Row Count Preservation",  "57,083 source rows = 57,083 fact rows loaded"),
        ("Null Tolerance Limits",   "Critical columns: 0 nulls; optional: <5%"),
        ("Result",                  "34 / 34 checks PASSED  ✔  (100%)"),
    ]

    check_top = BODY_TOP + Inches(0.50)
    for i, (chk, detail) in enumerate(checks):
        cy = check_top + Inches(i * 0.50)
        if chk == "Result":
            add_rect(slide, Inches(6.90), cy, Inches(5.88), Inches(0.42),
                     fill_color=GREEN)
            add_text(slide, f"  ✔  {detail}",
                     left=Inches(6.90), top=cy + Inches(0.04),
                     width=Inches(5.88), height=Inches(0.36),
                     font_size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        else:
            add_text(slide, f"✔  {chk}:",
                     left=Inches(6.90), top=cy,
                     width=Inches(2.50), height=Inches(0.40),
                     font_size=11, bold=True, color=PURPLE)
            add_text(slide, detail,
                     left=Inches(9.42), top=cy,
                     width=Inches(3.36), height=Inches(0.40),
                     font_size=11, color=DARK_GRAY)

    add_footer(slide)
    return slide


# ===========================================================================
# SLIDE 7 — Dimensional Data Warehouse & Star Schema
# ===========================================================================
def slide_07_star_schema(prs):
    slide = blank_slide(prs)
    add_rect(slide, 0, 0, SLIDE_W, SLIDE_H, fill_color=WHITE)
    add_title(slide, "Dimensional Data Warehouse & Star Schema Design")

    # Left: schema description
    add_text(slide, "Schema Specification",
             left=BODY_LEFT, top=BODY_TOP,
             width=Inches(4.80), height=Inches(0.38),
             font_size=15, bold=True, color=PURPLE)

    specs = [
        ("Grain", "One record = one standardized customer journey event"),
        ("Fact Table", "Fact_FunnelEvent  (57,083 rows)"),
        ("Dimensions", "6 conformed dimensions (Date, Channel, Campaign, LandingPage, Device, Geography)"),
        ("Indexes", "B-tree indexes on all FK columns + Event_Timestamp"),
        ("Storage", "MySQL InnoDB  |  marketing_funnel_dw database"),
        ("Views", "vw_funnel_summary, vw_channel_performance, vw_daily_trend, vw_funnel_conversion"),
    ]

    spec_top = BODY_TOP + Inches(0.48)
    for i, (k, v) in enumerate(specs):
        sy = spec_top + Inches(i * 0.68)
        add_text(slide, f"{k}:",
                 left=BODY_LEFT, top=sy,
                 width=Inches(1.50), height=Inches(0.50),
                 font_size=12, bold=True, color=PURPLE)
        add_text(slide, v,
                 left=Inches(2.10), top=sy,
                 width=Inches(3.40), height=Inches(0.50),
                 font_size=11, color=DARK_GRAY)

    # Right: Star schema diagram (native shapes)
    cx = Inches(9.50)   # center x of star
    cy = Inches(3.90)   # center y
    fact_w = Inches(2.30)
    fact_h = Inches(1.40)
    dim_w  = Inches(1.80)
    dim_h  = Inches(0.80)

    # Fact table center
    fx = cx - fact_w / 2
    fy = cy - fact_h / 2
    add_rect(slide, fx, fy, fact_w, fact_h, fill_color=PURPLE)
    add_text(slide, "Fact_FunnelEvent",
             left=fx, top=fy + Inches(0.08),
             width=fact_w, height=Inches(0.38),
             font_size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(slide, "57,083 rows\n17 measures + 6 FKs",
             left=fx, top=fy + Inches(0.50),
             width=fact_w, height=Inches(0.72),
             font_size=10, color=WHITE, align=PP_ALIGN.CENTER)

    import math
    dims = [
        ("Dim_Date",        "366 rows"),
        ("Dim_Channel",     "5 rows"),
        ("Dim_Campaign",    "7 rows"),
        ("Dim_LandingPage", "12 rows"),
        ("Dim_Device",      "6 rows"),
        ("Dim_Geography",   "46 rows"),
    ]
    radius_x = Inches(2.55)
    radius_y = Inches(2.00)

    for i, (dname, drows) in enumerate(dims):
        angle = (2 * math.pi * i / len(dims)) - math.pi / 2
        dx = cx + radius_x * math.cos(angle) - dim_w / 2
        dy = cy + radius_y * math.sin(angle) - dim_h / 2
        add_rect(slide, dx, dy, dim_w, dim_h,
                 fill_color=TEAL, line_color=WHITE, line_width_pt=0.5)
        add_text(slide, dname,
                 left=dx, top=dy + Inches(0.04),
                 width=dim_w, height=Inches(0.38),
                 font_size=10, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_text(slide, drows,
                 left=dx, top=dy + Inches(0.42),
                 width=dim_w, height=Inches(0.28),
                 font_size=9, color=WHITE, align=PP_ALIGN.CENTER)

    # Label
    add_text(slide, "Star Schema (MySQL — marketing_funnel_dw)",
             left=Inches(6.80), top=BODY_TOP,
             width=Inches(6.00), height=Inches(0.38),
             font_size=14, bold=True, color=PURPLE, align=PP_ALIGN.CENTER)

    add_footer(slide)
    return slide


# ===========================================================================
# SLIDE 8 — Power BI Architecture & DAX Metrics
# ===========================================================================
def slide_08_powerbi_dax(prs):
    slide = blank_slide(prs)
    add_rect(slide, 0, 0, SLIDE_W, SLIDE_H, fill_color=WHITE)
    add_title(slide, "Power BI Architecture & DAX Metric Reconciliation")

    # Left: Architecture
    lc = Inches(0.55)
    lw = Inches(5.70)

    add_text(slide, "Power BI Data Model Architecture",
             left=lc, top=BODY_TOP,
             width=lw, height=Inches(0.38),
             font_size=15, bold=True, color=PURPLE)

    arch_items = [
        "Single-direction 1:* relationships — avoids circular filter paths",
        "Import mode for star schema tables (fast in-memory analytics)",
        "Fact_FunnelEvent as central table connected to all 6 dimensions",
        "Date table marked as official date table for time intelligence",
        "Row-level security ready for multi-tenant deployment",
    ]

    arch_tb = slide.shapes.add_textbox(lc, BODY_TOP + Inches(0.46),
                                        lw, Inches(2.00))
    arch_tb.word_wrap = True
    atf = arch_tb.text_frame
    atf.word_wrap = True
    p0 = atf.paragraphs[0]
    p0.add_run()

    for item in arch_items:
        add_paragraph(atf, item, font_size=12, bullet=True,
                      color=DARK_GRAY, space_before_pt=6)

    # DAX measures box
    add_rect(slide, lc, BODY_TOP + Inches(2.60), lw, Inches(2.60),
             fill_color=RGBColor(245, 240, 255), line_color=PURPLE, line_width_pt=1)
    add_text(slide, "Core DAX Measures",
             left=lc + Inches(0.15), top=BODY_TOP + Inches(2.70),
             width=lw - Inches(0.20), height=Inches(0.36),
             font_size=13, bold=True, color=PURPLE)

    dax_measures = [
        "Total Revenue = SUM(Fact_FunnelEvent[Revenue])",
        "Total Users  = DISTINCTCOUNT(Fact_FunnelEvent[User_ID])",
        "CPA = DIVIDE([Total Spend], [Total Conversions], 0)",
        "ROAS = DIVIDE([Total Revenue], [Total Spend], 0)",
        "Funnel CR = DIVIDE([Purchase Events], [Landing Events], 0)",
    ]
    dax_top = BODY_TOP + Inches(3.14)
    for j, m in enumerate(dax_measures):
        add_text(slide, m,
                 left=lc + Inches(0.18), top=dax_top + Inches(j * 0.38),
                 width=lw - Inches(0.28), height=Inches(0.36),
                 font_size=10, font_name="Courier New", color=DARK_GRAY)

    # Right: 4-page dashboard map
    rc = Inches(6.80)
    rw = Inches(5.98)

    add_text(slide, "4-Page Dashboard Architecture",
             left=rc, top=BODY_TOP,
             width=rw, height=Inches(0.38),
             font_size=15, bold=True, color=PURPLE)

    pages = [
        ("Page 1", "Executive Overview",          "KPI Scorecards, Revenue Trend, Channel Mix",        PURPLE),
        ("Page 2", "Funnel Leakage & Abandonment","Stage-to-stage drop-off, cart & checkout rates",    TEAL),
        ("Page 3", "Channel & Campaign Attribution","Spend vs. Revenue, CPA comparison, ROAS ranking", GREEN),
        ("Page 4", "Customer & Device Segmentation","Mobile vs. desktop, geo-map, landing page perf.", ORANGE),
    ]

    pg_top = BODY_TOP + Inches(0.48)
    for i, (pg_num, pg_name, pg_detail, color) in enumerate(pages):
        py = pg_top + Inches(i * 1.22)
        add_rect(slide, rc, py, rw, Inches(1.12),
                 fill_color=RGBColor(248, 245, 255),
                 line_color=color, line_width_pt=1.5)
        add_rect(slide, rc, py, Inches(0.80), Inches(1.12), fill_color=color)
        add_text(slide, pg_num,
                 left=rc, top=py + Inches(0.32),
                 width=Inches(0.80), height=Inches(0.45),
                 font_size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_text(slide, pg_name,
                 left=rc + Inches(0.90), top=py + Inches(0.08),
                 width=Inches(5.00), height=Inches(0.36),
                 font_size=13, bold=True, color=color)
        add_text(slide, pg_detail,
                 left=rc + Inches(0.90), top=py + Inches(0.52),
                 width=Inches(5.00), height=Inches(0.50),
                 font_size=11, color=DARK_GRAY)

    add_footer(slide)
    return slide


# ===========================================================================
# SLIDE 9 — Executive Dashboard & KPI Scorecards
# ===========================================================================
def slide_09_executive_dashboard(prs):
    slide = blank_slide(prs)
    add_rect(slide, 0, 0, SLIDE_W, SLIDE_H, fill_color=WHITE)
    add_title(slide, "Executive Dashboard — KPI Scorecards & Funnel Overview")

    # KPI cards
    kpis = [
        ("Total Users",    "6,803",      PURPLE),
        ("Sessions",       "15,000",     TEAL),
        ("Revenue",        "$355,403",   GREEN),
        ("Ad Spend",       "$243,209",   ORANGE),
        ("ROAS",           "1.46×",      RGBColor(60, 90, 160)),
        ("Overall CPA",    "$178.70",    RED),
    ]

    card_w = Inches(2.00)
    card_h = Inches(1.30)
    card_gap = Inches(0.15)
    cards_total = len(kpis) * float(card_w) + (len(kpis)-1) * float(card_gap)
    card_start_x = (float(SLIDE_W) - cards_total) / 2

    kpi_top = BODY_TOP + Inches(0.10)

    for i, (label, value, color) in enumerate(kpis):
        cx = card_start_x + i * (float(card_w) + float(card_gap))
        add_rect(slide, Emu(int(cx)), kpi_top, card_w, card_h,
                 fill_color=color)
        add_text(slide, value,
                 left=Emu(int(cx)), top=kpi_top + Inches(0.18),
                 width=card_w, height=Inches(0.56),
                 font_size=22, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_text(slide, label,
                 left=Emu(int(cx)), top=kpi_top + Inches(0.80),
                 width=card_w, height=Inches(0.38),
                 font_size=11, color=WHITE, align=PP_ALIGN.CENTER)

    # Funnel summary table
    table_top = kpi_top + card_h + Inches(0.35)
    add_text(slide, "Funnel Conversion Analysis",
             left=BODY_LEFT, top=table_top,
             width=Inches(5.50), height=Inches(0.36),
             font_size=14, bold=True, color=PURPLE)

    funnel_data = [
        ("Stage",           "Events",   "Conv. Rate",  "Drop-off"),
        ("Impression",      "57,083",   "—",            "—"),
        ("Click",           "30,212",   "52.9%",        "47.1%"),
        ("Landing Page",    "15,000",   "49.6%",        "50.4%"),
        ("Product View",    "6,855",    "45.7%",        "54.3%  ⚠"),
        ("Cart",            "3,482",    "50.8%",        "49.2%"),
        ("Checkout",        "1,812",    "52.0%",        "48.0%"),
        ("Purchase",        "1,361",    "75.1%",        "24.9%"),
    ]

    tbl_left  = BODY_LEFT
    tbl_w     = [Inches(2.00), Inches(1.20), Inches(1.20), Inches(1.30)]
    row_h     = Inches(0.46)
    row_start = table_top + Inches(0.42)
    col_starts = [
        tbl_left,
        tbl_left + tbl_w[0],
        tbl_left + tbl_w[0] + tbl_w[1],
        tbl_left + tbl_w[0] + tbl_w[1] + tbl_w[2],
    ]

    for ri, row in enumerate(funnel_data):
        for ci, cell in enumerate(row):
            cy = row_start + Inches(ri * 0.46)
            is_header = ri == 0
            is_warning = "⚠" in cell
            bg = PURPLE if is_header else (RGBColor(255, 230, 230) if is_warning else (RGBColor(245, 240, 255) if ri % 2 == 0 else WHITE))
            fc = WHITE if is_header else (RED if is_warning else DARK_GRAY)
            add_rect(slide, col_starts[ci], cy, tbl_w[ci], row_h, fill_color=bg,
                     line_color=L_PURPLE, line_width_pt=0.5)
            add_text(slide, cell,
                     left=col_starts[ci] + Inches(0.05), top=cy + Inches(0.06),
                     width=tbl_w[ci] - Inches(0.08), height=row_h - Inches(0.08),
                     font_size=11, bold=is_header, color=fc, align=PP_ALIGN.CENTER)

    # Right: channel revenue split
    add_text(slide, "Channel Revenue Distribution",
             left=Inches(6.80), top=table_top,
             width=Inches(5.98), height=Inches(0.36),
             font_size=14, bold=True, color=PURPLE)

    channels = [
        ("Organic Search",  "38.2%", "$135,764", GREEN,   Inches(2.28)),
        ("Paid Search",     "29.7%", "$105,554", TEAL,    Inches(1.77)),
        ("Social",          "15.4%", "$ 54,732", PURPLE,  Inches(0.92)),
        ("Email",           "10.3%", "$ 36,607", ORANGE,  Inches(0.61)),
        ("Display",         " 6.4%", "$ 22,746", RED,     Inches(0.38)),
    ]

    bar_left  = Inches(6.80)
    bar_top   = table_top + Inches(0.50)
    bar_h     = Inches(0.54)
    bar_gap   = Inches(0.12)
    label_w   = Inches(1.50)
    pct_w     = Inches(0.60)
    bar_area_w = Inches(2.40)
    rev_w     = Inches(1.20)

    for i, (ch_name, pct, rev, color, bar_len) in enumerate(channels):
        ry = bar_top + Inches(i * (float(bar_h) + float(bar_gap)))
        add_text(slide, ch_name,
                 left=bar_left, top=ry + Inches(0.09),
                 width=label_w, height=Inches(0.36),
                 font_size=11, color=DARK_GRAY)
        add_rect(slide, bar_left + label_w, ry + Inches(0.08),
                 bar_area_w, Inches(0.38),
                 fill_color=RGBColor(230, 225, 240))
        add_rect(slide, bar_left + label_w, ry + Inches(0.08),
                 bar_len, Inches(0.38), fill_color=color)
        add_text(slide, pct,
                 left=bar_left + label_w + bar_area_w + Inches(0.05),
                 top=ry + Inches(0.09),
                 width=pct_w, height=Inches(0.36),
                 font_size=11, bold=True, color=color)
        add_text(slide, rev,
                 left=bar_left + label_w + bar_area_w + pct_w + Inches(0.05),
                 top=ry + Inches(0.09),
                 width=rev_w, height=Inches(0.36),
                 font_size=11, color=DARK_GRAY)

    add_footer(slide)
    return slide


# ===========================================================================
# SLIDE 10 — Channel & Campaign Attribution
# ===========================================================================
def slide_10_attribution(prs):
    slide = blank_slide(prs)
    add_rect(slide, 0, 0, SLIDE_W, SLIDE_H, fill_color=WHITE)
    add_title(slide, "Channel & Campaign Attribution Analysis")

    add_text(slide, "Campaign Efficiency Frontier — Ad Spend vs. Revenue",
             left=BODY_LEFT, top=BODY_TOP,
             width=BODY_WIDTH, height=Inches(0.36),
             font_size=14, bold=True, color=PURPLE)

    # CPA comparison table
    cpa_data = [
        ("Channel",          "Spend",      "Revenue",    "Conversions", "CPA",      "ROAS"),
        ("Organic Search",   "$0",         "$135,764",   "519",         "$0.00",    "∞"),
        ("Paid Search",      "$89,456",    "$105,554",   "401",         "$223.08",  "1.18×"),
        ("Retargeting",      "$24,112",    "$58,340",    "500",         "$48.20 ✔", "2.42×"),
        ("Social",           "$67,890",    "$54,732",    "218",         "$311.42",  "0.81×"),
        ("Display",          "$61,751",    "$22,746",    "199",         "$310.30",  "0.37×"),
        ("Email",            "$0",         "$36,607",    "140",         "$0.00",    "∞"),
    ]

    col_widths = [Inches(1.90), Inches(1.25), Inches(1.25), Inches(1.35), Inches(1.35), Inches(1.25)]
    col_starts = []
    cx = BODY_LEFT
    for cw in col_widths:
        col_starts.append(cx)
        cx = cx + cw

    row_h   = Inches(0.50)
    tbl_top = BODY_TOP + Inches(0.44)

    for ri, row in enumerate(cpa_data):
        for ci, cell in enumerate(row):
            ry = tbl_top + Inches(ri * 0.50)
            is_hdr   = ri == 0
            is_good  = "✔" in cell
            is_bad   = "0.37×" in cell or "0.81×" in cell
            bg = (PURPLE if is_hdr
                  else GREEN if is_good
                  else RGBColor(255, 225, 225) if is_bad
                  else (RGBColor(245, 242, 252) if ri % 2 == 0 else WHITE))
            fc = WHITE if (is_hdr or is_good) else (RED if is_bad else DARK_GRAY)
            add_rect(slide, col_starts[ci], ry, col_widths[ci], row_h,
                     fill_color=bg, line_color=L_PURPLE, line_width_pt=0.5)
            add_text(slide, cell,
                     left=col_starts[ci] + Inches(0.05), top=ry + Inches(0.08),
                     width=col_widths[ci] - Inches(0.08), height=row_h - Inches(0.10),
                     font_size=11, bold=is_hdr, color=fc, align=PP_ALIGN.CENTER)

    # Key insights
    ins_top = tbl_top + Inches(len(cpa_data) * 0.50) + Inches(0.25)
    insights = [
        "✔  Retargeting delivers the lowest CPA ($48.20) — 6× more efficient than Awareness campaigns.",
        "⚠  Display ($0.37× ROAS) and Social ($0.81× ROAS) channels are operating at a loss.",
        "➤  Recommendation: Reallocate 15–20% of Awareness/Display budget to Retargeting sequences.",
    ]
    colors_ins = [GREEN, RED, PURPLE]
    for j, (ins, col) in enumerate(zip(insights, colors_ins)):
        add_text(slide, ins,
                 left=BODY_LEFT, top=ins_top + Inches(j * 0.42),
                 width=BODY_WIDTH, height=Inches(0.38),
                 font_size=12, bold=False, color=col)

    add_footer(slide)
    return slide


# ===========================================================================
# SLIDE 11 — Customer Insights & Strategic Recommendations
# ===========================================================================
def slide_11_customer_recommendations(prs):
    slide = blank_slide(prs)
    add_rect(slide, 0, 0, SLIDE_W, SLIDE_H, fill_color=WHITE)
    add_title(slide, "Customer Insights & Strategic Business Recommendations")

    # Left: Device & Mobile Insights
    lc = Inches(0.55)
    lw = Inches(5.70)

    add_text(slide, "Customer & Device Segmentation",
             left=lc, top=BODY_TOP,
             width=lw, height=Inches(0.38),
             font_size=15, bold=True, color=PURPLE)

    device_data = [
        ("Mobile",  "56.4% sessions",  "42.1% checkout abandonment",  RGBColor(180, 30, 30)),
        ("Desktop", "35.8% sessions",  "22.3% checkout abandonment",  GREEN),
        ("Tablet",  " 7.8% sessions",  "31.5% checkout abandonment",  ORANGE),
    ]

    dev_top = BODY_TOP + Inches(0.50)
    for i, (dev, sess, abandon, color) in enumerate(device_data):
        dy = dev_top + Inches(i * 1.00)
        add_rect(slide, lc, dy, lw, Inches(0.88),
                 fill_color=RGBColor(248, 245, 255),
                 line_color=color, line_width_pt=1.5)
        add_rect(slide, lc, dy, Inches(0.20), Inches(0.88), fill_color=color)
        add_text(slide, dev,
                 left=lc + Inches(0.30), top=dy + Inches(0.06),
                 width=Inches(2.00), height=Inches(0.36),
                 font_size=13, bold=True, color=color)
        add_text(slide, sess,
                 left=lc + Inches(2.30), top=dy + Inches(0.06),
                 width=Inches(3.10), height=Inches(0.36),
                 font_size=12, color=DARK_GRAY)
        add_text(slide, abandon,
                 left=lc + Inches(0.30), top=dy + Inches(0.48),
                 width=Inches(5.20), height=Inches(0.32),
                 font_size=11, italic=True, color=DARK_GRAY)

    # Geographic note
    geo_top = dev_top + Inches(3.20)
    add_text(slide, "Top Markets: US (62%) | India (14%) | UK (8%) | Canada (5%) | Other (11%)",
             left=lc, top=geo_top,
             width=lw, height=Inches(0.38),
             font_size=12, bold=False, color=DARK_GRAY)
    add_text(slide, "Landing Page Insight: /products/apparel drives 34% of revenue but only 18% of sessions",
             left=lc, top=geo_top + Inches(0.44),
             width=lw, height=Inches(0.38),
             font_size=12, italic=True, color=PURPLE)

    # Right: Strategic Recommendations
    rc = Inches(6.80)
    rw = Inches(5.98)

    add_text(slide, "Strategic Recommendations",
             left=rc, top=BODY_TOP,
             width=rw, height=Inches(0.38),
             font_size=15, bold=True, color=PURPLE)

    recs = [
        ("Budget Reallocation",
         "Redirect 15–20% of awareness/display spend toward high-intent retargeting and cart-recovery email sequences.",
         PURPLE),
        ("Mobile Checkout Overhaul",
         "Redesign mobile checkout with one-click digital wallets (Apple Pay, Google Pay) to capture the 42.1% abandonment leakage.",
         RED),
        ("Product Discoverability",
         "Overhaul landing page product recommendation widgets to reduce the 54.3% Landing Page → Product View drop-off.",
         TEAL),
        ("Attribution Enhancement",
         "Move from single-touch to data-driven multi-touch attribution (MTA) for accurate cross-channel credit.",
         GREEN),
    ]

    rec_top = BODY_TOP + Inches(0.48)
    for i, (rec_title, rec_body, color) in enumerate(recs):
        ry = rec_top + Inches(i * 1.25)
        add_rect(slide, rc, ry, rw, Inches(1.15),
                 fill_color=RGBColor(248, 245, 255),
                 line_color=color, line_width_pt=1.5)
        add_rect(slide, rc, ry, Inches(0.22), Inches(1.15), fill_color=color)
        add_text(slide, rec_title,
                 left=rc + Inches(0.32), top=ry + Inches(0.06),
                 width=Inches(5.58), height=Inches(0.38),
                 font_size=13, bold=True, color=color)
        add_text(slide, rec_body,
                 left=rc + Inches(0.32), top=ry + Inches(0.50),
                 width=Inches(5.58), height=Inches(0.58),
                 font_size=11, color=DARK_GRAY)

    add_footer(slide)
    return slide


# ===========================================================================
# SLIDE 12 — Conclusion, Limitations, Future Scope & Thank You
# ===========================================================================
def slide_12_conclusion(prs):
    slide = blank_slide(prs)
    add_rect(slide, 0, 0, SLIDE_W, SLIDE_H, fill_color=WHITE)
    add_title(slide, "Conclusion, Limitations, Future Scope & Thank You")

    # Conclusion
    add_text(slide, "Project Conclusion",
             left=BODY_LEFT, top=BODY_TOP,
             width=Inches(5.70), height=Inches(0.36),
             font_size=15, bold=True, color=PURPLE)

    conclusion_tb = slide.shapes.add_textbox(BODY_LEFT, BODY_TOP + Inches(0.44),
                                              Inches(5.70), Inches(1.80))
    conclusion_tb.word_wrap = True
    ctf = conclusion_tb.text_frame
    ctf.word_wrap = True
    p0 = ctf.paragraphs[0]
    p0.add_run()

    conclusions = [
        "Delivered a complete, production-grade BI pipeline: GA4 → ETL → MySQL DW → Power BI.",
        "Quantified funnel leakage: 54.3% drop at Landing→Product View; $310+ CPA on Awareness channels.",
        "Validated 57,083 events through 34-point automated QA — zero silent data drops.",
        "Generated actionable recommendations with projected 15–20% budget efficiency improvement.",
    ]
    for c in conclusions:
        add_paragraph(ctf, c, font_size=12, bullet=True, color=DARK_GRAY, space_before_pt=5)

    # Limitations
    add_rect(slide, BODY_LEFT, BODY_TOP + Inches(2.38),
             Inches(5.70), Inches(1.50),
             fill_color=RGBColor(255, 245, 230), line_color=ORANGE, line_width_pt=1)
    add_text(slide, "Academic Limitations",
             left=BODY_LEFT + Inches(0.12), top=BODY_TOP + Inches(2.46),
             width=Inches(5.40), height=Inches(0.36),
             font_size=13, bold=True, color=ORANGE)

    limits = [
        "GA4 public export sample scope (synthetic data, not live production API)",
        "Single-touch top-of-funnel attribution vs. complex algorithmic MTA",
        "Unauthenticated external API integrations (Google Ads, Meta, HubSpot)",
    ]
    lim_tb = slide.shapes.add_textbox(BODY_LEFT + Inches(0.12), BODY_TOP + Inches(2.88),
                                       Inches(5.45), Inches(0.88))
    lim_tb.word_wrap = True
    ltf = lim_tb.text_frame
    ltf.word_wrap = True
    p0 = ltf.paragraphs[0]
    p0.add_run()
    for lim in limits:
        add_paragraph(ltf, lim, font_size=11, bullet=True, color=DARK_GRAY, space_before_pt=3)

    # Future Scope
    add_rect(slide, BODY_LEFT, BODY_TOP + Inches(4.00),
             Inches(5.70), Inches(1.30),
             fill_color=RGBColor(235, 250, 240), line_color=GREEN, line_width_pt=1)
    add_text(slide, "Future Scope",
             left=BODY_LEFT + Inches(0.12), top=BODY_TOP + Inches(4.08),
             width=Inches(5.45), height=Inches(0.36),
             font_size=13, bold=True, color=GREEN)

    future = [
        "ML churn prediction & Customer Lifetime Value (CLV) regression models",
        "Cloud DW migration: Snowflake / BigQuery for petabyte-scale analytics",
        "Real-time streaming pipeline via Apache Kafka + Spark Structured Streaming",
    ]
    fut_tb = slide.shapes.add_textbox(BODY_LEFT + Inches(0.12), BODY_TOP + Inches(4.48),
                                       Inches(5.45), Inches(0.75))
    fut_tb.word_wrap = True
    ftf = fut_tb.text_frame
    ftf.word_wrap = True
    p0 = ftf.paragraphs[0]
    p0.add_run()
    for f in future:
        add_paragraph(ftf, f, font_size=11, bullet=True, color=DARK_GRAY, space_before_pt=3)

    # Right: Thank You
    rc = Inches(6.80)
    add_rect(slide, rc, BODY_TOP, Inches(5.98), Inches(5.22),
             fill_color=PURPLE)

    add_text(slide, "Thank You !",
             left=rc, top=BODY_TOP + Inches(0.50),
             width=Inches(5.98), height=Inches(1.00),
             font_size=38, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    add_text(slide, "Questions & Discussion",
             left=rc, top=BODY_TOP + Inches(1.60),
             width=Inches(5.98), height=Inches(0.50),
             font_size=20, bold=False, color=WHITE, align=PP_ALIGN.CENTER, italic=True)

    add_rect(slide, rc + Inches(1.00), BODY_TOP + Inches(2.22),
             Inches(3.98), Inches(0.03),
             fill_color=L_PURPLE)

    details = [
        ("Student",  "Aman Yadav  |  Roll No. P-07"),
        ("Subject",  "Business Intelligence  (TAE-II — Winter 2026)"),
        ("Guide",    "Mrs. Vaishali Kapure"),
        ("Institute","G H Raisoni College of Engineering and Management"),
        ("Dept.",    "B.Tech CSE – Data Science"),
    ]
    det_top = BODY_TOP + Inches(2.40)
    for i, (k, v) in enumerate(details):
        dt = det_top + Inches(i * 0.54)
        add_text(slide, k + ":",
                 left=rc + Inches(0.30), top=dt,
                 width=Inches(0.95), height=Inches(0.44),
                 font_size=11, bold=True, color=L_PURPLE)
        add_text(slide, v,
                 left=rc + Inches(1.28), top=dt,
                 width=Inches(4.50), height=Inches(0.44),
                 font_size=11, color=WHITE)

    add_footer(slide)
    return slide


# ===========================================================================
# MAIN
# ===========================================================================
def main():
    print("=" * 65)
    print("  Cross-Channel Marketing Funnel Leakage Intelligence")
    print("  Academic PPTX Generator — python-pptx")
    print("=" * 65)

    prs = make_prs()

    build_steps = [
        ("Slide 1  — Title & Executive Summary",      slide_01_title),
        ("Slide 2  — Contents & Business Problem",    slide_02_contents),
        ("Slide 3  — Objectives & Funnel",            slide_03_objectives_funnel),
        ("Slide 4  — System Architecture",            slide_04_architecture),
        ("Slide 5  — Data Ingestion & ETL",           slide_05_ingestion_etl),
        ("Slide 6  — Data Quality Engine",            slide_06_quality),
        ("Slide 7  — Star Schema DW",                 slide_07_star_schema),
        ("Slide 8  — Power BI & DAX",                 slide_08_powerbi_dax),
        ("Slide 9  — Executive Dashboard",            slide_09_executive_dashboard),
        ("Slide 10 — Channel Attribution",            slide_10_attribution),
        ("Slide 11 — Customer Insights & Recs",       slide_11_customer_recommendations),
        ("Slide 12 — Conclusion & Thank You",         slide_12_conclusion),
    ]

    for label, func in build_steps:
        print(f"  Building {label} ...", end=" ", flush=True)
        func(prs)
        print("✓")

    prs.save(str(OUTPUT_PATH))
    print()
    print(f"  ✔  PPTX saved → {OUTPUT_PATH}")
    print(f"  ✔  Slides: {len(prs.slides)}")
    print("=" * 65)
    return str(OUTPUT_PATH)


if __name__ == "__main__":
    main()
