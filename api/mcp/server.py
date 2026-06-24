"""Kontablo MCP server — deterministic accounting tools for agents.

This makes the **MCP** claim in CLAUDE.md (architectural principle #4) and the
README *real* for Kontablo's deterministic core, rather than aspirational. It is
intentionally a thin adapter over the same engine that backs the REST API and
the gRPC server (``api/grpc/server.py``) — there is one mapping/consolidation
brain (``core.harness`` + ``core.engine``), exposed over multiple
machine-consumable faces (REST = the body, gRPC + MCP = additional faces). Every
tool below is deterministic: a graph lookup, a keyword rule, or arithmetic. No
tool calls an LLM (principle #5: determinism over stochasticity).

Tools (each mirrors a deterministic gRPC RPC over the same engine):
  resolve_account          ↔ MappingService.MapAccount      (Tier-1/Tier-2)
  get_account              ↔ AccountService.GetAccount       (by id or UUID)
  validate_balance_sheet   ↔ ValidationService.ValidateBalanceSheet
  consolidate_trial_balances ↔ ConsolidationService.ConsolidateTrialBalances
  list_jurisdictions       ↔ (coverage manifest; mirrors AccountService scope)

Deliberately NOT exposed in v1 (consistent with how gRPC returns UNIMPLEMENTED
for stochastic RPCs): the Tier-3 semantic/LLM fallback. Exposing it as if it
were deterministic would hide stochasticity and misrepresent the confidence of a
mapping. It is documented as planned in ``api/mcp/README.md``; if added later it
must return the boundary-library verdict + confidence, never a bare guess.

Run (stdio transport, the default MCP transport for local agents):
    python -m api.mcp.server
"""

from __future__ import annotations

import os
import sys
from typing import List, Optional

import yaml
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp.server.fastmcp import FastMCP  # noqa: E402

from core.engine import (  # noqa: E402
    ConsolidationEngine,
    IntercompanyLink,
    LocalEntry,
    SubsidiaryTB,
)
from core.harness import cra_validate  # noqa: E402
from core.harness.fx_provider import get_fx_provider  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COVERAGE_PATH = os.path.join(ROOT, "core/schemas/jurisdiction_coverage.yaml")

# Tier (harness vocabulary) -> match method label (mirrors the gRPC MatchMethod
# enum semantics in api/grpc/kontablo.proto, surfaced as a stable string here).
_TIER_TO_MATCH = {
    "tier1_exact": "exact_lookup",
    "tier2_keyword": "keyword_rule",
    "escalated": "not_found",
}


# ---------------------------------------------------------------------------
# Engine construction (one shared deterministic brain)
# ---------------------------------------------------------------------------
def build_engine() -> ConsolidationEngine:
    """Construct the shared consolidation engine, wired exactly like the gRPC
    server: env-gated FX (live rates in production via ``KONTABLO_FX_MODE``,
    pinned static fallback offline / in the hermetic test session)."""
    return ConsolidationEngine(fx_provider=get_fx_provider())


# ---------------------------------------------------------------------------
# Tool input models (give agents a rich JSON schema for each tool)
# ---------------------------------------------------------------------------
class TBEntryIn(BaseModel):
    """One trial-balance row."""

    local_code: str = Field("", description="Local statutory account code, e.g. '572'.")
    local_name: str = Field("", description="Local account name, e.g. 'Bancos'.")
    debit: float = Field(0.0, description="Debit amount in the subsidiary's local currency.")
    credit: float = Field(0.0, description="Credit amount in the subsidiary's local currency.")


class SubsidiaryIn(BaseModel):
    """A subsidiary's trial balance in its local currency."""

    subsidiary_id: str = Field(..., description="Stable subsidiary identifier.")
    jurisdiction: str = Field(..., description="ISO 3166-1 alpha-2 code (e.g. 'mx').")
    currency: str = Field(..., description="ISO 4217 currency of the trial balance (e.g. 'MXN').")
    entries: List[TBEntryIn] = Field(default_factory=list)
    fx_rate_to_usd: Optional[float] = Field(
        None,
        description="Optional manual USD-per-unit override (audited as a 'manual' "
        "FX quote for asynchronous/contract-rate transactions).",
    )
    fx_rate_as_of: Optional[str] = Field(None, description="Effective date of the manual rate.")
    fx_rate_note: Optional[str] = Field(None, description="Rationale for the manual rate.")


class EliminationIn(BaseModel):
    """An explicit intercompany pair to eliminate (deterministic, structured —
    never inferred from free text, per principle #5)."""

    from_subsidiary: str
    from_kontablo_id: str
    to_subsidiary: str
    to_kontablo_id: str
    amount_usd: float


# ---------------------------------------------------------------------------
# Tool implementations (pure functions over the engine; unit-testable offline)
# ---------------------------------------------------------------------------
def resolve_account_impl(
    engine: ConsolidationEngine,
    jurisdiction: str,
    local_code: str = "",
    local_name: str = "",
    nature: Optional[str] = None,
) -> dict:
    entry = LocalEntry(code=local_code, name=local_name, nature=nature)
    kid, tier, conf = engine.resolve(entry, jurisdiction)
    if kid is None:
        return {
            "jurisdiction": jurisdiction,
            "local_code": local_code,
            "local_name": local_name,
            "resolved": False,
            "kontablo_id": None,
            "kontablo_uuid": None,
            "label_en": None,
            "tier": tier,
            "match_method": _TIER_TO_MATCH.get(tier, "not_found"),
            "confidence": conf,
            "cra_flags": [],
            "note": "No deterministic mapping (Tier-1/Tier-2); escalate to human "
            "review (Co-responsibility Architecture). Tier-3 LLM fallback is not "
            "exposed over MCP.",
        }
    node = engine.accounts[kid]
    flags = cra_validate(
        {"code": local_code, "name": local_name, "nature": nature}, kid, engine.accounts
    )
    return {
        "jurisdiction": jurisdiction,
        "local_code": local_code,
        "local_name": local_name,
        "resolved": True,
        "kontablo_id": kid,
        "kontablo_uuid": str(node.get("uuid") or ""),
        "label_en": node["label"],
        "nature": node["nature"],
        "statement": node["statement"],
        "tier": tier,
        "match_method": _TIER_TO_MATCH.get(tier, "exact_lookup"),
        "confidence": conf,
        "cra_flags": flags,
        "note": f"Resolved deterministically via {tier}.",
    }


def get_account_impl(
    engine: ConsolidationEngine,
    account_id: Optional[str] = None,
    uuid: Optional[str] = None,
) -> dict:
    if not account_id and not uuid:
        return {"found": False, "error": "provide either account_id or uuid"}
    kid = account_id
    if kid is None:
        # Look up the kontablo_id whose node carries this UUID.
        target = str(uuid)
        kid = next((k for k, a in engine.accounts.items() if str(a.get("uuid")) == target), None)
    node = engine.accounts.get(kid) if kid else None
    if node is None:
        ref = account_id or uuid
        return {"found": False, "error": f"account {ref!r} not found"}
    return {
        "found": True,
        "kontablo_id": kid,
        "kontablo_uuid": str(node.get("uuid") or ""),
        "label_en": node["label"],
        "nature": node["nature"],
        "statement": node["statement"],
        "local_codes": node.get("local_codes", {}),
    }


def validate_balance_sheet_impl(entries: List[TBEntryIn]) -> dict:
    debits = round(sum(e.debit for e in entries), 2)
    credits = round(sum(e.credit for e in entries), 2)
    diff = round(debits - credits, 2)
    errors = []
    if abs(diff) > 0.01:
        errors.append(
            {
                "code": "UNBALANCED",
                "severity": "error",
                "message": f"Trial balance does not balance: Σdebits−Σcredits={diff}",
            }
        )
    return {
        "is_valid": not errors,
        "total_debits": debits,
        "total_credits": credits,
        "balance_difference": diff,
        "errors": errors,
    }


def consolidate_trial_balances_impl(
    engine: ConsolidationEngine,
    subsidiaries: List[SubsidiaryIn],
    eliminations: Optional[List[EliminationIn]] = None,
    target_currency: str = "USD",
    parent_company_id: str = "",
) -> dict:
    subs = [
        SubsidiaryTB(
            subsidiary_id=s.subsidiary_id,
            jurisdiction=s.jurisdiction,
            currency=s.currency,
            entries=[
                LocalEntry(code=e.local_code, name=e.local_name, debit=e.debit, credit=e.credit)
                for e in s.entries
            ],
            fx_rate_to_usd=s.fx_rate_to_usd,
            fx_rate_as_of=s.fx_rate_as_of,
            fx_rate_note=s.fx_rate_note,
        )
        for s in subsidiaries
    ]
    links = [
        IntercompanyLink(
            from_subsidiary=el.from_subsidiary,
            from_kontablo_id=el.from_kontablo_id,
            to_subsidiary=el.to_subsidiary,
            to_kontablo_id=el.to_kontablo_id or el.from_kontablo_id,
            amount_usd=el.amount_usd,
        )
        for el in (eliminations or [])
    ]
    try:
        result = engine.consolidate(
            subs, eliminations=links, target_currency=target_currency or "USD"
        )
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}

    warnings = list(result.cra_flags)
    if not result.is_balanced():
        warnings.append(f"trial_balance_unbalanced:diff={result.balance_difference}")
    return {
        "ok": True,
        "parent_company_id": parent_company_id,
        "target_currency": result.target_currency,
        "trial_balance": [
            {
                "kontablo_id": l.kontablo_id,
                "label_en": l.label_en,
                "debit": l.debit_usd,
                "credit": l.credit_usd,
                "net": l.net_usd,
            }
            for l in result.lines
        ],
        "eliminations_applied": result.eliminations_applied,
        "balanced": result.is_balanced(),
        "balance_difference": result.balance_difference,
        "escalations": [
            {
                "subsidiary_id": r.subsidiary_id,
                "local_code": r.local_code,
                "local_name": r.local_name,
            }
            for r in result.escalations
        ],
        "fx_audit": [
            {
                "subsidiary_id": sid,
                "currency": q.currency,
                "usd_per_unit": q.usd_per_unit,
                "source": q.source,
                "mode": q.mode,
                "as_of": q.as_of,
                "note": q.note,
            }
            for sid, q in result.fx_quotes.items()
        ],
        "warnings": warnings,
    }


_COVERAGE_CACHE: Optional[dict] = None


def _load_coverage() -> dict:
    global _COVERAGE_CACHE
    if _COVERAGE_CACHE is None:
        with open(COVERAGE_PATH, encoding="utf-8") as f:
            _COVERAGE_CACHE = yaml.safe_load(f)
    return _COVERAGE_CACHE


def list_jurisdictions_impl(
    region: Optional[str] = None,
    mapping_mode: Optional[str] = None,
    tier1_only: bool = False,
) -> dict:
    doc = _load_coverage()
    jurisdictions = doc.get("jurisdictions", [])
    summary = {
        "total": len(jurisdictions),
        "statutory_chart": sum(1 for j in jurisdictions if j.get("mapping_mode") == "statutory_chart"),
        "ifrs_direct": sum(1 for j in jurisdictions if j.get("mapping_mode") == "ifrs_direct"),
        "tier1_codes_available": sum(1 for j in jurisdictions if j.get("tier1_codes_available")),
    }
    filtered = jurisdictions
    if region:
        filtered = [j for j in filtered if (j.get("region") or "").lower() == region.lower()]
    if mapping_mode:
        filtered = [j for j in filtered if j.get("mapping_mode") == mapping_mode]
    if tier1_only:
        filtered = [j for j in filtered if j.get("tier1_codes_available")]
    return {
        "metadata": doc.get("metadata", {}),
        "summary": summary,
        "count_returned": len(filtered),
        "jurisdictions": filtered,
    }


# ---------------------------------------------------------------------------
# FastMCP server: register the deterministic tools
# ---------------------------------------------------------------------------
def build_mcp(engine: Optional[ConsolidationEngine] = None) -> FastMCP:
    """Build a FastMCP server with all deterministic Kontablo tools registered.

    The engine is constructed once and shared by every tool, mirroring how the
    gRPC servicers share a single ``ConsolidationEngine``.
    """
    engine = engine or build_engine()
    server = FastMCP(
        "kontablo",
        instructions=(
            "Kontablo deterministic accounting tools. Resolve local statutory "
            "accounts to universal UUIDs, query the ontology, validate trial "
            "balances, consolidate subsidiaries with intercompany elimination, "
            "and list jurisdiction coverage. All tools are deterministic (graph "
            "lookup / rule / arithmetic); none call an LLM. Unresolved mappings "
            "escalate to human review rather than guessing."
        ),
    )

    @server.tool(
        description="Resolve a local statutory account (jurisdiction + local "
        "code and/or name) to a universal Kontablo node UUID via the deterministic "
        "three-tier resolver (Tier-1 exact code lookup, Tier-2 multilingual "
        "keyword rules). Returns the kontablo_id, UUID, tier, confidence, and any "
        "Co-responsibility boundary flags. Returns resolved=false (no guess) when "
        "neither deterministic tier matches."
    )
    def resolve_account(
        jurisdiction: str, local_code: str = "", local_name: str = "", nature: Optional[str] = None
    ) -> dict:
        return resolve_account_impl(engine, jurisdiction, local_code, local_name, nature)

    @server.tool(
        description="Look up a Kontablo ontology node by its kontablo_id (e.g. "
        "'asset.current.cash') or by its UUID. Returns label, nature, statement, "
        "and the jurisdiction local-code overlay."
    )
    def get_account(account_id: Optional[str] = None, uuid: Optional[str] = None) -> dict:
        return get_account_impl(engine, account_id, uuid)

    @server.tool(
        description="Validate the double-entry identity of a trial balance: checks "
        "Σdebits − Σcredits == 0 deterministically. Returns is_valid, the totals, "
        "the balance difference, and any errors."
    )
    def validate_balance_sheet(entries: List[TBEntryIn]) -> dict:
        return validate_balance_sheet_impl(entries)

    @server.tool(
        description="Consolidate subsidiary trial balances into a single USD trial "
        "balance, applying explicit (structured) intercompany eliminations. Each "
        "subsidiary is resolved deterministically and normalised to USD with an "
        "auditable per-entity FX quote. Returns the consolidated lines, "
        "eliminations applied, balance check, escalations, FX audit, and warnings."
    )
    def consolidate_trial_balances(
        subsidiaries: List[SubsidiaryIn],
        eliminations: Optional[List[EliminationIn]] = None,
        target_currency: str = "USD",
        parent_company_id: str = "",
    ) -> dict:
        return consolidate_trial_balances_impl(
            engine, subsidiaries, eliminations, target_currency, parent_company_id
        )

    @server.tool(
        description="List Kontablo jurisdiction coverage from the 195-jurisdiction "
        "manifest. Optional filters: region, mapping_mode ('statutory_chart' | "
        "'ifrs_direct'), tier1_only (only jurisdictions with verified Tier-1 "
        "codes). Returns a summary (total / statutory_chart / ifrs_direct / "
        "tier1_codes_available) and the filtered jurisdiction list."
    )
    def list_jurisdictions(
        region: Optional[str] = None,
        mapping_mode: Optional[str] = None,
        tier1_only: bool = False,
    ) -> dict:
        return list_jurisdictions_impl(region, mapping_mode, tier1_only)

    return server


# Module-level server for `python -m api.mcp.server` and `mcp` CLI discovery.
mcp = build_mcp()


def main() -> None:
    """Run the MCP server over stdio (the standard local-agent transport)."""
    mcp.run()


if __name__ == "__main__":
    main()
