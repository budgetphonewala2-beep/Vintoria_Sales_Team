<p align="center">
  <img src="banner.svg" alt="Vintoria Sales" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/8_skills-instruction--only-8b5cf6?style=for-the-badge" alt="8 skills">
  <img src="https://img.shields.io/badge/no_code-any_bot-0ea5e9?style=for-the-badge" alt="No code">
  <img src="https://img.shields.io/badge/license-MIT-gray?style=for-the-badge" alt="MIT License">
</p>

# Vintoria Sales — skills that find clients on LinkedIn and Reddit

Eight instruction-only skills (no code, no installs) that run Vintoria's whole sales loop in any bot that can follow
instructions — Grok, Claude, GPT, Gemini, Codex, Cursor — best with a browser already logged in to **LinkedIn** and
**Reddit**:

- **Reddit:** the bot finds people asking for a website, app, AI chatbot, automation, Shopify store, SEO…, reads the post,
  and leaves a **professional, genuinely helpful comment** ending with Vintoria's clickable WhatsApp link.
- **LinkedIn:** the bot finds buyer posts, gets the **email** (post, contact info, company site) and writes a short
  personal email from **business@vintoria.org** — or a professional comment / connection note when there's no email.
- Then it answers replies, books the call in both time zones, preps it, writes the proposal and closes — keeping
  everything in plain Markdown files.

Vintoria is a digital product studio with **270 services in 12 disciplines** (strategy, web, SaaS, mobile, UI/UX,
branding, AI, automation, backend & cloud, e-commerce, marketing & SEO, growth). The skills cite services by exact
catalog ID, never invent prices or results, and read English, Hindi and Hinglish.

**Contact used in every message:** business@vintoria.org · WhatsApp +91 87660 33979 ·
[wa.me/918766033979](https://wa.me/918766033979)

## The 8 skills

| Skill | Say… | Does |
|---|---|---|
| `vintoria-sales` | "aaj ka kaam batao", "run my sales" | The operator: today's agenda from `PIPELINE.md`, routes every request; holds the truth, pricing, quality, compliance and contact rules and the full catalog |
| `vintoria-setup` | "set up Vintoria", "who should we target" | Profile interview (template pre-filled with the catalog, email and WhatsApp), offer lanes by catalog ID, ideal customer + search queries |
| `vintoria-lead-hunt` | "LinkedIn pe clients dhundo", "Reddit pe website wale leads" | LinkedIn posts + Reddit buyer posts, judged with an exact quote, scored, contact path chosen |
| `vintoria-prospect-research` | "research acme.com", "owner kaun hai" | Dossier, fact-only site audit, contacts + email status, BANT/MEDDIC, battle cards, full score — hooks mapped to catalog services |
| `vintoria-outreach` | "is post pe comment karo", "isko email likho" | Reddit comment with WhatsApp link, LinkedIn email from business@vintoria.org + 5-step sequence, follow-ups |
| `vintoria-reply-book` | "client ne reply kiya", "meeting fix karo" | Classifies replies from Reddit, LinkedIn, email and WhatsApp, answers, offers slots in both time zones, invite text |
| `vintoria-close` | "meeting ki taiyari karo", "proposal banao" | Prep brief, scored discovery call, proposal by catalog ID with 3 scope options, objections, negotiation, upsell |
| `vintoria-report` | "pipeline ka report do" | Funnel, rates, value, what works (sources, queries, hooks, services, markets), next week's plan |

```
setup ─► lead-hunt (LinkedIn + Reddit) ─► prospect-research ─► outreach ─► reply-book ─► close ─► report
profile     buyer posts + quotes            dossier + email     comment / email   answer + book   proposal → signed
```

## Use it in your bot

**Agents that support Agent Skills** (Claude Code, Codex, Cursor, Gemini CLI, OpenCode): copy the folders in `skills/`
into the agent's skills folder — `~/.claude/skills`, `~/.agents/skills` (Codex, Cursor, Gemini, OpenCode),
`~/.cursor/skills`, `~/.gemini/skills` or `~/.config/opencode/skills`.

**Grok and other chat bots / custom assistants:** give the bot `skills/vintoria-sales/SKILL.md` as its main
instructions, and add the other `SKILL.md` files plus their `references/` folders as knowledge files. Tell it to read the
matching skill before each job. Without file access it keeps the pipeline in the chat and prints the updated rows for you
to save (`skills/vintoria-sales/references/pipeline-format.md`).

**First run:** say **"use vintoria-setup"** and answer the questions (sender name, postal address, time zone, active
disciplines, prices, real case studies). Then **"aaj ka kaam batao"** every day.

**Approval mode** (in `SELLER-PROFILE.md`): `auto` — the bot posts comments and sends emails that pass every check
itself; `review` — you approve each message first. Daily limits: Reddit 8 comments, LinkedIn 10 comments /
15 connection requests / 20 DMs, ~20 cold emails.

## Folders

```
skills/
  vintoria-sales/        SKILL.md + references/: truth-rules, quality-bar, pricing-policy, compliance,
                         vintoria-contact, pipeline-format, team, service-catalog + services-01…12 (all 270 services)
  vintoria-setup/        + seller-profile-template, intake, offer-lanes, ICP playbook and format
  vintoria-lead-hunt/    + queries (LinkedIn boolean, subreddits), intent-rubric (30 labelled examples)
  vintoria-prospect-research/  + research, contacts, qualify, competitors, analysis playbooks, 5 roles
  vintoria-outreach/     + reddit-comment-playbook, linkedin-playbook, first-email guide, quality score, templates
  vintoria-reply-book/
  vintoria-close/        + prep, discovery call, proposal, objections, negotiation & handoff, expand & referrals
  vintoria-report/       + report playbook and format
docs/                    the Vintoria 270-service catalog (PDF)
```

Your working files (created by the bot): `SELLER-PROFILE.md`, `OFFER.md`, `IDEAL-CUSTOMER-PROFILE.md`, `PIPELINE.md`,
`DO-NOT-CONTACT.md` and `prospects/<slug>/`.

## Rules the skills enforce

- **No invented facts** — every sentence traces to a page, the prospect's words, the catalog or the profile; a written
  self-check runs before anything goes out.
- **No invented prices** — the catalog has none; prices come only from the profile, otherwise `[PRICE TO CONFIRM]`.
- **Real services only**, cited by exact catalog ID.
- **Reddit:** only real buyer posts, only where the subreddit allows offers, one comment per post, open about being
  Vintoria, helpful first, never the same text twice; a removed comment or warning stops Reddit activity.
- **LinkedIn:** a person's pace (LinkedIn's terms don't allow automation), cold email only to emails they published.
- **Compliance** per market: CAN-SPAM, UK PECR, EU GDPR, CASL, Australia Spam Act, India DPDP + TRAI; opt-outs honoured
  forever in `DO-NOT-CONTACT.md`.

Validate the skills with the official checker: `pip install skills-ref`, then `skills-ref validate skills/<name>`
(CI runs it on every push).

## Credits

Built on [ai-sales-team-claude](https://github.com/zubair-trabzada/ai-sales-team-claude) by Zubair Trabzada (MIT), with
ideas from lead-signal-listener, autonomous-sdr, marketingskills and gtm-agents — see
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). History: [CHANGELOG.md](CHANGELOG.md). License: [MIT](LICENSE).
