# Outreach compliance (guidance, not legal advice)

Every sequence must be legal to send:
- Truthful sender identity and subject lines (no fake "Re:"/"Fwd:"), and a working opt-out in every cold
  email (e.g. "Not relevant? Reply 'no' and I won't follow up."). Honour opt-outs immediately.
- **US (CAN-SPAM):** include the sender's physical postal address in the signature.
- **UK (PECR / UK GDPR):** B2B email to corporate addresses is allowed with identification + opt-out; sole
  traders and partnerships need prior consent.
- **EU (GDPR + national ePrivacy laws):** needs a documented legitimate interest and role relevance; Germany
  and some others effectively require prior consent for cold email — flag prospects there.
- **Canada (CASL):** generally requires consent (implied consent only in narrow cases) — flag Canadian prospects.
- **Australia (Spam Act 2003):** needs consent — inferred consent only when the address is conspicuously published
  for business AND your message relates to their role; identify the sender and include a working unsubscribe.
  Flag Australian prospects whose address you found in a database (Apollo etc.) rather than published by them.
- **New Zealand (Unsolicited Electronic Messages Act 2007):** similar consent rule (inferred from conspicuous
  publication); sender details and unsubscribe required.
- **India (DPDP Act 2023):** for prospects in India, use business contact details only, say who you are and why you
  are writing, and honour a withdrawal at once. Unsolicited commercial calls and SMS fall under TRAI rules — don't
  cold-call or text lists; WhatsApp only to a business number they published, one person at a time.
- Only mention a mutual connection the user confirmed is real and agreed to be named. Never invent one.
- Never post, comment or DM on social platforms on the user's behalf; suggest the message, the user sends it.
- WhatsApp: only to numbers the prospect published for business or shared with you, and only person-to-person
  via a click-to-chat link the user opens — no bulk or automated WhatsApp messages.
- Deliverability: plain text, at most one link, no tracking pixels, no attachments in the first email,
  verified addresses only (never send to `pattern-guessed` or `invalid`), and warm up new sending domains.
- Stop-loss: sending pauses by itself when bounces pass 2 % over the last 14 days (re-verify the list first); a reply
  rate under 1 % after 300 sends means the targeting or offer is wrong — change them, don't send more.
- Over-contact: at most `MAX_TOUCHES_PER_WEEK` (default 4) touches per prospect per week across all channels, and a
  reply on any channel stops every other channel.
- "How did you get my email?" gets an honest answer (their post, their site, a database) and an offer to remove them.
- Volume: start at 5 cold emails a day per inbox (weeks 1-2), then +5 per week, and stay under `DAILY_SEND_LIMIT` (default 30);
  `outreach.py send` refuses suppressed addresses, unverified addresses, missing opt-out lines and over-limit sends.
- Booking links only after interest: a calendar link in a cold email reads as presumptuous and hurts replies;
  `outreach.py` refuses it until the prospect has replied positively.
- Automation: queued sequences only send while an inbox check runs first (`autopilot.py`), so a prospect who
  replied never gets another follow-up. Use a sending domain/inbox you control, warmed up, with SPF/DKIM/DMARC.
- Opt-outs: run `python <SCRIPTS>/replies/reply_triage.py --file reply.txt --apply <slug>` on every reply — it adds
  opt-outs to the do-not-contact list (`pipeline.py suppressed`) so they are never emailed again.
- End the output with a short `Compliance notes` line naming which rules apply to this prospect's country.
