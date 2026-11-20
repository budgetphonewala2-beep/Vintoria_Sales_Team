# Lead queries — LinkedIn only, people looking for an agency

Vintoria hunts on **LinkedIn only**, through the account already logged in. The target is one kind of person: a founder,
owner or manager who is **looking to hire an agency, studio or outside team** — "looking for an agency", "can anyone
recommend a development partner", "we need a team to build our app", "our agency isn't delivering". Not freelancers
looking for work, not agencies selling, not companies hiring an employee.

## The formula

**AGENCY-SEEKING phrase + SERVICE phrase (+ niche / place) + exclusions + past 24 hours.**

| Part | Examples | Why |
|---|---|---|
| Agency-seeking | "looking for an agency", "recommend an agency", "agency recommendations", "looking for a partner", "development partner", "tech partner", "outsource", "looking for a team", "need a company to", "RFP", "request for proposal", "vendor for" | Without it you get freelancers, job ads and sellers |
| Service (their words) | "web development", "website", "app development", "mobile app", "software development", "AI", "automation", "Shopify", "SEO", "digital marketing", "performance marketing", "branding", "UI/UX" | Buyers name the outcome |
| Niche / place | "D2C", "SaaS", "real estate", "clinic", "restaurant", "startup"; Pune, Mumbai, Bangalore, Delhi, London, Sydney, New York | 5-10x less noise |
| Exclusions | `NOT hiring`, `NOT "open to work"`, `NOT freelancer`, `NOT internship`, `NOT "we are hiring"` | Removes job ads, job seekers and freelancers advertising |
| Recency | **Posts → Latest → Past 24 hours** | The first good agency reply usually gets the call |

## Where to search on LinkedIn

1. **Posts search** (main source) — search bar → Posts → **Latest** → **Past 24 hours**. Optionally filter "Author
   industry" or "From companies". Each lead: author name, headline, company, profile URL, post URL, age, comment count.
2. **Comments under "recommend an agency" posts** — when someone asks for agency recommendations, people in the comments
   often say "following" or "we need this too" — each of them is a lead too (same 24-hour rule for their comment).
3. **LinkedIn Services requests** — if Vintoria's LinkedIn Service Page is set up, buyers can send it proposal requests;
   check them in every hourly run (they're the warmest leads LinkedIn gives).
4. **Groups** the account has joined (founders, startups, D2C, SaaS, real estate) — sort by recent, same queries.

## Agency-seeking queries (at most 5 operators each — longer ones are ignored)

**Any service**
- `("looking for an agency" OR "recommend an agency" OR "agency recommendations") NOT hiring` (3)
- `("looking for a development partner" OR "looking for a tech partner" OR "outsourcing partner")` (2)
- `("need an agency" OR "hire an agency" OR "suggest an agency")` (2)
- `("request for proposal" OR RFP) AND (website OR app OR marketing)` (4)

**Web & e-commerce**
- `("website development agency" OR "web development agency" OR "web design agency") AND (looking OR recommend)` (4)
- `("Shopify agency" OR "Shopify partner" OR "ecommerce agency") AND (looking OR recommend OR need)` (5)

**Apps, SaaS & AI**
- `("app development agency" OR "app development company") AND (looking OR recommend OR need)` (4)
- `("software development company" OR "MVP development") AND ("looking for" OR recommend)` (3)
- `("AI agency" OR "AI development company" OR "automation agency") AND ("looking for" OR need)` (4)

**Marketing & growth (Radian's lane)**
- `("digital marketing agency" OR "performance marketing agency" OR "SEO agency") AND ("looking for" OR recommend)` (4)
- `("Amazon agency" OR "marketplace agency" OR "D2C agency") AND ("looking for" OR recommend)` (4)
- `("social media agency" OR "branding agency") AND ("looking for" OR recommend) NOT hiring` (4)

**More growth lanes (Radian's full service list — `../../vintoria-sales/references/radian-profile.md`)**
- `("Myntra agency" OR "Flipkart agency" OR "Nykaa agency" OR "marketplace management") AND ("looking for" OR recommend)` (5)
- `("quick commerce" OR Blinkit OR Zepto OR Instamart) AND ("looking for" OR onboarding)` (5)
- `("CRO agency" OR "conversion rate optimization" OR "landing page agency") AND ("looking for" OR recommend)` (4)
- `("email marketing agency" OR "retention agency" OR "WhatsApp marketing") AND ("looking for" OR recommend)` (4)
- `("Meta ads agency" OR "Google ads agency" OR "PPC agency") AND ("looking for" OR recommend) NOT hiring` (5)
- `("GEO" OR "AEO" OR "AI search visibility" OR "generative engine optimization") AND (agency OR "looking for")` (5)
- `("motion graphics agency" OR "explainer video agency" OR "UGC video agency" OR "video production agency") AND ("looking for" OR recommend)` (5)
- `("growth audit" OR "funnel audit" OR "marketing consultant") AND ("looking for" OR recommend) NOT hiring` (5)

**Switching agencies (very warm)**
- `("our agency" OR "current agency" OR "previous agency") AND ("not delivering" OR disappointed OR switching)` (5)
- `("developer disappeared" OR "agency ghosted" OR "looking to switch agencies")` (2)

**India, Hinglish and places**
- `("agency chahiye" OR "website banwana" OR "app banwana" OR "developer chahiye")` (3)
- `("looking for an agency" OR "recommend an agency") AND (Mumbai OR Pune OR Bangalore OR Delhi)` (5)
- `("looking for an agency" OR "recommend an agency") AND (London OR Sydney OR Melbourne OR "New York")` (5)

## Any of our ~330 services — the service rotation

Vintoria sells 270 catalog services and Radian ~60 more: **an agency-seeker for any of them is a lead.** The fixed
queries above catch the common asks; the rotation makes sure every other service gets searched too.

**Each PC's share** (`../../vintoria-sales/references/hermes-setup.md`):
| PC | Services it rotates through |
|---|---|
| PC1 | Vintoria 001-120: 01 Strategy, 02 Web, 03 SaaS, 04 Mobile, 05 UI/UX, 06 Branding |
| PC2 | Radian's full list (`../../vintoria-sales/references/radian-profile.md`) + Vintoria 211-270: 11 Marketing & SEO, 12 Growth |
| PC3 | Vintoria 121-210: 07 AI, 08 Automation, 09 Backend & Cloud, 10 E-Commerce |

**Every run:**
1. Read where the last run stopped (`Rotation to` on this PC's latest **Runs** record) and take the **next 6 services** in
   catalog order (wrap around at the end of the share).
2. Turn each service into **buyer words** — what a founder would actually type, using the service's file
   (`services-0X-….md` → "Who buys this", "Buying signals"):
   `173 PostgreSQL Development` → "PostgreSQL developer", "Postgres database help" ·
   `028 Booking Platform Development` → "booking website", "appointment booking system" ·
   Radian `Quickcommerce Onboarding` → "Blinkit onboarding", "Zepto listing".
3. One query per service: `("looking for an agency" OR "looking for a company" OR recommend) AND ("<buyer words 1>" OR "<buyer words 2>")`
   — 4 operators, past 24 hours, Latest.
4. Write `Rotation from` / `Rotation to` (service IDs or Radian names) and the queries used on this run's **Runs** record.
5. A lead found this way is cited by its exact service (`173 PostgreSQL Development`, or Radian's own name).

Six services a run cover a PC's whole share in about 20 runs. The position carries over to the next day, so every
service gets its turn even on days the 60 is reached early. A service whose query finds valuable leads
twice in a week joins the fixed queries in `IDEAL-CUSTOMER-PROFILE.md`.

## Which market, which hour (24/7 rotation)

People post during their own working day (times in IST):

| IST | Daytime in | Search first |
|---|---|---|
| 03:30-08:59 | Australia | AU cities (Sydney, Melbourne, Brisbane, Perth) |
| 09:00-13:29 | India | Indian cities, Hinglish queries |
| 13:30-18:29 | India + UK | London, Manchester, Birmingham, Indian cities |
| 18:30-23:59 | US East morning + UK afternoon | New York, Texas, Florida, California, London |
| 00:00-03:29 | US (all zones) | US cities and "any service" queries |

Sydney is 4.5-5.5 hours ahead of IST depending on daylight saving. "Any service" and "switching agencies" queries run
every hour regardless.

**Lane rotation:** hour of the day mod 8 → 0 web & e-commerce · 1 apps, SaaS & AI · 2 marketplaces & quick commerce ·
3 SEO, AEO & GEO · 4 paid ads (Meta, Google) · 5 social media & content · 6 CRO, landing pages & retention (email /
WhatsApp) · 7 branding, design & motion-graphics videos. Only lanes active in `OFFER.md`. Each run uses the lane of the hour plus the
"any service" and "switching" queries plus the two best queries from last week (`IDEAL-CUSTOMER-PROFILE.md`).

## Open the search directly

Replace `<q>` with the URL-encoded query (space → `%20`, `"` → `%22`, `(` → `%28`, `)` → `%29`):

`https://www.linkedin.com/search/results/content/?keywords=<q>&datePosted=%22past-24h%22&sortBy=%22date_posted%22`

If LinkedIn ignores a URL filter, set **Posts → Latest → Past 24 hours** by hand. Always confirm the age on the post
itself (`../../vintoria-sales/references/lead-quality.md`).

## Skip
- Agencies and freelancers advertising ("we are an agency…", "DM me for websites").
- Job ads ("we are hiring a developer", salary / CTC / full-time / internship).
- "Looking for a freelancer / intern / student, small budget" — they don't want an agency.
- People asking which agency to **join** (career questions).
- Posts where the author already chose ("found our agency, thanks").

## Keep what works
Every lead keeps its `source` in `PIPELINE.md` (`li:agency-any`, `li:agency-shopify`, `li:switching`). Each Monday
`vintoria-report` counts replies, calls and wins per query: double the queries that book calls, drop the rest.
