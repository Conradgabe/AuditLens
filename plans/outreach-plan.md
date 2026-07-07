# Outreach Plan — Validation Step 2

Goal: **10 conversations with compliance professionals in 2 weeks**, converting to
at least **1 "skin in the game" commitment** (a signed LOI for a paid pilot, or a
dummy dataset to test the engine against). "This looks cool" does not count.

---

## 1. Build the target list (Day 1–2)

**Who:** the people who feel the pain daily — not CEOs.

| Priority | Titles to search on LinkedIn |
|---|---|
| 1 | Head of Compliance, Chief Compliance Officer (CCO) |
| 2 | Head of Risk, Chief Risk Officer (CRO) |
| 3 | AML Manager, Transaction Monitoring Lead, Fraud & Risk Lead, MLRO |

**Where (Nigeria — primary):** mid-sized fintechs, digital lenders, wallets, and
microfinance banks. Big enough to feel alert fatigue, small enough that the
compliance lead reads their own DMs. Examples: Moniepoint, OPay, PalmPay, Kuda,
FairMoney, PiggyVest, Carbon, Renmoney, Baxi, TeamApt ecosystem companies.
Add 2–3 reaches at Paystack / Flutterwave / Interswitch.

**Where (foreign — secondary, 5–10 contacts):** UK/US digital banks and EMIs, to
test the foreign-market message. Expect slower replies and a data-trust objection;
lead with "runs in your environment, zero-PII."

**Quota:** 25–30 named people in the tracker before sending anything.

---

## 2. The messages

### 2a. Connection request note (≤300 characters — hard LinkedIn limit)

> Hi [Name] — I'm a software engineer building an agent that auto-investigates
> AML alerts and drafts NFIU-ready STRs, to kill false-positive fatigue. Not
> selling anything — I'd value 10 mins of your expert read on whether it fits
> real compliance workflows.

### 2b. After they accept (DM, attach `screenshots/overview.png`)

> Thanks for connecting, [Name]. Quick context: most monitoring tools stop at the
> raw alert — your team still investigates every false positive and writes every
> report. I'm building AuditLens: an agent that audits 100% of transactions,
> investigates each alert itself, clears the false positives *with a written
> justification retained for audit*, and pre-drafts the STR for the real ones.
>
> Attached is the dashboard from a demo week on synthetic data: 38 alerts → 34
> auto-cleared → 4 for human review, with the NFIU report drafts ready to sign.
>
> I'm not selling — this is early and I'm validating with people who live this
> daily. Could I get 10–15 minutes this week for your honest read on what this
> gets right and what it misses?

### 2c. Bump (4–5 days after 2b, no reply)

> Hi [Name] — I know compliance weeks are brutal, so one-line version: would an
> agent that cleared ~90% of your false-positive alerts *and documented why* be
> useful, or is the real pain somewhere else? Even a one-word answer helps me.

### 2d. Breakup (7 days after 2c, no reply — then move on)

> No response needed, [Name] — closing the loop so I'm not noise in your inbox.
> If alert fatigue or STR drafting ever becomes the fire of the week, happy to
> show what we've built. Good luck with the quarter.

**Rules:** personalize the first line when their profile gives you something
real; never send more than these 3 follow-ups; send 5–8/day (LinkedIn throttles
bursts); log every send in the tracker the moment it goes out.

---

## 3. The call (Step 3 — diagnose, don't pitch)

15 minutes. Talk max 30% of the time. Order matters: **questions first, demo
second** — showing the product first contaminates their answers.

**Opening questions (verbatim):**
1. "Walk me through what happens at your company when a transaction gets flagged
   — who touches it, and how long does it take end to end?"
2. "What's the most manual, frustrating part of your weekly compliance workflow?"
3. "Roughly how many hours a week does your team spend investigating alerts that
   turn out to be nothing?"
4. "When you do file an STR, how long does drafting and internal sign-off take?"

**Then the demo** (screen-share `demo/dashboard.html`, under 3 minutes, in this order):
overview hero → an auto-cleared case with its justification memo (CASE-2026-0139)
→ the structuring case and its draft STR (CASE-2026-0141) → Rules screen if they
ask "what does it check?"

**Closing questions:**
5. "What did this get wrong about how your team actually works?"
6. "If this flagged and drafted exactly like you just saw, what would stop you
   from deploying it tomorrow?" *(their answer = your real roadmap)*
7. **The ask:** "If I stand up a pilot on sandboxed or dummy data next month,
   would you run it? What would a fair pilot price be?"

**Objection notes:**
- *"We can't share data"* → Zero-PII ingestion, hashed IDs only; or fully
  on-prem/sandboxed; or run it on their dummy data.
- *"How do I trust the AI's clearances?"* → The agent never makes the final call;
  every clearance has a written justification retained for audit; humans sign
  everything that leaves the building.
- *"We already use [ComplyAdvantage / Hawk / etc.]"* → "Perfect — what does it
  still leave on your desk every day?" (That gap is the product.)

---

## 4. Tracking (the only dashboard that matters now)

One spreadsheet, one row per person:

| Column | Values |
|---|---|
| Name / Title / Company | — |
| Segment | NG fintech · NG MFB · Foreign |
| Connection sent / accepted | dates |
| DM sent / Bump / Breakup | dates |
| Call held | date |
| Top pain (their words) | free text |
| "What would stop you" answer | free text |
| Outcome | No reply · Not a fit · Interested · **Pilot ask** · **LOI signed** · **Data committed** |

**Weekly targets:** 25 connection requests → expect ~10 accepts → ~5 calls →
repeat. Two weeks ≈ 10 calls.

**Success bar for this phase:** 1+ LOI or data commitment, and the same pain
named unprompted in 5+ calls. If 10 calls produce neither, the finding is real
too — revisit the wedge (maybe the product is the STR drafter alone, or the
false-positive investigator alone) before writing more code.

---

## 5. Prep checklist (before the first send)

- [ ] LinkedIn profile headline says what you're building (people check before accepting)
- [ ] Demo walkthrough rehearsed to < 3 minutes
- [ ] `screenshots/overview.png` + `screenshots/case-file.png` ready to attach
- [ ] Tracker sheet created with the 25–30 names
- [ ] Calendar link (Calendly or similar) for frictionless booking
- [ ] Live-reproduction fallback ready (`docs/agent_prompt.md` + a `data/transactions.csv` slice) for "is the AI real?"
