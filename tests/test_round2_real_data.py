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


# ---------------------------------------------------------------------------
# Gold-standard accuracy (scored 2026-07-31)
# ---------------------------------------------------------------------------

def _agreement(experiment):
    path = ROOT / "research/experiments" / experiment / "gold/agreement.json"
    if not path.exists():
        pytest.skip(f"{path.relative_to(ROOT)} not generated")
    return json.loads(path.read_text(encoding="utf-8"))


def test_gold_sets_are_fully_adjudicated():
    """A half-arbitrated gold set is not admissible evidence (plan §6.3).

    `adjudicate_gold.py` DROPS an unadjudicated disagreement rather than
    resolving it by coin flip, so a pending row silently shrinks the sample
    instead of failing loudly. This is the loud failure.
    """
    for experiment, n_expected in (("tag_resolution_v1", 320), ("public_sector_gfs_v1", 212)):
        gold = ROOT / "research/experiments" / experiment / "gold/gold_labels_edgar.csv"
        if not gold.exists():
            pytest.skip(f"{experiment} gold not generated")
        rows = gold.read_text(encoding="utf-8").strip().splitlines()[1:]
        assert len(rows) == n_expected, (
            f"{experiment}: gold set has {len(rows)} rows, expected {n_expected}. "
            "A shortfall means a disagreement lost its adjudication note and was "
            "dropped -- re-run scripts/real_data/adjudicate_gold.py."
        )


def test_inter_annotator_agreement_is_reported_at_both_granularities():
    """Quoting only the coarse kappa would overstate agreement (plan §6.3)."""
    for experiment, exact, coarse in (
        ("tag_resolution_v1", 0.797, 0.777),
        ("public_sector_gfs_v1", 0.771, 0.807),
    ):
        agreement = _agreement(experiment)
        assert agreement["kappa_exact"]["kappa"] == pytest.approx(exact, abs=0.02), (
            f"{experiment}: kappa (exact) moved from {exact}. The gold labels changed; "
            "that must be a deliberate, documented relabeling, not silent drift."
        )
        assert agreement["kappa_class"]["kappa"] == pytest.approx(coarse, abs=0.02)
        assert "independence" in json.dumps(agreement).lower(), (
            f"{experiment}: the Addendum A.7 independence caveat must travel with "
            "the agreement statistics, not be stripped from them."
        )


def test_h1_is_partial_not_supported():
    """H1 measured 74.3% weighted -- inside the 50-75% PARTIAL band, not supported.

    The pre-registered bands are >=75% supports, 50-75% partial, <50% weakens.
    74.3% is 0.7 pp short of support. If this number moves up past 75, that is a
    real change of verdict and must be reported as such -- it must NOT be reached
    by rounding, nor by editing this assertion.
    """
    results = _load(TAG_RESULTS)
    pooled = results["accuracy_gold_sample"]["holdout"]["pooled"]
    assert pooled["n_codes"] == 320
    assert pooled["accuracy_pct_weighted"] == pytest.approx(74.3, abs=0.5)
    assert pooled["accuracy_pct_weighted"] < 75.0, (
        "H1 was PARTIAL at 74.3%. Crossing the 75% support threshold is a verdict "
        "change requiring a documented, dated addendum."
    )


def test_h1_failure_mode_is_over_mapping_not_wrong_node():
    """The load-bearing diagnosis: H1 loses points to false positives, not confusion.

    87 of 320 holdout codes were mapped when the gold says escalate; only 5
    resolved to the wrong node. If that ratio inverts, the resolver's failure mode
    has changed character and the write-up in ROUND2_RESULTS.md is stale.
    """
    results = _load(TAG_RESULTS)
    pooled = results["accuracy_gold_sample"]["holdout"]["pooled"]
    assert pooled["false_positive"] > 10 * pooled["wrong_node"], (
        f"H1's documented failure mode is over-mapping: {pooled['false_positive']} "
        f"false positives vs {pooled['wrong_node']} wrong-node errors."
    )
    leaf = results["accuracy_gold_sample"]["holdout"]["by_gold_class"]["leaf"]
    assert leaf["accuracy_pct_weighted"] == pytest.approx(94.6, abs=1.0), (
        "In-core accuracy (tags that genuinely ARE a core account) was 94.6% "
        "weighted. This is the number that says the resolver is accurate when the "
        "concept exists; it must not drift silently."
    )


def test_h5_clears_its_threshold_but_the_caveat_survives():
    """H5 scored 82.3% (>=70%), but 75% of the population is correct REFUSALS.

    The threshold is cleared as pre-registered. What must never be lost is that
    159 of 212 codes are COFOG functional codes whose correct answer is 'escalate',
    which the resolver achieves by having no COFOG rules at all -- and that only 13
    codes test real mapping. Stripping that caveat turns a weak result into a false
    validation claim.
    """
    results = _load(GFS_RESULTS)
    holdout = results["accuracy_gold_sample"]["holdout"]
    assert holdout["pooled"]["accuracy_pct_weighted"] == pytest.approx(82.3, abs=0.5)
    by_class = holdout["by_gold_class"]
    assert by_class["lens"]["n_codes"] == 159, (
        "The COFOG lens population drove H5's score; its size is load-bearing context."
    )
    assert by_class["leaf"]["n_codes"] == 13, (
        "Only 13 codes exercise an actual public-sector node mapping. If this grows, "
        "H5 becomes a stronger test and the write-up must be revisited."
    )
    text = SUMMARY.read_text(encoding="utf-8") if SUMMARY.exists() else ""
    assert "drafted, not yet empirically validated" in text, (
        "H5 clearing its numeric threshold does NOT license promoting public-sector "
        "coverage; ROUND2_RESULTS.md must keep the qualified wording."
    )


# ---------------------------------------------------------------------------
# Tier A2 -- ESEF (completed 2026-07-31)
# ---------------------------------------------------------------------------

def test_a2_esef_extensions_never_force_mapped():
    """H2 on a second, independent corpus: 0 Tier-1 hits on issuer extensions."""
    detail = ROOT / "research/experiments/tag_resolution_v1/resolution_detail.csv"
    if not detail.exists():
        pytest.skip("resolution_detail.csv not generated")
    import csv

    with detail.open(encoding="utf-8", newline="") as fh:
        esef = [r for r in csv.DictReader(fh) if r["source"] == "esef"]
    if not esef:
        pytest.skip("ESEF inventory not present")
    extensions = [r for r in esef if r["taxonomy_class"] == "extension"]
    assert len(extensions) == 1404
    violations = [r for r in extensions if r["tier"] == "tier1_exact"]
    assert not violations, (
        f"H2 violated on ESEF: {len(violations)} issuer extensions reached Tier 1 "
        "(exact code identity, confidence 1.0). An invented tag cannot have one; "
        "this means the crosswalk was contaminated with non-standard codes."
    )


def test_a2_ifrs_tag_ambiguity_is_recorded_not_coin_flipped():
    """The ontology's ifrs_tag field is not injective; ambiguous tags must escalate.

    Resolving them by sort order would be a coin flip presented as determinism
    (principle #5). The collisions are a reportable ontology defect, so they must
    stay visible in results.json rather than being quietly tie-broken away.
    """
    results = _load(TAG_RESULTS)
    ambiguous = results.get("ifrs_full_ambiguous_tags") or {}
    if not ambiguous:
        pytest.skip("ESEF inventory not present")
    assert set(ambiguous) == {
        "CashAndCashEquivalents",
        "CurrentTaxLiabilitiesCurrent",
        "OtherNonCurrentFinancialLiabilities",
    }
    for claimants in ambiguous.values():
        assert len(claimants) > 1
    assert results["crosswalk_sizes"]["ifrs-full"] == 24, (
        "27 distinct ifrs_tag values minus 3 ambiguous = 24 usable anchors."
    )


def test_a2_sample_is_train_only_and_says_so():
    """A2's mechanical rule produced an empty holdout; that must not be papered over."""
    summary = ROOT / "research/experiments/tag_resolution_v1/derived/esef_sample_summary.csv"
    if not summary.exists():
        pytest.skip("ESEF sample summary not generated")
    import csv

    with summary.open(encoding="utf-8", newline="") as fh:
        rows = {r["window"]: r for r in csv.DictReader(fh)}
    assert int(rows["train"]["n_filings"]) == 100
    assert int(rows["holdout"]["n_filings"]) == 0, (
        "A2's sample was entirely train-window. If a later run produces holdout "
        "filings, the selection rule changed -- which is post-hoc tuning unless "
        "recorded as a dated addendum."
    )
    assert int(rows["train"]["n_countries"]) == 20


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
