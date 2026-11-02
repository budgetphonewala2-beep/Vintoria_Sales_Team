# Email quality: score, AI tells, personalization, panel review

`python <SCRIPTS>/email_lint.py --sequence prospects/<slug>/SEQUENCE.json` scores each email 0-100 and lists the exact
fixes; `outreach.py approve --check` refuses emails under `LINT_MIN_SCORE` (default 65). Aim for **80+ on every email**.
The claim check proves an email is true; this proves it is worth replying to.

## The score (what the 100 points reward)

| Part | Points | Email 1 | Follow-ups |
|---|---|---|---|
| Situation | 25 | first two sentences are about **them** and specific (their post, a fact from their site) — never open with I/we | still about them (their site, goal, deadline) |
| Value | 20 | one plain line of what you do + one concrete proof (a number, a named result) | something **new**: a second fact, a fix idea, an example, a result |
| You-ratio | 10 | at least 2 sentences about them for every sentence only about you | same |
| CTA | 15 | one low-effort question ("worth a look?", "want me to send it?") — no "15 minutes?" in a first email | one question |
| Length | 15 | 50-120 words (body, without signature) | 25-90; breakup 10-60 |
| Subject | 5 | 2-5 words, lower-case, plain, internal-looking; no Re:/Fwd:, no hype | (same thread) |
| Clean | 10 | no AI tells, banned openers, jargon, em dashes, `!!`, more than one link, bold/HTML | same |

80+ ship · 65-79 one more pass · under 65 rewrite.

## Banned and AI-sounding phrases (prospects delete on sight)
- Openers: "I hope this email finds you well", "My name is…", "I wanted to reach out", "I came across your profile".
- AI tells: "Here's the thing", "I'll be honest", "unlock", "take it to the next level", "in today's fast-paced…",
  "game-changer", "seamless", "elevate", "supercharge", "delve", "It's not about X, it's about Y", self-answered
  questions ("The result? 40% more…"), em dashes.
- Jargon: synergy, leverage, best-in-class, cutting-edge, world-class, circle back, touch base, holistic, leading
  provider, innovative solution — and Indian-English idioms overseas buyers find odd: kindly, revert, do the needful.
- Follow-ups: "just checking in", "bumping this", "any update?", "did you get a chance…".

## Personalization that works (4 levels — use level 4)
1. Merge tags (name, company) — table stakes.
2. Industry pain — "most DTC brands…".
3. Role pain — "as the founder you're probably also running the store".
4. **Individual, timely, connected to the problem** — "you posted on Tuesday that the theme is slow on mobile; your
   homepage took 4.2 s to load in my test."

**The deletion test:** delete the first two sentences. If the email still makes sense, the personalization isn't
doing its job — rewrite it so the opener *leads into* why you're writing.

For people-database leads (Apollo, LinkedIn people search) there is no post to quote, so find **two independent,
verified signals** in the dossier (a site fact + hiring, a launch, reviews, a tool they use) before writing; one weak
signal makes a generic email.

## Panel review (before you show the user)
Read each email as five people and fix what each would object to:
1. **The buyer, on a phone between meetings** — do I see in two lines why this is for me? Can I answer in five words?
2. **A skeptical founder** — is every claim specific and believable? Anything sound like a template?
3. **A deliverability engineer** — plain text, ≤ 1 link, no tracking, no spammy words, opt-out + address present?
4. **A copy editor** — shortest version that says the same thing? Any sentence that doesn't earn its place?
5. **A compliance reviewer** — truthful sender and subject, real proof only, the right consent rule for their country?

Then run the score and the claim check again.
