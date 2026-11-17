---
name: vintoria-research
description: "Produces workspace/prospects/<slug>/DOSSIER.md for VINTORIA: a sourced profile of one company or person covering what they do, offers and pricing model, tech evidence, decision makers, buying signals, 1 to 3 catalog service fits with the observed signal beside each, ranked hooks, risks, unknowns and the next action, all behind a claim, source, date and tier evidence table. Use for 'research this company', 'build a dossier', 'who is the decision maker at', 'what does this company need', 'prospect this domain', 'deep dive on this lead', 'what stack do they use', or Hinglish like 'isko research karo'."
---

# VINTORIA Researcher

Turns one prospect's public footprint into a dossier a writer can use without inventing a single fact.

## When to use / When not to use

| Use it when | When not to use it |
|---|---|
| A pipeline row needs depth before outreach | The row is not in `pipeline.csv` yet (use `vintoria-hunt`) |
| The seller names a company or person to investigate | The user wants a technical website audit (use `vintoria-audit`) |
| A dossier is older than 90 days or a fact was challenged | The user wants the email written (use `vintoria-outreach`) |
| A reply asks a question the dossier cannot answer | The user wants a price or a proposal (use `vintoria-proposal`) |
| A deal stalled and the account needs re-reading | The user wants a market map (use `vintoria-icp`) |

## Inputs needed (and what to do if missing)

| Input | Source | If missing |
|---|---|---|
| Company domain or person plus company | User or pipeline row | Ask once. If still unclear, stop and list the two candidates. |
| ICP and scoring rubric | `workspace/icp/ICP.md` | Use the catalog and score with the rubric in `../vintoria-icp/SKILL.md`, flagged provisional. |
| Offer lanes and proof map | `workspace/profile/OFFER.md` | Use catalog IDs only and note the gap. |
| Existing dossier and history | `workspace/prospects/<slug>/` | Create the folder, `DOSSIER.md` and `HISTORY.md`. |
| Pipeline row | `workspace/pipeline/pipeline.csv` | Research anyway; add the row after, or say it is orphaned. |
| Suppressions | `workspace/pipeline/suppressions.md` | Check before any work; if listed, stop. |

Read `../vintoria/references/truth-rules.md`, `../vintoria/references/quality-bar.md` and the relevant discipline files before writing.

## Workflow

1. Resolve the slug per `../vintoria/references/pipeline-format.md`. Check suppressions. If suppressed, stop and report it.
2. Read the pipeline row, the ICP segment, the offer lane and any existing dossier. Update in place; never overwrite history.
3. Open pages in the priority order below. Minimum 6, maximum 12. Record every URL and access date as you go.
4. Build the evidence table first, then write prose from it. If a section has no row, that section says `Not found`.
5. Fill the 11 dossier sections in order. Keep each to 3 sentences or a short list.
6. Map service fit: exactly 1 to 3 services, each with the exact ID and name, the observed signal that justifies it, and the buyer problem it answers. More than 3 means the research is not sharp enough.
7. Write 3 ranked hooks. Each hook needs a source URL, a date, and a one-line shape the writer can use. A hook that could apply to any company in the industry is rejected.
8. List risks and disqualifiers, taking observable conditions from the discipline file's "Do not sell when" plus anything seen on their site.
9. List unknowns explicitly. `Not found` in a section is acceptable; a guess is not.
10. Score twice: the ICP lead score (0 to 100) and the dossier quality score from `../vintoria/references/quality-bar.md` (floor 70). Report both.
11. Write `DOSSIER.md`. Append a line to `HISTORY.md`: date, stage change, evidence count, score.
12. Update `pipeline.csv`: `stage=researched`, new `score`, `next_action=draft outreach`, `next_due` within 3 working days, `updated=today`.
13. Report the top hook, the fit, the score and the one risk in 4 lines.

### Page priority (open in this order)

| Order | Page | What to extract |
|---|---|---|
| 1 | Homepage | Positioning sentence, audience, primary action, visible proof |
| 2 | Pricing or plans | Model (seat, usage, project, retainer), tiers, what is excluded, `[PRICE TO CONFIRM]` for anything unstated |
| 3 | Product or features | Real workflows, screenshots, what is shipped versus promised |
| 4 | About, team, leadership | Size, locations, named leaders and titles |
| 5 | Careers, jobs | Roles, stacks, volume, repetition, process pain |
| 6 | Changelog, blog, release notes | Cadence, gaps, what shipped, pricing or plan changes |
| 7 | Docs, developer, API | Versioning, auth, integrations, deprecation |
| 8 | Help centre, support, contact | Manual processes, response promises, broken flows |
| 9 | Status, trust, security | Incidents, SSO, roles, audit logs, compliance claims |
| 10 | Reviews: G2, Capterra, Trustpilot, app stores | Repeated complaints with dates and versions |
| 11 | LinkedIn company and people | Headcount band, recent hires, named owners |
| 12 | Press, news, funding, ad library | Dated events, launches, expansion, spend |

Sitemap and robots are fair game for finding pages. A 404, a blocked page or a login wall is itself a finding: record it.

### What counts as evidence

- Tier `tool`: a page you fetched this session. Tier `prospect`: their own words. Tier `catalog` and `profile`: our own sources.
- A search snippet is not evidence. Open the page.
- Quote verbatim in quotation marks. Paraphrase is labelled `paraphrased`.
- An inference (for instance, that the checkout is custom) is labelled `inferred` and can never appear as fact in outreach.
- Every number must come from one source, with its unit and date.
- Two sources disagree: record both, prefer the page the company controls.
- No claim from memory, from another prospect, or from an old dossier of ours.

### Reading job ads

Extract the role, the named stack, seniority, posting date and whether it repeats. A job ad is a budget and pain signal, not a fact about the buyer. It proves the company is hiring for that function; it does not prove who owns the decision or what the budget is. Ask, do not assert.

### Reading changelogs and blogs

Record the newest dated entry and the gap since. A gap over 90 days with active marketing is a signal about delivery capacity. Entries without dates do not prove recency. Note what shipped, what was removed and any plan or pricing change.

### Reading reviews

Sort by newest, filter 1 to 3 stars, and quote with date and version. Separate product complaints from support complaints. Three or more reviews naming the same issue count as a pattern. Never present an old review as current, and never use a competitor's review.

### Inferring a decision maker

- Name a person only when the name and title appear together on a company page or a public professional profile, with the URL saved.
- If only a function is found (for example, a job ad naming a Head of Engineering), write `Head of Engineering (role only, name Not found)`.
- Describe the remit as likely, based on the title: "likely owns platform decisions". Mark it `inferred`.
- Prefer the owner of the specific problem: founder in small firms, the functional head in mid-market, the named programme owner in enterprise.
- Never guess an email. A guessed pattern gets `email_status=pattern-guessed` and cannot be used until verified.
- Never carry a person over from another company or another dossier.

## Output format

```markdown
# DOSSIER.md: <company>
Slug: <domain>
Research date: YYYY-MM-DD
Researched by: <owner>
Sources opened: N  |  Evidence rows: N  |  Lead score: NN (band)  |  Dossier score: NN

## Snapshot
- What they sell: <one sentence>
- Model: <B2B, B2C, marketplace, SaaS, services, commerce, Not found>
- Size and locations: <headcount band, offices, or Not found>
- Market: <countries, languages>
- Stage: <bootstrapped, funded, public, Not found>
- Why now: <one dated signal or Not found>

## What they do
<3 sentences, each traceable to the evidence table>

## Offers and pricing model
- Model: <seat, usage, project, retainer, commission, Not found>
- Published tiers: <names and what each includes, or Not found>
- Price shown: <amount and unit if published, otherwise [PRICE TO CONFIRM]>
- Exclusions stated: <list or Not found>

## Tech and stack evidence
| Layer | Observed | How observed | Confidence |
|---|---|---|---|
| Front end | <name or Not found> | page source, headers, docs | observed / inferred |
| Back end |  |  |  |
| Payments, auth, data |  |  |  |
| Hosting, analytics |  |  |  |

## Team and decision makers
| Name | Title | Source | Likely remit | Confidence |
|---|---|---|---|---|
| <name or Not found> |  |  |  | named / role only / inferred |

## Buying signals
1. "<quote>" (source, date)
2. <observed fact with date>
3. <hiring, funding, launch or review signal with date>

## Service fit
| # | Service ID and name | Observed signal | Buyer problem | Entry or follow-on |
|---|---|---|---|---|
| 1 | <ID> <exact name> | "<quote or fact>" |  | entry |

## Ranked hooks
1. <hook, one line, specific and dated> | source: <URL> | use as: <shape of the first line>
2. ...
3. ...

## Risks and disqualifiers
- <observable risk>
- <discipline "Do not sell when" match>

## Unknowns
- <question the research could not answer>

## Next action
<One action, one owner, one date. Default: draft outreach naming service <ID>.>

## Evidence table
| Claim | Source URL | Date | Tier | Quote or paraphrase |
|---|---|---|---|---|
|  |  |  | tool / prospect / catalog / profile |  |
```

## Quality gates

| Gate | Floor |
|---|---|
| Pages opened | 6 or more, 12 maximum |
| Evidence rows | 8 or more, every section backed by one |
| Unsourced claims | 0 |
| Service fits | 1 to 3, each with an ID and an observed signal |
| Named decision maker | 1 name plus title plus source, or an explicit role-only entry |
| Ranked hooks | 3, each specific, dated and sourced |
| Hooks that pass the swap test | 3 of 3 (would fail for a different company in the same industry) |
| Dossier quality score | 70 or above, per `../vintoria/references/quality-bar.md` |
| Prices | 0 invented; published prices quoted with source and date only |
| Pipeline update | `stage=researched` with an integer score |

Below 70: do not update the stage to `researched`; keep it `new` and say what is missing.

## Failure handling

- **No web access.** Do not fabricate. Write the dossier with every section `Not found`, score it 0, keep the stage `new`, and ask for a saved page, export or screenshots.
- **Site blocks the fetcher.** Try the sitemap, cached copies, docs, review sites and LinkedIn. Record which sources were blocked.
- **Company is a shell or has no site.** Research the people and the product listings instead; if still empty, disqualify with a reason.
- **Person, not company.** Use `name@platform` as the slug and research the company behind them.
- **Ambiguous company name.** Stop and ask, listing the two candidate domains.
- **Suppressed contact.** Stop, report, and do not research further.

## Definition of done

- [ ] Folder and `DOSSIER.md` exist under `workspace/prospects/<slug>/`.
- [ ] All 11 sections present; unknowns marked `Not found`.
- [ ] Evidence table has 8 or more rows with URL, date and tier.
- [ ] 1 to 3 service fits, each with the exact catalog ID, name and observed signal.
- [ ] At least one decision maker named with a source, or a role-only entry that says so.
- [ ] 3 ranked hooks, each passing the swap test.
- [ ] Risks and disqualifiers listed from observed facts.
- [ ] Both scores stated; dossier score 70 or above before the stage moves.
- [ ] `pipeline.csv` updated to `researched` with score and next action; `HISTORY.md` appended.
- [ ] Top hook, fit, score and one risk reported in 4 lines.
