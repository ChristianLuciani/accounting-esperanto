"""Contract tests: the connector's outgoing payloads must satisfy the real
Kontablo API request models, and a full round-trip (ERPNext → Kontablo → ERPNext
write-back) must succeed against the actual FastAPI app.

The connector POSTs to `/mapping/batch` and `/consolidation`. Those endpoints
live in `api/src/main.py` and are validated by `api.src.models.kontablo`
(BatchMappingRequest / ConsolidationRequest). This test pins that contract so a
drift in either side fails loudly.

(Note: the separate `/api/v1/map` MicroSaaS surface in `api/rest/main.py` uses a
different request schema and is NOT what this connector targets.)
"""

import pytest

import kontablo_client
from kontablo_client import ERPNextKontabloConnector

pydantic = pytest.importorskip("pydantic")

from api.src.models.kontablo import BatchMappingRequest, ConsolidationRequest  # noqa: E402

SAMPLE_COA = [
    {"name": "572", "account_name": "Bancos", "is_group": 0},
    {"name": "430", "account_name": "Clientes", "is_group": 0},
]


class _Resp:
    def __init__(self, data, status=200):
        self._d, self.status_code = data, status

    def json(self):
        return self._d

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests
            raise requests.exceptions.HTTPError(self.status_code)


def test_batch_mapping_payload_satisfies_api_model(monkeypatch):
    """The dict the connector POSTs to /mapping/batch must parse cleanly into
    the server's BatchMappingRequest model."""
    captured = {}

    class FakeReq:
        def get(self, url, **kw):
            return _Resp({"data": SAMPLE_COA})

        def post(self, url, **kw):
            captured["json"] = kw["json"]
            return _Resp({"mapped_count": 2, "mappings": []})

    monkeypatch.setattr(kontablo_client, "requests", FakeReq())
    conn = ERPNextKontabloConnector("http://erp", "k", "s", "http://kontablo")
    conn.sync_to_kontablo("Iberica", "es")

    # The real server-side model must accept this payload without error.
    model = BatchMappingRequest(**captured["json"])
    assert model.company_id == "Iberica"
    assert model.jurisdiction == "es"
    assert [a.local_code for a in model.accounts] == ["572", "430"]


def test_consolidation_payload_satisfies_api_model(monkeypatch):
    captured = {}
    tb_message = [
        ["c"],
        [{"account": "572", "account_name": "Bancos", "debit": 100.0, "credit": 0.0},
         {"account": "100", "account_name": "Capital", "debit": 0.0, "credit": 100.0}],
    ]

    class FakeReq:
        def get(self, url, **kw):
            return _Resp({"message": tb_message})

        def post(self, url, **kw):
            captured["json"] = kw["json"]
            return _Resp({"results": []})

    monkeypatch.setattr(kontablo_client, "requests", FakeReq())
    conn = ERPNextKontabloConnector("http://erp", "k", "s", "http://kontablo")
    conn.consolidate_in_kontablo("Iberica", "2026-06-11", "es", "EUR")

    model = ConsolidationRequest(**captured["json"])
    assert model.target_currency == "EUR"
    assert model.trial_balances[0].jurisdiction == "es"
    assert {e.local_code for e in model.trial_balances[0].entries} == {"572", "100"}


def test_full_round_trip_against_live_fastapi_app(monkeypatch):
    """ERPNext (mocked) → real Kontablo FastAPI app (TestClient) → ERPNext
    write-back (mocked). Exercises the genuine /mapping/batch handler."""
    fastapi_testclient = pytest.importorskip("fastapi.testclient")
    from api.src.main import app

    client = fastapi_testclient.TestClient(app)
    put_calls = []

    class RoutingRequests:
        """ERPNext calls return canned data; Kontablo calls hit the real app."""

        def get(self, url, **kw):
            if "/api/resource/Account" in url:
                return _Resp({"data": SAMPLE_COA})
            return _Resp({}, 404)

        def post(self, url, **kw):
            if "/mapping/batch" in url:
                # Route to the real FastAPI app via TestClient.
                r = client.post("/mapping/batch", json=kw["json"])
                return r  # httpx Response: has .json()/.raise_for_status()/.status_code
            return _Resp({}, 404)

        def put(self, url, **kw):
            put_calls.append((url, kw["json"]))
            return _Resp({"data": {}})

    monkeypatch.setattr(kontablo_client, "requests", RoutingRequests())
    conn = ERPNextKontabloConnector("http://erp", "k", "s", "http://kontablo")

    # 1) pull + map through the REAL app
    result = conn.sync_to_kontablo("Iberica", "es")
    assert result["total_accounts"] == 2
    assert result["mapped_count"] >= 1  # at least Bancos (572) resolves exactly
    mappings = result["mappings"]
    assert any(m["match_method"] == "exact_lookup" for m in mappings)

    # 2) write the mappings back onto ERPNext accounts
    conn.write_back_mappings(mappings)
    assert {u.rsplit("/", 1)[-1] for u, _ in put_calls} == {"572", "430"}
    # the written-back body carries a real kontablo_id from the live app
    written_ids = {body["kontablo_id"] for _, body in put_calls}
    assert "asset.current.cash" in written_ids
