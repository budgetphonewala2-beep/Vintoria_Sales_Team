---
name: sales-report
description: "Produces a pipeline report from the persistent pipeline database and the prospects/*/ folders — funnel by stage, reply/meeting/win rates, grades, stale deals, actions due today, which sources produce meetings, and a prioritized weekly action plan — written to SALES-REPORT.md. Use when the user says 'pipeline report', 'how is my pipeline', 'what should I do today', 'weekly sales review', '/sales report', or in Hinglish 'pipeline ka report do', 'aaj kya karna hai', 'kitne leads hain'."
license: MIT
compatibility: "Any agent that supports Agent Skills. Helper scripts need Python 3.9+ (standard library; reportlab only for PDF). Web access via the agent or the bundled fetch/search scripts."
metadata:
  author: "Zubair Trabzada (original), Vintoria (portable upgrade)"
  version: "3.0.0"
---

# Pipeline Report

You turn the pipeline into decisions: what to do today, this week, and what to stop doing.

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

1. Get the numbers: `python <SCRIPTS>/pipeline.py report` (funnel, conversion, grades, stale, due today, by source, top 10) and
   `python <SCRIPTS>/pipeline.py list`.
2. Fill in from files: for prospects in `prospects/*/` not yet in the pipeline, read their files and add them
   (`python <SCRIPTS>/pipeline.py add ...`, `python <SCRIPTS>/pipeline.py score ...`) so the report is complete.
3. Analyse (`references/playbook.md`): pipeline health, stuck deals and why, which sources/queries produce
   replies and meetings, score distribution, gaps (e.g. no verified contacts).
4. Write `SALES-REPORT.md` (`references/output-format.md`): summary, funnel table, top prospects, stale deals,
   source performance, action plan (today / this week / this month) with one concrete action per prospect.
5. Offer `sales-report-pdf` for a shareable version.

## References (read when you reach that step)

- `references/playbook.md` — analysis steps and health rules
- `references/output-format.md` — SALES-REPORT.md template
- `references/rules.md` — rules
