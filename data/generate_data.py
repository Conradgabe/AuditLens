"""
Synthetic transaction generator for the AuditLens smoke-and-mirrors demo.

Produces:
  transactions.csv     - ~1,250 anonymized Nigerian fintech transactions (7 days)
  audit_findings.json  - the "AI agent" audit output: alert stats + 6 case files
                         (4 requiring review, 2 auto-cleared) with justification
                         memos and NFIU-style STR drafts

All data is synthetic. User IDs are anonymized (Zero-PII posture: no names,
no BVNs, no card numbers) - consistent with the product's ingestion story.
Deterministic: seeded RNG, fixed planted cases.
"""

import csv
import json
import os
import random
import re
from datetime import datetime, timedelta

random.seed(42)

_HERE = os.path.dirname(os.path.abspath(__file__))
OUT_CSV = os.path.join(_HERE, "transactions.csv")
OUT_JSON = os.path.join(_HERE, "audit_findings.json")

PERIOD_START = datetime(2026, 6, 30, 0, 0, 0)
PERIOD_END = datetime(2026, 7, 6, 23, 59, 59)

BANKS = [
    "GTBank", "Access Bank", "Zenith Bank", "UBA", "First Bank",
    "Kuda", "OPay", "Moniepoint", "PalmPay", "Wema/ALAT", "Stanbic IBTC",
]
CHANNELS = ["app", "app", "app", "ussd", "web", "pos"]
TXN_TYPES = ["transfer_out", "transfer_out", "transfer_in", "bill_payment", "airtime", "card_spend"]

# Reserved actors for planted scenarios
PLANTED_USERS = {"USR-0417", "USR-2286", "USR-3050", "USR-1174", "USR-0892", "USR-1560"}


def rand_ts(start, end):
    delta = (end - start).total_seconds()
    return start + timedelta(seconds=random.uniform(0, delta))


def background_transactions(n=1200):
    """Normal, unremarkable activity from ~140 users."""
    rows = []
    users = []
    while len(users) < 140:
        uid = f"USR-{random.randint(1, 3999):04d}"
        if uid not in PLANTED_USERS and uid not in users:
            users.append(uid)
    user_profiles = {
        u: {
            "kyc_tier": random.choices([1, 2, 3], weights=[2, 6, 2])[0],
            "account_age_days": random.randint(90, 2200),
            "device_id": f"DEV-{random.randint(10000, 99999)}",
            "beneficiaries": [f"BEN-{random.randint(1000, 9999)}" for _ in range(random.randint(2, 6))],
        }
        for u in users
    }
    for _ in range(n):
        u = random.choice(users)
        p = user_profiles[u]
        ttype = random.choice(TXN_TYPES)
        new_ben = random.random() < 0.08
        ben = f"BEN-{random.randint(1000, 9999)}" if new_ben else random.choice(p["beneficiaries"])
        amount = round(random.lognormvariate(9.6, 1.1), 2)  # median ~N15k, tail to low millions
        amount = min(amount, 3_800_000)
        rows.append({
            "timestamp": rand_ts(PERIOD_START, PERIOD_END),
            "user_id": u,
            "kyc_tier": p["kyc_tier"],
            "account_age_days": p["account_age_days"],
            "channel": random.choice(CHANNELS),
            "txn_type": ttype,
            "amount_ngn": amount,
            "beneficiary_id": ben if ttype.startswith("transfer") else "",
            "beneficiary_bank": random.choice(BANKS) if ttype.startswith("transfer") else "",
            "beneficiary_country": "NG",
            "beneficiary_new": int(new_ben and ttype == "transfer_out"),
            "device_id": p["device_id"],
            "device_new": 0,
            "ip_country": "NG",
            "name_match_score": round(random.uniform(0.93, 1.0), 2),
            "status": "completed",
        })
    return rows


def planted_transactions():
    """The scenarios the audit agent will flag (and the ones it will clear)."""
    rows = []
    tags = {}  # scenario -> list of row indices into `rows`

    def add(scenario, row):
        tags.setdefault(scenario, []).append(len(rows))
        rows.append(row)

    # --- VEL-01: USR-0417 - 7 transfers to 7 NEW beneficiaries in 12 minutes ---
    base = datetime(2026, 7, 5, 21, 14, 0)
    for i, amt in enumerate([185_000, 240_000, 310_000, 150_000, 415_000, 275_000, 480_000]):
        add("velocity", {
            "timestamp": base + timedelta(minutes=[0, 2, 3, 5, 7, 9, 12][i]),
            "user_id": "USR-0417", "kyc_tier": 2, "account_age_days": 611,
            "channel": "app", "txn_type": "transfer_out", "amount_ngn": amt,
            "beneficiary_id": f"BEN-9{i}01", "beneficiary_bank": random.choice(BANKS),
            "beneficiary_country": "NG", "beneficiary_new": 1,
            "device_id": "DEV-30417", "device_new": 0, "ip_country": "NG",
            "name_match_score": round(random.uniform(0.94, 0.99), 2), "status": "completed",
        })

    # --- STR-02: USR-2286 - 6 transfers just under N1m each, same beneficiary,
    #     36 hours, cumulative N5.62m (> N5m individual CTR threshold) ---
    times = [
        datetime(2026, 7, 3, 18, 5), datetime(2026, 7, 3, 21, 40),
        datetime(2026, 7, 4, 7, 55), datetime(2026, 7, 4, 13, 20),
        datetime(2026, 7, 4, 19, 45), datetime(2026, 7, 5, 8, 50),
    ]
    for t, amt in zip(times, [985_000, 940_000, 970_000, 890_000, 955_000, 880_000]):
        add("structuring", {
            "timestamp": t,
            "user_id": "USR-2286", "kyc_tier": 2, "account_age_days": 402,
            "channel": "app", "txn_type": "transfer_out", "amount_ngn": amt,
            "beneficiary_id": "BEN-7731", "beneficiary_bank": "Access Bank",
            "beneficiary_country": "NG", "beneficiary_new": 0,
            "device_id": "DEV-52286", "device_new": 0, "ip_country": "NG",
            "name_match_score": 0.97, "status": "completed",
        })

    # --- CBM-03: USR-3050 - outbound remittances, KYC country NG, login IP CY,
    #     beneficiary in AE, weak beneficiary name match ---
    for t, amt in zip(
        [datetime(2026, 7, 4, 2, 12), datetime(2026, 7, 4, 2, 31), datetime(2026, 7, 4, 3, 4)],
        [2_400_000, 1_850_000, 1_200_000],
    ):
        add("cross_border", {
            "timestamp": t,
            "user_id": "USR-3050", "kyc_tier": 2, "account_age_days": 233,
            "channel": "web", "txn_type": "transfer_out", "amount_ngn": amt,
            "beneficiary_id": "BEN-INTL-204", "beneficiary_bank": "Correspondent (AE)",
            "beneficiary_country": "AE", "beneficiary_new": 1,
            "device_id": "DEV-88112", "device_new": 1, "ip_country": "CY",
            "name_match_score": 0.41, "status": "completed",
        })

    # --- DOR-04: USR-1174 - dormant ~8 months, reactivates, N4.2m out in 5 hours
    #     on a new device ---
    for t, amt in zip(
        [datetime(2026, 7, 6, 9, 18), datetime(2026, 7, 6, 11, 47), datetime(2026, 7, 6, 14, 2)],
        [1_500_000, 1_500_000, 1_200_000],
    ):
        add("dormant", {
            "timestamp": t,
            "user_id": "USR-1174", "kyc_tier": 3, "account_age_days": 1460,
            "channel": "app", "txn_type": "transfer_out", "amount_ngn": amt,
            "beneficiary_id": "BEN-4419", "beneficiary_bank": "Zenith Bank",
            "beneficiary_country": "NG", "beneficiary_new": 1,
            "device_id": "DEV-NEW-7734", "device_new": 1, "ip_country": "NG",
            "name_match_score": 0.95, "status": "completed",
        })

    # --- Cleared A: USR-0892 - 4 rapid transfers on payday, but ALL to known
    #     beneficiaries on a known device (classic false positive) ---
    base = datetime(2026, 7, 1, 8, 30, 0)
    for i, (ben, amt) in enumerate([("BEN-2201", 120_000), ("BEN-2205", 85_000),
                                    ("BEN-2211", 65_000), ("BEN-2218", 250_000)]):
        add("cleared_velocity", {
            "timestamp": base + timedelta(minutes=i * 4),
            "user_id": "USR-0892", "kyc_tier": 2, "account_age_days": 924,
            "channel": "app", "txn_type": "transfer_out", "amount_ngn": amt,
            "beneficiary_id": ben, "beneficiary_bank": random.choice(BANKS),
            "beneficiary_country": "NG", "beneficiary_new": 0,
            "device_id": "DEV-40892", "device_new": 0, "ip_country": "NG",
            "name_match_score": 0.98, "status": "completed",
        })

    # --- Cleared B: USR-1560 - tier-3 business account, single N6.5m transfer
    #     above the CTR threshold to a 14-month recurring supplier ---
    add("cleared_ctr", {
        "timestamp": datetime(2026, 7, 2, 10, 6),
        "user_id": "USR-1560", "kyc_tier": 3, "account_age_days": 1105,
        "channel": "web", "txn_type": "transfer_out", "amount_ngn": 6_500_000,
        "beneficiary_id": "BEN-3308", "beneficiary_bank": "Stanbic IBTC",
        "beneficiary_country": "NG", "beneficiary_new": 0,
        "device_id": "DEV-61560", "device_new": 0, "ip_country": "NG",
        "name_match_score": 0.98, "status": "completed",
    })

    return rows, tags


def main():
    bg = background_transactions()
    planted, tags = planted_transactions()

    all_rows = bg + planted
    all_rows.sort(key=lambda r: r["timestamp"])

    # Assign txn IDs in chronological order
    for i, r in enumerate(all_rows):
        r["txn_id"] = f"TXN-{100001 + i}"

    # Map planted scenario -> assigned txn ids (rows are shared objects)
    scenario_txns = {
        scen: [planted[i]["txn_id"] for i in idxs] for scen, idxs in tags.items()
    }

    fieldnames = [
        "txn_id", "timestamp", "user_id", "kyc_tier", "account_age_days",
        "channel", "txn_type", "amount_ngn", "beneficiary_id", "beneficiary_bank",
        "beneficiary_country", "beneficiary_new", "device_id", "device_new",
        "ip_country", "name_match_score", "status",
    ]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in all_rows:
            row = dict(r)
            row["timestamp"] = r["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            w.writerow(row)

    def structuring_note():
        acc = {"total": 0}

        def fn(r):
            acc["total"] += r["amount_ngn"]
            return f"Kept below N1m; running total N{int(acc['total']):,}"
        return fn

    def evidence(scen, note_fn):
        out = []
        for i in tags[scen]:
            r = planted[i]
            out.append({
                "txn_id": r["txn_id"],
                "timestamp": r["timestamp"].strftime("%Y-%m-%d %H:%M"),
                "amount_ngn": r["amount_ngn"],
                "note": note_fn(r),
            })
        return out

    findings = {
        "product": "AuditLens (demo)",
        "period": {"start": "2026-06-30", "end": "2026-07-06"},
        "summary": {
            "transactions_audited": len(all_rows),
            "alerts_raised": 38,
            "auto_cleared": 34,
            "auto_clear_rate": 0.89,
            "cases_for_review": 4,
            "str_drafts_ready": 4,
            "analyst_hours_saved_est": 22.8,
            "hours_saved_basis": "34 auto-cleared alerts x 35 min avg manual investigation + 4 report drafts x 45 min",
        },
        "alerts_by_rule": [
            {"rule_id": "VEL-01", "rule_name": "Beneficiary velocity spike", "raw": 14, "auto_cleared": 13, "for_review": 1},
            {"rule_id": "STR-02", "rule_name": "Structuring below CTR threshold", "raw": 6, "auto_cleared": 5, "for_review": 1},
            {"rule_id": "CBM-03", "rule_name": "Cross-border profile mismatch", "raw": 9, "auto_cleared": 8, "for_review": 1},
            {"rule_id": "DOR-04", "rule_name": "Dormant account reactivation", "raw": 4, "auto_cleared": 3, "for_review": 1},
            {"rule_id": "CTR-05", "rule_name": "Currency transaction threshold (auto-filed)", "raw": 5, "auto_cleared": 5, "for_review": 0},
        ],
        "cases": [
            {
                "case_id": "CASE-2026-0141",
                "user_id": "USR-2286",
                "rule_id": "STR-02",
                "rule_name": "Structuring below CTR threshold",
                "severity": "critical",
                "risk_score": 91,
                "status": "open",
                "amount_involved_ngn": 5_620_000,
                "detected_at": "2026-07-05 08:52",
                "headline": "6 transfers of N880k-N985k to one beneficiary in 36h; cumulative N5.62m exceeds the N5m individual CTR threshold",
                "regulatory_basis": [
                    "Money Laundering (Prevention and Prohibition) Act 2022 - s.2 threshold reporting (N5m, individuals); structured splitting to evade the threshold",
                    "MLPPA 2022 s.7 - suspicious transaction report to NFIU within 24 hours of suspicion",
                    "CBN AML/CFT/CPF Regulations 2022 - ongoing transaction monitoring obligations",
                ],
                "evidence": evidence("structuring", structuring_note()),
                "justification_memo": (
                    "USR-2286 executed six outbound transfers to a single beneficiary (BEN-7731) over a 36-hour window. "
                    "Every transfer sits in a narrow N880,000-N985,000 band - individually unremarkable, but the cumulative "
                    "N5,620,000 crosses the N5,000,000 individual currency-transaction threshold that would have triggered a "
                    "mandatory CTR if moved as one payment. The tight amount banding (variance < 11%), single beneficiary, and "
                    "even spacing across two calendar days match the classic structuring pattern. No matching inflow, invoice "
                    "reference, or historical relationship with BEN-7731 above N200k/month exists in the prior 90 days. "
                    "Agent confidence: HIGH. This is not clearable on behavioral history."
                ),
                "recommended_action": "Escalate to compliance officer. STR draft prepared for NFIU rendition within the 24-hour window. Consider temporary outbound limit pending review.",
                "str_draft": True,
            },
            {
                "case_id": "CASE-2026-0142",
                "user_id": "USR-3050",
                "rule_id": "CBM-03",
                "rule_name": "Cross-border profile mismatch",
                "severity": "critical",
                "risk_score": 87,
                "status": "open",
                "amount_involved_ngn": 5_450_000,
                "detected_at": "2026-07-04 03:06",
                "headline": "N5.45m in night-time remittances to AE beneficiary; login IP in CY, new device, beneficiary name match 0.41",
                "regulatory_basis": [
                    "CBN AML/CFT/CPF Regulations 2022 - enhanced due diligence for cross-border transfers and high-risk corridors",
                    "MLPPA 2022 s.7 - STR to NFIU within 24 hours",
                    "NDPA 2023 note: all analysis performed on anonymized identifiers (no PII ingested)",
                ],
                "evidence": evidence("cross_border", lambda r: f"Remittance to {r['beneficiary_country']} beneficiary; login IP {r['ip_country']} vs KYC country NG; name match {r['name_match_score']}"),
                "justification_memo": (
                    "USR-3050 (KYC country: Nigeria, account age 233 days) initiated three outbound international remittances "
                    "totaling N5,450,000 between 02:12 and 03:04 local time to a newly added UAE beneficiary. Three independent "
                    "risk signals coincide: (1) session IP geolocated to Cyprus while the KYC profile and all prior sessions are "
                    "Nigerian; (2) the transfers were initiated from a first-seen device; (3) beneficiary account-name resolution "
                    "returned a 0.41 match against the name supplied at beneficiary creation. Any one signal alone is clearable; "
                    "the conjunction within a 52-minute night-time window is not. Pattern is consistent with account takeover or "
                    "third-party-directed remittance. Agent confidence: HIGH."
                ),
                "recommended_action": "Escalate immediately. Recommend step-up re-authentication and hold on further international transfers. STR draft prepared.",
                "str_draft": True,
            },
            {
                "case_id": "CASE-2026-0143",
                "user_id": "USR-0417",
                "rule_id": "VEL-01",
                "rule_name": "Beneficiary velocity spike",
                "severity": "serious",
                "risk_score": 78,
                "status": "open",
                "amount_involved_ngn": 2_055_000,
                "detected_at": "2026-07-05 21:26",
                "headline": "7 transfers to 7 never-seen beneficiaries within 12 minutes, totaling N2.06m",
                "regulatory_basis": [
                    "CBN AML/CFT/CPF Regulations 2022 - transaction monitoring; internal Risk Policy s.4.2 velocity limits",
                    "MLPPA 2022 s.7 - STR to NFIU within 24 hours if suspicion is confirmed",
                ],
                "evidence": evidence("velocity", lambda r: f"Transfer to new beneficiary {r['beneficiary_id']} ({r['beneficiary_bank']})"),
                "justification_memo": (
                    "USR-0417 dispersed N2,055,000 across seven previously unknown beneficiaries at six different institutions "
                    "in a 12-minute window (21:14-21:26). The account's 90-day baseline is 2.1 outbound transfers/day to a "
                    "stable set of 4 beneficiaries. Rapid fan-out to many new counterparties is the primary money-mule "
                    "dispersal signature. Mitigating factor: session came from the user's registered device and home IP - "
                    "which weakens the account-takeover hypothesis but not the mule/proxy-payout hypothesis. "
                    "Agent confidence: MEDIUM-HIGH. Human review required; not auto-clearable."
                ),
                "recommended_action": "Review within 24h. Request source-of-funds context from customer if unexplained. STR draft prepared in case review confirms suspicion.",
                "str_draft": True,
            },
            {
                "case_id": "CASE-2026-0144",
                "user_id": "USR-1174",
                "rule_id": "DOR-04",
                "rule_name": "Dormant account reactivation",
                "severity": "serious",
                "risk_score": 74,
                "status": "open",
                "amount_involved_ngn": 4_200_000,
                "detected_at": "2026-07-06 14:05",
                "headline": "Account dormant ~8 months moves N4.2m out in 5 hours from a first-seen device",
                "regulatory_basis": [
                    "CBN AML/CFT/CPF Regulations 2022 - monitoring of dormant/reactivated accounts",
                    "Internal Risk Policy s.6.1 - dormancy reactivation review",
                ],
                "evidence": evidence("dormant", lambda r: f"Transfer to {r['beneficiary_id']} from new device {r['device_id']}"),
                "justification_memo": (
                    "USR-1174 recorded no transaction activity for approximately 8 months, then moved N4,200,000 across three "
                    "outbound transfers within 5 hours of reactivation - all to a newly added beneficiary, all from a device "
                    "never previously associated with the account. Dormant-then-drain is a recognized takeover pattern; "
                    "the new-device signal raises it above routine reactivation. Mitigating factor: transfers passed name-match "
                    "at 0.95 and the beneficiary bank is domestic. Agent confidence: MEDIUM. Recommend contact verification "
                    "before clearing."
                ),
                "recommended_action": "Outbound hold + customer contact verification. STR draft prepared pending outcome.",
                "str_draft": True,
            },
            {
                "case_id": "CASE-2026-0139",
                "user_id": "USR-0892",
                "rule_id": "VEL-01",
                "rule_name": "Beneficiary velocity spike",
                "severity": "warning",
                "risk_score": 12,
                "status": "auto_cleared",
                "amount_involved_ngn": 520_000,
                "detected_at": "2026-07-01 08:42",
                "headline": "4 rapid transfers on salary day - all to established beneficiaries; cleared automatically",
                "regulatory_basis": ["Internal Risk Policy s.4.2 - velocity limits (behavioral exception applied)"],
                "evidence": evidence("cleared_velocity", lambda r: f"Transfer to known beneficiary {r['beneficiary_id']} (relationship > 12 months)"),
                "justification_memo": (
                    "Raw velocity rule fired: 4 transfers in 16 minutes. Investigation: all four beneficiaries have a "
                    "12+ month history with this account; amounts match this user's recurring first-of-month pattern "
                    "(rent, family support, savings sweep) within 8% of the 6-month median; session from registered device "
                    "and habitual IP. This is the account's documented payday routine, not dispersal. "
                    "CLEARED automatically - justification retained for audit trail."
                ),
                "recommended_action": "None. False positive resolved without analyst time.",
                "str_draft": False,
            },
            {
                "case_id": "CASE-2026-0140",
                "user_id": "USR-1560",
                "rule_id": "CTR-05",
                "rule_name": "Currency transaction threshold (auto-filed)",
                "severity": "warning",
                "risk_score": 18,
                "status": "auto_cleared",
                "amount_involved_ngn": 6_500_000,
                "detected_at": "2026-07-02 10:08",
                "headline": "N6.5m corporate transfer above CTR threshold - CTR auto-drafted, no suspicion indicators",
                "regulatory_basis": [
                    "MLPPA 2022 s.2 - currency transaction reporting (N10m corporate threshold; institution policy applies N5m review line)",
                ],
                "evidence": evidence("cleared_ctr", lambda r: f"Single transfer to {r['beneficiary_id']} (Stanbic IBTC), 14-month recurring supplier"),
                "justification_memo": (
                    "Tier-3 business account transferred N6,500,000 to a beneficiary paid monthly for 14 consecutive months "
                    "(amount within 6% of trailing average; consistent narration pattern; registered device; business hours). "
                    "Threshold report drafted automatically for rendition; no suspicion indicators present. "
                    "CLEARED for STR purposes - CTR paperwork generated without analyst involvement."
                ),
                "recommended_action": "Compliance officer to countersign auto-drafted CTR.",
                "str_draft": False,
            },
        ],
    }

    payload = json.dumps(findings, indent=2, ensure_ascii=False)
    payload = re.sub(r"N(?=[0-9])", "₦", payload)  # N5m -> naira-sign amounts
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        f.write(payload)

    print(f"Wrote {OUT_CSV}: {len(all_rows)} transactions")
    print(f"Wrote {OUT_JSON}: {len(findings['cases'])} case files")
    print("\nPlanted scenario -> transaction IDs:")
    for scen, ids in scenario_txns.items():
        print(f"  {scen}: {', '.join(ids)}")


if __name__ == "__main__":
    main()
