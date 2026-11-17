# Reddit — read the post, answer it, leave Vintoria's WhatsApp

On Reddit the buyer asked in public, so the best first touch is a public, genuinely useful comment from the logged-in
account, ending with Vintoria's WhatsApp link. A helpful comment wins the client; a promo comment gets removed and the
account banned. Contact details: `../../vintoria-sales/references/vintoria-contact.md`.

## Before you comment — all must be true

1. **It's a real buyer** (intent rubric, confidence ≥ 0.7): they want to hire or are asking who can build/fix something.
   Not a seller, not a job seeker, not a discussion, not already solved ("found someone, thanks").
2. **The post is open and fresh**: not locked, archived or removed; ideally under 48 hours, never older than 7 days.
3. **The subreddit allows it.** Read the sidebar rules (and wiki for r/forhire-style subs) once and note them in
   `IDEAL-CUSTOMER-PROFILE.md`:
   - Offers allowed in comments (r/forhire `[Hiring]` posts, most "looking for a developer" posts) → comment with the link.
   - Links or self-promotion banned → comment with the help only, no link and no number; if the post says "DM me", a short
     DM is fine.
   - Commercial offers banned altogether → skip the post.
4. **Not already contacted**: no row for this author in `PIPELINE.md` in the last 30 days, and not in `DO-NOT-CONTACT.md`.
5. **Within today's limits**: at most **8 comments a day**, at least 20 minutes apart, never two in the same subreddit
   within an hour.

## Write the comment (60-110 words)

1. **Line 1 — their exact need**, using their words (name the thing: "a booking site for your clinic", "a Shopify store
   that loads fast on mobile"). Optional greeting: "Hi u/<username>,".
2. **Lines 2-3 — real help, free**: one or two concrete, correct tips that answer the post even if they never contact
   you (what to look for in a developer, a sensible stack, what to prepare, a common mistake to avoid). Only facts you're
   sure of; no invented numbers or clients.
3. **Line 4 — who we are, honestly**: "We're Vintoria, a digital product studio — we do exactly this (<catalog service
   name>)." One service, named as the catalog does. A real result only if it is in `SELLER-PROFILE.md`.
4. **Last line — the contact sign-off** from `../../vintoria-sales/references/vintoria-contact.md` with a pre-filled WhatsApp link about their post.

Rules: no price (unless the profile has one and they asked), no booking link, no emojis, no "DM me", no copy-paste —
every comment opens differently and refers to details only this post has (run the deletion test: remove their details;
if the comment fits any post, rewrite it). Match their language — an Indian buyer writing in Hinglish gets a polite
Hinglish/English mix.

### Example (r/smallbusiness, "Need a website for my physiotherapy clinic in Pune, what should I look for?")

> Hi u/neha_physio — for a clinic site the two things that bring patients are online appointment booking and a Google
> Business Profile that links to it, so ask any developer how they'd handle both. Keep it to 4-5 pages (services,
> doctors, booking, location, contact) and make sure it loads fast on phones, since most patients will open it there.
>
> We're Vintoria, a digital product studio — booking websites for clinics are exactly what we build
> (028 Booking Platform Development). Happy to share a simple plan.
>
> — Vintoria · [WhatsApp: +91 87660 33979](https://wa.me/918766033979?text=Hi%20Vintoria%2C%20I%20saw%20your%20reply%20on%20my%20clinic%20website%20post) · business@vintoria.org

### Bad (never)
> We are the best web agency!!! 🚀 Websites starting $199. DM now or WhatsApp +918766033979

Why: no help, hype, a price, emojis, a bare unclickable number, and the same text would fit every post.

## After posting

- Log it: `PIPELINE.md` row (stage `contacted`, `source` = subreddit + query, `channel` reddit, the comment URL in
  `HISTORY.md`, `next_action` "Check replies", `next_due` tomorrow) and the comment text in `THREAD.md`.
- Check the post and the Reddit inbox the next day: a reply or a WhatsApp message → `vintoria-reply-book`.
- **No follow-up comments.** One comment per post. If they reply asking for details, continue in that thread or move to
  WhatsApp/email; if not, the lead stays at `contacted` for 7 days, then `nurture`.
- If a comment is removed, or the account gets a warning or a temporary ban: **stop commenting on Reddit**, tell the
  user, and note which rule it broke in `IDEAL-CUSTOMER-PROFILE.md`.
- Never vote on your own comments, never use a second account, never ask others to upvote.
