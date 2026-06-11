from typing import List, Optional
from api.rest.models import AccountPayload, MappedAccount

class TaxComplianceAgent:
    """
    Overwrites mappings for complex tax cases and jurisdiction-specific rules.

    Overrides key on deterministic input fields (jurisdiction + the source
    account's local name/code), never on LLM free-text output, per
    architectural principle #5 (determinism over stochasticity).
    """

    def process(
        self,
        mapped_accounts: List[MappedAccount],
        country: str,
        source_accounts: Optional[List[AccountPayload]] = None,
    ) -> List[MappedAccount]:
        """
        Applies compliance overrides. `source_accounts` must be the same batch,
        in the same order, that produced `mapped_accounts`.
        """
        sources = source_accounts or []
        overridden = []
        for i, acc in enumerate(mapped_accounts):
            local_name = sources[i].local_name.upper() if i < len(sources) else ""

            # Brazil: PIS/COFINS cascading-tax accounts get a dedicated UUID
            if country == "BR" and ("COFINS" in local_name or "PIS" in local_name):
                acc.kontablo_uuid = "30000000-0000-4000-8000-000000000001"
                acc.confidence_score = max(acc.confidence_score, 0.9)
                acc.agent_justification += " (Tax Compliance override for Brazil SPED: PIS/COFINS rule)"

            # Venezuela: IAS 29 / NIC-29 hyperinflation adjustment accounts
            if country == "VE" and any(
                x in local_name for x in ["REMA", "AJUSTE POR INFLACIÓN", "AJUSTE POR INFLACION"]
            ):
                acc.kontablo_uuid = "50000000-0000-4000-8000-000000000001"
                acc.confidence_score = max(acc.confidence_score, 0.9)
                acc.agent_justification += " (Tax Compliance: NIC-29 hyperinflation adjustment enforced)"

            overridden.append(acc)
        return overridden
