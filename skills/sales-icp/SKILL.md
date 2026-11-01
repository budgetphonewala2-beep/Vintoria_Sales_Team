---
name: sales-icp
description: "Builds the Ideal Customer Profile every other sales skill scores against — firmographics, buying signals, pain points, budget qualifiers, negative ICP, scoring rubric, 2-3 buyer personas, channels and the intent phrases buyers use (English, Hindi, Hinglish) — from a description of what the user sells, written to IDEAL-CUSTOMER-PROFILE.md. Use when the user says 'build my ICP', 'who should I target', 'ideal customer', 'I sell X to Y', '/sales icp', or in Hinglish 'mera ideal client kaun hai', 'kisko target karun'."
license: MIT
compatibility: "Any agent that supports Agent Skills. Helper scripts need Python 3.9+ (standard library; reportlab only for PDF). Web access via the agent or the bundled fetch/search scripts."
metadata:
  author: "Zubair Trabzada (original), Vintoria (portable upgrade)"
  version: "3.0.0"
---

# Ideal Customer Profile

Start here. Every fit score in the other skills is only as good as this profile.

## Before you start

1. **Scripts.** `<SCRIPTS>` means the `scripts/` folder of the `sales` skill — `../sales/scripts/` next to this
   skill's folder. Run them with `python` (Windows) or `python3` (macOS/Linux). Every script prints one JSON
   object. Script output is evidence to check, not truth.
2. **Web access.** Use your agent's own web fetch / search if it has them. Otherwise run
   `python <SCRIPTS>/fetch_page.py <url> [<url> ...]` and `python <SCRIPTS>/web_search.py "<query>"`
   (search needs `BRIGHTDATA_API_KEY`). If you can't fetch something, write "Not found" — never fill gaps.
3. **Prospect folder.** Files about one prospect live in `prospects/<slug>/` (slug = domain without `www.`,
   e.g. `acme.com`). Given only a name, look for an existing `prospects/*/` folder first, then find the
   official domain. Never use another prospect's files as context. Shared files (`IDEAL-CUSTOMER-PROFILE.md`,
   `OBJECTION-PLAYBOOK.md`, `SALES-REPORT*`) stay in the working-directory root.
4. **Pipeline.** The pipeline database (`~/.ai-sales-team/pipeline.db`) is the source of truth across
   sessions and agents. Record what you learn with `python <SCRIPTS>/pipeline.py ...` (commands below).
5. **What the user sells.** Read `IDEAL-CUSTOMER-PROFILE.md` if it exists. If it doesn't and you don't know
   the offer, ask once: "What do you sell, and to whom?" If the user sells services (agency, freelancer,
   consultant), judge fit by visible need — site quality, public posts asking for help, hiring for the role,
   ad activity — not by funding or headcount.
6. **Facts, not fiction.** Never invent people, titles, emails, mutual connections, customer results,
   funding or metrics. Unknown = "Not found". Pattern-built emails = `pattern-guessed — verify before
   sending`. A missing proof point = a visible `[ADD REAL CUSTOMER RESULT]` marker.

## Steps

1. Parse what the user sells: services/products, price ranges, delivery capacity, markets (e.g. India + US/UK/AU),
   languages, best past clients. Ask for anything missing in one short message.
2. Research the market briefly (`references/playbook.md` Research Phase) — who buys this, where they talk.
3. Build the framework (Steps 2-7): firmographics, technographics, behavioural and **intent signals** (the exact
   phrases buyers post, e.g. "need a website for my clinic", "website banwana hai", "koi SEO wala batao"),
   pain map, budget qualifiers, channels, negative ICP, a 0-100 scoring rubric, 2-3 personas, prospecting playbook.
4. Write `IDEAL-CUSTOMER-PROFILE.md` in the working-directory root (`references/output-format.md`). Include a
   "Search queries" section with 5-10 X-ray queries for `sales-hunt`.

## References (read when you reach that step)

- `references/playbook.md` — the 7 ICP steps and rubric
- `references/output-format.md` — IDEAL-CUSTOMER-PROFILE.md template
- `references/rules.md` — quality rules
