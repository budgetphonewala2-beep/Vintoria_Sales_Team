---
name: vintoria-prospect-research
description: "Researches one prospect for Vintoria end to end: a sourced dossier (company, people, best contact, ranked hooks), a fact-only website audit as proof-of-work (mobile viewport, speed, title and description, CTA, contact form, click-to-call, WhatsApp, broken links, platform, copyright year), company research, the buying committee and the best email with an honest status (never a guess presented as real), BANT, MEDDIC and agency-buyer qualification, current vendors with battle cards, and a full 0-100 scored analysis with five role playbooks — each hook mapped to the exact Vintoria catalog services it justifies. Use it whenever one company, website or person needs looking into before contact or a call: 'research acme.com', 'audit their website', 'who is the owner', 'get their email', 'is this a good lead', 'what do they use today', 'score this prospect', or Hinglish 'is company ke baare mein batao', 'website check karo', 'owner kaun hai', 'iska email nikalo', 'ye lead qualified hai kya'."
license: MIT
compatibility: "Instruction-only Agent Skill: no code. Works in any agent or bot (Claude, Grok, GPT, Gemini…) that can follow instructions; best with a browser logged in to LinkedIn and Reddit, and file access."
metadata:
  author: "Vintoria (built on ai-sales-team-claude by Zubair Trabzada)"
  version: "5.0.0"
---

# Vintoria Prospect Research — everything about one prospect

Outreach is only as good as the research under it. You turn one URL, post or name into sourced facts, a safe way to
reach the decision maker, and the 1-3 Vintoria services the evidence actually justifies.

## Before you start

1. **Your files.** Everything lives in plain files — `SELLER-PROFILE.md`, `OFFER.md`, `IDEAL-CUSTOMER-PROFILE.md`,
   `PIPELINE.md`, `DO-NOT-CONTACT.md` and `prospects/<slug>/` (format: `../vintoria-sales/references/pipeline-format.md`). If you can't read or
   write files (a chat bot such as Grok), ask the user to paste `SELLER-PROFILE.md` and the relevant `PIPELINE.md` rows,
   and finish by printing every changed row and file in code blocks for them to save.
2. **Vintoria's profile.** Read `SELLER-PROFILE.md`. This skill builds queries, emails or prices from it — if it is
   missing or still full of `[ASK]`, run `vintoria-setup` first (in a hurry: ask only the missing answers in one message).
3. **What Vintoria sells.** 270 services in 12 disciplines — `../vintoria-sales/references/service-catalog.md`. Name a service exactly as the
   catalog does (`192 Shopify Development`), never invent one, and never quote a price, discount or date that isn't in
   `SELLER-PROFILE.md` — write `[PRICE TO CONFIRM]` (`../vintoria-sales/references/pricing-policy.md`).
4. **Platforms.** Leads come only from **LinkedIn and Reddit**, through the accounts already logged in on this machine.
   Open a page before you state a fact from it and note its URL and date; a search snippet alone is not a fact. If you
   can't open something, write "Not found".
5. **Facts only.** Every sentence traces to a page you opened, the prospect's own words, a fact you observed on their site,
   the catalog or the profile — never to memory. Never say something was sent, posted, booked or verified unless it
   really happened. Run the self-check in `../vintoria-sales/references/truth-rules.md` before anything goes out.
6. **Vintoria's contact details** — `business@vintoria.org`, WhatsApp +91 87660 33979 (`https://wa.me/918766033979`) —
   and every sign-off come only from `../vintoria-sales/references/vintoria-contact.md`.
7. **The team.** Read `TEAM-BOARD.md` before you start and handle messages to your role; `CLAIM` a lead before working it,
   hand off with full context, post `ALERT`s at once (`../vintoria-sales/references/team.md`). Alone, you play every role with the same files.

## Pick the mode

| The user wants | Mode | Output in `prospects/<slug>/` |
|---|---|---|
| "Look into this lead" (default for any new prospect) | **Dossier** | `DOSSIER.md` |
| A hook / "what's wrong with their site" | **Site audit** | `SITE-AUDIT.md` |
| Background on the company | **Company research** | `COMPANY-RESEARCH.md` |
| Who to contact + their email | **Contacts** | `DECISION-MAKERS.md` |
| Is it worth our time | **Qualify** | `LEAD-QUALIFICATION.md` |
| What they use today / who their agency is | **Competitors** | `COMPETITIVE-INTEL.md` |
| A full scored audit with a first email | **Full analysis** | `PROSPECT-ANALYSIS.md` |

Start with the dossier when there is none; the other modes build on it.

## Dossier
1. **Their words first:** the post or message that brought them in (exact quote, URL, date).
2. **Site audit** (below) and the pages that matter: home, about, services/pricing, team, careers, contact.
3. **Web:** reviews (Google, Justdial, Clutch…), news, hiring, ads, complaints, competitors — open each page you use.
4. **People + contact** (Contacts below) and the best channel.
5. **Hooks:** rank 3-5 sourced facts, strongest first, and give each its **fit** — the catalog service it justifies
   (no viewport + slow → `033 High-Performance Website Development`; no online booking → `028 Booking Platform Development`;
   manual enquiry handling → a service from discipline 08 Business Automation; asked for a chatbot → `123 AI Chatbot Development`).
6. Write `DOSSIER.md`: who they are, why now, hooks + evidence + fit, decision maker, contact + status, risks, next step.
   It must reach 70 on the dossier score in `../vintoria-sales/references/quality-bar.md` before any outreach.

## Site audit (facts only)
Open the homepage (and its HTML source if your browser can show it) and record only what you can see, each with its
evidence: page title; meta description; mobile viewport tag; HTTPS and whether `http://` redirects; how long the page took
to load for you (say it was your test); H1 count; a contact form; a click-to-call `tel:` link; a WhatsApp link; a clear CTA
("Book now", "Get a quote"); images without alt text; platform hints (Shopify, WordPress, Wix, Webflow, Next.js); footer
copyright year; any of the first internal links that error. Optional: Google PageSpeed (`pagespeed.web.dev`) mobile
score if you can open it. Pick the **top 3 observations** with `references/fact-to-hook.md` — the fact exactly as seen,
any consequence hedged ("so phone visitors may…"). Never claim a security or certificate problem, traffic or revenue.
Local business: compare with the top 3 rivals on Google Maps (rating, reviews, website, online booking).

## Company research
The 8 dimensions of `references/research-playbook.md`, adapted to the business (owner, locations, reviews, site and
marketing for an SMB; product and pricing for SaaS; catalogue and channels for e-commerce). Every fact gets a URL and date.
End `COMPANY-RESEARCH.md` (`references/research-output-format.md`) with **Why now** and the **3 best hooks**, then run the
truth self-check on it.

## Contacts
Team, about and leadership pages, then `site:linkedin.com/in "<company>" founder OR owner OR director`. Classify buying
roles (`references/contacts-playbook.md`; in an owner-run SMB the owner is buyer and champion). **Email, best first:**
1) written in their post, in their LinkedIn **Contact info**, or on their own site → `published`; 2) a business database the user has access to (Apollo,
Hunter…) → ask the user to verify it there → `verified`; 3) a name pattern (`first@domain`) → `pattern-guessed — verify
before sending`, never used for cold email. Best channel: usable email → email; a published business phone → WhatsApp
click-to-chat; only a social profile → the user replies or DMs. Write `DECISION-MAKERS.md` (`references/contacts-output-format.md`).

## Qualify
BANT (25 each) and MEDDIC, each with evidence or "Unknown" (`references/qualify-playbook.md`), cross-checked with its
agency-buyer table for public asks. Red flags — wants free samples or spec work, "just exploring", equity only, budget far
below the scope, many agencies already in the comments — two or more → `nurture` or `disqualified`. Write
`LEAD-QUALIFICATION.md` (`references/qualify-output-format.md`) with 3-5 discovery questions for the gaps.

## Competitors
Their platform, footer credits ("Designed by…"), job posts, case studies, reviews, ads; for local businesses their rivals on
Maps. One honest battle card per incumbent, switching cost, landmine questions (`references/competitors-playbook.md`) →
`COMPETITIVE-INTEL.md` (`references/competitors-output-format.md`). Never disparage a competitor with a claim you can't source.

## Full analysis
For leads worth real effort (value score 80+, a website, a big scope). Dossier → the five roles in order — Company Fit,
Contact Access, Opportunity, Competitive, then Outreach Readiness (it needs the other four; in a team the Researcher may
hand roles 1-4 to other bots in parallel). Prospect Score = 25 % + 20 % + 20 % + 15 % + 20 % (a missing role = 50, lower
confidence). Every dimension, the formula and the `PROSPECT-ANALYSIS.md` format: `references/full-analysis.md`.
Finish with a self-checked, critic-checked first message.

## Record (every mode)
Update the `PIPELINE.md` row (stage `researched`, score, services, contact, email status, next action + date) and add a line
to `HISTORY.md`. Finish with: score + grade, top 3 hooks with their catalog services, contact status, next skill
(usually `vintoria-outreach`). Terminal output, errors and edge cases: `references/rules.md`.

## Before anything is sent

- **Self-check** every message with `../vintoria-sales/references/truth-rules.md`; delete or rewrite every unsourced sentence and fill or flag
  every `[PLACEHOLDER]`.
- **Critic check** — the yes/no list in `../vintoria-sales/references/critic-check.md`, as a strict reviewer (another bot's `REVIEW` in a team).
  One "no" = fix it; two failed rewrites = skip the lead.
- **Score** it with `../vintoria-sales/references/quality-bar.md` (emails: 80 to show, 85+ premium) and say the score in one line.
- **Compliance:** `../vintoria-sales/references/compliance.md` — opt-out line, postal address for US, consent rules (UK/EU/CA/AU/NZ/India),
  and check `DO-NOT-CONTACT.md` first.
- **Language:** plain English — US spelling for US/CA, UK spelling for UK/IE/AU/NZ, clear Indian English for India (no
  "do the needful", "revert", "kindly"). If an Indian prospect wrote in Hindi or Hinglish, answer in the same register,
  still short and professional. Prices only in their currency and only from the profile.
- **Approval mode** (`SELLER-PROFILE.md` → Automation): `auto` — you post or send it yourself from the logged-in
  Reddit / LinkedIn account or `business@vintoria.org`, but only after it passes the self-check, scores 85+, fits that
  platform's rules (`../vintoria-sales/references/compliance.md`) and today's limits; `review` — show the exact text and wait for the user's OK.
  A message that fails any check is never sent in either mode — fix it or skip the lead. Count every post / send in
  `RUN-LOG.md` first; at the hourly limit (all bots together), queue it for the next hour.
- **Log every message that went out** — `THREAD.md` (exact text, link to it), `HISTORY.md`, `PIPELINE.md` — and give the
  user a summary of what was posted and sent.
- **No booking link** in a first message — only after they show interest.

## References (read when you reach that step)

- `references/fact-to-hook.md` — how each audit fact becomes a respectful one-line observation
- `references/research-playbook.md` — the 8 research dimensions and where to find each
- `references/research-output-format.md` — COMPANY-RESEARCH.md template
- `references/contacts-playbook.md` — contact discovery, buying roles, anchors, access score, multi-threading
- `references/contacts-output-format.md` — DECISION-MAKERS.md template
- `references/qualify-playbook.md` — BANT, MEDDIC and the agency-buyer score
- `references/qualify-output-format.md` — LEAD-QUALIFICATION.md template
- `references/competitors-playbook.md` — detection sources, battle cards, displacement strategy
- `references/competitors-output-format.md` — COMPETITIVE-INTEL.md template
- `references/full-analysis.md` — the five roles, their 0-10 dimensions, the Prospect Score, PROSPECT-ANALYSIS.md format
- `references/rules.md` — terminal output, errors and cross-skill use
