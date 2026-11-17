# Full analysis — five roles, one 0-100 Prospect Score

The deepest research mode, for leads worth real effort (value score 80+, a website, a clear budget or a big scope). Start
from the dossier (`DOSSIER.md` and `SITE-AUDIT.md`), then run the five roles **in this order** — the Strategy role needs the
other four. In a team the Researcher may hand roles 1-4 to other bots in parallel (`../../vintoria-sales/references/team.md`);
each returns its section in the format below. Every point needs evidence (a page with URL and date, their post, the
audit); unknown = "Not found" and a neutral 5.

## How each role scores

Each role rates five dimensions 0-10 (7+ needs strong evidence; 5 = neutral or unknown; under 5 = a negative signal).
Role score = sum × 2 (0-100).

### 1. Company Fit — 25 %
| Dimension | 10 means |
|---|---|
| Lane fit | Their need matches an active offer lane in `OFFER.md` exactly |
| Market fit | India / US / UK / AU and a business type in `IDEAL-CUSTOMER-PROFILE.md` |
| Activity | Signs of life: recent posts, new location, launch, hiring, active ads, fresh reviews |
| Digital maturity gap | Their current site / app / process is visibly behind what they need (audit facts) |
| Budget signals | A stated budget, paid ads, several locations, premium pricing, a funded launch |
Research: home, about, services, careers, contact; Google reviews; their LinkedIn page; news.

### 2. Contact Access — 20 %
| Dimension | 10 means |
|---|---|
| Decision maker found | The owner / founder / director named, with a source |
| Contact quality | A `published` or `verified` email, or an open channel (post accepts comments, "DM me") |
| Personalization depth | 3+ specific anchors (their post words, an audit fact, a recent event) |
| Warm paths | A real mutual connection, community or prior contact the owner confirms |
| Multi-threading | A second relevant person (co-founder, marketing head, ops manager) |
Research: team page, LinkedIn (`site:linkedin.com/in "<company>" founder OR owner OR director`), their post's author.

### 3. Opportunity Quality — 20 %
| Dimension | 10 means |
|---|---|
| Budget | They stated a budget that fits the scope, or clear spending signals |
| Authority | The author is the person who decides and pays |
| Need severity | The problem costs them now (lost bookings, a broken site, manual work every day) |
| Timeline | A date or event drives it ("before Diwali", "launch in March", "asap") |
| Champion potential | The person is engaged, specific and responsive (detailed post, answers comments) |
Use BANT / MEDDIC from `qualify-playbook.md` for the evidence; red flags from `../../vintoria-sales/references/lead-quality.md`.

### 4. Competitive Position — 15 %
| Dimension | 10 means |
|---|---|
| Gaps found | Clear gaps in what they use now that a Vintoria service fills |
| Switching ease | No lock-in: a template site, a freelancer who vanished, no contract |
| Vintoria advantage | A checkable advantage for this case (one studio for design + build + AI / automation, a matching real result) |
| Positioning clarity | A one-line "why switch / why us" with evidence |
| Win probability | Few competing replies, a fit budget, a decision maker in reach |
Research: footer credits ("Designed by…"), platform hints, reviews of their current provider, the comments under their post.

### 5. Outreach Readiness — 20 % (runs last)
| Dimension | 10 means |
|---|---|
| Personalization quality | A first line only this prospect could receive |
| Channel | The right channel is open (email found, Reddit offers allowed, LinkedIn comments open) |
| Message fit | The angle matches their situation and one catalog service |
| Objection readiness | The 2 likeliest objections answered (`../../vintoria-close/references/objections-playbook.md`) |
| Timing | Fresh post or a live trigger; their working hours known |
Output: the recommended channel, the first message (self-checked and critic-checked), the next 2 touches and their dates.

## Prospect Score

**Score = Company Fit × 0.25 + Contact Access × 0.20 + Opportunity × 0.20 + Competitive × 0.15 + Outreach Readiness × 0.20**
A role that couldn't run = 50, and confidence drops one level. Grades: A+ 90+ · A 75-89 · B 60-74 · C 40-59 · D < 40.

## `PROSPECT-ANALYSIS.md`

```markdown
# Prospect analysis — <company>  ·  <slug>  ·  <date>
Score: <N>/100 (<grade>) · Confidence: high | medium | low
Their words: "<exact quote>" (<post URL>, <age>)
Fit: <catalog ID name> (+ <ID name>) — because <signal>

## Score breakdown
| Role | Score | Strongest evidence | Biggest gap |
|---|---|---|---|
| Company Fit (25 %) | | | |
| Contact Access (20 %) | | | |
| Opportunity (20 %) | | | |
| Competitive (15 %) | | | |
| Outreach Readiness (20 %) | | | |

## Company · ## Decision maker and contact · ## Opportunity (BANT) · ## Competition
<3-6 sourced bullets each>

## Strategy
Channel: <…> · First message: <text> · Then: <touch, date>; <touch, date>
Objections to expect: <1> → <answer>; <2> → <answer>

## Action plan
Today: <…> · This week: <…> · Owner: <role>
Sources: <URL — date> …
```
