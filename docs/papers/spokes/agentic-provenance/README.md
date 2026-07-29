# Spoke 1 — Agentic Provenance

> **Deterministic Auditability Invariants for Autonomous Financial Agents:
> The Loss Ledger and Pre-Transaction Fiber Query**
> Christian Luciani · draft for arXiv **cs.MA** · integration branch
> `claude/spoke1-agentic-provenance`

This is the **first spoke** of the Kontablo hub-and-spoke publication program.
The canonical **hub** (specification of record) is the monolithic preprint,
Zenodo concept DOI [`10.5281/zenodo.20738795`](https://doi.org/10.5281/zenodo.20738795)
(resolves to the latest version; v0.3.0 version DOI `10.5281/zenodo.21465965`).
This spoke does **not** restate the hub's thesis. It isolates one question that
belongs to the **multi-agent-systems (cs.MA)** community and answers it with a
new, independently regenerable result.

## What question does this spoke answer?

> As AI agents begin to execute high-frequency financial transactions over
> protocols such as AP2 and A2A, **what deterministic auditability invariants
> must the semantic-resolution layer satisfy so those transactions are
> trustworthy without a human in the per-transaction critical path?**

Answer (the paper's contribution): three architectural invariants —
**I1** ontology-as-constraint, **I2** the loss ledger (`silent_losses == 0`),
**I3** the pre-transaction fiber query — demonstrated in a committed reference
implementation.

## Anti-salami compliance (non-negotiable spoke rule)

A spoke is not a trimmed copy of the hub. This one satisfies all three gates:

1. **New verifiable result the hub does not contain.** The hub's
   `agentic_economy.tex` still says the MCP server is "specified but not yet
   implemented." This spoke reports the **implemented** deterministic MCP core
   (6 tools, none calling an LLM) plus the **round-trip audit** proving
   `silent_losses == 0` over 441 entries — both shipped *after* the hub froze,
   both regenerable from committed code.
2. **A question owned by this community**, not the general thesis re-narrated:
   machine-verifiable trust at the resolution layer, positioned *beneath*
   settlement protocols (AP2/A2A), for cs.MA readers.
3. **Cite-back to the hub** as the normative specification (concept DOI).

## Claims → evidence (this spoke's own numbers)

Every quantitative claim regenerates from a committed, deterministic command
(the project-wide claims–evidence rule extends to the spokes).

| Claim in the paper | Generating command / source |
|---|---|
| 441 entries in → 441 resolved out; 0 missing / 0 phantom rows; reconstruction exact; 0 fiber mismatches; **`silent_losses == 0`** | `python scripts/roundtrip_audit.py` → `research/experiments/roundtrip_audit/results.json` (CI-gated) |
| Loss ledger: 0 collisions / 14 placeholders / 4 escalations / 2 CRA flags | same `results.json` (`loss_ledger` block) |
| 75 entities, 68 jurisdictions, 97.3% deterministic resolution, 4 escalations | `python scripts/mass_consolidation_v2.py` → `research/experiments/consolidation_v2/results.json` |
| **6** deterministic MCP tools, none invoking an LLM | `api/mcp/server.py` (`resolve_account`, `get_account`, `validate_balance_sheet`, `consolidate_trial_balances`, `get_node_fiber`, `list_jurisdictions`) |
| Fiber / rollup (I3) | `node_fiber`, `rollup` in `core/harness/ontology.py`; REST `GET /accounts/{id}/fiber`, MCP `get_node_fiber` |
| Figure 2's 57 local codes across 56 jurisdictions, and every code/name/local-parent shown | `python docs/papers/spokes/agentic-provenance/figures/gen_fig_fiber_query.py` → `figures/fig_fiber_query.tex` (regenerates byte-for-byte identical; verified in `REPRO_CHECK.md`) |
| Design decision of record | `docs/adr/016-lossless-translation-and-provenance.md` |

**Data-honesty guardrail:** the 75 entities / 441 entries are *synthetic* trial
balances. The audit demonstrates a **property of the architecture**
(conservation, reconstruction, ledgered loss), never a measurement of real
ledgers. Keep that distinction in every edit (see the hub's identical rule).

## Current structure of `main.tex` (v0.2, 2026-07-29)

Self-contained, single-file, **17 pp** on `clapps.cls` (clean-room house class).
Kept monolithic by decision — see `TASKS.md` T8:

1. Why does trust have to move into the architecture? (framing)
2. What is the resolution layer, and where can it lose information? (L1/L2/L3)
3. Which three invariants make the resolution step verifiable? (I1 / I2 / I3)
   - 3.4 What can a hostile or buggy agent do to these invariants? (threat model)
4. Result: a round-trip audit with zero silent losses (the anchor table)
   - 4.1 What does moving the decision off inference buy? (resource economy)
5. Related work: where these invariants sit (4 bodies of work + positioning)
6. Limitations and threats to validity
7. Conclusion + Reproducibility + Citing this work + License (CC BY 4.0)

Two figures, both regenerable: **Fig 1** the agent→layer decision flow with the
Tier-3/LLM path outside the tool surface (hand-written TikZ, every label
annotated with the `file:line` it comes from); **Fig 2** the pre-transaction
fiber query, *generated* from the live ontology by
`figures/gen_fig_fiber_query.py` so it cannot drift from the data it depicts.

## What's left before it can be published

**The T1–T11 backlog is complete** (2026-07-29). See
**[`TASKS.md`](TASKS.md)** for what each task decided and
[`WORKFLOW.md`](WORKFLOW.md#publication-gate--merge-to-main) for the merge gate.

Publication-gate status:

| Gate | State |
|---|---|
| P0: Related Work + references (T1), claim/code audit (T2), ≥1 figure (T3) | ☑ |
| Compiles clean; Reproducibility commands exit 0 in a fresh clone (T11) | ☑ — logged in [`REPRO_CHECK.md`](REPRO_CHECK.md); both `results.json` artifacts and the generated figure come back byte-for-byte identical |
| No unverifiable or fabricated claim; anti-salami gates hold | ☑ — residual audit TODOs closed in [`CLAIMS_AUDIT.md`](CLAIMS_AUDIT.md) §(d); the four external protocol quotations remain verified against the bibliography only, and are recorded as open rather than as verified |
| License + arXiv metadata staged (T9); `HUB_UPDATE.md` ready (T10) | ☑ — [`ARXIV_METADATA.md`](ARXIV_METADATA.md), [`HUB_UPDATE.md`](HUB_UPDATE.md) |
| Venue locked in the **local** playbook | ☐ — the one remaining item |

**The venue decision is the blocker, and DR5 reframed it.** arXiv `cs.MA`
requires endorsement, this project already hit that wall on the hub paper, and
the barrier got *harder* on 2026-01-21 (an institutional email alone no longer
suffices for auto-endorsement). So arXiv is **not** the first channel:
Zenodo first and unconditional, endorsement pursued in parallel and
non-blocking, arXiv when it lands. Full mechanics with primary sources in
[`research/dr5_arxiv_submission.md`](research/dr5_arxiv_submission.md);
submission-ready metadata in [`ARXIV_METADATA.md`](ARXIV_METADATA.md).

`DR6` (provenance/lineage models — W3C PROV, why/where/how-provenance) remains
**optional depth**, not a blocker.

## Workflow

See **[`WORKFLOW.md`](WORKFLOW.md)**. In short: atomic PRs land on this
integration branch; the branch merges to `main` only when the paper is
publication-ready. The publication/outreach **playbook is local-only**
(`docs/internal/`, gitignored) — never committed.

## How to build

```bash
cd docs/papers/spokes/agentic-provenance && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```
The `bibtex` pass is required since T1 — without it the citations render as
`[?]`. `clapps.cls` needs only a base TeX Live / MiKTeX install (degrades
gracefully if Lexend/tcolorbox are absent), and the bibliography uses the stock
`plain` style, so no extra packages are needed.

> `plain.bst` silently drops `url`/`eprint`/`doi` fields, so every entry in
> `references.bib` carries its locator inside `howpublished` (for `@misc`) or
> `note` (all other types). Keep that convention when adding references, or the
> new entry will render without a working link.
