# Prefilter — skip the obvious noise in seconds, read only the posts worth reading

Most posts a LinkedIn search returns are agencies advertising, job ads, people looking for work or advice posts. Judging
each of them carefully wastes the run. This check takes a few seconds per post: read the **first lines** and apply the
rules below. Only posts that survive get the full judgement (`intent-rubric.md` + `../../vintoria-sales/references/lead-quality.md`).

**The one rule that protects real buyers:** if the post contains **any buyer phrase**, never skip it here — the full
judgement decides (genuine buyers also write "hiring", "budget", "DM me if you know someone"). The only exception: a
buyer phrase together with **5+ hashtags and seller or job-seeker wording** is reach-bait — skip it.

## Buyer phrases (any one → keep for full judgement)
looking for · need a · need an · need someone · need help with · anyone know · anyone recommend · can you recommend ·
can anyone recommend · recommendations for · do you know anyone · in need of · seeking a · seeking an ·
looking to hire · want to hire · we are looking · we're looking · we need · our company needs · our team needs ·
hire an agency · hiring an agency · outsource our · need an outside team · who can handle · who can help ·
dm me if you know · send me recommendations · agency chahiye · koi batao · banwana hai

## Skip (only when NO buyer phrase is present)

| Type | Tell-tale wording |
|---|---|
| **Agency / seller** | we offer · we provide · we specialize · our agency can help · we help brands · book a call · free consultation · free audit · get a quote · contact us · dm me for · dm to book · limited spots · link in bio · we are a leading · we are a team of · our mission is · i help businesses · i help brands · my services include |
| **Job ad** | #hiring · now hiring · we're hiring · we are hiring a · apply now · apply here · send your resume · send your cv · job opening · open position · full-time position · salary range · benefits package · years of experience |
| **Job seeker** | open to work · #opentowork · available for projects · available for freelance · available for work · seeking new opportunities · seeking new clients · hire me · my portfolio · freelance for hire |
| **Talent marketplace / recruiter** | join our network · join our platform · talent pool · we place · staffing agency · vetted network · submit your portfolio · register as a freelancer |
| **Advice / engagement** | "5 tips…", "top 10", "lessons learned", "pro tip", "mistakes to avoid", "save this for later", "in this episode", "why your X is…" |
| **Hashtag wall** | 5 or more hashtags and no buyer phrase |

## Also skip, whatever the wording
- **Already filled:** "found our agency", "update: hired", "position filled", "contract awarded", "no longer looking",
  "thanks everyone, we found…".
- **Deleted or unavailable:** "this post is unavailable", "post not found", "this content isn't available".
- **Already handled:** the post URL is in **Seen** or **Leads** (any PC).

## Read the most promising first
After the prefilter, sort what's left: posts with a strong ask ("we are looking for an agency", "hiring an agency",
"outsource our…") → a date, budget or scope in the first lines → newest → fewest comments. The run reaches its 8 sooner
and stops reading.

## Record why
Every skipped post goes into **Seen** with its reason (`prefilter: seller`, `prefilter: job ad`, …). These counts are what
`queries.md` → "When yield is low" uses to fix the searches.
