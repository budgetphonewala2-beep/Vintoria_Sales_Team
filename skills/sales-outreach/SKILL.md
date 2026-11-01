---
name: sales-outreach
description: "Writes a personalized, compliant cold outreach sequence for a prospect — a short first email built on one verified observation (their public post or a site-audit fact), 4 follow-ups and LinkedIn touches — with A/B subject lines, every sentence claim-checked against evidence before it is shown, written to OUTREACH-SEQUENCE.md and tracked in the pipeline. Use when the user says 'write a cold email', 'outreach sequence', 'email this prospect', 'LinkedIn message', '/sales outreach', or in Hinglish 'is client ko email likho', 'cold email banao', 'pehla message likho'."
license: MIT
compatibility: "Any agent that supports Agent Skills. Helper scripts need Python 3.9+ (standard library; reportlab only for PDF). Web access via the agent or the bundled fetch/search scripts."
metadata:
  author: "Zubair Trabzada (original), Vintoria (portable upgrade)"
  version: "3.0.0"
---

# Cold Outreach Sequence

You write outreach a busy owner actually answers: short, specific, true, and easy to say yes to.

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

1. **Evidence first.** Collect what you know: their post (if they asked publicly), `prospects/<slug>/` files,
   `SITE-AUDIT.json` (run `sales-audit` if missing), `DECISION-MAKERS.md` and the pipeline record
   (`python <SCRIPTS>/pipeline.py show <slug>`). Recipient must have a `verified` email, or say clearly that it isn't.
2. **First email** — follow `references/first-email-guide.md`: plain text, under 120 words, mentions their post
   or business naturally, ONE specific observation backed by evidence, one soft CTA (a 15-minute call), the
   user's signature with postal address and an opt-out line.
3. **Sequence** — 4 follow-ups and LinkedIn touches using `references/playbook.md` (frameworks, timing,
   breakup email) and the templates `references/template-outreach-cold.md`, `-warm.md`, `-referral.md`.
   Use the warm or referral template only for a real, confirmed connection.
4. **Claim check** every email (see "Before anything is sent"); fix until it passes.
5. Write `prospects/<slug>/OUTREACH-SEQUENCE.md` (`references/output-format.md`).
6. Record: `python <SCRIPTS>/pipeline.py attach <slug> prospects/<slug>/OUTREACH-SEQUENCE.md --kind outreach` and
   `python <SCRIPTS>/pipeline.py next <slug> "Send email 1 (user)" --due <date>`. When the user confirms they sent it:
   `python <SCRIPTS>/pipeline.py stage <slug> contacted --reason "email 1 sent"`.

## Before anything is sent

- Run the claim check on every email/proposal you write and fix it until it passes:
  `python <SCRIPTS>/claim_check.py --draft <file> --evidence "prospects/<slug>/*.md" [--evidence prospects/<slug>/SITE-AUDIT.json] [--evidence-text "<their post>"]`
  Rewrite or delete each unsupported sentence; fill or remove every `[PLACEHOLDER]`.
- Follow `references/compliance.md` (opt-out line, postal address for US, consent rules for UK/EU/Canada/India).
- You write drafts only. The user sends them — never claim an email was sent.

## References (read when you reach that step)

- `references/first-email-guide.md` — style rules + 10 good/bad first-email examples
- `references/playbook.md` — personalization research, 4 frameworks, the 5-email sequence, LinkedIn, A/B, sending
- `references/output-format.md` — OUTREACH-SEQUENCE.md template
- `references/template-outreach-cold.md` — cold template
- `references/template-outreach-warm.md` — warm intro template
- `references/template-outreach-referral.md` — referral template
- `references/compliance.md` — legal and deliverability rules
- `references/rules.md` — terminal output, errors, cross-skill use
