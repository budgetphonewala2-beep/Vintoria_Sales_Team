---
name: vintoria-hourly-run
description: "The hourly 24/7 lead engine for Vintoria's bots: every hour finds up to 10 valuable LinkedIn posts and up to 10 valuable Reddit posts that are under 24 hours old and ask to hire something Vintoria sells (website, app, SaaS, design, AI chatbot, automation, Shopify, SEO, marketing), skips anything already seen or claimed by another bot, scores each lead, gets the email from LinkedIn and emails it from business@vintoria.org, posts a professional helpful Reddit comment with Vintoria's WhatsApp link, runs the critic check before every post, keeps the shared hourly limits for all bots, logs everything in RUN-LOG.md and posts an hourly summary and handoffs on the team board. Use it when the scheduler fires the hourly run, or when the user says 'run the hourly cycle', 'har ghante leads nikalo', '24 ghante wale leads', 'hourly run chalao', 'fresh leads abhi', 'start the 24/7 bot'."
license: MIT
compatibility: "Instruction-only Agent Skill: no code. Works in any agent or bot (Claude, Grok, GPT, Gemini…) that can follow instructions; best with a browser logged in to LinkedIn and Reddit, and file access."
metadata:
  author: "Vintoria (built on ai-sales-team-claude by Zubair Trabzada)"
  version: "5.0.0"
---

# Vintoria Hourly Run — fresh LinkedIn and Reddit leads, every hour, 24/7

Every hour the market posts new requests and the first good answer usually wins. This cycle finds the freshest valuable
buyers on LinkedIn and Reddit, contacts the best of them professionally within the hour, and leaves a clean trail so
every other bot — and the owner — knows exactly what happened.

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

## The cycle (one run = one hour)

0. **Sync.** Read `TEAM-BOARD.md` since your last run and act on `ALERT`s and messages to your role first
   (`../vintoria-sales/references/team.md`). Open this hour's block in `RUN-LOG.md` (create it if you are first) and read
   the limits in `SELLER-PROFILE.md` → Automation. A platform paused by a `DECISION` stays paused.
1. **Search, last 24 hours only** — `../vintoria-lead-hunt/references/queries.md`:
   - **LinkedIn:** Posts → Latest → past 24 hours, 4-6 boolean queries from `IDEAL-CUSTOMER-PROFILE.md`, rotating through
     the offer lanes hour by hour (web, app, AI, automation, e-commerce, SEO/marketing) and the markets (India, US, UK, AU).
   - **Reddit:** r/forhire (Hiring), r/smallbusiness, r/Entrepreneur, r/startups, r/indianstartups and Indian city subs,
     r/shopify, r/ChatGPT, r/automation and the niche subs, sorted **New**.
   Collect 25-40 candidates per platform; skip any URL already in `SEEN.md`.
2. **Filter with the exact rules** in `../vintoria-sales/references/lead-quality.md`: age on the post under 24 h (`1d` = too
   old), real buyer with an exact quote, a service in an active lane, right market, no red flags. Add every judged post to
   `SEEN.md` (kept or dropped, with the reason).
3. **Score and rank** (value score 0-100). Keep **up to 10 per platform** that score 65+, freshest and highest first. Fewer
   valuable posts this hour = keep fewer; never lower the bar to reach 10.
4. **Claim** each kept lead (`CLAIM` on the board, `owner` in `PIPELINE.md`) so no other bot touches it.
5. **Get the contact:**
   - LinkedIn: the email in the post → the profile's Contact info → their company site (contact / about). Found → email.
     Not found → a comment (if comments are open) or a connection note.
   - Reddit: the subreddit's rule on offers (in `IDEAL-CUSTOMER-PROFILE.md`; read the sidebar once and note it if new).
     Offers allowed → comment with the WhatsApp link; not allowed → a help-only comment or skip; "DM me" → a short DM.
   A lead scoring 80+ with a company website gets a 5-minute site check (`../vintoria-prospect-research/SKILL.md`, site audit)
   for one sharp observation.
6. **Write** with `../vintoria-outreach/SKILL.md`: the Reddit comment (`../vintoria-outreach/references/reddit-comment-playbook.md`),
   the LinkedIn email (`../vintoria-outreach/references/first-email-guide.md`) or the LinkedIn comment / note
   (`../vintoria-outreach/references/linkedin-playbook.md`). Every message is new — no opening
   line used in the last 7 days.
7. **Critic check** every message (`../vintoria-sales/references/critic-check.md`); in a team, `REVIEW-REQUEST` to the
   Reviewer. Fail twice → skip the lead and record why.
8. **Post / send within the shared limits.** Before each action add 1 to the counter in `RUN-LOG.md`; at the limit, queue
   it for the next hour. Reddit comments at least 4 minutes apart, never two in one subreddit in the same hour. Emails only
   08:00-19:00 on weekdays in the prospect's time zone — otherwise queue for their morning (`next_due`). `review` mode →
   post the drafts to the board for the owner instead of sending.
9. **Log:** `PIPELINE.md` row (stage `contacted`, channel, score, owner, `next_action`, `next_due`), `THREAD.md` (exact text +
   link), `HISTORY.md` (quote, score parts, critic result), `DONE` on the board.
10. **Check replies since the last run** on Reddit (comment replies, inbox, chat), LinkedIn (messages, comment replies) and the
    `business@vintoria.org` inbox: every reply → `ALERT` to the Closer (`vintoria-reply-book`), `outcome` set in `PIPELINE.md`.
    A removed comment or any warning → `ALERT` + pause that platform + `ESCALATE` to the owner.
11. **Summary:** close the hour's block in `RUN-LOG.md` and post one `HOURLY` line on the board:
    `HOURLY 14:00 · LinkedIn 31 found / 10 valuable / 6 emailed / 2 commented / 2 queued · Reddit 27 / 9 / 9 commented · replies 1 · skipped by critic 3`.

## Queue first
Start every run with last hour's queue (emails waiting for the prospect's morning, comments over the limit) — while still
under 24 hours old for comments; older queued comments are dropped, older queued emails still go out.

## When something is wrong
- No valuable posts this hour → say so in the `HOURLY` line and try different queries next hour (note which in `RUN-LOG.md`).
- Logged out, captcha, or a page won't load → `BLOCKED` on the board + `ESCALATE` to the owner; carry on with the other platform.
- The same lead appears on both platforms → one owner, one channel (email beats a comment).

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

- `../vintoria-sales/references/lead-quality.md` — the 24-hour rule, the must-haves, the value score, red flags
- `../vintoria-sales/references/critic-check.md` — the yes/no checks before anything is posted or sent
- `../vintoria-sales/references/team.md` — roles, the team board, claims, handoffs, reviews, alerts, standups
- `../vintoria-sales/references/pipeline-format.md` — PIPELINE.md, SEEN.md, RUN-LOG.md and TEAM-BOARD.md formats
- `../vintoria-lead-hunt/references/queries.md` — LinkedIn boolean queries and the subreddits
- `../vintoria-outreach/references/reddit-comment-playbook.md` — the Reddit comment
- `../vintoria-outreach/references/linkedin-playbook.md` — finding the LinkedIn email, the email, comment and note
