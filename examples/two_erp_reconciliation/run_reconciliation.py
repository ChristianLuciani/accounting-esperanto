#!/usr/bin/env python3
"""
Two-ERP transnational reconciliation driver (ERPNext + Odoo → Kontablo).

This is the "next tier up" from ``examples/transnational_reconciliation.py``. It
reconciles the SAME transnational group, but the two subsidiaries' books live in
two different real open-source ERPs:

  * Parent      — Ibérica Manufactura, S.A.         Spain (PGC)   in ERPNext
  * Subsidiary  — Manufactura del Norte, S.A. de C.V.  Mexico (SAT)  in Odoo

It supports two data sources:

  --source fixtures   (default)  Reads committed trial-balance exports under
                                 ``fixtures/`` — runs with zero Docker, fully
                                 deterministic, and is what the test asserts on.
  --source live                  Pulls live trial balances from running ERPNext
                                 + Odoo containers via the Apache-2.0 connectors
                                 (``connectors/erpnext``, ``connectors/odoo``).
                                 Requires ``docker compose up`` + seeding first
                                 (see README.md).

Both sources feed the IDENTICAL ``core.engine`` resolve()/consolidate() path, so
the reconciled USD trial balance is the same regardless of where the data came
from. Honesty: the fixture amounts are synthetic (balanced by construction); the
local PGC/SAT codes are real statutory codes from the Kontablo ontology.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.engine import (  # noqa: E402
    ConsolidationEngine,
    IntercompanyLink,
    LocalEntry,
    SubsidiaryTB,
)

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES = os.path.join(HERE, "fixtures")

# The single intercompany balance to eliminate (parent receivable ↔ sub payable).
INTERCOMPANY_USD = 100_000.0
INTERCOMPANY = IntercompanyLink(
    from_subsidiary="Ibérica Manufactura, S.A.",
    from_kontablo_id="asset.current.receivables",
    to_subsidiary="Manufactura del Norte, S.A. de C.V.",
    to_kontablo_id="liability.current.payables",
    amount_usd=INTERCOMPANY_USD,
)


def _tb_from_export(doc: dict) -> SubsidiaryTB:
    return SubsidiaryTB(
        subsidiary_id=doc["company"],
        jurisdiction=doc["jurisdiction"],
        currency=doc["currency"],
        entries=[
            LocalEntry(
                code=e["local_code"],
                name=e["local_name"],
                debit=float(e.get("debit", 0.0)),
                credit=float(e.get("credit", 0.0)),
                intercompany_with=e.get("intercompany_with"),
            )
            for e in doc["entries"]
        ],
    )


def load_from_fixtures() -> list[SubsidiaryTB]:
    parent = json.load(open(os.path.join(FIXTURES, "erpnext_iberica_trial_balance.json"), encoding="utf-8"))
    sub = json.load(open(os.path.join(FIXTURES, "odoo_norte_trial_balance.json"), encoding="utf-8"))
    return [_tb_from_export(parent), _tb_from_export(sub)]


def load_from_live() -> list[SubsidiaryTB]:
    """Pull live trial balances from running ERPNext + Odoo containers.

    Configured via environment variables (see README.md):
      ERPNEXT_URL, ERPNEXT_API_KEY, ERPNEXT_API_SECRET, ERPNEXT_COMPANY
      ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD
    """
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "..", "connectors", "erpnext"))
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "..", "connectors", "odoo"))
    from kontablo_client import ERPNextKontabloConnector  # type: ignore
    from odoo_client import OdooKontabloConnector  # type: ignore

    erp = ERPNextKontabloConnector(
        erpnext_url=os.environ["ERPNEXT_URL"],
        api_key=os.environ["ERPNEXT_API_KEY"],
        api_secret=os.environ["ERPNEXT_API_SECRET"],
    )
    company = os.environ.get("ERPNEXT_COMPANY", "Ibérica Manufactura, S.A.")
    erp_tb_rows = erp.get_trial_balance(company, "2026-06-11")
    parent_entries = []
    for row in erp_tb_rows[1]:  # [columns, data]
        if row.get("account") and (row.get("debit") or row.get("credit")):
            parent_entries.append(LocalEntry(
                code=row["account"], name=row.get("account_name") or row["account"],
                debit=row.get("debit", 0.0), credit=row.get("credit", 0.0)))
    parent = SubsidiaryTB(company, "es", "EUR", parent_entries)

    odoo = OdooKontabloConnector(
        odoo_url=os.environ["ODOO_URL"],
        db=os.environ["ODOO_DB"],
        username=os.environ["ODOO_USER"],
        password=os.environ["ODOO_PASSWORD"],
    )
    sub_rows = odoo.get_trial_balance()
    sub = SubsidiaryTB(
        "Manufactura del Norte, S.A. de C.V.", "mx", "MXN",
        [LocalEntry(code=r["local_code"], name=r["local_name"],
                    debit=r["debit"], credit=r["credit"]) for r in sub_rows],
    )
    return [parent, sub]


def reconcile(source: str = "fixtures"):
    subs = load_from_fixtures() if source == "fixtures" else load_from_live()
    engine = ConsolidationEngine()
    return engine.consolidate(subs, eliminations=[INTERCOMPANY])


def main() -> None:
    ap = argparse.ArgumentParser(description="Two-ERP transnational reconciliation")
    ap.add_argument("--source", choices=["fixtures", "live"], default="fixtures")
    args = ap.parse_args()

    print("=" * 92)
    print(f"KONTABLO — Two-ERP transnational reconciliation  (source: {args.source})")
    print("  ERPNext: Ibérica Manufactura, S.A.  Spain (PGC)   EUR")
    print("  Odoo:    Manufactura del Norte, S.A. de C.V.  Mexico (SAT)  MXN")
    print("=" * 92)

    result = reconcile(args.source)

    print("\nUNIFIED CROSS-BORDER TRIAL BALANCE (USD)")
    for l in sorted(result.lines, key=lambda x: x.kontablo_id):
        print(f"  {l.kontablo_id:<34} {l.label_en[:30]:<30} "
              f"D {l.debit_usd:>14,.2f}  C {l.credit_usd:>14,.2f}")
    print("-" * 92)
    print(f"  Σ DEBITS  {result.total_debits:>14,.2f}   "
          f"Σ CREDITS {result.total_credits:>14,.2f}   "
          f"diff {result.balance_difference:>10,.2f}")
    print(f"  Intercompany eliminations applied: {result.eliminations_applied}")
    print(f"  Reconciliation: {'BALANCED ✓' if result.is_balanced() else 'OUT OF BALANCE ✗'}")
    if result.escalations:
        print(f"  Escalated to human review (CRA): {len(result.escalations)}")
    print("=" * 92)


if __name__ == "__main__":
    main()
