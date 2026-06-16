"""
Minimal Kontablo gRPC server — deterministic RPCs only.

This makes the gRPC interface described in ``api/grpc/kontablo.proto`` *real*
for its deterministic core, rather than aspirational. It is intentionally a thin
adapter over the same engine that backs the REST API and the reconciliation
examples — there is one mapping/consolidation brain, exposed over two transports
(REST = the body, gRPC = a second machine-consumable face), per CLAUDE.md
architectural principle #4.

Implemented (deterministic — graph lookups + rules + arithmetic):
  AccountService.ListAccounts / GetAccount / GetLocalCodes
  MappingService.MapAccount / MapBatch (streaming) / ValidateChart
  ConsolidationService.ConsolidateTrialBalances  (with intercompany elimination)
  ValidationService.ValidateBalanceSheet

Deliberately NOT implemented here (return UNIMPLEMENTED, honestly):
  ClassificationService.*   — depends on stochastic LLM inference; exposing a
                              fake deterministic version would misrepresent it.
  ConsolidationService.GenerateFinancialStatements,
  ValidationService.ValidateCompleteness,
  SynonymService.*          — planned; no committed deterministic backing yet.

Run:  python -m api.grpc.server   (serves on 0.0.0.0:50051)
"""

from __future__ import annotations

import os
import sys
from concurrent import futures

import grpc

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api.grpc.gen import kontablo_pb2 as pb  # noqa: E402
from api.grpc.gen import kontablo_pb2_grpc as pb_grpc  # noqa: E402
from api.src.services.ontology import OntologyService  # noqa: E402
from core.harness.fx_provider import get_fx_provider  # noqa: E402
from core.engine import (  # noqa: E402
    ConsolidationEngine,
    IntercompanyLink,
    LocalEntry,
    SubsidiaryTB,
)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ONTOLOGY_PATH = os.path.join(ROOT, "core/schemas/level3_accounts.yaml")

_NATURE_TO_PB = {"debit": pb.NATURE_DEBIT, "credit": pb.NATURE_CREDIT}
_PB_TO_NATURE = {pb.NATURE_DEBIT: "debit", pb.NATURE_CREDIT: "credit"}
_STATEMENT_TO_PB = {
    "balance_sheet": pb.STATEMENT_BALANCE_SHEET,
    "income_statement": pb.STATEMENT_INCOME_STATEMENT,
    "cash_flow": pb.STATEMENT_CASH_FLOW,
}
_TIER_TO_MATCH = {
    "tier1_exact": pb.MATCH_EXACT_LOOKUP,
    "tier2_keyword": pb.MATCH_SEMANTIC_AI,  # closest proto enum for keyword rule
    "escalated": pb.MATCH_NOT_FOUND,
}


def _unimplemented(context, msg):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details(msg)
    return None


class AccountServicer(pb_grpc.AccountServiceServicer):
    def __init__(self, ontology: OntologyService):
        self.ontology = ontology

    def _to_pb(self, a) -> pb.KontabloAccount:
        return pb.KontabloAccount(
            id=a.id,
            uuid=str(a.uuid),
            label_en=a.label_en,
            label_es=a.label_es or "",
            ifrs_tag=a.ifrs_tag,
            nature=_NATURE_TO_PB.get(a.nature.value, pb.NATURE_UNSPECIFIED),
            statement=_STATEMENT_TO_PB.get(a.statement.value, pb.STATEMENT_UNSPECIFIED),
            level=a.level,
            parent=a.parent or "",
            is_aggregate=a.is_aggregate,
            optional=a.optional,
        )

    def ListAccounts(self, request, context):
        level = request.level or None
        nature = _PB_TO_NATURE.get(request.nature)
        statement = next((k for k, v in _STATEMENT_TO_PB.items() if v == request.statement), None)
        accounts = self.ontology.list_accounts(level=level, nature=nature, statement=statement)
        pb_accounts = [self._to_pb(a) for a in accounts]
        return pb.ListAccountsResponse(accounts=pb_accounts, total=len(pb_accounts))

    def GetAccount(self, request, context):
        a = self.ontology.get_account(request.account_id)
        if not a:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Account {request.account_id} not found")
            return pb.KontabloAccount()
        return self._to_pb(a)

    def GetLocalCodes(self, request, context):
        a = self.ontology.get_account(request.account_id)
        if not a:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Account {request.account_id} not found")
            return pb.LocalCodesResponse(account_id=request.account_id)
        codes = []
        for jur, code in (a.local_codes or {}).items():
            if request.jurisdiction and jur.lower() != request.jurisdiction.lower():
                continue
            codes.append(pb.LocalCode(jurisdiction=jur, code=str(code), label=a.label_en))
        return pb.LocalCodesResponse(account_id=request.account_id, codes=codes)


class MappingServicer(pb_grpc.MappingServiceServicer):
    def __init__(self, engine: ConsolidationEngine, ontology: OntologyService):
        self.engine = engine
        self.ontology = ontology

    def _map_one(self, req) -> pb.MapAccountResponse:
        entry = LocalEntry(
            code=req.local_code,
            name=req.local_name,
            nature=_PB_TO_NATURE.get(req.nature),
        )
        kid, tier, conf = self.engine.resolve(entry, req.jurisdiction)
        if kid is None:
            return pb.MapAccountResponse(
                local_code=req.local_code,
                kontablo_id="unknown",
                kontablo_uuid="",
                label_en="Unmapped Account",
                confidence_score=0.0,
                match_method=pb.MATCH_NOT_FOUND,
                justification="No deterministic mapping (Tier-1/Tier-2); escalate to human review.",
            )
        node = self.engine.accounts[kid]
        return pb.MapAccountResponse(
            local_code=req.local_code,
            kontablo_id=kid,
            kontablo_uuid=str(node.get("uuid") or ""),
            label_en=node["label"],
            confidence_score=conf,
            match_method=_TIER_TO_MATCH.get(tier, pb.MATCH_UNSPECIFIED),
            justification=f"Resolved via {tier}.",
        )

    def MapAccount(self, request, context):
        return self._map_one(request)

    def MapBatch(self, request_iterator, context):
        for req in request_iterator:
            yield self._map_one(req)

    def ValidateChart(self, request, context):
        mapped, unmapped = [], []
        for acc in request.accounts:
            res = self._map_one(acc)
            if res.match_method == pb.MATCH_NOT_FOUND:
                unmapped.append(acc)
            else:
                mapped.append(res)
        total = len(request.accounts)
        coverage = (len(mapped) / total) if total else 0.0
        return pb.ValidateChartResponse(
            coverage_pct=coverage,
            mapped=mapped,
            unmapped=unmapped,
        )


class ConsolidationServicer(pb_grpc.ConsolidationServiceServicer):
    def __init__(self, engine: ConsolidationEngine):
        self.engine = engine

    def ConsolidateTrialBalances(self, request, context):
        subs = []
        for s in request.subsidiaries:
            entries = [
                LocalEntry(
                    code=e.local_code,
                    name=e.local_name,
                    debit=e.debit,
                    credit=e.credit,
                )
                for e in s.entries
            ]
            subs.append(
                SubsidiaryTB(
                    subsidiary_id=s.subsidiary_id,
                    jurisdiction=s.jurisdiction,
                    currency=s.currency,
                    entries=entries,
                    fx_rate_to_usd=s.fx_rate_to_target or None,
                )
            )
        links = [
            IntercompanyLink(
                from_subsidiary=el.from_subsidiary,
                from_kontablo_id=el.kontablo_id,
                to_subsidiary=el.to_subsidiary,
                # Empty contra leg = single-node elimination (same node both sides).
                to_kontablo_id=el.contra_kontablo_id or el.kontablo_id,
                amount_usd=el.amount,
            )
            for el in request.eliminations
        ]
        try:
            result = self.engine.consolidate(
                subs, eliminations=links,
                target_currency=request.target_currency or "USD",
            )
        except ValueError as e:
            # Unsupported target currency / unknown FX: caller error, not crash.
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        tb = [
            pb.ConsolidatedEntry(
                kontablo_id=l.kontablo_id,
                label_en=l.label_en,
                debit=l.debit_usd,
                credit=l.credit_usd,
                net=l.net_usd,
            )
            for l in result.lines
        ]
        warnings = list(result.cra_flags)
        if not result.is_balanced():
            warnings.append(f"trial_balance_unbalanced:diff={result.balance_difference}")
        return pb.ConsolidationResponse(
            parent_company_id=request.parent_company_id,
            target_currency=result.target_currency,
            reporting_date=request.reporting_date,
            trial_balance=tb,
            eliminations_applied=result.eliminations_applied,
            warnings=warnings,
        )

    def GenerateFinancialStatements(self, request, context):
        _unimplemented(
            context,
            "GenerateFinancialStatements is a planned RPC; not yet implemented.",
        )
        return pb.FinancialStatementsResponse()


class ValidationServicer(pb_grpc.ValidationServiceServicer):
    def __init__(self, engine: ConsolidationEngine):
        self.engine = engine

    def ValidateBalanceSheet(self, request, context):
        # Resolve entries, then check Σdebits − Σcredits == 0 deterministically.
        debits = sum(e.debit for e in request.entries)
        credits = sum(e.credit for e in request.entries)
        diff = round(debits - credits, 2)
        errors = []
        if abs(diff) > 0.01:
            errors.append(
                pb.ValidationError(
                    code="UNBALANCED",
                    message=f"Trial balance does not balance: Σdebits−Σcredits={diff}",
                    severity=pb.SEVERITY_ERROR,
                )
            )
        return pb.ValidationResponse(
            is_valid=not errors,
            errors=errors,
            balance_difference=diff,
        )

    def ValidateCompleteness(self, request, context):
        _unimplemented(context, "ValidateCompleteness is a planned RPC; not yet implemented.")
        return pb.ValidationResponse()


def build_server(address: str = "[::]:50051", max_workers: int = 4) -> grpc.Server:
    """Construct (but do not start) a gRPC server with all servicers wired."""
    ontology = OntologyService(ONTOLOGY_PATH)
    # Env-gated FX: live runtime rates by default (KONTABLO_FX_MODE), pinned
    # static fallback offline / in tests. See core.harness.fx_provider.
    engine = ConsolidationEngine(fx_provider=get_fx_provider())
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    pb_grpc.add_AccountServiceServicer_to_server(AccountServicer(ontology), server)
    pb_grpc.add_MappingServiceServicer_to_server(MappingServicer(engine, ontology), server)
    pb_grpc.add_ConsolidationServiceServicer_to_server(ConsolidationServicer(engine), server)
    pb_grpc.add_ValidationServiceServicer_to_server(ValidationServicer(engine), server)
    server.add_insecure_port(address)
    return server


def serve(address: str = "[::]:50051") -> None:
    server = build_server(address)
    server.start()
    print(f"Kontablo gRPC server listening on {address}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
