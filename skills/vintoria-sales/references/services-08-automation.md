# 08 / Business Automation — 22 services
> Catalog scope template: "Workflow automation for {service}, connecting relevant systems, triggers, data movement, notifications, business rules and exception handling."

## Services
| ID | Service |
|---|---|
| 146 | Business Automation |
| 147 | Workflow Automation |
| 148 | CRM Automation |
| 149 | Lead Automation |
| 150 | Email Automation |
| 151 | WhatsApp Automation |
| 152 | Customer Support Automation |
| 153 | Sales Automation |
| 154 | Marketing Automation |
| 155 | Internal Operations Automation |
| 156 | Invoice Automation |
| 157 | Reporting Automation |
| 158 | Notification Automation |
| 159 | API Automation |
| 160 | Data Automation |
| 161 | Document Automation |
| 162 | Approval Workflow Automation |
| 163 | Employee Workflow Automation |
| 164 | No-Code Automation |
| 165 | Low-Code Automation |
| 166 | AI Automation |
| 167 | Multi-System Automation |

## Who buys this (segments)
- **Sales operations at growing teams** - buying CRM automation and lead automation. Trigger: reps enter the same data twice or leads go cold between systems.
- **Finance and admin teams** - buying invoice automation and approval workflow automation. Trigger: month-end close slips or an audit raises manual control gaps.
- **Support leads** - buying customer support automation and notification automation. Trigger: response time targets are missed at peak.
- **Marketing teams** - buying marketing automation and email automation. Trigger: campaign volume outgrew manual sending.
- **Operations managers in service businesses** - buying internal operations automation. Trigger: a new location, contract or headcount step is added.
- **Small teams and founders** - buying no-code automation for weekly manual routines. Trigger: a report or handoff is done by hand every week.
- **Multi-system enterprises** - buying multi-system automation and API automation. Trigger: a new system is added and records stop reconciling.
- **Agencies delivering automation** - buying white-label build capacity. Trigger: a client asks for an integration the agency cannot staff.

## Buying signals (observable)
- Careers page advertises an operations, RevOps or automation specialist (146, 155).
- Job ad lists manual data entry, spreadsheet upkeep or copy-paste between tools (146, 157).
- The same operational role is advertised repeatedly over consecutive months (155, 163).
- Integration or app directory page names tools that do not list each other (167, 159).
- Help centre describes a manual request form for access, refunds or invoices (162, 156).
- Contact or quote form promises a reply within a stated number of business days (158, 152).
- Reviews or community posts complain about slow quotes, onboarding or invoicing (153, 156).
- Documentation names CSV upload as the way to move data between systems (160, 167).
- Changelog announces a new tool with no mention of migration or sync (167, 159).
- LinkedIn post from an operations lead describes a spreadsheet that runs the business (157, 160).
- Multiple locations or brands use separate forms and separate inboxes (158, 167).
- Job ad requires advanced spreadsheet skills for a role that is mostly reporting (157).
- Site offers WhatsApp or chat with no published response or routing flow (151, 152).
- Public onboarding steps are described as a sequence of emails (149, 163).

## Discovery questions
- Which process breaks most often, and where does it break?
- Who runs it today, how often, and how long does one run take?
- Which systems hold the data, and which is the source of truth?
- What must happen before the next step can start?
- What should happen when a step fails or a record is missing?
- Who approves a change to this process?
- What have you already automated, and what did it not cover?
- What does a good month look like for this process?

## Proof-of-work audit angles
- Map the public lead path from form to stated response promise; report each step and the stated time.
- List every form on the site and its fields; report fields that duplicate data already held elsewhere.
- Identify systems named on integration, pricing or docs pages; report the list and any missing pairing.
- Read the help centre for processes described as email us or contact support; report each with its article count.
- Record the response-time claim stated in site copy; report only what is written.
- Check careers pages for repeated postings of one operational role; report titles and posting dates.
- Note every channel offered (email, phone, WhatsApp, chat) and whether a published flow exists; report per channel.
- Extract the customer steps for the core transaction from the help centre; report the step count.
- Check public status or changelog pages for incidents attributed to sync or integration; report quotes and dates.
- Identify spreadsheet or CSV workflows described publicly; report the pages and what they state.

## Deliverables (what the client receives)
- Process map with triggers, owners, systems and exceptions
- Automation build for agreed workflows inside the client's tools
- Integration layer connecting the named systems
- Error handling and alerting rules for each automated step
- Runbook covering retries, ownership and escalation
- Test log with cases run and observed outcomes
- Handover documentation and change log

## Common objections
| Objection | Real concern | One-line reframe | Evidence needed |
|---|---|---|---|
| Our process is too custom to automate | Fit | Automate the stable steps and keep judgement with people | Process map showing which steps are rule-based |
| We tried an automation tool and it broke | Reliability | Build with error handling, alerting and a named owner | Runbook, retry rules, test log |
| If it breaks we are stuck | Dependency | Handover documentation and a monitored failure path | Runbook and escalation list |
| Staff will resist it | Change management | Scope to the steps staff dislike and keep approvals human | 162 human approval step in the design |
| We need to fix our data first | Order of work | Pick one workflow and clean only the fields it uses | Field inventory from the audit |

## Do not sell when
- No system owner exists and nobody can grant access.
- The process changes every month and no stable version can be named.
- Data lives only in personal inboxes or spreadsheets nobody controls.
- Headcount reduction is the stated goal with no process change behind it.
- Vendor contracts forbid the integration.
- No test records or sandbox can be provided.
- They want unattended automation for a regulated decision.
