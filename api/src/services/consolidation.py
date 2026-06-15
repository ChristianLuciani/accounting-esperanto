from typing import List, Dict
from ..models.kontablo import TrialBalance, TrialBalanceEntry, SingleMappingRequest
from .mapping import MappingService
from .ontology import OntologyService

class ConsolidationService:
    def __init__(self, mapping_service: MappingService, ontology_service: OntologyService):
        self.mapping_service = mapping_service
        self.ontology_service = ontology_service

    async def consolidate(self, trial_balances: List[TrialBalance], target_currency: str) -> Dict:
        """
        Consolidates multiple trial balances into a single Kontablo-standardized trial balance.
        """
        consolidated_data = {} # Map k_id -> {debit, credit}
        
        for tb in trial_balances:
            for entry in tb.entries:
                # 1. Map local code to Kontablo ID
                mapping_req = SingleMappingRequest(
                    local_code=entry.local_code,
                    local_name=entry.local_name or "",
                    jurisdiction=tb.jurisdiction
                )
                mapping_res = await self.mapping_service.map_account(mapping_req)
                
                k_id = mapping_res.kontablo_id
                
                # 2. Currency Conversion
                # Priority: 1. Manual override (tb.exchange_rate), 2. Rate map.
                # No silent 1.0 fallback: an unknown pair would consolidate
                # mislabeled amounts, so it is an explicit caller error.
                rate_map = {
                    ("VES", "USD"): 0.027, # Hyper-extreme case: 36.5 official vs market
                    ("EUR", "USD"): 1.08,
                    ("BRL", "USD"): 0.20,
                    ("MXN", "USD"): 0.058
                }

                fx_key = (tb.currency.upper(), target_currency.upper())
                fx_rate = tb.exchange_rate or rate_map.get(fx_key)
                if fx_rate is None:
                    if fx_key[0] == fx_key[1]:
                        fx_rate = 1.0
                    else:
                        raise ValueError(
                            f"No FX rate for {fx_key[0]}->{fx_key[1]} "
                            f"(trial balance {tb.jurisdiction}); pass "
                            "exchange_rate explicitly."
                        )
                
                debit_val = entry.debit * fx_rate
                credit_val = entry.credit * fx_rate
                
                if k_id not in consolidated_data:
                    consolidated_data[k_id] = {"debit": 0.0, "credit": 0.0}
                
                consolidated_data[k_id]["debit"] += debit_val
                consolidated_data[k_id]["credit"] += credit_val
        
        # 3. Format result
        formatted_results = []
        for k_id, values in consolidated_data.items():
            account_info = self.ontology_service.get_account(k_id)
            formatted_results.append({
                "kontablo_id": k_id,
                "label_en": account_info.label_en if account_info else "Unknown",
                "debit": round(values["debit"], 2),
                "credit": round(values["credit"], 2),
                "net_balance": round(values["debit"] - values["credit"], 2)
            })
            
        return {
            "target_currency": target_currency,
            "entities_consolidated": len(trial_balances),
            "results": formatted_results
        }
