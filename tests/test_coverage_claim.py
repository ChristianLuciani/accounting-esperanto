"""
Claims–evidence gate for the transaction-VOLUME coverage figure.

The preprint and metadata surfaces state that the 30-account minimum core
covers ~N% of routine transaction volume (and an extended core reaches ~M%).
This test pins those cited numbers to the committed benchmark
(research/coverage_benchmark/coverage_results.json), so a citable surface can
never silently drift from the artifact that justifies it — the same discipline
the project applies to its other quantified claims.

It (1) regenerates the benchmark from the committed dataset, (2) checks the
core/extended node counts, and (3) asserts every citable surface carries the
benchmark's rounded numbers and no longer carries the retired, unbacked
"92% ... thousands of SME ledger exports" wording.

Run: pytest tests/test_coverage_claim.py
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "research/coverage_benchmark/coverage_results.json"
SCRIPT = ROOT / "scripts/coverage_benchmark.py"

# Surfaces that cite the figure and must stay consistent with the benchmark.
SURFACES = {
    "abstract": ROOT / "docs/papers/drafts/sections/abstract.tex",
    "readme": ROOT / "README.md",
    "citation": ROOT / "CITATION.cff",
    "zenodo": ROOT / ".zenodo.json",
}

# Legacy wording that overstated the evidence; must not reappear anywhere.
RETIRED_PHRASES = [
    "92\\% of routine",
    "92% of routine",
    "thousands of generic SME ledger exports",
    "thousands of SME ledger exports",
]


@pytest.fixture(scope="module")
def results():
    # Regenerate so the test fails if the dataset and the committed JSON diverge.
    subprocess.run([sys.executable, str(SCRIPT)], cwd=str(ROOT), check=True,
                   capture_output=True)
    return json.loads(RESULTS.read_text(encoding="utf-8"))


def test_node_counts(results):
    assert results["minimum_core_node_count"] == 30, \
        "Minimum core must stay exactly 30 (the frozen Pareto headline). ADR-015 " \
        "freezes this layer: admitted nodes go to extended_core, never here."
    assert results["extended_core_node_count"] == 35, \
        "Extended core must be 35 (minimum core + 5 extended nodes; " \
        "liability.current.lease admitted 2026-07-31 via the ADR-015 gate)."


def test_admission_basis_is_declared_and_the_headline_is_attributed(results):
    """The ~99% belongs to the volume-admitted nodes, and the split must be explicit.

    Four extended nodes were admitted on SYNTHETIC POSTING VOLUME measured by
    this benchmark; the fifth was admitted on REAL DISCLOSURE FREQUENCY (EDGAR),
    which this synthetic dataset cannot see, so it adds 0.0 pp. Both bases are
    legitimate under ADR-015 and they are not interchangeable. Without this
    assertion, "~99% with a 35-account extended core" would silently read as
    though all 35 earned it.
    """
    basis = results["extended_core_admission_basis"]
    assert "undeclared" not in basis.values(), \
        f"every extended_core node must declare an `admission.basis`: {basis}"
    assert set(basis.values()) <= {"synthetic_posting_volume", "real_disclosure_frequency"}

    on_benchmark = results["extended_core_admitted_on_this_benchmark"]
    assert len(on_benchmark) == 4, \
        "The ~99% headline is produced by exactly the four volume-admitted nodes."
    assert "liability.current.lease" not in on_benchmark, \
        "liability.current.lease was admitted on real EDGAR frequency, not on this " \
        "benchmark, and contributes 0.0 pp to the extended-core coverage figure."


def test_benchmark_is_in_expected_band(results):
    # Sanity guardrails, not a hard-coded value: the model should land the
    # minimum core in the low-90s and the extended core near 99 (line-weighted).
    mc = results["minimum_core_coverage_pct"]
    ec = results["extended_core_coverage_pct"]
    assert 90.0 <= mc <= 96.0, f"minimum-core volume coverage {mc}% out of expected band"
    assert 97.0 <= ec <= 99.9, f"extended-core volume coverage {ec}% out of expected band"
    assert ec > mc


def test_surfaces_cite_the_benchmark(results):
    mc = str(round(results["minimum_core_coverage_pct"]))   # "94"
    ec = str(round(results["extended_core_coverage_pct"]))  # "99"
    for name, path in SURFACES.items():
        text = path.read_text(encoding="utf-8")
        # Require the percent sign (plain or TeX-escaped): a bare "94" would
        # false-match unrelated digits (years, counts) and mask drift.
        assert (f"{mc}%" in text or f"{mc}\\%" in text), \
            f"{name} ({path.name}) does not cite minimum-core ~{mc}%"
        assert (f"{ec}%" in text or f"{ec}\\%" in text), \
            f"{name} ({path.name}) does not cite extended-core ~{ec}%"


def test_retired_wording_is_gone():
    # Scan the whole repo's text surfaces (cheap) for the unbacked phrasing.
    targets = list(SURFACES.values()) + [
        ROOT / "docs/papers/drafts/sections/ontology.tex",
        ROOT / "docs/papers/drafts/sections/evaluation.tex",
        ROOT / "docs/papers/drafts/sections/conclusion.tex",
    ]
    for path in targets:
        text = path.read_text(encoding="utf-8")
        for phrase in RETIRED_PHRASES:
            assert phrase not in text, \
                f"Retired unbacked wording '{phrase}' still present in {path.name}"
