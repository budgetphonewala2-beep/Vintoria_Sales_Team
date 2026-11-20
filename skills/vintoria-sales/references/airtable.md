# Airtable — the shared brain of the three Hermes PCs

Three Hermes agents run on three PCs. Local files are not shared between PCs, so **Airtable is the single source of
truth** for everything the team shares: leads, posts already seen, claims, messages, replies, counters, health and deals.
Every skill that mentions one of the shared files below reads and writes the matching **Airtable table** instead — never
a local copy.

| The skills say | On Hermes it is the Airtable table | Key (find before you create) |
|---|---|---|
| `PIPELINE.md` | **Leads** | `Post URL` (and `Person URL` for the same person on another post) |
| `SEEN.md` | **Seen** | `Post URL` |
| `TEAM-BOARD.md` | **Board** | `Message ID` |
| `RUN-LOG.md` | **Runs** | `Run ID` (`<PC>-<date>-<hour>`) |
| `HEALTH.md` | **Health** | `Check ID` |
| `DO-NOT-CONTACT.md` | **DoNotContact** | `Email` / `Person URL` / `Domain` |
| `PROOF-BANK.md` | **Proof** | `Proof ID` |
| `CONTENT-LOG.md` | **Content** | `Post URL` |
| `OUTREACH-SEQUENCE.md`, scheduled emails | **Emails** | `Email ID` (`<lead>-<brand>-<step>`) |
| `THREAD.md` (comments, notes, messages) | **Touches** | `Touch URL` or `Touch ID` |
| replies | **Replies** | `Lead` + `Received at` |
| calls, proposals, wins | **Deals** | `Lead` |
| daily totals | **Daily** | `Date` + `PC` |
| `prospects/<slug>/DOSSIER.md`, audits | `Dossier` and `Site audit` long-text fields on **Leads** (local copies optional) | the lead's record |
| `MEETING-PREP.md`, `CLIENT-PROPOSAL.md` and other close documents | files in PC3's `prospects/<slug>/`, summarised on the **Deals** record | `Lead` |

`SELLER-PROFILE.md`, `OFFER.md` and `IDEAL-CUSTOMER-PROFILE.md` stay as files: the **same copy** on all three PCs (the
owner changes all three, or keeps them in a **Settings** table and every run reads it).

## Tables and fields

**Leads** — one record per person looking for an agency
`Post URL` (URL) · `Person name` · `Headline` · `Person URL` (URL) · `Company` · `Website` (URL) · `Country` (single select:
IN / US / UK / AU) · `City` · `Quote` (long text, exact words) · `Need` (long text) · `Agency intent` (single select:
agency / open / switching) · `Lane` (single select: web-ecommerce / apps-saas-ai / design-branding / marketplaces-qcom /
seo-aeo-geo / paid-ads / social-content / cro-retention / video) · `Services` (multiple select, catalog IDs or Radian names)
· `Brand` (single select: Vintoria / Radian) · `Posted at` (date-time — `Found at` minus the age shown) · `Found at`
(date-time) · `Age at find (h)` (number) · `Comments at find` (number) · `Value score` (number) · `Score parts` (text) ·
`HOT` (checkbox) · `Email` (email) · `Email status` (single select: published / verified / catch_all / unverified /
pattern-guessed / invalid) · `Email source` (text) · `Stage` (single select: the stages in `pipeline-format.md`) ·
`Channel` (single select) · `Owner PC` (single select: PC1 / PC2 / PC3) · `Claimed at` (date-time) · `Last touch`
(date-time) · `Next action` (text) · `Next due` (date-time) · `Outcome` (single select) · `Value` (currency) ·
`Dossier` (long text) · `Site audit` (long text) · `Critic` (text) · `Updated at` (last modified time)

**Seen** — every judged post: `Post URL` · `Judged at` · `PC` · `Result` (kept / dropped) · `Reason` (seller, job ad,
freelancer-only, too old, wrong market, red flag, duplicate person…) · `Score`

**Emails** — `Email ID` · `Lead` (link to Leads) · `Brand` · `From` · `To` · `Step` (1-5) · `Day` (first brand 0/3/7/14/28;
a second brand one day later: 1/4/8/15/29) · `Scheduled for` (date-time, prospect's time zone noted) · `Sent at` · `Subject` · `Body` · `Score` ·
`Critic` · `Status` (scheduled / sent / bounced / replied / stopped / skipped) · `Sender PC`

**Touches** — `Touch ID` · `Lead` · `PC` · `LinkedIn account` · `Type` (comment / connection-note / message / authority-post /
authority-comment) · `Touch URL` · `Text` · `Opening shape` · `Critic` · `Status` (live / deleted / hidden / accepted /
pending) · `At`

**Replies** — `Lead` · `Received at` · `Channel` · `Brand` · `Category` · `Summary` · `Answered at` · `Minutes to answer`
(formula) · `Next step`

**Board** — `Message ID` · `At` · `From` (role + PC) · `To` · `Type` (HANDOFF, CLAIM, DONE, QUESTION, ANSWER, REVIEW-REQUEST,
REVIEW, ALERT, BLOCKED, HOURLY, STANDUP, DECISION, ESCALATE, HOT, HEALTH, DIGEST, SWEEP, HEARTBEAT) · `Lead` · `Text` ·
`Done` (checkbox)

**Runs** — `Run ID` · `PC` · `Started` · `Ended` · `Candidates` · `Valuable` · `HOT` · `Saved` · `Emails sent` ·
`Comments` · `Notes` · `Messages` · `Replies found` · `Skipped by critic` · `Queries used` · `Supply note`

**Daily** — `Date` (the sales day runs 05:00-04:59 IST) · `PC` · `Leads saved` · `Target` (60) · `Started at` ·
`Target reached at` · `Widening step` (0-4) · `Candidates judged` · `Valuable rate` (formula) · `Emails` ·
`LinkedIn touches` · `Replies` · `Calls` · `Health LinkedIn` · `Health email`

**Health** — `Check ID` · `At` · `PC` · `Channel` (LinkedIn account / Vintoria email / Radian email) · `Level`
(GREEN / YELLOW / RED) · `Reason` · `Acceptance 14d` · `Pending invites` · `Captchas 24h` · `Bounces 14d` · `Placement`

**Deals** — `Lead` (link) · `Brand` · `Stage` (meeting / proposal / negotiation / won / lost) · `Call at` · `Discovery score`
· `Proposal sent at` · `Options` (text) · `Value` (currency) · `Currency` · `Won at` · `Lost reason` · `Next step` ·
`Next due` · `Documents` (names of PC3's files: MEETING-PREP, MEETING-NOTES, CLIENT-PROPOSAL, CLOSE-PLAN) · `Proof ID`

**DoNotContact** — `Email` · `Person URL` · `Domain` · `Reason` (stop / unsubscribe / bounce / complaint) · `Date` ·
`Source brand` — every entry blocks **both** brands.

**Proof** — the fields in `../../vintoria-close/references/proof-bank.md`, plus `Brand` (Vintoria / Radian) and
`Permission` (name / quote / numbers). **Content** — the fields in `../../vintoria-authority/references/content-playbook.md`.

## After every email — what is saved (all details, every time)

1. **Before the first email** the lead is already in **Leads** with every detail: person, headline, profile URL,
   company, website, email + status + where it was found, country, city, the exact quote, post URL, `Posted at`,
   `Age at find (h)`, comments, agency intent, lane, services, brand, value score and its parts, HOT, owner PC.
2. **The moment an email is sent**, its **Emails** record gets `Sent at`, `Subject`, `Body`, `Score`, `Critic`,
   `Status` = sent — and the **Leads** record gets `Stage` = contacted, `Channel`, `Last touch`, `Next action`, `Next due`.
3. **Both agencies' emails are scheduled right then** as **Emails** records: the first agency's steps 2-5
   (day 3/7/14/28) with its `Sender PC`, and the second agency's email 1 on day 1 (+ its steps on day 4/8/15/29) with the
   other PC as `Sender PC`. The sending PC finds them in its next runs when they're due.
4. **Every reply, bounce or "stop"** sets all that lead's scheduled **Emails** records (both agencies) to `stopped`, and
   adds a **Replies** or **DoNotContact** record.

## How every PC writes (so three agents never collide)

1. **Find before you create.** Before saving a lead, search **Seen** and **Leads** for the `Post URL`, and **Leads** for
   the same `Person URL` in the last 30 days. Found → it's a duplicate: don't save it again (add the new post to the
   existing lead's notes if useful). **Right after saving, search once more** for the same `Post URL` / `Person URL`:
   if another PC saved it in the same moment, the record created first wins and the newer one is marked
   `Stage` = disqualified (`duplicate`) — never contacted, never counted. Prefer the tool's **upsert** on the key field (Airtable's `performUpsert` with
   `fieldsToMergeOn`) where the Airtable tool supports it.
2. **Claim with the record, not with a message.** To work a lead, set `Owner PC` and `Claimed at` on the Leads record,
   then read it back: if another PC's claim is newer than 60 minutes, let it go. The Board `CLAIM` message is optional.
3. **Batch writes.** Airtable accepts up to **10 records per create / update request** and about **5 requests per second
   per base** — group saves in tens and pause briefly between batches; on a 429 "too many requests" wait 30 seconds and
   retry once.
4. **Never delete records.** Change `Stage`, `Status` or `Result`. History and reports depend on it.
5. **Counters live in Runs.** Before sending or posting, add 1 to the right field of this hour's **Runs** record for your
   PC; the limits in `SELLER-PROFILE.md` → Automation are per LinkedIn account (per PC) and per inbox.
6. **Times** in ISO with zone (`2026-11-20T14:05+05:30`). `Posted at` = `Found at` minus the age shown on the post
   (`3h` → 3 hours earlier; `45m` → 45 minutes).
7. **Airtable unreachable** → keep working, save the records in a local `AIRTABLE-QUEUE.md`, write them first at the next
   run (oldest first, find-before-create still applies). Do **not** contact a lead that hasn't been saved and
   de-duplicated in Airtable.

## Views to create once (the owner's dashboard)

- **Latest leads** — Leads, sorted by `Posted at` newest first, filter `Found at` is today.
- **HOT now** — `HOT` = checked and `Stage` = new or contacted, newest first.
- **To contact** — `Stage` = new, sorted by `Value score` then `Posted at`.
- **Replies waiting** — Replies where `Answered at` is empty.
- **Due emails** — Emails where `Status` = scheduled and `Scheduled for` ≤ now.
- **By PC today** — Daily, grouped by `PC`.

Useful formulas: `Age now (h)` = `DATETIME_DIFF(NOW(), {Posted at}, 'hours')` · `Fresh at find` =
`IF({Age at find (h)} < 24, "yes", "no")` · `Minutes to answer` = `DATETIME_DIFF({Answered at}, {Received at}, 'minutes')`.
