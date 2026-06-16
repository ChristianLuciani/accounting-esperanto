"""The FX rate applied to a balance is auditable end-to-end: every resolved
entry and the consolidation result carry the FXQuote that priced it, and a
manual override (for asynchronous transactions) is captured with its as-of date
and rationale. Deterministic — runs in static mode (conftest)."""

from core.engine import ConsolidationEngine, LocalEntry, SubsidiaryTB


def _engine():
    return ConsolidationEngine()  # default: pinned static FX (no provider)


def test_default_static_run_stamps_provenance_on_every_entry():
    eng = _engine()
    tb = SubsidiaryTB(
        subsidiary_id="acme-de",
        jurisdiction="de",
        currency="EUR",
        entries=[LocalEntry(code="x", name="Cash", debit=1000.0, nature="debit")],
    )
    result = eng.consolidate([tb])

    # per-subsidiary FX audit trail
    quote = result.fx_quotes["acme-de"]
    assert quote.source == "static-pinned"
    assert quote.mode == "static"
    assert quote.currency == "EUR"
    assert quote.retrieved_at

    # every resolved entry carries the quote that priced it
    assert result.resolved
    for rec in result.resolved:
        assert rec.fx is quote


def test_manual_override_is_audited_with_as_of_and_note():
    eng = _engine()
    tb = SubsidiaryTB(
        subsidiary_id="acme-ve",
        jurisdiction="ve",
        currency="VES",
        entries=[LocalEntry(code="x", name="Cash", debit=1_000_000.0, nature="debit")],
        fx_rate_to_usd=0.0017,
        fx_rate_as_of="2026-03-31",
        fx_rate_note="contract rate per SPA clause 4.2",
    )
    result = eng.consolidate([tb])

    quote = result.fx_quotes["acme-ve"]
    assert quote.source == "manual"
    assert quote.mode == "manual"
    assert quote.usd_per_unit == 0.0017
    assert quote.as_of == "2026-03-31"
    assert quote.note == "contract rate per SPA clause 4.2"

    # and the rate actually applied to the balance is the manual one
    cash = next(line for line in result.lines if line.kontablo_id == "asset.current.cash")
    assert cash.debit_usd == round(1_000_000.0 * 0.0017, 2)


def test_fx_to_usd_still_returns_a_bare_float():
    # Backwards-compat: the old float accessor keeps working.
    eng = _engine()
    tb = SubsidiaryTB(subsidiary_id="s", jurisdiction="de", currency="EUR")
    assert isinstance(eng.fx_to_usd(tb), float)
