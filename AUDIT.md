# AUDIT — ai-sales-team-claude (upstream `efef8b8`) and what v3 did about it

Method: read every upstream file, ran all four scripts against synthetic HTML and live sites, generated PDFs
from both the demo data and the schema the skills document. Status column = state in v3.

## A. Structural problems

| # | Problem | Evidence | v3 status |
|---|---|---|---|
| 1 | No frontmatter in any SKILL.md | First line of all 14 files was a `# Heading` | **Fixed** — spec-only frontmatter; all 16 skills pass `skills-ref validate` |
| 2 | `agents/*.md` had no frontmatter, so the "5 parallel agents" never loaded; the strategy agent needs the other four's output but was launched with them | `sales-prospect` launched `general-purpose` agents pointed at other skill files | **Fixed** — role playbooks in `sales-prospect/references/role-*.md` run in sequence anywhere; strategy runs last; Claude subagents with proper frontmatter are an optional adapter |
| 3 | Skills ran `python3 scripts/...` from the user's CWD while the installer copied scripts elsewhere; `lead_scorer.py` and `contact_finder.py` were never used; `python3` is a Store stub on Windows | `sales-prospect:103`, `sales-report-pdf:201` | **Fixed** — scripts live inside the `sales` skill and are addressed relative to it; every script is used by a skill; `python` on Windows |
| 4 | SKILL.md bodies 321-851 lines, no progressive disclosure | `wc -l` | **Fixed** — 50-110 lines; details in `references/` |
| 5 | No discovery, email finding/verification, persistence; outputs were fixed-name files in the CWD (a second prospect overwrote the first; "if COMPANY-RESEARCH.md exists" reused another company's research) | — | **Fixed** — `sales-hunt`, `find_email.py`, SQLite `pipeline.py`, per-prospect folders |
| 6 | `lead_scorer.py` used US-SaaS signals (funding, headcount, C-suite count) — wrong for agencies selling services | — | **Fixed** — `--mode agency` buyer model; ICP-driven fit; SaaS defaults removed from roles |
| 7 | urllib with no retries, cache or concurrency; TLS verification **disabled** (`CERT_NONE`); `--timeout` ignored | — | **Fixed in 3.1** — v3.0 still retried page fetches with `CERT_NONE` after a certificate failure; 3.1 always verifies (certifi when available) and reports the page as unreachable instead. Parallel fetches, retries on 429/5xx for APIs, robots.txt respected |
| 8 | Claude-Code-only: `/sales` routing, Task tool, WebFetch/WebSearch, `~/.claude` paths | — | **Fixed** — no agent-specific tools in any skill (checked by `tools/validate_skills.py`); `fetch_page.py`/`web_search.py` for agents without web tools |

## B. Script bugs (each reproduced on upstream)

| # | Where | Bug | v3 status |
|---|---|---|---|
| 9 | `contact_finder.py` | Substring title matching: "Dire**cto**r" → CTO, "**Coo**rdinator" → COO, "Vice **President**" → C-suite | Fixed (word-boundary classifier; regression tests) |
| 10 | `contact_finder.py` | Any `linkedin.com/in/` URL within ±200 chars attached to a name | Fixed |
| 11 | `analyze_prospect.py` | Pricing tiers from a `set()` (random order) zipped with prices; "Pro" matched "Products" | Fixed |
| 12 | `analyze_prospect.py` | Tech detection by bare words (`striped-table.css` → Stripe) | Fixed |
| 13 | `analyze_prospect.py` | Emails regexed from raw HTML (`react@18.2.0`), any 10 digits = phone, "series a" in "series and" | Fixed |
| 14 | `analyze_prospect.py` | Any h2-h4 + p treated as a team member | Fixed |
| 15 | `analyze_prospect.py` | `/jobs` result overwrote `/careers` | Fixed |
| 16 | `generate_pdf_report.py` | Skill told the agent to write `action_items` as a list; script called `.get()` → crash on the documented flow | Fixed (accepts list or dict; tested from pipeline output) |
| 17 | Grades | README A+≥90/A≥75/B≥60/C≥40 vs script A≥75/B≥50/C≥25 | Fixed — one scale everywhere |
| 18 | `lead_scorer.py` | `"$10M"` → TypeError; empty MEDDIC gaps → "fill gaps in: ." | Fixed |
| 19 | `lead_scorer.py` | "Confidence" counted truthy fields only | Fixed (coverage-based) |
| 19b | `lead_scorer.py` (interim pass) | `stdin.lstrip("Feff")` stripped the letters F/e/f instead of the BOM | Fixed in v3 (regression test) |

## C. Honesty, safety, compliance

| # | Problem | v3 status |
|---|---|---|
| 20 | `sales-objections` told the model to "generate realistic placeholder examples" of customer results | Fixed — `[ADD REAL CUSTOMER RESULT]` markers; claim checker flags placeholders |
| 21 | Outreach "mutual connection" framework + "no placeholders" invited invented connections | Fixed — only user-confirmed connections |
| 22 | Pattern-guessed emails not labelled | Fixed — statuses `verified / catch_all / unverified / pattern-guessed / invalid` |
| 23 | One mention of CAN-SPAM; nothing on PECR, GDPR/ePrivacy, CASL, DPDP; no deliverability guidance | Fixed — `references/compliance.md` in every email-writing skill |
| 24 | Nothing checked that generated emails were true | Fixed — `claim_check.py` (numbers and quotes must match a single evidence source) |
| 24b | A TLS failure on the auditing machine could be reported as the prospect's "certificate problem" | Fixed — certificate state is never stated as a fact about the prospect |

## D. Design and maintainability

| # | Problem | v3 status |
|---|---|---|
| 25 | No ICP gate — fit scores silently fell back to "general B2B SaaS" | Fixed — ask once, or score against the stated offer |
| 26 | `templates/` installed but referenced by no skill | Fixed — each template moved into the skill that uses it |
| 27 | Duplicated, divergent rubrics between the prospect skill and agents | Fixed — one rubric per role file |
| 28 | Cost: dozens of uncapped fetches/searches per prospect | Improved — `--max-calls` cap on paid search, dedupe across runs |
| 29 | bash-only installer that swallowed `git clone` errors and needed `python3` | Fixed — `install.py` (Windows/macOS/Linux), backups, uninstall, dry run |
| 30 | No tests, versioning or changelog | Fixed — pytest suite, validator, CHANGELOG |

## E. Found in the v3.0 review (fixed in 3.1)

| # | Problem | v3.1 status |
|---|---|---|
| 31 | Unverified-TLS fallback in `fetch_url` contradicted #7 | Fixed — no fallback; `tls_error` flag |
| 32 | `site_audit.py` counted unreachable links (timeouts, local TLS issues) as broken | Fixed — only HTTP ≥ 400 counts |
| 33 | Generated SKILL.md files looked hand-editable | Fixed — "generated" notice, `build_skills.py --check` in CI |
| 34 | One-time `tools/split_skills.py` left in the repo | Removed |
| 35 | No CI; Python 3.9 support untested | Fixed — GitHub Actions on 3 OSes × Python 3.9/3.13; `vermin` clean for 3.9 |
| 36 | The flow stopped at the first email: no cadence, reply handling or booking | Fixed — `outreach.py`, `reply_triage.py`, `meeting.py`, `sales-reply`, `sales-book`, `sales-autopilot` |

## F. Found by the end-to-end test (fixed in 3.5)

| # | Problem | v3.5 status |
|---|---|---|
| 37 | Claim check counted the draft's own file as evidence when skills globbed `prospects/<slug>/*.md` | Fixed — drafts never evidence |
| 38 | Postal address in the signature failed the claim check | Fixed — seller identity is evidence |
| 39 | Hedged consequences blocked, contradicting the audit skill | Fixed — hedged = opinion, unhedged must be proven |
| 40 | Link bookings (Calendly/Cal.com) never reached the pipeline | Fixed — inbox detects them |
| 41 | Skill commands could drift from script flags | Fixed — validator checks every command |

## Known limits (honest)

- JavaScript-only sites return little HTML; the audit then reports only what the server sent.
- Social platforms are searched only through public Google results (Bright Data) or posts you paste —
  no logged-in scraping, by design.
- The skills don't read your inbox or calendar: paste replies (or save them to a file) for `sales-reply`, and the
  free-slot finder only knows meetings booked through `meeting.py`, so check your own calendar before confirming.
- Email is sent only through SMTP you configure: one approved message at a time, or an approved sequence that
  the scheduled autopilot sends (after an inbox check). There is no bulk blast.
- Hacker News (Algolia), Reddit JSON and Product Hunt GraphQL were implemented from their public API docs and tested
  with mocked responses; Reddit increasingly rate-limits unauthenticated requests, so the Apify actor is the
  dependable route. Product Hunt often redacts maker details; the product website is the lead.
- Apollo data comes through third-party Apify actors; their input fields (`url`, `totalRecords`, Leads Finder filter
  names) were taken from the actors' public pages and may change — override the actor with `APIFY_*_ACTOR` or pass
  your own `--input`. Scraping Apollo may conflict with Apollo's terms; that is between you and Apollo. Database
  emails are saved as `unverified` unless `--verify` passes.
- Apify actor inputs/outputs are set by each actor's publisher and can change; the defaults were checked against
  the actors' public docs (2026-11) and outputs are read defensively, but run a small test (`--max 5`) after
  switching actors. Provider APIs (Prospeo, Findymail, Apollo, verifiers) were implemented from their public docs
  and tested with mocked responses only.

## E. v4 review (2026-11-17) — what was still wrong in v3.10, and the fix

| # | Problem | Fix |
|---|---|---|
| 31 | 20 overlapping skills (`sales-research`, `-contacts`, `-qualify`, `-competitors`, `-audit`, `-prospect` all researched one prospect) — agents had to pick between near-duplicates | Merged into 8 skills, one per job, with modes inside |
| 32 | Two competing skill sets: the engine-backed `sales-*` and an instruction-only `vintoria-*` set with its own CSV pipeline and workspace layout | One set on the engine; the Vintoria catalog, pricing policy, quality bar and closing playbooks merged in |
| 33 | 27 scripts in one flat folder | Grouped into core / leads / research / outreach / replies / ops |
| 34 | The engine could not target India (no `IN` market) although Vintoria sells to Indian SMBs | `IN` added with Google country, time zone and cities; Vintoria preset targets IN, US, UK, AU |
| 35 | No way to hunt AI or automation buyers specifically (only a broad `software` code) | `ai` and `automation` codes with their own queries |
| 36 | 38 tests errored: an eval fixture was swallowed by `.gitignore` | Fixture rebuilt and un-ignored; CI green again |
| 37 | Upgrading left the old skills installed next to the new ones (duplicate triggers) | Installer retires legacy skills/subagents into a backup |
| 38 | Skills could name services loosely ("AI chatbot") or quote a price | Catalog IDs only (tested); pricing policy: profile prices or `[PRICE TO CONFIRM]` |
