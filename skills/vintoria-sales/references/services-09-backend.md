# 09 / Backend, API & Cloud — 23 services

> Catalog scope template: "Backend and infrastructure engineering for {service}, covering APIs, data, authentication, deployment, reliability and operational requirements."

## Services

| ID | Service |
|---|---|
| 168 | Backend Development |
| 169 | Custom API Development |
| 170 | REST API Development |
| 171 | GraphQL API Development |
| 172 | Database Architecture |
| 173 | PostgreSQL Development |
| 174 | MongoDB Development |
| 175 | MySQL Development |
| 176 | Authentication Systems |
| 177 | Authorization Systems |
| 178 | User Management Systems |
| 179 | Cloud Architecture |
| 180 | Serverless Development |
| 181 | Cloud Migration |
| 182 | DevOps |
| 183 | CI/CD Implementation |
| 184 | Infrastructure as Code |
| 185 | Performance Engineering |
| 186 | Security Hardening |
| 187 | Application Monitoring |
| 188 | Error Monitoring |
| 189 | Backend Optimization |
| 190 | Third-Party API Integration |

## Who buys this (segments)

- **Funded SaaS team with a single-region monolith.** Buying service extraction, database architecture and observability before a scaling deadline. Trigger: an uptime incident or a growth commitment published by the company.
- **Agency that sold a build it cannot staff.** Buying backend development, API development and DevOps capacity behind a fixed interface. Trigger: a signed client contract or an unfilled platform job ad.
- **Marketplace with a public API in beta.** Buying REST or GraphQL API development, authentication and third-party integration. Trigger: partner integrations still listed as coming soon.
- **Fintech or health product facing a procurement questionnaire.** Buying security hardening, authorization systems and audited infrastructure practice. Trigger: an enterprise deal blocked in security review.
- **Legacy business leaving managed hosting or a datacentre.** Buying cloud migration, infrastructure as code and CI/CD. Trigger: a renewal date or a datacentre exit notice.
- **Mobile team whose backend is the bottleneck.** Buying performance engineering, backend optimization and monitoring. Trigger: app store reviews reporting slow loads or failed sessions.
- **Platform team under a hiring freeze.** Buying DevOps, application monitoring and error monitoring as a scoped retainer. Trigger: increased on-call load or an open role frozen mid-process.
- **Startup preparing for technical due diligence.** Buying database architecture, cloud architecture and a technical audit. Trigger: a term sheet or an investor request list.

## Buying signals (observable)

1. Careers page lists backend, platform or SRE roles open across more than one quarter (168, 182).
2. Public status page or changelog shows repeated incidents, degraded notices or rollbacks (187, 188).
3. Developer docs mark endpoints as beta, deprecated or unversioned (169, 170, 171).
4. Product advertises an API but the developer docs link returns an error or a stale release (169, 190).
5. Marketing site or app responds slowly from more than one region when measured this session (185, 189, 269).
6. Job ad mentions manual deploys, FTP uploads or server access by request (182, 183, 184).
7. Product stores accounts, payments or health data with no visible security page (186, 176, 177).
8. Engineering blog or funding post describes a re-platform, cloud move or cost reduction programme (179, 181).
9. App store reviews report login failures, session drops or broken password reset (176, 178).
10. Documentation or status page names a single region or single availability zone (179, 180).
11. Public repository or blog describes a monolith split, queue backlog or service extraction (168, 172, 185).
12. Integration partner list shows the same items as coming soon for more than one release (190).
13. Product advertises integrations but publishes no webhook or API documentation (169, 190).
14. Engineer posts on LinkedIn asking for observability or infrastructure as code tooling advice (184, 187, 188).

## Discovery questions

1. Which system carried the last outage, and what did you learn from it?
2. What is deployed today, and what still needs a person at a keyboard?
3. Which endpoint or query is slowest, and do you have a number for it?
4. Who holds production access, and how is it granted and revoked?
5. Which database, and what is the largest table you expect in a year?
6. What breaks first when traffic doubles?
7. Which third-party APIs are in the critical path, and who owns the keys?
8. Is there an interface contract you want kept, or is this a clean build?

## Proof-of-work audit angles

- Open the developer docs and record whether versioning, auth scheme, rate limits and error format are documented. Report each gap by name.
- Request the marketing site and API hostname from two regions and record TTFB and status codes.
- Inspect response headers for HSTS, CSP and content-type protections, and list what is missing.
- Check whether admin, staging or database ports are reachable publicly, and report the exact hostname tested.
- Read the status page or changelog and count incidents in the visible window; note whether postmortems exist.
- Check the careers page for backend, platform or SRE roles and record how long each has been open.
- Review developer docs for deprecated endpoints and last-updated dates; list every stale page.
- Test password reset, session expiry and logout on an account you own, and record the observed behaviour.
- Compare the same record across two endpoints and report any value that differs.
- Check the sitemap and robots file for staging hosts or internal paths exposed publicly.

## Deliverables (what the client receives)

- Backend service map and interface contract document
- API specification with versioning, auth and error model
- Database schema, migration plan and index review
- Authentication and authorization design note
- Cloud architecture and environment diagram
- CI/CD pipeline definition and release checklist
- Observability setup covering logs, metrics, alerts and error tracking
- Security hardening report with a prioritised remediation list

## Common objections

| Objection | Real concern | One-line reframe | Evidence needed |
|---|---|---|---|
| We already have a backend team | Duplication and unclear ownership | Scope to one interface and hand it over | Interface contract, handover checklist, code ownership note |
| A cloud migration will break production | Downtime and data loss | Phase the migration with a parallel run and rollback criteria | Migration plan with acceptance criteria and rollback steps |
| We cannot give infrastructure access | Security and compliance | Work from a documented architecture and a least-privilege list | Access matrix showing exactly what is required |
| Our stack is unusual | Fit and learning cost | Assess the documented stack first, decline if outside 168 to 190 | Technology stack consulting output |
| Security work is a black box | Unclear output for the spend | Every item arrives as a reproducible finding with severity | One sample finding in the proposed format |

## Do not sell when

- The buyer cannot share logs, architecture or any readable system description.
- The request is per-head staffing with no defined scope or deliverable.
- The ask is a single server fix that does not map to 168 to 190.
- No named owner exists on the client side for the system.
- Zero downtime is demanded as a precondition before any architecture is shared.
- The root cause is a third-party outage the client does not control.
- The goal is a compliance certificate; the catalog covers hardening, not certification.
