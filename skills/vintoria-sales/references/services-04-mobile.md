# 04 / Mobile App Development — 20 services
> Catalog scope template: "Mobile product development for {service}, including agreed screens, navigation, device behavior, API connectivity, testing and release support."

## Services
| ID | Service |
|---|---|
| 061 | iOS App Development |
| 062 | Android App Development |
| 063 | Cross-Platform App Development |
| 064 | React Native Development |
| 065 | Flutter Development |
| 066 | Mobile MVP Development |
| 067 | Consumer Mobile Apps |
| 068 | Business Mobile Apps |
| 069 | FinTech Apps |
| 070 | Healthcare Apps |
| 071 | Education Apps |
| 072 | Marketplace Apps |
| 073 | Booking Apps |
| 074 | Social Apps |
| 075 | On-Demand Apps |
| 076 | Subscription Apps |
| 077 | Mobile Commerce Apps |
| 078 | Mobile Dashboard Development |
| 079 | Mobile API Integration |
| 080 | Mobile App Maintenance |

## Who buys this (segments)
- **Founder with a working web product** - buying a native or cross-platform app for a mobile audience. Trigger: mobile web traffic overtaking desktop, or users asking for an app.
- **Retail or D2C brand** - buying a commerce app tied to the existing store. Trigger: a loyalty push, a seasonal campaign, or an app store search result owned by a competitor.
- **Clinic, gym or services chain** - buying booking and reminders in an app. Trigger: no-show cost, phone-only booking, or a franchise launch.
- **Fintech or insurance product team** - buying an app that meets store and security review. Trigger: a partner requirement, a licence milestone, or a security review finding.
- **Education or training provider** - buying a learning app with offline content. Trigger: a course launch, or learners on poor connections.
- **Marketplace operator with two sides** - buying one or two apps for buyers and sellers. Trigger: manual matching, or a new city launch.
- **Field operations company** - buying an internal app for staff away from desks. Trigger: paper forms, or a device fleet already purchased.
- **Owner of an app with poor reviews** - buying a rescue, a rebuild or maintenance. Trigger: reviews naming crashes, or a store warning about an outdated build.

## Buying signals (observable)
1. Store listing shows the last update date is over a year old (080, 061).
2. Recent reviews name a crash, a login loop or data not loading; quote them with dates (080).
3. The app is phone-only and the store page shows no tablet screenshots (078, 063).
4. Website carries an "app coming soon" or a waitlist with no store link (066).
5. Mobile site shows a full-screen "download our app" interstitial before content (067, 075).
6. Careers page advertises a React Native or Flutter role while both store listings are maintained externally (063, 064).
7. App description lists features the website does not mention, or the reverse (067, 077).
8. Store listing names a minimum OS version that is far behind the current release (080).
9. The app requires an account before showing any content or catalogue (067, 072).
10. Booking or checkout in the app ends in a "call us" screen (073, 077).
11. Permissions list includes locations or contacts with no stated feature that needs them (075, 079).
12. Website is responsive but its primary action is "get the app", with no web fallback (063).
13. Reviews mention a missing feature that the web version has (078, 079).
14. A job ad for a mobile developer sits alongside ads for a backend developer for the same product (079).
15. The app exists on one platform only while the site promises both (061, 062).

## Discovery questions
1. Which platform matters first, and which can wait?
2. Which device behaviours are essential: offline, camera, push, location, biometrics?
3. What must the app do that the website cannot?
4. Which backend or API does the app talk to, and who owns it?
5. Who holds the store accounts and the signing certificates?
6. How will updates ship, and who approves a release?
7. Which OS versions and device types must be supported?
8. What happens to the current app if this work does not start?

## Proof-of-work audit angles
1. Record the last update date on each store listing and quote the version notes (080).
2. Read the twenty most recent reviews and quote every crash, login or loading complaint with its date (080).
3. Note the minimum OS version stated on each listing (061, 062).
4. Check whether tablet screenshots exist on the listing and whether the layout adapts (063, 078).
5. Record the permissions declared on the Android listing and the iOS privacy labels (075, 079).
6. Open the mobile website and note whether it is a responsive site, a wrapper or neither (063).
7. Follow the app's advertised primary action as described on the listing and record where it ends (072, 077).
8. Check whether the site and both stores state the same feature list; quote the differences (067).
9. Look for a public changelog or release notes page and record its most recent entry (080).
10. Verify whether an account is required before content is visible, from the listing description and reviews (067).

## Deliverables (what the client receives)
- Screen inventory with navigation map
- Interactive prototype for the agreed flows
- API contract and integration specification
- Offline and device behaviour specification
- QA plan across the agreed device matrix
- Store listing assets and metadata
- Release and rollback checklist
- Maintenance scope covering updates and store requirements

## Common objections
| Objection | Real concern | Reframe | Evidence needed |
|---|---|---|---|
| "Store fees and review make this risky." | Loss of control over release. | Review is a checklist; the work is planned around it and the listing requirements are named up front. | The current store account status and any past rejection notices. |
| "A mobile website is enough." | Cost and maintenance load. | It is enough until the flow needs offline, push or device access; name the flow that fails. | The specific flow and where the web version breaks on a phone. |
| "Our app just needs a small fix." | Not wanting a rebuild. | A fix is the right call when the build and the stack are still supported; the audit shows which. | Access to the code and the store account, plus the current build status. |
| "Cross-platform is the cheap option." | Fear of quality loss. | The choice is per screen and per device feature, not a slogan; scope names the trade-off. | The list of device features the app must use. |
| "Users will find it in the store." | Discovery assumption. | The listing is a product surface: title, screenshots and reviews decide installs. | The current listing traffic and keyword position, from the buyer's own console. |

## Do not sell when
- The buyer cannot hand over the store accounts or signing credentials.
- The request is to avoid store review by shipping a hidden or wrapper build.
- Health, finance or child-directed claims are needed without the buyer's own compliance sign-off.
- No backend, API or data access is available and none can be provided.
- The budget only covers a template reskin of an existing listing.
- The buyer requires a guaranteed store approval or a guaranteed install number.
- The goal is a copy of a competitor app including its content and assets.
