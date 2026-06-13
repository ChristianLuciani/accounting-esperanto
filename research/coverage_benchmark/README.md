# Transaction-Volume Coverage Benchmark

**What fraction of routine transaction volume does the Kontablo Level-3 core capture?**
This directory makes that claim reproducible from a single committed command,
in line with the project's epistemic standard (every non-trivial claim must be
citable and verifiable).

## The headline numbers (regenerate them yourself)

```bash
venv/bin/python scripts/coverage_benchmark.py
```

Current result (`coverage_results.json`, line-weighted = by posting count):

| Account set | By posting line | By whole transaction |
|---|---|---|
| **Minimum core — 30 nodes** | **94.2 %** | 87.3 % |
| **Extended core — 34 nodes** | **98.8 %** | 97.1 % |

**Honest two-number framing for the paper:**

> The 30-account minimum core covers an estimated **~94 %** of routine
> transaction volume (posting-line count; ~87 % counted by whole transaction);
> an extended core of **34** accounts reaches **~99 %** (~97 % by whole
> transaction).

This is the **single source of truth** for the figure. The claims–evidence test
`tests/test_coverage_claim.py` pins `coverage_results.json` to the numbers cited
in the abstract, README, `CITATION.cff` and `.zenodo.json`, so the surfaces
cannot silently drift from the benchmark.

## Why this replaces the old "92 %" wording

The preprint previously stated the 30-account core "empirically" covers 92 % of
routine transaction volume, "as benchmarked against thousands of generic SME
ledger exports." **No such corpus or script was committed to this repository.**
That phrasing therefore overstated the evidence and would not survive a
reviewer asking to see the benchmark. The number 92 % was not wrong — it sits
inside the band this model produces (87–94 %) — but it was unbacked.

This benchmark replaces the unbacked assertion with a model whose every
assumption is inspectable and editable. The honest label is now **"estimated
~94 %," a model-based figure**, not "empirically 92 %."

## What the metric is (and is not)

- **It is:** coverage by **posting volume** — of all journal lines a
  representative SME posts in a period, what fraction land on a core node.
- **It is not:** the deterministic resolution rate (`deterministic_coverage_pct
  = 97.3 %`) reported by `scripts/mass_consolidation_v2.py`. That measures the
  share of synthetic ledger *entries* the deterministic tiers resolve to *some*
  node — a different question. The two numbers are not interchangeable.
- **It is not** a count of distinct accounts hit (`distinct_nodes_hit = 25`).

## Provenance of the dataset — read before citing

`transaction_frequency.yaml` is a **synthetic, transparently-parameterized
reference distribution. It is NOT a measurement of a real ledger corpus.**

- **Structure** (which transaction types dominate volume) is grounded in the
  standard double-entry **"special journals"** taxonomy: the overwhelming
  majority of postings flow through four high-frequency journals — Sales, Cash
  Receipts, Purchases, Cash Payments — while the General Journal carries only
  infrequent adjusting/closing entries. Sources:
  - Weygandt, Kieso & Kimmel, *Accounting Principles*, 13e (Wiley), Ch. 7.
  - Horngren, Harrison & Oliver, *Accounting*, 10e (Pearson), special journals.

  The four special-journal types map entirely onto core nodes (cash, bank,
  receivables, payables, inventory, VAT, revenue, expense) — which is the
  mechanism behind high volume coverage from a small core.
- **Weights** (postings per representative month) are the author's reasoned
  estimates anchored to that taxonomy, *not counted from field data*. They are
  exposed as plain numbers so a reviewer can substitute their own profile and
  re-run. The `miscellaneous_idiosyncratic` bucket (~20/month, "one idiosyncratic
  entry per business day") is an explicit assumption representing the persistent
  tail (suspense, intercompany, local minor taxes, novel instruments) that every
  real ledger carries — it is the empirical face of the **principled residual**
  and is deliberately *not* absorbed by the extended core.

## Sensitivity: what if the General-Journal tail is underweighted?

The natural attack on a synthetic distribution is "you cherry-picked the tail
weight." The benchmark answers quantitatively: `--misc-weight K` multiplies
every General Journal (tail) transaction's weight by K and re-measures, and
the default run commits the sweep to `coverage_results.json →
sensitivity_misc_weight`:

| Tail weight | Minimum core (30 nodes) | Extended core (34 nodes) |
|---|---|---|
| ×1.0 (committed distribution) | 94.2 % | 98.8 % |
| ×1.5 | 92.6 % | 98.3 % |
| ×2.0 | 91.1 % | 97.9 % |
| ×3.0 | 88.7 % | 97.2 % |

Even with the entire non-routine tail **tripled**, the 30-node minimum core
still covers ~89 % of posting volume and the extended core ~97 %. The headline
is robust to the assumption an adversary would most plausibly contest.

Regenerate any row: `python scripts/coverage_benchmark.py --misc-weight 2.0`

## Why the extended core stops at 34, not 100 % coverage

The four extended nodes (`liability.current.payroll`,
`liability.current.deferred_revenue`, `asset.current.withholding_tax`,
`asset.current.other_receivables`) are the largest out-of-core volume slices the
benchmark identified. Adding them lifts coverage from ~94 % to ~99 %. The paper
deliberately does **not** claim 100 %: new instruments (tokenised assets, CBDC,
novel Islamic-finance structures) and local rules continuously regenerate the
tail, and the Co-responsibility Architecture escalates the residual to a human
rather than forcing a low-confidence posting. Coverage → high, with a *bounded,
instrumented, human-resolved* remainder.

## Files

| File | Role |
|---|---|
| `transaction_frequency.yaml` | The synthetic frequency dataset (inputs + provenance). |
| `coverage_results.json` | Computed result (committed, regenerated by the script). |
| `coverage_breakdown.csv` | Per-transaction leg-by-leg audit of what is scored in/out. |
| `../../scripts/coverage_benchmark.py` | The computation. |

## Roadmap to a real-corpus run

The script does not change; only the dataset does. To upgrade from a model-based
estimate to a measured one, replace `transactions:` weights with per-line counts
from a **licensed, anonymized open ledger corpus** (e.g. an openly-licensed
accounting dataset, or aggregated export statistics published under a citable
licence), document the corpus and its licence here, and re-run. At that point
the wording can move from "estimated ~94 %" to "measured ~X % (n=…)."
