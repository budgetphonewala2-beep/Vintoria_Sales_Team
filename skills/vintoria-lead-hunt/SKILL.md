---
name: vintoria-lead-hunt
description: "Finds people on LinkedIn and Reddit — through the accounts already logged in — who are publicly asking to hire something Vintoria sells: a website, app, SaaS or MVP, UI/UX or branding, an AI chatbot or agent, automation or a CRM, a Shopify store, SEO, ads or social media, in English, Hindi and Hinglish. Searches LinkedIn posts (Latest, past 24 hours) and Reddit (r/forhire, small-business, startup, Indian and niche subreddits), filters out agencies, freelancers, job seekers and job ads, judges every candidate with an exact quote, scores them, grabs the email from LinkedIn (post, contact info, company site) and hands each buyer to outreach — a professional Reddit comment with Vintoria's WhatsApp link, or an email from business@vintoria.org. Use it whenever the user wants leads or clients: 'find leads', 'find people looking for a web developer on Reddit', 'LinkedIn pe clients dhundo', 'leads chahiye', 'kaun website banwana chahta hai', 'hunt for clients this week'."
license: MIT
compatibility: "Instruction-only Agent Skill: no code. Works in any agent or bot (Claude, Grok, GPT, Gemini…) that can follow instructions; best with a browser logged in to LinkedIn and Reddit, and file access."
metadata:
  author: "Vintoria (built on ai-sales-team-claude by Zubair Trabzada)"
  version: "7.0.0"
---

# Vintoria Lead Hunt — LinkedIn and Reddit buyers

Intent beats cold lists: someone who posted "need a website for my clinic" today is worth fifty cold contacts. You
find those posts on LinkedIn and Reddit, separate real buyers from noise, and hand them to outreach before anyone else
answers.

## Before you start

1. **Your files.** Everything lives in plain files — `SELLER-PROFILE.md`, `OFFER.md`, `IDEAL-CUSTOMER-PROFILE.md`,
   `PIPELINE.md`, `DO-NOT-CONTACT.md` and `prospects/<slug>/` (format: `../vintoria-sales/references/pipeline-format.md`). If you can't read or
   write files (a chat bot such as Grok), ask the user to paste `SELLER-PROFILE.md` and the relevant `PIPELINE.md` rows,
   and finish by printing every changed row and file in code blocks for them to save. Mirror every change to the
   connected Google Sheet (`../vintoria-sales/references/sheet-sync.md`) — update by key, never duplicate, never delete.
2. **Vintoria's profile.** Read `SELLER-PROFILE.md`. This skill builds queries, emails or prices from it — if it is
   missing or still full of `[ASK]`, run `vintoria-setup` first (in a hurry: ask only the missing answers in one message).
3. **What Vintoria sells.** 270 services in 12 disciplines — `../vintoria-sales/references/service-catalog.md`. Name a service exactly as the
   catalog does (`192 Shopify Development`), never invent one, and never quote a price, discount or date that isn't in
   `SELLER-PROFILE.md` — write `[PRICE TO CONFIRM]` (`../vintoria-sales/references/pricing-policy.md`).
4. **Platforms.** Leads come only from **LinkedIn and Reddit**, through the accounts already logged in on this machine.
   Open a page before you state a fact from it and note its URL and date; a search snippet alone is not a fact. If you
   can't open something, write "Not found".
5. **Facts only.** Every sentence traces to a page you opened, the prospect's own words, a fact you observed on their site,
   the catalog or the profile — never to memory. Never say something was sent, posted, booked or verified unless it
   really happened. Run the self-check in `../vintoria-sales/references/truth-rules.md` before anything goes out.
6. **Contact details** — Vintoria: `business@vintoria.org`, WhatsApp +91 87660 33979 (`https://wa.me/918766033979`);
   Radian Marketing: `amar@radianmarketing.site` — and every sign-off come only from `../vintoria-sales/references/vintoria-contact.md`. Each
   brand's emails carry that brand's real identity (`../vintoria-sales/references/brands.md`).
7. **The team.** Read `TEAM-BOARD.md` before you start and handle messages to your role; `CLAIM` a lead before working it,
   hand off with full context, post `ALERT`s at once (`../vintoria-sales/references/team.md`). Alone, you play every role with the same files.

## Steps

1. **Aim.** Read `OFFER.md` (lanes and entry services) and the saved queries in `IDEAL-CUSTOMER-PROFILE.md`. Hunt one lane
   at a time. Catalog discipline → what buyers write:
   | Discipline | Buyers write |
   |---|---|
   | 02 Web, 03 SaaS | "need a website", "website redesign", "web developer", "build our platform / portal / MVP" |
   | 04 Mobile | "need an app", "app developer", "Flutter / React Native developer" |
   | 05 UI/UX, 06 Branding | "need a logo", "rebrand", "UI UX designer", "redesign our app" |
   | 07 AI Development | "AI chatbot", "AI agent", "chatbot for my website", "add AI to" |
   | 08 Business Automation | "automate", "Zapier / Make / n8n expert", "need a CRM", "manual data entry" |
   | 10 E-Commerce | "Shopify developer", "online store", "start selling online" |
   | 11 Marketing & SEO, 12 Growth | "SEO agency", "rank on Google", "run ads", "more leads", "social media manager" |
   | Hinglish | "website banwana hai", "app banwana hai", "developer chahiye", "koi SEO wala batao", "chatbot banwana hai" |
2. **Search, newest first** (`references/queries.md` has every query and subreddit):
   - **LinkedIn** — Posts, sort **Latest**, date posted **past 24 hours**, the boolean queries
     (max 5 operators). For each hit note: author, headline, profile URL, post URL, post date.
   - **Reddit** — r/forhire (`flair:Hiring`), r/smallbusiness, r/Entrepreneur, r/startups, r/indianstartups and Indian city
     subs, r/shopify, r/ChatGPT / r/automation, niche owner subs; sort **New**, past day (24 hours). For each hit note: username,
     post URL, age, comment count, and the subreddit's rule on self-promotion.
   **Freshness wins the client:** under 24 hours only, by the age shown on the post (`1d` = too old) —
   `../vintoria-sales/references/lead-quality.md`. Skip every URL already in `SEEN.md`; add each one you judge.
3. **Judge every candidate** with `references/intent-rubric.md`: buyer / seller / job_seeker / other, what they want (as a
   catalog service where clear — "AI chatbot for my clinic" → `123 AI Chatbot Development`), urgency, budget (only if
   stated), location, and an **exact quote** that proves intent. Drop anything under confidence 0.7.
4. **Score** with the value score in `../vintoria-sales/references/lead-quality.md` (must-haves first, then 0-100);
   valuable = 65+. Hourly 24/7 hunting runs through `vintoria-hourly-run`; this skill is the deeper one-off hunt.
5. **Contact path:**
   - **LinkedIn** → find the email: the post, the profile's **Contact info**, then their company website (contact/about
     pages). Found → status `published`, outreach by email. Not found → a LinkedIn comment or connection note.
   - **Reddit** → a public comment on the post with Vintoria's WhatsApp link (if the subreddit allows offers); a DM only if
     the post says "DM me".
6. **Add to `PIPELINE.md`** — stage `new`, `channel` (linkedin-email / linkedin-comment / reddit-comment), `source` = the
   query, slug = their website, or `name@linkedin` / `username@reddit`. Put the exact quote, post URL and date in
   `prospects/<slug>/HISTORY.md`. Check `DO-NOT-CONTACT.md` and skip anyone already contacted in the last 30 days.
7. **Hand over, freshest first:** strong buyers with a company site → a quick dossier (`vintoria-prospect-research`, the
   site audit gives the best hook); then `vintoria-outreach` (Reddit comment playbook or LinkedIn email).
8. **Report:** a table — buyer, platform, what they need (+ catalog service), exact quote, posted, score, contact path,
   done / next step.

## Rules
- The quote is copied exactly from the post. No quote = not a buyer.
- Agencies, freelancers offering services, "#hiring" job posts and job seekers are never buyers.
- Only public posts and what the logged-in account can normally see; no bulk scraping.
- Respect the limits in `SELLER-PROFILE.md` → Automation, counted for all bots together in `RUN-LOG.md`.
- Speed beats polish on intent leads: most asks get answered within a day or two.

## References (read when you reach that step)

- `references/intent-rubric.md` — 30 labelled examples (English + Hinglish): buyers, sellers, job seekers, spam
- `references/queries.md` — LinkedIn boolean queries, the subreddits to search and how, hidden-intent searches
