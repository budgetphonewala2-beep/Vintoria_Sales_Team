# Lead queries and sources — the playbook

Better queries = better leads. `python <SCRIPTS>/query_library.py --services web,seo --location Pune` prints every
query below, generated for your services and market. `lead_sources.py` runs them.

## The formula (why these queries work)

**ASKING phrase + SERVICE phrase + platform + exclusions + recency.**

| Part | Examples | Why |
|---|---|---|
| Asking | "looking for", "can anyone recommend", "need", "suggestions", "anyone know", "chahiye", "batao" | Without it you get sellers |
| Service (buyer words) | "web developer", "need a new website", "website redesign", "SEO agency", "rank on Google" | Buyers name the outcome, not "digital solutions" |
| Platform | `site:linkedin.com/posts`, `site:reddit.com`, r/forhire `flair:Hiring` | One platform per query = cleaner results |
| Exclusions | `-"for hire"` `-"open to work"` `-"we offer"` `-"I am a"`, LinkedIn `NOT "open to work"` | Removes freelancers advertising |
| Recency | `--posted 24h/week`, Google `qdr:w`, HN `created_at_i>` | A 3-day-old ask converts far better than a 3-week-old one |
| Location (local ICP only) | `AND "Pune"`, `"Bangalore"`, `"New York"` | Halves noise for local services; skip it for remote work |

## LinkedIn post search (HarvestAPI actor) — rules
- Boolean `AND`, `OR`, `NOT` (uppercase), `"exact phrases"`, parentheses. **Max 5 operators, 500 characters** per query —
  `query_library.valid_linkedin()` enforces it; longer queries are refused before any credits are spent.
- Put `NOT ...` last. LinkedIn returns up to ~400-500 posts per query, so split broad ideas into several sharp queries.
- Strong patterns (operators counted):
  - `"looking for" AND ("web developer" OR "website developer" OR "web designer")` (3)
  - `("can anyone recommend" OR "recommendations for") AND ("SEO agency" OR "SEO expert")` (3)
  - `("need a website" OR "need a new website" OR "website redesign") AND ("looking for" OR help)` (4)
  - `"need" AND ("Shopify developer" OR "Shopify expert") AND "India" NOT "open to work"` (4)
  - `("website banwana hai" OR "website banwani hai" OR "developer chahiye")` (2)
- Run with `--posted 24h` daily or `--posted week` weekly; sort by date.

## Every source, and what it is best for

| Source | Command | Best for | Notes |
|---|---|---|---|
| LinkedIn posts | `lead_sources.py linkedin` | B2B founders/owners asking publicly | Apify HarvestAPI; author name + headline + profile URL included |
| Hacker News | `lead_sources.py hackernews` | Startups: "Seeking freelancer" thread (monthly), Ask HN asks | Free, no key; posts often include an email → no finder needed |
| Reddit | `lead_sources.py reddit` | r/forhire `[Hiring]`, r/smallbusiness, r/startups, r/shopify, r/indianstartups | Apify, or free public JSON; buyers rarely leave an email → reply where they posted (user does it) |
| X / Twitter | `lead_sources.py x` | Founders, indie hackers, creators asking for help | Apify tweet scraper; uses `-filter:retweets -"for hire"` |
| Facebook groups | `lead_sources.py facebook --group-url ...` | Local business owners, Indian SMB groups | Public groups only; you name the groups |
| Google X-ray | `lead_sources.py google` | Quora, Indie Hackers, Upwork public jobs, FB groups, Hinglish phrases, hiring signals | Apify Google scraper or Bright Data |
| Google Maps | `lead_sources.py maps --location Pune` | Local businesses with **no website / social-only page / low rating / few reviews** | Outbound list with need signals + phone (WhatsApp) |
| Product Hunt | `lead_sources.py producthunt` | New launches with few upvotes → need marketing, SEO, design | Free developer token |
| Any Apify actor | `lead_sources.py actor user/name --input in.json` | Anything else (Instagram, YouTube comments, Craigslist, job boards...) | Output normalized and intent-scored |

`lead_sources.py hunt --services web,seo --location Pune` runs everything you have keys for, in this order:
Hacker News → LinkedIn → Reddit → Google X-ray → X.

## Hidden-intent (signal) searches — companies that need you but didn't ask
- Hiring for the role you replace: `(site:linkedin.com/jobs OR site:naukri.com OR site:indeed.com) ("SEO executive" OR "social media manager") "Pune"`
- Just launched / raised: Product Hunt launches; `"<city>" ("just launched" OR "soft launch" OR "grand opening") restaurant OR clinic`
- Bad web presence: Google Maps "no website"; `site:business.site <category> <city>` (free Google sites)
- Unhappy with the current provider: `("our agency" OR "our developer") ("disappeared" OR "not responding" OR "ghosted")`

## Hinglish / Hindi
- `"website banwana hai" OR "website banwani hai" OR "website chahiye"`
- `"developer chahiye" OR "koi developer batao" OR "app banwana hai"`
- `"seo karwana hai" OR "seo wala chahiye" OR "marketing agency chahiye"`
- `"वेबसाइट बनवानी है" OR "वेबसाइट चाहिए"`

## Keep what works
- Every lead keeps its `source` (`hunt:li-web`, `maps:dentist in Pune`, ...). Each Monday, `pipeline.py report` →
  `by_source` shows prospects, meetings and wins per source: double the queries that book meetings, drop the rest.
- Add your niche words to the strongest queries (`clinic`, `D2C`, `SaaS`, `real estate`) once you know what converts.
