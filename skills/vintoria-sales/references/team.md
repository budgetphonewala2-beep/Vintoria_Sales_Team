# The sales team — three Hermes PCs working as one, for Vintoria and Radian Marketing

Three Hermes agents on three PCs run the whole sale end to end for both agencies — find, research, contact, reply, book,
close, collect proof — like one professional team. They never call each other directly: everything they share lives in
**Airtable** (`airtable.md`), and they talk on its **Board** table with one message format. Setup: `hermes-setup.md`.

## Who does what

| PC | Roles | Skills it runs | Owns |
|---|---|---|---|
| **PC1 — Build** | Hunter (build lanes) · Writer (Vintoria) · Researcher for its leads | `vintoria-hourly-run`, `vintoria-lead-hunt`, `vintoria-prospect-research`, `vintoria-outreach`, `vintoria-authority` | agency-seekers for any service in Vintoria 001-120 (strategy, web, SaaS, mobile, UI/UX, branding); every Vintoria email from `business@vintoria.org` (signed Pratik Patil, Co-founder); PC1's LinkedIn touches; the daily LinkedIn post |
| **PC2 — Growth** | Hunter (growth lanes) · Writer (Radian) · Researcher for its leads | `vintoria-hourly-run`, `vintoria-lead-hunt`, `vintoria-prospect-research`, `vintoria-outreach` | agency-seekers for any Radian service and Vintoria 211-270 (marketing & SEO, growth); every Radian email from `amar@radianmarketing.site` (signed Amar) incl. Radian's day-1 emails for PC1's leads; PC2's LinkedIn touches |
| **PC3 — Manager & Closer** | Sales Manager · Closer · Hunter (cross-lane) | `vintoria-sales`, `vintoria-reply-book`, `vintoria-close`, `vintoria-account-health`, `vintoria-report`, `vintoria-hourly-run` | every reply (both inboxes, LinkedIn messages), booking, call prep, proposals, negotiation, the proof bank; account health; standups, digest, weekly report, self-test, watchdog; hunts any service in Vintoria 121-210 (AI, automation, backend & cloud, e-commerce) plus "switching agencies", "any service", comments under agency-request posts, LinkedIn service requests |

**Reviewer:** every message is checked by a `delegate_task` sub-agent with a fresh context (`critic-check.md`) on the PC
that wrote it — independent eyes without waiting for another PC.

## The Board (Airtable)

The **Board** table in Airtable (`airtable.md`): one record per message, never deleted. Every message has this shape:

```
### M-20261117-1405-PC1 · 14:05 IST · PC1 Hunter → PC1 Writer + PC2 (Radian day 1) · HANDOFF · glowkart.in
Need: agency to rebuild their D2C skincare store on Shopify before the festive sale.
Quote: "We're looking for an agency to rebuild our D2C store on Shopify before the festive sale."
Who: Riya Mehta, Founder, GlowKart (Mumbai) · email found on the company site's contact page (published)
Post: https://www.linkedin.com/posts/… · posted 1 h ago · 4 comments (2 agencies already "DM'd you")
Agency intent: agency 0.95 · Score: 87 HOT (intent 24, fresh 15, urgency 12, scope 10, budget 6, DM 8, competition 10, fit 5, contact 5)
Brand: Vintoria (192 Shopify Development) day 0; Radian day 1 — hook: no email/SMS flows on the store
Ask: email + comment within 10 minutes.
```

- **ID:** `M-<date>-<time>-<PC>` (PC1, PC2, PC3). Replies quote it: `Re: M-20261117-1405-RH`.
- **Types:** `HANDOFF` · `CLAIM` · `DONE` · `QUESTION` · `ANSWER` · `REVIEW-REQUEST` · `REVIEW` · `ALERT` · `BLOCKED` ·
  `HOURLY` · `STANDUP` · `DECISION` · `ESCALATE` · `HOT` (fast-track lead) · `HEALTH` (account level) · `DIGEST` (owner summary) · `SWEEP` (6-hour inbox sweep) ·
  `HEARTBEAT` (I'm alive — at least one Runs record and Board line per PC per hour; see `autopilot.md`) · `START` (05:00
  start of day) · `TARGET` (a PC reached its 60).
- **To:** a PC (`PC1`, `PC2`, `PC3`), a role on a PC, `@all`, or `@owner` (the human — only for `ESCALATE`).
- **Self-contained:** whoever receives a message must be able to act without opening another file — need, exact quote,
  link, age, score, service, ask, deadline.
- **Professional tone:** short, factual, polite, no chit-chat, no blame; disagree with a reason and a proposal.
- **Never** put passwords, tokens or private data of prospects beyond what the task needs on the board.

## How the three PCs coordinate (all through Airtable)

1. **Start of every run:** read the **Board** since your PC's last run; handle anything to your PC or `@all` first
   (`ALERT` > `HOT` > `QUESTION` > `REVIEW` > `HANDOFF`), then your own work. Check your channels' latest **Health** level
   before any post or send.
2. **Find before you save.** A post or person already in **Seen** or **Leads** (any PC) is never saved or contacted again.
3. **Claim on the record.** Set `Owner PC` + `Claimed at` on the Leads record and read it back; a newer claim (< 60 min)
   by another PC wins. Done → clear the claim or hand off. An expired claim may be taken over.
4. **Hand off with context** — a `HANDOFF` on the Board (format above) and `Owner PC` changed on the record. Typical
   handoffs: PC1 lead → PC2 for Radian's day-1 email, PC2 lead → PC1 for Vintoria's day-1 email (an **Emails** record with the other PC as `Sender PC`); any reply → PC3.
5. **Review** by a fresh-context sub-agent on the writing PC (`critic-check.md`); record `Critic: pass` on the record.
6. **Ask, don't guess:** a missing fact → `QUESTION` to the PC that knows; a price → `ESCALATE` to `@owner`. Keep
   working on other leads meanwhile.
7. **Alerts:** whoever sees a reply, WhatsApp message, booking, captcha, restriction or warning posts `ALERT` at once.
   Replies → PC3 within 15 minutes. A restriction on one PC's LinkedIn account pauses **that PC's** LinkedIn activity
   only (`DECISION: pause PC2 LinkedIn`); its lanes are covered by the other PCs if needed.
8. **Limits:** LinkedIn limits are per account (per PC); email limits per inbox (PC1 Vintoria, PC2 Radian). Count in the
   hour's **Runs** record before acting; at the limit, queue for the next hour.
9. **Conflicts:** two PCs on one lead, or a disagreement on a fact → PC3 posts a `DECISION`; the fact with a saved,
   dated source wins, otherwise it is "Not found".

## Rhythm (24/7)

| When | Who | What |
|---|---|---|
| 05:00 IST daily | each PC | the first run at or after 05:00 starts the day: today's **Daily** record (target 60), `START` on the Board |
| Every 30 min, all three PCs | each PC | `vintoria-hourly-run` for its lanes: due emails of its brand → hunt until 60 → save to Airtable (no duplicates) → contact → `HOURLY` |
| Every 15 min | PC3 | fast reply check (both inboxes, LinkedIn messages) — answer within 15 minutes |
| Every 6 hours (00/06/12/18 IST) | PC3 | full inbox sweep incl. Spam → `SWEEP` (`autopilot.md`) |
| Every 6 hours (:05) | each PC | `vintoria-account-health` for its own LinkedIn account and inbox → `HEALTH` |
| 09:30 and 18:30 IST | PC3 | `STANDUP` to `@all` from **Runs**, **Daily**, **Leads** |
| Weekdays 09:00 IST | PC1 | one LinkedIn post + 5-10 comments on buyers' posts (`vintoria-authority`) |
| Wednesday 11:00 IST | PC1, PC2 | nurture engine for their brand (`vintoria-outreach`) |
| 21:00 IST | PC3 | `DIGEST` to `@owner` |
| Monday 10:00 IST | PC3 | weekly review (`vintoria-report`): keep what got replies, drop what didn't, update queries and `OFFER.md` |
| Sunday 03:00 IST | each PC | `self-test.md` |

Standup format:
```
### M-20261117-0930-SM · 09:30 IST · Sales Manager → @all · STANDUP
Last 12 h: LinkedIn 112 found / 31 valuable (6 HOT) · emails 22 (Vintoria 14, Radian 8) · comments 9 · notes 11
Replies: 4 (2 email, 1 WhatsApp, 1 LinkedIn) · Calls booked: 1 · Acceptance 14 d: 36 %
Best: "switching agencies" query (2 replies) · Weak: "branding agency" (0 replies in 5 days) → drop
Focus today: D2C + SaaS founders in Mumbai and Bangalore; Writer: shorter comments, sharper first question
Blockers: none
```

## Owner digest (21:00, WhatsApp-ready, 10 lines at most)
```
### M-20261117-2100-SM · 21:00 IST · Sales Manager → @owner · DIGEST
Today: 186 found · 47 valuable (9 HOT) · 38 contacted (26 email, 12 LinkedIn) · 5 replies · 2 calls booked
Hot: Riya (GlowKart, Mumbai) wants a Shopify agency before the festive sale — call Thu 11:00
Calls tomorrow: Acme Dental 10:00 IST · Brightleaf (UK) 15:30 IST
Proposals out: 2 · waiting on you: price for 192 Shopify Development [PRICE TO CONFIRM]
Health: LinkedIn YELLOW (captcha 14:10) · Vintoria email GREEN · Radian email GREEN
Need from you: 1) Shopify price  2) permission to use the bakery result in posts
```
Numbers come from the Airtable **Runs**, **Daily**, **Leads** and **Health** tables — never estimated.

## Escalate to the owner (`@owner`)

Only for: a price, discount or contract term that isn't in the profile; a legal or compliance doubt; an angry or
threatening prospect; a platform warning, ban or removed comment; a prospect asking for a call today; anything about
money already paid. Use `ESCALATE`, keep it to five lines, and keep working on other leads.

## Targets (per day, adjust in `SELLER-PROFILE.md` → Automation)

| PC | Target | Quality bar |
|---|---|---|
| PC1, PC2, PC3 | 60 unique agency-seekers saved each, from 05:00 IST until done (up to 8 per run, every 30 min) | every saved lead under 24 h, agency intent, exact quote, no duplicates |
| PC3, also | every reply answered within 15 minutes | ≥ 40 % of positive replies → booked call |
| Team | 180 unique leads a day | 100 % of messages pass the critic check; numbers from Airtable, never estimated |
