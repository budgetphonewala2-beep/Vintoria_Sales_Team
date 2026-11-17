---
name: vintoria-account-health
description: "Protects the Reddit and LinkedIn accounts Vintoria's bots run on: checks for a Reddit shadowban and removed comments from a logged-out view, tracks karma, removals, warnings, captchas and LinkedIn restrictions, keeps the helpful-to-promotional comment mix healthy, and sets a GREEN / YELLOW / RED level in HEALTH.md that every other skill obeys (full limits, half limits, or pause and escalate). Use it every 6 hours, after any removed comment, captcha or warning, before raising limits, or when the user says 'account safe hai?', 'check shadowban', 'reddit ban to nahi hua', 'linkedin restricted', 'account health check', 'why are comments not showing'."
license: MIT
compatibility: "Instruction-only Agent Skill: no code. Works in any agent or bot (Claude, Grok, GPT, Gemini…) that can follow instructions; best with a browser logged in to LinkedIn and Reddit, and file access."
metadata:
  author: "Vintoria (built on ai-sales-team-claude by Zubair Trabzada)"
  version: "7.0.0"
---

# Vintoria Account Health — keep the Reddit and LinkedIn accounts alive

At 24/7 volume the most expensive thing that can happen is not a lost lead, it's a lost account. This skill watches the
accounts like a doctor, and every other skill slows down or stops when it says so.

## Before you start

1. **Your files.** Everything lives in plain files — `SELLER-PROFILE.md`, `OFFER.md`, `IDEAL-CUSTOMER-PROFILE.md`,
   `PIPELINE.md`, `DO-NOT-CONTACT.md` and `prospects/<slug>/` (format: `../vintoria-sales/references/pipeline-format.md`). If you can't read or
   write files (a chat bot such as Grok), ask the user to paste `SELLER-PROFILE.md` and the relevant `PIPELINE.md` rows,
   and finish by printing every changed row and file in code blocks for them to save. Mirror every change to the
   connected Google Sheet (`../vintoria-sales/references/sheet-sync.md`) — update by key, never duplicate, never delete.
2. **Vintoria's profile.** Read `SELLER-PROFILE.md` if it exists. If not, carry on with what the user told you and
   suggest `vintoria-setup` at the end — never block urgent work on it.
3. **What Vintoria sells.** 270 services in 12 disciplines — `../vintoria-sales/references/service-catalog.md`. Name a service exactly as the
   catalog does (`192 Shopify Development`), never invent one, and never quote a price, discount or date that isn't in
   `SELLER-PROFILE.md` — write `[PRICE TO CONFIRM]` (`../vintoria-sales/references/pricing-policy.md`).
4. **Platforms.** Leads come only from **LinkedIn and Reddit**, through the accounts already logged in on this machine.
   Open a page before you state a fact from it and note its URL and date; a search snippet alone is not a fact. If you
   can't open something, write "Not found".
5. **Facts only.** Every sentence traces to a page you opened, the prospect's own words, a fact you observed on their site,
   the catalog or the profile — never to memory. Never say something was sent, posted, booked or verified unless it
   really happened. Run the self-check in `../vintoria-sales/references/truth-rules.md` before anything goes out.
6. **Contact details** — Vintoria: `business@vintoria.org`, WhatsApp +91 87660 33979 (`https://wa.me/918766033979`);
   Radian Marketing: `amar@radianmarketing.site` — and every sign-off come only from `../vintoria-sales/references/vintoria-contact.md`. Each
   brand's emails carry that brand's real identity (`../vintoria-sales/references/brands.md`).
7. **The team.** Read `TEAM-BOARD.md` before you start and handle messages to your role; `CLAIM` a lead before working it,
   hand off with full context, post `ALERT`s at once (`../vintoria-sales/references/team.md`). Alone, you play every role with the same files.

## When it runs
Every 6 hours (00:00, 06:00, 12:00, 18:00 IST) via the scheduler, and **at once** after any removed comment, captcha,
warning, failed login or "you're doing that too much" message. The Sales Manager owns it.

## 1. Reddit checks
1. **Shadowban / removal check (logged out).** Open a private window (not logged in), go to
   `https://www.reddit.com/user/<username>` and to 3 of the last 10 comments by their URL.
   - Profile says the page doesn't exist / is suspended, while logged in it works → likely **shadowbanned** → RED.
   - Profile fine but a comment shows `[removed]` or is missing → **removed by the subreddit / filter** → note the
     subreddit; 1 in 24 h → YELLOW; 3+ in 24 h → RED.
2. **Counts from `RUN-LOG.md`** for the last 24 h: promotional comments (with the WhatsApp link) vs help-only comments.
   Keep at least **1 help-only comment for every promotional one**; Reddit's long-standing guidance is that most of an
   account's activity should not be self-promotion. Below that ratio → YELLOW until it recovers.
3. **Karma and age:** note comment karma and account age each check. Karma falling over two checks → YELLOW.
   Account younger than 30 days or under 100 comment karma → treat as YELLOW permanently (new accounts get filtered).
4. **Messages from Reddit or moderators** (inbox): any warning or temporary ban → RED.

## 2. LinkedIn checks
- A captcha, "verify it's you", "you've reached the weekly invitation limit" or "unusual activity" → YELLOW.
- A restricted-account page, forced logout or ID verification request → RED.
- Pending connection invitations over 300 → withdraw the oldest (LinkedIn counts pending invites) and YELLOW for invites.
- Email side (`business@vintoria.org`): bounces over 2 % or any spam complaint in 14 days → YELLOW for email; over 5 % → RED for email.

## 3. Set the level in `HEALTH.md`
```markdown
## 2026-11-17 12:00 IST
Reddit: GREEN | YELLOW | RED — <reason, with links>   · karma <n> (<+/-n>) · promo/help 24 h <a>/<b> · removed 24 h <n>
LinkedIn: GREEN | YELLOW | RED — <reason>            · pending invites <n> · captchas 24 h <n>
Email: GREEN | YELLOW | RED — <reason>               · bounces 14 d <n %>
Next check: <time>
```

| Level | What every skill does (the hourly run reads this first) |
|---|---|
| **GREEN** | Limits from `SELLER-PROFILE.md` → Automation. |
| **YELLOW** | Half the limits on that platform; Reddit: every promotional comment must be followed by a help-only one; no new subreddits; LinkedIn: no connection notes, comments only on posts under 6 h. Re-check in 2 hours; 24 h clean → GREEN. |
| **RED** | Stop all activity on that platform at once; `ALERT` + `ESCALATE` to the owner with the evidence; only the owner sets it back (to YELLOW, never straight to GREEN). Replies to existing conversations may continue by hand. |

## 4. Help-only comments (account health, not sales)
When Reddit needs help-only comments, the Writer posts genuinely useful answers in the same subreddits — questions about
websites, Shopify, apps, SEO, automation — with **no link, no number, no mention of Vintoria**, using the tip bank in
`../vintoria-outreach/references/comment-angles.md`. They count in `RUN-LOG.md` as `help-only`. They also earn karma and
make the account look (and be) a real contributor.

## 5. Report
Post one `HEALTH` line on `TEAM-BOARD.md`: `HEALTH 12:00 · Reddit GREEN (karma 412 +18, promo/help 22/25, removed 0) · LinkedIn GREEN · Email GREEN`.
A level change is an `ALERT`, and RED is also an `ESCALATE` to the owner.

## Rules
- Never create or use a second account, never vote-manipulate, never delete-and-repost a removed comment, never ask a
  moderator to restore it in the bot's name — the owner decides.
- Never raise limits while any platform is YELLOW or RED.

## References (read when you reach that step)

- `../vintoria-sales/references/team.md` — HEALTH and ALERT messages, escalation to the owner
- `../vintoria-sales/references/compliance.md` — platform rules for Reddit and LinkedIn
- `../vintoria-outreach/references/comment-angles.md` — the tip bank for help-only comments
