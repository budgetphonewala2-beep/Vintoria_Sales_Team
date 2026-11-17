# vintoria-setup — Output format


## Output Format

Write the complete ICP to `IDEAL-CUSTOMER-PROFILE.md` in the current working directory.

Structure the output file with these sections in order:

```markdown
# Ideal Customer Profile: [Business/Product Name]

> Generated on [date] | Based on: [brief description of the business]

## ICP Summary
[2-3 paragraph executive summary of who the ideal customer is]

## Firmographic Criteria
[Table format with criteria, ranges, rationale]

## Technographic Profile
[Tech stack requirements, sophistication level, integration needs]

## Behavioral Signals
[Observable behaviors, content consumption, community membership]

## Pain Point Map
[Ranked pain points with severity, manifestation, triggers]

## Budget Qualifiers
[Financial criteria, deal size, ROI expectations]

## Channel Strategy
[How to reach them, decision process, content preferences]

## Negative ICP (Who to Avoid)
[Disqualification criteria with explanations]

## ICP Scoring Rubric
[100-point scorecard with grade bands]

## Buyer Personas

### Persona 1: [Name]
[Full persona details]

### Persona 2: [Name]
[Full persona details]

### Persona 3: [Name] (if applicable)
[Full persona details]

## Prospecting Playbook
[Where to find them, search strategies, prioritization, timing]

## Competitive Context
[Brief competitive landscape, positioning, displacement scenarios]

## ICP Maintenance Guide
[When to review, what signals indicate the ICP needs updating]

---

*ICP built by AI Sales Team | Review and refine quarterly*
```

---

## ICP Maintenance Guidance

Include a brief section at the end of the output file that advises on ICP maintenance:

- **Review Cadence:** Recommend reviewing the ICP quarterly or after any major product change, pricing change, or market shift.
- **Update Triggers:** List specific events that should prompt an ICP review:
  - You close 3+ deals outside the current ICP parameters
  - You lose 3+ deals to the same competitor or objection
  - Your product adds a major new feature or enters a new market
  - Your pricing model changes significantly
  - A major competitor enters or exits the market
- **Feedback Loop:** After running `vintoria-prospect-research` on 10+ companies, review which scores correlated with actual deal outcomes. Adjust ICP criteria and scoring weights accordingly.
- **Version Control:** Encourage the user to date-stamp ICPs and keep previous versions for comparison.

---
