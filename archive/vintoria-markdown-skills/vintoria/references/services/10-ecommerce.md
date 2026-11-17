# 10 / E-Commerce — 20 services

> Catalog scope template: "Commerce development for {service}, covering the relevant storefront, catalog, checkout, payment, customer, order and integration workflows."

## Services

| ID | Service |
|---|---|
| 191 | E-Commerce Development |
| 192 | Shopify Development |
| 193 | WooCommerce Development |
| 194 | Custom E-Commerce Development |
| 195 | Headless Commerce |
| 196 | E-Commerce Marketplace Development |
| 197 | Product Catalog Systems |
| 198 | Payment Gateway Integration |
| 199 | Subscription Commerce |
| 200 | Checkout Development |
| 201 | Checkout Optimization |
| 202 | E-Commerce Automation |
| 203 | E-Commerce Analytics |
| 204 | Product Recommendation Systems |
| 205 | E-Commerce Search |
| 206 | Inventory Integration |
| 207 | Order Management Integration |
| 208 | Customer Account Systems |
| 209 | E-Commerce Performance Optimization |
| 210 | E-Commerce Conversion Optimization |

## Who buys this (segments)

- **Direct-to-consumer brand outgrowing a stock theme.** Buying a custom storefront, checkout and catalog structure. Trigger: a launch date, a funding round or a theme that cannot support the roadmap.
- **Retailer replatforming from a legacy cart.** Buying e-commerce development, payment integration and order management. Trigger: an end-of-life platform notice or a failed peak season.
- **B2B wholesaler moving orders online.** Buying customer accounts, catalog and inventory integration. Trigger: an account team drowning in manual purchase orders.
- **Marketplace operator with supply and demand sides.** Buying marketplace development, seller onboarding and payouts. Trigger: seller complaints about manual onboarding.
- **Subscription brand with billing edge cases.** Buying subscription commerce, checkout and payment gateway integration. Trigger: failed renewals or refund requests traced to billing logic.
- **Multi-store brand entering a new market.** Buying local payments, currency, tax and catalog translation. Trigger: a signed distribution deal or a local entity.
- **Agency subcontracting a storefront build.** Buying storefront and integration capacity under their brand. Trigger: a signed client statement of work.
- **Category leader with traffic but weak checkout.** Buying checkout optimization, search and conversion work. Trigger: a board question about conversion or a new head of digital.

## Buying signals (observable)

1. Cart or checkout returns a price different from the product page (197, 200).
2. Checkout forces account creation with no guest option visible (200, 201).
3. Site search returns no result for an obvious in-catalog product term (205).
4. Store is slow on mobile when measured this session, with a high largest contentful paint (209).
5. Only one payment method is offered at checkout (198).
6. Product pages promise subscriptions but the flow fails or links to a third-party page (199).
7. Currency or language selector is broken, hidden or missing on a multi-market store (191, 198).
8. Order tracking or returns links to a third-party portal that errors (207, 208).
9. Marketplace seller onboarding page describes a manual email process (196, 208).
10. Product feed for shopping ads is missing or returns malformed entries (203, 222).
11. App or plugin list shows overlapping inventory, review and email tools (192, 206, 207).
12. Careers page lists an e-commerce manager or Shopify developer role (192, 191).
13. Ad library shows active product ads landing on a generic collection page (210, 233).
14. Product structured data is absent when the page source is inspected (203, 213).

## Discovery questions

1. Which platform are you on, and what forced this review now?
2. How many products, variants and markets must the store handle?
3. What happens today when a customer pays, from authorisation to fulfilment?
4. Which integration breaks most often, and who owns it?
5. Is checkout one step or several, and what is the drop-off you see?
6. Do you sell subscriptions, bundles or pre-orders?
7. Who updates the catalogue, and how long does a product change take?
8. What must stay live during a migration, and when is your peak season?

## Proof-of-work audit angles

- Walk one product from listing to order confirmation and count the exact number of steps and form fields.
- Record whether guest checkout exists, and which fields are mandatory.
- Measure mobile page weight and largest contentful paint on the product and checkout pages this session.
- Run five in-catalogue search terms and record result quality and response time.
- List every payment method offered and whether a wallet or local method is missing for the stated market.
- Inspect page source for product, price and availability structured data, and record what is absent.
- Compare stock levels shown on the listing and product page for the same item at the same time.
- Check the returns, shipping and subscription terms pages for existence and last-updated date.
- Check canonical tags and duplicate URLs across filtered collection pages.

## Deliverables (what the client receives)

- Storefront build or replatform plan with scope boundaries
- Checkout flow specification with field and validation rules
- Payment and tax configuration sheet per market
- Catalog and variant data model
- Integration map for inventory, order management and fulfilment
- Analytics and tracking specification for the purchase funnel
- Conversion test backlog with hypotheses and success measures
- Handover guide covering catalogue, orders and admin tasks

## Common objections

| Objection | Real concern | One-line reframe | Evidence needed |
|---|---|---|---|
| We are locked into our platform | Migration risk and sunk cost | Phase one improves the current store without a move | Scoped optimisation list that works on the existing platform |
| Our theme already handles this | Paying twice | Audit the theme against the stated requirement, show only the gaps | Gap list naming each observed failure |
| We cannot change anything before peak season | Lost revenue during the busiest period | Read-only audits now, ship after the freeze | Work plan that names the freeze dates |
| We tried an agency and it stalled | Delivery and handover | Fixed scope, written acceptance criteria, a named owner at both ends | The acceptance criteria section of the proposal |
| Conversion is fine, we need more traffic | Attribution of the problem | Test checkout and search first, then decide where spend belongs | Observed funnel defects from the audit |

## Do not sell when

- The buyer will not name the platform, catalogue size or market list.
- The ask is a template purchase or a one-hour theme tweak.
- A migration is required but no product data export is available.
- Payment processing must be handled by a party outside the client and the processor.
- Peak-season traffic cannot support any scheduled change window.
- The client wants a sales guarantee tied to conversion, which the catalog does not offer.
- The scope is marketplace payouts and escrow, which needs legal and financial sign-off first.
