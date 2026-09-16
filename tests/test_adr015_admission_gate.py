"""Claims–evidence gate for the ADR-015 admission run.

`research/experiments/adr015_admission_v1/DECISION_RECORD.md` and ADR-015's
Addendum A quote measured percentages and a verdict per candidate. Under the
project's "no claim without a command" rule those numbers must be regenerable
and pinned, exactly like the consolidation and coverage figures.

This regenerates the gate from the committed round-2 derivatives and asserts the
decision record still describes what the data says. It does NOT re-score any
hypothesis: the gate reads frequency distributions and applies a policy; it never
touches H1, H5 or the gold standard.

Run: pytest tests/test_adr015_admission_gate.py
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "research/experiments/adr015_admission_v1/results.json"
RECORD = ROOT / "research/experiments/adr015_admission_v1/DECISION_RECORD.md"
SCRIPT = ROOT / "scripts/adr015_admission_gate.py"


@pytest.fixture(scope="module")
def results():
    # Regenerate so the test fails if the committed JSON and the derived data diverge.
    proc = subprocess.run([sys.executable, str(SCRIPT)], cwd=str(ROOT), capture_output=True)
    assert proc.returncode == 0, proc.stderr.decode()[-2000:]
    return json.loads(RESULTS.read_text(encoding="utf-8"))


def test_populations_match_round2(results):
    """The gate must be reading the corpora round 2 actually committed."""
    pops = results["populations"]
    assert pops["edgar_standard_monetary_face_facts"] == 3_878_245
    assert pops["edgar_distinct_tags"] == 5_330
    assert pops["esef_standard_monetary_facts"] == 33_039
    assert pops["eurostat_na_item_observations"] == 1_260_004
    assert pops["imf_gfs_observations"] == 136_834


def test_literal_threshold_does_not_transfer(results):
    """The methodological headline: 0.5% cannot be carried across populations.

    Every already-admitted extended node falls below the literal threshold on
    EDGAR. If this ever flips, the re-derivation in ADR-015 Addendum A is no
    longer justified and the addendum must be revisited — not this assertion.
    """
    cal = results["threshold_calibration"]
    assert cal["literal_threshold_transfers_to_this_population"] is False
    anchors = {a["node"]: a["measurement"]["pct_of_population"] for a in cal["anchors"]}
    assert len(anchors) == 4
    assert all(p < cal["literal_adr015_threshold_pct"] for p in anchors.values()), \
        f"an already-admitted node now clears the literal 0.5%: {anchors}"
    assert cal["calibrated_floor_derived_from"] == "liability.current.payroll"
    assert cal["calibrated_floor_pct"] == pytest.approx(0.100, abs=0.005)


def test_exactly_one_candidate_admitted(results):
    assert results["admitted"] == ["liability.current.lease"]
    assert len(results["decisions"]) == 7


def test_the_admitted_node_clears_every_criterion(results):
    d = next(x for x in results["decisions"] if x["id"] == "liability.current.lease")
    assert d["admitted"] is True
    assert d["blocking_criteria"] == []
    assert d["A1"]["measured_pct"] == pytest.approx(0.645, abs=0.005)
    # The only candidate above the LITERAL threshold too, not just the floor.
    assert d["A1"]["vs_literal_threshold"]["verdict"] == "pass"
    assert d["A1"]["marginal"] is False
    # A3's mechanical half: the proposed anchor must not collide with an existing one.
    assert d["A3"]["collision_check"]["collides_with_existing_core_tag"] is False
    assert d["A2"]["esef_attestation"]["n_facts"] == 125


def test_contra_assets_are_deferred_not_silently_dropped(results):
    """Item 5's outcome. A marginal A1 must not read as a pass."""
    d = next(x for x in results["decisions"] if x["id"] == "asset.contra")
    assert d["admitted"] is False
    assert d["A1"]["marginal"] is True, \
        "contra-assets sit inside the floor's noise band; if that changes, the " \
        "deferral in the decision record needs revisiting"
    assert d["A2"]["verdict"] == "not_measurable"
    assert "A1(marginal)" in d["blocking_criteria"]


def test_rejection_reasons_are_the_documented_ones(results):
    """Each rejection is pinned to the criterion the decision record names."""
    blocking = {d["id"]: set(d["blocking_criteria"]) for d in results["decisions"]}
    assert "A2" in blocking["asset.current.restricted_cash"]
    assert blocking["liability.noncurrent.tiers"] == {"A1"}
    assert "A4" in blocking["income.oci_total"]          # a subtotal is never a node
    assert "A3" in blocking["income.oci_components"]     # no statement class fits
    assert blocking["gov.intermediate_consumption"] == {"A2"}  # no IFRS anchor -> overlay


def test_intermediate_consumption_volume_is_recorded(results):
    """The largest measured volume in the run, rejected from the CORE on A2 alone.

    Pinned because the decision record cites it as the top public-sector overlay
    priority, and because a rejection this large must stay visible.
    """
    d = next(x for x in results["decisions"] if x["id"] == "gov.intermediate_consumption")
    assert d["A1"]["verdict"] == "pass"
    assert d["A1"]["measured_pct"] == pytest.approx(5.19, abs=0.01)
    assert d["admitted"] is False


def test_ontology_still_has_zero_code_collisions(results):
    """ADR-015 A3 requires zero-collision re-validation after any admission."""
    assert results["ontology_code_collisions"] == 0


def test_decision_record_states_the_numbers_it_was_generated_from(results):
    """Guard the prose against the JSON — the drift this repo has hit most often."""
    text = RECORD.read_text(encoding="utf-8")
    cal = results["threshold_calibration"]
    admitted = next(x for x in results["decisions"] if x["id"] == "liability.current.lease")
    for needle in (
        f"{cal['calibrated_floor_pct']:.3f}%",
        f"{admitted['A1']['measured_pct']:.3f}%",
        f"{results['populations']['edgar_standard_monetary_face_facts']:,}",
    ):
        assert needle in text, f"DECISION_RECORD.md no longer cites {needle}"


def test_gate_does_not_rescore_any_hypothesis(results):
    """H1/H5 are off-limits: the gold vocabulary was 'one of the 30 core leaves'.

    Adding a node makes the committed gold stale for accuracy purposes, so a
    re-score would be invalid twice over (stale gold, and evaluating a change on
    the set it was designed against). The gate must therefore never emit an
    accuracy figure, and the round-2 results must stay byte-untouched.
    """
    blob = json.dumps(results)
    for forbidden in ("accuracy", "h1_", "h5_", "weighted_accuracy", "gold_labels"):
        assert forbidden not in blob.lower(), \
            f"the admission gate emitted {forbidden!r} — it must not score anything"
    round2 = json.loads((ROOT / "research/experiments/tag_resolution_v1/results.json")
                        .read_text(encoding="utf-8"))
    assert round2["accuracy_gold_sample"], "round-2 accuracy block must remain present"
