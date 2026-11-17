# vintoria-outreach — rules, terminal output, errors and cross-skill use

## Cold outreach

### Terminal Output

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
  Email 1 (Day 0):  The Hook — [subject line A]
  Email 2 (Day 3):  The Value Add — [subject line A]
  Email 3 (Day 7):  The Social Proof — [subject line A]
  Email 4 (Day 14): The Different Angle — [subject line A]
  Email 5 (Day 28): The Breakup — [subject line A]

LinkedIn Touchpoints: 4 (Day 0, 5, 10, 18)

Best Send Time: [day/time recommendation]
Email Pattern: [detected pattern]

Full sequence saved to: prospects/<slug>/OUTREACH-SEQUENCE.md
```

---

### Error Handling

- If no personalization data is found, note the limitation and use industry-level personalization (weakest approach)
- If the contact's LinkedIn profile is not found, proceed with company-level personalization only
- If no case study or proof point is available for Email 3, use an industry benchmark or third-party data
- If the prospect company has very limited online presence, focus on industry triggers and general pain points
- Always generate a complete 5-email sequence regardless of personalization quality, but clearly note when emails rely on weak personalization
- If running as subagent and time is limited, prioritize Email 1 quality over completeness of emails 4-5

### Cross-Skill Integration

- If `COMPANY-RESEARCH.md` exists, use company data for personalization and context
- If `DECISION-MAKERS.md` exists, use contact profiles and personalization anchors
- If `LEAD-QUALIFICATION.md` exists, use pain points and buying signals for messaging
- If `COMPETITIVE-INTEL.md` exists, use competitive positioning for differentiation angles
- Suggest follow-up: `vintoria-close` for meeting preparation after getting a response, `vintoria-outreach` for post-meeting sequence, `vintoria-close` for deeper objection handling

## Follow-ups

### Rules and Constraints

1. **Every email must add NEW value.** Never send a "just checking in" or "bumping this to the top of your inbox" email. If there is nothing new to say, do not send.
2. **Reference specific conversation points.** Generic follow-ups get deleted. Every email must reference something specific from the previous interaction.
3. **One clear next step per email.** Never give multiple CTAs. One email = one ask.
4. **Under 100 words per email.** Busy people do not read long follow-ups. Respect their time.
5. **Appropriate urgency.** Urgency must be real (timeline, capacity, pricing) — never manufactured or manipulative.
6. **Personalization is mandatory.** Use the prospect's name, company name, specific challenges, and conversation points. No [PLACEHOLDER] brackets in the final output.
7. **Professional but human tone.** Write like a helpful human, not a sales bot. Contractions are fine. Overly formal language is not.
8. **No manipulation tactics.** No fake scarcity, no guilt trips, no "I noticed you opened my email" tracking callouts.
9. **Respect the prospect's time and intelligence.** They know you want to sell. Be direct about your intent while providing genuine value.
10. **If previous analysis files exist**, incorporate their data. Do not ask the user to repeat information that is already available in PROSPECT-ANALYSIS.md, COMPANY-RESEARCH.md, or other output files in the working directory.
