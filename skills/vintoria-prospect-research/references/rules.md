# vintoria-prospect-research — rules, terminal output, errors and cross-skill use

## Full scored analysis

### Terminal Output

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

### Error Handling

#### URL Unreachable
1. Try alternate URL formats (www/non-www, http/https)
2. If all fail, report error and stop: "Could not reach [url]. Please verify the URL and try again."
3. Do NOT generate a report based on zero data

#### Subagent Failure
1. Log which subagent failed and why
2. Assign neutral score (50) for that category
3. Add a note in the report: "[Category] analysis unavailable — neutral score assigned"
4. Reduce overall confidence by one level
5. Continue with remaining subagent data

#### Site Behind Authentication
1. Note what was publicly accessible
2. Analyze only the public pages
3. Add a note: "Site requires authentication. Analysis limited to publicly accessible pages."
4. Recommend manual review of gated content
5. Reduce confidence level accordingly

#### Minimal Content Site
1. If fewer than 3 pages are accessible, note "Limited site content"
2. Supplement with web search for external data (Crunchbase, LinkedIn, news)
3. Adjust confidence to Low or Very Low
4. Recommend additional manual research

---

### Cross-Skill Integration

- Prior files in `prospects/<slug>/` are passed to the agents as research to verify and update (see 1.5) — never copied blindly, and never taken from another prospect's folder.
- After writing the report, suggest next commands: `vintoria-outreach` (<url>) for the full sequence, `vintoria-close` (<url>) before a meeting, `vintoria-close` (<url>) for a deal-specific proposal, and `vintoria-report` once several prospects are analyzed.

## Company research

### Terminal Output

Display a condensed summary in the terminal:

```
=== COMPANY RESEARCH COMPLETE ===

Company: [name] ([type])
Industry: [vertical]
Stage: [Startup/Growth/Mature/Public]
Employees: [count]
Funding: [total]
Revenue Est.: [range]

Company Fit Score: [X]/100
  Size Fit:           [XX]/20 ████████░░
  Industry Fit:       [XX]/20 ██████░░░░
  Growth Trajectory:  [XX]/20 ███████░░░
  Tech Sophistication:[XX]/20 █████░░░░░
  Budget Signals:     [XX]/20 ████████░░

Top Strengths:
  1. [strength]
  2. [strength]
  3. [strength]

Top Risks:
  1. [risk]
  2. [risk]

Full report saved to: prospects/<slug>/COMPANY-RESEARCH.md
```

---

### Error Handling

- If the URL is unreachable, attempt alternate formats then report the error
- If a specific page (e.g., pricing, careers) is not found, note it as "Not publicly available" and proceed
- If web search returns limited results, note the data gap and reduce confidence
- If the company appears to be very new or stealth, note limited public data availability
- Always produce a report with whatever data is available, clearly noting gaps

### Cross-Skill Integration

- If `PROSPECT-ANALYSIS.md` exists, reference overall prospect context
- If `DECISION-MAKERS.md` exists, cross-reference leadership findings
- If `COMPETITIVE-INTEL.md` exists, incorporate competitive context
- Suggest follow-up: `vintoria-prospect-research` for decision maker deep dive, `vintoria-prospect-research` for opportunity assessment

## Qualification

### Terminal Output

Display a condensed summary in the terminal:

```
=== LEAD QUALIFICATION COMPLETE ===

Company:  [name]
Industry: [vertical]

BANT Score: [X]/100
  Budget:    [XX]/25 ████████░░
  Authority: [XX]/25 ██████░░░░
  Need:      [XX]/25 ███████░░░
  Timeline:  [XX]/25 █████░░░░░

MEDDIC Completeness: [X]%
  Metrics:          [Found/Partial/Missing]
  Economic Buyer:   [Found/Partial/Missing]
  Decision Criteria:[Found/Partial/Missing]
  Decision Process: [Found/Partial/Missing]
  Identify Pain:    [Found/Partial/Missing]
  Champion:         [Found/Partial/Missing]

Opportunity Quality Score: [X]/100
Lead Grade: [letter] — [label]

Top Buying Signals:
  1. [signal]
  2. [signal]
  3. [signal]

Red Flags:
  1. [flag]
  2. [flag]

Recommended Action: [one-line recommendation]

Full report saved to: prospects/<slug>/LEAD-QUALIFICATION.md
```

---

### Error Handling

- If the URL is unreachable, attempt alternate formats then report the error
- If job postings are not publicly accessible, note the gap and use alternative signals
- If the company has minimal public presence, reduce confidence levels across the board and note data limitations
- Always produce a qualification report with whatever data is available — even incomplete data is valuable for prioritization
- If BANT score is below 25 and confidence is Low/Inferred across all dimensions, recommend manual research before any outreach

### Cross-Skill Integration

- If `COMPANY-RESEARCH.md` exists, use it to pre-populate company data and skip redundant research
- If `DECISION-MAKERS.md` exists, use it for Authority and Champion analysis
- If `COMPETITIVE-INTEL.md` exists, use it for current solution and switching cost analysis
- Suggest follow-up: `vintoria-prospect-research` for decision maker deep dive, `vintoria-outreach` for engagement sequence

## Decision makers and contacts

### Terminal Output

Display a condensed summary in the terminal:

```
=== DECISION MAKER INTELLIGENCE COMPLETE ===

Company: [name]
Buying Committee Size: [X] contacts identified

Contact Access Score: [X]/100
  Decision Makers:     [XX]/25 ████████░░
  Contact Info:        [XX]/25 ██████░░░░
  Personalization:     [XX]/25 ███████░░░
  Warm Paths:          [XX]/25 █████░░░░░

Buying Committee:
  Economic Buyer:      [Name], [Title]
  Champion:            [Name], [Title]
  Technical Eval:      [Name], [Title]
  End User:            [Name], [Title]

Email Pattern: [pattern]

Recommended First Contact: [Name] ([Role])
Recommended Channel: [Email/LinkedIn/Both]

Full report saved to: prospects/<slug>/DECISION-MAKERS.md
```

---

### Error Handling

- If the team page does not exist or is empty, rely entirely on LinkedIn research and web search
- If no contacts are found, note this as a critical gap and recommend manual LinkedIn research
- If the company is very small (1-5 people), adapt the buying committee framework — the founder likely fills most roles
- If the company is very large (5000+), focus on the specific division or department most relevant to your solution
- Always produce a report with whatever contacts are found, even if incomplete

### Cross-Skill Integration

- If `COMPANY-RESEARCH.md` exists, use leadership data to pre-populate contacts
- If `LEAD-QUALIFICATION.md` exists, use authority and champion findings
- If `OUTREACH-SEQUENCE.md` exists, check for alignment with contact strategy
- Suggest follow-up: `vintoria-outreach` for full email sequence, `vintoria-close` for meeting preparation

## Competitive intelligence

### Rules and Constraints

1. **Honest about competitor strengths.** Every battle card must include genuine competitor strengths. If you portray every competitor as terrible, the salesperson loses credibility the moment the prospect pushes back.
2. **Never fabricate intelligence.** If a competitor's pricing, feature, or capability cannot be verified, label it as "Reported" or "Unverified." Sales credibility depends on accuracy.
3. **Specific over generic.** "Better customer support" is useless. "Dedicated account manager for all plans, with average response time of 2 hours vs. their 24-hour SLA" is actionable.
4. **Detection confidence matters.** Always label confidence levels on detected technologies. A High confidence detection (explicit badge on their website) carries different weight than a Low confidence inference (common tool in their industry).
5. **Never recommend bashing competitors.** The battle cards should help the salesperson position and differentiate, not attack. Negative selling backfires.
6. **Focus on what matters to THIS prospect.** Not every feature gap or competitive advantage is relevant to every deal. Prioritize the battle card content based on the prospect's likely priorities and pain points.
7. **Switching costs must be realistic.** Underestimating switching costs makes you look naive. Overestimating them makes the deal feel impossible. Be accurate.
8. **If previous analysis files exist** (PROSPECT-ANALYSIS.md, COMPANY-RESEARCH.md, LEAD-QUALIFICATION.md), incorporate findings about the prospect's priorities, pain points, and evaluation criteria into the competitive positioning.
9. **Landmine questions must be genuinely curious.** They should be questions any smart buyer would ask — not transparent traps designed to make the competitor look bad.
10. **Update frequency.** Competitive intelligence has a shelf life. Note the date of each source and recommend a refresh timeline (typically every 3-6 months or before a major competitive deal).
