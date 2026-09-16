# ADR-015 Admission Gate — First Run Against Real Filing Frequencies

**Run 2026-07-31.** Policy: [`docs/adr/015-core-node-admission-and-growth-policy.md`](../../../docs/adr/015-core-node-admission-and-growth-policy.md).
Evidence: [`research/experiments/ROUND2_RESULTS.md`](../ROUND2_RESULTS.md).
Regenerate: `python scripts/adr015_admission_gate.py` → [`results.json`](results.json).

ADR-015 has existed since 2026-06-11 and had **never been exercised**. Its A1
criterion demands a *measured* volume figure, and until round 2 the only
committed frequency distribution was the synthetic one behind
`coverage_benchmark.py` — so "measured" could only ever mean "measured against
numbers Kontablo generated itself". Round 2 committed 5.44M real SEC EDGAR
face-statement facts, 38,893 ESEF facts and the IMF/Eurostat government-finance
census. This is the policy's first run against data Kontablo did not author.

**Outcome: one admission out of seven candidates.**

| Candidate | A1 measured | Verdict | Blocked by |
|---|---:|---|---|
| **Current portion of lease liabilities** | **0.645%** | **ADMITTED → `extended_core`** | — |
| Restricted cash and cash equivalents | 0.463% | not admitted | A2, A3, A4 |
| Non-current tiers of tax / provision / payables | 0.048% | not admitted | **A1** |
| Contra-asset representation | 0.106% *(marginal)* | **deferred** | A2 not measurable, A1 marginal |
| OCI — period total | 0.530% | not admitted | A3, **A4 (it is a subtotal)** |
| OCI — components | 0.396% | not admitted | A2, **A3 (no statement class)** |
| Intermediate consumption (ESA P2 / GFSM G22) | 5.190% | not admitted **to core** | **A2 (no IFRS anchor)** → overlay |

## What this run is not

1. **Not a re-scoring of any hypothesis.** H1 (74.3%, partial) and H5 (82.3%)
   are untouched and must stay untouched — see "The gold set does not survive
   this change" below.
2. **Not a posting-volume measurement.** See the next section; this is the most
   important caveat in the document.
3. **Not a promotion of the public-sector extension.** It stays unwired and
   stays described as *drafted, not yet empirically validated*, per round 2's H5
   recommendation.

## The population problem, stated before any verdict

ADR-015 defines A1 as a share of **routine posting volume**. EDGAR and ESEF
measure a different quantity: **how often a concept is presented as a fact on a
face statement**. These do not rank concepts the same way, and the gap is not
small. A depreciation posting recurs monthly in a ledger and appears at most once
a year on a face statement — usually only in the notes, which round 2's derived
corpus deliberately excludes.

So the 0.5% threshold cannot simply be carried across. But ADR-015 does not
define 0.5% axiomatically. It defines it **operationally**:

> The working threshold is ≥ ~0.5% of total posting volume (**roughly the
> marginal contribution of the smallest of the four extended nodes already
> admitted**).

The faithful transfer is therefore to re-derive the floor *the same way* on the
new population: measure the four already-admitted extended-core nodes against
EDGAR and take the smallest.

### The calibration result — the methodological headline

| Already-admitted node | EDGAR share |
|---|---:|
| `liability.current.deferred_revenue` | 0.344% |
| `asset.current.other_receivables` | 0.144% |
| `asset.current.withholding_tax` | 0.124% |
| **`liability.current.payroll`** | **0.100%** ← calibrated floor |

**All four fall below 0.5%.** Applying the literal threshold to this population
would reject every node ADR-015 has already admitted — a reductio that settles
the question: the literal 0.5% does not transfer, and the re-derived floor of
**0.100%** is the faithful reading of the policy, not a relaxation of it.

The inversion is worth naming, because it is the concrete demonstration that the
two populations are genuinely different quantities and not just noisy versions of
each other: ADR-015 records payroll as capturing "by far the largest residual
slice" of posting volume, and payroll is the **smallest** of the four on EDGAR.
Payroll is posted constantly and disclosed once.

Both verdicts (literal and calibrated) are recorded per candidate in
`results.json` so a reader can apply either threshold and see exactly where they
disagree. A candidate clearing the floor by less than 1.25× is flagged
`marginal` and does **not** count as a pass — a pass inside the noise band of the
floor is not evidence.

## Decisions

### ADMITTED — `liability.current.lease` (current portion of lease liabilities)

| Criterion | Verdict | Evidence |
|---|---|---|
| **A1** volume | pass | **0.645%** of 3,878,245 EDGAR standard monetary face facts — 6.5× the calibrated floor and above the literal 0.5% as well, the only candidate to clear both. `OperatingLeaseLiabilityCurrent` 21,367 facts / 9,450 filings; `FinanceLeaseLiabilityCurrent` 3,664 / 1,627. |
| **A2** universality + IFRS anchor | pass | `ifrs-full:CurrentLeaseLiabilities` is a distinct IFRS taxonomy element, attested in the ESEF corpus at **125 facts across 29 filings** of the 100-filing, 20-country sample. IFRS 16 and ASC 842 both mandate the split, so this is not chart-family specific. |
| **A3** determinable invariants | pass | Fixed `nature: credit`, fixed `statement: balance_sheet`, distinct anchor colliding with **none** of the 27 `ifrs_tag` values already in use (checked mechanically). Boundary is binary: the portion due within twelve months. `ontology_code_collisions == 0` re-verified after admission. |
| **A4** non-decomposability | pass | Not representable today. `liability.noncurrent.lease` is explicitly non-current, and **its own `notes` field concedes** the balance is "split between current portion and non-current" while providing no home for the current half (ROUND2 defect 3). Labeler B logged `OperatingLeaseLiabilityCurrent` as "current portion; lease node is explicitly non-current". Netting it into the non-current node destroys the maturity distinction that the ontology's own `working_capital` and `total_current_liabilities` rules consume. |
| **A5** maturity | pass | IFRS 16 effective 2019-01-01, ASC 842 effective 2019. Seven years in force. |

This is the cleanest possible admission: a defect the ontology documents against
itself, confirmed independently by a blind labeler, and carrying real volume.

### DEFERRED — contra-asset representation (round-2 follow-up item 5)

**Not admitted, and not rejected on the merits.** A1 measures **0.106%** against
a 0.100% floor — inside the noise band, so it is flagged marginal and does not
pass. A2 is **not measurable** on either committed corpus.

The reason both corpora are silent is structural, not evidential:

- US filers present PP&E **net** on the face. `PropertyPlantAndEquipmentNet`
  carries 34,510 facts (0.890%); `PropertyPlantAndEquipmentGross` carries 695
  (0.018%) — a **49:1 ratio**. The gross/accumulated pair lives in the notes,
  which the derived corpus excludes by construction.
- The ESEF face-statement sample contains **no accumulated-depreciation concept
  at all**.

Counter-evidence pointing the other way, which is why this is a deferral:

- Round 2's **H4 reconciled 86/86 PP&E identities** (`gross − accumulated = net`)
  and **28/28 intangibles identities**, within a single `context_ref`, across the
  Companies House sample. The pair was present and internally consistent in
  every filing examined — but n=10, a case study that cannot carry a volume
  figure.
- SKR04, PCG and PUC all carry explicit contra accounts. That is chart presence,
  which is what A2 is really asking about, and neither corpus can attest it.

**The missing measurement, stated precisely:** contra-account frequency in a
corpus of *native coded local charts* (round 3's Distance-4) or of posting
volume, not of face-statement presentation. Until that exists, ADR-015's own rule
governs — *no measurement, no admission*.

**Consequence, stated plainly: item 5's Distance-4 blocker remains open.** A
whole account class stays unrepresentable, and round 3 will meet it again. This
run does not fix that; it establishes what would have to be measured to fix it
under policy rather than by fiat.

### Not admitted — the rest

**Restricted cash (0.463%).** Clears the calibrated floor but fails **A2**:
`ifrs-full:CurrentRestrictedCashAndCashEquivalents` is attested in only **14
facts across 3 filings** of the 20-country ESEF sample, against 29 filings for
`CurrentLeaseLiabilities`. Its prominence in EDGAR reflects ASU 2016-18, a US
requirement — jurisdictional prominence, which ADR-015 routes to an overlay by
construction. A3 and A4 are also recorded as **contested**, not resolved: filers
split it current/non-current inconsistently (the untiered variants outweigh
either tier, so the node boundary is undetermined), and "restricted" is arguably
a *property of* cash rather than a second leaf — `asset.current.cash` already
carries a `cash_flow` grouping lens, and principle #1 favours the lens reading.

**Non-current tiers of tax / provision / payables (0.048%).** Fails **A1** by a
factor of two against the floor, and by ten against the literal threshold. Every
other criterion passes — the defect is real (three current-only nodes with no
non-current counterpart, logged independently by both labelers) and simply
low-volume. **This is the policy working as designed**, not a shortfall:
ADR-015 states outright that "*most* candidates will fail here, by design", and
routes exactly this case to escalation or overlay.

**OCI — period total (0.530%).** Clears A1, fails **A4 decisively**: it is a
*subtotal*. Every Kontablo core node is a leaf; aggregation is computed through
rollup lenses and never stored as a node — the same rule that keeps `GrossProfit`
out of the core. Storing the OCI total would double-count against its own
components. Labeler B classified it `AGGREGATE:income` for precisely this reason.

**OCI — components (0.396%).** Clears the floor, fails **A3** on a structural
blocker worth recording because it names a real prerequisite:

> The ontology defines exactly **two** statement classes: `balance_sheet` (22
> nodes) and `income_statement` (8). OCI is by construction *outside* profit or
> loss, so filing an OCI node under `income_statement` would silently pull it
> into the `ebt` and `net_income` aggregation rules and corrupt both. The
> accumulated OCI *balance* already has a home (`equity.reserves`,
> gold-adjudicated); what is missing is the *flow*, and the flow has no statement
> to belong to.

Admitting OCI therefore requires a new statement class plus a
comprehensive-income rollup lens. That is a schema-structural change, which
ADR-015 places at major-version governance, not at extended-core admission. A2 is
additionally **contested**: "OCI components" is a family of dozens of elements
with no single anchor, and admitting only translation differences would privilege
one component with no stated rule for the rest.

**Intermediate consumption / use of goods and services (5.190%).** By far the
largest measured volume in this run — **65,395 of 1,260,004 Eurostat `na_item`
observations (5.19%), 3.42% by absolute value, and 2,229 of 136,834 IMF GFS
observations (1.63%)**. Both round-2 labelers flagged it independently as the
single most consequential gap in the drafted public-sector extension, and it is
the largest unmapped government expense line worldwide.

It nonetheless fails **A2 for the universal core**, decisively and correctly: it
is a national-accounts concept with **no IFRS anchor at all**. ADR-015's
non-growth criteria route a single-sector concept to an **overlay**, and the
overlay layer exists precisely so that "not core" never reads as "not supported".

**This is therefore a rejection *from the core*, not a rejection of the concept.**
It is recorded as the highest-priority addition to the public-sector overlay —
which **stays unwired**, per round 2's H5 finding that the threshold cleared on
evidence too thin and too structurally skewed to carry a validation claim (75% of
that score was correct refusals of COFOG codes; 13 codes tested real mapping; 12
of 19 drafted nodes received no evidence at all).

## Consequences

**Published numbers that move.** One: the extended core goes from **34 to 35**
nodes. `extended_core_coverage_pct` does **not** move — the synthetic coverage
dataset has no residual label routing to a lease-current node, so the admitted
node contributes **0.0 pp** to the ~99% figure. That is expected and is stated
here so nobody later reads "35 nodes → ~99%" as though the 35th earned any of it:
**~99% is reached by the four volume-admitted nodes; the fifth was admitted on a
different, real-data criterion.** `scripts/coverage_benchmark.py` now reports the
admission basis per node so this stays machine-checkable rather than prose-only.

**Published numbers that do not move.** All eight CI-pinned validation figures
(75 entities, 68 countries, 97.3%, 25 distinct nodes, 4 escalations, total assets
14,746,037.81, and the 195/60/56 coverage manifest) are **unchanged**, because
`core.harness.ontology.load_ontology()` ingests only the `level3:` block and the
bare-list sections — it never reads `extended_core:`. Verified empirically before
and after, not assumed. The **minimum core stays frozen at exactly 30.**

## What this run does not license

**H1 and H5 must not be re-scored.** The gold standard's label vocabulary was
explicitly "one of the 30 core leaves", and the four blind labelers were
instructed to invent nothing outside it. A tag labeled empty *because no node
existed* may now have a node — `OperatingLeaseLiabilityCurrent` is exactly such a
tag. Adding a node therefore makes the committed gold **stale for accuracy
purposes**. Re-running the scorer and reporting an improved H1 would be invalid
twice over: **stale gold**, and **tuning on the set the change was designed
against**. Measuring the effect requires a fresh labeling round against the new
vocabulary, which is separate work.

**A finding deliberately left unacted-on.** `liability.noncurrent.lease` carries
`ifrs_tag: ifrs-full:OtherNonCurrentFinancialLiabilities` — one of the three
collisions item 3 documents — while a distinct `ifrs-full:NoncurrentLeaseLiabilities`
element exists and is attested in the ESEF corpus (134 facts / 31 filings).
Retagging it would genuinely resolve that collision. **It was not done here**,
for two reasons: it would change round 2's published A2 coverage figure in the
favourable direction on the very corpus that measured it, and it would break the
provenance argument that carries A2's non-circularity (`ifrs_tag` last touched
2026-07-20, before the round-2 branch opened 2026-07-30). It is recorded in the
item-3 allowlist as a candidate correction for a fresh-corpus round.
