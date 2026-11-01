"""Specs for every skill. Edit here, then run tools/build_skills.py."""

PIPE = "python <SCRIPTS>/pipeline.py"

SKILLS = [
# --------------------------------------------------------------------------- router
{
"name": "sales",
"title": "AI Sales Team — Router",
"description": "AI sales team for B2B prospecting and agency client hunting: find people publicly asking for a service, research and score prospects, find and verify decision makers, write compliant cold emails and follow-ups, prep meetings, write proposals, handle objections, track a persistent pipeline and produce reports/PDFs. Use when the user says 'sales', '/sales <command>', 'find me leads', 'prospect this company', 'write a cold email', 'pipeline report', or in Hinglish 'clients dhundo', 'leads chahiye', 'is company ko email likho', 'meeting ki taiyari karo'.",
"intro": """You coordinate a team of sales skills. Work out what the user needs, then follow the matching skill.
Every skill works in any agent: they use shell commands (`python <SCRIPTS>/...`), files and your reasoning.""",
"body": """## Which skill to use

| The user wants... | Skill | Main output |
|---|---|---|
| To define who to sell to (**start here**) | `sales-icp` | `IDEAL-CUSTOMER-PROFILE.md` |
| People publicly asking for what they sell (intent leads) | `sales-hunt` | scored candidates → pipeline |
| A full scored audit of one company | `sales-prospect` | `prospects/<slug>/PROSPECT-ANALYSIS.md` |
| A fast 60-second estimate | quick snapshot (below) | terminal only |
| Fact-only website audit (proof-of-work for outreach) | `sales-audit` | `prospects/<slug>/SITE-AUDIT.json` + `.md` |
| Company research / firmographics | `sales-research` | `COMPANY-RESEARCH.md` |
| BANT + MEDDIC qualification | `sales-qualify` | `LEAD-QUALIFICATION.md` |
| Decision makers + verified emails | `sales-contacts` | `DECISION-MAKERS.md` |
| What they use today + battle cards | `sales-competitors` | `COMPETITIVE-INTEL.md` |
| Cold email + LinkedIn sequence | `sales-outreach` | `OUTREACH-SEQUENCE.md` |
| Follow-ups after a meeting/demo/proposal/silence | `sales-followup` | `FOLLOWUP-SEQUENCE.md` |
| Meeting preparation brief | `sales-prep` | `MEETING-PREP.md` |
| Client proposal with pricing options | `sales-proposal` | `CLIENT-PROPOSAL.md` |
| Objection handling scripts | `sales-objections` | `OBJECTION-PLAYBOOK.md` |
| Pipeline report | `sales-report` | `SALES-REPORT.md` |
| Pipeline report as PDF | `sales-report-pdf` | `SALES-REPORT-<date>.pdf` |

If your agent supports slash commands, `/sales <command> <input>` maps to `sales-<command>`. If the request is
unclear, show this table and suggest `sales-icp` first. To use a skill, read its `SKILL.md` (a sibling folder of
this one) and follow it; its instructions take precedence over this router.

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
| `pipeline.py` | Persistent pipeline: add, score, stage, contact, note, attach, next, report |
| `intent_scan.py` | Find + score posts asking for a service (EN/HI/Hinglish; Bright Data optional) |
| `site_audit.py` | Fact-only website audit (each fact with evidence) |
| `find_email.py` | Find + verify contact emails (Hunter optional; guesses always labelled) |
| `claim_check.py` | Flags sentences in a draft that no evidence supports |
| `fetch_page.py` / `web_search.py` | Web access for agents without web tools |
| `analyze_prospect.py` | Site scrape → industry, tech, hiring, team, pricing, size signals |
| `contact_finder.py` | Team/leadership extraction with seniority and buying role |
| `lead_scorer.py` | Deterministic BANT/MEDDIC score, or `--mode agency` buyer score |
| `generate_pdf_report.py` | PDF pipeline report (needs `pip install reportlab`) |

API keys (all optional) go in environment variables or `~/.ai-sales-team/.env`, never in files you write:
`BRIGHTDATA_API_KEY`, `BRIGHTDATA_ZONE`, `HUNTER_API_KEY`.

## Typical week

```
sales-icp          "We build websites and SEO for clinics and restaurants in India, US and UK"
sales-hunt         find people asking for that this week → judge → pipeline
sales-prospect     https://bestlead.com          (deep audit of the best ones)
sales-audit        https://bestlead.com          (proof-of-work facts)
sales-outreach     bestlead.com                  (claim-checked first email + sequence)
sales-followup / sales-prep / sales-proposal      as deals move
sales-report       weekly pipeline review
```
""",
"before": True,
"refs": [],
},
# --------------------------------------------------------------------------- hunt
{
"name": "sales-hunt",
"title": "Intent Hunt — find people asking for what you sell",
"description": "Finds public posts (LinkedIn, Reddit, Facebook groups, forums) where someone is actively asking to hire a service the user sells — website, app, SEO, marketing, design, software — scores them in English, Hindi and Hinglish, filters out sellers, job seekers and job ads, judges real buyers with a labelled rubric and adds them to the pipeline. Use when the user says 'find leads', 'find people looking for a web developer', 'who needs an agency', 'hunt for clients', or in Hinglish 'clients dhundo', 'leads chahiye', 'kaun website banwana chahta hai', 'developer chahiye wale posts dhundo'.",
"intro": """Intent beats cold lists: a person who wrote "need a website for my clinic" this week is worth fifty
cold contacts. This skill finds those posts, separates real buyers from noise, and puts them in the pipeline.""",
"body": f"""## Steps

1. **Know the offer.** Read `IDEAL-CUSTOMER-PROFILE.md` or ask what services, which countries, which languages.
2. **Collect posts** — any of these:
   - With a Bright Data key: `python <SCRIPTS>/intent_scan.py --serp --lookback 7 --max-calls 10 [--country in] --save hunt.json`
     (`--list-queries` shows the default X-ray queries; add your own with `--query '...'`, repeatable).
   - Without a key: search yourself (your web tool, or ask the user to paste posts) for queries like those in
     `references/queries.md`, save posts one per line or as JSON lines (`url`, `text`, `author`) and run
     `python <SCRIPTS>/intent_scan.py --file posts.jsonl --save hunt.json`.
   - One post: `python <SCRIPTS>/intent_scan.py --text "..."`.
   The scanner skips posts seen in earlier runs and rejects sellers, job seekers and job ads for free.
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
6. **Find a contact** for the top buyers: `python <SCRIPTS>/find_email.py --text "<post text>" [--domain <site>] [--first X --last Y]`,
   then `{PIPE} contact <slug> --name ... --email ... --email-status <status> --source <source>`.
   No verified email? Suggest the user reply publicly under the post or DM from their own account — give
   them a 2-line message. Never post or DM on their behalf.
7. **Report**: a table — buyer, what they need, quote, score, contact status, suggested next step
   (`sales-audit` then `sales-outreach` for the best ones).

## Rules
- The quote must be copied exactly from the post. No quote = not a buyer.
- Agencies advertising, freelancers offering services, "#hiring" job posts and job seekers are never buyers.
- Respect each platform's terms: only public posts, no scraping behind logins, no automated messaging.
- Paid search calls are capped by `--max-calls`; tell the user how many calls a run used.
""",
"refs": [("intent-rubric.md", "30 labelled examples (EN + Hinglish): buyers, sellers, job seekers, spam"),
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
   (add `--no-links` for a faster run; robots.txt is respected).
2. Write `prospects/<slug>/SITE-AUDIT.md`: the URL, date, and a table of every fact (`statement` + `evidence`).
3. Pick the **top 3 observations** that matter to the prospect's business, using
   `references/fact-to-hook.md` (e.g. no viewport → phone visitors get the desktop layout; no CTA →
   visitors don't know the next step; copyright 2019 → site looks unmaintained). State the fact exactly as the
   audit does; any consequence you add must be phrased as likely ("so phone visitors probably..."), never as a
   measured number.
4. Record it: `{PIPE} add --url <url>` (if new), `{PIPE} attach <slug> prospects/<slug>/SITE-AUDIT.json --kind site-audit`,
   `{PIPE} note <slug> "Audit hooks: <hook 1>; <hook 2>"`.
5. Suggest `sales-outreach` next — it will use these facts as evidence.

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

1. **Discovery** (see `references/playbook.md` Phase 1): fetch the homepage and key pages, detect company type
   and industry, run `python <SCRIPTS>/analyze_prospect.py --url <url>` and
   `python <SCRIPTS>/site_audit.py --url <url> --save prospects/<slug>/SITE-AUDIT.json`, read any existing
   files in `prospects/<slug>/`, and write a short discovery briefing.
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

1. Fetch the homepage, about, team, careers, pricing/services, blog/news pages (several at once:
   `python <SCRIPTS>/fetch_page.py <url1> <url2> ...`). Run `python <SCRIPTS>/analyze_prospect.py --url <url>`.
2. Search for recent news, funding/expansion, leadership and reviews (your search tool or `web_search.py`).
3. Cover the 8 dimensions in `references/playbook.md`. Adapt to the business type: for a local business or
   SMB focus on owner, locations, reviews, website quality and marketing activity; for SaaS on product,
   pricing, team growth; for e-commerce on catalogue, platform, channels.
4. Write `prospects/<slug>/COMPANY-RESEARCH.md` using `references/output-format.md`, with a source for each fact.
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
4. Write `prospects/<slug>/LEAD-QUALIFICATION.md` (`references/output-format.md`), including the 3-5
   discovery questions that would close the biggest gaps.
5. Record: `{PIPE} score <slug> <score>`, `{PIPE} stage <slug> qualified --reason "<grade + main reason>"`
   (or `disqualified` / `nurture`), `{PIPE} next <slug> "<next step>"`.
""",
"refs": [("playbook.md", "BANT and MEDDIC rubrics with scoring guidance"), ("output-format.md", "LEAD-QUALIFICATION.md template"),
         ("rules.md", "terminal output, errors, cross-skill use")],
},
# --------------------------------------------------------------------------- contacts
{
"name": "sales-contacts",
"title": "Decision Makers & Verified Contacts",
"description": "Maps the buying committee at a prospect — names, titles, buying roles, personalization anchors, warm paths and a multi-threading plan — and finds and verifies contact emails with find_email.py (Hunter optional; guesses always labelled pattern-guessed), writing DECISION-MAKERS.md and saving contacts to the pipeline. Use when the user says 'who should I contact', 'find the decision maker', 'get their email', 'who is the owner', '/sales contacts', or in Hinglish 'owner kaun hai', 'iska email nikalo', 'kisse baat karun'.",
"intro": """You find the right people and the safest way to reach them. A wrong or guessed address costs
deliverability, so verification status is always shown.""",
"body": f"""## Steps

1. **People**: run `python <SCRIPTS>/contact_finder.py --url <url>`, read the team/about pages, and search
   for leaders (e.g. `site:linkedin.com/in "<company>" founder OR owner OR director`). Only list people you
   found evidence for.
2. **Roles**: classify each as Economic Buyer, Champion, Technical Evaluator, User, Influencer or Blocker
   (`references/playbook.md` Phase 2). For an owner-run SMB the owner is usually buyer and champion.
3. **Emails**: for the top 1-3 people run
   `python <SCRIPTS>/find_email.py --domain <domain> --first <first> --last <last>`.
   Use the status exactly as returned: `verified`, `catch_all`, `unverified`, `pattern-guessed`, `invalid`.
   Only `verified` addresses are safe for cold email; say so.
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
   reports the platform), footer credits ("Designed by ..."), job posts, case studies, review sites.
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

1. **Evidence first.** Collect what you know: their post (if they asked publicly), `prospects/<slug>/` files,
   `SITE-AUDIT.json` (run `sales-audit` if missing), `DECISION-MAKERS.md` and the pipeline record
   (`{PIPE} show <slug>`). Recipient must have a `verified` email, or say clearly that it isn't.
2. **First email** — follow `references/first-email-guide.md`: plain text, under 120 words, mentions their post
   or business naturally, ONE specific observation backed by evidence, one soft CTA (a 15-minute call), the
   user's signature with postal address and an opt-out line.
3. **Sequence** — 4 follow-ups and LinkedIn touches using `references/playbook.md` (frameworks, timing,
   breakup email) and the templates `references/template-outreach-cold.md`, `-warm.md`, `-referral.md`.
   Use the warm or referral template only for a real, confirmed connection.
4. **Claim check** every email (see "Before anything is sent"); fix until it passes.
5. Write `prospects/<slug>/OUTREACH-SEQUENCE.md` (`references/output-format.md`).
6. Record: `{PIPE} attach <slug> prospects/<slug>/OUTREACH-SEQUENCE.md --kind outreach` and
   `{PIPE} next <slug> "Send email 1 (user)" --due <date>`. When the user confirms they sent it:
   `{PIPE} stage <slug> contacted --reason "email 1 sent"`.
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
   or nurture, and its cadence.
3. Write the emails plus LinkedIn/phone/SMS touches only where appropriate (SMS only for warm leads who
   shared their number). Reference real details from the conversation.
4. Claim-check every email.
5. Write `prospects/<slug>/FOLLOWUP-SEQUENCE.md` (`references/output-format.md`).
6. Record: `{PIPE} note <slug> "<what happened>"`, `{PIPE} next <slug> "<next touch>" --due <date>`, and update
   the stage (`replied`, `meeting`, `proposal`, `nurture`, `lost`) when the user tells you.
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

1. Load everything known: `{PIPE} show <slug>`, all files in `prospects/<slug>/` (post quote, SITE-AUDIT,
   research, contacts, outreach, replies the user pasted). Ask for the meeting time, attendees and goal if unknown.
2. Fill gaps with fresh research on the company and each attendee (`references/playbook.md` Step 1).
3. Build the brief (Step 2): cheat sheet first; then snapshot, attendees, their original request in their own
   words, audit facts, the conversation so far, qualification status (budget, timeline, decision maker, scope —
   mark unknowns), talking points, 10 discovery questions aimed at the unknowns, objections, landmines,
   success metrics, next steps to propose, and an agenda (Step 3) for 15/30/60 minutes.
4. Write `prospects/<slug>/MEETING-PREP.md` (`references/output-format.md`, `references/template-meeting-prep.md`).
5. Record: `{PIPE} stage <slug> meeting --reason "meeting <date>"` and `{PIPE} attach <slug> prospects/<slug>/MEETING-PREP.md --kind meeting-prep`.
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
   (e.g. Essential / Growth / Complete) anchored to the stated need; ROI only with explicit, conservative
   assumptions.
3. **Follow-up sequence** after sending (Step 3).
4. Claim-check the whole proposal and its emails.
5. Write `prospects/<slug>/CLIENT-PROPOSAL.md` (`references/output-format.md`).
6. Record: `{PIPE} stage <slug> proposal --reason "proposal sent <date>"`, attach the file, `{PIPE} next <slug> "Walkthrough offer" --due <date+2>`.
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
"description": "Generates word-for-word objection responses for calls, emails and chat — 15 universal objections, industry-specific and competitor objections, pricing tactics and prevention — tailored to what the user sells and, optionally, one prospect or industry, written to OBJECTION-PLAYBOOK.md. Includes Indian-market objections such as 'bahut mehenga hai' or 'mera bhatija website bana dega'. Use when the user says 'handle objections', 'they said it's too expensive', 'what do I say if', '/sales objections', or in Hinglish 'client bol raha hai mehenga hai', 'objection ka jawab do'.",
"intro": """You give the user exact words for the hard moments, true to their offer.""",
"body": f"""## Steps

1. Context (`references/playbook.md` Step 1): what the user sells, price points, the industry/prospect, the
   objections they actually hear.
2. Frameworks (Feel-Felt-Found, Acknowledge-Bridge-Close) and the 15 universal objections (Steps 2-3), each
   with a call version, an email version and a follow-up question.
3. Industry, competitive and pricing objections (Steps 4-6); prevention tactics (Step 7). For agencies include
   "my nephew/freelancer will do it cheaper", "we tried an agency before", "can you guarantee page 1?"
   (never promise rankings).
4. Write `OBJECTION-PLAYBOOK.md` in the working-directory root (or `prospects/<slug>/` for one prospect), using
   `references/template-objection-playbook.md`. Proof points must be real — otherwise `[ADD REAL CUSTOMER RESULT]`.
""",
"refs": [("playbook.md", "frameworks, 15 objections, industry/competitive/pricing, prevention"),
         ("output-format.md", "OBJECTION-PLAYBOOK.md format"), ("template-objection-playbook.md", "structural template"),
         ("rules.md", "rules")],
},
# --------------------------------------------------------------------------- icp
{
"name": "sales-icp",
"title": "Ideal Customer Profile",
"description": "Builds the Ideal Customer Profile every other sales skill scores against — firmographics, buying signals, pain points, budget qualifiers, negative ICP, scoring rubric, 2-3 buyer personas, channels and the intent phrases buyers use (English, Hindi, Hinglish) — from a description of what the user sells, written to IDEAL-CUSTOMER-PROFILE.md. Use when the user says 'build my ICP', 'who should I target', 'ideal customer', 'I sell X to Y', '/sales icp', or in Hinglish 'mera ideal client kaun hai', 'kisko target karun'.",
"intro": """Start here. Every fit score in the other skills is only as good as this profile.""",
"body": f"""## Steps

1. Parse what the user sells: services/products, price ranges, delivery capacity, markets (e.g. India + US/UK/AU),
   languages, best past clients. Ask for anything missing in one short message.
2. Research the market briefly (`references/playbook.md` Research Phase) — who buys this, where they talk.
3. Build the framework (Steps 2-7): firmographics, technographics, behavioural and **intent signals** (the exact
   phrases buyers post, e.g. "need a website for my clinic", "website banwana hai", "koi SEO wala batao"),
   pain map, budget qualifiers, channels, negative ICP, a 0-100 scoring rubric, 2-3 personas, prospecting playbook.
4. Write `IDEAL-CUSTOMER-PROFILE.md` in the working-directory root (`references/output-format.md`). Include a
   "Search queries" section with 5-10 X-ray queries for `sales-hunt`.
""",
"refs": [("playbook.md", "the 7 ICP steps and rubric"), ("output-format.md", "IDEAL-CUSTOMER-PROFILE.md template"), ("rules.md", "quality rules")],
},
# --------------------------------------------------------------------------- report
{
"name": "sales-report",
"title": "Pipeline Report",
"description": "Produces a pipeline report from the persistent pipeline database and the prospects/*/ folders — funnel by stage, reply/meeting/win rates, grades, stale deals, actions due today, which sources produce meetings, and a prioritized weekly action plan — written to SALES-REPORT.md. Use when the user says 'pipeline report', 'how is my pipeline', 'what should I do today', 'weekly sales review', '/sales report', or in Hinglish 'pipeline ka report do', 'aaj kya karna hai', 'kitne leads hain'.",
"intro": """You turn the pipeline into decisions: what to do today, this week, and what to stop doing.""",
"body": f"""## Steps

1. Get the numbers: `{PIPE} report` (funnel, conversion, grades, stale, due today, by source, top 10) and
   `{PIPE} list`.
2. Fill in from files: for prospects in `prospects/*/` not yet in the pipeline, read their files and add them
   (`{PIPE} add ...`, `{PIPE} score ...`) so the report is complete.
3. Analyse (`references/playbook.md`): pipeline health, stuck deals and why, which sources/queries produce
   replies and meetings, score distribution, gaps (e.g. no verified contacts).
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
