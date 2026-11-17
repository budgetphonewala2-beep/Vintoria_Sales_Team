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
| Recency | Date posted: past 24 hours only; sort by Latest / New | The first good answer usually wins; older posts are skipped (`../../vintoria-sales/references/lead-quality.md`) |

## Which market, which hour (24/7 rotation)

People post during their own working day, so each hourly run aims where it is daytime now (times in IST):

| IST | Daytime in | Search first | Then |
|---|---|---|---|
| 03:30-08:59 | Australia (Sydney 09:00-14:30*) | AU: Sydney, Melbourne, Brisbane, Perth; r/australia, r/sydney, r/melbourne and Australian small-business subs you have checked | India early posts |
| 09:00-13:29 | India | Indian cities and Hinglish phrases; r/indianstartups, r/india, r/bangalore, r/pune, r/mumbai, r/delhi, r/hyderabad | AU afternoon |
| 13:30-18:29 | India + UK | UK: London, Manchester, Birmingham; UK small-business subs you have checked, r/smallbusiness | India |
| 18:30-23:59 | US East morning + UK afternoon | US: New York, Texas, Florida, California; r/smallbusiness, r/Entrepreneur, r/forhire | UK |
| 00:00-03:29 | US (all zones) | US niches and r/forhire, r/shopify, r/ecommerce | — |

\* Sydney is 4.5-5.5 hours ahead of IST depending on daylight saving. Global subreddits (r/forhire, r/smallbusiness,
r/shopify, r/Entrepreneur) are searched every hour regardless.

**Lane rotation:** hour of the day mod 6 → 0 web & booking · 1 Shopify / e-commerce · 2 apps & MVPs · 3 AI chatbots &
agents · 4 automation & CRM · 5 SEO & marketing. Only lanes active in `OFFER.md`; skip inactive ones. Each run uses
the lane of the hour **plus** the two best-performing queries from last week (`IDEAL-CUSTOMER-PROFILE.md`).

## Open the search directly (fewer clicks, fewer mistakes)

Replace `<q>` with the URL-encoded query (space → `%20`, `"` → `%22`, `(` → `%28`, `)` → `%29`).

| What | URL |
|---|---|
| LinkedIn posts, past 24 h, newest | `https://www.linkedin.com/search/results/content/?keywords=<q>&datePosted=%22past-24h%22&sortBy=%22date_posted%22` |
| Reddit, one subreddit, newest, past day | `https://www.reddit.com/r/<sub>/search/?q=<q>&restrict_sr=1&sort=new&t=day` |
| Reddit, all of Reddit, newest, past day | `https://www.reddit.com/search/?q=<q>&sort=new&t=day` |
| A subreddit's newest posts (no query) | `https://www.reddit.com/r/<sub>/new/` |

If LinkedIn ignores a URL filter, set **Posts → Latest → Past 24 hours** by hand and continue. Always confirm the age on
the post itself (`../../vintoria-sales/references/lead-quality.md`).

## LinkedIn (logged in)

**Where:** search bar → Posts → sort **Latest**, **Date posted: Past 24 hours**; optionally
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
- India: `("website developer" OR "app developer") AND (Pune OR Mumbai OR Bangalore) AND "looking for"` (4)
- Hinglish: `("website chahiye" OR "app banwana" OR "developer chahiye")` (2)
- UK / AU wording: `("web designer" OR "website designer") AND recommend AND (London OR Sydney)` (4)
- Hidden intent: `("developer disappeared" OR "agency not responding" OR "website is down") NOT hiring` (3)

Also useful: posts in the **Jobs → "Services" / ProFinder-style requests** and comments under "looking for agency
recommendations" posts by founders. Each lead: author name, headline, profile URL, the post URL and its date.

## Reddit (logged in)

**Where:** search inside a subreddit (`subreddit → search`, sort **New**, time **Past 24 hours**), or Reddit-wide search
with `subreddit:` / `flair:` filters.

| Subreddit | What to search | Notes |
|---|---|---|
| r/forhire | `flair:Hiring website OR app OR SEO OR shopify OR "AI"` | Buyers post `[Hiring]`; offers in comments are expected — read the rules |
| r/hiring, r/freelance_forhire | `website OR app OR developer OR shopify` | Read each sub's rules; only posts by people hiring |
| r/smallbusiness | `"need a website" OR "looking for a developer" OR "recommend" web` | Check rules for self-promotion before linking |
| r/Entrepreneur, r/startups | `"looking for" developer OR agency OR "MVP"` | Founders building MVPs, apps, automations |
| r/indianstartups, r/india, r/bangalore, r/pune, r/mumbai | `"website" OR "app developer" OR "developer chahiye"` | Indian SMBs and founders; Hinglish posts |
| r/shopify, r/ecommerce | `"looking for" OR "hire" developer OR expert` | Store builds, speed, conversion |
| r/SEO, r/PPC, r/socialmedia | `"looking for" agency OR "recommend"` | Strict rules — often no promotion; help-only comments |
| r/ChatGPT, r/automation, r/zapier, r/n8n | `"looking for" OR hire chatbot OR automation` | AI and automation buyers |
| Niche subs (r/Dentistry, r/restaurateur, r/realtors, r/gymowner…) | `website OR app OR "marketing"` | Owners talking shop |

Each lead: username, the post URL, its age, the comment count (fewer = less competition) and the subreddit's rules on
promotion (note them once per subreddit).

**Skip:** r/slavelabour-style "cheapest possible" requests, students' assignment help, and any subreddit whose rules
ban commercial replies (note it once in `IDEAL-CUSTOMER-PROFILE.md` and stop searching it).

## Hidden intent (they need us but didn't ask)
- LinkedIn: "our agency disappeared", "developer not responding", "website is down again", "launching next month".
- Reddit: complaints about their current site, store speed or a freelancer who vanished — help-only comments work best.

## Keep what works
Every lead keeps its `source` in `PIPELINE.md` (`li:need-website-clinic`, `rd:forhire-hiring`). Each Monday
`vintoria-report` counts replies, calls and wins per source: double the queries that book calls, drop the rest.
