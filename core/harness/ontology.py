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
LOCALIZATIONS_DIR = os.path.join(ROOT, "localizations")


def load_localization(iso):
    """Load a jurisdiction's full localization mapping structure (v2-aware).

    Returns the parsed YAML document of ``localizations/<iso>/*_mapping.yaml``
    including the OPTIONAL structure-preservation fields (``local_parent``,
    ``facets``, ``aggregation_group``, ``local_hierarchy`` — ADR-014), or
    ``None`` if the jurisdiction has no dict-format mapping file. This is a
    *read* surface for fiber/lineage queries; it does NOT feed the Tier-1
    resolution index (which is built from the ontology + chart families), so
    adding v2 fields can never change resolution behavior.
    """
    import glob

    iso = iso.lower()
    for path in sorted(glob.glob(os.path.join(LOCALIZATIONS_DIR, iso, "*_mapping.yaml"))):
        doc = yaml.safe_load(open(path, encoding="utf-8"))
        if not isinstance(doc, dict):
            continue
        mappings = doc.get("mappings")
        if isinstance(mappings, dict):  # v1/v2 dict schema (legacy list = mx_sat only)
            doc["_path"] = path
            return doc
    return None


def rollup(accounts, lens):
    """Partition the ontology's nodes by the value of a grouping lens.

    Returns ``{lens_value: [kontablo_id, ...]}``. The same node set can be
    rolled up simultaneously under different lenses (``ifrs``, ``cash_flow``,
    ...) — this is the DAG the "graph, not tree" principle promises: one UUID,
    multiple parallel rollup hierarchies. Nodes that do not carry the lens are
    grouped under ``None`` (explicit, never silently dropped — ADR-014).
    """
    out = {}
    for kid in sorted(accounts):
        value = (accounts[kid].get("groupings") or {}).get(lens)
        out.setdefault(value, []).append(kid)
    return out


def node_fiber(accounts, by_code, kontablo_id, jurisdiction=None):
    """The fiber of a Kontablo node: which local statutory codes collapse into
    it, per jurisdiction (the preimage of the projection — ADR-014).

    Sources, in order:
      1. the deterministic Tier-1 reverse index (ontology ``local_codes`` +
         statutory chart-family overlays), tagged ``source: tier1_index``;
      2. when ``jurisdiction`` is given, that jurisdiction's localization
         mapping file — which can add codes the Tier-1 index excludes and
         enriches members with the v2 structure fields (``local_parent``,
         ``facets``, ``aggregation_group``), tagged ``source: localization``.

    Without ``jurisdiction`` the localization enrichment is skipped (loading
    all 195+ files per query would be pointlessly slow); the Tier-1 view is
    still complete across jurisdictions. Returns ``None`` for an unknown node.
    """
    node = accounts.get(kontablo_id)
    if node is None:
        return None
    want = jurisdiction.lower() if jurisdiction else None
    fiber = {}
    for j, codes in by_code.items():
        if want and j != want:
            continue
        for code, target in codes.items():
            if target == kontablo_id:
                fiber.setdefault(j, []).append({"code": code, "source": "tier1_index"})
    if want:
        doc = load_localization(want)
        if doc:
            uuid = str(node.get("uuid"))
            known = {m["code"] for m in fiber.get(want, [])}
            for code, entry in doc["mappings"].items():
                if str(entry.get("kontablo_uuid")) != uuid:
                    continue
                member = next(
                    (m for m in fiber.setdefault(want, []) if m["code"] == str(code)),
                    None,
                )
                if member is None:
                    member = {"code": str(code), "source": "localization"}
                    fiber[want].append(member)
                member["name"] = entry.get("name")
                for field in ("local_parent", "facets", "aggregation_group"):
                    if entry.get(field) is not None:
                        member[field] = entry[field]
    for members in fiber.values():
        members.sort(key=lambda m: m["code"])
    return {
        "kontablo_id": kontablo_id,
        "kontablo_uuid": str(node.get("uuid") or ""),
        "label_en": node["label"],
        "jurisdictions": dict(sorted(fiber.items())),
        "total_codes": sum(len(m) for m in fiber.values()),
    }


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
            # Multi-lens rollup memberships (ADR-014, principle #1 "graph, not
            # tree"): the primary IFRS lens is composed from ``parent`` (one
            # source of truth, no duplication drift); additional lenses (e.g.
            # cash_flow) come from the node's explicit ``groupings`` block.
            groupings = {"ifrs": item.get("parent")}
            for lens, value in (item.get("groupings") or {}).items():
                groupings[str(lens)] = value
            accounts[item["id"]] = {
                "uuid": item.get("uuid"),
                "label": item.get("label_en", item["id"]),
                "nature": item.get("nature", "unknown"),
                "statement": item.get("statement", "unknown"),
                "local_codes": {k: str(v) for k, v in (item.get("local_codes") or {}).items()},
                "groupings": groupings,
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
