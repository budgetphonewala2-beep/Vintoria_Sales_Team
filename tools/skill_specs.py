"""Specs for the 8 Vintoria sales skills. Edit here, then run tools/build_skills.py (and tools/validate_skills.py)."""

PIPE = "python <SCRIPTS>/core/pipeline.py"
PROF = "python <SCRIPTS>/core/seller_profile.py"
OUT = "python <SCRIPTS>/outreach/outreach.py"
CLAIM = "python <SCRIPTS>/outreach/claim_check.py"
LINT = "python <SCRIPTS>/outreach/email_lint.py"
MEET = "python <SCRIPTS>/replies/meeting.py"
TRIAGE = "python <SCRIPTS>/replies/reply_triage.py"
INBOX = "python <SCRIPTS>/replies/inbox.py"
SRC = "python <SCRIPTS>/leads/lead_sources.py"
SERP = "python <SCRIPTS>/leads/serp.py"
QL = "python <SCRIPTS>/leads/query_library.py"
SCORE = "python <SCRIPTS>/leads/lead_scorer.py"
POST = "python <SCRIPTS>/leads/post_lead.py"
INTENT = "python <SCRIPTS>/leads/intent_scan.py"
SCAN = "python <SCRIPTS>/research/prospect_scan.py"
AUDIT = "python <SCRIPTS>/research/site_audit.py"
FIND = "python <SCRIPTS>/research/find_email.py"
FETCH = "python <SCRIPTS>/research/fetch_page.py"
LEARN = "python <SCRIPTS>/ops/learn.py"
AUTO = "python <SCRIPTS>/ops/autopilot.py"

SERVICES = [("services-01-strategy.md", "01 Strategy & Consulting (001-015)"), ("services-02-web.md", "02 Web Development (016-040)"),
            ("services-03-saas.md", "03 SaaS & Digital Products (041-060)"), ("services-04-mobile.md", "04 Mobile App Development (061-080)"),
            ("services-05-design.md", "05 UI/UX & Product Design (081-102)"), ("services-06-branding.md", "06 Branding & Creative (103-120)"),
            ("services-07-ai.md", "07 AI Development (121-145)"), ("services-08-automation.md", "08 Business Automation (146-167)"),
            ("services-09-backend.md", "09 Backend, API & Cloud (168-190)"), ("services-10-ecommerce.md", "10 E-Commerce (191-210)"),
            ("services-11-marketing.md", "11 Digital Marketing & SEO (211-236)"),
            ("services-12-growth.md", "12 Growth, Analytics & Continuous Development (237-270)")]

SKILLS = [
# =========================================================================== 1. router + daily operator
{
"name": "vintoria-sales",
"title": "Vintoria Sales — the operator",
"description": "Vintoria's sales operator and the entry point to every Vintoria sales skill: runs the whole loop from finding buyers to booked meetings and signed deals for Vintoria, a digital product studio selling 270 services (web, apps, SaaS, UI/UX, branding, AI, automation, cloud, e-commerce, SEO and marketing, growth) to SMBs in India, the US, UK and Australia. Builds today's agenda from the pipeline (replies, fresh buyer posts, meetings, due follow-ups, stale deals) and works it in priority order, routes any sales request to the right skill, and holds the shared truth, pricing, quality and compliance rules. Use it whenever the user talks about sales, clients, leads, prospects, the pipeline or their day, even without naming a skill: 'what should I do today', 'run my sales', 'find clients', 'is lead ka kya karein', or Hinglish 'aaj ka kaam batao', 'clients dhundo', 'leads chahiye', 'pura sales process chalao'.",
"profile": "soft",
"intro": """You run Vintoria's sales desk. Every session you turn the pipeline into finished work in the order that books
the most meetings, you pick the right skill for each job, and you never send anything the user hasn't approved.""",
"body": f"""## The skills

| Job | Skill | Main output |
|---|---|---|
| Set up Vintoria's profile, offer lanes and ideal customer (**first run**) | `vintoria-setup` | `SELLER-PROFILE.json`, `OFFER.md`, `IDEAL-CUSTOMER-PROFILE.md` |
| Find people publicly asking for what Vintoria sells | `vintoria-lead-hunt` | judged, scored buyers in the pipeline |
| Everything about one prospect: deep scan, site audit, research, contacts + verified email, qualification, competitors, full scored analysis | `vintoria-prospect-research` | `prospects/<slug>/DOSSIER.md` and friends |
| First email + 5-email sequence, follow-ups after silence/meetings/proposals | `vintoria-outreach` | claim-checked `SEQUENCE.json`, queued after approval |
| A prospect replied; book the meeting | `vintoria-reply-book` | answer drafted, stage updated, `.ics` invite |
| Meeting prep + discovery call, proposal, objections, negotiation, handoff, upsell and referrals | `vintoria-close` | `MEETING-PREP.md`, `CLIENT-PROPOSAL.md`, `OBJECTION-PLAYBOOK.md` |
| Pipeline report, what's working, PDF | `vintoria-report` | `SALES-REPORT.md`, `SALES-REPORT-<date>.pdf` |

To use a skill, read its `SKILL.md` (a sibling folder of this one) and follow it — its steps win over this page. If a
request is unclear, show this table; if `{PROF} check` isn't `Ready.`, start with `vintoria-setup`.

```
setup → lead-hunt → prospect-research (dossier + verified email) → outreach (approve 5 emails)
  → autopilot sends day 0/3/7/14/28 → reply-book (answer, book) → close (prep, discovery, proposal, sign, expand)
```

## Run the day ("aaj ka kaam")

1. **Where are we:** `{PIPE} status` (never spends: profile, keys, funnel, queue, sending health, fresh leads), then
   `{PIPE} today`. Show the agenda as a short numbered list by priority with a time estimate, then work it top-down:
   | Priority | Item | Skill |
   |---|---|---|
   | 1 | `reply` — someone answered | `vintoria-reply-book` (reply within the hour) |
   | 1 | `fresh-leads` — new buyer posts | `vintoria-lead-hunt` step 3 — judge newest first, answer the same session |
   | 2 | `meeting` / `meeting-outcome` | `vintoria-close` (prep for tomorrow; outcome for past calls) |
   | 3 | `due` — follow-up or next action | `vintoria-outreach` / `vintoria-close` |
   | 4 | `stale` — idle deal | `vintoria-outreach` ghost recovery, or `nurture` / `lost` |
   | 5 | `new-lead` — best untouched prospects | `vintoria-prospect-research` → `vintoria-outreach` |
2. **Refill the funnel** when the agenda says open leads are under 20: `vintoria-lead-hunt`, then deep-scan the buyers.
3. **Batch approvals.** Draft every message of the session, claim-check each, then show them together (recipient,
   subject, body, claim-check result, quality score). Queue approved sequences with `{OUT} approve ...`.
4. **Close the session:** sent/logged, replies handled, meetings booked (`{MEET} list`), what is due tomorrow, and one
   concrete suggestion. Mondays: `vintoria-report` and `{LEARN} report --apply`.

Hands-free: with SMTP + IMAP set, `{AUTO} schedule` prints the cron / Task Scheduler line for `{AUTO} tick --send` every
30 minutes — inbox first, then due follow-ups; a prospect who replied never gets another automated email.

## Quick snapshot (no files)
Fetch the homepage (plus `/about` or `/pricing` if thin), judge fit against `IDEAL-CUSTOMER-PROFILE.md`, name the 1-3
catalog services that match what you saw, and answer in under 30 lines: score + grade, top 3 opportunities, top 3 concerns,
the skill to run next. Say it is an estimate from 1-2 pages.

## One grade scale everywhere
| Score | Grade | Meaning |
|---|---|---|
| 90-100 | A+ | Hot — act today |
| 75-89 | A | Strong — worth real effort |
| 60-74 | B | Qualified — standard approach |
| 40-59 | C | Lukewarm — nurture |
| 0-39 | D | Poor fit — deprioritise |

## The engine (`<SCRIPTS>` = this skill's `scripts/` folder)

| Folder | Scripts |
|---|---|
| `core/` | `pipeline.py` (status, today, add, find, show, score, stage, contact, note, attach, next, value, where, report, suppress), `seller_profile.py` (init --preset vintoria, check, questions, show, set), `sales_common.py` |
| `leads/` | `serp.py` (Bright Data: watch, hunt, fresh), `lead_sources.py` (Apify, Apollo, Maps, Reddit, HN, research), `query_library.py`, `intent_scan.py`, `post_lead.py`, `lead_scorer.py` |
| `research/` | `prospect_scan.py` (deep scan → DOSSIER), `site_audit.py` (+ PageSpeed), `find_email.py` (finder + verifier waterfall), `contact_finder.py`, `analyze_prospect.py`, `fetch_page.py`, `web_search.py` |
| `outreach/` | `outreach.py` (approve, run, send, log, queue, doctor, whatsapp), `claim_check.py`, `email_lint.py`, `mailboxes.py` |
| `replies/` | `inbox.py` (IMAP, read-only), `reply_triage.py`, `meeting.py` (slots in both zones, `.ics`, outcomes) |
| `ops/` | `autopilot.py` (tick, schedule), `learn.py`, `notify.py`, `generate_pdf_report.py` |

API keys and settings live only in `~/.ai-sales-team/.env` (template: `examples/env.example`): `BRIGHTDATA_API_KEY` +
`BRIGHTDATA_ZONE` (main lead engine), `APIFY_TOKEN`, a finder (`PROSPEO_API_KEY`, `FINDYMAIL_API_KEY`, `HUNTER_API_KEY`,
`APOLLO_API_KEY`), a verifier (`MILLIONVERIFIER_API_KEY`, `ZEROBOUNCE_API_KEY`, `NEVERBOUNCE_API_KEY`), `SMTP_*`, `IMAP_*`,
`BOOKING_URL`, `MEETING_LINK`, `TIMEZONE`, `DAILY_SEND_LIMIT`, alert channels (`TELEGRAM_BOT_TOKEN`, `SLACK_WEBHOOK_URL`).

## Working as a team
One agent can run every step; several agents can split the roles (Manager, Hunter, Researcher, Writer, Closer) and hand
off through pipeline stages — `references/team.md`.

## Rules
- The user approves every outgoing message; a sequence is approved once, as a whole.
- Respect `DAILY_SEND_LIMIT` and the do-not-contact list; `outreach.py` enforces both.
- One prospect at a time; never mix one prospect's facts into another's email.
- If a step fails (no verified email, site down, no key), say so, skip it and move on.
""",
"writes_email": True,
"refs": [("team.md", "roles, handoffs, daily and weekly rhythm, targets, ownership rules"),
         ("truth-rules.md", "what counts as evidence, every place an agent could invent facts and the guard that stops it"),
         ("quality-bar.md", "the scores an email, dossier and proposal must reach before anyone sees them"),
         ("pricing-policy.md", "the catalog has no prices: what you may and may not say about money"),
         ("service-catalog.md", "the 12 disciplines, how to cite a service, what the catalog covers")]
       + [(f, f"discipline {d}: every service, signals, who buys it, when not to sell it") for f, d in SERVICES]
       + [("compliance.md", "legal and deliverability rules for every message")],
},
# =========================================================================== 2. setup
{
"name": "vintoria-setup",
"before": False,
"title": "Vintoria Setup — profile, offer lanes and ideal customer",
"description": "Sets Vintoria up before any prospecting: interviews the user and saves SELLER-PROFILE.json (sender identity, postal address, time zone, active service disciplines from the 270-service catalog, niches, target markets in India, US, UK and Australia, deal size and currency, real case studies, differentiators, buyer pains and triggers), then builds OFFER.md (3-5 offer lanes mapped to exact catalog service IDs, active vs dormant disciplines, a claim-by-claim proof map) and IDEAL-CUSTOMER-PROFILE.md (firmographics, buying signals, personas, scoring rubric, the exact search queries). Every query, email and proposal in the other Vintoria skills is built from these files. Use it at the start of a workspace, whenever SELLER-PROFILE.json is missing or incomplete, or when the user says 'set up', 'onboard me', 'build my ICP', 'which services should we push', 'who should we target', 'change our niche', or Hinglish 'setup karo', 'mera ideal client kaun hai', 'humein kya bechna chahiye', 'profile banao'.",
"intro": """Nothing good comes from generic queries and generic emails. You learn Vintoria's business properly once, save it,
and every agent after you builds on the same facts.

`<SCRIPTS>` is `../vintoria-sales/scripts/`. The catalog is `../vintoria-sales/references/service-catalog.md`; prices
follow `../vintoria-sales/references/pricing-policy.md`; never write a fact the user didn't give you.""",
"body": f"""## Steps

1. **What exists:** `{PROF} check`. `Ready.` → show a 5-line summary and ask only what changed. Missing →
   `{PROF} init --preset vintoria` (fills what the catalog already says: the services, India + US/UK/AU, English + Hindi,
   buyer titles; everything else stays empty until the user answers).
2. **Interview** (`references/intake.md`; `{PROF} questions` lists every field and why it matters) in at most **3 short
   rounds**, grouped, each question with an example answer — never 25 at once:
   - Round 1 — Vintoria: website, sender name + email, postal address, time zone; which of the 12 disciplines are
     **active** this month (staffed, with proof) vs dormant; the offer in one line; niches.
   - Round 2 — the buyer: countries and cities (India / US / UK / AU), buyer titles, company size, deal size +
     currency per market (INR for India, USD/GBP/AUD abroad), pains right before they hire, buying triggers, tools they leave.
   - Round 3 — proof: 2-3 real results (client, result, link) per active discipline, portfolio, years / projects / team,
     why Vintoria over freelancers and big agencies, any real guarantee, booking link.
   Accept "skip" for optional fields. Never fill an answer the user didn't give — case studies and prices especially.
3. **Read Vintoria's website** (if given) to pre-fill and confirm — not to invent.
4. **Save** each answer: `{PROF} set <field> '<json or text>'` (e.g. `{PROF} set offer.niches '["dental clinics", "D2C brands"]'`),
   then `{PROF} check` until `Ready.`
5. **Offer lanes** → `OFFER.md` in the working folder, following `references/offer-lanes.md`: 2-8 active disciplines,
   3-5 lanes (one buyer problem each, an entry service + 1-4 follow-on services by exact catalog ID), 2 observable
   disqualifiers per lane, a proof map (`Have` / `Partial` / `Missing` — outreach may only use `Have`), and positioning
   against freelancers and large agencies that contains only checkable claims.
6. **Ideal customer** → `IDEAL-CUSTOMER-PROFILE.md` (`references/icp-playbook.md`, `references/icp-output-format.md`):
   firmographics per market, intent phrases buyers really post (English and Hinglish — "need a website for my clinic",
   "website banwana hai", "koi SEO wala batao"), pains, budget qualifiers, negative ICP, a 0-100 rubric, 2-3 personas,
   and the **search queries** from `{QL}` worth keeping (LinkedIn boolean, X-ray, subreddits, Google Maps categories).
   Feed what you learn back: `{PROF} set signals.pains '[...]'` — the queries update by themselves.
7. **Keys:** `{PIPE} status` and `{FIND} --providers`. Tell the user which sources and automations are on, and the one
   key that would add the most (usually `BRIGHTDATA_API_KEY` + `BRIGHTDATA_ZONE`, then a verifier).
8. **Show the queries** (`{QL}`) and ask whether they look like Vintoria's buyers; adjust niches/pains until they do.
   Next: `vintoria-lead-hunt`.

## Rules
- The profile is the single source of truth for who Vintoria is. Emails may cite only proof that is in it.
- `OFFER.md` never holds prices; prices live in the profile, or are `[PRICE TO CONFIRM]`.
- No API keys in the profile — keys live only in `~/.ai-sales-team/.env`.
- Re-run whenever the offer, the active disciplines or the target market change.
""",
"refs": [("intake.md", "every interview question, why it matters, good vs weak answers, how answers become queries"),
         ("offer-lanes.md", "active/dormant disciplines, 3-5 offer lanes by catalog ID, the proof map, breadth positioning"),
         ("icp-playbook.md", "the 7 ICP steps and the scoring rubric"), ("icp-output-format.md", "IDEAL-CUSTOMER-PROFILE.md template"),
         ("rules.md", "quality rules for the ICP")],
},
# =========================================================================== 3. lead hunt
{
"name": "vintoria-lead-hunt",
"profile": "required",
"title": "Vintoria Lead Hunt — find people asking for what we sell",
"description": "Finds people publicly asking to hire a service Vintoria sells — website, app, SaaS, UI/UX, branding, AI chatbot or agent, automation and CRM, Shopify or e-commerce, SEO, ads and social media — on LinkedIn posts, Reddit, X, Facebook groups, Quora, Hacker News, Indie Hackers and Upwork, in English, Hindi and Hinglish, plus local businesses with a visible need from Google Maps and decision-maker lists from Apollo, all built from Vintoria's profile and offer lanes. Filters out agencies, freelancers, job seekers and job ads, judges every candidate with an exact quote, scores buyers, deep-researches the best and adds them to the pipeline, freshest first. Use it whenever the user wants more clients or leads, even without naming a platform: 'find leads', 'find people looking for a web developer', 'who needs an AI chatbot', 'hunt for clients this week', or Hinglish 'clients dhundo', 'leads chahiye', 'kaun website banwana chahta hai', 'developer chahiye wale posts dhundo'.",
"intro": """Intent beats cold lists: someone who wrote "need a website for my clinic" this week is worth fifty cold contacts.
You find those posts, separate real buyers from noise, and put them in the pipeline before anyone else answers.""",
"body": f"""## Steps

1. **Aim.** Read `OFFER.md` (the lanes and their entry services) and `{PROF} show`. Hunt one lane at a time — its
   services decide the queries. Map catalog disciplines to engine service codes:
   | Discipline | Codes | Discipline | Codes |
   |---|---|---|---|
   | 02 Web, 03 SaaS | `web`, `software` | 07 AI Development | `ai` |
   | 04 Mobile | `app` | 08 Business Automation | `automation` |
   | 05 UI/UX, 06 Branding | `design` | 09 Backend & Cloud, 01 Strategy | `software` |
   | 10 E-Commerce | `ecommerce` | 11 Marketing & SEO, 12 Growth | `seo`, `marketing` |
   Preview the queries: `{QL} --services ai,automation` (formula and sources: `references/queries.md`).
2. **Collect leads** with what the user has:
   | They have | Run | Gives |
   |---|---|---|
   | `BRIGHTDATA_API_KEY` + `BRIGHTDATA_ZONE` | **`{SERP} watch`** — newest posts since the last watch, never-seen only; or `{SERP} hunt --hours 24` / `--days 7` (`{SERP} providers` shows the cost) | **main source**: Google X-ray across LinkedIn posts, Reddit, Quora, X, FB groups, Indie Hackers, Upwork in the profile's countries, newest first, with exact post times |
   | `APIFY_TOKEN` | `{SRC} hunt --posted week --max 30 --save hunt.json` | LinkedIn post search, Hacker News, Reddit, X |
   | `APOLLO_API_KEY` or an Apollo connector | `{SRC} apollo-api --max 100` (or the connector with the profile's titles, countries, size, niches) | decision-maker lists (no intent) |
   | a local niche (clinics, restaurants, coaching) | `{SRC} maps --add` | businesses with no site / poor reviews + phone — strong in Indian cities |
   | nothing | `{SRC} hackernews`, `{SRC} reddit` (free); otherwise run `{QL}` queries in your own search, save posts as JSON lines (`url`, `text`, `author`) and `{INTENT} --file posts.jsonl --save hunt.json` | |
   Before a paid run, tell the user the ceiling (`APIFY_MAX_USD` × `APIFY_MAX_RUNS`, default $1 × 8); after it, what ran
   (`sources_run`, `by_source`, `kept_by_source`, `excluded_market`). A candidate with `contact_in_post` already has an
   email/phone — use it, don't pay a finder.
   **Freshness wins the client.** Work newest first (`age_hours`): under 6 h → judge, scan and answer this session;
   under 48 h → today; older than a week only if nobody has replied under it. Mark what you judged: `{SERP} judged <url> ...`.
3. **Judge every candidate** with `references/intent-rubric.md`: buyer / seller / job_seeker / other, services wanted
   (as catalog IDs where clear — "AI chatbot for my clinic" → `123 AI Chatbot Development`), urgency, budget (only if
   stated), location, and an **exact quote** that proves intent. Drop anything under confidence 0.6.
4. **Score buyers:** `{SCORE} --mode agency signals.json` (`intent_confidence`, `urgency`, `posted_days_ago`, `comments`,
   `budget_stated`, `services_requested`, `services_offered`, `email_status`, `sources_count`). Leave unknown fields out —
   unknowns score neutral; writing 0 would claim "posted today, no competition".
5. **Add to the pipeline** — their own website if the post or profile names one, else the post URL (becomes
   `name@platform`, so leads never merge):
   `{PIPE} add --url <site or post URL> --name "<person or company>" --source serp:<query id> --quote "<exact words>" --post-text "<the post>"`
   (the quote is checked word for word; a paraphrase is refused), then `{PIPE} score <slug> <score>`.
   `{PIPE} contact` takes the person's **profile** URL as `--linkedin`, never the post URL.
6. **Deep research on every buyer kept**, freshest first — one command per post:
   `{POST} --post-url <url> --post-text "<the post>" --author "<name>" --author-url <profile> --headline "<headline>" --source serp:<query-id> --quote "<exact words>"`
   (or all kept buyers: `{POST} --hunt hunt.json --only <url>,<url> --top 20`). It reads the post (email, phone, site —
   free), the author's profile, finds the company site (**never guessed**), runs the full deep scan and writes
   `prospects/<slug>/DOSSIER.md`. No verified email → give the user a 2-line public reply or DM to send themselves.
7. **Report:** buyer, platform, what they need (+ catalog service), exact quote, posted, score, contact status, next step.
   Fresh asks (< 48 h) get answered today — email if verified, otherwise the user's own public reply.

## Rules
- The quote is copied exactly from the post. No quote = not a buyer.
- Agencies, freelancers offering services, "#hiring" job posts and job seekers are never buyers.
- Only public posts; no scraping behind logins; never post, comment or DM for the user.
- Speed beats polish on intent leads: most asks get answered within a day or two.
""",
"refs": [("intent-rubric.md", "30 labelled examples (English + Hinglish): buyers, sellers, job seekers, spam"),
         ("queries.md", "the query formula, LinkedIn boolean rules, every source and what it is best for, signal searches")],
},
# =========================================================================== 4. prospect research
{
"name": "vintoria-prospect-research",
"profile": "required",
"title": "Vintoria Prospect Research — everything about one prospect",
"description": "Researches one prospect for Vintoria end to end: deep scan into DOSSIER.md (website audit with PageSpeed, company, people, best verified email, web research, ranked hooks), a fact-only website audit as proof-of-work, sourced company research, the buying committee with verified emails (finder + verifier waterfall; guesses always labelled), BANT/MEDDIC and agency-buyer qualification, current vendors and battle cards, and a full 0-100 scored analysis with five role playbooks — each hook mapped to the exact Vintoria catalog services it justifies. Use it whenever one company, website or person needs looking into before contact or a call: 'research acme.com', 'audit their website', 'who is the owner', 'get their email', 'is this a good lead', 'what do they use today', 'score this prospect', or Hinglish 'is company ke baare mein batao', 'website check karo', 'owner kaun hai', 'iska email nikalo', 'ye lead qualified hai kya'.",
"intro": """Outreach is only as good as the research under it. You turn one URL, post or name into facts with sources, a
verified way to reach the decision maker, and the 1-3 Vintoria services the evidence actually justifies.""",
"body": f"""## Pick the mode

| The user wants | Mode | Output in `prospects/<slug>/` |
|---|---|---|
| "Look into this lead" (default for any new prospect) | **Deep scan** | `DOSSIER.json` + `DOSSIER.md` |
| A hook / "what's wrong with their site" | **Site audit** | `SITE-AUDIT.json` + `SITE-AUDIT.md` |
| Background on the company | **Company research** | `COMPANY-RESEARCH.md` |
| Who to contact + their email | **Contacts** | `DECISION-MAKERS.md` |
| Is it worth our time | **Qualify** | `LEAD-QUALIFICATION.md` |
| What they use today / who their agency is | **Competitors** | `COMPETITIVE-INTEL.md` |
| A full scored audit with a first email | **Full analysis** | `PROSPECT-ANALYSIS.md` |

Always start from the deep scan when there is no `DOSSIER.json`; the other modes build on it.

## Deep scan
`{SCAN} <url> [--name "<company>"] [--post-text "<their post>"] [--city <city>]` — audit + PageSpeed, company, people,
best email (skipped if known), web research (reviews, news, hiring, complaints, ads, competitors) and ranked hooks. From
a buyer post use `{POST} ...` instead (see `vintoria-lead-hunt` step 6). Then add **Fit**: for each top hook name the
catalog service it justifies (no viewport + slow → `033 High-Performance Website Development`; no booking →
`028 Booking Platform Development`; manual enquiry handling → an automation service from discipline 08). The dossier must
reach 70 on the dossier score in `../vintoria-sales/references/quality-bar.md` before outreach.

## Site audit
`{AUDIT} --url <url> --save prospects/<slug>/SITE-AUDIT.json [--pagespeed] [--no-links]` (robots.txt respected). Write
`SITE-AUDIT.md` (URL, date, every `statement` + `evidence`) and pick the **top 3 observations** for this business with
`references/fact-to-hook.md` — the fact exactly as measured, any consequence hedged ("so phone visitors may…"), never a
guessed number. Local businesses: compare with the top nearby rivals (`{SRC} maps --search "<category> in <area>" --max 10`).
Never claim certificate or security problems from a TLS error on your side.

## Company research
Fill the 8 dimensions of `references/research-playbook.md`, adapted to the business (owner, locations, reviews, site and
marketing for an SMB; product and pricing for SaaS; catalogue and channels for e-commerce). Save every page you rely on:
`{FETCH} <url> --save prospects/<slug>/sources` (snippets are leads, not facts). End `COMPANY-RESEARCH.md`
(`references/research-output-format.md`) with **Why now** and the **3 best hooks**, then
`{CLAIM} --draft prospects/<slug>/COMPANY-RESEARCH.md --prospect <slug>` and fix every unsupported line.

## Contacts
Start from the dossier's `people` / `decision_maker`; otherwise `python <SCRIPTS>/research/contact_finder.py --url <url>`,
the team page and `site:linkedin.com/in "<company>" founder OR owner OR director`. Classify buying roles
(`references/contacts-playbook.md`). Emails for the top 1-3: `{FIND} --domain <domain> --first <first> --last <last>` —
post/site first, then finders, then verifiers (`{FIND} --providers` shows what is set); an address from a database:
`{FIND} --email <address>` (verify only). Use the status exactly as returned; only `verified` is safe for cold email, and
typing `--email-status verified` without a verification on record gets downgraded. Best channel: verified email → email;
a published business phone → WhatsApp click-to-chat (`{OUT} whatsapp`); only a social profile → the user replies or DMs.
Write `DECISION-MAKERS.md` (`references/contacts-output-format.md`) and save each person:
`{PIPE} contact <slug> --name "<name>" --title "<title>" --role "<buying role>" --email <email> --email-status <status> --source <source> --linkedin <profile url>`.

## Qualify
BANT (25 each) and MEDDIC with evidence or "Unknown" (`references/qualify-playbook.md`). Cross-check:
`{SCORE} prospects/<slug>/_bant_signals.json` (format: `{SCORE} --example`), or `{SCORE} --mode agency <file>` for a
public ask; explain any gap over 15 points. Service-buyer red flags — wants free samples or spec work, "just exploring",
equity only, budget far below scope, many agencies already in the comments — two or more → `nurture` or `disqualified`.
Write `LEAD-QUALIFICATION.md` (`references/qualify-output-format.md`) with 3-5 discovery questions for the gaps, then
`{PIPE} stage <slug> qualified --reason "<grade + reason>"` (or `nurture` / `disqualified`).

## Competitors
Detect today's site platform, footer credits ("Designed by…"), job posts, case studies, reviews and the `competitors` /
`ads` research sections; for local businesses their rivals on Maps. One honest battle card per incumbent, switching
cost, landmine questions (`references/competitors-playbook.md`) → `COMPETITIVE-INTEL.md`
(`references/competitors-output-format.md`). Never disparage a competitor with a claim you can't source.

## Full analysis
Deep scan → the five roles in order — `references/role-company.md`, `role-contacts.md`, `role-opportunity.md`,
`role-competitive.md`, then `role-strategy.md` (it needs the other four; agents with subagents may run the first four in
parallel). Prospect Score = Company Fit 25% + Contact Access 20% + Opportunity 20% + Competitive 15% + Outreach Readiness
20% (missing role = 50, lower confidence). Write `PROSPECT-ANALYSIS.md` (`references/analysis-playbook.md`,
`references/analysis-output-format.md`) including a claim-checked first email, then
`{PIPE} score <slug> <score> --breakdown '{{"company_fit": .., "contact_access": .., "opportunity": .., "competitive": .., "outreach_readiness": ..}}'`.

## Record (every mode)
`{PIPE} add --url <url> --name "<company>" --stage researched`, `{PIPE} attach <slug> prospects/<slug>/<FILE> --kind <kind>`,
`{PIPE} note <slug> "<top hooks + services>"`, `{PIPE} next <slug> "<next action>" --due <YYYY-MM-DD>`. Finish with: score
+ grade, top 3 hooks with their catalog services, contact status, and the next skill (usually `vintoria-outreach`).
""",
"writes_email": True,
"refs": [("fact-to-hook.md", "how each audit fact becomes a respectful one-line observation"),
         ("research-playbook.md", "the 8 research dimensions and where to find each"), ("research-output-format.md", "COMPANY-RESEARCH.md template"),
         ("contacts-playbook.md", "contact discovery, buying roles, anchors, access score, multi-threading"),
         ("contacts-output-format.md", "DECISION-MAKERS.md template"),
         ("qualify-playbook.md", "BANT and MEDDIC rubrics with scoring guidance"), ("qualify-output-format.md", "LEAD-QUALIFICATION.md template"),
         ("competitors-playbook.md", "detection sources, battle cards, displacement strategy"), ("competitors-output-format.md", "COMPETITIVE-INTEL.md template"),
         ("analysis-playbook.md", "discovery, role orchestration, scoring and synthesis"), ("analysis-output-format.md", "PROSPECT-ANALYSIS.md template"),
         ("role-company.md", "Company Fit role"), ("role-contacts.md", "Contact Access role"), ("role-opportunity.md", "Opportunity role (BANT, pain, timeline)"),
         ("role-competitive.md", "Competitive Position role"), ("role-strategy.md", "Outreach Readiness role + first email"),
         ("rules.md", "terminal output, errors and cross-skill use for every mode"), ("compliance.md", "rules for the first email")],
},
# =========================================================================== 5. outreach
{
"name": "vintoria-outreach",
"profile": "required",
"title": "Vintoria Outreach — first emails, sequences and follow-ups",
"description": "Writes Vintoria's outreach and follow-ups: a short first email built on one verified observation (their public post or a site-audit fact) tied to one Vintoria catalog service, a 5-email sequence on day 0/3/7/14/28 with A/B subject lines, LinkedIn and WhatsApp touches for the user to send, and follow-ups after silence, a meeting, a demo or a proposal. Every sentence is claim-checked against evidence and every email quality-scored (85+ premium) before the user sees it; approved sequences are queued and stop the moment the prospect replies. Use it whenever a prospect needs a message — even if the user only names a company — or says 'write a cold email', 'outreach sequence', 'follow up with', 'they went quiet', 'after the meeting what do I send', or Hinglish 'is client ko email likho', 'cold email banao', 'follow up likho', 'reply nahi aaya'.",
"intro": """You write outreach a busy owner actually answers: short, specific, true, about them, and easy to say yes to.""",
"body": f"""## Cold sequence (new prospect)

1. **Evidence first.** No `prospects/<slug>/DOSSIER.json`? Run the deep scan (`vintoria-prospect-research`). Read
   `DOSSIER.md` (ranked hooks, "Who wrote it", decision maker, best email), `OFFER.md` (which lane and entry service this
   prospect fits) and `{PIPE} show <slug>`. The recipient needs a `verified` email — or say clearly that it isn't.
   **Channel by source:** they posted asking → the user replies there first (2 helpful lines, no pitch) + email if
   verified; a Maps lead with a phone and no email → WhatsApp click-to-chat; a Product Hunt launch → email the maker.
2. **Email 1** (`references/first-email-guide.md`): plain text, under 120 words, their post or business in the first
   line, ONE observation backed by evidence, one sentence on what Vintoria does about it (one named catalog service —
   never a list), one soft question as the CTA ("worth a quick look?"), signature with postal address and an opt-out line.
   **No booking link** — the goal is a reply; the calendar link follows a yes.
3. **The sequence** (`{OUT} cadence`), each email adding something new (`references/outreach-playbook.md`, templates
   `references/template-outreach-cold.md`, `references/template-outreach-warm.md`, `references/template-outreach-referral.md`):
   | Email | Day | Content | Words |
   |---|---|---|---|
   | 1 | 0 | Their post / top hook + one fact + soft question | ≤ 120 |
   | 2 | 3 | Second hook (another audit fact) + a one-line fix idea | ≤ 70 |
   | 3 | 7 | Proof: a real result from the profile, or a mini teardown of their page (`[ADD REAL CUSTOMER RESULT]` if none) | ≤ 90 |
   | 4 | 14 | Different angle: a competitor or market fact (Maps comparison, reviews) or one simple question | ≤ 60 |
   | 5 | 28 | Polite breakup — "close the file?" — door left open | ≤ 50 |
   Subjects: 2-5 words, lower case, specific ("acme homepage on mobile"); follow-ups reply in the same thread. Signature,
   offer line and proof only from `{PROF} show`. Warm/referral templates only for a real, confirmed connection.
4. **Write the files.** `prospects/<slug>/SEQUENCE.json` is the source of truth
   (`[{{"step": 1, "subject": "...", "subject_b": "...", "hook": "<dossier hook key>", "body": "..."}}, {{"step": 2, "body": "..."}}, ...]`;
   `subject_b` runs an A/B test, `hook` feeds `learn.py`). `OUTREACH-SEQUENCE.md` is the human view
   (`references/outreach-output-format.md`) with the same emails, both subjects and the LinkedIn/WhatsApp touches.
5. **Check all five at once:** `{OUT} approve <slug> --to <email> --file prospects/<slug>/SEQUENCE.json --check` runs the
   claim check, the quality score (`{LINT} --sequence prospects/<slug>/SEQUENCE.json --prospect <slug>`, must reach
   `LINT_MIN_SCORE`, default 80 — aim for **85+ on every email**: the first two lines only this prospect could receive,
   no sentence over 28 words, every follow-up brings a new fact, idea or result), and the opt-out, address, booking-link,
   over-contact and recipient gates — and queues nothing. Before that, run the panel review and the deletion test in
   `references/quality.md`. Fix and re-run until it passes.
6. **Show the user and deliver** in the mode `{OUT} doctor` reports — `autopilot`: after approval run the same command
   without `--check` (each email goes out on its day in their morning; everything stops on a reply, opt-out, bounce or
   booking); `send-one-by-one` / `manual`: see "Before anything is sent".
7. Record: `{PIPE} attach <slug> prospects/<slug>/OUTREACH-SEQUENCE.md --kind outreach`. WhatsApp:
   `{OUT} whatsapp <number with country code> --text-file msg.txt` gives the user a click-to-chat link; log it with `--channel whatsapp`.

## Follow-ups (after something happened)

1. Read what happened — last touch, their words, what was promised, prices shared, objections — from `{PIPE} show <slug>`
   and the folder. If they replied, use `vintoria-reply-book` instead.
2. Pick the scenario (`references/followup-playbook.md`): **post-meeting** recap within 24 h (their words, what was agreed,
   next step with a date); **post-proposal** day 2 walkthrough offer, day 5 one question on the option they liked, day 10 a
   real deadline (start slot, price validity), day 20 breakup; **ghost recovery**; **nurture**.
3. Write the emails (plus LinkedIn/phone/SMS only where appropriate — SMS only for warm leads who shared their number),
   claim-check each, write `FOLLOWUP-SEQUENCE.md` (`references/followup-output-format.md`).
4. Queued cold sequences need nothing here. Log a manual follow-up when it goes out:
   `{OUT} log <slug> --channel email --to <email> --subject "..."` (schedules the next one), or
   `{PIPE} next <slug> "<next touch>" --due <date>`; update the stage when the user tells you.
""",
"writes_email": True,
"refs": [("first-email-guide.md", "style rules + 10 good/bad first-email examples"),
         ("quality.md", "the 0-100 score, banned and AI phrases, personalization levels, deletion test, panel review"),
         ("outreach-playbook.md", "personalization research, 4 frameworks, the 5-email sequence, LinkedIn, A/B, sending"),
         ("outreach-output-format.md", "OUTREACH-SEQUENCE.md template"), ("template-outreach-cold.md", "cold template"),
         ("template-outreach-warm.md", "warm intro template"), ("template-outreach-referral.md", "referral template"),
         ("followup-playbook.md", "the 5 follow-up scenarios, multi-channel touches, cadence, breakup emails"),
         ("followup-output-format.md", "FOLLOWUP-SEQUENCE.md template"), ("compliance.md", "legal and deliverability rules"),
         ("rules.md", "terminal output, errors, cross-skill use")],
},
# =========================================================================== 6. reply + book
{
"name": "vintoria-reply-book",
"title": "Vintoria Replies & Booking — answer fast, book the call",
"description": "Handles a prospect's reply and books the meeting for Vintoria: classifies the reply in English, Hindi or Hinglish (interested, meeting request, question, price/timing/vendor objection, referral, not interested, opt-out, out-of-office, bounce), updates the pipeline (stage, follow-ups stopped, opt-outs suppressed, bounces marked invalid), drafts a short truthful answer whose goal is a booked call, proposes slots that work in both time zones (India ↔ US/UK/Australia), writes the .ics calendar invite, schedules prep and reminders, and records the outcome (held, no-show, rescheduled). Use it whenever the user pastes or forwards a message from a prospect — even with no instructions — or says 'they replied', 'what should I answer', 'they want to talk', 'book a meeting', 'send a calendar invite', or Hinglish 'client ne reply kiya', 'iska jawab likho', 'unhone price poocha', 'meeting fix karo', 'call schedule karo'.",
"intro": """A reply is the most valuable moment in the pipeline. Answer what they asked, fast, and move to a call in one email.""",
"body": f"""## Reply

1. **Find the prospect:** `{PIPE} find <sender email or name>`, then `{PIPE} show <slug>` (thread, country, time zone,
   stage). Unknown sender → ask which prospect it is.
2. **Classify and update in one go.** With IMAP: `{INBOX} check --apply` (every new reply and bounce, read-only).
   Otherwise: `{TRIAGE} --file reply.txt --apply <slug> [--from <their email>]`. Either way the queued sequence stops.
   Read the reply yourself too — if the category is wrong, say so and fix it with `{PIPE} stage`.
3. **Answer by category:**
   | Category | What you write |
   |---|---|
   | `meeting_request` | Book it (below): confirm their time or offer 2 slots |
   | `interested` / `question` | Answer in 1-3 sentences (facts only from the profile, `OFFER.md` and their files), then 2 slots in their zone and the booking link — now it is welcome |
   | `objection_price` / `objection_has_vendor` | Use `../vintoria-close/references/objections-playbook.md`: change scope, never the price; offer a smaller first phase, then a call |
   | `objection_timing` | Agree a date; `{PIPE} next <slug> "Check back as agreed" --due <date>`; stage stays `nurture` |
   | `referral` | Thank them; a 3-line email to the named person saying who referred you (`vintoria-outreach`) |
   | `out_of_office` | Nothing to write; the triage moves the queued emails past their return date |
   | `send_info` | ONE specific thing (a 2-minute teardown of their page, one case study from the profile) + one easy question |
   | `how_got_email` | Say honestly where the address came from and offer to remove them |
   | `wrong_person` | Ask once who owns it; no name → stop |
   | `not_interested` | One gracious line, no pitch, never follow up again |
   | `unsubscribe` / `bounce` | Nothing to write — confirm it's suppressed / find another verified contact |
   **"How much?"** — follow `../vintoria-sales/references/pricing-policy.md`: a price only if the profile has it;
   otherwise "Depends on scope — two quick questions and I'll send a written scope with options."
4. **Short and matched:** at most ~100 words before the slots and signature, not much longer than their message, their
   questions answered in the first two sentences, at most one `[TO CONFIRM]`.
5. Claim-check, show the user, and log it when sent:
   `{OUT} log <slug> --channel email --to <email> --subject "Re: <their subject>" --no-schedule`. Tell the user the new stage
   and the next step with its date.

## Book

1. **Their time zone** from their post, site address, phone code (+91 India, +1 US/Canada, +44 UK, +61 Australia) or
   signature; record it once: `{PIPE} where <slug> --country US --tz America/Chicago`.
2. **Slots:** if they named a time, use it. Otherwise `{MEET} slots --prospect-tz <IANA zone> [--count 3] [--minutes 30]`
   — 2 slots on different days in both zones (two concrete times beat a bare link), skipping booked meetings, plus a ready
   message with `BOOKING_URL`. India ↔ US slots marked `outside_your_work_hours` need the user's OK.
3. **When they confirm:**
   `{MEET} book <slug> --start "YYYY-MM-DD HH:MM" [--tz <zone of that time>] --prospect-tz <their zone> --attendee <email> --attendee-name "<name>" [--link <video link>] [--agenda "<one line>"]`
   — writes `prospects/<slug>/MEETING-<date>.ics`, sets stage `meeting`, stops follow-ups, schedules prep for the day before.
   Give the user the confirmation and tell them to attach the `.ics`.
4. **Before:** run `vintoria-close` (prep + discovery). The day before, a confirmation that carries something useful — the
   agenda and the 2-3 audit findings you'll walk through (a pre-read raises show rates); an hour before, one line.
5. **After:** `{MEET} outcome <id> held|no_show|rescheduled|cancelled --notes "<what was agreed>"`. Held → `vintoria-close`
   (discovery score, proposal) and the post-meeting recap in `vintoria-outreach`. No-show → the same day, one warm note with
   2 new slots; a second no-show moves them to `nurture`.

## Rules
- Reply within the hour to `meeting_request` and `interested` — speed decides most deals.
- The booking link goes out only after interest; `outreach.py` refuses it in cold emails. Bookings made through the link
  are picked up by `{INBOX} check --apply` (and the autopilot) automatically.
- Times in **their** zone first, Vintoria's in brackets. Never invent a video link (`--link`, `MEETING_LINK`, or "link to follow").
- A proposed slot is not a meeting: book only what the prospect confirmed.
""",
"writes_email": True,
"refs": [("compliance.md", "legal and deliverability rules")],
},
# =========================================================================== 7. close
{
"name": "vintoria-close",
"profile": "required",
"title": "Vintoria Close — prep, discovery, proposal, objections, signature, expansion",
"description": "Takes a Vintoria deal from booked call to signed contract and beyond: builds the meeting brief (their original request, audit facts, the thread, qualification so far), runs and scores the discovery call (timed agenda, 0-100 scorecard, go/no-go bands, question banks, red-flag tests), writes the proposal from the buyer's own words with scope by exact Vintoria catalog service IDs, three scope options and prices only from the profile, prepares word-for-word objection answers (price, timing, current vendor, offshore worries), runs negotiation where concessions change scope not price, drives signature and the delivery handoff, and plans upsells and referral asks. Use it for 'prep me for my call', 'discovery call questions', 'write a proposal', 'quotation for this client', 'client says it's too expensive', 'they said yes, now what', 'negotiate', 'handoff to delivery', 'upsell this client', or Hinglish 'meeting ki taiyari karo', 'proposal banao', 'client bol raha hai mehenga hai', 'deal close kar do'.",
"intro": """Meetings are won before they start and deals are lost in the details after them. You prepare, qualify honestly,
propose scope the buyer recognises as their own, and close without ever inventing a price, a date or a result.""",
"body": f"""## Pick the stage

| Stage | When | Output in `prospects/<slug>/` |
|---|---|---|
| **Prep** | a meeting is booked | `MEETING-PREP.md` |
| **Discovery** | the call is happening / just happened | `MEETING-NOTES.md` + qualification score |
| **Proposal** | discovery scored A (80+), or they asked for one | `CLIENT-PROPOSAL.md` |
| **Objections** | an objection came up (any stage) | answers in the reply, or `OBJECTION-PLAYBOOK.md` |
| **Negotiate & sign** | they've seen the proposal / said yes verbally | terms summary, mutual action plan, handoff checklist |
| **Expand** | won and delivering | upsell map, referral and review asks |

## Prep
1. Load what is known: `{PIPE} show <slug>`, `{MEET} list`, every file in `prospects/<slug>/` (dossier, post quote, audit,
   research, contacts, outreach, replies). No dossier → run the deep scan (`vintoria-prospect-research`) first.
2. Build the brief (`references/prep-playbook.md`, `references/prep-output-format.md`, `references/template-meeting-prep.md`):
   a one-page cheat sheet, their original request in their own words, the audit facts, the conversation so far,
   qualification status (budget, timeline, decision maker, scope — unknowns marked), 1-3 catalog services that fit with
   the signal beside each, talking points, 10 discovery questions aimed at the unknowns, objections, landmines, and the
   exact ask for the close ("Shall I send a written scope with 3 options by Friday?").
3. A **3-minute screen-share plan**: their site on a phone view, the top 2 audit facts, one competitor doing it better —
   then ask, don't pitch.
4. `{CLAIM} --draft prospects/<slug>/MEETING-PREP.md --prospect <slug>` — talking points built on an invented fact are
   worse than none. Attach it: `{PIPE} attach <slug> prospects/<slug>/MEETING-PREP.md --kind meeting-prep`.

## Discovery
Run the call with `references/discovery-call.md`: 30- or 45-minute agenda, one question at a time from the banks (core
first, then the discipline bank — AI, automation, web/SaaS, e-commerce, SEO/growth), verbatim quotes, red-flag tests.
Score after the call: problem 20, impact 15, authority 20, timeline 15, budget signal 10, service fit 10, risk 10.
**A 80-100** proposal · **B 65-79** paid discovery or a bounded pilot · **C 50-64** nurture with a trigger · **D < 50**
disqualify politely. Hard no-go whatever the score: no route to the economic buyer within 30 days, need outside the 270
services, regulated data with no compliance owner, free build or guaranteed result demanded. Write `MEETING-NOTES.md`
within 2 hours, then `{MEET} outcome <id> held --notes "<budget, scope, decision date>"`,
`{PIPE} score <slug> <score>` and `{PIPE} stage <slug> qualified --reason "<band + reason>"` (or `nurture` / `disqualified`).

## Proposal
1. **Inputs** (`references/proposal-playbook.md`): the buyer's needs in their words (post, replies, `MEETING-NOTES.md`),
   and from the profile only: prices, timelines, process, team, case studies. Missing → `[PRICE TO CONFIRM]` /
   `[TO CONFIRM]` — never a guess, never "agencies usually charge".
2. **Write** with `references/template-proposal-template.md` and `references/proposal-output-format.md`: their problem with
   evidence; scope where every line cites a catalog service ID + name with inclusions and **exclusions**; three options
   (core / recommended / expanded) that differ in scope, never in discount; phases with dependencies and acceptance
   criteria (working days, or `[TO CONFIRM]`); assumptions, buyer responsibilities, change-request path; payment terms,
   validity (14 days) and acceptance ("reply 'approved Option B'"). Price in their currency (INR, USD, GBP, AUD) only from
   the profile. Tax on exported services is for the accountant — don't state it.
3. Score it against the proposal bar in `../vintoria-sales/references/quality-bar.md` (floor 80) and claim-check it.
4. Record: `{PIPE} stage <slug> proposal --reason "proposal sent <date>"`, `{PIPE} value <slug> <recommended option price> --currency <cur>`
   (only a real price), attach the file, `{PIPE} next <slug> "Walkthrough offer" --due <date+2>`; the post-proposal follow-ups
   are in `vintoria-outreach`.

## Objections
Exact words for calls, emails and chat (`references/objections-playbook.md`, `references/objections-output-format.md`,
`references/template-objection-playbook.md`): the frameworks, 15 universal objections, industry and competitor
objections, prevention. Price objections change scope or phasing, never the price (`../vintoria-sales/references/pricing-policy.md`).
For overseas buyers include the offshore-agency worries — time zones (overlap hours, response time), communication and
quality (named owner, weekly calls), "burned by an offshore team" (milestone payments, code ownership, references), IP and
contracts, how to pay. For Indian SMBs: "a freelancer will do it cheaper", "my nephew can build it", "we tried an agency
before", "guarantee page 1?" (never promise rankings). Map each to the `reply_triage.py` categories so replies get the
right answer. Proof points must be real — otherwise `[ADD REAL CUSTOMER RESULT]`.

## Negotiate & sign
Follow `references/negotiation-and-handoff.md`: capture their decision criteria, build a mutual action plan with dates
both sides own, sequence concessions that change only scope, phasing or start date, prepare procurement / legal /
security answers, check contract terms against the catalog IDs in scope, rescue a buyer who goes quiet after a yes, and
hand off to delivery with a checklist. `{PIPE} stage <slug> won` when signed — or `lost --reason "<why>"` (the reason
feeds the weekly review).

## Expand
After the win, `references/expand-and-referrals.md`: the natural follow-on services from the offer lane (e.g. a website → `212 Search Engine Optimization` or
`214 Local SEO`, then an automation service from discipline 08), timing for the upsell, and the review and referral asks — only when
the client got a real result.
""",
"writes_email": True,
"refs": [("prep-playbook.md", "research steps, the brief sections, agendas"), ("prep-output-format.md", "MEETING-PREP.md format"),
         ("template-meeting-prep.md", "meeting brief template"), ("discovery-call.md", "discovery call: brief, agenda, scorecard, question banks, red flags, scripts"),
         ("proposal-playbook.md", "inputs, sections, follow-up sequence"), ("proposal-output-format.md", "CLIENT-PROPOSAL.md format"),
         ("template-proposal-template.md", "proposal template"), ("objections-playbook.md", "frameworks, 15 objections, industry/competitive/pricing, prevention"),
         ("objections-output-format.md", "OBJECTION-PLAYBOOK.md format"), ("template-objection-playbook.md", "objection playbook template"),
         ("negotiation-and-handoff.md", "decision criteria, mutual action plan, concessions, legal/security, signature, handoff, loss debrief"),
         ("expand-and-referrals.md", "upsell map, retention, review and referral asks"),
         ("compliance.md", "legal rules for every email"), ("rules.md", "terminal output, errors, cross-skill use")],
},
# =========================================================================== 8. report
{
"name": "vintoria-report",
"title": "Vintoria Report — pipeline, what works, PDF",
"description": "Produces Vintoria's pipeline report from the persistent pipeline and the prospects/ folders: funnel by stage, reply / meeting / win rates, deal value forecast per currency, stale deals, actions due, which sources, queries, hooks, subjects and catalog services produce replies and meetings, and a prioritised weekly action plan — written to SALES-REPORT.md, optionally as a designed PDF — and feeds the winning queries back into the lead engine. Use it for 'pipeline report', 'how is my pipeline', 'weekly sales review', 'which leads are working', 'how much revenue is in the pipeline', 'PDF report for my team', or Hinglish 'pipeline ka report do', 'kitne leads hain', 'is hafte ka review', 'PDF report banao'. For today's to-do list use vintoria-sales instead.",
"intro": """You turn the pipeline into decisions: what to do this week, what to keep doing, and what to stop.""",
"body": f"""## Steps

1. **Numbers:** `{PIPE} report` (funnel, conversion, activity, grades, stale, due, by source, top 10, forecast),
   `{PIPE} list`, `{PIPE} today`, and upcoming meetings with `{MEET} list`.
2. **Complete it:** prospects in `prospects/*/` that aren't in the pipeline yet — read their files and add them
   (`{PIPE} add ...`, `{PIPE} score ...`).
3. **What works:** `{LEARN} report` — reply, positive-reply and meeting rates by source, query, platform, hook, subject A/B,
   sequence step, quality score and country, with recommendations. `{LEARN} report --apply` writes the query weights so the
   next `serp.py watch/hunt` runs the winners first and skips queries that never produced a positive reply.
4. **Analyse** (`references/report-playbook.md`): health, stuck deals and why, which offer lanes and catalog services get
   replies, which markets (India vs US/UK/AU) convert, gaps (no verified contacts, sequences not approved, inbox not
   connected), and the **forecast** (open, weighted and won value per currency from `{PIPE} value`) — missing values on
   meeting/proposal deals are a gap to fix.
5. **Write** `SALES-REPORT.md` (`references/report-output-format.md`): summary, funnel table, top prospects, stale deals,
   source performance, and an action plan (today / this week / this month) with one concrete action per prospect.
6. **PDF** (when asked, or for sharing): check `python -c "import reportlab"` (else `pip install reportlab`), then
   `{PIPE} report --pdf-input _pdf_input.json`, merge any extra context from `SALES-REPORT.md` following
   `references/pdf-playbook.md`, and `python <SCRIPTS>/ops/generate_pdf_report.py _pdf_input.json "SALES-REPORT-<YYYY-MM-DD>.pdf"`
   (`--demo` previews the layout). Give the user the path and delete `_pdf_input.json` unless they want it.
""",
"refs": [("report-playbook.md", "analysis steps and pipeline-health rules"), ("report-output-format.md", "SALES-REPORT.md template"),
         ("pdf-playbook.md", "PDF input schema and field-by-field guidance"), ("rules.md", "errors and troubleshooting")],
},
]
