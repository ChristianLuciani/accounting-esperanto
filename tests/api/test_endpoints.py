import pytest
from fastapi.testclient import TestClient
from api.src.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_list_accounts():
    # Should list top-level accounts correctly
    response = client.get("/accounts")
    assert response.status_code == 200
    data = response.json()
    assert "accounts" in data
    assert len(data["accounts"]) > 0
    # Check for a core account
    account_ids = [a["id"] for a in data["accounts"]]
    assert "asset.current" in account_ids or "asset.current.receivables" in account_ids

def test_get_account_detail():
    response = client.get("/accounts/asset.current.receivables")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "asset.current.receivables"
    assert data["nature"] == "debit"

def test_map_account_endpoint():
    payload = {
        "local_code": "105",
        "local_name": "Clientes",
        "jurisdiction": "mx"
    }
    response = client.post("/mapping/account", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["local_code"] == "105"
    assert data["kontablo_id"] == "asset.current.receivables"
    assert data["confidence_score"] > 0.8
    assert data["match_method"] == "exact_lookup"

def test_get_local_codes():
    response = client.get("/accounts/asset.current.receivables/local-codes?jurisdiction=mx")
    assert response.status_code == 200
    data = response.json()
    assert "local_codes" in data
    assert any(lc["code"] == "105" for lc in data["local_codes"])
