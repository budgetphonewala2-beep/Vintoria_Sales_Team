# vintoria-report — Playbook

> Web access: use your agent's web tools if it has them; otherwise run the scripts in the `vintoria-sales` skill's
> `scripts/` folder (`<SCRIPTS>` = `../vintoria-sales/scripts/` next to this skill): `fetch_page.py <url>` and
> `web_search.py "<query>"`. Never invent what you could not fetch — write "Not found".

## Purpose

You generate a professional, visually polished PDF version of the sales pipeline report. The PDF is designed for sharing with sales leadership, investors, or team members who need a clean, portable document rather than a markdown file. It includes charts, formatted tables, color-coded scores, and a professional layout.

---

## Instructions

When the user invokes `vintoria-report`, follow this process:

### Step 1: Verify Prerequisites

Check that `SALES-REPORT.md` exists in the current working directory.

**If SALES-REPORT.md does NOT exist:**
- Inform the user: "No SALES-REPORT.md found. Run `vintoria-report` first to generate the pipeline report, then run `vintoria-report` to create the PDF version."
- Stop execution.

**If SALES-REPORT.md exists:**
- Read its contents
- Also read the per-prospect files in `prospects/*/` (`PROSPECT-ANALYSIS.md`, `COMPANY-RESEARCH.md`, etc.) to enrich the PDF with additional detail

### Step 2: Check Python and reportlab

Find a working Python (on Windows `python3` is often a Microsoft Store stub that prints "Python was not found"):

```bash
python -c "import reportlab, sys; print(sys.version.split()[0], reportlab.Version)"   # Windows
python -c "import reportlab, sys; print(sys.version.split()[0], reportlab.Version)"  # macOS/Linux
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

The installer puts it at `<SCRIPTS>/ops/generate_pdf_report.py`. If it isn't there, check `scripts/generate_pdf_report.py` in a local clone of ai-sales-team-claude. If neither exists, tell the user to re-run the installer (`install.sh`) and stop.

### Step 6: Generate the PDF

```bash
<python> "<SCRIPTS>/ops/generate_pdf_report.py" _pdf_input.json "SALES-REPORT-<YYYY-MM-DD>.pdf"
```


To preview the layout with clearly fictional sample data: `<python> "<SCRIPTS>/ops/generate_pdf_report.py" --demo`.

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
