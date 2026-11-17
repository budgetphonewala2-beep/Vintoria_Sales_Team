---
name: vintoria-outreach
description: "Contacts Vintoria's buyers on the right channel and writes every follow-up: on Reddit, a professional, genuinely helpful public comment on the buyer's post that answers their question and ends with Vintoria's clickable WhatsApp link (+91 87660 33979) and business@vintoria.org; on LinkedIn, a short personal email from business@vintoria.org to the address found in the post, contact info or company site, or a professional comment or connection note when there's no email; plus a 5-email sequence (day 0, 3, 7, 14, 28) and follow-ups after silence, a meeting or a proposal. Every message passes the truth self-check, scores 85+, respects subreddit rules and daily limits, and is posted or sent per the approval mode. Use it whenever a buyer needs a message: 'comment on this Reddit post', 'write a cold email', 'reply to this LinkedIn post', 'follow up with', 'they went quiet', or Hinglish 'is post pe comment karo', 'isko email likho', 'follow up likho', 'reply nahi aaya'."
license: MIT
compatibility: "Instruction-only Agent Skill: no code. Works in any agent or bot (Claude, Grok, GPT, Gemini…) that can follow instructions; best with a browser logged in to LinkedIn and Reddit, and file access."
metadata:
  author: "Vintoria (built on ai-sales-team-claude by Zubair Trabzada)"
  version: "5.0.0"
---

# Vintoria Outreach — Reddit comments, LinkedIn and email

You write the message a busy owner actually answers: about their exact request, helpful before it sells, honest that
it's Vintoria, and one tap away from a conversation.

## Before you start

1. **Your files.** Everything lives in plain files — `SELLER-PROFILE.md`, `OFFER.md`, `IDEAL-CUSTOMER-PROFILE.md`,
   `PIPELINE.md`, `DO-NOT-CONTACT.md` and `prospects/<slug>/` (format: `../vintoria-sales/references/pipeline-format.md`). If you can't read or
   write files (a chat bot such as Grok), ask the user to paste `SELLER-PROFILE.md` and the relevant `PIPELINE.md` rows,
   and finish by printing every changed row and file in code blocks for them to save.
2. **Vintoria's profile.** Read `SELLER-PROFILE.md`. This skill builds queries, emails or prices from it — if it is
   missing or still full of `[ASK]`, run `vintoria-setup` first (in a hurry: ask only the missing answers in one message).
3. **What Vintoria sells.** 270 services in 12 disciplines — `../vintoria-sales/references/service-catalog.md`. Name a service exactly as the
   catalog does (`192 Shopify Development`), never invent one, and never quote a price, discount or date that isn't in
   `SELLER-PROFILE.md` — write `[PRICE TO CONFIRM]` (`../vintoria-sales/references/pricing-policy.md`).
4. **Platforms.** Leads come only from **LinkedIn and Reddit**, through the accounts already logged in on this machine.
   Open a page before you state a fact from it and note its URL and date; a search snippet alone is not a fact. If you
   can't open something, write "Not found".
5. **Facts only.** Every sentence traces to a page you opened, the prospect's own words, a fact you observed on their site,
   the catalog or the profile — never to memory. Never say something was sent, posted, booked or verified unless it
   really happened. Run the self-check in `../vintoria-sales/references/truth-rules.md` before anything goes out.
6. **Vintoria's contact details** — `business@vintoria.org`, WhatsApp +91 87660 33979 (`https://wa.me/918766033979`) —
   and every sign-off come only from `../vintoria-sales/references/vintoria-contact.md`.
7. **The team.** Read `TEAM-BOARD.md` before you start and handle messages to your role; `CLAIM` a lead before working it,
   hand off with full context, post `ALERT`s at once (`../vintoria-sales/references/team.md`). Alone, you play every role with the same files.

## Pick the channel

| Lead | Channel | Playbook |
|---|---|---|
| Reddit post asking for help | Public comment on the post + WhatsApp link (DM only if they said "DM me") | `references/reddit-comment-playbook.md` |
| LinkedIn post, email found | Email from `business@vintoria.org` + the 5-email sequence | `references/linkedin-playbook.md`, below |
| LinkedIn post, no email | Professional comment on the post, then a connection note | `references/linkedin-playbook.md` |
| Already talking (reply, call, proposal) | Follow-ups | below |

Before writing, read `prospects/<slug>/DOSSIER.md` if there is one (hooks with evidence), `OFFER.md` (which lane and entry
service fits), the `PIPELINE.md` row and `DO-NOT-CONTACT.md`. Contact details and sign-offs only from
`../vintoria-sales/references/vintoria-contact.md`.

## Reddit comment
Follow `references/reddit-comment-playbook.md`: their exact need in line 1 → one or two real, useful tips → "We're
Vintoria, a digital product studio — we do exactly this (<catalog service>)" → the sign-off with a pre-filled
`https://wa.me/918766033979?text=…` link. 60-110 words, no price, no emojis, no copy-paste, only where the subreddit
allows offers, within the hourly limits in `RUN-LOG.md`. One comment per post; after that the conversation moves to the thread, WhatsApp or email.

## LinkedIn email — the first email and the sequence
1. **Email 1** (`references/first-email-guide.md`): plain text, under 120 words, their post in their words in the first line,
   ONE sourced observation (their post or a site-audit fact), one sentence on what Vintoria does about it (one catalog
   service — never a list), one soft question as the CTA ("worth a quick look?"), the email sign-off (with WhatsApp link,
   postal address and opt-out). No booking link.
2. **The sequence**, each email adding something new (`references/sequence-playbook.md` — frameworks, the 5 emails,
   examples, A/B, timing):
   | Email | Day | Content | Words |
   |---|---|---|---|
   | 1 | 0 | Their post / top hook + one fact + soft question | ≤ 120 |
   | 2 | 3 | Second hook (another audit fact) + a one-line fix idea | ≤ 70 |
   | 3 | 7 | Proof: a real result from `SELLER-PROFILE.md`, or a mini teardown of their page (`[ADD REAL CUSTOMER RESULT]` if none) | ≤ 90 |
   | 4 | 14 | A different angle or one simple question | ≤ 60 |
   | 5 | 28 | Polite breakup — "close the file?" — door left open | ≤ 50 |
   Subjects: 2-5 words, lower case, about them ("your clinic booking site"), plus a B version; follow-ups reply in the
   same thread. Warm or referral templates only for a real, confirmed connection.
3. **No email found** → the LinkedIn comment or connection note in `references/linkedin-playbook.md`.

## Check everything, then send
Self-check every sentence; score with `references/quality.md` (first two lines only this prospect could receive — the
deletion test; no sentence over 28 words; each follow-up brings something new) and fix until 85+. Write
`OUTREACH-SEQUENCE.md` (format in `references/sequence-playbook.md`) with every message, its channel, send day and score. Then
post or send per the approval mode, log it (`THREAD.md` with the comment or email link, `HISTORY.md`, the `PIPELINE.md` row →
`contacted`, `last_touch`, `next_action` + `next_due`), and check for replies the next day. Any reply stops the sequence →
`vintoria-reply-book`.

## Follow-ups (after something happened)
1. Read what happened in `THREAD.md` and `HISTORY.md`. If they replied, use `vintoria-reply-book` instead.
2. Pick the scenario (`references/followup-playbook.md`): **post-meeting** recap within 24 h (their words, what was agreed,
   the next step with a date); **post-proposal** day 2 walkthrough offer, day 5 one question on the option they liked, day 10
   a real deadline, day 20 breakup; **ghost recovery**; **nurture**.
3. Write them (email, or a WhatsApp message if they started a WhatsApp chat), self-check and score, write
   `FOLLOWUP-SEQUENCE.md` (`references/followup-output-format.md`), and set the next touch in `PIPELINE.md`.
   Edge cases: `references/rules.md`.

## Before anything is sent

- **Self-check** every message with `../vintoria-sales/references/truth-rules.md`; delete or rewrite every unsourced sentence and fill or flag
  every `[PLACEHOLDER]`.
- **Critic check** — the yes/no list in `../vintoria-sales/references/critic-check.md`, as a strict reviewer (another bot's `REVIEW` in a team).
  One "no" = fix it; two failed rewrites = skip the lead.
- **Score** it with `../vintoria-sales/references/quality-bar.md` (emails: 80 to show, 85+ premium) and say the score in one line.
- **Compliance:** `../vintoria-sales/references/compliance.md` — opt-out line, postal address for US, consent rules (UK/EU/CA/AU/NZ/India),
  and check `DO-NOT-CONTACT.md` first.
- **Language:** plain English — US spelling for US/CA, UK spelling for UK/IE/AU/NZ, clear Indian English for India (no
  "do the needful", "revert", "kindly"). If an Indian prospect wrote in Hindi or Hinglish, answer in the same register,
  still short and professional. Prices only in their currency and only from the profile.
- **Approval mode** (`SELLER-PROFILE.md` → Automation): `auto` — you post or send it yourself from the logged-in
  Reddit / LinkedIn account or `business@vintoria.org`, but only after it passes the self-check, scores 85+, fits that
  platform's rules (`../vintoria-sales/references/compliance.md`) and today's limits; `review` — show the exact text and wait for the user's OK.
  A message that fails any check is never sent in either mode — fix it or skip the lead. Count every post / send in
  `RUN-LOG.md` first; at the hourly limit (all bots together), queue it for the next hour.
- **Log every message that went out** — `THREAD.md` (exact text, link to it), `HISTORY.md`, `PIPELINE.md` — and give the
  user a summary of what was posted and sent.
- **No booking link** in a first message — only after they show interest.

## References (read when you reach that step)

- `references/reddit-comment-playbook.md` — when to comment, the comment shape, a good and a bad example, limits, what to do after
- `references/linkedin-playbook.md` — finding the email on LinkedIn, the email, comment and connection-note fallbacks, limits
- `references/first-email-guide.md` — style rules + 10 good/bad first-email examples
- `references/quality.md` — the 0-100 score, banned and AI phrases, personalization levels, deletion test, panel review
- `references/sequence-playbook.md` — the 4 frameworks, the 5 emails with examples, A/B tests, timing, OUTREACH-SEQUENCE.md format
- `references/followup-playbook.md` — the 5 follow-up scenarios, multi-channel touches, cadence, breakup emails
- `references/followup-output-format.md` — FOLLOWUP-SEQUENCE.md template
- `references/rules.md` — terminal output, errors, cross-skill use
