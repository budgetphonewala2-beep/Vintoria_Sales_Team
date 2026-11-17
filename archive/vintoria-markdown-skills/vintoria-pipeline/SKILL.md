---
name: vintoria-pipeline
description: "Gives the operator the whole VINTORIA pipeline in one view: safe edits to workspace/pipeline/pipeline.csv, a dated status report with counts by stage, discipline, country and owner, exact metric formulas with named numerators and denominators, stale-deal rules, forecast rules that only use seller-provided values, a data-quality audit, suppression handling, a weekly review agenda and a monthly cohort view. Use for 'pipeline status', 'how many replies', 'what are my numbers', 'which deals are stale', 'run the weekly review', 'fix my pipeline', 'show the funnel', 'what is my forecast', or Hinglish 'pipeline ka status batao'."
---

# VINTORIA Pipeline — Operator View

Read the files, compute the truth, name what is missing, and never estimate a number the CSV can answer.

## When to use / When not to use

**Use when**
- The seller asks for pipeline status, counts or conversion rates.
- A weekly review, forecast or stale-deal sweep is due.
- `pipeline.csv` needs a safe add, update or archive.
- Data quality or suppression hygiene needs checking.
- The seller wants a monthly cohort read.

**Do not use when**
- The seller wants work done today. Use `vintoria-daily`.
- A single prospect needs research, a message or a proposal. Use the matching skill.
- The request is to set targets or quotas. Targets come from the seller, not from this skill.
- There is no `workspace/pipeline/pipeline.csv`. Say so, offer to create it from the schema, and stop.

## Inputs needed (and what to do if missing)

| Input | Where | If missing |
|---|---|---|
| Pipeline rows | `workspace/pipeline/pipeline.csv` | Create the header only, then say the pipeline is empty. Do not invent rows. |
| Stage history and dates | `workspace/prospects/<slug>/HISTORY.md` | Metrics that need transitions are unavailable. Report the gap per row and use current-stage counts only. |
| Reply classifications | `workspace/prospects/<slug>/REPLIES.md` | Positive-reply rate cannot be computed. Mark replies unclassified. |
| Suppressions | `workspace/pipeline/suppressions.md` | Create the file empty and warn that no send can be cleared until it exists. |
| Seller-confirmed values | `PROPOSAL.md` or `HISTORY.md`, line reading `value confirmed by seller` with a date | No forecast. Print "not available: no seller-confirmed values on file". |
| Stage probabilities | Seller | No weighted forecast. Show counts and values by stage only. |
| Target and owner list | Seller | Report actuals only, with no target line. |

Read `../vintoria/references/pipeline-format.md` first. It is the schema authority; this skill never changes a column.

## Workflow

1. **Validate the file before computing anything.** Header must read exactly:
   `slug,company,contact_name,title,email,email_status,country,services,stage,score,next_action,next_due,owner,source,updated`
   Run the data-quality checklist in step 9 and list failures. Do not silently repair; report and fix only with the seller's approval.

2. **Perform add, update and archive correctly.**
   - **Add:** one row per person. `slug` is the domain without `www` or `name@platform`. Fill all 15 fields. `services` holds catalog IDs only, comma separated. `score` is an integer 0 to 100. `next_due` and `updated` are `YYYY-MM-DD`. Leave no field empty except `email` when it is genuinely unknown, which must then be marked `unverified`.
   - **Update:** change only the fields affected. Always refresh `updated`. If the stage changes, also set `next_action` and `next_due`. Never overwrite `HISTORY.md`; append.
   - **Archive:** only rows at `done`, `lost` or `nurture` with no activity for 12 months. Move the row unchanged to `workspace/pipeline/archive.csv` with the same header and no extra columns. Record the archive date in `HISTORY.md`. Suppressions stay in place forever.
   - Never delete a row. Never renumber a slug. Never merge two people into one row.

3. **Compute counts from the CSV, not from memory.**
   - By stage: count rows per stage value. All 13 values in the ladder are valid.
   - By discipline: map each ID in `services` to its discipline range, count rows per discipline, and note rows spanning two or more.
   - By country and by owner: count rows, then count open rows only, meaning stages other than `done`, `lost` and `nurture`.
   - Report the as-of date and the total row count next to every table.

4. **Compute the six rates with exact numerators and denominators.** Use stage-entry dates in `HISTORY.md`. Define the cohort as rows whose first `contacted` entry falls inside the reporting window.

   | Metric | Numerator | Denominator | Rules |
   |---|---|---|---|
   | Reply rate | Cohort rows with a `replied` entry dated after their `contacted` entry | Cohort rows with a `contacted` entry in the window | One reply per row counts once; opt-outs count as replies; bounces do not |
   | Positive reply rate | Replies classified positive in `REPLIES.md`, meaning interested, asked a question or requested a call | All rows with any reply in the window | Unclassified replies count as neutral and are flagged; opt-outs and not-now are not positive |
   | Meeting rate | Rows reaching `discovery` | Rows reaching `replied` | Discovery means scheduled or held, per the ladder |
   | Proposal rate | Rows reaching `proposal` | Rows reaching `discovery` | A proposal is a sent document, not a verbal scope |
   | Win rate | Rows reaching `won` | Rows reaching `proposal` | Report rows and, separately, count of deals if one row produced several |
   | Median days per transition | Median of later date minus earlier date for rows with both entries | Rows with both entries | Compute for `contacted` to `replied`, `replied` to `discovery`, `discovery` to `proposal`, `proposal` to `won`. Use median, not mean, and print n |

   If a denominator is below 10, print the rate and add "small sample". If a denominator is zero, print `n/a` with the reason. Never substitute a remembered figure.

5. **Apply the stale rules and produce the stale list.**
   - Over 14 days since the last entry in `HISTORY.md` and stage is open, the row is **at risk**. It needs a dated next step or a stage change within the week.
   - Over 30 days, the row moves to **nurture** unless the seller says otherwise, with a re-entry trigger written in `next_action`.
   - Over 45 days at `proposal` with no reply, recommend a direct decision question, not another reminder.
   - List stale rows with slug, stage, last activity, days silent, owner and the recommended action.

6. **Build the forecast under the evidence rule.**
   - Eligible only if a file contains a line naming the value, the currency and `confirmed by seller` with a date.
   - Group into three bands: **signed** (stage `won`), **in closing** (`proposal` and `negotiation`), **early** (`discovery` and before).
   - Sum only eligible values. Print row count and value per band, plus the count of rows with no confirmed value.
   - Label every total as an estimate. Never apply a probability unless the seller supplies stage probabilities in writing; if supplied, show the probability next to each row.
   - If zero rows are eligible, print: `Forecast not available. 0 rows carry a seller-confirmed value.` and stop there.

7. **Clear suppressions before reporting anything as sendable.** Match email, domain and phone, case-insensitive on domains. A match blocks every channel and overrides every stage. Set `next_action` to `suppressed, do not contact` and leave the stage unchanged unless the seller decides otherwise. Record new suppressions immediately, append-only, with date, channel and reason. Never remove a line from the file.

8. **Prepare the weekly review agenda.** Forty-five minutes, fixed order, no new research in the meeting.

   | Minutes | Item | Output |
   |---|---|---|
   | 0 to 5 | Numbers: counts, rates, medians, sample sizes | One screen, no commentary yet |
   | 5 to 12 | Replies due and unanswered | Owner and reply window for each |
   | 12 to 20 | Stale deals over 14 and over 30 days | Keep, move to nurture, or close |
   | 20 to 28 | Top 10 by score and next action | Confirm or resequence |
   | 28 to 35 | Forecast bands and gaps | One line per band, labelled estimate |
   | 35 to 41 | Hunt refill for next week | Target count and segments |
   | 41 to 45 | Data quality failures and suppressions | Fix list with owners |

9. **Run the data-quality checklist.** Report every failure with the slug and the field.

   | # | Check | Fail condition |
   |---|---|---|
   | 1 | Header exact | Any difference from the 15-column header |
   | 2 | Slug format | Spaces, slashes, `www`, or duplicates |
   | 3 | Required fields | Empty `company`, `stage`, `score`, `next_action`, `next_due`, `owner`, `source`, `updated` |
   | 4 | Stage valid | Value not in the ladder |
   | 5 | Score range | Not an integer 0 to 100 |
   | 6 | Services format | Names instead of IDs, invented IDs, or a range outside 001 to 270 |
   | 7 | Email status | Value not one of `verified`, `catch_all`, `unverified`, `pattern-guessed`, `invalid` |
   | 8 | Dates | Not `YYYY-MM-DD`, or `next_due` in the past with an open stage |
   | 9 | History agreement | Latest stage in `HISTORY.md` differs from the CSV |
   | 10 | Suppression | Row matches a suppressed email, domain or phone |
   | 11 | Duplicates | Same person under two slugs |
   | 12 | Data minimisation | Fields beyond the minimum, or any sensitive category present |
   | 13 | Owner | Missing, or two owners active on one row |
   | 14 | Source | Missing, or not a URL, post or named referral |
   | 15 | Staleness | Open stage with no activity for more than 14 days |

10. **Produce the monthly cohort view.** Group rows by the month of first contact. One row per cohort, with counts and rates. Add a note on samples below 10. Compare cohorts only on rate and median days, never on raw counts alone, because volume changes with hunt capacity.

11. **Write the report and stop.** Save it, state the three decisions it implies, and ask the seller which to action. Do not start outreach or research inside this skill.

## Output format

Write `workspace/pipeline/reports/STATUS-YYYY-MM-DD.md` in this shape.

```md
# Pipeline status — <YYYY-MM-DD>

Rows: <n>   Open: <n>   Archived excluded: <yes | no>   Window: <start> to <end>

## Counts
| Stage | Rows | % of open |
|---|---|---|

| Discipline | Rows (open) | Won | Lost |
|---|---|---|---|

| Country | Rows | Replies | Meetings |
|---|---|---|---|

| Owner | Open rows | Overdue next_due | At risk |
|---|---|---|---|

## Rates
| Metric | Value | Numerator | Denominator | n | Note |
|---|---|---|---|---|---|
| Reply rate | | | | | |
| Positive reply rate | | | | | |
| Meeting rate | | | | | |
| Proposal rate | | | | | |
| Win rate | | | | | |
| Median days, contacted to replied | | | | | |
| Median days, replied to discovery | | | | | |
| Median days, discovery to proposal | | | | | |
| Median days, proposal to won | | | | | |

## Replies due
| Slug | Contact | Reply received | Age (h) | Owner | Action |
|---|---|---|---|---|---|

## Meetings
| Slug | Date | Owner | Prep done |
|---|---|---|---|

## Stale deals
| Slug | Stage | Last activity | Days | Rule | Recommendation |
|---|---|---|---|---|---|

## Top 10 by score
| Slug | Company | Score | Stage | Next action | Due | Owner |
|---|---|---|---|---|---|---|

## Forecast (estimate)
| Band | Rows | Seller-confirmed value | Rows without value |
|---|---|---|---|
| Signed | | | |
| In closing | | | |
| Early | | | |
| Total (estimate) | | | |

## Data quality
| # | Check | Failing rows | Fix |
|---|---|---|---|

## Suppressions
- Checked on:
- New this period:
- Rows blocked:

## Decisions for the seller
1.
2.
3.

## Not available
- <metric or section> because <missing file or field>
```

For the monthly view, add a second file `COHORT-YYYY-MM.md` with columns: cohort month, contacted, replied, positive, meetings, proposals, won, reply rate, meeting rate, win rate, median days to won, top source, top service. Include the small-sample note.

## Quality gates

Do not show a report until all of these pass.

- Header: 100% match to the 15-column schema. Zero extra or renamed columns.
- Arithmetic: every rate carries a numerator, a denominator and n. Every rate recomputes from the CSV or is marked `n/a`.
- Small samples: 100% of rates with n below 10 carry the label. Zero rates printed with a zero denominator.
- Stale coverage: 100% of open rows over 14 days appear in the stale table with a recommended action.
- Forecast integrity: 100% of values trace to a seller-confirmed line with a date. Zero weighted values unless the seller supplied probabilities. The word `estimate` appears on every total.
- Data quality: all 15 checks run. Failures are listed, not hidden.
- Suppression: 100% of matched rows blocked, zero rows marked sendable while a match exists.
- Truth: zero remembered or rounded numbers. Missing data is named, never filled.

## Failure handling

| Situation | Action |
|---|---|
| `pipeline.csv` missing or empty | Create the header, state that there are no rows, and offer `vintoria-hunt` as the next step. |
| `HISTORY.md` missing for many rows | Report current-stage counts only. Mark all transition metrics unavailable, with the number of rows lacking history. |
| The CSV has duplicate slugs | List them, pick the row with the later `updated` as the live one, and ask the seller before deleting anything. |
| Two sources disagree on a stage | Prefer the latest dated `HISTORY.md` entry. If undated, mark the row `Not found` and flag it. |
| No seller-confirmed values | Print the forecast line for zero eligible rows and stop. Do not substitute scored rows. |
| No web access | Nothing here needs the web. If a row's source cannot be verified, mark it `unverified` and continue. |
| Ambiguous request such as "how are we doing" | Produce the full status report, then name the three decisions it implies. |
| Seller asks for a target or a promise | State that targets come from the seller and that this skill reports actuals only. |

## Definition of done

- [ ] File validated against the exact 15-column header.
- [ ] Add, update and archive rules applied without deleting history.
- [ ] Counts produced by stage, discipline, country and owner, with the as-of date.
- [ ] Six rates with explicit numerator, denominator and sample size.
- [ ] Stale list covers every open row over 14 days, with actions.
- [ ] Forecast uses only seller-confirmed values and is labelled an estimate.
- [ ] Suppression check run before any row is called sendable.
- [ ] All 15 data-quality checks reported.
- [ ] Weekly agenda ready with the seven timed items.
- [ ] Monthly cohort view produced where the window requires it.
- [ ] Report saved, missing data named, three decisions stated.
