---
name: Claim Change
about: Change, add, or retire a quantitative claim published in a citable surface
title: '[CLAIM] '
labels: claims-evidence
assignees: ''
---

## The claim

**Current wording** — quote it exactly:

> [exact current text, and the file it lives in]

**Proposed wording** — quote it exactly:

> [exact proposed text]

## Why it changes

[New measurement? Corrected methodology? A claim being retired? Be specific.
"Cleanup" is not a reason, and neither is "sounds better".]

## Regenerating command

Every quantitative claim must be regenerable from a committed, deterministic command.
If it cannot be, the claim must be labelled as an estimate or projection, with its basis.

```bash
# the command
# the artifact it writes
```

**What changed in the output:** [paste the relevant key and value from the artifact]

## The four citable surfaces

These must be updated **in the same PR**. Stale-count drift across them is this
repository's documented failure mode — the "23 jurisdictions" residue survived two
release-prep passes.

- [ ] `docs/papers/drafts/sections/abstract.tex`
- [ ] `README.md`
- [ ] `CITATION.cff`
- [ ] `.zenodo.json`

## Rounding

The command reports `[X]`; this claim says `[Y]`.

- [ ] Rounding moves **toward** the command's figure, never away from it
      (97.3% may be written as 97%, never as 98%)
- [ ] If a threshold was missed, it is stated as missed — not rounded until it passes

## Honesty check

- [ ] This is a **measurement**, not a model, projection or illustrative estimate
- [ ] If it is an estimate or model, the wording itself says so
- [ ] Synthetic data is described as synthetic — never as real ledger data
- [ ] Coverage is not described as accuracy
- [ ] The gap between the paper and the prototype is not blurred

## CI gate

The published numbers are asserted in `.github/workflows/ci.yml`. If this change moves
one of them, **update that block in this same PR.**

A red build on claim drift is working as designed. Do not weaken the assertion to make
it pass.
