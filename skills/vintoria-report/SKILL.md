---
name: vintoria-report
description: "Produces Vintoria's pipeline report from PIPELINE.md and the prospects/ folders: funnel by stage, reply / meeting / win rates, deal value per currency, stale deals, actions due, which sources, queries, hooks, subjects, catalog services and markets (India vs US/UK/AU) produce replies and calls, and a prioritised action plan for today, this week and this month — written to SALES-REPORT.md, ready to export as a PDF. Use it for 'pipeline report', 'how is my pipeline', 'weekly sales review', 'which leads are working', 'how much revenue is in the pipeline', 'report for my team', or Hinglish 'pipeline ka report do', 'kitne leads hain', 'is hafte ka review'. For today's to-do list use vintoria-sales instead."
license: MIT
compatibility: "Instruction-only Agent Skill: no code. Works in any agent or bot (Claude, Grok, GPT, Gemini…) that can follow instructions; best with a browser logged in to LinkedIn and Reddit, and file access."
metadata:
  author: "Vintoria (built on ai-sales-team-claude by Zubair Trabzada)"
  version: "5.0.0"
---

# Vintoria Report — pipeline, what works, next week

You turn the pipeline into decisions: what to do this week, what to keep doing, and what to stop.

## Before you start

1. **Your files.** Everything lives in plain files — `SELLER-PROFILE.md`, `OFFER.md`, `IDEAL-CUSTOMER-PROFILE.md`,
   `PIPELINE.md`, `DO-NOT-CONTACT.md` and `prospects/<slug>/` (format: `../vintoria-sales/references/pipeline-format.md`). If you can't read or
   write files (a chat bot such as Grok), ask the user to paste `SELLER-PROFILE.md` and the relevant `PIPELINE.md` rows,
   and finish by printing every changed row and file in code blocks for them to save.
2. **Vintoria's profile.** Read `SELLER-PROFILE.md` if it exists. If not, carry on with what the user told you and
   suggest `vintoria-setup` at the end — never block urgent work on it.
3. **What Vintoria sells.** 270 services in 12 disciplines — `../vintoria-sales/references/service-catalog.md`. Name a service exactly as the
   catalog does (`192 Shopify Development`), never invent one, and never quote a price, discount or date that isn't in
   `SELLER-PROFILE.md` — write `[PRICE TO CONFIRM]` (`../vintoria-sales/references/pricing-policy.md`).
4. **Platforms.** Leads come only from **LinkedIn and Reddit**, through the accounts already logged in on this machine.
   Open a page before you state a fact from it and note its URL and date; a search snippet alone is not a fact. If you
   can't open something, write "Not found".
5. **Facts only.** Every sentence traces to a page you opened, the prospect's own words, a fact you observed on their site,
   the catalog or the profile — never to memory. Never say something was sent, posted, booked or verified unless it
   really happened. Run the self-check in `../vintoria-sales/references/truth-rules.md` before anything goes out.
6. **Vintoria's contact details** — `business@vintoria.org`, WhatsApp +91 87660 33979 (`https://wa.me/918766033979`) —
   and every sign-off come only from `../vintoria-sales/references/vintoria-contact.md`.

## Steps

1. **Count, don't estimate** (`../vintoria-sales/references/pipeline-format.md`, "Metrics"): rows by stage, source, country
   and discipline; rows that reached `contacted`, `replied`, `meeting`, `proposal`, `won`; reply, positive-reply, meeting
   and win rates; open and won `value` per currency; stale rows (14+ days); rows due today or overdue.
2. **Complete it:** prospect folders in `prospects/` without a `PIPELINE.md` row — read their files and add the row.
3. **What works** (`references/report-playbook.md`): which sources and queries (`source`), first-email hooks, subject
   lines (A vs B), offer lanes and catalog services, and markets get replies and calls; which sequence step gets the
   reply; gaps (no usable emails, sequences not sent, replies waiting). Meetings and proposals without a `value` are a gap
   to fix with a real price.
4. **Decide:** keep and double what booked calls; drop sources and queries with no positive reply after a fair test;
   update `IDEAL-CUSTOMER-PROFILE.md` (queries) and `OFFER.md` (proof map) with what you learned.
5. **Write `SALES-REPORT.md`** (`references/report-output-format.md`): summary, funnel table, top prospects, stale deals,
   source performance, and an action plan (today / this week / this month) with one concrete action per prospect.
   No file access → give the report in your answer. For a PDF, the user exports the Markdown (print to PDF, Google Docs,
   Notion) — never say a PDF was created. Quality and edge cases: `references/rules.md`.

## References (read when you reach that step)

- `references/report-playbook.md` — analysis steps and pipeline-health rules
- `references/report-output-format.md` — SALES-REPORT.md template
- `references/rules.md` — quality standards and edge cases
