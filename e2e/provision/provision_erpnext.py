#!/usr/bin/env python3
"""Provision the Spanish PARENT company in ERPNext for the e2e harness.

Creates (idempotently, via the ERPNext REST API):
  1. Company "Iberia Holding" (EUR), abbr "IH".
  2. The PGC ledger accounts the scenario needs, each with an explicit
     ``account_number`` so the connector can recover the statutory code.
  3. Journal entries reproducing the parent trial balance from
     ``examples.transnational_reconciliation.build_scenario()`` — including the
     intra-group receivable (PGC 4330) against the Mexican subsidiary.

REAL vs FIXTURE (honesty, CLAUDE.md): the company, accounts, and journal
entries created here are REAL ERPNext records, posted through the public REST
API. The *amounts* come from the in-repo fixture so the two ERPs form a known,
balanced group. The connector then pulls them back as if they were any tenant's
books.

Run (after `docker compose up` and wait_for):
    python e2e/provision/provision_erpnext.py \
        --url http://localhost:8081 --api-key KEY --api-secret SECRET
or with username/password to mint an API key automatically.
"""

from __future__ import annotations

import argparse
import os
import sys

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from examples.transnational_reconciliation import build_scenario  # noqa: E402

COMPANY = "Iberia Holding"
ABBR = "IH"
CURRENCY = "EUR"
COUNTRY = "Spain"

# PGC code -> (account_name, root_type) for the ledger accounts we post to.
# root_type drives ERPNext's debit/credit conventions.
PGC_ACCOUNTS = {
    "572": ("Bancos", "Asset"),
    "430": ("Clientes", "Asset"),
    "4330": ("Clientes empresas del grupo", "Asset"),   # intercompany receivable
    "300": ("Existencias comerciales", "Asset"),
    "400": ("Proveedores", "Liability"),
    "100": ("Capital social", "Equity"),
    "700": ("Ventas de mercaderias", "Income"),
}


class ERPNextProvisioner:
    def __init__(self, url: str, api_key: str, api_secret: str):
        self.url = url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"token {api_key}:{api_secret}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def _post(self, doctype: str, doc: dict) -> dict:
        r = self.session.post(f"{self.url}/api/resource/{doctype}", json=doc)
        if r.status_code >= 400:
            raise RuntimeError(f"{doctype} create failed [{r.status_code}]: {r.text}")
        return r.json().get("data", {})

    def _exists(self, doctype: str, name: str) -> bool:
        r = self.session.get(f"{self.url}/api/resource/{doctype}/{requests.utils.quote(name)}")
        return r.status_code == 200

    def ensure_company(self) -> None:
        if self._exists("Company", COMPANY):
            print(f"[erpnext] company {COMPANY!r} already exists")
            return
        print(f"[erpnext] creating company {COMPANY!r}")
        self._post(
            "Company",
            {
                "company_name": COMPANY,
                "abbr": ABBR,
                "default_currency": CURRENCY,
                "country": COUNTRY,
            },
        )

    def ensure_account(self, number: str, account_name: str, root_type: str) -> str:
        name = f"{number} - {account_name} - {ABBR}"
        if self._exists("Account", name):
            return name
        # Parent group account by root type (auto-created with the company CoA).
        parent = {
            "Asset": f"Application of Funds (Assets) - {ABBR}",
            "Liability": f"Source of Funds (Liabilities) - {ABBR}",
            "Equity": f"Equity - {ABBR}",
            "Income": f"Income - {ABBR}",
            "Expense": f"Expenses - {ABBR}",
        }[root_type]
        print(f"[erpnext] creating account {name!r}")
        self._post(
            "Account",
            {
                "account_name": account_name,
                "account_number": number,
                "company": COMPANY,
                "root_type": root_type,
                "parent_account": parent,
                "is_group": 0,
                "account_currency": CURRENCY,
            },
        )
        return name

    def post_trial_balance(self) -> None:
        parent = next(e for e in build_scenario() if e.jurisdiction == "es")
        accounts = {}
        for code, (acc_name, root_type) in PGC_ACCOUNTS.items():
            accounts[code] = self.ensure_account(code, acc_name, root_type)

        # One opening journal entry that books every line of the parent TB.
        je_accounts = []
        for line in parent.lines:
            acc_name = accounts[line.local_code]
            if line.nature == "debit":
                je_accounts.append({"account": acc_name, "debit_in_account_currency": line.amount})
            else:
                je_accounts.append({"account": acc_name, "credit_in_account_currency": line.amount})

        print("[erpnext] posting parent opening journal entry")
        doc = self._post(
            "Journal Entry",
            {
                "voucher_type": "Opening Entry",
                "company": COMPANY,
                "posting_date": "2026-01-01",
                "title": "Kontablo e2e opening balance",
                "accounts": je_accounts,
            },
        )
        # Submit (docstatus 1) so it hits the ledger.
        name = doc.get("name")
        if name:
            r = self.session.put(
                f"{self.url}/api/resource/Journal Entry/{requests.utils.quote(name)}",
                json={"docstatus": 1},
            )
            if r.status_code >= 400:
                raise RuntimeError(f"Journal Entry submit failed: {r.text}")
        print("[erpnext] parent provisioned OK")


def mint_api_key(url: str, username: str, password: str) -> tuple[str, str]:
    """Log in with user/password and generate API key+secret for `username`."""
    s = requests.Session()
    r = s.post(f"{url.rstrip('/')}/api/method/login",
               json={"usr": username, "pwd": password})
    r.raise_for_status()
    r = s.post(
        f"{url.rstrip('/')}/api/method/frappe.core.doctype.user.user.generate_keys",
        json={"user": username},
    )
    r.raise_for_status()
    secret = r.json()["message"]["api_secret"]
    # api_key is stored on the User; fetch it.
    u = s.get(f"{url.rstrip('/')}/api/resource/User/{requests.utils.quote(username)}")
    u.raise_for_status()
    return u.json()["data"]["api_key"], secret


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=os.environ.get("ERPNEXT_URL", "http://localhost:8081"))
    ap.add_argument("--api-key", default=os.environ.get("ERPNEXT_API_KEY"))
    ap.add_argument("--api-secret", default=os.environ.get("ERPNEXT_API_SECRET"))
    ap.add_argument("--username", default=os.environ.get("ERPNEXT_USER", "Administrator"))
    ap.add_argument("--password", default=os.environ.get("ERPNEXT_PASSWORD", "admin"))
    args = ap.parse_args()

    key, secret = args.api_key, args.api_secret
    if not (key and secret):
        print("[erpnext] no API key supplied; minting one via login")
        key, secret = mint_api_key(args.url, args.username, args.password)
        print(f"[erpnext] minted API key {key}")

    prov = ERPNextProvisioner(args.url, key, secret)
    prov.ensure_company()
    prov.post_trial_balance()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
