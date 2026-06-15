"""
Deterministic regression tests for KnowledgeBase.valid_uuids() / has_uuid().

These guard the Deterministic Boundary Library's membership check on the served
semantic-matcher path. The check previously crashed on the one list-shaped
localization (localizations/mx_sat/mapping.yaml) and the few mappings-less
files, because it assumed `mappings` was always a dict; the exception was then
swallowed by the matcher's try/except, so every semantic proposal escalated
instead of being validated. No LLM key is required for these tests.

Run: pytest tests/test_knowledge_base.py
"""

from logic.knowledge_base import KnowledgeBase


def test_valid_uuids_builds_over_all_localization_shapes():
    """Must not raise on dict-, list-, or None-shaped `mappings`, and must
    return a non-trivial set drawn from the committed localizations."""
    kb = KnowledgeBase()
    uuids = kb.valid_uuids()
    assert isinstance(uuids, set)
    assert len(uuids) > 100, f"expected the loaded ontology UUID set, got {len(uuids)}"


def test_has_uuid_accepts_real_nodes_and_rejects_bogus():
    kb = KnowledgeBase()
    # Cash and Trade Receivables are present across the committed localizations.
    assert kb.has_uuid("00000000-0000-4000-8000-000000000101")
    assert kb.has_uuid("00000000-0000-4000-8000-000000000104")
    # A well-formed but non-existent UUID must be rejected (the hallucination
    # the boundary check exists to catch).
    assert not kb.has_uuid("ffffffff-ffff-4fff-8fff-ffffffffffff")


def test_has_uuid_is_case_and_whitespace_insensitive():
    kb = KnowledgeBase()
    assert kb.has_uuid("  00000000-0000-4000-8000-000000000101  ")
    assert kb.has_uuid("00000000-0000-4000-8000-000000000101".upper())
