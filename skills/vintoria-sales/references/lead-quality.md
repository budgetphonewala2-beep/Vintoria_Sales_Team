# Lead quality — gates, score, and the 24-hour rule

Leads come from **LinkedIn only**, from people **looking to hire an agency** or an outside team / partner, for any of
our ~330 services. Each PC saves **60 unique leads a day** (180 for the team, `hermes-setup.md`).

The method is the one Lead-Forge measured on live LinkedIn searches. A lead must pass **every gate** (the gates catch
sellers, job ads and wrong-direction posts), and then it is **ranked** by a score. Clearing an average is never enough,
but a genuine buyer is never rejected just because the post doesn't mention a budget, a country or an email.

Expected yield: about **10-15 %** of the posts that pass the cheap prefilter
(`../../vintoria-lead-hunt/references/prefilter.md`). Under 3 % after 200 prefiltered posts means the **searches** are
wrong, not the market — see "When yield is low" in `../../vintoria-lead-hunt/references/queries.md`.

## 1. The 24-hour rule

Read the age on the post (or comment) itself. Use LinkedIn's **Posts → Latest → Past 24 hours** filter, then confirm.

| LinkedIn shows | Keep? |
|---|---|
| `12m`, `45m`, `3h`, `23h` | yes |
| `1d`, `2d`, `1w` | **no** — `1d` can mean 24-47 hours |
| Edited post | the original post time counts |

Priority by age: under 2 hours = act first, 2-12 hours = high, 12-24 hours = normal.

## 2. Gates — all must pass (any "no" = not a lead; record which gate in **Seen**)

| # | Gate | Passes when |
|---|---|---|
| 1 | **Buyer, not seller** | the author needs the work done — not offering it, not looking for work, not recruiting talent (`../../vintoria-lead-hunt/references/intent-rubric.md`) |
| 2 | **Agency direction** | agency intent is `agency`, `open` or `switching` — not `freelancer` (one person) and not `employee` (a job). "We're **hiring an agency**" passes; "hiring **for our agency team**" doesn't |
| 3 | **Real ask** | intent strength is `explicit`, `active_search` or `recommendation` (not just a problem, research or opinion) |
| 4 | **Quality bar** | at least ONE concrete buying signal: **scope** (what the agency will own — "handle our SEO", "rebuild our store"), **money** (budget, retainer, ad spend), **time** (deadline, "this quarter", "before launch"), **outsourcer framing** ("outsource our…", "need an outside team") or an **owner's referral ask** ("anyone know a good X agency for our launch?") |
| 5 | **We sell it** | service match ≥ 50: the need is one of Vintoria's 270 catalog services or a Radian service. An adjacent craft we don't sell scores ≤ 50 |
| 6 | **Fresh** | under 24 hours (section 1) |
| 7 | **Market not excluded** | no country named outside India, US, UK, Australia. **No location mentioned = passes** (most posts don't say) |
| 8 | **Still open** | the post still exists and the need isn't filled ("found our agency", "update: hired", "contract awarded") |
| 9 | **Not excluded** | not in **DoNotContact**, **Seen** or **Leads**; not claimed by another PC; no red flag (section 4) |

A post that looks like a genuine ask but is **cut off** before the service or direction is clear → open the full post and
judge again. Never reject a cut-off post for what you can't see.

## 3. Score (0-100) — only for posts that passed every gate; it ranks and decides HOT

| Part | Weight | How |
|---|---|---|
| Intent strength | 30 | explicit 100 % · active_search 85 % · recommendation 70 % |
| Service match | 25 | the exact service named 90-100 % · clearly part of the ask 70 % · close 50 % |
| Commercial signal | 15 | budget / scale / deadline 70-100 % · bare ask with scope 40-60 % |
| Decision maker | 10 | founder, owner, CEO, director, head of marketing / tech / growth = 10 · otherwise 0 |
| Freshness | 10 | < 2 h 10 · 2-6 h 8 · 6-12 h 6 · 12-24 h 5 |
| Evidence | 10 | explicit ask + budget 90-100 % · clear ask 60-80 % · vague 40 % |

**Valuable = every gate passed and score ≥ 60.** HOT = 80+, under 2 hours, 10 comments or fewer → `HOT` on the Board.
Comment count is only a tie-breaker (fewer comments first), never a reason to reject — agency asks always attract
replies. A missing email is never a penalty: every LinkedIn post can get a comment and a connection note.
Write the gates, the score and its parts in **Leads** (`Score parts`).

### Calibration (score these the same way every time)
- "Looking for a marketing agency for our D2C skincare brand — recommendations?" (founder, 15 h, 25 comments) →
  gates pass (owner referral + scope "for our D2C brand") → intent 21 + match 23 + commercial 7 + DM 10 + fresh 5 +
  evidence 7 = **73 → valuable**.
- "We're hiring an agency to run our Google Ads, ₹2L/month spend, starting next month." (head of growth, 1 h) →
  30 + 24 + 14 + 10 + 10 + 10 = **98 → HOT**.
- "Need an agency." (no scope, money, time or owner context) → gate 4 fails → not a lead (cut off? open the full post first).
- "We're a full-service creative agency helping DTC brands scale — DM for a free audit." → gate 1 fails (seller).
- "Hiring a designer to join our agency team, 3+ years, apply with CV." → gate 2 fails (employee job ad).

## 4. Red flags (any one = gate 9 fails)

Wants free work or spec samples · "equity only" · a budget far below the scope ("full app for ₹10,000") · a student or
college project · white-label or reselling requests from another agency · agency-to-agency "collab" with no client
need · "we're compiling a list of top agencies" · crypto, gambling or adult · only the cheapest price, no other detail.

Bonus signals (note them in **Leads**, they sharpen the message): switching from another agency · an RFP or written
brief · a date ("before Diwali", "launch in March") · a funding or launch announcement in the last 30 days.
