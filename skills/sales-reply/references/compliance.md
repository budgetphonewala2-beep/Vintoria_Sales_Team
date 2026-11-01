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
- **India (DPDP Act 2023):** use business contact details only, state the purpose, honour withdrawal promptly.
- Only mention a mutual connection the user confirmed is real and agreed to be named. Never invent one.
- Never post, comment or DM on social platforms on the user's behalf; suggest the message, the user sends it.
- WhatsApp: only to numbers the prospect published for business or shared with you, and only person-to-person
  via a click-to-chat link the user opens — no bulk or automated WhatsApp messages.
- Deliverability: plain text, at most one link, no tracking pixels, no attachments in the first email,
  verified addresses only (never send to `pattern-guessed` or `invalid`), and warm up new sending domains.
- Volume: start at 10-20 cold emails a day per inbox and stay under `DAILY_SEND_LIMIT` (default 30);
  `outreach.py send` refuses suppressed addresses, unverified addresses, missing opt-out lines and over-limit sends.
- Opt-outs: run `python <SCRIPTS>/reply_triage.py --file reply.txt --apply <slug>` on every reply — it adds
  opt-outs to the do-not-contact list (`pipeline.py suppressed`) so they are never emailed again.
- End the output with a short `Compliance notes` line naming which rules apply to this prospect's country.
