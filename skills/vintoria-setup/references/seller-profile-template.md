# SELLER-PROFILE.md — template (pre-filled with what the Vintoria catalog already says)

Copy this into `SELLER-PROFILE.md` in the work folder of all three PCs (the same copy on each), then fill every
`[ASK]` through the interview in `intake.md`. Never fill an `[ASK]` with a guess — especially prices and case studies.
Field keys in brackets match `intake.md`.

```markdown
# SELLER-PROFILE — Vintoria
Last updated: YYYY-MM-DD · Status: Incomplete | Ready

## Seller
- Company (seller.company): Vintoria — digital product studio
- Website (seller.website): [ASK]
- Sender name (seller.name): Pratik Patil — title: Co-founder (the only name that signs for Vintoria)
- Sender email (seller.email): business@vintoria.org
- WhatsApp (seller.whatsapp): +91 87660 33979 — https://wa.me/918766033979
- Postal address (seller.postal_address): [ASK]   ← required in US commercial email
- Time zone (seller.timezone): [ASK]   (e.g. Asia/Kolkata)
- Booking link (seller.booking_url): [ASK — optional, sent only after a prospect says yes]
- Video meeting link (seller.meeting_link): [ASK — optional]

## Offer
- Services (offer.services): web, app, seo, marketing, design, software, ecommerce, ai, automation
- What we deliver (offer.service_details): Digital product studio — strategy, web and SaaS development, mobile apps,
  UI/UX and branding, AI development, business automation, backend and cloud, e-commerce, digital marketing and SEO,
  growth — 270 named services across 12 disciplines.
- Active disciplines this month: [ASK — 2 to 8 of the 12, with proof]
- Niches (offer.niches): [ASK — top 1-5]
- Platforms (offer.platforms): [ASK — e.g. Shopify, WordPress, Next.js, Flutter, HubSpot]
- Outcomes clients buy (offer.outcomes): [ASK — in the client's words]

## Pricing (the only place prices may come from)
- Currency per market: [ASK — e.g. INR for India, USD / GBP / AUD abroad]
- Deal size (offer.deal_size): minimum [ASK] · typical [ASK]
- Pricing model (offer.pricing_model): [ASK — fixed per milestone / retainer / hourly]
- Delivery time (offer.delivery_time): [ASK]
- Payment terms: [ASK]
If this section is empty, every price is written `[PRICE TO CONFIRM]`.

## Targets
- Countries (targets.countries): India, United States, United Kingdom, Australia
- Cities (targets.cities): [ASK — for local businesses]
- Company size (targets.company_size): [ASK]
- Buyer titles (targets.buyer_titles): Founder, Owner, CEO, Managing Director, Head of Marketing, CTO
- Excluded markets (targets.exclude_countries): none
- Never target: agencies, freelancers, job seekers
- Languages: English; Hindi / Hinglish when the prospect writes in it

## Proof (with `PROOF-BANK.md`, the only proof any message may cite)
- Case studies (proof.case_studies): [ASK — 2-3: client or type, what we did, the result, a link]
- Portfolio (proof.portfolio_url): [ASK]
- Years / projects / team (proof.years_in_business, projects_done, team_size): [ASK]
- Notable clients (with permission): [ASK]

## Positioning
- Differentiators (positioning.differentiators): 270 named services across 12 disciplines, so strategy, design,
  build, AI, automation and growth stay with one studio · [ASK — 1-2 more, concrete]
- Real guarantees (positioning.guarantees): [ASK — or "none"]

## Buyer signals
- Pains right before they hire (signals.pains): [ASK]
- Buying triggers (signals.triggers): [ASK — launch, funding, rebrand, festive season, migration…]
- Tools they leave (signals.tools_they_leave): [ASK — Wix, Squarespace, spreadsheets…]

## Brands & sheet
- Brand 1: Vintoria — business@vintoria.org — build services (disciplines 02-10)
- Brand 2: Radian Marketing — amar@radianmarketing.site — sender: Amar, Tech & Development Head — angle: marketing and
  growth (SEO, local SEO / GMB, ads, social, CRO, content, Amazon) — all facts in
  `../../vintoria-sales/references/radian-profile.md` (from radianmarketing.com, 2026-11-17)
- Radian website: https://radianmarketing.com · phone / WhatsApp: +91 93106 42998 · public email: hi@radianmarketing.com
- Radian postal address: 55, 3rd Floor, Saidulajab, Near Westend Marg Lane-2, New Delhi, India
- radianmarketing.site redirects to radianmarketing.com: [ASK: yes / no]
- Radian prices: Shopify Development from ₹35,000 · Woocommerce Development from ₹25,000 · Wordpress Sites from ₹15,000 ·
  Custom website from ₹45,000 (all "starts from", INR) — every other Radian service: [ASK]
- Radian case-study numbers to confirm (the site contradicts itself): [ASK]
- Radian domain set up (SPF, DKIM, DMARC) and warming up: [ASK: yes / no, start date]
- Daily email cap per inbox (warm-up): business@vintoria.org [ASK, e.g. 30] · amar@radianmarketing.site [ASK: start 10-15, +5 a week]

## Automation (channels and limits)
- Lead source: LinkedIn only (each PC's own logged-in account) — only people looking to hire an agency or outside team
- LinkedIn: email (Vintoria day 0, Radian day 1) when an email is found; otherwise comment + connection note, then a message once they accept — yes
- WhatsApp: buyers message +91 87660 33979 first (click-to-chat); the Closer replies from the business phone
- Cold calls / SMS: no
- Approval mode: auto   ← `auto` = the PCs post and send messages that pass every check; `review` = the owner approves each one
- Hourly run: on, 24/7 on all three PCs (`vintoria-hourly-run`, Hermes scheduled jobs — `../../vintoria-sales/references/hermes-setup.md`)
- Daily lead target: 60 on every PC (180 team, no duplicates) · start 05:00 IST · every 30 minutes until reached · up to 8 per run ·
  behind pace → widen the search, never the quality bar
- Airtable base: [ASK: name + link] — tables per `../../vintoria-sales/references/airtable.md`
- LinkedIn accounts: PC1 [ASK] · PC2 [ASK] · PC3 [ASK] (three different accounts, never one account on two PCs)
- Per-hour target: up to 10 valuable LinkedIn agency-seekers (a ceiling, never a quota)
- Per-hour limits per PC (each PC's LinkedIn account; emails per inbox): emails 10 (only 08:00-19:00 on weekdays in the prospect's time zone; otherwise
  queued; each inbox also within its daily warm-up cap) · LinkedIn comments 3 (≥ 10 minutes apart) · LinkedIn
  connection notes 15 per day (LinkedIn's own weekly invitation limit applies) · LinkedIn messages 20 per day
- Circuit breakers: `vintoria-account-health` every 6 hours → GREEN (full limits) / YELLOW (half) / RED (pause + escalate);
  a captcha, warning or restriction triggers the check at once · email bounces over 2 % in 14 days → YELLOW
- Hot leads (value 85+, under 2 h, ≤ 5 comments): fast track, contacted within ~15 minutes
- Authority: one LinkedIn post a weekday from Pratik Patil's profile + 5-10 comments on buyers' posts — yes / no
- Google Business Profile review link (for the proof bank): [ASK]
- Owner digest: 21:00 IST to the owner (WhatsApp-ready)
- Team: three Hermes PCs — PC1 Build, PC2 Growth, PC3 Manager & Closer (`../../vintoria-sales/references/team.md`); owner = the human (escalations)
```

**Ready** = every required field in `intake.md` is filled. Until then, keep working but mark gaps `[ASK]` in anything
you write and tell the user which answers are missing.
