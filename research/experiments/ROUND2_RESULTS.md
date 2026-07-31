# Round-2 Real-Data Validation — Results

**Run date: 2026-07-30.** Design: [`research/real_data_validation_plan.md`](../real_data_validation_plan.md)
(pre-registered 2026-07-18) plus Addendum A in the same file, which records the
operationalizations chosen **before** any hypothesis was scored.

## What this round is and is not

Kontablo's published validation figure — 97.3% deterministic resolution across 75
entities and 68 jurisdictions — is measured on **synthetic** trial balances whose
local codes are drawn from the ontology's own `local_codes` table. That is the
circularity finding in §1 of the plan. This round measures the **same resolver**
against account vocabularies Kontablo did not generate.

**The two numbers are not comparable and must never be presented as if they
were.** They answer different questions on different corpora. Nothing here
supersedes or restates the 97.3% figure, which is unchanged.

## Corpora

| Tier | Source | Scale | License regime |
|---|---|---|---|
| A1 | SEC EDGAR Financial Statement Data Sets | 53,255 filings, 5.44M face-statement facts, 9 quarterly ZIPs (970 MB) | public domain |
| A5 | IMF GFSM 2014 + Eurostat `gov_10a_exp` | 119 countries (IMF), 30 reporters (Eurostat), 1990–2025 | Eurostat open data; **IMF no-redistribution** |
| B | UK Companies House bulk accounts | 77,263 filings inventoried, 10 extracted | **no redistribution** |
| A2 | filings.xbrl.org ESEF | **not completed** | — |

Raw payloads are never committed. Each experiment carries a `manifest.json`
recording every file's source URL, SHA-256, byte size, retrieval date and license
regime, so a third party reproduces by re-downloading and checking the hash.
Scoring runs offline from committed derivatives.

**IMF licensing correction.** IMF SDMX responses carry "All Rights Reserved"
(imf.org/external/terms.htm), not an open-data grant. They were relabelled to the
plan's ambiguous-license regime after reading the payloads. Only Kontablo's own
derived counts are committed.

## Hypothesis verdicts

| # | Hypothesis | Threshold | Result | Verdict |
|---|---|---|---|---|
| **H1** | Standardized tags resolve to the **correct** node | ≥75% weighted | **NOT SCORED** | incomplete |
| **H2** | Extensions never silently force-mapped | 0 Tier-1 hits | 0 violations / 194,718 extension codes | **holds (weak test)** |
| **H3** | Real uncurated captions resolve via Tier 2/3 | ≥60% supports, <30% weakens | **22.7%** | **FALSIFIED** |
| **H4** | Reconstructed subtotals match reported subtotals | ≥90% reconcile | **100%** (144/144) | **supported** |
| **H5** | Public-sector crosswalk resolves real fiscal data | ≥70% weighted | **NOT SCORED** | incomplete |

### H1 and H5 are not scored, and coverage is not a substitute

H1 and H5 are **accuracy** thresholds — "resolves to the *correct* node". Accuracy
requires the gold standard of plan §6: a stratified sample, independently
double-labeled, with Cohen's κ reported and disagreements adjudicated. The
sampling frames and blind labeling sheets are built, committed and deterministic
(`gold/sampling_frame.csv`, 320 tags for A1 and a 212-code census for A5), but the
labeling passes did not complete in this session.

Coverage — *did the resolver return some node* — **is** measured, and is reported
below. **Coverage is not accuracy and must not be quoted as if it satisfied H1 or
H5.** A resolver that maps everything to something scores high coverage and is
useless; that is precisely why the pre-registered thresholds are accuracy-based.

## Tier A1 — EDGAR (coverage only)

Holdout window 2025q3–2026q1, monetary standard face-statement tags:

| Stratum | Weighted | Unweighted | n codes |
|---|---|---|---|
| pooled | 48.4% | 33.2% | 4,777 |
| seen in train | 48.4% | 33.4% | 4,624 |
| **unseen in train** | 53.2% | **28.8%** | 153 |

Tier 1 resolved 270,963 facts, Tier 2 resolved 367,858, and 679,881 escalated.

The unseen-in-train stratum is the only genuinely non-circular evidence here, and
it carries just 590 facts — its weighted figure (53.2%) rests on so few
observations that the unweighted 28.8% is the more trustworthy reading. By
construction no unseen tag can reach Tier 1, so that stratum measures the Tier-2
keyword rules alone.

**The extension tail is the headline structural finding.** Real filers invent far
more taxonomy elements than the standard provides: 386,279 extension tags against
13,893 standard tags in the train window — a 28:1 ratio — yet those extensions
carry only ~11% of face-statement facts. The standard vocabulary is small and
dense; the invented vocabulary is vast and sparse.

### H2 holds, but the test is weak — stated plainly

Zero Tier-1 violations across 78,267 holdout and 116,451 train extension codes.
However, **none of the 138,920 distinct extension codes reuses any of the 130
crosswalk tag names**, so the collision surface was small. The hazard is real —
119 extension codes *do* collide with the wider standard tag namespace — so a
larger crosswalk would face it. H2 should be re-tested when the crosswalk grows.

Tier-2 name matches on extensions (34,723 holdout codes) are reported separately
and counted as neither violations nor clean escalations, per Addendum A.2: Tier 2
is the designed name-based path, reports confidence 0.85 rather than 1.0, and
names the rule that fired, so it is auditable rather than silent.

## Tier A5 — public sector (coverage only)

Coverage 27.7% weighted on both windows. This number is **depressed by design**
and should not be read as a failure: 10 of the 47 crosswalk entries are COFOG
**functional** codes that deliberately do not map to accounts (see below), and
correctly escalate.

**Temporal holdout is a weak test for statistical classifications.** Code drift
between train (≤2020) and holdout (2021+) is **zero** for both IMF and Eurostat —
every holdout code also appears in train. Statistical classifications are stable
by design, unlike corporate taxonomies. The A5 holdout therefore tests whether the
*mappings* generalize, not whether the resolver handles novel vocabulary. This
limits what H5 can demonstrate even once it is scored.

### COFOG is a lens, not a chart of accounts

Eurostat `gov_10a_exp` is a two-dimensional cube: every cell is a (`cofog99`
function × `na_item` transaction) pair. The axes are not interchangeable.
`na_item` is account-like; `cofog99` classifies by **purpose** — the same payroll
euro is simultaneously an economic-type expense and a functional-category expense.

In Kontablo terms a function is a rollup **lens**, not a node (principle #1,
"graph, not tree"). Scoring functional codes as though they had to resolve to an
account would be a category error that penalizes the ontology for a distinction it
models correctly, so they carry a typed `lens` non-mapping.

### Gaps found in the drafted extension

- **GFSM `G22` / ESA `P2`** (use of goods and services / intermediate consumption)
  has no node, and is one of the largest real government expense lines.
- **Correction to the plan:** §2 and §8 state the extension carries "39 mappings".
  It carries **19**. No summation of the file's blocks yields 39. Recorded in
  Addendum A.1.

Public-sector coverage remains **drafted, not yet empirically validated** in all
public wording, and the extension is still not wired into `core/harness/`.

## Tier B — UK Companies House case study (n=10)

A **case study, not a statistical benchmark.** It does not generalize to the UK
filing population.

### H4 supported: 100% (144/144 checks, 10 companies)

| Identity | Reconciled |
|---|---|
| `Equity = NetAssetsLiabilities` (balance-sheet equation) | 30/30 |
| PP&E carrying amount = gross cost − accumulated depreciation | 86/86 |
| Intangibles carrying amount = gross cost − accumulated amortisation | 28/28 |

Every identity is checked **within a single iXBRL `context_ref`**. Comparing
across contexts would silently check a 2025 figure against a 2024 one and produce
a meaningless result. The `net_current_assets` identity never had all components
present in one context and contributed no checks.

### H3 falsified: 22.7% against a 30% floor

Reported as a falsification, **not repaired**. Adding the missing keywords and
re-running would be tuning on the test set; the fix and its evaluation belong to a
future round with a fresh holdout.

A first pass read 16.7%, but that population was wrong: the extractor collected
every tagged fact, including note movement tables, so the resolver was being
scored against `At 31 October 2025`, `Additions` and `Disposals`. Rows are now
classified `balance` / `movement` / `period_marker` by the same deterministic rule
Tier A1 applies (Addendum A.5); all three populations are reported in
`results.json`.

**The falsification is diagnosable, which is what makes it useful.** The shipped
Tier-2 rule set carries Spanish, French, Portuguese, German, Russian, Korean and
Arabic vocabulary but lacks basic British English. There is no rule for
`creditor`, `prepayment`, `turnover`, `deferred income` or `wages`, and **6 of the
30 core nodes have no Tier-2 rule at all** (`asset.noncurrent.investments`,
`asset.noncurrent.rou_assets`, `expense.tax`, `liability.current.accrued`,
`liability.noncurrent.deferred_tax`, `liability.noncurrent.lease`). The unresolved
captions are ordinary accounting terms: Trade creditors, Prepayments, Tangible
assets, Deferred income, Investments.

This locates the semantic coverage boundary precisely: the deterministic keyword
tier generalizes poorly to a national vocabulary it was not authored for. That is
a more actionable result than a passing score would have been.

## Tier A2 — ESEF: not completed

45 filing payloads were fetched and manifested before the run was interrupted; no
derived inventory or score exists. The downloader is not committed. A2 is
**outstanding**, not negative.

## Reproducing

```bash
python scripts/real_data/download_edgar.py            # or KONTABLO_REAL_DATA_OFFLINE=1
python scripts/real_data/download_gfs.py
python scripts/real_data/resolve_real_facts.py
python scripts/real_data/score_companies_house.py
python scripts/real_data/build_gold_sample.py         # regenerates the labeling frames
python scripts/real_data/adjudicate_gold.py           # once labels_A/B exist
```

## What must not be claimed from this round

1. That any real-data figure supersedes or restates the synthetic 97.3%.
2. That H1 or H5 passed — they are **unscored**, and coverage is not accuracy.
3. That public-sector support is empirically validated — H5 is unscored and the
   extension remains unwired.
4. That Tier B generalizes — it is n=10, a case study.
5. That H3's falsification has been fixed — it has not, deliberately.
