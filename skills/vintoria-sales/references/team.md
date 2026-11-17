# The Vintoria sales team — roles, the team board, and how bots work together

Several bots can run Vintoria's sales 24/7 like one professional team: each has a role, they talk on a shared **team
board**, hand work over with full context, review each other's messages, and never step on each other. One bot can also
play every role — the protocol is the same.

They can't call each other directly, so everything goes through shared files (`pipeline-format.md`): `TEAM-BOARD.md`
(messages), `PIPELINE.md` (who owns which lead), `SEEN.md` (posts already judged or claimed), `RUN-LOG.md` (counters).
If the bots don't share a folder, use one shared channel all of them can read and write (a Telegram / Slack / Discord
group or a shared Google Doc) with exactly the same message format.

## Roles

| Role | Skill | Owns | Hands off to |
|---|---|---|---|
| **Sales Manager** | `vintoria-sales`, `vintoria-report`, `vintoria-account-health` | the plan, priorities, standups, account health, the owner digest, conflicts, limits, weekly review, escalations | everyone |
| **LinkedIn Hunter** | `vintoria-hourly-run` (LinkedIn half), `vintoria-lead-hunt` | finding valuable LinkedIn posts < 24 h, getting the email | Writer |
| **Reddit Hunter** | `vintoria-hourly-run` (Reddit half), `vintoria-lead-hunt` | finding valuable Reddit posts < 24 h, subreddit rules | Writer |
| **Researcher** | `vintoria-prospect-research` | quick dossiers and site audits for leads scoring 80+ with a website | Writer |
| **Writer** | `vintoria-outreach`, `vintoria-authority` | Reddit comments, LinkedIn emails / comments / notes, follow-ups, nurture, the daily LinkedIn post | Reviewer, then posts |
| **Reviewer** | `critic-check.md` | the critic check on the Writer's messages (any bot except the one that wrote it) | Writer |
| **Closer** | `vintoria-reply-book`, `vintoria-close` | every reply, WhatsApp chat, booking, call prep, proposal, closing, the proof bank after launch | Manager (won / lost) |

With fewer bots, combine roles: 2 bots = Hunter+Researcher / Writer+Closer (Manager = whichever starts the day);
1 bot = all roles, and the Reviewer step is a fresh-eyes self-review.

## The team board (`TEAM-BOARD.md`)

Append-only, newest at the bottom. Every message has this shape:

```
### M-20261117-1405-RH · 14:05 IST · Reddit Hunter → Writer · HANDOFF · neha_physio@reddit
Need: booking website for a physiotherapy clinic in Pune.
Quote: "Need a website for my physio clinic where patients can book appointments"
Post: https://www.reddit.com/r/smallbusiness/comments/… · posted 2 h ago · 1 reply · offers allowed in comments
Score: 82 (intent 23, fresh 12, urgency 9, scope 10, budget 0, DM 7, competition 10, fit 5, contact 5)
Suggested service: 028 Booking Platform Development
Ask: comment within 30 minutes (post is fresh, little competition).
```

- **ID:** `M-<date>-<time>-<role initials>` (SM, LH, RH, RS, WR, RV, CL). Replies quote it: `Re: M-20261117-1405-RH`.
- **Types:** `HANDOFF` · `CLAIM` · `DONE` · `QUESTION` · `ANSWER` · `REVIEW-REQUEST` · `REVIEW` · `ALERT` · `BLOCKED` ·
  `HOURLY` · `STANDUP` · `DECISION` · `ESCALATE` · `HOT` (fast-track lead) · `HEALTH` (account level) · `DIGEST` (owner summary) · `SWEEP` (6-hour inbox sweep) ·
  `HEARTBEAT` (I'm alive — at least one line per bot per hour; see `autopilot.md`).
- **To:** a role, `@all`, or `@owner` (the human — only for `ESCALATE`).
- **Self-contained:** whoever receives a message must be able to act without opening another file — need, exact quote,
  link, age, score, service, ask, deadline.
- **Professional tone:** short, factual, polite, no chit-chat, no blame; disagree with a reason and a proposal.
- **Never** put passwords, tokens or private data of prospects beyond what the task needs on the board.

## How bots coordinate

1. **Start of every turn:** read the board since your last message; handle anything addressed to your role or `@all`
   first (`ALERT` > `HOT` > `QUESTION` > `REVIEW-REQUEST` > `HANDOFF`), then your own work. Check the latest `HEALTH`
   level before any post or send.
2. **Claim before you work.** Post `CLAIM <slug or post URL>` and set `owner` + `claimed_at` in `PIPELINE.md` (and the
   post in `SEEN.md` with your role). A claim lasts 60 minutes; post `DONE` when finished. Never work a lead someone else
   holds; an expired claim can be taken over with a `CLAIM` that quotes the old one.
3. **Hand off with context** (`HANDOFF` message above) and change `owner` in `PIPELINE.md` to the next role.
4. **Review before posting** (Writer → Reviewer): `REVIEW-REQUEST` with the exact text and the critic result; the Reviewer
   answers `REVIEW: approve` or `REVIEW: change — <line> — <fix>` within 10 minutes. No answer in 10 minutes → the Writer
   runs the critic check itself with fresh eyes and records "self-reviewed".
5. **Ask, don't guess:** missing fact → `QUESTION` to the role that knows (a price → `@owner` via `ESCALATE`). The
   asker keeps working on other leads meanwhile.
6. **Alerts:** anyone who sees a reply, WhatsApp message, booking, removed comment or platform warning posts `ALERT` at
   once. Replies → the Closer acts within 15 minutes. A removed comment or warning → the Manager pauses that platform
   (`DECISION: pause Reddit`) until the owner reviews.
7. **Shared limits:** before posting or sending, add 1 to the hour's counter in `RUN-LOG.md`; if the counter is at the
   limit, queue the message for the next hour instead. All bots together stay within the limits in `SELLER-PROFILE.md`.
8. **Conflicts:** two bots on one lead, or disagreement on a fact → the Manager posts a `DECISION`; the fact with a saved,
   dated source wins, otherwise it is "Not found".

## Rhythm (24/7)

| When | Who | What |
|---|---|---|
| Every hour | Hunters | `vintoria-hourly-run`, then one `HOURLY` line: found / valuable / handed off / queued |
| Every hour | Writer, Reviewer | clear all handoffs (freshest first) within the hour |
| Within 15 min of an `ALERT` | Closer | answer the reply, move to WhatsApp / email / call |
| 09:30 and 18:30 owner time | Manager | `STANDUP` to `@all`: last 12 h numbers (from `RUN-LOG.md`), wins, replies, blockers, today's focus (best queries / subreddits) |
| Every 6 hours | Manager | `vintoria-account-health` → `HEALTH` line; level changes are `ALERT`s; the watchdog (`autopilot.md`) |
| Every 6 hours (00/06/12/18 IST) | Closer | full inbox sweep of both brands incl. spam → `SWEEP` line (`autopilot.md`) |
| Weekdays 08:30-10:00 (market morning) | Writer | one LinkedIn post + 5-10 comments on buyers' posts (`vintoria-authority`) |
| Wednesday | Writer | nurture engine on `nurture` leads (`vintoria-outreach`) |
| 21:00 owner time | Manager | `DIGEST` to `@owner` (below) |
| Monday 10:00 | Manager | weekly review (`vintoria-report`): keep what got replies, drop what didn't, update queries and `OFFER.md` |

Standup format:
```
### M-20261117-0930-SM · 09:30 IST · Sales Manager → @all · STANDUP
Last 12 h: LinkedIn 58 found / 21 valuable / 14 emailed · Reddit 61 found / 19 valuable / 17 commented
Replies: 4 (2 WhatsApp, 1 email, 1 Reddit) · Calls booked: 1 · Removed comments: 0
Best: r/smallbusiness + "need a website" (3 replies) · Weak: r/SEO (0 replies, strict rules) → drop
Focus today: clinics + restaurants in Pune and Mumbai; Writer: shorter Reddit openers
Blockers: none
```

## Owner digest (21:00, WhatsApp-ready, 10 lines at most)
```
### M-20261117-2100-SM · 21:00 IST · Sales Manager → @owner · DIGEST
Today: 214 found · 41 valuable · 36 contacted (19 Reddit, 14 email, 3 LinkedIn) · 5 replies · 2 calls booked
Hot: Neha (physio clinic, Pune) wants booking site before Jan — call Thu 11:00
Calls tomorrow: Acme Dental 10:00 IST · Brightleaf (UK) 15:30 IST
Proposals out: 2 · waiting on you: price for 192 Shopify Development [PRICE TO CONFIRM]
Health: Reddit GREEN · LinkedIn YELLOW (captcha 14:10) · Email GREEN
Need from you: 1) Shopify price  2) permission to use the bakery result in posts
```
Numbers come from `RUN-LOG.md`, `PIPELINE.md` and `HEALTH.md` — never estimated.

## Escalate to the owner (`@owner`)

Only for: a price, discount or contract term that isn't in the profile; a legal or compliance doubt; an angry or
threatening prospect; a platform warning, ban or removed comment; a prospect asking for a call today; anything about
money already paid. Use `ESCALATE`, keep it to five lines, and keep working on other leads.

## Targets (per day, adjust in `SELLER-PROFILE.md`)

| Role | Target | Quality bar |
|---|---|---|
| Hunters | up to 10 valuable leads per platform per hour | ≥ 80 % of handed-off leads pass the critic check |
| Writer | every handoff answered within the hour | 100 % pass the critic check; reply rate tracked per opening |
| Closer | every reply answered within 15 minutes | ≥ 40 % of positive replies → booked call |
| Manager | 2 standups, 1 weekly review | numbers from `RUN-LOG.md`, never estimated |
