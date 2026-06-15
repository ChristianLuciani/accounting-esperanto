"""
Surface-drift gate (adversarial review M3).

Stale-count drift across the four citable surfaces is this repo's documented
failure mode: the "23 jurisdictions" residue survived two release-prep passes,
and B1/B2 of the adversarial review caught numbers wrong by an order of
magnitude on two surfaces. This test pins the current headline numbers to all
four surfaces and bans every retired phrasing, so drift fails CI instead of
shipping.

Run: pytest tests/test_surface_claims.py
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

SURFACES = {
    "abstract": ROOT / "docs/papers/drafts/sections/abstract.tex",
    "readme": ROOT / "README.md",
    "citation": ROOT / "CITATION.cff",
    "zenodo": ROOT / ".zenodo.json",
}

# Every citable surface must carry the current headline numbers, in the
# phrasing that anchors them to their object (bare digits would false-match).
REQUIRED = [
    "195",                # sovereign jurisdictions mapped
    "75 entities",        # validation matrix size
    "68 jurisdictions",   # validation matrix breadth
    "56",                 # statutory charts exercised against primary sources
]

# Retired / superseded numbers that must never reappear on a citable surface.
# ("10 entities / 9 countries" is the initial run — legitimate in
# evaluation.tex, but never a headline on these four surfaces.)
BANNED = [
    "23 jurisdiction",
    "10 entities",
    "9 countries",
    "20 entities",        # pre-v2 matrix size
    "17 jurisdictions",   # pre-v2 matrix breadth
]


@pytest.mark.parametrize("name,path", SURFACES.items(), ids=SURFACES.keys())
def test_required_numbers_present(name, path):
    text = path.read_text(encoding="utf-8")
    missing = [n for n in REQUIRED if n not in text]
    assert not missing, f"{path.name} is missing headline number(s): {missing}"


@pytest.mark.parametrize("name,path", SURFACES.items(), ids=SURFACES.keys())
def test_banned_numbers_absent(name, path):
    text = path.read_text(encoding="utf-8")
    present = [n for n in BANNED if n in text]
    assert not present, f"{path.name} carries retired number(s): {present}"
