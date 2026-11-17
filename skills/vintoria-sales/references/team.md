# Running the skills as a sales team

One agent can play every role in order; several agents (or several sessions) can each take a role and work in
parallel. Either way they share the same state, so nothing is lost between them:

- `SELLER-PROFILE.json` + `IDEAL-CUSTOMER-PROFILE.md` (working folder) — who we are, who we sell to
- `~/.ai-sales-team/pipeline.db` — every prospect, contact, touch, reply, sequence, meeting, deal value
- `prospects/<slug>/` — the files about one prospect (dossier, audit, research, drafts)

**Handoffs are pipeline states, not chat messages.** A role picks up work by reading `pipeline.py today` /
`pipeline.py list --stage <stage>` and hands it on by changing the stage and the next action.

## Roles

| Role | Skills | Picks up | Produces | Hands off when |
|---|---|---|---|---|
| **Manager** (setup + daily driver) | `vintoria-setup`, `vintoria-sales`, `vintoria-report` | the day's agenda | profile, ICP, priorities, weekly review | each item is assigned to the right role |
| **Hunter** | `vintoria-lead-hunt` | low funnel (< 20 open leads), new queries | judged buyers + people lists in the pipeline (`new`) with source tags | `stage new`, note with the exact post quote |
| **Researcher** | deep scan (`prospect_scan.py`), `vintoria-prospect-research` | `new` prospects, best score first | `DOSSIER.md`, verified decision-maker email, score | `stage researched` (or `qualified`), `next "write sequence"` |
| **Writer** | `vintoria-outreach`, `vintoria-close` | `researched/qualified` with a verified email | 5-email sequence, claim-checked, approved by the user, queued | `outreach.py approve` done → autopilot sends |
| **Closer** | `vintoria-reply-book`, `vintoria-close` | replies, meetings, proposals | answers within the hour, booked meetings, briefs, proposals, deal values | `stage meeting → proposal → won/lost` |

## Daily rhythm (one agent or many)

1. Manager: `python <SCRIPTS>/ops/autopilot.py tick` (inbox → due emails → agenda), then `python <SCRIPTS>/core/pipeline.py today`.
2. Closer first: every `reply` and `meeting` item (speed wins deals).
3. Writer: sequences for every `researched` prospect with a verified email; batch the approvals for the user.
4. Researcher: deep-scan the top `new` prospects (freshest intent posts first, then best-fit people-database leads).
5. Hunter: only if the agenda tip says the funnel is low, or on the weekly hunt day.
6. Manager (Mondays): `vintoria-report` — keep the sources and queries that booked meetings, drop the rest, update the
   profile (`seller_profile.py set ...`) so every query improves.

## Targets per role (adjust to capacity)

| Role | Weekly target | Quality bar |
|---|---|---|
| Hunter | 50-150 judged leads | ≥ 30 % of kept leads are real buyers (spot-check 10) |
| Researcher | 30-60 dossiers | every dossier has ≥ 2 fact hooks; ≥ 60 % end with a verified email |
| Writer | 20-50 approved sequences | 100 % claim check pass, first email ≤ 120 words |
| Closer | every reply answered < 1 business hour | ≥ 40 % of positive replies → booked meeting |
| Manager | one review | reply rate, meeting rate, cost per meeting by source |

## Rules for every role
- Read `SELLER-PROFILE.json` before acting; never invent proof, prices, people or emails.
- One prospect at a time; never mix facts between prospects.
- The user approves every outgoing message (a sequence is approved once, as a whole).
- Write your result into the pipeline before you finish (stage, note, next action, file attached) — the next role
  only sees what the pipeline shows.
- Parallel agents: don't work the same prospect at once — take the next item in `pipeline.py today` and set its
  next action to "<role> working" first. The database tolerates several writers; `autopilot.py` has its own lock.

## Weekly rhythm

- **Monday:** pipeline review (`vintoria-report`), drop dead segments, refill the funnel, `learn.py report --apply`.
- **Wednesday:** reply quality and objection themes; update the proof map in `OFFER.md` (`vintoria-setup`).
- **Friday:** forecast, stale-deal review, referral and review asks (`vintoria-close`), next week's hunt plan.

## Ownership rules

- One prospect, one owner at a time: set the next action to "<role> working" before you start, clear it when you hand off.
- The Hunter never writes outreach, the Writer never invents research, the Closer never changes the offer.
- Anyone can flag a truth-rule breach; the owner fixes it. If two agents disagree on a fact, the one with a saved, dated
  source wins; otherwise the fact is "Not found".
