"""Ontology loading for the Kontablo harness.

Loads the real Level-3 ontology YAML and the statutory-chart-family overlays,
and builds the deterministic Tier-1 reverse index (jurisdiction -> {local_code
-> kontablo_id}) used by the three-tier resolver. Collided codes and
descriptive (non-numeric) placeholders are excluded from the Tier-1 index so
they are never silently mis-resolved (boundary condition B1).

This is shared infrastructure: the deterministic engine (``core.engine``) and
the validation runner (``scripts/mass_consolidation_v2.py``) both build their
account graph from these loaders, guaranteeing a single source of truth.
"""

from __future__ import annotations

import os
from collections import defaultdict

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ONTOLOGY_PATH = os.path.join(ROOT, "core/schemas/level3_accounts.yaml")
FAMILIES_PATH = os.path.join(ROOT, "core/schemas/chart_families.yaml")


def load_families():
    """family -> {members:[iso], codes:{kontablo_id: local_code}}."""
    doc = yaml.safe_load(open(FAMILIES_PATH, encoding="utf-8"))
    return doc.get("families", {})


def merge_family_codes(by_code, families):
    """Add shared statutory-chart-family codes into the per-jurisdiction Tier-1
    index for every member jurisdiction (e.g., SYSCOHADA -> 17 OHADA states)."""
    for fam in families.values():
        for member in fam.get("members", []):
            for kid, code in fam.get("codes", {}).items():
                by_code.setdefault(member, {}).setdefault(str(code), kid)
    return by_code


def load_ontology():
    # The YAML is multi-section: the ASSETS section is a dict with key "level3";
    # LIABILITIES/EQUITY/INCOME/roadmap sections are bare YAML lists (no key).
    # Collect account dicts from BOTH shapes; an account is any item carrying
    # both "id" and "nature" (this excludes aggregation/validation rule blocks).
    docs = list(yaml.safe_load_all(open(ONTOLOGY_PATH, encoding="utf-8")))
    accounts = {}

    def ingest(item):
        if isinstance(item, dict) and "id" in item and "nature" in item:
            accounts[item["id"]] = {
                "uuid": item.get("uuid"),
                "label": item.get("label_en", item["id"]),
                "nature": item.get("nature", "unknown"),
                "statement": item.get("statement", "unknown"),
                "local_codes": {k: str(v) for k, v in (item.get("local_codes") or {}).items()},
            }

    for d in docs:
        if isinstance(d, dict) and "level3" in d:
            for a in d["level3"]:
                ingest(a)
        elif isinstance(d, list):
            for a in d:
                ingest(a)
    # reverse index: jurisdiction -> {local_code -> kontablo_id}, detecting
    # collisions (same jurisdiction+code mapped to >1 Kontablo node = a latent
    # ontology data-quality defect). Collided codes are EXCLUDED from the
    # deterministic index so they are not silently mis-resolved.
    # A real statutory code contains at least one digit. Descriptive text
    # placeholders (e.g. "Cash", "Vorsteuer", "IVA Acreditable") are NOT codes
    # and are excluded from the Tier-1 index (boundary condition B1).
    def is_code(c):
        return any(ch.isdigit() for ch in str(c))

    raw = defaultdict(lambda: defaultdict(list))
    placeholders = []
    for kid, a in accounts.items():
        for j, code in a["local_codes"].items():
            if is_code(code):
                raw[j][code].append(kid)
            else:
                placeholders.append({"jurisdiction": j, "code": str(code), "id": kid})
    by_code = defaultdict(dict)
    collisions = []
    for j in raw:
        for code, ids in raw[j].items():
            if len(ids) > 1:
                collisions.append({"jurisdiction": j, "code": code, "ids": sorted(ids)})
            else:
                by_code[j][code] = ids[0]
    return accounts, by_code, collisions, placeholders
