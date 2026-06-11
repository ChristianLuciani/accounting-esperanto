#!/usr/bin/env python3
"""End-to-end runner for the Kontablo two-ERP harness.

Pipeline (``--mode live``):
  1. Pull the Spanish parent chart + trial balance from ERPNext via the
     Apache-2.0 ERPNext connector.
  2. Pull the Mexican subsidiary chart + trial balance from Odoo via the
     Apache-2.0 Odoo connector.
  3. POST each chart to the Kontablo mapping API (`/api/v1/map`) — proves the
     service container is live and honors the mapping contract.
  4. Consolidate → convert to the presentation currency → eliminate the
     intra-group position → ASSERT the consolidated trial balance balances and
     the intercompany nets to zero.

Steps 4's math is the *exact same* :func:`reconcile` / :func:`assert_reconciled`
path the self-contained example and the fast unit test use
(``examples/transnational_reconciliation.py``), so the Dockerized run and the
no-Docker run can never silently diverge.

``--mode fixtures`` skips the ERPs entirely and reconciles the in-repo fixtures.
This validates the consolidation logic with zero Docker — it is what the fast
test suite and offline developers run. It is clearly labelled FIXTURE data.

Honesty note: in ``live`` mode the parent/subsidiary balances are REAL records
posted into REAL ERPNext / Odoo instances by the provisioning scripts; only the
*amounts* originate from the in-repo fixture so the group is a known, balanced
pair (see e2e/README.md).
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from typing import List

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from connectors.erpnext.kontablo_client import ERPNextKontabloConnector  # noqa: E402
from connectors.odoo.kontablo_odoo_client import OdooKontabloConnector  # noqa: E402
from examples.transnational_reconciliation import (  # noqa: E402
    Entity,
    Line,
    assert_reconciled,
    build_scenario,
    format_report,
    reconcile,
)

_LEADING_CODE = re.compile(r"^\s*(\d[\w.]*)")


def _leading_code(label: str) -> str:
    """Recover the statutory account code from an ERP account label.

    Both ERPs surface the code as the leading token (ERPNext:
    "4330 - Clientes grupo - IH"; Odoo: "216 Cuentas por pagar ...").
    Deterministic field extraction — never free-text classification.
    """
    m = _LEADING_CODE.match(label or "")
    return m.group(1) if m else (label or "").strip()


def _row_to_line(local_code: str, local_name: str, debit: float, credit: float) -> Line:
    debit = float(debit or 0.0)
    credit = float(credit or 0.0)
    if debit >= credit:
        return Line(local_code, local_name, "debit", round(debit - credit, 2))
    return Line(local_code, local_name, "credit", round(credit - debit, 2))


# --------------------------------------------------------------------------- #
# Live pulls
# --------------------------------------------------------------------------- #
def pull_erpnext_parent(url: str, api_key: str, api_secret: str, company: str) -> Entity:
    conn = ERPNextKontabloConnector(url, api_key, api_secret)
    tb = conn.get_trial_balance(company, to_date="2026-12-31")
    # ERPNext reports return [columns, data]; rows carry account/debit/credit.
    rows = tb[1] if isinstance(tb, list) and len(tb) > 1 else tb
    lines: List[Line] = []
    for row in rows:
        account = row.get("account") or ""
        debit = row.get("debit", 0.0)
        credit = row.get("credit", 0.0)
        if not account or (not debit and not credit):
            continue
        code = _leading_code(account)
        lines.append(_row_to_line(code, account, debit, credit))
    return Entity("ES-PARENT", company, "es", "EUR", "erpnext", lines)


def pull_odoo_subsidiary(url: str, db: str, user: str, password: str, company: str) -> Entity:
    conn = OdooKontabloConnector(url=url, db=db, username=user, password=password)
    tb = conn.get_trial_balance(company)
    lines = [
        _row_to_line(r["local_code"], r["local_name"], r["debit"], r["credit"])
        for r in tb
    ]
    return Entity("MX-SUB", company, "mx", "MXN", "odoo", lines)


def probe_mapping_api(kontablo_url: str, entity: Entity) -> None:
    """POST the entity's chart to /api/v1/map — liveness + contract check."""
    payload = {
        "company_id": entity.entity_id,
        "context": {"country": entity.jurisdiction, "currency": entity.currency},
        "accounts": [
            {"local_code": ln.local_code, "local_name": ln.local_name, "nature": ln.nature}
            for ln in entity.lines
        ],
    }
    r = requests.post(f"{kontablo_url.rstrip('/')}/api/v1/map", json=payload, timeout=30)
    r.raise_for_status()
    body = r.json()
    mapped = body.get("mapped_accounts", [])
    print(f"[api] /api/v1/map {entity.entity_id}: status={body.get('status')} "
          f"mapped={len(mapped)}/{len(entity.lines)}")


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def run_fixtures() -> int:
    print(">>> MODE: fixtures (no Docker / no ERP — in-repo FIXTURE data)\n")
    result = reconcile(build_scenario())
    print(format_report(result))
    assert_reconciled(result)
    print("\n✅ e2e (fixtures) reconciliation invariants hold.")
    return 0


def run_live(args) -> int:
    print(">>> MODE: live (REAL ERPNext + REAL Odoo)\n")
    parent = pull_erpnext_parent(
        args.erpnext_url, args.erpnext_api_key, args.erpnext_api_secret, args.erpnext_company
    )
    sub = pull_odoo_subsidiary(
        args.odoo_url, args.odoo_db, args.odoo_user, args.odoo_password, args.odoo_company
    )
    print(f"[pull] ERPNext parent: {len(parent.lines)} lines")
    print(f"[pull] Odoo subsidiary: {len(sub.lines)} lines")

    probe_mapping_api(args.kontablo_url, parent)
    probe_mapping_api(args.kontablo_url, sub)

    result = reconcile([parent, sub])
    print(format_report(result))
    assert_reconciled(result)
    print("\n✅ e2e (live, two real ERPs) reconciliation invariants hold.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Kontablo two-ERP e2e runner")
    ap.add_argument("--mode", choices=["live", "fixtures"], default="live")
    ap.add_argument("--kontablo-url", default=os.environ.get("KONTABLO_URL", "http://localhost:8000"))
    # ERPNext
    ap.add_argument("--erpnext-url", default=os.environ.get("ERPNEXT_URL", "http://localhost:8081"))
    ap.add_argument("--erpnext-api-key", default=os.environ.get("ERPNEXT_API_KEY", ""))
    ap.add_argument("--erpnext-api-secret", default=os.environ.get("ERPNEXT_API_SECRET", ""))
    ap.add_argument("--erpnext-company", default=os.environ.get("ERPNEXT_COMPANY", "Iberia Holding"))
    # Odoo
    ap.add_argument("--odoo-url", default=os.environ.get("ODOO_URL", "http://localhost:8069"))
    ap.add_argument("--odoo-db", default=os.environ.get("ODOO_DB", "kontablo"))
    ap.add_argument("--odoo-user", default=os.environ.get("ODOO_USER", "admin"))
    ap.add_argument("--odoo-password", default=os.environ.get("ODOO_PASSWORD", "admin"))
    ap.add_argument("--odoo-company", default=os.environ.get("ODOO_COMPANY", "Azteca Servicios"))
    args = ap.parse_args()

    if args.mode == "fixtures":
        return run_fixtures()
    return run_live(args)


if __name__ == "__main__":
    raise SystemExit(main())
