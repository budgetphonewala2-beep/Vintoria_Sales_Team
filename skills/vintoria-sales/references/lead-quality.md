# Lead quality — what a "valuable lead" is, and the 24-hour rule

The hourly run keeps up to 10 leads per platform per hour. They must be **valuable**, not just many: one real buyer
answered fast is worth more than ten weak ones. If an hour has only four valuable posts, keep four and say so.

## 1. The 24-hour rule (exact)

Read the age on the post itself, not on the search result.

| Platform | Shows | Keep? |
|---|---|---|
| LinkedIn | `12m`, `45m`, `3h`, `23h` | yes |
| LinkedIn | `1d`, `2d`, `1w` | **no** — `1d` can mean 24-47 hours |
| Reddit | `5 min. ago`, `3 hr. ago`, `23 hr. ago` | yes |
| Reddit | `1 day ago` or older | **no** |
| Edited post | the original post time counts | |

Priority by age: under 2 hours = act first, 2-12 hours = high, 12-24 hours = normal.

## 2. Must-haves (all of them, or it isn't a lead)

1. **A buyer** — the author (or their business) wants to hire or pay for a service, per
   `../../vintoria-lead-hunt/references/intent-rubric.md`, confidence ≥ 0.7, with an **exact quote** that proves it.
2. **We sell it** — the need maps to at least one catalog service in an active lane of `OFFER.md`.
3. **Right market** — India, United States, United Kingdom or Australia (or the profile's targets): stated, or clear from
   the profile, subreddit, currency or city.
4. **Not excluded** — not an agency, freelancer, job seeker or job ad; not in `DO-NOT-CONTACT.md`; not in `SEEN.md`; not
   claimed by another bot; not contacted in the last 30 days.
5. **Reachable** — Reddit: the subreddit allows offers in comments (or the post says "DM me"). LinkedIn: an email in the
   post, contact info or company site — or the post accepts comments.

## 3. Value score (0-100) — rank the must-haves, keep the best

| Part | Max | Score |
|---|---|---|
| Intent | 25 | 25 × confidence they are a real buyer (0-1) |
| Freshness | 15 | < 2 h 15 · 2-6 h 12 · 6-12 h 9 · 12-24 h 6 |
| Urgency | 15 | deadline / "asap" / launch date 15 · clear plan 9 · unknown 6 · "someday" 3 |
| Scope clarity | 10 | they described what they need (pages, features, platform) 10 · vague 4 |
| Budget | 8 | a budget or range stated 8 · none 0 |
| Decision maker | 7 | founder / owner / director / the person paying 7 · an employee asking for a boss 3 |
| Low competition | 10 | 0-2 replies 10 · 3-10 → 6 · 11-30 → 2 · more → 0 |
| Service fit | 5 | matches an entry service exactly 5 · close 2 |
| Contactability | 5 | email found / offers allowed 5 · comment only 2 |

**Valuable = all must-haves met and score ≥ 65.** 80+ = act first. Write the score and its parts in `HISTORY.md`.

## 4. Red flags (any one drops the lead)

Wants free work or spec samples · "equity only" · a budget far below the scope ("full app for $100") · "just exploring" ·
a homework or school project · reselling / white-label requests · crypto, gambling or adult · they already picked someone
("found a developer, thanks") · asks only for the cheapest price with no other detail.
