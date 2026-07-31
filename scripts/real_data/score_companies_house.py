#!/usr/bin/env python3
"""
Kontablo — Tier B: UK Companies House real-filing case study (H3, H4).

WHY THIS EXISTS
  Tiers A1/A2 test alignment to STANDARDIZED taxonomies, where upstream filers
  already did the normalization work. Tier B is the harder, more diagnostic case
  from plan §4: real, uncurated, name-only captions with no shared code standard
  -- the closest public proxy for "local chart, local language". These are real
  statutory accounts filed with UK Companies House.

WHAT IT MEASURES
  H3  Do real captions resolve through the deterministic name-based tiers?
      Pre-registered as a RESOLUTION rate (>=60% supports, <30% weakens), so it
      is scored as coverage and needs no gold labels.
  H4  Do subtotals reconstructed from the filed line items match what the
      entity itself reported? (>=90% of subtotal lines reconcile.) This is an
      external, auditable check that does not depend on invisible eliminations.

  This is a CASE STUDY (n=10 filings), not a statistical benchmark. It does not
  generalize to the UK filing population and must never be described as if it
  did.

THE RESOLVER IS NOT MODIFIED
  Captions are fed to core.harness.resolve_with_rule as {code, name} entries
  under jurisdiction "uk", exactly as the engine would receive them. Tier 1
  cannot fire (a caption is not a statutory code), so this measures the shipped
  Tier-2 keyword rules against real language. Those rules were written long
  before this corpus was downloaded and were not tuned to it.

RECONCILIATION IS CONTEXT-SCOPED
  Every identity is checked WITHIN a single iXBRL context_ref. A filing reports
  the same concept for several periods and for both consolidated and
  company-only views; comparing across contexts would silently check a 2025
  figure against a 2024 one and produce a meaningless pass or fail.

LICENSING
  Companies House publishes no explicit reuse license for the bulk accounts
  product, so raw filings are NEVER redistributed (plan §7). The snapshots are
  gitignored and hash-manifested; only Kontablo's own derived output is
  committed.

OUTPUT
  research/experiments/consolidation_v3_real/results.json

Run:  venv/bin/python scripts/real_data/score_companies_house.py
"""

from __future__ import annotations

import csv
import json
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from core.harness.ontology import load_ontology  # noqa: E402
from core.harness.resolution import resolve_with_rule  # noqa: E402

EXPERIMENT = "consolidation_v3_real"
DERIVED = os.path.join(ROOT, "research/experiments", EXPERIMENT, "derived")
LINE_ITEMS = os.path.join(DERIVED, "ch_line_items.csv")

# UK FRS-102 accounting identities, expressed over the taxonomy's own concept
# local-names. Each is a statement the FILING ITSELF makes: the entity reported
# both sides, so a mismatch is either an ingestion bug or a real inconsistency.
# `lhs` must equal sum(plus) - sum(minus).
IDENTITIES = [
    {
        "name": "balance_sheet_equation",
        "lhs": "Equity",
        "plus": ["NetAssetsLiabilities"],
        "minus": [],
        "note": "Equity = net assets. The balance-sheet identity H4 targets.",
    },
    {
        "name": "net_current_assets",
        "lhs": "NetCurrentAssetsLiabilities",
        "plus": ["CurrentAssets"],
        "minus": ["Creditors"],
        "note": "Net current assets = current assets - creditors due within one year.",
    },
    {
        "name": "ppe_net_of_depreciation",
        "lhs": "PropertyPlantEquipment",
        "plus": ["PropertyPlantEquipmentGrossCost"],
        "minus": ["AccumulatedDepreciationImpairmentPropertyPlantEquipment"],
        "note": "Carrying amount = gross cost - accumulated depreciation.",
    },
    {
        "name": "intangibles_net_of_amortisation",
        "lhs": "IntangibleAssets",
        "plus": ["IntangibleAssetsGrossCost"],
        "minus": ["AccumulatedAmortisationImpairmentIntangibleAssets"],
        "note": "Carrying amount = gross cost - accumulated amortisation.",
    },
]


def parse_value(raw: str, sign: str) -> float | None:
    """Parse a filed iXBRL numeric value.

    Two real-world hazards, both of which silently corrupt totals if ignored:
    thousands separators, and the iXBRL ``sign="-"`` attribute, which negates a
    value that is PRINTED without a minus sign (plan §9, sign convention).
    """
    if raw is None:
        return None
    text = str(raw).strip().replace(",", "").replace(" ", "")
    if text in ("", "nan", "-", "—"):
        return None
    if text.startswith("(") and text.endswith(")"):
        text = "-" + text[1:-1]
    try:
        value = float(text)
    except ValueError:
        return None
    if str(sign).strip() == "-":
        value = -value
    return value


def local_name(qname: str) -> str:
    return str(qname).split(":")[-1]


# ---------------------------------------------------------------------------
# Population classification for H3
# ---------------------------------------------------------------------------
# The extractor collected every tagged numeric fact in each filing, which is far
# more than the face statements: it also picked up the NOTE movement tables
# (PP&E and intangibles roll-forwards) and their period markers. Those rows are
# "At 31 October 2025", "Additions", "Disposals", "Charge for the year" -- they
# are not accounts and no chart of accounts has a node for them.
#
# H3 is pre-registered over face-statement captions, so scoring the resolver
# against date headers would not falsify H3, it would just measure the wrong
# population. Rows are therefore classified deterministically, by the same rule
# already applied in Tier A1 and recorded in Addendum A.5: a BALANCE is an
# account, a MOVEMENT (a change in a balance) is not.
#
# The classification reads the taxonomy's own concept names and the caption
# shape -- no per-row discretion -- and BOTH populations are reported, so the
# effect of the filter is visible rather than assumed.
_PERIOD_MARKER = re.compile(r"^\s*(at|as at|balance at|cost at)\b", re.IGNORECASE)
_MOVEMENT_CONCEPT = re.compile(
    r"(Additions|Disposals|IncreaseFrom|DecreaseIn|DecreaseFrom|ChargeForYear"
    r"|Revaluation|TransferTo|TransferFrom|ExchangeDifference|Impairment(?:Loss|Charge)"
    r"|Amortisation(?:Charge|Expense)|WrittenOff|Reclassification)",
    re.IGNORECASE,
)


def classify_row(concept: str, caption: str) -> str:
    """balance | movement | period_marker -- deterministic, no per-row judgment."""
    if _PERIOD_MARKER.match(caption or ""):
        return "period_marker"
    if _MOVEMENT_CONCEPT.search(concept or ""):
        return "movement"
    return "balance"


def load_line_items() -> list[dict]:
    with open(LINE_ITEMS, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:
        row["value_num"] = parse_value(row.get("value"), row.get("sign"))
        row["concept"] = local_name(row.get("concept_qname", ""))
        row["row_class"] = classify_row(row["concept"], row.get("caption_text") or "")
    return rows


def score_h3(rows: list[dict], accounts: dict) -> dict:
    """H3: do real uncurated captions resolve through the deterministic tiers?"""
    by_code: dict = {"uk": {}}
    detail = []
    for row in rows:
        caption = (row.get("caption_text") or "").strip()
        if not caption:
            continue
        entry = {"code": row["concept"], "name": caption}
        kid, tier, conf, rule = resolve_with_rule(entry, "uk", accounts, by_code)
        detail.append({
            "company_number": row["company_number"],
            "concept": row["concept"],
            "caption": caption,
            "row_class": row["row_class"],
            "is_subtotal": str(row.get("is_subtotal_guess")).lower() == "true",
            "resolved_id": kid,
            "tier": tier,
            "rule": rule,
        })

    def bucket(items):
        n = len(items)
        resolved = sum(1 for d in items if d["resolved_id"])
        captions = {d["caption"] for d in items}
        resolved_captions = {d["caption"] for d in items if d["resolved_id"]}
        return {
            "n_line_items": n,
            "n_resolved": resolved,
            "resolved_pct_by_line": round(100.0 * resolved / n, 1) if n else 0.0,
            "n_distinct_captions": len(captions),
            "n_distinct_captions_resolved": len(resolved_captions),
            "resolved_pct_by_distinct_caption": (
                round(100.0 * len(resolved_captions) / len(captions), 1) if captions else 0.0
            ),
        }

    balances = [d for d in detail if d["row_class"] == "balance"]
    leaves = [d for d in balances if not d["is_subtotal"]]
    result = {
        "population_mix": {
            k: sum(1 for d in detail if d["row_class"] == k)
            for k in ("balance", "movement", "period_marker")
        },
        "all_tagged_facts": bucket(detail),
        "balances_incl_subtotals": bucket(balances),
        # Subtotals are aggregates, which the leaf resolver is not supposed to
        # map (same rule as Tier A1). The leaf-only view is the population H3 is
        # actually about; both are reported so the choice is visible.
        "leaf_line_items_only": bucket(leaves),
        "unresolved_top_captions": [],
    }
    misses: dict = defaultdict(int)
    for d in leaves:
        if not d["resolved_id"]:
            misses[d["caption"]] += 1
    result["unresolved_top_captions"] = [
        {"caption": c, "n": n}
        for c, n in sorted(misses.items(), key=lambda kv: (-kv[1], kv[0]))[:30]
    ]
    result["resolved_examples"] = [
        {"caption": d["caption"], "resolved_id": d["resolved_id"], "rule": d["rule"]}
        for d in sorted({d["caption"]: d for d in leaves if d["resolved_id"]}.values(),
                        key=lambda d: d["caption"])[:25]
    ]
    return result, detail


def score_h4(rows: list[dict]) -> dict:
    """H4: do the entity's own reported subtotals reconcile from its own line items?"""
    # (company, context) -> concept -> value. Context scoping is mandatory: see
    # the module docstring.
    cube: dict = defaultdict(dict)
    for row in rows:
        if row["value_num"] is None:
            continue
        key = (row["company_number"], row.get("context_ref") or "")
        # A concept can legitimately repeat inside one context (e.g. restated
        # blocks). Keep the first and flag rather than summing, which would
        # double-count.
        cube[key].setdefault(row["concept"], row["value_num"])

    checks = []
    for (company, context), concepts in sorted(cube.items()):
        for identity in IDENTITIES:
            needed = [identity["lhs"], *identity["plus"], *identity["minus"]]
            if not all(c in concepts for c in needed):
                continue
            lhs = concepts[identity["lhs"]]
            rhs = sum(concepts[c] for c in identity["plus"]) - sum(
                concepts[c] for c in identity["minus"]
            )
            # Tolerance is rounding only, per plan §3 H4. Filings are rounded to
            # the unit or to thousands; 1 unit plus 0.5 per component absorbs
            # rounding without absorbing a real error.
            tolerance = max(1.0, 0.5 * len(needed))
            checks.append({
                "company_number": company,
                "context_ref": context,
                "identity": identity["name"],
                "lhs_concept": identity["lhs"],
                "lhs": lhs,
                "rhs": rhs,
                "difference": round(lhs - rhs, 2),
                "reconciles": abs(lhs - rhs) <= tolerance,
            })

    by_identity: dict = defaultdict(lambda: {"n": 0, "ok": 0})
    for check in checks:
        node = by_identity[check["identity"]]
        node["n"] += 1
        node["ok"] += 1 if check["reconciles"] else 0
    for node in by_identity.values():
        node["reconcile_pct"] = round(100.0 * node["ok"] / node["n"], 1) if node["n"] else 0.0

    total = len(checks)
    ok = sum(1 for c in checks if c["reconciles"])
    return {
        "n_checks": total,
        "n_reconciled": ok,
        "reconcile_pct": round(100.0 * ok / total, 1) if total else 0.0,
        "by_identity": dict(sorted(by_identity.items())),
        "n_companies": len({c["company_number"] for c in checks}),
        "failures": [c for c in checks if not c["reconciles"]][:25],
    }


def main() -> None:
    if not os.path.exists(LINE_ITEMS):
        print(f"{EXPERIMENT}: {os.path.relpath(LINE_ITEMS, ROOT)} not found -- skipped")
        return
    accounts, _by_code, _collisions, _placeholders = load_ontology()
    rows = load_line_items()

    h3, h3_detail = score_h3(rows, accounts)
    h4 = score_h4(rows)

    results = {
        "experiment": EXPERIMENT,
        "design": "case study, n=10 real UK filings -- NOT a statistical benchmark",
        "provenance": (
            "UK Companies House free bulk accounts data (5 daily ZIPs, 77k filings "
            "inventoried, 10 extracted). No explicit reuse license published, so raw "
            "filings are hash-manifested and never redistributed."
        ),
        "h3_caption_resolution": h3,
        "h4_subtotal_reconciliation": h4,
    }
    out = os.path.join(ROOT, "research/experiments", EXPERIMENT, "results.json")
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)
        fh.write("\n")

    detail_path = os.path.join(ROOT, "research/experiments", EXPERIMENT, "h3_detail.csv")
    with open(detail_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["company_number", "concept", "caption", "is_subtotal",
                        "row_class", "resolved_id", "tier", "rule"],
            lineterminator="\n",
        )
        writer.writeheader()
        for row in sorted(h3_detail, key=lambda r: (r["company_number"], r["caption"])):
            writer.writerow({k: ("" if v is None else v) for k, v in row.items()})

    print("=" * 74)
    print("Kontablo round-2 Tier B -- UK Companies House case study (n=10 filings)")
    print("=" * 74)
    leaf = h3["leaf_line_items_only"]
    every = h3["all_tagged_facts"]
    print(f"  population mix: {h3['population_mix']}")
    print(f"  H3 caption resolution (balance leaf lines -- the pre-registered population):")
    print(f"      by line item      {leaf['resolved_pct_by_line']:>5.1f}%  "
          f"({leaf['n_resolved']}/{leaf['n_line_items']})")
    print(f"      by distinct caption {leaf['resolved_pct_by_distinct_caption']:>5.1f}%  "
          f"({leaf['n_distinct_captions_resolved']}/{leaf['n_distinct_captions']})")
    print(f"  H3 balances incl. subtotals: "
          f"{h3['balances_incl_subtotals']['resolved_pct_by_line']:>5.1f}% by line item")
    print(f"  H3 ALL tagged facts (incl. note movement tables, NOT the H3 population): "
          f"{every['resolved_pct_by_line']:>5.1f}%")
    print(f"  H4 subtotal reconciliation: {h4['reconcile_pct']:>5.1f}%  "
          f"({h4['n_reconciled']}/{h4['n_checks']} checks, {h4['n_companies']} companies)")
    for name, node in h4["by_identity"].items():
        print(f"      {name:<34} {node['reconcile_pct']:>5.1f}%  ({node['ok']}/{node['n']})")
    print("  Top unresolved real captions:")
    for miss in h3["unresolved_top_captions"][:12]:
        print(f"      {miss['n']:>4}x  {miss['caption'][:60]}")
    print(f"  Wrote research/experiments/{EXPERIMENT}/results.json")


if __name__ == "__main__":
    main()
