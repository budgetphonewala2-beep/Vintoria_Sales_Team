# Pipeline format — the records every PC reads and writes

**On Hermes these live in Airtable** (`airtable.md`): each file name below is the name the skills use for the matching
Airtable table. The formats, values and rules here are the same in both.

No code, no database: the pipeline is a few Markdown files any agent (or person) can read and edit. Keep them boring
and consistent, because the next agent only knows what these files say.

## Files

```
SELLER-PROFILE.md            who Vintoria is: sender, address, markets, active disciplines, prices, proof (user-owned)
OFFER.md                     offer lanes by catalog service ID + the proof map
IDEAL-CUSTOMER-PROFILE.md    segments, signals, disqualifiers, scoring, the search queries that work
PIPELINE.md                  one row per prospect (format below) — the agenda is built from it
DO-NOT-CONTACT.md            opt-outs and bounces, one per line, append-only, never removed
TEAM-BOARD.md                the shared message board (team.md) — the Airtable **Board** — handoffs, claims, reviews, alerts, standups
SEEN.md                      every post URL already judged or claimed, so no post is handled twice
RUN-LOG.md                   per-hour counters and results of the hourly run (shared limits)
HEALTH.md                    account health levels (GREEN / YELLOW / RED) per platform, every 6 hours
PROOF-BANK.md                real results, quotes, reviews and referrals, with the client's permission
CONTENT-LOG.md               LinkedIn posts and their results (vintoria-authority)
AIRTABLE-QUEUE.md            records waiting for Airtable when it couldn't be reached (airtable.md) — local to each PC
SEEN-ARCHIVE.md              SEEN.md lines older than 30 days
SALES-REPORT.md              the weekly report (vintoria-report)
prospects/<slug>/
  DOSSIER.md                 sourced research, hooks, fit to catalog services, contact
  SITE-AUDIT.md              fact-only website audit
  OUTREACH-SEQUENCE.md       the approved emails with their scores and send dates
  THREAD.md                  every message sent and received, with dates (the conversation)
  MEETING-PREP.md            brief for the call
  MEETING-NOTES.md           discovery notes + qualification score
  CLIENT-PROPOSAL.md         the proposal
  HISTORY.md                 append-only log: date — what happened — who
  COMPANY-RESEARCH.md        company research (vintoria-prospect-research)
  DECISION-MAKERS.md         who decides, contacts, email status
  LEAD-QUALIFICATION.md      BANT / MEDDIC qualification
  COMPETITIVE-INTEL.md       what they use today, battle cards
  PROSPECT-ANALYSIS.md       the five-role full analysis
  FOLLOWUP-SEQUENCE.md       follow-ups after a call or proposal
  OBJECTION-PLAYBOOK.md      objection answers prepared for this deal
  CLOSE-PLAN.md              negotiation and signature plan
  EXPANSION-MAP.md           upsell and referral plan after the win
```

`<slug>` = their domain without `www` (`acme.com`), or `name@platform` for someone without a website
(`anita-desai@linkedin`). Never use another prospect's folder as context.

## `PIPELINE.md`

```markdown
| slug | company | contact | title | email | email_status | country | services | channel | stage | score | source | post_url | owner | last_touch | next_action | next_due | outcome | value |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| acme.com | Acme Dental | Priya Shah | Owner | priya@acme.com | published | IN | 033,214 | linkedin-email | contacted | 78 | li:need-website-clinic | https://www.linkedin.com/posts/… | Writer | 2026-11-17 | Email 2 (day 3) | 2026-11-20 | | |
| riya-mehta@linkedin | GlowKart | Riya Mehta | Founder | | | IN | 192 | linkedin-comment | contacted | 87 | li:agency-shopify | https://www.linkedin.com/posts/… | Closer | 2026-11-17 | Check replies | 2026-11-18 | linkedin-reply | |
```

- `services` — catalog IDs, comma-separated (`033,214`); names live in the catalog.
- `channel` — `linkedin-email`, `linkedin-comment`, `linkedin-note`, `linkedin-message` (after they accept), `whatsapp` (they messaged).
- `email_status` — `verified` (a verifier tool said so) · `published` (on their own site or post) · `catch_all` ·
  `unverified` (found elsewhere) · `pattern-guessed` · `invalid`. Cold email only to `verified` or `published`.
- `score` — 0-100 from the scoring tables; `value` — only a real price from the profile, with currency.
- `channel` for email leads is `linkedin-email`; which brand sent which step lives in `OUTREACH-SEQUENCE.md` and the
  Airtable **Emails** table (`Brand` = Vintoria / Radian, `Sender PC` = PC1 / PC2).
- `next_due` — always a real date. A row without `next_action` + `next_due` is not in the pipeline.
- `owner` — the role working it now (plus `claimed_at` time in `HISTORY.md`); change it at every handoff.
- `outcome` — what the first touch produced: `no-reply` · `email-reply` · `linkedin-reply` · `connection-accepted` ·
  `whatsapp-reply` · `call-booked` · `comment-deleted` · `opt-out`. The weekly report ranks queries, lanes, agency intent
  and openings by it.

## `SEEN.md`

One line per post, added the moment it is judged or claimed: `2026-11-17 14:05 · HA · linkedin · https://… · kept 87 (agency)`
or `… · dropped: freelancer-only`. Check it before judging any post; keep 30 days, then move old lines to `SEEN-ARCHIVE.md`.

## `RUN-LOG.md`

One record per PC per hour (Airtable **Runs**); the PC adds to it before it posts or sends (that is how the limits hold):

```markdown
## 2026-11-17 14:00-15:00 IST
- LinkedIn: found 34 · valuable 9 (2 HOT) · emailed 6 (Vintoria 4, Radian 2) · commented 3 · notes 2 · queued 1
- Due emails sent: 11 · Replies: 1 (email) · Alerts: 0 · Skipped by critic: 2
- Limits this hour: emails 6/10 · LinkedIn comments 3/3 · notes today 9/15 · inbox caps today Vintoria 18/30 · Radian 9/15
- Openings used: "For a clinic site the two things…", "Shopify speed usually comes down to…"
```

## Stages

| Stage | Meaning | Moves when |
|---|---|---|
| `new` | found, not researched | dossier written → `researched` |
| `researched` | dossier (+ audit) done | first message sent → `contacted` |
| `contacted` | in the sequence | any human reply → `replied`; no reply after the last email of both brands (day 29) or 7 days after a single comment / note → `nurture` |
| `replied` | they answered | call booked → `meeting`; no → `lost` |
| `meeting` | call booked or held | qualified → `proposal`; not a fit → `lost` / `nurture` |
| `proposal` | proposal sent | verbal yes → `negotiation` |
| `negotiation` | terms being agreed | signed → `won`; no → `lost` |
| `won` → `delivery` → `expand` | signed, being delivered, upsell found | |
| `nurture` | not now, revisit on a trigger | nurture touch sent → `contacted`; 3 nurture touches with no answer → `lost` (`no-response`) |
| `lost` / `disqualified` | closed, reason in `HISTORY.md` (`timing`, `budget`, `no-fit`, `chose-other`, `no-response`, `not-interested`, `opt-out`) | only `timing` / `budget` may re-enter via the nurture engine after 90 days; `no-response`, `not-interested` and `opt-out` never |

## The cadence

- **LinkedIn email:** the first agency's email 1 on day 0, then day 3, 7, 14 and 28; the second agency's email 1 on
  day 1, then day 4, 8, 15 and 29 — every emailed lead gets both (`brands.md`). Never two emails on one day.
- **LinkedIn comment or note (no email found):** one comment per post and one connection note; check the next day; once
  they accept, one short message; no answer 7 days after the last touch → `nurture`.
After every message that went out, write it into `THREAD.md` (with its link), update `last_touch`, and set
`next_action` / `next_due`. Any reply on any channel stops every sequence for that prospect at once.

## Today's agenda (read `PIPELINE.md`, in this order)

1. Rows at `replied` whose last message is theirs — answer within the hour.
2. Fresh buyer posts (under 24 h) not yet in `SEEN.md`.
3. `meeting` rows with a call in the next 24 h (prep) or a past call without notes (outcome).
4. Rows with `next_due` today or earlier.
5. Stale rows (no touch for 14+ days and no email scheduled) — next step, `nurture` or `lost`.
6. The best `new` rows — research them.
If fewer than 20 rows are open (not won / lost / disqualified / nurture), the funnel is low: hunt.

## Metrics (count them from the file, never estimate)

Prospects by stage, source, country and discipline · reply rate = rows that reached `replied` ÷ rows that reached
`contacted` · positive-reply, meeting, proposal and win rates · open and won value per currency · which sources, hooks and
services produced meetings.
