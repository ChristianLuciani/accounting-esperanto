"""The loss-ledger invariant (ADR-016): the pipeline may fail to translate,
but it may never LOSE — every point where information is not carried forward
must emit a typed, countable record. These tests pin the invariant at the
engine level and gate the full round-trip audit (the claims-evidence command
behind ``silent_losses == 0``). Deterministic; no LLM, no network."""

import importlib.util
import os

from core.engine import ConsolidationEngine, IntercompanyLink, LocalEntry, SubsidiaryTB

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _engine():
    return ConsolidationEngine()


def test_ontology_exclusions_are_typed_records():
    """Codes excluded from the Tier-1 index (collisions, non-code
    placeholders) are surfaced as structured records, never silently
    swallowed by the loader."""
    eng = _engine()
    for rec in eng.collisions:
        assert set(rec) == {"jurisdiction", "code", "ids"}
    for rec in eng.placeholders:
        assert set(rec) == {"jurisdiction", "code", "id"}
    # The exclusions exist in the real ontology (descriptive placeholders like
    # "Cash"); if this ever drops to zero the invariant is untested — revisit.
    assert len(eng.placeholders) > 0


def test_consolidate_conserves_every_entry():
    eng = _engine()
    tbs = [
        SubsidiaryTB(
            subsidiary_id="acme-es",
            jurisdiction="es",
            currency="EUR",
            entries=[
                LocalEntry(code="572", name="Bancos", debit=100.0, nature="debit"),
                LocalEntry(code="9998", name="???", credit=100.0, nature="credit"),
            ],
        ),
    ]
    result = eng.consolidate(tbs)
    # Nothing dropped: one resolved record per input row, escalations included.
    assert len(result.resolved) == 2
    assert len(result.escalations) == 1
    fibers = result.lineage()
    assert sum(len(f) for f in fibers.values()) + len(result.escalations) == 2
    # Full provenance on every record — including the escalated one.
    for r in result.resolved:
        assert r.mapping is not None
        assert r.fx is not None


def test_skipped_elimination_is_flagged_never_silent():
    eng = _engine()
    tb = SubsidiaryTB(
        subsidiary_id="a",
        jurisdiction="es",
        currency="EUR",
        entries=[LocalEntry(code="572", name="Bancos", debit=100.0, nature="debit")],
    )
    result = eng.consolidate(
        [tb],
        eliminations=[
            IntercompanyLink(
                from_subsidiary="a",
                from_kontablo_id="asset.current.receivables",  # not in this TB
                to_subsidiary="a",
                to_kontablo_id="liability.current.payables",
                amount_usd=50.0,
            )
        ],
    )
    assert result.eliminations_applied == 0
    assert any(f.startswith("elimination_skipped:") for f in result.cra_flags)


def test_roundtrip_audit_reports_zero_silent_losses():
    """The claims-evidence gate: on the exact dataset of the published v2
    validation run, the translation must conserve all entries, reconstruct
    every local trial balance exactly, and account for every non-translation
    in the typed loss ledger."""
    path = os.path.join(ROOT, "scripts", "roundtrip_audit.py")
    spec = importlib.util.spec_from_file_location("roundtrip_audit", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    summary = mod.run_audit()
    assert summary["silent_losses"] == 0
    assert summary["reconstruction_exact"] is True
    assert summary["provenance_complete"] is True
    assert summary["entries_in"] == summary["entries_resolved_out"] > 0
    assert summary["conservation"] == {"missing_rows": 0, "phantom_rows": 0}
    assert summary["fiber_mismatches"] == []
    # The published validation numbers stay recognizable in the audit view.
    assert summary["entities"] == 75
    assert summary["jurisdictions"] == 68
    assert summary["loss_ledger"]["escalated_entries"] == 4
