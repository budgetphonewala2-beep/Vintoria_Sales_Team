# Negotiation, signature and delivery handoff

> Imported from the instruction-only Vintoria set and wired to the engine (pipeline, prospect folders, seller profile).

Turn a verbal yes into a signed, well-scoped contract and a delivery team that can start on day one.

## When to use / When not to use

**Use when**
- The buyer has seen a proposal and is choosing terms, timing or scope.
- The buyer said yes verbally but has not signed.
- Procurement, legal or security has entered the thread.
- The seller needs a mutual action plan, a counter-signature or a delivery handoff.
- A deal is lost and the seller wants a reason code and a re-entry date.

**Do not use when**
- No proposal exists. Run `vintoria-close` first; closing without scope invites invented terms.
- The buyer has not been qualified. Run `vintoria-close` first.
- The buyer only objects to price. Run `vintoria-close`, then return here.
- The task is drafting contract language. Agents summarise terms; the seller and their adviser write them.
- The request is a discount approval. Only the seller sets price. See `../vintoria-sales/references/pricing-policy.md`.

## Inputs needed (and what to do if missing)

| Input | Where it lives | If missing |
|---|---|---|
| Proposal with options | `CLIENT-PROPOSAL.md` | Stop. Write the proposal first. Do not negotiate air. |
| Discovery notes and qualification score | `MEETING-NOTES.md` | Ask the seller for the call notes; otherwise mark criteria `Not found` and ask the buyer directly. |
| Buyer's stated decision criteria | `MEETING-NOTES.md`, their replies in the pipeline (`python <SCRIPTS>/core/pipeline.py show`) | Ask one question: "What has to be true for you to sign?" Record verbatim. |
| Authority and signatory | `DOSSIER.md`, call notes | Ask the buyer in writing who signs and who pays. |
| Price and payment terms | `SELLER-PROFILE.json` (`python <SCRIPTS>/core/seller_profile.py show`) | Use `[PRICE TO CONFIRM]`. Never fill the gap. |
| Contract template or standard terms | Seller | Ask for the file. If none, list what must be agreed and mark `[TO CONFIRM: legal review]`. |
| Deal value and dates | Seller or `CLIENT-PROPOSAL.md` | Leave blank and name the gap in one line to the seller. |

Read `../vintoria-sales/references/truth-rules.md` before writing a single term. Terms you cannot source are not terms; they are questions.

## Workflow

1. **Confirm the stage.** Check the pipeline (`python <SCRIPTS>/core/pipeline.py`) says `proposal` or `negotiation`. If not, move the stage first and append the change to the pipeline history (`python <SCRIPTS>/core/pipeline.py note`). Do not close a row that still reads `discovery`.

2. **Score the proposal internally.** Apply the proposal rubric in `../vintoria-sales/references/quality-bar.md`. Below 80, fix the scope, exclusions, acceptance criteria and change-request path before any negotiation. A weak proposal negotiates into a weak contract.

3. **Capture decision criteria.** Write down what the buyer must see to sign, in their words, with the source and date. Minimum three criteria. For each, record the weight the buyer implied and whether VINTORIA can evidence it. If a criterion cannot be evidenced, say so early rather than at signature.

4. **Build the mutual action plan.** One table: step, owner, date, artefact, dependency. Include buyer-side steps (security review, legal read, budget release, PO) alongside ours. Every step needs a real date and a named owner. If the buyer will not commit to a date for their own step, that is the deal risk; name it.

5. **Set the concession ladder.** Prepare, in advance, three to five rungs you may offer. Every rung changes scope, phasing or start date only. No rung changes price. Order them cheapest to most costly for VINTORIA and log the trigger for each.

   | Rung | What changes | Example from the catalog | Trigger |
   |---|---|---|---|
   | 1 | Move an optional service to a later phase | 249 A/B Testing moves to phase 2 | Buyer wants a smaller first commitment |
   | 2 | Remove a named service and its deliverable | 090 Design Systems removed, 081 UI Design stays | Budget below the recommended option |
   | 3 | Narrow the market, locale or channel count | One locale instead of three | Scope must shrink without losing the core outcome |
   | 4 | Move the start date later | Start moves to the buyer's next budget cycle | Buyer has no approval this quarter |
   | 5 | Split into two contracts with a review gate | Phase 1 scope only | Buyer needs a proof point before the full programme |

   - Never offer a rung before the buyer states the constraint.
   - Never stack two rungs in one message.
   - Never propose a discount, a free extra, a payment holiday or a deferred invoice. If the buyer asks, say: "I can change what is included or when it starts. Price is the seller's call, not mine."
   - Write every rung into `CLOSE-PLAN.md` before the call, not during it.

6. **Prepare the procurement, legal and security question bank.** Answer from files, not memory. Mark gaps `Not found` and route them to the seller the same day. Typical groups:

   | Group | Questions to have answers for |
   |---|---|
   | Company | Legal entity name, registration, address, years trading, insurance, references allowed |
   | Commercial | Payment schedule, invoicing entity, currency, taxes, PO process, validity window |
   | Security | Data handled, hosting location, access model, subcontractors, incident contact, current attestations (only if the seller holds them) |
   | Legal | Standard terms, liability position, IP position, termination position, DPA availability |
   | Delivery | Named team roles, start capacity, cadence, escalation path, acceptance process |

   Say "confirm with the seller" wherever the answer is not written down. Do not improvise a legal or security claim.

7. **Complete the contract terms checklist.** Seven items, each marked `Confirmed`, `To confirm with seller` or `Not found`.

   | # | Term | What must be explicit |
   |---|---|---|
   | 1 | Scope | Every deliverable cites a catalog ID and name. Inclusions and exclusions are both listed. |
   | 2 | Payment schedule | Milestones tied to phases, deposit, invoice timing, currency, taxes, late-payment position. |
   | 3 | IP | What transfers, when it transfers, what stays licensed, third-party and open-source components. |
   | 4 | Confidentiality | Mutual, term, carve-outs, return or deletion on exit. |
   | 5 | Change requests | Written request, impact assessment, approval by both sides, no work before sign-off. |
   | 6 | Acceptance | Criteria per deliverable, review window, rework path, what counts as accepted. |
   | 7 | Termination and data protection | Notice period, payment for work done, handover of materials, controller and processor roles, sub-processors, retention, breach notice. |

   Do not paraphrase these into legal advice. State the position, cite the seller's file, and stop.

8. **Plan the signature and countersignature.** Follow this order and log each step in `CLOSE-PLAN.md`:
   1. Confirm the legal entity, signatory name, title and authority in writing.
   2. Confirm whether a PO, vendor form or portal is required, and who submits it.
   3. Send the final document with scope IDs, payment schedule and MAP dates attached.
   4. If the buyer signs first, countersign within one business day.
   5. Return the fully executed copy to the buyer and file it in the prospect folder.
   6. Update the pipeline (`python <SCRIPTS>/core/pipeline.py`) to `won`, set `next_action` to the handoff step, set `next_due`, set `updated`.
   7. Append the signature date, signatory and next stage to the pipeline history (`python <SCRIPTS>/core/pipeline.py note`).

9. **Handle silence after a yes.** A verbal yes is not a signature. Run this protocol and do not re-pitch:
   - Within 24 hours: written recap of what was agreed, the MAP, the scope IDs, and one question: "Shall I send the paperwork to you or to procurement?"
   - Business day 3: one nudge carrying a useful artefact, such as the draft statement of work or confirmed start dates.
   - Business day 5: contact the champion with a process question, not a pressure question.
   - Business day 10: ask directly whether the decision has changed, and offer to pause the deal.
   - Business day 14: re-qualify. Either the deal has a new date and owner, or it moves to `negotiation` with a later `next_due`, or it moves to `nurture`.
   - Never invent urgency, a price expiry the seller did not set, or a deadline that does not exist.

10. **Assemble the handoff package.** Delivery receives five things: files, decisions, access, risks, kickoff agenda.
    - Files: signed contract, final scope with catalog IDs, proposal option chosen, MAP, discovery notes, audit findings, brand or technical assets the buyer shared.
    - Decisions: a numbered list of what was agreed, what was excluded, and what was deferred to a later phase.
    - Access: accounts, environments, domains, store consoles, analytics, and who grants each one.
    - Risks: open dependencies, buyer-side responsibilities, assumptions, and the first thing likely to slip.
    - Kickoff agenda: attendees by role, 60 minutes, items with owners and outcomes.

11. **Run the loss debrief when the deal dies.** Record reason codes, evidence and a re-entry date of at least 90 days. Do not soften the reason for internal comfort.

    | Code | Meaning | Required evidence |
    |---|---|---|
    | `price-scope` | Price exceeded budget for the scope offered | Buyer's words plus the option they compared |
    | `no-budget` | No approved budget in the period | Buyer's statement or a dated email |
    | `no-authority` | Contact could not decide or sponsor | Named blocker and their role |
    | `incumbent` | Stayed with the current supplier | Named supplier and stated reason |
    | `competitor` | Chose another vendor | Named vendor if the buyer says it |
    | `timing` | Deferred to a later date | The date and the trigger event |
    | `no-decision` | Process stalled with no answer | Last contact date and silence length |
    | `fit` | Genuine mismatch with the catalog | The requirement no catalog service covers |
    | `compliance` | Legal, security or data block | The specific requirement that failed |
    | `unresponsive` | No reply after a full cadence | Touch dates and channels |

12. **Close the loop.** Update the pipeline (`python <SCRIPTS>/core/pipeline.py`) to `won` or `lost`, append the pipeline history (`python <SCRIPTS>/core/pipeline.py note`), move the row to `delivery`, `nurture` or `expand` as appropriate, and tell the seller the one next action with a date.

## Output format

Write `prospects/<slug>/CLOSE-PLAN.md` using exactly this shape, then update the pipeline history (`python <SCRIPTS>/core/pipeline.py note`) and the pipeline (`python <SCRIPTS>/core/pipeline.py`).

```md
# Close plan — <company>

Stage: <proposal | negotiation>   Owner: <name>   As of: <YYYY-MM-DD>
Chosen option: <A | B | C>   Value: <[PRICE TO CONFIRM] or seller figure>   Currency: <code>

## Decision criteria
| # | Criterion (buyer's words) | Source + date | Weight | Can we evidence it? |
|---|---|---|---|---|

## Mutual action plan
| # | Step | Owner | Date | Artefact | Dependency |
|---|---|---|---|---|---|

## Concession ladder (scope, phasing, start date only)
| Rung | Change | Catalog IDs affected | Trigger | Approved by seller? |
|---|---|---|---|---|

## Procurement, legal and security answers
| Group | Question | Answer | Source | Status |
|---|---|---|---|---|

## Contract terms checklist
| # | Term | Position | Status |
|---|---|---|---|

## Signature plan
- Legal entity:
- Signatory and title:
- Authority confirmed on:
- PO or vendor portal:
- Send date:
- Countersign date:
- Filed copy:

## Silence protocol
| Day | Action taken | Channel | Response |
|---|---|---|---|

## Handoff package
- Files:
- Decisions:
- Access:
- Risks:
- Kickoff agenda:

## Loss debrief (only if lost)
- Reason code:
- What the buyer said:
- What we verified:
- What we would change:
- Re-entry date:
```

## Quality gates

Do not show the plan until all of these pass.

- Decision criteria: at least 3, each with a source and date. Zero criteria sourced from memory.
- Mutual action plan: 100% of steps have an owner, a real date and an artefact. Any buyer-side step without a date is flagged as a risk.
- Concession ladder: at least 3 rungs, ordered by cost to VINTORIA, zero rungs that alter price, discount, payment terms or a guarantee.
- Question bank: all five groups answered or explicitly marked `Not found`, with the owner of the gap.
- Contract checklist: 7 of 7 items carry a status. Items 1 and 6 must be `Confirmed` before signature is requested.
- Price integrity: 100% of figures trace to `SELLER-PROFILE.json`. Any unverified figure is `[PRICE TO CONFIRM]`, and no figure is ever derived from a market average.
- Stage truth: the pipeline (`python <SCRIPTS>/core/pipeline.py`) stage matches the evidence in the pipeline history (`python <SCRIPTS>/core/pipeline.py note`). No row is marked `won` without an executed copy.
- Handoff: all five sections present, kickoff agenda has at least five items with owners.
- Reading level: no sentence over 28 words in buyer-facing text, no em dash, no exclamation mark.

## Failure handling

| Situation | Action |
|---|---|
| Seller profile or pricing missing | Use placeholders, print one line naming the gap, continue. Never block a live negotiation on a profile. |
| No web access while verifying the buyer's company | Work from saved `DOSSIER.md` and `SITE-AUDIT.md`, mark new questions `Not found`, and list them for the seller. |
| Buyer sends a contract with unfamiliar terms | Summarise each clause in plain language, mark the ones needing review, and say "confirm with the seller and their adviser". Do not accept or reject on the seller's behalf. |
| Buyer asks for a discount | Offer a ladder rung that changes scope or phasing. State that price is the seller's decision. Log the request in `CLOSE-PLAN.md`. |
| Silence after a yes | Run the day 3, 5, 10, 14 protocol exactly. Do not add touches outside it. |
| Two documents disagree on scope | Prefer the document the buyer signed most recently, show both, and ask the seller to confirm before signature. |
| Request is ambiguous | Ask one question: "Is this deal at proposal, negotiation or already agreed?" Then proceed from that stage. |

## Definition of done

- [ ] `CLOSE-PLAN.md` exists and every section is filled or marked `Not found`.
- [ ] Decision criteria captured verbatim with sources.
- [ ] Mutual action plan has dated, owned steps on both sides.
- [ ] Concession ladder prepared, price untouched, seller-approved rungs only.
- [ ] Procurement, legal and security answers routed or marked open.
- [ ] Contract checklist complete, items 1 and 6 confirmed.
- [ ] Signature path clear with entity, signatory, authority and countersign order.
- [ ] Silence protocol scheduled with dates.
- [ ] Handoff package complete, kickoff agenda ready.
- [ ] the pipeline (`python <SCRIPTS>/core/pipeline.py`) and the pipeline history (`python <SCRIPTS>/core/pipeline.py note`) updated, stage truthful, one next action with a date.
