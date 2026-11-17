# Running the skills as a sales team

One bot can play every role in order; several bots (or several chats) can each take a role. Either way they share the
same files, so nothing is lost between them: `SELLER-PROFILE.md`, `OFFER.md`, `IDEAL-CUSTOMER-PROFILE.md`,
`PIPELINE.md`, `DO-NOT-CONTACT.md` and `prospects/<slug>/` (`pipeline-format.md`).

**Handoffs are pipeline states, not chat messages.** A role picks up work by reading `PIPELINE.md` (stage, `next_action`,
`next_due`) and hands it on by changing the stage and the next action, and adding a line to the prospect's `HISTORY.md`.

## Roles

| Role | Skills | Picks up | Produces | Hands off when |
|---|---|---|---|---|
| **Manager** | `vintoria-sales`, `vintoria-setup`, `vintoria-report` | the day's agenda | profile, offer, ICP, priorities, weekly review | each item has an owner |
| **Hunter** | `vintoria-lead-hunt` | low funnel (< 20 open), new queries | judged buyers with exact quotes, rows at `new` | row added with source + quote |
| **Researcher** | `vintoria-prospect-research` | `new` rows, freshest intent first | `DOSSIER.md`, audit, contact + email status, score, fitting services | `researched`, next action "write sequence" |
| **Writer** | `vintoria-outreach` | `new`/`researched` rows | Reddit comments with the WhatsApp link, LinkedIn emails from business@vintoria.org, sequences — checked and scored | first message posted/sent → `contacted` |
| **Closer** | `vintoria-reply-book`, `vintoria-close` | replies, meetings, proposals | answers within the hour, booked calls, briefs, proposals | `meeting → proposal → won/lost` |

## Daily rhythm

1. Manager: build today's agenda from `PIPELINE.md` (`pipeline-format.md`).
2. Closer first: every reply and every meeting (speed wins deals).
3. Writer: sequences for every researched prospect with a usable email; batch the approvals for the user.
4. Researcher: the best `new` rows (freshest buyer posts first).
5. Hunter: when the funnel is low, or on the weekly hunt day.

## Weekly rhythm

- **Monday:** `vintoria-report` — keep the sources, queries and hooks that booked meetings, drop the rest, refill the funnel.
- **Wednesday:** reply quality and objection themes; update the proof map in `OFFER.md`.
- **Friday:** forecast, stale-deal review, referral and review asks, next week's hunt plan.

## Targets (adjust to capacity)

| Role | Weekly target | Quality bar |
|---|---|---|
| Hunter | 50-150 judged posts | ≥ 30 % of kept leads are real buyers |
| Researcher | 30-60 dossiers | every dossier ≥ 2 sourced hooks and ≥ 70 on the dossier score |
| Writer | 20-50 approved sequences | 100 % pass the self-check, first email ≤ 120 words, score ≥ 80 |
| Closer | every reply answered < 1 business hour | ≥ 40 % of positive replies → booked call |
| Manager | one review | reply rate, meeting rate, wins by source |

## Ownership rules

- One prospect, one owner at a time: set `next_action` to "<role> working" before you start, change it when you hand off.
- The Hunter never writes outreach, the Writer never invents research, the Closer never changes the offer.
- Nothing goes out that fails the self-check or a platform rule; in `review` mode the user approves every message.
- If two bots disagree on a fact, the one with a saved, dated source wins; otherwise the fact is "Not found".
