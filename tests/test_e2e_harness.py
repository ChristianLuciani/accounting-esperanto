"""Fast guards for the e2e harness that need no Docker.

These keep the Dockerized two-ERP harness honest on the fast CI gate:
  * the Odoo connector parses Odoo's XML-RPC shapes correctly (fake transport);
  * the runner's row→Line adapter derives nature/amount correctly;
  * the runner's fixtures mode reproduces the reconciliation invariants.

The heavy live path (real ERPNext + real Odoo) runs only in the opt-in
`.github/workflows/e2e.yml` workflow — never on the fast PR gate.
"""

from connectors.odoo.kontablo_odoo_client import OdooKontabloConnector
from e2e.runner import _leading_code, _row_to_line, run_fixtures


class _FakeProxy:
    """Minimal stand-in for an Odoo XML-RPC ServerProxy."""

    def __init__(self, responses):
        self._responses = responses

    def authenticate(self, db, user, pwd, ctx):
        return 7  # non-zero uid

    def execute_kw(self, db, uid, pwd, model, method, args, kwargs=None):
        return self._responses[(model, method)]


def test_odoo_connector_chart_and_trial_balance():
    common = _FakeProxy({})
    models = _FakeProxy({
        ("res.company", "search"): [42],
        ("account.account", "search_read"): [
            {"code": "102", "name": "Bancos", "account_type": "asset_cash"},
            {"code": "216", "name": "Cuentas por pagar a partes relacionadas",
             "account_type": "liability_payable"},
        ],
        ("account.move.line", "read_group"): [
            {"account_id": [11, "102 Bancos"], "debit": 800000.0, "credit": 0.0},
            {"account_id": [12, "216 Cuentas por pagar a partes relacionadas"],
             "debit": 0.0, "credit": 600000.0},
            {"account_id": [13, "999 Empty"], "debit": 0.0, "credit": 0.0},  # dropped
        ],
    })
    conn = OdooKontabloConnector(common=common, models=models)

    coa = conn.get_chart_of_accounts("Azteca Servicios")
    assert {a["local_code"] for a in coa} == {"102", "216"}

    tb = conn.get_trial_balance("Azteca Servicios")
    codes = {r["local_code"]: r for r in tb}
    assert set(codes) == {"102", "216"}  # zero-balance row dropped
    assert codes["102"]["debit"] == 800000.0
    assert codes["216"]["credit"] == 600000.0


def test_leading_code_extraction():
    assert _leading_code("4330 - Clientes empresas del grupo - IH") == "4330"
    assert _leading_code("216 Cuentas por pagar a partes relacionadas") == "216"
    assert _leading_code("701.04 Finance Costs") == "701.04"


def test_row_to_line_nets_debit_credit():
    ln = _row_to_line("102", "Bancos", 800000.0, 0.0)
    assert ln.nature == "debit" and ln.amount == 800000.0
    ln = _row_to_line("216", "IC payable", 0.0, 600000.0)
    assert ln.nature == "credit" and ln.amount == 600000.0
    ln = _row_to_line("430", "Clientes", 50000.0, 10000.0)
    assert ln.nature == "debit" and ln.amount == 40000.0


def test_runner_fixtures_mode_passes():
    assert run_fixtures() == 0
