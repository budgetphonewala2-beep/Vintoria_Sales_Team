---
name: vintoria-outreach
description: "Writes a scored, approval-ready cold outreach sequence for one VINTORIA prospect and saves it to workspace/prospects/<slug>/OUTREACH.md, using a five-touch email cadence plus LinkedIn and WhatsApp variants, 1-3 exact services from the 270 VINTORIA services, and a quality-bar floor of 80 before the seller sees it. Use when the user says 'write a cold email', 'outreach for this lead', 'email sequence for this company', 'LinkedIn message for them', 'first touch for this prospect', 'email likho iske liye', 'cold mail banao', or 'follow-up sequence draft karo'."
---

# VINTORIA Outreach

Write one prospect's full cold sequence, scored and waiting for the seller's approval, never sent by an agent.

## When to use / When not to use

Use when:
- A prospect has a `SITE-AUDIT.md` or `DOSSIER.md` with at least one verified hook and a named contact.
- The seller wants first contact by email, LinkedIn or WhatsApp click-to-chat.
- A sequence needs rewriting because it scored below 80 or the hook changed.

Do not use when:
- There is no verified hook. Run `vintoria-audit` or `vintoria-research` first.
- The prospect already replied. Use `vintoria-reply`.
- The sequence is mid-flight and needs the next touch. Use `vintoria-followup`.
- The seller wants a bulk blast, a purchased list or automated social DMs. Refuse and cite `../vintoria/references/compliance.md`.

## Inputs needed (and what to do if missing)

| Input | Use | If missing |
|---|---|---|
| `slug`, company, domain | folder and identity | Ask; never guess |
| Contact name, title, email | recipient and personalisation | Use a role address only if published; otherwise stop |
| `email_status` | risk handling | Default `unverified` and say so |
| `SITE-AUDIT.md` top hooks | the observation | Build a hook from `DOSSIER.md`; still verify it on the page |
| Country and market | compliance regime | `Not found`; ask before sending |
| `SELLER-PROFILE.md` | proof, sender identity, postal address | Omit proof, use `[ADD REAL CUSTOMER RESULT]`, tell the seller to run `vintoria-offer` |

Read first: `../vintoria/references/truth-rules.md`, `../vintoria/references/quality-bar.md`, `../vintoria/references/compliance.md`, `../vintoria/references/pricing-policy.md`, `../vintoria/references/pipeline-format.md`, and the discipline files for the chosen services.

## Workflow

1. Read the dossier, audit and pipeline row. Confirm `slug`, contact, `email_status`, country, owner.
2. Run the suppression check on the exact email, the domain and any phone. One hit anywhere means stop, log it, do not draft.
3. Confirm the contact basis and source URL. A contact with no public source is not contactable.
4. Choose 1-3 services that the top hook actually supports. Exact IDs and names only.
5. Choose one hook. It must be reproducible from one URL in under ten seconds.
6. Choose the channel: email by default; LinkedIn only if the profile is public and business-facing; WhatsApp only if a public business number offers click-to-chat.
7. Draft all five touches from scratch. No touch is a reword of another.
8. Apply the subject rules to touch 1 only. Touches 2-5 reply in the same thread, no new subject.
9. Score every email with `quality-bar.md` section 1. Floor 80. Below 80, rewrite the weak part and rescore.
10. Run the deletion test, the truth check and the compliance check on every touch.
11. Present the sequence with score, approval status `pending`, recipient, channel and proposed send date.
12. After written approval, record `approved by <seller> on <date>` in `OUTREACH.md`. The agent never sends.

Decision rules:
- Two hooks from one discipline: use the higher severity one and keep the other for follow-up.
- Hook cannot be verified on a second fetch: drop it, do not soften it.
- No named contact but a published role address: one touch only, ask for the right person, do not run five.
- Prospect under 50 staff with no dedicated marketing or product role: prefer the founder, one service, shorter sequence.
- Regulated industry (health, finance, legal, children): stop and ask the seller before drafting.

## The five touches

| Day | Purpose | What must be new | Words |
|---|---|---|---|
| 0 | Earn a reply with one verified observation about them | The observation and its consequence | 50-120 |
| 3 | Add a second fact they can check | A different finding or page from the audit | 25-90 |
| 7 | Be useful with no meeting | A specific explanation or a one-page teardown offer, no attachment | 25-90 |
| 14 | Name the service and the smallest first step | Service name plus a scoped first step in one sentence | 25-90 |
| 28 | Breakup: close the loop, leave the door open | An explicit close and permission to return | 60 or fewer |

Rules for every touch:
- One question maximum. One idea maximum.
- At least two sentences about them for every one about VINTORIA.
- No link in touch 1. No calendar link until they reply with interest.
- No attachment in any cold touch.
- Identify the sender and keep the opt-out line in every email, in plain text.
- Plain text only: no bold, no HTML, no images, no tracking pixel.
- No sentence longer than 28 words.

## Subject lines

Rules: 2-5 words, lowercase, no colon, no question mark, no exclamation, no emoji, no fake `Re:` or `Fwd:`, nothing that could be factually wrong, no "quick question".

| Pattern | Example shape |
|---|---|
| The problem noun | `mobile checkout steps` |
| The page name | `your pricing page` |
| The measured fact | `eleven h1 tags` |
| The task framing | `shopify migration check` |
| Context without a date | `before your launch` |

## First line formula

Observation, then relevance, then question. Fill the slots, do not paraphrase the pattern.

`Your <page or flow> <measured fact from the audit>. That <hedged consequence for them>. <One question about their intent or constraint>?`

- Observation must contain a detail only this company has: a page name, a count, a quoted label.
- Relevance is one clause, hedged, never a statistic.
- Question is answerable in one line by someone busy.

## Deletion test (hard gate)

Remove the company name and every personal noun. If the email still makes sense for any company in the same industry, the situation score is capped at 10 and the email cannot go out. Rewrite with a detail that only this prospect has.

## Service naming

- One to three services, exact ID and name, from `../vintoria/references/service-catalog.md`.
- Name the service only when the hook supports it.
- Never dump a discipline, a package or a list of ten.
- Never rename a service or invent one outside the 270.
- Outside the catalog: say so plainly and name the closest covered services.

## CTA ladder

| Stage | Ask |
|---|---|
| Touch 1 | One low-effort question about their situation. No meeting, no call, no link. |
| Touches 2-3 | Permission to send one specific finding, or a yes/no question. |
| Touch 4 | The smallest first step, stated as a question: "worth a 15 minute look?" |
| After interest only | Propose two time windows as questions, marked `[CONFIRM WITH SELLER]`. |

## Proof rules

- Proof comes only from `workspace/profile/SELLER-PROFILE.md`, verbatim.
- No client name, logo, metric, award, team size or delivery date unless it is written there.
- Missing proof: write `[ADD REAL CUSTOMER RESULT]` visibly and do not send that line until the seller fills it.
- No "we have helped companies like yours" without a named, verified example in the profile.
- No guarantee, no outcome claim, no timeline.

## Four things never to include

1. Any price, range, discount, day rate or budget hint. Use `[PRICE TO CONFIRM]` and never in a cold touch.
2. Any timeline, delivery date, deadline or urgency that is not the buyer's own.
3. Any invented proof: client, metric, case study, award, team size, partner.
4. Any second question, link, attachment, calendar or tracking element before they show interest.

## Channel variants

| Channel | Rules |
|---|---|
| Email | The five touches above. Full text, opt-out, sender identity, postal address where the market requires it. |
| LinkedIn connection note | 200-300 characters. One reason for connecting, one specific observation, no pitch, no link, no "I'd love to". |
| LinkedIn message (after connection) | 3-5 sentences, one observation, one question, no link, no attachment, no price. Manual send only. |
| WhatsApp click-to-chat | Public business number only. First line says who you are and why. One observation, one question. No files, no voice notes, no forwarding. |

Never automate LinkedIn or WhatsApp. Never message a personal number. Never send the same text on two channels on the same day.

## Suppression, approval and scoring

- Suppression check before every touch: email, domain, phone, person. Check `workspace/pipeline/suppressions.md` and `REPLIES.md` for a stop.
- Approval gate: the seller approves the exact text, the exact recipient, the channel and the send date in writing. Record it. Approval on one touch is not approval of the sequence.
- Score: use `quality-bar.md` section 1 for every email. Show the score and the one-line fix. Floor 80; below it, do not show the draft.

## Email status handling

| Status | Action |
|---|---|
| `verified` | Draft normally; still requires approval |
| `catch_all` | Draft, note bounce risk, expect no delivery confirmation |
| `unverified` | Prefer another channel; if emailing, one address, no attachment, state the uncertainty to the seller |
| `pattern-guessed` | Label it in the file, never present it as verified, send no more than one touch until a reply or bounce confirms it |
| `invalid` | Do not send. Find another contact or another channel. |

## Stop conditions

Stop the sequence on: any human reply, any opt-out, a hard bounce, wrong person, suppression hit, or completion of touch 5. Out of office pauses the sequence, it does not end it. A reply of any kind gets handed to `vintoria-reply` before anything else.

## Output format

Write to `workspace/prospects/<slug>/OUTREACH.md`:

```markdown
# Outreach: <company>

Contact: <name>, <title> | Email: <email> (<status>) | Country: <country>
Channel: <email | LinkedIn | WhatsApp> | Basis: <public source URL> | Suppression: clear on <date>
Services: <ID Name>, <ID Name> | Hook: HOOK <n> | Owner: <seller>

## Compliance block
Sender: <name, VINTORIA, reply address> | Opt-out line: <text> | Postal address: <if required> | Regime: <market>

## Sequence

### Touch 1 - Day 0 - first touch
Subject: <2-5 words>
Body:
<text>
Words: <n>/120 | Score: <n>/100 (<premium | ship>) | Approval: pending | Sent: not sent

### Touch 2 - Day 3 - <purpose>
Body:
<text>
Words: <n>/90 | Score: <n>/100 | Approval: pending | Sent: not sent

### Touch 3 - Day 7 - <purpose>
### Touch 4 - Day 14 - <purpose>
### Touch 5 - Day 28 - breakup
Words: <n>/60 | Score: <n>/100 | Approval: pending | Sent: not sent

## Scorecard
| Touch | Day | Words | Score | Verdict | Approval |
|---|---|---|---|---|---|

## Stop log
| Date | Event | Action | By |
|---|---|---|---|
```

## Quality gates (before showing anything)

| Gate | Floor |
|---|---|
| Quality-bar score, every email | 80 or above |
| Deletion test | passed on touch 1 |
| Services named | 1-3, exact ID and name, each supported by the hook |
| Price, timeline, guarantee, invented proof | 0 instances |
| Questions per touch | 1 |
| Opt-out present in every email | yes |
| Suppression checked | yes, dated |
| Approval status shown per touch | yes |
| Bulk, automation or purchased-list signals | 0 |

## Failure handling

- **No web access.** Build the sequence only from saved audit and dossier evidence. If no hook is verified, stop and write `evidence unavailable, not drafted`.
- **Missing profile.** No proof lines, no postal address, one line to the seller: run `vintoria-offer`.
- **Ambiguous request** ("write something for this company"). Ask for the channel, the contact and the goal. With no answer, default to a five-touch email sequence to the named decision maker.
- **Suspected suppression.** Treat as suppressed. Ask the seller to confirm before anything else.
- **Seller asks to skip scoring, add a price, or add a fake client.** Refuse in one line, state which rule, offer the compliant alternative.

## Definition of done

- [ ] Five touches drafted, each with a different new element.
- [ ] Every email scored 80 or above and marked `pending`.
- [ ] Exact recipient, channel, basis and send dates listed.
- [ ] Suppression check dated and clear.
- [ ] Opt-out and sender identity in every email.
- [ ] `pipeline.csv` set to `contacted` only after the seller confirms a send, with `next_due`.
- [ ] `HISTORY.md` appended; nothing marked sent by the agent.

## Example (illustrative) - e-commerce

Company `harborline.example`, fictional outdoor gear store, contact `Maya Rao`, Head of E-commerce. Services: 200 Checkout Development, 201 Checkout Optimization. Hook: guest checkout absent. Score 88, verdict `premium`.

Touch 1, day 0, subject `mobile checkout steps`:

> Your Ridge Pack page loads cleanly on desktop, but at 390 pixels the buy button sits below the fold, and checkout then asks for an account before payment. That second step is where some phone buyers may leave. 200 Checkout Development and 201 Checkout Optimization cover exactly that flow. Is the account requirement deliberate, or a platform default you have wanted to remove?

Words 67. Passes the deletion test because of the named product, the width and the account step. No price, no link, one question.

## Example (illustrative) - AI

Company `fieldnote.example`, fictional field-service software, contact `Tom Achterberg`, VP Customer Experience. Services: 125 AI Knowledge Bases, 124 AI Customer Support Systems. Hook: help centre has 34 articles with no search. Score 84, verdict `ship`.

Touch 1, day 0, subject `support article gaps`:

> Your help centre lists 34 articles and has no search field. I ran five ordinary customer questions through it, including refund timing and changing a plan, and none returned a matching article from the public page. A retrieval layer over your own articles is what 125 AI Knowledge Bases and 124 AI Customer Support Systems build. Which three questions do your agents answer by hand most often?

Words 63. The count and the missing search are checkable. The consequence is implied by the questions, not asserted as a statistic.
