# Intent rubric — is the AUTHOR trying to buy a service we sell?

Judge the **author's** intent, not the topic. For each candidate post produce:

```json
{"role": "buyer | seller | job_seeker | other", "is_buyer": true, "services": ["web", "app", "seo", "marketing", "design", "software"],
 "urgency": "high | medium | low | unknown", "budget": "only if stated, else null", "location": "only if stated/obvious, else null",
 "agency_intent": "agency | open | switching | freelancer | employee",
 "intent_strength": "explicit | active_search | recommendation | problem_awareness | research | none",
 "signals": ["scope", "money", "time", "outsourcer", "owner_referral"], "decision_maker": true,
 "cut_off": false, "evidence_quote": "EXACT words copied from the post", "confidence": 0.0}
```

## Decision rules

1. **Buyer** = the author (or their business) wants to hire/pay someone for a service. Asking for
   recommendations counts ("can anyone recommend an SEO agency?").
2. **Seller** = agencies, freelancers or tools advertising ("we build websites starting at...", "DM for
   affordable SEO"). Also people "looking for clients".
3. **Job seeker** = wants employment ("open to work", "looking for a web developer job", "kaam chahiye").
4. **Other** = employers hiring an employee (salary, CTC, full-time, "we are hiring"), discussions,
   tutorials, memes, people who already found someone, spam, crypto.
5. **Urgency**: high = deadline or "asap/urgent/this week/before Diwali"; medium = clear plan, no date; low =
   "thinking about", "maybe next year".
6. **Confidence** is recorded, not a gate on its own: 0.9+ explicit request with details; 0.7 clear request; 0.5
   ambiguous. The gates in `../../vintoria-sales/references/lead-quality.md` decide. If unsure whether it's a job or
   a project, weigh the signals (rule 12 below) instead of guessing.
7. The quote must be copied verbatim. If you can't quote the intent, it isn't there.

## Agency intent — the second question (Vintoria only works with agency-seekers)

After "is the author a buyer?", ask "**do they want an agency or outside team?**" and add `"agency_intent"` to the JSON:

| `agency_intent` | Means | Examples | Keep? |
|---|---|---|---|
| `agency` (0.85-1.0) | names an agency, studio, company, firm, partner, vendor, outside team, or sends an RFP / brief | "looking for an agency", "recommend a development partner", "RFP for a website" | **yes** |
| `open` (0.7-0.85) | wants it done and doesn't care who — an agency fits | "who can build an app for us?", "recommendations for someone to run our ads" | **yes** |
| `switching` (0.9) | unhappy with their current agency or developer | "our agency isn't delivering", "developer disappeared mid-project" | **yes — very warm** |
| `freelancer` | explicitly wants one freelancer, a student, part-time help, or "cheapest possible" | "anyone know a freelancer…", "part-time freelancer, paid per task" | no |
| `employee` | a job: full-time, salary, CTC, internship | "we're hiring a Flutter developer" | no |

`agency`, `open` and `switching` pass gate 2; `freelancer` and `employee` don't. In the 30 examples below, #8 and #25
are buyers but `freelancer` → **skip**.

## Intent strength (gate 3 — only the first three pass)

| Level | Means | Example |
|---|---|---|
| `explicit` | a clear procurement ask | "We're hiring an agency to run our Google Ads from next month." |
| `active_search` | sourcing right now | "Talking to agencies this week for our app build — who should I add?" |
| `recommendation` | asking for referrals | "Can anyone recommend a good SEO agency for a B2B SaaS?" |
| `problem_awareness` | a problem, no ask | "Our website conversions are terrible." → not a lead (yet — the nurture engine may watch them) |
| `research` | exploring | "Thinking about outsourcing marketing next year — pros and cons?" |
| `none` | no buying intent | tips, opinions, news |

## The quality bar (gate 4) — at least one concrete signal

`scope` (what the agency will own: "handle our SEO", "rebuild our store", "manage our ads") · `money` (budget, retainer,
ad spend) · `time` (deadline, "this quarter", "before launch") · `outsourcer` ("outsource our…", "need an outside team",
"hire an agency") · `owner_referral` (an owner asking "anyone know a good X agency for our launch?").
A bare "need an agency" with none of these is vague → not a lead. If the post is **cut off** before the service, the
direction or the scope is visible, set `cut_off: true`, open the full post and judge again — never reject what you
couldn't see.

## Agency traps — reject each, even in disguise

8. **Agency self-promotion** — "we're a full-service X agency", "we help brands with…", "taking new clients", "we
   scale DTC brands". "Looking to partner with ambitious brands" is an agency hunting clients = seller.
9. **A freelancer selling agency-level work** — "I run a one-person agency", "agency-quality work, available" = job
   seeker, never a buyer.
10. **Agency-to-agency collab with no client** — "looking for an agency to partner with", "collab with fellow
    agencies?", "white-label partnership" = not a lead. It becomes one only with a clear need of their own ("we need an
    agency to handle OUR rebrand").
11. **Agency directories / "vetted network"** — a platform recruiting agencies as inventory = seller.
12. **Hiring AN agency vs hiring FOR an agency** — "we're **hiring an agency** for our SEO" = buyer (the thing hired
    is an outside firm). "Hiring a designer **to join our agency team**, 3+ years, apply with CV" = employee job ad.
    Weigh the signals: years-of-experience thresholds, "join our team", application forms, salary or benefits →
    employment; a bounded job, a deadline, a budget, "for our project" → buyer. Decide — don't keyword-match.
13. **List-building / engagement bait** — "we're compiling a list of top agencies, comment below" = not a lead.
14. **A recruiter "for our client"** — placing people at someone else's company = seller.
15. **Mixed signals** — "need a video agency — DM me if you know one" is a buyer asking for referrals; "DM me for
    video production" is a seller. Judge the main intent.

## Already filled or gone
"found our agency", "update: hired", "contract awarded", "no longer looking", "thanks everyone, we found…" → gate 8
fails. A deleted post ("this post is unavailable") → skip.

### 12 LinkedIn agency-intent examples

| # | Post (abridged) | Buyer | Agency intent | Keep? |
|---|---|---|---|---|
| A1 | "We're looking for an agency to rebuild our D2C store on Shopify before the festive sale. Recommendations welcome." | 0.95 | agency 0.95 | yes — HOT if fresh |
| A2 | "Can anyone recommend a reliable app development company in Pune? We have the specs ready." | 0.95 | agency 0.95 | yes |
| A3 | "Founders — which performance marketing agency has actually worked for you? Scaling Meta ads next quarter." | 0.85 | agency 0.85 | yes (Radian lane) |
| A4 | "Our current agency has missed three deadlines. Looking to switch. Who do you trust for web development?" | 0.9 | switching 0.9 | yes — very warm |
| A5 | "Sharing an RFP: we need a partner to build an AI support chatbot for our SaaS. DM for the brief." | 0.95 | agency 0.95 | yes |
| A6 | "Who can build a booking platform for a chain of 4 clinics? Open to agencies or teams." | 0.9 | open 0.85 | yes |
| A7 | "Need help with SEO for our real estate site. Any suggestions?" | 0.8 | open 0.75 | yes |
| A8 | "Looking for a freelancer for a quick logo, small budget." | 0.85 | freelancer | no |
| A9 | "We are a digital agency helping brands grow. Looking for new clients!" | seller | — | no |
| A10 | "Hiring: Senior React developer, full-time, Bangalore." | other | employee | no |
| A11 | "Which agency should I join as a fresher — product or service company?" | job seeker | — | no |
| A12 | "Thanks for all the agency suggestions — we've signed with one!" | other | — | no (already chose) |

## 30 labelled examples

| # | Post (abridged) | Verdict | Services | Urgency | Quote / why |
|---|---|---|---|---|---|
| 1 | "Looking for a web developer to redo our bakery website, budget around 50k. Need it before Diwali!" | buyer 0.95 | web | high | "Looking for a web developer to redo our bakery website" |
| 2 | "Can anyone recommend a good SEO agency for a dental clinic in Austin?" | buyer 0.9 | seo | medium | "Can anyone recommend a good SEO agency" |
| 3 | "Mujhe apne restaurant ke liye website banwani hai, koi achha developer batao" | buyer 0.9 | web | medium | "restaurant ke liye website banwani hai" |
| 4 | "Hamare clinic ke liye Google pe ranking chahiye, koi SEO wala jaanta hai?" | buyer 0.85 | seo | medium | "Google pe ranking chahiye" |
| 5 | "We need an app for our gym members to book classes. Who builds these?" | buyer 0.9 | app | medium | "We need an app for our gym members" |
| 6 | "Our Shopify store looks dated, want a redesign + better product pages. DM quotes." | buyer 0.9 | web, design | medium | "want a redesign + better product pages" |
| 7 | "Need a logo and branding for my new chai startup, urgent" | buyer 0.9 | design | high | "Need a logo and branding for my new chai startup" |
| 8 | "Anyone know a freelancer who can run Meta ads for a real-estate project in Pune?" | buyer 0.85 | marketing | medium | "who can run Meta ads for a real-estate project" |
| 9 | "Website banwana hai coaching institute ka, budget 25-30k, jaldi" | buyer 0.9 | web | high | "Website banwana hai coaching institute ka" |
| 10 | "Thinking about maybe getting a website next year for the shop" | other 0.4 | web | low | Too vague — not a buyer yet (note for nurture) |
| 11 | "Need someone to fix our WordPress site, contact form stopped working" | buyer 0.85 | web | high | "Need someone to fix our WordPress site" |
| 12 | "Looking for an agency to handle social media for 3 cafes in London" | buyer 0.9 | marketing | medium | "Looking for an agency to handle social media" |
| 13 | "Koi CRM bana sakta hai hamare distribution business ke liye?" | buyer 0.8 | software | medium | "Koi CRM bana sakta hai" |
| 14 | "Recommendations for someone to build a booking system for my salon?" | buyer 0.85 | web, software | medium | "build a booking system for my salon" |
| 15 | "Need an e-commerce website for my handloom sarees, Instagram se zyada sales chahiye" | buyer 0.9 | web, marketing | medium | "Need an e-commerce website for my handloom sarees" |
| 16 | "We build stunning websites starting at $299! DM for a free quote 🚀" | seller 0.95 | — | — | Advertising a service |
| 17 | "I'm a freelance React developer available for projects. Check out my portfolio" | seller 0.95 | — | — | "available for projects" |
| 18 | "Hum website aur app banate hain, sasta aur achha. Contact karein" | seller 0.95 | — | — | "Hum website aur app banate hain" |
| 19 | "Looking for clients who need SEO, 5 years experience" | seller 0.9 | — | — | Seeking clients, not buying |
| 20 | "#OpenToWork Web developer with 3 years of experience looking for opportunities" | job_seeker 0.95 | — | — | "looking for opportunities" |
| 21 | "Fresher hoon, koi web developer job ho to batao" | job_seeker 0.9 | — | — | "web developer job ho to batao" |
| 22 | "Looking for a web developer job in Bangalore, immediate joiner" | job_seeker 0.95 | — | — | "web developer job" |
| 23 | "We're hiring! Full-time Flutter developer, 4-6 LPA, Noida, apply now" | other 0.95 | — | — | Employer hiring staff (salary, full-time) |
| 24 | "Hiring SEO executive, work from office, CTC 3-4 LPA" | other 0.95 | — | — | Job ad |
| 25 | "Need a part-time freelancer to build our landing page, paid per project" | buyer 0.8 | web | medium | "build our landing page, paid per project" — project, not employment |
| 26 | "Which is better for a small business, Wix or WordPress?" | other 0.6 | web | low | Discussion; could be nurture, not a buyer |
| 27 | "Thanks everyone, we found a developer for the app!" | other 0.9 | — | — | Already solved |
| 28 | "Free airdrop! Build your crypto website with our AI tool" | other 0.99 | — | — | Spam |
| 29 | "Our current agency isn't delivering on SEO, considering switching. Suggestions?" | buyer 0.85 | seo | medium | "considering switching. Suggestions?" |
| 30 | "मुझे अपनी दुकान के लिए वेबसाइट बनवानी है, कोई बताओ" | buyer 0.9 | web | medium | "दुकान के लिए वेबसाइट बनवानी है" |

## After judging

- Buyers → a row in `PIPELINE.md` (`source` = the query that found them), with the exact quote in their `HISTORY.md`.
- Low-urgency "thinking about it" posts → optional `nurture` stage, never cold-emailed as if they asked.
- Track which queries produced real buyers; drop queries that only return sellers or job ads.
