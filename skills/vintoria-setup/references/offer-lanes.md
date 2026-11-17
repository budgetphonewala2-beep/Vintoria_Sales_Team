# Offer lanes, active disciplines and the proof map

> Imported from the instruction-only Vintoria set and wired to the engine (pipeline, prospect folders, seller profile).

Produces one file, `OFFER.md`: the lanes we sell, the disciplines we can staff, the proof we may claim, and the work we refuse.

## When to use / When not to use

| Use it when | Do not use it when |
|---|---|
| `OFFER.md` does not exist and the seller is starting | One deal needs scoping (use `vintoria-outreach` or `vintoria-close`) |
| The seller changed focus, capacity or target market | The user wants buyer segments (use `vintoria-setup`) |
| The proof map is older than 90 days or a claim was challenged | The user wants a price (only the seller profile holds prices) |
| Lost deals keep citing "unclear what you do" | The user wants to rename or add a catalog service (the catalog is fixed) |
| A new discipline became staffable and should go active | The user wants a website audit (use `vintoria-prospect-research`) |

## Inputs needed (and what to do if missing)

| Input | Source | If missing |
|---|---|---|
| Service catalog | `../vintoria-sales/references/service-catalog.md` and `services/*.md` | Stop. Never work without the catalog. |
| Seller identity, markets, currency | `SELLER-PROFILE.md` | Create a skeleton with `Not found` fields and continue. |
| Staffing truth (what can be delivered now) | Seller interview | Ask. Do not infer from the catalog. |
| Proof artefacts (live URLs, cases, screenshots, repos) | Seller interview | Mark every unproven lane `Provisional`. |
| Existing `OFFER.md` | `OFFER.md` | Create it in this run. |
| Win/loss reasons | `PIPELINE.md`, the prospect's `HISTORY.md` files | Skip and note `Not found` in the interview record. |

Read `../vintoria-sales/references/truth-rules.md` and `../vintoria-sales/references/pricing-policy.md` before writing a single claim.

## Workflow

1. Read `../vintoria-sales/SKILL.md`, the catalog, all 12 discipline files, truth rules, pricing policy and the quality bar.
2. Read `SELLER-PROFILE.md`. If absent, write the skeleton with these headings only: identity, markets, languages, delivery owner, pricing (empty), proof (empty). Continue.
3. Ask the interview questions below in **one batch**. Stop at 12. If the seller answers fewer than 6, produce a `Provisional` offer and say which lanes are guesses.
4. Classify every discipline as **Active**, **Dormant** or **Excluded** using the rules in step 5. Write the classification down before choosing lanes.
5. Apply the classification rules:
   - Active = the seller can staff it this month without subcontracting **and** holds at least one showable artefact.
   - Dormant = sellable only with a partner, a hire or a longer lead time.
   - Excluded = the seller refuses the work, cannot serve the market, or the discipline conflicts with the profile.
   - Floor 2 active, ceiling 8 active. Above 8, force a ranking and cut the weakest. A studio claiming all 12 is not a positioning.
6. Build 3 to 5 lanes. Rules:
   - One lane = one buyer problem that a single search query could surface.
   - Every lane must map to an **Active** discipline. A Dormant discipline may appear only as a clearly labelled next step.
   - Each lane names 2 to 5 service IDs with exact catalog names. The first is the entry service, the rest are the natural follow-on.
   - Never invent a lane the catalog cannot serve. Never merge two services into one line.
7. Write the disqualifiers. Take 2 or more from the discipline file's "Do not sell when" list and add one seller-specific refusal. Disqualifiers must be observable, not a feeling.
8. Build the proof map. For each claim the seller wants to make, name the exact artefact required and set status `Have`, `Partial` or `Missing`.
   - `Have` = a saved, dated artefact exists and can be shown on request.
   - `Partial` = producible within one working day (a fresh audit of a public URL counts as Partial).
   - `Missing` = nothing exists.
   - Rule: outreach may use `Have` only. `Partial` becomes `[ADD REAL CUSTOMER RESULT]`. `Missing` is deleted or turned into a question.
9. Position breadth without inventing anything:
   - Against freelancers: claim only catalog facts, that 270 named services sit across 12 disciplines, so scope that crosses brand, build and automation stays with one vendor. Never claim seniority, speed, price or availability.
   - Against large agencies: claim only what the file can show, which is named service-level scope, one named owner per prospect (the `owner` column) and written exclusions. Never claim team size, awards, logos, retention rates or "no account managers".
   - Any comparative sentence that cannot be checked against the catalog or the seller profile is deleted.
10. Write `OFFER.md` using the template below. Keep pricing out except the placeholder line.
11. Run the quality gates. If any gate fails, set `Status: Provisional`, list the failing gate at the top, and still save the file.
12. If the request is really about identity, markets, currency or pricing numbers, update `SELLER-PROFILE.md` instead and tell the seller in one line. `OFFER.md` never holds prices.

### Interview questions (maximum 12)

1. Which 3 to 5 problems do buyers pay you for today, in their words?
2. Which disciplines can you staff this month without subcontracting?
3. Which disciplines are on request only, and who delivers them?
4. For each active discipline, what proof can you show: live URL, case, repo, screenshot, client permission?
5. Which proof is public and which is under NDA?
6. Which buyer types do you want more of, and which drain the team?
7. What work do you refuse, and why?
8. Which countries and languages can you serve properly?
9. Who owns delivery, and what is the escalation path when it slips?
10. What do buyers consistently misunderstand about what you do?
11. Which service is the usual first purchase, and which one naturally follows?
12. Which competitor claim have you seen that you cannot honestly support?

## Output format

Write exactly this structure to `OFFER.md`.

```markdown
# OFFER.md
Status: Confirmed | Provisional
Last updated: YYYY-MM-DD
Owner: <seller name>
Built from: catalog 2026, SELLER-PROFILE.md (date), interview (date)

## Positioning statement
<One sentence, 40 words max: who we serve, the problem, the disciplines we use, and one checkable differentiator or nothing.>

## Active disciplines (2 to 8)
| # | Discipline | Services we sell now | Why active | Capacity note |
|---|---|---|---|---|

## Dormant disciplines
| Discipline | When we say yes | Delivery path | Never promise |
|---|---|---|---|

## Excluded disciplines
| Discipline | Reason |
|---|---|

## Offer lanes
### Lane 1: <name>
- Buyer problem: <one sentence>
- Who has it: <role and company shape>
- Entry service: <ID> <exact name>
- Follow-on services: <ID> <name>; <ID> <name>
- Proof we can show: <artefact or [ADD REAL CUSTOMER RESULT]>
- Proof status: Have | Partial | Missing
- Disqualifiers: <observable condition>; <observable condition>
- Where to find these buyers: <source and query shape from ICP.md>

### Lane 2: <name>
<same fields>

### Lane 3: <name>
<same fields>

## Proof map
| Claim | Exact evidence required | Status | Where stored |
|---|---|---|---|
| <claim> | <artefact, date, owner> | Have / Partial / Missing | <path or Not found> |

## What we never sell
- <refusal, with the reason>

## Breadth positioning
### Against freelancers
<checked claims only>
### Against large agencies
<checked claims only>
### What we never say
- <banned claim>

## Commercial boundary
Pricing lives in SELLER-PROFILE.md. Any figure here is [PRICE TO CONFIRM].

## Interview record
| # | Question | Answer | Answered |
|---|---|---|---|
```

## Quality gates

| Gate | Floor |
|---|---|
| Lanes | 3 to 5, no lane outside the catalog |
| Services per lane | 2 to 5 valid IDs, names copied exactly |
| Active disciplines | 2 to 8, each with a stated capacity note |
| Lanes with `Have` proof | at least 2 |
| Proof map rows | 6 or more, at least 50 percent `Have` |
| Disqualifiers per lane | 2 or more, observable |
| Positioning statement | 40 words or fewer, one checkable differentiator or none |
| Interview questions | 12 or fewer, unanswered ones marked `Unanswered` |
| Prices | zero, except `[PRICE TO CONFIRM]` |
| Invented facts | zero clients, metrics, awards, team sizes, timelines, guarantees |

Below the floor: label `Provisional`, state the failing gate, and keep the file usable.

## Failure handling

- **No web access.** The catalog is local, so build the file. Live proof checks become `Partial` with a note to verify.
- **No seller profile.** Create the skeleton, mark identity fields `Not found`, continue.
- **Vague or empty answers.** Use the discipline files' own segment and signal lists as candidate lanes, mark the file `Provisional`, and ask the 5 highest-value questions again next session.
- **Interview conflicts with the profile.** The profile wins for facts; log the conflict in the interview record.
- **Request is really about prices.** Do not build lanes; send the seller to `SELLER-PROFILE.md` pricing and say why.
- **Ambiguous request.** If the user asks what we sell, build the offer. If they ask what to say to one buyer, route to `vintoria-outreach`.

## Definition of done

- [ ] `OFFER.md` exists with `Status`, date and owner.
- [ ] 3 to 5 lanes, each with a buyer problem, exact service IDs, proof requirement and 2 disqualifiers.
- [ ] Active disciplines between 2 and 8; dormant and excluded lists present.
- [ ] Proof map complete, statuses set, every `Missing` claim removed from outreach language.
- [ ] "What we never sell" has at least 4 entries.
- [ ] Breadth positioning contains no unverifiable comparative claim.
- [ ] Zero prices other than `[PRICE TO CONFIRM]`; zero invented proof.
- [ ] Quality gates run and the result stated in one line to the seller.
- [ ] Seller told in one line which lane to hunt first and which proof gap to close first.
