# Changelog

## 3.9.0 — 2026-11-02 (hallucination guards)

### Added
- `references/truth-rules.md`: what counts as evidence (script output, saved pages, the prospect's words, the seller
  profile) and the guard for every place an agent could invent something.
- `claim_check.py`: every declarative sentence is checked; source tiers (tool / page / prospect / profile / guarantee /
  calendar / snippet); names, brands and places must be in the evidence; numbers must come from one source; quotes
  verbatim; negation flips caught; generalisations and promises need strong / guarantee support; a search snippet alone
  never proves a claim; every clause of a sentence needs evidence (no invented tail on a true sentence); opinions
  about the prospect are claims; agent-written research docs are never evidence; replies, holidays and proposed slots are.
- `fetch_page.py --save DIR`: saves opened pages (with URL and fetch time) as evidence.
- `pipeline.py add --quote --post-text/--post-file`: refuses a quote that isn't word-for-word in the post.
- `find_email.py` logs every verification; `pipeline.py contact --email-status verified` is downgraded without one.
- `outreach.py` blocks a greeting whose name doesn't match the contact on file.
- `lead_sources.py research` only turns results that name the prospect into facts.
- `tests/test_hallucination_guards.py`: adversarial sentences that must be blocked and true ones that must pass.

## 3.8.0 — 2026-11-02 (learning loop, A/B, mailbox rotation, alerts, PageSpeed)

### Added
- `learn.py report [--apply]` / `learn.py ab`: rates by source, query, platform, hook, subject variant, reply step,
  quality score and country; recommendations; `learned.json` query weights and drops used by `serp.py`.
- Subject A/B: `subject_b` and `hook` fields in SEQUENCE.json; variant, hook and quality score stored per sequence step.
- `mailboxes.py` + `mailboxes.json`: rotation across inboxes, sticky sender per prospect, per-mailbox limits and
  warm-up, IMAP read from every inbox; single-inbox `.env` setup still works unchanged.
- `notify.py`: Telegram / Slack / Discord alerts; autopilot pings for fresh leads, replies and bookings (`ALERT_ON`).
- Google PageSpeed Insights facts (`site_audit.py --pagespeed`, on by default in `prospect_scan.py`) and hooks.

### Fixed
- `prospect_scan.py` no longer marks an unreachable site as `researched`.
- `learn.py` counts a meeting only when one was booked, not when a reply asked for one.

## 3.7.0 — 2026-11-02 (Bright Data freshness + lessons from other sales skill sets)

### Added
- `serp.py watch` / `fresh` / `judged`: newest buyer posts since the last run (1-24 h, `qdr:hN`, sorted by date), exact
  post times from LinkedIn activity IDs and X status IDs (else parsed from the snippet), never-seen-only, queued at the
  top of `pipeline.py today`; autopilot runs it every `HUNT_EVERY_HOURS` (default 2, `HUNT_MAX_QUERIES` per run).
- `email_lint.py`: deterministic 0-100 reply-worthiness score (situation, value, you-ratio, CTA, length by step,
  subject, AI tells/jargon) with exact fixes; `approve --check` enforces `LINT_MIN_SCORE` (default 65).
- Deliverability stop-loss (`BOUNCE_STOP_PCT`, default 2 % over 14 days; reply-rate warning after 300 sends) and an
  over-contact limit (`MAX_TOUCHES_PER_WEEK`, default 4).
- Reply categories `how_got_email`, `send_info`, `wrong_person`; out-of-office return dates move queued emails.
- `pipeline.py status` — one call for setup, keys, funnel, queue, sending health, fresh leads and the next action.
- `skills/sales-outreach/references/quality.md` (score, banned phrases, 4 personalization levels, deletion test, panel review).
- THIRD_PARTY_NOTICES: marketingskills (MIT) and gtm-agents (Apache-2.0).

### Changed
- SERP is Bright Data only by default (`SERP_PROVIDERS=brightdata`; others only if listed).
- Warm-up ramp: 5/day for weeks 1-2, then +5 per week. Booking proposes 2 slots + link; the day-before confirmation
  carries a pre-read; a second no-show moves the deal to nurture.

## 3.6.0 — 2026-11-02 (skill-creator review: evals, SERP first, bug fixes)

### Fixed
- Leads from post URLs (LinkedIn, Reddit, X, HN, Facebook, Upwork ...) no longer merge into one "linkedin.com" prospect:
  the slug is `name@platform` (e.g. `anita-desai@linkedin`, `post-abc123@reddit`); `prospect_scan.py` refuses platform URLs.
- `lead_scorer.py --mode agency`: unknown post age / comment count score neutral (were treated as "today, 0 comments").
- `prospect_scan.py` no longer overwrites a prospect's real name with its slug.

### Added
- `serp.py` — SERP lead engine: the profile's Google X-ray queries via Serper (cheapest), SerpAPI, Bright Data, Brave or
  Apify, with recency, pages and country rotation; now the first row of the hunt playbook. `lead_sources.google`
  (research, X-ray) uses a cheap SERP provider before Apify.
- `outreach.py doctor` (delivery mode) and `outreach.py approve --check` (validate a sequence, queue nothing).
- `pipeline.py find <email|name|domain>`.
- Skill-creator eval cases in `skills/sales-outreach|sales-reply|sales-hunt/evals/`; the installer skips `evals/`.

### Changed
- Shared skill blocks rewritten: shorter, explain why; the seller profile is required only where queries, emails or
  prices are built from it; one delivery section driven by `outreach.py doctor`.
- `sales-hunt` step 2 is a "keys → command" table with a cost ceiling before paid runs; LinkedIn contact field takes the
  author's profile URL; unknown score inputs are left out.
- `sales-reply` drafts stay under ~100 words with at most one `[TO CONFIRM]`; the prospect is found by sender and its time zone used.
- `sales-report` no longer competes with `sales-autopilot` for "what should I do today".

## 3.5.0 — 2026-11-01 (end-to-end tested, team mode)

### Fixed
- `claim_check.py`: drafts (OUTREACH-SEQUENCE, FOLLOWUP-SEQUENCE, CLIENT-PROPOSAL, SEQUENCE, MEETING-PREP, *DRAFT*,
  *EMAIL*, the draft itself) are never used as evidence — a glob over `prospects/<slug>/*.md` used to let a draft
  prove itself. Seller identity (signature, address) and real proof from the profile are evidence; hedged
  consequences ("so … may …") are treated as opinion.
- Bookings made through a booking link were not detected; `inbox.py` now records them from Calendly, Cal.com,
  SavvyCal, TidyCal, HubSpot, Zoom Scheduler, YouCanBook.me notifications and from calendar invites (ICS, with TZID).

### Added
- `claim_check.py --prospect <slug>` (auto evidence) and `--no-profile`; `outreach.py` preflight uses it.
- `pipeline.py value <slug> <amount> --currency`, weighted `forecast` in `report` (stage odds).
- Warm-up ramp: `SENDING_STARTED` (10/day in week 1, +5/week, up to `DAILY_SEND_LIMIT`).
- `lead_sources.py apollo-api` — Apollo's official people search with `APOLLO_API_KEY`.
- Agenda: exact next step per lead (deep scan → verify email → write and approve the sequence).
- Seller profile is the fallback for SENDER_NAME, SENDER_EMAIL, SENDER_ADDRESS, BOOKING_URL, MEETING_LINK, TIMEZONE.
- Team mode: `skills/sales/references/team.md` (roles, handoffs, rhythm, targets) and Claude Code subagents
  `sales-hunter`, `sales-researcher`, `sales-writer`, `sales-closer`.
- `tools/validate_skills.py` checks every script command, subcommand and flag written in the skills.
- Tests: `tests/test_full_flow.py` (whole loop + each fix) — 111 tests in total.

## 3.4.0 — 2026-11-01 (seller profile first, international clients, Apollo + people databases)

### Added
- `sales-setup` skill + `seller_profile.py` (`init`, `check`, `questions`, `show`, `set`): a 3-round intake saved
  to `SELLER-PROFILE.json`; the shared "Before you start" block now makes every skill check it first.
- Profile-driven queries (`query_library.from_profile` / `auto`): niche × service, pain, trigger, switching,
  platform and outcome queries (LinkedIn ≤ 5 operators, `NOT India` when excluded), niche X-ray, niche subreddits,
  Maps searches in target cities, Apollo people-search URLs, LinkedIn people filters, Leads Finder filters.
- People databases in `lead_sources.py`: `apollo` (code_crafter/apollo-scraper), `leads` (code_crafter/leads-finder),
  `people` (harvestapi/linkedin-profile-search), `employees` (harvestapi/linkedin-company-employees); `--add --verify`.
- `find_email.py --email` / `verify_only()` — verify a known address without finder credits.
- Excluded markets: leads (posts and people) mentioning an excluded country, its cities or currency are dropped.
- `pipeline.py where <slug> --country --tz`; prospects get a country from their domain (.co.uk, .com.au, .ca ...).
- Compliance notes for Australia (Spam Act 2003) and New Zealand (UEMA 2007).
- Tests: `tests/test_profile_people.py`.

### Changed
- International, English-only defaults: Hinglish queries off (opt in with `languages: ["hinglish"]`), default
  X-ray queries replaced with r/forhire / small-business ones, directories without India-only sites, US/UK
  spelling and currency guidance in outreach, proposals in $/£/C$/A$/€, offshore-agency objections.
- Queued emails send at 09:00-17:00 on weekdays in the **prospect's** time zone (`SEND_HOURS`, `PROSPECT_DEFAULT_TZ`),
  and due dates use the prospect's calendar.

## 3.3.0 — 2026-11-01 (all lead sources, query library, deep scans, skill review)

### Added
- `query_library.py` — buyer queries for 8 services (web, app, seo, marketing, design, software, ecommerce, video):
  LinkedIn boolean (validated: ≤ 5 AND/OR/NOT, ≤ 500 chars, NOT last), Google X-ray per platform with seller
  exclusions, X search, subreddit plan (r/forhire `flair:Hiring` ...), Hacker News asks, Google Maps categories,
  Hinglish, location-aware.
- `lead_sources.py`: `hackernews` (Algolia API, free; asks + the monthly "Freelancer? Seeking freelancer?" thread),
  `reddit` free public-JSON fallback, `x` (Apify tweet scraper), `facebook` (public groups), `maps` (Google Maps
  businesses with need signals, `--add` to pipeline), `producthunt` (GraphQL, launches), `hunt` runs them all.
- `prospect_scan.py` — deep scan per prospect → `DOSSIER.json` (claim-check evidence) + `DOSSIER.md` with ranked
  hooks; records prospect, decision maker, best email and files in the pipeline.
- Research covers complaints, founder, ads and competitors too.
- Intent phrases for freelance/agency asks (`seeking freelancer`, `[hiring]`, `rfp`, `who built your website` ...)
  and seller phrases (`[for hire]`, `seeking work` ...); `platform_of` knows HN, Product Hunt, Indie Hackers, Upwork, Maps.
- Tests: `tests/test_sources_v33.py`.

### Changed
- `find_email.py` spends no finder credits when the address is already in the post, or (for the named person) on
  their website — it is only verified (`finders_skipped` says why).
- `intent_scan.py` candidates carry `contact_in_post` (emails/phones/sites written in the post) and author details.
- All 19 skills reviewed and upgraded (dossier-first, channel by source, sequence content plan, qualification red
  flags, proposal terms, local competitor hooks via Maps, ICP hunt settings, objection ↔ reply categories).
- Outreach references aligned to the day 0/3/7/14/28 cadence.

## 3.2.0 — 2026-11-01 (hands-free: Apify sources, email waterfall, self-sending sequences, inbox)

### Added
- `lead_sources.py` — Apify actors: LinkedIn post search (`harvestapi/linkedin-post-search`), Google
  (`apify/google-search-scraper`, Bright Data fallback), Reddit (`trudax/reddit-scraper-lite`), any actor;
  results normalized and intent-scored; `research <domain>` saves `WEB-RESEARCH.json` evidence. Actor IDs and
  spend caps are settings (`APIFY_*`).
- `find_email.py` provider waterfall: Prospeo, Findymail, Hunter, Apollo finders; MillionVerifier, ZeroBounce,
  NeverBounce, Hunter verifiers; failing providers are skipped; name patterns are verified when nothing is found;
  `--providers`, `--no-api`.
- `outreach.py approve / queue / run / cancel` — approve a whole sequence once; due emails send themselves,
  threaded as replies, inside `SEND_HOURS`, and stop on reply, opt-out, bounce, stage change or suppression.
- `inbox.py` — read-only IMAP reply/bounce detection (thread → contact → domain matching), optional instant
  booking-link reply (`AUTO_REPLY`, `AUTO_REPLY_CATEGORIES`).
- `autopilot.py tick / schedule` — inbox → due emails → agenda, with a lock; refuses to send without an inbox check.
- Tests: `tests/test_sources_inbox.py`.

### Changed
- Default cadence is now **day 3, 7, 14, 28 after email 1** (calendar days, weekend → Monday). `CADENCE_DAYS`
  now lists offsets from email 1 (it was gaps between emails in business days).
- Booking links (BOOKING_URL, Calendly, Cal.com, ...) are refused until the prospect has replied with interest.
- Replying to a prospect is no longer blocked by the "emailed in the last 2 days" rule.
- Skills `sales-hunt`, `sales-contacts`, `sales-research`, `sales-outreach`, `sales-followup`, `sales-reply`,
  `sales-book`, `sales-autopilot` and the router use the new scripts.

## 3.1.0 — 2026-11-01 (end to end: find → contact → follow up → reply → book)

### Added
- `sales-autopilot` — daily driver: builds today's agenda from the pipeline and works through it end to end.
- `sales-reply` — classify and answer replies; pipeline updated automatically.
- `sales-book` — slots in both time zones, `.ics` invites, prep/reminder scheduling, meeting outcomes.
- `outreach.py` — touch log, business-day follow-up cadence (`CADENCE_DAYS`), optional SMTP sending behind
  gates (verified address, claim check, opt-out, postal address, daily limit, do-not-contact list, dry run
  first, plain text, `List-Unsubscribe`), WhatsApp click-to-chat links.
- `reply_triage.py` — 12 reply categories in English, Hindi and Hinglish; stops follow-ups, suppresses
  opt-outs, marks bounced addresses invalid, never moves a deal backwards.
- `meeting.py` — free-slot finder that respects both parties' hours (stretches only your day for India ↔ US),
  RFC 5545 invites, clash detection, outcomes (held / no-show / rescheduled / cancelled).
- `pipeline.py today`, `suppress`, `suppressed`; `report` now includes activity (touches, meetings booked).
- `examples/env.example`, GitHub Actions CI, `tools/build_skills.py --check`, `tests/test_end_to_end.py`.

### Changed
- Email-writing skills: approve-then-send/log flow replaces "drafts only"; compliance notes cover WhatsApp,
  sending volume and automatic opt-outs.
- `sales-outreach`, `sales-followup`, `sales-prep`, `sales-report` and the router use the new scripts.
- Generated files carry a "do not edit" notice; author metadata updated.

### Fixed
- `fetch_url` no longer retries without TLS verification when a certificate fails (AUDIT #7 was only partly fixed).
- `site_audit.py` no longer counts links that got no HTTP answer (timeout/TLS on the auditing machine) as broken.

### Removed
- `tools/split_skills.py` (one-time v2 → v3 migration helper).

## 3.0.0 — 2026-11-01 (portable upgrade)

### Added
- **Portable Agent Skills**: spec-only frontmatter (name, description, license, compatibility, metadata); all
  16 skills validated with `skills-ref`; English + Hinglish trigger phrases.
- `sales-hunt` — find public posts asking for your service (EN/HI/Hinglish), judge with a 30-example rubric.
- `sales-audit` — fact-only website audit with evidence, and a fact-to-hook guide.
- Scripts: `pipeline.py` (SQLite pipeline), `intent_scan.py` (Bright Data SERP + phrase scoring),
  `site_audit.py`, `find_email.py` (Hunter finder/verifier), `claim_check.py`, `fetch_page.py`, `web_search.py`.
- `lead_scorer.py --mode agency` buyer model.
- Role playbooks for `sales-prospect` (`references/role-*.md`), runnable in any agent.
- `install.py` (Windows/macOS/Linux; claude-code, codex, cursor, gemini, opencode, shared `~/.agents/skills`),
  with backups, `--link`, `--uninstall`, `--dry-run`.
- `references/compliance.md` and a first-email style guide with 10 good/bad examples.
- Tests (`tests/`), `tools/validate_skills.py`, `tools/build_skills.py`, `AUDIT.md`.

### Changed
- SKILL.md bodies cut from 320-850 lines to 50-110; playbooks, output formats and templates moved to `references/`.
- Claude Code subagents moved to `adapters/claude-code/agents/` (optional parallelism).
- TLS verification uses certifi when available; certificate errors are never reported as prospect facts.
- `install.sh` / `uninstall.sh` are thin wrappers around `install.py`.

### Fixed
- `lead_scorer.py` stdin BOM handling (`lstrip("Feff")` stripped letters, not the BOM).
- Plus the interim fixes listed in AUDIT.md (title classifier, pricing tiers, tech detection, PDF crash, grades).

## 2.x — interim fix pass (local)
Frontmatter, per-prospect folders, script bug fixes, compliance notes.

## 1.0 — upstream
Original release by Zubair Trabzada.
