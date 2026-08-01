# Round-2 Follow-Ups — Work Items and Spoke Allocation

**Recorded 2026-07-31**, at the close of the round-2 execution (PR #112).
Parent document: [`research/real_data_validation_plan.md`](real_data_validation_plan.md).
Evidence for every item below: [`research/experiments/ROUND2_RESULTS.md`](experiments/ROUND2_RESULTS.md).

This is a **planning document, not a claim surface.** Nothing here is asserted as
a result; each item names what round 2 actually showed and what would have to be
built or measured to turn it into one.

## The distinction this document turns on

**Where the work happens ≠ where the result is published.** Most items below are
core-repo engineering whose *finding* lands in a spoke. Conflating the two is how
a spoke ends up carrying engineering it should only be citing, which is the
anti-salami rule's failure mode in reverse.

Second axis, and the one that actually governs cost:

| Class | What it touches | Cost |
|---|---|---|
| **Free** | new scripts, new tests, new derived artifacts | ship whenever |
| **Gated** | `level3_accounts.yaml` node set or `local_codes` | moves `mass_consolidation_v2.py` → trips the CI claims gate → forces the four citable surfaces to be updated **in the same PR** |
| **Fresh-holdout** | anything that would raise a score it is evaluated on | must be split before it is built, or the result is inadmissible |

Items 3, 5 and 7 are **gated**. Items 1 and 6 are **fresh-holdout**. Plan
accordingly — a gated change is never a quick fix in this repo.

## Spoke inventory (as decided; unchanged by this document)

| | Target | Status |
|---|---|---|
| **Hub** | Zenodo + SSRN monolith | **published**; frozen canonical; v1.10 planned |
| **Spoke 1** — agentic-provenance | arXiv cs.MA | **draft — NOT published.** Content-complete, nine PRs stacked unmerged, never merged to `main`, blocked on venue lock |
| **Spoke 2** — accountants / real data | SSRN → journal | **not started; this is round 2's spoke** |
| **Spoke 3** — mathematical | math.CT / ACT | pending; H¹ obstruction now demonstrable |
| **Spoke 4** — architecture | — | only if it accumulates its own result |

### Spoke 1 receives nothing from this list — deliberately

Items 1 and 3 both touch machinery spoke 1 claims (I1 ontology-as-constraint, I3
fiber query), so the pull to "just add this finding" is real. **Do not.** Spoke 1
is content-complete with nine stacked PRs waiting to merge in order, and its only
remaining blocker is a venue decision. Re-opening it to absorb a round-2 result
is precisely the "one more thing before publishing" pattern `CLAUDE.md` names as
an anti-pattern, and it would cost weeks to add a paragraph.

If a round-2 finding sharpens a spoke-1 invariant, that is a **citation from
spoke 2 back to spoke 1**, not an edit to spoke 1.

### The gated batch also has a mechanical dependency on spoke 1 (verified)

Not just an editorial one. `docs/papers/spokes/agentic-provenance/figures/gen_fig_fiber_query.py`
(on `claude/spoke1-agentic-provenance`) **generates** spoke 1's Figure 2 by calling
`core.harness.ontology.load_ontology()` and `node_fiber()` — over
`NODE = "asset.current.cash"`, which is one of the two nodes in item 3's
`CashAndCashEquivalents` collision. Spoke 1's T11 repro check asserts that figure
**regenerates byte-identical in a clean clone**.

So a gated change that alters `load_ontology()` / `node_fiber()` output for that
node changes that figure. Whether item 3 *specifically* does depends on how it is
implemented — a pure metadata/typing change to `ifrs_tag` should not touch
`node_fiber`, which reads `local_codes`, while restructuring `groupings` or
`local_codes` would. Items 5 and 7 add nodes and are riskier.

**Spoke 1 is NOT published.** It is a content-complete *draft*: nine PRs still
stacked and unmerged, never merged to `main`, blocked on the venue lock. So the
cost of disturbing it is **rework in an unmerged stack** — regenerate Figure 2,
re-verify the T11 repro check — not damage to a published artifact. That is
cheaper and fully reversible.

**Which means the sequencing argument cuts both ways, and the naive "wait for
spoke 1" is not automatically right:**

- *Land the gated batch first* → rework in the stack now, but spoke 1 publishes
  against a **corrected** ontology and never drifts from it.
- *Land it after* → no rework now, but a published spoke 1 drifts from the live
  repo the moment the ontology changes. **Stale-surface drift is this project's
  single most documented failure mode.**

### DECIDED 2026-07-31 (Christian): gated batch lands FIRST

**Spoke 1 publishes against a corrected ontology rather than drifting from it.**
The trade accepted knowingly: rework in spoke 1's unmerged stack now, in exchange
for eliminating a future drift between a published spoke and the live repo —
the failure mode this project has hit most often. Cheap precisely *because*
spoke 1 is still a draft; this option disappears the moment it publishes.

Consequences that follow, and are binding on the implementing session:

- Items 3, 5 and 7 ship as **one PR**, one claims-evidence rerun, one surface
  update.
- Item 7's *analysis* runs first — measuring real frequencies and emitting an
  ADR-015 decision record changes no number. Only its *outcome* is gated. Item 5
  is decided **by** item 7, not by fiat.
- Spoke 1's Figure 2 is regenerated **before and after** and any change reported,
  so its stack absorbs the new figure before publishing.

**The gold set does not survive this change.** The four blind labelers were
instructed to use "one of the 30 core leaves" and to invent nothing outside it, so
a tag labeled empty *because no node existed* may now have a node. Adding nodes
makes the committed gold **stale for accuracy purposes**. H1 and H5 must therefore
**not** be re-scored after this batch: doing so would be invalid twice over —
stale gold, and evaluating a change on the set it was designed against. Measuring
the effect requires a fresh labeling round against the new vocabulary, which is a
separate piece of work.

**What is non-negotiable either way:** regenerate Figure 2 and re-run the T11
repro check whenever the batch lands. If spoke 1 has published by then, the
ontology change joins the reconciliation list for its next revision rather than
being left as silent drift.

**Note that item 3 is already half-done.** The collision is recorded in
`results.json` (`ifrs_full_ambiguous_tags`) and CI-pinned by
`test_a2_ifrs_tag_ambiguity_is_recorded_not_coin_flipped`, so the finding is
captured and protected against silent tie-breaking. What remains is the formal
treatment (spoke 3) and any structural change — and only the latter is gated.

---

### STATUS 2026-07-31: the gated batch (3 / 5 / 7) has LANDED

Shipped as one PR, one claims-evidence rerun, one surface update, in the
sequence this document specified. Decision record:
[`research/experiments/adr015_admission_v1/DECISION_RECORD.md`](experiments/adr015_admission_v1/DECISION_RECORD.md);
policy addendum: [ADR-015 Addendum A](../docs/adr/015-core-node-admission-and-growth-policy.md).

- **Item 3 — done.** `ifrs_tag` is declared a many-to-one projection in
  `level3_accounts.yaml` and gated by `tests/test_ifrs_tag_projection.py`, whose
  allowlist fails the build in *both* directions (new undeclared collision, and
  stale entry). Scoping the gate to core **+ extended** immediately surfaced a
  **fourth** collision this document did not know about:
  `ifrs-full:CurrentTaxAssetsCurrent`, claimed by `asset.current.vat_input` and
  `asset.current.withholding_tax`. Round 2 scoped to the 30 and saw three.
- **Item 7 — done, and it produced a methodological result larger than the
  admission.** The literal 0.5% threshold **does not transfer** to real filing
  frequencies: all four already-admitted extended nodes fall below it on EDGAR,
  so applying it would reject the nodes ADR-015 already admitted. The floor is
  re-derived the way ADR-015 itself defines it (smallest already-admitted node,
  same population) → **0.100%**. One admission of seven:
  `liability.current.lease` at 0.645%.
- **Item 5 — DEFERRED, not delivered.** Item 7 decided it, as specified, and
  decided against: contra-assets measure 0.106% against a 0.100% floor — inside
  the noise band — and both corpora structurally under-observe the class because
  they measure face-statement presentation while contra accounts live in the
  notes (`PropertyPlantAndEquipmentNet` 34,510 facts vs `…Gross` 695). **The
  Distance-4 blocker this item names is therefore still open**, with the missing
  measurement now stated precisely rather than assumed.
- **Published numbers:** only one moved — extended core 34 → **35**. All eight
  CI-pinned validation figures and every coverage percentage are unchanged
  (`load_ontology()` never ingests `extended_core`; verified empirically, not
  assumed). Four citable surfaces updated in the same PR.
- **Spoke 1:** Figure 2 regenerated before and after — **byte-identical**, and
  identical to spoke 1's committed copy, so its T11 repro check still passes and
  the stack needs no rework. The prediction in this document held: a pure
  metadata/typing change to `ifrs_tag` does not touch `node_fiber`, which reads
  `local_codes`, and the admitted node landed in a layer the loader never reads.
- **H1 and H5 were NOT re-scored**, deliberately. See the closing section of the
  decision record.

Items 1, 2, 4 and 6 below remain open and unchanged.

## 1. Deterministic aggregate detection (XBRL calculation linkbase)

**Evidence.** H1's dominant error is over-mapping: **87 of 320 codes (27%)** were
mapped when the gold says escalate, against only **5** wrong-node errors. On tags
that genuinely are core accounts the resolver is right **94.6%** by fact volume.
The resolver has no notion of "this element is a subtotal"; Tier 2 sees a name,
matches a keyword, and maps.

**What to build.** Plan §9 already names the mechanism: an XBRL
presentation/calculation linkbase **explicitly marks totals** — an element with
children in the calculation linkbase is an aggregate. The ingestion currently
discards this. Wiring it in moves the aggregate/leaf decision from keyword
guessing to a graph lookup: principle #5 applied to the largest single error
class in the round.

**Hazard — fresh-holdout.** This will raise H1. It therefore **cannot** be scored
on the 2025q3–2026q1 window it was designed against. Reserve a later EDGAR
quarter before building.

**Home:** core engineering → result reported in **spoke 2**.

## 2. Re-derive the coverage headline from real frequencies

**Evidence.** `research/coverage_benchmark/` rests on a *labeled synthetic*
frequency distribution, which is why `CLAUDE.md` requires "~94%" to be described
as a model-based estimate. Round 2 committed **5.44M real EDGAR face-statement
facts with real frequencies**, satisfying the benchmark README's own stated
"roadmap to a real-corpus run".

**Honest framing constraint.** EDGAR is US-listed-company face statements, not
SME ledgers — a genuinely different population. This does **not** replace the SME
figure; it is a *second, independent, real-data estimate* reported alongside it.
Presenting it as a correction to the SME number would be a population swap
dressed as a measurement.

**Gated if the number moves.** ~94% sits on all four citable surfaces. If a
real-corpus figure is adopted as headline, the "one number, four surfaces" rule
applies and it becomes a **hub v1.10** change.

**Home:** core → **spoke 2** (reports it) → **hub** (only if a headline moves).

## 3. Decide what `ifrs_tag` *is* — a lens, not an identity

**Evidence.** The 30 core nodes carry **27** distinct `ifrs_tag` values.
`CashAndCashEquivalents` (cash vs bank), `CurrentTaxLiabilitiesCurrent`
(vat_output vs tax) and `OtherNonCurrentFinancialLiabilities` (debt vs lease) are
each claimed by two nodes. Real consequence: the most fundamental IFRS
balance-sheet tag of all cannot resolve.

**Why this is spoke 3's, not a bug ticket.** The fix is not inventing distinct
IFRS tags — `CashAndCashEquivalents` genuinely *is* one IFRS concept; cash-vs-bank
is a finer distinction Kontablo chose to make. The honest resolution is to type
`ifrs_tag` as a **many-to-one projection whose inverse is not a function**, which
is the same fiber/obstruction language spoke 3 already exists to formalize. This
is the tree-vs-graph tension appearing *inside* the ontology — a mathematical
statement with a worked instance, not a defect report.

**Home:** small core change; formal statement in **spoke 3**. **Gated.**

## 4. Ontology self-consistency CI gate

**Evidence.** All four internal inconsistencies share one root cause: a node's
meaning lives in **four places that can drift** — `label_en`, `ifrs_tag`, `notes`,
`aggregation_rules`. The sharp case is `expense.admin`, whose `ifrs_tag` says
narrow G&A while its own rule `ebit = gross_profit − expense.admin` makes it
absorb all operating expense. The two readings disagree about
`SellingGeneralAndAdministrativeExpense`, the largest opex line in US filings —
and both blind labelers got stuck there independently.

**What to build.** `tests/test_ontology_self_consistency.py`. Asserting only
"a node whose notes claim a current/non-current split has both halves present"
and "a node consumed by an aggregation rule has a scope-compatible `ifrs_tag`"
would have caught three of the four.

**Home:** **core only — no spoke.** Pure hygiene, no publishable result. Cheapest
item on this list and it protects the definitions every future gold standard
depends on. Do it first.

## 5. Model contra-accounts

**Evidence.** `PropertyPlantAndEquipmentGross` and
`AccumulatedDepreciation…` have **no home**; only the net carrying amount maps.
Both A1 labelers ruled them out of scope for the same reason: mapping gross *and*
net to one leaf would double-count, and the core has no contra leaf to pair with.

**Why it matters more than it looks.** For a project claiming lossless
translation and byte-exact reconstruction, a whole account *class* being
unrepresentable is structural. And it is the real blocker for Distance-4 (native
coded local charts): SKR04, PCG and PUC all carry explicit contra accounts, so
the gap bites hardest exactly where round 3 wants to go.

**Home:** core ontology change; structural treatment in **spoke 3**; unblocks
Distance-4 for a later round. **Gated** — this adds nodes.

## 6. Split a fresh Companies House holdout *before* touching `TIER2_RULES`

**Evidence.** H3 is falsified at 22.7% with a fully diagnosed cause (no British
English in Tier 2; 6 of 30 nodes have no rule at all). **77,263 filings are
inventoried and only 10 extracted.**

**Do this now, while there is no temptation.** Split by company-number hash into
dev/test before anyone adds a keyword. Doing the split first is the entire
difference between a publishable repair and tuning on the test set. It is nearly
free today and impossible to do honestly afterwards.

**Home:** core prep now → repair and evaluation reported in **spoke 2**.

## 7. Run the ADR-015 admission gate with real frequencies

**Evidence.** The gold pass produced an evidence-backed missing-node list:
intermediate consumption (the largest unmapped government expense line
worldwide), non-current tiers of tax/provision/payables, the current lease
portion, OCI components, restricted cash.

**Why now.** ADR-015's admission gate requires a *measured* volume criterion
(~0.5%). Until round 2 that could only be asserted against synthetic frequencies;
EDGAR now makes it measurable. The policy has never been exercised with real
data — this is what it was written for.

**Home:** core governance → **spoke 2** (coverage/admission narrative). **Gated**
if any node is admitted.

---

## Hub v1.10 — the strategic item

The hub's headline is the synthetic **97.3%**; round 2 measures **74.3%**
accuracy on real tags. These answer different questions on different corpora and
`ROUND2_RESULTS.md` documents that carefully — but a hostile reader will place
them side by side regardless.

Better to absorb round 2 into the hub's framing deliberately in v1.10 than to
have someone else draw the comparison. This is the same reconciliation slot
already reserved for the λ-claims correction via spoke 3.

## Suggested order

1. **#4** self-consistency gate — free, cheap, protects everything downstream.
2. **#6** Companies House holdout split — free, and the window to do it honestly
   closes the moment anyone edits `TIER2_RULES`.
3. **#2** real-frequency coverage — free, data already committed, feeds #7.
4. **#1** aggregate detection — needs a reserved holdout; largest score impact.
5. **#3 / #5 / #7** — the gated batch. Sequence together, one claims-evidence
   rerun, one PR touching the four citable surfaces.

## What is deliberately NOT on this list

Production NetSuite/SAP connectors, Rust migration, PQC implementation, security
audit. `CLAUDE.md` names these as the backlog a session wanders into when a phase
gate has passed. They are unrelated to round 2 and remain out of scope.
