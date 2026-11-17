# Expansion, retention and referrals

> Imported from the instruction-only Vintoria set and wired to the engine (pipeline, prospect folders, seller profile).

Grow each delivered account through catalog-backed adjacencies, dated triggers and permissioned proof, never through invented results.

## When to use / When not to use

**Use when**
- A project is in `delivery` or `done` and the next need is repeat work.
- The seller asks what to sell an existing client next.
- A client reports a launch, funding, new market, hiring, incident, redesign or migration.
- The seller wants a referral, case study or testimonial.
- A churned client may be worth re-approaching.

**Do not use when**
- The client has an open complaint, outage or unpaid invoice. Resolve it first; expansion during a fire destroys trust.
- No delivery record exists. Finish the current engagement and capture acceptance first.
- The need is a brand-new prospect. Use `vintoria-lead-hunt` and `vintoria-prospect-research`.
- The request is to change price, discount or add a free extra. Price is the seller's decision, see `../vintoria-sales/references/pricing-policy.md`.
- The client asked for no further contact. Log it in `pipeline/suppressions.md` and stop.

## Inputs needed (and what to do if missing)

| Input | Where | If missing |
|---|---|---|
| Delivery status and acceptance | the pipeline history (`python <SCRIPTS>/core/pipeline.py note`), contract, acceptance notes | Ask the seller which deliverables were accepted and on what date. Do not assume completion. |
| What was bought and delivered | `CLIENT-PROPOSAL.md`, the pipeline (`python <SCRIPTS>/core/pipeline.py`) `services` | Rebuild the service list from the contract. Mark unknown IDs `Not found`. |
| Client-reported outcomes | Client emails, meeting notes, review calls | Leave the outcome field blank. Never infer a metric from traffic, screenshots or a hunch. |
| Client contacts and roles | the pipeline (`python <SCRIPTS>/core/pipeline.py`), `DOSSIER.md` | Ask the seller for the day-to-day contact and the budget holder. |
| Written permission for proof | A dated email or note from the client | No permission means no case study, no logo, no quote, no numbers. |
| Churn reason | `CLOSE-PLAN.md` loss debrief or exit notes | Ask the seller; otherwise mark `Not found` and do not guess. |
| Expansion target and timing | Seller | Propose one candidate and one date; ask the seller to confirm. |

Read `../vintoria-sales/references/services-` for every discipline before proposing a service. Read `../vintoria-sales/references/truth-rules.md` before writing any outcome sentence.

## Workflow

1. **Confirm the account is safe to grow.** Check three facts: the last deliverable was accepted, there is no open incident or complaint, and the invoice position is not in dispute. If any is unclear, pause and ask the seller. Log the check date in the pipeline history (`python <SCRIPTS>/core/pipeline.py note`).

2. **Record what was actually delivered.** List catalog IDs and names, the acceptance date and any buyer-stated outcome with its source. Anything the client did not state stays blank. A delivered service is the only proof you may reference.

3. **Build the adjacency map for this account.** Start from the discipline or disciplines already bought, then select two to four natural next services from the table. Every suggestion must carry an ID from the catalog and a reason tied to an observed signal, not to a wish.

   | Bought here | Natural next services (catalog IDs) | Signal to watch |
   |---|---|---|
   | 01 Strategy & Consulting | 010 Product Roadmapping, 015 Product-Market Fit Strategy, 022 Custom Web Application Development, 042 SaaS MVP Development | Strategy accepted, build not yet scoped |
   | 02 Web Development | 212 Search Engine Optimization, 246 Analytics Implementation, 257 Website Maintenance, 230 Conversion Rate Optimization | Site live, no measurement or visibility work attached |
   | 03 SaaS & Digital Products | 048 SaaS Billing Systems, 055 SaaS Performance Optimization, 060 SaaS Maintenance & Scaling, 187 Application Monitoring | Product live, billing or load pressure appears |
   | 04 Mobile App Development | 080 Mobile App Maintenance, 079 Mobile API Integration, 249 A/B Testing, 261 Performance Optimization | App shipped, store reviews or releases slow down |
   | 05 UI/UX & Product Design | 090 Design Systems, 102 Design-to-Development Handoff, 099 Product Usability Testing, 265 UX Audits | Design delivered, squad shipping inconsistent screens |
   | 06 Branding & Creative | 119 Digital Brand Experience, 110 Social Media Brand Kits, 120 Marketing Creative Design, 107 Brand Guidelines | Identity approved, assets produced weekly by hand |
   | 07 AI Development | 134 RAG Systems, 136 AI Assistants, 143 AI Internal Tools, 131 AI Workflow Automation | One AI surface live, adjacent manual work remains |
   | 08 Business Automation | 157 Reporting Automation, 167 Multi-System Automation, 166 AI Automation, 162 Approval Workflow Automation | One workflow automated, the next one still manual |
   | 09 Backend, API & Cloud | 182 DevOps, 183 CI/CD Implementation, 186 Security Hardening, 187 Application Monitoring | Backend shipped, deploys or alerts still manual |
   | 10 E-Commerce | 201 Checkout Optimization, 203 E-Commerce Analytics, 206 Inventory Integration, 210 E-Commerce Conversion Optimization | Store live, traffic rising with flat orders |
   | 11 Digital Marketing & SEO | 230 Conversion Rate Optimization, 232 Marketing Funnel Development, 231 Marketing Analytics, 227 Content Marketing | Traffic growing, measurement or funnel gaps remain |
   | 12 Growth, Analytics & Continuous Development | 270 Continuous Development, 257 Website Maintenance, 258 SaaS Maintenance, 254 Custom Analytics Dashboards | Programme delivered, no owner for ongoing work |

   Rules for the map:
   - Two to four services per discipline, no long lists, no service outside 001 to 270.
   - One primary recommendation per account, with one sentence on why now.
   - Never recommend a service the client has just bought and not yet accepted.

4. **Match a trigger event.** A trigger turns a suggestion into a timely conversation. Use only triggers you can observe or the client states.

   | Trigger | Observable signal | Lead with | Timing |
   |---|---|---|---|
   | Launch | A dated launch, waitlist or press note | 246 Analytics Implementation, 261 Performance Optimization | 1 to 3 weeks after launch |
   | Traffic growth | Client states growth or a new channel | 230 Conversion Rate Optimization, 232 Marketing Funnel Development | Same month |
   | New market | New locale, country or currency announced | 214 Local SEO, 191 E-Commerce Development, 198 Payment Gateway Integration | Before the market goes live |
   | Funding | A round is announced or the client says so | 042 SaaS MVP Development, 015 Product-Market Fit Strategy, 114 Startup Branding | 2 to 6 weeks after the announcement |
   | Hiring | A role opens that the catalog could serve | 270 Continuous Development, 258 SaaS Maintenance, 102 Design-to-Development Handoff | When the role is posted |
   | Security incident | Public status entry, disclosure or client statement | 186 Security Hardening, 263 Security Updates, 187 Application Monitoring | After the incident is closed, never during |
   | Redesign | New site, identity or navigation appears | 212 Search Engine Optimization, 262 Core Web Vitals Optimization, 265 UX Audits | 2 to 4 weeks after release |
   | Platform migration | Host, cart or CMS change is stated | 181 Cloud Migration, 054 SaaS Migration, 209 E-Commerce Performance Optimization | Before the cutover date |

   If no trigger exists, do not manufacture one. Use the 90-day review instead.

5. **Set the 30/60/90-day account rhythm.** Each touch has a purpose and an artefact, never a check-in call with no agenda.

   | Day | Purpose | Artefact to bring |
   |---|---|---|
   | 7 | Onboarding or kickoff confirmation | Access list, success measures, named owners |
   | 30 | Adoption review | What was accepted, what is blocked, first open risk |
   | 60 | Value review | Client-stated outcomes only, plus the next open need |
   | 90 | Expansion conversation | One adjacency, one scope sketch, no price |
   | Each quarter after | Business review | Delivered register, open risks, one next step |

   Cap: one expansion ask per 30 days. Never ask during an open incident, within 14 days of a complaint, or while an invoice is disputed.

6. **Ask for a referral with an exact script.** Use one of these, chosen by the moment, and adapt only the bracketed facts. Never hint at a reward.

   - After an acceptance milestone: "You said the [deliverable] landed well. Is there one other team you work with that has the same [named problem]? A name is enough, and I will not contact them until you say it is fine."
   - After a positive value review: "Glad that held up. If a peer asks you who did this, would you be comfortable pointing them to me? I will keep the first note short and say you suggested it."
   - After a case study is approved: "Thank you for approving that. Would you introduce me to one person in your network facing the same [problem]? One line from you is worth more than any cold email."
   - On a decline: "Understood. I will not ask again this quarter." Then record the date and do not repeat.

7. **Capture a case study only with permission.** Five sections, each with a source. No section may be filled from imagination.

   | Section | Collect | Rule |
   |---|---|---|
   | Problem | The client's own description, with date | Quote or paraphrase precisely; no invented stakes |
   | Work | Delivered services as catalog IDs and names | Only what the contract and acceptance record confirm |
   | Evidence | Artefacts the client allows you to show | Screenshots, documents, demos; name each file |
   | Outcome | Numbers or statements the client provides in writing | No derived figures, no industry averages, no projections |
   | Permission | Named approver, channels allowed, date, quote approval | Required before any external use; store in the prospect folder |

   If the client cannot provide an outcome number, publish a scope-and-evidence story and leave the result blank. That is a complete case study; an invented number is not.

8. **Request a testimonial in three questions.** Ask: what problem were you trying to solve, what was working with the team, and what would you tell a peer considering this. Offer to draft from their words and send it back for approval. Record the approved version, who approved it, the date and where it may be used. Never edit meaning; only trim with consent.

9. **Run win-back after churn.** Sequence: day 30 exit review with the reason code from `../vintoria-sales/references/team.md` practice, day 90 a useful artefact with no ask, day 180 a trigger-based note. Maximum four touches per year. Stop immediately on any request. Reference the original reason and what changed; never guilt, never a discount.

10. **Move the pipeline correctly.** Keep the row at `delivery` while work is live. Move to `expand` only when a repeat opportunity is identified and dated. When scope is agreed, create the next step as `proposal`. Always set `next_action`, `next_due` and `updated`, and append the change to the pipeline history (`python <SCRIPTS>/core/pipeline.py note`).

## Output format

Write `prospects/<slug>/EXPANSION-MAP.md` in this shape, then update the pipeline history (`python <SCRIPTS>/core/pipeline.py note`) and the pipeline (`python <SCRIPTS>/core/pipeline.py`).

```md
# Expansion map — <company>

Stage: <delivery | done | expand | lost>   Owner: <name>   As of: <YYYY-MM-DD>
Delivered: <catalog IDs and names>   Accepted on: <YYYY-MM-DD>

## Delivered record
| Service ID | Service | Accepted | Client-stated outcome | Source |
|---|---|---|---|---|

## Adjacency map
| Discipline bought | Next service ID | Next service | Why now (observed signal) | Priority |
|---|---|---|---|---|

Primary recommendation: <ID and name> because <signal>.
Not recommended yet: <ID and name> because <reason>.

## Trigger watch
| Trigger | Status today | Evidence | Conversation date |
|---|---|---|---|

## 30/60/90 plan
| Day | Date | Purpose | Artefact | Owner |
|---|---|---|---|---|

## Referral
- Ask date:
- Script used:
- Person suggested:
- Permission to contact: <yes | no | not yet>

## Case study
- Problem:
- Work (IDs):
- Evidence:
- Outcome (client-provided):
- Permission: approver, channels, date

## Testimonial
- Requested on:
- Approved text:
- Approved by:
- Use allowed:

## Win-back (if churned)
- Churn reason code:
- Last touch:
- Next touch and date:
- Stop condition:
```

## Quality gates

Do not show the map until all of these pass.

- Adjacency coverage: 12 of 12 disciplines present in the reference table, each with 2 to 4 IDs. For this account, at least 3 candidate services, each validated against its discipline file.
- Catalog integrity: 100% of IDs exist, names match exactly, zero invented or merged services.
- Outcome integrity: 100% of numbers are client-provided with a source and date. Zero derived, estimated or benchmarked figures.
- Permission: case study and testimonial each carry a named approver and a date, or are marked blocked.
- Contact discipline: no more than one expansion ask in 30 days, zero asks during an open incident or within 14 days of a complaint.
- Referral volume: at most one request per 30 days per account, zero repeats after a decline in the same quarter.
- Stage truth: `expand` set only with a dated opportunity; every row has `next_action` and `next_due`.
- Language: no sentence over 28 words in client-facing text, no em dash, no exclamation mark, no invented urgency.

## Failure handling

| Situation | Action |
|---|---|
| No delivery record | Ask the seller for the acceptance note. If none exists, treat the account as `delivery` and do not propose expansion. |
| Client outcomes unavailable | Leave outcome fields blank, publish scope and evidence only, and say so in one line. |
| No trigger observed | Use the 90-day review. Do not invent a launch, funding round or incident. |
| Client is unresponsive | Maximum four touches per year across all channels. Record each and stop on any signal. |
| Client asked for no contact | Append to `pipeline/suppressions.md`, move to `nurture` or close, and never contact again on any channel. |
| Ambiguous request such as "grow this account" | Produce the adjacency map and the 90-day plan, then stop for seller approval. |
| Seller profile missing proof | Recommend services from the catalog only, mark proof `Not found`, and ask the seller for a real reference. |

## Definition of done

- [ ] Account safety checked: acceptance, no open incident, no invoice dispute.
- [ ] Delivered record written with catalog IDs and acceptance dates.
- [ ] Adjacency map built from the 12-discipline table, 3 or more candidates.
- [ ] Primary recommendation has one observed signal behind it.
- [ ] Trigger watch populated or explicitly empty.
- [ ] 30/60/90 plan dated with artefacts and owners.
- [ ] Referral asked at most once, script recorded, permission noted.
- [ ] Case study and testimonial captured with named approval, or marked blocked.
- [ ] Win-back scheduled with reason code and stop condition where relevant.
- [ ] the pipeline (`python <SCRIPTS>/core/pipeline.py`) and the pipeline history (`python <SCRIPTS>/core/pipeline.py note`) updated, stage truthful, next action dated.
