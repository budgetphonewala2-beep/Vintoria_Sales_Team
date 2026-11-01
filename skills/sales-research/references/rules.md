# sales-research — Rules, errors and integration


## Terminal Output

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

## Error Handling

- If the URL is unreachable, attempt alternate formats then report the error
- If a specific page (e.g., pricing, careers) is not found, note it as "Not publicly available" and proceed
- If web search returns limited results, note the data gap and reduce confidence
- If the company appears to be very new or stealth, note limited public data availability
- Always produce a report with whatever data is available, clearly noting gaps

## Cross-Skill Integration

- If `PROSPECT-ANALYSIS.md` exists, reference overall prospect context
- If `DECISION-MAKERS.md` exists, cross-reference leadership findings
- If `COMPETITIVE-INTEL.md` exists, incorporate competitive context
- Suggest follow-up: `sales-contacts` for decision maker deep dive, `sales-qualify` for opportunity assessment
