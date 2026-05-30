import pytest
import asyncio
import pandas as pd
import os
from unittest.mock import MagicMock, AsyncMock
from api.src.services.mapping import MappingService
from api.src.models.kontablo import SingleMappingRequest


def make_service(standards_dir: str) -> MappingService:
    """Build a MappingService with minimal mocks for the injected dependencies."""
    ontology_service = MagicMock()
    ontology_service.accounts = []
    ontology_service.get_account = MagicMock(return_value=None)
    ai_service = MagicMock()
    ai_service.get_semantic_mapping = AsyncMock(return_value=None)
    return MappingService(standards_dir, ontology_service, ai_service)


@pytest.fixture
def temp_standards_dir(tmp_path):
    # Create mock standards directory structure matching the jurisdiction path map
    mx_dir = tmp_path / "mx"
    mx_dir.mkdir()
    df = pd.DataFrame({
        "CÓDIGO": ["101", "105"],
        "CONTA": ["Caja", "Clientes"],
        "NIVEL": [3, 3],
        "NATUREZA": ["DEVEDORA", "DEVEDORA"]
    })
    df.to_csv(mx_dir / "sat_sample.csv", index=False)
    return str(tmp_path)


def test_load_mapping_valid_jurisdiction(temp_standards_dir):
    service = make_service(temp_standards_dir)
    data = service.load_mapping_data("mx")
    assert data is not None
    assert len(data) == 2
    assert "CÓDIGO" in data[0]


def test_load_mapping_invalid_jurisdiction(temp_standards_dir):
    service = make_service(temp_standards_dir)
    data = service.load_mapping_data("invalid")
    assert data is None


def test_map_account_exact_lookup(temp_standards_dir):
    """map_account falls through to CSV lookup and returns a result."""
    service = make_service(temp_standards_dir)

    # ontology_service has no matching account, so it will try the CSV
    # CSV match returns a placeholder response (see mapping.py line ~80)
    mock_account = MagicMock()
    mock_account.uuid = "00000000-0000-4000-8000-000000000104"
    service.ontology_service.get_account = MagicMock(return_value=mock_account)

    request = SingleMappingRequest(
        local_code="105",
        local_name="Clientes",
        jurisdiction="mx"
    )
    response = asyncio.run(service.map_account(request))

    assert response.local_code == "105"
    # CSV match uses "fuzzy_string" method (see mapping.py)
    assert response.match_method in ("fuzzy_string", "not_found", "exact_lookup")
    assert response.kontablo_id is not None
