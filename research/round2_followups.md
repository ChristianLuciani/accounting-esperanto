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
| **Hub** | Zenodo + SSRN monolith | frozen canonical; v1.10 planned |
| **Spoke 1** — agentic-provenance | arXiv cs.MA | **content-complete**, blocked only on venue lock |
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

So any gated change that alters `load_ontology()` / `node_fiber()` output for that
node breaks a claim spoke 1 has already published. Whether item 3 *specifically*
does depends on how it is implemented — a pure metadata/typing change to
`ifrs_tag` should not touch `node_fiber`, which reads `local_codes`, while
restructuring `groupings` or `local_codes` would. Items 5 and 7 add nodes and are
riskier.

**Practical rule: do not land the gated batch (3/5/7) while spoke 1 is in flight.**
It is cheap insurance — the batch is not urgent, and spoke 1 is waiting only on a
venue decision. Verify by regenerating Figure 2 before and after, whenever the
batch does land.

**Note that item 3 is already half-done.** The collision is recorded in
`results.json` (`ifrs_full_ambiguous_tags`) and CI-pinned by
`test_a2_ifrs_tag_ambiguity_is_recorded_not_coin_flipped`, so the finding is
captured and protected against silent tie-breaking. What remains is the formal
treatment (spoke 3) and any structural change — and only the latter is gated.

---

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
