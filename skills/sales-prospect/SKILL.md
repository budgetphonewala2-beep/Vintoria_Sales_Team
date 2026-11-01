---
name: sales-prospect
description: "Full prospect audit of a company URL: runs 4 research agents in parallel (company fit, contacts, opportunity/BANT, competitive) then an outreach-strategy agent, and writes a scored PROSPECT-ANALYSIS.md with a ready-to-send first email. Use for /sales prospect or when the user asks to analyze/score a prospect company."
argument-hint: "<company-url>"
---
# Full Prospect Analysis Orchestrator

You are the full prospect audit engine for `/sales prospect <url>`. You launch 4 research subagents in parallel, then an outreach-strategy subagent that builds on their findings, aggregate the results, and produce a unified `prospects/<slug>/PROSPECT-ANALYSIS.md` report that is ready-to-use and deal-focused.

<!-- shared-conventions v2 -->
## Shared Conventions (apply before anything else)

1. **Prospect folder.** Per-prospect files never go in the working-directory root. They live in `prospects/<slug>/`:
`PROSPECT-ANALYSIS.md`, `COMPANY-RESEARCH.md`, `LEAD-QUALIFICATION.md`, `DECISION-MAKERS.md`, `COMPETITIVE-INTEL.md`, `OUTREACH-SEQUENCE.md`, `FOLLOWUP-SEQUENCE.md`, `MEETING-PREP.md`, `CLIENT-PROPOSAL.md`.
- `<slug>` = the prospect's domain, lowercase, without protocol, `www.`, path or trailing slash (`https://www.Acme.com/about` → `acme.com`).
- Given a company name instead of a URL: first look for an existing `prospects/*/` folder for it (folder name, or the `**URL:**` / title line inside its files). If none exists, find the official domain with WebSearch and use that. Only if no domain can be found, use the kebab-case name (`acme-corp`).
- Whenever this skill says to read or write one of those files — including "if `X.md` exists" — it means `prospects/<slug>/X.md` for **this prospect only**. Never use another prospect's folder as context. Create the folder if needed.
- Shared files stay in the working-directory root: `IDEAL-CUSTOMER-PROFILE.md`, `OBJECTION-PLAYBOOK.md`, `SALES-REPORT.md`, `SALES-REPORT-*.pdf`.

2. **What the user sells.** Fit, need and competitive scores only mean something relative to the user's own offer. Read `IDEAL-CUSTOMER-PROFILE.md` (working-directory root) if it exists. If it doesn't and the user hasn't said what they sell in this conversation, ask one short question first — "What do you sell, and to whom?" If they'd rather skip it, proceed and put this line at the top of the output: `> No ICP provided — fit scores are generic B2B estimates.` Suggest `/sales icp` for future runs.

3. **Helper scripts** are installed in `$HOME/.claude/skills/sales/scripts/`. Run them with `python` on Windows (where `python3` is often a Microsoft Store stub) or `python3` on macOS/Linux — use whichever prints a real version for `--version`. Example: `python "$HOME/.claude/skills/sales/scripts/analyze_prospect.py" --url https://acme.com`. Script output is heuristic: treat it as leads to verify, not facts.

4. **Facts, not fiction.** Never invent people, titles, email addresses, mutual connections, customer results, funding, or metrics. If something can't be verified, write "Not found" or label it "Unverified". Email addresses built from a detected pattern must be marked `pattern-guessed — verify before sending`. When a deliverable needs a proof point you don't have, leave a visible `[ADD REAL CUSTOMER RESULT]` marker instead of making one up.

5. **Outreach compliance.** Every sequence must be legal to send. This is guidance, not legal advice:
- Truthful sender identity and subject lines (no fake "Re:"/"Fwd:"), and a working opt-out in every cold email (e.g. "Not relevant? Reply 'no' and I won't follow up."). Honor opt-outs immediately.
- **US (CAN-SPAM):** include the sender's physical postal address in the signature.
- **UK (PECR/UK GDPR):** B2B email to corporate addresses is allowed with identification + opt-out; sole traders and partnerships need prior consent.
- **EU (GDPR + national ePrivacy laws):** needs a documented legitimate interest and role relevance; Germany and some others effectively require prior consent for cold email — flag prospects there.
- **Canada (CASL):** generally requires consent (implied consent only in narrow cases) — flag Canadian prospects.
- **India (DPDP Act 2023):** use business contact details only, state the purpose, and honor withdrawal promptly.
- Only use the Mutual Connection framework when the user confirms a real, named connection who agreed to be mentioned. Never invent one.
- End the output with a short `Compliance notes` line naming which of these rules apply to this prospect's country.

---

## When This Skill Is Invoked

The user runs `/sales prospect <url>`. This is the flagship command of the entire suite. It produces the most comprehensive deliverable: a scored, prioritized, actionable prospect analysis with a ready-to-send outreach email.

---

## Phase 1: Discovery (Sequential — Pre-Analysis)

Before launching subagents, perform these discovery steps sequentially. Every subsequent phase depends on this data.

### 1.1 Fetch the Target URL

Use `WebFetch` to retrieve the company homepage. Store the full content for subagent consumption.

If the homepage loads successfully, also fetch up to 5 key interior pages:
- About / Company page
- Team / Leadership page
- Pricing page
- Blog / Resources page
- Careers / Jobs page
- Contact page

For each page, store:
- Page URL
- Page title
- Raw content (text)
- Key data points extracted (names, numbers, product details)

**If the URL is unreachable:**
1. Report the error to the user: "Could not reach [url] — HTTP [status code]"
2. Attempt alternate URLs: try with/without www, try https vs http
3. If still unreachable, suggest the user verify the URL and try again
4. Do NOT proceed to Phase 2 if zero pages are accessible

### 1.2 Detect Company Type

Classify the prospect into one of these categories. This classification shapes every subagent's analysis focus and scoring calibration:

| Company Type | Detection Signals | Analysis Focus |
|--------------|-------------------|----------------|
| **SaaS/Software** | Free trial CTA, pricing tiers, feature pages, "login" link, API docs, developer documentation, integration marketplace | Tech stack, ARR signals, product-led growth, integration ecosystem, developer team size, churn indicators |
| **Agency/Services** | Case studies, portfolio, "work with us", client logos, testimonials, service packages, hourly/retainer pricing | Client roster quality, team size, service positioning, retainer vs project pricing, industry specialization |
| **E-commerce** | Product listings, cart/checkout, product categories, SKU counts, reviews, shipping info, return policy | Product catalog size, traffic signals, tech platform (Shopify, WooCommerce), revenue estimates, fulfillment model |
| **Enterprise** | Large employee count (500+), multiple office locations, compliance pages, procurement portal, partner ecosystem | Org structure, procurement process, budget cycles, compliance needs, vendor requirements, multi-stakeholder buying |
| **SMB** | Small team (1-50), owner-operator signals, local focus, simple pricing, limited product line | Budget constraints, quick ROI needs, ease of implementation, owner as decision maker, price sensitivity |
| **Startup** | "Backed by" investor logos, founding year recent, small team growing fast, beta/early access language, Y Combinator/accelerator badges | Funding stage, burn rate signals, growth trajectory, founding team background, product-market fit signals |

**Detection procedure:**
1. Scan homepage for signals from each category
2. Check careers page for employee count and hiring velocity
3. Check pricing page for pricing model complexity
4. Look for investor/funding mentions
5. Assign the best-fit category (if ambiguous, note the two most likely categories)

### 1.3 Extract Key Pages and Site Architecture

Map the site architecture to identify all pages relevant to sales intelligence:

| Page Type | Common URLs | Data to Extract |
|-----------|-------------|-----------------|
| **Homepage** | / | Headline, value prop, CTAs, social proof, product positioning |
| **About** | /about, /company, /about-us | Founding story, mission, team size, locations, history |
| **Team** | /team, /leadership, /about/team, /people | Names, titles, photos, bios, LinkedIn links |
| **Pricing** | /pricing, /plans, /packages | Tiers, prices, features per tier, enterprise CTA |
| **Blog** | /blog, /resources, /insights, /news | Recent topics, posting frequency, content depth |
| **Careers** | /careers, /jobs, /join-us, /hiring | Open roles, team sizes by department, growth signals |
| **Contact** | /contact, /get-in-touch, /demo | Contact forms, phone numbers, office addresses |
| **Products** | /products, /features, /solutions, /platform | Product lines, features, use cases, integrations |
| **Customers** | /customers, /case-studies, /testimonials | Customer logos, case study details, industry verticals served |
| **Partners** | /partners, /integrations, /ecosystem | Technology partners, integration depth, ecosystem maturity |

### 1.4 Identify Industry Vertical

Determine the prospect's primary industry vertical from these categories:

- Technology / Software
- Financial Services / Fintech
- Healthcare / Healthtech
- Education / Edtech
- E-commerce / Retail
- Manufacturing / Industrial
- Media / Entertainment
- Real Estate / Proptech
- Professional Services / Consulting
- Marketing / Advertising
- Logistics / Supply Chain
- Energy / Cleantech
- Food / Hospitality
- Non-profit / Government
- Other (specify)

**Detection signals:** Industry-specific terminology, customer logos, case study industries, job posting requirements, compliance mentions, regulatory references.

### 1.5 Run Structured Data Extraction

Run the analysis script (it fetches ~17 common subpages concurrently, skips SPA soft-404s, and returns JSON):

```bash
python "$HOME/.claude/skills/sales/scripts/analyze_prospect.py" --url <url>
```

(Use `python3` instead of `python` on macOS/Linux.) It returns: company name, description, `slug`, industry signals, tech stack (vendor-script detection), applicant-tracking system (hiring signal), social profiles, team members with seniority/department/likely buying role, pricing tiers, public contact emails/phones, size/funding/location/founded signals, and `warnings`.

**Treat the output as leads, not facts.** Verify anything you put in the report. If `warnings` says the site is JavaScript-rendered, rely on WebFetch/WebSearch instead.

**If the script is unavailable or fails:**
1. Note the error and continue
2. Extract the same data manually from the WebFetch results
3. Note in the report that automated extraction was unavailable

Also check `prospects/<slug>/` for earlier outputs (`COMPANY-RESEARCH.md`, `DECISION-MAKERS.md`, `LEAD-QUALIFICATION.md`, `COMPETITIVE-INTEL.md`). If any exist, include them in the briefing as **prior research to verify and update**, noting their date.

### 1.6 Compile Discovery Briefing

Before launching subagents, compile a discovery briefing object containing:

```
DISCOVERY BRIEFING
==================
URL: [target url]
Company Name: [detected name]
Company Type: [SaaS/Agency/E-commerce/Enterprise/SMB/Startup]
Industry Vertical: [detected vertical]
Key Pages Found: [list of accessible pages with URLs]
Homepage Content: [stored content]
Team Page Content: [stored content or "not found"]
Pricing Page Content: [stored content or "not found"]
Blog Content: [stored content or "not found"]
Careers Content: [stored content or "not found"]
Script Output: [JSON data or "unavailable"]
Prior Research: [contents of existing prospects/<slug>/ files, with dates, or "none"]
What The User Sells: [summary of IDEAL-CUSTOMER-PROFILE.md or the user's answer, or "not provided — generic B2B scoring"]
Initial Signals: [key observations from discovery]
```

This briefing is passed to every subagent as context.

---

## Phase 2: Agent Analysis (4 in parallel, then 1)

The five specialist agents are installed in `~/.claude/agents/`. Each agent file defines its own research steps, its 5-dimension scoring rubric (each 0-10, scaled to a 0-100 category score) and its output format — do not restate or override those rubrics in the prompt.

**How to launch:** use the Agent/Task tool with `subagent_type` set to the agent name (`sales-company`, `sales-contacts`, `sales-opportunity`, `sales-competitive`, `sales-strategy`). If an agent type is not available in this session, fall back to `subagent_type: "general-purpose"` and start the prompt with: *"Read `$HOME/.claude/agents/<name>.md` and follow it exactly."*

**Every agent prompt must contain:** the prospect URL and company name, the full discovery briefing (including script output and prior research), the "What The User Sells" context, and this instruction: *"Return your analysis in your Output Format as your final message. Do not write any files."*

### Wave 1 — launch these four in a single message so they run in parallel

| Agent | Category | Weight | Returns |
|-------|----------|--------|---------|
| `sales-company` | Company Fit | 25% | Firmographics, growth, tech stack, budget signals, risks |
| `sales-contacts` | Contact Access | 20% | Buying committee map, priority contacts, personalization anchors, warm paths |
| `sales-opportunity` | Opportunity Quality | 20% | BANT scorecard, pain points, timeline, champion potential, red flags |
| `sales-competitive` | Competitive Position | 15% | Current tools/vendors, switching costs, gaps, positioning angles |

### Wave 2 — after all four have returned

| Agent | Category | Weight | Returns |
|-------|----------|--------|---------|
| `sales-strategy` | Outreach Readiness | 20% | Channel plan, messaging framework, per-contact personalization, objections, timing, first-email draft |

Pass the four Wave 1 outputs to `sales-strategy` in full (it needs the real contacts, pain points and competitive angles — that is why it runs second).

**Cost note:** this command makes many web requests across five agents. If the user asked for something quick, use `/sales quick` instead.

---

## Phase 3: Synthesis (Sequential — Aggregation and Scoring)

After all 5 subagents complete, aggregate their results into the final analysis.

### 3.1 Handle Subagent Failures

If any subagent fails or times out:
1. Note the failure in the report: "[Agent name] analysis unavailable — [reason]"
2. Assign a neutral score of 50 for that category
3. Reduce confidence level of the overall Prospect Score
4. Continue with all available data
5. Recommend manual follow-up for the failed analysis area

### 3.2 Calculate Prospect Score (0-100)

Compute the composite Prospect Score using the weighted formula:

```
Prospect Score = (
    Company_Fit      * 0.25 +
    Contact_Access   * 0.20 +
    Opportunity_Quality * 0.20 +
    Competitive_Position * 0.15 +
    Outreach_Readiness  * 0.20
)
```

**Score interpretation:**

| Score Range | Grade | Label | Meaning | Recommended Action |
|-------------|-------|-------|---------|-------------------|
| 90-100 | A+ | Hot Lead | Exceptional fit across all dimensions. High close probability. | Prioritize immediately. Assign senior rep. Multi-thread outreach within 24 hours. |
| 75-89 | A | Strong Prospect | Strong fit with minor gaps. Worth significant sales investment. | Begin personalized outreach within 48 hours. Invest in deep research. |
| 60-74 | B | Qualified Lead | Good fit but notable gaps. Standard sales approach warranted. | Add to active pipeline. Begin standard outreach sequence. Monitor for trigger events. |
| 40-59 | C | Lukewarm | Mixed signals. Some fit indicators but significant concerns. | Nurture with value-add content. Do not hard sell. Re-evaluate in 30-60 days. |
| 0-39 | D | Poor Fit | Fundamental misalignment on multiple dimensions. | Deprioritize. Add to long-term nurture only if one dimension scores above 70. |

### 3.3 Generate Prioritized Action Plan

Based on the Prospect Score and subagent findings, create a three-tier action plan:

**Immediate Actions (Next 24-48 Hours):**
- Specific outreach actions to take right now
- Decision makers to connect with on LinkedIn
- Content to share or engage with
- Internal preparation (CRM notes, team briefing)
- List 3-5 specific actions with assigned priority

**Short-Term Actions (Next 1-2 Weeks):**
- Follow-up sequence to execute
- Additional research to conduct
- Stakeholders to engage (multi-threading)
- Competitive positioning to prepare
- List 3-5 specific actions with timeline

**Long-Term Actions (Next 1-3 Months):**
- Relationship-building activities
- Content nurture strategy
- Event or conference opportunities
- Partnership or referral approaches
- List 2-3 specific actions with milestones

### 3.4 Create Ready-to-Use First Email

Using the outreach strategy subagent's findings, craft the actual first outreach email. This must be:
- Copy-paste ready — the only allowed placeholders are the sender's own signature details (`[Your name]`, `[Company]`, `[Postal address]` where CAN-SPAM applies)
- Ends with a one-line opt-out (e.g. "Not relevant? Just reply 'no' and I won't follow up.")
- Personalized to the specific prospect (reference real data found during research)
- Under 100 words in the body
- Using one of the four outreach frameworks from the sales-outreach skill
- With a clear, low-friction CTA
- With 2 subject line options for A/B testing
- With the specific send target (name, title, company)

### 3.5 Confidence Assessment

Rate the overall confidence of the analysis:

| Confidence Level | Criteria |
|-----------------|---------|
| **High** | All 5 subagents completed successfully. Rich public data available. Multiple data sources confirmed findings. |
| **Medium** | 4 of 5 subagents completed. Moderate public data. Some findings based on inference. |
| **Low** | 3 or fewer subagents completed. Limited public data. Significant reliance on inference. |
| **Very Low** | Major data gaps. Most findings are speculative. Recommend manual research before outreach. |

---

## Output Format: PROSPECT-ANALYSIS.md

Write the final report to `prospects/<slug>/PROSPECT-ANALYSIS.md` with this exact structure:

```markdown
# Prospect Analysis: [Company Name]
**URL:** [url]
**Date:** [current date]
**Company Type:** [detected type]
**Industry:** [detected vertical]
**Prospect Score: [X]/100 (Grade: [letter grade] — [label])**
**Confidence:** [High/Medium/Low/Very Low]

---

## Executive Summary

[3-5 paragraph summary for a sales leader. Lead with the Prospect Score and grade.
Highlight the single biggest opportunity, the single biggest risk, and the
recommended approach. Include the top decision maker to target and the
recommended outreach timing. End with a clear go/no-go recommendation
and expected deal timeline.]

---

## Prospect Snapshot

| Dimension | Value |
|-----------|-------|
| **Company** | [name] |
| **Website** | [url] |
| **Industry** | [vertical] |
| **Company Type** | [SaaS/Agency/E-commerce/Enterprise/SMB/Startup] |
| **Founded** | [year] |
| **Employees** | [count or estimate] |
| **Funding** | [total or "Bootstrapped" or "Public"] |
| **Revenue Est.** | [estimate range] |
| **HQ Location** | [city, state/country] |
| **Key Decision Maker** | [name, title] |
| **Prospect Score** | [X]/100 ([grade]) |
| **Recommended Action** | [one-line action] |

---

## Score Breakdown

| Category | Score | Weight | Weighted | Key Finding |
|----------|-------|--------|----------|-------------|
| Company Fit | [X]/100 | 25% | [X] | [one-line finding] |
| Contact Access | [X]/100 | 20% | [X] | [one-line finding] |
| Opportunity Quality | [X]/100 | 20% | [X] | [one-line finding] |
| Competitive Position | [X]/100 | 15% | [X] | [one-line finding] |
| Outreach Readiness | [X]/100 | 20% | [X] | [one-line finding] |
| **TOTAL** | | **100%** | **[X]/100** | |

---

## Company Profile

[Full company research findings from the sales-company subagent.
Include: overview, business model, product/technology, funding history,
market position, recent developments. Cite specific sources.]

---

## Decision Maker Map

### Buying Committee

| Name | Title | Buying Role | Personalization Anchor | Approach Strategy |
|------|-------|-------------|----------------------|-------------------|
| [name] | [title] | [Economic Buyer/Champion/Technical Evaluator/End User/Blocker] | [specific anchor] | [1-line strategy] |

### Org Chart (Text-Based)

```
[CEO Name] — CEO
├── [CTO Name] — CTO (Technical Evaluator)
│   ├── [VP Eng] — VP Engineering
│   └── [Dir Product] — Director of Product
├── [CRO Name] — CRO (Economic Buyer)
│   └── [VP Sales] — VP Sales (Champion)
└── [CMO Name] — CMO
    └── [Dir Marketing] — Director of Marketing
```

### Top 3 Priority Contacts

[Detailed profile for each: name, title, role in buying process,
LinkedIn summary, recent activity, personalization anchors,
recommended approach, suggested first message]

---

## Opportunity Assessment

### BANT Scorecard

| Dimension | Score | Evidence | Confidence |
|-----------|-------|----------|------------|
| Budget | [X]/25 | [specific evidence] | [High/Medium/Low] |
| Authority | [X]/25 | [specific evidence] | [High/Medium/Low] |
| Need | [X]/25 | [specific evidence] | [High/Medium/Low] |
| Timeline | [X]/25 | [specific evidence] | [High/Medium/Low] |
| **Total** | **[X]/100** | | |

### MEDDIC Assessment

| Element | Finding | Evidence | Confidence |
|---------|---------|----------|------------|
| Metrics | [what metrics matter to them] | [source] | [level] |
| Economic Buyer | [who] | [source] | [level] |
| Decision Criteria | [what factors] | [source] | [level] |
| Decision Process | [how they buy] | [source] | [level] |
| Identify Pain | [specific pain points] | [source] | [level] |
| Champion | [potential champion] | [source] | [level] |

### Buying Signals Detected
[Bulleted list of positive buying signals with evidence]

### Red Flags
[Bulleted list of concerns or risks with evidence]

---

## Competitive Landscape

### Current Solutions Detected
[What tools/vendors the prospect currently uses, with evidence]

### Switching Cost Assessment
[Analysis of how difficult it would be for them to switch]

### Competitive Positioning Angles
[How to position against their current solution. Key differentiators to emphasize.
Weaknesses of their current solution to highlight.]

---

## Recommended Outreach Strategy

### Selected Framework
[Which of the 4 outreach frameworks was selected and why]

### Channel Strategy
[Primary and secondary channels. LinkedIn + email timing.]

### Personalization Research
[All personalization anchors found: trigger events, personal interests,
shared connections, recent content, career milestones]

### Objection Preparation
[Top 3 likely objections and prepared responses]

---

## Prioritized Action Plan

### Immediate (Next 24-48 Hours)
1. [Specific action with details]
2. [Specific action with details]
3. [Specific action with details]

### Short-Term (Next 1-2 Weeks)
1. [Specific action with details]
2. [Specific action with details]
3. [Specific action with details]

### Long-Term (Next 1-3 Months)
1. [Specific action with details]
2. [Specific action with details]

---

## Ready-to-Send First Email

**To:** [Name], [Title] at [Company]
**Subject Line A:** [subject]
**Subject Line B:** [subject]

---

[Full email body — copy-paste ready, under 100 words,
personalized with real data from the research]

---

**CTA:** [specific ask]
**Send Timing:** [recommended day/time]
**Follow-Up:** [when and how to follow up if no response]

---

*Generated by AI Sales Team — `/sales prospect`*
```

---

## Terminal Output

In addition to the file, display a condensed scorecard in the terminal:

```
============================================
  PROSPECT ANALYSIS COMPLETE
============================================

Company:  [name] ([type])
Industry: [vertical]
URL:      [url]

Prospect Score: [X]/100 (Grade: [letter] — [label])
Confidence:     [High/Medium/Low]

Score Breakdown:
  Company Fit:         [XX]/100 ████████░░
  Contact Access:      [XX]/100 ██████░░░░
  Opportunity Quality: [XX]/100 ███████░░░
  Competitive Position:[XX]/100 █████░░░░░
  Outreach Readiness:  [XX]/100 ████████░░

Key Decision Maker: [Name], [Title]

Top 3 Opportunities:
  1. [opportunity]
  2. [opportunity]
  3. [opportunity]

Top 3 Risks:
  1. [risk]
  2. [risk]
  3. [risk]

Next Step: [single most important action]

Full report saved to: prospects/<slug>/PROSPECT-ANALYSIS.md
============================================
```

**Bar chart rendering rules:**
- Each bar is 10 characters wide
- Score 0-10 = 1 filled block, 11-20 = 2 filled blocks, etc.
- Use Unicode block characters: filled = `\u2588`, empty = `\u2591`
- Align all bars and labels for clean terminal display

---

## Error Handling

### URL Unreachable
1. Try alternate URL formats (www/non-www, http/https)
2. If all fail, report error and stop: "Could not reach [url]. Please verify the URL and try again."
3. Do NOT generate a report based on zero data

### Subagent Failure
1. Log which subagent failed and why
2. Assign neutral score (50) for that category
3. Add a note in the report: "[Category] analysis unavailable — neutral score assigned"
4. Reduce overall confidence by one level
5. Continue with remaining subagent data

### Site Behind Authentication
1. Note what was publicly accessible
2. Analyze only the public pages
3. Add a note: "Site requires authentication. Analysis limited to publicly accessible pages."
4. Recommend manual review of gated content
5. Reduce confidence level accordingly

### Minimal Content Site
1. If fewer than 3 pages are accessible, note "Limited site content"
2. Supplement with WebSearch for external data (Crunchbase, LinkedIn, news)
3. Adjust confidence to Low or Very Low
4. Recommend additional manual research

---

## Cross-Skill Integration

- Prior files in `prospects/<slug>/` are passed to the agents as research to verify and update (see 1.5) — never copied blindly, and never taken from another prospect's folder.
- After writing the report, suggest next commands: `/sales outreach <url>` for the full sequence, `/sales prep <url>` before a meeting, `/sales proposal <url>` for a deal-specific proposal, and `/sales report` once several prospects are analyzed.
