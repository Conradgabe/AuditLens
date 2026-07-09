# Call Q&A prep - Validation Step 3

Draft answers for the questions most likely to come up on the 15-minute calls.
Read alongside `DEMO_GUIDE.md` (talking points and demo order) and
`plans/outreach-plan.md` (the interview script this supports).

**Ground rule for all of these:** where the honest answer is "I don't know yet"
or "that's not built," say that plainly. This is a validation MVP - the goal of
the call is to learn what they need, not to convince them it's finished.
Overclaiming to a compliance officer costs more credibility than any single gap
in the product.

---

## About the model / methodology

**"What's the metric behind the risk score?"**
See the dedicated section in `DEMO_GUIDE.md`. Short version: illustrative today,
not a calibrated model. Sketch the plausible signal-count / baseline-deviation /
threshold-proximity shape if pushed, but don't claim it's built.

**"Is this rule-based or machine learning?"**
Rule-based today - five explicit pattern rules (VEL-01 through CTR-05), each with
a defined threshold or signal combination. ML-based scoring would need labeled
outcome data (confirmed STRs vs. confirmed false positives) to train against,
which doesn't exist yet. That's a phase-2 conversation, not a phase-1 claim.

**"How do you know the agent's justification memos are actually correct, not
just plausible-sounding text?"**
Fair challenge. Today, the memos are generated from the same structured evidence
shown in the case file (transaction IDs, timestamps, amounts, the specific
pattern matched) - so they're grounded in the underlying data, not
free-invented. But nothing has been through a real accuracy audit against expert
review yet. That's part of what a pilot would validate: have your analysts spot
check a sample of memos against their own judgment and tell me the error rate.

**"What happens when the agent gets it wrong - clears something that was
actually suspicious, or escalates something that's actually fine?"**
Two different failure modes, worth answering separately:
- *False clearance (the dangerous one):* this is the core risk of the auto-clear
  design, and honestly the central thing to validate with your team - see the
  "auto-clear without pre-approval" question below.
- *False escalation:* low-cost - a human reviews and dismisses it, same as any
  legacy tool's false positive today, just with less work per review.

**"Does this replace our existing transaction monitoring system, or sit next to
it?"**
Sits next to it, at least initially. The wedge is investigation and reporting,
not detection - most institutions already have a TM system generating alerts;
this is aimed at what happens after the alert fires. If their real pain is
detection quality, not investigation load, say so and treat it as a finding, not
a rebuttal.

---

## About trust and control

**"How do I trust the AI's clearances?"**
Don't pre-answer this with a reassuring line - let it surface naturally, ideally
via your own closing question ("what would stop you from deploying it
tomorrow?"). When it comes up, be precise: nothing reaches NFIU without a human
signature on the STR side. The auto-clear step itself is not currently
pre-approved by a human before disposition - only logged and sample-auditable
after the fact. Ask them directly whether that's acceptable to their MLRO, or
whether they'd need pre-disposition sign-off on some sample of clearances. Their
answer is real product direction, not an objection to overcome.

**"Who's liable if the agent clears something that turns out to be money
laundering?"**
Say plainly: that's a real open question, and it's exactly the kind of thing
that would need to be worked out with their legal/compliance team before any
pilot goes near real dispositions, let alone production. Institutional
liability doesn't transfer to a vendor's software by default - this needs a
real answer, not a hand-wave, and you don't have it yet.

**"Can a human override or reopen a case the agent auto-cleared?"**
This is a reasonable requirement to commit to even at MVP stage: yes, every
auto-cleared case should remain visible and reopenable, not silently closed.
If the current demo doesn't make that reopening flow obvious, flag it as
something you'd build before a pilot, not after.

---

## About data and security

**"We can't share customer data with a third party."**
Zero-PII posture: hashed customer/account identifiers only - names, BVNs, and
card data never leave the institution in the current design. Also offer: fully
on-prem or sandboxed deployment, or running against their own dummy/synthetic
data for the pilot, same as this demo does.

**"Where would this actually run - your servers, ours, cloud?"**
Genuinely undecided at this stage - say so. This is a validation MVP with no
production infrastructure. Deployment model (on-prem, VPC, hosted) is a
pilot-design question you'd solve with them, shaped by their own data
residency and NDPA requirements.

**"Does this comply with NDPA (Nigeria Data Protection Act)?"**
The zero-PII design is meant to reduce NDPA exposure by never ingesting
identifiable data in the first place, but this hasn't been reviewed by a data
protection specialist. Don't claim compliance - say that's a pre-pilot
checkbox, not a solved problem.

---

## About regulation

**"Are the legal citations accurate?"**
Yes, checked against primary and authoritative sources: the ₦5m/₦10m CTR
threshold (MLPPA 2022 s.2), the 24-hour STR rendition window (MLPPA 2022
s.7(2)(1)(a), confirmed directly against NFIU's own December 2024 STR
Guidelines), and the CBN AML/CFT/CPF Regulations 2022 as a real instrument. If
someone says they've seen a 7-day STR window elsewhere, that figure is
DNFBP-specific or from older guidance - the NFIU's own guideline for financial
institutions is 24 hours.

**"Does this only work for Nigeria?"**
The demo is built specifically for the Nigerian framework (NFIU, CBN, MLPPA
2022) because that's the market being validated first. The underlying
architecture - rules, evidence, justification, draft report - could generalize
to other regimes (FCA, FinCEN) by swapping the policy layer, but that's
unbuilt and untested; don't overstate it as a current feature.

**"We already use ComplyAdvantage / Hawk AI / [incumbent]."**
"Perfect - what does it still leave on your desk every day?" That gap is the
product. Don't position this as a replacement for an incumbent TM system;
position it as covering what happens after the incumbent's alert fires.

---

## About commercials and timeline

**"What would this cost?"**
Don't quote a number - this is exactly what the pilot-pricing question in your
own interview script is for ("what would a fair pilot price be?"). Let them
anchor first; you're gathering data, not selling yet.

**"How long until this could actually run on our data?"**
Honest answer: unknown until a specific pilot is scoped, since this is
pre-infrastructure. Better to ask what timeline *they'd* need to see something
real, and let that shape the roadmap, than to promise a date now.

**"Who else have you talked to / has anyone signed on?"**
Answer honestly with wherever the outreach tracker actually stands. Compliance
people can tell when traction is being oversold, and it costs more trust than
admitting "you're early in this conversation."

---

## If you don't know the answer

It's fine, and often better, to say: "I don't have a solid answer to that yet -
can I note it and follow up?" Then actually follow up. A validation call is
supposed to surface exactly these gaps; treat each one as a data point for the
tracker, not a test you failed.
