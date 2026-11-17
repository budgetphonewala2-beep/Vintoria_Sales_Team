# From audit fact to outreach hook

Pick facts that touch money: getting found, looking trustworthy, and making it easy to contact or buy.
State the fact exactly as the audit does. Any consequence must be phrased as likely, never as a measurement.

| Audit fact (`key`) | Why an owner cares | Example hook (respectful, specific) |
|---|---|---|
| `viewport` = false | Most visitors are on phones | "Your homepage doesn't set a mobile viewport, so on phones it probably shows the shrunken desktop layout." |
| `cta` = false | Visitors don't know the next step | "I couldn't find a clear 'Get a quote' or 'Book now' button on your homepage." |
| `contact_form` = false and `click_to_call` = false | Leads have no easy way in | "There's no contact form or tap-to-call link on the homepage — interested visitors have to hunt for a way to reach you." |
| `whatsapp_link` = false (India/UAE/LatAm SMBs) | Customers expect WhatsApp | "There's no WhatsApp chat link — for a local business that's often the fastest way customers reach out." |
| `copyright_year` old (2+ years) | Site looks unmaintained | "Your footer still says © 2019, which can make visitors wonder if you're still active." |
| `response_time_ms` > 3000 | Slow pages lose visitors | "Your homepage took 4.2 seconds to download in my test." (quote the number exactly) |
| `meta_description` missing | Weak Google snippet | "Your homepage has no meta description, so Google picks its own snippet for your listing." |
| `title` generic ("Home") | Weak search presence | "Your homepage title is just \"Home\", which doesn't tell Google what you do or where." |
| `h1_count` = 0 or > 1 | Unclear page topic | "The homepage has no main H1 heading." |
| `images_missing_alt` high | Accessibility + image search | "12 of 15 images on your homepage have no alt text." |
| `broken_internal_links` > 0 | Dead ends | "Two links on your homepage lead to error pages (e.g. /services/seo)." |
| `http_redirects_to_https` = false | Browser warnings | "The http:// version of your site doesn't redirect to HTTPS." |
| `tech` = Wix/Squarespace + growth goals | Platform limits | Mention only if it relates to their stated need; never mock a platform. |

## Rules
- One observation per first email — the strongest one for THIS business. Save others for follow-ups.
- Never attach a full audit to a cold email; offer it ("happy to send the 5 other things I noticed").
- Never invent impact numbers ("you're losing 40% of visitors"). If a number isn't in the audit, it doesn't go in.
- Good news counts too: "Your site loads fast and has a clear booking button — the gap I noticed is..."
