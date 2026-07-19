"""Integrity checks for every localization YAML.

Regression guard for the Norway-class bug: bare YAML 1.1 literals (NO, ON,
OFF, YES, N, Y) silently parse as booleans, which crashed the KnowledgeBase
at startup and 500'd every mapping endpoint. These tests load all
localizations and assert the invariants the rest of the pipeline relies on.
"""
import glob
import os
import sys

import yaml

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from logic.knowledge_base import KnowledgeBase

LOCALIZATIONS_DIR = os.path.join(project_root, "localizations")
MAPPING_FILES = sorted(glob.glob(os.path.join(LOCALIZATIONS_DIR, "*", "*.yaml")))

# 193 UN members + Holy See + Palestine = 195 sovereign; TW/HK/MO are
# non-sovereign extras. See scripts/build_jurisdiction_manifest.py.
SOVEREIGN_TARGET = 195


def test_localization_files_exist():
    assert len(MAPPING_FILES) >= SOVEREIGN_TARGET, (
        f"Expected at least {SOVEREIGN_TARGET} localization files, "
        f"found {len(MAPPING_FILES)}"
    )


def test_every_yaml_parses_and_country_is_string():
    bad = []
    for path in MAPPING_FILES:
        with open(path) as f:
            data = yaml.safe_load(f)
        if data is None:
            bad.append((path, "empty file"))
            continue
        country = (data.get("metadata") or {}).get("country")
        if country is not None and not isinstance(country, str):
            bad.append((path, f"metadata.country is {type(country).__name__} "
                              f"({country!r}) — quote YAML 1.1 literals like NO"))
    assert not bad, f"Localization YAML integrity failures: {bad}"


def test_mappings_are_well_formed():
    bad = []
    for path in MAPPING_FILES:
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        mappings = data.get("mappings")
        if mappings is None:
            continue  # universal-layer files may carry other structures
        if isinstance(mappings, list):
            # Legacy v0 schema (pre-rename, e.g. mx_sat): list of dicts with
            # local_codes/esperanto_uuid. Kept as audit trail; never extend it.
            if not all(isinstance(e, dict) for e in mappings):
                bad.append((path, "legacy list mappings contain non-dict entries"))
            continue
        if not isinstance(mappings, dict):
            bad.append((path, "mappings is neither dict nor legacy list"))
            continue
        for code, entry in mappings.items():
            if not isinstance(code, str):
                bad.append((path, f"mapping key {code!r} is not a string"))
            if not isinstance(entry, dict):
                bad.append((path, f"mapping entry for {code!r} is not a dict"))
    assert not bad, f"Malformed mappings: {bad[:10]}"


def test_knowledge_base_loads_all_jurisdictions():
    kb = KnowledgeBase(base_path=LOCALIZATIONS_DIR)
    assert len(kb.standards) >= SOVEREIGN_TARGET, (
        f"KnowledgeBase loaded only {len(kb.standards)} jurisdictions "
        f"(expected >= {SOVEREIGN_TARGET}) — a localization file is "
        "failing to load or register"
    )


# ---------------------------------------------------------------------------
# v2 structure-preservation fields (ADR-014): local_parent / facets /
# aggregation_group / local_hierarchy. All OPTIONAL — these tests only
# constrain files that opt in, so the 190+ v1 files stay untouched and valid.
# ---------------------------------------------------------------------------

def _dict_schema_files():
    for path in MAPPING_FILES:
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        if isinstance(data.get("mappings"), dict):
            yield path, data


def test_v2_local_parent_edges_are_referentially_sound():
    """A declared local_parent must point at a code that exists in the same
    file (another mapping or a local_hierarchy header) — a dangling tree edge
    would be a silent structural loss, the exact defect v2 exists to prevent."""
    bad = []
    for path, data in _dict_schema_files():
        mappings = data["mappings"]
        hierarchy = data.get("local_hierarchy") or {}
        known = set(mappings) | set(hierarchy)
        for code, entry in mappings.items():
            parent = entry.get("local_parent")
            if parent is not None and parent not in known:
                bad.append((path, code, parent))
        for code, node in hierarchy.items():
            parent = node.get("local_parent")
            if parent is not None and parent not in hierarchy:
                bad.append((path, f"local_hierarchy:{code}", parent))
    assert not bad, f"Dangling local_parent references: {bad[:10]}"


def test_v2_facets_and_groups_are_well_typed():
    bad = []
    for path, data in _dict_schema_files():
        for code, entry in data["mappings"].items():
            facets = entry.get("facets")
            if facets is not None:
                if not isinstance(facets, dict) or not all(
                    isinstance(k, str) and isinstance(v, str)
                    for k, v in facets.items()
                ):
                    bad.append((path, code, "facets must be a dict of strings"))
            group = entry.get("aggregation_group")
            if group is not None and not isinstance(group, str):
                bad.append((path, code, "aggregation_group must be a string"))
    assert not bad, f"Malformed v2 fields: {bad[:10]}"


def test_v2_aggregation_groups_declare_real_fibers():
    """An aggregation_group is a declared N:1 fiber: every member must map to
    the SAME kontablo_uuid (that is what makes it one fiber), and a group of
    one is a tagging mistake."""
    bad = []
    for path, data in _dict_schema_files():
        groups = {}
        for code, entry in data["mappings"].items():
            group = entry.get("aggregation_group")
            if isinstance(group, str):
                groups.setdefault(group, []).append(
                    (code, entry.get("kontablo_uuid"))
                )
        for group, members in groups.items():
            if len(members) < 2:
                bad.append((path, group, "declared on fewer than 2 codes"))
            if len({uuid for _, uuid in members}) > 1:
                bad.append((path, group, f"members target different nodes: {members}"))
    assert not bad, f"Inconsistent aggregation groups: {bad[:10]}"


def test_v2_exemplars_validate_against_json_schema():
    """The three v2 exemplar jurisdictions (mx SAT, br SPED, de SKR04) must
    validate against the formal mapping schema, and must actually exercise the
    v2 fields (so the schema is tested by real data, not just by absence)."""
    import jsonschema

    schema_path = os.path.join(
        project_root, "core", "schemas", "localization_mapping.schema.json"
    )
    import json

    with open(schema_path) as f:
        schema = json.load(f)

    exercised = {"local_parent": 0, "facets": 0, "aggregation_group": 0,
                 "local_hierarchy": 0}
    for iso, fname in (("mx", "sat_mapping.yaml"),
                       ("br", "sped_mapping.yaml"),
                       ("de", "skr04_mapping.yaml")):
        path = os.path.join(LOCALIZATIONS_DIR, iso, fname)
        with open(path) as f:
            data = yaml.safe_load(f)
        # last_updated parses as datetime.date; the schema leaves it untyped.
        jsonschema.validate(instance=data, schema=schema)
        if data.get("local_hierarchy"):
            exercised["local_hierarchy"] += 1
        for entry in data["mappings"].values():
            for field in ("local_parent", "facets", "aggregation_group"):
                if entry.get(field) is not None:
                    exercised[field] += 1
    assert all(count > 0 for count in exercised.values()), (
        f"exemplars must exercise every v2 field, got {exercised}"
    )


def test_load_localization_exposes_v2_structure():
    from core.harness import load_localization

    doc = load_localization("de")
    assert doc is not None
    assert doc["metadata"]["country"] == "de"
    assert "1600" in doc["mappings"]
    assert doc["mappings"]["1600"]["local_parent"] == "1"
    assert doc["local_hierarchy"]["1"]["name"]
    assert doc["mappings"]["3806"]["facets"]["vat_rate"] == "19"
    # A jurisdiction with no dict-format mapping file returns None (mx_sat's
    # legacy list format is deliberately not served by this loader).
    assert load_localization("zz-nonexistent") is None
