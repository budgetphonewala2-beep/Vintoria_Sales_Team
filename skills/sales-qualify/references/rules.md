# sales-qualify — Rules, errors and integration


## Terminal Output

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

## Error Handling

- If the URL is unreachable, attempt alternate formats then report the error
- If job postings are not publicly accessible, note the gap and use alternative signals
- If the company has minimal public presence, reduce confidence levels across the board and note data limitations
- Always produce a qualification report with whatever data is available — even incomplete data is valuable for prioritization
- If BANT score is below 25 and confidence is Low/Inferred across all dimensions, recommend manual research before any outreach

## Cross-Skill Integration

- If `COMPANY-RESEARCH.md` exists, use it to pre-populate company data and skip redundant research
- If `DECISION-MAKERS.md` exists, use it for Authority and Champion analysis
- If `COMPETITIVE-INTEL.md` exists, use it for current solution and switching cost analysis
- Suggest follow-up: `sales-contacts` for decision maker deep dive, `sales-outreach` for engagement sequence
