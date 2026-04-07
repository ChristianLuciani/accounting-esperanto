import pandas as pd
import os
from typing import List, Optional
from ..models.kontablo import SingleMappingRequest, SingleMappingResponse
from uuid import UUID
from .ontology import OntologyService
from .ai import AIService

class MappingService:
    def __init__(self, standards_dir: str, ontology_service: OntologyService, ai_service: AIService):
        self.standards_dir = standards_dir
        self.ontology_service = ontology_service
        self.ai_service = ai_service
        self.cached_mappings = {}

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

    def load_mapping_df(self, jurisdiction: str) -> Optional[pd.DataFrame]:
        jurisdiction = jurisdiction.lower()
        if jurisdiction in self.cached_mappings:
            return self.cached_mappings[jurisdiction]
        
        path = self.get_standard_path(jurisdiction)
        if not path or not os.path.exists(path):
            return None
        
        try:
            # Handle different CSV formats (encoding, separators)
            # Mexican SAT sample uses CÓDIGO
            df = pd.read_csv(path, dtype={"CÓDIGO": str, "Code": str, "Code PCG": str})
            self.cached_mappings[jurisdiction] = df
            return df
        except Exception as e:
            print(f"Error loading mapping for {jurisdiction}: {e}")
            return None

    def _get_ontology_summary(self) -> str:
        # Create a compact summary for the LLM
        return "\n".join([f"- {a.id}: {a.label_en} ({a.nature})" for a in self.ontology_service.accounts])

    async def map_account(self, request: SingleMappingRequest) -> SingleMappingResponse:
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
        df = self.load_mapping_df(request.jurisdiction)
        if df is not None:
            code_cols = ["CÓDIGO", "Code", "Code PCG", "CONTA"]
            match = None
            for col in code_cols:
                if col in df.columns:
                    match = df[df[col].astype(str) == str(request.local_code)]
                    if not match.empty:
                        break
            
            if match is not None and not match.empty:
                # We assume the CSV match is high confidence, even without a linked Kontablo ID yet.
                # In reality, the CSV would map to a core ID.
                return SingleMappingResponse(
                    local_code=request.local_code,
                    kontablo_id="asset.current.receivables", # Placeholder
                    kontablo_uuid=UUID("00000000-0000-4000-8000-000000000104"),
                    label_en="Trade Receivables",
                    confidence_score=0.8,
                    match_method="fuzzy_string",
                    justification=f"Match found in {request.jurisdiction.upper()} CSV standard."
                )

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
            kontablo_uuid=UUID("00000000-0000-4000-0000-000000000000"),
            label_en="Unmapped Account",
            confidence_score=0.0,
            match_method="not_found",
            justification="No mapping found through lookup or AI fallback."
        )
