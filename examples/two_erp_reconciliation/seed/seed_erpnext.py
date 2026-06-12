#!/usr/bin/env python3
"""
Seed the ERPNext container with the Spanish parent for the demo.

Creates the PGC-coded accounts and posts opening Journal Entries (including the
intercompany receivable from the Mexican subsidiary) via the ERPNext REST API,
so that ``run_reconciliation.py --source live`` can pull a real trial balance.

Data mirrors ``fixtures/erpnext_iberica_trial_balance.json``. Amounts are
synthetic (balanced by construction).

Usage (after `docker compose up` and creating an ERPNext site + API keys):
    ERPNEXT_URL=http://localhost:8080 ERPNEXT_API_KEY=... ERPNEXT_API_SECRET=... \
    ERPNEXT_COMPANY="Ibérica Manufactura, S.A." python seed/seed_erpnext.py

NOTE: Reference script for a live ERPNext instance; not exercised in CI.
The engine path it feeds IS covered by the offline test.
"""

import json
import os
import sys

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURE = os.path.join(os.path.dirname(HERE), "fixtures", "erpnext_iberica_trial_balance.json")


def main() -> None:
    base = os.environ.get("ERPNEXT_URL", "http://localhost:8080")
    key = os.environ.get("ERPNEXT_API_KEY")
    secret = os.environ.get("ERPNEXT_API_SECRET")
    company = os.environ.get("ERPNEXT_COMPANY", "Ibérica Manufactura, S.A.")
    if not (key and secret):
        sys.exit("Set ERPNEXT_API_KEY and ERPNEXT_API_SECRET (Settings → API Access).")

    headers = {"Authorization": f"token {key}:{secret}", "Content-Type": "application/json"}
    doc = json.load(open(FIXTURE, encoding="utf-8"))
    print(f"Seeding ERPNext company '{company}' ({doc['jurisdiction'].upper()} / {doc['standard']})")

    def root_type(code: str) -> str:
        if code in {"572", "430", "300", "21"}:
            return "Asset"
        if code in {"400", "170"}:
            return "Liability"
        if code in {"100", "129"}:
            return "Equity"
        if code.startswith("7"):
            return "Income"
        return "Expense"

    # 1) Create leaf accounts with explicit PGC codes (account_number).
    for e in doc["entries"]:
        payload = {
            "doctype": "Account",
            "account_name": e["local_name"],
            "account_number": e["local_code"],
            "company": company,
            "root_type": root_type(e["local_code"]),
            "is_group": 0,
        }
        r = requests.post(f"{base}/api/resource/Account", headers=headers, json=payload)
        if r.status_code >= 400 and "already exists" not in r.text.lower():
            print(f"  warn: account {e['local_code']} → {r.status_code}: {r.text[:120]}")

    # 2) Post one opening Journal Entry carrying the trial balance.
    je_accounts = [{
        "account": f"{e['local_code']} - {e['local_name']} - {company[:3]}",
        "debit_in_account_currency": e["debit"],
        "credit_in_account_currency": e["credit"],
    } for e in doc["entries"]]
    je = {
        "doctype": "Journal Entry",
        "voucher_type": "Opening Entry",
        "company": company,
        "posting_date": doc["reporting_date"],
        "accounts": je_accounts,
    }
    r = requests.post(f"{base}/api/resource/Journal Entry", headers=headers, json=je)
    print(f"Journal Entry create → {r.status_code}. Done "
          f"(verify account naming matches your ERPNext naming series).")


if __name__ == "__main__":
    main()
