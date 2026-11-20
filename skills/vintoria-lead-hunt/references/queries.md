# Lead queries — LinkedIn only, people looking for an agency

Weak queries are the single biggest reason for few leads. This method comes from Lead-Forge's engine and was measured on
live LinkedIn searches. Follow it exactly; don't improvise long keyword lists.

## Six rules (measured)

1. **Quote real buyer sentences.** Every phrase is in quotes, written the way a buyer writes it ("looking for a marketing
   agency"). Loose words joined with AND match random posts.
2. **Use the short head noun.** "looking for a **marketing** agency / marketing **partner**" found **45 %** genuine buyers;
   the full "looking for a **digital marketing** agency" found **10 %** (mostly agencies advertising). Lead with the
   short noun, then use the full service name in later queries.
3. **First person beats impersonal.** "we are looking for…", "I need…", "can anyone recommend…" are buyers;
   "hiring X…" and "searching for X…" alone mostly return advice posts and job ads.
4. **Pack 2-4 phrases per query** with OR — at most about 18 words inside the quotes.
5. **A short exclusion tail only:** `NOT "we offer" NOT "open to work"` (add `NOT "available for hire"` if there's room).
   **Never `NOT hiring`** — it deletes real buyers who write "looking to **hire** an agency".
6. **Wide, not deep.** Posts → **Latest** → **Past 24 hours**, read the **first ~25 results** of a query, then run the next
   query. Scrolling deep into one search is where the sellers and old posts are.

## The query shape

```
("<buyer phrase 1>" OR "<buyer phrase 2>" OR "<buyer phrase 3>") NOT "we offer" NOT "open to work"
```
No results twice → run it without the `NOT` tail (the prefilter removes sellers anyway). Still nothing → one plain
unquoted phrase: `looking for marketing agency recommendations`.

## Phrase families — fill in H, S and T

- **H** = the short head noun: the last word of the service ("digital marketing" → marketing, "web development" →
  development, "app development" → development, "meta ads" → ads, "UI/UX design" → design, "social media marketing" →
  marketing). Firms by trade: consulting → "consulting firm", architecture → "architecture firm".
- **S** = the service the way buyers name it ("web development", "Shopify", "SEO", "Meta ads", "AI chatbot").
- **T** = the job to be done ("rebuild our website", "build our app", "manage our Meta ads", "set up our Shopify store",
  "run our SEO", "redesign our brand", "automate our lead follow-up", "list us on Amazon").

| # | Family | Pack |
|---|---|---|
| 1 | **Head noun** (always first) | `("looking for a H agency" OR "looking for a H partner" OR "need a H agency" OR "recommend a H agency")` |
| 2 | Agency for S | `("looking for an agency for S" OR "need an agency for S")` |
| 3 | Named S agency | `("recommendations for a S agency" OR "looking for a S agency" OR "hiring an agency for S")` |
| 4 | Seeking / recommend | `("need a S agency" OR "seeking an agency for S" OR "anyone recommend a S agency")` |
| 5 | Handle / hire | `("looking to hire an agency for S" OR "looking for an agency to handle S" OR "need an agency to handle S")` |
| 6 | **The task** | `("need an agency to T" OR "looking for a team to T" OR "want to outsource T")` |
| 7 | Partner / outsource / referral | `("need a partner for S" OR "outsource S to an agency" OR "anyone know a good S agency")` |
| 8 | **First person, any service** | `("we are looking for an agency" OR "we need an agency to" OR "i need an agency for")` |
| 9 | **Switching (very warm)** | `("looking to switch agencies" OR "our current agency" OR "our agency is not delivering")` |
| 10 | Hinglish | `("agency chahiye" OR "achhi agency batao" OR "website banwana hai" OR "app banwana hai")` |

Use "an" before vowel sounds: "an SEO agency", "an AI agency", "an app development agency", "an ads agency".
From the second query on, at least half the packs should be family 6 (the task) — buyers describe the job, not a title.

## Ready-made packs for the main services (from Lead-Forge's builder)

Each line is one query; add ` NOT "we offer" NOT "open to work"` to every one.

| Service | Query 1 (head noun) | Query 2 | Query 3 |
|---|---|---|---|
| Digital marketing (Radian) | `("looking for a marketing agency" OR "looking for a marketing partner" OR "need a marketing agency" OR "recommend a marketing agency")` | `("looking for an agency for digital marketing" OR "need an agency for digital marketing")` | `("need an agency to handle our marketing" OR "outsource our marketing" OR "anyone know a good marketing agency")` |
| Web development | `("looking for a development agency" OR "looking for a development partner" OR "need a development agency" OR "recommend a development agency")` | `("looking for a web development agency" OR "need a web development agency" OR "hiring an agency for web development")` | `("need an agency to rebuild our website" OR "looking for a team to build our website" OR "need a website agency")` |
| App development | (same head pack as web) | `("looking for an app development agency" OR "need an app development agency" OR "anyone recommend an app development agency")` | `("need an agency to build our app" OR "looking for a team to build our app" OR "app development partner")` |
| Shopify / e-commerce | `("looking for a Shopify agency" OR "looking for a Shopify partner" OR "need a Shopify agency" OR "recommend a Shopify agency")` | `("looking for an ecommerce agency" OR "need an ecommerce agency" OR "ecommerce agency recommendations")` | `("need an agency to set up our Shopify store" OR "looking for a team to build our store")` |
| SEO (Radian) | `("looking for an SEO agency" OR "need an SEO agency" OR "anyone recommend an SEO agency" OR "SEO agency recommendations")` | `("looking for an agency to handle SEO" OR "need an agency to handle our SEO" OR "outsource SEO to an agency")` | `("looking for an agency for SEO" OR "need a partner for SEO" OR "anyone know a good SEO agency")` |
| Paid ads (Radian) | `("looking for an ads agency" OR "looking for an ads partner" OR "need an ads agency" OR "recommend an ads agency")` | `("looking for a Meta ads agency" OR "need a Google ads agency" OR "performance marketing agency recommendations")` | `("need an agency to manage our Meta ads" OR "need an agency to run our Google ads" OR "outsource our paid ads")` |
| Social media (Radian) | `("looking for a social media agency" OR "need a social media agency" OR "recommend a social media agency")` | `("need an agency to handle our social media" OR "outsource our social media" OR "anyone know a good social media agency")` | |
| Branding & design | `("looking for a branding agency" OR "need a branding agency" OR "recommend a branding agency" OR "branding agency recommendations")` | `("looking for a design agency" OR "looking for a design partner" OR "need a UI UX agency")` | `("need an agency to redesign our brand" OR "need an agency for our rebrand")` |
| AI & automation | `("looking for an AI agency" OR "looking for an AI development partner" OR "need an AI agency" OR "recommend an AI agency")` | `("need an agency to build an AI chatbot" OR "looking for an automation agency" OR "need help automating our")` | `("looking for a development agency" OR "looking for a development partner")` |
| Marketplaces (Radian) | `("looking for an Amazon agency" OR "need an Amazon agency" OR "recommend an Amazon agency")` | `("need an agency to manage our Amazon" OR "marketplace management agency" OR "agency for Myntra" OR "agency for Flipkart")` | `("quick commerce onboarding" OR "agency for Blinkit" OR "agency for Zepto")` |
| CRO & landing pages (Radian) | `("looking for a CRO agency" OR "need a CRO agency" OR "conversion rate optimization agency")` | `("need an agency to fix our landing page" OR "need an agency to improve our conversion rate" OR "landing page agency recommendations")` | |
| Email & WhatsApp retention (Radian) | `("looking for an email marketing agency" OR "need an email marketing agency" OR "recommend a retention agency")` | `("need an agency to set up our email flows" OR "need an agency for WhatsApp marketing" OR "outsource our email marketing")` | |
| AEO / GEO (Radian) | `("need an agency for AI search visibility" OR "generative engine optimization agency" OR "answer engine optimization agency")` | `("need an agency to get us into ChatGPT answers" OR "looking for a GEO agency" OR "looking for an AEO agency")` | |
| Video (Radian) | `("looking for a video agency" OR "need a video production agency" OR "recommend a video agency")` | `("need an agency for our explainer video" OR "looking for a motion graphics agency" OR "need UGC videos for our brand")` | |

## Any of our ~330 services — the service rotation

An agency-seeker for **any** Vintoria catalog service (270) or Radian service (~60) is a lead. The packs above cover the
common asks; the rotation makes sure every other service gets searched.

| PC | Services it rotates through |
|---|---|
| PC1 | Vintoria 001-120: 01 Strategy, 02 Web, 03 SaaS, 04 Mobile, 05 UI/UX, 06 Branding |
| PC2 | Radian's full list (`../../vintoria-sales/references/radian-profile.md`) + Vintoria 211-270: 11 Marketing & SEO, 12 Growth |
| PC3 | Vintoria 121-210: 07 AI, 08 Automation, 09 Backend & Cloud, 10 E-Commerce |

**Every run:**
1. Read where the last run stopped (`Rotation to` on this PC's latest **Runs** record) and take the **next 6 services**
   (wrap around at the end of the share).
2. For each service write down, from its file (`../../vintoria-sales/references/services-0X-….md` → "Who buys this",
   "Buying signals", "Deliverables"): **H**, **S**, one **T**, and its vocabulary — **counts as** (synonyms, role nouns)
   and **not this service** (adjacent crafts). Example, `173 PostgreSQL Development`: H = development, S = PostgreSQL,
   T = "migrate our database to PostgreSQL"; counts as: Postgres, database migration; not this: MongoDB, data analyst.
3. One query per service:
   `("looking for an agency for S" OR "need a S agency" OR "need an agency to T") NOT "we offer" NOT "open to work"`.
4. Judge matches with that vocabulary (gate 5 in `../../vintoria-sales/references/lead-quality.md`: "not this service" scores ≤ 50).
5. Write `Rotation from` / `Rotation to` and the queries on this run's **Runs** record. The position carries over to the
   next day, so every service gets its turn even on days the 60 is reached early.

## A run's search plan (about 8 queries × the first 25 results ≈ 200 posts)

1. Family 8 (first person, any service) and family 9 (switching) — every run.
2. The head-noun pack (family 1) for this hour's lane, then two more ready-made packs for it.
3. The 6 rotation queries.
4. Behind pace (`../../vintoria-hourly-run/SKILL.md`): families 5-7 and 10 for the lane, other lanes' head packs.

Expected: ~200 posts → ~40 pass the prefilter (`prefilter.md`) → **4-8 leads**.

## When yield is low — read the drop reasons in **Seen**, fix the cause

| Most drops are… | Cause | Fix next run |
|---|---|---|
| sellers / agencies advertising | packs lean on "S agency" (agencies use those words about themselves) | more families 6 and 8; check the `NOT "we offer"` tail is there |
| job ads | impersonal "hiring" / "searching for" phrasings | drop them; use "need an agency to T", "we are looking for an agency" |
| freelancer-only | nouns that attract individuals | use agency / partner / team / company nouns |
| too old | not sorted by Latest, or scrolled too deep | Latest + Past 24 hours, first ~25 results only |
| not our service | wrong buyer words | use the head noun H; fix the rotation vocabulary |
| no results | the NOT tail or a long phrase is too narrow | drop the tail; shorter phrases; plain fallback |
| bare asks with no signal | snippet cut off, or vague posts | open the full post before judging; more family 6 |

If under 5 % of judged posts are accepted for two runs in a row, change the family order next run and note it in
**Runs** (`Supply note`).

## Where to search on LinkedIn

1. **Posts search** — the main source (settings in rule 6). Note author, headline, company, profile URL, post URL, age
   and comment count.
2. **LinkedIn Services requests** — if Vintoria's Service Page is set up, check its proposal requests every run.
3. **Groups** the account has joined (founders, startups, D2C, SaaS, real estate), sorted by recent, the same packs.
4. **Comments under "recommend an agency" posts** — most commenters are agencies pitching; keep only a commenter who
   states their **own** need ("we need this too for our store").

## Which market, which hour (24/7 rotation)

| IST | Daytime in | Run first |
|---|---|---|
| 03:30-08:59 | Australia | packs + "Australia", "Sydney", "Melbourne" on the first query of the window |
| 09:00-13:29 | India | Hinglish pack (family 10); "India" / city on the first query |
| 13:30-18:29 | India + UK | "UK", "London" on the first query |
| 18:30-23:59 | US East + UK | "US", "New York" on the first query |
| 00:00-03:29 | US | plain packs |

Add a place word only to the **first** query of a window (it narrows results a lot); every other query runs without one.
Sydney is 4.5-5.5 hours ahead of IST depending on daylight saving.

**Lane rotation:** hour of the day mod 8 → 0 web & e-commerce · 1 apps, SaaS & AI · 2 marketplaces & quick commerce ·
3 SEO, AEO & GEO · 4 paid ads (Meta, Google) · 5 social media & content · 6 CRO, landing pages & retention (email /
WhatsApp) · 7 branding, design & motion-graphics videos.

## Open the search directly

Replace `<q>` with the URL-encoded query (space → `%20`, `"` → `%22`, `(` → `%28`, `)` → `%29`):

`https://www.linkedin.com/search/results/content/?keywords=<q>&datePosted=%22past-24h%22&sortBy=%22date_posted%22`

If LinkedIn ignores a URL filter, set **Posts → Latest → Past 24 hours** by hand. Always confirm the age on the post
itself (`../../vintoria-sales/references/lead-quality.md`).

## Skip
- Agencies and freelancers advertising, job ads, job seekers, advice posts — the prefilter (`prefilter.md`) removes them.
- "Freelancer only / intern / student, small budget" — they don't want an agency.
- People asking which agency to **join** (career questions).
- Posts where the author already chose ("found our agency, thanks").

## Keep what works
Every lead keeps its `source` in **Leads** (`li:f1-marketing`, `li:f6-task-shopify`, `li:rotation-173`). Each Monday
`vintoria-report` counts replies, calls and wins per family and service: run the winners first, drop the rest.
