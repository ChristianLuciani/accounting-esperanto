#!/usr/bin/env python3
"""
Kontablo — Round-2 real-data resolution benchmark (reproducible).

WHY THIS EXISTS
  The published 97.3% figure (scripts/mass_consolidation_v2.py) is measured on
  SYNTHETIC trial balances whose local codes are drawn from the ontology's own
  local_codes table — the circularity finding recorded in §1 of
  research/real_data_validation_plan.md. This script measures the same resolver
  against account vocabularies Kontablo did not generate: real tags from real
  public filings and real government finance statistics.

  A lower number here is not a failure. It is the measurement the synthetic
  experiment structurally cannot produce.

WHAT IT MEASURES (and what it does NOT)
  Two DIFFERENT quantities, never to be conflated:

  1. COVERAGE  — did the resolver return some node? Computable over the whole
     corpus, needs no human judgment. Coverage is NOT correctness.
  2. ACCURACY  — did it return the RIGHT node? Computable only over the
     gold-labeled sample (research/.../gold/), built per plan §6 by independent
     double-labeling. The pre-registered hypotheses H1 and H5 are ACCURACY
     thresholds, so the headline number for each is the gold-sample accuracy,
     not coverage.

  Scoring rule for out-of-core tags: real taxonomies contain many face-statement
  concepts with no Kontablo core node (share counts, per-share amounts, segment
  roll-forwards). For those, gold_kontablo_id is empty and the CORRECT behavior
  is to ESCALATE. Resolving them anyway is scored as an error (false positive),
  not as coverage. This is what keeps "high coverage" from being gamed by a
  resolver that maps everything to something.

THE RESOLVER IS NOT MODIFIED
  A real taxonomy is loaded as a PSEUDO-JURISDICTION code table: the crosswalk
  us_gaap_tags.yaml becomes by_code["us-gaap"] exactly as a statutory chart
  overlay becomes by_code["fr"]. core.harness.resolve_with_rule is then called
  unchanged, so this benchmark exercises the same Tier-1/Tier-2 logic that
  produces the published synthetic number. Nothing here imports INTO
  core.harness (plan §13); the dependency points one way only.

THE HOLDOUT IS WHAT MAKES THIS NON-CIRCULAR
  Each crosswalk is built from the TRAIN window only. Scoring happens on the
  HOLDOUT window, which contains codes that did not exist when the crosswalk was
  written. Those codes cannot be resolved by Tier 1 and must fall through to the
  Tier-2 keyword rules or escalate. Results are therefore always reported split
  into seen-in-train and unseen-in-train strata: the pooled number is dominated
  by the stable head of the distribution, and quoting it alone would reproduce
  the very circularity this round exists to escape.

INPUTS (all committed and small; raw filings are never vendored -- see §7)
  core/schemas/level3_accounts.yaml            the ontology (unchanged)
  core/schemas/us_gaap_tags.yaml               crosswalk, built from TRAIN only
  core/schemas/gfs_cofog_tags.yaml             crosswalk, built from TRAIN only
  research/experiments/*/derived/*.csv         real code inventories + weights
  research/experiments/*/gold/*.csv            adjudicated gold labels (optional)

OUTPUT
  research/experiments/tag_resolution_v1/results.json
  research/experiments/public_sector_gfs_v1/results.json

Run:  venv/bin/python scripts/real_data/resolve_real_facts.py
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from core.harness.ontology import load_ontology  # noqa: E402
from core.harness.resolution import resolve_with_rule  # noqa: E402

CROSSWALKS = {
    "us-gaap": os.path.join(ROOT, "core/schemas/us_gaap_tags.yaml"),
    "ifrs-full": os.path.join(ROOT, "core/schemas/ifrs_full_tags.yaml"),
    "gfs": os.path.join(ROOT, "core/schemas/gfs_cofog_tags.yaml"),
}


# ---------------------------------------------------------------------------
# Normalized inventory contract
# ---------------------------------------------------------------------------
# Every source adapter must yield rows with exactly these keys. Keeping one
# shape means the scorer has no per-source branches and cannot accidentally
# apply a different rule to a different corpus.
INVENTORY_FIELDS = (
    "source",          # edgar | esef | imf_gfs | eurostat_cofog
    "taxonomy",        # pseudo-jurisdiction key into the crosswalks above
    "window",          # train | holdout
    "code",            # the tag / classification code as filed
    "name",            # human-readable label, "" if the source provides none
    "taxonomy_class",  # standard | extension
    "measure_class",   # monetary | non_monetary | unknown
    "n_facts",         # weight: occurrences in the corpus
    "n_filings",       # secondary weight: distinct reporting entities
)

# Face-statement facts are not all ledger amounts. Roughly 8% of real EDGAR
# standard face-statement facts are share counts, per-share amounts or ratios
# (datatype shares / perShare / percent / pure / decimal). A chart of accounts
# maps MONETARY ledger balances; it structurally has no node for "weighted
# average diluted shares outstanding", and counting those against it would
# understate coverage for a reason that has nothing to do with the ontology.
#
# The monetary subset is therefore the PRIMARY population for H1, and the
# exclusion is deterministic (it reads the taxonomy's own declared datatype --
# no human judgment, no per-tag discretion). The full population is reported
# alongside it so the exclusion is visible and quantified rather than assumed.
MONETARY_DATATYPES = {"monetary"}
NON_MONETARY_DATATYPES = {"shares", "persharesitemtype", "pershare", "percent", "pure", "decimal"}


def classify_measure(datatype: str) -> str:
    dt = (datatype or "").strip().lower()
    if not dt:
        return "unknown"
    if dt in MONETARY_DATATYPES:
        return "monetary"
    if dt in NON_MONETARY_DATATYPES:
        return "non_monetary"
    return "unknown"


def _read_csv(path: str) -> list[dict]:
    """Read a derived CSV, transparently handling the gzipped inventories.

    The EDGAR tag inventories are committed gzipped (~110 MB raw, ~11 MB
    compressed) so that scoring stays hermetic and offline without vendoring a
    hundred megabytes of derived text.
    """
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _find(base: str, stem: str) -> str | None:
    """Locate a derived artifact whether it is stored plain or gzipped."""
    for candidate in (os.path.join(base, stem), os.path.join(base, stem + ".gz")):
        if os.path.exists(candidate):
            return candidate
    return None


def _require(row: dict, path: str, *cols: str) -> None:
    missing = [c for c in cols if c not in row]
    if missing:
        raise SystemExit(
            f"{os.path.relpath(path, ROOT)} is missing required column(s): "
            f"{', '.join(missing)}\nFound: {', '.join(row)}"
        )


def _int(value: str) -> int:
    try:
        return int(float(value or 0))
    except (TypeError, ValueError):
        return 0


def load_inventory(experiment: str) -> list[dict]:
    """Load every derived inventory CSV for an experiment into the normalized shape."""
    base = os.path.join(ROOT, "research/experiments", experiment, "derived")
    rows: list[dict] = []

    edgar = {
        "train": _find(base, "edgar_tags_train.csv"),
        "holdout": _find(base, "edgar_tags_holdout.csv"),
    }
    for window, path in edgar.items():
        if path is None:
            continue
        raw = _read_csv(path)
        if raw:
            _require(raw[0], path, "tag", "custom", "n_facts")
        for r in raw:
            rows.append({
                "source": "edgar",
                "taxonomy": "us-gaap",
                "window": window,
                "code": r["tag"],
                "name": r.get("tlabel") or r.get("plabel_modal") or "",
                "taxonomy_class": "extension" if r.get("custom") == "1" else "standard",
                "measure_class": classify_measure(r.get("datatype", "")),
                "n_facts": _int(r.get("n_facts")),
                "n_filings": _int(r.get("n_filings")),
            })

    esef = _find(base, "esef_tags.csv")
    if esef:
        raw = _read_csv(esef)
        if raw:
            _require(raw[0], esef, "local_name", "taxonomy_class", "window", "n_facts")
        for r in raw:
            cls = "extension" if r["taxonomy_class"] == "extension" else "standard"
            rows.append({
                "source": "esef",
                "taxonomy": "ifrs-full",
                "window": r["window"],
                "code": r["local_name"],
                "name": r.get("label_en") or "",
                "taxonomy_class": cls,
                "measure_class": classify_measure(r.get("datatype", "")),
                "n_facts": _int(r.get("n_facts")),
                "n_filings": _int(r.get("n_filings")),
            })

    for source, fname in (("imf_gfs", "imf_gfs_usage.csv"),
                          ("eurostat_cofog", "eurostat_cofog_usage.csv")):
        path = _find(base, fname)
        if path is None:
            continue
        raw = _read_csv(path)
        if raw:
            _require(raw[0], path, "code", "window")
        for r in raw:
            rows.append({
                "source": source,
                "taxonomy": "gfs",
                "window": r["window"],
                "code": r["code"],
                "name": r.get("label_en") or "",
                "taxonomy_class": "standard",
                # Government finance statistics report monetary aggregates
                # throughout; there is no share-count analogue in GFS/COFOG.
                "measure_class": "monetary",
                "n_facts": _int(r.get("n_observations")) or _int(r.get("n_facts")),
                "n_filings": _int(r.get("n_countries")) or _int(r.get("n_filings")),
            })

    return collapse_versions(rows)


def collapse_versions(rows: list[dict]) -> list[dict]:
    """Aggregate to one row per (source, taxonomy, window, code).

    EDGAR's inventory is keyed by (tag, version), so a tag that survives a
    taxonomy release appears once per vintage -- e.g. Assets under both
    us-gaap/2024 and us-gaap/2025. Left uncollapsed this would (a) let the same
    tag be drawn twice into the gold sample and labeled twice, and (b) make
    "unseen in train" wildly overstated, since almost every holdout
    (tag, version) pair is new purely because the version string advanced. The
    hypothesis is about a TAG resolving, not about a tag-vintage pair, so the
    version dimension is summed away here.
    """
    merged: dict[tuple, dict] = {}
    for row in rows:
        key = (row["source"], row["taxonomy"], row["window"], row["code"])
        node = merged.get(key)
        if node is None:
            merged[key] = dict(row)
            continue
        node["n_facts"] += row["n_facts"]
        node["n_filings"] = max(node["n_filings"], row["n_filings"])
        # Prefer a populated label and a decided measure class over an empty one.
        if not node["name"] and row["name"]:
            node["name"] = row["name"]
        if node["measure_class"] == "unknown" and row["measure_class"] != "unknown":
            node["measure_class"] = row["measure_class"]
        # An element declared as an issuer extension in ANY vintage is treated as
        # an extension throughout: H2 must not be softened by a later vintage
        # that happens to label the same name as standard.
        if row["taxonomy_class"] == "extension":
            node["taxonomy_class"] = "extension"
    return sorted(merged.values(), key=lambda r: (r["source"], r["window"], r["code"]))


# ---------------------------------------------------------------------------
# Crosswalk -> pseudo-jurisdiction code table
# ---------------------------------------------------------------------------
PUBLIC_SECTOR_EXT = os.path.join(ROOT, "localizations/industries/public_sector_ipsas.yaml")


def load_public_sector_nodes() -> dict:
    """Load the drafted IPSAS/public-sector nodes as SCORING-LOCAL ontology entries.

    The extension is deliberately NOT wired into core/harness/ontology.py, and
    plan §14 puts wiring it explicitly out of scope for round 2 -- that decision
    comes only after H5 clears its threshold. But H5 cannot be measured at all if
    the nodes do not exist in the scoring vocabulary.

    So this loader augments the accounts dict used by THIS BENCHMARK ONLY. The
    live resolver is untouched: no core file is modified and nothing is written
    back. Running the production resolver against a government chart today still
    resolves nothing, which is exactly the status quo the plan describes and the
    reason public-sector coverage must stay described as "drafted, not yet
    empirically validated" until the threshold clears.
    """
    if not os.path.exists(PUBLIC_SECTOR_EXT):
        return {}
    doc = yaml.safe_load(open(PUBLIC_SECTOR_EXT, encoding="utf-8")) or {}
    nodes = {}
    for key, entry in (doc.get("mappings") or {}).items():
        entry = entry or {}
        nodes[str(key)] = {
            "uuid": entry.get("kontablo_uuid"),
            "label": entry.get("name", str(key)),
            "nature": str(entry.get("nature", "unknown")).lower(),
            "statement": entry.get("statement", "unknown"),
            "local_codes": {},
            "groupings": {"ifrs": entry.get("parent_kontablo")},
        }
    return nodes


def load_crosswalk(taxonomy: str) -> tuple[dict, dict]:
    """Return (code -> kontablo_id for mapped codes, full annotation dict).

    A crosswalk entry with ``kontablo_id: null`` is a DELIBERATE out-of-core
    declaration: the curator saw the tag and judged that Kontablo's core has no
    node for it. That is different from a tag being absent from the crosswalk
    (never seen). Both escalate at resolution time, but only the first is
    evidence about the semantic coverage boundary, so they are counted apart.
    """
    path = CROSSWALKS[taxonomy]
    if not os.path.exists(path):
        return {}, {}
    doc = yaml.safe_load(open(path, encoding="utf-8")) or {}
    mappings = doc.get("mappings") or {}
    by_code = {}
    for code, entry in mappings.items():
        entry = entry or {}
        kid = entry.get("kontablo_id")
        if kid:
            by_code[str(code)] = kid
    return by_code, mappings


# ---------------------------------------------------------------------------
# Baseline (a) from plan §6.5: naive English-label string match
# ---------------------------------------------------------------------------
_WORD = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> frozenset:
    return frozenset(_WORD.findall((text or "").lower()))


def build_label_index(accounts: dict) -> list[tuple[str, frozenset]]:
    return [(kid, _tokens(a["label"])) for kid, a in sorted(accounts.items())]


def naive_label_match(name: str, label_index) -> str | None:
    """Exact normalized-token-set equality against a node's English label.

    Deliberately dumb: this is the floor a real system must beat, so it gets no
    stemming, no synonyms, and no partial credit.
    """
    toks = _tokens(name)
    if not toks:
        return None
    for kid, label_toks in label_index:
        if toks == label_toks:
            return kid
    return None


# ---------------------------------------------------------------------------
# Gold labels
# ---------------------------------------------------------------------------
def load_gold(experiment: str) -> dict:
    """(taxonomy, code) -> adjudicated gold kontablo_id ('' means out-of-core)."""
    gold_dir = os.path.join(ROOT, "research/experiments", experiment, "gold")
    out = {}
    if not os.path.isdir(gold_dir):
        return out
    for fname in sorted(os.listdir(gold_dir)):
        if not fname.startswith("gold_labels") or not fname.endswith(".csv"):
            continue
        path = os.path.join(gold_dir, fname)
        raw = _read_csv(path)
        if raw:
            _require(raw[0], path, "taxonomy", "code", "gold_kontablo_id")
        for r in raw:
            out[(r["taxonomy"], r["code"])] = (r["gold_kontablo_id"] or "").strip()
    return out


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------
def score(rows, accounts, gold, crosswalk_tables, annotations):
    """Resolve every inventory row and accumulate coverage + accuracy metrics."""
    label_index = build_label_index(accounts)
    train_codes = {
        (r["taxonomy"], r["code"]) for r in rows if r["window"] == "train"
    }
    detail = []

    for r in rows:
        taxonomy = r["taxonomy"]
        by_code = {taxonomy: crosswalk_tables.get(taxonomy, {})}
        entry = {"code": r["code"], "name": r["name"]}
        kid, tier, conf, rule = resolve_with_rule(entry, taxonomy, accounts, by_code)

        key = (taxonomy, r["code"])
        annotation = (annotations.get(taxonomy) or {}).get(r["code"]) or {}
        detail.append({
            **r,
            "resolved_id": kid,
            "tier": tier,
            "confidence": conf,
            "rule": rule,
            "seen_in_train": key in train_codes,
            "in_crosswalk": r["code"] in crosswalk_tables.get(taxonomy, {}),
            "declared_out_of_core": (
                r["code"] in (annotations.get(taxonomy) or {})
                and not annotation.get("kontablo_id")
            ),
            "baseline_naive": naive_label_match(r["name"], label_index),
            "gold": gold.get(key),
        })
    return detail


def _bucket() -> dict:
    return {
        "n_codes": 0, "n_facts": 0,
        "tier1_codes": 0, "tier1_facts": 0,
        "tier2_codes": 0, "tier2_facts": 0,
        "escalated_codes": 0, "escalated_facts": 0,
    }


def _add(bucket: dict, row: dict) -> None:
    bucket["n_codes"] += 1
    bucket["n_facts"] += row["n_facts"]
    tier = {"tier1_exact": "tier1", "tier2_keyword": "tier2"}.get(row["tier"], "escalated")
    bucket[f"{tier}_codes"] += 1
    bucket[f"{tier}_facts"] += row["n_facts"]


def _pct(num: float, den: float) -> float:
    return round(100.0 * num / den, 1) if den else 0.0


def summarize_coverage(detail: list[dict]) -> dict:
    """Coverage by population, window and seen/unseen stratum.

    ``monetary`` is the primary population (see MONETARY_DATATYPES); ``all``
    retains every standard face-statement tag so the exclusion stays visible.
    Coverage is not accuracy -- see the module docstring.
    """
    out: dict = {}
    for row in detail:
        if row["taxonomy_class"] != "standard":
            continue  # extensions are scored under H2, never counted as coverage
        populations = ["all"] + (["monetary"] if row["measure_class"] == "monetary" else [])
        stratum = "seen_in_train" if row["seen_in_train"] else "unseen_in_train"
        for population in populations:
            node = out.setdefault(population, {}).setdefault(
                row["window"], {"pooled": _bucket(), "by_stratum": {}}
            )
            _add(node["pooled"], row)
            _add(node["by_stratum"].setdefault(stratum, _bucket()), row)

    for windows in out.values():
        for node in windows.values():
            for bucket in [node["pooled"], *node["by_stratum"].values()]:
                resolved_codes = bucket["tier1_codes"] + bucket["tier2_codes"]
                resolved_facts = bucket["tier1_facts"] + bucket["tier2_facts"]
                bucket["resolved_pct_unweighted"] = _pct(resolved_codes, bucket["n_codes"])
                bucket["resolved_pct_weighted"] = _pct(resolved_facts, bucket["n_facts"])
    return out


def summarize_h2(detail: list[dict]) -> dict:
    """H2: company-specific extensions must never be silently force-mapped.

    OPERATIONALIZATION (recorded 2026-07-30, before scoring, per the plan's
    "dated addendum" discipline -- the plan fixes the hypothesis but did not
    define "silently"):

      * A Tier-1 hit on an extension is a VIOLATION. Tier 1 asserts an exact
        code identity at confidence 1.0; an issuer-invented tag cannot have one.
        An extension reaching Tier 1 would mean the crosswalk was contaminated
        with non-standard codes.
      * A Tier-2 hit is NOT a violation and NOT silent: Tier 2 is the designed
        name-based path, it reports confidence 0.85, and it names the exact rule
        that fired (tier2:<node>:<keyword>), so the decision is auditable and
        reviewable. It is reported separately and its correctness is measured
        against the gold sample like any other resolution.
      * Escalation is the conservative outcome.

    Reporting Tier-2 extension hits separately rather than folding them into
    either bucket is the honest treatment: hiding them would overstate H2, and
    calling them violations would mean the resolver is penalized for doing
    exactly what its documented design says Tier 2 is for.
    """
    out: dict = {}
    for row in detail:
        if row["taxonomy_class"] != "extension":
            continue
        node = out.setdefault(row["window"], {
            "n_extension_codes": 0, "n_extension_facts": 0,
            "tier1_violations": 0, "tier1_violation_facts": 0,
            "tier2_name_matches": 0, "tier2_name_match_facts": 0,
            "escalated": 0, "escalated_facts": 0,
            "violating_codes": [],
        })
        node["n_extension_codes"] += 1
        node["n_extension_facts"] += row["n_facts"]
        if row["tier"] == "tier1_exact":
            node["tier1_violations"] += 1
            node["tier1_violation_facts"] += row["n_facts"]
            if len(node["violating_codes"]) < 25:
                node["violating_codes"].append(
                    {"code": row["code"], "resolved_id": row["resolved_id"], "rule": row["rule"]}
                )
        elif row["tier"] == "tier2_keyword":
            node["tier2_name_matches"] += 1
            node["tier2_name_match_facts"] += row["n_facts"]
        else:
            node["escalated"] += 1
            node["escalated_facts"] += row["n_facts"]

    for node in out.values():
        node["escalation_rate_pct_unweighted"] = _pct(node["escalated"], node["n_extension_codes"])
        node["escalation_rate_pct_weighted"] = _pct(node["escalated_facts"], node["n_extension_facts"])
        node["h2_holds"] = node["tier1_violations"] == 0
    return out


def gold_class(gold: str) -> str:
    """Classify a gold label into the three kinds of thing a real tag can be.

    Real face statements are presentation trees, not trial balances: alongside
    leaf accounts they carry SUBTOTALS (Assets, LiabilitiesAndStockholdersEquity,
    OperatingIncomeLoss). Kontablo's 30 core nodes are all leaves -- aggregation
    is computed by the engine through rollup lenses, never stored as a node.

    Folding subtotals into "outside Kontablo's scope" would be false: Kontablo
    does represent them, as derived rollups. Mapping them to a leaf node would
    also be false, and would silently double-count against that leaf. So they get
    their own class. For scoring, the correct resolver behavior on an aggregate
    is to ESCALATE -- the deterministic tiers resolve leaves, and a subtotal
    reaching a leaf node is a real error worth catching.

      "<node id>"              leaf      resolvable to a Kontablo core node
      "AGGREGATE:<lens>"       aggregate representable only as a computed rollup
      ""                       out_of_scope  no Kontablo concept at all
    """
    if not gold:
        return "out_of_scope"
    return "aggregate" if gold.startswith("AGGREGATE:") else "leaf"


def summarize_accuracy(detail: list[dict]) -> dict:
    """Accuracy over the gold-labeled sample. This is the H1/H5 headline.

    Outcome taxonomy:
      correct                  predicted node == gold node (leaf labels only)
      wrong_node               resolved, but to the wrong node
      missed                   gold has a leaf node; resolver escalated
      correct_escalation       gold is aggregate/out-of-scope and resolver escalated
      false_positive           gold is aggregate/out-of-scope; resolver mapped it anyway
    """
    out: dict = {}
    for row in detail:
        if row["gold"] is None:
            continue
        window = row["window"]
        stratum = "seen_in_train" if row["seen_in_train"] else "unseen_in_train"
        klass = gold_class(row["gold"])
        scopes = (
            out.setdefault(window, {}).setdefault("pooled", {}),
            out[window].setdefault("by_stratum", {}).setdefault(stratum, {}),
            out[window].setdefault("by_gold_class", {}).setdefault(klass, {}),
        )
        for scope in scopes:
            scope.setdefault("n_codes", 0)
            scope.setdefault("n_facts", 0)
            for k in ("correct", "wrong_node", "false_positive", "missed", "correct_escalation"):
                scope.setdefault(k, 0)
                scope.setdefault(f"{k}_facts", 0)

        gold_id = row["gold"]
        predicted = row["resolved_id"]
        if klass == "leaf":
            outcome = "correct" if predicted == gold_id else ("missed" if predicted is None else "wrong_node")
        else:
            # Aggregates and out-of-scope tags: escalating is the right answer.
            outcome = "correct_escalation" if predicted is None else "false_positive"

        for scope in scopes:
            scope["n_codes"] += 1
            scope["n_facts"] += row["n_facts"]
            scope[outcome] += 1
            scope[f"{outcome}_facts"] += row["n_facts"]

    for window, node in out.items():
        scopes = [node["pooled"], *node["by_stratum"].values(),
                  *node.get("by_gold_class", {}).values()]
        for scope in scopes:
            # "Correct" credits both a right mapping and a right refusal: a
            # resolver that correctly declines an out-of-core tag is behaving
            # exactly as designed and must not be scored as a miss.
            right = scope["correct"] + scope["correct_escalation"]
            right_facts = scope["correct_facts"] + scope["correct_escalation_facts"]
            scope["accuracy_pct_unweighted"] = _pct(right, scope["n_codes"])
            scope["accuracy_pct_weighted"] = _pct(right_facts, scope["n_facts"])
            # Accuracy restricted to tags that DO have a core node -- the
            # narrower question "when Kontablo should map, does it map right?"
            in_scope = scope["correct"] + scope["wrong_node"] + scope["missed"]
            in_scope_facts = scope["correct_facts"] + scope["wrong_node_facts"] + scope["missed_facts"]
            scope["in_core_accuracy_pct_unweighted"] = _pct(scope["correct"], in_scope)
            scope["in_core_accuracy_pct_weighted"] = _pct(scope["correct_facts"], in_scope_facts)
    return out


def summarize_baseline(detail: list[dict]) -> dict:
    """Baseline (a): naive English-label match, scored on the same gold sample."""
    out: dict = {}
    for row in detail:
        if row["gold"] is None:
            continue
        node = out.setdefault(row["window"], {"n_codes": 0, "n_facts": 0,
                                              "correct": 0, "correct_facts": 0})
        node["n_codes"] += 1
        node["n_facts"] += row["n_facts"]
        predicted = row["baseline_naive"]
        gold_id = row["gold"]
        hit = (predicted == gold_id) if gold_id else (predicted is None)
        if hit:
            node["correct"] += 1
            node["correct_facts"] += row["n_facts"]
    for node in out.values():
        node["accuracy_pct_unweighted"] = _pct(node["correct"], node["n_codes"])
        node["accuracy_pct_weighted"] = _pct(node["correct_facts"], node["n_facts"])
    return out


def run(experiment: str, accounts: dict) -> dict:
    rows = load_inventory(experiment)
    if not rows:
        return {}
    # H5 is measured against the drafted public-sector extension, which is not
    # part of the live resolver's ontology (plan §2/§14). Augment the scoring
    # vocabulary here, never core/harness/.
    public_sector_nodes = {}
    if any(r["taxonomy"] == "gfs" for r in rows):
        public_sector_nodes = load_public_sector_nodes()
        accounts = {**accounts, **public_sector_nodes}
    taxonomies = sorted({r["taxonomy"] for r in rows})
    crosswalk_tables, annotations = {}, {}
    for taxonomy in taxonomies:
        table, annotation = load_crosswalk(taxonomy)
        crosswalk_tables[taxonomy] = table
        annotations[taxonomy] = annotation

    gold = load_gold(experiment)
    detail = score(rows, accounts, gold, crosswalk_tables, annotations)

    results = {
        "experiment": experiment,
        "provenance": {
            "corpus": "real public filings / official statistics; see manifest.json",
            "synthetic_comparison": (
                "NOT comparable to the 97.3% synthetic figure from "
                "scripts/mass_consolidation_v2.py -- different corpus, different question"
            ),
        },
        "taxonomies": taxonomies,
        "public_sector_extension_nodes_loaded": len(public_sector_nodes),
        "public_sector_extension_status": (
            "scoring-local augmentation only; NOT wired into core/harness (plan §14). "
            "Public-sector coverage stays 'drafted, not yet empirically validated' in all "
            "public wording until H5 clears its threshold."
        ) if public_sector_nodes else None,
        "crosswalk_sizes": {t: len(crosswalk_tables[t]) for t in taxonomies},
        "crosswalk_declared_out_of_core": {
            t: sum(1 for e in (annotations[t] or {}).values() if not (e or {}).get("kontablo_id"))
            for t in taxonomies
        },
        "inventory": {
            "n_rows": len(rows),
            "by_window": {
                w: {
                    "n_codes": sum(1 for r in rows if r["window"] == w),
                    "n_facts": sum(r["n_facts"] for r in rows if r["window"] == w),
                }
                for w in sorted({r["window"] for r in rows})
            },
        },
        "coverage": summarize_coverage(detail),
        "h2_extensions": summarize_h2(detail),
        "accuracy_gold_sample": summarize_accuracy(detail),
        "baseline_naive_label_match": summarize_baseline(detail),
        "gold_labels_loaded": len(gold),
    }

    out_path = os.path.join(ROOT, "research/experiments", experiment, "results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)
        fh.write("\n")

    detail_path = os.path.join(ROOT, "research/experiments", experiment, "resolution_detail.csv")
    fields = [
        "source", "taxonomy", "window", "code", "name", "taxonomy_class",
        "measure_class", "n_facts", "n_filings", "resolved_id", "tier", "confidence", "rule",
        "seen_in_train", "in_crosswalk", "declared_out_of_core",
        "baseline_naive", "gold",
    ]
    with open(detail_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in sorted(detail, key=lambda r: (r["source"], r["window"], -r["n_facts"], r["code"])):
            writer.writerow({k: ("" if row.get(k) is None else row.get(k)) for k in fields})
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--experiment", action="append",
        help="experiment dir under research/experiments (repeatable)",
    )
    args = parser.parse_args()
    experiments = args.experiment or ["tag_resolution_v1", "public_sector_gfs_v1"]

    accounts, _by_code, _collisions, _placeholders = load_ontology()

    for experiment in experiments:
        results = run(experiment, accounts)
        if not results:
            print(f"{experiment}: no derived inventory found -- skipped")
            continue
        print("=" * 74)
        print(f"Kontablo round-2 real-data resolution -- {experiment}")
        print("=" * 74)
        print(f"  ontology nodes: {len(accounts)}   "
              f"crosswalk sizes: {results['crosswalk_sizes']}")
        for population in sorted(results["coverage"], reverse=True):
            print(f"  -- population: {population} "
                  f"{'(primary for H1/H5)' if population == 'monetary' else ''}")
            for window, node in sorted(results["coverage"][population].items()):
                pooled = node["pooled"]
                print(f"    [{window}] standard tags: {pooled['n_codes']} codes / "
                      f"{pooled['n_facts']} facts")
                print(f"        coverage  weighted {pooled['resolved_pct_weighted']:>5.1f}%   "
                      f"unweighted {pooled['resolved_pct_unweighted']:>5.1f}%")
                for stratum, bucket in sorted(node["by_stratum"].items()):
                    print(f"          {stratum:<16} weighted {bucket['resolved_pct_weighted']:>5.1f}%   "
                          f"unweighted {bucket['resolved_pct_unweighted']:>5.1f}%   "
                          f"(n={bucket['n_codes']})")
        for window, node in sorted(results["h2_extensions"].items()):
            print(f"  [{window}] H2 extensions: {node['n_extension_codes']} codes   "
                  f"tier1 violations: {node['tier1_violations']}   "
                  f"tier2 name-matches: {node['tier2_name_matches']}   "
                  f"escalated: {node['escalated']}")
        for window, node in sorted(results["accuracy_gold_sample"].items()):
            pooled = node["pooled"]
            print(f"  [{window}] GOLD accuracy: weighted "
                  f"{pooled['accuracy_pct_weighted']:>5.1f}%   "
                  f"unweighted {pooled['accuracy_pct_unweighted']:>5.1f}%   "
                  f"(n={pooled['n_codes']} labeled)")
        if not results["gold_labels_loaded"]:
            print("  NOTE: no gold labels present -- coverage only; H1/H5 are ACCURACY")
            print("        hypotheses and cannot be scored from coverage alone.")
        print(f"  Wrote research/experiments/{experiment}/results.json")


if __name__ == "__main__":
    main()
