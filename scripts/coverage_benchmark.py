#!/usr/bin/env python3
"""
Kontablo — Transaction-Volume Coverage Benchmark (reproducible).

WHY THIS EXISTS
  The preprint claims the 30-account Level-3 minimum core covers ~92% of
  routine transaction VOLUME. That figure was previously asserted as
  "empirically benchmarked against thousands of SME ledger exports" with NO
  committed dataset or script behind it — a violation of the project's
  epistemic standard (every non-trivial claim must be citable and verifiable).
  This script makes the number regenerable from a single command, and is the
  single source of truth for it.

WHAT IT MEASURES (and what it does NOT)
  It measures coverage by POSTING VOLUME (journal-line count): of all journal
  lines a representative SME posts, what fraction land on a minimum-core node.
  This is DISTINCT from mass_consolidation_v2.py's deterministic_coverage_pct
  (97.3%), which is the share of synthetic ledger ENTRIES the deterministic
  tiers resolve to *some* node. Two different questions; do not conflate them.

INPUTS
  core/schemas/level3_accounts.yaml
      - level3: + bare-list sections -> the 30-node MINIMUM CORE
      - extended_core: (optional dict block) -> the EXTENDED CORE nodes
  research/coverage_benchmark/transaction_frequency.yaml
      - transactions: weighted transaction types with journal-line legs
      - extended_absorption: residual.* label -> extended_core node id

OUTPUT
  research/coverage_benchmark/coverage_results.json   (committed)
  stdout: the honest two-number framing.

PROVENANCE
  The frequency dataset is a SYNTHETIC, transparently-parameterized reference
  distribution, not measured field data. See the header of
  transaction_frequency.yaml for citations and caveats. The headline must be
  reported as a model-based estimate ("estimated to cover ~X%").

Run:  venv/bin/python scripts/coverage_benchmark.py
      python3 scripts/coverage_benchmark.py --unit transaction   # strict mode
"""

import os
import sys
import csv
import json
import argparse
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONTOLOGY_PATH = os.path.join(ROOT, "core/schemas/level3_accounts.yaml")
DATASET_PATH = os.path.join(ROOT, "research/coverage_benchmark/transaction_frequency.yaml")
OUT_PATH = os.path.join(ROOT, "research/coverage_benchmark/coverage_results.json")
CSV_PATH = os.path.join(ROOT, "research/coverage_benchmark/coverage_breakdown.csv")


def load_core_and_extended():
    """Return (minimum_core_ids:set, extended_core_ids:set).

    Minimum core = every account dict (has both 'id' and 'nature') reachable
    from the 'level3:' dict block and the bare-list sections (LIABILITIES,
    EQUITY, INCOME STATEMENT). This deliberately mirrors the loader in
    mass_consolidation_v2.py so the SAME 30 nodes are counted.

    Extended core = node dicts under the optional 'extended_core:' dict block.
    Kept under its own key precisely so the minimum-core loader (and the 30
    headline) never picks them up.
    """
    docs = list(yaml.safe_load_all(open(ONTOLOGY_PATH, encoding="utf-8")))
    core, extended = set(), set()

    def is_account(item):
        return isinstance(item, dict) and "id" in item and "nature" in item

    for d in docs:
        if isinstance(d, dict) and "level3" in d:
            for a in d["level3"]:
                if is_account(a):
                    core.add(a["id"])
        elif isinstance(d, list):
            for a in d:
                if is_account(a):
                    core.add(a["id"])
        elif isinstance(d, dict) and "extended_core" in d:
            for a in d["extended_core"]:
                if is_account(a):
                    extended.add(a["id"])
    return core, extended


def load_dataset():
    doc = yaml.safe_load(open(DATASET_PATH, encoding="utf-8"))
    return doc["transactions"], doc.get("extended_absorption", {}), doc.get("meta", {})


def measure(transactions, absorption, core_ids, extended_node_ids, unit):
    """Compute coverage. unit='line' (line-weighted) or 'transaction' (a
    transaction counts as covered only if ALL its legs are covered)."""
    # A residual.* leg is covered-in-extended iff the absorption map routes it
    # to an extended_core node that actually exists.
    def covered_core(leg):
        return leg in core_ids

    def covered_ext(leg):
        if leg in core_ids:
            return True
        target = absorption.get(leg)
        return target is not None and target in extended_node_ids

    tot = core = ext = 0.0
    residual_volume = {}  # residual leg -> line-volume still uncovered in extended
    for t in transactions:
        w = float(t["weight"])
        legs = t["legs"]
        if unit == "line":
            tot += w * len(legs)
            core += w * sum(covered_core(l) for l in legs)
            ext += w * sum(covered_ext(l) for l in legs)
            for l in legs:
                if not covered_ext(l):
                    residual_volume[l] = residual_volume.get(l, 0.0) + w
        else:  # transaction-level (strict): all legs must be covered
            tot += w
            core += w * all(covered_core(l) for l in legs)
            ext += w * all(covered_ext(l) for l in legs)
            if not all(covered_ext(l) for l in legs):
                for l in legs:
                    if not covered_ext(l):
                        residual_volume[l] = residual_volume.get(l, 0.0) + w
    return {
        "total": round(tot, 2),
        "min_core_covered": round(core, 2),
        "extended_covered": round(ext, 2),
        "min_core_pct": round(100.0 * core / tot, 1),
        "extended_pct": round(100.0 * ext / tot, 1),
        "residual_volume_by_label": {k: round(v, 2) for k, v in sorted(
            residual_volume.items(), key=lambda kv: -kv[1])},
    }


def scale_misc(transactions, factor):
    """Return a copy of the dataset with every General Journal (tail)
    transaction's weight multiplied by `factor`. The general journal is the
    long tail the coverage claim could be accused of underweighting; the
    sensitivity sweep makes that attack quantitative instead of rhetorical."""
    if factor == 1.0:
        return transactions
    return [
        {**t, "weight": float(t["weight"]) * factor}
        if t.get("journal") == "general" else t
        for t in transactions
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--unit", choices=["line", "transaction"], default="line",
                    help="line = journal-line weighted (default, headline); "
                         "transaction = strict (all legs must be covered).")
    ap.add_argument("--misc-weight", type=float, default=1.0, metavar="K",
                    help="multiply every General Journal (tail) transaction "
                         "weight by K before measuring (sensitivity analysis; "
                         "default 1.0 = the committed distribution).")
    args = ap.parse_args()

    core_ids, extended_node_ids = load_core_and_extended()
    transactions, absorption, meta = load_dataset()
    transactions = scale_misc(transactions, args.misc_weight)

    # Sanity: the minimum core must be exactly 30 (the frozen headline).
    if len(core_ids) != 30:
        print(f"WARNING: minimum-core node count = {len(core_ids)}, expected 30. "
              f"The 30-account headline and this benchmark have drifted.",
              file=sys.stderr)

    line_res = measure(transactions, absorption, core_ids, extended_node_ids, "line")
    txn_res = measure(transactions, absorption, core_ids, extended_node_ids, "transaction")
    res = line_res if args.unit == "line" else txn_res

    # Sensitivity sweep: how the headline moves if the General Journal tail
    # is systematically underweighted in the committed distribution.
    sweep = {}
    for k in (1.0, 1.5, 2.0, 3.0):
        r = measure(scale_misc(load_dataset()[0], k), absorption,
                    core_ids, extended_node_ids, "line")
        sweep[str(k)] = {"minimum_core_pct": r["min_core_pct"],
                         "extended_core_pct": r["extended_pct"]}

    out = {
        "metric": "routine_transaction_volume_coverage",
        "unit_reported": args.unit,
        "misc_weight_factor": args.misc_weight,
        "sensitivity_misc_weight": sweep,
        "artifact_status": "synthetic_reference_distribution (not measured field data)",
        "minimum_core_node_count": len(core_ids),
        "extended_core_node_count": len(core_ids) + len(extended_node_ids),
        "extended_core_added": sorted(extended_node_ids),
        "line_weighted": line_res,
        "transaction_weighted": txn_res,
        # headline numbers (line-weighted, the natural "by volume / count" sense)
        "minimum_core_coverage_pct": line_res["min_core_pct"],
        "extended_core_coverage_pct": line_res["extended_pct"],
        "dataset_meta": meta,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    # Per-transaction breakdown CSV (committed) so a reviewer can audit exactly
    # which legs are scored in/out of core and extended core.
    def covered_ext_leg(leg):
        if leg in core_ids:
            return True
        tgt = absorption.get(leg)
        return tgt is not None and tgt in extended_node_ids
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["type", "journal", "weight", "n_legs",
                    "legs_in_min_core", "legs_in_extended", "legs"])
        for t in transactions:
            legs = t["legs"]
            w.writerow([
                t["type"], t.get("journal", ""), t["weight"], len(legs),
                sum(l in core_ids for l in legs),
                sum(covered_ext_leg(l) for l in legs),
                " | ".join(legs),
            ])

    mc = line_res["min_core_pct"]
    ec = line_res["extended_pct"]
    n_ext = len(core_ids) + len(extended_node_ids)
    print("=" * 70)
    print("Kontablo transaction-VOLUME coverage benchmark (line-weighted)")
    print("=" * 70)
    print(f"  Minimum core   (30 nodes): {mc:>5.1f}% of routine posting volume")
    print(f"  Extended core ({n_ext} nodes): {ec:>5.1f}% of routine posting volume")
    print(f"  (strict transaction-level: {txn_res['min_core_pct']:.1f}% / "
          f"{txn_res['extended_pct']:.1f}%)")
    print("-" * 70)
    print("  Honest two-number framing for the paper:")
    print(f"    \"The 30-account minimum core covers ~{mc:.0f}% of routine")
    print(f"     transaction volume; an extended core of {n_ext} accounts reaches")
    print(f"     ~{ec:.0f}%.\"  (model-based estimate; see transaction_frequency.yaml)")
    print("-" * 70)
    print("  Sensitivity (General-Journal tail weight x K -> minimum-core %):")
    print("    " + "   ".join(f"x{k}: {v['minimum_core_pct']:.1f}%"
                              for k, v in sweep.items()))
    print("-" * 70)
    print("  Largest residual labels still uncovered by the extended core:")
    for k, v in list(line_res["residual_volume_by_label"].items())[:8]:
        print(f"    {k:<34} {v:>7.1f} line-units")
    print("=" * 70)
    print(f"  Wrote {os.path.relpath(OUT_PATH, ROOT)}")


if __name__ == "__main__":
    main()
