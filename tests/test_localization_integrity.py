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
