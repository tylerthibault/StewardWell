# StewardWell — Product Roadmap

> **Vision:** A calm, intentional family chore ledger. The app tracks the work; real life is the reward.
> No streaks. No badges. No notification hooks. Just a fair record the whole family can trust.

---

## Philosophy

StewardWell sits at the intersection of **responsibility** and **real-world reward**. Parents define the rules. Kids do the work. The app keeps the score. The kiosk mode turns any iPad into a shared family bulletin board — always on, always accurate, zero screen-time temptation built in.

---

## Current State (as of v0.1)

| Area | Status |
|---|---|
| User auth (register / login / logout) | ✅ Done |
| Family creation & child profile management | ✅ Done |
| Chore CRUD — name, description, coins, points, priority, due date, recurring days | ✅ Done |
| Chore assignment (child or adult) | ✅ Done |
| Chore status workflow: `pending → submitted → completed / rejected` | ✅ Done |
| Family Store — individual rewards (coins), family rewards (points), conversion items | ✅ Done |
| Family points pool — add / subtract / set | ✅ Done |
| Kiosk base — idle screen, child select, PIN entry / first-time setup, child board, parent exit | ✅ Done |
| Kiosk UI polish — shared CSS, glassmorphism, live clock, animations, priority borders | ✅ Done |

---

## Milestones

---

### Milestone 1 — Kiosk End-to-End (MVP Playable)
> **Goal:** A family can sit down with an iPad, enable kiosk mode, and kids can claim chores from start to finish with coins actually awarded.

**Why this first:** The kiosk experience is the core differentiator. Right now `child_done` clears the session but doesn't actually process the chore claim — coins are never awarded and parents have no approval queue.

| # | Feature | Notes |
|---|---|---|
| 1.1 | **Fix chore claim → submit** | `claimChore()` on kiosk should call `ChoreLogic.submit_chore()`, not just redirect. Status moves to `submitted`. |
| 1.2 | **Parent approval queue** | New view: list of all `submitted` chores across all children. One-tap approve or reject. |
| 1.3 | **Coin award on approval** | `approve_chore` awards `chore.coin_amount` to `child.coins`. Currently only adds family points. |
| 1.4 | **Kiosk chore state refresh** | After claim, child board shows a "Submitted — waiting for approval" state instead of vanishing the card. |
| 1.5 | **Submitted chores on dashboard** | Parent dashboard shows a badge/count of pending approvals. |

**Exit criteria:** Kid taps a chore on the iPad → parent sees it in the queue → approves → kid's coin balance updates.

---

### Milestone 2 — Reward Redemption
> **Goal:** Coins and family points have somewhere to go. Kids can spend; families can celebrate.

| # | Feature | Notes |
|---|---|---|
| 2.1 | **Individual reward redemption (kiosk)** | Child views their coin balance + available rewards on the child board. Tap to redeem, deducts coins. |
| 2.2 | **Reward redemption confirmation** | Parent must confirm real-world delivery ("Movie night approved!") before coins are deducted. Or auto-deduct with a redemption log. Decide with Tyler. |
| 2.3 | **Family reward redemption (parent dashboard)** | Parent spends family points on a family reward. Logs the event. |
| 2.4 | **Coin / point transaction ledger** | Per-child history: earned X coins for "Take out trash" on DATE. Per-family history: redeemed Y points for "Pizza night". |
| 2.5 | **Coin → family points conversion (kiosk)** | Child can convert personal coins to family points using a conversion item. Currently exists in store logic but has no kiosk UI. |

**Exit criteria:** A child can see their coins, pick a reward, and the parent sees a redemption event in the ledger.

---

### Milestone 3 — Photo Proof
> **Goal:** Kids snap a photo when claiming a chore. Parents see the photo before approving. Ends "but I did do it!" arguments.

| # | Feature | Notes |
|---|---|---|
| 3.1 | **Camera capture on chore claim (kiosk)** | Tap chore → camera opens (HTML5 `getUserMedia`) → snap → preview → confirm claim with photo attached. |
| 3.2 | **Photo storage** | Save to `/uploads/chore_proofs/<chore_id>_<timestamp>.jpg`. Add `proof_photo` column to Chore model. |
| 3.3 | **Photo in approval queue** | Parent sees the photo alongside approve/reject buttons. |
| 3.4 | **Photo optional flag** | Per-chore toggle: "Require photo proof." Some chores don't need it (e.g. "Be kind today"). |

**Exit criteria:** Parent can visually verify a chore was done before awarding coins.

---

### Milestone 4 — Parent Dashboard Polish
> **Goal:** The parent view is functional but sparse. Give parents the overview they need at a glance.

| # | Feature | Notes |
|---|---|---|
| 4.1 | **PIN management UI** | Per-child: view/reset PIN from Family Management. Parents can set or clear a child's PIN. |
| 4.2 | **Dashboard summary cards** | Pending approvals count, total family points, each child's coin balance — all visible without navigating away. |
| 4.3 | **Chore history per child** | Filter chore center by child + status. Show completed history with timestamps. |
| 4.4 | **Bulk chore actions** | Approve all submitted chores at once. Mark recurring chore as skipped this week. |
| 4.5 | **Child profile improvements** | Edit child name, avatar color, deactivate a child (hide from kiosk without deleting). |

**Exit criteria:** Parent can manage the full family in under 2 minutes without hunting through multiple pages.

---

### Milestone 5 — Recurring Chores & Scheduling
> **Goal:** The app keeps itself fresh. Recurring chores reset automatically so the kiosk is always current.

| # | Feature | Notes |
|---|---|---|
| 5.1 | **Auto-reset recurring chores** | After a recurring chore is completed, it resets to `pending` on its next scheduled day. Needs a background job (APScheduler or simple cron check at app start). |
| 5.2 | **Chore schedule view** | Calendar-style list: "These chores are due this week." Grouped by day. |
| 5.3 | **Chore template library** | Pre-built chore suggestions parents can add in one click: "Take out trash", "Vacuum living room", "Set the table", etc. |
| 5.4 | **Due-date overdue highlighting** | Overdue chores show red on parent dashboard and on the kiosk child board. |

**Exit criteria:** A family can set up recurring chores once and the kiosk stays accurate week over week without parent intervention.

---

### Milestone 6 — Onboarding & First-Time Experience
> **Goal:** A new family can go from signup to a working kiosk in under 5 minutes.

| # | Feature | Notes |
|---|---|---|
| 6.1 | **First-time setup wizard** | Step-by-step: Create family → Add children → Add 3 starter chores → Enable kiosk. Skip-able at any step. |
| 6.2 | **iPad PWA install prompt** | "Add to Home Screen" banner on `/kiosk/` so the iPad installs it as a full-screen app. Requires manifest.json + service worker stub. |
| 6.3 | **Empty state guidance** | When the chore list / store is empty, show friendly prompts ("Add your first chore →"). |
| 6.4 | **Kiosk mode tutorial overlay** | First time entering kiosk mode: brief animated guide showing where to tap. Dismissable. |

**Exit criteria:** A non-technical parent can self-onboard without reading any documentation.

---

### Milestone 7 — Future Considerations
> These are valuable but not blocking the core experience. Revisit after M6 ships.

| Feature | Notes |
|---|---|
| **Push notifications (parent)** | When a child submits a chore, parent gets a notification on their phone. Requires PWA service worker + push subscription. |
| **Multi-parent household** | Second parent account linked to same family with equal admin rights. Currently only one user per family is assumed. |
| **Family activity export** | Export last 30 days of chore history as CSV or PDF. Useful for school or chore charts. |
| **Seasonal / bonus chores** | Parent can create a "Holiday Bonus" chore worth extra coins for a limited time. |
| **Child spend history (kiosk)** | Kid can review their own coin history on the kiosk without parent access. |
| **Soft time-lock** | Parent can set a time window when kiosk is active (e.g. 3pm–8pm). Outside that window it shows a "Check back after school" screen. |

---

## Milestone Summary

| Milestone | Theme | Approximate Scope |
|---|---|---|
| **M1** — Kiosk End-to-End | Core loop works | 5 features |
| **M2** — Reward Redemption | Coins have meaning | 5 features |
| **M3** — Photo Proof | Accountability | 4 features |
| **M4** — Dashboard Polish | Parent experience | 5 features |
| **M5** — Recurring & Scheduling | Self-maintaining | 4 features |
| **M6** — Onboarding | First-time UX | 4 features |
| **M7** — Future | Nice to have | 6 ideas |

---

## Open Questions

- **Reward redemption flow (2.2):** Auto-deduct coins when child taps "Redeem" and parent confirms in real life later? Or require parent to approve the redemption in the app first?
- **Photo storage (3.2):** Local filesystem (fine for self-hosted) or object storage (S3/Cloudflare R2) for a hosted version?
- **Recurring chore reset (5.1):** APScheduler running inside Flask, or a simple "check on each kiosk load and reset if past due"?
- **Multi-parent (M7):** Is there a second adult in the home who needs app access, or is one parent account sufficient for v1?

---

*Last updated: 2025-05-29 | Branch: `feature/kiosk-mode-auth`*
