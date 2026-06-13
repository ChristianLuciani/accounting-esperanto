import os
from typing import List, Optional
import json
from ..models.kontablo import SingleMappingRequest, SingleMappingResponse

class AIService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            # Lazy import: the deterministic tiers (and the whole API when no
            # key is configured) must not require the genai package at all.
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    async def get_semantic_mapping(self, request: SingleMappingRequest, ontology_summary: str) -> Optional[dict]:
        if not self.model:
            return None
        
        prompt = f"""
        You are a senior expert accountant specializing in IFRS and global localizations.
        Map the following local account to the most appropriate Kontablo Universal ID.
        
        Local Account:
        Code: {request.local_code}
        Name: {request.local_name}
        Jurisdiction: {request.jurisdiction}
        Nature: {request.nature}
        
        Available Kontablo Ontology (summarized):
        {ontology_summary}
        
        Return ONLY a JSON object with:
        - kontablo_id: The mapped ID
        - confidence_score: 0.0 to 1.0
        - justification: Brief reason for this mapping
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Find JSON in response
            text = response.text
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != -1:
                return json.loads(text[start:end])
        except Exception as e:
            print(f"AI Mapping Error: {e}")
        
        return None

    async def classify_transaction(self, narration: str, jurisdiction: str, ontology_summary: str) -> Optional[dict]:
        if not self.model:
            return None
            
        prompt = f"""
        Classify this transaction narration into the appropriate Kontablo accounts (Debit and Credit).
        Narration: "{narration}"
        Jurisdiction: {jurisdiction}
        
        Available Kontablo Ontology:
        {ontology_summary}
        
        Return ONLY a JSON object with:
        - debit_account_id: Kontablo ID for the debit
        - credit_account_id: Kontablo ID for the credit
        - confidence_score: 0.0 to 1.0
        - justification: Brief reasoning
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != -1:
                return json.loads(text[start:end])
        except Exception as e:
            print(f"AI Classification Error: {e}")
            
        return None
