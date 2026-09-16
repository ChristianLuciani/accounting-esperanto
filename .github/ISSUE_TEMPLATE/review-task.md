---
name: Review Task
about: Track a review that spans one or more pull requests
title: '[REVIEW] '
labels: needs-review
assignees: ''
---

## What is under review

[PR numbers, branches, or artifact. For a stacked PR, name the base it actually targets.]

## Diff to review

Review the branch against its **declared base**, not `main`. For a stack, `main...head`
would make you review the same code several times over.

```bash
git diff origin/<base>...origin/<head>
```

## Scope

[What this review is responsible for — and what it explicitly is not.]

## Checklist

Beyond correctness, this repository has non-negotiables that CI cannot check:

- [ ] **Claims–evidence** — every quantitative claim is regenerable from a committed command
- [ ] **Four surfaces** — `abstract.tex`, `README.md`, `CITATION.cff`, `.zenodo.json` agree
- [ ] **Epistemic honesty** — synthetic data called synthetic; coverage not called accuracy;
      missed thresholds stated as missed
- [ ] **No LLM free-text in control flow** — branching keys on deterministic fields only
      (jurisdiction, local code, ontology node)
- [ ] **YAML 1.1 traps** — `NO`, `ON`, `OFF`, `YES`, `Y`, `N` are quoted
- [ ] **Validation honesty** — 56 of 60 statutory charts verified is not "all 60"
- [ ] **Tests assert** — no test that prints `PASSED` instead of asserting
- [ ] **Scope** — no work beyond the stated objective

## Outcome

- [ ] Approve
- [ ] Request changes
- [ ] Close as superseded — superseded by: [link]

## Findings

[Record findings here.]

> **Line-anchored findings belong in the PR's own review, not in this issue** — an issue
> cannot anchor to a diff line, and `request changes` is a merge gate that an issue is not.
