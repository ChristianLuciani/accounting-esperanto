"""The REST consolidation response carries per-entry mapping provenance
(ADR-016): a ``mapping_audit`` array (the ``fx_audit`` pattern applied to the
mapping decision) and a ``source_entries`` fiber size per consolidated line, so
no local code, name, or amount is discarded at the API boundary. Deterministic:
uses Tier-1 codes and a manual exchange rate only (no AI, no network)."""

from fastapi.testclient import TestClient

from api.src.main import app

client = TestClient(app, raise_server_exceptions=False)


def _payload():
    return {
        "target_currency": "USD",
        "trial_balances": [
            {
                "subsidiary_id": "acme-mx",
                "jurisdiction": "mx",
                "currency": "MXN",
                "reporting_date": "2026-03-31",
                "entries": [
                    {"local_code": "101", "local_name": "Caja", "debit": 100.0, "credit": 0.0},
                    {"local_code": "102", "local_name": "Bancos", "debit": 50.0, "credit": 0.0},
                ],
                "exchange_rate": 0.05,
                "exchange_rate_as_of": "2026-03-31",
                "exchange_rate_note": "test pinned rate",
            },
            {
                "subsidiary_id": "acme-mx-2",
                "jurisdiction": "mx",
                "currency": "MXN",
                "reporting_date": "2026-03-31",
                "entries": [
                    {"local_code": "101", "local_name": "Caja chica", "debit": 20.0, "credit": 0.0},
                ],
                "exchange_rate": 0.05,
            },
        ],
    }


def test_consolidation_exposes_mapping_audit_and_fiber_sizes():
    r = client.post("/consolidation", json=_payload())
    assert r.status_code == 200
    body = r.json()

    # One provenance record per source entry — nothing dropped at the boundary.
    audit = body["mapping_audit"]
    assert len(audit) == 3
    for rec in audit:
        assert rec["subsidiary_id"]
        assert rec["jurisdiction"] == "mx"
        assert rec["local_code"]
        assert rec["kontablo_id"]
        assert rec["match_method"] == "exact_lookup"
        assert rec["tier"] == "tier1_exact"
        assert rec["confidence"] == 1.0
        # Original local amounts survive alongside the converted figures.
        assert rec["debit_local"] in (100.0, 50.0, 20.0)

    # Fiber sizes: 101 appears in two subsidiaries, 102 in one.
    lines = {line["kontablo_id"]: line for line in body["results"]}
    cash = lines["asset.current.cash"]
    bank = lines["asset.current.bank"]
    assert cash["source_entries"] == 2
    assert bank["source_entries"] == 1

    # Reconstruction: each consolidated line equals the sum of its fiber.
    for k_id, line in lines.items():
        fiber = [a for a in audit if a["kontablo_id"] == k_id]
        assert len(fiber) == line["source_entries"]
        assert round(sum(a["debit"] for a in fiber), 2) == line["debit"]
        assert round(sum(a["credit"] for a in fiber), 2) == line["credit"]


def test_single_mapping_response_reports_tier():
    r = client.post(
        "/mapping/account",
        json={"local_code": "101", "local_name": "Caja", "jurisdiction": "mx"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["match_method"] == "exact_lookup"
    assert body["tier"] == "tier1_exact"
