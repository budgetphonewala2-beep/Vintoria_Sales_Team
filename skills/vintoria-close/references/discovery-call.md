# Discovery call: brief, agenda, scorecard, questions

> Imported from the instruction-only Vintoria set and wired to the engine (pipeline, prospect folders, seller profile).

Turns a booked call into a scored, evidence-backed qualification with one written next step.

## When to use / When not to use

- Use when a call is booked and needs a brief, agenda, question set or scoring, or when a call was held and needs notes and a next step.
- Use when a no-show or reschedule needs a policy and a recovery message.
- Do not use before any contact exists (`vintoria-outreach`), before a reply is classified (`vintoria-reply-book`), or to write a proposal (`vintoria-close`). Never invent buyer answers, price work, or replace the seller's judgement on a live call.

## Inputs needed (and what to do if missing)

| Input | Read from | If missing |
|---|---|---|
| Workspace rules | `../vintoria-sales/references/truth-rules.md`, `../vintoria-sales/references/quality-bar.md` | Read them before writing one line. |
| What we sell | `OFFER.md` and the matching file under `../vintoria-sales/references/services-` | Fall back to `../vintoria-sales/references/service-catalog.md`; never cite an unlisted service. |
| Who we target | `IDEAL-CUSTOMER-PROFILE.md` | Score service fit from the catalogue; run `vintoria-setup` after the call. |
| Prospect research and proof | `prospects/<slug>/DOSSIER.md`, `SITE-AUDIT.md` | Use whichever exists; if both are missing, run `vintoria-prospect-research` or triage live first. Never claim an audit that does not exist. |
| Prior contact | `OUTREACH-SEQUENCE.md`, their replies in the pipeline (`python <SCRIPTS>/core/pipeline.py show`), `MEETING-PREP.md` | Start from zero and ask what prompted the meeting. |
| Seller identity and price position | `SELLER-PROFILE.json` (`python <SCRIPTS>/core/seller_profile.py show`) and `../vintoria-sales/references/pricing-policy.md` | Keep working; never claim proof, clients or prices; score budget signal on the buyer's words only. |

## Workflow

1. Read `../vintoria-sales/references/truth-rules.md`, `../vintoria-sales/references/quality-bar.md` and `../vintoria-sales/references/team.md` before drafting anything.
2. Build the pre-call brief from saved files only, in this order: `MEETING-PREP.md`, `DOSSIER.md`, `SITE-AUDIT.md`, `OUTREACH-SEQUENCE.md`, their replies in the pipeline (`python <SCRIPTS>/core/pipeline.py show`), the pipeline history (`python <SCRIPTS>/core/pipeline.py note`), then the discipline file. Write five lines only: who they are, why now, the problem, the service IDs, the one thing to confirm. Every line carries a source or `Not found`.
3. Confirm the call length. Use 30 minutes by default; use 45 when the work spans two disciplines or the buyer brings more than two people.
4. Run the agenda below and do not skip playback.
5. Ask from the banks. Core first, service banks only after the problem is named. Never ask more than one question per turn.
6. Record verbatim quotes where possible; if the buyer did not answer, write `Not found`. Never fill a gap with an assumption.
7. Score after the call, not during it: all seven parts, then the bands and the hard no-go rules. Test each red flag and record the test and the observation.
8. Choose exactly one next step from the scripts, with the exact words, the owner and the date.
9. Write `MEETING-NOTES.md` within 2 hours, update the pipeline history (`python <SCRIPTS>/core/pipeline.py note`) and the pipeline (`python <SCRIPTS>/core/pipeline.py`) (`stage`, `score`, `next_action`, `next_due`, `owner`, `updated`), then send the 24-hour follow-up at a score of 80 or above.

### Pre-call research checklist

| Check | Pass condition |
|---|---|
| Problem and evidence | One sentence in the buyer's words, plus at least two dated observations from their site, store, ads or job ads, all sourced. |
| Service fit | One to three catalogue IDs, each beside the signal that justifies it. |
| People and history | The person on the call, their title, who else decides, and every prior touch with dates. |
| Open questions | Three questions the files cannot answer. |

### 30-minute agenda

| Min | Segment | What happens | Output |
|---|---|---|---|
| 0 to 2 | Frame | Confirm time, purpose, attendees and what happens after the call. | Agenda agreed |
| 2 to 6 | Situation | "What changed that made this worth a call now?" Let them talk. | Their words, dated |
| 6 to 12 | Problem and impact | One problem, then its cost, risk or lost outcome. | Problem and impact statement |
| 12 to 17 | Current state | Tools, owners, workarounds, the last attempt. | Systems map |
| 17 to 21 | Decision and money | Who decides, how money is approved, what the signal is. | Decision map |
| 21 to 25 | Timeline and fit | Dates, constraints, what must not change. | Timeline and service fit |
| 25 to 30 | Playback and next step | Repeat problem, impact, decision path and next step, then book it. | Confirmed understanding, owner and date |

**45-minute version:** same order, plus 5 minutes to problem and impact (probe the evidence), 5 to current state (walk one workflow end to end), and 5 to decision and money (name every approver). Do not add segments.

### Qualification scorecard (0 to 100)

| Part | Max | Full marks when |
|---|---|---|
| Problem clarity | 20 | One problem, in their words, with the person who feels it named. |
| Impact | 15 | A cost, risk or lost outcome, with a number or a concrete consequence. |
| Authority | 20 | The economic buyer attended, or is named with a route and a date. |
| Timeline | 15 | A real date or event drives the work. |
| Budget signal | 10 | A budget exists, a range was stated, or a funding route is named. |
| Service fit | 10 | The need maps to named IDs from the 270. |
| Risk | 10 | Delivery, data, access and compliance risks are known and owned. |

Score each part as an integer from 0 to its maximum; an unanswered part scores 0 and is written as `Not found`. Total the seven parts.

Bands: **A 80 to 100** proposal ready; **B 65 to 79** paid discovery or a bounded pilot before any proposal; **C 50 to 64** nurture with a named trigger and revisit date, no proposal; **D 0 to 49** disqualify, record the reason, close politely.

**Hard no-go, whatever the score:** no authority in the room and no route to the economic buyer within 30 days; the need falls outside all 270 services; regulated data with no compliance owner on their side; a free build, guaranteed result, or work before scope; no one owns the problem after the call.

### Question banks

Ask 8 to 12 questions in total. Core first, then the service bank that matches the named problem.

| Bank | Questions |
|---|---|
| Opening | 1) What changed that made this worth a call now? 2) What have you already tried? 3) Who else is involved? 4) What would a good outcome look like in one sentence? |
| Problem and impact | 1) Which task or decision is failing today? 2) What happens when it fails, and who feels it first? 3) What does it cost in money, time or risk? 4) How often does it happen, and what happens if nothing changes this year? |
| Current state and decisions | 1) Which systems hold the data, and who runs the process step by step? 2) What breaks most often, and where? 3) Who signs this off, and who can say no? 4) What does the approval step look like, and what would make you cancel? |
| Budget signal | 1) Is there a budget line, or does one need creating? 2) Which cycle does it sit in? 3) What did the last similar project cost, roughly? 4) Who controls that budget? |
| Timeline | 1) What date matters, and why? 2) What must be live before that date? 3) What can wait? 4) What would delay the start? |

| Service bank | Questions |
|---|---|
| AI and data | 1) Which decision should the system handle, and what is a correct answer? 2) Where does the knowledge live, and who keeps it current? 3) How will you judge output quality before launch? 4) Which data may the model never see? |
| Automation | 1) Which process breaks most often, and where? 2) How long does one run take today? 3) Which system is the source of truth? 4) What should happen when a step fails? |
| Web and SaaS | 1) Which pages or flows carry revenue today? 2) Who edits content after launch? 3) Which integrations must exist on day one? 4) What must keep working during the switch? |
| E-commerce | 1) Which platform, and what forced this review now? 2) How many products, variants and markets? 3) What happens from payment to fulfilment? 4) What is the peak season, and what must stay live? |
| SEO and growth | 1) Which channel produced the last ten customers? 2) Which pages or terms matter most to revenue? 3) Who owns analytics and ad accounts? 4) Which number does the board ask about? |

### Red flags and how to test them

| Red flag | Test | What it means |
|---|---|---|
| Vague problem | Ask for one failing task and one recent example. | If no example exists, the problem is not real. Score problem clarity 0. |
| No owner | Ask who signs the invoice, who owns the result after launch, and who has said no before. | Two silences, or more than three approvers with no named owner, stalls every proposal. |
| Budget theatre | Ask which cycle and who controls it, then what was spent last time. | A range with no owner is not a budget signal. |
| Free work request | Ask what they need before any paid step. | A free audit or sample is a disqualifier unless the seller agrees. |
| Urgency without access | Ask for the date and the access needed to hit it. | A date with no access is pressure, not a timeline. |

### No authority, no budget, no urgency

- **No authority:** "Who else needs to see this before a decision, and can we get them into a short call?" Ask for a joint 20-minute call; never send a proposal to a non-buyer.
- **No budget:** "Is this unfunded, or funded in a later cycle? Which one, and when does it open?" Scope one small phase and set a revisit date at the budget gate.
- **No urgency:** "What would have to happen for this to become the priority this quarter?" Record the trigger event and move to nurture with that trigger.

### Next-step scripts

| Outcome | Exact words | Commit |
|---|---|---|
| Proposal | "I will send a written scope with three options by <date>. It will name what is included, what is not, and what we need from you. Can we hold 20 minutes on <date> to walk through it?" | Owner, date, time |
| Paid discovery | "Before I quote a build, I recommend a short paid discovery. It produces the scope and the risks in writing. Shall I send that as a separate one-page scope?" | Scope sent by date |
| Pilot | "The lowest-risk start is one bounded phase: <named scope>. It proves the approach before the full programme. Do you want me to price that phase alone?" | Pilot scope owner |
| Nurture | "This sounds like a next-quarter decision. I will check in on <date> unless something changes sooner. Is there a trigger I should watch for?" | Trigger and revisit date |
| Disqualify | "From what you have described, this is not work we do well. The closest fit would be <named service> if that becomes the need. I would rather say so now than waste your time." | Polite close, reason recorded |

### No-show policy

- Wait 10 minutes, then send one short message confirming you are present. No more than two calls and one message per no-show.
- Log the no-show in the pipeline history (`python <SCRIPTS>/core/pipeline.py note`) with the date, channel and attempt, and offer two specific slots in the same message.
- After two no-shows, move to nurture with a trigger date. Never mark a call as held, booked or completed unless it happened.

### 24-hour follow-up

- Send within 24 hours on the same channel, 50 to 120 words: their problem in their words, the one next step, one date.
- Make no new claims and attach nothing that was not promised.
- Score it against `../vintoria-sales/references/quality-bar.md`; the floor to send is 80.
- Log it in `OUTREACH-SEQUENCE.md` and update the pipeline (`python <SCRIPTS>/core/pipeline.py`).

## Output format

Write `prospects/<slug>/MEETING-NOTES.md` exactly in this shape:

```
# Discovery notes: <company>
Date: <YYYY-MM-DD> | Duration: <minutes> | Channel: <call or video>
Attendees: <name, title> (buyer) | <seller name> (VINTORIA)
Source files: <BRIEF, DOSSIER, SITE-AUDIT, OUTREACH, REPLIES>

## Why now and the problem
<one paragraph in the buyer's words, sourced>
Problem: <verbatim quote or Not found> | Evidence: <file or page, date>
Impact: <verbatim quote or Not found>

## Current state
| Area | What they said | Source |
|---|---|---|
| | | |

## Decision, budget and timeline
Economic buyer: <name or Not found> | Approvers: <names or Not found>
Approval route: <words or Not found>
Budget signal: <what was said, or Not found>
Trigger date: <date or Not found> | Constraints: <words or Not found>

## Service fit
| ID | Service | Signal from the call |
|---|---|---|
| | | |

## Qualification score
| Part | Score | Max | Evidence |
|---|---|---|---|
| Problem clarity | | 20 | |
| Impact | | 15 | |
| Authority | | 20 | |
| Timeline | | 15 | |
| Budget signal | | 10 | |
| Service fit | | 10 | |
| Risk | | 10 | |
| **Total** | | **100** | |

Band: <A, B, C or D> | Decision: <proposal, paid discovery, pilot, nurture, disqualify>

## Red flags and open questions
<each flag, the test used, the observation, or "None observed">
<questions the files cannot answer, each with an owner>

## Next step
Action: <one action> | Owner: <name> | Date: <YYYY-MM-DD>
Exact words used: "<quote>"

## Follow-up
Sent: <date or not sent> | Channel: <channel> | Score: <0 to 100>
```

## Quality gates

- All seven scorecard parts are filled; an unanswered part is 0 with `Not found` beside it.
- The band and decision match the score table, and no proposal is recommended below 80.
- At least three verbatim buyer quotes appear in the notes.
- The banks hold at least 30 questions before the call, and at least 8 were asked.
- Every buyer fact carries a source or `Not found`; zero invented answers.
- The next step has one action, one owner and one real date.
- The follow-up is written within 24 hours and scores at least 80 before sending.
- the pipeline history (`python <SCRIPTS>/core/pipeline.py note`) and the pipeline (`python <SCRIPTS>/core/pipeline.py`) are updated in the same session; no price appears anywhere.

## Failure handling

- **No web access:** work from saved `DOSSIER.md`, `SITE-AUDIT.md` and their replies in the pipeline (`python <SCRIPTS>/core/pipeline.py show`) only; mark each with its save date as possibly stale; never guess a fact.
- **Missing profile:** keep the call and the score; omit proof claims; use `[PRICE TO CONFIRM]` if money arises; tell the seller to run `vintoria-setup` afterwards.
- **Missing dossier and audit:** run a 20-minute live triage from public pages before the call, or ask the seller to postpone rather than walk in blind.
- **Ambiguous request:** ask which prospect, which call date, and whether the call is booked or held; never score a call that has not happened.
- **Buyer cancels mid-call:** record the reason verbatim, choose nurture or disqualify, and do not chase within 24 hours.
- **Two facts conflict:** prefer the page the prospect controls, say so in the notes, and keep the discrepancy visible.

## Definition of done

- [ ] Pre-call brief written with a source on every line.
- [ ] Agenda chosen and timed to the call length.
- [ ] Questions asked from the banks, one per turn.
- [ ] All seven parts scored, total calculated, band stated.
- [ ] Hard no-go rules applied and recorded.
- [ ] One next step with exact words, owner and date.
- [ ] `MEETING-NOTES.md` written within 2 hours.
- [ ] the pipeline history (`python <SCRIPTS>/core/pipeline.py note`) and the pipeline (`python <SCRIPTS>/core/pipeline.py`) updated.
- [ ] 24-hour follow-up sent and scored at 80 or above.
