# Kontablo chart-of-accounts fidelity sweep — protocol

**Why this exists.** `localizations/<cc>/` files were found to be curated
subsets rather than exhaustive transcriptions of each country's official
chart (Ecuador had 13 hand-picked accounts against an official chart of 721).
This sweep corrects every `statutory_chart` jurisdiction, one country per
round, without letting `main` see partial/inconsistent claims mid-sweep.

## Branch structure

- **`claude/coa-fidelity-sweep`** — the long-lived trunk. Lives in its own
  worktree (`.claude/worktrees/coa-fidelity-sweep`). Every country round
  merges here. **Never PR this branch's per-round content to `main` directly**
  — `main` only receives the sweep as one deliberate, reconciled PR (see
  "Closing the sweep" below), reviewed and merged by Christian.
- **`claude/coa-fidelity-<cc>`** — one branch + worktree per country round,
  branched from the sweep trunk's current (merged) tip. Deleted after its PR
  merges.

## Per-round protocol (what `/loop` executes)

1. **Preflight.** Check whether the previous round's PR (into
   `claude/coa-fidelity-sweep`) is merged. If it's still open, do nothing —
   report status and wait. Manual review is deliberate (Christian reviews
   every country's PR before it lands on the trunk); the sweep paces itself
   to that review cadence, it does not rush ahead.
2. **Cleanup.** Once merged: `git worktree remove` the previous round's
   worktree, delete its local and remote branch.
3. **Pick the next jurisdiction.** Read `research/coa_fidelity/STATUS.yaml`
   (pull the sweep trunk first so it reflects the just-merged round). Take
   the next row with `fidelity_status: partial_curated_subset` and
   `mapping_mode: statutory_chart`, in file order — unless the invocation
   named an explicit ISO code, in which case use that instead.
4. **Branch + worktree.** `git worktree add .claude/worktrees/coa-fidelity-<cc>
   -b claude/coa-fidelity-<cc> claude/coa-fidelity-sweep` (branch from the
   trunk's tip, not from `main`).
5. **Research.** Find the country's official, government/regulator-published
   chart of accounts (or equivalent mandated statutory chart). Cite the
   exact URL. If no primary source is locatable, mark the row `blocked` with
   why, and stop this round (do not guess).
6. **Extract.** `pdftotext -layout` (or equivalent) + a parser in the style
   of `scripts/coa_fidelity/parse_official_chart.py` (write a new one if the
   source's layout differs) → `localizations/<cc>/<source>_official_chart.yaml`,
   a verbatim, source-cited transcription. No hand-picked subsetting.
7. **Classify.** `scripts/coa_fidelity/map_official_chart.py`-style
   deterministic longest-prefix classification onto
   `core/schemas/level3_accounts.yaml`'s existing Level-3 nodes. Every
   official code must appear; unmappable leaves are `needs_review: true`
   (never a forced/guessed node), statement-presentation captions are
   `is_statement_caption: true` (excluded from postable accounts).
8. **ERPNext tree.** `scripts/coa_fidelity/build_erpnext_tree.py` →
   `localizations/<cc>/default_tree_<cc>.json`.
9. **Ontology local_codes.** Add `<cc>: "<code>"` to the relevant nodes in
   `core/schemas/level3_accounts.yaml` (text-level insertion preserving
   existing comments — do not `yaml.safe_dump` the whole file).
10. **README.** Write `localizations/<cc>/README.md` documenting source,
    regenerate commands, and coverage honesty numbers (mapped / captions /
    aggregate / needs_review), matching `localizations/ec/README.md`'s
    format.
11. **Update `STATUS.yaml`** for this jurisdiction: `fidelity_status:
    verified`, official/current code counts, source URL + authority,
    `last_verified` date, notes.
12. **Scope discipline — do NOT touch this round:** `results.json`,
    `core/schemas/jurisdiction_coverage.yaml`, the CI claims-evidence
    `expected` block, `tests/test_surface_claims.py`, or any of the four
    citable surfaces (abstract.tex, README.md, CITATION.cff, .zenodo.json).
    Those are reconciled exactly once, at sweep close (see below) — touching
    them every round thrashes a reviewed academic preprint for no reason.
13. **Test.** `pytest tests/ connectors/` must stay green (this round's
    changes should not regenerate `results.json` — if running any script
    would do that as a side effect, don't run it this round).
14. **Commit, push, PR.** Commit only the files from steps 6–11. Push
    `claude/coa-fidelity-<cc>`. Open a PR with `--base
    claude/coa-fidelity-sweep` (never `main`), title
    `fix(<cc>): verified <N>-code official chart (round <k> of COA-fidelity sweep)`.
    Then **stop** — do not merge it yourself, and do not start the next
    round until it's reviewed.

## Closing the sweep (later, deliberate step — not part of any single round)

When the sweep reaches a stopping point the user chooses (all 61 statutory
jurisdictions, or a batch cut as v0.2.0):

1. Run `scripts/mass_consolidation_v2.py` once on the sweep trunk to get the
   final entity/country/coverage-pct/nodes-hit numbers.
2. Run `scripts/build_jurisdiction_manifest.py` for the final
   statutory/Tier-1 counts.
3. Update all four citable surfaces, `.github/workflows/ci.yml`'s expected
   block, and `tests/test_surface_claims.py`'s REQUIRED/BANNED lists in one
   commit.
4. Open the one PR from `claude/coa-fidelity-sweep` into `main` for
   Christian's review — this is the only point `main` moves.

## Status

See `STATUS.yaml` for live counts. Ecuador is the pilot (round 1, PR #78).
