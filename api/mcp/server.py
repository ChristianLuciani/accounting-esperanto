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

import math
import os
import sys
from typing import Annotated, List, Optional

import yaml
from pydantic import BaseModel, Field, field_validator

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

_VALID_NATURES = ("debit", "credit")


def _require_finite(value: float, field: str) -> float:
    """Reject NaN / ±Infinity. A non-finite monetary amount silently defeats the
    double-entry check (``abs(nan) > tol`` is False, so a NaN "balances") and is
    not even valid JSON on the wire — neither is acceptable in an accounting
    standard. Caught at the input boundary so the client gets a clean error, not
    a corrupted result."""
    if not math.isfinite(value):
        raise ValueError(
            f"{field} must be a finite number (got {value!r}); "
            "NaN/Infinity are not valid accounting amounts."
        )
    return value


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

    @field_validator("debit", "credit")
    @classmethod
    def _finite_amount(cls, v: float, info) -> float:
        return _require_finite(v, info.field_name)


class SubsidiaryIn(BaseModel):
    """A subsidiary's trial balance in its local currency."""

    subsidiary_id: str = Field(..., description="Stable subsidiary identifier.")
    jurisdiction: str = Field(..., description="ISO 3166-1 alpha-2 code (e.g. 'mx').")
    currency: str = Field(..., description="ISO 4217 currency of the trial balance (e.g. 'MXN').")
    entries: List[TBEntryIn] = Field(
        default_factory=list, description="The subsidiary's trial-balance rows in local currency."
    )
    fx_rate_to_usd: Optional[float] = Field(
        None,
        description="Optional manual USD-per-unit override (audited as a 'manual' "
        "FX quote for asynchronous/contract-rate transactions).",
    )
    fx_rate_as_of: Optional[str] = Field(None, description="Effective date of the manual rate.")
    fx_rate_note: Optional[str] = Field(None, description="Rationale for the manual rate.")

    @field_validator("fx_rate_to_usd")
    @classmethod
    def _positive_finite_rate(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return v
        _require_finite(v, "fx_rate_to_usd")
        if v <= 0:
            # A zero rate silently zeroes every converted amount; a negative rate
            # sign-flips them — both corrupt the consolidation while still being
            # stamped into the FX audit trail as if legitimate.
            raise ValueError(
                f"fx_rate_to_usd must be > 0 (got {v!r}); a currency's USD value "
                "cannot be zero or negative."
            )
        return v


class EliminationIn(BaseModel):
    """An explicit intercompany pair to eliminate (deterministic, structured —
    never inferred from free text, per principle #5)."""

    from_subsidiary: str = Field(..., description="subsidiary_id of the first leg.")
    from_kontablo_id: str = Field(
        ..., description="Kontablo node id of the first leg, e.g. 'asset.current.receivables'."
    )
    to_subsidiary: str = Field(..., description="subsidiary_id of the counterparty leg.")
    to_kontablo_id: str = Field(
        "",
        description="Kontablo node id of the counterparty leg, e.g. 'liability.current.payables'. "
        "Defaults to from_kontablo_id (single-node elimination) if omitted.",
    )
    amount_usd: float = Field(..., description="USD amount to remove from each leg (finite).")

    @field_validator("amount_usd")
    @classmethod
    def _finite_amount(cls, v: float) -> float:
        return _require_finite(v, "amount_usd")


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
    # A non-empty nature must be a real accounting nature; otherwise the
    # boundary-library nature check would silently flag every mapping. Reject it
    # cleanly so the contract is unambiguous.
    norm_nature = nature or None
    if norm_nature is not None and norm_nature not in _VALID_NATURES:
        return {
            "jurisdiction": jurisdiction,
            "local_code": local_code,
            "local_name": local_name,
            "resolved": False,
            "error": f"nature must be one of {_VALID_NATURES} or omitted (got {nature!r}).",
        }
    entry = LocalEntry(code=local_code, name=local_name, nature=norm_nature)
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
        {"code": local_code, "name": local_name, "nature": norm_nature}, kid, engine.accounts
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
    # Per-entry amounts are validated finite at the model boundary, but a sum of
    # finite values can still overflow to ±inf (e.g. 1e308 + 1e308). Treat a
    # non-finite total as an explicit error rather than reporting a NaN/inf diff.
    if not (math.isfinite(debits) and math.isfinite(credits) and math.isfinite(diff)):
        errors.append(
            {
                "code": "NON_FINITE_TOTAL",
                "severity": "error",
                "message": "Trial-balance totals overflowed to a non-finite value; "
                "amounts are too large to sum safely.",
            }
        )
        diff = None
    elif abs(diff) > 0.01:
        errors.append(
            {
                "code": "UNBALANCED",
                "severity": "error",
                "message": f"Trial balance does not balance: Σdebits−Σcredits={diff}",
            }
        )
    return {
        "is_valid": not errors,
        "total_debits": debits if math.isfinite(debits) else None,
        "total_credits": credits if math.isfinite(credits) else None,
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
        jurisdiction: Annotated[
            str,
            Field(description="ISO 3166-1 alpha-2 jurisdiction code, e.g. 'mx', 'es', 'us' "
            "(case-insensitive). Determines which Tier-1 statutory code index is searched."),
        ],
        local_code: Annotated[
            str,
            Field(description="Local statutory account code as a STRING, e.g. '101' or '1.1.01'. "
            "Used for the Tier-1 exact lookup. Omit if you only have the name."),
        ] = "",
        local_name: Annotated[
            str,
            Field(description="Local account name in any supported language, e.g. 'Caja', "
            "'Bancos', 'Trade Receivables'. Used for the Tier-2 multilingual keyword match "
            "when the code does not resolve."),
        ] = "",
        nature: Annotated[
            Optional[str],
            Field(description="Optional account nature: 'debit' or 'credit' (or omit). Used only "
            "for a boundary-library sanity check; any other value is rejected."),
        ] = None,
    ) -> dict:
        return resolve_account_impl(engine, jurisdiction, local_code, local_name, nature)

    @server.tool(
        description="Look up a Kontablo ontology node by its kontablo_id (e.g. "
        "'asset.current.cash') or by its UUID. Returns label, nature, statement, "
        "and the jurisdiction local-code overlay."
    )
    def get_account(
        account_id: Annotated[
            Optional[str],
            Field(description="Kontablo node id, e.g. 'asset.current.cash'. Provide this OR uuid."),
        ] = None,
        uuid: Annotated[
            Optional[str],
            Field(description="Kontablo node UUID (e.g. as returned by resolve_account). "
            "Provide this OR account_id."),
        ] = None,
    ) -> dict:
        return get_account_impl(engine, account_id, uuid)

    @server.tool(
        description="Validate the double-entry identity of a trial balance: checks "
        "Σdebits − Σcredits == 0 deterministically. Returns is_valid, the totals, "
        "the balance difference, and any errors."
    )
    def validate_balance_sheet(
        entries: Annotated[
            List[TBEntryIn],
            Field(description="Trial-balance rows to check. Each row has debit and/or credit "
            "amounts (finite numbers; negatives allowed). The tool sums all debits and all "
            "credits and checks they are equal."),
        ],
    ) -> dict:
        return validate_balance_sheet_impl(entries)

    @server.tool(
        description="Consolidate subsidiary trial balances into a single USD trial "
        "balance, applying explicit (structured) intercompany eliminations. Each "
        "subsidiary is resolved deterministically and normalised to USD with an "
        "auditable per-entity FX quote. Returns the consolidated lines, "
        "eliminations applied, balance check, escalations, FX audit, and warnings."
    )
    def consolidate_trial_balances(
        subsidiaries: Annotated[
            List[SubsidiaryIn],
            Field(description="The subsidiary trial balances to consolidate, each in its own "
            "local currency. Each is resolved to universal nodes and converted to USD."),
        ],
        eliminations: Annotated[
            Optional[List[EliminationIn]],
            Field(description="Optional explicit intercompany pairs to eliminate. Each names both "
            "legs by (subsidiary_id, kontablo_id) and the USD amount to remove. Eliminations are "
            "structured — never inferred from text."),
        ] = None,
        target_currency: Annotated[
            str,
            Field(description="Reporting currency. v0.x supports 'USD' only; any other value is "
            "rejected with a clear error rather than mislabelling USD figures."),
        ] = "USD",
        parent_company_id: Annotated[
            str,
            Field(description="Optional label for the parent entity, echoed back in the response."),
        ] = "",
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
        region: Annotated[
            Optional[str],
            Field(description="Optional region filter, e.g. 'Africa', 'Europe', 'Americas', "
            "'Asia', 'Oceania' (case-insensitive)."),
        ] = None,
        mapping_mode: Annotated[
            Optional[str],
            Field(description="Optional filter: 'statutory_chart' (a mandated national chart "
            "exists) or 'ifrs_direct' (mapped via the IFRS tag, no national numeric chart)."),
        ] = None,
        tier1_only: Annotated[
            bool,
            Field(description="If true, return only jurisdictions with verified, primary-source-"
            "cited Tier-1 code sets (the strongest coverage claim)."),
        ] = False,
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
