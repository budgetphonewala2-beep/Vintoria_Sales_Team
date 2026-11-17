# The email sequence — frameworks, the 5 emails, A/B tests, output format

For LinkedIn leads with an email (sent from `business@vintoria.org`). Reddit leads get one comment instead
(`reddit-comment-playbook.md`). Every email also follows `first-email-guide.md`, `quality.md` and the critic check.

## 1. Pick the framework (one per prospect)

| Framework | Use when | Shape |
|---|---|---|
| **Their post → help → ask** (default) | they asked publicly | "Saw your post about <their need>." → one useful observation → what Vintoria does about it → soft question |
| **Observation → connection → ask** | no post, but a clear fact on their site | "Your <page> <fact from the audit>." → why it matters for them (hedged) → soft question |
| **Trigger** | a dated event: launch, new location, rebrand, hiring for the role | "Saw <event, with date>." → the need it creates → soft question |
| **Referral / warm** | only a real, named connection who agreed to be mentioned | "<Name> suggested I get in touch about <need>." → one line → soft question |

No framework may cite a result, client or number that isn't in `SELLER-PROFILE.md`. With no proof, the email leans on
the observation and the help, never on invented case studies.

**Write them premium:** the anatomy, the five formats with full examples and the HTML template for warm emails are in
`premium-email.md`. Vintoria emails are signed Pratik Patil, Co-founder.

## 2. Rules for every email

- **Subject:** 2-5 words, lower case, about them ("your clinic booking site", "acme homepage on mobile"); a B version for
  A/B; no fake "Re:", no "free", "urgent", "guarantee", no `!`.
- **First line:** about them — their post, their site, their event. Never "I hope…", "My name is…", "I'm reaching out…".
- **Body:** plain text, 1-2-sentence paragraphs, one idea, no jargon ("synergy", "leverage", "touch base", "deep dive").
- **CTA:** one soft question ("worth a quick look?", "want me to send the 3 fixes?"); no booking link before interest.
- **Tone:** a helpful peer — confident, brief, specific, never pushy. Their spelling (US / UK / Indian English).
- **Signature:** the email sign-off in `../../vintoria-sales/references/vintoria-contact.md` (WhatsApp link, postal
  address, opt-out).

## 3. The 5 emails

| # | Day | Goal | What to write | Words |
|---|---|---|---|---|
| 1 | 0 | Get a reply | Their post / top fact + what Vintoria does about it (one catalog service) + soft question | ≤ 120 |
| 2 | 3 | Add value | A second, different fact from their site or post + a one-line fix idea they could use even without us | ≤ 70 |
| 3 | 7 | Proof | The closest real result from the profile (same niche or platform), or a 3-point mini teardown of their page; no proof → `[ADD REAL CUSTOMER RESULT]` flagged to the owner | ≤ 90 |
| 4 | 14 | New angle | A market or competitor fact you checked (e.g. "3 of the top 5 clinics near you take online bookings") or one simple question | ≤ 60 |
| 5 | 28 | Close the loop | "Should I close the file on this?" + door open + WhatsApp line | ≤ 50 |

Follow-ups reply in the same thread (no new subject). Any reply, opt-out, bounce or booking stops the sequence at once.

### Example — email 1 (LinkedIn post, India)
> **Subject:** your clinic booking site
>
> Hi Priya,
>
> Saw your post about wanting patients to book physio sessions online instead of calling. On your current site the
> "Book" button opens a phone number, so evening visitors may give up before they reach you.
>
> At Vintoria we build booking websites for clinics (028 Booking Platform Development) — patients pick a slot, you get
> a confirmation on WhatsApp.
>
> Worth a quick look at how that would work for your clinic?
>
> <email sign-off>

### Example — email 5 (breakup)
> Hi Priya — I haven't heard back, so I'll assume online booking isn't a priority right now and close the file. If it
> comes back up, reply here or message us on WhatsApp and I'll pick it up straight away.

## 4. A/B testing

Test one thing at a time across at least 20 sends: the subject (A vs B), the first line (post quote vs site fact), or
the CTA ("quick look?" vs "send the fixes?"). Log which version each prospect got in `OUTREACH-SEQUENCE.md`; the weekly
report compares reply rates and keeps the winner.

## 4b. The second brand

LinkedIn leads with a real marketing hook also get Radian Marketing's sequence from `amar@radianmarketing.site`, starting
on day 1 (one day after Vintoria's) with its own 3/7/14/28 follow-ups — calendar, honest-identity rules and an example in
`../../vintoria-sales/references/brands.md`. `OUTREACH-SEQUENCE.md` lists both brands' emails in one table with a `Brand`
column.

## 5. Timing

Emails go out 08:00-19:00 on weekdays in the **prospect's** time zone (best: 08:00-10:00 and 13:00-14:00). India ↔ US:
queue for their morning. Never more than one email per prospect per day, and at most 4 emails in any 7 days across both brands
(`../../vintoria-sales/references/brands.md`). Each inbox stays under its daily warm-up cap.

## 6. `OUTREACH-SEQUENCE.md` (one per prospect)

```markdown
# Outreach — <Company / Person>  ·  <slug>
Source: <post URL> (posted <age> ago) · Quote: "<exact words>"
Contact: <name>, <title> · <email> (<status, where found>) · Country / time zone: <…>
Framework: <name> · Service: <ID name> · Top hooks: <1>; <2>; <3>

| # | Brand | Send on (their time) | Subject (A / B) | Words | Score | Critic | Status |
|---|---|---|---|---|---|---|---|
| 1 | Vintoria | 2026-11-18 09:00 IST | your clinic booking site / clinic bookings | 96 | 88 | pass | sent 09:02 |
| 1 | Radian | 2026-11-19 09:00 IST | your google reviews | 84 | 90 | pass | scheduled |

## Email 1
<body>
## Email 2 … ## Email 5
<bodies>

## LinkedIn / Reddit touches
<comment or note text, if any, with its link once posted>

Compliance notes: <rules for their country>
```
