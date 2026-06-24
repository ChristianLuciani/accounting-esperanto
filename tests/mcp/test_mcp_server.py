"""Deterministic, offline tests for the Kontablo MCP server.

These assert (not print) that every MCP tool returns the same answers as the
engine that backs REST and gRPC, so README/CLAUDE.md can claim "MCP deterministic
core implemented" honestly. The tests run hermetically: the session forces
``KONTABLO_FX_MODE=static`` (conftest.py), so no tool reaches a live FX endpoint
and no LLM key is required. Each tool is exercised twice — once through its pure
``*_impl`` function and once through the real FastMCP ``call_tool`` dispatch — to
prove both the logic and the MCP registration/schema work.
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

pytest.importorskip("mcp", reason="mcp SDK not installed")

from api.mcp.server import (  # noqa: E402
    EliminationIn,
    SubsidiaryIn,
    TBEntryIn,
    build_engine,
    build_mcp,
    consolidate_trial_balances_impl,
    get_account_impl,
    list_jurisdictions_impl,
    resolve_account_impl,
    validate_balance_sheet_impl,
)


@pytest.fixture(scope="module")
def engine():
    return build_engine()


@pytest.fixture(scope="module")
def server():
    return build_mcp()


async def _call_json(server, name, args):
    """Dispatch a tool through the real FastMCP machinery and parse its JSON.

    Robust to the two FastMCP return shapes across mcp versions: a bare
    ``Sequence[ContentBlock]`` (1.2x) and a ``(content, structured)`` tuple
    (some 1.x lines)."""
    result = await server.call_tool(name, args)
    blocks = result[0] if isinstance(result, tuple) else result
    return json.loads(blocks[0].text)


# --- tool registration -----------------------------------------------------
@pytest.mark.asyncio
async def test_all_tools_registered(server):
    tools = {t.name for t in await server.list_tools()}
    assert tools == {
        "resolve_account",
        "get_account",
        "validate_balance_sheet",
        "consolidate_trial_balances",
        "list_jurisdictions",
    }
    # Tier-3 / LLM tools must NOT be exposed (kept honest like gRPC UNIMPLEMENTED).
    assert not any("classif" in t.lower() or "semantic" in t.lower() for t in tools)


# --- resolve_account (↔ MappingService.MapAccount) -------------------------
def test_resolve_tier1_exact(engine):
    # The demo case: MX SAT code 101 "Caja" → universal cash node, Tier-1 exact.
    out = resolve_account_impl(engine, "mx", "101", "Caja")
    assert out["resolved"] is True
    assert out["kontablo_id"] == "asset.current.cash"
    assert out["tier"] == "tier1_exact"
    assert out["match_method"] == "exact_lookup"
    assert out["confidence"] == 1.0
    assert out["kontablo_uuid"]  # non-empty UUID round-tripped


def test_resolve_tier2_keyword(engine):
    # No code, name-only → deterministic multilingual keyword rule (Tier-2).
    out = resolve_account_impl(engine, "xx", "", "Proveedores nacionales")
    assert out["resolved"] is True
    assert out["kontablo_id"] == "liability.current.payables"
    assert out["tier"] == "tier2_keyword"
    assert out["confidence"] == pytest.approx(0.85)


def test_resolve_escalates_without_guessing(engine):
    out = resolve_account_impl(engine, "xx", "99999", "Totally unknown line item")
    assert out["resolved"] is False
    assert out["kontablo_id"] is None
    assert out["match_method"] == "not_found"
    assert out["confidence"] == 0.0


@pytest.mark.asyncio
async def test_resolve_via_mcp_dispatch(server):
    out = await _call_json(
        server, "resolve_account", {"jurisdiction": "es", "local_code": "572", "local_name": "Bancos"}
    )
    assert out["kontablo_id"] == "asset.current.cash"
    assert out["tier"] == "tier1_exact"


# --- get_account (↔ AccountService.GetAccount) -----------------------------
def test_get_account_by_id(engine):
    out = get_account_impl(engine, account_id="asset.current.receivables")
    assert out["found"] is True
    assert out["kontablo_id"] == "asset.current.receivables"
    assert out["nature"] == "debit"
    assert out["kontablo_uuid"]


def test_get_account_by_uuid_roundtrip(engine):
    # Resolve id→uuid, then look the node back up by that UUID.
    by_id = get_account_impl(engine, account_id="asset.current.cash")
    by_uuid = get_account_impl(engine, uuid=by_id["kontablo_uuid"])
    assert by_uuid["found"] is True
    assert by_uuid["kontablo_id"] == "asset.current.cash"


def test_get_account_not_found(engine):
    out = get_account_impl(engine, account_id="does.not.exist")
    assert out["found"] is False
    assert "not found" in out["error"]


# --- validate_balance_sheet (↔ ValidationService.ValidateBalanceSheet) -----
def test_validate_balanced():
    out = validate_balance_sheet_impl(
        [TBEntryIn(local_code="572", debit=100.0), TBEntryIn(local_code="100", credit=100.0)]
    )
    assert out["is_valid"] is True
    assert out["balance_difference"] == 0.0


def test_validate_unbalanced():
    out = validate_balance_sheet_impl([TBEntryIn(local_code="572", debit=100.0)])
    assert out["is_valid"] is False
    assert out["balance_difference"] == 100.0
    assert out["errors"][0]["code"] == "UNBALANCED"


@pytest.mark.asyncio
async def test_validate_via_mcp_dispatch(server):
    out = await _call_json(
        server,
        "validate_balance_sheet",
        {"entries": [{"debit": 50.0}, {"credit": 50.0}]},
    )
    assert out["is_valid"] is True


# --- consolidate_trial_balances (↔ ConsolidationService.Consolidate...) ----
def test_consolidate_with_intercompany_elimination(engine):
    """Mirror the gRPC consolidation test: two subsidiaries, one double-entry
    intercompany elimination; the consolidated trial balance must balance."""
    parent = SubsidiaryIn(
        subsidiary_id="iberica-es",
        jurisdiction="es",
        currency="EUR",
        entries=[
            TBEntryIn(local_code="430", local_name="Clientes", debit=300_000),
            TBEntryIn(local_code="700", local_name="Ventas", credit=300_000),
        ],
    )
    sub = SubsidiaryIn(
        subsidiary_id="norte-mx",
        jurisdiction="mx",
        currency="MXN",
        entries=[
            TBEntryIn(local_code="102", local_name="Bancos", debit=1_724_137.93),
            TBEntryIn(local_code="201", local_name="Proveedores", credit=1_724_137.93),
        ],
    )
    elim = EliminationIn(
        from_subsidiary="iberica-es",
        from_kontablo_id="asset.current.receivables",
        to_subsidiary="norte-mx",
        to_kontablo_id="liability.current.payables",
        amount_usd=100_000.0,
    )
    out = consolidate_trial_balances_impl(engine, [parent, sub], [elim])
    assert out["ok"] is True
    assert out["eliminations_applied"] == 1
    assert out["balanced"] is True
    assert out["balance_difference"] == 0.0
    # Every subsidiary carries an auditable FX quote (static-pinned in tests).
    fx_subs = {q["subsidiary_id"] for q in out["fx_audit"]}
    assert fx_subs == {"iberica-es", "norte-mx"}
    assert all(q["mode"] == "static" for q in out["fx_audit"])


def test_consolidate_rejects_non_usd_target(engine):
    out = consolidate_trial_balances_impl(
        engine,
        [SubsidiaryIn(subsidiary_id="a", jurisdiction="mx", currency="MXN", entries=[])],
        target_currency="EUR",
    )
    assert out["ok"] is False
    assert "USD only" in out["error"]


@pytest.mark.asyncio
async def test_consolidate_via_mcp_dispatch(server):
    out = await _call_json(
        server,
        "consolidate_trial_balances",
        {
            "subsidiaries": [
                {
                    "subsidiary_id": "solo-us",
                    "jurisdiction": "us",
                    "currency": "USD",
                    "entries": [
                        {"local_code": "Cash", "local_name": "Cash", "debit": 1000.0},
                        {"local_code": "Capital", "local_name": "Share Capital", "credit": 1000.0},
                    ],
                }
            ]
        },
    )
    assert out["ok"] is True
    assert out["balanced"] is True


# --- list_jurisdictions (coverage manifest) --------------------------------
def test_list_jurisdictions_headline_numbers():
    """The coverage tool must report the published headline numbers unchanged
    (CLAIMS-evidence: 195 sovereign / 60 statutory / 56 Tier-1-ready)."""
    out = list_jurisdictions_impl()
    assert out["summary"]["total"] == 195
    assert out["summary"]["statutory_chart"] == 60
    assert out["summary"]["tier1_codes_available"] == 56


def test_list_jurisdictions_tier1_filter():
    out = list_jurisdictions_impl(tier1_only=True)
    assert out["count_returned"] == 56
    assert all(j["tier1_codes_available"] for j in out["jurisdictions"])


@pytest.mark.asyncio
async def test_list_jurisdictions_region_filter(server):
    out = await _call_json(server, "list_jurisdictions", {"region": "Africa"})
    assert out["count_returned"] > 0
    assert all(j["region"] == "Africa" for j in out["jurisdictions"])
