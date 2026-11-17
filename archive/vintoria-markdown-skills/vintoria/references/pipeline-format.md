# Pipeline format — files are the database

No scripts. The pipeline is a folder of plain files an agent can read, edit and reason about. Keep it boring and
consistent.

## Folder layout

```
workspace/
├─ profile/
│  ├─ SELLER-PROFILE.md          # who we are, what we sell, proof, pricing (seller-owned)
│  └─ OFFER.md                   # which of the 270 services we actively sell + proof map
├─ icp/
│  └─ ICP.md                     # segments, triggers, disqualifiers, scoring
├─ pipeline/
│  ├─ pipeline.csv               # one row per prospect (schema below)
│  ├─ suppressions.md            # do-not-contact list (append-only)
│  └─ daily-log/YYYY-MM-DD.md    # what happened today
└─ prospects/<slug>/
   ├─ BRIEF.md                   # one-screen summary: who, why now, service, next step
   ├─ DOSSIER.md                 # sourced research + hooks
   ├─ SITE-AUDIT.md              # fact-only audit with evidence
   ├─ OUTREACH.md                # sequence with scores and approval state
   ├─ REPLIES.md                 # every reply, classification, drafted response
   ├─ MEETING-NOTES.md           # discovery notes, qualification, next step
   ├─ PROPOSAL.md                # scope and options
   └─ HISTORY.md                 # stage changes, dates, owners
```

`slug` = the company domain without `www` (`acme.com`), or `name@platform` for a person with no website
(`anita-desai@linkedin`). Never use spaces or slashes.

## `pipeline.csv` schema

Header exactly:

```csv
slug,company,contact_name,title,email,email_status,country,services,stage,score,next_action,next_due,owner,source,updated
```

- `services` — catalog IDs, semicolon-free, comma-separated (`121,146`). Never names.
- `email_status` — `verified` | `catch_all` | `unverified` | `pattern-guessed` | `invalid`.
- `stage` — see the stage ladder below.
- `score` — 0–100, integer, from the ICP scoring rubric.
- `next_due` — `YYYY-MM-DD`, always a real date the owner can act on.
- `updated` — `YYYY-MM-DD`.

## Stage ladder

| Stage | Meaning | Exit rule |
|---|---|---|
| `new` | imported, not researched | research done → `researched` |
| `researched` | dossier + audit exist | outreach drafted → `contacted` |
| `contacted` | first touch sent/logged | reply → `replied`; 28 days silent → `nurture` |
| `replied` | any human reply | discovery booked → `discovery`; not interested → `lost` |
| `discovery` | call scheduled or held | qualified → `proposal`; not a fit → `lost` |
| `proposal` | proposal sent | verbal yes → `negotiation`; silent 14 days → follow-up |
| `negotiation` | terms being agreed | signed → `won`; no → `lost` |
| `won` | signed | handoff → `delivery` |
| `delivery` | in fulfilment | upsell → `expand`; closed out → `done` |
| `expand` | repeat/upsell opportunity | new deal → `proposal` |
| `nurture` | not now, revisit later | trigger event → `researched` |
| `lost` | closed no | reason recorded; may re-enter after 90 days |
| `done` | delivered and closed | referral request → `expand` |

## Hygiene rules

1. Every row has `next_action` + `next_due`. A row without them is not in the pipeline.
2. Update `updated` whenever anything changes; never rewrite history — append to `HISTORY.md`.
3. One contact row per person. If a person changes company, create a new prospect and note the move.
4. Suppressions: email, domain or phone, one per line, with date and reason. Check before every send.
5. Weekly: stale rows (>14 days no activity) either get a next step or move to `nurture`.

## Metrics the skills report (compute from the CSV, do not estimate)

- Prospects by stage, by discipline, by country.
- Reply rate = rows reaching `replied` ÷ rows reaching `contacted`.
- Positive-reply rate, meeting rate, proposal rate, win rate.
- Median days from `contacted` → `replied`, `replied` → `proposal`, `proposal` → `won`.
- Which source and which service produced meetings and wins.
