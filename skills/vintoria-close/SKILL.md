---
name: vintoria-close
description: "Takes a Vintoria deal from booked call to signed contract and beyond: builds the meeting brief (their original request, audit facts, the thread, qualification so far), runs and scores the discovery call (timed agenda, 0-100 scorecard, go/no-go bands, question banks, red-flag tests), writes the proposal from the buyer's own words with scope by exact Vintoria catalog service IDs, three scope options and prices only from the profile, prepares word-for-word objection answers (price, timing, current vendor, offshore worries), runs negotiation where concessions change scope not price, drives signature and the delivery handoff, and plans upsells and referral asks. Use it for 'prep me for my call', 'discovery call questions', 'write a proposal', 'quotation for this client', 'client says it's too expensive', 'they said yes, now what', 'negotiate', 'handoff to delivery', 'upsell this client', or Hinglish 'meeting ki taiyari karo', 'proposal banao', 'client bol raha hai mehenga hai', 'deal close kar do'."
license: MIT
compatibility: "Instruction-only Agent Skill: no code. Works in any agent or bot (Claude, Grok, GPT, Gemini…) that can follow instructions; best with a browser logged in to LinkedIn and Reddit, and file access."
metadata:
  author: "Vintoria (built on ai-sales-team-claude by Zubair Trabzada)"
  version: "7.0.0"
---

# Vintoria Close — prep, discovery, proposal, objections, signature, expansion

Calls are won before they start and deals are lost in the details after them. You prepare, qualify honestly, propose
scope the buyer recognises as their own, and close without ever inventing a price, a date or a result.

## Before you start

1. **Your files.** Everything lives in plain files — `SELLER-PROFILE.md`, `OFFER.md`, `IDEAL-CUSTOMER-PROFILE.md`,
   `PIPELINE.md`, `DO-NOT-CONTACT.md` and `prospects/<slug>/` (format: `../vintoria-sales/references/pipeline-format.md`). If you can't read or
   write files (a chat bot such as Grok), ask the user to paste `SELLER-PROFILE.md` and the relevant `PIPELINE.md` rows,
   and finish by printing every changed row and file in code blocks for them to save. Mirror every change to the
   connected Google Sheet (`../vintoria-sales/references/sheet-sync.md`) — update by key, never duplicate, never delete.
2. **Vintoria's profile.** Read `SELLER-PROFILE.md`. This skill builds queries, emails or prices from it — if it is
   missing or still full of `[ASK]`, run `vintoria-setup` first (in a hurry: ask only the missing answers in one message).
3. **What Vintoria sells.** 270 services in 12 disciplines — `../vintoria-sales/references/service-catalog.md`. Name a service exactly as the
   catalog does (`192 Shopify Development`), never invent one, and never quote a price, discount or date that isn't in
   `SELLER-PROFILE.md` — write `[PRICE TO CONFIRM]` (`../vintoria-sales/references/pricing-policy.md`).
4. **Platforms.** Leads come only from **LinkedIn and Reddit**, through the accounts already logged in on this machine.
   Open a page before you state a fact from it and note its URL and date; a search snippet alone is not a fact. If you
   can't open something, write "Not found".
5. **Facts only.** Every sentence traces to a page you opened, the prospect's own words, a fact you observed on their site,
   the catalog or the profile — never to memory. Never say something was sent, posted, booked or verified unless it
   really happened. Run the self-check in `../vintoria-sales/references/truth-rules.md` before anything goes out.
6. **Contact details** — Vintoria: `business@vintoria.org`, WhatsApp +91 87660 33979 (`https://wa.me/918766033979`);
   Radian Marketing: `amar@radianmarketing.site` — and every sign-off come only from `../vintoria-sales/references/vintoria-contact.md`. Each
   brand's emails carry that brand's real identity (`../vintoria-sales/references/brands.md`).
7. **The team.** Read `TEAM-BOARD.md` before you start and handle messages to your role; `CLAIM` a lead before working it,
   hand off with full context, post `ALERT`s at once (`../vintoria-sales/references/team.md`). Alone, you play every role with the same files.

## Pick the stage

| Stage | When | Output in `prospects/<slug>/` |
|---|---|---|
| **Prep** | a call is booked | `MEETING-PREP.md` |
| **Discovery** | the call is happening / just happened | `MEETING-NOTES.md` + qualification score |
| **Proposal** | discovery scored A (80+), or they asked for one | `CLIENT-PROPOSAL.md` |
| **Objections** | an objection came up (any stage) | the answer, or `OBJECTION-PLAYBOOK.md` |
| **Negotiate & sign** | they've seen the proposal / said yes verbally | `CLOSE-PLAN.md`, handoff checklist |
| **Expand** | won and delivering | `EXPANSION-MAP.md`, referral and review asks |

## Prep
1. Read everything known: the `PIPELINE.md` row, `DOSSIER.md`, `SITE-AUDIT.md`, research, contacts, `OUTREACH-SEQUENCE.md`,
   `THREAD.md`, `HISTORY.md`. No dossier → `vintoria-prospect-research` first.
2. Build the brief (`references/prep-playbook.md`, `references/prep-output-format.md`, `references/template-meeting-prep.md`):
   a one-page cheat sheet; their request in their own words; the audit facts; the conversation so far; qualification
   status (budget, timeline, decision maker, scope — unknowns marked); 1-3 catalog services that fit, with the signal
   beside each; talking points; 10 discovery questions aimed at the unknowns; objections; landmines; and the exact ask for
   the close ("Shall I send a written scope with 3 options by Friday?").
3. A **3-minute screen-share plan**: their site on a phone view, the top 2 audit facts, one competitor doing it better —
   then ask, don't pitch. Self-check the brief: talking points built on an invented fact are worse than none.

## Discovery
Run the call with `references/discovery-call.md`: 30- or 45-minute agenda, one question at a time (core bank first, then
the discipline bank — AI, automation, web/SaaS, e-commerce, SEO/growth), verbatim quotes, red-flag tests. Score after the
call: problem 20, impact 15, authority 20, timeline 15, budget signal 10, service fit 10, risk 10.
**A 80-100** proposal · **B 65-79** paid discovery or a bounded pilot · **C 50-64** nurture with a trigger · **D < 50**
disqualify politely. Hard no-go whatever the score: no route to the economic buyer within 30 days, a need outside the 270
services, regulated data with no compliance owner, a free build or guaranteed result demanded. Write `MEETING-NOTES.md`
within 2 hours and update the `PIPELINE.md` row (score, stage, next action + date).

## Proposal
1. **Inputs** (`references/proposal-playbook.md`): the buyer's needs in their words (post, replies, `MEETING-NOTES.md`),
   and — from `SELLER-PROFILE.md` only — prices, timelines, process, team, case studies. Missing → `[PRICE TO CONFIRM]` /
   `[TO CONFIRM]`; never a guess, never "agencies usually charge".
2. **Write** with `references/template-proposal-template.md` and `references/proposal-output-format.md`: their problem with
   evidence; scope where every line cites a catalog service ID + name with inclusions and **exclusions**; three options
   (core / recommended / expanded) that differ in scope, never in discount; phases with dependencies and acceptance
   criteria (working days, or `[TO CONFIRM]`); assumptions, buyer responsibilities, a change-request path; payment terms,
   validity (14 days) and acceptance ("reply 'approved Option B'"). Prices in their currency (INR, USD, GBP, AUD) only from
   the profile. Tax on exported services is for the accountant — don't state it.
3. Score it against the proposal bar in `../vintoria-sales/references/quality-bar.md` (floor 80) and self-check it.
4. When the user sends it: row → `proposal`, `value` = the recommended option's real price (if any), `next_action`
   "Walkthrough offer" in 2 days; the post-proposal follow-ups are in `vintoria-outreach`.

## Objections
Exact words for calls, emails and chat (`references/objections-playbook.md`, `references/objections-output-format.md`,
`references/template-objection-playbook.md`): the frameworks, 15 universal objections, industry and competitor objections,
prevention. Price objections change scope or phasing, never the price (`../vintoria-sales/references/pricing-policy.md`).
Overseas buyers: time zones (overlap hours, response time), communication and quality (a named owner, weekly calls),
"burned by an offshore team" (milestone payments, code ownership, references), IP and contracts, how to pay. Indian SMBs:
"a freelancer will do it cheaper", "my nephew can build it", "we tried an agency before", "guarantee page 1?" (never promise
rankings). Proof points must be real — otherwise `[ADD REAL CUSTOMER RESULT]`.

## Negotiate & sign
`references/negotiation-and-handoff.md`: capture their decision criteria, a mutual action plan with dates both sides own,
concessions that change only scope, phasing or start date, procurement / legal / security answers, contract terms checked
against the catalog IDs in scope, rescuing a buyer who goes quiet after a yes, and the delivery handoff checklist. Signed →
`won`; lost → `lost` with the reason in `HISTORY.md` (it feeds the weekly review).

## Expand
After the win, `references/expand-and-referrals.md`: the natural follow-on services from the offer lane (a website →
`212 Search Engine Optimization` or `214 Local SEO`, then a service from discipline 08 Business Automation), when to raise
the upsell, and the review and referral asks — only after the client got a real result. Edge cases: `references/rules.md`.

## Proof bank — after every launch
Schedule the asks in `PIPELINE.md` (`references/proof-bank.md`): launch-day reaction, a testimonial and naming permission
at +7 days, the client's own result and a Google review at +30, a referral at +45. Write each into `PROOF-BANK.md` with
exactly what the client allowed. Every other skill uses it as real proof — closest niche first.

## Before anything is sent

- **Self-check** every message with `../vintoria-sales/references/truth-rules.md`; delete or rewrite every unsourced sentence and fill or flag
  every `[PLACEHOLDER]`.
- **Critic check** — the yes/no list in `../vintoria-sales/references/critic-check.md`, as a strict reviewer (another bot's `REVIEW` in a team).
  One "no" = fix it; two failed rewrites = skip the lead.
- **Score** it with `../vintoria-sales/references/quality-bar.md` (emails: 80 to show, 85+ premium) and say the score in one line.
- **Compliance:** `../vintoria-sales/references/compliance.md` — opt-out line, postal address for US, consent rules (UK/EU/CA/AU/NZ/India),
  and check `DO-NOT-CONTACT.md` first.
- **Language:** plain English — US spelling for US/CA, UK spelling for UK/IE/AU/NZ, clear Indian English for India (no
  "do the needful", "revert", "kindly"). If an Indian prospect wrote in Hindi or Hinglish, answer in the same register,
  still short and professional. Prices only in their currency and only from the profile.
- **Approval mode** (`SELLER-PROFILE.md` → Automation): `auto` — you post or send it yourself from the logged-in
  Reddit / LinkedIn account or `business@vintoria.org`, but only after it passes the self-check, scores 85+, fits that
  platform's rules (`../vintoria-sales/references/compliance.md`) and today's limits; `review` — show the exact text and wait for the user's OK.
  A message that fails any check is never sent in either mode — fix it or skip the lead. Count every post / send in
  `RUN-LOG.md` first; at the hourly limit (all bots together), queue it for the next hour.
- **Log every message that went out** — `THREAD.md` (exact text, link to it), `HISTORY.md`, `PIPELINE.md` — and give the
  user a summary of what was posted and sent.
- **No booking link** in a first message — only after they show interest.

## References (read when you reach that step)

- `references/prep-playbook.md` — research steps, the brief sections, agendas
- `references/prep-output-format.md` — MEETING-PREP.md format
- `references/template-meeting-prep.md` — meeting brief template
- `references/discovery-call.md` — discovery call: brief, agenda, scorecard, question banks, red flags, scripts
- `references/proposal-playbook.md` — inputs, sections, follow-up sequence
- `references/proposal-output-format.md` — CLIENT-PROPOSAL.md format
- `references/template-proposal-template.md` — proposal template
- `references/objections-playbook.md` — frameworks, 15 objections, industry/competitive/pricing, prevention
- `references/objections-output-format.md` — OBJECTION-PLAYBOOK.md format
- `references/template-objection-playbook.md` — objection playbook template
- `references/negotiation-and-handoff.md` — decision criteria, mutual action plan, concessions, legal/security, signature, handoff, loss debrief
- `references/expand-and-referrals.md` — upsell map, retention, review and referral asks
- `references/proof-bank.md` — when and how to ask for results, testimonials, reviews, referrals; PROOF-BANK.md format; rules for using proof
- `references/rules.md` — terminal output, errors, cross-skill use
