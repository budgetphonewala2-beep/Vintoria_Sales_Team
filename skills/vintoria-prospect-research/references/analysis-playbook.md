# vintoria-prospect-research — Playbook

> Web access: use your own browser and web search (LinkedIn and Reddit are logged in). Open the page before you state a
> fact from it, and note its URL and date. Never invent what you could not open — write "Not found".

## When This Skill Is Invoked

The user runs `vintoria-prospect-research` (<url>). This is the flagship command of the entire suite. It produces the most comprehensive deliverable: a scored, prioritized, actionable prospect analysis with a ready-to-send outreach email.

---

## Phase 1: Discovery (Sequential — Pre-Analysis)

Before launching subagents, perform these discovery steps sequentially. Every subsequent phase depends on this data.

### 1.1 Fetch the Target URL

Use `web fetch` to retrieve the company homepage. Store the full content for subagent consumption.

If the homepage loads successfully, also fetch up to 5 key interior pages:
- About / Company page
- Team / Leadership page
- Pricing page
- Blog / Resources page
- Careers / Jobs page
- Contact page

For each page, store:
- Page URL
- Page title
- Raw content (text)
- Key data points extracted (names, numbers, product details)

**If the URL is unreachable:**
1. Report the error to the user: "Could not reach [url] — HTTP [status code]"
2. Attempt alternate URLs: try with/without www, try https vs http
3. If still unreachable, suggest the user verify the URL and try again
4. Do NOT proceed to Phase 2 if zero pages are accessible

### 1.2 Detect Company Type

Classify the prospect into one of these categories. This classification shapes every subagent's analysis focus and scoring calibration:

| Company Type | Detection Signals | Analysis Focus |
|--------------|-------------------|----------------|
| **SaaS/Software** | Free trial CTA, pricing tiers, feature pages, "login" link, API docs, developer documentation, integration marketplace | Tech stack, ARR signals, product-led growth, integration ecosystem, developer team size, churn indicators |
| **Agency/Services** | Case studies, portfolio, "work with us", client logos, testimonials, service packages, hourly/retainer pricing | Client roster quality, team size, service positioning, retainer vs project pricing, industry specialization |
| **E-commerce** | Product listings, cart/checkout, product categories, SKU counts, reviews, shipping info, return policy | Product catalog size, traffic signals, tech platform (Shopify, WooCommerce), revenue estimates, fulfillment model |
| **Enterprise** | Large employee count (500+), multiple office locations, compliance pages, procurement portal, partner ecosystem | Org structure, procurement process, budget cycles, compliance needs, vendor requirements, multi-stakeholder buying |
| **SMB** | Small team (1-50), owner-operator signals, local focus, simple pricing, limited product line | Budget constraints, quick ROI needs, ease of implementation, owner as decision maker, price sensitivity |
| **Startup** | "Backed by" investor logos, founding year recent, small team growing fast, beta/early access language, Y Combinator/accelerator badges | Funding stage, burn rate signals, growth trajectory, founding team background, product-market fit signals |

**Detection procedure:**
1. Scan homepage for signals from each category
2. Check careers page for employee count and hiring velocity
3. Check pricing page for pricing model complexity
4. Look for investor/funding mentions
5. Assign the best-fit category (if ambiguous, note the two most likely categories)

### 1.3 Extract Key Pages and Site Architecture

Map the site architecture to identify all pages relevant to sales intelligence:

| Page Type | Common URLs | Data to Extract |
|-----------|-------------|-----------------|
| **Homepage** | / | Headline, value prop, CTAs, social proof, product positioning |
| **About** | /about, /company, /about-us | Founding story, mission, team size, locations, history |
| **Team** | /team, /leadership, /about/team, /people | Names, titles, photos, bios, LinkedIn links |
| **Pricing** | /pricing, /plans, /packages | Tiers, prices, features per tier, enterprise CTA |
| **Blog** | /blog, /resources, /insights, /news | Recent topics, posting frequency, content depth |
| **Careers** | /careers, /jobs, /join-us, /hiring | Open roles, team sizes by department, growth signals |
| **Contact** | /contact, /get-in-touch, /demo | Contact forms, phone numbers, office addresses |
| **Products** | /products, /features, /solutions, /platform | Product lines, features, use cases, integrations |
| **Customers** | /customers, /case-studies, /testimonials | Customer logos, case study details, industry verticals served |
| **Partners** | /partners, /integrations, /ecosystem | Technology partners, integration depth, ecosystem maturity |

### 1.4 Identify Industry Vertical

Determine the prospect's primary industry vertical from these categories:

- Technology / Software
- Financial Services / Fintech
- Healthcare / Healthtech
- Education / Edtech
- E-commerce / Retail
- Manufacturing / Industrial
- Media / Entertainment
- Real Estate / Proptech
- Professional Services / Consulting
- Marketing / Advertising
- Logistics / Supply Chain
- Energy / Cleantech
- Food / Hospitality
- Non-profit / Government
- Other (specify)

**Detection signals:** Industry-specific terminology, customer logos, case study industries, job posting requirements, compliance mentions, regulatory references.

### 1.5 Run Structured Data Extraction

Open the homepage, about, services/pricing, team, careers and contact pages yourself and note for each: what
they sell, who to, size signals, tech hints in the page (Shopify, WordPress, Wix…), hiring, and contact details.

**Treat what you find as leads, not facts** until the page itself shows it; if a site is JavaScript-only and shows
little text, use search results and other pages instead and say so.
