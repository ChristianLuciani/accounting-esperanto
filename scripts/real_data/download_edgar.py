#!/usr/bin/env python3
"""
Kontablo round-2 real-data validation -- EDGAR ingestion (Tier A1).

WHY THIS EXISTS
  research/real_data_validation_plan.md Tier A1 (H1, H2): the synthetic 97.3%
  deterministic-resolution figure in mass_consolidation_v2.py is partly
  circular -- its Tier-1 synthetic entities are derived from the same
  local_codes table the resolver looks them up in. This script produces the
  first non-circular ingredient: a REAL tag-frequency distribution drawn from
  SEC EDGAR's "Financial Statement Data Sets", independent of anything
  Kontablo generated. A later script builds core/schemas/us_gaap_tags.yaml
  from the TRAIN window only and scores it against HOLDOUT -- this script
  does not do any resolution or scoring itself.

WHAT IT MEASURES (and what it deliberately does NOT)
  Presentation FREQUENCY: how often each XBRL tag appears as a face-statement
  line item (a row in pre.txt), per the plan's own methodology note (S9).
  This script NEVER reads or sums num.txt (the monetary-value file). Summing
  XBRL facts is a known correctness hazard -- num.txt mixes subtotals and
  their components on the same statement (e.g. a "Total assets" fact and the
  line items that roll up into it both appear as separate facts), so a naive
  sum double-counts. Counting presentation frequency instead of value sidesteps
  the hazard entirely: we ask "how often does a filer use this tag on a face
  statement", never "what does this tag sum to".

SOURCE
  https://www.sec.gov/files/dera/data/financial-statement-data-sets/<q>.zip
  Each quarterly ZIP (~66 MB) contains sub.txt, num.txt, pre.txt, tag.txt
  (tab-separated, latin-1). We read pre.txt, tag.txt, sub.txt directly out of
  the ZIP with zipfile + pandas -- num.txt (~1 GB extracted, the biggest file
  by far) is never opened, deliberately, both because we do not need it (see
  above) and to avoid the disk/memory cost of extracting it.

WINDOWS (pre-registered temporal holdout -- research/real_data_validation_plan.md
S6 point 4: "train/test split is temporal, not random, to avoid the same
leakage risk as the crosswalk itself". Do not change these without a dated,
visible addendum to the plan.)
  TRAIN:   2024q1 2024q2 2024q3 2024q4 2025q1 2025q2
  HOLDOUT: 2025q3 2025q4 2026q1

OUTPUTS (committed; small derived artifacts, never the raw payload)
  research/experiments/tag_resolution_v1/derived/edgar_tags_train.csv.gz
  research/experiments/tag_resolution_v1/derived/edgar_tags_holdout.csv.gz
  research/experiments/tag_resolution_v1/derived/edgar_window_summary.csv
  research/experiments/tag_resolution_v1/manifest.json   (written by _snapshot)

Raw ZIPs land in the gitignored research/real_data_snapshots/tag_resolution_v1/
tree, content-addressed and manifested by scripts/real_data/_snapshot.py --
see that module's docstring for the reproducibility model (public_domain
license regime: EDGAR is a U.S. government work, so the manifest records the
hash and the payload may also be vendored/deposited per the plan S7, but this
script itself never copies raw payloads into research/experiments/).

Run:  venv/bin/python scripts/real_data/download_edgar.py
      KONTABLO_REAL_DATA_OFFLINE=1 venv/bin/python scripts/real_data/download_edgar.py
      venv/bin/python scripts/real_data/download_edgar.py --smoke-test   # 1+1 quarters, fast pipeline check
"""

from __future__ import annotations

import argparse
import csv as csv_module
import os
import sys
import zipfile
from collections import Counter

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts.real_data._snapshot import fetch  # noqa: E402

EXPERIMENT = "tag_resolution_v1"
BASE_URL = "https://www.sec.gov/files/dera/data/financial-statement-data-sets"
DERIVED_DIR = os.path.join(ROOT, "research", "experiments", EXPERIMENT, "derived")

# Pre-registered temporal holdout -- research/real_data_validation_plan.md S6.
# Do not change without a dated, visible addendum to the plan.
TRAIN_QUARTERS = ["2024q1", "2024q2", "2024q3", "2024q4", "2025q1", "2025q2"]
HOLDOUT_QUARTERS = ["2025q3", "2025q4", "2026q1"]

# Face statements only; UN (notes/unclassifiable) and anything else is excluded.
FACE_STATEMENTS = {"BS", "IS", "CF", "EQ", "CI"}
# Forms this analysis is scoped to (annual/quarterly US filers + foreign private
# issuers filing IFRS or Canadian MJDS in Inline XBRL).
KEEP_FORMS = {"10-K", "10-Q", "20-F", "40-F"}

# Columns this script depends on from each file. EDGAR's column set has drifted
# slightly release to release (e.g. a "prevrpt" or "srcvalue"-style flag added
# in later years); we only require what we actually use, and default anything
# genuinely missing to NA with a printed warning rather than assuming a fixed
# schema across 2024-2026 vintages.
PRE_NEEDED = ["adsh", "report", "line", "stmt", "inpth", "rfile", "tag", "version", "plabel", "negating"]
TAG_NEEDED = ["tag", "version", "custom", "abstract", "datatype", "crdr", "tlabel", "doc"]
SUB_NEEDED = ["adsh", "form"]

DERIVED_TAG_COLUMNS = [
    "tag",
    "version",
    "custom",
    "abstract",
    "crdr",
    "datatype",
    "tlabel",
    "stmt_primary",
    "n_facts",
    "n_filings",
    "plabel_modal",
]


def _read_member(zf: zipfile.ZipFile, member: str, needed: list[str], label: str) -> pd.DataFrame:
    """Read one tab-separated member straight out of the ZIP, no extraction.

    latin-1 because EDGAR bulk files are not clean UTF-8 (filer-supplied free
    text -- company names, tag labels -- routinely contains Windows-1252/
    latin-1 bytes). QUOTE_NONE because plabel/tlabel/doc free text can contain
    literal double-quote characters that would otherwise be mis-parsed as CSV
    quoting and corrupt row boundaries; EDGAR's own bulk files are plain TSV
    with no quoting convention.
    """
    with zf.open(member) as fh:
        df = pd.read_csv(
            fh,
            sep="\t",
            dtype=str,
            encoding="latin-1",
            on_bad_lines="warn",
            quoting=csv_module.QUOTE_NONE,
        )
    missing = [c for c in needed if c not in df.columns]
    for c in missing:
        df[c] = pd.NA
    if missing:
        print(f"  [warn] {label}: columns missing from this vintage, defaulted to NA: {missing}")
    return df


def _modal(series: pd.Series) -> str:
    """Deterministic mode: most frequent non-empty value, ties broken alphabetically.

    Using Counter.most_common() alone breaks ties by first-seen order, which
    would make the derived CSV depend on row-concatenation order rather than
    being a pure function of the (tag, version) group's content. Alphabetical
    tie-break makes re-running the script byte-identical regardless of any
    incidental ordering upstream.
    """
    counts = Counter(v for v in series if isinstance(v, str) and v != "")
    if not counts:
        return ""
    top = max(counts.values())
    return sorted(k for k, v in counts.items() if v == top)[0]


def _first_valid(series: pd.Series) -> str:
    for v in series:
        if isinstance(v, str) and v != "":
            return v
    return ""


def download_quarter(q: str) -> str:
    url = f"{BASE_URL}/{q}.zip"
    return fetch(
        url,
        experiment=EXPERIMENT,
        key=f"edgar/{q}.zip",
        license_regime="public_domain",
        timeout=600,
        retries=3,
        note="SEC EDGAR Financial Statement Data Sets, quarterly bulk export",
    )


def load_quarter(zip_path: str, q: str) -> tuple[pd.DataFrame, Counter]:
    """Return (filtered face-statement facts, form-mix counts) for one quarter."""
    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
        for member in ("pre.txt", "tag.txt", "sub.txt"):
            if member not in names:
                raise RuntimeError(f"{q}: {member} missing from {zip_path}")
        pre = _read_member(zf, "pre.txt", PRE_NEEDED, f"{q}/pre.txt")
        tag = _read_member(zf, "tag.txt", TAG_NEEDED, f"{q}/tag.txt")
        sub = _read_member(zf, "sub.txt", SUB_NEEDED, f"{q}/sub.txt")

    pre = pre[pre["stmt"].isin(FACE_STATEMENTS)]
    pre = pre[pre["inpth"] != "1"]  # drop parentheticals

    sub_keep = sub[sub["form"].isin(KEEP_FORMS)][["adsh", "form"]].drop_duplicates(subset=["adsh"])
    form_counts = Counter(sub_keep["form"])
    pre = pre.merge(sub_keep, on="adsh", how="inner")

    tag_meta = tag[TAG_NEEDED].drop_duplicates(subset=["tag", "version"])
    pre = pre.merge(tag_meta, on=["tag", "version"], how="left", suffixes=("", "_tagmeta"))

    pre = pre[pre["abstract"] != "1"]  # headers carry no value; not a real fact

    pre = pre.copy()
    pre["quarter"] = q
    return pre, form_counts


def aggregate_window(frames: list[pd.DataFrame]) -> pd.DataFrame:
    df = pd.concat(frames, ignore_index=True)
    df = df.sort_values(["tag", "version"], kind="mergesort")  # stable -> deterministic re-runs

    counts = df.groupby(["tag", "version"], as_index=False).agg(
        n_facts=("adsh", "size"),
        n_filings=("adsh", "nunique"),
    )
    meta = df.groupby(["tag", "version"], as_index=False).agg(
        custom=("custom", _first_valid),
        abstract=("abstract", _first_valid),
        crdr=("crdr", _first_valid),
        datatype=("datatype", _first_valid),
        tlabel=("tlabel", _first_valid),
    )
    stmt_primary = df.groupby(["tag", "version"])["stmt"].apply(_modal).reset_index(name="stmt_primary")
    plabel_modal = df.groupby(["tag", "version"])["plabel"].apply(_modal).reset_index(name="plabel_modal")

    out = counts.merge(meta, on=["tag", "version"]).merge(stmt_primary, on=["tag", "version"]).merge(
        plabel_modal, on=["tag", "version"]
    )
    out = out.sort_values(["tag", "version"], kind="mergesort").reset_index(drop=True)
    return out[DERIVED_TAG_COLUMNS]


def build_window(quarters: list[str], label: str) -> tuple[pd.DataFrame, dict, pd.DataFrame]:
    frames = []
    form_totals: Counter = Counter()
    for q in quarters:
        print(f"  fetching {q} ...")
        zip_path = download_quarter(q)
        pre, form_counts = load_quarter(zip_path, q)
        print(f"    {q}: {len(pre):,} face-statement facts, {pre['adsh'].nunique():,} filings")
        frames.append(pre)
        form_totals.update(form_counts)

    all_facts = pd.concat(frames, ignore_index=True)
    tags_df = aggregate_window(frames)

    n_facts = len(all_facts)
    n_custom_facts = int((all_facts["custom"] == "1").sum())
    summary = {
        "window": label,
        "n_quarters": len(quarters),
        "n_filings": int(all_facts["adsh"].nunique()),
        "n_facts": n_facts,
        "n_distinct_tags": len(tags_df),  # distinct (tag, version) pairs
        "n_distinct_base_tags": int(all_facts["tag"].nunique()),  # ignoring version
        "n_standard_tags": int((tags_df["custom"] == "0").sum()),
        "n_custom_tags": int((tags_df["custom"] == "1").sum()),
        "pct_facts_custom": round(100.0 * n_custom_facts / n_facts, 4) if n_facts else 0.0,
    }
    for form in sorted(KEEP_FORMS):
        summary[f"form_{form.replace('-', '')}"] = int(form_totals.get(form, 0))

    return tags_df, summary, all_facts


def _write_csv(df: pd.DataFrame, path: str) -> None:
    """Write a derived CSV, gzipping when the path says so.

    The tag inventories are ~110 MB raw, dominated by the 570k-row extension
    tail. They are committed (scoring must run offline from committed
    derivatives, per plan §7) so they are gzipped to ~11 MB. mtime is pinned to
    0 so re-running the deterministic pipeline reproduces byte-identical gzip
    output instead of a fresh blob on every run.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if path.endswith(".gz"):
        df.to_csv(path, index=False, lineterminator="\n",
                  compression={"method": "gzip", "mtime": 0})
    else:
        df.to_csv(path, index=False, lineterminator="\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help=(
            "Restrict each window to its first quarter only, for a fast pipeline "
            "check. Never use this to regenerate the committed derived CSVs -- "
            "the pre-registered windows require the full 6+3 quarter run."
        ),
    )
    args = parser.parse_args(argv)

    train_quarters = TRAIN_QUARTERS[:1] if args.smoke_test else TRAIN_QUARTERS
    holdout_quarters = HOLDOUT_QUARTERS[:1] if args.smoke_test else HOLDOUT_QUARTERS

    print("Kontablo round-2 real-data validation -- EDGAR ingestion (Tier A1)")
    print(f"TRAIN window:   {', '.join(train_quarters)}")
    print(f"HOLDOUT window: {', '.join(holdout_quarters)}")
    if args.smoke_test:
        print("(--smoke-test: windows truncated to 1 quarter each -- do not treat as final)")
    print()

    print("Building TRAIN window ...")
    train_tags, train_summary, train_facts = build_window(train_quarters, "train")
    print("Building HOLDOUT window ...")
    holdout_tags, holdout_summary, holdout_facts = build_window(holdout_quarters, "holdout")

    _write_csv(train_tags, os.path.join(DERIVED_DIR, "edgar_tags_train.csv.gz"))
    _write_csv(holdout_tags, os.path.join(DERIVED_DIR, "edgar_tags_holdout.csv.gz"))

    summary_df = pd.DataFrame([train_summary, holdout_summary])
    _write_csv(summary_df, os.path.join(DERIVED_DIR, "edgar_window_summary.csv"))

    # Cross-window diagnostic (H1/H2's non-circular stratum): tags present in
    # HOLDOUT that never appeared in TRAIN. Reported two ways -- by exact
    # (tag, version) pair (inflated by routine annual taxonomy version bumps,
    # e.g. us-gaap/2024 -> us-gaap/2025 relabels every recurring tag) and by
    # base tag name ignoring version (the concept-level novelty that actually
    # matters for whether a crosswalk built on TRAIN generalizes).
    train_pairs = set(zip(train_tags["tag"], train_tags["version"]))
    holdout_pairs = set(zip(holdout_tags["tag"], holdout_tags["version"]))
    new_pairs = holdout_pairs - train_pairs

    train_base = set(train_tags["tag"])
    holdout_base = set(holdout_tags["tag"])
    new_base = holdout_base - train_base

    print()
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    for summary in (train_summary, holdout_summary):
        print(f"\n[{summary['window'].upper()}]")
        for k, v in summary.items():
            if k == "window":
                continue
            print(f"  {k}: {v}")
    print("\n[CROSS-WINDOW]")
    print(f"  holdout (tag,version) pairs not seen in train: {len(new_pairs)} / {len(holdout_pairs)}")
    print(f"  holdout base tags (version-agnostic) not seen in train: {len(new_base)} / {len(holdout_base)}")
    print()
    print(f"Derived CSVs written to {DERIVED_DIR}")
    print(f"  edgar_tags_train.csv.gz : {len(train_tags):,} rows")
    print(f"  edgar_tags_holdout.csv.gz: {len(holdout_tags):,} rows")
    print(f"  edgar_window_summary.csv: {len(summary_df):,} rows")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
