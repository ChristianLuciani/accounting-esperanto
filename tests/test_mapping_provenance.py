"""The account-resolution decision is auditable end-to-end (ADR-014): every
resolved entry carries a ``MappingQuote`` naming the deterministic tier and the
exact rule that fired, the consolidated lines expose their fiber size, and the
lineage reconstructs each consolidated figure — and the original local trial
balance — from the per-entry provenance. Mirrors ``test_fx_provenance.py``
(the ``FXQuote`` pattern applied to the mapping decision)."""

from core.engine import ConsolidationEngine, LocalEntry, SubsidiaryTB
from core.harness import resolve, resolve_with_rule


def _engine():
    return ConsolidationEngine()  # default: pinned static FX (no provider)


def _sample_tbs():
    return [
        SubsidiaryTB(
            subsidiary_id="acme-es",
            jurisdiction="es",
            currency="EUR",
            entries=[
                LocalEntry(code="572", name="Bancos", debit=1000.0, nature="debit"),
                LocalEntry(code="9999", name="Caja chica", debit=50.0, nature="debit"),
                LocalEntry(code="9998", name="???", credit=1050.0, nature="credit"),
            ],
        ),
        SubsidiaryTB(
            subsidiary_id="acme-de",
            jurisdiction="de",
            currency="EUR",
            entries=[
                LocalEntry(code="1000", name="Kasse", debit=200.0, nature="debit"),
            ],
        ),
    ]


def test_every_resolved_entry_carries_a_mapping_quote():
    result = _engine().consolidate(_sample_tbs())
    assert result.resolved
    for rec in result.resolved:
        mq = rec.mapping
        assert mq is not None
        assert mq.local_code == rec.local_code
        assert mq.local_name == rec.local_name
        assert mq.jurisdiction == rec.jurisdiction
        assert mq.kontablo_id == rec.kontablo_id
        assert mq.tier == rec.tier
        assert mq.confidence == rec.confidence
        assert mq.resolved_at


def test_rule_id_names_the_exact_deterministic_rule():
    eng = _engine()
    # Tier 1: exact Spanish PGC code lookup.
    t1 = eng.mapping_quote_for(LocalEntry(code="572", name="Bancos"), "es")
    assert t1.tier == "tier1_exact"
    assert t1.rule_id == "tier1:es:572"
    assert t1.kontablo_uuid
    # Tier 2: multilingual keyword rule; the rule id names node AND keyword.
    t2 = eng.mapping_quote_for(LocalEntry(code="zz", name="Petty Cash box"), "es")
    assert t2.tier == "tier2_keyword"
    assert t2.rule_id == "tier2:asset.current.cash:cash"
    # Escalated: no rule fired; explicit, never silent.
    esc = eng.mapping_quote_for(LocalEntry(code="9998", name="???"), "es")
    assert esc.tier == "escalated"
    assert esc.rule_id is None
    assert esc.kontablo_id is None
    assert not esc.resolved


def test_resolve_and_resolve_with_rule_agree():
    # The published deterministic-coverage behavior must be unchanged:
    # resolve() is a thin wrapper over resolve_with_rule().
    eng = _engine()
    cases = [
        ({"code": "572", "name": "Bancos", "nature": "debit"}, "es"),
        ({"code": "zz", "name": "Petty Cash", "nature": None}, "es"),
        ({"code": "9998", "name": "???", "nature": None}, "es"),
        ({"code": "1000", "name": "Kasse", "nature": "debit"}, "de"),
    ]
    for entry, j in cases:
        full = resolve_with_rule(entry, j, eng.accounts, eng.by_code)
        assert resolve(entry, j, eng.accounts, eng.by_code) == full[:3]


def test_lineage_reconstructs_every_consolidated_line():
    result = _engine().consolidate(_sample_tbs())
    fibers = result.lineage()
    assert fibers  # at least one consolidated node
    for line in result.lines:
        fiber = fibers[line.kontablo_id]
        assert line.source_count == len(fiber) > 0
        # The consolidated figure is exactly the sum of its fiber (no
        # eliminations in this scenario).
        assert round(sum(r.debit_usd for r in fiber), 2) == line.debit_usd
        assert round(sum(r.credit_usd for r in fiber), 2) == line.credit_usd
    # No resolved entry is outside a fiber, and no escalation is inside one.
    n_in_fibers = sum(len(f) for f in fibers.values())
    assert n_in_fibers == len(result.resolved) - len(result.escalations)
    for esc in result.escalations:
        assert esc.kontablo_id is None


def test_local_amounts_survive_translation_for_exact_roundtrip():
    # The USD figures are rounded post-FX and are NOT invertible through the
    # rate; the entry itself must keep the original local amounts.
    result = _engine().consolidate(_sample_tbs())
    by_key = {(r.subsidiary_id, r.local_code): r for r in result.resolved}
    assert by_key[("acme-es", "572")].debit_local == 1000.0
    assert by_key[("acme-es", "9998")].credit_local == 1050.0
    assert by_key[("acme-de", "1000")].debit_local == 200.0
    # And the escalated entry keeps its amounts too — nothing is dropped.
    esc = by_key[("acme-es", "9998")]
    assert esc in result.escalations
