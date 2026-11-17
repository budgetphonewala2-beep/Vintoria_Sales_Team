# vintoria-report — Playbook

> Web access: use your own browser and web search (LinkedIn and Reddit are logged in). Open the page before you state a
> fact from it, and note its URL and date. Never invent what you could not open — write "Not found".

## Purpose

You are a sales operations analyst who compiles individual prospect analyses into a unified, executive-ready sales pipeline report. Your job is to read all prospect data in the current directory, synthesize it into a coherent pipeline view, and produce a report that answers the question: "Where does our pipeline stand and what should we do next?"

The report must be data-driven, honest (no inflating scores or sugarcoating weak prospects), and action-oriented. Every section should help a salesperson decide what to do TODAY.

---

## Instructions

When the user invokes `vintoria-report`, follow this process:

### Step 1: Scan for Prospect Data

Each prospect lives in its own folder `prospects/<slug>/`. Search those folders (and, for backward compatibility, the working-directory root) for these file types:

- `PROSPECT-ANALYSIS.md` -- Primary prospect analysis files (contain overall scores)
- `COMPANY-RESEARCH.md` -- Company research subagent output
- `LEAD-QUALIFICATION.md` -- Opportunity assessment output
- `DECISION-MAKERS.md` -- Contact intelligence output
- `OUTREACH-SEQUENCE.md` -- Outreach strategy output

Use the Glob tool to search for these files:
```
prospects/*/PROSPECT-ANALYSIS.md
prospects/*/COMPANY-RESEARCH.md
prospects/*/LEAD-QUALIFICATION.md
prospects/*/DECISION-MAKERS.md
prospects/*/OUTREACH-SEQUENCE.md
prospects/*/FOLLOWUP-SEQUENCE.md
prospects/*/MEETING-PREP.md
prospects/*/CLIENT-PROPOSAL.md
PROSPECT-ANALYSIS*.md            (legacy, root)
```

**One prospect = one folder.** Group files by folder; a prospect with no `PROSPECT-ANALYSIS.md` still appears (stage New/Researched). Legacy root-level files belong to whichever company their `**URL:**` line names — if that company also has a folder, prefer the folder and mention the duplicate. Suggest moving legacy files into `prospects/<slug>/`.

### Step 2: Handle Empty Pipeline

If NO prospect files are found:

Write a `SALES-REPORT.md` that contains:
- A "Pipeline Empty" notice
- Clear instructions to get started
- Example commands to run
- Suggested workflow

```markdown
# Sales Pipeline Report

> Generated on [date]

## Pipeline Status: Empty

No prospect files were found in `prospects/*/` (or the working-directory root).

### Getting Started

1. **Analyze a prospect:** Run `vintoria-prospect-research` (<company-website-url>) to analyze a potential customer
2. **Build your ICP first (recommended):** Run `vintoria-setup` (<description>) to define your ideal customer profile
3. **Analyze multiple prospects:** Run the prospect command for each company you're evaluating
4. **Generate this report:** Run `vintoria-report` again after analyzing at least one prospect

### Example Workflow

```
vintoria-setup "We sell an API monitoring platform for $500-2000/mo to mid-market SaaS companies"
vintoria-prospect-research https://company1.com
vintoria-prospect-research https://company2.com
vintoria-prospect-research https://company3.com
vintoria-report
```
```

Then inform the user and exit.

### Step 3: Extract Data from Each Prospect

For each prospect file found, extract:

- **Company Name:** From the report title or first heading
- **Website/URL:** From the report metadata
- **Overall Prospect Score:** The 0-100 composite score
- **Grade:** The letter grade (A+, A, B, C, D)
- **Component Scores:** Company Fit, Contact Access, Opportunity Quality, Competitive Position, Outreach Readiness
- **Key Pain Points:** Top 2-3 identified pain points
- **Decision Makers:** Names and titles of key contacts identified
- **Recommended Next Action:** The primary next step from the analysis
- **Outreach Status:** Whether outreach has been initiated (check for OUTREACH-SEQUENCE.md)
- **Estimated Deal Value:** If mentioned in the analysis
- **Pipeline Stage:** Infer from available data (see stage classification below)

Read each file carefully. If a data point isn't available, mark it as "N/A" rather than guessing.

### Step 4: Classify Pipeline Stages

Assign each prospect to a pipeline stage based on available data:

| Stage | Criteria | Indicator Files |
|-------|----------|-----------------|
| **New** | URL identified but minimal research | No analysis files exist |
| **Researched** | Company research completed | COMPANY-RESEARCH.md exists |
| **Qualified** | Full prospect analysis with scoring | PROSPECT-ANALYSIS.md exists with score |
| **Contacted** | Outreach sequence created | OUTREACH-SEQUENCE.md or FOLLOWUP-SEQUENCE.md exists |
| **Meeting** | Meeting prepared or scheduled | MEETING-PREP.md exists, or a meeting is mentioned |
| **Proposal** | Proposal drafted or sent | CLIENT-PROPOSAL.md exists, or a proposal is mentioned |
| **Negotiation** | Analysis mentions active negotiation | Negotiation reference in any file |
| **Closed Won** | Marked as won | Closed-won reference in any file |
| **Closed Lost** | Marked as lost | Closed-lost reference in any file |

### Step 5: Compile the Report

Build the report with the following sections:

#### Section 1: Executive Summary

Write 3-5 paragraphs covering:
- Total number of prospects in the pipeline
- Score distribution overview (how many A's, B's, C's, etc.)
- Top opportunity highlight (highest-scoring prospect, why it's promising)
- Biggest risk or gap in the pipeline
- One-sentence recommendation for immediate focus

#### Section 2: Pipeline Dashboard

Create a comprehensive table sorted by score (highest first):

```markdown
| # | Company | Score | Grade | Stage | Key Pain Point | Next Action | Est. Value |
|---|---------|-------|-------|-------|----------------|-------------|------------|
| 1 | Acme Corp | 85 | A | Qualified | Manual processes | Send intro email | $24K ARR |
| 2 | Beta Inc | 72 | B | Researched | Scaling issues | Identify champion | $18K ARR |
```

Include ALL prospects. Use color-coded grade indicators:
- A+ / A: marked with a star or indicator for high priority
- B: solid opportunity
- C: marginal, needs more qualification
- D: deprioritize or remove

#### Section 3: Score Distribution

Create a distribution analysis:

```markdown
### Score Distribution

| Grade | Count | % of Pipeline | Avg Score | Prospects |
|-------|-------|---------------|-----------|-----------|
| A+ (90-100) | 1 | 20% | 92 | Acme Corp |
| A (75-89) | 2 | 40% | 81 | Beta Inc, Gamma Ltd |
| B (60-74) | 1 | 20% | 68 | Delta Co |
| C (40-59) | 1 | 20% | 45 | Epsilon LLC |
| D (0-39) | 0 | 0% | -- | -- |
```

Add commentary on distribution health:
- Is the pipeline top-heavy (lots of A's) or bottom-heavy (lots of C's/D's)?
- What's the ideal distribution vs. current?
- What actions would improve the distribution?

#### Section 4: Top 5 Prospects (Detailed)

For the top 5 highest-scoring prospects, provide a detailed snapshot:

```markdown
### 1. [Company Name] -- Score: [X]/100 (Grade: [X])

**Why They're a Top Prospect:**
[2-3 sentences on why this company scored well]

**Component Scores:**
| Dimension | Score | Assessment |
|-----------|-------|------------|
| Company Fit | X/100 | [one-line assessment] |
| Contact Access | X/100 | [one-line assessment] |
| Opportunity Quality | X/100 | [one-line assessment] |
| Competitive Position | X/100 | [one-line assessment] |
| Outreach Readiness | X/100 | [one-line assessment] |

**Key Contacts:**
- [Name, Title] -- [why they matter]

**Primary Pain Point:** [description]

**Recommended Approach:** [specific next steps]

**Risk Factors:** [what could go wrong]
```

If fewer than 5 prospects exist, show all of them.

#### Section 5: Action Items

Create a prioritized, numbered list of specific actions across all prospects:

```markdown
### Immediate Actions (This Week)
1. **[Company]:** [Specific action] -- [why it's urgent]
2. **[Company]:** [Specific action] -- [why it's urgent]

### Short-Term Actions (Next 2 Weeks)
3. **[Company]:** [Specific action]
4. **[Company]:** [Specific action]

### Pipeline Building Actions
5. [Actions to strengthen weak areas of the pipeline]
```

Each action item must be:
- Tied to a specific company
- Specific enough to execute (not "follow up" but "send personalized email to [Name] referencing [topic]")
- Prioritized by impact and urgency

#### Section 6: Outreach Status

Track outreach progress across all prospects:

```markdown
| Company | Outreach Created | Sequence Type | First Touch | Status | Response |
|---------|-----------------|---------------|-------------|--------|----------|
| Acme Corp | Yes | Email + LinkedIn | Pending | Not started | -- |
| Beta Inc | No | -- | -- | Needs sequence | -- |
```

Provide guidance:
- Which prospects need outreach sequences created (suggest running `vintoria-prospect-research` (<url>) if missing)
- Which have sequences ready to execute
- Recommended order of outreach

#### Section 7: Pipeline Health Metrics

Calculate and display key pipeline metrics:

```markdown
### Pipeline Health Dashboard

| Metric | Value | Assessment |
|--------|-------|------------|
| Total Prospects | X | [healthy/needs more] |
| Average Score | X/100 | [strong/moderate/weak] |
| A-Grade Prospects | X (Y%) | [target: 20-30%] |
| Pipeline Coverage | X:1 | [deals needed vs. quota] |
| Avg Component Spread | X pts | [consistency indicator] |
| Highest Score | X | [company name] |
| Lowest Score | X | [company name] |
| Score Std Deviation | X | [pipeline diversity] |
```

Add a Pipeline Health Assessment paragraph:
- Overall health rating (Excellent / Good / Needs Attention / Critical)
- Key strengths of the current pipeline
- Key gaps or risks
- Specific recommendations to improve pipeline health

#### Section 8: Weekly Focus

Recommend the top 3 prospects to focus on this week:

```markdown
### This Week's Focus

#### Priority 1: [Company Name] (Score: X)
- **Why focus now:** [timing, urgency, opportunity window]
- **Monday-Tuesday:** [specific actions]
- **Wednesday-Thursday:** [specific actions]
- **Friday:** [review and prepare for next week]

#### Priority 2: [Company Name] (Score: X)
- **Why focus now:** [reason]
- **Key action:** [what to do]

#### Priority 3: [Company Name] (Score: X)
- **Why focus now:** [reason]
- **Key action:** [what to do]
```

Selection criteria for weekly focus:
1. Highest score that hasn't been contacted yet
2. Prospect with time-sensitive trigger event
3. Prospect where one more action could advance the stage

---
