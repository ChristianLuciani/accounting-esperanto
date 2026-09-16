#!/usr/bin/env python3
"""
Kontablo round-2 real-data validation -- ESEF ingestion (Tier A2, H1/H2).

Extraction half of research/real_data_validation_plan.md S10 "A2 -- ESEF /
ifrs-full": no new crosswalk is built here (level3_accounts.yaml already
carries an ifrs_tag field per node -- scoring against it is a separate,
later script, per S13's file layout). This script only DOWNLOADS a
mechanically-selected sample of real ESEF filings and EXTRACTS their tag
sets, producing the population H1/H2 will later be scored against.

WHY xBRL-JSON, NOT AN iXBRL PARSER
  filings.xbrl.org serves every successfully-processed filing as xBRL-JSON
  (the XBRL OIM JSON representation, documentType
  "https://xbrl.org/2021/xbrl-json") via the `json_url` field in its filing
  index. This lets the script parse facts with the stdlib `json` module only
  -- no Arelle (GPL) or any other iXBRL parser, avoiding the licensing
  hazard research/real_data_validation_plan.md S7 flags explicitly. Verified
  this session against real filings from FR, NL, IT, ES, PL, FI, AT, NO, GR:
  the JSON always has exactly two top-level keys, `documentInfo` (with a
  `namespaces` prefix->URI map) and `facts` (an id -> fact dict). A numeric
  fact carries a `unit` under `dimensions`; a non-numeric fact (text block,
  address, footnote `xbrl:note`) does not. Confirmed no top-level `labels`
  key in any sampled filing -- this corpus's xBRL-JSON never carries human-
  readable labels, so `label_en` is always emitted empty (never invented).

WHAT "EXTENSION" MEANS HERE (and what it does not)
  Company-specific extension concepts live in a namespace the issuer
  declares itself (observed pattern: the issuer's own domain, e.g.
  "https://www.linz-textil.at/xbrl/2022/", "http://citycon.com/2022-12-31").
  A genuine *country-shared* extension taxonomy (used by many unrelated
  filers) must NOT be counted in the H2 "company-specific" population. There
  is no registry of national ESEF extension taxonomies to consult
  mechanically, so this script uses an auditable, data-driven proxy instead:
  a namespace URI is classified "extension" only if, across every filing in
  THIS sample, it was declared by exactly one distinct entity_identifier;
  otherwise "other". Every row still carries the raw namespace_uri, so the
  call is independently re-checkable. Reconnaissance this session (7 filings
  across IT/ES/PL/FI/AT/NO/GR) found zero shared namespaces and zero
  "esef_cor"-prefixed or esma.europa.eu-hosted concepts at all -- see the
  script's own run for whether that held over the full n=100 sample.

MECHANICAL SAMPLE SELECTION (anti-cherry-picking -- fixed before looking at
extraction results, per project convention: see consolidation_v1's and
mass_consolidation_v2's own pre-stated, non-tuned selection rules):
  eligible = filings with error_count == 0, a non-null json_url, and a
  period_end in [WINDOW_MIN, WINDOW_MAX] (see the window comment below for
  why those specific bounds).
  Sort eligible filings by (country, period_end, fxo_id); iterate countries
  alphabetically, take up to 5 per country, stop the moment 100 filings are
  collected (the boundary country's contribution is truncated, not
  overshot, to land on exactly 100 when the pool supports it).

TEMPORAL SPLIT (pre-registered, S6 -- do not change post hoc):
  TRAIN = period_end <= 2022-12-31, HOLDOUT = period_end >= 2023-01-01.

filings.xbrl.org API QUIRKS discovered this session (see the reporting notes
this script prints, and the caller's final report):
  - Server-side filtering on `error_count` returns HTTP 500 for every
    operator/value tried (eq/le/lt, int or string). error_count==0 MUST be
    applied client-side after fetching full records; do not rely on a
    filter[error_count]=0 query parameter, it will 500.
  - filter[attr][op]=val (bracket-nested operator) is silently ignored down
    to a plain equality match; the operator this API actually honours is the
    complex `filter=[{"name":...,"op":...,"val":...}]` JSON list syntax.
  - The API's own `sha256` attribute on a filing record does NOT hash the
    `json_url` payload (verified: computing sha256 over a downloaded JSON
    file did not match the record's `sha256` field) -- it almost certainly
    hashes the original filed package/report, not the JSON transform this
    script consumes. `sha256_recorded` in the sample CSV is a verbatim
    passthrough of that API field for cross-reference only; it is NOT a
    checksum of the file this script downloaded. The trustworthy hash of
    what we actually fetched is the one `_snapshot.py` computes independently
    and stores in manifest.json.

Run:  venv/bin/python scripts/real_data/download_esef_sample.py
Outputs (committed):
  research/experiments/tag_resolution_v1/derived/esef_filings_sample.csv
  research/experiments/tag_resolution_v1/derived/esef_tags.csv
  research/experiments/tag_resolution_v1/derived/esef_sample_summary.csv
  research/experiments/tag_resolution_v1/manifest.json (via _snapshot.py)
Payloads (gitignored, not committed):
  research/real_data_snapshots/tag_resolution_v1/esef/...
"""

from __future__ import annotations

import csv
import json
import os
import sys
import urllib.parse
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _snapshot import fetch  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXPERIMENT = "tag_resolution_v1"
DERIVED_DIR = os.path.join(ROOT, "research", "experiments", EXPERIMENT, "derived")

API_BASE = "https://filings.xbrl.org/api/filings"
FILINGS_HOST = "https://filings.xbrl.org"
LICENSE_REGIME = "open_data"
LICENSE_NOTE = "issuer public disclosure; see filings.xbrl.org terms"

# Target period_end window for the eligible pool. Pre-stated, not tuned to
# the data: 2015-01-01 is a generous lower bound well before ESEF existed in
# any voluntary form, so it excludes nothing plausible; 2025-12-31 excludes
# data-entry errors observed live in the raw feed this session -- one real
# filing (259400ULGKWTD96ABA70-2031-03-01-ESEF-PL-0) carries
# period_end="2031-03-01", evidently a typo in the source instance (its own
# report_url names "2022-12-31"). Both bounds are applied server-side via
# the API's complex filter syntax AND re-checked client-side below.
WINDOW_MIN = "2015-01-01"
WINDOW_MAX = "2025-12-31"

# Pre-registered temporal split (research/real_data_validation_plan.md S6).
# Fixed -- do not change once sample collection has run.
TRAIN_CUTOFF = "2022-12-31"    # period_end <= this -> train
HOLDOUT_START = "2023-01-01"   # period_end >= this -> holdout

SAMPLE_TARGET = 100
PER_COUNTRY_CAP = 5
INDEX_PAGE_SIZE = 1000  # ~23s/page measured this session; larger pages (5000) scale worse, not better

SELECTION_RULE = (
    "eligible = filings with error_count==0, a non-null json_url, and "
    f"period_end in [{WINDOW_MIN}, {WINDOW_MAX}]; sort eligible filings by "
    "(country, period_end, fxo_id); iterate countries alphabetically, take "
    "up to 5 per country, stop the moment 100 filings are collected "
    "(truncate, never overshoot, the boundary country's contribution)."
)


def _log(msg: str) -> None:
    print(msg, file=sys.stderr)


# --------------------------------------------------------------------------
# Index crawl
# --------------------------------------------------------------------------

def _index_page_url(page_number: int) -> str:
    filt = json.dumps(
        [
            {"name": "period_end", "op": "ge", "val": WINDOW_MIN},
            {"name": "period_end", "op": "le", "val": WINDOW_MAX},
        ],
        separators=(",", ":"),
    )
    params = {
        "filter": filt,
        "sort": "fxo_id",
        "page[size]": INDEX_PAGE_SIZE,
        "page[number]": page_number,
    }
    return API_BASE + "?" + urllib.parse.urlencode(params)


def _entity_id_from_relationships(rel: dict) -> str:
    link = (rel or {}).get("entity", {}).get("links", {}).get("related", "") or ""
    return link.rsplit("/", 1)[-1] if link else ""


def crawl_index() -> list[dict]:
    """Page through the filings index (cached via _snapshot.py, one manifest
    entry per page) and return the flattened list of filing records."""
    by_fxo_id: dict[str, dict] = {}
    page = 1
    while True:
        url = _index_page_url(page)
        key = f"esef/index/page-{page:04d}.json"
        path = fetch(
            url, EXPERIMENT, key, LICENSE_REGIME,
            timeout=300, note=LICENSE_NOTE,
        )
        with open(path, encoding="utf-8") as fh:
            payload = json.load(fh)
        data = payload.get("data", [])
        if not data:
            break
        for item in data:
            attrs = item.get("attributes", {})
            fxo_id = attrs.get("fxo_id")
            if not fxo_id:
                continue
            by_fxo_id[fxo_id] = {
                "fxo_id": fxo_id,
                "country": attrs.get("country"),
                "period_end": attrs.get("period_end"),
                "error_count": attrs.get("error_count"),
                "json_url": attrs.get("json_url"),
                "sha256": attrs.get("sha256"),
                "entity_identifier": _entity_id_from_relationships(item.get("relationships")),
            }
        _log(f"  index page {page}: {len(data)} records (running total: {len(by_fxo_id)})")
        if len(data) < INDEX_PAGE_SIZE:
            break
        page += 1
    return list(by_fxo_id.values())


def build_eligible(records: list[dict]) -> list[dict]:
    eligible = []
    for r in records:
        if r.get("error_count") != 0:
            continue
        if not r.get("json_url"):
            continue
        period_end = r.get("period_end")
        if not period_end or not (WINDOW_MIN <= period_end <= WINDOW_MAX):
            continue
        eligible.append(r)
    return eligible


def select_sample(eligible: list[dict]) -> list[dict]:
    ordered = sorted(eligible, key=lambda r: (r["country"], r["period_end"], r["fxo_id"]))
    by_country: dict[str, list[dict]] = defaultdict(list)
    for r in ordered:
        by_country[r["country"]].append(r)

    sample: list[dict] = []
    for country in sorted(by_country.keys()):
        if len(sample) >= SAMPLE_TARGET:
            break
        remaining = SAMPLE_TARGET - len(sample)
        take = by_country[country][:PER_COUNTRY_CAP][:remaining]
        sample.extend(take)
    return sample


def window_for(period_end: str) -> str:
    if period_end <= TRAIN_CUTOFF:
        return "train"
    if period_end >= HOLDOUT_START:
        return "holdout"
    return "unassigned"  # unreachable given adjacent cutoffs; kept defensive


# --------------------------------------------------------------------------
# Filing download + parse
# --------------------------------------------------------------------------

def download_filing(record: dict) -> str:
    # json_url is a raw filesystem-derived path, NOT a URL: 154 of the 25,182
    # indexed paths contain literal spaces and 11 contain non-ASCII characters
    # (the filer named the report file in Czech/Polish/Croatian). urllib refuses
    # a URL with control characters, so the path MUST be percent-encoded before
    # it is a legal URL. No indexed path contains a literal '%', so encoding is
    # unconditional and cannot double-encode. The manifest records the encoded
    # URL, which is what was actually requested.
    url = FILINGS_HOST + urllib.parse.quote(record["json_url"], safe="/")
    key = f"esef/{record['fxo_id']}.json"
    return fetch(url, EXPERIMENT, key, LICENSE_REGIME, timeout=300, note=LICENSE_NOTE)


def classify_unit(unit: str) -> str:
    """Map an xBRL-JSON unit reference onto the datatype vocabulary the scorer reads.

    Addendum A.4 makes the MONETARY subset the primary population for H1, and
    requires the exclusion to be deterministic -- read from the filing's own
    declared type, with no per-tag discretion. EDGAR supplies a `datatype`
    column directly; xBRL-JSON does not, but it declares a `unit` per numeric
    fact, which carries the same information:

      iso4217:EUR              a currency amount            -> monetary
      iso4217:EUR/xbrli:shares a compound (per-share) unit  -> pershare
      xbrli:shares             a share count                -> shares
      xbrli:pure               a ratio/percentage           -> pure

    The returned strings are exactly the tokens resolve_real_facts.py's
    MONETARY_DATATYPES / NON_MONETARY_DATATYPES already recognize, so no
    scorer-side special-casing is needed for this corpus.
    """
    u = (unit or "").strip()
    if not u:
        return ""
    if "/" in u:  # compound unit: an amount PER something, not a ledger balance
        return "pershare"
    low = u.lower()
    if low.startswith("iso4217:"):
        return "monetary"
    if low.endswith(":shares"):
        return "shares"
    if low.endswith(":pure"):
        return "pure"
    return ""


def parse_filing(path: str) -> tuple[Counter, dict, dict, dict]:
    """Return (concept_counts, concept_prefix, concept_units, namespaces) for one filing.

    concept_counts: {(namespace_uri, local_name): n_qualifying_facts}
    concept_prefix: {(namespace_uri, local_name): prefix_as_declared}
    concept_units:  {(namespace_uri, local_name): Counter(datatype_token)}
    namespaces: prefix -> namespace_uri, exactly as documentInfo declares it
    """
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    namespaces = doc.get("documentInfo", {}).get("namespaces", {}) or {}
    facts = doc.get("facts", {}) or {}

    concept_counts: Counter = Counter()
    concept_prefix: dict = {}
    concept_units: dict = defaultdict(Counter)

    for fact in facts.values():
        dims = fact.get("dimensions") or {}
        concept = dims.get("concept")
        if not concept or ":" not in concept:
            continue
        if "unit" not in dims:
            continue  # non-numeric (text block, address, xbrl:note footnote, ...)
        if fact.get("value") is None:
            continue  # nil fact -- does not "carry" a value
        prefix, _, local = concept.partition(":")
        uri = namespaces.get(prefix, f"(undeclared-prefix:{prefix})")
        key = (uri, local)
        concept_counts[key] += 1
        concept_prefix.setdefault(key, prefix)
        concept_units[key][classify_unit(dims.get("unit"))] += 1

    return concept_counts, concept_prefix, concept_units, namespaces


def decide_datatype(counter: Counter) -> str:
    """Collapse a concept's observed unit kinds to ONE declared datatype.

    Deterministic and conservative: a concept whose qualifying facts all carry
    the same unit kind is reported as that kind; a concept reported under mixed
    units (or under a unit this script does not recognize) is reported as
    unknown -- which excludes it from the monetary primary population rather
    than guessing. Guessing here would silently move H1's denominator.
    """
    kinds = {kind for kind, n in counter.items() if n}
    return next(iter(kinds)) if len(kinds) == 1 else ""


def classify_namespace(uri: str, namespace_entities: dict) -> str:
    if not uri or uri.startswith("(undeclared-prefix:"):
        return "other"
    u = uri.lower()
    if "xbrl.ifrs.org/taxonomy" in u:
        return "ifrs_full"
    if "esma.europa.eu" in u:
        return "esef_core"
    entities_using = namespace_entities.get(uri, set())
    if len(entities_using) == 1:
        return "extension"
    return "other"


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> None:
    os.makedirs(DERIVED_DIR, exist_ok=True)

    _log("Crawling filings.xbrl.org index (period_end in target window)...")
    records = crawl_index()
    _log(f"  {len(records)} filings in the period_end window (server-side filtered)")

    eligible = build_eligible(records)
    eligible_pool_size = len(eligible)
    _log(f"Eligible pool (error_count==0, json_url present): {eligible_pool_size}")

    sample = select_sample(eligible)
    _log(f"Selected sample: {len(sample)} filings across "
         f"{len({r['country'] for r in sample})} countries")

    # Pass 1: download + parse every selected filing.
    filing_data = []  # list of (record, window, concept_counts, concept_prefix)
    namespace_entities: dict = defaultdict(set)  # namespace_uri -> set(entity_identifier)

    for i, record in enumerate(sample, 1):
        _log(f"  [{i}/{len(sample)}] {record['fxo_id']}")
        path = download_filing(record)
        concept_counts, concept_prefix, concept_units, namespaces = parse_filing(path)
        window = window_for(record["period_end"])
        filing_data.append((record, window, concept_counts, concept_prefix, concept_units))
        for uri in namespaces.values():
            namespace_entities[uri].add(record["entity_identifier"])

    # Pass 2: classify every (namespace_uri, local_name) seen anywhere in the
    # sample, using the cross-filing namespace-sharing signal for anything
    # that isn't ifrs_full/esef_core by URI pattern.
    all_concept_keys = set()
    for _, _, concept_counts, _, _ in filing_data:
        all_concept_keys.update(concept_counts.keys())
    classification = {key: classify_namespace(key[0], namespace_entities) for key in all_concept_keys}

    # Aggregate esef_tags.csv rows: (concept, window) -> stats.
    tag_facts: dict = defaultdict(lambda: defaultdict(int))          # key -> window -> n_facts
    tag_filings: dict = defaultdict(lambda: defaultdict(set))        # key -> window -> {fxo_id}
    tag_units: dict = defaultdict(lambda: defaultdict(Counter))      # key -> window -> Counter(datatype)
    tag_prefix: dict = {}

    # esef_filings_sample.csv rows.
    filings_rows = []

    for record, window, concept_counts, concept_prefix, concept_units in filing_data:
        n_facts = sum(concept_counts.values())
        n_concepts = len(concept_counts)
        n_ifrs_full = sum(1 for k in concept_counts if classification[k] == "ifrs_full")
        n_extension = sum(1 for k in concept_counts if classification[k] == "extension")

        filings_rows.append({
            "fxo_id": record["fxo_id"],
            "entity_identifier": record["entity_identifier"],
            "country": record["country"],
            "period_end": record["period_end"],
            "window": window,
            "json_url": record["json_url"],
            "sha256_recorded": record["sha256"] or "",
            "n_facts": n_facts,
            "n_concepts": n_concepts,
            "n_ifrs_full": n_ifrs_full,
            "n_extension": n_extension,
        })

        for key, cnt in concept_counts.items():
            tag_facts[key][window] += cnt
            tag_filings[key][window].add(record["fxo_id"])
            tag_units[key][window].update(concept_units[key])
            tag_prefix.setdefault(key, concept_prefix[key])

    # Build esef_tags.csv rows.
    tags_rows = []
    for key in all_concept_keys:
        uri, local = key
        prefix = tag_prefix.get(key, "")
        qname = f"{prefix}:{local}" if prefix else local
        tclass = classification[key]
        for window in ("train", "holdout"):
            n_facts = tag_facts[key].get(window, 0)
            if n_facts == 0:
                continue
            tags_rows.append({
                "concept_qname": qname,
                "namespace_uri": uri,
                "local_name": local,
                "taxonomy_class": tclass,
                "window": window,
                "n_facts": n_facts,
                "n_filings": len(tag_filings[key].get(window, ())),
                "datatype": decide_datatype(tag_units[key].get(window, Counter())),
                "label_en": "",  # confirmed absent from this corpus's xBRL-JSON (see module docstring)
            })

    # Build esef_sample_summary.csv rows.
    summary_rows = []
    for window in ("train", "holdout"):
        window_filing_rows = [r for r in filings_rows if r["window"] == window]
        window_tag_rows = [r for r in tags_rows if r["window"] == window]
        n_filings = len(window_filing_rows)
        n_countries = len({r["country"] for r in window_filing_rows})
        n_concepts = len(window_tag_rows)
        n_ifrs_full = sum(1 for r in window_tag_rows if r["taxonomy_class"] == "ifrs_full")
        n_extension_concepts = sum(1 for r in window_tag_rows if r["taxonomy_class"] == "extension")
        total_facts = sum(r["n_facts"] for r in window_tag_rows)
        extension_facts = sum(r["n_facts"] for r in window_tag_rows if r["taxonomy_class"] == "extension")
        pct_facts_extension = round(100.0 * extension_facts / total_facts, 4) if total_facts else 0.0

        summary_rows.append({
            "window": window,
            "n_filings": n_filings,
            "n_countries": n_countries,
            "n_concepts": n_concepts,
            "n_ifrs_full": n_ifrs_full,
            "n_extension": n_extension_concepts,
            "pct_facts_extension": pct_facts_extension,
            "eligible_pool_size": eligible_pool_size,
            "selection_rule": SELECTION_RULE,
        })

    # --- Write CSVs (deterministically sorted, lineterminator="\n") ---
    filings_rows.sort(key=lambda r: (r["country"], r["period_end"], r["fxo_id"]))
    tags_rows.sort(key=lambda r: (r["window"], r["taxonomy_class"], -r["n_facts"], r["concept_qname"]))
    # summary_rows already in fixed (train, holdout) order.

    _write_csv(
        os.path.join(DERIVED_DIR, "esef_filings_sample.csv"),
        filings_rows,
        ["fxo_id", "entity_identifier", "country", "period_end", "window", "json_url",
         "sha256_recorded", "n_facts", "n_concepts", "n_ifrs_full", "n_extension"],
    )
    _write_csv(
        os.path.join(DERIVED_DIR, "esef_tags.csv"),
        tags_rows,
        ["concept_qname", "namespace_uri", "local_name", "taxonomy_class", "window",
         "n_facts", "n_filings", "datatype", "label_en"],
    )
    _write_csv(
        os.path.join(DERIVED_DIR, "esef_sample_summary.csv"),
        summary_rows,
        ["window", "n_filings", "n_countries", "n_concepts", "n_ifrs_full", "n_extension",
         "pct_facts_extension", "eligible_pool_size", "selection_rule"],
    )

    _log("Done.")
    _log(f"  eligible_pool_size = {eligible_pool_size}")
    _log(f"  sample = {len(sample)} filings, "
         f"train={sum(1 for r in filings_rows if r['window']=='train')}, "
         f"holdout={sum(1 for r in filings_rows if r['window']=='holdout')}")


def _write_csv(path: str, rows: list[dict], fieldnames: list[str]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow(row)


if __name__ == "__main__":
    main()
