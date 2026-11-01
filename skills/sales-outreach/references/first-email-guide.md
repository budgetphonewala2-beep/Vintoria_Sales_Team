# First email — style guide and examples

## The shape (plain text, under 120 words)

1. **Subject**: 2-6 words, lowercase-ish, specific, no clickbait, no fake "Re:". e.g. `your bakery website`, `quick idea for sweet crumbs`.
2. **Line 1 — why them, why now**: their public post or a real trigger, in plain words. Not "I hope this finds you well".
3. **Line 2 — one observation** backed by evidence (a site-audit fact or something on their site/post). Exactly one.
4. **Line 3 — relevance**: what you do about that, in one sentence, ideally with one REAL proof point (or none).
5. **CTA**: one soft question — a 15-minute call, or "want me to send the 3 other things I noticed?".
6. **Signature + postal address + opt-out line** ("Not relevant? Reply 'no' and I won't follow up.").

Rules: no attachments, at most one link (better none), no images, no tracking, no "guaranteed", no fake
urgency, no flattery you can't back up, no invented mutual connections. Match their language: a Hinglish post can
get a short Hinglish opener; keep the rest clear and professional. Every factual sentence must pass `claim_check.py`.

## 10 examples

### 1. GOOD — replying to a public request (English)
> Subject: your bakery website
>
> Hi Anita,
>
> Saw your post looking for a web developer to redo your bakery website before Diwali.
> I had a quick look: the homepage has no mobile viewport tag, so phones probably get the shrunken desktop layout.
> We build fast, mobile-first sites for food businesses and can usually launch in 3-4 weeks.
>
> Worth a 15-minute call this week to see if we're a fit?

Why it works: names the real request, one checkable fact, one relevant line, one easy question. (The "3-4 weeks"
must be in the user's own notes/ICP or the claim check fails.)

### 2. BAD — generic and unverifiable
> Subject: Grow your business 10X!!!
> Hi there, I hope this email finds you well. We are a leading agency with 500+ happy clients worldwide and we
> guarantee page 1 rankings...

Why it fails: no reason it's for them, invented numbers, a guarantee, shouty subject.

### 3. GOOD — Hinglish request, mixed reply
> Subject: coaching institute ki website
>
> Namaste Rahul ji,
>
> Aapki post dekhi — coaching institute ke liye website banwani hai, budget 25-30k.
> Aapka current Facebook page hi main contact point hai; ek simple site with course pages and a WhatsApp enquiry
> button se students direct reach kar payenge.
>
> Kya is hafte 15 minute call kar sakte hain?

### 4. BAD — invented observation
> "I noticed your website gets very little traffic and you're losing about 40% of mobile visitors."

Why it fails: no tool measured traffic or loss; the claim check will flag both numbers.

### 5. GOOD — audit-led, no public post
> Subject: sweet crumbs homepage
>
> Hi Anita,
>
> I was looking at bakeries in Pune and found Sweet Crumbs. Your footer still says © 2019 and there's no
> "Order" or "Call" button on the homepage, so visitors may not see an easy next step.
> We fix exactly this for local food businesses.
>
> Want me to send the other 3 quick wins I noticed? No call needed.

### 6. BAD — too many asks
> "Can we jump on a 45-minute demo Tuesday or Wednesday? Also please fill this form and share your Google
> Analytics access."

### 7. GOOD — SEO request on Reddit
> Subject: seo for your dental clinic
>
> Hi Dr. Shah,
>
> Saw your r/dentistry question about finding a good SEO agency for the clinic.
> Your homepage title is just "Home", which doesn't tell Google you're a dentist in Austin — a small, quick fix.
> We do local SEO for clinics; I can show you what we'd change first.
>
> Open to a 15-minute call next week?

### 8. BAD — fake familiarity
> "Great catching up last week! As discussed..." (there was no last week)

### 9. GOOD — honest when there's no proof yet
> "We're a small team, so you'd work directly with me." (true, and a real advantage) — instead of inventing a case study.

### 10. BAD — attachment + link dump
> "Please see our 12-page deck attached and our portfolio at link1, link2, link3."

## Before showing the draft
- Recipient email status is `verified` (or tell the user it isn't).
- `claim_check.py` passes; no `[PLACEHOLDER]` left.
- Under 120 words (count them), one link max, opt-out line present, postal address for US recipients.
