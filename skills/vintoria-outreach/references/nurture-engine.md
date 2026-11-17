# Nurture engine — win back the "not now" leads

Most buyers who don't answer aren't saying no — the timing was wrong. The nurture engine watches those leads for a new
reason to talk and contacts them only when there is one. It runs weekly (Wednesday, the Writer) on every `PIPELINE.md`
row with stage `nurture`, and on `lost` rows whose reason was `timing` or `budget` (90+ days old) — **never** on opt-outs,
`DO-NOT-CONTACT.md`, "not interested" or anyone who asked not to be contacted.

## 1. Look for a trigger (10 minutes per lead, newest leads first)

| Trigger | Where to look | Strength |
|---|---|---|
| They posted again about the same need ("still looking for…") | Their LinkedIn activity, their Reddit profile | Strong — act today |
| A new, related need ("now we need an app too") | Same | Strong |
| A dated business event: new branch, launch, funding, rebrand, hiring a marketer | LinkedIn, their site, news | Medium |
| The problem is still visible (site still slow / booking still by phone) after 60+ days | Their site (quick audit facts) | Medium |
| Their date has come ("check back in January") | `next_due` in `PIPELINE.md` | Strong — they asked |
| Nothing new | — | Don't contact |

## 2. Contact only with a trigger

- One message that **starts with the trigger**, adds one useful thing, and asks one easy question. Never "just checking in",
  never "following up on my last email".
- Channel: the one they last answered on; otherwise email (LinkedIn leads) or a reply in their **new** Reddit post (only
  if it's a fresh buyer post under 24 h — it then goes through the normal hourly-run checks).
- Limits: at most **one nurture touch per lead per 30 days**, and **3 in total** without an answer → stage `lost`
  (reason `no-response`), never contacted again.

### Example
> Hi Arjun — saw you opened the second Andheri outlet last week, congratulations. With two locations, letting guests pick
> the branch when they book online saves a lot of phone calls. Are you still taking bookings by phone at both?

## 3. Log
`HISTORY.md` (trigger + source link + date), `THREAD.md` (the message), `PIPELINE.md` (stage `contacted`, `last_touch`,
`next_due` = +30 days, `next_action` "Nurture check"); an answer → `replied` and `vintoria-reply-book`; no answer by
`next_due` → back to `nurture` (or `lost` / `no-response` after the third touch). Count each touch in `RUN-LOG.md` as
`nurture` and add it to the sheet's **Emails** or **Social** tab.

## 4. Monthly value list (optional, only with consent)
Leads who said "keep me posted" or opted in may get one short, useful note a month (a tip from
`comment-angles.md`, a real project story from `PROOF-BANK.md`). No consent → no list. Every note carries the opt-out line.
