# Lead queries and sources — the playbook

Better queries = better leads. The sharpest queries come from **your** profile: `SELLER-PROFILE.json` (made by
`sales-setup`) feeds your niches, platforms, buyer pains, buying triggers, tools clients leave, buyer titles,
target countries and excluded markets into every query. `python <SCRIPTS>/query_library.py` prints them;
`lead_sources.py` runs them. Without a profile you get generic service queries — fine to start, weak to scale.

## The formula (why these queries work)

**ASKING phrase + SERVICE phrase + platform + exclusions + recency.**

| Part | Examples | Why |
|---|---|---|
| Asking | "looking for", "can anyone recommend", "need", "suggestions", "anyone know" | Without it you get sellers |
| Niche (from your profile) | "DTC skincare", "dental clinics", "specialty coffee" | 5-10x fewer irrelevant posts |
| Pain / trigger / switch | "store is slow", "product launch", "moving from Wix" | Catches buyers who never name the role |
| Service (buyer words) | "web developer", "need a new website", "website redesign", "SEO agency", "rank on Google" | Buyers name the outcome, not "digital solutions" |
| Platform | `site:linkedin.com/posts`, `site:reddit.com`, r/forhire `flair:Hiring` | One platform per query = cleaner results |
| Exclusions | `-"for hire"` `-"open to work"` `-"we offer"` `-"I am a"`, LinkedIn `NOT "open to work"` | Removes freelancers advertising |
| Recency | `--posted 24h/week`, Google `qdr:w`, HN `created_at_i>` | A 3-day-old ask converts far better than a 3-week-old one |
| Market | Google country code from your target countries; `NOT India` / `-India` when you exclude it | Overseas clients only; leads mentioning an excluded market are dropped |
| Location (local ICP only) | `AND "Austin"`, `"Manchester"`, `"Sydney"` | Halves noise for local services; skip it for remote work |

## LinkedIn post search (HarvestAPI actor) — rules
- Boolean `AND`, `OR`, `NOT` (uppercase), `"exact phrases"`, parentheses. **Max 5 operators, 500 characters** per query —
  `query_library.valid_linkedin()` enforces it; longer queries are refused before any credits are spent.
- Put `NOT ...` last. LinkedIn returns up to ~400-500 posts per query, so split broad ideas into several sharp queries.
- Strong patterns (operators counted):
  - `"looking for" AND ("web developer" OR "website developer" OR "web designer")` (3)
  - `("can anyone recommend" OR "recommendations for") AND ("SEO agency" OR "SEO expert")` (3)
  - `("need a website" OR "need a new website" OR "website redesign") AND ("looking for" OR help)` (4)
  - `"looking for" AND ("Shopify developer" OR "Shopify expert") AND skincare NOT India` (4) — niche × service
  - `("store is slow" OR "low conversion" OR "theme looks dated") AND ("our website" OR "our store" OR help)` (5) — pain
  - `("moving from Wix" OR "migrate from Wix" OR "switching from Squarespace") AND (help OR developer)` (5) — switch
- Run with `--posted 24h` daily or `--posted week` weekly; sort by date.

## Every source, and what it is best for

| Source | Command | Best for | Notes |
|---|---|---|---|
| **Google SERP (main)** | `serp.py hunt` | Everything at once: LinkedIn posts, Reddit, Quora, X, FB groups, Indie Hackers, Upwork jobs via X-ray, in your countries | Serper (~$1/1k), SerpAPI, Bright Data, Brave, Apify — first key that works; `serp.py providers` |
| LinkedIn posts | `lead_sources.py linkedin` | B2B founders/owners asking publicly | Apify HarvestAPI; author name + headline + profile URL included |
| Hacker News | `lead_sources.py hackernews` | Startups: "Seeking freelancer" thread (monthly), Ask HN asks | Free, no key; posts often include an email → no finder needed |
| Reddit | `lead_sources.py reddit` | r/forhire `[Hiring]`, r/smallbusiness, r/startups, r/shopify, r/indianstartups | Apify, or free public JSON; buyers rarely leave an email → reply where they posted (user does it) |
| X / Twitter | `lead_sources.py x` | Founders, indie hackers, creators asking for help | Apify tweet scraper; uses `-filter:retweets -"for hire"` |
| Facebook groups | `lead_sources.py facebook --group-url ...` | Local business owners, Indian SMB groups | Public groups only; you name the groups |
| Google X-ray | `lead_sources.py google` | Quora, Indie Hackers, Upwork public jobs, FB groups, hiring signals | Apify Google scraper or Bright Data |
| Apollo (via Apify) | `lead_sources.py apollo [--url ...] --add --verify` | Decision makers by title × country × size × niche | Lists, not intent — deep-scan first, strong first line |
| Leads Finder | `lead_sources.py leads --add --verify` | Apollo-style filters without an Apollo account | Same |
| LinkedIn people | `lead_sources.py people` / `employees --company <url>` | Founders/owners in a niche; the right person at a known company | Pair with their company's dossier |
| Google Maps | `lead_sources.py maps` (cities from your profile) | Local businesses with **no website / social-only page / low rating / few reviews** | Outbound list with need signals + phone (WhatsApp) |
| Product Hunt | `lead_sources.py producthunt` | New launches with few upvotes → need marketing, SEO, design | Free developer token |
| Any Apify actor | `lead_sources.py actor user/name --input in.json` | Anything else (Instagram, YouTube comments, Craigslist, job boards...) | Output normalized and intent-scored |

`lead_sources.py hunt` runs every intent source you have keys for, with your profile's queries, in this order:
Hacker News → LinkedIn → Reddit → Google X-ray → X.

## Hidden-intent (signal) searches — companies that need you but didn't ask
- Hiring for the role you replace: `(site:linkedin.com/jobs OR site:indeed.com OR site:glassdoor.com) ("SEO specialist" OR "Shopify developer") "Austin"`
- Just launched / raised: Product Hunt launches; `"<city>" ("just launched" OR "soft launch" OR "grand opening") restaurant OR clinic`;
  `site:techcrunch.com OR site:crunchbase.com "raised" seed <niche>`
- Bad web presence: Google Maps "no website"; `site:business.site <category> <city>` (free Google sites)
- Unhappy with the current provider: `("our agency" OR "our developer") ("disappeared" OR "not responding" OR "ghosted")`

## Keep what works
- Every lead keeps its `source` (`hunt:li-web`, `maps:dentist in Austin`, ...). Each Monday, `pipeline.py report` →
  `by_source` shows prospects, meetings and wins per source: double the queries that book meetings, drop the rest.
- Add your niche words to the strongest queries (`clinic`, `D2C`, `SaaS`, `real estate`) once you know what converts.
