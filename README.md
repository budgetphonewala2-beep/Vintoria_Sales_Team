<p align="center">
  <img src="banner.svg" alt="AI Sales Team" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/16_skills-Agent_Skills_spec-8b5cf6?style=for-the-badge" alt="16 skills">
  <img src="https://img.shields.io/badge/works_in-Claude_Code·Codex·Cursor·Gemini·OpenCode-0ea5e9?style=for-the-badge" alt="Agents">
  <img src="https://img.shields.io/badge/license-MIT-gray?style=for-the-badge" alt="MIT License">
</p>

# AI Sales Team — portable sales skills for any coding agent

Find people who are **asking** for what you sell, research and score them, find **verified** contacts, write
outreach that only states **checked facts**, prep meetings, write proposals, and keep a **persistent
pipeline** — from Claude Code, OpenAI Codex CLI, Cursor, Gemini CLI, OpenCode or any agent that supports the
open [Agent Skills](https://agentskills.io/specification) format.

Built for B2B sellers and especially for **agencies, freelancers and consultants** (web, app, SEO, marketing,
design) selling to SMBs in India, the US, UK and Australia. Posts and replies can be English, Hindi or Hinglish.

> v3 is a portable upgrade of [zubair-trabzada/ai-sales-team-claude](https://github.com/zubair-trabzada/ai-sales-team-claude)
> (MIT). See [AUDIT.md](AUDIT.md) for what was wrong with v1/v2 and [CHANGELOG.md](CHANGELOG.md) for what changed.

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
```

Without keys everything still works: your agent's own web tools (or `fetch_page.py`) do the research, and
emails are labelled `unverified` / `pattern-guessed` instead of `verified`.

## Skills

| Skill | Ask your agent... | Output |
|---|---|---|
| `sales` | "use the sales skill" — routes to the rest | — |
| `sales-icp` | "build my ideal customer profile: we build websites for clinics" | `IDEAL-CUSTOMER-PROFILE.md` |
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
| `sales-report` | "how is my pipeline, what should I do today" | `SALES-REPORT.md` |
| `sales-report-pdf` | "PDF of the pipeline" | `SALES-REPORT-<date>.pdf` |

In Claude Code you can also type `/sales <command> <input>`.

## A typical week

```
sales-icp       "We build websites + local SEO for clinics and restaurants in India, US and UK"
sales-hunt      → 14 candidates, 5 real buyers judged with exact quotes, added to the pipeline
sales-audit     sweetcrumbs.in → "no mobile viewport", "© 2019 footer", "no Book/Call button"
sales-contacts  sweetcrumbs.in → Anita Desai, Founder, anita@sweetcrumbs.in (verified via Hunter)
sales-outreach  sweetcrumbs.in → 96-word first email, claim check: 4/4 sentences supported
...you send it, then: pipeline.py stage sweetcrumbs.in contacted
sales-report    Monday review: funnel, stale deals, which hunt queries produced meetings
```

## Helper scripts (`skills/sales/scripts/`)

Every script prints one JSON object and is safe to run from any agent or by hand.

| Script | What it does |
|---|---|
| `pipeline.py` | `add`, `list`, `show`, `stage`, `score`, `note`, `contact`, `attach`, `next`, `report [--pdf-input]`, `remove` |
| `intent_scan.py` | `--serp` (Bright Data X-ray queries, recency filter, `--max-calls` cap), `--file`, `--text`; dedupes across runs |
| `site_audit.py` | Fact-only homepage audit; robots.txt respected; `--save` |
| `find_email.py` | Post text → website contact pages → Hunter finder → Hunter verifier → labelled guesses |
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
- Skills write drafts only. They never send email, post, comment or DM on social platforms.
- robots.txt respected; paid API calls capped per run; keys never written to files or output.

## Development

```bash
pip install pytest reportlab skills-ref
python -m pytest tests            # scripts, installer, skill validation
python tools/validate_skills.py   # Agent Skills spec + portability checks (uses skills-ref if installed)
python tools/build_skills.py      # regenerate SKILL.md files from tools/skill_specs.py
```

Layout: `skills/<name>/SKILL.md` (+ `references/`), shared scripts in `skills/sales/scripts/`, optional
agent extras in `adapters/`, the installer in `install.py`.

## Credits

Original skill set, frameworks and PDF layout by [Zubair Trabzada](https://github.com/zubair-trabzada/ai-sales-team-claude) (MIT).
Intent phrase scoring adapted from [lead-signal-listener](https://github.com/yangyixxxx/lead-signal-listener) (MIT);
claim matching and bounce/reply ideas from [autonomous-sdr](https://github.com/RodricDib06/autonomous-sdr) (MIT).
See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). License: [MIT](LICENSE).
