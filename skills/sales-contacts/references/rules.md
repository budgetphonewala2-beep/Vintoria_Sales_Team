# sales-contacts — Rules, errors and integration


## Terminal Output

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

## Error Handling

- If the team page does not exist or is empty, rely entirely on LinkedIn research and web search
- If no contacts are found, note this as a critical gap and recommend manual LinkedIn research
- If the company is very small (1-5 people), adapt the buying committee framework — the founder likely fills most roles
- If the company is very large (5000+), focus on the specific division or department most relevant to your solution
- Always produce a report with whatever contacts are found, even if incomplete

## Cross-Skill Integration

- If `COMPANY-RESEARCH.md` exists, use leadership data to pre-populate contacts
- If `LEAD-QUALIFICATION.md` exists, use authority and champion findings
- If `OUTREACH-SEQUENCE.md` exists, check for alignment with contact strategy
- Suggest follow-up: `sales-outreach` for full email sequence, `sales-prep` for meeting preparation
