<p align="center">
  <img src="banner.svg" alt="Vintoria Sales" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/8_skills-Agent_Skills_spec-8b5cf6?style=for-the-badge" alt="8 skills">
  <img src="https://img.shields.io/badge/works_in-Claude_Code·Codex·Cursor·Gemini·OpenCode-0ea5e9?style=for-the-badge" alt="Agents">
  <img src="https://img.shields.io/badge/license-MIT-gray?style=for-the-badge" alt="MIT License">
</p>

# Vintoria Sales — from "who needs us?" to a signed client

Eight skills and a tested Python engine that run Vintoria's whole sales loop in any coding agent that supports
[Agent Skills](https://agentskills.io/specification) (Claude Code, Codex CLI, Cursor, Gemini CLI, OpenCode):
find people **publicly asking** for what Vintoria sells, research them, reach the decision maker at a **verified**
address, write outreach that states only **checked facts**, run the follow-ups, answer replies, **book the call**,
prep and run discovery, write the proposal and close.

Vintoria is a digital product studio with **270 services in 12 disciplines** — strategy, web, SaaS, mobile, UI/UX,
branding, AI, automation, backend & cloud, e-commerce, digital marketing & SEO, growth. The skills sell from that
catalog (exact service IDs, never invented ones) to SMBs in **India, the US, UK and Australia**, and read posts and
replies in English, Hindi and Hinglish.

## The 8 skills

| Skill | Say… | Does |
|---|---|---|
| `vintoria-sales` | "aaj ka kaam batao", "run my sales" | The operator: today's agenda from the pipeline, worked in priority order; routes everything else; holds the truth, pricing, quality and compliance rules and the catalog |
| `vintoria-setup` | "set up Vintoria", "who should we target" | Profile interview (starts from the Vintoria preset), offer lanes by catalog ID with a proof map, ideal customer + search queries |
| `vintoria-lead-hunt` | "clients dhundo", "who needs an AI chatbot" | Finds buyer posts on LinkedIn, Reddit, X, FB groups, Quora, HN, Upwork + Maps/Apollo lists; judges with an exact quote; deep-researches the best |
| `vintoria-prospect-research` | "research acme.com", "owner kaun hai", "audit their site" | Deep scan → dossier, fact-only site audit, sourced research, verified emails, BANT/MEDDIC, battle cards, full 0-100 analysis — hooks mapped to catalog services |
| `vintoria-outreach` | "is client ko email likho", "follow up likho" | First email + 5-step sequence (day 0/3/7/14/28), claim-checked and quality-scored, queued after your approval; follow-ups after meetings and proposals |
| `vintoria-reply-book` | "client ne reply kiya", "meeting fix karo" | Classifies the reply, answers it, stops the sequence, offers slots in both time zones, writes the `.ics` invite, records the outcome |
| `vintoria-close` | "meeting ki taiyari karo", "proposal banao", "bahut mehenga hai" | Prep brief, scored discovery call, proposal by catalog ID with 3 scope options, objection answers, negotiation, handoff, upsell and referrals |
| `vintoria-report` | "pipeline ka report do" | Funnel, rates, forecast, what works (sources, queries, hooks, services, markets), weekly plan, PDF |

```
setup ─► lead-hunt ─► prospect-research ─► outreach ─► (auto follow-ups) ─► reply-book ─► close ─► report
profile    buyer posts    dossier + email     approved     day 3/7/14/28       answer+book    prep → proposal → signed
```

## Install

```bash
git clone https://github.com/radianmarketingg-collab/Sales_Team.git
cd Sales_Team
python -m pip install -r requirements.txt   # ReportLab (PDF), certifi (TLS), tzdata (Windows time zones)
python install.py                           # ~/.agents/skills (Codex, Cursor, Gemini, OpenCode) + ~/.claude/skills
```

Options: `--agent claude-code|codex|cursor|gemini|opencode|agents|all`, `--link` (edits in the repo apply at once),
`--with-claude-agents` (parallel research roles and team subagents in Claude Code), `--project <dir>`, `--uninstall`,
`--dry-run`. Upgrading from v3 retires the old `sales-*` skills and subagents (backed up to `~/.ai-sales-team/backups/`).

Then, in your agent: **"use vintoria-setup"**. It starts from `seller_profile.py init --preset vintoria` and asks
only what it can't know: sender name and email, postal address, time zone, active disciplines, niches, deal sizes,
real case studies.

**API keys (all optional)** go in `~/.ai-sales-team/.env` — never in the repo. Template: [`examples/env.example`](examples/env.example).

| Key | Adds |
|---|---|
| `BRIGHTDATA_API_KEY` + `BRIGHTDATA_ZONE` | the main lead engine: newest buyer posts via Google X-ray |
| `APIFY_TOKEN` | LinkedIn post search, Maps, Apollo-style lists, web research |
| `PROSPEO_API_KEY` / `FINDYMAIL_API_KEY` / `HUNTER_API_KEY` / `APOLLO_API_KEY` | email finders |
| `MILLIONVERIFIER_API_KEY` / `ZEROBOUNCE_API_KEY` / `NEVERBOUNCE_API_KEY` | email verification |
| `SMTP_*`, `IMAP_*` | sending approved emails, reading replies (hands-free mode) |
| `BOOKING_URL`, `MEETING_LINK`, `TIMEZONE` | booking and invites |

Without keys everything still works: research uses your agent's web tools or `fetch_page.py`, and emails are
labelled `unverified` / `pattern-guessed` instead of `verified`.

**Hands-free mode:** with SMTP + IMAP set, `python skills/vintoria-sales/scripts/ops/autopilot.py schedule` prints the
cron / Task Scheduler line; every 30 minutes it reads replies first, then sends only the follow-ups you approved.

## Repository layout

```
skills/
  vintoria-sales/            operator + shared references + the engine
    references/              truth-rules, quality-bar, pricing-policy, team, compliance,
                             service-catalog + services-01..12 (all 270 services)
    scripts/
      core/                  pipeline.py, seller_profile.py (+ presets/vintoria.json), sales_common.py
      leads/                 serp.py, lead_sources.py, query_library.py, intent_scan.py, post_lead.py, lead_scorer.py
      research/              prospect_scan.py, site_audit.py, find_email.py, contact_finder.py, analyze_prospect.py,
                             fetch_page.py, web_search.py
      outreach/              outreach.py, claim_check.py, email_lint.py, mailboxes.py
      replies/               inbox.py, reply_triage.py, meeting.py
      ops/                   autopilot.py, learn.py, notify.py, generate_pdf_report.py
  vintoria-setup/ … vintoria-report/   SKILL.md + references/ (+ evals/ test cases)
adapters/claude-code/agents/ optional subagents (parallel roles)
docs/vintoria/               the 270-service catalog (PDF, JSON, list)
examples/                    env.example, sample posts
tools/                       build_skills.py, skill_specs.py, validate_skills.py
tests/                       192 tests (scripts, end-to-end flow, guards, installer, skill validation)
archive/                     the earlier instruction-only Vintoria skill set, kept for reference (not installed)
```

User data stays outside the repo: `~/.ai-sales-team/` (pipeline database, `.env`, backups) and, in your working
folder, `SELLER-PROFILE.json`, `OFFER.md`, `IDEAL-CUSTOMER-PROFILE.md` and `prospects/<domain>/`.

## Safety and honesty (enforced in code)

- **No invented facts.** `claim_check.py` checks every declarative sentence against saved evidence: numbers from one
  source, quotes verbatim, names and brands present in the evidence, negations caught, snippets alone never enough.
- **No invented prices.** The catalog has none; a price comes only from the profile, otherwise `[PRICE TO CONFIRM]`.
- **Real catalog services only**, named by exact ID (a test checks every ID quoted in a skill).
- **Verified emails only** for cold email; a hand-typed "verified" is downgraded without a verifier record.
- **You approve every message.** Sending passes every gate: verified address, claim check, quality score, opt-out,
  postal address, daily limit, warm-up, do-not-contact list, no booking link before interest.
- **Compliance** per market: CAN-SPAM, UK PECR, EU GDPR/ePrivacy, CASL, Australia Spam Act, India DPDP + TRAI.
- Never posts, comments or DMs on social platforms; WhatsApp is a click-to-chat link you open yourself.
- Opt-outs and bounces are applied at once and never contacted again; robots.txt respected; paid calls capped.

## Development

```bash
python -m pip install pytest reportlab skills-ref
python -m pytest tests                # everything
python tools/build_skills.py          # regenerate SKILL.md files from tools/skill_specs.py
python tools/validate_skills.py       # Agent Skills spec, commands and flags, references, catalog paths
python tools/build_skills.py --check  # CI: fail if a generated file was edited by hand
```

`skills/*/SKILL.md` and `references/compliance.md` are generated — edit `tools/skill_specs.py` (and the shared blocks in
`tools/build_skills.py`), never the generated files. CI runs everything on Windows, macOS and Linux (Python 3.9, 3.13).

## Credits

Built on [ai-sales-team-claude](https://github.com/zubair-trabzada/ai-sales-team-claude) by Zubair Trabzada (MIT).
Intent scoring adapted from [lead-signal-listener](https://github.com/yangyixxxx/lead-signal-listener) (MIT); claim
matching and reply ideas from [autonomous-sdr](https://github.com/RodricDib06/autonomous-sdr) (MIT). See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Version history: [CHANGELOG.md](CHANGELOG.md). License: [MIT](LICENSE).
