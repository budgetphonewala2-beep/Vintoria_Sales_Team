# Intent search queries

Run with `python <SCRIPTS>/intent_scan.py --serp --query '<query>' --lookback 7` (Bright Data key), or paste them
into your own search tool and save the results as posts for `--file`. `--list-queries` shows the defaults.

Google operators: `site:` limits to a platform, quotes force exact phrases, `OR` must be uppercase,
parentheses group. The scanner adds a recency filter (`--lookback` days). Keep each query focused — every
query is one paid call.

## By platform (English)
- LinkedIn posts: `site:linkedin.com/posts ("looking for" OR "need" OR "recommend") ("web developer" OR website OR "app developer")`
- LinkedIn, marketing: `site:linkedin.com/posts ("looking for" OR "need") ("marketing agency" OR "social media agency" OR "SEO agency")`
- Reddit: `site:reddit.com ("looking for" OR recommend OR "need help") (agency OR developer) (website OR app OR SEO)`
- Reddit, small business subs: `site:reddit.com/r/smallbusiness ("need a website" OR "recommend a web designer")`
- Facebook groups (public posts only): `site:facebook.com/groups ("need a website" OR "website banwana")`
- Quora: `site:quora.com ("best agency" OR "hire a developer") (website OR app) India`

## By service
- App: `("need an app" OR "build an app" OR "app developer") (startup OR business) -job -hiring`
- SEO: `("need SEO" OR "SEO agency" OR "rank on google") (clinic OR restaurant OR store OR business) -job`
- Design: `("need a logo" OR "branding agency" OR "brand identity") -"we offer" -hiring`
- Fix/redesign: `("redesign our website" OR "website is outdated" OR "fix our wordpress")`

## Hinglish / Hindi
- `"website banwana hai" OR "website banwani hai" OR "website chahiye"`
- `"developer chahiye" OR "koi developer batao" OR "app banwana hai"`
- `"seo karwana hai" OR "seo wala chahiye" OR "marketing agency chahiye"`
- `"वेबसाइट बनवानी है" OR "वेबसाइट चाहिए"`

## Tips
- Add a city or country to target markets: `... (Pune OR Mumbai OR Bangalore)` or `--country in`.
- Exclude noise with `-hiring -job -"we offer" -"our services"`.
- Save your best queries as JSON (`[{"id": "clinic-seo", "query": "..."}]`) and run `--queries my-queries.json`.
- Review `pipeline.py report` → `by_source` monthly and keep the queries that produce meetings.
