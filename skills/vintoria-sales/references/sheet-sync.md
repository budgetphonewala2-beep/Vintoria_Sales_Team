# Spreadsheet sync — every lead, message, reply and deal in one live sheet

The owner's Google Sheet (connected to the bots) is the team's dashboard. The Markdown files stay the bots' working
memory; the sheet mirrors them so the owner sees everything live and can sort, filter and share it.
Sheet name and link: `SELLER-PROFILE.md` → Brands & sheet.

## Tabs and columns (create them exactly like this, row 1 = headers)

**Leads** — one row per prospect (key: `slug`)
`slug | found_at | platform | post_url | post_age_h | quote | name | title | company | website | email | email_status |
country | timezone | services | value_score | hot | brand_primary | radian_sequence | stage | owner | last_touch |
next_action | next_due | outcome | deal_value | currency | updated_at`

**Emails** — one row per scheduled or sent email (key: `email_id` = `<slug>-<brand>-<step>`)
`email_id | slug | brand | from | to | step | day | scheduled_for | sent_at | subject | words | quality_score | critic |
status | thread_link | updated_at`
`brand` = Vintoria / Radian · `step` = 1-5 · `day` = 0/3/7/14/28 (Radian: 1/4/8/15/29) ·
`status` = scheduled / sent / bounced / replied / stopped / skipped

**Social** — one row per Reddit comment, LinkedIn comment, note or post (key: `link`)
`at | platform | type | slug | subreddit_or_author | link | words | opening_shape | critic | status | replies | updated_at`
`type` = reddit-comment / help-only / linkedin-comment / linkedin-note / authority-post / authority-comment ·
`status` = live / removed / deleted

**Replies** — one row per incoming reply (key: `slug` + `received_at`)
`received_at | slug | channel | brand | category | summary | answered_at | minutes_to_answer | next_step`

**Deals** — one row per call or proposal (key: `slug`)
`slug | call_at | discovery_score | proposal_sent_at | options | value | currency | status | won_at | lost_reason | proof_id`

**Daily** — one row per day (key: `date`)
`date | found | valuable | hot | contacted_reddit | contacted_email_v | contacted_email_r | linkedin_touches | replies |
calls_booked | proposals | won | value_won | removed_comments | health_reddit | health_linkedin | health_email`

**Health** — one row per health check: `at | platform | level | reason | karma | promo_help_24h | removed_24h | bounces_14d`

## When to write (the bot that did the action writes the row)

| Event | Tab | Action |
|---|---|---|
| Lead kept in the hourly run | Leads | add row (or update if `slug` exists) |
| Email scheduled / sent / bounced | Emails | add on schedule, update `sent_at` / `status` |
| Comment, note or post published | Social | add row with the live link |
| Reply received | Replies + Leads | add reply; Leads `stage`, `outcome`; Emails of **both** brands for that slug → `stopped` |
| Opt-out or bounce | Leads + Emails | `stage` lost, all future emails of both brands → `stopped` |
| Call booked / proposal / won / lost | Deals + Leads | add or update |
| End of each hourly run | Daily | update today's row from `RUN-LOG.md` |
| Health check | Health + Daily | add row; update today's levels |

## Rules that keep it clean

- **Update, never duplicate:** find the row by its key column first; add a new row only if the key isn't there.
- **Never delete rows.** Change `status` / `stage` instead, so history and reports stay correct.
- `updated_at` on every write, ISO time with zone (`2026-11-17T14:05+05:30`).
- **Same values as the files:** stages, categories and statuses exactly as in `pipeline-format.md`; dates `YYYY-MM-DD`.
- **Reconcile hourly** (Sales Manager, end of the hourly run): every `PIPELINE.md` row has a Leads row with the same
  `stage`, `next_due` and `outcome`; every message in `THREAD.md` this hour has an Emails or Social row. On a mismatch the
  newer `updated_at` wins; fix the other side and note it in `RUN-LOG.md`.
- **Sheet not reachable** → keep working, queue the rows in `SHEET-QUEUE.md`, write them at the next run (oldest first).
- No passwords, tokens, or private data beyond what the job needs (no personal phone numbers unless they shared them to
  be contacted).

## Dashboard tab (formulas the owner can paste once)

| Cell | Shows | Formula |
|---|---|---|
| B2 | Leads today | `=COUNTIFS(Leads!B:B,">="&TODAY())` |
| B3 | Hot leads today | `=COUNTIFS(Leads!B:B,">="&TODAY(),Leads!Q:Q,TRUE)` |
| B4 | Emails sent today | `=COUNTIFS(Emails!I:I,">="&TODAY(),Emails!N:N,"sent")` |
| B5 | Replies today | `=COUNTIFS(Replies!A:A,">="&TODAY())` |
| B6 | Reply rate, last 30 days | `=COUNTIFS(Replies!A:A,">="&TODAY()-30)/MAX(1,COUNTIFS(Emails!I:I,">="&TODAY()-30,Emails!N:N,"sent")+COUNTIFS(Social!A:A,">="&TODAY()-30))` |
| B7 | Replies to Vintoria vs Radian | `=COUNTIFS(Replies!D:D,"Vintoria")&" / "&COUNTIFS(Replies!D:D,"Radian")` |
| B8 | Median minutes to answer | `=MEDIAN(Replies!H:H)` |
| B9 | Calls booked this month | `=COUNTIFS(Deals!B:B,">="&EOMONTH(TODAY(),-1)+1)` |
| B10 | Won value this month | `=SUMIFS(Deals!F:F,Deals!H:H,"won",Deals!I:I,">="&EOMONTH(TODAY(),-1)+1)` |
| B11 | Removed comments, 7 days | `=COUNTIFS(Social!A:A,">="&TODAY()-7,Social!J:J,"removed")` |

Column letters follow the header order above; if a column is added, update the formulas. Format `found_at`, `sent_at`,
`at`, `received_at`, `call_at` and `won_at` as date-time so the `>=TODAY()` comparisons work.
