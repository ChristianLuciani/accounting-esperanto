# Archived: pre-modular single-file preprint

These files are the **superseded, single-file (monolithic) build** of the Kontablo
preprint, kept for audit trail only. **Do not publish or cite them.**

- `kontablo_preprint.tex` / `kontablo_preprint.pdf` — the original monolithic
  source and its last generated PDF (PDF last built 2026-04-20). This build
  predates preprint v1.9.2 and is missing later content (e.g. the
  harness-architecture and labor-market sections, the Harari/LeCun
  non-delegability material, and the open-source call to action). The PDF was
  not rebuilt after later `.tex` edits, so it does not even match its own source.

## The canonical preprint

The current, citable preprint is the **modular** build, assembled from
`../sections/`:

```
docs/papers/drafts/kontablo_preprint_modular.tex   (source)
docs/papers/drafts/kontablo_preprint_modular.pdf   (publish this one)
```

Build it with:

```bash
export PATH="/usr/local/texlive/2024basic/bin/universal-darwin:$PATH"
cd docs/papers/drafts
latexmk -pdf kontablo_preprint_modular.tex     # auto-runs the needed passes
```

`.zenodo.json`, `README.md`, and `CLAUDE.md` all point to the modular PDF.
