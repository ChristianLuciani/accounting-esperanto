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

# Citation hygiene: the canonical surfaces must cite the Zenodo *concept* DOI,
# which always resolves to the latest version. The per-version DOIs are pinned
# archives — citing one on a canonical surface freezes that version's frozen
# metadata (e.g. the v0.1.0 archive still carries the pre-release 2030-05-28
# BSL Change Date). This guards the regression fixed in PR #57: every surface
# carried the v0.1.0 *version* DOI (…796) and none carried the concept DOI.
# (release-notes-v0.1.0.md legitimately cites the v0.1.0 version DOI — it
#  documents that specific release — and is deliberately not a SURFACE here.)
CONCEPT_DOI = "10.5281/zenodo.20738795"
VERSION_DOIS = [
    "10.5281/zenodo.20738796",   # v0.1.0 version DOI (stale archive)
    "10.5281/zenodo.20739765",   # v0.1.1 version DOI
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


@pytest.mark.parametrize("name,path", SURFACES.items(), ids=SURFACES.keys())
def test_concept_doi_present(name, path):
    """Every canonical surface must cite the always-latest Zenodo concept DOI."""
    text = path.read_text(encoding="utf-8")
    assert CONCEPT_DOI in text, (
        f"{path.name} does not cite the Zenodo concept DOI {CONCEPT_DOI} "
        f"(it must resolve to the latest version, not a pinned archive)"
    )


# The v0.1.0 version DOI is a stale archive (frozen 2030-05-28 BSL date) and
# must never be a citation target on these surfaces. The v0.1.1 version DOI is
# allowed ONLY in CITATION.cff, where PR #57 records it as a secondary
# `identifiers` entry alongside the concept DOI.
STALE_VERSION_DOI = VERSION_DOIS[0]


@pytest.mark.parametrize("name,path", SURFACES.items(), ids=SURFACES.keys())
def test_stale_version_doi_absent(name, path):
    text = path.read_text(encoding="utf-8")
    assert STALE_VERSION_DOI not in text, (
        f"{path.name} carries the stale v0.1.0 version DOI {STALE_VERSION_DOI}; "
        f"cite the concept DOI {CONCEPT_DOI} instead"
    )
