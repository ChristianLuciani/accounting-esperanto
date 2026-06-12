"""Unit tests for OdooKontabloConnector (Odoo XML-RPC + Kontablo API mocked)."""

import pytest
import requests

import odoo_client
from odoo_client import OdooKontabloConnector


@pytest.fixture
def connector(monkeypatch):
    c = OdooKontabloConnector("http://odoo", "norte", "admin", "pw", "http://kontablo")
    c._uid = 1  # pretend already authenticated
    return c


def test_get_trial_balance_parses_read_group(connector, monkeypatch):
    fake_rows = [
        {"account_id": [10, "101 Caja"], "debit": 500000.0, "credit": 0.0},
        {"account_id": [11, "201 Proveedores"], "debit": 0.0, "credit": 1724137.93},
        {"account_id": [12, "999 Sin movimiento"], "debit": 0.0, "credit": 0.0},
        {"account_id": False, "debit": 1.0, "credit": 0.0},  # malformed → skipped
    ]
    monkeypatch.setattr(connector, "_execute", lambda *a, **k: fake_rows)

    tb = connector.get_trial_balance()
    codes = {r["local_code"] for r in tb}
    assert codes == {"101", "201"}  # zero-movement and malformed excluded
    caja = next(r for r in tb if r["local_code"] == "101")
    assert caja["local_name"] == "Caja"
    assert caja["debit"] == 500000.0


def test_sync_to_kontablo_builds_batch_payload(connector, monkeypatch):
    monkeypatch.setattr(
        connector, "get_chart_of_accounts",
        lambda *a, **k: [{"code": "101", "name": "Caja", "account_type": "asset_cash"},
                         {"code": "", "name": "Skip me"}],
    )
    captured = {}

    class FakeReq:
        def post(self, url, **kw):
            captured["url"] = url
            captured["json"] = kw["json"]

            class R:
                status_code = 200

                def json(self_inner):
                    return {"mapped_count": 1, "mappings": []}

                def raise_for_status(self_inner):
                    pass

            return R()

    monkeypatch.setattr(odoo_client, "requests", FakeReq())
    connector.sync_to_kontablo(None, "mx", "Norte")
    assert captured["url"].endswith("/mapping/batch")
    payload = captured["json"]
    assert payload["jurisdiction"] == "mx"
    assert [a["local_code"] for a in payload["accounts"]] == ["101"]  # blank code dropped


def test_authentication_failure_raises(connector, monkeypatch):
    connector._uid = None

    class FakeCommon:
        def authenticate(self, *a, **k):
            return False

    monkeypatch.setattr(connector, "_common", lambda: FakeCommon())
    with pytest.raises(PermissionError):
        connector.authenticate()
