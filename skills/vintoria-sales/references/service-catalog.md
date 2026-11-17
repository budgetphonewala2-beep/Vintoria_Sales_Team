# VINTORIA Service Catalog — canonical reference

Source: `VINTORIA_270_Services_SERVICE_ONLY_2026.pdf` (service-only; no pricing, packages or commercial terms).
This file is the naming authority. Never rename a service, never merge two services into one line, never invent a
service number, and never quote a price from this catalog.

## The 12 disciplines

| # | Discipline | Services | ID range | File |
|---|---|---|---|---|
| 01 | Strategy & Consulting | 15 | 001–015 | `services-01-strategy.md` |
| 02 | Web Development | 25 | 016–040 | `services-02-web.md` |
| 03 | SaaS & Digital Products | 20 | 041–060 | `services-03-saas.md` |
| 04 | Mobile App Development | 20 | 061–080 | `services-04-mobile.md` |
| 05 | UI/UX & Product Design | 22 | 081–102 | `services-05-design.md` |
| 06 | Branding & Creative | 18 | 103–120 | `services-06-branding.md` |
| 07 | AI Development | 25 | 121–145 | `services-07-ai.md` |
| 08 | Business Automation | 22 | 146–167 | `services-08-automation.md` |
| 09 | Backend, API & Cloud | 23 | 168–190 | `services-09-backend.md` |
| 10 | E-Commerce | 20 | 191–210 | `services-10-ecommerce.md` |
| 11 | Digital Marketing & SEO | 26 | 211–236 | `services-11-marketing.md` |
| 12 | Growth, Analytics & Continuous Development | 34 | 237–270 | `services-12-growth.md` |

**Total: 270 services.**

## How to cite a service

Always cite the exact ID and name from the discipline file:

```
121 AI Product Development
192 Shopify Development
249 A/B Testing
```

- In outreach: one to three services, named exactly, never a list dump.
- In proposals: grouped by discipline, each line with ID, name and a scope sentence.
- In the pipeline: `services` column holds IDs (`121,146`) and `service_names` holds names.

## Discipline map — what the catalog covers

- **01 Strategy & Consulting** — direction before build: discovery, feasibility, roadmap, MVP and GTM strategy.
- **02 Web Development** — marketing sites, portals, marketplaces, booking platforms, and modern front-end stacks.
- **03 SaaS & Digital Products** — multi-tenant product engineering, billing, auth, admin, migration, scaling.
- **04 Mobile App Development** — iOS, Android, cross-platform, industry apps, commerce apps, maintenance.
- **05 UI/UX & Product Design** — research, flows, design systems, audits, prototyping, handoff.
- **06 Branding & Creative** — strategy, identity, logo, guidelines, creative direction, brand experience.
- **07 AI Development** — AI products, chatbots, RAG, agents, copilots, document and voice AI, custom AI.
- **08 Business Automation** — CRM, lead, sales, marketing, ops, invoice, reporting and multi-system automation.
- **09 Backend, API & Cloud** — APIs, databases, auth, cloud architecture, DevOps, CI/CD, monitoring, hardening.
- **10 E-Commerce** — storefronts, checkout, payments, catalog, inventory, subscriptions, conversion.
- **11 Digital Marketing & SEO** — SEO (technical, local, programmatic, on/off-page), paid media, content, social.
- **12 Growth, Analytics & Continuous Development** — experiments, funnels, analytics, BI, audits, maintenance.

## Rules

1. The catalog is **service scope only**. It contains no price, SLA, timeline, team size, guarantee or client name.
2. Never state or imply a VINTORIA price, discount, delivery time or past result unless the seller's own
   `SELLER-PROFILE.json` (`python <SCRIPTS>/core/seller_profile.py show`) contains it verbatim.
3. Anything not in the catalog or the seller profile is `Not found` (research) or omitted (outreach).
4. If a buyer needs something outside the 270, say so plainly and name the closest covered services instead of
   inventing a new one.
