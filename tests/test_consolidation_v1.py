"""
Claims–evidence gate for the initial-run consolidation artifact (v1).

The preprint's evaluation section opens with a 10-entity / 9-country run whose
ledgers are synthetic trial balances written in four source-ERP export
layouts. This test regenerates the artifact from the committed script and pins
the numbers the paper cites, so the narrative can never drift from the
evidence again (the original B3 finding of the adversarial review).

Run: pytest tests/test_consolidation_v1.py
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts/consolidation_v1_initial_run.py"
OUT = ROOT / "research/experiments/consolidation_v1"


@pytest.fixture(scope="module")
def results():
    # Regenerate so the test fails if script and committed JSON diverge.
    subprocess.run([sys.executable, str(SCRIPT)], cwd=str(ROOT), check=True,
                   capture_output=True)
    return json.loads((OUT / "results.json").read_text(encoding="utf-8"))


def test_headline_shape(results):
    assert results["entities"] == 10
    assert results["n_countries"] == 9
    assert sorted(results["source_erp_formats"]) == [
        "erpnext", "odoo", "sap_b1", "zoho_books"]


def test_every_trial_balance_balances(results):
    for ent in results["per_entity"]:
        assert ent["balanced"], f"{ent['entity']} does not balance"
        assert ent["total_debits_local"] == ent["total_credits_local"]


def test_consolidated_identity_exact(results):
    assert results["identity"]["gap_usd"] == 0.0


def test_tier_pattern_cited_in_paper(results):
    """evaluation.tex cites SA escalating 7/12 and VN resolving 12/13 at
    Tier 1; pin those so the prose stays true to the artifact."""
    tiers = results["tiers_by_jurisdiction"]
    assert tiers["sa"]["escalated"] == 7
    assert tiers["vn"]["tier1_exact"] == 12
    assert results["escalated"] == 8
    assert results["deterministic_coverage_pct"] == 93.9


def test_fixtures_committed(results):
    fixtures = sorted(p.name for p in (OUT / "fixtures").glob("*.csv"))
    assert len(fixtures) == 10, f"expected 10 fixtures, found {fixtures}"


def test_synthetic_provenance_stated():
    """The artifact must declare itself synthetic (validation-honesty rule)."""
    readme = " ".join((OUT / "README.md").read_text(encoding="utf-8").split())
    assert "Not real company data" in readme
    assert "synthetic" in readme.lower()
