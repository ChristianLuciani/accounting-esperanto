# Round-2 Real-Data Validation — Results

**First run 2026-07-30; completed 2026-07-31** (gold labeling, Tier A2).
Design: [`research/real_data_validation_plan.md`](../real_data_validation_plan.md)
(pre-registered 2026-07-18) plus Addendum A (operationalizations recorded before
any hypothesis was scored) and Addendum B (recorded before H1/H5 were scored).

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
| A2 | filings.xbrl.org ESEF | 100 filings, 20 countries, 2,821 concepts, 38,893 facts | issuer public disclosure |
| A5 | IMF GFSM 2014 + Eurostat `gov_10a_exp` | 119 countries (IMF), 30 reporters (Eurostat), 1990–2025 | Eurostat open data; **IMF no-redistribution** |
| B | UK Companies House bulk accounts | 77,263 filings inventoried, 10 extracted | **no redistribution** |

Raw payloads are never committed. Each experiment carries a `manifest.json`
recording every file's source URL, SHA-256, byte size, retrieval date and license
regime, so a third party reproduces by re-downloading and checking the hash.
Scoring runs offline from committed derivatives (`KONTABLO_REAL_DATA_OFFLINE=1`).

**IMF licensing correction.** IMF SDMX responses carry "All Rights Reserved"
(imf.org/external/terms.htm), not an open-data grant. They were relabelled to the
plan's ambiguous-license regime after reading the payloads. Only Kontablo's own
derived counts are committed.

## Hypothesis verdicts

| # | Hypothesis | Threshold | Result | Verdict |
|---|---|---|---|---|
| **H1** | Standardized tags resolve to the **correct** node | ≥75% supports / 50–75% partial | **74.3%** weighted (n=320) | **partial — 0.7 pp short** |
| **H2** | Extensions never silently force-mapped | 0 Tier-1 hits | 0 violations / 196,122 extension codes (EDGAR + ESEF) | **holds (weak test)** |
| **H3** | Real uncurated captions resolve via Tier 2/3 | ≥60% supports, <30% weakens | **22.7%** | **FALSIFIED** |
| **H4** | Reconstructed subtotals match reported subtotals | ≥90% reconcile | **100%** (144/144) | **supported** |
| **H5** | Public-sector crosswalk resolves real fiscal data | ≥70% supports | **82.3%** weighted (n=212) | **threshold cleared, but structurally weak — see below** |

Every hypothesis is now scored. **Coverage is not accuracy**: H1 and H5 are
accuracy thresholds and are scored against the adjudicated gold standard of plan
§6, never against coverage. Coverage figures are reported separately below.

## The gold standard (plan §6)

Four labeling agents produced two independent passes per experiment. Each was
blind to: both crosswalk YAMLs, `resolve_real_facts.py`, `core/harness/resolution.py`,
every `results.json` and `resolution_detail.csv`, and the other labeler's sheet;
each confirmed this explicitly. Labeler A reasoned **tag-first**, labeler B
**node-first with default-to-no-match**, to decorrelate errors (Addendum A.7).

| | A1 (us-gaap) | A5 (GFS/COFOG) |
|---|---|---|
| items double-labeled | 320 | 212 |
| raw agreement (exact label) | 89.4% | 90.1% |
| **Cohen's κ (exact label)** | **0.797** (substantial, 39 categories) | **0.771** (substantial, 18 categories) |
| **Cohen's κ (3-way class)** | **0.777** (substantial) | **0.807** (substantial) |
| disagreements adjudicated | 34 | 21 |

**Independence caveats, carried forward and not diluted.** (1) Both passes are the
same model family under different instructed reasoning orders — weaker
independence than two unaffiliated human CPAs, so κ overstates true independence
(Addendum A.7). (2) The crosswalks under test were authored by the *previous*
session; the gold labels were not, so the accuracy figures are **not** a
self-consistency check — but the third-pass adjudicator was this session's
orchestrator, which had read `resolve_real_facts.py` (never either crosswalk
YAML). Adjudication touched 34/320 and 21/212 rows; the rest is unmediated
labeler agreement. Full disclosure in Addendum B.6.

## H1 — partial, and the failure mode is over-mapping

**74.3% weighted / 66.6% unweighted on the holdout (n=320).** The pre-registered
bands are ≥75% supports, 50–75% partial. At 74.3% H1 lands in the **partial**
band, 0.7 pp below support. Reported as measured; not rounded up to 75%.

The class breakdown is where the result becomes useful:

| gold class | n codes | weighted acc. | what the resolver did |
|---|---|---|---|
| **leaf** (really is a core account) | 58 | **94.6%** | 38 correct, 5 wrong node, 15 missed |
| aggregate (subtotal) | 32 | 72.7% | 22 correctly escalated, **10 false positives** |
| out_of_scope | 230 | 56.3% | 153 correctly escalated, **77 false positives** |

**When a tag genuinely is a core account, the resolver is right 94.6% of the time
by fact volume.** The score is dragged down by the opposite error: **87 of 320
codes (27%) were mapped to a node when the correct behavior was to escalate**,
covering 179,155 holdout facts. Only 5 codes resolved to the *wrong* node.

That distinction matters. This is not a resolver that confuses one account for
another; it is a resolver that **over-claims**, mapping subtotals and
out-of-scope concepts onto leaves. It is exactly the failure that coverage cannot
see — a resolver maximizing coverage scores well and is wrong — and it is the
reason plan §6 required an accuracy gold standard in the first place. Sampling
from the whole population rather than only resolved facts (Addendum A.3) is what
made these 87 visible.

## H5 — threshold cleared, but the test is structurally weak

**82.3% weighted / 88.2% unweighted (n=212)**, against a ≥70% support threshold.
Per the pre-registered rule, **H5 clears**. Stating that alone would be
misleading, so the composition follows:

| gold class | n codes | share | weighted acc. | note |
|---|---|---|---|---|
| **lens** (COFOG functional) | 159 | **75.0%** | 100% | all correct escalations |
| leaf (real account mapping) | 13 | 6.1% | 100% | 13/13 correct |
| aggregate | 37 | 17.5% | 54.8% | **24 false positives** |
| out_of_scope | 3 | 1.4% | 53.3% | 1 false positive |

**Three-quarters of the scored population is COFOG functional codes whose correct
answer is "escalate", and the resolver escalates them because it has no COFOG
rules at all.** It is right for a structural reason, not because the crosswalk is
good. Strip those out and the mapping evidence is **13 codes** — a case study, not
a benchmark. On the aggregate class it does badly (35.1% unweighted, 24 false
positives): it maps totals onto leaves, the same over-mapping failure H1 exposes.

Both labelers independently reported that **12 of the 19 drafted public-sector
nodes receive zero evidence from this census** — every `ASSET_*`, `LIAB_*` and
`EQ_*` node among them, because the census is flow-dominated and its only stock
rows are top-level totals. A threshold cleared on 13 mapped codes covering 7 of
19 nodes does not establish that the extension works.

**Recommendation (for the owner to ratify, not a unilateral change):** keep all
public-facing public-sector wording qualified as **"drafted, not yet empirically
validated"**, and keep the extension unwired (plan §14). Plan §2 ties promotion to
H5 clearing its threshold; the threshold cleared, but on evidence too thin and too
structurally skewed to carry a validation claim. Promoting on this basis would be
the letter of the plan against its intent. A census that exercises the stock nodes
is the missing evidence.

### Gaps found in the drafted extension

- **GFSM `G22` / ESA `P2`** (use of goods and services / intermediate consumption)
  has no node, and is one of the largest real government expense lines. Both
  labelers flagged it independently as the single most consequential gap.
- `EXP_GrantsAndSubsidiesPaid` absorbs four economically distinct instruments
  (subsidies, other current transfers, capital transfers, investment grants) that
  fiscal analysts treat separately — a real granularity loss.
- No node and no attribute for the **counterparty/subsector axis** (`D4_S13xx`
  etc.), which is the elimination dimension for whole-of-government consolidation.
- **Correction to the plan:** §2 and §8 state the extension carries "39 mappings".
  It carries **19**. Recorded in Addendum A.1.

### COFOG is a lens, not a chart of accounts

Eurostat `gov_10a_exp` is a two-dimensional cube: every cell is a (`cofog99`
function × `na_item` transaction) pair. `na_item` is account-like; `cofog99`
classifies by **purpose** — the same payroll euro is simultaneously an
economic-type expense and a functional-category expense. In Kontablo terms a
function is a rollup **lens**, not a node (principle #1, "graph, not tree"), so
functional codes carry a typed `lens` gold label whose correct resolver behavior
is to escalate. Per-axis coverage makes the split visible: `eurostat_na_item`
56.9% weighted, `eurostat_cofog` 0.0%, `imf_gfs` 15.8%.

## Tier A1 — EDGAR coverage

Holdout window 2025q3–2026q1, monetary standard face-statement tags:

| Stratum | Weighted | Unweighted | n codes |
|---|---|---|---|
| pooled | 48.4% | 33.2% | 4,777 |
| seen in train | 48.4% | 33.4% | 4,624 |
| **unseen in train** | 53.2% | **28.8%** | 153 |

Tier 1 resolved 270,963 facts, Tier 2 resolved 367,858, and 679,881 escalated.

The unseen-in-train stratum is the only genuinely non-circular coverage evidence
here, and it carries just 590 facts — its weighted figure (53.2%) rests on so few
observations that the unweighted 28.8% is the more trustworthy reading. By
construction no unseen tag can reach Tier 1, so that stratum measures the Tier-2
keyword rules alone.

**The extension tail is the headline structural finding.** Real filers invent far
more taxonomy elements than the standard provides: 386,279 extension tags against
13,893 standard tags in the train window — a 28:1 ratio — yet those extensions
carry only ~11% of face-statement facts. The standard vocabulary is small and
dense; the invented vocabulary is vast and sparse.

## Tier A2 — ESEF / ifrs-full (completed 2026-07-31)

100 filings across 20 countries (AT BE CY CZ DK EE ES FI FR GB GR HR HU IS IT LT
LU LV MT NL), 5 per country by the pre-stated mechanical rule, parsed from
**xBRL-JSON with the stdlib `json` module** — no Arelle, avoiding the GPL
licensing hazard plan §7 flags.

| | concepts | facts | share of facts |
|---|---|---|---|
| `ifrs-full` base | 1,347 | 33,434 | 86.0% |
| issuer **extension** | 1,474 | 5,459 | 14.0% |

**Two findings, one of them a correction to an assumption A1 invited.**

1. **The extension ratio is corpus-specific, not universal.** EDGAR shows 28:1
   extension-to-standard *concepts*; ESEF shows **1.1:1** (1,474 vs 1,347). ESEF's
   mandated core taxonomy plus its tagging rules produce a far narrower invented
   vocabulary than US filers do — yet extensions still carry a *higher* share of
   facts (14.0% vs ~11%). Any claim about "how much filers invent" must name its
   corpus.
2. **Coverage against the ontology's own `ifrs_tag` is very low: 6.3% weighted /
   2.3% unweighted** (16 of 692 monetary base concepts, all Tier 1). Real ESEF
   face statements use ~692 distinct monetary `ifrs-full` concepts; the 30-node
   core anchors 24 usable ones. Tier 2 **cannot fire at all** on this corpus —
   filings.xbrl.org's xBRL-JSON carries no human-readable labels, so the
   name-based tier has no input. A2 coverage is therefore Tier-1-only by
   construction and is not comparable to A1's Tier-1+Tier-2 figure.

The largest unresolved concepts are dominated by subtotals and movements that
*should* escalate (`Equity` 3,572 facts, `ProfitLoss` 1,574, `ComprehensiveIncome`
1,467, `IncreaseDecreaseThrough*` roll-forwards) — but also include
**`CashAndCashEquivalents` (600 facts)**, which escalates for a different and more
interesting reason: see below.

### The ontology's `ifrs_tag` field is not injective

The 30 core nodes carry only **27 distinct** `ifrs_tag` values; three tags are
each claimed by two nodes:

| IFRS tag | claimed by |
|---|---|
| `ifrs-full:CashAndCashEquivalents` | `asset.current.cash`, `asset.current.bank` |
| `ifrs-full:CurrentTaxLiabilitiesCurrent` | `liability.current.vat_output`, `liability.current.tax` |
| `ifrs-full:OtherNonCurrentFinancialLiabilities` | `liability.noncurrent.debt`, `liability.noncurrent.lease` |

Given only the tag the correct leaf is undetermined, so these escalate rather than
being resolved by an arbitrary tie-break (principle #5 — a coin flip is not
determinism). The visible cost is that the most fundamental IFRS balance-sheet tag
of all, `CashAndCashEquivalents`, cannot resolve. **This is an ontology defect
surfaced by real data, and fixing it is a design decision, not a scoring
adjustment.** Direction of bias: excluding them can only lower A2 coverage.

### A2 does not exercise the temporal holdout

The committed mechanical selection rule sorts by `(country, period_end, fxo_id)`
and takes 5 per country — which deterministically picks each country's *earliest*
filings. Against a 24,376-filing eligible pool the sample is 100 filings with
`period_end` 2018-06-30…2021-12-31, **all train, zero holdout**. The rule was
fixed before any data was inspected and was **not** re-run with a different rule
after seeing this; that would be post-hoc selection tuning. A2's non-circularity
instead rests on **provenance**: `ifrs_tag` was written 2026-03-23 and last
touched 2026-07-20, both before the round-2 branch opened (2026-07-30), so it
cannot have been fitted to this corpus (Addendum B.1–B.2).

### H2 holds on ESEF too — and the test is weaker still

**0 Tier-1 violations across all 1,404 ESEF extension codes; all 1,404 escalated,
with 0 Tier-2 name matches.** Combined with EDGAR's 194,718, H2 sees 0 violations
across 196,122 extension codes.

But the ESEF test is *weaker* than EDGAR's, not stronger: with no labels in the
payload, Tier 2 has nothing to match on, so extensions escalate by default rather
than by discrimination. On EDGAR the corresponding caveat is that **none of the
138,920 distinct extension codes reuses any of the 130 crosswalk tag names**, so
the collision surface was small — though 119 extension codes *do* collide with the
wider standard tag namespace, so the hazard is real and H2 should be re-tested
when the crosswalk grows.

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
across contexts would silently check a 2025 figure against a 2024 one. The
`net_current_assets` identity never had all components present in one context and
contributed no checks.

### H3 falsified: 22.7% against a 30% floor

Reported as a falsification, **not repaired**. Adding the missing keywords and
re-running would be tuning on the test set; the fix and its evaluation belong to a
future round with a fresh holdout.

A first pass read 16.7%, but that population was wrong: the extractor collected
every tagged fact, including note movement tables, so the resolver was being
scored against `At 31 October 2025`, `Additions` and `Disposals`. Rows are now
classified `balance` / `movement` / `period_marker` by the same deterministic rule
Tier A1 applies (Addendum A.5).

**The falsification is diagnosable, which is what makes it useful.** The shipped
Tier-2 rule set carries Spanish, French, Portuguese, German, Russian, Korean and
Arabic vocabulary but lacks basic British English. There is no rule for
`creditor`, `prepayment`, `turnover`, `deferred income` or `wages`, and **6 of the
30 core nodes have no Tier-2 rule at all**. The unresolved captions are ordinary
accounting terms: Trade creditors, Prepayments, Tangible assets, Deferred income,
Investments.

## Defects in the ontology surfaced by this round

Real data and blind labeling exposed four internal inconsistencies. Each is
recorded because a labeler had to rule on it, and the ruling is only as sound as
the ontology's own definition:

1. **`asset.noncurrent.investments`** — `label_en` is the broad "Long-term
   Investments" but `ifrs_tag` is the narrow
   `InvestmentsAccountedForUsingEquityMethod`. Under the broad reading
   `HeldToMaturitySecurities` maps; under the narrow one it does not.
2. **`expense.admin`** — `ifrs_tag` is `AdministrativeExpenses` (narrow G&A), but
   the ontology's own rule `ebit = gross_profit − expense.admin` makes it the sole
   operating-expense deduction. The two readings disagree about the single largest
   US opex line, `SellingGeneralAndAdministrativeExpense`.
3. **`liability.noncurrent.lease`** — its note says the balance is "split between
   current portion and non-current", contradicting its non-current node id; the
   current portion has no home.
4. **`EXP_SocialBenefitsExpense`** (public sector) — `ipsas_ref: IPSAS 42` scopes
   to cash benefits and excludes transfers in kind, but its `examples` list
   includes in-kind healthcare.

Also a **label-vocabulary gap**, reported independently by both A1 labelers: there
is no combined liability+equity lens, so `LiabilitiesAndStockholdersEquity` —
a genuine balance-sheet total — has no correct `AGGREGATE:` label.

## Reproducing

```bash
python scripts/real_data/download_edgar.py            # or KONTABLO_REAL_DATA_OFFLINE=1
python scripts/real_data/download_esef_sample.py
python scripts/real_data/download_gfs.py
python scripts/real_data/resolve_real_facts.py
python scripts/real_data/score_companies_house.py
python scripts/real_data/build_gold_sample.py         # regenerates the labeling frames
python scripts/real_data/adjudicate_gold.py           # kappa + gold assembly
```

## What must not be claimed from this round

1. That any real-data figure supersedes or restates the synthetic 97.3%.
2. That H1 passed — it is **partial** at 74.3%, below the 75% support threshold.
3. That H5's clearing of its threshold validates public-sector support. 75% of
   that score is correct refusals of COFOG codes, only 13 codes test real mapping,
   and 12 of 19 drafted nodes receive no evidence. Public-sector wording stays
   **drafted, not yet empirically validated**, and the extension stays unwired.
4. That A2 tested the temporal holdout — its sample is entirely train-window.
5. That A2 and A1 coverage are comparable — Tier 2 cannot fire on ESEF at all.
6. That Tier B generalizes — it is n=10, a case study.
7. That H3's falsification has been fixed — it has not, deliberately.
8. That κ ≈ 0.78–0.81 represents human-grade independent agreement — both passes
   are the same model family (Addendum A.7).
