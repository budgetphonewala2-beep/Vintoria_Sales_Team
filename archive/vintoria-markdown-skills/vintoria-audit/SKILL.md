---
name: vintoria-audit
description: "Produces a fact-only, dated proof-of-work website audit for one VINTORIA prospect and writes workspace/prospects/<slug>/SITE-AUDIT.md as a table of measured facts, exact evidence, where observed, severity and the catalog service each row supports, drawn from the 270 VINTORIA services across 12 disciplines. Use when the user says 'audit this site', 'find what is broken on their website', 'proof of work for this lead', 'site audit before outreach', 'check their SEO and checkout', 'audit kar do iska website', 'website ki problem batao', or 'turn this into a hook for the email'."
---

# VINTORIA Site Audit

Turn one prospect's public web presence into a dated, evidence-only audit the seller can use as proof of work and as the source of outreach hooks.

## When to use / When not to use

Use when:
- A prospect folder exists in `workspace/prospects/<slug>/` and proof of work is needed before outreach.
- The seller asks what is slow, broken, missing or risky on a prospect's site, store, app, docs or help centre.
- `DOSSIER.md` has generic hooks and needs concrete, checkable ones.

Do not use when:
- The prospect is not identified. Run `vintoria-hunt` or `vintoria-research` first.
- The request needs logged-in access, admin panels, payment flows or private analytics. This skill reads public pages only.
- The seller wants a penetration test, a legal opinion or a paid technical assessment.
- The site shows nothing without an account. Record that in one line and stop.

## Inputs needed (and what to do if missing)

| Input | Use | If missing |
|---|---|---|
| `slug` and domain | folder path, all evidence URLs | Ask for the domain; never guess a company |
| `DOSSIER.md` or `BRIEF.md` | plausible disciplines, buyer context | Read the site briefly, note the gap, continue |
| Country and market | language, currency, local checks | Mark `Not found`; skip market-specific checks |
| `SELLER-PROFILE.md` | not needed for the audit | Continue; the audit cites services, not proof |
| Audit date | every row carries a date | Use today's date |

Read first: `../vintoria/references/truth-rules.md`, `../vintoria/references/quality-bar.md`, `../vintoria/references/service-catalog.md`, and each tested discipline under `../vintoria/references/services/`.

## Workflow

1. Confirm domain, slug, country and the 2-4 plausible disciplines. Write them at the top of a scratch list.
2. Read `robots.txt` and the sitemap first. Record the URL, the allow and disallow rules, sitemap present or absent.
3. Fetch the homepage, then 6-10 high-value pages: pricing, product, checkout start, contact, about, docs or help, blog index, legal pages, store listing.
4. Run the checklists in at least three disciplines. If those produce fewer than 10 verified rows, add two more disciplines before calling the site clean.
5. Record one row per finding: a measured fact, not an opinion. Exact text, count, status code, measured value or file name.
6. Test only as a logged-out visitor. Never create an account, submit a writing form, place an order, reset a real password, scan ports or load-test.
7. Hedge every consequence. "So phone visitors may see the desktop layout" is allowed. "This is costing you 40% of sales" is not.
8. Score with the local rubric. Below 75, fix the rows and rescore before showing anyone.
9. Choose exactly three hooks using the rules below and mark them `HOOK 1` to `HOOK 3`.
10. Write `SITE-AUDIT.md` in the exact template. Do not start outreach in the same pass.

Decision rules:
- Under 10 verified rows after five disciplines: mark the audit `Not ready`, name what was blocked, hand back to research.
- Seen once and not reproduced on a second load: label `single observation`, drop severity one level.
- Two pages disagree: record both rows with both URLs, state the disagreement, lower severity.
- A page returns 403, 429 or a bot challenge: record that and do not describe its contents.
- A page sits behind a login or a cookie wall you cannot dismiss: `Not found`.

## Public testing and robots rules

- Respect `Disallow`. Never fetch a disallowed path to prove a point. A blocked revenue section is itself a valid SEO row.
- One request per page per audit. No loops, no fuzzing, no load testing, no port scans.
- Public data only: the site, its sitemap, public store listings, public docs, public ad library, public business profile.
- No personal data. Never record an employee name, email or phone number anywhere in the audit.
- No screenshots you did not take. Never describe an image you cannot attach or save.

## What not to report

| Do not report | Why |
|---|---|
| Certificate or TLS errors on your own machine, proxy or clock | Machine fault, not their site |
| Pages behind a login you never saw | Unverified |
| Bot-blocked or rate-limited pages | Not observed |
| Anything from a search snippet alone | Snippet tier; open the page |
| Traffic, revenue, conversion or churn estimates | Unmeasured |
| Theme, plugin or server versions you cannot read in source | Guessed |
| Broken things you did not reproduce | Unverified |
| Competitor comparisons with no saved source | Unsupported |
| "Studies show", "users expect", industry averages | Invented benchmark |
| Any promise that the fix produces a result | Guarantee |

## Hedging: measured fact versus consequence

| Measured fact (write as is) | Consequence (must be hedged) |
|---|---|
| No viewport meta tag in page source | Phone visitors may see the desktop layout |
| Homepage largest image is 1.4 MB | The first screen likely loads slowly on mobile data |
| 11 H1 tags on the homepage | Crawlers may see several competing page topics |
| Checkout requires 9 fields, no guest option | Some buyers may abandon before payment |
| `robots.txt` disallows `/collections/` | Collection pages may be excluded from organic results |
| Blog newest post dated 2021 | The site may read as inactive to a first-time buyer |

Never write a hedge as a fact ("this is why sales are down") and never write a fact as a hedge ("there might be no viewport tag").

## Severity and hook selection

| Level | Use when |
|---|---|
| Blocker | A revenue, checkout, signup or contact path visibly fails |
| High | A core page or flow is missing, broken or unreachable |
| Medium | A measurable gap that likely affects trust, speed or discovery |
| Low | A polish issue with a small but clear effect |
| Observation | A fact worth quoting with no clear effect |

Hook rules, exactly three: one URL proves it and the buyer can open it in ten seconds; it maps to a catalog service you actively sell; the buyer would recognise it as costing money, time or credibility; not all three from one discipline; never the lowest row when a higher one exists.

## Per-discipline checklists

Tick every check in a row you test. All six are required per discipline.

| Discipline | Six checks (record the exact count, text, status or value for each) | Services |
|---|---|---|
| Web and UX | [ ] H1 count and each text on homepage; [ ] viewport tag present and 390px layout breaks; [ ] primary call to action followed to end state and step count; [ ] nav links returning 404 or leading to PDFs; [ ] contact form fields, validation, success state; [ ] footer copyright year versus current year | 016, 019, 039, 097 |
| E-commerce | [ ] one product from listing to order confirmation, steps and required fields; [ ] guest checkout present or absent; [ ] payment methods shown, wallet or local gap; [ ] product, price and availability structured data in source; [ ] stock level on collection versus product page, same item and time; [ ] returns and shipping pages exist, last-updated date | 191, 196, 200, 201, 206 |
| SEO | [ ] robots.txt read, revenue section blocked; [ ] sitemap fetched, 20 URLs sampled, every non-200 listed; [ ] titles and meta descriptions on 10 pages, missing or duplicate or truncated; [ ] canonical tags on filtered and paginated collections; [ ] structured data types on homepage, product and article; [ ] blog newest and oldest dates, gap in months | 212, 213, 216, 267 |
| SaaS and product | [ ] signup steps to first value and every required field; [ ] pricing dimensions: seats, usage, features, limits; [ ] changelog most recent dated entry; [ ] docs: API version, deprecation policy, rate limits; [ ] trust page: SSO, roles, audit logs, encryption; [ ] password reset completes or names support | 041, 047, 049, 053 |
| AI | [ ] every public AI claim quoted, live feature reachable or not; [ ] support flow steps to reach a human; [ ] help centre article count, update dates, search present; [ ] five real questions through public search, relevant article or not; [ ] privacy policy AI or model-processing language with date; [ ] chat widget response time on three attempts | 123, 124, 134, 145 |
| Automation | [ ] lead form to stated response promise, steps and time; [ ] every form and its fields, data duplicated across forms; [ ] systems named on integration or docs pages; [ ] help centre articles ending in "email support"; [ ] channels offered and published flow per channel; [ ] status entries attributed to sync failures | 146, 148, 154, 157 |
| Mobile | [ ] store listing last update date and version notes; [ ] 20 recent reviews: crashes, login, loading, with dates; [ ] minimum OS version per listing; [ ] tablet screenshots present, layout adapts or not; [ ] Android permissions and iOS privacy labels; [ ] mobile site: responsive, wrapper or neither | 061, 063, 064, 080 |
| Branding | [ ] logo files from header, favicon, app icon, social avatar, matching or not; [ ] font families and weights across five pages; [ ] palette hex values from site, deck, social, where they diverge; [ ] public brand or press kit and its contents; [ ] hero, about and meta description positions; [ ] logo at favicon size and in single colour | 103, 106, 107, 115 |
| Backend and performance | [ ] homepage weight, request count, largest image file; [ ] TTFB and status from two fetches; [ ] headers: HSTS, CSP, content-type protections; [ ] public admin, staging or database ports reachable, exact hostname; [ ] third-party script hosts on homepage and login page; [ ] mixed content and HTTP to HTTPS redirect | 168, 179, 186, 261, 262 |
| Analytics and growth | [ ] analytics and tag manager in source, owner field if shown; [ ] key action instrumented, event seen in network panel; [ ] privacy notice mentions analytics and consent; [ ] Core Web Vitals on three URLs, values and tool; [ ] ad or social message versus landing headline; [ ] referral or loyalty link resolves, destination recorded | 246, 249, 251, 253 |

## Output format

Write to `workspace/prospects/<slug>/SITE-AUDIT.md`:

```markdown
# Site audit: <company>

Domain: <domain> | Country: <country> | Audited: <YYYY-MM-DD> | Boundary: public pages only
Disciplines tested: <list> | Rows: <n> | Score: <n>/100

## Top three hooks
| # | Hook | Evidence URL | Serves |
|---|---|---|---|
| HOOK 1 | <one measured sentence> | <url> | <ID Name> |
| HOOK 2 | <one measured sentence> | <url> | <ID Name> |
| HOOK 3 | <one measured sentence> | <url> | <ID Name> |

## Findings
| # | Statement (measured fact) | Exact evidence | Where observed | Severity | Service |
|---|---|---|---|---|---|
| 1 | <measured fact> | <quoted text, count, status, value> | <url> (<date>) | Blocker | <ID Name> |

## Hedged consequences
- <finding #>: <may / likely / from the page alone>

## Not tested or not found
- <path>: <login required | disallowed by robots | blocked | not present>

## Evidence index
| Ref | URL | Fetched |
|---|---|---|
| E1 | <url> | <YYYY-MM-DD> |
```

## Quality gates (before showing anything)

| Gate | Floor |
|---|---|
| Verified rows | at least 10 |
| Disciplines tested | at least 3 |
| Rows with a dated URL | 100 per cent |
| Rows citing an exact catalog ID and name | 100 per cent |
| Unhedged consequence claims | 0 |
| Invented benchmarks, "studies show", guarantees | 0 |
| Hooks | exactly 3, one URL each, no duplicate discipline |
| Local score | 75 or above |
| Personal data recorded | 0 |

Local score: Evidence 40, Specificity 25, Service mapping 20, Hedge discipline 15. Score deterministically, print the score and the one-line fix, never round up.

## Failure handling

- **No web access.** Write the skeleton with `Not found` in every evidence cell, list the blocked pages, and state the audit is unverified. Never infer from memory.
- **Missing profile or dossier.** Continue from the site alone, mark hook relevance as inferred, say so in one line.
- **Ambiguous request** ("look at this company"). Ask which site, which market and whether the goal is proof of work or SEO. With no answer, default to Web, SEO and Performance.
- **Site behind a login or bot wall.** Record it as the finding, stop, and suggest `vintoria-research` or a discovery call.
- **One page loads inconsistently.** Re-fetch once, record both results, label `single observation`, drop severity.

## Definition of done

- [ ] `SITE-AUDIT.md` exists with 10 or more dated, sourced rows.
- [ ] Every row names one exact catalog service by ID and name.
- [ ] Three hooks chosen, one evidence URL each.
- [ ] Consequences hedged; no invented benchmark, metric or promise.
- [ ] Blocked and untested paths listed, not guessed.
- [ ] Local score 75 or above, printed at the top with the fixes.
- [ ] `HISTORY.md` and `pipeline.csv` updated; nothing marked sent or verified.

## Example (illustrative)

Company `harborline.example`, a fictional outdoor gear store. Audited 2026-03-04, Web, E-commerce and Performance tested, 12 rows, score 84.

| Statement | Exact evidence | Where observed | Severity | Service |
|---|---|---|---|---|
| No viewport meta tag in page source | no `name="viewport"` element in `<head>` | harborline.example (2026-03-04) | High | 039 Frontend Development |
| Checkout requires an account | "Create an account to continue"; no guest link | harborline.example/checkout (2026-03-04) | Blocker | 200 Checkout Development |
| Homepage hero image is 1.4 MB | `hero-fallback.jpg`, 1,432,910 bytes | harborline.example (2026-03-04) | Medium | 262 Core Web Vitals Optimization |
| Product pages carry no structured data | no `application/ld+json` Product or Offer block | harborline.example/products/ridge-pack (2026-03-04) | Medium | 213 Technical SEO |

Hooks: the guest checkout block (HOOK 1, 200), the missing viewport (HOOK 2, 039), the 1.4 MB hero (HOOK 3, 262). Hedge written as "so some phone buyers may hit a fixed desktop layout and a required account before payment". Not reported: a certificate warning seen on the auditor's own laptop, because a clean second fetch returned a valid certificate.
