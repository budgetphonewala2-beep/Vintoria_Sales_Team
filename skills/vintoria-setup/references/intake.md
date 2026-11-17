# Seller intake interview

Goal: a `SELLER-PROFILE.md` complete enough that every query, filter, email and proposal is specific to this
seller. Ask in at most three short rounds. Give an example answer under each question. Accept "skip" for
optional fields. Never invent answers; above all, never invent proof.

## Round 1 — the business (2 minutes)

| Ask | Field | Why it matters | Weak answer → better |
|---|---|---|---|
| Business name and website? | `seller.company`, `seller.website` | Signature, proposals, research on your own site | — |
| Your name and the address you send from? | `seller.name`, `seller.email` | Truthful sender (CAN-SPAM), reply detection | "info@" → a real person's mailbox |
| Business postal address? | `seller.postal_address` | Required in US commercial email | — |
| Your time zone? | `seller.timezone` | Meeting slots in both zones | "IST" → `Asia/Kolkata` |
| Which services? (web, app, seo, marketing, design, software, ecommerce, video) | `offer.services` | Picks the service vocabulary for every query | "digital" → `web, seo` |
| What exactly do you deliver, in one line? | `offer.service_details` | The "what we do" line in emails | "end-to-end solutions" → "Shopify stores for DTC brands in 4-6 weeks" |
| Your best niches (1-5)? | `offer.niches` | **The biggest single improvement to lead quality** | "everyone" → "DTC skincare, specialty coffee, dental clinics" |

## Round 2 — the buyer (3 minutes)

| Ask | Field | Why it matters | Weak → better |
|---|---|---|---|
| Which countries? Any cities? | `targets.countries`, `targets.cities` | Google country, Maps cities, send times, compliance | "abroad" → `US, UK, CA, AU`; cities only for local businesses |
| Markets to exclude? | `targets.exclude_countries` | Leads mentioning them are dropped | `India` (if you only want overseas clients) |
| Who signs off? (job titles) | `targets.buyer_titles` | Apollo / LinkedIn people filters | "decision makers" → "Founder, Owner, CEO, Head of E-commerce" |
| Company size? | `targets.company_size` | Apollo size ranges | `1-50` |
| Typical project and your minimum, with currency? | `offer.deal_size` | Qualification, proposal options | "depends" → `{"min": 2000, "typical": 5000, "currency": "USD"}` |
| What problems do clients have right before they hire you? | `signals.pains` | Pain-language queries ("our store is slow") | "bad website" → "store is slow", "low conversion", "site looks outdated" |
| What events make them buy? | `signals.triggers` | Trigger queries | "product launch", "rebrand", "raised a seed round", "opening a second location" |
| Which tools/platforms do they move away from? | `signals.tools_they_leave` | Switching queries ("moving from Wix") | `Wix, Squarespace, WooCommerce` |
| Which platforms do you specialise in? | `offer.platforms` | "Shopify developer"-type queries | `Shopify, Klaviyo` |
| What outcome do they buy, in their words? | `offer.outcomes` | Subject lines, first lines | "faster store", "more booked appointments" |

## Round 3 — proof and positioning (2 minutes)

| Ask | Field | Why it matters |
|---|---|---|
| 2-3 real results: client (or type), what you did, the result, a link | `proof.case_studies` | The **only** proof emails may cite; truth self-check enforces it |
| Portfolio link; years in business, projects done, team size | `proof.*` | Credibility line, follow-up email 3 |
| Why you over other agencies (2-3 concrete reasons)? | `positioning.differentiators` | Objections, proposals (only real ones the owner confirms — e.g. "works in US hours", "fixed price per milestone", a certification actually held) |
| Any guarantee you really offer? | `positioning.guarantees` | Risk reversal, only if true |
| Booking link? | `seller.booking_url` | Sent only after a prospect says yes |

## From answers to queries (what the scripts do with them)

- `offer.niches` × `offer.services/platforms` → LinkedIn `"looking for" AND ("Shopify developer" OR "Shopify expert") AND skincare NOT India`
- `signals.pains` → `("store is slow" OR "low conversion" OR "site looks outdated") AND ("our website" OR "our store" OR help)`
- `signals.triggers` → `("product launch" OR rebrand) AND ("looking for" OR need)`
- `signals.tools_they_leave` → `("moving from Wix" OR "migrate from Wix" OR "switching from Squarespace") AND (help OR developer)`
- `targets.buyer_titles` × `targets.countries` × `targets.company_size` × `offer.niches` → Apollo people-search URLs,
  Leads Finder filters and LinkedIn profile searches
- `offer.niches` → niche subreddits (r/Dentistry, r/shopify, r/realtors ...) and Google Maps searches in `targets.cities`
- `targets.exclude_countries` → `NOT India` / `-India` in queries, and leads mentioning that market are dropped
- `targets.countries` → Google country code, and each prospect's send window in their own time zone

Write the resulting queries into `IDEAL-CUSTOMER-PROFILE.md` and show the user a sample before hunting.

## Example: a complete profile (abridged)

Vintoria's own profile in this shape — real values where known, `[ASK]` where only the owner can answer. Never copy a
value from any other example; never fill an `[ASK]` with a guess.

```json
{"seller": {"name": "Pratik Patil", "title": "Co-founder", "company": "Vintoria", "email": "business@vintoria.org",
            "whatsapp": "+91 87660 33979", "country": "India", "timezone": "Asia/Kolkata",
            "postal_address": "[ASK]", "booking_url": "[ASK]"},
 "offer": {"services": "the 270-service catalog, active lanes in OFFER.md",
           "deal_size": "[ASK — or leave empty: prices stay [PRICE TO CONFIRM]]"},
 "targets": {"countries": ["IN", "US", "UK", "AU"], "buyer_titles": ["Founder", "Owner", "Director", "Head of Marketing"],
             "company_size": "1-200"},
 "proof": {"case_studies": "[ASK — only real ones; empty is fine]", "years_in_business": "[ASK]"},
 "brands": {"second": "Radian Marketing — see radian-profile.md"},
 "signals": {"pains": ["no online booking", "slow or outdated site", "store loads slowly on mobile", "manual work"],
             "triggers": ["new location", "launch", "rebrand", "agency or developer stopped responding"]}}
```
