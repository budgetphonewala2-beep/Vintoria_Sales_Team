---
name: vintoria-hunt
description: "Finds in-market buyers for VINTORIA's 270 services across LinkedIn, X, Reddit, Hacker News, Facebook groups, Google and X-ray search, job boards, Product Hunt, Google Maps, app stores, review sites, marketplaces and people search, then adds scored rows to workspace/pipeline/pipeline.csv. Includes exact query patterns per discipline, boolean limits, recency filters, market handling for US, UK, CA, AU, EU and India, hard filters against sellers, job seekers and competitors, dedupe rules and a 10-a-day cap. Use for 'find leads', 'hunt prospects', 'find people asking for a website', 'who is hiring Next.js developers', 'find SEO clients', 'add 10 prospects', 'daily hunting', or Hinglish like 'clients dhundo'."
---

# VINTORIA Hunter

Finds people publicly showing a buying signal for one of our services, scores them against the ICP, and appends at most 10 clean rows to the pipeline.

## When to use / When not to use

| Use it when | Do not use it when |
|---|---|
| The pipeline needs new prospects and `ICP.md` exists | `ICP.md` is missing or stale (run `vintoria-icp` first) |
| The seller asks for leads in a named discipline or market | A company is already known and needs depth (use `vintoria-research`) |
| Someone asks who is hiring, asking or complaining publicly | The user wants outreach written (use `vintoria-outreach`) |
| A segment needs refilling after review | The user wants a website audit (use `vintoria-audit`) |
| The daily routine calls for prospecting | The user wants to email or DM anyone (this skill never sends) |

## Inputs needed (and what to do if missing)

| Input | Source | If missing |
|---|---|---|
| Segments, signals, scoring rubric | `workspace/icp/ICP.md` | Stop and run `vintoria-icp`, or use a provisional segment and say so. |
| Active lanes and service IDs | `workspace/profile/OFFER.md` | Use catalog IDs for the chosen discipline and note the gap. |
| Existing rows | `workspace/pipeline/pipeline.csv` | Create it with the exact header from `../vintoria/references/pipeline-format.md`. |
| Suppressions | `workspace/pipeline/suppressions.md` | Create an empty file with a one-line header. |
| Language and market limits | `SELLER-PROFILE.md` | Default to the markets listed in the ICP. |
| Today's count | `workspace/pipeline/daily-log/YYYY-MM-DD.md` | Treat as 0 and create the file. |

Read `../vintoria/references/compliance.md` before the first search. No purchased lists, no scraped contact dumps, no bulk social messaging.

## Workflow

1. Read the ICP, the offer, the pipeline and today's log. Note how many prospects were already added today.
2. Choose the hunt target. Rules:
   - One or two disciplines per session, never more.
   - Prefer the segment with the best reply rate; if there is no data, use segment 1.
   - If the user named a discipline, use it even if it is dormant, and flag that the offer does not support outreach.
3. Build 6 to 10 queries from the discipline patterns below, mixing at least three sources.
4. Run the sources in the order listed in the source table. Stop when you have 25 raw candidates or 45 minutes of searching, whichever comes first.
5. Apply the recency window per source. Anything older is dropped, not scored.
6. Open every candidate page. A search snippet alone is never enough.
7. Apply the hard filters. Reject on the first match and record the reason code.
8. Dedupe against the pipeline, suppressions and `workspace/prospects/`. Update instead of adding where a person already exists.
9. Verify the buying signal on the page: quote it, date it, save the URL. No verified signal, no row.
10. Score with the ICP rubric. Cap at 74 until a dossier exists; cap at 55 if the only evidence was a snippet. Add only rows at 60 or above.
11. Rank by score, then by signal recency. Keep the top 10 minus what was already added today.
12. Append rows to `pipeline.csv` with `stage=new` and `next_action=build dossier`. Update the daily log with what was searched, added, rejected and why.
13. Report the candidate table, the count added and the next action per row. Never contact anyone.

### Sources and recency

| Source | Surfaces | Query shape | Recency |
|---|---|---|---|
| LinkedIn posts | public asks, launches, role changes | keyword on Posts tab, past week | 7 days |
| X | complaints, build-in-public asks | keyword plus `anyone` or `recommend` | 7 days |
| Reddit | buying questions in niche subreddits | `site:reddit.com "recommend" keyword` sorted new | 30 days |
| Hacker News | technical asks and gaps | Algolia search, `Ask HN` plus keyword | 14 days |
| Facebook groups | local and trade buyers | group search, keyword plus `anyone know` | 14 days |
| Google and X-ray | companies with a visible gap | `site:` plus `careers` plus keyword | none |
| Job boards | hiring means budget and pain | role keyword, posted last 14 days | 14 days |
| Product Hunt | new launches needing build work | launch comments asking who built it | 30 days |
| Google Maps | local firms with missing or dated sites | category plus city, check website field | none |
| App stores | review complaints | newest first, 1 to 3 star | 30 days |
| Review sites | G2, Capterra, Trustpilot complaints | keyword in reviews | 90 days |
| Marketplaces | public project briefs | brief keyword matching a service | 7 days |
| People search | title, size and geography | LinkedIn or Apollo-style filters, manual review | none |

### Query patterns by discipline (use 3 or more)

| Discipline | Patterns |
|---|---|
| 01 Strategy | `("looking for" OR "need help with") ("product strategy" OR "MVP strategy") -job -hiring` ; `"digital transformation" ("consultant" OR "partner") ("stalled" OR "roadmap") -jobs` ; `site:linkedin.com/posts ("product discovery" OR "roadmap") ("recommend" OR "advice")` |
| 02 Web | `("rebuild our website" OR "website redesign") ("agency" OR "developer") -job -salary` ; `("Next.js" OR "headless CMS") ("migration" OR "rebuild") ("our site")` ; `("client portal" OR "booking platform") ("we need" OR "build for us") -tutorial` |
| 03 SaaS | `("SaaS MVP" OR "multi-tenant") ("build" OR "help") -jobs -course` ; `("subscription billing" OR "plan changes") ("Stripe" OR "Paddle") ("broken" OR "migrate")` ; `site:news.ycombinator.com ("multi-tenant" OR "billing") ("how did you" OR "advice")` |
| 04 Mobile | `("React Native" OR "Flutter") ("rescue" OR "rebuild" OR "maintenance") -job -salary` ; `("app store" ("rejected" OR "crashes")) ("our app") -course` ; `("iOS app" OR "Android app") ("development partner" OR "quote") -job` |
| 05 UI/UX | `("UX audit" OR "design system") ("need" OR "looking for") -jobs -course` ; `("our dashboard" OR "our portal") ("confusing" OR "hard to use")` ; `("Figma" OR "design handoff") ("developers" AND ("mismatch" OR "rebuild"))` |
| 06 Branding | `("rebrand" OR "brand identity") ("launching" OR "raising" OR "merger") -jobs` ; `("our logo" OR "brand guidelines") ("inconsistent" OR "refresh")` ; `("pitch deck" OR "investor deck") ("design" OR "redesign") ("founder" OR "startup")` |
| 07 AI | `("RAG" OR "LLM") ("pilot" OR "production") ("we need" OR "help") -jobs -course` ; `("AI chatbot" OR "AI agent") ("custom" OR "support tickets")` ; `("OpenAI API" OR "vector database") ("accuracy" OR "scaling") ("issue" OR "advice")` |
| 08 Automation | `("Zapier" OR "Make.com" OR "n8n") ("broke" OR "replace" OR "scale")` ; `("manual data entry" OR "copy paste") ("systems" OR "spreadsheets") -jobs` ; `("CRM automation" OR "invoice automation") ("need" OR "recommend") -course` |
| 09 Backend | `("API documentation" OR "API versioning") ("partners" OR "customers") ("missing" OR "bad")` ; `("cloud migration" OR "AWS costs") ("downtime" OR "bill") ("help" OR "advice")` ; `("CI/CD" OR "DevOps") ("set up" OR "audit") ("we need") -jobs` |
| 10 E-Commerce | `("Shopify" OR "WooCommerce") ("migration" OR "replatform") ("store" OR "brand") -jobs` ; `("checkout" AND ("abandonment" OR "drop-off")) ("our store")` ; `("headless commerce" OR "subscription commerce") ("build" OR "move to") -course` |
| 11 Marketing | `("technical SEO" OR "local SEO") ("audit" OR "help") ("traffic dropped")` ; `("Google Ads" OR "Meta Ads") ("wasted spend" OR "no leads") -course` ; `("keyword research" OR "content strategy") ("B2B" OR "SaaS") ("need" OR "recommend") -jobs` |
| 12 Growth | `("conversion rate" OR "activation rate") ("drop-off" OR "stuck") ("signup" OR "funnel")` ; `("A/B testing" OR "experiment programme") ("set up" OR "need") -course -jobs` ; `("Core Web Vitals" OR "analytics implementation") ("failing" OR "broken")` |

### Boolean rules

- LinkedIn: 5 operators maximum across the whole query, 500 characters maximum, no wildcards, no parentheses (flatten them), no `site:` operator.
- Google: quotes for exact phrases, uppercase `OR`, parentheses allowed, at most 4 `OR` groups, one minus per excluded idea.
- X: 3 operators maximum, quotes work, no `since:` inside a quoted phrase.
- Reddit and Hacker News: use site or Algolia scoping first, then keywords, then sort by new.
- Every query carries the exclusion block: `-job -jobs -hiring -salary -course -tutorial -intern -free`.
- Never search for contact dumps, email lists, leaked data or "database of leads".

### Market handling

| Market | Query and wording | Notes |
|---|---|---|
| United States | English, state or metro name, `zip`, `Series A`, `DTC`, `SMB` | Public sector and health need a compliance owner before adding |
| United Kingdom | English with `-ise` spelling, `postcode`, `SME`, `Ltd`, `sole trader` | PECR: business address, identify yourself, opt-out |
| Canada | English, `GST/HST`, `CAD`, city names; French for Quebec | CASL: record the basis for contact |
| Australia | English with `-ise` spelling, `AUD`, `ABN`, city names | Spam Act: inferred consent from a public business page |
| EU | Search in the local language first, then English | GDPR: business data only, state the purpose, minimal fields |
| India | English plus Hinglish terms such as `website banwana hai` | DPDP: business data only, no personal numbers, no price talk |

Record the market in `country` as an ISO code plus region where useful. Never mix languages inside one query.

### Hard filters (reject on first match)

| Code | Reject when |
|---|---|
| SELLER | Bio or page sells the same work: web design, development, SEO, branding, automation agency, freelance developer |
| SEEKER | "open to work", "looking for a role", "hire me", CV or portfolio post |
| JOBAD | The post is a company advertising a vacancy |
| STUDENT | Student, bootcamp, intern, final-year project, learning exercise |
| COMPETITOR | Named agency, dev shop or catalog-equivalent studio |
| RECRUITER | Recruiter, lead-gen vendor, list seller |
| MARKET | Country or language outside the ICP or the seller's stated ability |
| REGULATED | Health, finance, legal or child-directed with no compliance owner |
| NOCHANNEL | Personal address only, or no lawful business contact route |
| DUPLICATE | Domain or person already in the pipeline |

### Dedupe

- Normalise: lowercase, strip protocol, `www`, trailing slash and path. `slug` = domain.
- Person key = lowercase full name plus `@` plus domain.
- Check `pipeline.csv`, `suppressions.md` and `workspace/prospects/` before writing.
- Existing person: update the row, never add a second.
- Existing domain, new person: add the person, note the link in `HISTORY.md`.
- Same company found on two platforms: one row, keep the earliest source and log the second.

## Output format

```markdown
## Hunt run YYYY-MM-DD
Segment: <name> | Discipline: <number and name> | Added today before this run: N

| # | Company | Contact | Title | Country | Services | Score | Band | Source | Why now (quoted, dated) | Next action |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 |  |  |  |  | 121,146 | 78 | A | linkedin.com/posts/... | "<quote>" 2026-11-02 | build dossier by 2026-11-16 |

Added: N of 10 | Rejected: N (codes) | Duplicates skipped: N | Sources searched: ...
Next: <one line, what the researcher should take first>
```

`pipeline.csv` header, exactly:

```csv
slug,company,contact_name,title,email,email_status,country,services,stage,score,next_action,next_due,owner,source,updated
```

Field rules: `stage=new`; `services` is 1 to 3 IDs, comma separated, never names; no email found means blank `email` with `email_status=unverified` and never a guessed pattern; `score` is an integer 60 to 74 at this stage; `next_due` is a real date within 3 working days; `owner` is the hunter; `source` is platform plus a short reference.

## Quality gates

| Gate | Floor |
|---|---|
| New rows this run | 10 maximum including earlier runs today |
| Verified trigger | 100 percent of rows, opened and dated this session |
| Source URL | 100 percent of rows |
| Hard-filter matches | 0 |
| Duplicates | 0 |
| Score | 60 or above on every added row |
| Disciplines per session | 2 maximum |
| Top-segment share | 5 or more of 10 from segment 1 |
| Email accuracy claims | 0 verified claims unless a tool actually verified it |
| Messages sent | 0, always |

Below the floor: do not append the weak rows. Report how many were found, how many passed, and which filter removed the rest.

## Failure handling

- **No web access.** Say so plainly, report 0 added, and do not reconstruct leads from memory.
- **A source is blocked or logged out.** Skip it, name it in the report, continue with the others.
- **ICP missing.** Run `vintoria-icp` or use a provisional segment and label every row `provisional`.
- **Results are all sellers and agencies.** Tighten with `-agency -studio -freelance` and switch source, do not lower the bar.
- **Ambiguous request.** Ask for one discipline and one market, or default to segment 1 and one discipline, and state the assumption.
- **Cap already reached.** Add nothing, list the best 5 candidates as a watchlist in the daily log for tomorrow.

## Definition of done

- [ ] Segment and discipline stated, with the reasoning in one line.
- [ ] At least three sources searched, with counts.
- [ ] Every added row has an opened, dated source and one quoted signal.
- [ ] All hard filters applied; rejection codes recorded.
- [ ] Dedupe run against pipeline, suppressions and prospect folders.
- [ ] `pipeline.csv` rows use the exact header; `stage=new`; score 60 to 74.
- [ ] Daily log updated, and the report shows the count added plus one next action per row.
- [ ] Zero messages, emails, DMs or connection requests sent.
