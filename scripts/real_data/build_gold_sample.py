#!/usr/bin/env python3
"""
Kontablo — build the stratified gold-standard sampling frame (round 2).

WHY THIS EXISTS
  Real data gives COVERAGE for free (did the resolver return a node) but never
  CORRECTNESS ("resolved" is not "resolved right"). Plan §6 therefore requires a
  stratified random sample, independently double-labeled, before any accuracy
  claim can be made. This script produces that sample deterministically, so the
  frame itself can never be accused of being drawn to flatter the result.

WHY THE SAMPLE IS DRAWN FROM THE WHOLE POPULATION, NOT ONLY RESOLVED FACTS
  Plan §6.1 says "stratified random sample of resolved facts". Sampling only
  resolved facts measures PRECISION and is structurally blind to misses: a
  resolver that escalates almost everything would score perfectly. This script
  samples the whole holdout population instead, so the gold set can score all
  four outcomes (correct / wrong node / missed / false positive). That is a
  deliberate strengthening of the pre-registered protocol, recorded here rather
  than applied silently; it can only lower the measured accuracy, never raise it.

STRATIFICATION
  Frequency bands are assigned by CUMULATIVE fact share, not by rank, because
  real tag distributions are extremely long-tailed: a handful of tags carry half
  the facts. Bands:
    head  tags composing the first 50% of facts
    mid   the next 40%
    tail  the final 10%
  Crossed with the holdout stratum that actually matters for circularity:
    seen_in_train / unseen_in_train
  Unseen-in-train tags are deliberately OVERSAMPLED. They are a small share of
  facts but they are the only genuinely non-circular evidence in the corpus, and
  a proportional sample would leave too few of them to say anything.

DETERMINISM
  Selection is a seeded shuffle over a canonically sorted list, so the same
  inputs always yield the same sample. The seed is committed. No wall-clock, no
  set iteration order, no dict ordering dependence.

OUTPUT
  research/experiments/<experiment>/gold/sampling_frame.csv
      the drawn sample, with stratum labels and the resolver's answer WITHHELD
  research/experiments/<experiment>/gold/labeling_task_<n>.csv
      blind labeling sheets (no resolver answer, no other labeler's answer)

Run:  venv/bin/python scripts/real_data/build_gold_sample.py
"""

from __future__ import annotations

import argparse
import csv
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from scripts.real_data.resolve_real_facts import load_inventory  # noqa: E402

SEED = 20260730  # committed; changing it invalidates every accuracy number
TARGET_N = 320   # plan §6.1 asks for n>=300 per hypothesis
UNSEEN_FLOOR = 60  # minimum unseen-in-train tags, oversampled on purpose


def assign_bands(rows: list[dict]) -> None:
    """Tag each row with a cumulative-fact-share frequency band."""
    ordered = sorted(rows, key=lambda r: (-r["n_facts"], r["code"]))
    total = sum(r["n_facts"] for r in ordered) or 1
    running = 0
    for row in ordered:
        share = running / total
        row["band"] = "head" if share < 0.50 else ("mid" if share < 0.90 else "tail")
        running += row["n_facts"]


def draw(experiment: str, target_n: int) -> list[dict]:
    rows = [
        r for r in load_inventory(experiment)
        if r["window"] == "holdout"
        and r["taxonomy_class"] == "standard"
        and r["measure_class"] == "monetary"
    ]
    if not rows:
        return []

    train_codes = {
        (r["taxonomy"], r["code"])
        for r in load_inventory(experiment)
        if r["window"] == "train"
    }
    for row in rows:
        row["seen_in_train"] = (row["taxonomy"], row["code"]) in train_codes
    assign_bands(rows)

    strata: dict[tuple, list[dict]] = {}
    for row in rows:
        key = (row["source"], row["band"], "seen" if row["seen_in_train"] else "unseen")
        strata.setdefault(key, []).append(row)

    rng = random.Random(SEED)
    unseen_keys = [k for k in strata if k[2] == "unseen"]
    seen_keys = [k for k in strata if k[2] == "seen"]

    picked: list[dict] = []

    # Oversample the unseen stratum first -- it is the scientifically load-bearing
    # one and is too small to survive proportional allocation.
    unseen_pool = sorted(
        (r for k in unseen_keys for r in strata[k]),
        key=lambda r: (r["source"], r["band"], r["code"]),
    )
    rng.shuffle(unseen_pool)
    picked.extend(unseen_pool[: min(UNSEEN_FLOOR, len(unseen_pool))])

    # Allocate the remainder across seen strata proportionally to FACT share, so
    # the weighted accuracy estimate is not dominated by rare tags.
    remaining = max(target_n - len(picked), 0)
    seen_total = sum(sum(r["n_facts"] for r in strata[k]) for k in seen_keys) or 1
    for key in sorted(seen_keys):
        pool = sorted(strata[key], key=lambda r: (r["source"], r["band"], r["code"]))
        rng.shuffle(pool)
        share = sum(r["n_facts"] for r in pool) / seen_total
        quota = min(len(pool), max(5, round(remaining * share)))
        picked.extend(pool[:quota])

    # Proportional allocation can undershoot when a stratum's pool is smaller
    # than its fact-share quota -- the head band is only ~100 tags because a
    # handful of tags carry half the facts. Top up deterministically from the
    # unpicked remainder so the sample still clears the plan's n>=300 floor.
    if len(picked) < target_n:
        chosen = {(r["taxonomy"], r["code"]) for r in picked}
        leftover = sorted(
            (r for r in rows if (r["taxonomy"], r["code"]) not in chosen),
            key=lambda r: (r["source"], r["band"], r["code"]),
        )
        rng.shuffle(leftover)
        picked.extend(leftover[: target_n - len(picked)])

    for row in picked:
        row["stratum"] = f"{row['band']}/{'seen' if row['seen_in_train'] else 'unseen'}"
    return sorted(picked, key=lambda r: (r["source"], r["stratum"], -r["n_facts"], r["code"]))


FRAME_FIELDS = [
    "source", "taxonomy", "code", "name", "measure_class",
    "n_facts", "n_filings", "band", "seen_in_train", "stratum",
]


def write_frame(experiment: str, sample: list[dict], n_labelers: int) -> None:
    gold_dir = os.path.join(ROOT, "research/experiments", experiment, "gold")
    os.makedirs(gold_dir, exist_ok=True)

    frame_path = os.path.join(gold_dir, "sampling_frame.csv")
    with open(frame_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FRAME_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in sample:
            writer.writerow({k: row.get(k, "") for k in FRAME_FIELDS})

    # Blind labeling sheets: the resolver's answer is deliberately absent, and
    # each labeler gets an identical sheet so their answers stay independent
    # (plan §6.2). Row order is identical across sheets to make adjudication a
    # straight join rather than a fuzzy match.
    for n in range(1, n_labelers + 1):
        path = os.path.join(gold_dir, f"labeling_task_{n}.csv")
        with open(path, "w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh, lineterminator="\n")
            writer.writerow(["taxonomy", "code", "name", "stratum",
                             "gold_kontablo_id", "labeler_note"])
            for row in sample:
                writer.writerow([row["taxonomy"], row["code"], row["name"],
                                 row["stratum"], "", ""])
    print(f"  wrote {os.path.relpath(frame_path, ROOT)} and {n_labelers} blind sheets")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", action="append")
    parser.add_argument("--target-n", type=int, default=TARGET_N)
    parser.add_argument("--labelers", type=int, default=2)
    args = parser.parse_args()

    for experiment in args.experiment or ["tag_resolution_v1", "public_sector_gfs_v1"]:
        sample = draw(experiment, args.target_n)
        if not sample:
            print(f"{experiment}: no holdout monetary inventory -- skipped")
            continue
        print("=" * 74)
        print(f"Gold sampling frame -- {experiment}  (seed={SEED})")
        print("=" * 74)
        counts: dict[str, int] = {}
        facts: dict[str, int] = {}
        for row in sample:
            counts[row["stratum"]] = counts.get(row["stratum"], 0) + 1
            facts[row["stratum"]] = facts.get(row["stratum"], 0) + row["n_facts"]
        for stratum in sorted(counts):
            print(f"  {stratum:<14} n={counts[stratum]:>4}   facts={facts[stratum]:>8}")
        print(f"  TOTAL n={len(sample)}")
        write_frame(experiment, sample, args.labelers)


if __name__ == "__main__":
    main()
