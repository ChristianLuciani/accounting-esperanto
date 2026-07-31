"""
Claims-evidence gate for the round-2 real-data validation.

Round 2 scored the resolver against real filings and real government finance
statistics. Two of its results are load-bearing and easy to misreport, so they
are pinned here:

  * H3 was FALSIFIED and H4 was SUPPORTED. If someone "fixes" the Tier-2 rules
    and re-runs, H3's number moves -- which is legitimate, but it must be a
    deliberate, documented act with a fresh holdout, not a silent drift. This
    test fails loudly in that case.
  * COVERAGE IS NOT ACCURACY. H1 and H5 are accuracy thresholds and are
    unscored; the artifacts must keep saying so, and must not start reporting a
    gold-derived accuracy without the agreement statistics that plan §6
    requires.

These tests read committed artifacts and never hit the network.

Run: pytest tests/test_round2_real_data.py
"""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TAG_RESULTS = ROOT / "research/experiments/tag_resolution_v1/results.json"
GFS_RESULTS = ROOT / "research/experiments/public_sector_gfs_v1/results.json"
CH_RESULTS = ROOT / "research/experiments/consolidation_v3_real/results.json"
SUMMARY = ROOT / "research/experiments/ROUND2_RESULTS.md"


def _load(path):
    if not path.exists():
        pytest.skip(f"{path.relative_to(ROOT)} not generated")
    return json.loads(path.read_text(encoding="utf-8"))


def test_tier_b_h4_supported():
    """H4: reconstructed subtotals reconcile at or above the 90% threshold."""
    results = _load(CH_RESULTS)
    h4 = results["h4_subtotal_reconciliation"]
    assert h4["n_checks"] > 0, "H4 ran no checks; the identity set or corpus broke"
    assert h4["reconcile_pct"] >= 90.0, (
        f"H4 was SUPPORTED at 100% on 2026-07-30 and is now {h4['reconcile_pct']}%. "
        "A drop below the pre-registered 90% floor is a real regression -- most "
        "likely a sign-convention or context-scoping bug in ingestion (plan §9)."
    )


def test_tier_b_h3_falsification_is_not_silently_repaired():
    """H3 was falsified at 22.7%. Moving it must be deliberate and documented.

    Adding the missing British-English keywords to TIER2_RULES would raise this
    number, but doing so and re-running against the SAME corpus is tuning on the
    test set. If this test fails because the number went UP, the fix is not to
    edit the assertion: it is to re-run against a fresh holdout and record the
    change as a dated addendum to the plan.
    """
    results = _load(CH_RESULTS)
    leaf = results["h3_caption_resolution"]["leaf_line_items_only"]
    assert leaf["resolved_pct_by_line"] == pytest.approx(22.7, abs=0.5), (
        f"H3 was measured at 22.7% (falsified, floor 30%) and is now "
        f"{leaf['resolved_pct_by_line']}%. See the docstring: do not edit this "
        "assertion to match a rule change made against the same corpus."
    )


def test_h1_and_h5_are_not_reported_as_scored():
    """Coverage must never be presented as if it satisfied an accuracy threshold."""
    for path in (TAG_RESULTS, GFS_RESULTS):
        results = _load(path)
        accuracy = results.get("accuracy_gold_sample") or {}
        if not accuracy:
            # Unscored is the expected state until gold labels are adjudicated.
            assert results.get("gold_labels_loaded", 0) == 0
            continue
        # If accuracy IS reported, plan §6 requires the agreement statistics
        # alongside it -- an accuracy number without kappa is not admissible.
        gold_dir = path.parent / "gold"
        assert (gold_dir / "agreement.json").exists(), (
            f"{path.relative_to(ROOT)} reports a gold accuracy but "
            f"{gold_dir.relative_to(ROOT)}/agreement.json is missing. Plan §6 "
            "requires inter-annotator agreement to be reported with it."
        )


def test_public_sector_extension_stays_unwired_and_qualified():
    """H5 is unscored, so the extension must remain scoring-local and qualified."""
    results = _load(GFS_RESULTS)
    status = results.get("public_sector_extension_status") or ""
    assert "NOT wired into core/harness" in status, (
        "The public-sector extension's scoring-local status disclaimer is gone. "
        "Wiring it into the live resolver is out of scope until H5 clears "
        "(plan §14)."
    )
    from core.harness.ontology import load_ontology

    accounts, _by_code, _collisions, _placeholders = load_ontology()
    leaked = [k for k in accounts if k.startswith(("GOV_", "EXP_", "LIAB_", "EQ_", "ASSET_"))]
    assert not leaked, (
        f"Public-sector extension nodes leaked into the live resolver ontology: "
        f"{leaked[:5]}. That is the §14 boundary this round must not cross."
    )


def test_round2_summary_keeps_the_non_comparability_warning():
    """The synthetic 97.3% and the real-data numbers must never be conflated."""
    if not SUMMARY.exists():
        pytest.skip("ROUND2_RESULTS.md not present")
    text = SUMMARY.read_text(encoding="utf-8")
    assert "97.3%" in text and "not comparable" in text.lower(), (
        "ROUND2_RESULTS.md must keep stating that the real-data figures are not "
        "comparable to the synthetic 97.3% validation."
    )
    assert "Coverage is not accuracy" in text or "coverage is not accuracy" in text.lower()
