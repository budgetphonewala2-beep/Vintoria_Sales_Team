# SELLER-PROFILE.md — template (pre-filled with what the Vintoria catalog already says)

Copy this into `SELLER-PROFILE.md` in the working folder (or keep it in the conversation for a chat bot), then fill every
`[ASK]` through the interview in `intake.md`. Never fill an `[ASK]` with a guess — especially prices and case studies.
Field keys in brackets match `intake.md`.

```markdown
# SELLER-PROFILE — Vintoria
Last updated: YYYY-MM-DD · Status: Incomplete | Ready

## Seller
- Company (seller.company): Vintoria — digital product studio
- Website (seller.website): [ASK]
- Sender name (seller.name): [ASK]
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

## Proof (the only proof emails and proposals may cite)
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

## Channels and automation
- Lead sources: LinkedIn and Reddit only (accounts logged in on the bot's machine)
- Reddit: public comments on buyer posts with the WhatsApp link — yes
- LinkedIn: email from business@vintoria.org when an email is found; otherwise comment / connection note — yes
- WhatsApp: buyers message +91 87660 33979 first (click-to-chat); Vintoria replies from the business phone
- Cold calls / SMS: no
- Approval mode: auto   ← `auto` = the bot posts and sends messages that pass every check; `review` = the user approves each one
- Daily limits: Reddit 8 comments · LinkedIn 10 comments, 15 connection requests, 20 DMs · cold emails 20
```

**Ready** = every required field in `intake.md` is filled. Until then, keep working but mark gaps `[ASK]` in anything
you write and tell the user which answers are missing.
