"""`ifrs_tag` is a declared many-to-one projection — this test is the gate.

Round 2 measured real ESEF filings against the ontology and found `ifrs_tag` is
not injective: the 30 core nodes carry only 27 distinct values
(ROUND2_RESULTS.md, "The ontology's ifrs_tag field is not injective"). The
resolution was NOT to invent distinct IFRS tags — `ifrs-full:CashAndCashEquivalents`
genuinely is one IFRS concept, and cash-vs-bank is a finer distinction Kontablo
chose to make — but to TYPE the field as what it is: a projection whose inverse
returns a fiber, not a value.

A declared property that nothing enforces is a comment. This test makes it a
build gate, in both directions:

  * a NEW, unlisted collision FAILS — the accidental case the round-2 finding
    warns about, e.g. copy-pasting a node and leaving its neighbour's tag;
  * a LISTED fiber that no longer collides ALSO FAILS — so the allowlist cannot
    rot into a rubber stamp that silences whatever is added to it.

Scope is minimum core AND extended core. A collision that straddles the two
layers is still a collision, and scoping to the 30 is exactly why the round-2
analysis saw three fibers rather than four.

Run: pytest tests/test_ifrs_tag_projection.py
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.harness.ontology import load_ifrs_tag_projection  # noqa: E402

VALID_STATUSES = {"intended", "candidate_mistag"}


@pytest.fixture(scope="module")
def projection():
    return load_ifrs_tag_projection()


def declared_fibers(declaration):
    """{ifrs_tag: sorted[node_id]} as declared in the YAML allowlist."""
    return {
        entry["ifrs_tag"]: sorted(entry["nodes"])
        for entry in declaration.get("known_multi_node_fibers", [])
    }


def test_declaration_is_present_and_typed(projection):
    _, _, declaration = projection
    assert declaration, (
        "level3_accounts.yaml must carry an `ifrs_tag_projection` block. It is the "
        "declaration that ifrs_tag is a projection and not an identity."
    )
    for key in ("semantics", "resolution_rule", "governance", "known_multi_node_fibers"):
        assert key in declaration, f"`ifrs_tag_projection` is missing `{key}`"


def test_every_node_carries_a_tag(projection):
    """The projection must be TOTAL — every node maps to some IFRS concept.

    Many-to-one is declared; partial is not. A node with no tag would be
    invisible to the projection and would silently escape this gate.
    """
    from core.harness.ontology import ONTOLOGY_PATH  # local: path only, no reload cost
    import yaml

    ids = set()
    for doc in yaml.safe_load_all(open(ONTOLOGY_PATH, encoding="utf-8")):
        if isinstance(doc, dict) and "level3" in doc:
            items = doc["level3"]
        elif isinstance(doc, dict) and "extended_core" in doc:
            items = doc["extended_core"]
        elif isinstance(doc, list):
            items = doc
        else:
            continue
        ids.update(i["id"] for i in items if isinstance(i, dict) and "nature" in i)

    mapped, _, _ = projection
    assert ids - set(mapped) == set(), \
        f"nodes with no ifrs_tag (projection must be total): {sorted(ids - set(mapped))}"


def test_projection_is_many_to_one_not_injective(projection):
    """The declared structural property itself, asserted rather than assumed."""
    mapped, fibers, _ = projection
    assert len(fibers) < len(mapped), (
        "ifrs_tag is declared NON-injective. If it has become injective, that is a "
        "real change in the ontology's structure — update the declaration in "
        "level3_accounts.yaml and the spoke-3 framing, do not delete this test."
    )
    assert all(len(nodes) >= 1 for nodes in fibers.values())


def test_no_undeclared_collisions(projection):
    """A NEW collision fails the build. This is the accident-catching direction."""
    _, fibers, declaration = projection
    declared = declared_fibers(declaration)
    actual = {tag: nodes for tag, nodes in fibers.items() if len(nodes) > 1}

    undeclared = {t: n for t, n in actual.items() if t not in declared}
    assert not undeclared, (
        "New ifrs_tag collision(s) not declared in `known_multi_node_fibers`:\n  "
        + "\n  ".join(f"{t} -> {n}" for t, n in sorted(undeclared.items()))
        + "\n\nifrs_tag is a many-to-one projection, so a collision is legal — but it "
          "must be INTENDED and recorded with a reason. If this is an accidental "
          "duplicate (a copied node keeping its neighbour's tag), fix the tag. If it "
          "is a genuine one-IFRS-concept case, add it to the allowlist with its "
          "reason and status."
    )


def test_no_stale_declarations(projection):
    """A listed fiber that no longer collides fails too — the allowlist self-cleans."""
    _, fibers, declaration = projection
    declared = declared_fibers(declaration)
    actual = {tag: nodes for tag, nodes in fibers.items() if len(nodes) > 1}

    stale = sorted(t for t in declared if t not in actual)
    assert not stale, (
        f"`known_multi_node_fibers` lists tag(s) that no longer collide: {stale}. "
        "Remove them — an allowlist that outlives its entries stops being evidence "
        "of anything and starts silencing whatever is added to it."
    )
    drifted = {
        t: {"declared": declared[t], "actual": actual[t]}
        for t in declared
        if t in actual and declared[t] != actual[t]
    }
    assert not drifted, f"declared fiber membership no longer matches the ontology: {drifted}"


def test_every_declaration_carries_a_reason_and_status(projection):
    _, _, declaration = projection
    for entry in declaration["known_multi_node_fibers"]:
        tag = entry.get("ifrs_tag")
        assert entry.get("reason", "").strip(), \
            f"allowlisted fiber {tag} has no reason — an unexplained allowlist entry is a silencer"
        assert entry.get("status") in VALID_STATUSES, \
            f"allowlisted fiber {tag} has status {entry.get('status')!r}, expected one of {VALID_STATUSES}"
        assert len(entry.get("nodes", [])) > 1, \
            f"allowlisted fiber {tag} declares fewer than two nodes"


def test_known_collisions_are_the_documented_four(projection):
    """Pin the current fiber structure so a silent change is visible in the diff.

    Three of these are the collisions round 2 published; the fourth
    (CurrentTaxAssetsCurrent) straddles the minimum and extended cores and was
    surfaced by this test's wider scope on 2026-07-31.
    """
    _, fibers, _ = projection
    actual = {tag: nodes for tag, nodes in fibers.items() if len(nodes) > 1}
    assert actual == {
        "ifrs-full:CashAndCashEquivalents": ["asset.current.bank", "asset.current.cash"],
        "ifrs-full:CurrentTaxAssetsCurrent": ["asset.current.vat_input",
                                              "asset.current.withholding_tax"],
        "ifrs-full:CurrentTaxLiabilitiesCurrent": ["liability.current.tax",
                                                   "liability.current.vat_output"],
        "ifrs-full:OtherNonCurrentFinancialLiabilities": ["liability.noncurrent.debt",
                                                          "liability.noncurrent.lease"],
    }


def test_singleton_fibers_are_the_resolvable_ones(projection):
    """The declared resolution rule, made concrete.

    A tag resolves to a node iff its fiber is a singleton. This asserts the
    partition is non-degenerate in both directions — there really are resolvable
    tags, and there really are ambiguous ones — so neither branch of the rule is
    vacuous.
    """
    _, fibers, _ = projection
    singletons = {t for t, n in fibers.items() if len(n) == 1}
    ambiguous = {t for t, n in fibers.items() if len(n) > 1}
    assert singletons and ambiguous
    assert singletons.isdisjoint(ambiguous)
    assert "ifrs-full:CashAndCashEquivalents" in ambiguous, (
        "The worked instance of the finding: the most fundamental IFRS balance-sheet "
        "tag of all is the one that cannot resolve."
    )
