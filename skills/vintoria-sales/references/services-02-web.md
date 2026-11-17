# 02 / Web Development — 25 services
> Catalog scope template: "Design and engineering for {service}, covering the agreed interface, responsive behavior, integrations, quality assurance and production delivery."

## Services
| ID | Service |
|---|---|
| 016 | Corporate Website Development |
| 017 | Business Website Development |
| 018 | Startup Website Development |
| 019 | Landing Page Development |
| 020 | Marketing Website Development |
| 021 | Custom Website Development |
| 022 | Custom Web Application Development |
| 023 | Progressive Web App Development |
| 024 | Web Portal Development |
| 025 | Membership Website Development |
| 026 | Directory Platform Development |
| 027 | Marketplace Development |
| 028 | Booking Platform Development |
| 029 | Customer Portal Development |
| 030 | Client Portal Development |
| 031 | Internal Web Application Development |
| 032 | Interactive Website Development |
| 033 | High-Performance Website Development |
| 034 | Headless Website Development |
| 035 | Jamstack Development |
| 036 | Next.js Development |
| 037 | React Development |
| 038 | TypeScript Development |
| 039 | Frontend Development |
| 040 | Full-Stack Web Development |

## Who buys this (segments)
- **Company with a site older than its brand** - buying a rebuild that matches current positioning. Trigger: a rebrand, a new logo, or a sales team complaining the site loses credibility.
- **B2B firm with no enquiries from the site** - buying a marketing site that produces leads. Trigger: a paid campaign that spent budget and returned nothing measurable.
- **Multi-brand or multi-location operator** - buying one system that serves many brands or regions. Trigger: a new location, acquisition or franchise launch.
- **Association or professional body** - buying a membership site with gated content and renewals. Trigger: renewal season, or a forum and CMS that members describe as broken.
- **Marketplace or directory operator** - buying listing, search and transaction flows. Trigger: manual matching or a spreadsheet that no longer scales.
- **Service business that takes bookings** - buying a booking platform with live availability. Trigger: phone-only booking, double bookings, or no-shows.
- **Operations lead with a spreadsheet process** - buying an internal web application. Trigger: a second team needing the same tool, or an audit finding.
- **Startup preparing to launch or raise** - buying a launch site and a product one-pager. Trigger: a demo day, a fundraise or a public waitlist.

## Buying signals (observable)
1. Footer copyright year is older than the current year (016, 017).
2. Page source shows no viewport meta tag (033, 039).
3. Homepage loads an uncompressed image over one megabyte; record the file and size (033).
4. Site is served over plain HTTP or shows mixed-content warnings (021).
5. Navigation points to PDF files instead of pages (016, 021).
6. A "latest news" section shows posts older than twelve months (020).
7. Careers page hires a front-end developer while the site is still on the old stack (037, 039).
8. A booking flow exists but the only contact route is a telephone number or mailto link (028).
9. Login area exists but the password reset link is absent from the page (025, 029).
10. Sitemap lists pages that return 404; record each URL and status (021, 033).
11. A prototype "app" is shipped as a mobile-only page with no install or offline behaviour (023).
12. Job ads name React, Next.js or TypeScript while the live site shows another framework (036, 037, 038).
13. Site source exposes an admin path or a directory listing (022, 031).
14. A marketing page promotes a feature the product pages do not describe (019, 020).
15. Cookie banner covers the primary content on first load (032, 039).

## Discovery questions
1. Which pages carry revenue today, and which exist only because someone asked for them?
2. Who edits content after launch, and with what access?
3. Which integrations must exist on day one: CRM, payments, auth, ERP?
4. What is the one action a visitor must be able to complete without help?
5. Which devices and browsers matter to your actual audience?
6. What breaks today that you work around manually?
7. Who signs off design, and who signs off content?
8. What must keep working during the switch: URLs, forms, campaigns, tracking?

## Proof-of-work audit angles
1. Count H1 tags on the homepage and report the count and the text of each (021, 033).
2. Check the viewport meta tag and screenshot the page at 390 pixels wide (039).
3. Record page weight, request count and largest image file from a single homepage load (033).
4. Fetch the sitemap, sample twenty URLs, and list every non-200 response (021).
5. Read page source for framework and hosting signals; report what is visible without guessing (034, 036).
6. Open the contact or lead form and note whether validation messages and a success state are specified (019, 040).
7. Follow the primary call to action from the homepage to its end state and record the number of steps (020).
8. Check the certificate, HTTP to HTTPS redirects and any mixed-content warnings (021).
9. Open the login and password reset pages and record which exist and which return an error (025, 029).
10. Count third-party scripts on the homepage and name each host (033).

## Deliverables (what the client receives)
- Page templates and component library
- Content model and CMS setup
- Redirect map for existing URLs
- Integration specification with named endpoints
- Accessibility checklist against the agreed standard
- Performance report with before and after measurements
- Deployment pipeline and environment notes
- Launch checklist with rollback steps

## Common objections
| Objection | Real concern | Reframe | Evidence needed |
|---|---|---|---|
| "We can rebuild this ourselves." | Cost, plus loss of internal control. | A rebuild is mostly content, redirects and integrations, not pages; we scope that part explicitly. | The current page count and the list of integrations. |
| "Our current site works fine." | Not wanting to disturb a working asset. | Fine is measurable; the audit shows what visitors and crawlers actually get. | Audit findings for speed, mobile layout and broken URLs. |
| "Just give us a landing page." | Small budget, fast proof. | A landing page works when one action is defined; otherwise it repeats the problem. | The single conversion goal and the traffic source. |
| "Why not a template?" | Speed and price. | A template fits when the flows are standard; this one is not, and here is the flow that breaks it. | The custom flow named and the template's gap against it. |
| "Our marketing team will handle content." | Fear of an open-ended content project. | Content stays with them; we provide the model, limits and preview. | The content owner named and the launch content list. |

## Do not sell when
- No one owns content and no content exists for the key pages.
- The buyer wants a pixel copy of a competitor site, including its assets.
- The site must run on a platform the buyer will not allow us to touch, and no access will be granted.
- The real request is a one-off page for a campaign that no one will maintain.
- Tracking, consent and data collection must bypass the buyer's own legal review.
- The scope is a migration with no access to the current host or DNS.
- Success is defined only as a ranking position or a traffic number no one will verify.
