---
name: sales-report-pdf
description: "Turns SALES-REPORT.md into a professional PDF pipeline report (gauges, charts, tables) via the bundled ReportLab script; writes SALES-REPORT-<date>.pdf. Use for /sales report-pdf or when the user wants the pipeline report as a PDF."
---
# Professional Sales Report PDF Generator

## Metadata
- **Title:** Professional Sales Report PDF Generator
- **Invocation:** `/sales report-pdf`
- **Input:** None (reads SALES-REPORT.md and prospect files from current directory)
- **Output:** `SALES-REPORT-{YYYY-MM-DD}.pdf` written to the current working directory
- **Dependencies:** Python 3, `reportlab`, and the bundled script `$HOME/.claude/skills/sales/scripts/generate_pdf_report.py`

<!-- shared-conventions v2 -->
## Shared Conventions (apply before anything else)

1. **Prospect folder.** Per-prospect files never go in the working-directory root. They live in `prospects/<slug>/`:
`PROSPECT-ANALYSIS.md`, `COMPANY-RESEARCH.md`, `LEAD-QUALIFICATION.md`, `DECISION-MAKERS.md`, `COMPETITIVE-INTEL.md`, `OUTREACH-SEQUENCE.md`, `FOLLOWUP-SEQUENCE.md`, `MEETING-PREP.md`, `CLIENT-PROPOSAL.md`.
- `<slug>` = the prospect's domain, lowercase, without protocol, `www.`, path or trailing slash (`https://www.Acme.com/about` → `acme.com`).
- Given a company name instead of a URL: first look for an existing `prospects/*/` folder for it (folder name, or the `**URL:**` / title line inside its files). If none exists, find the official domain with WebSearch and use that. Only if no domain can be found, use the kebab-case name (`acme-corp`).
- Whenever this skill says to read or write one of those files — including "if `X.md` exists" — it means `prospects/<slug>/X.md` for **this prospect only**. Never use another prospect's folder as context. Create the folder if needed.
- Shared files stay in the working-directory root: `IDEAL-CUSTOMER-PROFILE.md`, `OBJECTION-PLAYBOOK.md`, `SALES-REPORT.md`, `SALES-REPORT-*.pdf`.

2. **Helper scripts** are installed in `$HOME/.claude/skills/sales/scripts/`. Run them with `python` on Windows (where `python3` is often a Microsoft Store stub) or `python3` on macOS/Linux — use whichever prints a real version for `--version`. Example: `python "$HOME/.claude/skills/sales/scripts/analyze_prospect.py" --url https://acme.com`. Script output is heuristic: treat it as leads to verify, not facts.

---

---

## Purpose

You generate a professional, visually polished PDF version of the sales pipeline report. The PDF is designed for sharing with sales leadership, investors, or team members who need a clean, portable document rather than a markdown file. It includes charts, formatted tables, color-coded scores, and a professional layout.

---

## Instructions

When the user invokes `/sales report-pdf`, follow this process:

### Step 1: Verify Prerequisites

Check that `SALES-REPORT.md` exists in the current working directory.

**If SALES-REPORT.md does NOT exist:**
- Inform the user: "No SALES-REPORT.md found. Run `/sales report` first to generate the pipeline report, then run `/sales report-pdf` to create the PDF version."
- Stop execution.

**If SALES-REPORT.md exists:**
- Read its contents
- Also read the per-prospect files in `prospects/*/` (`PROSPECT-ANALYSIS.md`, `COMPANY-RESEARCH.md`, etc.) to enrich the PDF with additional detail

### Step 2: Check Python and reportlab

Find a working Python (on Windows `python3` is often a Microsoft Store stub that prints "Python was not found"):

```bash
python -c "import reportlab, sys; print(sys.version.split()[0], reportlab.Version)"   # Windows
python3 -c "import reportlab, sys; print(sys.version.split()[0], reportlab.Version)"  # macOS/Linux
```

Use whichever command succeeds as `<python>` below.

- **reportlab missing:** tell the user it's required and offer to run `<python> -m pip install reportlab`, then continue.
- **No Python at all:** tell the user to install Python 3 from https://python.org, then stop.

### Step 3: Parse Report Data

Extract the following data from `SALES-REPORT.md` and any prospect analysis files:

#### Pipeline Overview Data
- Report generation date
- Total number of prospects
- Average pipeline score (0-100)
- Overall pipeline health assessment

#### Prospect Data Array
For each prospect, extract into a structured object:
```json
{
  "name": "Company Name",
  "url": "https://company.com",
  "score": 85,
  "grade": "A",
  "stage": "Qualified",
  "next_action": "Send intro email to VP Engineering",
  "est_value": "$24,000 ARR",
  "component_scores": {
    "company_fit": 88,
    "contact_access": 75,
    "opportunity_quality": 90,
    "competitive_position": 82,
    "outreach_readiness": 80
  },
  "key_pain_point": "Manual API monitoring causing outages",
  "key_contact": "Jane Smith, VP Engineering",
  "risk_factors": "Long procurement cycle"
}
```

#### Top Prospects Data
For the top 5 prospects, extract detailed data including:
- Full component score breakdown
- Key contacts with titles
- Pain points with severity
- Recommended approach
- Risk factors

#### Action Items
Extract the prioritized action list:
```json
[
  {
    "priority": 1,
    "company": "Acme Corp",
    "action": "Send personalized email to VP Engineering",
    "urgency": "immediate",
    "reason": "Recent funding round creates budget window"
  }
]
```

#### Pipeline Health Metrics
```json
{
  "total_prospects": 10,
  "average_score": 72,
  "a_grade_count": 3,
  "a_grade_pct": 30,
  "b_grade_count": 4,
  "b_grade_pct": 40,
  "c_grade_count": 2,
  "c_grade_pct": 20,
  "d_grade_count": 1,
  "d_grade_pct": 10,
  "highest_score": 92,
  "lowest_score": 35,
  "health_rating": "Good"
}
```

### Step 4: Build JSON Input File
<!-- PDF-INPUT-SCHEMA v2 -->

Write `_pdf_input.json` in the working directory, **exactly in this shape** (it is what the script reads). Every field except `prospects` is optional — omit unknowns rather than inventing them; the script derives grades, averages, grade counts and category averages from `prospects` when they're missing.

```json
{
  "title": "Sales Pipeline Report",
  "date": "2026-11-01",
  "executive_summary": "2-4 sentence plain-text summary.",
  "overall_pipeline_score": 72,
  "health_rating": "Good",
  "prospects": [
    {
      "name": "Acme Corp",
      "url": "https://acme.com",
      "score": 85,
      "grade": "A",
      "stage": "Qualified",
      "next_action": "Send intro email to VP Engineering",
      "est_value": "$24,000 ARR",
      "key_contact": "Jane Smith, VP Engineering",
      "key_pain_point": "Manual API monitoring causing outages",
      "risk_factors": "Long procurement cycle",
      "component_scores": {
        "company_fit": 88, "contact_access": 75, "opportunity_quality": 90,
        "competitive_position": 82, "outreach_readiness": 80
      }
    }
  ],
  "action_items": [
    {"company": "Acme Corp", "action": "Send personalized email to VP Engineering",
      "urgency": "immediate", "reason": "Recent funding round creates a budget window"}
  ],
  "weekly_focus": [
    {"rank": 1, "company": "Acme Corp", "score": 85, "reason": "Highest score with an active trigger event",
      "actions": ["Send intro email", "Connect on LinkedIn"]}
  ],
  "methodology": {
    "company_fit_weight": 25, "contact_access_weight": 20, "opportunity_quality_weight": 20,
    "competitive_position_weight": 15, "outreach_readiness_weight": 20
  }
}
```

Notes:
- `grade` must be one of `A+`, `A`, `B`, `C`, `D` (90/75/60/40 thresholds) — or omit it and the script computes it from `score`.
- `action_items[].urgency`: `immediate` → Quick Wins, `this week` → This Week, `this month` → This Month.
- Plain text only in string fields (no Markdown); the script escapes special characters like `&` and `<`.
- Validate the JSON (e.g. `<python> -m json.tool _pdf_input.json`) before running the script.

### Step 5: Locate the PDF Generation Script

The installer puts it at `$HOME/.claude/skills/sales/scripts/generate_pdf_report.py`. If it isn't there, check `scripts/generate_pdf_report.py` in a local clone of ai-sales-team-claude. If neither exists, tell the user to re-run the installer (`install.sh`) and stop.

### Step 6: Generate the PDF

```bash
<python> "$HOME/.claude/skills/sales/scripts/generate_pdf_report.py" _pdf_input.json "SALES-REPORT-$(date +%Y-%m-%d).pdf"
```

On Windows PowerShell, build the date with `$(Get-Date -Format yyyy-MM-dd)` instead of `$(date +%Y-%m-%d)`. The script prints the absolute output path and file size.

To preview the layout with clearly fictional sample data: `<python> "$HOME/.claude/skills/sales/scripts/generate_pdf_report.py" --demo`.

The PDF contains these sections:

#### PDF Section 1: Cover Page
- Title: "Sales Pipeline Report"
- Date of generation
- Overall Pipeline Score displayed as a large circular gauge (0-100)
- Pipeline health rating with color indicator
- Quick stats: total prospects, average score, top grade count

#### PDF Section 2: Score Breakdown
- Horizontal bar chart of average category scores (from `component_scores`)
- Category table with Strong / Good / Needs Work / Critical status

#### PDF Section 3: Prospect Comparison Table
- Full table of all prospects with columns: Rank, Company, Score, Grade, Stage, Next Action, Est. Value
- Alternating row colors for readability
- Grade column color-coded
- Sorted by score descending

#### PDF Section 4: Top Prospects Detail
- One page (or half-page) per top prospect
- Component score radar chart or bar chart
- Key contacts listed
- Pain points and approach summary
- Risk factors highlighted

#### PDF Section 5: Action Plan
- Prioritized action items in a numbered list
- Grouped by timeframe: Immediate, Short-Term, Pipeline Building
- Each with company name, specific action, and urgency level

#### PDF Section 6: Methodology
- Brief explanation of the scoring methodology
- Weight breakdown with percentages
- Grade band definitions
- Disclaimer that scores are based on publicly available information

### Step 7: Clean Up and Report

After PDF generation:

1. Verify the PDF file was created and check its file size
2. Remove the temporary `_pdf_input.json` file
3. Report to the user:
   - PDF file name and location
   - File size
   - Number of pages
   - Summary of contents

---

## Error Handling

### reportlab Not Installed
```
The PDF generation requires the reportlab Python library.
Install it by running: pip install reportlab

Shall I install it for you?
```

### Python Not Available
```
Python 3 is required for PDF generation but was not found.
Please install Python 3 from https://python.org and then run:
  pip install reportlab
```

### Script Not Found
```
The PDF generation script was not found at
$HOME/.claude/skills/sales/scripts/generate_pdf_report.py.
Re-run the AI Sales Team installer (install.sh) to restore it.
```

### No Report Data
```
SALES-REPORT.md was not found in the current directory.
Run `/sales report` first to generate the pipeline report, then run
`/sales report-pdf` to create the PDF version.
```

### PDF Generation Failed
If the Python script exits with an error:
1. Capture the error output
2. Check for common issues:
   - Invalid JSON input (malformed data)
   - File permission errors
   - Disk space issues
   - reportlab version incompatibility
3. Report the specific error to the user with a suggested fix
4. Keep the `_pdf_input.json` file for debugging (don't delete it on failure)

---

## Output Specifications

- **File Name:** `SALES-REPORT-{YYYY-MM-DD}.pdf` (using current date)
- **Page Size:** Letter (8.5" x 11")
- **Orientation:** Portrait for most pages, landscape for wide tables if needed
- **Color Scheme:** Professional blues and grays with color-coded score indicators
- **Font:** Helvetica or similar sans-serif for readability
- **Margins:** 0.75 inch on all sides
- **Expected Length:** 4-8 pages depending on number of prospects

---

## Important Rules

1. ALWAYS check for SALES-REPORT.md before attempting PDF generation. Never generate a PDF from scratch without the markdown report.
2. ALWAYS check for reportlab before running the script. Provide clear installation instructions if missing.
3. Clean up temporary files (_pdf_input.json) on success. Keep them on failure for debugging.
4. The JSON input must be valid JSON. Validate it before passing to the script.
5. If the PDF script fails, provide the full error output to help the user debug.
6. Never modify the original SALES-REPORT.md file during PDF generation.
7. Report the final PDF file path, size, and page count to the user after successful generation.
8. If prospect data is incomplete, still generate the PDF with available data rather than failing. Mark missing data as "N/A" in the PDF.
