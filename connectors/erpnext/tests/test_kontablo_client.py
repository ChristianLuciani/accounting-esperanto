"""Unit tests for ERPNextKontabloConnector (ERPNext REST + Kontablo API mocked).

All real assertions (per CLAUDE.md "tests must assert"). No live ERPNext or
Kontablo server is required — every HTTP call is mocked, including error paths.
"""

import json

import pytest
import requests

import kontablo_client
from kontablo_client import ERPNextKontabloConnector


# --- sample ERPNext payloads -------------------------------------------------
SAMPLE_COA = [
    {"name": "572", "account_name": "Bancos", "parent_account": None,
     "is_group": 0, "root_type": "Asset", "account_type": "Bank",
     "account_currency": "EUR"},
    {"name": "430", "account_name": "Clientes", "parent_account": None,
     "is_group": 0, "root_type": "Asset", "account_type": "Receivable",
     "account_currency": "EUR"},
]

SAMPLE_KONTABLO_BATCH_RESP = {
    "company_id": "Iberica",
    "jurisdiction": "es",
    "total_accounts": 2,
    "mapped_count": 2,
    "unmapped_count": 0,
    "coverage_pct": 1.0,
    "mappings": [
        {"local_code": "572", "kontablo_id": "asset.current.cash",
         "kontablo_uuid": "00000000-0000-4000-8000-000000000101",
         "label_en": "Cash", "confidence_score": 1.0,
         "match_method": "exact_lookup"},
        {"local_code": "430", "kontablo_id": "asset.current.receivables",
         "kontablo_uuid": "00000000-0000-4000-8000-000000000104",
         "label_en": "Trade Receivables", "confidence_score": 1.0,
         "match_method": "exact_lookup"},
    ],
}


@pytest.fixture
def connector():
    return ERPNextKontabloConnector(
        erpnext_url="http://erp.example",
        api_key="k",
        api_secret="s",
        kontablo_url="http://kontablo.example",
    )


class RecordingRequests:
    """Records calls and returns programmed responses per (method, url-substring)."""

    def __init__(self, fake_response_cls):
        self.calls = []
        self._routes = {}
        self._fr = fake_response_cls

    def route(self, method, url_substr, json_data=None, status_code=200):
        self._routes[(method, url_substr)] = (json_data, status_code)

    def _dispatch(self, method, url, **kwargs):
        self.calls.append({"method": method, "url": url, "kwargs": kwargs})
        for (m, sub), (data, code) in self._routes.items():
            if m == method and sub in url:
                return self._fr(data, code)
        return self._fr({}, 404)

    def get(self, url, **kwargs):
        return self._dispatch("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self._dispatch("POST", url, **kwargs)

    def put(self, url, **kwargs):
        return self._dispatch("PUT", url, **kwargs)


@pytest.fixture
def http(monkeypatch, fake_response_cls):
    rec = RecordingRequests(fake_response_cls)
    monkeypatch.setattr(kontablo_client, "requests", rec)
    # keep exceptions reachable on the patched object
    rec.exceptions = requests.exceptions
    return rec


# --- get_chart_of_accounts ---------------------------------------------------
def test_get_chart_of_accounts_calls_erpnext_and_returns_data(connector, http):
    http.route("GET", "/api/resource/Account", {"data": SAMPLE_COA})
    coa = connector.get_chart_of_accounts("Iberica")
    assert coa == SAMPLE_COA
    call = http.calls[0]
    assert call["url"].endswith("/api/resource/Account")
    # auth header carries token key:secret
    assert call["kwargs"]["headers"]["Authorization"] == "token k:s"
    # company filter is JSON-encoded
    filters = json.loads(call["kwargs"]["params"]["filters"])
    assert filters == [["company", "=", "Iberica"]]


def test_get_chart_of_accounts_propagates_http_error(connector, http):
    http.route("GET", "/api/resource/Account", {"exc": "boom"}, status_code=500)
    with pytest.raises(requests.exceptions.HTTPError):
        connector.get_chart_of_accounts("Iberica")


# --- sync_to_kontablo (payload shape) ---------------------------------------
def test_sync_to_kontablo_builds_expected_payload(connector, http):
    http.route("GET", "/api/resource/Account", {"data": SAMPLE_COA})
    http.route("POST", "/mapping/batch", SAMPLE_KONTABLO_BATCH_RESP)

    result = connector.sync_to_kontablo("Iberica", "es")
    assert result["mapped_count"] == 2

    post_call = next(c for c in http.calls if c["method"] == "POST")
    payload = post_call["kwargs"]["json"]
    assert payload["company_id"] == "Iberica"
    assert payload["jurisdiction"] == "es"
    assert len(payload["accounts"]) == 2
    first = payload["accounts"][0]
    assert set(first) == {"local_code", "local_name", "jurisdiction"}
    assert first["local_code"] == "572"
    assert first["local_name"] == "Bancos"


def test_sync_to_kontablo_raises_when_kontablo_unreachable(connector, http, monkeypatch):
    http.route("GET", "/api/resource/Account", {"data": SAMPLE_COA})

    def boom(url, **kwargs):
        raise requests.exceptions.ConnectionError("kontablo down")

    monkeypatch.setattr(http, "post", boom)
    with pytest.raises(requests.exceptions.ConnectionError):
        connector.sync_to_kontablo("Iberica", "es")


def test_sync_to_kontablo_raises_on_kontablo_4xx(connector, http):
    http.route("GET", "/api/resource/Account", {"data": SAMPLE_COA})
    http.route("POST", "/mapping/batch", {"detail": "bad request"}, status_code=422)
    with pytest.raises(requests.exceptions.HTTPError):
        connector.sync_to_kontablo("Iberica", "es")


# --- write-back --------------------------------------------------------------
def test_write_back_mappings_puts_uuid_to_each_account(connector, http):
    http.route("PUT", "/api/resource/Account/", {"data": {}})
    results = connector.write_back_mappings(SAMPLE_KONTABLO_BATCH_RESP["mappings"])
    assert len(results) == 2
    put_calls = [c for c in http.calls if c["method"] == "PUT"]
    assert put_calls[0]["url"].endswith("/api/resource/Account/572")
    body = put_calls[0]["kwargs"]["json"]
    assert body["kontablo_uuid"] == "00000000-0000-4000-8000-000000000101"
    assert body["kontablo_id"] == "asset.current.cash"
    assert body["kontablo_confidence"] == 1.0


def test_write_back_skips_entries_without_local_code(connector, http):
    http.route("PUT", "/api/resource/Account/", {"data": {}})
    results = connector.write_back_mappings([{"kontablo_id": "x"}])  # no local_code
    assert results == []
    assert not [c for c in http.calls if c["method"] == "PUT"]


# --- consolidation path ------------------------------------------------------
def test_consolidate_in_kontablo_parses_trial_balance_report(connector, http):
    # ERPNext report shape: message = [columns, data]
    tb_message = [
        ["col1", "col2"],
        [
            {"account": "700", "account_name": "Ventas", "debit": 0.0, "credit": 300000.0},
            {"account": "572", "account_name": "Bancos", "debit": 300000.0, "credit": 0.0},
            {"account": "ZERO", "debit": 0.0, "credit": 0.0},  # skipped (no movement)
        ],
    ]
    http.route("GET", "trial_balance.trial_balance.execute", {"message": tb_message})
    http.route("POST", "/consolidation", {"results": [], "entities_consolidated": 1})

    connector.consolidate_in_kontablo("Iberica", "2026-06-11", "es", "EUR")
    post_call = next(c for c in http.calls if c["method"] == "POST")
    payload = post_call["kwargs"]["json"]
    assert payload["target_currency"] == "EUR"
    tb = payload["trial_balances"][0]
    assert tb["subsidiary_id"] == "Iberica"
    assert tb["jurisdiction"] == "es"
    # the zero-movement row is excluded
    codes = {e["local_code"] for e in tb["entries"]}
    assert codes == {"700", "572"}
