---
name: vintoria-setup
description: "Sets Vintoria up before any prospecting: interviews the user and writes SELLER-PROFILE.md (sender identity, postal address, time zone, active disciplines from the 270-service catalog, niches, target markets in India, US, UK and Australia, prices per market, real case studies, differentiators, buyer pains and triggers), then OFFER.md (3-5 offer lanes mapped to exact catalog service IDs, active vs dormant disciplines, a claim-by-claim proof map) and IDEAL-CUSTOMER-PROFILE.md (firmographics, buying signals, personas, scoring rubric and the exact LinkedIn search queries for agency-seekers). Every query, email and proposal in the other Vintoria skills is built from these files. Use it at the start, whenever SELLER-PROFILE.md is missing or incomplete, or when the user says 'set up', 'onboard me', 'build my ICP', 'which services should we push', 'who should we target', 'change our niche', or Hinglish 'setup karo', 'mera ideal client kaun hai', 'humein kya bechna chahiye', 'profile banao'."
license: MIT
compatibility: "Instruction-only Agent Skill for Hermes Agent (Nous Research) on three PCs, agentskills.io format; needs the browser logged in to LinkedIn, Airtable, and the brand inbox for that PC."
metadata:
  author: "Vintoria (built on ai-sales-team-claude by Zubair Trabzada)"
  version: "7.0.0"
---

# Vintoria Setup — profile, offer lanes and ideal customer

Generic queries find generic leads and generic emails get ignored. You learn Vintoria's business properly once, write
it down, and all three PCs build on the same facts.

The catalog is `../vintoria-sales/references/service-catalog.md`; prices follow
`../vintoria-sales/references/pricing-policy.md`; never write a fact the user didn't give you.

## Steps

1. **What exists.** `SELLER-PROFILE.md` present and without `[ASK]`? Show a 5-line summary and ask only what changed.
   Missing? Start from `references/seller-profile-template.md` — it already holds what the catalog says (the services,
   India + US/UK/AU, English + Hindi, buyer titles); everything else is `[ASK]`.
2. **Interview** with `references/intake.md` in at most **3 short rounds**, grouped, each question with an example
   answer — never 25 questions at once:
   - Round 1 — Vintoria: website, sender name, postal address, time zone (the email `business@vintoria.org` and
     WhatsApp +91 87660 33979 are already in the template); which of the 12 disciplines are
     **active** this month (staffed, with proof) vs dormant; the offer in one line; niches.
   - Round 2 — the buyer: countries and cities (India / US / UK / AU), buyer titles, company size, deal size and
     currency per market (INR in India, USD / GBP / AUD abroad), pains right before they hire, triggers, tools they leave.
   - Round 3 — proof: 2-3 real results per active discipline (client, result, link), portfolio, years / projects / team,
     why Vintoria over freelancers and big agencies, any real guarantee, booking link.
   Accept "skip" for optional fields. Never fill an answer the user didn't give — case studies and prices especially.
3. **Read Vintoria's own website** (if given) to pre-fill and confirm — not to invent. Write `SELLER-PROFILE.md`.
4. **Offer lanes** → `OFFER.md` (`references/offer-lanes.md`): 2-8 active disciplines, 3-5 lanes (one buyer problem
   each, an entry service + 1-4 follow-on services by exact catalog ID), 2 observable disqualifiers per lane, a proof map
   (`Have` / `Partial` / `Missing` — outreach may only use `Have`), and positioning against freelancers and large
   agencies that contains only checkable claims.
5. **Ideal customer** → `IDEAL-CUSTOMER-PROFILE.md` (`references/icp-playbook.md`, `references/icp-output-format.md`):
   firmographics per market, the phrases buyers really post (English and Hinglish — "need a website for my clinic",
   "website banwana hai", "koi SEO wala batao"), pains, budget qualifiers, negative ICP, a 0-100 rubric, 2-3 personas,
   and **10-20 ready search queries** built with the formula in `../vintoria-lead-hunt/references/queries.md` —
   LinkedIn boolean queries for people looking for an agency (posts, comments, groups).
6. **Show the queries** and ask whether the results look like Vintoria's buyers; adjust niches and pains until they do.
   Next: `vintoria-lead-hunt`. Create an empty `PIPELINE.md` and `DO-NOT-CONTACT.md` if they don't exist.

## Rules
- `SELLER-PROFILE.md` is the single source of truth for who Vintoria is; emails may cite only proof that is in it.
- `OFFER.md` never holds prices — prices live in the profile, or are `[PRICE TO CONFIRM]`.
- No passwords or API keys in any file.
- Re-run whenever the offer, the active disciplines or the target markets change.

## References (read when you reach that step)

- `references/seller-profile-template.md` — the SELLER-PROFILE.md template, pre-filled with the catalog facts
- `references/intake.md` — every interview question, why it matters, good vs weak answers
- `references/offer-lanes.md` — active/dormant disciplines, 3-5 offer lanes by catalog ID, the proof map, positioning
- `references/icp-playbook.md` — the ICP steps and the scoring rubric
- `references/icp-output-format.md` — IDEAL-CUSTOMER-PROFILE.md template
- `references/rules.md` — quality rules for the ICP
