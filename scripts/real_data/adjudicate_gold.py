#!/usr/bin/env python3
"""
Kontablo — inter-annotator agreement and gold adjudication (round 2, plan §6).

WHY THIS EXISTS
  Plan §6 requires that the gold standard be built by INDEPENDENT double
  labeling, that inter-annotator agreement be reported as Cohen's kappa, and
  that disagreements be adjudicated by a third pass BEFORE scoring. A gold
  standard produced by a single pass would silently inherit that pass's biases
  and would make the accuracy number unfalsifiable.

  This script computes the agreement statistics, emits the disagreement set for
  adjudication, and assembles the final gold file once adjudications exist.

WHAT KAPPA IS BEING REPORTED ON
  Two granularities, because they answer different questions:
    exact   the full label space (each node id, each AGGREGATE:<lens>, and the
            empty out-of-scope label are distinct categories). This is the
            strict number.
    class   the coarse three-way class (leaf / aggregate / out_of_scope). Higher
            by construction; it says whether the labelers agreed about what KIND
            of thing a tag is, even when they disagreed on which node.
  Both are reported. Quoting only the coarse one would overstate agreement.

INDEPENDENCE CAVEAT — STATED, NOT HIDDEN
  Both labeling passes were produced by the same model family under different
  instructed reasoning orders (tag-first vs node-first, the latter defaulting to
  no-match). That is weaker independence than two unaffiliated human CPAs would
  provide: correlated errors are possible and kappa will overstate true
  independence. The plan permits LLM labelers (§6.2) and this limitation must be
  carried into any public wording of the resulting accuracy figure. It is a
  known bound on the strength of the evidence, not a defect to paper over.

OUTPUT
  research/experiments/<experiment>/gold/agreement.json     kappa + confusion
  research/experiments/<experiment>/gold/disagreements.csv  for the third pass
  research/experiments/<experiment>/gold/gold_labels_edgar.csv  final gold set

Run:  venv/bin/python scripts/real_data/adjudicate_gold.py
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from scripts.real_data.resolve_real_facts import gold_class  # noqa: E402


def _read(path: str) -> dict:
    with open(path, encoding="utf-8", newline="") as fh:
        return {r["code"]: r for r in csv.DictReader(fh)}


def cohens_kappa(pairs: list[tuple[str, str]]) -> dict:
    """Cohen's kappa for two raters over a shared, unordered category set."""
    n = len(pairs)
    if not n:
        return {"n": 0, "observed_agreement": 0.0, "expected_agreement": 0.0, "kappa": 0.0}
    observed = sum(1 for a, b in pairs if a == b) / n

    categories = {c for pair in pairs for c in pair}
    count_a = {c: sum(1 for a, _ in pairs if a == c) for c in categories}
    count_b = {c: sum(1 for _, b in pairs if b == c) for c in categories}
    expected = sum((count_a[c] / n) * (count_b[c] / n) for c in categories)

    kappa = 1.0 if expected == 1.0 else (observed - expected) / (1 - expected)
    return {
        "n": n,
        "observed_agreement": round(observed, 4),
        "expected_agreement": round(expected, 4),
        "kappa": round(kappa, 4),
        "n_categories": len(categories),
    }


def interpret(kappa: float) -> str:
    """Landis & Koch (1977) benchmark bands, named so the number is not free-floating."""
    for threshold, label in ((0.81, "almost perfect"), (0.61, "substantial"),
                             (0.41, "moderate"), (0.21, "fair"), (0.0, "slight")):
        if kappa >= threshold:
            return label
    return "poor (worse than chance)"


def run(experiment: str) -> dict | None:
    gold_dir = os.path.join(ROOT, "research/experiments", experiment, "gold")
    path_a = os.path.join(gold_dir, "labels_A.csv")
    path_b = os.path.join(gold_dir, "labels_B.csv")
    if not (os.path.exists(path_a) and os.path.exists(path_b)):
        print(f"{experiment}: need both labels_A.csv and labels_B.csv -- skipped")
        return None

    a, b = _read(path_a), _read(path_b)
    shared = sorted(set(a) & set(b))
    if len(shared) != len(a) or len(shared) != len(b):
        print(f"  [warn] sheets differ: A={len(a)} B={len(b)} shared={len(shared)}")

    exact_pairs, class_pairs = [], []
    disagreements = []
    for code in shared:
        la = (a[code]["gold_kontablo_id"] or "").strip()
        lb = (b[code]["gold_kontablo_id"] or "").strip()
        exact_pairs.append((la or "(out_of_scope)", lb or "(out_of_scope)"))
        class_pairs.append((gold_class(la), gold_class(lb)))
        if la != lb:
            disagreements.append({
                "taxonomy": a[code].get("taxonomy", "us-gaap"),
                "code": code,
                "name": a[code].get("name", ""),
                "stratum": a[code].get("stratum", ""),
                "label_A": la,
                "label_B": lb,
                "note_A": a[code].get("labeler_note", ""),
                "note_B": b[code].get("labeler_note", ""),
                "adjudicated": "",
                "adjudication_note": "",
            })

    exact = cohens_kappa(exact_pairs)
    coarse = cohens_kappa(class_pairs)
    exact["interpretation"] = interpret(exact["kappa"])
    coarse["interpretation"] = interpret(coarse["kappa"])

    agreement = {
        "experiment": experiment,
        "n_items": len(shared),
        "n_disagreements": len(disagreements),
        "kappa_exact": exact,
        "kappa_class": coarse,
        "independence_caveat": (
            "Both passes are the same model family under different instructed "
            "reasoning orders (tag-first vs node-first). Weaker independence than "
            "two unaffiliated human CPAs; correlated errors are possible and kappa "
            "overstates true independence. Carry this caveat into any public wording."
        ),
        "class_confusion": {},
    }
    for ca, cb in class_pairs:
        key = f"{ca}|{cb}"
        agreement["class_confusion"][key] = agreement["class_confusion"].get(key, 0) + 1

    with open(os.path.join(gold_dir, "agreement.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(agreement, fh, indent=2, sort_keys=True)
        fh.write("\n")

    dis_path = os.path.join(gold_dir, "disagreements.csv")
    existing = _read(dis_path) if os.path.exists(dis_path) else {}
    for row in disagreements:  # preserve adjudications already recorded
        prior = existing.get(row["code"])
        if prior:
            row["adjudicated"] = prior.get("adjudicated", "")
            row["adjudication_note"] = prior.get("adjudication_note", "")
    fields = ["taxonomy", "code", "name", "stratum", "label_A", "label_B",
              "note_A", "note_B", "adjudicated", "adjudication_note"]
    with open(dis_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in sorted(disagreements, key=lambda r: r["code"]):
            writer.writerow(row)

    # Assemble the gold set: agreements pass straight through; disagreements
    # require an explicit adjudication. An unadjudicated disagreement is DROPPED
    # rather than resolved by coin-flip or by preferring one labeler -- scoring
    # against a half-arbitrated gold set would be worse than scoring against a
    # smaller, fully arbitrated one.
    resolved, pending = [], 0
    adjudications = _read(dis_path)
    for code in shared:
        la = (a[code]["gold_kontablo_id"] or "").strip()
        lb = (b[code]["gold_kontablo_id"] or "").strip()
        if la == lb:
            final, basis = la, "agreed"
        else:
            adj = adjudications.get(code, {})
            # An adjudicated label may legitimately BE the empty string (the
            # adjudicator ruled the tag out of scope), so emptiness cannot mark
            # "not yet done". The non-empty note is the completion signal.
            if not (adj.get("adjudication_note") or "").strip():
                pending += 1
                continue
            final, basis = (adj.get("adjudicated") or "").strip(), "adjudicated"
        resolved.append({
            "taxonomy": a[code].get("taxonomy", "us-gaap"),
            "code": code,
            "name": a[code].get("name", ""),
            "stratum": a[code].get("stratum", ""),
            "gold_kontablo_id": final,
            "basis": basis,
        })

    gold_path = os.path.join(gold_dir, "gold_labels_edgar.csv")
    with open(gold_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["taxonomy", "code", "name", "stratum", "gold_kontablo_id", "basis"],
            lineterminator="\n",
        )
        writer.writeheader()
        for row in sorted(resolved, key=lambda r: r["code"]):
            writer.writerow(row)

    agreement["n_gold_final"] = len(resolved)
    agreement["n_pending_adjudication"] = pending

    print("=" * 74)
    print(f"Inter-annotator agreement -- {experiment}")
    print("=" * 74)
    print(f"  items double-labeled : {len(shared)}")
    print(f"  disagreements        : {len(disagreements)}")
    print(f"  kappa (exact label)  : {exact['kappa']:.3f}  ({exact['interpretation']}, "
          f"{exact['n_categories']} categories)")
    print(f"  kappa (3-way class)  : {coarse['kappa']:.3f}  ({coarse['interpretation']})")
    print(f"  raw agreement        : exact {100*exact['observed_agreement']:.1f}%   "
          f"class {100*coarse['observed_agreement']:.1f}%")
    print(f"  gold rows finalized  : {len(resolved)}   pending adjudication: {pending}")
    if pending:
        print(f"  -> fill 'adjudicated' + 'adjudication_note' in "
              f"{os.path.relpath(dis_path, ROOT)} and re-run")
    return agreement


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", action="append")
    args = parser.parse_args()
    for experiment in args.experiment or ["tag_resolution_v1", "public_sector_gfs_v1"]:
        run(experiment)


if __name__ == "__main__":
    main()
