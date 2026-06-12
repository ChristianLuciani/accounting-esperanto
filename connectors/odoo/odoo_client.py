"""
Odoo ↔ Kontablo connector (Apache-2.0).

Licensing: per Kontablo's connector policy (CLAUDE.md, decided 2026-05-28),
connectors to open-source ERPs (Odoo, ERPNext/Frappe, …) are Apache-2.0, not
BSL — the open interface is opened to grow the ecosystem; the protectable assets
are the validated ontology and connectors to proprietary ERPs.

Odoo exposes an external API over XML-RPC (stdlib ``xmlrpc.client`` — no third-
party dependency). This connector authenticates, pulls the chart of accounts
(``account.account``) and a trial balance (aggregated ``account.move.line``),
and shapes both into Kontablo's request payloads — the same payloads the
ERPNext connector produces, so a single Kontablo engine consolidates both.

No business logic keys on free text; jurisdiction is an explicit argument.
"""

from __future__ import annotations

import xmlrpc.client
from typing import Dict, List, Optional

import requests


class OdooKontabloConnector:
    def __init__(
        self,
        odoo_url: str,
        db: str,
        username: str,
        password: str,
        kontablo_url: str = "http://localhost:8000",
    ):
        self.odoo_url = odoo_url.rstrip("/")
        self.db = db
        self.username = username
        self.password = password
        self.kontablo_url = kontablo_url
        self._uid: Optional[int] = None
        self._models = None

    # -- Odoo XML-RPC plumbing ---------------------------------------------
    def _common(self):
        return xmlrpc.client.ServerProxy(f"{self.odoo_url}/xmlrpc/2/common")

    def _object(self):
        if self._models is None:
            self._models = xmlrpc.client.ServerProxy(f"{self.odoo_url}/xmlrpc/2/object")
        return self._models

    def authenticate(self) -> int:
        """Authenticate and cache the Odoo uid."""
        self._uid = self._common().authenticate(self.db, self.username, self.password, {})
        if not self._uid:
            raise PermissionError("Odoo authentication failed (check db/user/password).")
        return self._uid

    def _execute(self, model: str, method: str, *args, **kwargs):
        if self._uid is None:
            self.authenticate()
        return self._object().execute_kw(
            self.db, self._uid, self.password, model, method, list(args), kwargs
        )

    # -- chart of accounts -------------------------------------------------
    def get_chart_of_accounts(self, company_id: Optional[int] = None) -> List[Dict]:
        """Read account.account rows (code, name, account_type)."""
        domain = []
        if company_id is not None:
            domain.append(["company_id", "=", company_id])
        return self._execute(
            "account.account",
            "search_read",
            domain,
            fields=["code", "name", "account_type"],
        )

    def get_trial_balance(self, company_id: Optional[int] = None) -> List[Dict]:
        """Aggregate posted journal items into per-account debit/credit totals.

        Returns rows shaped as {local_code, local_name, debit, credit}.
        """
        domain = [["parent_state", "=", "posted"]]
        if company_id is not None:
            domain.append(["company_id", "=", company_id])
        rows = self._execute(
            "account.move.line",
            "read_group",
            domain,
            fields=["debit:sum", "credit:sum"],
            groupby=["account_id"],
            lazy=False,
        )
        out = []
        for r in rows:
            account = r.get("account_id")
            # Odoo read_group returns account_id as [id, "code name"] or False.
            if not account:
                continue
            label = account[1] if isinstance(account, (list, tuple)) else str(account)
            code = label.split(" ", 1)[0]
            name = label.split(" ", 1)[1] if " " in label else label
            debit = float(r.get("debit", 0.0) or 0.0)
            credit = float(r.get("credit", 0.0) or 0.0)
            if debit or credit:
                out.append({"local_code": code, "local_name": name,
                            "debit": debit, "credit": credit})
        return out

    # -- push to Kontablo --------------------------------------------------
    def sync_to_kontablo(self, company_id: Optional[int], jurisdiction: str,
                         company_label: str) -> Dict:
        accounts = self.get_chart_of_accounts(company_id)
        payload = {
            "company_id": company_label,
            "jurisdiction": jurisdiction,
            "accounts": [
                {"local_code": a["code"], "local_name": a["name"],
                 "jurisdiction": jurisdiction}
                for a in accounts if a.get("code")
            ],
        }
        response = requests.post(f"{self.kontablo_url}/mapping/batch", json=payload)
        response.raise_for_status()
        return response.json()

    def consolidate_in_kontablo(self, company_id: Optional[int], jurisdiction: str,
                                currency: str, reporting_date: str,
                                company_label: str) -> Dict:
        tb = self.get_trial_balance(company_id)
        payload = {
            "target_currency": currency,
            "trial_balances": [
                {
                    "subsidiary_id": company_label,
                    "jurisdiction": jurisdiction,
                    "currency": currency,
                    "reporting_date": reporting_date,
                    "entries": tb,
                }
            ],
        }
        response = requests.post(f"{self.kontablo_url}/consolidation", json=payload)
        response.raise_for_status()
        return response.json()
