---
name: sales-audit
description: "Runs a fact-only audit of a prospect's website — title, meta description, mobile viewport, HTTPS redirect, load time, page size, H1s, contact form, click-to-call, WhatsApp link, call-to-action, images missing alt text, tech stack (WordPress, Shopify, Wix, Webflow, Next.js), copyright year, broken internal links — each fact with evidence, no opinions, and turns the strongest facts into outreach observations. Use when the user says 'audit this website', 'check their site', 'what's wrong with their website', 'give me a hook for this prospect', or in Hinglish 'is website ko check karo', 'site mein kya problem hai'."
license: MIT
compatibility: "Any agent that supports Agent Skills. Helper scripts need Python 3.9+ (standard library; reportlab only for PDF). Web access via the agent or the bundled fetch/search scripts."
metadata:
  author: "Zubair Trabzada (original), Vintoria (portable upgrade)"
  version: "3.0.0"
---

# Website Audit — proof-of-work facts for outreach

A specific, true observation about someone's own website is the strongest opener an agency has.
This skill produces only facts the page itself proves, so outreach built on it survives the claim check.

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

1. Run the audit and save it in the prospect folder:
   `python <SCRIPTS>/site_audit.py --url <url> --save prospects/<slug>/SITE-AUDIT.json`
   (add `--no-links` for a faster run; robots.txt is respected).
2. Write `prospects/<slug>/SITE-AUDIT.md`: the URL, date, and a table of every fact (`statement` + `evidence`).
3. Pick the **top 3 observations** that matter to the prospect's business, using
   `references/fact-to-hook.md` (e.g. no viewport → phone visitors get the desktop layout; no CTA →
   visitors don't know the next step; copyright 2019 → site looks unmaintained). State the fact exactly as the
   audit does; any consequence you add must be phrased as likely ("so phone visitors probably..."), never as a
   measured number.
4. Record it: `python <SCRIPTS>/pipeline.py add --url <url>` (if new), `python <SCRIPTS>/pipeline.py attach <slug> prospects/<slug>/SITE-AUDIT.json --kind site-audit`,
   `python <SCRIPTS>/pipeline.py note <slug> "Audit hooks: <hook 1>; <hook 2>"`.
5. Suggest `sales-outreach` next — it will use these facts as evidence.

## Rules
- Facts only. No scores like "your SEO is 4/10", no guessed traffic, no "your site is slow" unless the fact
  says the download took N seconds — and then quote N.
- Never claim certificate or security problems from a TLS error on your side.
- If the homepage didn't load or robots.txt blocks it, say so and stop.

## References (read when you reach that step)

- `references/fact-to-hook.md` — how each audit fact becomes a respectful one-line observation, with examples
