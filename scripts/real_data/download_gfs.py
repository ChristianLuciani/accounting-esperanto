#!/usr/bin/env python3
"""
Kontablo — public-sector GFS/COFOG real-data ingestion (Tier A5, hypothesis H5).

WHY THIS EXISTS
  Round-2 real-data validation (research/real_data_validation_plan.md) tests
  whether Kontablo's public-sector/IPSAS extension survives contact with real,
  publicly filed government finance statistics — not synthetic data Kontablo
  generated itself. This script is ingestion only: it downloads and derives a
  clean inventory of the classification code systems actually used in real
  government finance statistics (codes, official labels, real usage
  frequency). It does NOT build the crosswalk to Kontablo's ontology and it
  does NOT score anything — that is a separate, later step (per the plan's
  Tier A design, §10).

LICENSING (corrected 2026-07-30 after inspecting the responses themselves)
  Eurostat responses are open data. IMF responses are NOT: every fetched IMF
  SDMX payload carries LICENSE="(c) International Monetary Fund Copyright. All
  Rights Reserved. https://www.imf.org/external/terms.htm". That is not an
  open-data grant, so IMF payloads take the plan's ambiguous-license regime
  (§7): the snapshot is hashed and manifested but NEVER redistributed. Only
  Kontablo's own derived output -- code lists and observation counts, which are
  original work -- is committed. This was found by reading the payloads rather
  than assuming, and the regime label was corrected to match.

SOURCES
  1. IMF SDMX 2.1 API (https://api.imf.org/external/sdmx/2.1/) — the GFSM 2014
     statement dataflows GFS_COFOG (Classification of Functions of
     Government), GFS_SOO (Statement of Operations: revenue/expense) and
     GFS_BS (Balance Sheet: assets/liabilities), all sharing one DSD
     (IMF.STA:DSD_GFS). The DSD's INDICATOR dimension is enumerated by
     codelist IMF.STA:CL_GFS_INDICATOR, which — usefully — contains BOTH the
     COFOG function codes (GF-prefixed, 80 codes: 10 divisions + 70 classes)
     and the general economic classification codes (revenue/expense/
     balance-sheet, G/F/L/N-prefixed) in one flat vocabulary. That codelist is
     this script's primary IMF deliverable.
  2. Eurostat dissemination API (gov_10a_exp, general government expenditure
     by function and transaction) — cofog99 (function, ESA2010-flavoured
     COFOG numbering, distinct from IMF's own GF-code numbering — see the
     parent_code note below) and na_item (ESA2010 economic transaction codes,
     e.g. D1, P2, D62).

CURRENCY / UNIT DISCIPLINE (do not "fix" this by adding FX conversion)
  IMF's raw domestic-currency series (TYPE_OF_TRANSFORMATION=XDC) is each
  country's OWN currency — summing it across countries silently mixes USD,
  JPY, EUR, etc. This script never does that. Instead it pulls
  TYPE_OF_TRANSFORMATION=POGDP_PT (percent of GDP), IMF's own currency-neutral
  ratio, for every usage/magnitude figure. Eurostat's magnitude figures use
  unit=MIO_EUR, which is Eurostat's OWN published euro-denominated series for
  every reporter (including non-euro-area members) — Kontablo performs no
  conversion of its own in either case. See public_sector_source_summary.csv's
  unit_note column.

TEMPORAL HOLDOUT (pre-registered in research/real_data_validation_plan.md — do
not change without a dated addendum there)
  TRAIN:   year <= 2020
  HOLDOUT: year >= 2021
  The crosswalk (built later, by the orchestrator) is trained on TRAIN-window
  codes only and scored on HOLDOUT, including any code absent from TRAIN.

SCOPE OF THE "usage" MEASUREMENT (an explicit, documented narrowing)
  imf_gfs_codelist.csv carries the FULL CL_GFS_INDICATOR vocabulary (493
  codes) — the complete vocabulary a later crosswalk can draw on.
  imf_gfs_usage.csv, by contrast, only measures usage for:
    - all 80 COFOG (GF-prefixed) codes, and
    - a curated set of 20 top-level economic-classification codes (revenue,
      expense, balance-sheet) hand-picked from the codelist as the
      GFSM-2014-standard top categories (G1/G11..G14 revenue; G2/G21..G28
      expense; NFA_A_SP/FA_A_SP/L_SP/G6_A_SP balance-sheet; GGB_T/GPB_T
      balancing items).
  The remaining ~400 codes in the codelist are highly granular
  financial-instrument/counterparty breakdowns (e.g. "F62_G33_L_T" — life
  insurance liabilities to foreign creditors) that are not first-order
  chart-of-accounts categories; measuring their usage was out of scope for
  this pass. This narrowing is deliberate, not an oversight — see the
  CURATED_ECONOMIC_CODES constant below for the exact list and rationale.

PARENT-CODE HIERARCHY (derived, not sourced — documented explicitly)
  Neither IMF's SDMX codelist nor Eurostat's JSON-stat codelist exposes an
  explicit parent/child relation. Where a hierarchy is reconstructed here, it
  is a DETERMINISTIC, DOCUMENTED string-prefix inference over codes that
  already exist in the fetched vocabulary (never a fabricated code):
    - IMF COFOG (GF-prefixed, all sharing the "_T" suffix): parent is the
      longest strict numeric-prefix code that also exists, e.g. GF0140_T's
      base "GF0140" strictly contains "GF01" -> parent GF01_T.
    - IMF general economic codes: left blank. Outside the COFOG family the
      numbering is not a clean prefix hierarchy in this codelist (e.g. G11_T
      "Taxes" has no G111_T sibling here — that granularity lives in
      differently-prefixed instrument codes), so no parent is inferred.
    - Eurostat cofog99: 6-char class codes (GF0101) -> 4-char division
      code (GF01); 4-char division codes -> "TOTAL"; TOTAL has no parent.
    - Eurostat na_item: left blank (ESA2010 transaction codes are not a
      clean digit hierarchy; some, e.g. D29_D5_D8, are additive combinations
      of several codes, not children of a single parent).

Run:  venv/bin/python scripts/real_data/download_gfs.py
      KONTABLO_REAL_DATA_OFFLINE=1 venv/bin/python scripts/real_data/download_gfs.py   (replay, no network)
Output:
  research/experiments/public_sector_gfs_v1/manifest.json          (written by _snapshot)
  research/experiments/public_sector_gfs_v1/derived/*.csv          (five files, see module end)
"""

from __future__ import annotations

import csv
import json
import os
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts.real_data import _snapshot as snap  # noqa: E402

EXPERIMENT = "public_sector_gfs_v1"
DERIVED_DIR = os.path.join(ROOT, "research", "experiments", EXPERIMENT, "derived")
LICENSE_REGIME_EUROSTAT = "open_data"
# IMF payloads are All-Rights-Reserved; hash-and-manifest only, never redistribute.
LICENSE_REGIME_IMF = "no_redistribution"

TRAIN_MAX_YEAR = 2020  # inclusive; holdout is everything after this (pre-registered)

IMF_SDMX_BASE = "https://api.imf.org/external/sdmx/2.1"
EUROSTAT_BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

# Curated top-level GFSM 2014 economic-classification codes (see module
# docstring "SCOPE OF THE usage MEASUREMENT" for why these and not all 493).
IMF_REVENUE_CODES = ["G1_T", "G11_T", "G12_T", "G13_T", "G14_T"]
IMF_EXPENSE_CODES = [
    "G2_T", "G21_T", "G22_T", "G23_T", "G24_T", "G25_T", "G26_T", "G27_T", "G28_T",
]
IMF_BALANCE_SHEET_CODES = ["NFA_A_SP", "FA_A_SP", "L_SP", "G6_A_SP"]
IMF_BALANCING_ITEM_CODES = ["GGB_T", "GPB_T"]
IMF_SOO_QUERY_CODES = sorted(IMF_REVENUE_CODES + IMF_EXPENSE_CODES + IMF_BALANCING_ITEM_CODES)
IMF_BS_QUERY_CODES = sorted(IMF_BALANCE_SHEET_CODES)

IMF_SECTOR = "S13"  # General government (consolidated) — avoids double-counting subsectors
IMF_TRANSFORMATION = "POGDP_PT"  # percent of GDP: currency-neutral, see module docstring
IMF_FREQUENCY = "A"
IMF_START_PERIOD = "1990"
IMF_END_PERIOD = "2025"

EUROSTAT_DATASET = "gov_10a_exp"
EUROSTAT_UNIT = "MIO_EUR"
EUROSTAT_SECTOR = "S13"


def _local(tag: str) -> str:
    """Strip the SDMX/XML namespace prefix from an ElementTree tag."""
    return tag.rsplit("}", 1)[-1]


def _xml_lang_text(elem: ET.Element, local_name: str) -> str:
    """Return the English-language text of the first matching child, or ''."""
    for child in elem:
        if _local(child.tag) == local_name and child.get(
            "{http://www.w3.org/XML/1998/namespace}lang"
        ) == "en":
            return (child.text or "").strip()
    return ""


# ---------------------------------------------------------------------------
# IMF SDMX
# ---------------------------------------------------------------------------


def imf_fetch_dataflow_versions() -> dict:
    """Discover the current (agencyID, version) of the three GFS dataflows we
    use, rather than hardcoding version numbers that IMF can bump — the
    fetched response itself is hashed into the manifest for reproducibility.
    """
    path = snap.fetch(
        f"{IMF_SDMX_BASE}/dataflow",
        EXPERIMENT,
        key="imf_dataflow_list",
        license_regime=LICENSE_REGIME_IMF,
        relpath="imf/dataflow_list.xml",
        timeout=120,
        note="Full IMF SDMX dataflow catalogue; parsed for GFS_COFOG/GFS_SOO/GFS_BS versions.",
    )
    tree = ET.parse(path)
    wanted = {"GFS_COFOG", "GFS_SOO", "GFS_BS"}
    found = {}
    for elem in tree.getroot().iter():
        if _local(elem.tag) == "Dataflow" and elem.get("id") in wanted:
            found[elem.get("id")] = (elem.get("agencyID"), elem.get("version"))
    missing = wanted - found.keys()
    if missing:
        raise RuntimeError(f"IMF dataflow catalogue is missing expected dataflows: {sorted(missing)}")
    return found


def imf_fetch_codelist() -> list:
    """Fetch IMF.STA:CL_GFS_INDICATOR — the flat vocabulary of economic
    classification codes AND COFOG function codes (see module docstring).
    Returns a list of dicts: code, label_en, description.
    """
    path = snap.fetch(
        f"{IMF_SDMX_BASE}/codelist/IMF.STA/CL_GFS_INDICATOR",
        EXPERIMENT,
        key="imf_codelist_gfs_indicator",
        license_regime=LICENSE_REGIME_IMF,
        relpath="imf/codelist_gfs_indicator.xml",
        timeout=60,
        note="IMF.STA:CL_GFS_INDICATOR — INDICATOR dimension codelist shared by all GFSM 2014 GFS dataflows.",
    )
    tree = ET.parse(path)
    rows = []
    for elem in tree.getroot().iter():
        if _local(elem.tag) == "Code" and elem.get("id"):
            rows.append(
                {
                    "code": elem.get("id"),
                    "label_en": _xml_lang_text(elem, "Name"),
                    "description": _xml_lang_text(elem, "Description"),
                }
            )
    if not rows:
        raise RuntimeError("IMF CL_GFS_INDICATOR codelist parsed to zero codes — check the XML shape.")
    return rows


def _imf_key(codes: list) -> str:
    """Build the SDMX data-key for DSD_GFS's six dimensions in DSD order:
    COUNTRY.SECTOR.GFS_GRP.INDICATOR.TYPE_OF_TRANSFORMATION.FREQUENCY.
    COUNTRY and GFS_GRP are left wildcarded (blank); INDICATOR accepts a
    "+"-joined OR-list so many codes are fetched in one request.
    """
    indicator = "+".join(codes)
    return f".{IMF_SECTOR}..{indicator}.{IMF_TRANSFORMATION}.{IMF_FREQUENCY}"


def imf_fetch_data(dataflow_id: str, agency: str, version: str, codes: list, key_suffix: str) -> list:
    """Fetch observations for `codes` from one GFS dataflow. Returns a list of
    dicts: code, country, year (int), value (float). Missing observations
    (STATUS=NA, no OBS_VALUE attribute) are skipped, not coerced to 0.
    """
    data_key = _imf_key(codes)
    url = (
        f"{IMF_SDMX_BASE}/data/{agency},{dataflow_id},{version}/{data_key}"
        f"?startPeriod={IMF_START_PERIOD}&endPeriod={IMF_END_PERIOD}"
    )
    path = snap.fetch(
        url,
        EXPERIMENT,
        key=f"imf_data_{key_suffix}",
        license_regime=LICENSE_REGIME_IMF,
        relpath=f"imf/data_{key_suffix}.xml",
        timeout=300,
        retries=3,
        note=(
            f"{dataflow_id} v{version}; SECTOR={IMF_SECTOR}; "
            f"TYPE_OF_TRANSFORMATION={IMF_TRANSFORMATION}; {len(codes)} INDICATOR codes OR-joined; "
            f"{IMF_START_PERIOD}-{IMF_END_PERIOD}."
        ),
    )
    tree = ET.parse(path)
    records = []
    for series_elem in tree.getroot().iter():
        if _local(series_elem.tag) != "Series":
            continue
        indicator = series_elem.get("INDICATOR")
        country = series_elem.get("COUNTRY")
        for obs_elem in series_elem:
            if _local(obs_elem.tag) != "Obs":
                continue
            raw_value = obs_elem.get("OBS_VALUE")
            if raw_value is None:
                continue
            try:
                value = float(raw_value)
            except ValueError:
                continue
            year_raw = obs_elem.get("TIME_PERIOD")
            try:
                year = int(year_raw)
            except (TypeError, ValueError):
                continue
            records.append({"code": indicator, "country": country, "year": year, "value": value})
    return records


def imf_cofog_parent(code: str, cofog_codes: set) -> str:
    """Longest strict numeric-prefix ancestor within the GF-prefixed "_T"
    family (see module docstring). Returns "" if code is a top-level division
    or is not itself a GF/_T code.
    """
    if not (code.startswith("GF") and code.endswith("_T")):
        return ""
    base = code[:-2]  # strip "_T"
    for cut in range(len(base) - 1, 3, -1):  # down to "GF01" (len 4), exclusive of full length
        candidate = base[:cut] + "_T"
        if candidate != code and candidate in cofog_codes:
            return candidate
    return ""


# ---------------------------------------------------------------------------
# Eurostat
# ---------------------------------------------------------------------------


def eurostat_fetch_geo_list() -> list:
    """Small probe query (one unit/na_item/cofog99 slice, all geos, one year)
    to discover the real reporter list without pulling the full dataset.
    Aggregate zones (EA19, EA20, EA21, EU27_2020, ...) are excluded by their
    length: real ISO-3166 alpha-2 country/EEA codes are exactly 2 characters,
    every Eurostat aggregate zone code observed is longer.
    """
    url = (
        f"{EUROSTAT_BASE}/{EUROSTAT_DATASET}?format=JSON&time=2022"
        f"&unit={EUROSTAT_UNIT}&na_item=D1&cofog99=GF01"
    )
    path = snap.fetch(
        url,
        EXPERIMENT,
        key="eurostat_geo_probe",
        license_regime=LICENSE_REGIME_EUROSTAT,
        relpath="eurostat/geo_probe.json",
        timeout=60,
        note="Single-slice probe (unit=MIO_EUR, na_item=D1, cofog99=GF01, time=2022) to enumerate reporters.",
    )
    with open(path, encoding="utf-8") as fh:
        payload = json.load(fh)
    geo_codes = list(payload["dimension"]["geo"]["category"]["index"].keys())
    return sorted(g for g in geo_codes if len(g) == 2)


def eurostat_fetch_country(geo: str) -> str:
    url = (
        f"{EUROSTAT_BASE}/{EUROSTAT_DATASET}?format=JSON"
        f"&unit={EUROSTAT_UNIT}&sector={EUROSTAT_SECTOR}&geo={geo}"
    )
    return snap.fetch(
        url,
        EXPERIMENT,
        key=f"eurostat_data_{geo}",
        license_regime=LICENSE_REGIME_EUROSTAT,
        relpath=f"eurostat/data_{geo}.json",
        timeout=120,
        note=f"gov_10a_exp full time series for geo={geo}, unit={EUROSTAT_UNIT}, sector={EUROSTAT_SECTOR}.",
    )


def _eurostat_decode_flat_index(flat: int, sizes: list) -> list:
    """JSON-stat 2.0: dimensions in `id` order, last dimension fastest-varying."""
    n = len(sizes)
    strides = [1] * n
    for i in range(n - 2, -1, -1):
        strides[i] = strides[i + 1] * sizes[i + 1]
    idxs = []
    remaining = flat
    for stride in strides:
        idxs.append(remaining // stride)
        remaining %= stride
    return idxs


def eurostat_parse(path: str):
    """Parse one geo's JSON-stat response. Returns (records, labels) where
    records is a list of dicts {cofog99, na_item, year, value} and labels is
    {"cofog99": {code: label}, "na_item": {code: label}} for this response
    (the full fixed codelist, present regardless of which geo was queried).
    """
    with open(path, encoding="utf-8") as fh:
        payload = json.load(fh)
    dim_ids = payload["id"]
    sizes = payload["size"]
    dims = payload["dimension"]

    position_to_code = {}
    labels = {}
    for dim in dim_ids:
        index = dims[dim]["category"]["index"]
        position_to_code[dim] = {pos: code for code, pos in index.items()}
        if dim in ("cofog99", "na_item"):
            labels[dim] = dict(dims[dim]["category"].get("label", {}))

    records = []
    for flat_str, value in payload.get("value", {}).items():
        if value is None:
            continue
        idxs = _eurostat_decode_flat_index(int(flat_str), sizes)
        combo = {dim: position_to_code[dim][idx] for dim, idx in zip(dim_ids, idxs)}
        try:
            year = int(combo["time"])
        except (KeyError, ValueError):
            continue
        records.append(
            {
                "cofog99": combo.get("cofog99"),
                "na_item": combo.get("na_item"),
                "geo": combo.get("geo"),
                "year": year,
                "value": float(value),
            }
        )
    return records, labels


def eurostat_cofog_parent(code: str) -> str:
    if code == "TOTAL":
        return ""
    if len(code) == 6:
        return code[:4]
    if len(code) == 4:
        return "TOTAL"
    return ""


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------


def _window(year: int) -> str:
    return "train" if year <= TRAIN_MAX_YEAR else "holdout"


def _write_csv(filename: str, fieldnames: list, rows: list) -> str:
    os.makedirs(DERIVED_DIR, exist_ok=True)
    out_path = os.path.join(DERIVED_DIR, filename)
    with open(out_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return out_path


def main() -> None:
    # ---------------- IMF ----------------
    print("Fetching IMF dataflow catalogue (for dataflow versions)...")
    dataflow_versions = imf_fetch_dataflow_versions()

    print("Fetching IMF CL_GFS_INDICATOR codelist...")
    imf_codes = imf_fetch_codelist()
    imf_code_ids = {row["code"] for row in imf_codes}
    cofog_codes = sorted(c for c in imf_code_ids if c.startswith("GF"))
    missing_curated = (set(IMF_SOO_QUERY_CODES) | set(IMF_BS_QUERY_CODES)) - imf_code_ids
    if missing_curated:
        raise RuntimeError(f"Curated IMF codes not found in fetched codelist: {sorted(missing_curated)}")

    print(f"Fetching IMF COFOG data ({len(cofog_codes)} codes, all reporters, {IMF_START_PERIOD}-{IMF_END_PERIOD})...")
    agency, version = dataflow_versions["GFS_COFOG"]
    cofog_records = imf_fetch_data("GFS_COFOG", agency, version, cofog_codes, "cofog")

    print(f"Fetching IMF Statement of Operations data ({len(IMF_SOO_QUERY_CODES)} codes)...")
    agency, version = dataflow_versions["GFS_SOO"]
    soo_records = imf_fetch_data("GFS_SOO", agency, version, IMF_SOO_QUERY_CODES, "soo")

    print(f"Fetching IMF Balance Sheet data ({len(IMF_BS_QUERY_CODES)} codes)...")
    agency, version = dataflow_versions["GFS_BS"]
    bs_records = imf_fetch_data("GFS_BS", agency, version, IMF_BS_QUERY_CODES, "bs")

    imf_all_records = cofog_records + soo_records + bs_records
    imf_measured_codes = sorted(set(cofog_codes) | set(IMF_SOO_QUERY_CODES) | set(IMF_BS_QUERY_CODES))

    # imf_gfs_codelist.csv — full vocabulary
    label_by_code = {row["code"]: row["label_en"] for row in imf_codes}
    cofog_code_set = set(cofog_codes)
    codelist_rows = []
    for row in sorted(imf_codes, key=lambda r: r["code"]):
        codelist_rows.append(
            {
                "codelist_id": "CL_GFS_INDICATOR",
                "code": row["code"],
                "label_en": row["label_en"],
                "parent_code": imf_cofog_parent(row["code"], cofog_code_set),
                "description": row["description"],
            }
        )
    imf_codelist_path = _write_csv(
        "imf_gfs_codelist.csv",
        ["codelist_id", "code", "label_en", "parent_code", "description"],
        codelist_rows,
    )

    # imf_gfs_usage.csv — measured subset only (COFOG + curated top-level economic codes)
    imf_usage_agg = defaultdict(lambda: {"n_observations": 0, "countries": set(), "years": set(), "sum_abs_value": 0.0})
    for rec in imf_all_records:
        win = _window(rec["year"])
        agg = imf_usage_agg[(rec["code"], win)]
        agg["n_observations"] += 1
        agg["countries"].add(rec["country"])
        agg["years"].add(rec["year"])
        agg["sum_abs_value"] += abs(rec["value"])

    imf_usage_rows = []
    for code in imf_measured_codes:
        for win in ("train", "holdout"):
            agg = imf_usage_agg.get((code, win))
            imf_usage_rows.append(
                {
                    "code": code,
                    "label_en": label_by_code.get(code, ""),
                    "window": win,
                    "n_observations": agg["n_observations"] if agg else 0,
                    "n_countries": len(agg["countries"]) if agg else 0,
                    "n_years": len(agg["years"]) if agg else 0,
                    "sum_abs_value": round(agg["sum_abs_value"], 6) if agg else 0.0,
                }
            )
    imf_usage_rows.sort(key=lambda r: (r["code"], r["window"]))
    imf_usage_path = _write_csv(
        "imf_gfs_usage.csv",
        ["code", "label_en", "window", "n_observations", "n_countries", "n_years", "sum_abs_value"],
        imf_usage_rows,
    )

    # ---------------- Eurostat ----------------
    print("Discovering Eurostat gov_10a_exp reporter list...")
    geo_list = eurostat_fetch_geo_list()
    print(f"  {len(geo_list)} real (non-aggregate) reporters: {geo_list}")

    eurostat_records = []
    eurostat_labels = {"cofog99": {}, "na_item": {}}
    for i, geo in enumerate(geo_list, 1):
        print(f"Fetching Eurostat gov_10a_exp for {geo} ({i}/{len(geo_list)})...")
        path = eurostat_fetch_country(geo)
        recs, labels = eurostat_parse(path)
        eurostat_records.extend(recs)
        for dim in ("cofog99", "na_item"):
            eurostat_labels[dim].update(labels.get(dim, {}))

    # eurostat_cofog_codelist.csv
    eurostat_codelist_rows = []
    for dim in ("cofog99", "na_item"):
        for code, label in sorted(eurostat_labels[dim].items()):
            parent = eurostat_cofog_parent(code) if dim == "cofog99" else ""
            eurostat_codelist_rows.append(
                {"dimension": dim, "code": code, "label_en": label, "parent_code": parent}
            )
    eurostat_codelist_path = _write_csv(
        "eurostat_cofog_codelist.csv",
        ["dimension", "code", "label_en", "parent_code"],
        eurostat_codelist_rows,
    )

    # eurostat_cofog_usage.csv — keyed on (cofog99, na_item) pairs x window
    eurostat_usage_agg = defaultdict(
        lambda: {"n_observations": 0, "countries": set(), "years": set(), "sum_abs_value": 0.0}
    )
    for rec in eurostat_records:
        win = _window(rec["year"])
        agg = eurostat_usage_agg[(rec["cofog99"], rec["na_item"], win)]
        agg["n_observations"] += 1
        agg["countries"].add(rec["geo"])
        agg["years"].add(rec["year"])
        agg["sum_abs_value"] += abs(rec["value"])

    eurostat_usage_rows = []
    for (cofog99, na_item, win), agg in eurostat_usage_agg.items():
        eurostat_usage_rows.append(
            {
                "cofog99": cofog99,
                "cofog99_label_en": eurostat_labels["cofog99"].get(cofog99, ""),
                "na_item": na_item,
                "na_item_label_en": eurostat_labels["na_item"].get(na_item, ""),
                "window": win,
                "n_observations": agg["n_observations"],
                "n_countries": len(agg["countries"]),
                "n_years": len(agg["years"]),
                "sum_abs_value": round(agg["sum_abs_value"], 6),
            }
        )
    eurostat_usage_rows.sort(key=lambda r: (r["cofog99"], r["na_item"], r["window"]))
    eurostat_usage_path = _write_csv(
        "eurostat_cofog_usage.csv",
        [
            "cofog99",
            "cofog99_label_en",
            "na_item",
            "na_item_label_en",
            "window",
            "n_observations",
            "n_countries",
            "n_years",
            "sum_abs_value",
        ],
        eurostat_usage_rows,
    )

    # ---------------- Source summary ----------------
    imf_years = {rec["year"] for rec in imf_all_records}
    imf_countries = {rec["country"] for rec in imf_all_records}
    imf_train_obs = sum(1 for rec in imf_all_records if _window(rec["year"]) == "train")
    imf_holdout_obs = sum(1 for rec in imf_all_records if _window(rec["year"]) == "holdout")

    eu_years = {rec["year"] for rec in eurostat_records}
    eu_countries = {rec["geo"] for rec in eurostat_records}
    eu_train_obs = sum(1 for rec in eurostat_records if _window(rec["year"]) == "train")
    eu_holdout_obs = sum(1 for rec in eurostat_records if _window(rec["year"]) == "holdout")

    summary_rows = [
        {
            "source": "imf_gfs",
            "endpoint": f"{IMF_SDMX_BASE}/data/IMF.STA,{{GFS_COFOG|GFS_SOO|GFS_BS}},<version>/...",
            "n_codes": len(codelist_rows),
            "n_countries": len(imf_countries),
            "year_min": min(imf_years) if imf_years else "",
            "year_max": max(imf_years) if imf_years else "",
            "n_observations_train": imf_train_obs,
            "n_observations_holdout": imf_holdout_obs,
            "unit_note": (
                "TYPE_OF_TRANSFORMATION=POGDP_PT (percent of GDP, GFSM2014). Chosen because the "
                "domestic-currency series (XDC) is denominated in each reporter's own currency; "
                "summing it across countries without FX conversion (which this script never performs) "
                "would silently mix currencies. sum_abs_value is a sum of dimensionless percent-of-GDP "
                "ratios, not a monetary total. SECTOR=S13 (general government, consolidated)."
            ),
        },
        {
            "source": "eurostat_gov_10a_exp",
            "endpoint": f"{EUROSTAT_BASE}/{EUROSTAT_DATASET}?format=JSON&unit={EUROSTAT_UNIT}&sector={EUROSTAT_SECTOR}&geo=<geo>",
            "n_codes": len(eurostat_codelist_rows),
            "n_countries": len(eu_countries),
            "year_min": min(eu_years) if eu_years else "",
            "year_max": max(eu_years) if eu_years else "",
            "n_observations_train": eu_train_obs,
            "n_observations_holdout": eu_holdout_obs,
            "unit_note": (
                "unit=MIO_EUR (millions of euro) — Eurostat's own published euro-denominated series "
                "for every reporter, including non-euro-area members; Kontablo performs no currency "
                "conversion of its own. SECTOR=S13 (general government, consolidated)."
            ),
        },
    ]
    summary_path = _write_csv(
        "public_sector_source_summary.csv",
        [
            "source", "endpoint", "n_codes", "n_countries", "year_min", "year_max",
            "n_observations_train", "n_observations_holdout", "unit_note",
        ],
        summary_rows,
    )

    # ---------------- Report ----------------
    holdout_only_imf = {
        code for (code, win) in imf_usage_agg if win == "holdout"
    } - {code for (code, win) in imf_usage_agg if win == "train"}
    holdout_only_eu = {
        (c, n) for (c, n, win) in eurostat_usage_agg if win == "holdout"
    } - {(c, n) for (c, n, win) in eurostat_usage_agg if win == "train"}

    print("\n=== public_sector_gfs_v1 ingestion complete ===")
    print(f"IMF codelist rows: {len(codelist_rows)} -> {imf_codelist_path}")
    print(f"IMF usage rows: {len(imf_usage_rows)} -> {imf_usage_path}")
    print(f"IMF measured codes: {len(imf_measured_codes)} (COFOG {len(cofog_codes)} + curated {len(imf_measured_codes) - len(cofog_codes)})")
    print(f"IMF codes with usage in HOLDOUT but not TRAIN: {len(holdout_only_imf)} {sorted(holdout_only_imf) if holdout_only_imf else ''}")
    print(f"Eurostat codelist rows: {len(eurostat_codelist_rows)} -> {eurostat_codelist_path}")
    print(f"Eurostat usage rows: {len(eurostat_usage_rows)} -> {eurostat_usage_path}")
    print(f"Eurostat (cofog99,na_item) pairs with usage in HOLDOUT but not TRAIN: {len(holdout_only_eu)}")
    print(f"Summary -> {summary_path}")


if __name__ == "__main__":
    main()
