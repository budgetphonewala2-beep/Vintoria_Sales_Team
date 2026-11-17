# Lead queries — LinkedIn and Reddit only

Vintoria hunts on the two platforms the bot is logged in to. Better queries = better leads, and the sharpest come from
`SELLER-PROFILE.md` and `OFFER.md`: niches, pains, triggers, tools clients leave, target countries. Keep the queries that
work in `IDEAL-CUSTOMER-PROFILE.md`.

## The formula

**ASKING phrase + SERVICE phrase (+ niche / pain / place) + exclusions + recency.**

| Part | Examples | Why |
|---|---|---|
| Asking | "looking for", "can anyone recommend", "need", "suggestions", "anyone know", "koi batao", "chahiye" | Without it you get sellers |
| Service (buyer words) | "web developer", "need a website", "website redesign", "app developer", "AI chatbot", "automate", "Shopify developer", "SEO agency", "rank on Google" | Buyers name the outcome, not "digital solutions" |
| Niche / pain / trigger | "clinic", "restaurant", "D2C", "store is slow", "moving from Wix", "launching next month" | 5-10x fewer irrelevant posts |
| Place (local work) | "Pune", "Mumbai", "Bangalore", "London", "Sydney", "Texas" | Halves noise for local services |
| Exclusions | `NOT "open to work"`, `NOT hiring` (job ads), `-"for hire"` | Removes freelancers advertising and job posts |
| Recency | Date posted: past 24 hours / past week; sort by Latest / New | A 1-day-old ask converts far better than a 3-week-old one |

## LinkedIn (logged in)

**Where:** search bar → Posts → sort **Latest**, **Date posted: Past 24 hours** (daily) or **Past week**; optionally
Author industry / location filters.
**Rules:** boolean `AND`, `OR`, `NOT` in capitals, `"exact phrases"`, parentheses, at most 5 operators per query (longer
ones are ignored), `NOT …` last.

Strong queries (operators counted):
- `"looking for" AND ("web developer" OR "website developer" OR "web designer")` (3)
- `("need a website" OR "new website" OR "website redesign") AND ("looking for" OR recommend)` (4)
- `("can anyone recommend" OR "recommendations for") AND ("app developer" OR "mobile app")` (3)
- `"looking for" AND ("AI chatbot" OR "AI agent" OR "AI developer")` (3)
- `("automate" OR "CRM setup" OR "Zapier") AND ("looking for" OR "need help")` (4)
- `"looking for" AND ("Shopify developer" OR "Shopify expert")` (2)
- `("SEO agency" OR "SEO expert" OR "digital marketing agency") AND recommend NOT hiring` (4)
- Niche × service: `"looking for" AND ("web developer" OR "app developer") AND clinic` (3)

Also useful: posts in the **Jobs → "Services" / ProFinder-style requests** and comments under "looking for agency
recommendations" posts by founders. Each lead: author name, headline, profile URL, the post URL and its date.

## Reddit (logged in)

**Where:** search inside a subreddit (`subreddit → search`, sort **New**, time **Past week**), or Reddit-wide search
with `subreddit:` / `flair:` filters.

| Subreddit | What to search | Notes |
|---|---|---|
| r/forhire | `flair:Hiring website OR app OR SEO OR shopify OR "AI"` | Buyers post `[Hiring]`; offers in comments are expected — read the rules |
| r/smallbusiness | `"need a website" OR "looking for a developer" OR "recommend" web` | Check rules for self-promotion before linking |
| r/Entrepreneur, r/startups | `"looking for" developer OR agency OR "MVP"` | Founders building MVPs, apps, automations |
| r/indianstartups, r/india, r/bangalore, r/pune, r/mumbai | `"website" OR "app developer" OR "developer chahiye"` | Indian SMBs and founders; Hinglish posts |
| r/shopify, r/ecommerce | `"looking for" OR "hire" developer OR expert` | Store builds, speed, conversion |
| r/SEO, r/PPC, r/socialmedia | `"looking for" agency OR "recommend"` | Strict rules — often no promotion; help-only comments |
| r/ChatGPT, r/automation, r/zapier, r/n8n | `"looking for" OR hire chatbot OR automation` | AI and automation buyers |
| Niche subs (r/Dentistry, r/restaurateur, r/realtors, r/gymowner…) | `website OR app OR "marketing"` | Owners talking shop |

Each lead: username, the post URL, its age, the comment count (fewer = less competition) and the subreddit's rules on
promotion (note them once per subreddit).

## Hidden intent (they need us but didn't ask)
- LinkedIn: "our agency disappeared", "developer not responding", "website is down again", "launching next month".
- Reddit: complaints about their current site, store speed or a freelancer who vanished — help-only comments work best.

## Keep what works
Every lead keeps its `source` in `PIPELINE.md` (`li:need-website-clinic`, `rd:forhire-hiring`). Each Monday
`vintoria-report` counts replies, calls and wins per source: double the queries that book calls, drop the rest.
