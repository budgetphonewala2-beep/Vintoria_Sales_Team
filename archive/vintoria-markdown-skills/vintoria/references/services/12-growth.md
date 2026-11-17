# 12 / Growth, Analytics & Continuous Development — 34 services

> Catalog scope template: "Growth, analytics, optimization or continuous-development work focused on {service}, with measurement and actionable improvement where applicable."

## Services

| ID | Service |
|---|---|
| 237 | Growth Strategy |
| 238 | Growth Experiments |
| 239 | Funnel Optimization |
| 240 | Landing Page Optimization |
| 241 | Conversion Optimization |
| 242 | Lead Funnel Development |
| 243 | Customer Acquisition Strategy |
| 244 | Customer Retention Strategy |
| 245 | Referral Systems |
| 246 | Analytics Implementation |
| 247 | Product Analytics |
| 248 | Marketing Analytics |
| 249 | A/B Testing |
| 250 | Growth Automation |
| 251 | Conversion Tracking |
| 252 | Event Tracking |
| 253 | Business Intelligence |
| 254 | Custom Analytics Dashboards |
| 255 | Data Visualization |
| 256 | Marketing Attribution |
| 257 | Website Maintenance |
| 258 | SaaS Maintenance |
| 259 | App Maintenance |
| 260 | Bug Fixing |
| 261 | Performance Optimization |
| 262 | Core Web Vitals Optimization |
| 263 | Security Updates |
| 264 | Technical Audits |
| 265 | UX Audits |
| 266 | Conversion Audits |
| 267 | SEO Audits |
| 268 | Code Refactoring |
| 269 | Infrastructure Optimization |
| 270 | Continuous Development |

## Who buys this (segments)

- **SaaS team with flat activation.** Buying product analytics, event tracking and funnel experiments. Trigger: a signup-to-paid gap the team cannot explain.
- **App team with installs but weak retention.** Buying product analytics, retention strategy and UX audits. Trigger: a release that did not move the retention number.
- **Store with traffic and low conversion.** Buying conversion audits, A/B testing and landing page optimisation. Trigger: a new head of e-commerce or a missed quarter.
- **Services firm with no measurement.** Buying analytics implementation, conversion tracking and dashboards. Trigger: a board request for a single source of truth.
- **Post-funding scale-up under a growth target.** Buying growth strategy, experiments and attribution. Trigger: an investor commitment or a new growth lead.
- **Marketplace balancing two sides.** Buying acquisition, retention and referral systems. Trigger: one side of the market outpacing the other.
- **Company after a redesign that lost performance.** Buying core web vitals, performance optimisation and technical audits. Trigger: a post-launch traffic or speed complaint.
- **Product owner without an internal engineering team.** Buying maintenance, bug fixing and continuous development. Trigger: an unstaffed backlog or an expiring support contract.

## Buying signals (observable)

1. Pricing page exists but no trial or signup action appears above the fold (241, 239).
2. Analytics script is present yet no event calls or tag manager are visible in the source (246, 252).
3. Marketing copy cites outcomes with no linked case page or source (247, 253).
4. Core Web Vitals fail when the public URL is tested this session (262, 261).
5. Distinct ad URLs point to the same undifferentiated landing page (240, 249).
6. App store reviews describe onboarding confusion or a broken first session (265, 241).
7. Changelog shows releases but no experiment or measurement notes (238, 270).
8. Careers page lists a growth, analytics or CRO role (237, 249).
9. Cookie banner blocks client tracking and no server-side option is described (251, 256).
10. Site navigation or footer links return errors on a sample check (257, 260).
11. Security headers are missing or the copyright line shows an older year (263, 264).
12. Paid or social ads land on the homepage instead of a matching page (240, 242).
13. A referral or loyalty programme is mentioned but its page returns an error (245).
14. A BI tool is named in a job ad while no data role is listed (253, 254).

## Discovery questions

1. Which single number does the board ask about, and where does it come from?
2. What event tells you a new user reached value?
3. Which funnel step loses the most people, and how is that measured?
4. Who changes the site today, and how long does a test take to ship?
5. What was the last experiment, and what did you conclude?
6. Which tools already collect data, and who owns each?
7. What is broken in production right now that nobody has time for?
8. If one improvement landed this quarter, which would it be?

## Proof-of-work audit angles

- Inspect the page source for analytics and tag management, and list every tool detected and its owner field if shown.
- Walk the signup or purchase path and record each step, field and observed failure.
- Record whether a distinct event fires on the key action using the browser network panel, and describe what was seen.
- Test three key URLs for Core Web Vitals and record the measured values and the tool used.
- Check every link in the header, footer and pricing page, and list each error with its URL.
- Compare the ad or social post message with the landing page headline and record the mismatch.
- Read the changelog and record whether entries name a measurable change.
- Check security headers and the copyright year, and list what is stale.
- Review the app store listing and record the onboarding steps described in recent reviews.
- Check whether a referral or loyalty link resolves, and record the destination.

## Deliverables (what the client receives)

- Measurement plan with event names, properties and owners
- Funnel map with each step and its current instrumentation
- Analytics implementation and validation checklist
- Experiment backlog with hypothesis, metric and stop rule
- Dashboard specification with definitions per metric
- Audit findings register with severity and reproduction steps
- Maintenance plan with a prioritised defect list
- Continuous development backlog ordered by user impact

## Common objections

| Objection | Real concern | One-line reframe | Evidence needed |
|---|---|---|---|
| We already have analytics | Duplicate tooling and cost | Audit what fires today, keep only what is used | Detection list showing which events actually fire |
| Experiments are too slow to matter | Throughput and engineering time | Ship changes that need no test, then sequence the rest | Backlog split into ship-now and test-later items |
| Maintenance is boring spend | Perceived lack of growth value | Defects and speed are the first conversion levers | Findings register with before values |
| We cannot send user data to a third party | Privacy and legal exposure | Define what is collected and who can read it before adding tags | Data map with lawful basis fields for their counsel |
| Our team can do this internally | Ownership and knowledge transfer | The runbook and definitions let the team take over | The handover section of the plan |

## Do not sell when

- No one can name the number the business is trying to move.
- Analytics access, site access or app console access is refused entirely.
- The buyer wants a guaranteed uplift or a fixed revenue promise.
- The product has no traffic or users yet; strategy work comes first.
- The request is a redesign with no measurement or acceptance criteria.
- A test would need a sample the site cannot reach within the buying cycle.
- The work would require accessing personal data without a lawful basis confirmed by the client.
