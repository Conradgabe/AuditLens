# AuditLens — smoke-and-mirrors MVP

This is Step 1 of the validation playbook: a demo that **looks like a working
product** without any production infrastructure. Use it to get validation
conversations with compliance officers — not to process real data.

**Everything here is synthetic.** No real transactions, no PII, no client data.
"AuditLens" is a placeholder name — check availability before using it publicly.

## What's in this folder

| File | What it is |
|---|---|
| `dashboard.html` | **The demo.** Self-contained — double-click to open in any browser. Light-mode dashboard with a working left sidebar: **Overview** (navy hero tile, stat tiles, alerts-by-rule chart, needs-review list), **Case queue** (full grouped list), **Reports** (4 STR drafts awaiting sign-off + the auto-filed CTR), and **Rules & policies** (the 5 detection rules with thresholds and per-rule stats). Clicking any case opens its case file — agent memo, evidence with running totals, risk dial, and the STR draft as a paper document with a Copy button; Esc or the back link returns. Every tab and row works — nothing is dead chrome. IBM Plex type loads from Google Fonts when online; falls back gracefully offline. |
| `screenshots/` | Ready-to-send PNGs: `overview.png` (the LinkedIn/DM shot), `case-file.png` (the case file with the STR draft), `reports.png`, `rules.png`. |
| `transactions.csv` | 1,224 synthetic Nigerian fintech transactions over 7 days (Jun 30 – Jul 6, 2026) with planted violations. |
| `audit_findings.json` | The "agent output": alert statistics + 6 case files with justification memos. |
| `generate_data.py` | Regenerates the CSV and JSON (`python generate_data.py`). Seeded — same output every run. |
| `dashboard_template.html` | Dashboard source with a `__AUDIT_DATA__` placeholder. |
| `agent_prompt.md` | Prompt to reproduce the audit **live with Claude on a call** — the counter to "is this real AI output?" |

Rebuild the dashboard after regenerating data:

```
python generate_data.py
python -c "import io; d=io.open('audit_findings.json',encoding='utf-8').read(); t=io.open('dashboard_template.html',encoding='utf-8').read(); io.open('dashboard.html','w',encoding='utf-8').write(t.replace('__AUDIT_DATA__', d))"
```

## The story the demo tells (your talking points)

1. **100% coverage, not samples.** 1,224 transactions audited continuously — where
   a human team samples 5% at month-end.
2. **The funnel is the product:** 38 raw alerts → 34 auto-cleared by the agent with
   written justifications → only 4 reach an analyst. Legacy tools (ComplyAdvantage,
   Hawk AI) stop at the raw alert; the 90% false-positive investigation burden is
   exactly what stays manual today. This is the "alert fatigue" gap.
3. **Every clear is defensible.** Click CASE-2026-0139 (payday false positive):
   the agent cleared it *and wrote down why* — an audit trail, not a black box.
4. **The one-click STR draft.** Click CASE-2026-0141 (structuring): evidence,
   plain-English grounds for suspicion, statutory citations, NFIU-ready draft —
   the 45 minutes of report-writing reduced to a review-and-sign.
5. **Zero-PII posture.** Hashed identifiers only; names/BVNs/card data never leave
   the institution. This answers the data-security objection before it's raised.

The planted scenarios, if anyone asks what the agent caught:

- **CASE-0141 · STR-02** — six transfers of ₦880k–₦985k to one beneficiary in 36h;
  ₦5.62m total, structured under the ₦5m CTR threshold.
- **CASE-0142 · CBM-03** — ₦5.45m in night-time remittances to a UAE beneficiary;
  Cyprus login IP, new device, 0.41 name match.
- **CASE-0143 · VEL-01** — seven transfers to seven never-seen beneficiaries in
  12 minutes (mule-dispersal pattern).
- **CASE-0144 · DOR-04** — dormant ~8 months, then ₦4.2m out in 5 hours from a
  first-seen device.
- **CASE-0139 / CASE-0140** — the auto-cleared false positives (payday routine;
  recurring supplier payment above the CTR line).

## How to use it in outreach (playbook Step 2)

- Attach `overview.png` to the LinkedIn message — it makes the "2-minute
  screenshot" line literal.
- On calls: share your screen with `dashboard.html`. The overview makes the pitch
  itself ("4 cases need your review" out of 38 alerts). Then open CASE-2026-0139
  (an auto-cleared false positive with its written justification), go back, and
  open CASE-2026-0141 (the STR draft). That order sells the funnel.
- Ask, don't pitch: *"What does your current monitoring miss, and what part of your
  week does this not save?"* Then listen.
- If they doubt the AI is real, run the live reproduction from `agent_prompt.md`.

## Honesty and caveats

- **Say it's a demo on synthetic data.** The DEMO badge stays on. You're validating
  demand, not faking traction — compliance people punish overclaiming.
- **Verify the legal citations before client-facing use.** The thresholds and
  references (MLPPA 2022 ₦5m/₦10m CTR thresholds, s.7 24-hour STR rendition to the
  NFIU, CBN AML/CFT/CPF Regulations 2022) are believed correct but were written for
  a mockup — have a compliance professional confirm exact sections and current
  circulars. Getting a citation wrong in front of a compliance officer costs
  credibility.
- **The goal of every conversation** is playbook Step 4: a signed LOI for a paid
  pilot, or a commitment of (dummy) data to test against. "This looks cool" is not
  validation.
