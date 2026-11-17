# 07 / AI Development — 25 services
> Catalog scope template: "AI engineering for {service}, covering the relevant model/API layer, business context, workflow, evaluation and product integration."

## Services
| ID | Service |
|---|---|
| 121 | AI Product Development |
| 122 | AI SaaS Development |
| 123 | AI Chatbot Development |
| 124 | AI Customer Support Systems |
| 125 | AI Knowledge Bases |
| 126 | AI Search |
| 127 | AI Recommendation Systems |
| 128 | AI Document Processing |
| 129 | AI Content Systems |
| 130 | AI Data Analysis |
| 131 | AI Workflow Automation |
| 132 | LLM Integration |
| 133 | AI API Integration |
| 134 | RAG Systems |
| 135 | AI Agent Development |
| 136 | AI Assistants |
| 137 | AI Copilots |
| 138 | AI Lead Qualification |
| 139 | AI Personalization |
| 140 | AI Voice Applications |
| 141 | AI Image Applications |
| 142 | AI Document Intelligence |
| 143 | AI Internal Tools |
| 144 | AI-Powered Dashboards |
| 145 | Custom AI Solutions |

## Who buys this (segments)
- **Support and customer success leaders** - buying AI customer support systems and a knowledge base. Trigger: ticket volume outgrew headcount or a hiring freeze started.
- **Sales operations** - buying AI lead qualification and routing. Trigger: inbound volume rose and first-response time slipped.
- **Product teams adding an AI feature** - buying AI product development and LLM integration. Trigger: a competitor shipped an AI feature or a customer requested one.
- **Operations and back office** - buying AI document processing and document intelligence. Trigger: a PDF or paper step is producing errors or delays.
- **Internal platform teams** - buying AI internal tools and copilots. Trigger: analysts spend days assembling the same report.
- **SaaS companies monetising AI** - buying AI SaaS development and personalisation. Trigger: a pricing model change or a waitlist opens.
- **Agencies reselling AI builds** - buying implementation capacity. Trigger: they sold an AI proof of concept they cannot deliver.
- **Knowledge-heavy teams** - buying AI search and RAG systems. Trigger: policies and documents are spread across drives, wikis and inboxes.

## Buying signals (observable)
- Job ad for an AI engineer, ML engineer or role naming LLMs (121, 132, 135).
- Careers or about page states AI-first or lists AI as a roadmap pillar (121, 145).
- Changelog entry mentions an AI assistant, copilot or AI beta feature (136, 137).
- Blog or docs page describes an AI feature with a waitlist or early access (121, 122).
- Help centre article explains how to use the company chatbot (123, 124).
- Public roadmap board carries an AI card in discovery or planned (121, 143).
- Marketing claims AI while the public demo shows a scripted sequence (145, 139).
- Reviews or community posts ask for search that understands questions (126, 134).
- Job ad lists prompt design or evaluation as responsibilities (132, 142).
- Privacy or terms page updated with third-party model processing language (125, 134).
- Conference talk or LinkedIn post about an internal AI pilot (131, 143).
- Documentation names a model provider or an AI integration partner (132, 133).
- Repeated manual document handling is advertised as a role responsibility (128, 142).
- Status page or help centre shows repeated question categories at scale (124, 125).

## Discovery questions
- Which decision or task should the system handle, and what does a correct answer look like?
- Where does the knowledge live today, and who keeps it current?
- What is the current human process, step by step?
- How will you judge output quality before and after launch?
- What happens today when a person gets this wrong?
- Which data can the model see, and which must it never see?
- Who owns the feature after launch?
- What has already been tried, and why did it stop?

## Proof-of-work audit angles
- Map the published support flow and count steps to reach a human; report the count and each step.
- Inventory the public help centre: article count, visible update dates, and whether search exists; report what is visible.
- Run five real customer-style questions through public search; report each query and whether a relevant article surfaced.
- Find every public claim of AI and quote the exact wording; report whether a live feature is reachable.
- List the documents a customer must submit for the core process; report the list and formats.
- Open the trial or demo and record what any AI feature does end to end; report observed behaviour only.
- Quote AI or model-processing language from the privacy policy with its date.
- Count repeated question patterns in public forums, reviews or help pages; report verbatim examples.
- Note model providers named in docs, job ads or integration pages; report each with its source.
- Open the public chat widget repeatedly and record response times; report observed times and the date.

## Deliverables (what the client receives)
- Solution design note covering model layer, data flow and evaluation
- Working AI feature integrated into the agreed product surface
- Retrieval corpus and ingestion pipeline for agreed sources
- Evaluation set with scoring criteria and a review log
- Admin controls for content, prompts and access
- Monitoring and failure-handling runbook
- Handover documentation with architecture and known limits
- Pilot report stating what was tested and what was observed

## Common objections
| Objection | Real concern | One-line reframe | Evidence needed |
|---|---|---|---|
| AI will hallucinate and embarrass us | Reputational risk | Scope to grounded retrieval with refusal behaviour and evaluation | Evaluation set, cited sources, refusal rules |
| We tried a chatbot and it failed | Wasted spend | Diagnose whether the failure was retrieval, scope or handoff | Audit of the old flow and transcripts if the client shares them |
| Our data is not ready | Dependency risk | Start with one bounded corpus and expand | Source inventory with owners and freshness from discovery |
| How do we know it works | No acceptance test | Agree the evaluation set before build | Scoring criteria and a signed review sample |
| Legal will not allow it | Compliance | Define data boundaries and processing terms first | Privacy review, data-flow diagram, provider terms quoted |

## Do not sell when
- No data owner exists and nobody can approve data use.
- The task requires deterministic output with zero tolerance for error and no human review step.
- They ask for an AI strategy with no process, data or user named.
- The knowledge base does not exist in any digital form.
- They expect the model to replace a regulated decision.
- There is no way to evaluate output quality.
- The buyer wants a demo, not a deployed system.
