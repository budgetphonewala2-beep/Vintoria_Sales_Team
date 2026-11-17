# Pipeline format — plain files are the database

No code, no database: the pipeline is a few Markdown files any agent (or person) can read and edit. Keep them boring
and consistent, because the next agent only knows what these files say.

## Files

```
SELLER-PROFILE.md            who Vintoria is: sender, address, markets, active disciplines, prices, proof (user-owned)
OFFER.md                     offer lanes by catalog service ID + the proof map
IDEAL-CUSTOMER-PROFILE.md    segments, signals, disqualifiers, scoring, the search queries that work
PIPELINE.md                  one row per prospect (format below) — the agenda is built from it
DO-NOT-CONTACT.md            opt-outs and bounces, one per line, append-only, never removed
TEAM-BOARD.md                the bots' shared message board (team.md) — handoffs, claims, reviews, alerts, standups
SEEN.md                      every post URL already judged or claimed, so no post is handled twice
RUN-LOG.md                   per-hour counters and results of the hourly run (shared limits)
prospects/<slug>/
  DOSSIER.md                 sourced research, hooks, fit to catalog services, contact
  SITE-AUDIT.md              fact-only website audit
  OUTREACH-SEQUENCE.md       the approved emails with their scores and send dates
  THREAD.md                  every message sent and received, with dates (the conversation)
  MEETING-PREP.md            brief for the call
  MEETING-NOTES.md           discovery notes + qualification score
  CLIENT-PROPOSAL.md         the proposal
  HISTORY.md                 append-only log: date — what happened — who
```

`<slug>` = their domain without `www` (`acme.com`), or `name@platform` for someone without a website
(`anita-desai@linkedin`). Never use another prospect's folder as context.

### When you can't save files (chat bots, Grok, custom GPTs)
Keep the same structure in the conversation: at the end of every task print the **changed `PIPELINE.md` rows** and any
new file contents in code blocks, and ask the user to save them (or paste them back next session). Start each session by
asking the user to paste `SELLER-PROFILE.md` and `PIPELINE.md` if you don't have them.

## `PIPELINE.md`

```markdown
| slug | company | contact | title | email | email_status | country | services | channel | stage | score | source | post_url | owner | last_touch | next_action | next_due | outcome | value |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| acme.com | Acme Dental | Priya Shah | Owner | priya@acme.com | published | IN | 033,214 | linkedin-email | contacted | 78 | li:need-website-clinic | https://www.linkedin.com/posts/… | Writer | 2026-11-17 | Email 2 (day 3) | 2026-11-20 | | |
| neha_physio@reddit | Neha's Physio | u/neha_physio | Owner | | | IN | 028 | reddit-comment | contacted | 71 | rd:smallbusiness-website | https://www.reddit.com/r/… | Closer | 2026-11-17 | Check replies | 2026-11-18 | whatsapp-reply | |
```

- `services` — catalog IDs, comma-separated (`033,214`); names live in the catalog.
- `channel` — `reddit-comment`, `reddit-dm`, `linkedin-email`, `linkedin-comment`, `linkedin-note`, `whatsapp` (they messaged).
- `email_status` — `verified` (a verifier tool said so) · `published` (on their own site or post) · `catch_all` ·
  `unverified` (found elsewhere) · `pattern-guessed` · `invalid`. Cold email only to `verified` or `published`.
- `score` — 0-100 from the scoring tables; `value` — only a real price from the profile, with currency.
- `next_due` — always a real date. A row without `next_action` + `next_due` is not in the pipeline.
- `owner` — the role working it now (plus `claimed_at` time in `HISTORY.md`); change it at every handoff.
- `outcome` — what the first touch produced: `no-reply` · `reddit-reply` · `whatsapp-reply` · `email-reply` ·
  `linkedin-reply` · `call-booked` · `removed` (comment removed) · `opt-out`. The weekly report ranks queries, subreddits
  and openings by it.

## `SEEN.md`

One line per post, added the moment it is judged or claimed: `2026-11-17 14:05 · RH · reddit · https://… · kept 82`
or `… · dropped: seller`. Check it before judging any post; keep 30 days, then move old lines to `SEEN-ARCHIVE.md`.

## `RUN-LOG.md`

One block per hour; every bot adds to the same block before it posts or sends (that is how the shared limits hold):

```markdown
## 2026-11-17 14:00-15:00 IST
- LinkedIn: found 31 · valuable 10 · emailed 6 · commented 2 · notes 1 · queued 1
- Reddit: found 27 · valuable 9 · commented 9 · help-only 0 · queued 0
- Replies: 1 (WhatsApp) · Alerts: 0 · Removed: 0 · Skipped by critic: 3
- Limits this hour: Reddit 9/10 · LinkedIn emails 6/10 · LinkedIn comments+notes 3/5
- Openings used: "For a clinic site the two things…", "Shopify speed usually comes down to…"
```

## Stages

| Stage | Meaning | Moves when |
|---|---|---|
| `new` | found, not researched | dossier written → `researched` |
| `researched` | dossier (+ audit) done | first message sent → `contacted` |
| `contacted` | in the sequence | any human reply → `replied`; day 28 with no reply → `nurture` |
| `replied` | they answered | call booked → `meeting`; no → `lost` |
| `meeting` | call booked or held | qualified → `proposal`; not a fit → `lost` / `nurture` |
| `proposal` | proposal sent | verbal yes → `negotiation` |
| `negotiation` | terms being agreed | signed → `won`; no → `lost` |
| `won` → `delivery` → `expand` | signed, being delivered, upsell found | |
| `nurture` | not now, revisit on a trigger | trigger → `researched` |
| `lost` / `disqualified` | closed, reason in `HISTORY.md` | may re-enter after 90 days |

## The cadence

- **LinkedIn email:** email 1 on day 0, then day 3, 7, 14 and 28.
- **Reddit comment / LinkedIn comment or note:** one touch only; check for a reply the next day; no answer in 7 days →
  `nurture` (LinkedIn: one short message after they accept a connection).
After every message that went out, write it into `THREAD.md` (with its link), update `last_touch`, and set
`next_action` / `next_due`. Any reply on any channel stops every sequence for that prospect at once.

## Today's agenda (read `PIPELINE.md`, in this order)

1. Rows at `replied` whose last message is theirs — answer within the hour.
2. Fresh buyer posts (under 24 h) not yet in `SEEN.md`.
3. `meeting` rows with a call in the next 24 h (prep) or a past call without notes (outcome).
4. Rows with `next_due` today or earlier.
5. Stale rows (no touch for 14+ days) — next step, `nurture` or `lost`.
6. The best `new` rows — research them.
If fewer than 20 rows are open (not won / lost / disqualified / nurture), the funnel is low: hunt.

## Metrics (count them from the file, never estimate)

Prospects by stage, source, country and discipline · reply rate = rows that reached `replied` ÷ rows that reached
`contacted` · positive-reply, meeting, proposal and win rates · open and won value per currency · which sources, hooks and
services produced meetings.
