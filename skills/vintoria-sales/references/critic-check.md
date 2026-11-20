# Critic check — the last gate before anything is posted or sent

The agent that wrote a message is the worst judge of it. Before posting, switch roles: read the message fresh, as a strict
reviewer who wants to reject it, and answer every line with **yes** or **no**. One "no" = fix it and check again; still
"no" after two rewrites = skip the lead and note why. On Hermes the check runs in a fresh-context `delegate_task` sub-agent
(`team.md`, "Review").

## Every message

- [ ] The lead passed `lead-quality.md` (buyer, under 24 h, valuable, not seen, not claimed by another PC).
- [ ] It opens with **their** exact need, in their words — not with "We" or "I".
- [ ] Deletion test: remove their name and details — it no longer fits anyone else's post.
- [ ] Every fact traces to their post, their page, the catalog or the profile (`truth-rules.md`). No invented client,
      number, result, price or date.
- [ ] Signed by the right person: Vintoria = **Pratik Patil, Co-founder** (no other name anywhere); Radian = Amar.
- [ ] Exactly one Vintoria service, named as the catalog does; no list of services.
- [ ] Says openly that it's Vintoria.
- [ ] Contact details exactly as `vintoria-contact.md`: `business@vintoria.org`, `https://wa.me/918766033979…`.
- [ ] No banned phrase (`I hope this finds you well`, `I came across your`, `touching base`, `game-changer`, `leverage`,
      `seamless`, `cutting-edge`, `elevate`, `unlock`, `best agency`, `guaranteed`), no emoji, no `!!`, no ALL CAPS.
- [ ] No sentence over 28 words. Plain, professional, warm.
- [ ] Not the same opening line as any message sent in the last 7 days (check `THREAD.md` / `RUN-LOG.md`).
- [ ] Language matches theirs (English, or polite Hinglish if they wrote Hinglish).
- [ ] Not in `DO-NOT-CONTACT.md`; within the hourly limit in `RUN-LOG.md`.


## LinkedIn email, also

- [ ] Sent to an email they published (post, contact info, company site) — never a guess.
- [ ] Subject 2-5 words, lower case, about them; no fake "Re:".
- [ ] Under 120 words (follow-ups shorter), one soft question as the CTA, no link except the WhatsApp line in the signature.
- [ ] Signature with postal address and the opt-out line (`vintoria-contact.md`).
- [ ] It's between 08:00 and 19:00 on a weekday in **their** time zone — otherwise queue it for their morning.
- [ ] The right brand: sender, signature, address and contact line all belong to the same brand (`brands.md`); it doesn't
      mention the other brand; no other email to this person today; at most 4 in the last 7 days across both brands;
      the other brand hasn't received a reply or opt-out from them.
- [ ] Second agency's email: a fact or angle not used in the first agency's email to this person; Radian's own service names
      (`radian-profile.md`), not Vintoria catalog IDs.
- [ ] Proof stays in its brand: no Radian client, testimonial or case study in a Vintoria message, and the reverse; no
      `[TO CONFIRM]` item from `radian-profile.md`.
- [ ] The first agency's email 1 goes out Monday-Thursday in their time zone (so the second agency's lands the next
      working day).

## LinkedIn comment / connection note / message, also

- [ ] The author is looking for an agency or outside team (agency intent `agency`, `open` or `switching`, `lead-quality.md`).
- [ ] Comment 40-80 words: their need restated, one or two real approach points, who we are once, one easy question
      (`../../vintoria-outreach/references/comment-angles.md`); none of "DM'd you", "check your inbox", "we'd love to help".
- [ ] Signed `— Pratik Patil, Co-founder, Vintoria · business@vintoria.org`; no WhatsApp link, no price, no "DM me".
- [ ] No other Vintoria comment on this post; at least 10 minutes since the last Vintoria comment.
- [ ] Connection note ≤ 300 characters, no link; the message after they accept is 2-3 lines and may carry the WhatsApp link.

Record the result in one line: `Critic: pass (12/12)` or `Critic: fail — <which line>`.
