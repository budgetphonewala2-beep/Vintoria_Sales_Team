<p align="center">
  <img src="banner.svg" alt="AI Sales Team" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/20_skills-Agent_Skills_spec-8b5cf6?style=for-the-badge" alt="20 skills">
  <img src="https://img.shields.io/badge/works_in-Claude_Code·Codex·Cursor·Gemini·OpenCode-0ea5e9?style=for-the-badge" alt="Agents">
  <img src="https://img.shields.io/badge/license-MIT-gray?style=for-the-badge" alt="MIT License">
</p>

# AI Sales Team — portable sales skills for any coding agent

Find people who are **asking** for what you sell, research and score them, find **verified** contacts, write
outreach that only states **checked facts**, run the **follow-up cadence**, handle **replies**, **book the
meeting** with a calendar invite, prep it, write the proposal, and keep a **persistent pipeline** — from Claude Code, OpenAI Codex CLI, Cursor, Gemini CLI, OpenCode or any agent that supports the
open [Agent Skills](https://agentskills.io/specification) format.

Built for B2B sellers and especially for **agencies, freelancers and consultants** (web, app, SEO, marketing,
design) selling to SMBs in India, the US, UK and Australia. Posts and replies can be English, Hindi or Hinglish.

> v3 is a portable upgrade of [zubair-trabzada/ai-sales-team-claude](https://github.com/zubair-trabzada/ai-sales-team-claude)
> (MIT). See [AUDIT.md](AUDIT.md) for what was wrong with v1/v2 and [CHANGELOG.md](CHANGELOG.md) for what changed.

## End to end: client dhundne se meeting book karne tak

```
sales-hunt ─► sales-audit ─► sales-contacts ─► sales-outreach ─► follow-up cadence ─► sales-reply ─► sales-book ─► sales-prep ─► sales-proposal
   find          proof          verified          email 1          auto-scheduled        classify        slots + .ics      brief         close
```

Say **"aaj ka kaam batao"** / "run my sales" and `sales-autopilot` builds today's agenda from the pipeline —
replies first, then meetings to prep, follow-ups due, stale deals, best new leads — and works through it with
you, refilling the funnel with `sales-hunt` when it runs low. You approve every message before it goes out.

## What's new in v3.4 — it learns you first, then hunts overseas clients

| | v3.3 | v3.4 |
|---|---|---|
| First run | Agent asked "what do you sell?" | **`sales-setup`** interviews you in 3 short rounds → `SELLER-PROFILE.json` (services, niches, platforms, outcomes, deal size, countries, excluded markets, buyer titles, pains, triggers, tools clients leave, real proof). Every skill checks it first |
| Queries | Per service | **Built from your profile**: niche × service, pain, trigger, switching ("moving from Wix"), platform and recommendation queries; Apollo URLs; LinkedIn people filters; niche subreddits; Maps in your cities |
| Market | India + abroad, Hinglish | **International by default** (US, UK, CA, AU…), English only; `NOT India` / `-India` in queries and leads mentioning an excluded market dropped |
| People databases | — | **Apollo via Apify** (`code_crafter/apollo-scraper`), **Leads Finder** (Apollo-style filters), **LinkedIn people search** and **company employees** (HarvestAPI); `--add --verify` |
| Send time | Your hours | **The prospect's morning** — each email waits for 09:00-17:00 in their time zone (country from domain, `pipeline.py where`, or your first target country) |
| Compliance | US/UK/EU/CA/IN | + **Australia Spam Act** and **NZ UEMA** consent rules |

```
python skills/sales/scripts/seller_profile.py check      # what the agent still needs to ask you
python skills/sales/scripts/query_library.py             # the queries your profile produces
python skills/sales/scripts/lead_sources.py apollo --max 200 --add --verify
```

## What's new in v3.3 — every lead source, sharper queries, deep scans

| | v3.2 | v3.3 |
|---|---|---|
| Sources | LinkedIn, Google, Reddit (Apify) | + **Hacker News** (free, incl. monthly "Seeking freelancer" thread), **Reddit free JSON**, **X/Twitter**, **Facebook groups**, **Google Maps** (no-website / low-rating businesses + phone), **Product Hunt** launches, Quora / Indie Hackers / Upwork jobs / hiring signals via X-ray |
| Queries | A few defaults | **`query_library.py`**: ASK + SERVICE + platform + exclusions + recency for 8 services; LinkedIn boolean queries checked against the 5-operator / 500-char limit; Hinglish; location-aware |
| Email in the post | Finders still ran | **No finder credits spent** when the post (or their site, for the named person) already has the address — it's only verified |
| Research | Separate scripts | **`prospect_scan.py`**: site audit + company + people + email + 11 web searches → `DOSSIER.md` with ranked, evidence-backed hooks, straight into the pipeline |
| Skills | — | All 19 reviewed: dossier-first workflow, channel by lead source, day-by-day sequence content plan, service-buyer red flags, proposal terms, local competitor hooks, ICP → hunt settings |

```
python skills/sales/scripts/lead_sources.py hunt --services web,seo --location Pune --save hunt.json
python skills/sales/scripts/prospect_scan.py https://lead.com --post-text "<their post>" --source hunt:li-web-1
```

## What's new in v3.2 — hands-free from lead to booked call

| | v3.1 | v3.2 |
|---|---|---|
| Lead sources | Bright Data Google X-ray, pasted posts | **Apify**: LinkedIn posts via HarvestAPI (no cookies), Google, Reddit, or any actor — one `lead_sources.py hunt` |
| Research | Website only | `lead_sources.py research`: reviews, news, LinkedIn, social, directories, hiring → evidence file |
| Email finding | Hunter | **Waterfall**: Prospeo → Findymail → Hunter → Apollo, then MillionVerifier / ZeroBounce / NeverBounce / Hunter verification (patterns verified too) |
| Follow-ups | Scheduled, sent by hand | **Approve once, sends itself** on day **3, 7, 14, 28** in the same thread, inside send hours, under the daily cap |
| Replies | Pasted by hand | **`inbox.py`** reads IMAP (read-only); any reply/bounce/opt-out stops the sequence |
| Booking link | Anywhere | **Only after interest** — refused in cold emails; optional instant link reply to "let's talk" |
| Running it | Every session | **`autopilot.py tick --send`** every 30 min via cron / Task Scheduler (never sends without an inbox check) |

```
                ┌──────────── autopilot.py tick (every 30 min) ────────────┐
lead_sources ─► find_email ─► outreach approve ─► run: day 0 · 3 · 7 · 14 · 28
 (Apify)        (waterfall)    (you OK 5 emails)        ▲ stops on reply
                                                        │
                               inbox.py ── reply? ──────┘──► "let's talk" → booking link → meeting.py book
```

## What's new in v3.1

| | v3.0 | v3.1 |
|---|---|---|
| After the first email | You tracked follow-ups by hand | **`outreach.py`** logs every touch and schedules follow-ups on a business-day cadence |
| Sending | Copy-paste only | Copy-paste **or** optional SMTP sending with hard gates: verified address, claim check, opt-out line, postal address, daily limit, do-not-contact list, dry run first |
| Replies | Not handled | **`sales-reply`** + `reply_triage.py`: 12 categories (EN/HI/Hinglish), stops follow-ups, suppresses opt-outs, marks bounces invalid |
| Booking | Not handled | **`sales-book`** + `meeting.py`: slots that fit both time zones (incl. India ↔ US), `.ics` invites, prep + reminder scheduled, outcomes |
| Daily driver | `sales-report` | **`sales-autopilot`** + `pipeline.py today`: prioritised agenda, end to end |
| WhatsApp | — | Click-to-chat links (the user sends) |
| TLS | Unverified fallback when a certificate failed | **Always verified**, no fallback |
| CI | none | GitHub Actions: Windows/macOS/Linux × Python 3.9/3.13, generated-file check, validator, tests |

## What's new in v3

| | v2 | v3 |
|---|---|---|
| Agents | Claude Code only | Any Agent Skills agent (spec-only frontmatter, validated with `skills-ref`) |
| Lead sources | You bring a URL | **`sales-hunt`**: finds public posts asking for your service (EN/HI/Hinglish), filters sellers, job seekers and job ads |
| Proof for outreach | Generic research | **`sales-audit`**: fact-only website audit, every fact with evidence |
| Emails | Pattern guesses | **`find_email.py`**: website + JSON-LD extraction, Hunter verification; guesses always labelled |
| Hallucination guard | Prompt rules | **`claim_check.py`**: flags every sentence no evidence supports (numbers and quotes must match) |
| Memory | Loose Markdown files | **`pipeline.py`**: SQLite pipeline with stages, contacts, history, stale-deal and source reports |
| Scoring | US-SaaS signals only | BANT/MEDDIC **plus an agency-buyer model** (intent, urgency, freshness, contactability) |
| Prospect roles | 5 Claude subagents (never actually loaded) | 5 role playbooks any agent runs in sequence; optional Claude subagents for parallelism |
| Install | bash only | `python install.py` on Windows, macOS, Linux |
| Skill size | 320-850 lines each | 50-110 lines each, details in `references/` |
| Tests | none | pytest suite + skill validator |

## Install

```bash
git clone https://github.com/radianmarketingg-collab/Sales_Team.git
cd Sales_Team
python install.py                 # ~/.agents/skills (Codex, Cursor, Gemini, OpenCode) + ~/.claude/skills
```

Options: `--agent claude-code|codex|cursor|gemini|opencode|agents|all` (repeatable), `--link` (symlink, edits
apply immediately), `--with-claude-agents` (parallel prospect roles in Claude Code), `--project <dir>`
(install into `<dir>/.agents/skills`), `--uninstall`, `--dry-run`. Existing copies are backed up to
`~/.ai-sales-team/backups/` before an upgrade.

Requirements: Python 3.9+. `pip install -r requirements.txt` adds ReportLab (PDF reports) and certifi (TLS on
some Windows/macOS Pythons). Everything else is the standard library.

**Optional API keys** — put them in `~/.ai-sales-team/.env` (never in the repo):

```ini
BRIGHTDATA_API_KEY=...   # Google search for sales-hunt / web_search.py (Bright Data SERP API)
BRIGHTDATA_ZONE=serp_api1
HUNTER_API_KEY=...       # email finder + verifier
SMTP_PASSWORD=...        # only if you want the agent to send approved emails (see examples/env.example)
APIFY_TOKEN=...          # LinkedIn posts (HarvestAPI), Google, Reddit, X, Facebook groups, Google Maps via Apify
PRODUCTHUNT_TOKEN=...    # new launches (free developer token); Hacker News needs no key
PROSPEO_API_KEY=...      # or FINDYMAIL_API_KEY / APOLLO_API_KEY — email finders, tried in order
MILLIONVERIFIER_API_KEY=...  # or ZEROBOUNCE_API_KEY / NEVERBOUNCE_API_KEY — email verification
```

**Hands-free mode** (optional): set SMTP + IMAP in the `.env`, approve a sequence per prospect
(`outreach.py approve`), then run `python skills/sales/scripts/autopilot.py schedule` and add the line it prints
to cron (macOS/Linux) or Task Scheduler (Windows). Every 30 minutes it reads replies first, then sends the
follow-ups that are due. The computer (or a small VPS) has to be on.

Your sender details, time zone, work hours and booking link go in the same file — copy
[`examples/env.example`](examples/env.example) and fill in what you use.

Without keys everything still works: your agent's own web tools (or `fetch_page.py`) do the research, and
emails are labelled `unverified` / `pattern-guessed` instead of `verified`.

## Skills

| Skill | Ask your agent... | Output |
|---|---|---|
| `sales` | "use the sales skill" — routes to the rest | — |
| `sales-setup` | "set me up" / "mere business ke baare mein pucho" — **run first** | `SELLER-PROFILE.json` |
| `sales-icp` | "build my ideal customer profile" | `IDEAL-CUSTOMER-PROFILE.md` |
| `sales-hunt` | "find people looking for a web developer this week" / "clients dhundo" | candidates → pipeline |
| `sales-audit` | "audit sweetcrumbs.in" | `SITE-AUDIT.json` + `.md` |
| `sales-prospect` | "full prospect analysis of acme.com" | `PROSPECT-ANALYSIS.md` (0-100 score) |
| `sales-research` | "research acme.com" | `COMPANY-RESEARCH.md` |
| `sales-qualify` | "qualify this lead (BANT/MEDDIC)" | `LEAD-QUALIFICATION.md` |
| `sales-contacts` | "who should I contact at acme.com, get their email" | `DECISION-MAKERS.md` |
| `sales-competitors` | "who is their current agency, battle card" | `COMPETITIVE-INTEL.md` |
| `sales-outreach` | "write a cold email to acme.com" | `OUTREACH-SEQUENCE.md` (claim-checked) |
| `sales-followup` | "they went quiet after the proposal" | `FOLLOWUP-SEQUENCE.md` |
| `sales-prep` | "prep me for tomorrow's call with acme" | `MEETING-PREP.md` |
| `sales-proposal` | "write a proposal for acme" | `CLIENT-PROPOSAL.md` |
| `sales-objections` | "client says it's too expensive" / "bahut mehenga hai" | `OBJECTION-PLAYBOOK.md` |
| `sales-reply` | "they replied: 'kitna lagega?'" / "iska jawab likho" | classified reply + answer |
| `sales-book` | "book a call with Priya, she's in New York" / "meeting fix karo" | `MEETING-<date>.ics` + pipeline |
| `sales-autopilot` | "run my sales today" / "aaj ka kaam batao" | today's agenda, done step by step |
| `sales-report` | "how is my pipeline, what should I do today" | `SALES-REPORT.md` |
| `sales-report-pdf` | "PDF of the pipeline" | `SALES-REPORT-<date>.pdf` |

In Claude Code you can also type `/sales <command> <input>`.

## A typical week

```
sales-setup     3-round interview → SELLER-PROFILE.json (Shopify stores for DTC brands; US, UK, CA, AU; not India)
sales-icp       ICP + the queries that profile produces
sales-hunt      → 14 candidates, 5 real buyers judged with exact quotes, added to the pipeline
sales-audit     sweetcrumbs.in → "no mobile viewport", "© 2019 footer", "no Book/Call button"
sales-contacts  sweetcrumbs.in → Anita Desai, Founder, anita@sweetcrumbs.in (verified via Hunter)
sales-outreach  sweetcrumbs.in → 96-word first email, claim check: 4/4 sentences supported
                you approve → outreach.py send (or you send it, outreach.py log) → follow-up #1 due Thursday
sales-reply     "Haan interested, kal 5 baje call karte hain" → meeting_request, follow-ups stopped
sales-book      Thu 5:00 PM IST → MEETING-2026-11-05.ics, stage meeting, prep due Wednesday
sales-prep      Wednesday: brief with her post, audit facts and the whole thread
sales-autopilot every morning: replies → meetings → follow-ups → new leads
sales-report    Monday review: funnel, stale deals, which hunt queries produced meetings
```

## Helper scripts (`skills/sales/scripts/`)

Every script prints one JSON object and is safe to run from any agent or by hand.

| Script | What it does |
|---|---|
| `pipeline.py` | `add`, `list`, `show`, `stage`, `score`, `note`, `contact`, `attach`, `next`, `report [--pdf-input]`, `today`, `suppress`, `remove` |
| `lead_sources.py` | `hunt` (all), `linkedin`, `hackernews`, `reddit`, `x`, `facebook`, `google`, `apollo`, `leads`, `people`, `employees`, `maps`, `producthunt`, `actor`, `research`, `queries` |
| `query_library.py` | Queries from your profile (LinkedIn boolean, X-ray, X, subreddits, HN, Maps, Apollo URLs, people filters) |
| `seller_profile.py` | `init`, `check` (what to ask), `questions`, `show`, `set` — your business, read by every skill |
| `prospect_scan.py` | Deep scan → `DOSSIER.json/.md` + pipeline (audit, company, people, email, web research, hooks) |
| `outreach.py` | `log`, `cadence`, `approve` / `queue` / `run` / `cancel` sequences, `send` (dry run → `--send`), `whatsapp` |
| `inbox.py` | `check [--apply] [--auto-reply]` — IMAP replies and bounces → pipeline |
| `autopilot.py` | `tick [--send]`, `schedule` |
| `reply_triage.py` | Classify a reply, extract times/phones/emails, `--apply` to update the pipeline |
| `meeting.py` | `slots` (both time zones), `book` (`.ics` invite), `list`, `outcome` |
| `intent_scan.py` | `--serp` (Bright Data X-ray queries, recency filter, `--max-calls` cap), `--file`, `--text`; dedupes across runs |
| `site_audit.py` | Fact-only homepage audit; robots.txt respected; `--save` |
| `find_email.py` | Post text → website → Prospeo / Findymail / Hunter / Apollo → MillionVerifier / ZeroBounce / NeverBounce / Hunter → labelled guesses; `--providers` |
| `claim_check.py` | Exit 1 if any factual sentence or `[PLACEHOLDER]` is unsupported by the evidence files |
| `fetch_page.py` / `web_search.py` | Web access for agents without web tools |
| `analyze_prospect.py` / `contact_finder.py` | Site scrape for company signals and team members |
| `lead_scorer.py` | BANT + MEDDIC, or `--mode agency` |
| `generate_pdf_report.py` | PDF pipeline report (`--demo` for a sample) |

Your data lives in `~/.ai-sales-team/` (override with `AI_SALES_HOME`): `pipeline.db`, `.env`, backups.
Per-prospect files go in `prospects/<domain>/` in your working folder.

## Safety and honesty (built in)

- No invented people, emails, connections, results or metrics. Unknown = "Not found".
- `claim_check.py` blocks unsupported numbers and quotes before a draft is shown.
- Guessed emails are always marked; only `verified` addresses are recommended for cold email.
- Compliance notes per country (CAN-SPAM, UK PECR, EU GDPR/ePrivacy, CASL, India DPDP) in every email skill.
- You approve every message. Email is sent only by you, or by `outreach.py send --send` after a dry run passes
  every gate (verified address, claim check, opt-out, postal address, daily limit, do-not-contact list).
- Skills never post, comment or DM on social platforms; WhatsApp is a click-to-chat link you open yourself.
- Opt-outs and bounces from replies are applied automatically and never contacted again.
- Hands-free sending only sends emails you approved, only after an inbox check, only inside `SEND_HOURS`,
  under `DAILY_SEND_LIMIT`; booking links wait until the prospect says yes.
- Apify/Bright Data collect public data only; every paid run is capped (`APIFY_MAX_USD`, `APIFY_MAX_RUNS`, `--max-calls`).
- robots.txt respected; paid API calls capped per run; keys never written to files or output.

## Development

```bash
pip install pytest reportlab skills-ref
python -m pytest tests                # scripts, end-to-end flow, installer, skill validation
python tools/validate_skills.py       # Agent Skills spec + portability checks (uses skills-ref if installed)
python tools/build_skills.py          # regenerate SKILL.md files from tools/skill_specs.py
python tools/build_skills.py --check  # CI: fail if a generated file was edited by hand
```

**Don't edit `skills/*/SKILL.md` or `references/compliance.md` by hand** — they are generated from
`tools/skill_specs.py` (and the shared blocks in `tools/build_skills.py`) and your edit would be overwritten.
All other `references/*.md` files are hand-written. CI (`.github/workflows/ci.yml`) runs all of the above on
Windows, macOS and Linux with Python 3.9 and 3.13.

Layout: `skills/<name>/SKILL.md` (+ `references/`), shared scripts in `skills/sales/scripts/`, optional
agent extras in `adapters/`, the installer in `install.py`.

## Credits

Original skill set, frameworks and PDF layout by [Zubair Trabzada](https://github.com/zubair-trabzada/ai-sales-team-claude) (MIT).
Intent phrase scoring adapted from [lead-signal-listener](https://github.com/yangyixxxx/lead-signal-listener) (MIT);
claim matching and bounce/reply ideas from [autonomous-sdr](https://github.com/RodricDib06/autonomous-sdr) (MIT).
See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). License: [MIT](LICENSE).
