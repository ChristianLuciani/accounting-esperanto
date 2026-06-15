import logging
from typing import List, Dict, Any
from api.rest.models import AccountPayload, MappedAccount
from logic.knowledge_base import KnowledgeBase
from scripts.ai_router import router

logger = logging.getLogger(__name__)

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
                uuid = uuid.strip()
                # Deterministic Boundary Library: the proposed UUID must be a
                # member of the ontology graph. A non-member is by definition
                # a hallucination and is escalated, never posted.
                if self.kb.has_uuid(uuid):
                    return MappedAccount(
                        local_code=account.local_code,
                        kontablo_uuid=uuid,
                        confidence_score=0.8,
                        agent_justification=justification.strip()
                    )
                return self._escalate(
                    account,
                    f"AI proposed UUID '{uuid}' is not in the ontology; "
                    "rejected by the deterministic boundary check."
                )
            return self._escalate(
                account, "AI response did not follow the UUID | justification format."
            )
        except Exception as e:
            logger.warning("Semantic match failed for %s: %s", account.local_code, e)
            return self._escalate(account, f"AI matching unavailable ({type(e).__name__}).")

    def _escalate(self, account: AccountPayload, reason: str) -> MappedAccount:
        """Escalation path: no UUID is fabricated; the entry routes to human
        review (Co-responsibility Architecture)."""
        return MappedAccount(
            local_code=account.local_code,
            kontablo_uuid="00000000-0000-0000-0000-000000000000",
            confidence_score=0.1,
            agent_justification=f"Escalated to human review: {reason}"
        )
