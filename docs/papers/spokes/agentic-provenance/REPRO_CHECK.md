# Reproducibility check — clean-clone run (T11)

**Run date:** 2026-07-29
**Commit under test:** `c45a28f` (`claude/spoke1-geo-polish`, tip of the T3→T8 stack)
**Method:** fresh `git clone` into an empty directory outside the working tree —
no reuse of the development worktree's build artifacts, caches, or regenerated
files. Every command in the paper's Reproducibility section was then run in
order, and the resulting tree diffed against the committed artifacts.

**Verdict: PASS.** Every command exits 0; every published number regenerates;
the two `results.json` claims-evidence artifacts and the generated figure source
come back **byte-for-byte identical**. One non-blocking artifact-hygiene defect
was found and is recorded below with its fix — it is hub-side, so it is *not*
fixed in this spoke (see `WORKFLOW.md` rule 3).

---

## Environment

| Component | Version |
|---|---|
| Python | 3.12.13 |
| pdfTeX | 3.141592653-2.6-1.40.26 (TeX Live 2024) |
| BibTeX | TeX Live 2024 |

The two claim-generating scripts import only `json`, `os`, `sys`, `csv`,
`collections`, `importlib` and **`yaml`** from outside the standard library.
`pyyaml` is therefore the only third-party dependency needed to regenerate every
number in the paper, even though `requirements.txt` covers the whole repository
(FastAPI, pandas, grpcio, the MCP SDK, and so on). The figure generator adds
nothing: it imports `os`, `sys` and `core.harness.ontology`.

`clapps.cls` needs only a base TeX Live install; it degrades gracefully when
Lexend, titlesec, epigraph and tcolorbox are absent. TikZ, graphicx, booktabs,
amsmath, amssymb, float and url are all base-install packages.

---

## Results, command by command

### 1. `python scripts/roundtrip_audit.py`

Exit **0**. Console output matches the paper's Table 1 field for field:

```
entities                 75
jurisdictions            68
entries_in               441
entries_resolved_out     441
reconstruction_exact     True
provenance_complete      True
loss_ledger              {'ontology_code_collisions': 0, 'non_code_placeholders': 14,
                          'escalated_entries': 4, 'cra_flags': 2}
SILENT LOSSES            0
```

`research/experiments/roundtrip_audit/results.json` regenerated **byte-for-byte
identical** to the committed artifact (unchanged in `git status`).

### 2. `python scripts/mass_consolidation_v2.py`

Exit **0**. `research/experiments/consolidation_v2/results.json` regenerated
**byte-for-byte identical**, so the `97.3%` deterministic-coverage figure, the
`310` / `46` / `4` / `6` tier distribution quoted in §4.1, and the 75-entity /
68-jurisdiction counts all still hold at this commit.

`per_entry.csv` came back **modified** — see the defect below. Content is
identical; only the line terminator differs.

### 3. `python docs/papers/spokes/agentic-provenance/figures/gen_fig_fiber_query.py`

Exit **0**, reporting:

```
asset.current.cash: 57 local codes across 56 jurisdictions; shown: ['de', 'br', 'mx']
```

`figures/fig_fiber_query.tex` regenerated **byte-for-byte identical** to the
committed file. This is the property the generator exists to guarantee: Figure 2
cannot drift from the ontology it depicts without the diff showing it.

### 4. Six deterministic MCP tools

`grep -c "@server.tool(" api/mcp/server.py` → **6**, matching the paper's claim
and the T2 audit.

### 5. Paper build

`pdflatex` → `bibtex` → `pdflatex` ×2, all exit **0**:

- **16 pages**
- **0** undefined references
- **0** undefined citations
- **0** BibTeX warnings

Both TikZ figures render, and both land near their references (pp. 4 and 6)
rather than being deferred to the end of the document.

---

## Defect found: `per_entry.csv` is not byte-stable across regeneration

**Severity:** low. Cosmetic with respect to every published claim; annoying with
respect to the claims-evidence workflow.

**Symptom.** After running `scripts/mass_consolidation_v2.py` in a clean clone,
`git status` reports `research/experiments/consolidation_v2/per_entry.csv` as
modified even though nothing about the computation changed.

**Cause.** `mass_consolidation_v2.py` opens the file with `newline=""` (correct,
and required for the `csv` module), so `csv.DictWriter` writes its own standard
`\r\n` terminator. The *committed* copy of the file has LF terminators — it was
normalised at some point after generation. So the regenerated file is CRLF, the
committed file is LF, and the two differ by exactly 442 bytes (one extra `\r`
per line) with **identical content**: normalising line endings on both sides
makes them equal, verified.

**Why it matters.** `results.json` is the artifact every published number comes
from, and it *is* byte-stable — so no claim is affected. But a repro run that
leaves the tree dirty trains a reader to ignore a dirty tree, which is precisely
the signal the claims-evidence gate depends on.

**Fix (hub-side, not applied here).** Pass `lineterminator="\n"` to the
`DictWriter` in `scripts/mass_consolidation_v2.py:464` so the generated artifact
matches the committed one, then re-commit `per_entry.csv` once. Alternatively
add `research/experiments/**/*.csv text eol=crlf` to `.gitattributes`, though
that fixes the symptom rather than the mismatch.

This spoke does **not** apply the fix: `WORKFLOW.md` rule 3 forbids the spoke
from touching `scripts/mass_consolidation_v2.py` or the hub's experiment
artifacts. It is filed as separate hub-side work.

---

## Caveats on this run

- The clone was executed against a Python interpreter that already had `pyyaml`
  installed, rather than a freshly created virtualenv. The dependency surface
  was verified by inspecting the scripts' imports (only `yaml` is third-party),
  but a `python -m venv && pip install pyyaml` run was **not** performed. That is
  the one step between this check and a fully cold-start reproduction.
- The paper's numbers were checked against the regenerated artifacts, not
  re-derived independently. That is by design: the claim is that the committed
  command reproduces the committed artifact, which it does.
- `pytest` was not run as part of this check; it is the hub's CI gate, exercised
  on every push, and no code in this spoke changes behaviour.
