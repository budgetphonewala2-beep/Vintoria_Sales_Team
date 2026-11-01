# sales-prospect — Playbook

> Web access: use your agent's web tools if it has them; otherwise run the scripts in the `sales` skill's
> `scripts/` folder (`<SCRIPTS>` = `../sales/scripts/` next to this skill): `fetch_page.py <url>` and
> `web_search.py "<query>"`. Never invent what you could not fetch — write "Not found".

## When This Skill Is Invoked

The user runs `sales-prospect` (<url>). This is the flagship command of the entire suite. It produces the most comprehensive deliverable: a scored, prioritized, actionable prospect analysis with a ready-to-send outreach email.

---

## Phase 1: Discovery (Sequential — Pre-Analysis)

Before launching subagents, perform these discovery steps sequentially. Every subsequent phase depends on this data.

### 1.1 Fetch the Target URL

Use `web fetch` to retrieve the company homepage. Store the full content for subagent consumption.

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
python "<SCRIPTS>/analyze_prospect.py" --url <url>
```

(Use `python3` instead of `python` on macOS/Linux.) It returns: company name, description, `slug`, industry signals, tech stack (vendor-script detection), applicant-tracking system (hiring signal), social profiles, team members with seniority/department/likely buying role, pricing tiers, public contact emails/phones, size/funding/location/founded signals, and `warnings`.

**Treat the output as leads, not facts.** Verify anything you put in the report. If `warnings` says the site is JavaScript-rendered, rely on web fetch/web search instead.

**If the script is unavailable or fails:**
1. Note the error and continue
2. Extract the same data manually from the web fetch results
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

This briefing is the input for every role.

---

## Phase 2: Role Analysis (4 research roles, then strategy)

The five role playbooks live next to this file: `role-company.md`, `role-contacts.md`, `role-opportunity.md`,
`role-competitive.md`, `role-strategy.md`. Each defines its own research steps, its 5-dimension scoring rubric
(each 0-10, scaled to a 0-100 category score) and its output format — follow them exactly; don't restate or
override the rubrics.

**Default (works in every agent): run them yourself, in sequence.** For each role: read the playbook, do the
research it describes using the discovery briefing, and write its result in its Output Format under a heading
`### Role: <name>`. Keep each role's findings separate so the scores stay independent.

**Optional parallelism:** if your agent can run subagents (e.g. Claude Code with the adapters in
`adapters/claude-code/agents/` installed), you may run the four research roles in parallel, each given the
discovery briefing and its playbook, and told: *"Return your analysis in your Output Format. Do not write files."*

| Order | Role | Category | Weight | Returns |
|-------|------|----------|--------|---------|
| 1 | company | Company Fit | 25% | Firmographics, growth, tech stack, budget signals, risks |
| 2 | contacts | Contact Access | 20% | Buying committee, priority contacts, personalization anchors, warm paths |
| 3 | opportunity | Opportunity Quality | 20% | BANT scorecard, pain points, timeline, champion potential, red flags |
| 4 | competitive | Competitive Position | 15% | Current tools/vendors, switching costs, gaps, positioning angles |
| 5 | strategy | Outreach Readiness | 20% | Channel plan, messaging, per-contact personalization, objections, timing, first email |

The strategy role always runs LAST and gets the four research results in full (it needs the real contacts,
pain points and competitive angles).

**Cost note:** this is the deepest command (many page fetches). For a fast estimate use the router's quick
snapshot instead.

---

## Phase 3: Synthesis (Sequential — Aggregation and Scoring)

After all 5 roles are done, aggregate their results into the final analysis.

### 3.1 Handle Missing Role Results

If a role could not be completed (no data, blocked pages):
1. Note the failure in the report: "[Role] analysis unavailable — [reason]"
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
