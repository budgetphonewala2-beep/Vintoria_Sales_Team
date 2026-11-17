# Autopilot — the team runs 24/7 without waiting for a human

With `Approval mode: auto` the bots never stop to wait for the owner. Every situation has a **default safe action**; an
`ESCALATE` to the owner is a notification, never a pause. The bots keep working on everything else and pick the
escalated item back up when the owner answers (`TEAM-BOARD.md`).

## The loop (scheduler messages in `bot-prompts.md`)

| Every | Who | What |
|---|---|---|
| 15 min | Closer | fast reply check: Reddit, LinkedIn, both email inboxes, WhatsApp (where the bot has access) |
| 1 hour | Hunters | `vintoria-hourly-run` — due emails of both brands first, then new leads, then a reply check |
| **6 hours** (00:00, 06:00, 12:00, 18:00 IST) | Closer | **full inbox sweep** (below) |
| 6 hours | Manager | `vintoria-account-health` + the **watchdog** (below) |
| Daily 21:00 | Manager | owner `DIGEST` |
| Weekly | Manager | `vintoria-report`; Writer: nurture (Wed); Manager: self-test (Sun 03:00 IST, `self-test.md`) |

## Full inbox sweep — every 6 hours, both brands

Fast checks can miss things; the sweep catches everything:
1. Open **both** inboxes — `business@vintoria.org` and `amar@radianmarketing.site` (and `hi@radianmarketing.com` if the
   bot has access) — including **Spam / Junk, Promotions and Updates** folders, back to the previous sweep.
2. Match every message to a lead (sender address, domain, name, subject thread, `THREAD.md`). Unknown sender → new lead
   check (`lead-quality.md`) or `wrong person`.
3. Classify (`vintoria-reply-book`): human reply · out-of-office (move the next email past their return date) · bounce
   (`invalid`, stop that address) · unsubscribe / "stop" (`DO-NOT-CONTACT.md`, both brands) · auto-reply / ticket.
4. **Any human reply → stop both brands' sequences** (sheet **Emails** → `stopped`), `ALERT` to the Closer, answer within
   the reply rules. Replies found in Spam → move them to the inbox (helps future delivery) and answer.
5. Also sweep: Reddit inbox and comment replies, LinkedIn messages and comment replies, missed WhatsApp chats.
6. Log one line on the board: `SWEEP 12:00 · Vintoria 3 replies / 1 bounce / 2 OOO · Radian 1 reply · Spam 1 rescued · Reddit 2 · LinkedIn 1 · all answered`
   and update the sheet (**Replies**, **Emails**, **Leads**).

## The watchdog — no role is ever left empty

Every bot posts at least one line on `TEAM-BOARD.md` per hour (`HOURLY`, `DONE`, `SWEEP`, or `HEARTBEAT <role> ok`).
Every 6 hours — and whenever any bot notices — the Manager checks:

| Problem | Default action (no human needed) |
|---|---|
| A bot silent for 2+ hours | Its role fails over: the next bot in this order takes it over and posts `CLAIM role:<role>` — Closer → Writer → Manager; Writer → Reviewer → Manager; Hunters → each other → Manager; Manager → Closer. The silent bot gets its role back when it posts again. |
| A claim older than 60 min with no `DONE` | Re-claim it and finish the work. |
| A `REVIEW-REQUEST` unanswered for 10 min | The Writer self-reviews with fresh eyes and records "self-reviewed". |
| Due emails not sent for 2+ hours | The next hourly run sends them first; if the inbox fails, `BLOCKED` + switch that brand's emails to the next working window. |
| The sheet unreachable | Rows to `SHEET-QUEUE.md`; sync at the next run. |
| `PIPELINE.md` and the sheet disagree | The newer `updated_at` wins; fix the other. |

## Default actions for everything else

| Situation | Default action | Owner notified? |
|---|---|---|
| A price that isn't in the profile / `radian-profile.md` | "Depends on scope — two quick questions and I'll send a written scope with options"; proposal with `[PRICE TO CONFIRM]` sent only after the owner fills it | yes, in the `DIGEST` |
| A fact you can't verify | Leave it out | no |
| A lead you're unsure about (confidence < 0.7) | Skip it | no |
| A message that fails the critic check twice | Skip the lead | no |
| Page won't load / timeout | Retry once after 5 minutes, then skip and move on | no |
| Captcha / "verify it's you" / logged out | Stop that platform, set YELLOW, continue on the other platforms | yes, `ESCALATE` — only a human can solve a captcha or log in |
| Removed comment / warning / ban | Health check at once; YELLOW or RED; RED pauses the platform | yes, `ESCALATE` |
| Email bounces over 2 % | That inbox to YELLOW (half volume), verify addresses before sending | in the `DIGEST` |
| A prospect wants a call today | Offer the two earliest slots from the profile's booking link | yes, `ALERT` |
| An angry or legal message | One calm, polite line, no argument; stop all outreach to them | yes, `ESCALATE` |
| WhatsApp reply but no bot has WhatsApp access | Answer by email or on the platform they came from if possible; draft the WhatsApp reply on the board | yes, `ALERT` (a human sends it) |
| A skill or prompt seems broken (repeated mistakes) | Run `self-test.md`; any fail → that bot switches to `review` mode until fixed | yes, `ESCALATE` |

## What truly needs a human (keep these few and fast)
Logging in and solving captchas · lifting a RED account level · prices and discounts not in the profile · sending
WhatsApp messages when no bot has WhatsApp Web access · confirming the radianmarketing.site redirect (one time) ·
real client results for the proof bank. Everything else runs on its own.

## Never on autopilot
No new platform, no new email address, no limit increase, no change to the skills themselves — those wait for the owner.
A new subreddit only after the bot has read its rules and noted them in `IDEAL-CUSTOMER-PROFILE.md`. A bot never tries to bypass a captcha, a rate limit or a ban.
