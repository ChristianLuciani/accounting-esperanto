from typing import List
from api.rest.models import MappedAccount

class TaxComplianceAgent:
    """
    Overwrites mappings for complex tax cases and jurisdiction-specific rules.
    """
    
    def process(self, mapped_accounts: List[MappedAccount], country: str) -> List[MappedAccount]:
        """
        Applies compliance overrides.
        """
        overridden = []
        for acc in mapped_accounts:
            # Brazil Example: PIS/COFINS specific UUID
            if country == "BR" and "COFINS" in acc.agent_justification:
                acc.kontablo_uuid = "30000000-0000-4000-8000-000000000001"
                acc.agent_justification += " (Tax Compliance override for Brazil SPED)"
            
            # Venezuela Example: Hyperinflation adjustments
            if country == "VE" and any(x in acc.agent_justification for x in ["REMA", "Adjuste"]):
                acc.kontablo_uuid = "50000000-0000-4000-8000-000000000001" # Mock VE inflation UUID
                acc.agent_justification += " (Tax Compliance: NIC-29 hyperinflation adjustment enforced)"
            
            overridden.append(acc)
        return overridden
