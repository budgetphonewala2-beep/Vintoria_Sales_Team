"""Specs for every skill. Edit here, then run tools/build_skills.py."""

PIPE = "python <SCRIPTS>/pipeline.py"
OUT = "python <SCRIPTS>/outreach.py"
MEET = "python <SCRIPTS>/meeting.py"
TRIAGE = "python <SCRIPTS>/reply_triage.py"
SRC = "python <SCRIPTS>/lead_sources.py"
AUTO = "python <SCRIPTS>/autopilot.py"
INBOX = "python <SCRIPTS>/inbox.py"
SCAN = "python <SCRIPTS>/prospect_scan.py"
QL = "python <SCRIPTS>/query_library.py"
PROF = "python <SCRIPTS>/seller_profile.py"

SKILLS = [
# --------------------------------------------------------------------------- router
{
"name": "sales",
"title": "AI Sales Team — Router",
"description": "AI sales team for B2B prospecting and agency client hunting: find people publicly asking for a service, research and score prospects, find and verify decision makers, write compliant cold emails and follow-ups, prep meetings, write proposals, handle objections, handle replies, book meetings with calendar invites, run the whole loop end-to-end every day, track a persistent pipeline and produce reports/PDFs. Use when the user says 'sales', '/sales <command>', 'find me leads', 'prospect this company', 'write a cold email', 'book a meeting', 'what should I do today', 'pipeline report', or in Hinglish 'clients dhundo', 'leads chahiye', 'is company ko email likho', 'meeting book karo', 'aaj ka kaam batao'.",
"intro": """You coordinate a team of sales skills. Work out what the user needs, then follow the matching skill.
Every skill works in any agent: they use shell commands (`python <SCRIPTS>/...`), files and your reasoning.""",
"body": """## Which skill to use

| The user wants... | Skill | Main output |
|---|---|---|
| **First run / new user** — who you are, what you sell, who to target (**always first**) | `sales-setup` | `SELLER-PROFILE.json` |
| The whole job, every day: find → contact → follow up → book (**daily driver**) | `sales-autopilot` | today's agenda, done step by step |
| To define who to sell to (**start here**) | `sales-icp` | `IDEAL-CUSTOMER-PROFILE.md` |
| People publicly asking for what they sell (intent leads) | `sales-hunt` | scored candidates → pipeline |
| Everything about one prospect in one run (site, people, email, web) | deep scan: `prospect_scan.py` | `prospects/<slug>/DOSSIER.json` + `.md` |
| A full scored audit of one company | `sales-prospect` | `prospects/<slug>/PROSPECT-ANALYSIS.md` |
| A fast 60-second estimate | quick snapshot (below) | terminal only |
| Fact-only website audit (proof-of-work for outreach) | `sales-audit` | `prospects/<slug>/SITE-AUDIT.json` + `.md` |
| Company research / firmographics | `sales-research` | `COMPANY-RESEARCH.md` |
| BANT + MEDDIC qualification | `sales-qualify` | `LEAD-QUALIFICATION.md` |
| Decision makers + verified emails | `sales-contacts` | `DECISION-MAKERS.md` |
| What they use today + battle cards | `sales-competitors` | `COMPETITIVE-INTEL.md` |
| Cold email + LinkedIn sequence | `sales-outreach` | `OUTREACH-SEQUENCE.md` |
| Follow-ups after a meeting/demo/proposal/silence | `sales-followup` | `FOLLOWUP-SEQUENCE.md` |
| A prospect replied — what now? | `sales-reply` | classified reply + drafted answer |
| Book a meeting (slots in both time zones, calendar invite) | `sales-book` | `prospects/<slug>/MEETING-<date>.ics` |
| Meeting preparation brief | `sales-prep` | `MEETING-PREP.md` |
| Client proposal with pricing options | `sales-proposal` | `CLIENT-PROPOSAL.md` |
| Objection handling scripts | `sales-objections` | `OBJECTION-PLAYBOOK.md` |
| Pipeline report | `sales-report` | `SALES-REPORT.md` |
| Pipeline report as PDF | `sales-report-pdf` | `SALES-REPORT-<date>.pdf` |

If your agent supports slash commands, `/sales <command> <input>` maps to `sales-<command>`. If the request is
unclear, show this table and suggest `sales-icp` first. To use a skill, read its `SKILL.md` (a sibling folder of
this one) and follow it; its instructions take precedence over this router.

## The end-to-end flow

```
sales-setup → sales-icp → sales-hunt (lead_sources) → prospect_scan (dossier) → sales-outreach (approve 5 emails)
   → autopilot sends day 0/3/7/14/28 → inbox.py reply → sales-reply → sales-book → sales-prep → sales-proposal
```
Default for any new prospect: run the deep scan first (`python <SCRIPTS>/prospect_scan.py <url> [--post-text "..."]`),
then write from `DOSSIER.md`. Its `facts` are claim-check evidence.

## Working as a team

One agent can run every step; several agents can split the work by role — Manager, Hunter, Researcher, Writer,
Closer — sharing the profile, the pipeline and `prospects/`. Handoffs are pipeline stages and next actions.
Read `references/team.md` for the roles, daily rhythm, targets and rules.

## Quick snapshot (no files)

1. Fetch the homepage (and `/pricing` or `/about` only if the homepage is thin).
2. Assess: what they do, size signals, fit against `IDEAL-CUSTOMER-PROFILE.md`, visible needs, decision-maker
   visibility. Optionally `python <SCRIPTS>/analyze_prospect.py --url <url>`.
3. Output under 30 lines: estimated score + grade, top 3 opportunities, top 3 concerns, the one skill to run next.
4. Say it is a quick estimate from 1-2 pages.

## One grade scale everywhere

| Score | Grade | Meaning |
|---|---|---|
| 90-100 | A+ | Hot — act today |
| 75-89 | A | Strong — worth real effort |
| 60-74 | B | Qualified — standard approach |
| 40-59 | C | Lukewarm — nurture |
| 0-39 | D | Poor fit — deprioritise |

## Helper scripts (`<SCRIPTS>` = this skill's `scripts/` folder)

| Script | Purpose |
|---|---|
| `pipeline.py` | Persistent pipeline: add, score, stage, contact, note, attach, next, report (+ forecast), `today`, `value`, `where`, suppress |
| `lead_sources.py` | Intent: LinkedIn posts, Hacker News, Reddit, X, Facebook groups, Google X-ray · People: Apollo, Leads Finder, LinkedIn people/employees · Companies: Google Maps, Product Hunt · any Apify actor · `research` |
| `query_library.py` | The search queries per service/platform/location (LinkedIn boolean ≤ 5 operators, X-ray, subreddits, Maps) |
| `prospect_scan.py` | Deep scan → `DOSSIER.json/.md`: audit + company + people + email (skipped if already known) + web research + ranked hooks |
| `outreach.py` | Log touches, approve whole sequences, `run` due follow-ups (day 3/7/14/28), safe SMTP send, WhatsApp links |
| `inbox.py` | Read replies/bounces over IMAP (read-only) → pipeline; optional instant booking-link reply |
| `autopilot.py` | `tick`: inbox → due sequence emails → today's agenda (schedule it every 30 min) |
| `seller_profile.py` | Your profile (`init`, `check`, `questions`, `show`, `set`) — every query and email is built from it |
| `reply_triage.py` | Classify a reply → stage, next step, stop follow-ups, opt-outs |
| `meeting.py` | Free slots in both time zones, `.ics` invites, meeting list and outcomes |
| `intent_scan.py` | Score posts asking for a service; rejects sellers, job ads, job seekers |
| `site_audit.py` | Fact-only website audit (each fact with evidence) |
| `find_email.py` | Email waterfall: site → Prospeo / Findymail / Hunter / Apollo → MillionVerifier / ZeroBounce / NeverBounce / Hunter |
| `claim_check.py` | Flags sentences in a draft that no evidence supports |
| `fetch_page.py` / `web_search.py` | Web access for agents without web tools |
| `analyze_prospect.py` | Site scrape → industry, tech, hiring, team, pricing, size signals |
| `contact_finder.py` | Team/leadership extraction with seniority and buying role |
| `lead_scorer.py` | Deterministic BANT/MEDDIC score, or `--mode agency` buyer score |
| `generate_pdf_report.py` | PDF pipeline report (needs `pip install reportlab`) |

API keys (all optional) go in environment variables or `~/.ai-sales-team/.env`, never in files you write:
`APIFY_TOKEN`, `BRIGHTDATA_API_KEY`, `HUNTER_API_KEY`, `PROSPEO_API_KEY`, `FINDYMAIL_API_KEY`, `APOLLO_API_KEY`,
`MILLIONVERIFIER_API_KEY`, `ZEROBOUNCE_API_KEY`, `NEVERBOUNCE_API_KEY`, `SMTP_PASSWORD`, `IMAP_PASSWORD`.
Settings in the same file: `SENDER_NAME`, `SENDER_EMAIL`, `SENDER_ADDRESS`, `SMTP_HOST`, `SMTP_PORT`, `TIMEZONE`,
`WORK_HOURS`, `SEND_HOURS`, `BOOKING_URL`, `MEETING_LINK`, `DAILY_SEND_LIMIT`, `CADENCE_DAYS`, `AUTO_SEND`, `AUTO_REPLY`.
The template is `examples/env.example` in the repository.

## Typical week

```
sales-setup        interview → SELLER-PROFILE.json (services, niches, countries, deal size, proof, buyer titles)
sales-icp          ICP + the sharpest queries for that profile
sales-hunt         find people asking for that this week → judge → pipeline
sales-prospect     https://bestlead.com          (deep audit of the best ones)
sales-audit        https://bestlead.com          (proof-of-work facts)
sales-outreach     bestlead.com                  (claim-checked first email + sequence)
sales-reply        they answered → classify, reply, stop follow-ups
sales-book         slots in both time zones → .ics invite → meeting in the pipeline
sales-prep / sales-proposal / sales-followup      as deals move
sales-autopilot    every morning: "aaj ka kaam" — runs the whole loop from today's agenda
sales-report       weekly pipeline review
```
""",
"before": True,
"refs": [("team.md", "running the skills as a sales team: roles, handoffs, daily rhythm, targets, rules")],
},
# --------------------------------------------------------------------------- hunt
{
"name": "sales-hunt",
"title": "Intent Hunt — find people asking for what you sell",
"description": "Finds people publicly asking to hire a service the user sells (website, app, SEO, marketing, design, software, e-commerce, video) on LinkedIn posts (Apify HarvestAPI), Hacker News (incl. the Seeking-freelancer thread), Reddit (r/forhire and more), X, Facebook groups, Quora, Indie Hackers and Upwork via Google X-ray, plus companies with a visible need from Google Maps and Product Hunt — using a query library with strong boolean queries — plus decision-maker lists from Apollo, Leads Finder and LinkedIn people search — all built from the seller profile (niches, countries, buyer titles) — filters sellers, job seekers, job ads and excluded markets, judges real buyers, deep-scans the best and adds them to the pipeline. Use when the user says 'find leads', 'find people looking for a web developer', 'who needs an agency', 'hunt for clients', or in Hinglish 'clients dhundo', 'leads chahiye', 'kaun website banwana chahta hai', 'developer chahiye wale posts dhundo'.",
"intro": """Intent beats cold lists: a person who wrote "need a website for my clinic" this week is worth fifty
cold contacts. This skill finds those posts, separates real buyers from noise, and puts them in the pipeline.""",
"body": f"""## Steps

1. **Know the seller.** `{PROF} check` — if the profile is missing or incomplete, run `sales-setup` first. The
   queries are generated from it (niches, platforms, pains, triggers, tools clients leave, buyer titles,
   countries, excluded markets): preview them with `{QL}`. Read `references/queries.md` for the formula.
2. **Collect posts** — any of these (best first):
   - Everything at once: `{SRC} hunt --posted week --max 30 --save hunt.json` (profile-driven; leads from excluded
     markets are dropped and counted in `excluded_market`)
     (Hacker News free; LinkedIn, Reddit, X, Google X-ray with `APIFY_TOKEN`). Or one source:
     `{SRC} linkedin` · `{SRC} hackernews` (incl. the monthly "Seeking freelancer" thread) · `{SRC} reddit`
     (r/forhire [Hiring] and more; free JSON without Apify) · `{SRC} x` · `{SRC} facebook --group-url <public group>`
     · `{SRC} google` — each uses the profile, or `--services/--location`, or your own `--query` (repeatable).
   - **People databases** (decision makers matching the profile — lists, no intent). Best: Apollo's official
     API — `{SRC} apollo-api` with your `APOLLO_API_KEY`, or your agent's Apollo connector if it has one (search
     people with the profile's titles, countries, size and niches, then reveal emails per person). Otherwise
     `{SRC} apollo` (Apollo search
     URLs built from the profile, or `--url` from your Apollo account), `{SRC} leads` (Apollo-style filters, no
     account), `{SRC} people` (LinkedIn profile search), `{SRC} employees --company <LinkedIn company URL>`.
     Add `--add --verify` to save them with verified emails. These need a stronger first line — deep-scan first.
   - Companies with a visible need (outbound): `{SRC} maps --add` (cities from the profile; no website,
     social-only page, low rating, few reviews + phone) and `{SRC} producthunt --days 7 --add` (new launches).
   - Any other Apify actor: `{SRC} actor <user/actor> --input in.json`.
     Spend is capped by `APIFY_MAX_USD` (default $1/run) and `APIFY_MAX_RUNS`; tell the user what ran and the counts
     (`sources_run`, `by_source`, `kept_by_source`).
   - With a Bright Data key: `python <SCRIPTS>/intent_scan.py --serp --lookback 7 --max-calls 10 [--country in] --save hunt.json`
     (`--list-queries` shows the default X-ray queries; add your own with `--query '...'`, repeatable).
   - Without a key: search yourself (your web tool, or ask the user to paste posts) for queries like those in
     `references/queries.md`, save posts one per line or as JSON lines (`url`, `text`, `author`) and run
     `python <SCRIPTS>/intent_scan.py --file posts.jsonl --save hunt.json`.
   - One post: `python <SCRIPTS>/intent_scan.py --text "..."`.
   The scanner skips posts seen in earlier runs and rejects sellers, job seekers and job ads for free.
   LinkedIn results include the author's name, headline and profile URL — keep them for step 6. A candidate with
   `contact_in_post` already has an email/phone from the post: use it, don't pay a finder for it.
3. **Judge every candidate** with `references/intent-rubric.md`. For each, decide: buyer / seller /
   job_seeker / other, services wanted, urgency, budget (only if stated), location/timezone (only if stated
   or obvious), and an **exact quote** from the post that proves intent. Discard anything below confidence 0.6.
4. **Score buyers**: write their signals to a JSON file and run
   `python <SCRIPTS>/lead_scorer.py --mode agency signals.json` (fields: `intent_confidence`, `urgency`,
   `posted_days_ago`, `comments`, `budget_stated`, `services_requested`, `services_offered`, `email_status`,
   `sources_count`).
5. **Add to the pipeline** (one per buyer):
   `{PIPE} add --url <their site or post URL> --name "<name/company>" --source hunt:<query-id> --services web,seo`
   `{PIPE} score <slug> <score>` · `{PIPE} note <slug> "Post: <url> — quote: '<exact quote>'"`
6. **Deep-scan the top buyers** (best 5-10, freshest first):
   `{SCAN} <their site or domain> --post-text "<post>" --post-url <url> [--first X --last Y] --source hunt:<query-id>`
   → `prospects/<slug>/DOSSIER.md` with the audit, people, the best email (finders skipped when the post or site
   already has one), web research and ranked hooks; the prospect and contact go into the pipeline. No website?
   `python <SCRIPTS>/find_email.py --text "<post text>"` and record with `{PIPE} contact ...`.
   No verified email? Suggest the user reply publicly under the post or DM from their own account — give
   them a 2-line message. Never post or DM on their behalf.
7. **Report**: a table — buyer, platform, what they need, exact quote, posted, score, contact status, next step.
   Respond to fresh asks (under 48 h) the same day: an email if there is a verified address, otherwise a
   2-line public reply or DM for the user to post from their own account.

## Rules
- The quote must be copied exactly from the post. No quote = not a buyer.
- Agencies advertising, freelancers offering services, "#hiring" job posts and job seekers are never buyers.
- Respect each platform's terms: only public posts, no scraping behind logins, no automated messaging.
- Paid search calls are capped by `--max-calls`; tell the user how many calls a run used.
- Speed beats polish on intent leads: most asks get answered within a day or two by someone.
""",
"refs": [("intent-rubric.md", "30 labelled examples (EN + Hinglish): buyers, sellers, job seekers, spam"),
         ("queries.md", "the query formula, LinkedIn boolean rules, every source and what it's best for, signal searches"),
         ("queries.md", "search queries by service and language, and how to add your own")],
},
# --------------------------------------------------------------------------- audit
{
"name": "sales-audit",
"title": "Website Audit — proof-of-work facts for outreach",
"description": "Runs a fact-only audit of a prospect's website — title, meta description, mobile viewport, HTTPS redirect, load time, page size, H1s, contact form, click-to-call, WhatsApp link, call-to-action, images missing alt text, tech stack (WordPress, Shopify, Wix, Webflow, Next.js), copyright year, broken internal links — each fact with evidence, no opinions, and turns the strongest facts into outreach observations. Use when the user says 'audit this website', 'check their site', 'what's wrong with their website', 'give me a hook for this prospect', or in Hinglish 'is website ko check karo', 'site mein kya problem hai'.",
"intro": """A specific, true observation about someone's own website is the strongest opener an agency has.
This skill produces only facts the page itself proves, so outreach built on it survives the claim check.""",
"body": f"""## Steps

1. Run the audit and save it in the prospect folder:
   `python <SCRIPTS>/site_audit.py --url <url> --save prospects/<slug>/SITE-AUDIT.json`
   (add `--no-links` for a faster run; robots.txt is respected). For the full picture in one run — audit plus
   company, people, email and web research with ranked hooks — use `{SCAN} <url>` instead.
2. Write `prospects/<slug>/SITE-AUDIT.md`: the URL, date, and a table of every fact (`statement` + `evidence`).
3. Pick the **top 3 observations** that matter to the prospect's business, using
   `references/fact-to-hook.md` (e.g. no viewport → phone visitors get the desktop layout; no CTA →
   visitors don't know the next step; copyright 2019 → site looks unmaintained). State the fact exactly as the
   audit does; any consequence you add must be phrased as likely ("so phone visitors probably..."), never as a
   measured number.
4. Record it: `{PIPE} add --url <url>` (if new), `{PIPE} attach <slug> prospects/<slug>/SITE-AUDIT.json --kind site-audit`,
   `{PIPE} note <slug> "Audit hooks: <hook 1>; <hook 2>"`.
5. **Local comparison** (local businesses, powerful hook): `{SRC} maps --search "<category> in <area>" --max 10`
   and compare rating, reviews and website with the top 3 nearby competitors — "3 of the 5 top-rated dentists in
   Koregaon Park have online booking; yours doesn't" is a fact if the data shows it.
6. Suggest `sales-outreach` next — it will use these facts as evidence.

## Rules
- Facts only. No scores like "your SEO is 4/10", no guessed traffic, no "your site is slow" unless the fact
  says the download took N seconds — and then quote N.
- Never claim certificate or security problems from a TLS error on your side.
- If the homepage didn't load or robots.txt blocks it, say so and stop.
""",
"refs": [("fact-to-hook.md", "how each audit fact becomes a respectful one-line observation, with examples")],
},
# --------------------------------------------------------------------------- prospect
{
"name": "sales-prospect",
"title": "Full Prospect Analysis",
"description": "Full scored prospect audit of a company URL using five role playbooks — company fit, contacts, opportunity (BANT), competitive position, then outreach strategy — run in sequence in any agent (or in parallel where supported), producing PROSPECT-ANALYSIS.md with a 0-100 prospect score, grade, action plan and a claim-checked first email, recorded in the pipeline. Use when the user says 'analyze this prospect', 'score this company', 'full audit of acme.com', '/sales prospect', or in Hinglish 'is company ka pura analysis karo', 'ye prospect kaisa hai'.",
"intro": """You run the deepest analysis in the team: discovery, five role playbooks, a weighted score, an action
plan and a ready first email for `prospects/<slug>/PROSPECT-ANALYSIS.md`.""",
"body": f"""## Steps

1. **Discovery** (see `references/playbook.md` Phase 1): run the deep scan —
   `{SCAN} <url> [--name "<company>"] [--post-text "<their post>"] [--city <city>]` — which audits the site,
   analyses the company, finds people and the best email, searches the web (reviews, news, hiring, complaints,
   ads, competitors) and writes `prospects/<slug>/DOSSIER.json/.md`. Read it plus any other files in
   `prospects/<slug>/`, then write a short discovery briefing.
2. **Roles** (Phase 2): follow, in this order, `references/role-company.md`, `role-contacts.md`,
   `role-opportunity.md`, `role-competitive.md`, then `role-strategy.md` (which needs the other four). Each
   returns a 0-100 category score with evidence. If your agent can run subagents, the first four may run in
   parallel; the default is sequential and works everywhere.
3. **Score** (Phase 3): Prospect Score = Company Fit 25% + Contact Access 20% + Opportunity 20% +
   Competitive 15% + Outreach Readiness 20%. Missing role = 50 and lower confidence.
4. **Write** `prospects/<slug>/PROSPECT-ANALYSIS.md` in the format of `references/output-format.md`:
   summary, score breakdown, company profile, decision makers, BANT/MEDDIC, competition, strategy, action plan,
   first email.
5. **Record**:
   `{PIPE} add --url <url> --name "<company>" --stage researched`
   `{PIPE} score <slug> <score> --breakdown '{{"company_fit": .., "contact_access": .., "opportunity": .., "competitive": .., "outreach_readiness": ..}}'`
   `{PIPE} attach <slug> prospects/<slug>/PROSPECT-ANALYSIS.md --kind prospect-analysis`
   `{PIPE} next <slug> "<first action>" --due <YYYY-MM-DD>` and one `contact` line per named decision maker.
6. **Terminal summary**: score + grade, top 3 reasons, the first email, the next skill to run.
""",
"writes_email": True,
"refs": [("playbook.md", "discovery, role orchestration, scoring and synthesis in detail"),
         ("role-company.md", "Company Fit role"), ("role-contacts.md", "Contact Access role"),
         ("role-opportunity.md", "Opportunity Quality role (BANT, pain, timeline)"),
         ("role-competitive.md", "Competitive Position role"), ("role-strategy.md", "Outreach Readiness role + first email"),
         ("output-format.md", "PROSPECT-ANALYSIS.md template"), ("rules.md", "terminal output, errors, cross-skill use")],
},
# --------------------------------------------------------------------------- research
{
"name": "sales-research",
"title": "Company Research & Firmographics",
"description": "Deep company research for a prospect URL across 8 dimensions — what they do, size, growth, tech stack, leadership, news, financial and buying signals — with every claim sourced, written to COMPANY-RESEARCH.md and recorded in the pipeline. Works for SaaS, agencies, e-commerce, local businesses and enterprises. Use when the user says 'research this company', 'tell me about acme.com', 'company background', '/sales research', or in Hinglish 'is company ke baare mein batao', 'company research karo'.",
"intro": """You produce sourced, structured intelligence on one company. Every claim has a source page or
"Not found".""",
"body": f"""## Steps

1. Start with the deep scan: `{SCAN} <url> [--name "<company>"] [--city <city>]` (site audit, company analysis,
   people, email, web research → `DOSSIER.md`). Then fetch what it missed — about, team, careers, services,
   blog/news, case studies — with your web tool or `python <SCRIPTS>/fetch_page.py <url1> <url2> ...`.
2. The web research inside the scan (`{SRC} research <domain> --name "<company>"` on its own) covers mentions,
   reviews, complaints, news, LinkedIn, founder, social, directories, hiring, ads and competitors and saves
   `prospects/<slug>/WEB-RESEARCH.json` (needs `APIFY_TOKEN` or `BRIGHTDATA_API_KEY`; otherwise use your own
   search tool). Snippets are leads — open the page before stating a fact from it.
3. Cover the 8 dimensions in `references/playbook.md`. Adapt to the business type: for a local business or
   SMB focus on owner, locations, reviews, website quality and marketing activity; for SaaS on product,
   pricing, team growth; for e-commerce on catalogue, platform, channels.
4. Write `prospects/<slug>/COMPANY-RESEARCH.md` using `references/output-format.md`, with a source for each fact,
   ending with **"Why now"** (the trigger: their post, a launch, hiring, bad reviews, an outdated site) and the
   **3 best hooks** for outreach.
5. Record: `{PIPE} add --url <url> --name "<company>" --stage researched` and
   `{PIPE} attach <slug> prospects/<slug>/COMPANY-RESEARCH.md --kind research`; add named leaders with
   `{PIPE} contact <slug> --name ... --title ... --source website`.
""",
"refs": [("playbook.md", "the 8 research dimensions and where to find each"), ("output-format.md", "COMPANY-RESEARCH.md template"),
         ("rules.md", "terminal output, errors, cross-skill use")],
},
# --------------------------------------------------------------------------- qualify
{
"name": "sales-qualify",
"title": "Lead Qualification (BANT + MEDDIC)",
"description": "Qualifies a prospect with BANT and MEDDIC from public signals and any notes or replies the user has, cross-checked with the deterministic lead_scorer.py (or its agency-buyer mode for service sellers), and writes LEAD-QUALIFICATION.md with grade, gaps and discovery questions, recorded in the pipeline. Use when the user says 'qualify this lead', 'is this a good lead', 'BANT score', 'MEDDIC', '/sales qualify', or in Hinglish 'ye lead qualified hai kya', 'lead check karo'.",
"intro": """You decide whether a prospect deserves time, and what is still unknown.""",
"body": f"""## Steps

1. Gather evidence: existing `prospects/<slug>/` files, the user's notes and the prospect's replies, plus
   fresh research where needed (`references/playbook.md`).
2. Assess BANT (Budget, Authority, Need, Timeline — 25 each) and MEDDIC (Metrics, Economic buyer, Decision
   criteria, Decision process, Identify pain, Champion), each with evidence or "Unknown".
3. Cross-check with the script:
   - B2B account: write signals to `prospects/<slug>/_bant_signals.json` (`python <SCRIPTS>/lead_scorer.py --example`
     shows the format) and run `python <SCRIPTS>/lead_scorer.py prospects/<slug>/_bant_signals.json`.
   - Someone who asked for a service publicly: `python <SCRIPTS>/lead_scorer.py --mode agency <file>`.
   If your score and the script differ by more than 15, explain why.
4. **Service-buyer checks** (agencies/freelancers): budget stated or implied (₹/$ range, "cheap" = flag),
   decision maker = the poster/owner?, timeline trigger (launch, festive season, event, "ASAP"), scope clarity,
   red flags (wants free samples/spec work, "just exploring", equity-only, unrealistic budget for scope, many
   agencies already in the comments). Two or more red flags → `nurture` or `disqualified`, fast.
5. Write `prospects/<slug>/LEAD-QUALIFICATION.md` (`references/output-format.md`), including the 3-5
   discovery questions that would close the biggest gaps (budget range, decision process, timeline, success
   measure, what went wrong last time).
6. Record: `{PIPE} score <slug> <score>`, `{PIPE} stage <slug> qualified --reason "<grade + main reason>"`
   (or `disqualified` / `nurture`), `{PIPE} next <slug> "<next step>"`.
""",
"refs": [("playbook.md", "BANT and MEDDIC rubrics with scoring guidance"), ("output-format.md", "LEAD-QUALIFICATION.md template"),
         ("rules.md", "terminal output, errors, cross-skill use")],
},
# --------------------------------------------------------------------------- contacts
{
"name": "sales-contacts",
"title": "Decision Makers & Verified Contacts",
"description": "Maps the buying committee at a prospect — names, titles, buying roles, personalization anchors, warm paths and a multi-threading plan — and finds and verifies contact emails with find_email.py (post/site first, then Prospeo, Findymail, Hunter, Apollo and MillionVerifier/ZeroBounce/NeverBounce; guesses always labelled pattern-guessed), writing DECISION-MAKERS.md and saving contacts to the pipeline. Use when the user says 'who should I contact', 'find the decision maker', 'get their email', 'who is the owner', '/sales contacts', or in Hinglish 'owner kaun hai', 'iska email nikalo', 'kisse baat karun'.",
"intro": """You find the right people and the safest way to reach them. A wrong or guessed address costs
deliverability, so verification status is always shown.""",
"body": f"""## Steps

1. **People**: if a `DOSSIER.json` exists, start from its `people` and `decision_maker`. Otherwise run
   `python <SCRIPTS>/contact_finder.py --url <url>`, read the team/about pages, and search for leaders
   (`site:linkedin.com/in "<company>" founder OR owner OR director`). A hunt lead already names the person:
   the post author (LinkedIn profile URL, HN/Reddit username). Only list people you found evidence for.
2. **Roles**: classify each as Economic Buyer, Champion, Technical Evaluator, User, Influencer or Blocker
   (`references/playbook.md` Phase 2). For an owner-run SMB the owner is usually buyer and champion.
3. **Emails**: for the top 1-3 people run
   `python <SCRIPTS>/find_email.py --domain <domain> --first <first> --last <last>`.
   It runs a waterfall and stops at the first verified address: their post → website → finders
   (Prospeo, Findymail, Hunter, Apollo — whichever keys are set, order in `EMAIL_FINDERS`) → verifiers
   (MillionVerifier, ZeroBounce, NeverBounce, Hunter) on the candidates, or on likely name patterns if nothing
   was found. `find_email.py --providers` shows what is configured.
   If the post or website already shows an address it is used and only verified — no finder credits. An address
   from a people database (Apollo, Leads Finder): `python <SCRIPTS>/find_email.py --email <address>` (verify only).
   Use the status exactly as returned: `verified`, `catch_all`, `unverified`, `pattern-guessed`, `invalid`.
   Only `verified` addresses are safe for cold email; say so.
   **Best channel** per person: verified email → email; business phone from the site or Google Maps → WhatsApp
   click-to-chat (`python <SCRIPTS>/outreach.py whatsapp`); only a LinkedIn/Reddit/HN profile → the user replies
   where they posted or sends a DM themselves.
4. **Personalization anchors** and **multi-threading plan** (Phases 3-5).
5. Write `prospects/<slug>/DECISION-MAKERS.md` (`references/output-format.md`).
6. Record each person: `{PIPE} contact <slug> --name "<name>" --title "<title>" --role "<buying role>"
   --email <email> --email-status <status> --source <source> --linkedin <url>`.
""",
"refs": [("playbook.md", "contact discovery, buying roles, anchors, access score, multi-threading"),
         ("output-format.md", "DECISION-MAKERS.md template"), ("rules.md", "terminal output, errors, cross-skill use")],
},
# --------------------------------------------------------------------------- competitors
{
"name": "sales-competitors",
"title": "Competitive Intelligence & Battle Cards",
"description": "Detects which tools, vendors or agencies a prospect uses today (site tech, job posts, case studies, reviews) and builds honest battle cards, switching-cost assessment, landmine questions and a displacement strategy, written to COMPETITIVE-INTEL.md. For agencies it covers the prospect's current web/SEO/marketing provider and platform. Use when the user says 'what do they use', 'who is their current agency', 'how do I beat their vendor', 'battle card', '/sales competitors', or in Hinglish 'abhi kaun sa tool use karte hain', 'competitor ko kaise harayein'.",
"intro": """You find what the prospect relies on today and how to win against it — honestly.""",
"body": f"""## Steps

1. Detect current solutions (`references/playbook.md` Step 1): site tech (`python <SCRIPTS>/site_audit.py --url <url> --no-links`
   reports the platform), footer credits ("Designed by ...", "Powered by ..."), job posts, case studies, review
   sites, and the `competitors` / `ads` sections of `WEB-RESEARCH.json` if present.
   **Their market competitors** (strong for local businesses): `{SRC} maps --search "<category> in <city>" --max 15`
   gives nearby rivals' ratings, review counts and websites — use the gap as a fact-based hook.
2. Categorise them and build one battle card per competitor (Step 3): honest strengths, specific weaknesses,
   your advantages, switching cost, triggers, landmine questions, a positioning statement.
3. Feature/service gap analysis, win/loss patterns, recommended strategy (Steps 4-6).
4. Write `prospects/<slug>/COMPETITIVE-INTEL.md` (`references/output-format.md`), with the source of each detection.
5. Record: `{PIPE} attach <slug> prospects/<slug>/COMPETITIVE-INTEL.md --kind competitive` and a note with the
   main incumbent.

Never disparage a competitor with claims you can't source.
""",
"refs": [("playbook.md", "detection sources, battle card format, strategy"), ("output-format.md", "COMPETITIVE-INTEL.md template"),
         ("rules.md", "rules")],
},
# --------------------------------------------------------------------------- outreach
{
"name": "sales-outreach",
"title": "Cold Outreach Sequence",
"description": "Writes a personalized, compliant cold outreach sequence for a prospect — a short first email built on one verified observation (their public post or a site-audit fact), 4 follow-ups and LinkedIn touches — with A/B subject lines, every sentence claim-checked against evidence before it is shown, written to OUTREACH-SEQUENCE.md and tracked in the pipeline. Use when the user says 'write a cold email', 'outreach sequence', 'email this prospect', 'LinkedIn message', '/sales outreach', or in Hinglish 'is client ko email likho', 'cold email banao', 'pehla message likho'.",
"intro": """You write outreach a busy owner actually answers: short, specific, true, and easy to say yes to.""",
"body": f"""## Steps

1. **Evidence first.** If `prospects/<slug>/DOSSIER.json` is missing, run the deep scan:
   `{SCAN} <url> [--post-text "<their post>" --post-url <url>]`. Read `DOSSIER.md` (ranked hooks, decision maker,
   best email), other `prospects/<slug>/` files and `{PIPE} show <slug>`. Recipient must have a `verified` email,
   or say clearly that it isn't.
   **Channel by source:** they posted asking (LinkedIn/Reddit/HN/X/FB) → reply there first (user posts it, 2 lines,
   helpful, no pitch) + email if verified; Google Maps lead with a phone and no email → WhatsApp click-to-chat;
   Product Hunt launch → email the maker or comment on the launch (user).
2. **First email** — follow `references/first-email-guide.md`: plain text, under 120 words, mentions their post
   or business naturally, ONE specific observation backed by evidence, one soft question as the CTA ("worth a
   quick call?"), the user's signature with postal address and an opt-out line. **No booking link** — the goal of
   the cold emails is a reply; the calendar link is sent only once they say yes (`sales-reply` / `sales-book`).
3. **Sequence** — 4 follow-ups on **day 3, 7, 14 and 28** after email 1 (`{OUT} cadence`), each adding something
   new, using `references/playbook.md` and the templates `references/template-outreach-cold.md`, `-warm.md`, `-referral.md`:
   | Email | Day | Content | Words |
   |---|---|---|---|
   | 1 | 0 | Their post / top hook + one fact + soft question | ≤ 120 |
   | 2 | 3 | Second hook (another audit fact) + a 1-line fix idea | ≤ 70 |
   | 3 | 7 | Proof: a relevant real result, or a mini teardown of their page (`[ADD REAL CUSTOMER RESULT]` if none) | ≤ 90 |
   | 4 | 14 | Different angle: competitor/market fact (Maps comparison, reviews) or a simple question | ≤ 60 |
   | 5 | 28 | Polite breakup: "close the file?" + leave the door open | ≤ 50 |
   Subject lines: 2-5 words, lower-case, specific ("acme homepage on mobile"), no clickbait; follow-ups reply
   in the same thread. Write in plain international English — US spelling for US/CA prospects, UK spelling for
   UK/IE/AU/NZ — no Indian-English idioms ("do the needful", "revert", "kindly"), prices in their currency.
   Pull the signature, offer line and proof only from `SELLER-PROFILE.json` (`{PROF} show`).
   Use the warm or referral template only for a real, confirmed connection.
4. **Claim check** every email (see "Before anything is sent"); fix until it passes.
5. Write `prospects/<slug>/OUTREACH-SEQUENCE.md` (`references/output-format.md`).
6. Record: `{PIPE} attach <slug> prospects/<slug>/OUTREACH-SEQUENCE.md --kind outreach`.
7. **Put it on autopilot** (with SMTP + IMAP set up): save the 5 emails as `prospects/<slug>/SEQUENCE.json`
   (`[{{"step": 1, "subject": "...", "body": "..."}}, {{"step": 2, "body": "..."}}, ...]` — follow-ups reply in the same
   thread), show them to the user, and on approval run
   `{OUT} approve <slug> --to <email> --file prospects/<slug>/SEQUENCE.json` (the dossier, audit and research files
   and your profile's proof are used as evidence automatically; add `--evidence-text "<their post>"` if it isn't in the dossier).
   It checks every email now and queues them; `{AUTO} tick --send` (scheduled) sends each on its day and stops
   the moment they reply, opt out, bounce or book.
8. **Or send one at a time** (see "Before anything is sent"): either the user sends it and you log it —
   `{OUT} log <slug> --channel email --step 1 --to <email> --subject "<subject>"` — or, if SMTP is set up and the
   user approves this exact email, `{OUT} send ...` (dry run first, then `--send`). Logging moves the stage to
   `contacted` and schedules follow-up #1 automatically (`{OUT} cadence` shows the schedule).
9. Other channels: LinkedIn/WhatsApp messages are sent by the user; for WhatsApp give a click-to-chat link
   (`{OUT} whatsapp <number with country code> --text-file msg.txt`), then log it with `--channel whatsapp`.
""",
"writes_email": True,
"refs": [("first-email-guide.md", "style rules + 10 good/bad first-email examples"),
         ("playbook.md", "personalization research, 4 frameworks, the 5-email sequence, LinkedIn, A/B, sending"),
         ("output-format.md", "OUTREACH-SEQUENCE.md template"), ("template-outreach-cold.md", "cold template"),
         ("template-outreach-warm.md", "warm intro template"), ("template-outreach-referral.md", "referral template"),
         ("compliance.md", "legal and deliverability rules"), ("rules.md", "terminal output, errors, cross-skill use")],
},
# --------------------------------------------------------------------------- followup
{
"name": "sales-followup",
"title": "Follow-Up Sequences",
"description": "Writes follow-up sequences after a meeting, demo, proposal, a prospect going silent, or for long-term nurture — emails, LinkedIn touches, voicemail and SMS scripts with a cadence calendar — based on what actually happened (meeting notes, replies), claim-checked, written to FOLLOWUP-SEQUENCE.md and tracked in the pipeline. Use when the user says 'follow up with', 'they went quiet', 'after the demo', 'proposal follow-up', 'ghosted', '/sales followup', or in Hinglish 'follow up likho', 'reply nahi aaya', 'meeting ke baad kya bhejun'.",
"intro": """Follow-ups win most deals. You write ones that add value instead of "just checking in".""",
"body": f"""## Steps

1. Ask (or read) what happened: last touch, what they said, what was promised, pricing shared, objections.
   Read `{PIPE} show <slug>` and the prospect folder.
2. Pick the scenario (`references/playbook.md` Step 2): post-meeting, post-demo, post-proposal, ghost recovery
   or nurture, and its cadence. Post-meeting recap goes out within 24 hours: what they said (their words),
   what you agreed, the next step with a date. Post-proposal: day 2 walkthrough offer, day 5 one question on
   the option they liked, day 10 a deadline that is real (start slot, price validity), day 20 breakup.
3. Write the emails plus LinkedIn/phone/SMS touches only where appropriate (SMS only for warm leads who
   shared their number). Reference real details from the conversation.
4. Claim-check every email.
5. Write `prospects/<slug>/FOLLOWUP-SEQUENCE.md` (`references/output-format.md`).
6. Cold sequences already queued with `{OUT} approve` need nothing here — they send on day 3, 7, 14, 28.
   Record: `{PIPE} note <slug> "<what happened>"`, and log each manual follow-up when it goes out —
   `{OUT} log <slug> --channel email --to <email> --subject "..."` (this schedules the next one from the
   cadence) — or `{PIPE} next <slug> "<next touch>" --due <date>` for a custom date. Update the stage
   (`replied`, `meeting`, `proposal`, `nurture`, `lost`) when the user tells you. If they replied, use `sales-reply`.
""",
"writes_email": True,
"refs": [("playbook.md", "the 5 scenarios, multi-channel touches, cadence, breakup emails"),
         ("output-format.md", "FOLLOWUP-SEQUENCE.md template"), ("compliance.md", "legal and deliverability rules"), ("rules.md", "rules")],
},
# --------------------------------------------------------------------------- prep
{
"name": "sales-prep",
"title": "Meeting Preparation Brief",
"description": "Builds a meeting brief for an upcoming prospect call: one-page cheat sheet, company snapshot, attendee profiles, the prospect's original post or request, site-audit facts, the full email thread and qualification answers so far, talking points, 10 discovery questions, likely objections, landmines, agenda and next steps — written to MEETING-PREP.md. Use when the user says 'prep me for my call', 'meeting tomorrow with', 'brief me on', '/sales prep', or in Hinglish 'meeting ki taiyari karo', 'call se pehle kya jaanna chahiye'.",
"intro": """You make the user the best-prepared person in the meeting, using what is already known first.""",
"body": f"""## Steps

1. Load everything known: `{PIPE} show <slug>`, `{MEET} list`, all files in `prospects/<slug>/` (`DOSSIER.md`,
   post quote, SITE-AUDIT, research, contacts, outreach, replies). If there's no dossier, run `{SCAN} <url>` first.
   Ask for the meeting goal if unknown.
2. Fill gaps with fresh research on the company and each attendee (`references/playbook.md` Step 1).
3. Build the brief (Step 2): cheat sheet first; then snapshot, attendees, their original request in their own
   words, audit facts, the conversation so far, qualification status (budget, timeline, decision maker, scope —
   mark unknowns), talking points, 10 discovery questions aimed at the unknowns, objections, landmines,
   success metrics, next steps to propose, and an agenda (Step 3) for 15/30/60 minutes.
4. Add a **3-minute screen-share plan**: open their site on a phone view, show the top 2 audit facts, show one
   competitor doing it better — then ask, don't pitch. End the brief with the exact ask for the meeting's close
   ("Shall I send a proposal with 2 options by Friday?").
5. Write `prospects/<slug>/MEETING-PREP.md` (`references/output-format.md`, `references/template-meeting-prep.md`).
6. Record: `{PIPE} attach <slug> prospects/<slug>/MEETING-PREP.md --kind meeting-prep`. If the meeting isn't in
   the pipeline yet, book it with `sales-book` (`{MEET} book ...`) so reminders and outcomes are tracked.
7. Give the user the reminder message to send the day before (from `{MEET} list`) and, after the call,
   record the outcome: `{MEET} outcome <id> held --notes "<budget, scope, decision date>"`.
""",
"refs": [("playbook.md", "research steps, the 11 brief sections, agendas"), ("output-format.md", "MEETING-PREP.md format"),
         ("template-meeting-prep.md", "structural template"), ("rules.md", "rules")],
},
# --------------------------------------------------------------------------- proposal
{
"name": "sales-proposal",
"title": "Client Proposal",
"description": "Writes a client-ready proposal from the prospect's stated needs and the user's real pricing — executive summary, situation, solution, scope, timeline, three investment options, ROI with stated assumptions, team, real case studies only, next steps — plus a post-send follow-up sequence, claim-checked, written to CLIENT-PROPOSAL.md and tracked in the pipeline. Use when the user says 'write a proposal', 'quote for this client', 'pricing proposal', 'SOW', '/sales proposal', or in Hinglish 'proposal banao', 'quotation bhejna hai', 'client ko price batana hai'.",
"intro": """You write a proposal that sells the outcome, priced from the user's real numbers.""",
"body": f"""## Steps

1. **Inputs** (`references/playbook.md` Step 1): the prospect's needs in their words (post, replies, meeting
   notes, `MEETING-PREP.md`, `LEAD-QUALIFICATION.md`), and the user's pricing ranges, timelines, process, team
   and real case studies — from `IDEAL-CUSTOMER-PROFILE.md`, their notes, or ask. Never invent prices,
   timelines or results: use `[TO CONFIRM]` until the user gives them.
2. **Write** the 11 sections (Step 2) using `references/template-proposal-template.md`. Three options
   (e.g. Essential / Growth / Complete) anchored to the stated need — the middle one is the one you recommend;
   ROI only with explicit, conservative assumptions. Make it easy to say yes:
   - Price in their currency ($, £, C$, A$, €) from the profile's deal size, what's included and **not** included.
     If you invoice from India, the tax treatment of exported services is for your accountant — don't state it.
   - Payment terms (e.g. 50% to start, 50% on launch, or milestones), timeline per phase, revision rounds.
   - Validity date (e.g. 14 days) and a start slot if real; acceptance = reply "approved Option B".
   - Their words from the post/meeting in the "Situation" section, and 2-3 audit facts as the "why".
3. **Follow-up sequence** after sending (Step 3).
4. Claim-check the whole proposal and its emails.
5. Write `prospects/<slug>/CLIENT-PROPOSAL.md` (`references/output-format.md`).
6. Record: `{PIPE} stage <slug> proposal --reason "proposal sent <date>"`, `{PIPE} value <slug> <recommended option price> --currency <cur>`,
   attach the file, `{PIPE} next <slug> "Walkthrough offer" --due <date+2>`. When they decide: `{PIPE} stage <slug> won`
   (or `lost --reason "<why>"` — the reason feeds the weekly review).
""",
"writes_email": True,
"refs": [("playbook.md", "inputs, the 11 sections, follow-up sequence"), ("output-format.md", "CLIENT-PROPOSAL.md format"),
         ("template-proposal-template.md", "structural template"), ("compliance.md", "legal rules for the follow-up emails"),
         ("rules.md", "rules")],
},
# --------------------------------------------------------------------------- objections
{
"name": "sales-objections",
"title": "Objection Handling Playbook",
"description": "Generates word-for-word objection responses for calls, emails and chat — 15 universal objections, industry-specific and competitor objections, pricing tactics and prevention — tailored to what the user sells and, optionally, one prospect or industry, written to OBJECTION-PLAYBOOK.md. Covers the objections overseas clients raise about offshore agencies (time zones, communication, quality, trust, IP, payment). Use when the user says 'handle objections', 'they said it's too expensive', 'what do I say if', '/sales objections', or in Hinglish 'client bol raha hai mehenga hai', 'objection ka jawab do'.",
"intro": """You give the user exact words for the hard moments, true to their offer.""",
"body": f"""## Steps

1. Context (`references/playbook.md` Step 1): what the user sells, price points, the industry/prospect, the
   objections they actually hear.
2. Frameworks (Feel-Felt-Found, Acknowledge-Bridge-Close) and the 15 universal objections (Steps 2-3), each
   with a call version, an email version and a follow-up question.
3. Industry, competitive and pricing objections (Steps 4-6); prevention tactics (Step 7). For agencies include
   "a freelancer will do it cheaper", "we tried an agency before", "can you guarantee page 1?"
   (never promise rankings).
4. Map each objection to the reply categories `reply_triage.py` detects (`objection_price`, `objection_timing`,
   `objection_has_vendor`, `not_interested`) so `sales-reply` can use the right answer, and include a short
   email version (≤ 60 words). Include the offshore-agency objections overseas buyers raise: "you're in another
   time zone" (overlap hours, response time), "quality/communication worries" (process, named PM, weekly calls),
   "I've been burned by an offshore team" (milestone payments, code ownership, references), "IP and contracts"
   (contract under their law if needed, NDA), "how do I pay you" (Wise/Payoneer/Stripe invoice).
5. Write `OBJECTION-PLAYBOOK.md` in the working-directory root (or `prospects/<slug>/` for one prospect), using
   `references/template-objection-playbook.md`. Proof points must be real — otherwise `[ADD REAL CUSTOMER RESULT]`.
""",
"refs": [("playbook.md", "frameworks, 15 objections, industry/competitive/pricing, prevention"),
         ("output-format.md", "OBJECTION-PLAYBOOK.md format"), ("template-objection-playbook.md", "structural template"),
         ("rules.md", "rules")],
},
# --------------------------------------------------------------------------- setup
{
"name": "sales-setup",
"title": "Seller Setup — learn everything about the seller first",
"description": "First-run onboarding that interviews the seller before any prospecting: agency name, sender identity, postal address, services, niches, platforms, outcomes, deal size and currency, target countries and cities, excluded markets, buyer job titles, company size, real case studies and proof, differentiators, buyer pains, buying triggers, tools clients leave, booking link — saved to SELLER-PROFILE.json, which every other skill and script (queries, Apollo/LinkedIn filters, emails, proposals, send times) is built from. Also checks which API keys are set. Use at the start of any new session or when the user says 'set up', 'onboard me', 'start', 'here is my business', 'update my profile', 'change my niche', or in Hinglish 'setup karo', 'mere business ke baare mein pucho', 'profile banao'.",
"intro": """Nothing good comes from generic queries and generic emails. Before hunting, writing or pricing anything,
you learn the seller's business properly and save it, so every agent after you builds on the same facts.""",
"body": f"""## Steps

1. **Check what exists:** `{PROF} check`. If it says `Ready.`, show a 5-line summary and ask only whether
   anything changed. If the profile is missing: `{PROF} init`.
2. **Interview** (`references/intake.md`; `{PROF} questions` lists every field with why it matters). Ask in at
   most **3 short rounds**, grouped, with an example answer for each question — never 25 questions at once:
   - Round 1 — the business: name, website, sender name + email, postal address, time zone; services
     (codes: web, app, seo, marketing, design, software, ecommerce, video); the offer in one line; niches.
   - Round 2 — the buyer: target countries/cities, excluded markets, buyer titles, company size, deal size +
     currency, their pains right before they hire, buying triggers, tools/platforms they leave.
   - Round 3 — proof and positioning: 2-3 real results (client, result, link), portfolio, years/projects/team,
     why you over others, any real guarantee, booking link.
   Accept "skip" for optional fields. Never fill an answer the user didn't give — case studies especially.
3. **Read their website** (if given) to pre-fill and confirm, not invent: services, niches, case studies, address.
4. **Save** each answer: `{PROF} set <field> '<json or text>'` (e.g. `{PROF} set offer.niches '["DTC skincare", "coffee brands"]'`),
   then `{PROF} check` until it says `Ready.`
5. **Keys check:** `python <SCRIPTS>/find_email.py --providers` and look for `APIFY_TOKEN`, `SMTP_*`, `IMAP_*`,
   `BOOKING_URL`, `APOLLO_API_KEY` in `~/.ai-sales-team/.env` (template `examples/env.example`), and whether your
   agent has an Apollo connector. Tell the user which sources and
   automations are on, and the one key that would add the most (usually `APIFY_TOKEN`, then a verifier).
6. **Show the queries this profile produces:** `{QL}` — 3 LinkedIn queries, 2 X-ray queries, the Apollo URL and the
   subreddits — and ask if they look like their buyers. Adjust niches/pains/triggers and re-run until they do.
7. Next: `sales-icp` (full ICP), then `sales-hunt`.

## Rules
- The profile is the single source of truth for who the seller is. Emails may cite only proof that is in it.
- Default market is international (US, UK, Canada, Australia); excluded markets are respected by every source.
- Store no API keys in the profile — keys live only in `~/.ai-sales-team/.env`.
- Re-run this skill whenever the offer, niche or target market changes.
""",
"before": False,
"refs": [("intake.md", "the interview: every question, why it matters, good vs weak answers, how answers become queries")],
},
# --------------------------------------------------------------------------- icp
{
"name": "sales-icp",
"title": "Ideal Customer Profile",
"description": "Builds the Ideal Customer Profile every other sales skill scores against — firmographics, buying signals, pain points, budget qualifiers, negative ICP, scoring rubric, 2-3 buyer personas, channels, the phrases buyers use and the best search queries — from the seller profile (sales-setup), written to IDEAL-CUSTOMER-PROFILE.md. Use when the user says 'build my ICP', 'who should I target', 'ideal customer', 'I sell X to Y', '/sales icp', or in Hinglish 'mera ideal client kaun hai', 'kisko target karun'.",
"intro": """Start here. Every fit score in the other skills is only as good as this profile.""",
"body": f"""## Steps

1. Load the seller profile: `{PROF} show` (run `sales-setup` if `{PROF} check` says it's incomplete). It holds the
   services, niches, deal size, target countries (e.g. US/UK/CA/AU), excluded markets, buyer titles, pains,
   triggers and proof.
2. Research the market briefly (`references/playbook.md` Research Phase) — who buys this, where they talk.
3. Build the framework (Steps 2-7): firmographics, technographics, behavioural and **intent signals** (the exact
   phrases buyers post, e.g. "need a website for my clinic", "can anyone recommend a Shopify developer", "our site looks dated"),
   pain map, budget qualifiers, channels, negative ICP, a 0-100 scoring rubric, 2-3 personas, prospecting playbook.
   Feed new findings back into the profile (`{PROF} set signals.pains '[...]'`) — the queries update automatically.
4. Write `IDEAL-CUSTOMER-PROFILE.md` in the working-directory root (`references/output-format.md`). Include:
   - **Hunt settings**: services as codes (`web, app, seo, marketing, design, software, ecommerce, video`),
     countries/cities (or "remote"), excluded markets, price floor — mirror `SELLER-PROFILE.json`.
   - **Search queries**: run `{QL}` (profile-driven) and keep the 5-10 best LinkedIn
     boolean queries, X-ray queries, subreddits and Google Maps categories for this ICP (add niche words).
   - **Proof**: 2-3 real results the user can cite (or `[ADD REAL CUSTOMER RESULT]`), so outreach has evidence.
""",
"refs": [("playbook.md", "the 7 ICP steps and rubric"), ("output-format.md", "IDEAL-CUSTOMER-PROFILE.md template"), ("rules.md", "quality rules")],
},
# --------------------------------------------------------------------------- reply
{
"name": "sales-reply",
"title": "Reply Handling",
"description": "Handles a prospect's reply to outreach: classifies it (interested, meeting request, question, price/timing/vendor objection, referral, not interested, opt-out, out-of-office, bounce) in English, Hindi or Hinglish, updates the pipeline (stage, follow-ups stopped, opt-outs suppressed, bounced emails marked invalid) and drafts a short, truthful answer whose goal is a booked call. Use when the user pastes a reply or says 'they replied', 'what should I answer', 'client ne reply kiya', 'iska jawab likho', 'unhone price poocha', '/sales reply'.",
"intro": """A reply is the most valuable moment in the pipeline. Answer fast, answer exactly what they asked, and move to a call.""",
"body": f"""## Steps

1. Get the reply text (the user pastes it or saves it to a file) and the prospect slug.
2. Classify and update the pipeline in one go. With IMAP set up, `{INBOX} check --apply` does this for every new
   reply and bounce (read-only); otherwise the user pastes the reply and you run
   `{TRIAGE} --file reply.txt --apply <slug> [--from <their email>]`. Either way the queued sequence stops.
   Read the reply yourself too — if the script's category is wrong, say so and fix the stage with `{PIPE} stage`.
3. Act on the category:
   | Category | What you write |
   |---|---|
   | `meeting_request` | Go straight to `sales-book`: confirm the time they named, or offer 2-3 slots |
   | `interested` / `question` | Answer in 1-3 sentences (facts only from the ICP / their files), then offer 2-3 slots (`{MEET} slots --prospect-tz <tz>`) and the booking link — now it is welcome |
   | `objection_price` / `_has_vendor` | Use `OBJECTION-PLAYBOOK.md` or `sales-objections`; offer a smaller first step, then a call |
   | `objection_timing` | Agree a date; `{PIPE} next <slug> "Check back as agreed" --due <date>`; stage stays `nurture` |
   | `referral` | Thank them; write a 3-line email to the named person mentioning who referred you (`sales-outreach`) |
   | `out_of_office` | No reply; `{PIPE} next <slug> "Follow up after they return" --due <return date + 1>` |
   | `not_interested` | One gracious line, no pitch; never follow up again |
   | `unsubscribe` | Nothing to write. It's already suppressed — confirm to the user |
   | `bounce` | Find another verified contact with `sales-contacts` |
4. Claim-check the answer (see "Before anything is sent"), show it to the user, and log it when it's sent:
   `{OUT} log <slug> --channel email --to <email> --subject "Re: <their subject>" --no-schedule`.
5. Tell the user the new stage and the next step with its due date (`{PIPE} show <slug>`).

## Rules
- Reply within the hour for `meeting_request` and `interested` — speed decides most deals.
- Answer what they asked first. Don't paste the whole pitch again.
- Never claim a price, timeline or result the user hasn't confirmed; use `[TO CONFIRM: ...]` and ask.
- Reply in plain English that matches their tone and spelling (US vs UK); short beats formal.
""",
"writes_email": True,
"refs": [("compliance.md", "legal and deliverability rules")],
},
# --------------------------------------------------------------------------- book
{
"name": "sales-book",
"title": "Meeting Booking",
"description": "Books the meeting: proposes free slots that fit both the user's and the prospect's time zone (US, UK, Canada, Australia, Europe and others), offers the user's booking link, writes a calendar invite (.ics for Google Calendar, Outlook, Apple), records the meeting in the pipeline, stops follow-ups, schedules prep and a reminder, and records the outcome afterwards (held, no-show, rescheduled, cancelled). Use when the user says 'book a meeting', 'schedule a call', 'they want to talk', 'send calendar invite', 'meeting fix karo', 'call schedule karo', 'meeting book karo', '/sales book'.",
"intro": """Getting to "yes, let's talk" is hard; losing it to back-and-forth about times is avoidable. You make booking take one email.""",
"body": f"""## Steps

1. **Who and where.** Read `{PIPE} show <slug>`. Work out the prospect's time zone from their post, site
   address, phone code (+91 India, +1 US/Canada, +44 UK, +61 Australia) or email signature; if unsure, ask.
2. **If they named a time**, use it (check it with `{MEET} slots` only if it may clash). Otherwise propose:
   `{MEET} slots --prospect-tz <IANA zone> [--count 3] [--minutes 30]`
   It returns 2-3 slots on different days in both zones, avoiding meetings already booked, plus a ready
   message that includes `BOOKING_URL` if the user has one (Cal.com, Calendly, Google booking page). Slots
   marked `outside_your_work_hours` need the user's OK (common for Asia ↔ US). Record where they are once:
   `{PIPE} where <slug> --country US --tz America/Chicago` — follow-ups then land in their morning too.
3. Write the booking email: one line of context + the slots + the link. Claim-check it, the user sends it,
   then `{OUT} log <slug> --channel email --to <email> --subject "..." --no-schedule`.
4. **When they confirm**, book it:
   `{MEET} book <slug> --start "YYYY-MM-DD HH:MM" [--tz <zone the time is in>] --prospect-tz <their zone> --attendee <email> --attendee-name "<name>" [--link <video link>] [--agenda "<one line>"]`
   This writes `prospects/<slug>/MEETING-<date>.ics`, sets the stage to `meeting`, stops follow-ups and
   schedules prep for the day before. Give the user the confirmation message and tell them to attach the `.ics`.
5. **Before the meeting:** run `sales-prep`; the day before, give the user the reminder message.
6. **After the meeting:** `{MEET} outcome <id> held|no_show|rescheduled|cancelled --notes "<what was agreed>"`.
   Held → `{PIPE} stage <slug> proposal` when a proposal is due and run `sales-followup` (post-meeting recap)
   and `sales-proposal`. No-show → send a kind note with 2 new slots (step 2). Rescheduled → book the new time.

## Settings (in `~/.ai-sales-team/.env`)
`TIMEZONE` (default Asia/Kolkata), `WORK_HOURS` (10:00-18:00), `EXTENDED_HOURS` (07:00-23:00, used only
when time zones barely overlap), `WORK_DAYS` (Mon-Fri), `MEETING_MINUTES` (30), `BOOKING_URL`, `MEETING_LINK`,
`SENDER_NAME`, `SENDER_EMAIL`. Ask the user once and suggest they add them.

## Rules
- The booking link goes out only after they've shown interest; `outreach.py` refuses it in cold emails.
- When they book through the link, `{INBOX} check --apply` (and the autopilot) spots the Calendly / Cal.com /
  calendar-invite email, records the meeting with its time, moves the stage and schedules prep — no manual step.
  With `AUTO_REPLY=1` and IMAP, a "let's talk" reply gets the link automatically within one autopilot tick.
- Always show times in **their** zone first, with yours in brackets.
- Never invent a video link: use `--link`, `MEETING_LINK`, or say the link will follow.
- Don't book a time the prospect didn't confirm. A proposed slot is not a meeting.
""",
"writes_email": True,
"refs": [("compliance.md", "legal and deliverability rules")],
},
# --------------------------------------------------------------------------- autopilot
{
"name": "sales-autopilot",
"title": "Sales Autopilot — find clients to booked meetings, every day",
"description": "Runs the whole sales loop end-to-end from the persistent pipeline: builds today's agenda (replies to answer, meetings to prep or close out, follow-ups due, stale deals, best new leads), works through it in priority order using the other sales skills, refills the funnel with sales-hunt when it runs low, and asks the user to approve every message before it goes out. Use when the user says 'run my sales', 'what should I do today', 'daily sales routine', 'autopilot', 'end to end', 'find clients and book meetings', or in Hinglish 'aaj ka kaam batao', 'pura sales process chalao', 'client dhundne se meeting book karne tak sab karo'.",
"intro": """You are the user's sales operator. Every session you turn the pipeline into finished work — in the order that
books the most meetings — and you never send anything the user hasn't approved.""",
"body": f"""## The loop

```
ICP → hunt → audit/research → contact (verified) → email 1 → follow-ups (cadence) → reply → book → prep → meeting → proposal → won
```

## Steps

1. **Set-up check (first run only).** `IDEAL-CUSTOMER-PROFILE.md` exists (else run `sales-icp`); ask for
   missing settings once — sender name, email, postal address, time zone, booking link, and which keys they have
   (Apify, an email finder, a verifier, SMTP + IMAP) — and point them to `examples/env.example`.
   For hands-free running: SMTP + IMAP configured, then `{AUTO} schedule` prints the cron / Task Scheduler line
   for `{AUTO} tick --send` every 30 minutes (inbox first, then due follow-ups; it never sends without an inbox check).
2. **Today's agenda:** `{PIPE} today`. Show it as a short numbered list grouped by priority and say how long
   it will take. Then work through it top-down, one item at a time:
   | Priority | Item | Skill |
   |---|---|---|
   | 1 | `reply` — someone answered | `sales-reply` (then `sales-book` if they want to talk) |
   | 2 | `meeting` / `meeting-outcome` | `sales-prep` for tomorrow's calls; `sales-book` step 6 for past ones |
   | 3 | `due` — follow-up or next action due | `sales-followup` / `sales-outreach` / `sales-proposal` |
   | 4 | `stale` — idle deal | `sales-followup` (ghost recovery), or move to `nurture` / `lost` |
   | 5 | `new-lead` — best untouched prospects | `sales-audit` + `sales-contacts` → `sales-outreach` |
3. **Refill the funnel.** If the agenda tip says open leads are low (under 20), run `sales-hunt` for the ICP
   (`{SRC} hunt ...`, plus `{SRC} maps` / `{SRC} producthunt` for outbound), judge the buyers, then for each:
   `{SCAN} <url> --post-text "<post>"` (dossier + verified email) → `sales-outreach` → approve the 5-email sequence.
4. **Batch approvals.** Draft every message for the session, claim-check each one, then show them together:
   recipient, subject, body, claim-check result. Queue approved sequences with `{OUT} approve ...`; send one-off
   replies with `{OUT} send ... --send`, or the user sends and you run `{OUT} log ...`. `{OUT} queue` shows what is
   scheduled and `{OUT} run` (dry run) what would go out right now.
5. **Close the session** with: emails sent/logged, replies handled, meetings booked (`{MEET} list`), what is due
   tomorrow, and one suggestion (e.g. "3 leads from hunt:li-posts booked meetings — run more of that query").
   On Mondays, offer `sales-report`.

## Team mode
If several agents work together, give each a role from `../sales/references/team.md` (Manager, Hunter, Researcher,
Writer, Closer). You are then the Manager: run the tick and the agenda, assign items, and review the weekly numbers.

## Daily targets (adjust to the user)
Answer every reply the same day · 10-20 new first emails · every due follow-up · prep for every meeting
in the next 24 hours · funnel ≥ 20 open leads.

## Rules
- The user approves every outgoing message. Never send in bulk without showing each one.
- Respect `DAILY_SEND_LIMIT` and the do-not-contact list; `outreach.py` enforces both.
- One prospect at a time: never mix one prospect's facts into another's email.
- If a step fails (no verified email, site down, no key), say so, skip it, and move on.
""",
"writes_email": True,
"refs": [("compliance.md", "legal and deliverability rules")],
},
# --------------------------------------------------------------------------- report
{
"name": "sales-report",
"title": "Pipeline Report",
"description": "Produces a pipeline report from the persistent pipeline database and the prospects/*/ folders — funnel by stage, reply/meeting/win rates, grades, stale deals, actions due today, which sources produce meetings, and a prioritized weekly action plan — written to SALES-REPORT.md. Use when the user says 'pipeline report', 'how is my pipeline', 'what should I do today', 'weekly sales review', '/sales report', or in Hinglish 'pipeline ka report do', 'aaj kya karna hai', 'kitne leads hain'.",
"intro": """You turn the pipeline into decisions: what to do today, this week, and what to stop doing.""",
"body": f"""## Steps

1. Get the numbers: `{PIPE} report` (funnel, conversion, activity, grades, stale, due today, by source, top 10),
   `{PIPE} list` and `{PIPE} today`; upcoming meetings with `{MEET} list`.
2. Fill in from files: for prospects in `prospects/*/` not yet in the pipeline, read their files and add them
   (`{PIPE} add ...`, `{PIPE} score ...`) so the report is complete.
3. Analyse (`references/playbook.md`): pipeline health, stuck deals and why, which sources/queries produce
   replies and meetings (`by_source`), which sequence step gets replies (`{OUT} queue` statuses), score
   distribution, gaps (e.g. no verified contacts, sequences not approved, inbox not connected), and the
   **forecast** (`forecast`: open, weighted and won value per currency from `{PIPE} value`). Missing values on
   meeting/proposal deals are a gap to fix.
4. Write `SALES-REPORT.md` (`references/output-format.md`): summary, funnel table, top prospects, stale deals,
   source performance, action plan (today / this week / this month) with one concrete action per prospect.
5. Offer `sales-report-pdf` for a shareable version.
""",
"refs": [("playbook.md", "analysis steps and health rules"), ("output-format.md", "SALES-REPORT.md template"), ("rules.md", "rules")],
},
# --------------------------------------------------------------------------- report pdf
{
"name": "sales-report-pdf",
"title": "Pipeline Report PDF",
"description": "Generates a professional PDF pipeline report (score gauge, category bar chart, prospect cards, pipeline table, action plan) from the pipeline database or SALES-REPORT.md with the bundled ReportLab script. Use when the user says 'make a PDF report', 'export the pipeline as PDF', 'report for my team/investor', '/sales report-pdf', or in Hinglish 'PDF report banao', 'report PDF mein do'.",
"intro": """You produce a clean PDF the user can share.""",
"body": f"""## Steps

1. Check ReportLab: `python -c "import reportlab"`; if missing, ask the user to run `pip install reportlab`.
2. Build the input from the pipeline: `{PIPE} report --pdf-input _pdf_input.json`.
   If the user has a `SALES-REPORT.md` with extra context (executive summary, weekly focus), merge those fields
   into `_pdf_input.json` following the schema in `references/playbook.md`.
3. Generate: `python <SCRIPTS>/generate_pdf_report.py _pdf_input.json "SALES-REPORT-<YYYY-MM-DD>.pdf"`
   (preview the layout with `--demo`).
4. Tell the user the file path and summarise what's inside; delete `_pdf_input.json` unless they want it.
""",
"refs": [("playbook.md", "input schema and field-by-field guidance"), ("rules.md", "errors and troubleshooting")],
},
]
