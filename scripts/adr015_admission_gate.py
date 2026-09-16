#!/usr/bin/env python3
"""ADR-015 core-node admission gate, run against REAL filing frequencies.

WHY THIS SCRIPT EXISTS
======================
ADR-015 makes core-node growth evidence-gated: a candidate is admitted only if
all five criteria (A1..A5) hold, and A1 -- "material, measured volume" -- must be
*measured*, never asserted. Until round 2 the only committed frequency
distribution was the synthetic one behind ``coverage_benchmark.py``, so A1 could
only ever be exercised against numbers Kontablo itself generated. Round 2
committed 5.44M real SEC EDGAR face-statement facts, 38,893 ESEF facts and the
IMF/Eurostat government-finance census. This script runs the candidate list the
round-2 gold pass produced through A1..A5 against those real distributions.

It is a GOVERNANCE artifact, not a scorer. It changes no hypothesis result and
re-scores nothing. Its output is a decision record.

WHAT A1 CAN AND CANNOT MEASURE HERE -- READ BEFORE USING A NUMBER
================================================================
ADR-015 defines A1 as a share of *routine posting volume*. EDGAR and ESEF
measure something different: how often a concept is **presented as a fact on a
face statement**. Those are not the same quantity and they do not rank concepts
the same way. A monthly depreciation posting is high-frequency in a ledger and
appears at most once a year on a face statement -- usually only in the notes,
which the round-2 derived corpus deliberately excludes.

So the threshold cannot simply be carried over. ADR-015 does not define ~0.5%
axiomatically; it defines it *operationally*, as "roughly the marginal
contribution of the smallest of the four extended nodes already admitted". This
script therefore re-derives the floor the same way on the new population: it
measures the four ALREADY-ADMITTED extended-core nodes against EDGAR and takes
the smallest as the calibrated floor. Both verdicts are reported for every
candidate -- against the literal 0.5% and against the re-derived floor -- so a
reader can apply either and see where they disagree.

If the four admitted nodes themselves fall below 0.5% on EDGAR, that is not a
finding about those nodes; it is proof that the literal threshold does not
transfer between populations. Applying it anyway would reject the very nodes
ADR-015 already admitted -- a reductio, and the reason the re-derivation exists.

DETERMINISM (principle #5)
==========================
Every candidate and every calibration anchor is an EXPLICIT, ENUMERATED tag
list, never a regex over the taxonomy. A regex is how you accidentally count
``StockIssuedDuringPeriodValueRestrictedStockAward`` as restricted *cash*, or a
cash-flow roll-forward as a balance -- which is precisely the over-mapping
failure mode H1 exposed (87 of 320 codes mapped where the gold says escalate).
Enumeration is auditable line by line; a regex is not.

Run:  python scripts/adr015_admission_gate.py
Out:  research/experiments/adr015_admission_v1/results.json
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core.harness.ontology import load_ontology  # noqa: E402
from scripts.real_data.resolve_real_facts import load_inventory  # noqa: E402

OUT_DIR = os.path.join(ROOT, "research/experiments/adr015_admission_v1")

# ---------------------------------------------------------------------------
# Population definitions -- stated before any number is read.
# ---------------------------------------------------------------------------
# A1 denominator: EDGAR standard-taxonomy monetary face-statement facts, both
# windows pooled. Standard-only because an issuer extension is by definition not
# a shared concept and cannot motivate a universal node (that is H2's territory).
# Monetary-only because Kontablo maps monetary balances; share counts and
# per-share amounts are structurally out of scope (resolve_real_facts.py:111).
# Both windows pooled because this is a governance measurement of how often a
# concept is used, not a held-out predictive evaluation -- there is nothing here
# to overfit, and pooling doubles the observation base.
EDGAR_FILTER = dict(source="edgar", taxonomy_class="standard", measure_class="monetary")

# Tag-inclusion rule, applied uniformly to anchors and candidates alike:
#   1. BALANCES AND PERIOD FLOWS ONLY. Roll-forward and movement elements
#      (``PeriodIncreaseDecrease``, ``EffectOfExchangeRate``, ``WriteOffs``,
#      ``Recoveries``, ``Additions``) describe a change in a balance, not an
#      account. Round 2's Addendum A.5 made the same cut for Tier B.
#   2. TIER MUST MATCH THE NODE. A current-only node does not get credit for
#      facts tagged explicitly non-current. Untiered variants of the same
#      concept are counted, and flagged, because filers use them for the
#      dominant (current) tier.
#   3. NO SUPERSET ELEMENTS. ``OtherLiabilitiesNoncurrent`` is an
#      undifferentiated residual bucket, not a provision; counting it would
#      manufacture volume for a node it does not evidence.

# ---------------------------------------------------------------------------
# Calibration anchors: the FOUR nodes ADR-015 has already admitted.
# ---------------------------------------------------------------------------
CALIBRATION_ANCHORS = [
    {
        "node": "liability.current.payroll",
        "label": "Payroll liabilities (wages & statutory withholdings)",
        "edgar_tags": [
            "EmployeeRelatedLiabilitiesCurrent",
            "AccruedSalariesCurrent",
            "AccruedEmployeeBenefitsCurrent",
            "AccruedPayrollTaxesCurrent",
            "AccruedBonusesCurrent",
            "AccruedVacationCurrent",
        ],
    },
    {
        "node": "liability.current.deferred_revenue",
        "label": "Contract liabilities / deferred revenue (IFRS 15)",
        "edgar_tags": [
            "ContractWithCustomerLiabilityCurrent",
            "DeferredRevenueCurrent",
            "ContractWithCustomerLiability",
            "DeferredRevenue",
        ],
    },
    {
        "node": "asset.current.withholding_tax",
        "label": "Tax withheld at source / tax credits receivable",
        "edgar_tags": [
            "IncomeTaxesReceivable",
            "IncomeTaxReceivable",
            "PrepaidTaxes",
        ],
    },
    {
        "node": "asset.current.other_receivables",
        "label": "Other / non-trade receivables",
        "edgar_tags": [
            "OtherReceivablesNetCurrent",
            "OtherReceivables",
            "OtherReceivablesGrossCurrent",
        ],
    },
]

# ---------------------------------------------------------------------------
# Candidates. Source: the round-2 gold pass. Every one is backed by a labeler
# note in research/experiments/tag_resolution_v1/gold/labels_{A,B}.csv recording
# that a real filed concept had no home in the ontology.
#
# A2/A3/A4/A5 fields are RECORDED JUDGEMENT with their basis, per ADR-015's own
# statement that A4 and A5 "are not fully mechanical; they require an accounting
# judgement call, recorded in the proposal". A1 and the A2 attestation count and
# the A3 collision check are computed; nothing else is.
# ---------------------------------------------------------------------------
CANDIDATES = [
    {
        "id": "liability.current.lease",
        "title": "Current portion of lease liabilities (IFRS 16 / ASC 842)",
        "corpus": "edgar",
        "edgar_tags": ["OperatingLeaseLiabilityCurrent", "FinanceLeaseLiabilityCurrent"],
        "esef_concepts": ["CurrentLeaseLiabilities"],
        "proposed": {
            "ifrs_tag": "ifrs-full:CurrentLeaseLiabilities",
            "nature": "credit",
            "statement": "balance_sheet",
            "parent": "liability.current",
        },
        "a2": {
            "verdict": "pass",
            "basis": "IFRS 16 (mandatory 2019-01-01) and ASC 842 both require the "
                     "current/non-current split of the lease liability, so the concept "
                     "is not chart-family specific. ifrs-full:CurrentLeaseLiabilities is "
                     "a distinct element of the IFRS taxonomy and is attested in the "
                     "round-2 ESEF corpus (count computed below).",
        },
        "a3": {
            "verdict": "pass",
            "basis": "Fixed nature (credit), fixed statement (balance_sheet), and a "
                     "distinct IFRS anchor that collides with none of the 27 tags "
                     "already in use (checked mechanically below). The boundary is "
                     "binary: the portion of the lease liability due within twelve "
                     "months of the reporting date.",
        },
        "a4": {
            "verdict": "pass",
            "basis": "Not representable today. liability.noncurrent.lease is explicitly "
                     "non-current, and its own notes field concedes the balance is "
                     "'split between current portion and non-current' while providing no "
                     "home for the current half (ROUND2_RESULTS.md defect 3; labeler B "
                     "logged OperatingLeaseLiabilityCurrent as 'current portion; lease "
                     "node is explicitly non-current'). Netting it into the non-current "
                     "node destroys the maturity distinction, which is decision-relevant "
                     "and is consumed by the ontology's own working_capital and "
                     "total_current_liabilities rules.",
        },
        "a5": {
            "verdict": "pass",
            "basis": "IFRS 16 effective 2019-01-01, ASC 842 effective 2019 for public "
                     "filers. Seven years in force; not emergent.",
        },
    },
    {
        "id": "asset.current.restricted_cash",
        "title": "Restricted cash and cash equivalents",
        "corpus": "edgar",
        "edgar_tags": [
            "RestrictedCashCurrent",
            "RestrictedCashAndCashEquivalents",
            "RestrictedCashNoncurrent",
            "RestrictedCashAndCashEquivalentsAtCarryingValue",
            "RestrictedCashAndCashEquivalentsNoncurrent",
            "RestrictedCashEquivalents",
            "RestrictedCashEquivalentsCurrent",
            "RestrictedCashEquivalentsNoncurrent",
        ],
        "esef_concepts": ["CurrentRestrictedCashAndCashEquivalents",
                          "RestrictedCashAndCashEquivalents"],
        "proposed": {
            "ifrs_tag": "ifrs-full:CurrentRestrictedCashAndCashEquivalents",
            "nature": "debit",
            "statement": "balance_sheet",
            "parent": "asset.current",
        },
        "a2": {
            "verdict": "fail",
            "basis": "The IFRS element exists, but attestation across jurisdictions is "
                     "thin: it appears in a small minority of the 100-filing, 20-country "
                     "ESEF sample (count computed below), against 37 filings for "
                     "CurrentLeaseLiabilities in the same sample. ASU 2016-18 makes the "
                     "concept prominent in US reporting specifically; that is a "
                     "jurisdictional-prominence signal, which ADR-015 routes to an "
                     "overlay rather than the universal core.",
        },
        "a3": {
            "verdict": "contested",
            "basis": "The current/non-current split is filed both ways and the untiered "
                     "variants outweigh either tier, so the node boundary (one node or "
                     "two) is not determined by the evidence.",
        },
        "a4": {
            "verdict": "contested",
            "basis": "Arguable both ways, and recorded as such rather than resolved. "
                     "For: the restriction is decision-relevant (liquidity), so netting "
                     "into asset.current.cash loses information. Against: 'restricted' "
                     "is a property OF cash, and asset.current.cash already carries a "
                     "cash_flow grouping lens -- restricted-vs-unrestricted is naturally "
                     "a value on that lens, not a second leaf. Principle #1 favours the "
                     "lens reading; a leaf would also collide conceptually with the "
                     "cash/bank pair item 3 documents.",
        },
        "a5": {"verdict": "pass", "basis": "IAS 7 and ASU 2016-18 (2018) are settled."},
    },
    {
        "id": "liability.noncurrent.tiers",
        "title": "Non-current tiers of tax / provision / payables (current-only nodes)",
        "corpus": "edgar",
        "edgar_tags": [
            "AccruedIncomeTaxesNoncurrent",
            "LossContingencyAccrualCarryingValueNoncurrent",
            "NoncurrentPayables",
            "AccountsPayableAndAccruedLiabilitiesNoncurrent",
            "AccountsPayableInterestBearingNoncurrent",
        ],
        "esef_concepts": [],
        "proposed": None,
        "a2": {
            "verdict": "pass",
            "basis": "The current/non-current split is IAS 1 doctrine and universal.",
        },
        "a3": {"verdict": "pass", "basis": "Each tier has a fixed nature and statement."},
        "a4": {
            "verdict": "pass",
            "basis": "Genuinely unrepresentable: liability.current.tax, "
                     ".payables and .accrued are current-only, so a non-current balance "
                     "of the same concept has no home. Both labelers logged this "
                     "independently ('tax node is current only', 'payables node is "
                     "current only', 'accrued node is current only').",
        },
        "a5": {"verdict": "pass", "basis": "IAS 1 is settled."},
    },
    {
        "id": "asset.contra",
        "title": "Contra-asset representation (accumulated depreciation/amortisation, "
                 "allowances, and the gross carrying amount they pair with)",
        "corpus": "edgar",
        "edgar_tags": [
            "AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment",
            "FiniteLivedIntangibleAssetsAccumulatedAmortization",
            "AllowanceForDoubtfulAccountsReceivableCurrent",
            "AllowanceForDoubtfulAccountsReceivable",
            "AllowanceForDoubtfulAccountsReceivableNoncurrent",
            "PropertyPlantAndEquipmentGross",
            "FiniteLivedIntangibleAssetsGross",
            "AccountsReceivableGrossCurrent",
        ],
        "esef_concepts": [],
        "proposed": None,
        "a2": {
            "verdict": "not_measurable",
            "basis": "Contra accounts are universal in native statutory charts -- SKR04, "
                     "PCG and PUC all carry explicit accumulated-depreciation accounts -- "
                     "but neither committed corpus can attest that, because both measure "
                     "face-statement presentation and the gross/accumulated pair is "
                     "presented in the NOTES. The ESEF face-statement sample contains no "
                     "accumulated-depreciation concept at all.",
        },
        "a3": {
            "verdict": "pass",
            "basis": "A contra-asset node has a fixed nature (credit against a debit "
                     "parent) and a fixed statement (balance_sheet).",
        },
        "a4": {
            "verdict": "pass",
            "basis": "Strongly non-decomposable, and the sharpest A4 case in this run. "
                     "Only the net carrying amount maps today, so net = gross - "
                     "accumulated is inexpressible. Both A1 labelers ruled "
                     "PropertyPlantAndEquipmentGross and the accumulated-depreciation "
                     "elements out of scope for the same reason: mapping gross AND net "
                     "to one leaf would double-count and there is no contra leaf to pair "
                     "with.",
        },
        "a5": {"verdict": "pass", "basis": "IAS 16 is settled; contra accounts predate it."},
    },
    {
        "id": "income.oci_total",
        "title": "Other comprehensive income -- period total",
        "corpus": "edgar",
        "edgar_tags": ["OtherComprehensiveIncomeLossNetOfTax"],
        "esef_concepts": ["OtherComprehensiveIncome"],
        "proposed": None,
        "a2": {"verdict": "pass", "basis": "IAS 1 mandates OCI presentation; well attested in ESEF."},
        "a3": {"verdict": "fail", "basis": "See income.oci_components -- no statement class fits."},
        "a4": {
            "verdict": "fail",
            "basis": "It is a SUBTOTAL. Every one of Kontablo's core nodes is a leaf; "
                     "aggregation is computed through rollup lenses and never stored as "
                     "a node -- the same rule that keeps GrossProfit out of the core. "
                     "Storing the OCI total as a node would double-count against its own "
                     "components. Labeler B classified it AGGREGATE:income for exactly "
                     "this reason.",
        },
        "a5": {"verdict": "pass", "basis": "IAS 1 is settled."},
    },
    {
        "id": "income.oci_components",
        "title": "Other comprehensive income -- components (largest: FX translation reserve)",
        "corpus": "edgar",
        "edgar_tags": [
            "OtherComprehensiveIncomeLossForeignCurrencyTransactionAndTranslationAdjustmentNetOfTax",
        ],
        "esef_concepts": ["OtherComprehensiveIncomeNetOfTaxExchangeDifferencesOnTranslation"],
        "proposed": None,
        "a2": {
            "verdict": "contested",
            "basis": "A single component (translation differences) does have a distinct "
                     "IFRS element and is attested. But 'OCI components' as a class is a "
                     "family of dozens of elements, so admitting the class has no single "
                     "anchor; admitting only translation differences privileges one "
                     "component with no stated rule for the rest.",
        },
        "a3": {
            "verdict": "fail",
            "basis": "NO DETERMINABLE STATEMENT CLASS -- this is the blocking criterion. "
                     "The ontology defines exactly two: balance_sheet (22 nodes) and "
                     "income_statement (8). OCI is by construction outside profit or "
                     "loss, so filing it under income_statement would silently pull it "
                     "into the ebt and net_income aggregation rules and corrupt both. "
                     "The accumulated OCI *balance* already has a home (equity.reserves, "
                     "gold-adjudicated); what is missing is the *flow*, and the flow has "
                     "no statement to belong to. Admitting it requires a new statement "
                     "class plus a comprehensive-income rollup lens -- a schema-structural "
                     "change, which ADR-015 puts at major-version governance, not at "
                     "extended-core admission.",
        },
        "a4": {
            "verdict": "pass",
            "basis": "The OCI flow is not representable by any existing node.",
        },
        "a5": {"verdict": "pass", "basis": "IAS 1 is settled."},
    },
    {
        "id": "gov.intermediate_consumption",
        "title": "Intermediate consumption / use of goods and services (ESA P2, GFSM G22)",
        "corpus": "government",
        "eurostat_na_items": ["P2"],
        "imf_codes": ["G22_T"],
        "esef_concepts": [],
        "proposed": None,
        "a2": {
            "verdict": "fail",
            "basis": "Decisive, and a rejection FROM THE UNIVERSAL CORE only. Intermediate "
                     "consumption is a national-accounts / government-sector concept with "
                     "no IFRS anchor at all. ADR-015's non-growth criteria route a "
                     "single-sector concept to an overlay by construction. Its real "
                     "volume (measured below) makes it the highest-priority addition to "
                     "the public-sector overlay -- which stays UNWIRED per the round-2 H5 "
                     "recommendation, since H5's threshold cleared on evidence too thin "
                     "to carry a validation claim.",
        },
        "a3": {"verdict": "pass", "basis": "Fixed nature (debit) and a settled GFSM definition."},
        "a4": {
            "verdict": "pass",
            "basis": "No node exists. Both round-2 labelers flagged it independently as "
                     "the single most consequential gap in the drafted public-sector "
                     "extension.",
        },
        "a5": {"verdict": "pass", "basis": "GFSM 2014 and ESA 2010 are settled."},
    },
]

LITERAL_THRESHOLD_PCT = 0.5  # ADR-015 as written, calibrated on synthetic posting volume.


def pct(part: float, whole: float) -> float:
    return round(100.0 * part / whole, 4) if whole else 0.0


def build_edgar_index(rows: list[dict]) -> tuple[dict, dict, int, int]:
    """(facts_by_tag, filings_by_tag, total_facts, n_distinct_tags) for the A1 population."""
    facts: dict[str, int] = {}
    filings: dict[str, int] = {}
    for r in rows:
        if all(r[k] == v for k, v in EDGAR_FILTER.items()):
            facts[r["code"]] = facts.get(r["code"], 0) + r["n_facts"]
            # n_filings is a per-window distinct-filing count; summing across the
            # two windows would double-count a filer present in both. Max is the
            # conservative reading.
            filings[r["code"]] = max(filings.get(r["code"], 0), r["n_filings"])
    return facts, filings, sum(facts.values()), len(facts)


def build_esef_index(rows: list[dict]) -> tuple[dict, dict, int]:
    facts: dict[str, int] = {}
    filings: dict[str, int] = {}
    for r in rows:
        if r["source"] == "esef" and r["taxonomy_class"] == "standard" and r["measure_class"] == "monetary":
            facts[r["code"]] = facts.get(r["code"], 0) + r["n_facts"]
            filings[r["code"]] = filings.get(r["code"], 0) + r["n_filings"]
    return facts, filings, sum(facts.values())


def build_gov_index(rows: list[dict], source: str) -> tuple[dict, int]:
    obs: dict[str, int] = {}
    for r in rows:
        if r["source"] == source:
            obs[r["code"]] = obs.get(r["code"], 0) + r["n_facts"]
    return obs, sum(obs.values())


def measure_tags(tags: list[str], facts: dict, filings: dict, total: int) -> dict:
    per_tag = [
        {"tag": t, "n_facts": facts.get(t, 0), "n_filings": filings.get(t, 0),
         "pct_of_population": pct(facts.get(t, 0), total)}
        for t in tags
    ]
    per_tag.sort(key=lambda d: -d["n_facts"])
    n = sum(d["n_facts"] for d in per_tag)
    return {
        "n_tags": len(tags),
        "n_tags_observed": sum(1 for d in per_tag if d["n_facts"] > 0),
        "n_facts": n,
        "pct_of_population": pct(n, total),
        "max_filings_single_tag": max((d["n_filings"] for d in per_tag), default=0),
        "per_tag": per_tag,
    }


def a3_collision_check(candidate: dict, core_ifrs_tags: set[str]) -> dict:
    """Mechanical half of A3: would the proposed anchor collide with an existing one?"""
    proposed = candidate.get("proposed")
    if not proposed:
        return {"checked": False, "reason": "no concrete node proposed for this candidate"}
    tag = proposed["ifrs_tag"]
    return {
        "checked": True,
        "proposed_ifrs_tag": tag,
        "collides_with_existing_core_tag": tag in core_ifrs_tags,
    }


def load_core_ifrs_tags() -> set[str]:
    """The ifrs_tag values already claimed by minimum-core nodes (item 3's surface)."""
    import yaml
    path = os.path.join(ROOT, "core/schemas/level3_accounts.yaml")
    tags = set()
    for doc in yaml.safe_load_all(open(path, encoding="utf-8")):
        items = doc["level3"] if isinstance(doc, dict) and "level3" in doc else (
            doc if isinstance(doc, list) else [])
        for item in items:
            if isinstance(item, dict) and "nature" in item and item.get("ifrs_tag"):
                tags.add(item["ifrs_tag"])
    return tags


def main() -> int:
    rows = load_inventory("tag_resolution_v1")
    gov_rows = load_inventory("public_sector_gfs_v1")

    ed_facts, ed_filings, ed_total, ed_tags = build_edgar_index(rows)
    es_facts, es_filings, es_total = build_esef_index(rows)
    eu_obs, eu_total = build_gov_index(gov_rows, "eurostat_na_item")
    imf_obs, imf_total = build_gov_index(gov_rows, "imf_gfs")

    core_ifrs_tags = load_core_ifrs_tags()
    _, _, collisions, _ = load_ontology()

    # --- Step 1: re-derive the A1 floor on the EDGAR population -------------
    anchors = []
    for a in CALIBRATION_ANCHORS:
        m = measure_tags(a["edgar_tags"], ed_facts, ed_filings, ed_total)
        anchors.append({**{k: a[k] for k in ("node", "label")}, "measurement": m})
    anchor_pcts = [a["measurement"]["pct_of_population"] for a in anchors]
    calibrated_floor = min(anchor_pcts)
    smallest_anchor = min(anchors, key=lambda a: a["measurement"]["pct_of_population"])["node"]
    literal_transfers = all(p >= LITERAL_THRESHOLD_PCT for p in anchor_pcts)

    # --- Step 2: run every candidate through A1..A5 -------------------------
    decisions = []
    for c in CANDIDATES:
        if c["corpus"] == "government":
            eu = measure_tags(c.get("eurostat_na_items", []), eu_obs, {}, eu_total)
            imf = measure_tags(c.get("imf_codes", []), imf_obs, {}, imf_total)
            a1_pct = max(eu["pct_of_population"], imf["pct_of_population"])
            volume = {"population": "government finance census (observation counts)",
                      "eurostat_na_item": eu, "imf_gfs": imf}
        else:
            m = measure_tags(c["edgar_tags"], ed_facts, ed_filings, ed_total)
            a1_pct = m["pct_of_population"]
            volume = {"population": "edgar standard monetary face-statement facts", "edgar": m}

        esef = measure_tags(c.get("esef_concepts", []), es_facts, es_filings, es_total)

        a1 = {
            "measured_pct": a1_pct,
            "vs_literal_threshold": {"threshold_pct": LITERAL_THRESHOLD_PCT,
                                     "verdict": "pass" if a1_pct >= LITERAL_THRESHOLD_PCT else "fail"},
            "vs_calibrated_floor": {"floor_pct": calibrated_floor,
                                    "derived_from": smallest_anchor,
                                    "verdict": "pass" if a1_pct >= calibrated_floor else "fail"},
        }
        # The operative A1 verdict uses the calibrated floor, because the literal
        # 0.5% demonstrably does not transfer to this population (see step 1).
        a1["verdict"] = a1["vs_calibrated_floor"]["verdict"]
        # A margin under 1.25x the floor is not a pass anyone should lean on.
        a1["marginal"] = calibrated_floor <= a1_pct < calibrated_floor * 1.25

        verdicts = {"A1": a1["verdict"], "A2": c["a2"]["verdict"], "A3": c["a3"]["verdict"],
                    "A4": c["a4"]["verdict"], "A5": c["a5"]["verdict"]}
        admitted = all(v == "pass" for v in verdicts.values()) and not a1["marginal"]
        blocking = [k for k, v in verdicts.items() if v != "pass"]
        if a1["marginal"] and "A1" not in blocking:
            blocking.append("A1(marginal)")

        decisions.append({
            "id": c["id"],
            "title": c["title"],
            "corpus": c["corpus"],
            "admitted": admitted,
            "blocking_criteria": blocking,
            "A1": a1,
            "A2": {**c["a2"], "esef_attestation": esef},
            "A3": {**c["a3"], "collision_check": a3_collision_check(c, core_ifrs_tags)},
            "A4": c["a4"],
            "A5": c["a5"],
            "volume": volume,
            "proposed_node": c.get("proposed"),
        })

    results = {
        "experiment": "adr015_admission_v1",
        "policy": "docs/adr/015-core-node-admission-and-growth-policy.md",
        "evidence": "research/experiments/ROUND2_RESULTS.md",
        "what_this_is_not": [
            "Not a re-scoring of any round-2 hypothesis. H1 and H5 are untouched.",
            "Not a measurement of posting volume. EDGAR/ESEF measure how often a "
            "concept is presented on a face statement, which is a different quantity.",
        ],
        "populations": {
            "edgar_standard_monetary_face_facts": ed_total,
            "edgar_distinct_tags": ed_tags,
            "esef_standard_monetary_facts": es_total,
            "eurostat_na_item_observations": eu_total,
            "imf_gfs_observations": imf_total,
        },
        "threshold_calibration": {
            "literal_adr015_threshold_pct": LITERAL_THRESHOLD_PCT,
            "literal_threshold_transfers_to_this_population": literal_transfers,
            "calibrated_floor_pct": calibrated_floor,
            "calibrated_floor_derived_from": smallest_anchor,
            "method": "ADR-015 defines its threshold operationally as the marginal "
                      "contribution of the smallest already-admitted extended node. The "
                      "floor is re-derived the same way on the EDGAR population.",
            "note": "Every one of the four already-admitted extended nodes falls below "
                    "0.5% here, so the literal threshold cannot be applied to this "
                    "population without rejecting nodes ADR-015 has already admitted. "
                    "The re-derived floor is the faithful transfer of the policy, not a "
                    "relaxation of it.",
            "anchors": anchors,
        },
        "ontology_code_collisions": len(collisions),
        "core_ifrs_tags_in_use": len(core_ifrs_tags),
        "decisions": decisions,
        "admitted": sorted(d["id"] for d in decisions if d["admitted"]),
        "not_admitted": sorted(d["id"] for d in decisions if not d["admitted"]),
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "results.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)
        fh.write("\n")

    # ---------------------------- report ----------------------------------
    print("=" * 78)
    print("ADR-015 ADMISSION GATE — measured against real filing frequencies")
    print("=" * 78)
    print(f"\nA1 population: {ed_total:,} EDGAR standard monetary face-statement facts "
          f"({ed_tags:,} distinct tags)")
    print(f"A2 attestation: {es_total:,} ESEF standard monetary facts, 100 filings, 20 countries")
    print(f"Government:     {eu_total:,} Eurostat na_item obs / {imf_total:,} IMF GFS obs")

    print(f"\n-- Threshold calibration ({'literal 0.5% TRANSFERS' if literal_transfers else 'literal 0.5% DOES NOT TRANSFER'}) --")
    for a in anchors:
        m = a["measurement"]
        print(f"   already-admitted  {m['pct_of_population']:>6.3f}%  {a['node']}")
    print(f"   => calibrated floor {calibrated_floor:.3f}% (smallest: {smallest_anchor})")

    print("\n-- Decisions --")
    for d in decisions:
        mark = "ADMIT " if d["admitted"] else "REJECT"
        margin = " (marginal)" if d["A1"]["marginal"] else ""
        print(f"\n [{mark}] {d['id']}  —  A1 = {d['A1']['measured_pct']:.3f}%{margin}")
        print(f"          {d['title']}")
        print(f"          A1 {d['A1']['verdict']:<14} A2 {d['A2']['verdict']:<14} "
              f"A3 {d['A3']['verdict']:<14} A4 {d['A4']['verdict']:<10} A5 {d['A5']['verdict']}")
        if d["blocking_criteria"]:
            print(f"          blocked by: {', '.join(d['blocking_criteria'])}")

    print(f"\nADMITTED    : {results['admitted'] or 'none'}")
    print(f"NOT ADMITTED: {results['not_admitted']}")
    print(f"\nArtifact: {os.path.relpath(out, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
