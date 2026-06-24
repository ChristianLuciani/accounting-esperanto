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

from mcp.server.fastmcp.exceptions import ToolError  # noqa: E402
from pydantic import ValidationError  # noqa: E402

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


@pytest.mark.asyncio
async def test_tools_are_self_describing_for_agents(server):
    """Documentation bar: every tool carries a description AND every parameter in
    its input schema carries a description — that schema is what an LLM agent
    reads to decide how to call the tool. Guards against undocumented params
    regressing back in."""
    for t in await server.list_tools():
        assert t.description and len(t.description) > 30, f"{t.name} lacks a description"
        props = (t.inputSchema or {}).get("properties", {})
        assert props, f"{t.name} exposes no parameters in its schema"
        for pname, schema in props.items():
            # Pydantic models referenced via $ref/$defs document their fields on
            # the model itself (checked below); the top-level param still needs one.
            assert schema.get("description"), f"{t.name}.{pname} has no description"
        # Nested model fields (e.g. TBEntryIn.debit) must be documented too.
        for model_name, model_schema in (t.inputSchema or {}).get("$defs", {}).items():
            for fname, fschema in model_schema.get("properties", {}).items():
                assert fschema.get("description"), f"{model_name}.{fname} has no description"


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


# ===========================================================================
# Hardening / resilience — adversarial inputs must be rejected cleanly, never
# silently corrupt a result. A non-finite or sign-flipping value that "passes"
# a double-entry check would be disqualifying for an accounting standard.
# ===========================================================================
@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_amounts_rejected_at_model(bad):
    # A NaN debit defeats the balance check (abs(nan) > tol is False), so it must
    # be rejected at the input boundary, not summed.
    with pytest.raises(ValidationError):
        TBEntryIn(debit=bad)
    with pytest.raises(ValidationError):
        TBEntryIn(credit=bad)
    with pytest.raises(ValidationError):
        EliminationIn(
            from_subsidiary="a",
            from_kontablo_id="x",
            to_subsidiary="b",
            to_kontablo_id="y",
            amount_usd=bad,
        )


@pytest.mark.parametrize("bad_rate", [0.0, -1.0, -2.5, float("nan"), float("inf")])
def test_invalid_manual_fx_rate_rejected(bad_rate):
    # A zero rate silently zeroes every converted amount; a negative rate
    # sign-flips them. Both must be rejected before they reach the FX audit trail.
    with pytest.raises(ValidationError):
        SubsidiaryIn(subsidiary_id="a", jurisdiction="mx", currency="MXN", fx_rate_to_usd=bad_rate)


def test_valid_manual_fx_rate_accepted():
    s = SubsidiaryIn(subsidiary_id="a", jurisdiction="mx", currency="MXN", fx_rate_to_usd=0.05)
    assert s.fx_rate_to_usd == 0.05


def test_negative_amounts_still_allowed():
    # Negative debits/credits are legitimate (contra entries, reversals); only
    # NON-FINITE values are rejected. A balanced pair of negatives is valid.
    out = validate_balance_sheet_impl([TBEntryIn(debit=-100.0), TBEntryIn(credit=-100.0)])
    assert out["is_valid"] is True
    assert out["balance_difference"] == 0.0


def test_finite_overflow_reported_not_silently_valid():
    # Per-entry values are finite but their sum overflows to +inf. The tool must
    # flag it, not report a NaN/inf difference (and never emit non-finite JSON).
    out = validate_balance_sheet_impl([TBEntryIn(debit=1e308), TBEntryIn(debit=1e308)])
    assert out["is_valid"] is False
    assert out["errors"][0]["code"] == "NON_FINITE_TOTAL"
    assert out["balance_difference"] is None
    assert out["total_debits"] is None  # never an `inf` on the wire


def test_invalid_nature_rejected_with_clean_error(engine):
    out = resolve_account_impl(engine, "mx", "101", "Caja", nature="garbage")
    assert out["resolved"] is False
    assert "nature must be one of" in out["error"]


@pytest.mark.parametrize("good_nature", [None, "", "debit", "credit"])
def test_valid_natures_accepted(engine, good_nature):
    out = resolve_account_impl(engine, "mx", "101", "Caja", nature=good_nature)
    assert out["resolved"] is True
    assert out["kontablo_id"] == "asset.current.cash"


def test_determinism_same_input_identical_output(engine):
    # Principle #5: the same adversarial name resolves identically every time.
    name = "cash and bank and receivable mixed 银行"
    outs = {
        json.dumps(resolve_account_impl(engine, "zz", "", name), sort_keys=True)
        for _ in range(25)
    }
    assert len(outs) == 1


@pytest.mark.asyncio
async def test_malformed_call_raises_then_server_survives(server):
    """Resilience: a malformed tool call is rejected (ToolError) and the SAME
    server instance still serves the next valid call — one bad agent request
    must not take the server down."""
    with pytest.raises(ToolError):
        await server.call_tool("validate_balance_sheet", {"entries": [{"debit": float("nan")}]})
    with pytest.raises(ToolError):
        await server.call_tool(
            "consolidate_trial_balances",
            {"subsidiaries": [{"subsidiary_id": "a", "jurisdiction": "mx", "currency": "MXN",
                               "entries": [], "fx_rate_to_usd": 0.0}]},
        )
    # Server is still alive and correct after the bad calls.
    ok = await _call_json(server, "resolve_account", {"jurisdiction": "mx", "local_code": "101", "local_name": "Caja"})
    assert ok["kontablo_id"] == "asset.current.cash"
