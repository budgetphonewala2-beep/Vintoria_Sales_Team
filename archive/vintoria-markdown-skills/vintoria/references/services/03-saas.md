# 03 / SaaS & Digital Products — 20 services
> Catalog scope template: "Product engineering for {service}, covering product workflows, users, permissions, integrations, architecture, QA and scalable delivery within the defined scope."

## Services
| ID | Service |
|---|---|
| 041 | SaaS Product Development |
| 042 | SaaS MVP Development |
| 043 | Multi-Tenant SaaS Development |
| 044 | B2B SaaS Development |
| 045 | B2C SaaS Development |
| 046 | SaaS Dashboard Development |
| 047 | SaaS Subscription Systems |
| 048 | SaaS Billing Systems |
| 049 | SaaS Authentication Systems |
| 050 | SaaS User Management |
| 051 | SaaS Admin Panels |
| 052 | SaaS API Development |
| 053 | SaaS Architecture |
| 054 | SaaS Migration |
| 055 | SaaS Performance Optimization |
| 056 | SaaS Feature Development |
| 057 | SaaS Product Redesign |
| 058 | SaaS UI/UX Development |
| 059 | SaaS Analytics Integration |
| 060 | SaaS Maintenance & Scaling |

## Who buys this (segments)
- **Pre-seed SaaS founder** - buying a working product with accounts and billing before hiring. Trigger: a design partner asking for logins, or a first paid commitment.
- **Non-technical founder with a freelance build** - buying a rescue, a rebuild or a completion of a half-finished product. Trigger: the freelancer left, or the code will not deploy.
- **B2B SaaS with enterprise buyers** - buying roles, permissions, SSO and audit trails. Trigger: a security questionnaire or a procurement review that names missing controls.
- **SaaS with billing problems** - buying subscription, invoicing and dunning flows. Trigger: manual invoices, failed payments handled by hand, or a plan change breaking access.
- **Product team needing one feature** - buying scoped feature delivery inside an existing codebase. Trigger: a committed customer date or a roadmap item that keeps slipping.
- **SaaS on a legacy stack** - buying a migration without downtime. Trigger: hosting costs, an unsupported runtime, or an acquisition review.
- **SaaS at a scale wall** - buying performance and architecture work. Trigger: slow dashboards, support tickets about timeouts, or a single-tenant workaround.
- **Agency or reseller with a white-label product** - buying multi-tenant separation and admin tooling. Trigger: a second client demanding its own branding or data isolation.

## Buying signals (observable)
1. Pricing page says "contact us" for every tier and lists no plan limits (047, 048).
2. Signup flow exists but the product is behind a "request access" form (042, 049).
3. Changelog or release notes show no entry for several months (056, 060).
4. Help centre screenshots show an interface the live product no longer has (057, 058).
5. Public reviews mention failed payments, double charges or access after a plan change (047, 048).
6. Security or trust page exists and does not mention SSO, roles or audit logs (049, 050).
7. Careers page hires a platform or infrastructure engineer for a product that appears single-region (053, 060).
8. API documentation is unversioned or marked beta for longer than a year (052).
9. Status page is missing, or its last incident entry is unresolved (060).
10. A "beta" or "new" label sits on a feature that appears in the main navigation (056).
11. Cookie list on the login domain names several third-party analytics hosts (059).
12. Job ads describe "cleaning up" or "rewriting" the product's core (054, 057).
13. Documentation shows tenant or workspace setup done manually by support (043, 051).
14. Dashboard marketing screenshots show numbers no user could generate (046, 059).
15. Site advertises an integration list with logos that do not appear in the docs (052).

## Discovery questions
1. Who is the paying user, and who is the admin, and are they different people?
2. What does a new account do in the first ten minutes?
3. How are plans, seats and limits enforced today?
4. Which enterprise requirement comes up in every deal: SSO, roles, data residency or audit logs?
5. Which support tickets repeat every week?
6. What is the codebase, who wrote it, and who can deploy it now?
7. What breaks if a tenant needs its own data or branding?
8. Which integration is named in your best deals, and does it exist yet?

## Proof-of-work audit angles
1. Open the signup flow and count the steps to first value; note every field required (042, 049).
2. Quote the pricing page and note which plan dimensions are stated: seats, usage, features, limits (047, 048).
3. Read the changelog and record the date of the most recent entry (056, 060).
4. Check the documentation for an API version and a deprecation policy; quote what is written (052).
5. Look for a public status page and record its most recent incident date (060).
6. Read the trust or security page and list which of SSO, roles, audit logs and encryption are named (049, 050).
7. Open the help centre and note any screenshot that differs from the live interface (057, 058).
8. Request a password reset and record whether the flow completes or names a support contact (049).
9. List third-party scripts loaded on the login page and name each host (059).
10. Read the last twenty public reviews and quote every mention of billing or access loss (047, 048).

## Deliverables (what the client receives)
- Product scope with roles, permissions and limits defined
- Data model and tenancy decision record
- Billing and subscription flow specification
- Auth and user management specification
- API contract with versioning rules
- Admin panel with the agreed operational actions
- Test plan covering critical user journeys
- Release and rollback checklist

## Common objections
| Objection | Real concern | Reframe | Evidence needed |
|---|---|---|---|
| "We already have an MVP." | Paying again for work that exists. | The question is whether it can take payment, hold tenants apart and survive support load; we scope the gap. | Access to the code, or a walkthrough of the current flows. |
| "We will hire in-house instead." | Long-term cost and ownership. | In-house is right eventually; the first version needs decisions made quickly and written down. | The hiring plan and the date the first hire starts. |
| "Enterprise buyers will not accept a young product." | Deal risk. | The questionnaire is the real requirement list; we answer it with controls, not assurances. | The actual security questionnaire or procurement list. |
| "Billing is just Stripe." | Assuming billing is one integration. | The work is plan changes, proration, failures and access; the provider is the easy part. | The current plan structure and how failures are handled today. |
| "Can you just add this one feature?" | Scope and regression risk. | A feature touches permissions, billing and the data model; scope names all three. | The feature request plus the affected flows. |

## Do not sell when
- The buyer will not grant code or admin access for the scoping work.
- The current build is entangled with a vendor the buyer cannot leave.
- The product handles regulated data and no compliance owner is available.
- The request is a single bug fix treated as a product engagement.
- Billing must bypass the payment provider's own review or the buyer's finance team.
- The buyer expects the product to pass an enterprise security review without changing scope.
- There is no named owner for product decisions after launch.
