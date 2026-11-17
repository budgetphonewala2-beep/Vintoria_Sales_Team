<p align="center">
  <img src="banner.svg" alt="Vintoria Sales" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/11_skills-instruction--only-8b5cf6?style=for-the-badge" alt="11 skills">
  <img src="https://img.shields.io/badge/no_code-any_bot-0ea5e9?style=for-the-badge" alt="No code">
  <img src="https://img.shields.io/badge/license-MIT-gray?style=for-the-badge" alt="MIT License">
</p>

# Vintoria Sales — skills that find clients on LinkedIn and Reddit

Eleven instruction-only skills (no code, no installs) that run Vintoria's whole sales loop in any bot that can follow
instructions — Grok, Claude, GPT, Gemini, Codex, Cursor — best with a browser already logged in to **LinkedIn** and
**Reddit**:

- **Reddit:** the bot finds people asking for a website, app, AI chatbot, automation, Shopify store, SEO…, reads the post,
  and leaves a **professional, genuinely helpful comment** ending with Vintoria's clickable WhatsApp link.
- **LinkedIn:** the bot finds buyer posts, gets the **email** (post, contact info, company site) and writes a short
  personal email from **business@vintoria.org** — or a professional comment / connection note when there's no email.
- **Every hour, 24/7:** up to 10 valuable LinkedIn leads and up to 10 valuable Reddit posts, all **under 24 hours old**,
  found, scored, critic-checked and contacted within safe shared limits (`vintoria-hourly-run`).
- **A real sales team of bots:** Sales Manager, LinkedIn Hunter, Reddit Hunter, Researcher, Writer, Reviewer and Closer
  talk to each other on a shared team board — handoffs, claims, reviews, alerts, hourly lines and standups — so no lead
  is handled twice and every reply reaches the Closer within 15 minutes.
- **Account health autopilot:** shadowban and removal checks every 6 hours, GREEN / YELLOW / RED limits that every bot
  obeys, help-only comments to keep Reddit accounts healthy (`vintoria-account-health`).
- **Inbound authority:** a LinkedIn post every weekday and comments under buyers' posts; people who engage become warm
  leads (`vintoria-authority`).
- **Two email brands:** Vintoria (business@vintoria.org) on day 0, Radian Marketing (amar@radianmarketing.site) on day 1
  with a different, deeper marketing angle — each with 3/7/14/28-day follow-ups, honest sender identity, and one shared
  stop rule (a reply or opt-out to either brand stops both).
- **24/7 autopilot:** a full inbox sweep of both brands every 6 hours (spam included), a watchdog that hands a silent
  bot's role to another, and a default safe action for every situation — the owner is notified, never waited for
  (`skills/vintoria-sales/references/autopilot.md`).
- **Live Google Sheet:** every lead, email, comment, reply, deal, daily total and health check synced to tabs with a
  ready dashboard (`skills/vintoria-sales/references/sheet-sync.md`).
- **Hot-lead fast track, nurture engine, proof bank and a nightly owner digest** — the fastest answer to the best
  buyers, "not now" leads won back on real triggers, real results and referrals collected after every launch.
- Then it answers replies, books the call in both time zones, preps it, writes the proposal and closes — keeping
  everything in plain Markdown files.

Vintoria is a digital product studio with **270 services in 12 disciplines** (strategy, web, SaaS, mobile, UI/UX,
branding, AI, automation, backend & cloud, e-commerce, marketing & SEO, growth). The skills cite services by exact
catalog ID, never invent prices or results, and read English, Hindi and Hinglish.

**Contact used in every message:** business@vintoria.org · WhatsApp +91 87660 33979 ·
[wa.me/918766033979](https://wa.me/918766033979)

## The 11 skills

| Skill | Say… | Does |
|---|---|---|
| `vintoria-sales` | "aaj ka kaam batao", "run my sales" | The operator: today's agenda from `PIPELINE.md`, routes every request; holds the truth, pricing, quality, compliance and contact rules and the full catalog |
| `vintoria-setup` | "set up Vintoria", "who should we target" | Profile interview (template pre-filled with the catalog, email and WhatsApp), offer lanes by catalog ID, ideal customer + search queries |
| `vintoria-account-health` | "account safe hai?", "check shadowban" | Logged-out shadowban / removal checks, karma, warnings, LinkedIn restrictions → GREEN / YELLOW / RED in `HEALTH.md` |
| `vintoria-authority` | "LinkedIn post likho", "inbound leads" | Weekly content plan, one post a day in 5 formats, comments on buyers' posts, engagers → warm leads |
| `vintoria-hourly-run` | "hourly run chalao", "har ghante leads nikalo" | The 24/7 engine: every hour up to 10 + 10 valuable leads under 24 h from LinkedIn and Reddit, scored, claimed, contacted within shared limits, logged in `RUN-LOG.md`, summary on the team board |
| `vintoria-lead-hunt` | "LinkedIn pe clients dhundo", "Reddit pe website wale leads" | LinkedIn posts + Reddit buyer posts, judged with an exact quote, scored, contact path chosen |
| `vintoria-prospect-research` | "research acme.com", "owner kaun hai" | Dossier, fact-only site audit, contacts + email status, BANT/MEDDIC, battle cards, full score — hooks mapped to catalog services |
| `vintoria-outreach` | "is post pe comment karo", "isko email likho" | Reddit comment with WhatsApp link, LinkedIn email from business@vintoria.org + 5-step sequence, follow-ups |
| `vintoria-reply-book` | "client ne reply kiya", "meeting fix karo" | Classifies replies from Reddit, LinkedIn, email and WhatsApp, answers, offers slots in both time zones, invite text |
| `vintoria-close` | "meeting ki taiyari karo", "proposal banao" | Prep brief, scored discovery call, proposal by catalog ID with 3 scope options, objections, negotiation, upsell |
| `vintoria-report` | "pipeline ka report do" | Funnel, rates, value, what works (sources, queries, hooks, services, markets), next week's plan |

```
setup ─► hourly-run (every hour, 24/7) ─► prospect-research ─► outreach ─► reply-book ─► close ─► report
profile   LinkedIn + Reddit, < 24 h          dossier + email     comment / email   answer + book   proposal → signed
          (lead-hunt = deeper one-off hunt)        all bots talk on TEAM-BOARD.md
```

## Use it in your bot

**Agents that support Agent Skills** (Claude Code, Codex, Cursor, Gemini CLI, OpenCode): copy the folders in `skills/`
into the agent's skills folder — `~/.claude/skills`, `~/.agents/skills` (Codex, Cursor, Gemini, OpenCode),
`~/.cursor/skills`, `~/.gemini/skills` or `~/.config/opencode/skills`.

**Grok and other chat bots / custom assistants:** the fastest setup is
`skills/vintoria-sales/references/bot-prompts.md` — a paste-ready core prompt, one role line per bot, the knowledge
files to attach and the scheduler messages. Or by hand: give the bot `skills/vintoria-sales/SKILL.md` as its main
instructions, and add the other `SKILL.md` files plus their `references/` folders as knowledge files. Tell it to read the
matching skill before each job. Without file access it keeps the pipeline in the chat and prints the updated rows for you
to save (`skills/vintoria-sales/references/pipeline-format.md`).

**Before going live:** run `skills/vintoria-sales/references/self-test.md` with every bot — 29 scenarios, go live only at
29 / 29.

**First run:** say **"use vintoria-setup"** and answer the questions (sender name, postal address, time zone, active
disciplines, prices, real case studies). Then **"aaj ka kaam batao"** every day.

**24/7 hourly run:** set your bot platform's scheduler to send **"run vintoria-hourly-run"** every hour (the skill
defines what each run does; the timer itself comes from the platform). Each run: up to 10 valuable LinkedIn + 10 valuable
Reddit leads under 24 hours old — a ceiling, never a quota, so weak posts are never contacted just to reach 10.

**Several bots as one team:** give each bot its role from `skills/vintoria-sales/references/team.md` and one shared
folder (or one shared Telegram / Slack / Discord group) for `TEAM-BOARD.md`, `PIPELINE.md`, `SEEN.md` and `RUN-LOG.md`.
One bot alone plays every role.

**Approval mode** (in `SELLER-PROFILE.md`): `auto` — the bots post comments and send emails that pass every check
themselves; `review` — you approve each message first. Hourly limits for all bots together (edit them in the profile):
Reddit 10 comments (≥ 4 minutes apart, 1 per subreddit per hour), LinkedIn 10 emails (prospect's working hours only),
3 comments, 15 connection notes a day. **Be aware:** this pace is far above what Reddit and LinkedIn treat as normal for
one account — expect a high risk of removed comments, shadowbans or restrictions. The circuit breakers pause a platform
at the first removed comment or warning and escalate to you; lower the limits if that happens.

## Folders

```
skills/
  vintoria-sales/        SKILL.md + references/: bot-prompts, truth-rules, quality-bar, lead-quality, critic-check, team,
                         pricing-policy, compliance, vintoria-contact, pipeline-format, service-catalog +
                         services-01…12 (all 270 services)
  vintoria-hourly-run/   SKILL.md — the hourly 24/7 cycle (with hot-lead fast track)
  vintoria-account-health/  SKILL.md — GREEN / YELLOW / RED account levels
  vintoria-authority/    + content-playbook (5 post formats, hooks, 4-week rotation)
  vintoria-setup/        + seller-profile-template, intake, offer-lanes, ICP playbook and format
  vintoria-lead-hunt/    + queries (24/7 market rotation, direct search URLs, LinkedIn boolean, subreddits),
                         intent-rubric (30 labelled examples)
  vintoria-prospect-research/  + research, contacts, qualify, competitors playbooks, full-analysis (5 roles)
  vintoria-outreach/     + reddit-comment-playbook, comment-angles (tip bank), linkedin-playbook, first-email guide,
                         sequence playbook, quality score
  vintoria-reply-book/   + whatsapp-playbook (where deals close)
  vintoria-close/        + prep, discovery call, proposal, objections, negotiation & handoff, expand & referrals
  vintoria-report/       + report playbook and format
docs/                    the Vintoria 270-service catalog (PDF)
```

Your working files (created by the bots): `SELLER-PROFILE.md`, `OFFER.md`, `IDEAL-CUSTOMER-PROFILE.md`, `PIPELINE.md`,
`DO-NOT-CONTACT.md`, `TEAM-BOARD.md`, `SEEN.md`, `RUN-LOG.md`, `HEALTH.md`, `PROOF-BANK.md`, `CONTENT-LOG.md` and
`prospects/<slug>/`.

## Rules the skills enforce

- **No invented facts** — every sentence traces to a page, the prospect's words, the catalog or the profile; a written
  self-check runs before anything goes out.
- **No invented prices** — the catalog has none; prices come only from the profile, otherwise `[PRICE TO CONFIRM]`.
- **Real services only**, cited by exact catalog ID.
- **Only valuable, fresh leads** — under 24 hours by the age on the post, a real buyer with an exact quote, value score
  65+, never a post already in `SEEN.md` or claimed by another bot.
- **Critic check** — a strict yes/no review (by another bot in a team) before anything is posted or sent.
- **Reddit:** only real buyer posts, only where the subreddit allows offers, one comment per post, open about being
  Vintoria, helpful first, never the same text twice; a removed comment or warning pauses Reddit and alerts you.
- **LinkedIn:** a person's pace (LinkedIn's terms don't allow automation), cold email only to emails they published.
- **Compliance** per market: CAN-SPAM, UK PECR, EU GDPR, CASL, Australia Spam Act, India DPDP + TRAI; opt-outs honoured
  forever in `DO-NOT-CONTACT.md`.

Validate the skills with the official checker: `pip install skills-ref`, then `skills-ref validate skills/<name>`
(CI runs it on every push).

## Credits

Built on [ai-sales-team-claude](https://github.com/zubair-trabzada/ai-sales-team-claude) by Zubair Trabzada (MIT), with
ideas from lead-signal-listener, autonomous-sdr, marketingskills and gtm-agents — see
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). History: [CHANGELOG.md](CHANGELOG.md). License: [MIT](LICENSE).
