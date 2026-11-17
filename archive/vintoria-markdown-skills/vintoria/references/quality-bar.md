# Quality bar — the score an agent must hit before showing work

Three artifacts get scored: the **first email**, the **dossier**, and the **proposal**. Score deterministically, list
the exact fixes, and do not show a human anything below the floor.

## 1. First email / sequence email — 0–100

| Part | Max | Full marks when |
|---|---|---|
| Situation | 25 | The first two lines are only about them, reference something specific you verified (their page, post, ad, product), and survive the deletion test below |
| Value | 20 | One sentence says what VINTORIA does for this exact problem, and it maps to a named catalog service |
| You-ratio | 10 | At least 2 sentences about them for every 1 about us |
| CTA | 15 | Exactly one low-effort question; no meeting ask, no calendar link, no call request in email 1 |
| Length | 15 | Email 1: 50–120 words. Follow-ups: 25–90. Breakup: ≤ 60 |
| Subject | 5 | Email 1 only: 2–5 words, lowercase, no hype, no fake `Re:`/`Fwd:` |
| Clean | 10 | No banned openers, no AI tells, no jargon, no em dash, no `!`, no links in email 1, no bold/HTML, no sentence over 28 words |

**Deletion test (hard gate).** Remove the prospect's company name and every personal noun. If the email still makes
sense for any company in the same industry, the situation score is capped at 10 and the email cannot go out.

**Banned openers:** `I hope this email finds you well`, `Hope you're doing well`, `I came across your`, `I wanted to
reach out`, `My name is` (in line 1), `Quick question`, `Just following up` as a whole email, `Touching base`.

**AI tells to remove:** `delve`, `leverage` (as a verb), `seamless`, `robust`, `cutting-edge`, `elevate`, `unlock`,
`game-changer`, `in today's fast-paced`, `it's worth noting`, three-item lists in every sentence, `not only… but also`,
`—` em dash, curly-quote padding, `I'd be happy to`.

**Verdicts**

| Score | Verdict | Action |
|---|---|---|
| 85–100 | premium | show it |
| 80–84 | ship | show it, note the remaining fix |
| 65–79 | one more pass | rewrite the weak part, rescore |
| 0–64 | rewrite | do not show |

Floor to show the seller: **80**.

## 2. Dossier — 0–100

| Part | Max | Full marks when |
|---|---|---|
| Evidence | 30 | Every section has a source (URL + date); no section relies on memory or a snippet alone |
| Fit | 20 | Names 1–3 catalog services that match observed signals, with the signal next to each |
| Buyer | 15 | At least one named decision maker with a title and a source; role predicted from title |
| Hook | 15 | The top hook is specific, verified, and relevant to a service VINTORIA sells |
| Risks | 10 | Real disqualifiers or unknowns stated plainly |
| Next step | 10 | One concrete next action with an owner and a date |

**Floor: 70.** Below 70, the dossier is not ready for outreach; keep researching or disqualify.

## 3. Proposal — 0–100

| Part | Max | Full marks when |
|---|---|---|
| Problem | 20 | Restates the buyer's problem in their words with evidence |
| Scope | 25 | Every line cites a catalog service ID + name; inclusions and exclusions are explicit |
| Options | 15 | Three options (core / recommended / expanded) with different scope, never different discounts |
| Plan | 15 | Phases, dependencies, acceptance criteria; no invented dates — use working days or `[TO CONFIRM]` |
| Risk | 10 | Assumptions, buyer responsibilities, change-request path |
| Commercial | 15 | Price fields are placeholders filled by the seller; nothing invented |

**Floor: 80.** A proposal without exclusions, acceptance criteria or a change-request path is not shippable.

## Self-review discipline

1. Score before showing. State the score and the fixes in one line.
2. If the user asks to skip scoring, score anyway and say why it matters.
3. Never round up. A 79 is not an 80.
