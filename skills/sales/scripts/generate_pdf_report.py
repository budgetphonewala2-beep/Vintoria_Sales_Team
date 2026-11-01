#!/usr/bin/env python3
"""
Sales Pipeline PDF Report Generator — AI Sales Team for Claude Code

Generates a professional, multi-page PDF sales pipeline report with score gauges,
bar charts, prospect cards, pipeline summary tables, and prioritized action plans.

Usage:
    python generate_pdf_report.py <json_data_file> [output_pdf_file]
    python generate_pdf_report.py --demo [output_pdf_file]   # sample report with fake data

Input schema: see skills/sales-report-pdf/SKILL.md. The script is tolerant: action_items
may be a list or a {quick_wins, this_week, this_month} object; categories, pipeline_health
and grades are derived from the prospects list when missing.
"""

import json
import sys
import os
from xml.sax.saxutils import escape as _xml_escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.graphics.shapes import Drawing, Circle, String, Wedge
from reportlab.graphics.charts.barcharts import HorizontalBarChart

# --- Color Palette (Sales-focused) ---
PRIMARY = colors.HexColor("#1B2A4A")       # dark navy
ACCENT = colors.HexColor("#0EA5E9")        # sales blue
HIGHLIGHT = colors.HexColor("#F59E0B")     # amber/gold for scores
SUCCESS = colors.HexColor("#10B981")       # green
WARNING = colors.HexColor("#F59E0B")       # amber
DANGER = colors.HexColor("#EF4444")        # red
LIGHT_BG = colors.HexColor("#F0F9FF")      # light blue tint
BODY_TEXT = colors.HexColor("#1E293B")
SECONDARY_TEXT = colors.HexColor("#64748B")
BORDER = colors.HexColor("#CBD5E1")
WHITE = colors.white
GRADE_A_BG = colors.HexColor("#ECFDF5")
GRADE_B_BG = colors.HexColor("#EFF6FF")
GRADE_C_BG = colors.HexColor("#FFFBEB")
GRADE_D_BG = colors.HexColor("#FEF2F2")
DARK_GREEN = colors.HexColor("#047857")

# Single grade scale shared by every skill, lead_scorer.py and this report.
GRADE_SCALE = [
    (90, "A+", "Hot Lead", "Prioritize immediately; multi-thread within 24 hours"),
    (75, "A", "Strong Prospect", "Personalized outreach within 48 hours"),
    (60, "B", "Qualified Lead", "Standard outreach sequence; watch for triggers"),
    (40, "C", "Lukewarm", "Nurture with value-add content; re-evaluate in 30-60 days"),
    (0, "D", "Poor Fit", "Deprioritize; long-term nurture only"),
]
DEFAULT_WEIGHTS = [
    ("Company Fit", 25, "Size, industry, growth trajectory, tech sophistication, budget signals"),
    ("Contact Access", 20, "Decision makers identified, contact quality, personalization, warm paths"),
    ("Opportunity Quality", 20, "BANT + MEDDIC: budget, authority, need severity, timeline urgency"),
    ("Competitive Position", 15, "Current solution, switching feasibility, exploitable gaps, win probability"),
    ("Outreach Readiness", 20, "Personalization, channel strategy, messaging fit, timing"),
]


def esc(value):
    """Escape user/LLM-provided text for reportlab Paragraph markup ('AT&T <Ent>' safe)."""
    return _xml_escape("" if value is None else str(value))


def to_score(value):
    try:
        return max(0, min(100, int(round(float(str(value).split("/")[0].strip())))))
    except (TypeError, ValueError):
        return 0


def grade_for(score):
    for floor, grade, *_ in GRADE_SCALE:
        if score >= floor:
            return grade
    return "D"


def score_color(score):
    """Return color based on score value."""
    if score >= 80:
        return SUCCESS
    elif score >= 60:
        return ACCENT
    elif score >= 40:
        return WARNING
    else:
        return DANGER


def grade_color(grade):
    """Return color based on letter grade."""
    grade_map = {"A+": DARK_GREEN, "A": SUCCESS, "B": ACCENT, "C": WARNING, "D": DANGER}
    return grade_map.get(grade, SECONDARY_TEXT)


def grade_bg(grade):
    """Return background color for grade."""
    bg_map = {"A+": GRADE_A_BG, "A": GRADE_A_BG, "B": GRADE_B_BG, "C": GRADE_C_BG, "D": GRADE_D_BG}
    return bg_map.get(grade, LIGHT_BG)


# ---------------------------------------------------------------------------
# Input normalisation — accept the documented schema and older/looser variants
# ---------------------------------------------------------------------------

_COMPONENT_LABELS = {
    "company_fit": "Company Fit", "contact_access": "Contact Access",
    "opportunity_quality": "Opportunity Quality", "competitive_position": "Competitive Position",
    "outreach_readiness": "Outreach Readiness",
}


def normalize_data(data):
    data = dict(data or {})

    # Prospects: numeric scores, derived grades, sorted best-first
    prospects = []
    for p in data.get("prospects") or []:
        if not isinstance(p, dict):
            continue
        p = dict(p)
        p["score"] = to_score(p.get("score"))
        g = str(p.get("grade") or "").strip().upper()
        p["grade"] = g if g in ("A+", "A", "B", "C", "D") else grade_for(p["score"])
        prospects.append(p)
    prospects.sort(key=lambda x: -x["score"])
    data["prospects"] = prospects

    # Overall score
    if data.get("overall_pipeline_score") is None and prospects:
        data["overall_pipeline_score"] = round(sum(p["score"] for p in prospects) / len(prospects))
    data["overall_pipeline_score"] = to_score(data.get("overall_pipeline_score", 0))

    # Categories for the bar chart: explicit, else averaged component scores
    cats = data.get("categories")
    if isinstance(cats, dict) and cats:
        data["categories"] = {k: {"score": to_score(v.get("score") if isinstance(v, dict) else v)}
                              for k, v in cats.items()}
    else:
        sums, counts = {}, {}
        for p in prospects:
            for k, v in (p.get("component_scores") or {}).items():
                label = _COMPONENT_LABELS.get(k, k.replace("_", " ").title())
                sums[label] = sums.get(label, 0) + to_score(v)
                counts[label] = counts.get(label, 0) + 1
        data["categories"] = {k: {"score": round(sums[k] / counts[k])} for k in sums}

    # Pipeline health: fill anything missing from the prospects list
    ph = dict(data.get("pipeline_health") or {})
    counts = {g: sum(1 for p in prospects if p["grade"] == g) for g in ("A+", "A", "B", "C", "D")}
    ph.setdefault("total_prospects", data.get("total_prospects") or len(prospects))
    ph.setdefault("avg_score", ph.get("average_score",
                  round(sum(p["score"] for p in prospects) / len(prospects)) if prospects else 0))
    for g, key in (("A+", "a_plus_grade"), ("A", "a_grade"), ("B", "b_grade"), ("C", "c_grade"), ("D", "d_grade")):
        ph.setdefault(key, ph.get(f"{key}_count", counts[g]))
    if data.get("health_rating"):
        ph.setdefault("health_rating", data["health_rating"])
    data["pipeline_health"] = ph

    # Action items: dict of buckets, or a flat list of strings / objects
    ai = data.get("action_items")
    buckets = {"quick_wins": [], "this_week": [], "this_month": []}
    if isinstance(ai, dict):
        for k in buckets:
            buckets[k] = [_action_text(x) for x in ai.get(k) or []]
    elif isinstance(ai, list):
        for x in ai:
            urgency = str(x.get("urgency", "")).lower() if isinstance(x, dict) else ""
            key = ("quick_wins" if urgency in ("immediate", "today", "urgent", "high", "now")
                   else "this_month" if urgency in ("this month", "month", "low", "long-term", "pipeline building")
                   else "this_week")
            buckets[key].append(_action_text(x))
    data["action_items"] = buckets
    return data


def _action_text(x):
    if isinstance(x, dict):
        action = x.get("action") or x.get("task") or ""
        company = x.get("company")
        reason = x.get("reason")
        text = f"<b>{esc(company)}:</b> {esc(action)}" if company else esc(action)
        return text + (f" <i>— {esc(reason)}</i>" if reason else "")
    return esc(x)


def build_styles():
    """Build all paragraph styles for the report."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=28,
        textColor=PRIMARY,
        alignment=TA_LEFT,
        spaceAfter=6,
        leading=34,
    ))
    styles.add(ParagraphStyle(
        name="CoverSubtitle",
        fontName="Helvetica",
        fontSize=14,
        textColor=SECONDARY_TEXT,
        alignment=TA_LEFT,
        spaceAfter=4,
        leading=18,
    ))
    styles.add(ParagraphStyle(
        name="SectionTitle",
        fontName="Helvetica-Bold",
        fontSize=20,
        textColor=PRIMARY,
        spaceBefore=12,
        spaceAfter=10,
        leading=26,
    ))
    styles.add(ParagraphStyle(
        name="SubSection",
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=PRIMARY,
        spaceBefore=10,
        spaceAfter=6,
        leading=17,
    ))
    styles.add(ParagraphStyle(
        name="BodyText2",
        fontName="Helvetica",
        fontSize=10,
        textColor=BODY_TEXT,
        spaceAfter=6,
        leading=14,
    ))
    styles.add(ParagraphStyle(
        name="SmallText",
        fontName="Helvetica",
        fontSize=8,
        textColor=SECONDARY_TEXT,
        leading=10,
    ))
    styles.add(ParagraphStyle(
        name="TableCell",
        fontName="Helvetica",
        fontSize=9,
        textColor=BODY_TEXT,
        leading=12,
    ))
    styles.add(ParagraphStyle(
        name="TableHeader",
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=WHITE,
        leading=12,
    ))
    styles.add(ParagraphStyle(
        name="ActionItem",
        fontName="Helvetica",
        fontSize=10,
        textColor=BODY_TEXT,
        leftIndent=20,
        spaceAfter=4,
        leading=13,
    ))
    styles.add(ParagraphStyle(
        name="ProspectName",
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=PRIMARY,
        spaceAfter=2,
        leading=15,
    ))
    styles.add(ParagraphStyle(
        name="ProspectDetail",
        fontName="Helvetica",
        fontSize=9,
        textColor=BODY_TEXT,
        leading=12,
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name="FooterText",
        fontName="Helvetica",
        fontSize=7,
        textColor=SECONDARY_TEXT,
        alignment=TA_CENTER,
    ))
    return styles


def draw_score_gauge(score, size=180):
    """Draw a circular score gauge with colored ring and score number in center."""
    d = Drawing(size, size + 20)
    cx, cy = size / 2, size / 2 + 10
    radius = size / 2 - 10

    # Background circle (track)
    d.add(Circle(cx, cy, radius, fillColor=LIGHT_BG, strokeColor=BORDER, strokeWidth=2))

    # Score arc
    col = score_color(score)
    angle_extent = (score / 100) * 360
    if angle_extent > 0:
        d.add(Wedge(cx, cy, radius, 90, 90 - angle_extent,
                     fillColor=col, strokeColor=col, strokeWidth=0))

    # Inner white circle to create donut effect
    inner_r = radius * 0.65
    d.add(Circle(cx, cy, inner_r, fillColor=WHITE, strokeColor=WHITE, strokeWidth=0))

    # Score number
    d.add(String(cx, cy + 8, str(score),
                 fontSize=36, fontName="Helvetica-Bold",
                 fillColor=PRIMARY, textAnchor="middle"))
    d.add(String(cx, cy - 12, "Pipeline Score",
                 fontSize=9, fontName="Helvetica",
                 fillColor=SECONDARY_TEXT, textAnchor="middle"))

    grade = grade_for(score)

    d.add(String(cx, cy - 30, f"Grade: {grade}",
                 fontSize=12, fontName="Helvetica-Bold",
                 fillColor=col, textAnchor="middle"))

    return d


def create_bar_chart(categories, width=480, height=200):
    """Draw a horizontal bar chart for category scores."""
    d = Drawing(width, height)

    names = list(categories.keys())
    scores = [categories[n]["score"] for n in names]

    chart = HorizontalBarChart()
    chart.x = 160
    chart.y = 10
    chart.width = width - 180
    chart.height = height - 20
    chart.data = [scores]
    chart.categoryAxis.categoryNames = names
    chart.categoryAxis.labels.fontName = "Helvetica"
    chart.categoryAxis.labels.fontSize = 8
    chart.categoryAxis.labels.fillColor = BODY_TEXT
    chart.categoryAxis.visibleGrid = False
    chart.categoryAxis.visibleAxis = False
    chart.categoryAxis.visibleTicks = False

    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = 100
    chart.valueAxis.valueStep = 20
    chart.valueAxis.labels.fontName = "Helvetica"
    chart.valueAxis.labels.fontSize = 7
    chart.valueAxis.labels.fillColor = SECONDARY_TEXT
    chart.valueAxis.visibleGrid = True
    chart.valueAxis.gridStrokeColor = BORDER
    chart.valueAxis.gridStrokeWidth = 0.5
    chart.valueAxis.visibleAxis = False
    chart.valueAxis.visibleTicks = False

    chart.bars[0].fillColor = ACCENT
    chart.barWidth = 14
    chart.barSpacing = 6

    # Color each bar by score
    bar_colors = [score_color(s) for s in scores]
    for i, col in enumerate(bar_colors):
        chart.bars[(0, i)].fillColor = col

    d.add(chart)

    # Add score labels at end of each bar
    bar_total_height = len(names) * (chart.barWidth + chart.barSpacing)
    start_y = chart.y + (chart.height - bar_total_height) / 2
    for i, s in enumerate(scores):
        bar_y = start_y + i * (chart.barWidth + chart.barSpacing) + chart.barWidth / 2
        bar_end_x = chart.x + (s / 100) * chart.width + 4
        d.add(String(bar_end_x, bar_y - 3, str(s),
                     fontSize=8, fontName="Helvetica-Bold",
                     fillColor=score_color(s), textAnchor="start"))

    return d


def add_header_footer(canvas, doc, report_title=""):
    """Add header and footer to each page."""
    canvas.saveState()
    # Header line
    canvas.setStrokeColor(ACCENT)
    canvas.setLineWidth(2)
    canvas.line(54, letter[1] - 40, letter[0] - 54, letter[1] - 40)

    # Header text
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(PRIMARY)
    canvas.drawString(54, letter[1] - 35, f"Sales Pipeline Report — {report_title}")

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(SECONDARY_TEXT)
    canvas.drawRightString(letter[0] - 54, letter[1] - 35, f"Page {doc.page}")

    # Footer line
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(54, 40, letter[0] - 54, 40)

    # Footer text
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(SECONDARY_TEXT)
    canvas.drawCentredString(letter[0] / 2, 28,
                              "Generated by AI Sales Team for Claude Code")
    canvas.restoreState()


def generate_report(data, output_path):
    """Generate the full PDF report from data dict."""
    styles = build_styles()
    data = normalize_data(data)
    report_date = esc(data.get("date", ""))
    report_title = esc(data.get("title") or "Sales Pipeline Report")

    out_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(out_dir, exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    story = []

    # ==================== PAGE 1: COVER ====================
    story.append(Spacer(1, 1.2 * inch))
    story.append(Paragraph(report_title, styles["CoverTitle"]))
    story.append(Spacer(1, 40))
    story.append(Paragraph(f"<b>{report_date}</b>", styles["CoverSubtitle"]))

    pipeline_health = data.get("pipeline_health", {})
    total_prospects = pipeline_health.get("total_prospects", 0)
    if total_prospects:
        story.append(Spacer(1, 30))
        rating = pipeline_health.get("health_rating")
        line = f"{esc(total_prospects)} Prospects Analyzed"
        if rating:
            line += f" &nbsp;·&nbsp; Pipeline Health: <b>{esc(rating)}</b>"
        story.append(Paragraph(line, styles["CoverSubtitle"]))
    story.append(Spacer(1, 60))

    # Overall pipeline score gauge
    overall_score = data.get("overall_pipeline_score", 0)
    gauge = draw_score_gauge(overall_score)
    story.append(gauge)
    story.append(Spacer(1, 40))

    # Executive Summary
    summary = data.get("executive_summary", "")
    if summary:
        story.append(Paragraph("Executive Summary", styles["SubSection"]))
        story.append(Paragraph(esc(summary), styles["BodyText2"]))

    story.append(PageBreak())

    # ==================== PAGE 2: SCORE BREAKDOWN ====================
    story.append(Paragraph("Score Breakdown", styles["SectionTitle"]))
    story.append(Spacer(1, 6))

    categories = data.get("categories", {})
    if categories:
        chart = create_bar_chart(categories)
        story.append(chart)
        story.append(Spacer(1, 16))

        # Score comparison table
        header = [
            Paragraph("<b>Category</b>", styles["TableHeader"]),
            Paragraph("<b>Score</b>", styles["TableHeader"]),
            Paragraph("<b>Status</b>", styles["TableHeader"]),
        ]
        table_data = [header]

        for cat_name, cat_info in categories.items():
            s = cat_info.get("score", 0)
            col = score_color(s)
            hex_col = col.hexval() if hasattr(col, 'hexval') else str(col)
            if s >= 80:
                label = "Strong"
            elif s >= 60:
                label = "Good"
            elif s >= 40:
                label = "Needs Work"
            else:
                label = "Critical"

            table_data.append([
                Paragraph(esc(cat_name), styles["TableCell"]),
                Paragraph(f"<b>{s}/100</b>", styles["TableCell"]),
                Paragraph(f'<font color="{hex_col}"><b>{label}</b></font>', styles["TableCell"]),
            ])

        # Overall row
        overall_col = score_color(overall_score)
        hex_overall = overall_col.hexval() if hasattr(overall_col, 'hexval') else str(overall_col)
        table_data.append([
            Paragraph("<b>OVERALL PIPELINE</b>", styles["TableCell"]),
            Paragraph(f"<b>{overall_score}/100</b>", styles["TableCell"]),
            Paragraph(f'<font color="{hex_overall}"><b>Pipeline Score</b></font>', styles["TableCell"]),
        ])

        col_widths = [200, 100, 100]
        t = Table(table_data, colWidths=col_widths)
        t_style = [
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
            ("TOPPADDING", (0, 1), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("BACKGROUND", (0, -1), (-1, -1), LIGHT_BG),
        ]
        for i in range(1, len(table_data) - 1):
            if i % 2 == 0:
                t_style.append(("BACKGROUND", (0, i), (-1, i), LIGHT_BG))
        t.setStyle(TableStyle(t_style))
        story.append(t)

    story.append(PageBreak())

    # ==================== PAGE 3: TOP PROSPECTS ====================
    prospects = data.get("prospects", [])
    if prospects:
        story.append(Paragraph("Top Prospects", styles["SectionTitle"]))
        story.append(Spacer(1, 6))

        # Show top 5 as detailed cards
        for i, prospect in enumerate(prospects[:5]):
            name = esc(prospect.get("name", "Unknown"))
            p_score = prospect.get("score", 0)
            p_grade = prospect.get("grade", "?")
            stage = esc(prospect.get("stage") or "N/A")
            url = esc(prospect.get("url", ""))
            next_action = esc(prospect.get("next_action", ""))
            extras = [f"{label}: <b>{esc(prospect[k])}</b>" for k, label in
                      (("key_contact", "Contact"), ("est_value", "Est. value"),
                       ("key_pain_point", "Pain"), ("risk_factors", "Risk")) if prospect.get(k)]

            col = score_color(p_score)
            hex_col = col.hexval() if hasattr(col, 'hexval') else str(col)
            g_col = grade_color(p_grade)
            hex_g = g_col.hexval() if hasattr(g_col, 'hexval') else str(g_col)

            # Prospect card as a mini table
            card_data = [
                [
                    Paragraph(f'<b>{i+1}. {name}</b>', styles["ProspectName"]),
                    Paragraph(f'<font color="{hex_col}" size="14"><b>{p_score}</b></font>', styles["TableCell"]),
                    Paragraph(f'<font color="{hex_g}" size="12"><b>{p_grade}</b></font>', styles["TableCell"]),
                ],
                [
                    Paragraph(f'Stage: <b>{stage}</b> &nbsp;&nbsp; {url}', styles["ProspectDetail"]),
                    Paragraph("Score", styles["SmallText"]),
                    Paragraph("Grade", styles["SmallText"]),
                ],
            ]
            full_rows = []
            for extra in extras:
                card_data.append([Paragraph(extra, styles["ProspectDetail"]), "", ""])
                full_rows.append(len(card_data) - 1)
            if next_action:
                card_data.append([Paragraph(f'Next: <i>{next_action}</i>', styles["ProspectDetail"]), "", ""])
                full_rows.append(len(card_data) - 1)

            card = Table(card_data, colWidths=[340, 50, 50])
            card_style = [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                *[("SPAN", (0, r), (-1, r)) for r in full_rows],
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOX", (0, 0), (-1, -1), 1, BORDER),
                ("BACKGROUND", (0, 0), (-1, -1), grade_bg(p_grade)),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ]
            card.setStyle(TableStyle(card_style))
            story.append(KeepTogether([card, Spacer(1, 8)]))

    story.append(PageBreak())

    # ==================== PAGE 4: PIPELINE SUMMARY ====================
    if prospects:
        story.append(Paragraph("Pipeline Summary", styles["SectionTitle"]))
        story.append(Spacer(1, 6))

        header = [
            Paragraph("<b>Company</b>", styles["TableHeader"]),
            Paragraph("<b>Score</b>", styles["TableHeader"]),
            Paragraph("<b>Grade</b>", styles["TableHeader"]),
            Paragraph("<b>Stage</b>", styles["TableHeader"]),
            Paragraph("<b>Next Action</b>", styles["TableHeader"]),
        ]
        table_data = [header]

        for prospect in prospects:
            p_score = prospect.get("score", 0)
            p_grade = prospect.get("grade", "?")
            col = score_color(p_score)
            hex_col = col.hexval() if hasattr(col, 'hexval') else str(col)
            g_col = grade_color(p_grade)
            hex_g = g_col.hexval() if hasattr(g_col, 'hexval') else str(g_col)

            table_data.append([
                Paragraph(esc(prospect.get("name", "")), styles["TableCell"]),
                Paragraph(f'<font color="{hex_col}"><b>{p_score}</b></font>', styles["TableCell"]),
                Paragraph(f'<font color="{hex_g}"><b>{p_grade}</b></font>', styles["TableCell"]),
                Paragraph(esc(prospect.get("stage") or "N/A"), styles["TableCell"]),
                Paragraph(esc(prospect.get("next_action") or "N/A"), styles["TableCell"]),
            ])

        col_widths = [110, 45, 40, 80, 225]
        t = Table(table_data, colWidths=col_widths)
        t_style = [
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("ALIGN", (1, 0), (2, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
            ("TOPPADDING", (0, 1), (-1, -1), 5),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ]
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                t_style.append(("BACKGROUND", (0, i), (-1, i), LIGHT_BG))
        t.setStyle(TableStyle(t_style))
        story.append(t)

        # Pipeline health summary
        if pipeline_health:
            story.append(Spacer(1, 16))
            story.append(Paragraph("Pipeline Health", styles["SubSection"]))

            cols = [("Total", "total_prospects"), ("Avg Score", "avg_score"), ("A+", "a_plus_grade"),
                    ("A", "a_grade"), ("B", "b_grade"), ("C", "c_grade"), ("D", "d_grade")]
            health_data = [
                [Paragraph(f"<b>{label}</b>", styles["TableCell"]) for label, _ in cols],
                [Paragraph(esc(pipeline_health.get(key, 0)), styles["TableCell"]) for _, key in cols],
            ]
            ht = Table(health_data, colWidths=[72] * 7)
            ht_style = [
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ]
            ht.setStyle(TableStyle(ht_style))
            story.append(ht)

    story.append(PageBreak())

    # ==================== PAGE 5: ACTION PLAN ====================
    story.append(Paragraph("Action Plan", styles["SectionTitle"]))
    story.append(Spacer(1, 8))

    action_items = data.get("action_items", {})

    # This week's focus (ranked accounts with their actions)
    weekly_focus = [w for w in (data.get("weekly_focus") or []) if isinstance(w, dict)]
    if weekly_focus:
        story.append(Paragraph("This Week's Focus Accounts", styles["SubSection"]))
        for n, w in enumerate(weekly_focus[:5], 1):
            rank = esc(w.get("rank", n))
            head = f'<b>{rank}. {esc(w.get("company", ""))}</b>'
            if w.get("score") is not None:
                head += f' &nbsp;({esc(w.get("score"))}/100)'
            if w.get("reason"):
                head += f' — <i>{esc(w["reason"])}</i>'
            story.append(Paragraph(head, styles["ActionItem"]))
            for act in w.get("actions") or []:
                story.append(Paragraph(f"&bull; {esc(act)}", styles["ActionItem"]))
        story.append(Spacer(1, 12))

    if not weekly_focus and not any(action_items.get(k) for k in ("quick_wins", "this_week", "this_month")):
        story.append(Paragraph("No action items provided.", styles["BodyText2"]))

    # Quick Wins
    quick_wins = action_items.get("quick_wins", [])
    if quick_wins:
        story.append(Paragraph("Quick Wins (Immediate)", styles["SubSection"]))
        for i, item in enumerate(quick_wins, 1):
            col_hex = SUCCESS.hexval() if hasattr(SUCCESS, 'hexval') else str(SUCCESS)
            story.append(Paragraph(
                f'<font color="{col_hex}"><b>{i}.</b></font> {item}', styles["ActionItem"]
            ))
        story.append(Spacer(1, 12))

    # This Week
    this_week = action_items.get("this_week", [])
    if this_week:
        story.append(Paragraph("This Week", styles["SubSection"]))
        for i, item in enumerate(this_week, 1):
            col_hex = ACCENT.hexval() if hasattr(ACCENT, 'hexval') else str(ACCENT)
            story.append(Paragraph(
                f'<font color="{col_hex}"><b>{i}.</b></font> {item}', styles["ActionItem"]
            ))
        story.append(Spacer(1, 12))

    # This Month
    this_month = action_items.get("this_month", [])
    if this_month:
        story.append(Paragraph("This Month", styles["SubSection"]))
        for i, item in enumerate(this_month, 1):
            col_hex = WARNING.hexval() if hasattr(WARNING, 'hexval') else str(WARNING)
            story.append(Paragraph(
                f'<font color="{col_hex}"><b>{i}.</b></font> {item}', styles["ActionItem"]
            ))

    story.append(PageBreak())

    # ==================== PAGE 6: METHODOLOGY ====================
    story.append(Paragraph("Scoring Methodology", styles["SectionTitle"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "Each prospect receives a composite Prospect Score (0-100): a weighted average of five "
        "category scores, each produced by a dedicated research agent from publicly available "
        "information. Opportunity Quality incorporates BANT and MEDDIC qualification. Scores are "
        "evidence-based estimates, not guarantees — verify key facts in discovery.",
        styles["BodyText2"]
    ))
    story.append(Spacer(1, 10))

    # Methodology table — weights from the input if provided
    method_header = [
        Paragraph("<b>Category</b>", styles["TableHeader"]),
        Paragraph("<b>Weight</b>", styles["TableHeader"]),
        Paragraph("<b>Signals Measured</b>", styles["TableHeader"]),
    ]
    method_data = [method_header]
    weights_in = data.get("methodology") or {}
    for label, default_w, desc in DEFAULT_WEIGHTS:
        key = label.lower().replace(" ", "_") + "_weight"
        w = weights_in.get(key, default_w)
        method_data.append([
            Paragraph(f"<b>{esc(label)}</b>", styles["TableCell"]),
            Paragraph(f"{esc(w)}%", styles["TableCell"]),
            Paragraph(esc(desc), styles["TableCell"]),
        ])

    t = Table(method_data, colWidths=[100, 60, 340])
    t_style = [
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
        ("TOPPADDING", (0, 1), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
    ]
    for i in range(1, len(method_data)):
        if i % 2 == 0:
            t_style.append(("BACKGROUND", (0, i), (-1, i), LIGHT_BG))
    t.setStyle(TableStyle(t_style))
    story.append(t)

    story.append(Spacer(1, 16))

    # Grade scale
    story.append(Paragraph("Grade Scale", styles["SubSection"]))

    grade_header = [
        Paragraph("<b>Score Range</b>", styles["TableHeader"]),
        Paragraph("<b>Grade</b>", styles["TableHeader"]),
        Paragraph("<b>Interpretation</b>", styles["TableHeader"]),
        Paragraph("<b>Recommended Action</b>", styles["TableHeader"]),
    ]
    grade_data = [grade_header]
    grade_rows = []
    upper = 100
    for floor, grade, label, action in GRADE_SCALE:
        grade_rows.append((f"{floor}-{upper}", grade, label, action))
        upper = floor - 1
    for score_range, grade, interp, action in grade_rows:
        g_col = grade_color(grade)
        hex_g = g_col.hexval() if hasattr(g_col, 'hexval') else str(g_col)
        grade_data.append([
            Paragraph(score_range, styles["TableCell"]),
            Paragraph(f'<font color="{hex_g}"><b>{grade}</b></font>', styles["TableCell"]),
            Paragraph(interp, styles["TableCell"]),
            Paragraph(action, styles["TableCell"]),
        ])

    t = Table(grade_data, colWidths=[80, 50, 130, 240])
    t_style = [
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("ALIGN", (0, 0), (1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
        ("TOPPADDING", (0, 1), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
    ]
    t.setStyle(TableStyle(t_style))
    story.append(t)

    # Build PDF
    doc.build(
        story,
        onFirstPage=lambda c, d: add_header_footer(c, d, report_date),
        onLaterPages=lambda c, d: add_header_footer(c, d, report_date),
    )

    return output_path


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--demo", "-d"):
        # Demo mode — generate sample report with clearly fictional data
        sample_data = {
            "date": "March 6, 2026",
            "overall_pipeline_score": 72,
            "executive_summary": (
                "Our pipeline shows strong momentum with 12 active prospects across multiple stages. "
                "Three A-grade prospects are ready for immediate engagement, while five B-grade "
                "prospects show strong potential with targeted nurturing. Key areas for improvement "
                "include deepening contact access and strengthening competitive positioning intelligence."
            ),
            "prospects": [
                {"name": "TechFlow Inc", "url": "https://techflow.io", "score": 92, "stage": "Discovery Call", "next_action": "Schedule demo with VP Engineering"},
                {"name": "DataBridge Corp", "url": "https://databridge.com", "score": 85, "stage": "Qualified", "next_action": "Send proposal with 3-tier pricing"},
                {"name": "CloudScale AI", "url": "https://cloudscale.ai", "score": 78, "stage": "Engaged", "next_action": "Connect with CTO via warm intro"},
                {"name": "FinanceHub Pro", "url": "https://financehub.pro", "score": 71, "stage": "Researching", "next_action": "Send cold outreach sequence"},
                {"name": "RetailEdge", "url": "https://retailedge.com", "score": 68, "stage": "Nurturing", "next_action": "Share case study from similar company"},
                {"name": "SecureNet Labs", "url": "https://securenet.io", "score": 65, "stage": "Qualified", "next_action": "Prepare meeting brief for next call"},
                {"name": "EduPlatform", "url": "https://eduplatform.co", "score": 62, "stage": "Engaged", "next_action": "Follow up on pricing discussion"},
                {"name": "GreenEnergy AI", "url": "https://greenenergy.ai", "score": 58, "stage": "Researching", "next_action": "Identify decision makers"},
                {"name": "MediaStack", "url": "https://mediastack.io", "score": 45, "stage": "Initial Research", "next_action": "Complete prospect analysis"},
                {"name": "LogiTrack", "url": "https://logitrack.com", "score": 42, "stage": "Cold", "next_action": "Research company and find contacts"},
                {"name": "HealthFirst", "url": "https://healthfirst.com", "score": 38, "stage": "Cold", "next_action": "Validate ICP fit before outreach"},
                {"name": "BuildCo Tools", "url": "https://buildco.tools", "score": 22, "stage": "Unqualified", "next_action": "Add to long-term nurture list"},
            ],
            "categories": {
                "Company Fit": {"score": 75},
                "Contact Access": {"score": 68},
                "Need Alignment": {"score": 82},
                "Budget Signals": {"score": 70},
                "Timeline Signals": {"score": 58},
                "Competitive Position": {"score": 63},
            },
            "action_items": {
                "quick_wins": [
                    "Send personalized outreach to TechFlow VP Engineering (A-grade, ready for demo)",
                    "Prepare and send 3-tier proposal to DataBridge Corp",
                    "Request warm intro to CloudScale CTO via mutual connection",
                ],
                "this_week": [
                    "Launch cold outreach sequence for FinanceHub Pro",
                    "Create tailored case study for RetailEdge (retail vertical)",
                    "Complete meeting prep brief for SecureNet Labs call",
                    "Map decision-making committee at EduPlatform",
                ],
                "this_month": [
                    "Run full prospect analysis on MediaStack and LogiTrack",
                    "Build competitive battle cards for top 3 competitors",
                    "Develop vertical-specific value props for Healthcare and Education",
                    "Review and refresh ICP based on pipeline learnings",
                    "Establish referral network for warm introductions",
                ],
            },
            "pipeline_health": {"health_rating": "Good"},
            "title": "Sales Pipeline Report (SAMPLE DATA)",
        }
        output = sys.argv[2] if len(sys.argv) > 2 else "SALES-REPORT-sample.pdf"
        generate_report(sample_data, output)
        print(f"Sample report generated: {os.path.abspath(output)}")
        return

    json_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "SALES-REPORT.pdf"

    try:
        with open(json_path, "r", encoding="utf-8-sig") as f:  # tolerate BOM (PowerShell)
            data = json.load(f)
    except FileNotFoundError:
        sys.exit(f"Error: input file not found: {json_path}")
    except json.JSONDecodeError as exc:
        sys.exit(f"Error: invalid JSON in {json_path}: {exc}")
    if not isinstance(data, dict):
        sys.exit("Error: input JSON must be an object")

    generate_report(data, output_path)
    size_kb = os.path.getsize(output_path) / 1024
    print(f"Report generated: {os.path.abspath(output_path)} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
