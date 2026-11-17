# Premium emails — sharp, specific, never boring

Vintoria's emails are signed **Pratik Patil, Co-founder** (Radian's: Amar). Premium does not mean decorated. A cold email
that looks designed lands in Promotions or Spam, so **cold emails stay plain text**. They feel premium because they are
specific, well structured and short, and because every touch looks different. The branded HTML template at the end is
only for **warm** emails, after the person has replied.

## Anatomy of a premium cold email

| Part | Rule | Example |
|---|---|---|
| Subject | 2-5 words, lower case, about **their** thing | `your booking flow` · `acme on mobile` |
| Preview (first line) | the inbox shows it next to the subject, so make it the hook | "Tried booking a session on your site from my phone." |
| Greeting | "Hi <first name>," — nothing else | |
| Hook | one sentence, their post or one fact you checked | |
| Insight | 1-2 sentences: why it matters to **them**, hedged where it's a judgement | |
| Offer | one sentence: what Vintoria does about it (one catalog service) | |
| CTA | one soft question, answerable in 5 words | "Worth a quick look?" |
| Sign-off | the signature from `../../vintoria-sales/references/vintoria-contact.md` | |
| P.S. (optional) | a small, useful extra, free and with no strings attached | "P.S. Happy to send the 3 fixes as a short list either way." |

Layout: short paragraphs of 1-2 lines, blank lines between them, at most 3 bullets, no bold, no emojis, no images, no
links in the body of email 1.

## Five touches, five formats (so it never feels like "just following up")

| Day | Format | Why it isn't boring |
|---|---|---|
| 0 | **Observation**: their post or site, one insight, one offer | it's about them, not us |
| 3 | **Mini teardown**: 3 bullets they could fix without us | it gives value before asking for anything |
| 7 | **Proof or picture**: a real result (`PROOF-BANK.md`), or "what it would look like for you" in 3 steps | it makes the result concrete |
| 14 | **One question**: a single line that is easy to answer | it's the lowest effort to reply to |
| 28 | **Close the loop**: polite, no guilt, the door left open | it often gets the reply |

### Day 0 — observation
```
Subject: your booking flow

Hi Priya,

Saw your post about wanting patients to book online instead of calling. I tried it on your site from my phone:
the "Book now" button opens a phone number, so anyone visiting after clinic hours can't book at all.

At Vintoria we build booking websites for clinics (028 Booking Platform Development). Patients pick a slot,
and you get the confirmation on WhatsApp.

Worth a quick look at how that would work for your clinic?

Best,
Pratik Patil
Co-founder, Vintoria — Digital Product Studio
business@vintoria.org  |  WhatsApp +91 87660 33979  |  https://wa.me/918766033979
<postal address>

Not the right time? Reply "stop" and I won't write again.
```

### Day 3 — mini teardown (reply in the same thread)
```
Hi Priya,

Three quick things I noticed on your site that you could fix this week, with or without us:

- The homepage has no "Book" button above the fold on a phone.
- The services page doesn't list session lengths, so people call just to ask.
- Your Google Business Profile links to the homepage instead of a booking page.

Happy to help with any of them.

Pratik
```

### Day 7 — the picture (no proof yet) or proof (from `PROOF-BANK.md`)
```
Hi Priya,

Here's how online booking could work for your clinic, in three steps:

1. A patient picks the treatment and a free slot, on their phone, any time.
2. They get a WhatsApp confirmation and a reminder the day before.
3. You see every booking in one calendar. No calls, no double bookings.

Would that fit how you run the clinic?

Pratik
```

### Day 14 — one question
```
Hi Priya, is online booking still on the list for this quarter, or should I check back later in the year?

Pratik
```

### Day 28 — close the loop
```
Hi Priya,

I'll stop here so I don't crowd your inbox. If online booking comes back on the list, just reply to this email or
message me on WhatsApp (+91 87660 33979) and I'll pick it up from there.

Wishing the clinic a great year,
Pratik
```

## Radian's premium version (Amar)
Same anatomy with the growth angle and Radian's own names and signature (`../../vintoria-sales/references/radian-profile.md`).
Hooks that feel premium: one ad visible in the Meta ads library and what it lands on; a marketplace listing with missing
images or A+ content; a Google Business Profile with unanswered reviews. Day 3 is a 3-point growth audit, and day 7 is a
"30-day plan" in three lines. Never reuse a fact from Vintoria's email to the same person.

## What makes an email boring (the critic rejects these)
"I hope you're doing well" · "I wanted to reach out" · "just following up" / "bumping this up" · a paragraph about
Vintoria before anything about them · a list of 5 services · "we are a leading agency" · the same opening twice in a
sequence · a CTA that needs a calendar (save the booking link until they're interested).

## Warm emails: the branded HTML template (only after they reply)
For recaps, proposals, onboarding and anything sent after a reply. Inline styles only (email clients strip `<style>`),
600 px wide, one accent colour, no tracking pixels, always with a plain-text version alongside. Logo URL:
`SELLER-PROFILE.md` → Brands (leave the logo out if it isn't set).

```html
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f6f7f9;padding:24px 0;">
  <tr><td align="center">
    <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:8px;font-family:Arial,Helvetica,sans-serif;color:#1f2933;">
      <tr><td style="padding:28px 32px 8px 32px;font-size:13px;letter-spacing:1px;color:#5b6b7b;text-transform:uppercase;">Vintoria — Digital Product Studio</td></tr>
      <tr><td style="padding:8px 32px 0 32px;font-size:20px;line-height:28px;font-weight:bold;color:#111827;">{{headline: their project in their words}}</td></tr>
      <tr><td style="padding:16px 32px 0 32px;font-size:15px;line-height:24px;">
        <p style="margin:0 0 14px 0;">Hi {{first name}},</p>
        <p style="margin:0 0 14px 0;">{{1-3 short paragraphs: what we discussed, what happens next}}</p>
        <p style="margin:0 0 14px 0;">{{the next step with a date}}</p>
      </td></tr>
      <tr><td style="padding:8px 32px 24px 32px;">
        <a href="{{one link: proposal, booking or WhatsApp}}" style="display:inline-block;background:#4f46e5;color:#ffffff;text-decoration:none;font-size:15px;font-weight:bold;padding:12px 22px;border-radius:6px;">{{button text, 2-4 words}}</a>
      </td></tr>
      <tr><td style="padding:0 32px 28px 32px;border-top:1px solid #e5e7eb;font-size:13px;line-height:20px;color:#5b6b7b;">
        <p style="margin:16px 0 0 0;"><strong style="color:#111827;">Pratik Patil</strong><br>Co-founder, Vintoria<br>
        business@vintoria.org · WhatsApp <a href="https://wa.me/918766033979" style="color:#4f46e5;">+91 87660 33979</a><br>
        {{postal address}}</p>
      </td></tr>
    </table>
  </td></tr>
</table>
```
For Radian: the same template with "Radian Marketing" in the header, Amar's signature, Radian's details and its own
accent colour. Never mix the two brands in one email.

## Premium checklist (add to the critic check for every email)
- [ ] The subject and preview line are about them and work together.
- [ ] The first sentence could only be sent to this person.
- [ ] One insight, one offer, one question; under 120 words (follow-ups under 70).
- [ ] This touch uses a different format from the previous one.
- [ ] Plain text for cold email; HTML only after a reply.
- [ ] Signed by the right person (Vintoria: Pratik Patil, Co-founder · Radian: Amar).
