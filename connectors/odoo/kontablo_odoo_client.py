# Copyright 2026 Christian Luciani
# Licensed under the Apache License, Version 2.0 (the "License").
# See the LICENSE file in this directory.
#
# Apache-2.0 per the Kontablo connector licensing policy (CLAUDE.md): connectors
# to open-source ERPs (Odoo, ERPNext/Frappe, ...) are Apache-2.0, not BSL, to
# maximize adoption. The protectable commercial assets are the validated
# ontology and the connectors to proprietary ERPs (NetSuite, SAP).
"""Minimal Odoo ↔ Kontablo connector.

Mirrors the contract of ``connectors/erpnext/kontablo_client.py`` so the two
ERPs are interchangeable from the consolidation runner's point of view:

  * :meth:`get_chart_of_accounts(company)` → list of normalized account dicts.
  * :meth:`get_trial_balance(company)` → list of normalized trial-balance rows.

Odoo exposes an `external API`_ over XML-RPC (and JSON-RPC). We use XML-RPC via
the standard-library :mod:`xmlrpc.client` so the connector has no third-party
dependency. The transport is injectable (``models`` / ``common`` callables) so
the parsing logic can be unit-tested without a live Odoo server.

.. _external API: https://www.odoo.com/documentation/17.0/developer/reference/external_api.html
"""

from __future__ import annotations

import xmlrpc.client
from typing import Callable, Dict, List, Optional


def _extract_code(name: str, code: Optional[str]) -> str:
    """Prefer Odoo's account ``code`` field; fall back to a name-leading token."""
    if code:
        return str(code)
    return str(name).split(" ", 1)[0] if name else ""


class OdooKontabloConnector:
    """Pull a chart of accounts and a trial balance from a single Odoo company.

    Parameters
    ----------
    url, db, username, password
        Standard Odoo external-API credentials.
    common, models
        Optional pre-built XML-RPC server proxies (used for testing with a fake
        transport). When omitted, real proxies are created from ``url``.
    """

    def __init__(
        self,
        url: str = "http://localhost:8069",
        db: str = "kontablo",
        username: str = "admin",
        password: str = "admin",
        common: Optional[Callable] = None,
        models: Optional[Callable] = None,
    ):
        self.url = url.rstrip("/")
        self.db = db
        self.username = username
        self.password = password
        self._common = common or xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self._models = models or xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")
        self._uid: Optional[int] = None

    # -- auth ------------------------------------------------------------- #
    def authenticate(self) -> int:
        if self._uid is None:
            self._uid = self._common.authenticate(self.db, self.username, self.password, {})
            if not self._uid:
                raise PermissionError(
                    f"Odoo authentication failed for user {self.username!r} on db {self.db!r}"
                )
        return self._uid

    def _execute(self, model: str, method: str, args: list, kwargs: Optional[dict] = None):
        uid = self.authenticate()
        return self._models.execute_kw(
            self.db, uid, self.password, model, method, args, kwargs or {}
        )

    def _company_id(self, company: str) -> int:
        ids = self._execute(
            "res.company", "search", [[["name", "=", company]]], {"limit": 1}
        )
        if not ids:
            raise LookupError(f"Odoo company not found: {company!r}")
        return ids[0]

    # -- chart of accounts ------------------------------------------------ #
    def get_chart_of_accounts(self, company: str) -> List[Dict]:
        """Return the company's accounts, normalized to the connector contract."""
        cid = self._company_id(company)
        rows = self._execute(
            "account.account",
            "search_read",
            [[["company_id", "=", cid]]],
            {"fields": ["code", "name", "account_type"]},
        )
        return [
            {
                "local_code": _extract_code(r.get("name"), r.get("code")),
                "local_name": r.get("name", ""),
                "account_type": r.get("account_type", ""),
            }
            for r in rows
        ]

    # -- trial balance ---------------------------------------------------- #
    def get_trial_balance(self, company: str, only_posted: bool = True) -> List[Dict]:
        """Aggregate posted journal lines into a per-account trial balance.

        Uses ``account.move.line.read_group`` grouped by account, summing the
        debit and credit columns — Odoo's native trial-balance primitive.
        """
        cid = self._company_id(company)
        domain = [["company_id", "=", cid]]
        if only_posted:
            domain.append(["parent_state", "=", "posted"])
        grouped = self._execute(
            "account.move.line",
            "read_group",
            [domain, ["debit", "credit"], ["account_id"]],
            {"lazy": False},
        )
        balance = []
        for g in grouped:
            account_id = g.get("account_id")
            # read_group returns a [id, "code name"] pair for many2one groupings.
            if isinstance(account_id, (list, tuple)) and len(account_id) == 2:
                label = account_id[1]
            else:
                label = str(account_id)
            code = label.split(" ", 1)[0] if label else ""
            name = label.split(" ", 1)[1] if " " in (label or "") else label
            debit = float(g.get("debit") or 0.0)
            credit = float(g.get("credit") or 0.0)
            if debit == 0.0 and credit == 0.0:
                continue
            balance.append(
                {
                    "local_code": code,
                    "local_name": name,
                    "debit": debit,
                    "credit": credit,
                }
            )
        return balance
