import math
from typing import List, Dict, Optional, Tuple
from ..models.kontablo import TrialBalance, TrialBalanceEntry, SingleMappingRequest
from .mapping import MappingService
from .ontology import OntologyService
from core.harness.fx_provider import FXProvider, get_fx_provider, manual_quote, _utcnow_iso

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

    def _resolve_fx(self, tb: TrialBalance, target_currency: str) -> Tuple[float, Dict]:
        """Resolve the FX rate for one trial balance *and* an attachable audit
        record. Priority: (1) manual ``exchange_rate`` (recorded as a ``manual``
        rate with its as-of date and note); (2) the live provider, cross-rated
        via USD (source-attributed, dated); (3) identity for same-currency. No
        silent 1.0 fallback for a genuinely unpriceable pair."""
        src_ccy = tb.currency.upper()
        tgt_ccy = target_currency.upper()
        base = {
            "subsidiary_id": tb.subsidiary_id,
            "jurisdiction": tb.jurisdiction,
            "currency": src_ccy,
            "target_currency": tgt_ccy,
        }
        if tb.exchange_rate is not None:
            q = manual_quote(
                src_ccy, tb.exchange_rate,
                as_of=tb.exchange_rate_as_of, note=tb.exchange_rate_note,
            )
            return tb.exchange_rate, {
                **base, "rate_applied": tb.exchange_rate, "source": q.source,
                "mode": q.mode, "as_of": q.as_of, "retrieved_at": q.retrieved_at,
                "note": q.note,
            }
        if src_ccy == tgt_ccy:
            return 1.0, {
                **base, "rate_applied": 1.0, "source": "identity",
                "mode": "identity", "as_of": None, "retrieved_at": _utcnow_iso(),
                "note": "same currency; no conversion",
            }
        src_q = self.fx_provider.quote(src_ccy)
        tgt_q = self.fx_provider.quote(tgt_ccy)
        if src_q is None or tgt_q is None:
            raise ValueError(
                f"No FX rate for {src_ccy}->{tgt_ccy} "
                f"(trial balance {tb.jurisdiction}); the FX provider could not "
                "price it. Pass exchange_rate explicitly."
            )
        rate = src_q.usd_per_unit / tgt_q.usd_per_unit
        audit = {
            **base, "rate_applied": rate, "source": src_q.source,
            "mode": src_q.mode, "as_of": src_q.as_of,
            "retrieved_at": src_q.retrieved_at, "note": src_q.note,
            "usd_per_unit": src_q.usd_per_unit,
        }
        if tgt_ccy != "USD":
            # Cross rate via USD pivot: record the target leg's provenance too.
            audit["target_leg"] = {
                "source": tgt_q.source, "as_of": tgt_q.as_of,
                "usd_per_unit": tgt_q.usd_per_unit,
            }
        return rate, audit

    async def consolidate(self, trial_balances: List[TrialBalance], target_currency: str) -> Dict:
        """
        Consolidates multiple trial balances into a single Kontablo-standardized trial balance.
        """
        consolidated_data = {} # Map k_id -> {debit, credit}
        fx_audit: List[Dict] = []  # one FX provenance record per trial balance

        for tb in trial_balances:
            # FX is per trial balance, resolved once (with provenance).
            fx_rate, fx_record = self._resolve_fx(tb, target_currency)
            fx_audit.append(fx_record)

            for entry in tb.entries:
                # 1. Map local code to Kontablo ID
                mapping_req = SingleMappingRequest(
                    local_code=entry.local_code,
                    local_name=entry.local_name or "",
                    jurisdiction=tb.jurisdiction
                )
                mapping_res = await self.mapping_service.map_account(mapping_req)

                k_id = mapping_res.kontablo_id

                debit_val = entry.debit * fx_rate
                credit_val = entry.credit * fx_rate

                if k_id not in consolidated_data:
                    consolidated_data[k_id] = {"debit": 0.0, "credit": 0.0}

                consolidated_data[k_id]["debit"] += debit_val
                consolidated_data[k_id]["credit"] += credit_val

        # 3. Format result. Per-entry amounts are validated finite at the model
        # boundary, but a sum of finite values can still overflow to ±inf; refuse
        # to emit a non-finite figure (it would crash JSON serialization with a
        # 500) and surface it as a clean caller error instead.
        formatted_results = []
        total_debit = 0.0
        total_credit = 0.0
        for k_id, values in consolidated_data.items():
            account_info = self.ontology_service.get_account(k_id)
            debit = round(values["debit"], 2)
            credit = round(values["credit"], 2)
            if not (math.isfinite(debit) and math.isfinite(credit)):
                raise ValueError(
                    f"consolidated totals for {k_id} overflowed to a non-finite "
                    "value; input amounts are too large to sum safely."
                )
            total_debit += debit
            total_credit += credit
            formatted_results.append({
                "kontablo_id": k_id,
                "label_en": account_info.label_en if account_info else "Unknown",
                "debit": debit,
                "credit": credit,
                "net_balance": round(debit - credit, 2)
            })

        balance_difference = round(total_debit - total_credit, 2)
        return {
            "target_currency": target_currency,
            "entities_consolidated": len(trial_balances),
            "results": formatted_results,
            # Double-entry observability: does the consolidated trial balance
            # balance? (Parity with the gRPC and MCP consolidation surfaces.)
            "total_debit": round(total_debit, 2),
            "total_credit": round(total_credit, 2),
            "balance_difference": balance_difference,
            "balanced": abs(balance_difference) <= 0.05,
            "fx_audit": fx_audit,
        }
