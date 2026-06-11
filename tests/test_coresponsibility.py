import asyncio
import sys
import os
from uuid import UUID

# Fix sys.path to include the root project
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import using absolute paths from the project root
from api.src.models.kontablo import SingleMappingRequest, AccountNature
from api.src.services.ontology import OntologyService
from api.src.services.mapping import MappingService

class MockAIService:
    async def get_semantic_mapping(self, request, ontology_summary):
        # Simulator: AI "hallucinates" and maps a liquid account to a Fixed Asset node
        # 'asset.noncurrent.ppe' is a valid ID from level3_accounts.yaml
        return {
            "kontablo_id": "asset.noncurrent.ppe",
            "confidence_score": 0.9,
            "justification": "Simulated AI error for testing flags."
        }

async def test_flag():
    print("--- STARTING CO-RESPONSIBILITY FLAG TEST ---")
    
    # 1. Setup Services
    # The correct schema path is core/schemas/level3_accounts.yaml
    ontology_path = os.path.join(project_root, "core/schemas/level3_accounts.yaml")
    ontology = OntologyService(schema_path=ontology_path) 
    ai = MockAIService()
    
    # Use a dummy standards dir to ensure we reach the AI fallback
    mapping_service = MappingService(standards_dir="/tmp/no_standards", ontology_service=ontology, ai_service=ai)

    # 2. Case: The 'Incoherent' Mapping
    # Local account name contains 'Cash' (Current), but AI maps it to 'PPE' (Non-Current)
    request = SingleMappingRequest(
        local_code="CASE-001",
        local_name="Petty Cash Fund",
        jurisdiction="mx",
        nature=AccountNature.debit
    )

    print(f"Requesting mapping for: {request.local_name} (Code: {request.local_code})")
    
    # 3. Perform Mapping
    response = await mapping_service.map_account(request)

    # 4. Assertions/Results
    print(f"\n[RESULTS]")
    print(f"Match Method: {response.match_method}")
    print(f"Target Kontablo ID: {response.kontablo_id}")
    print(f"Inconsistency Flag: {response.inconsistency_flag}")
    print(f"Audit Note: {response.inconsistency_note}")
    print(f"Adjusted Confidence: {response.confidence_score}")

    # The flag should be True because 'Cash' is in name and ID is 'noncurrent'
    assert response.inconsistency_flag, (
        "System ignored the inconsistency: a 'Petty Cash Fund' account mapped to "
        "a non-current PPE node must raise the deterministic boundary flag."
    )
    print("\n✅ TEST PASSED: System successfully flagged a deterministic boundary violation.")

if __name__ == "__main__":
    asyncio.run(test_flag())
