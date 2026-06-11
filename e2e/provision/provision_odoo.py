#!/usr/bin/env python3
"""Provision the Mexican SUBSIDIARY company in Odoo for the e2e harness.

Creates (idempotently, via Odoo's XML-RPC external API):
  1. Database `kontablo` + a company "Azteca Servicios" (MXN) if absent.
  2. The SAT (Anexo 24) ledger accounts the scenario needs, each with its
     statutory ``code``.
  3. A posted journal entry (account.move) reproducing the subsidiary trial
     balance from ``examples.transnational_reconciliation.build_scenario()`` —
     including the intra-group payable (SAT 216) to the Spanish parent.

REAL vs FIXTURE (honesty): company, accounts, and the journal entry are REAL
Odoo records. The amounts come from the in-repo fixture so the group is a known,
balanced pair. The Odoo connector then pulls them back like any tenant's books.

Run (after `docker compose up` and wait_for):
    python e2e/provision/provision_odoo.py \
        --url http://localhost:8069 --db kontablo --user admin --password admin
"""

from __future__ import annotations

import argparse
import os
import sys
import xmlrpc.client

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from examples.transnational_reconciliation import build_scenario  # noqa: E402

COMPANY = "Azteca Servicios"
CURRENCY = "MXN"

# SAT code -> (name, odoo account_type). account_type drives Odoo's
# balance-sheet vs P&L classification.
SAT_ACCOUNTS = {
    "102": ("Bancos", "asset_cash"),
    "105": ("Clientes", "asset_receivable"),
    "107": ("Almacen (Inventario)", "asset_current"),
    "201": ("Proveedores", "liability_payable"),
    "216": ("Cuentas por pagar a partes relacionadas", "liability_payable"),  # intercompany
    "300": ("Capital social", "equity"),
    "401": ("Ventas y/o servicios gravados", "income"),
}


class OdooProvisioner:
    def __init__(self, url: str, db: str, user: str, password: str):
        self.url = url.rstrip("/")
        self.db = db
        self.password = password
        self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self.db_proxy = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/db")
        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")
        self.user = user
        self.uid = None

    def ensure_database(self, master_password: str = "admin") -> None:
        dbs = self.db_proxy.list()
        if self.db not in dbs:
            print(f"[odoo] creating database {self.db!r} with demo=False")
            # create_database(master_pwd, db_name, demo, lang, admin_pwd)
            self.db_proxy.create_database(master_password, self.db, False, "en_US", self.password)
        else:
            print(f"[odoo] database {self.db!r} already exists")

    def auth(self) -> int:
        if self.uid is None:
            self.uid = self.common.authenticate(self.db, self.user, self.password, {})
            if not self.uid:
                raise PermissionError("Odoo authentication failed")
        return self.uid

    def x(self, model, method, args, kwargs=None):
        return self.models.execute_kw(self.db, self.auth(), self.password, model, method, args, kwargs or {})

    def ensure_company(self) -> int:
        ids = self.x("res.company", "search", [[["name", "=", COMPANY]]])
        if ids:
            return ids[0]
        cur = self.x("res.currency", "search", [[["name", "=", CURRENCY]]])
        vals = {"name": COMPANY}
        if cur:
            vals["currency_id"] = cur[0]
        print(f"[odoo] creating company {COMPANY!r}")
        return self.x("res.company", "create", [vals])

    def ensure_account(self, company_id: int, code: str, name: str, account_type: str) -> int:
        ids = self.x("account.account", "search",
                     [[["code", "=", code], ["company_id", "=", company_id]]])
        if ids:
            return ids[0]
        print(f"[odoo] creating account {code} {name!r}")
        return self.x("account.account", "create", [{
            "code": code,
            "name": name,
            "account_type": account_type,
            "company_id": company_id,
        }])

    def post_trial_balance(self, company_id: int) -> None:
        sub = next(e for e in build_scenario() if e.jurisdiction == "mx")
        acc_ids = {
            code: self.ensure_account(company_id, code, nm, at)
            for code, (nm, at) in SAT_ACCOUNTS.items()
        }
        # A general journal for the company.
        journal_ids = self.x("account.journal", "search",
                             [[["type", "=", "general"], ["company_id", "=", company_id]]],
                             {"limit": 1})
        if not journal_ids:
            journal_ids = [self.x("account.journal", "create", [{
                "name": "Opening", "code": "OPEN", "type": "general", "company_id": company_id,
            }])]
        lines = []
        for line in sub.lines:
            aid = acc_ids[line.local_code]
            lines.append((0, 0, {
                "account_id": aid,
                "name": line.local_name,
                "debit": line.amount if line.nature == "debit" else 0.0,
                "credit": line.amount if line.nature == "credit" else 0.0,
            }))
        existing = self.x("account.move", "search",
                          [[["ref", "=", "kontablo-e2e-opening"], ["company_id", "=", company_id]]])
        if existing:
            print("[odoo] opening move already exists")
            return
        print("[odoo] posting subsidiary opening journal entry")
        move_id = self.x("account.move", "create", [{
            "ref": "kontablo-e2e-opening",
            "journal_id": journal_ids[0],
            "company_id": company_id,
            "date": "2026-01-01",
            "line_ids": lines,
        }])
        self.x("account.move", "action_post", [[move_id]])
        print("[odoo] subsidiary provisioned OK")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=os.environ.get("ODOO_URL", "http://localhost:8069"))
    ap.add_argument("--db", default=os.environ.get("ODOO_DB", "kontablo"))
    ap.add_argument("--user", default=os.environ.get("ODOO_USER", "admin"))
    ap.add_argument("--password", default=os.environ.get("ODOO_PASSWORD", "admin"))
    ap.add_argument("--master-password", default=os.environ.get("ODOO_MASTER_PASSWORD", "admin"))
    args = ap.parse_args()

    prov = OdooProvisioner(args.url, args.db, args.user, args.password)
    prov.ensure_database(args.master_password)
    company_id = prov.ensure_company()
    prov.post_trial_balance(company_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
