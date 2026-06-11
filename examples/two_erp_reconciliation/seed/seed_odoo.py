#!/usr/bin/env python3
"""
Seed the Odoo container with the Mexican subsidiary for the demo.

Creates a company on a SAT-style chart and posts a handful of opening journal
entries (including the intercompany payable to the Spanish parent) so that
``run_reconciliation.py --source live`` can pull a real trial balance.

Data mirrors ``fixtures/odoo_norte_trial_balance.json`` so the live run matches
the offline/fixtures run. Amounts are synthetic (balanced by construction).

Usage (after `docker compose up`):
    ODOO_URL=http://localhost:8069 ODOO_DB=norte ODOO_USER=admin \
    ODOO_PASSWORD=admin python seed/seed_odoo.py

NOTE: This script is provided as a runnable reference for a live Odoo instance.
It is not exercised in CI (no Odoo in CI); the deterministic engine path it
feeds IS covered by tests/examples/test_two_erp_reconciliation.py.
"""

import json
import os
import sys
import xmlrpc.client

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURE = os.path.join(os.path.dirname(HERE), "fixtures", "odoo_norte_trial_balance.json")


def main() -> None:
    url = os.environ.get("ODOO_URL", "http://localhost:8069")
    db = os.environ.get("ODOO_DB", "norte")
    user = os.environ.get("ODOO_USER", "admin")
    pw = os.environ.get("ODOO_PASSWORD", "admin")

    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, user, pw, {})
    if not uid:
        sys.exit("Odoo authentication failed — is the container up and the db initialised?")
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

    def call(model, method, *args, **kw):
        return models.execute_kw(db, uid, pw, model, method, list(args), kw)

    doc = json.load(open(FIXTURE, encoding="utf-8"))
    print(f"Seeding Odoo company '{doc['company']}' ({doc['jurisdiction'].upper()} / {doc['standard']})")

    # 1) Ensure accounts exist (account.account: code + name + a coarse type).
    type_for = lambda code: (
        "asset_cash" if code in {"101", "102"} else
        "asset_receivable" if code == "105" else
        "liability_payable" if code == "201" else
        "income" if code.startswith("4") else
        "expense" if code.startswith("5") else
        "equity" if code in {"300", "305"} else
        "asset_current"
    )
    code_to_id = {}
    for e in doc["entries"]:
        existing = call("account.account", "search", [["code", "=", e["local_code"]]])
        if existing:
            code_to_id[e["local_code"]] = existing[0]
            continue
        code_to_id[e["local_code"]] = call("account.account", "create", {
            "code": e["local_code"],
            "name": e["local_name"],
            "account_type": type_for(e["local_code"]),
        })

    # 2) Post one opening journal entry carrying the whole trial balance.
    journal = call("account.journal", "search", [["type", "=", "general"]])[0]
    lines = [(0, 0, {
        "account_id": code_to_id[e["local_code"]],
        "name": e["local_name"],
        "debit": e["debit"],
        "credit": e["credit"],
    }) for e in doc["entries"]]
    move = call("account.move", "create", {
        "journal_id": journal,
        "ref": "Kontablo demo opening balance",
        "line_ids": lines,
    })
    call("account.move", "action_post", [move])
    print(f"Posted opening journal entry {move} with {len(lines)} lines. Done.")


if __name__ == "__main__":
    main()
