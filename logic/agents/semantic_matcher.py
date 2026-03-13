from typing import List, Dict, Any
from api.rest.models import AccountPayload, MappedAccount
from logic.knowledge_base import KnowledgeBase
from scripts.ai_router import router

class SemanticMatcherAgent:
    """
    Finds the best Kontablo UUID for a given local account.
    """
    
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb

    def match_batch(self, accounts: List[AccountPayload], context: Dict[str, Any]) -> List[MappedAccount]:
        """
        Processes a batch of accounts.
        """
        results = []
        country = context.get("country", "UNKNOWN")
        
        for acc in accounts:
            # 1. Try Knowledge Base (Exact Code Match)
            kb_match = self.kb.get_mapping(country, acc.local_code)
            if kb_match:
                results.append(MappedAccount(
                    local_code=acc.local_code,
                    kontablo_uuid=kb_match["kontablo_uuid"],
                    confidence_score=1.0,
                    agent_justification=f"Exact code match in {country} standard: {kb_match['name']}"
                ))
                continue
            
            # 2. If no exact match, try Semantic Match with AI
            results.append(self._semantic_match(acc, country))
            
        return results

    def _semantic_match(self, account: AccountPayload, country: str) -> MappedAccount:
        """
        Uses LLM to find the best match based on names.
        """
        prompt = f"""
        Map this local accounting account to the nearest Kontablo UUID.
        
        Account:
        Code: {account.local_code}
        Name: {account.local_name}
        Country Context: {country}
        
        Kontablo uses these standard Level 1 UUIDs:
        - 00000000-0000-4000-8000-000000000101 (Cash)
        - 00000000-0000-4000-8000-000000000102 (Banks)
        - 00000000-0000-4000-8000-000000000104 (Trade Receivables)
        - 00000000-0000-4000-8000-000000000201 (Trade Payables)
        - 00000000-0000-4000-8000-000000000203 (Current Tax Liabilities)
        - 00000000-0000-4000-8000-000000000301 (Revenue)
        
        Provide the UUID and a short justification.
        Format: UUID | Justification
        """
        
        try:
            response = router.complete(prompt, task_type="research", priority="speed")
            content = response["content"].strip()
            
            if "|" in content:
                uuid, justification = content.split("|", 1)
                return MappedAccount(
                    local_code=account.local_code,
                    kontablo_uuid=uuid.strip(),
                    confidence_score=0.8,
                    agent_justification=justification.strip()
                )
        except Exception as e:
            pass

        return MappedAccount(
            local_code=account.local_code,
            kontablo_uuid="00000000-0000-0000-0000-000000000000",
            confidence_score=0.1,
            agent_justification="Fallback: AI matching failed."
        )
