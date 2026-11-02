# Truth rules — where an agent could make things up, and what stops it

Every sentence that reaches a prospect must trace back to something nobody invented. These are the places an agent
could hallucinate in this workflow and the guard in the scripts that catches each one.

## What counts as evidence (and what doesn't)

| Evidence (trusted) | Tier | Not evidence |
|---|---|---|
| Script outputs: `DOSSIER.json`, `SITE-AUDIT.json` (+ PageSpeed), contact records in the pipeline | tool | Anything the agent wrote: `COMPANY-RESEARCH.md`, `DECISION-MAKERS.md`, `COMPETITIVE-INTEL.md`, `LEAD-QUALIFICATION.md`, `DOSSIER.md`, `SITE-AUDIT.md`, drafts, proposals, meeting preps |
| Pages opened and saved by `fetch_page.py --save prospects/<slug>/sources` | page | What the agent "remembers" about a company |
| The prospect's own words: their post, their replies (the pipeline keeps them) | prospect | A search snippet on its own (`WEB-RESEARCH.json` is a list of leads to check) |
| The seller's profile: case studies, years, clients, pricing, delivery, guarantees | profile | Results, clients or guarantees that aren't in the profile |
| Today's date | calendar | Holidays, deadlines, "25 days away" — compute them and put the source in evidence |

`claim_check.py` skips the second column even when a glob matches it, and tells you which file supported each claim.

## The guards

| Where an agent could invent | Guard |
|---|---|
| A sentence with no obvious "fact word" ("Your competitors already do this") | Every declarative sentence is checked; only greetings, sign-offs, the opt-out line, offers ("Happy to send…") and plain questions are exempt |
| Flipping a fact ("your site **has** a viewport tag") | Negation check: a claim must not contradict the evidence sentence it matches |
| An invented client, tool, person or place ("we rebuilt Sephora's store", "your WordPress site") | Every name/brand/place in a claim must appear in the same source that supports it |
| A wrong or invented number | Every number in a claim must be in one single source |
| A misquote | Text in quotation marks must appear verbatim; `pipeline.py add --quote` refuses a quote that isn't word-for-word in the post |
| Industry "facts" ("most of your visitors…", "studies show…") | Generalisations need a 75 % match to a source that says it |
| Promises ("we guarantee page one", "you'll double sales") | Only supported by the guarantees in the seller profile |
| A search snippet about a different company with a similar name | Research results that don't name the prospect never become evidence; a snippet alone never supports a claim — open the page and save it |
| An email marked "verified" by hand | `pipeline.py contact --email-status verified` is downgraded to `unverified` unless a verifier recorded it (`verifications.jsonl`) |
| A guessed address presented as real | Guesses are `pattern-guessed`; `outreach.py` never sends to anything but `verified` (or approved `catch_all`) |
| The wrong name in the greeting ("Hi Jessica" to Jane) | `outreach.py` checks the greeting against the contact on file |
| Saying something was sent, booked, verified or scanned | Only say it when a script's output says so (`"sent": true`, a `meeting_id`, `verified_by`, a saved `DOSSIER.json`); otherwise say what is still to do |
| Prices, timelines, scope in proposals and replies | Numbers must come from the profile (deal size, pricing model, delivery time) or be marked `[TO CONFIRM]` |
| Agent research documents | Before saving one, run `claim_check.py --draft <the doc> --prospect <slug>` — every line needs a source |

## How to write when you don't know
- Unknown fact → "Not found" (in research) or leave it out (in an email). Never fill the gap with something plausible.
- A likely consequence → hedge it ("so phone visitors may see the desktop layout"); never state it as measured.
- A missing proof point → a visible `[ADD REAL CUSTOMER RESULT]`; a missing price → `[TO CONFIRM: ...]`.
- If two sources disagree, say so and use the more direct one (the page itself over a snippet, the prospect's own
  words over anyone else's).
