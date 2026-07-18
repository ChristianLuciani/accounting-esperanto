"""MCP surface of the entry-level lossless-translation guarantee (ADR-014):
``resolve_account`` names the exact deterministic rule that fired, and
``consolidate_trial_balances`` returns a per-entry ``mapping_audit`` plus
``source_entries`` fiber sizes so every consolidated figure is reconstructible.
Hermetic and keyless (static FX via conftest)."""

from api.mcp.server import (
    SubsidiaryIn,
    TBEntryIn,
    build_engine,
    consolidate_trial_balances_impl,
    resolve_account_impl,
)


def _engine():
    return build_engine()


def test_resolve_account_reports_rule_id():
    eng = _engine()
    out = resolve_account_impl(eng, "es", local_code="572", local_name="Bancos")
    assert out["resolved"] is True
    assert out["tier"] == "tier1_exact"
    assert out["rule_id"] == "tier1:es:572"

    kw = resolve_account_impl(eng, "es", local_code="zz", local_name="Petty Cash")
    assert kw["tier"] == "tier2_keyword"
    assert kw["rule_id"] == "tier2:asset.current.cash:cash"

    esc = resolve_account_impl(eng, "es", local_code="9998", local_name="???")
    assert esc["resolved"] is False
    assert esc["rule_id"] is None


def test_consolidate_returns_mapping_audit_with_full_lineage():
    eng = _engine()
    subs = [
        SubsidiaryIn(
            subsidiary_id="acme-es",
            jurisdiction="es",
            currency="EUR",
            entries=[
                TBEntryIn(local_code="572", local_name="Bancos", debit=1000.0),
                TBEntryIn(local_code="430", local_name="Clientes", debit=500.0),
                TBEntryIn(local_code="9998", local_name="???", credit=1500.0),
            ],
        ),
    ]
    out = consolidate_trial_balances_impl(eng, subs)
    assert out["ok"] is True

    audit = out["mapping_audit"]
    # One record per source entry — including the escalated one (never silent).
    assert len(audit) == 3
    escalated = [a for a in audit if a["kontablo_id"] is None]
    assert len(escalated) == 1
    assert escalated[0]["local_code"] == "9998"
    assert escalated[0]["credit_local"] == 1500.0

    for rec in audit:
        assert rec["tier"] in ("tier1_exact", "tier2_keyword", "escalated")
        if rec["kontablo_id"] is not None:
            assert rec["rule_id"]

    # Fiber sizes and reconstruction: each line equals the sum of its audit rows.
    for line in out["trial_balance"]:
        fiber = [a for a in audit if a["kontablo_id"] == line["kontablo_id"]]
        assert line["source_entries"] == len(fiber) > 0
        assert round(sum(a["debit_usd"] for a in fiber), 2) == line["debit"]
        assert round(sum(a["credit_usd"] for a in fiber), 2) == line["credit"]
