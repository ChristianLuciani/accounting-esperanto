"""Robustness regression tests for the deterministic REST API.

A malformed-but-parseable request (NaN/Infinity amounts, a non-positive FX rate,
or amounts that overflow on summation) must return a clean 4xx — never an opaque
500 and never a silently-corrupted consolidation. Before hardening, a raw `NaN`
debit was parsed, propagated as `nan`, and crashed response serialization with
an unhandled 500.
"""

from fastapi.testclient import TestClient

from api.src.main import app

# raise_server_exceptions=False so a 500 surfaces as a 500 response (what a real
# client sees) instead of re-raising into the test.
client = TestClient(app, raise_server_exceptions=False)
JSON = {"content-type": "application/json"}


def _tb(entries, **extra):
    tb = {
        "subsidiary_id": "a",
        "jurisdiction": "mx",
        "currency": "MXN",
        "reporting_date": "2026-03-31",
        "entries": entries,
    }
    tb.update(extra)
    return {"target_currency": "USD", "trial_balances": [tb]}


def test_raw_nan_debit_is_clean_422_not_500():
    raw = ('{"target_currency":"USD","trial_balances":[{"subsidiary_id":"a",'
           '"jurisdiction":"mx","currency":"MXN","reporting_date":"2026-03-31",'
           '"entries":[{"local_code":"101","local_name":"Caja","debit":NaN,"credit":0}]}]}')
    r = client.post("/consolidation", content=raw, headers=JSON)
    assert r.status_code == 422
    body = r.json()  # must be valid JSON (the bug was this crashing serialization)
    assert "finite" in str(body).lower()


def test_raw_infinity_credit_is_clean_422():
    raw = ('{"target_currency":"USD","trial_balances":[{"subsidiary_id":"a",'
           '"jurisdiction":"mx","currency":"MXN","reporting_date":"2026-03-31",'
           '"entries":[{"local_code":"101","debit":0,"credit":Infinity}]}]}')
    r = client.post("/consolidation", content=raw, headers=JSON)
    assert r.status_code == 422


def test_zero_exchange_rate_rejected():
    r = client.post("/consolidation", json=_tb([{"local_code": "101", "debit": 100, "credit": 0}], exchange_rate=0.0))
    assert r.status_code == 422


def test_negative_exchange_rate_rejected():
    r = client.post("/consolidation", json=_tb([{"local_code": "101", "debit": 100, "credit": 0}], exchange_rate=-2.0))
    assert r.status_code == 422


def test_finite_overflow_is_clean_400_not_500():
    huge = [{"local_code": "Cash", "local_name": "Cash", "debit": 1e308, "credit": 0},
            {"local_code": "Cash", "local_name": "Cash", "debit": 1e308, "credit": 0}]
    r = client.post("/consolidation", json={"target_currency": "USD", "trial_balances": [
        {"subsidiary_id": "a", "jurisdiction": "us", "currency": "USD",
         "reporting_date": "2026-03-31", "entries": huge}]})
    assert r.status_code == 400
    assert "overflow" in r.json()["detail"].lower()


def test_classification_non_finite_amount_rejected():
    r = client.post("/classification/transaction",
                    content='{"narration":"x","jurisdiction":"mx","amount":Infinity}', headers=JSON)
    assert r.status_code == 422


def test_valid_consolidation_reports_balance():
    r = client.post("/consolidation", json=_tb([
        {"local_code": "101", "local_name": "Caja", "debit": 100, "credit": 0},
        {"local_code": "301", "local_name": "Capital", "debit": 0, "credit": 100},
    ]))
    assert r.status_code == 200
    data = r.json()
    # New double-entry observability fields (parity with gRPC/MCP).
    assert data["balanced"] is True
    assert data["balance_difference"] == 0.0
    assert "fx_audit" in data


def test_negative_amounts_still_accepted():
    # Negatives are legitimate (contra entries); only non-finite is rejected.
    r = client.post("/consolidation", json=_tb([
        {"local_code": "101", "local_name": "Caja", "debit": -100, "credit": 0},
        {"local_code": "301", "local_name": "Capital", "debit": 0, "credit": -100},
    ]))
    assert r.status_code == 200
