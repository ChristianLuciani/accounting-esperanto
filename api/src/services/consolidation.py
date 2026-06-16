from typing import List, Dict, Optional
from ..models.kontablo import TrialBalance, TrialBalanceEntry, SingleMappingRequest
from .mapping import MappingService
from .ontology import OntologyService
from core.harness.fx_provider import FXProvider, get_fx_provider

class ConsolidationService:
    def __init__(
        self,
        mapping_service: MappingService,
        ontology_service: OntologyService,
        fx_provider: Optional[FXProvider] = None,
    ):
        self.mapping_service = mapping_service
        self.ontology_service = ontology_service
        # Runtime FX: env-gated chain (ECB/Frankfurter -> open.er-api -> pinned
        # static fallback). Default resolves at runtime so the consolidated
        # statement prices balances at current rates instead of frozen demo
        # numbers; the test session forces static mode (see conftest.py).
        self.fx_provider = fx_provider or get_fx_provider()

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
                # Priority: 1. Manual override (tb.exchange_rate), 2. live FX
                # provider (cross rate via USD pivot). No silent 1.0 fallback:
                # an unpriceable pair would consolidate mislabeled amounts, so
                # it is an explicit caller error.
                src_ccy = tb.currency.upper()
                tgt_ccy = target_currency.upper()
                if tb.exchange_rate is not None:
                    fx_rate = tb.exchange_rate
                elif src_ccy == tgt_ccy:
                    fx_rate = 1.0
                else:
                    src_usd = self.fx_provider.usd_per_unit(src_ccy)
                    tgt_usd = self.fx_provider.usd_per_unit(tgt_ccy)
                    if src_usd is None or tgt_usd is None:
                        raise ValueError(
                            f"No FX rate for {src_ccy}->{tgt_ccy} "
                            f"(trial balance {tb.jurisdiction}); the FX provider "
                            "could not price it. Pass exchange_rate explicitly."
                        )
                    fx_rate = src_usd / tgt_usd

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
