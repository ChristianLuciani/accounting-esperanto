import csv
import os
from typing import List, Optional, Dict
from ..models.kontablo import SingleMappingRequest, SingleMappingResponse
from uuid import UUID
from .ontology import OntologyService
from .ai import AIService

class MappingService:
    def __init__(self, standards_dir: str, ontology_service: OntologyService, ai_service: AIService):
        self.standards_dir = standards_dir
        self.ontology_service = ontology_service
        self.ai_service = ai_service
        self.cached_mappings: Dict[str, List[Dict]] = {}

    def get_standard_path(self, jurisdiction: str) -> Optional[str]:
        path_map = {
            "mx": "mx/sat_sample.csv",
            "br": "br/plano_referencial_sample.csv",
            "ru": "ru/plan_schetov_sample.csv",
            "fr": "fr/pcg_fr_sample.csv",
            "il": "il/israel_gaap_sample.csv",
            "in": "in/ind_as_gst_sample.csv"
        }
        rel_path = path_map.get(jurisdiction.lower())
        if not rel_path:
            return None
        return os.path.join(self.standards_dir, rel_path)

    def load_mapping_data(self, jurisdiction: str) -> Optional[List[Dict]]:
        jurisdiction = jurisdiction.lower()
        if jurisdiction in self.cached_mappings:
            return self.cached_mappings[jurisdiction]
        
        path = self.get_standard_path(jurisdiction)
        if not path or not os.path.exists(path):
            return None
        
        try:
            with open(path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
                self.cached_mappings[jurisdiction] = data
                return data
        except Exception as e:
            print(f"Error loading mapping for {jurisdiction}: {e}")
            return None

    def _get_ontology_summary(self) -> str:
        # Create a compact summary for the LLM
        return "\n".join([f"- {a.id}: {a.label_en} ({a.nature})" for a in self.ontology_service.accounts])


    async def map_account(self, request: SingleMappingRequest) -> SingleMappingResponse:
        response = await self._perform_mapping(request)
        
        # 5. Global Co-responsibility Check for ALL mapped results
        if response.kontablo_id != "unknown":
            k_account = self.ontology_service.get_account(response.kontablo_id)
            if k_account:
                self.validate_co_responsibility(request, response, k_account)
        
        return response

    async def _perform_mapping(self, request: SingleMappingRequest) -> SingleMappingResponse:
        # 1. Check in YAML ontology first (direct mapping)
        jurisdiction = request.jurisdiction.lower()
        for account in self.ontology_service.accounts:
            if account.local_codes and account.local_codes.get(jurisdiction) == str(request.local_code):
                return SingleMappingResponse(
                    local_code=request.local_code,
                    kontablo_id=account.id,
                    kontablo_uuid=account.uuid,
                    label_en=account.label_en,
                    confidence_score=1.0,
                    match_method="exact_lookup",
                    justification=f"Direct match found in Kontablo {jurisdiction.upper()} ontology."
                )

        # 2. Then check in jurisdiction research CSV
        data = self.load_mapping_data(request.jurisdiction)
        if data:
            code_cols = ["CÓDIGO", "Code", "Code PCG", "CONTA"]
            match = None
            for row in data:
                for col in code_cols:
                    if col in row and str(row[col]) == str(request.local_code):
                        match = row
                        break
                if match:
                    break
            
            if match:
                # The research CSVs carry the local chart (code, name, level)
                # but no Kontablo node, so a hit here cannot produce a mapping
                # by itself. It DOES confirm the code exists in the
                # jurisdiction's statutory chart and gives us its official
                # name — use that to enrich the request for the semantic
                # tier instead of fabricating a node.
                if not request.local_name:
                    name_cols = ["NOMBRE DE LA CUENTA Y/O SUBCUENTA", "Name",
                                 "Nom du compte", "NOME DA CONTA"]
                    for col in name_cols:
                        if match.get(col):
                            request.local_name = str(match[col])
                            break

        # 3. AI Semantic Fallback
        if self.ai_service:
            ontology_summary = self._get_ontology_summary()
            ai_result = await self.ai_service.get_semantic_mapping(request, ontology_summary)
            
            if ai_result:
                mapped_id = ai_result.get("kontablo_id")
                # Look up full details from ontology
                k_account = self.ontology_service.get_account(mapped_id)
                if k_account:
                    return SingleMappingResponse(
                        local_code=request.local_code,
                        kontablo_id=k_account.id,
                        kontablo_uuid=k_account.uuid,
                        label_en=k_account.label_en,
                        confidence_score=ai_result.get("confidence_score", 0.5),
                        match_method="semantic_ai",
                        justification=ai_result.get("justification", "Identified by AI mapping.")
                    )

        # 4. Final Fallback (Not Found)
        return SingleMappingResponse(
            local_code=request.local_code,
            kontablo_id="unknown",
            kontablo_uuid=UUID("00000000-0000-4000-b000-000000000000"),
            label_en="Unmapped Account",
            confidence_score=0.0,
            match_method="not_found",
            justification="No mapping found through lookup or AI fallback."
        )
    def validate_co_responsibility(self, request: SingleMappingRequest, response: SingleMappingResponse, k_account):
        """
        Implements the Co-responsibility Architecture.
        Checks if the mapping violates the deterministic rules of the Kontablo Graph.
        """
        inconsistencies = []
        
        # Rule 1: Nature Mismatch (Debit vs Credit)
        if request.nature and request.nature != k_account.nature:
            # We allow it, but we FLAG it as a major inconsistency
            inconsistencies.append(f"Nature Mismatch: Account is {request.nature} but target node {k_account.id} is {k_account.nature}.")
        
        # Rule 2: Deterministic Boundary Violation (Example: Cash vs Non-Current)
        if "cash" in request.local_name.lower() or "bank" in request.local_name.lower():
            if "noncurrent" in k_account.id:
                inconsistencies.append("Deterministic Violation: A liquid asset (Cash/Bank) is being mapped to a Non-Current node.")

        if inconsistencies:
            response.inconsistency_flag = True
            response.inconsistency_note = " | ".join(inconsistencies)
            response.confidence_score = min(response.confidence_score, 0.3) # Penality for inconsistency

