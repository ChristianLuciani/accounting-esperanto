## What

[One paragraph. What changes, and where.]

## Why

[The reason — not a restatement of the what. Link the issue: `Closes #N`.]

## Type

- [ ] `feat` — new capability
- [ ] `fix` — corrects something broken
- [ ] `docs` — documentation only
- [ ] `chore` — maintenance, tooling, dependencies
- [ ] `refactor` — no behaviour change
- [ ] `test` — tests only

## Claims and numbers

If this PR changes any number that appears in public documentation, it **must** update all four
citable surfaces in the same PR. Stale-count drift across them is this repository's documented
failure mode — the "23 jurisdictions" residue survived two release-prep passes.

- [ ] This PR changes a published number
  - [ ] All four surfaces updated: `docs/papers/drafts/sections/abstract.tex`, `README.md`,
        `CITATION.cff`, `.zenodo.json`
  - [ ] Expected value in `.github/workflows/ci.yml` updated if the number is gated
  - [ ] Regenerating command named below
- [ ] **OR** this PR does not touch any published number

**Regenerating command:**

```bash

```

## Evidence

- [ ] Every quantitative claim here is regenerable from the command above
- [ ] Synthetic data is described as synthetic — never as real ledger data
- [ ] Coverage is not described as accuracy
- [ ] Any threshold that was missed is stated as missed, not rounded to pass

## Tests

```bash
python -m pytest tests/
```

[Result: N passed, M skipped, K failed. If something is skipped, say why.]

## Scope

- [ ] One logical change
- [ ] No unrelated changes bundled in

## Checklist

- [ ] Branch follows `CONTRIBUTING.md` (`claude/`, `cursor/`, `contrib/<username>/`)
- [ ] Commits use Conventional Commits
- [ ] No LLM free-text drives control flow — branching keys on deterministic fields
- [ ] YAML values colliding with YAML 1.1 literals are quoted (`NO`, `ON`, `OFF`, `YES`, `Y`)
- [ ] New or corrected jurisdiction mappings cite a primary source
