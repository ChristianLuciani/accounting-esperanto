import pytest
import pandas as pd
import os
from api.src.services.mapping import MappingService
from api.src.models.kontablo import SingleMappingRequest

@pytest.fixture
def temp_standards_dir(tmp_path):
    # Create mock standards directory structure
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
    service = MappingService(temp_standards_dir)
    df = service.load_mapping_df("mx")
    assert df is not None
    assert len(df) == 2
    assert "CÓDIGO" in df.columns

def test_load_mapping_invalid_jurisdiction(temp_standards_dir):
    service = MappingService(temp_standards_dir)
    df = service.load_mapping_df("invalid")
    assert df is None

def test_map_account_exact_lookup(temp_standards_dir):
    service = MappingService(temp_standards_dir)
    request = SingleMappingRequest(
        local_code="105",
        local_name="Clientes",
        jurisdiction="mx"
    )
    response = service.map_account(request)
    
    assert response.local_code == "105"
    assert response.match_method == "exact_lookup"
    # We'll need real logic to map "105" to "asset.current.receivables"
    # For now, we test the interface
    assert response.kontablo_id is not None
