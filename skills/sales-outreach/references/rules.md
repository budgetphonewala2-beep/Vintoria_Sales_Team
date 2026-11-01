# sales-outreach — Rules, errors and integration


## Terminal Output

Display a condensed summary in the terminal:

```
=== OUTREACH SEQUENCE GENERATED ===

Prospect:  [company name]
Contact:   [name], [title]
Framework: [selected framework]

Outreach Readiness Score: [X]/100
  Personalization:    [XX]/25 ████████░░
  Trigger Events:     [XX]/25 ██████░░░░
  Channel Strategy:   [XX]/25 ███████░░░
  Message-Market Fit: [XX]/25 █████░░░░░

Sequence Overview:
  Email 1 (Day 1):  The Hook — [subject line A]
  Email 2 (Day 3):  The Value Add — [subject line A]
  Email 3 (Day 7):  The Social Proof — [subject line A]
  Email 4 (Day 14): The Different Angle — [subject line A]
  Email 5 (Day 21): The Breakup — [subject line A]

LinkedIn Touchpoints: 4 (Day 0, 5, 10, 18)

Best Send Time: [day/time recommendation]
Email Pattern: [detected pattern]

Full sequence saved to: prospects/<slug>/OUTREACH-SEQUENCE.md
```

---

## Error Handling

- If no personalization data is found, note the limitation and use industry-level personalization (weakest approach)
- If the contact's LinkedIn profile is not found, proceed with company-level personalization only
- If no case study or proof point is available for Email 3, use an industry benchmark or third-party data
- If the prospect company has very limited online presence, focus on industry triggers and general pain points
- Always generate a complete 5-email sequence regardless of personalization quality, but clearly note when emails rely on weak personalization
- If running as subagent and time is limited, prioritize Email 1 quality over completeness of emails 4-5

## Cross-Skill Integration

- If `COMPANY-RESEARCH.md` exists, use company data for personalization and context
- If `DECISION-MAKERS.md` exists, use contact profiles and personalization anchors
- If `LEAD-QUALIFICATION.md` exists, use pain points and buying signals for messaging
- If `COMPETITIVE-INTEL.md` exists, use competitive positioning for differentiation angles
- Suggest follow-up: `sales-prep` for meeting preparation after getting a response, `sales-followup` for post-meeting sequence, `sales-objections` for deeper objection handling
