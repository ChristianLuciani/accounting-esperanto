# arXiv submission — Kontablo preprint

Paste-ready package for submitting the Kontablo preprint to arXiv. The source has
been compile-verified (65 pages, 12 figures) with TeX Live and bundled as a
ready-to-upload tarball.

> **License note.** On arXiv, select **CC BY 4.0** for the paper. This is the
> paper's license and is independent of the *code's* BSL 1.1 — paper text and
> source code are separate works (see [`docs/papers/LICENSE`](../papers/LICENSE)).
> It matches the license used on Zenodo, SSRN, and ResearchGate.

---

## What to upload

**Preferred — LaTeX source** (arXiv recompiles it; cleaner result, real metadata):

- File: [`docs/papers/arxiv/kontablo-arxiv-src.tar.gz`](../papers/arxiv/kontablo-arxiv-src.tar.gz)
- Contents: `kontablo_preprint_modular.tex` (main), `clapps.cls` (house style),
  `sections/*.tex`, `figures/*.tex`, and `figures/fig_tree_graph_tree.pdf`.
- Verified: compiles standalone with `latexmk -pdf` → 65 pages, 0 errors.
- Regenerate with [`scripts/build_arxiv_tarball.sh`](../../scripts/build_arxiv_tarball.sh).

**Fallback — single PDF:** `docs/papers/drafts/kontablo_preprint_modular.pdf`
(accepted, but arXiv prefers source; use only if the source upload is rejected).

---

## Form fields (copy-paste)

**Title**

```
Kontablo: A Graph-Based Universal Accounting Ontology for the M2M Agentic Economy
```

**Authors**

```
Christian Luciani
```
- Affiliation: Independent Researcher, Cuenca, Ecuador
- ORCID: 0000-0002-6955-5384 (link it in the arXiv author profile)

**Categories**

| Role | Category |
|---|---|
| Primary | **cs.CE** (Computational Engineering, Finance, and Science) |
| Cross-list | **cs.AI** (Artificial Intelligence) |
| Cross-list | **q-fin.GN** (General Finance) |
| Optional cross-list | cs.CY (Computers and Society) |

**Comments** (free-text field)

```
65 pages, 12 figures. Preprint also on Zenodo (doi:10.5281/zenodo.20738795,
concept DOI) and SSRN (abstract 6960598). Reference implementation:
https://github.com/ChristianLuciani/accounting-esperanto
```

**License**: Creative Commons Attribution 4.0 International (CC BY 4.0)

**Abstract** (plain text — paste verbatim)

```
Kontablo is an open, graph-based universal accounting ontology anchored to International Financial Reporting Standards (IFRS) and mapped across all 195 sovereign jurisdictions, with statutory chart-of-accounts overlays for the 60 jurisdictions that mandate a national chart, providing a deterministic, jurisdiction-agnostic subledger for both multinational ERP consolidation and the Machine-to-Machine (M2M) Agentic Economy. The global accounting ecosystem remains fragmented across incompatible national standards — an "Accounting Babel" that costs multinational enterprises billions in manual reconciliation and poses a structural barrier to high-frequency autonomous transactions. As AI agents begin to execute financial operations via Agent Payments (AP2) and Agent2Agent (A2A) protocols, they require a semantic execution layer that existing reporting standards (XBRL) and payment messaging protocols (ISO 20022) do not provide. Kontablo addresses this gap through three core contributions: (1) a Level 3 minimum-core taxonomy of 30 universal accounts covering an estimated ~94% of routine transaction volume by posting count (rising to ~99% with a 34-account extended core), reproducible from a committed transaction-frequency benchmark; (2) a Three-Tier Resolution Strategy combining deterministic exact-code lookups and regex-based disambiguation rules with a confidence-scored semantic AI fallback, bounded by a Deterministic Boundary Library that eliminates the classical accounting hallucination class at the harness level; and (3) a Co-responsibility Architecture (CRA) that pairs every AI mapping proposal with a mandatory human review pathway and an append-only inconsistency audit trail, keeping legal accountability with the human operator in all cases. We validate the framework on a synthetic matrix built from the ontology's own committed code sets, using a reproducible mass-consolidation engine across 75 entities in 68 jurisdictions, spanning fourteen languages and five writing systems, including four IAS 29 dual-rate hyperinflation stress tests (Venezuela, Argentina, Lebanon, Turkey); the deterministic tiers resolve 97% of entries, and Tier-1 exact-code coverage is exercised against primary-source-cited statutory charts in 56 of the 60 statutory-chart jurisdictions.
```

> The committed `.zenodo.json` `description` ends with a sentence about the code's
> BSL 1.1 license; it is dropped above because arXiv has a dedicated license field
> and the BSL applies to the code, not the paper.

---

## Two hurdles to expect

1. **Endorsement.** As a first-time independent submitter to `cs.*`, arXiv may
   require an endorsement before the paper can post. If so, arXiv emails an
   endorsement code; a colleague who already publishes in cs.CE / cs.AI can
   endorse you. Submit first and see whether it is triggered — don't pre-empt it.

2. **Moderation / reclassification.** Moderators may move the paper to another
   category (e.g. cs.DB) or hold a submission that reads as a "standard proposal"
   rather than a research result. Mitigation: the abstract already leads with the
   validated result (75 entities / 68 jurisdictions / 97% deterministic resolution)
   and three named contributions — keep that framing in any cover note.

---

## After it posts

- Add the arXiv ID to your ORCID record and Google Scholar.
- Add an `isIdenticalTo` related-identifier for the arXiv URL in `.zenodo.json`
  and a `url` identifier in `CITATION.cff` (mirroring how SSRN/ResearchGate are
  wired), then announce "now also on arXiv" on the launch thread.
