# Autopilot — the team runs 24/7 without waiting for a human

With `Approval mode: auto` the three PCs never stop to wait for the owner. Every situation has a **default safe action**; an
`ESCALATE` to the owner is a notification, never a pause. They keep working on everything else and pick the
escalated item back up when the owner answers (the Airtable **Board**).

## The loop (the scheduled jobs in `hermes-setup.md`)

| Every | Which PC | What |
|---|---|---|
| 15 min | PC3 | fast reply check: LinkedIn messages and comment replies, both email inboxes |
| 1 hour | PC1, PC2, PC3 | `vintoria-hourly-run` for its lanes — due emails of its brand first, then new leads, then a reply check |
| **6 hours** (00:00, 06:00, 12:00, 18:00 IST) | PC3 | **full inbox sweep** (below) |
| 6 hours (:05) | each PC | `vintoria-account-health` for its own LinkedIn account and inbox |
| Daily 08:00 | PC3 | the **watchdog** (below) |
| Daily 21:00 | PC3 | owner `DIGEST` |
| Weekly | PC3 · PC1 + PC2 · every PC | `vintoria-report` (Mon) · nurture (Wed) · `self-test.md` (Sun 03:00 IST) |

## Full inbox sweep — every 6 hours, both brands

Fast checks can miss things; the sweep catches everything:
1. Open **both** inboxes — `business@vintoria.org` and `amar@radianmarketing.site` (and `hi@radianmarketing.com` if the
   PC has access) — including **Spam / Junk, Promotions and Updates** folders, back to the previous sweep.
2. Match every message to a lead (sender address, domain, name, subject thread, `THREAD.md`). Unknown sender → new lead
   check (`lead-quality.md`) or `wrong person`.
3. Classify (`vintoria-reply-book`): human reply · out-of-office (move the next email past their return date) · bounce
   (`invalid`, stop that address) · unsubscribe / "stop" (`DO-NOT-CONTACT.md`, both brands) · auto-reply / ticket.
4. **Any human reply → stop both brands' sequences** (Airtable **Emails** → `stopped`), `ALERT` to the Closer, answer within
   the reply rules. Replies found in Spam → move them to the inbox (helps future delivery) and answer.
5. Also sweep: LinkedIn messages, comment replies, accepted connections (→ the short follow-up message), missed WhatsApp chats.
6. Log one line on the board: `SWEEP 12:00 · Vintoria 3 replies / 1 bounce / 2 OOO · Radian 1 reply · Spam 1 rescued · LinkedIn 2 · all answered`
   and update Airtable (**Replies**, **Emails**, **Leads**).

## The watchdog — no PC's work is ever left undone

Every PC writes a **Runs** record every hour. The watchdog (PC3 daily, and every hourly run as it starts) checks:

| Problem | Default action (no human needed) |
|---|---|
| A PC with no Runs record for 2+ hours | Its lanes are hunted by the other PCs until it is back (`CLAIM role:<PC>-lanes` on the Board); the owner is told (the PC may be off, logged out, or on a captcha). |
| PC3 silent for 2+ hours | PC1 takes the reply checks (if it can read both inboxes) and PC2 the digest, until PC3 is back. |
| A claim older than 60 min, not done | Re-claim it and finish the work. |
| Due emails not sent for 2+ hours | The sending PC's next run sends them first; if its inbox fails, `BLOCKED` + `ESCALATE`. |
| The same post or person saved twice | Keep the older record, mark the newer `Stage` = disqualified (`duplicate`), stop its emails. |
| Airtable unreachable | Records to `AIRTABLE-QUEUE.md` on that PC; written first at the next run; nobody is contacted until saved. |
| A scheduled run failed | Hermes delivers the failure to the owner; the next run retries. |

## Default actions for everything else

| Situation | Default action | Owner notified? |
|---|---|---|
| A price that isn't in the profile / `radian-profile.md` | "Depends on scope — two quick questions and I'll send a written scope with options"; proposal with `[PRICE TO CONFIRM]` sent only after the owner fills it | yes, in the `DIGEST` |
| A fact you can't verify | Leave it out | no |
| A lead you're unsure about (confidence < 0.7) | Skip it | no |
| A message that fails the critic check twice | Skip the lead | no |
| Page won't load / timeout | Retry once after 5 minutes, then skip and move on | no |
| Captcha / "verify it's you" / logged out | Stop LinkedIn activity, set YELLOW, keep sending due emails | yes, `ESCALATE` — only a human can solve a captcha or log in |
| Deleted comments / warning / restriction | Health check at once; YELLOW or RED; RED pauses LinkedIn | yes, `ESCALATE` |
| Email bounces over 2 % | That inbox to YELLOW (half volume), verify addresses before sending | in the `DIGEST` |
| A prospect wants a call today | Offer the two earliest slots from the profile's booking link | yes, `ALERT` |
| An angry or legal message | One calm, polite line, no argument; stop all outreach to them | yes, `ESCALATE` |
| A prospect messages on WhatsApp | PC3 drafts the reply on the Board within 5 minutes and answers by email or LinkedIn too if they used it | yes, `ALERT` (a human sends it) |
| A skill or prompt seems broken (repeated mistakes) | Run `self-test.md`; any fail → that PC switches to `review` mode until fixed | yes, `ESCALATE` |

## What truly needs a human (keep these few and fast)
Logging in and solving captchas · lifting a RED account level · prices and discounts not in the profile · sending
sending the WhatsApp replies PC3 drafts · confirming the radianmarketing.site redirect (one time) ·
real client results for the proof bank. Everything else runs on its own.

## Never on autopilot
No new platform, no new email address, no limit increase, no change to the skills themselves — those wait for the owner. A PC never tries to bypass a captcha, a rate limit or a ban.
