---
name: vintoria-icp
description: "Builds workspace/icp/ICP.md for VINTORIA: 3 to 5 buyer segments drawn from the 270 services and 12 disciplines, each with firmographics, observable triggers, pains in the buyer's words, titles, best-fit service IDs, anti-fit and where to find them, plus a deterministic 0 to 100 lead scoring rubric with A+ to D bands and a 10-signal verification test. Use for 'define our ICP', 'who should we target', 'build lead scoring', 'which segment first', 'score this lead', 'who buys our services', 'our ICP is stale', or Hinglish like 'kisko bechna hai'."
---

# VINTORIA ICP Builder

Produces `workspace/icp/ICP.md`: the segments we hunt, the signals that prove a buyer is in market, and the score that decides whether a lead enters the pipeline.

## When to use / When not to use

| Use it when | Do not use it when |
|---|---|
| `ICP.md` is missing and hunting is about to start | Scoring one existing lead (apply the rubric, no rebuild) |
| `OFFER.md` changed lanes or active disciplines | Building the offer itself (use `vintoria-offer`) |
| Reply or win rate has shifted across segments | Researching one company (use `vintoria-research`) |
| The seller wants new markets, sizes or industries | Writing messages (use `vintoria-outreach`) |
| Anti-fit keeps appearing in lost deals | The user wants a price or a timeline |

## Inputs needed (and what to do if missing)

| Input | Source | If missing |
|---|---|---|
| Offer lanes and active disciplines | `workspace/profile/OFFER.md` | Build a provisional ICP from the catalog and tell the seller to run `vintoria-offer`. |
| Seller markets, languages, capacity | `workspace/profile/SELLER-PROFILE.md` | Assume the seller's stated countries only. If none, mark geography `Not found`. |
| Win and loss evidence | `pipeline.csv`, `workspace/prospects/*/HISTORY.md` | Use `Not found` and mark the rubric as untested. |
| Segment candidate list | Discipline files `../vintoria/references/services/*.md` | Read all 12 before proposing segments. |
| Existing `ICP.md` | `workspace/icp/ICP.md` | Create it. |

Read `../vintoria/references/truth-rules.md` and `../vintoria/references/compliance.md`. A segment that can only be reached with purchased lists is not a segment.

## Workflow

1. Read `OFFER.md`, the seller profile, all 12 discipline files and the last 40 pipeline rows if they exist.
2. Collect candidate segments from the discipline files ("Who buys this") and the seller's actual wins. Label each candidate with its source.
3. Cut to 3 to 5 segments. Decision rules:
   - Keep a segment only if at least 2 observable signals exist for it in a discipline file or the pipeline.
   - Drop any segment we cannot serve from an **Active** discipline.
   - Drop any segment whose only route to market is a purchased list.
   - If more than 5 survive, rank by (active lanes served, existing wins, reachability) and cut the rest.
4. For each segment, write the eight fields: firmographics, observable triggers, pains in the buyer's words, buyer titles, best-fit service IDs, anti-fit, where to find them, message angle.
   - Pains must be written as the buyer would say them, short and plain. Never as a marketing claim.
   - Service IDs: 2 to 6 exact IDs from the catalog, all inside active disciplines.
   - Anti-fit: at least 2 observable conditions, taken from the discipline file's "Do not sell when".
5. Apply the scoring rubric below. Weights are fixed and sum to 100. Never re-weight mid-scoring.
6. Write the 10-signal test plan. For each signal, state exactly how to verify it, which source proves it, and how many intent points it contributes.
7. Define the score bands and the action each band triggers. Bands are hard cut-offs, never rounded.
8. Write segment message angles: one angle per segment, one first-line shape, the service to name, and the proof needed before sending.
9. Save `ICP.md`. Then run the quality gates against it.
10. State in one line which segment to hunt first, and why, using evidence from the file.

### Scoring rubric (0 to 100, deterministic)

| Part | Weight | 0 points | Partial | Full marks |
|---|---|---|---|---|
| Intent | 30 | no signal found | signal older than 90 days, or inferred only (15) | dated trigger verified this session, 90 days or newer (30) |
| Fit | 25 | wrong industry, size or model | 2 of 3 match (15) | industry, size and business model match the segment and a service gap is observable (25) |
| Authority | 20 | nobody identified | influencer or champion only (12) | named economic buyer with title and a public source (20) |
| Reachability | 15 | no route | role inbox, contact form or switchboard only (5); named person, channel unverified (10) | named person with a business email or public business channel (15) |
| Timing | 10 | no event | event within 180 days (6) | dated deadline, budget cycle or launch within 90 days (10) |

Rules:
- Score each part once, from the evidence table only. Snippet-only evidence caps Intent at 15.
- Sum the parts, round down, record the integer in `pipeline.csv`.
- A lead with no named person is capped at 45 (C band) however strong the fit.
- Never score a lead above 74 until the dossier exists.

### Score bands

| Band | Score | Meaning | Action |
|---|---|---|---|
| A+ | 90 to 100 | in market now, right person, reachable | research and outreach the same day |
| A | 75 to 89 | strong fit, one gap | research next, outreach within 48 hours |
| B | 60 to 74 | worth a dossier, timing unproven | research queue, no outreach yet |
| C | 40 to 59 | weak signal or no person | verify one more signal or park |
| D | 0 to 39 | out of segment | do not add; log the reason |

Pipeline entry floor: **B (60)**. Outreach preference: **A (75)** and above.

### 10-signal test plan

| # | Signal | How to verify | Source | Intent points |
|---|---|---|---|---|
| 1 | Public ask for this work | Open the post, record URL, date, exact words | LinkedIn, X, Reddit, HN | 30 |
| 2 | Job ad naming the role or stack | Open the ad, record board, posted date, requirement line | Job boards, careers page | 20 |
| 3 | Site defect visible in one session | Fetch the page, record what is missing (title, viewport, 404) | Prospect site | 15 |
| 4 | Changelog or blog gap | Record the newest dated entry and months since | Prospect site | 10 |
| 5 | Store review complaint | Quote the review with date and app version | App Store, Play Store | 20 |
| 6 | Funding, merger or leadership change | Record the announcement date and source | Press page, news | 15 |
| 7 | Hiring spike in one function | Count 3 or more related roles within 60 days | Careers page, job boards | 15 |
| 8 | Pricing or plan change | Record the page and capture date | Pricing page | 10 |
| 9 | Stack or platform migration | Quote the ad or doc naming the old and new stack | Job ad, docs, blog | 15 |
| 10 | Public vendor or tool recommendation request | Open the thread, record date and the ask | Reddit, HN, communities | 25 |

Rule: at least **2 of 10** must be verified from a page you opened before a prospect is added, and at least **1** must be dated within 90 days. Signals stack only up to the intent weight of 30.

## Output format

```markdown
# ICP.md
Version: 1.0
Last updated: YYYY-MM-DD
Built from: OFFER.md (date), SELLER-PROFILE.md (date), pipeline rows reviewed: N

## Scoring rubric
| Part | Weight | Scoring rule |
|---|---|---|
| Intent | 30 | ... |

## Score bands
| Band | Score | Action |
|---|---|---|

## Segment priority
1. <segment> because <evidence>
2. ...

## Segment 1: <name>
- Firmographics: industry, headcount, revenue band, geography, business model, tech maturity
- Observable triggers: 2 to 5, each verifiable
- Pains in the buyer's words: "<plain quote-shaped sentence>"
- Buyer titles: <3 to 5 titles, economic buyer first>
- Best-fit services: <ID> <name>; <ID> <name>
- Anti-fit: <observable condition>; <observable condition>
- Where to find them: <source and query shape>
- Message angle: <one angle, one first-line shape, service to name, proof needed>

## Segment 2: <name>
<same fields>

## Segment 3: <name>
<same fields>

## 10-signal test plan
| # | Signal | Verification step | Source | Points |
|---|---|---|---|---|

## Segment message angles
| Segment | Angle | First-line shape | Service to name | Proof required |
|---|---|---|---|---|

## Change log
| Version | Date | What changed | Evidence |
|---|---|---|---|
```

## Quality gates

| Gate | Floor |
|---|---|
| Segments | 3 to 5 |
| Signals per segment | 2 or more, each observable |
| Service IDs per segment | 2 to 6, all valid and inside active disciplines |
| Anti-fit conditions per segment | 2 or more, observable |
| Rubric weights | exactly 30 / 25 / 20 / 15 / 10 |
| Bands | A+ 90-100, A 75-89, B 60-74, C 40-59, D 0-39, no gaps |
| Test plan | exactly 10 signals, each with a verification step and a source |
| Message angles | one per segment, none making an unproven claim |
| Invented facts | zero metrics, benchmarks, market sizes or buyer quotes |
| Purchased-list routes | zero |

Below the floor: do not hand the file to `vintoria-hunt`. Fix it first, or mark `Version: 0.9 provisional` and say which gate failed.

## Failure handling

- **No web access.** Build the ICP from the catalog and pipeline. Mark trigger verification as `Unverified` and cap every score at 55 until checked.
- **No OFFER.md.** Build from the catalog's discipline segments, mark `provisional`, and run `vintoria-offer` before hunting.
- **No wins yet.** Use reachability and signal strength only, and say the rubric is untested.
- **Seller wants 8 segments.** Refuse to exceed 5. Ask for the two that produced replies or meetings; keep those.
- **Ambiguous request.** "Who should we target" builds the ICP. "Is this lead good" applies the rubric and returns a band only.
- **Conflicting evidence.** Two sources disagree: prefer the page the prospect controls, record both, and score the lower.

## Definition of done

- [ ] `workspace/icp/ICP.md` exists with a version, date and build sources.
- [ ] 3 to 5 segments, each with all eight fields filled or `Not found`.
- [ ] Rubric weights and bands match this file exactly.
- [ ] 10-signal test plan complete with verification steps.
- [ ] Segment priority ordered with a stated evidence reason.
- [ ] Message angles present, each tied to a named service and a proof requirement.
- [ ] Zero invented metrics, quotes or market data.
- [ ] Quality gates run; result stated in one line.
- [ ] Hunter told which segment to start with and the pipeline entry floor.
