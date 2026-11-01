---
name: sales-followup
description: "Writes follow-up sequences after a meeting, demo, proposal, a prospect going silent, or for long-term nurture — emails, LinkedIn touches, voicemail and SMS scripts with a cadence calendar — based on what actually happened (meeting notes, replies), claim-checked, written to FOLLOWUP-SEQUENCE.md and tracked in the pipeline. Use when the user says 'follow up with', 'they went quiet', 'after the demo', 'proposal follow-up', 'ghosted', '/sales followup', or in Hinglish 'follow up likho', 'reply nahi aaya', 'meeting ke baad kya bhejun'."
license: MIT
compatibility: "Any agent that supports Agent Skills. Helper scripts need Python 3.9+ (standard library; reportlab only for PDF). Web access via the agent or the bundled fetch/search scripts."
metadata:
  author: "Zubair Trabzada (original), Vintoria (portable upgrade)"
  version: "3.0.0"
---

# Follow-Up Sequences

Follow-ups win most deals. You write ones that add value instead of "just checking in".

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

1. Ask (or read) what happened: last touch, what they said, what was promised, pricing shared, objections.
   Read `python <SCRIPTS>/pipeline.py show <slug>` and the prospect folder.
2. Pick the scenario (`references/playbook.md` Step 2): post-meeting, post-demo, post-proposal, ghost recovery
   or nurture, and its cadence.
3. Write the emails plus LinkedIn/phone/SMS touches only where appropriate (SMS only for warm leads who
   shared their number). Reference real details from the conversation.
4. Claim-check every email.
5. Write `prospects/<slug>/FOLLOWUP-SEQUENCE.md` (`references/output-format.md`).
6. Record: `python <SCRIPTS>/pipeline.py note <slug> "<what happened>"`, `python <SCRIPTS>/pipeline.py next <slug> "<next touch>" --due <date>`, and update
   the stage (`replied`, `meeting`, `proposal`, `nurture`, `lost`) when the user tells you.

## Before anything is sent

- Run the claim check on every email/proposal you write and fix it until it passes:
  `python <SCRIPTS>/claim_check.py --draft <file> --evidence "prospects/<slug>/*.md" [--evidence prospects/<slug>/SITE-AUDIT.json] [--evidence-text "<their post>"]`
  Rewrite or delete each unsupported sentence; fill or remove every `[PLACEHOLDER]`.
- Follow `references/compliance.md` (opt-out line, postal address for US, consent rules for UK/EU/Canada/India).
- You write drafts only. The user sends them — never claim an email was sent.

## References (read when you reach that step)

- `references/playbook.md` — the 5 scenarios, multi-channel touches, cadence, breakup emails
- `references/output-format.md` — FOLLOWUP-SEQUENCE.md template
- `references/compliance.md` — legal and deliverability rules
- `references/rules.md` — rules
