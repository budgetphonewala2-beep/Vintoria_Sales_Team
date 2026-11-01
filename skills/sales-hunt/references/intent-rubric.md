# Intent rubric — is the AUTHOR trying to buy a service we sell?

Judge the **author's** intent, not the topic. For each candidate post produce:

```json
{"role": "buyer | seller | job_seeker | other", "is_buyer": true, "services": ["web", "app", "seo", "marketing", "design", "software"],
 "urgency": "high | medium | low | unknown", "budget": "only if stated, else null", "location": "only if stated/obvious, else null",
 "evidence_quote": "EXACT words copied from the post", "confidence": 0.0}
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
6. **Confidence**: 0.9+ explicit request with details; 0.7 clear request, few details; 0.5 ambiguous → **not**
   a buyer (threshold 0.6). If unsure whether it's a job or a project, it's not a buyer.
7. The quote must be copied verbatim. If you can't quote the intent, it isn't there.

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

- Buyers → pipeline (`pipeline.py add ... --source hunt:<query-id>`), with the quote saved as a note.
- Low-urgency "thinking about it" posts → optional `nurture` stage, never cold-emailed as if they asked.
- Track which queries produced real buyers; drop queries that only return sellers or job ads.
