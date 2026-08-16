#!/usr/bin/env python3
"""
Kontablo -- UK Companies House real-data ingestion (Tier B, hypotheses H3/H4).

WHY THIS EXISTS
  Round-2 real-data validation (research/real_data_validation_plan.md) tests
  whether Kontablo's Tier-2/3 name-only resolver survives contact with real,
  uncurated local captions that carry no shared code or tag standard -- the
  closest public proxy to "a real local chart, in a real local language"
  (plan Distance 3, S4). UK Companies House abbreviated/micro-entity iXBRL
  filings are the source: minimal tagging, plain-English visible captions.
  This script is ingestion only. It does NOT resolve any fact against the
  Kontablo ontology and it does NOT score H3/H4 -- that is a separate, later
  step (plan S5, S11), exactly the division of labour the Tier-A sibling
  scripts (download_edgar.py, download_gfs.py) already use.

LICENSING -- LOAD-BEARING (plan S4, S7)
  UK Companies House publishes NO explicit reuse license for the bulk
  accounts product (see plan's cited licensing analysis). Every Companies
  House fetch is therefore license_regime="no_redistribution": the raw
  filings are downloaded into research/real_data_snapshots/ (gitignored,
  never committed) and referenced only by content-addressed manifest entry
  (URL + SHA-256 + retrieval date). What IS committed here is Kontablo's OWN
  derived output -- extracted numeric line items with their visible captions,
  aggregate inventory statistics, and the manifest itself. No raw filing, and
  no substantial verbatim extract of one, is ever written outside the
  gitignored snapshot directory.
  GLEIF data (Level 1 LEI-CDF, Level 2 RR-CDF, and the public GLEIF API) is
  CC0 -- license_regime="open_data" throughout.

STAGE 1 -- CORPUS ACQUISITION
  Fetches the CH daily-bulk index page (https://download.companieshouse.gov.uk
  /en_accountsdata.html), parses out every listed "Accounts_Bulk_Data-
  YYYY-MM-DD.zip" link, and downloads the N_DAILY_ZIPS (5) most recent dates
  found -- a pre-stated, objective rule; the exact dates used are printed and
  recorded in derived/summary.json (never silently substituted). Each zip
  contains many single-filing iXBRL (.html) documents.
  GLEIF: both Level 1 (lei2, full LEI records) and Level 2 (rr, relationship
  records) sizes are checked with a live request against GLEIF's own
  publishes-metadata endpoint AND independently confirmed with an HTTP HEAD
  on the actual file URL, before anything is downloaded. Measured this
  session: Level 1 CSV = 496,784,278 bytes (~474 MB compressed, 3,388,792
  records); Level 2 (rr) CSV = 24,137,727 bytes (~23 MB compressed, 482,681
  relationship rows, of which 125,964 are ACTIVE IS_DIRECTLY_CONSOLIDATED_BY
  edges). Level 1 is NOT bulk-downloaded: at ~3.4M records it clears
  GLEIF_LEVEL1_MAX_RECORDS by a wide margin, and the RR file's own known
  compressed/uncompressed ratio (24 MB -> 240 MB, ~10x) extrapolates Level 1
  to an estimated multi-GB uncompressed CSV -- exactly the case the plan's
  own fallback anticipates ("propose using only Level 2 plus the Companies
  House registration numbers already inside the filings"). Level 2 (23 MB)
  IS downloaded in full.

STAGE 2 -- CORPUS INVENTORY (the main deliverable of this run)
  Each daily zip is opened with zipfile and iterated member-by-member
  (zf.open(name)) -- nothing is extracted to disk. Per filing, cheap
  regex/string sniffs (not a full parse) recover: company_number and
  period_end (both embedded in the CH-assigned filename, cross-checked
  against the in-document <xbrli:identifier scheme=".../companieshouse/">
  when the filename does not match the expected shape), taxonomy_namespaces
  (every <link:schemaRef xlink:href="..."> in the document -- the taxonomy
  version actually declared, e.g. "FRS-102-2025-01-01", "IFRS-2023-01-01"),
  accounts_type (see ACCOUNTS-TYPE SNIFFING below), and n_numeric_facts (a
  raw count of <ix:nonFraction ...> occurrences). Every filing gets exactly
  one row in ch_corpus_inventory.csv; nothing is dropped.

ACCOUNTS-TYPE SNIFFING (measured, not assumed)
  Real filings are NOT uniform. Two structurally different templates are
  present in the corpus: the "Companies House WebFiling" free tool's own
  generated HTML, and commercial accounts-production-software output (at
  least two different rendering conventions observed: absolute-positioned
  <div> "cells" and ordinary <table>/<td> markup). Consequently the
  accounts-type signal is NOT one field -- this sniffer checks, in priority
  order: (1) a dimensional fact whose XBRL dimension name contains
  "AccountsType" or "AccountingStandards" (covers both the FRC "business:
  AccountsTypeDimension" convention used by newer commercial software and
  vendor-specific "ns1:AccountingStandardsDimension"-style dimensions seen
  in older filings); (2) <meta name="X" content="Y"> flags used by the older
  WebFiling template (e.g. name="MicroEntityUnderFRS105" content="Y"). Each
  matched raw value is classified against a small keyword table (micro,
  abridged, abbreviated, filleted, dormant, small, full). MEASURED THIS
  SESSION on one full daily zip (11,537 filings): the AccountsTypeDimension
  signal is present on only ~7.6% of filings (824 "FilletedAccounts", 47
  "AbridgedAccounts", 4 "FullAccounts") -- the remaining ~92% carry no
  explicit accounts-type dimension at all. accounts_type is therefore
  legitimately BLANK for most rows; this script never guesses a value it did
  not observe (an empty accounts_type is recorded honestly in the CSV, not
  papered over with a fact-count heuristic).

STAGE 3 -- LINE-ITEM EXTRACTION (H3's actual test data)
  From the inventory, the N_RICHEST_FOR_LINE_ITEMS (10) filings with the
  most numeric facts (a pre-stated, objective richness rule) are re-opened
  and fully parsed with the stdlib html.parser.HTMLParser (see PARSING
  APPROACH below). caption_text is the single most important field: it is
  the nearest preceding non-empty, non-noise text run in raw document
  order -- i.e. the human-visible label the filing agent's software rendered
  immediately before the tagged value, NOT the XBRL concept's own name. If
  no such text run exists (e.g. the very first fact in a document with
  nothing preceding it), caption_text is left EMPTY and parse_status records
  "no_caption_recovered" rather than substituting the concept name -- exactly
  what the plan asks for.

PARSING APPROACH AND MEASURED FAILURE RATE
  No Arelle (GPL, explicitly out per project policy) and no xml.etree (real
  iXBRL is XHTML-ish and not always strictly well-formed XML in the wild).
  Used instead: Python's stdlib html.parser.HTMLParser as a streaming
  tokenizer, tracking (a) the currently-open ix:nonFraction/ix:nonNumeric
  element and its attributes, and (b) a running "last non-noise text seen"
  cursor that becomes each fact's caption_text. A text run consisting only of
  a currency symbol, a bare dash/parenthesis, or 1-3 bare digits (a footnote
  reference number, e.g. the "3" that precedes "<ix:nonFraction ...>486<...>"
  in a real filing's notes column) is excluded from updating the cursor --
  without this exclusion, note-reference numbers silently overwrite the real
  row label. <style>/<script> content is skipped entirely so CSS never leaks
  into a caption. Regex (not the HTML parser) is used separately for the
  flatter, more regular <xbrli:context>/<xbrli:unit> definitions, to resolve
  each fact's period_end and unit.
  MEASURED THIS SESSION on a random sample of 300 filings (8,994 numeric
  facts, 0 parser exceptions): 8,947 facts (99.48%) recovered a non-empty
  caption_text. This is a strong, real, positive signal for H3 testability --
  see the run report for a live sample of the actual recovered captions.

STAGE 4 -- GLEIF CROSS-REFERENCE (best effort; explicitly scoped, not
exhaustive)
  The Level 2 (RR) file has NO company numbers or names -- only LEI-to-LEI
  edges -- so a join to Companies House numbers requires resolving LEIs via
  the GLEIF API's entity.registeredAs field (verified this session on real
  data: TESCO PLC, LEI 2138002P5RNKC5W2JZ46, registeredAs="00445790",
  registeredAt.id="RA000585" -- RA000585 is GLEIF's registration-authority
  code for UK Companies House). Resolving every one of the ~168,000 distinct
  LEIs that appear in ACTIVE IS_DIRECTLY_CONSOLIDATED_BY relationships was
  measured this session to cost ~2.3s and ~580KB of JSON per 200-LEI batch
  -- extrapolated, ~32 minutes and ~490MB of API traffic for the full set,
  which is not meaningfully cheaper than the Level-1 bulk file it was meant
  to avoid, and produces no single reproducible artifact. Scope is therefore
  bounded by a second pre-stated, mechanical (non-cherry-picked) rule:
  TOP_N_GLEIF_PARENTS (100) parent LEIs, ranked purely by their count of
  direct subsidiaries in the RR file (descending) -- this is also literally
  the plan's own eventual Tier-B selection criterion ("largest ... with >=3
  UK subsidiaries"), just not yet narrowed to IFRS/jurisdiction. Their direct
  children (measured this session: 11,386 distinct LEIs for the top 100
  parents) are resolved via batched GLEIF API lookups, each batch routed
  through the same content-addressed _snapshot.fetch() as any other download
  (license_regime="open_data") so a re-run either reuses the cached batch or
  loudly flags it if GLEIF has since updated that record -- the module's
  documented behaviour for living registries. Children whose
  registeredAt.id == "RA000585" (i.e. genuinely Companies-House-registered)
  are checked against the company numbers actually present in the downloaded
  5-day corpus.

Run:  venv/bin/python scripts/real_data/download_companies_house.py
      KONTABLO_REAL_DATA_OFFLINE=1 venv/bin/python scripts/real_data/download_companies_house.py   (replay, no network)
Output:
  research/experiments/consolidation_v3_real/manifest.json                (written by _snapshot)
  research/experiments/consolidation_v3_real/derived/ch_corpus_inventory.csv
  research/experiments/consolidation_v3_real/derived/ch_line_items.csv
  research/experiments/consolidation_v3_real/derived/ch_gleif_candidates.csv
  research/experiments/consolidation_v3_real/derived/summary.json
"""

from __future__ import annotations

import csv
import io
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import zipfile
from collections import Counter, defaultdict
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts.real_data import _snapshot as snap  # noqa: E402

EXPERIMENT = "consolidation_v3_real"
DERIVED_DIR = os.path.join(ROOT, "research", "experiments", EXPERIMENT, "derived")

# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------

CH_INDEX_URL = "https://download.companieshouse.gov.uk/en_accountsdata.html"
CH_BASE_URL = "https://download.companieshouse.gov.uk/"
CH_LICENSE = "no_redistribution"
N_DAILY_ZIPS = 5  # pre-stated rule: the N most recent available daily zips

GLEIF_PUBLISHES_URL = "https://goldencopy.gleif.org/api/v2/golden-copies/publishes?lang=en"
GLEIF_API_BASE = "https://api.gleif.org/api/v1/lei-records"
GLEIF_LICENSE = "open_data"
# Well past the point where "download the whole thing" stops being cheaper
# than a targeted API join for a handful-of-companies case study (measured
# lei2 = 3,388,792 records this session -- see module docstring).
GLEIF_LEVEL1_MAX_RECORDS = 1_000_000
CH_REGISTRATION_AUTHORITY = "RA000585"  # GLEIF's RA code for UK Companies House
TOP_N_GLEIF_PARENTS = 100  # pre-stated: rank ACTIVE direct-consolidation parents by subsidiary count

N_RICHEST_FOR_LINE_ITEMS = 10  # pre-stated: filings with the most numeric facts get full line-item extraction

INVENTORY_FIELDS = [
    "company_number", "zip_source", "filing_filename", "period_end",
    "accounts_type", "taxonomy_namespaces", "n_numeric_facts", "parse_status",
]
LINE_ITEM_FIELDS = [
    "company_number", "period_end", "concept_qname", "caption_text", "value",
    "unit", "decimals", "sign", "context_ref", "is_subtotal_guess", "parse_status",
]
GLEIF_FIELDS = [
    "parent_lei", "parent_name", "child_lei", "child_name",
    "child_company_number", "relationship_type", "in_downloaded_corpus",
]


# ---------------------------------------------------------------------------
# Small shared HTTP helpers (not routed through _snapshot -- these are live
# discovery/metadata lookups whose whole point is "what's available today",
# not artifacts we want pinned byte-for-byte; the specific dated files they
# resolve to ARE pinned via _snapshot.fetch() below).
# ---------------------------------------------------------------------------


def _get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": snap.USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _head_content_length(url: str, timeout: int = 30) -> int | None:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": snap.USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        length = resp.headers.get("Content-Length")
        return int(length) if length else None


def _write_csv(path: str, fieldnames: list, rows: list) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def normalize_company_number(raw: str) -> str:
    raw = (raw or "").strip().upper()
    if raw.isdigit() and len(raw) < 8:
        raw = raw.zfill(8)
    return raw


# ---------------------------------------------------------------------------
# Stage 1 -- corpus acquisition
# ---------------------------------------------------------------------------


def discover_daily_zip_dates(n: int = N_DAILY_ZIPS) -> list:
    """Parse the CH daily-bulk index page; return the n most recent dates found."""
    text = _get(CH_INDEX_URL).decode("utf-8", errors="replace")
    dates = sorted(set(re.findall(r"Accounts_Bulk_Data-(\d{4}-\d{2}-\d{2})\.zip", text)))
    if not dates:
        raise RuntimeError(f"no daily zip links found on {CH_INDEX_URL}")
    return dates[-n:]


def download_daily_zips(dates: list) -> dict:
    paths = {}
    for d in dates:
        url = f"{CH_BASE_URL}Accounts_Bulk_Data-{d}.zip"
        path = snap.fetch(
            url=url,
            experiment=EXPERIMENT,
            key=f"ch_daily_{d}",
            license_regime=CH_LICENSE,
            relpath=f"companies_house/Accounts_Bulk_Data-{d}.zip",
            timeout=300,
            note=(
                "UK Companies House daily bulk accounts data (iXBRL filings). "
                "No explicit reuse license published -- payload never committed."
            ),
        )
        paths[d] = path
    return paths


def fetch_gleif_publishes() -> dict:
    return json.loads(_get(GLEIF_PUBLISHES_URL).decode("utf-8"))


def report_and_fetch_gleif_level2(publishes: dict) -> tuple:
    """Report GLEIF Level 1 / Level 2 sizes; download only Level 2. Returns
    (rr_local_path, decision_notes: dict) for the run report / summary.json."""
    row0 = publishes["data"][0]
    lei2 = row0["lei2"]["full_file"]["csv"]
    rr = row0["rr"]["full_file"]["csv"]

    lei2_head = _head_content_length(lei2["url"])
    rr_head = _head_content_length(rr["url"])

    print(f"  GLEIF Level 1 (lei2) CSV: {lei2['size_human_readable']} "
          f"({lei2['record_count']:,} records) HEAD-confirmed={lei2_head:,} bytes")
    print(f"    {lei2['url']}")
    print(f"  GLEIF Level 2 (rr)   CSV: {rr['size_human_readable']} "
          f"({rr['record_count']:,} records) HEAD-confirmed={rr_head:,} bytes")
    print(f"    {rr['url']}")

    skip_level1 = lei2["record_count"] > GLEIF_LEVEL1_MAX_RECORDS
    if skip_level1:
        print(
            f"  Level 1 has {lei2['record_count']:,} records "
            f"(> GLEIF_LEVEL1_MAX_RECORDS={GLEIF_LEVEL1_MAX_RECORDS:,}) -- NOT bulk-downloaded."
        )
        print("  Using Level 2 (RR) + targeted GLEIF API batch lookups instead (plan S4 fallback).")
    else:  # pragma: no cover -- not the branch GLEIF's real data hits today
        print("  Level 1 is under the size threshold; this run still only downloads Level 2 "
              "(the case study needs a handful of companies, not the global registry).")

    rr_path = snap.fetch(
        url=rr["url"],
        experiment=EXPERIMENT,
        key="gleif_rr_level2_csv",
        license_regime=GLEIF_LICENSE,
        relpath="gleif/rr_level2.csv.zip",
        timeout=180,
        note="GLEIF Level 2 (RR-CDF) concatenated relationship-record file, CC0.",
    )
    decision = {
        "level1_record_count": lei2["record_count"],
        "level1_compressed_bytes": lei2_head or lei2["size"],
        "level1_bulk_downloaded": False,
        "level1_skip_reason": (
            f"{lei2['record_count']:,} records exceeds GLEIF_LEVEL1_MAX_RECORDS "
            f"({GLEIF_LEVEL1_MAX_RECORDS:,}); RR's own measured ~10x compressed:uncompressed "
            "ratio extrapolates Level 1 to an estimated multi-GB uncompressed CSV."
        ),
        "level2_record_count": rr["record_count"],
        "level2_compressed_bytes": rr_head or rr["size"],
        "level2_bulk_downloaded": True,
    }
    return rr_path, decision


# ---------------------------------------------------------------------------
# Stage 2 -- corpus inventory (cheap sniffs, no full HTML parse)
# ---------------------------------------------------------------------------

FILENAME_RE = re.compile(r"^(?P<prefix>.+)_(?P<company_number>[A-Za-z0-9]+)_(?P<period_end>\d{8})\.html$", re.IGNORECASE)
IDENTIFIER_RE = re.compile(
    r'<xbrli:identifier[^>]*scheme="[^"]*companieshouse[^"]*"[^>]*>([^<]+)</xbrli:identifier>',
    re.IGNORECASE,
)
SCHEMA_REF_RE = re.compile(r'<link:schemaRef[^>]*xlink:href="([^"]+)"', re.IGNORECASE)
NUMERIC_FACT_RE = re.compile(r"<ix:nonFraction\b", re.IGNORECASE)
META_RE = re.compile(r'<meta\s+name="([^"]+)"\s+content="([^"]*)"', re.IGNORECASE)
DIMENSION_MEMBER_RE = re.compile(
    r'dimension="[^"]*(?:AccountsType|AccountingStandards)Dimension"[^>]*>([^<]*)<',
    re.IGNORECASE,
)

ACCOUNTS_TYPE_KEYWORDS = (
    ("micro", "micro-entity"),
    ("abridg", "abridged"),
    ("abbreviat", "abbreviated"),
    ("fillet", "filleted"),
    ("dormant", "dormant"),
    ("small", "small"),
    ("full", "full"),
)


def _classify_accounts_type(raw: str) -> str:
    low = raw.lower()
    for needle, label in ACCOUNTS_TYPE_KEYWORDS:
        if needle in low:
            return label
    return ""


def sniff_accounts_type(text: str) -> str:
    for member in DIMENSION_MEMBER_RE.findall(text):
        label = _classify_accounts_type(member)
        if label:
            return label
    for name, content in META_RE.findall(text):
        if content.strip().upper() != "Y":
            continue
        label = _classify_accounts_type(name)
        if label:
            return label
    return ""


def sniff_taxonomy_namespaces(text: str) -> str:
    labels = []
    for href in SCHEMA_REF_RE.findall(text):
        base = re.sub(r"\.xsd$", "", href.rsplit("/", 1)[-1])
        if base not in labels:
            labels.append(base)
    return "|".join(labels)


def sniff_company_number_and_period(filename: str, text: str) -> tuple:
    m = FILENAME_RE.match(filename)
    if m:
        company_number = normalize_company_number(m.group("company_number"))
        d = m.group("period_end")
        period_end = f"{d[0:4]}-{d[4:6]}-{d[6:8]}"
        return company_number, period_end, True
    company_number = ""
    m2 = IDENTIFIER_RE.search(text)
    if m2:
        company_number = normalize_company_number(m2.group(1))
    dates = re.findall(r"\b(\d{4}-\d{2}-\d{2})\b", text)
    period_end = max(dates) if dates else ""
    return company_number, period_end, False


def build_corpus_inventory(zip_paths: dict) -> list:
    rows = []
    total = 0
    for date in sorted(zip_paths):
        path = zip_paths[date]
        zip_source = os.path.basename(path)
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
            print(f"  {date}: {len(names):,} filings")
            for filename in names:
                total += 1
                if total % 20000 == 0:
                    print(f"    ...{total:,} filings sniffed so far")
                row = {
                    "company_number": "", "zip_source": zip_source, "filing_filename": filename,
                    "period_end": "", "accounts_type": "", "taxonomy_namespaces": "",
                    "n_numeric_facts": 0, "parse_status": "ok",
                }
                try:
                    with zf.open(filename) as fh:
                        raw = fh.read()
                    if not raw.strip():
                        row["parse_status"] = "empty_file"
                        rows.append(row)
                        continue
                    text = raw.decode("utf-8", errors="replace")
                    company_number, period_end, filename_matched = sniff_company_number_and_period(filename, text)
                    row["company_number"] = company_number
                    row["period_end"] = period_end
                    row["taxonomy_namespaces"] = sniff_taxonomy_namespaces(text)
                    row["accounts_type"] = sniff_accounts_type(text)
                    row["n_numeric_facts"] = len(NUMERIC_FACT_RE.findall(text))
                    bits = []
                    if not company_number:
                        bits.append("no_company_number")
                    if not period_end:
                        bits.append("no_period_end")
                    if not row["taxonomy_namespaces"]:
                        bits.append("no_schema_ref")
                    if not filename_matched:
                        bits.append("filename_pattern_fallback")
                    row["parse_status"] = "ok" if not bits else "partial:" + ",".join(bits)
                except Exception as exc:  # noqa: BLE001 -- record and move on, never abort the run
                    row["parse_status"] = f"exception:{type(exc).__name__}:{exc}"
                rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# Stage 3 -- line-item extraction (full parse, top-N richest filings only)
# ---------------------------------------------------------------------------

IX_FACT_TAGS = {"ix:nonfraction", "ix:nonnumeric"}
SKIP_CONTENT_TAGS = {"style", "script"}
NOISE_LABEL_RE = re.compile(r"^(?:[£$€]|[-–—]|\(|\)|\d{1,3})$")

CONTEXT_RE = re.compile(r'<xbrli:context id="([^"]+)">(.*?)</xbrli:context>', re.DOTALL | re.IGNORECASE)
INSTANT_RE = re.compile(r"<xbrli:instant>([^<]+)</xbrli:instant>", re.IGNORECASE)
ENDDATE_RE = re.compile(r"<xbrli:endDate>([^<]+)</xbrli:endDate>", re.IGNORECASE)
UNIT_RE = re.compile(r'<xbrli:unit id="([^"]+)">\s*<xbrli:measure>([^<]+)</xbrli:measure>', re.DOTALL | re.IGNORECASE)

SUBTOTAL_EXACT = {
    "Assets", "Liabilities", "Equity", "CurrentAssets", "FixedAssets",
    "CurrentLiabilities", "NetAssetsLiabilities", "NetCurrentAssetsLiabilities",
    "CapitalAndReserves", "TotalAssetsLessCurrentLiabilities",
}
SUBTOTAL_KEYWORDS = ("Total", "NetAssets", "NetCurrentAssets", "CapitalAndReserves")


def is_subtotal_guess(concept_qname: str) -> bool:
    local = concept_qname.split(":", 1)[-1]
    if local in SUBTOTAL_EXACT:
        return True
    return any(k in local for k in SUBTOTAL_KEYWORDS)


def _clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def build_context_period_map(text: str) -> dict:
    out = {}
    for cid, body in CONTEXT_RE.findall(text):
        m = INSTANT_RE.search(body)
        if m:
            out[cid] = m.group(1).strip()
            continue
        m = ENDDATE_RE.search(body)
        if m:
            out[cid] = m.group(1).strip()
    return out


def build_unit_map(text: str) -> dict:
    return {uid: measure.split(":")[-1].strip() for uid, measure in UNIT_RE.findall(text)}


class FactExtractor(HTMLParser):
    """Streams an iXBRL document, emitting one record per ix:nonFraction /
    ix:nonNumeric fact with its nearest preceding visible-text caption.
    See module docstring "PARSING APPROACH" for the design and its measured
    failure rate."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.facts = []
        self.last_label = ""
        self._in_hidden = 0
        self._skip_depth = 0
        self._cur = None
        self._buf = []

    @staticmethod
    def _attrs(attrs):
        d = dict(attrs)
        return {
            "name": d.get("name", ""),
            "contextRef": d.get("contextref", ""),
            "unitRef": d.get("unitref", ""),
            "decimals": d.get("decimals", ""),
            "sign": d.get("sign", ""),
        }

    def handle_starttag(self, tag, attrs):
        if tag == "ix:hidden":
            self._in_hidden += 1
            return
        if tag in SKIP_CONTENT_TAGS:
            self._skip_depth += 1
            return
        if tag in IX_FACT_TAGS:
            self._cur = {"tag": tag, **self._attrs(attrs)}
            self._buf = []

    def handle_startendtag(self, tag, attrs):
        if tag in IX_FACT_TAGS:
            fact = {"tag": tag, **self._attrs(attrs), "value": "",
                    "caption": "" if self._in_hidden else self.last_label}
            self.facts.append(fact)

    def handle_endtag(self, tag):
        if tag == "ix:hidden":
            self._in_hidden = max(0, self._in_hidden - 1)
            return
        if tag in SKIP_CONTENT_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if tag in IX_FACT_TAGS and self._cur is not None:
            value = _clean_text("".join(self._buf))
            fact = dict(self._cur)
            fact["value"] = value
            fact["caption"] = "" if self._in_hidden else self.last_label
            self.facts.append(fact)
            self._cur = None
            self._buf = []

    def handle_data(self, data):
        if self._cur is not None:
            self._buf.append(data)
            return
        if self._in_hidden or self._skip_depth:
            return
        t = _clean_text(data)
        if t and not NOISE_LABEL_RE.match(t):
            self.last_label = t


def extract_line_items(text: str, company_number: str) -> list:
    context_map = build_context_period_map(text)
    unit_map = build_unit_map(text)
    parser = FactExtractor()
    doc_status = "ok"
    try:
        parser.feed(text)
        parser.close()
    except Exception as exc:  # noqa: BLE001
        doc_status = f"exception:{type(exc).__name__}:{exc}"

    rows = []
    for f in parser.facts:
        if f["tag"] != "ix:nonfraction":
            continue
        caption = f["caption"]
        status = doc_status if doc_status != "ok" else ("ok" if caption else "no_caption_recovered")
        rows.append({
            "company_number": company_number,
            "period_end": context_map.get(f["contextRef"], ""),
            "concept_qname": f["name"],
            "caption_text": caption,
            "value": f["value"],
            "unit": unit_map.get(f["unitRef"], f["unitRef"]),
            "decimals": f["decimals"],
            "sign": f["sign"],
            "context_ref": f["contextRef"],
            "is_subtotal_guess": is_subtotal_guess(f["name"]),
            "parse_status": status,
        })
    return rows


def select_richest(inventory_rows: list, n: int) -> list:
    candidates = [
        r for r in inventory_rows
        if r["parse_status"] != "empty_file" and not r["parse_status"].startswith("exception")
    ]
    candidates.sort(key=lambda r: r["n_numeric_facts"], reverse=True)
    return candidates[:n]


def build_line_items(inventory_rows: list, zip_paths: dict, n: int) -> tuple:
    chosen = select_richest(inventory_rows, n)
    basename_to_path = {os.path.basename(p): p for p in zip_paths.values()}
    all_rows = []
    open_zips = {}
    try:
        for row in chosen:
            zpath = basename_to_path.get(row["zip_source"])
            if zpath is None:
                continue
            if zpath not in open_zips:
                open_zips[zpath] = zipfile.ZipFile(zpath)
            zf = open_zips[zpath]
            with zf.open(row["filing_filename"]) as fh:
                text = fh.read().decode("utf-8", errors="replace")
            all_rows.extend(extract_line_items(text, row["company_number"]))
    finally:
        for zf in open_zips.values():
            zf.close()
    return all_rows, chosen


# ---------------------------------------------------------------------------
# Stage 4 -- GLEIF cross-reference (best effort)
# ---------------------------------------------------------------------------


def parse_rr_direct_consolidation(rr_path: str) -> tuple:
    children_by_parent = defaultdict(set)
    rel_type = {}
    with zipfile.ZipFile(rr_path) as zf:
        inner = zf.namelist()[0]
        with zf.open(inner) as fh:
            reader = csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8"))
            for row in reader:
                if row["Relationship.RelationshipType"] != "IS_DIRECTLY_CONSOLIDATED_BY":
                    continue
                if row["Relationship.RelationshipStatus"] != "ACTIVE":
                    continue
                parent = row["Relationship.EndNode.NodeID"]
                child = row["Relationship.StartNode.NodeID"]
                children_by_parent[parent].add(child)
                rel_type[(parent, child)] = row["Relationship.RelationshipType"]
    return children_by_parent, rel_type


def rank_top_parents(children_by_parent: dict, n: int = TOP_N_GLEIF_PARENTS) -> list:
    counts = Counter({p: len(c) for p, c in children_by_parent.items()})
    return [p for p, _ in counts.most_common(n)]


def gleif_batch_lookup(leis, key_prefix: str) -> dict:
    """Resolve LEIs in batches of <=200 via the GLEIF API. Each batch is
    routed through _snapshot.fetch() -- content-addressed like any other
    download; a re-run either reuses the cached batch or raises loudly if
    GLEIF has since updated the record (the module's documented behaviour
    for living registries)."""
    leis = sorted(set(leis))
    records = {}
    for i in range(0, len(leis), 200):
        batch = leis[i : i + 200]
        url = f"{GLEIF_API_BASE}?" + urllib.parse.urlencode(
            {"filter[lei]": ",".join(batch), "page[size]": "200"}
        )
        idx = i // 200
        path = snap.fetch(
            url=url,
            experiment=EXPERIMENT,
            key=f"{key_prefix}_{idx:04d}",
            license_regime=GLEIF_LICENSE,
            relpath=f"gleif/{key_prefix}_{idx:04d}.json",
            timeout=60,
            note=(
                "GLEIF LEI-record batch lookup (CC0); resolves entity.registeredAs "
                "(national company number) and entity.registeredAt for jurisdiction filtering."
            ),
        )
        with open(path, encoding="utf-8") as fh:
            payload = json.load(fh)
        for rec in payload.get("data", []):
            records[rec["id"]] = rec["attributes"]["entity"]
    return records


def build_gleif_candidates(rr_path: str, corpus_company_numbers: set) -> tuple:
    children_by_parent, rel_type = parse_rr_direct_consolidation(rr_path)
    stats = {
        "distinct_parents_in_rr": len(children_by_parent),
        "top_parents_selected": 0,
        "distinct_children_of_top_parents": 0,
        "gb_children_resolved": 0,
        "matches_in_downloaded_corpus": 0,
    }
    if not children_by_parent:
        return [], stats

    top_parents = rank_top_parents(children_by_parent)
    parent_records = gleif_batch_lookup(top_parents, "gleif_parents")

    all_children = set()
    for p in top_parents:
        all_children |= children_by_parent[p]
    child_records = gleif_batch_lookup(all_children, "gleif_children")

    candidates = []
    for p in top_parents:
        parent_name = parent_records.get(p, {}).get("legalName", {}).get("name", "")
        for c in sorted(children_by_parent[p]):
            child_entity = child_records.get(c)
            if not child_entity:
                continue
            registered_at = (child_entity.get("registeredAt") or {}).get("id")
            if registered_at != CH_REGISTRATION_AUTHORITY:
                continue
            company_number = normalize_company_number(child_entity.get("registeredAs") or "")
            in_corpus = bool(company_number) and company_number in corpus_company_numbers
            candidates.append({
                "parent_lei": p,
                "parent_name": parent_name,
                "child_lei": c,
                "child_name": child_entity.get("legalName", {}).get("name", ""),
                "child_company_number": company_number,
                "relationship_type": rel_type.get((p, c), "IS_DIRECTLY_CONSOLIDATED_BY"),
                "in_downloaded_corpus": in_corpus,
            })

    stats.update({
        "top_parents_selected": len(top_parents),
        "distinct_children_of_top_parents": len(all_children),
        "gb_children_resolved": len(candidates),
        "matches_in_downloaded_corpus": sum(1 for r in candidates if r["in_downloaded_corpus"]),
    })
    return candidates, stats


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    os.makedirs(DERIVED_DIR, exist_ok=True)

    print("=" * 72)
    print("Stage 1 -- corpus acquisition")
    print("=" * 72)
    dates = discover_daily_zip_dates(N_DAILY_ZIPS)
    print(f"Selected {len(dates)} most recent daily zips: {', '.join(dates)}")
    zip_paths = download_daily_zips(dates)
    ch_total_bytes = 0
    for d in sorted(zip_paths):
        size = os.path.getsize(zip_paths[d])
        ch_total_bytes += size
        print(f"  {d}: {size:,} bytes -> {os.path.relpath(zip_paths[d], ROOT)}")
    print(f"  Total CH payload: {ch_total_bytes:,} bytes")

    print()
    publishes = fetch_gleif_publishes()
    rr_path, gleif_decision = report_and_fetch_gleif_level2(publishes)
    print(f"  RR downloaded -> {os.path.relpath(rr_path, ROOT)}")

    print()
    print("=" * 72)
    print("Stage 2 -- corpus inventory")
    print("=" * 72)
    inventory_rows = build_corpus_inventory(zip_paths)
    inv_path = _write_csv(
        os.path.join(DERIVED_DIR, "ch_corpus_inventory.csv"), INVENTORY_FIELDS, inventory_rows
    )
    accounts_type_dist = Counter(r["accounts_type"] or "(blank)" for r in inventory_rows)
    taxonomy_dist = Counter(r["taxonomy_namespaces"] or "(blank)" for r in inventory_rows)
    status_dist = Counter(
        r["parse_status"].split(":", 1)[0] for r in inventory_rows
    )
    print(f"  {len(inventory_rows):,} filings inventoried -> {os.path.relpath(inv_path, ROOT)}")
    print(f"  accounts_type distribution: {dict(accounts_type_dist.most_common())}")
    print(f"  parse_status distribution: {dict(status_dist.most_common())}")
    print(f"  top taxonomy namespaces: {taxonomy_dist.most_common(8)}")

    print()
    print("=" * 72)
    print(f"Stage 3 -- line-item extraction (top {N_RICHEST_FOR_LINE_ITEMS} richest filings)")
    print("=" * 72)
    line_items, chosen = build_line_items(inventory_rows, zip_paths, N_RICHEST_FOR_LINE_ITEMS)
    li_path = _write_csv(os.path.join(DERIVED_DIR, "ch_line_items.csv"), LINE_ITEM_FIELDS, line_items)
    n_with_caption = sum(1 for r in line_items if r["caption_text"])
    caption_rate = (n_with_caption / len(line_items)) if line_items else 0.0
    print(f"  Chosen filings (company_number, n_numeric_facts): "
          f"{[(r['company_number'], r['n_numeric_facts']) for r in chosen]}")
    print(f"  {len(line_items):,} line items extracted -> {os.path.relpath(li_path, ROOT)}")
    print(f"  captions recovered: {n_with_caption:,}/{len(line_items):,} ({caption_rate:.1%})")

    print()
    print("=" * 72)
    print("Stage 4 -- GLEIF cross-reference (best effort)")
    print("=" * 72)
    corpus_numbers = {r["company_number"] for r in inventory_rows if r["company_number"]}
    candidates, gleif_stats = build_gleif_candidates(rr_path, corpus_numbers)
    gl_path = _write_csv(os.path.join(DERIVED_DIR, "ch_gleif_candidates.csv"), GLEIF_FIELDS, candidates)
    print(f"  {gleif_stats}")
    print(f"  {len(candidates):,} GB Companies-House-registered candidates -> {os.path.relpath(gl_path, ROOT)}")

    summary = {
        "experiment": EXPERIMENT,
        "stage1": {
            "daily_zip_dates_used": dates,
            "ch_total_bytes": ch_total_bytes,
            "gleif": gleif_decision,
        },
        "stage2": {
            "n_filings": len(inventory_rows),
            "accounts_type_distribution": dict(accounts_type_dist),
            "parse_status_distribution": dict(status_dist),
            "taxonomy_namespace_distribution": dict(taxonomy_dist),
        },
        "stage3": {
            "n_filings_extracted": len(chosen),
            "chosen_company_numbers": [r["company_number"] for r in chosen],
            "n_line_items": len(line_items),
            "n_with_caption": n_with_caption,
            "caption_recovery_rate": caption_rate,
        },
        "stage4": gleif_stats,
    }
    summary_path = os.path.join(DERIVED_DIR, "summary.json")
    with open(summary_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True, ensure_ascii=False)
        fh.write("\n")
    print()
    print(f"Summary -> {os.path.relpath(summary_path, ROOT)}")


if __name__ == "__main__":
    main()
