# Spoke 1 — Branch & PR workflow (the rule)

This spoke uses a **long-lived integration branch** with **atomic PRs**, decided
2026-07-24. The rule, verbatim intent: *we make PRs onto this branch, as atomic
as possible, until the preprint is publication-ready; at that moment we merge to
`main` and publish on the open platform best suited to the target audience.*

## The branch model

```
main ──────────────────────────────────────────────●──►  (final merge, publication day)
                                                   ╱
claude/spoke1-agentic-provenance  ●──●──●──●──●──●●        (integration branch — this worktree)
                                  ▲  ▲  ▲  ▲  ▲            each ● = one merged atomic PR
                                  │  │  │  │  │
        claude/spoke1-related-work┘  │  │  │  └ claude/spoke1-figures ...
        claude/spoke1-claim-audit────┘  │  └─ claude/spoke1-inference-cost
                                        └─ claude/spoke1-threat-model
```

- **Integration branch:** `claude/spoke1-agentic-provenance` (off `main`, lives in
  `.claude/worktrees/spoke1-agentic-provenance`). The paper accumulates here.
- **Atomic work:** each task in `TASKS.md` gets its own branch
  `claude/spoke1-<task>` → **PR into the integration branch** (not into `main`).
- **Final merge:** integration branch → `main` **once, at publication**, then the
  release/DOI/cross-link steps run (see the local playbook).

Rationale: `main` stays clean and citable; the hub's CI claims-evidence gate is
never at risk from work-in-progress; Christian reviews small, single-concern PRs;
the whole spoke lands atomically when it is actually ready.

## What "atomic" means here

One PR = one concern, reviewable in isolation:
- ✅ "Add Related Work + references" · "Add Figure 1 (agent decision flow)" ·
  "Adversarial-agent threat-model subsection" · "Claim/code audit pass."
- ❌ "Related work + figures + threat model" (three concerns) — split it.

## Rules for every PR onto the integration branch

1. **Regenerable claims only.** Any new number cites a committed command
   (claims-evidence rule). No new figure/number without its generator.
2. **No fabricated citations.** Every reference is real and verifiable
   (epistemic-standards rule). Prefer primary sources.
3. **Don't touch the hub's citable surfaces or CI gate.** The spoke never edits
   `scripts/mass_consolidation_v2.py`, `results.json`, or the hub's
   abstract/README/CITATION.cff/.zenodo.json. Hub-side changes (the companion-
   paper cross-link) are staged in `HUB_UPDATE.md` and cut as a *separate* PR to
   `main` on publication day.
4. **Build stays green.** `pdflatex main.tex` (×2) compiles with no undefined refs
   before merge. Build artifacts are gitignored (`.gitignore`) — commit source
   only; `main.pdf` is added just once, at the publication merge.
5. **Data honesty.** The 75-entity / 441-entry dataset is *synthetic*; never
   describe it as real ledgers.

## Publication gate → merge to `main`

Merge the integration branch to `main` only when **all** are true:
- [ ] P0 tasks done: Related Work + references (T1), claim/code audit (T2),
      ≥1 figure (T3).
- [ ] `main.tex` compiles clean; Reproducibility commands all exit 0 in a fresh
      clone (T11).
- [ ] No unverifiable or fabricated claim; anti-salami gates (README) still hold.
- [ ] License + arXiv metadata staged (T9); `HUB_UPDATE.md` ready (T10).
- [ ] Venue locked in the **local** playbook (see below).

Then: run the local playbook (Zenodo/arXiv/workshop sequence), commit the final
`main.pdf`, cut the hub cross-link PR.

## The playbook is LOCAL ONLY

The publication/outreach playbook lives at
`docs/internal/spoke1-agentic-provenance-playbook.md` — inside the repo-wide
**gitignored** `docs/internal/` (same convention as the hub's launch playbook).
It carries venue tactics, endorsement strategy, and cross-posting notes. **It is
never committed.** Do not move it into the tracked tree.
