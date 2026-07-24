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
| Design decision of record | `docs/adr/016-lossless-translation-and-provenance.md` |

**Data-honesty guardrail:** the 75 entities / 441 entries are *synthetic* trial
balances. The audit demonstrates a **property of the architecture**
(conservation, reconstruction, ledgered loss), never a measurement of real
ledgers. Keep that distinction in every edit (see the hub's identical rule).

## Current structure of `main.tex` (v0.1, adopted 2026-07-24)

Self-contained, single-file, ~10 pp on `clapps.cls` (clean-room house class):

1. Why does trust have to move into the architecture? (framing)
2. What is the resolution layer, and where can it lose information? (L1/L2/L3)
3. Three invariants for machine-verifiable trust (I1 / I2 / I3)
4. Result: a round-trip audit with zero silent losses (the anchor table)
5. Positioning: this is a resolution-layer property (vs. AP2/A2A)
6. Limitations and threats to validity
7. Conclusion + Reproducibility + Citing this work

## What's left before it can be published

See **[`TASKS.md`](TASKS.md)** — prioritized backlog + deep-research prompts.
The single biggest gap is **related work / references** (the draft currently has
zero `\cite`), which is why several of the deep-research prompts feed
`references.bib`.

## Workflow

See **[`WORKFLOW.md`](WORKFLOW.md)**. In short: atomic PRs land on this
integration branch; the branch merges to `main` only when the paper is
publication-ready. The publication/outreach **playbook is local-only**
(`docs/internal/`, gitignored) — never committed.

## How to build

```bash
cd docs/papers/spokes/agentic-provenance
pdflatex main.tex && pdflatex main.tex   # twice for \compactcontents + refs
```
`clapps.cls` needs only a base TeX Live / MiKTeX install (degrades gracefully if
Lexend/tcolorbox are absent).
