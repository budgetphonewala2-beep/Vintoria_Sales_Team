# Agent roles — one team, one workspace, no duplicated work

Any single agent can run the whole loop. When the platform supports parallel or sub-agents, split by role. Roles
communicate only through files in `workspace/` so a handoff never depends on chat memory.

## The five roles

| Role | Skill | Owns | Hands off to |
|---|---|---|---|
| **Manager** | `vintoria-daily` | the agenda, pipeline hygiene, weekly review, priorities | hunter / writer / closer |
| **Hunter** | `vintoria-hunt` | finding in-market buyers, first-pass scoring, adding rows | researcher |
| **Researcher** | `vintoria-research`, `vintoria-audit` | dossier, audit, hooks, buyer names, fit score | writer |
| **Writer** | `vintoria-outreach`, `vintoria-followup`, `vintoria-reply` | sequences, follow-ups, reply drafts, quality score | closer |
| **Closer** | `vintoria-discovery`, `vintoria-proposal`, `vintoria-objections`, `vintoria-close` | qualification, proposal, negotiation, signature | delivery / expand |

Two supporting skills are shared by everyone: `vintoria-offer` (what we sell) and `vintoria-icp` (who we sell to).
They are read, never rewritten by a single deal.

## Handoff contract

Every handoff is a file update, never a message:

1. Update the prospect's `HISTORY.md` with stage, date, owner, and what changed.
2. Update `pipeline.csv` (`stage`, `next_action`, `next_due`, `owner`, `updated`).
3. Leave the artifact the next role needs in the prospect folder.
4. Do not do the next role's work "quickly" — it is how quality and truth rules slip.

## Daily rhythm (manager)

| Slot | Work |
|---|---|
| Morning | Replies first, then meetings, then due follow-ups |
| Midday | Research + outreach for the best new leads (cap: 10 new prospects/day per agent) |
| Afternoon | Discovery calls, proposals, objection prep |
| End of day | Update files, log the day, set tomorrow's top 3 |

## Weekly rhythm

- Monday: pipeline review, metrics, drop dead segments, refill the funnel.
- Wednesday: check reply quality and objection themes; update `OFFER.md` proof map.
- Friday: forecast, stale-deal review, referral asks, next week's hunt plan.

## Ownership rules

- One prospect, one owner at a time. The `owner` column is the source of truth.
- The hunter never writes outreach. The writer never invents research. The closer never changes the offer.
- Anyone can flag a truth-rule violation; only the owner fixes it.
- If two agents disagree on a fact, the one with a saved, dated source wins; otherwise the fact is `Not found`.
