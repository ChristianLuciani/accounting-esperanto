# ADR 012: Mathematical Foundations and Prior-Art Positioning

**Status:** Proposed
**Date:** 2026-05-29
**Deciders:** Christian Luciani

> Note: ADR number **011** was already taken (`011-client-specific-determinism-agent.md`),
> so this record uses the next clean slot, **012**. The ADR README still carries known
> numbering debt (collisions on 005 and 008) — see Consequences. Do not renumber ad hoc.

## Context

Kontablo's core mechanism is described operationally across ADR 001 (graph over tree),
ADR 009 (determinism over stochasticity), and ADR 013 (ERP tree-to-graph compatibility):
a local statutory chart-of-accounts **tree** is lifted into a multi-dimensional universal
property **graph**, then projected back to a single-parent tree on export (linearization).
The preprint formalizes the carrier as `G = (V, E, λ, μ)` with a universal pivot node set
`V_universal`.

What is missing, ahead of public release, is (a) a formal account of *why* this mechanism
resolves the N:M mappings that defeat tree-to-tree approaches, (b) an honest boundary
between what is genuinely novel and what is an instance of established mathematics, and
(c) verifiable citations. The project's epistemic standard requires every non-trivial claim
to carry explicit uncertainty and a verifiable source.

Two failure modes to avoid:

- **Overclaiming novelty** where the construction is already known — a credibility and
  reviewer risk, especially at an applied-math or accounting venue.
- **Underclaiming** — omitting prior art that would strengthen the work and signal
  scholarly awareness of convergent results in other fields.

## Decision

### 1. Adopt a formal characterization of the translation mechanism

- **Import (tree → graph) and export (graph → tree linearization) are a pair of adjoint
  data-migration functors** in the sense of Spivak (2012). A schema mapping between two
  finitely-presented categories induces a pushforward (Σ, a "lift / merge") and a pullback
  (Δ, a "project"), and these are adjoint. Kontablo's import/export streams *are* an
  instance of this construction, not a new one. This is the precise sense in which the
  round trip is principled rather than ad hoc.
- **The Level-3 universal node set `V_universal` is the pivot (interlingua).** It is a
  jurisdiction-independent intermediate representation — the same role the *interlingua*
  plays at the apex of the Vauquois triangle in machine translation, and a colimit-like
  universal object in the categorical reading. "Raising the dimension" denotes two distinct
  moves that should not be conflated: (i) constructing this pivot, and (ii) admitting
  multi-dimensional (multi-parent) membership that a single-parent tree cannot express.
- **Round-trip fidelity is not free, and the loss is characterizable.** Linearization
  discards secondary analytical dimensions; the discarded content is exactly the failure of
  the graph to be a tree. Cross-jurisdiction reconciliability is characterized in
  **sheaf-cohomological** terms: `H⁰` is the globally consistent reconciliation, and
  `H¹ ≠ 0` is the formal obstruction to consistent gluing of local ledgers into a global
  one. This gives the **Inconsistency Flag** of the co-responsibility architecture a precise
  mathematical referent, and it ties back to ADR 009: a node's *deterministic boundary* is a
  sheaf **restriction map**, and a flagged mapping is a local section that fails to extend
  globally. Determinism and reconciliation thus share one formal language.

### 2. Position prior art in explicit strength tiers

Every cross-domain reference is tagged with the strength of the claim it supports, so the
paper never conflates a rigorous instance with a suggestive analogy.

| Tier | Meaning | References |
|------|---------|------------|
| **Foundation** | Kontablo's mechanism *is an instance of* this; cite as ground truth. | Functorial data migration (Spivak 2012; Spivak & Kent 2012, *ologs*); sheaf cohomology for data fusion (Robinson 2017; Curry 2014; Hansen & Ghrist 2019); the Pacioli group and multi-dimensional vector accounting (Ellerman 2014). |
| **Sibling** | A different field solves the *same* problem the *same* way; cite as convergent prior art. | Ontology / schema matching (Thiéblin et al. 2020); gene-tree/species-tree reconciliation (phylogenetics; e.g., Hasić & Tannier 2019); interlingua machine translation (Vauquois 1968); Gromov–Wasserstein structural alignment (Mémoli 2011; Xu et al. 2019). |
| **Analogy** | Shares the *principle* ("lift to resolve") but not the mechanism; cite only with the difference stated. | Cover's theorem / kernel methods (Cover 1965); the Leibniz–Descartes *characteristica universalis* (the historical-philosophical lineage of the Babel problem). |

The accounting-native anchor is **Ellerman (2014)**: double-entry bookkeeping *is* the group
of differences (the "Pacioli group"), and it already generalizes to multi-dimensional vector
accounting. Kontablo's multi-dimensional property graph is the data-structure realization of
exactly that generalization — making this a Foundation-tier citation that ties the work to
existing accounting scholarship, not only to mathematics.

### 3. Keep one integrative paper now; seed a roadmap of spin-outs

Continue with the single integrative preprint (currently v1.75). Do **not** split yet. Seed,
but do not start, a roadmap of targeted spin-outs to evaluate *after* the integrative
preprint is public:

- **Applied-math note** — the import/export adjunction plus the sheaf-cohomological
  reconciliation obstruction, with the Kontablo COA mapping as a worked example. Venue
  candidates: *Journal of Applied and Computational Topology*, *Compositionality*, or an
  applied-category-theory workshop.
- **Accounting note** — positioning relative to Ellerman and to the XBRL / ISO 20022
  execution gap; the deterministic ledger-mapping protocol as the contribution. Venue: an
  accounting-information-systems venue or one adjacent to *Accounting Education*.
- **Graph-theory review (parallel task)** — a focused survey of the tree → graph → tree
  translation problem (multi-parent membership, lossy linearization, reconciliation) as it
  appears across graph theory and topological data analysis, to map the frontier precisely.

**Split criterion:** a spin-out is justified only when its core claim is *load-bearing on its
own* — a theorem, or a measured empirical result — rather than a restatement of the
integrative paper. Mathematizing the solution is what makes the frontier legible: it shows
where the deterministic guarantees hold and where the obstruction (`H¹`) begins, which is
precisely the surface on which applicability can be widened.

## Consequences

**Easier:**

- Defensible, reviewer-proof citations with a clear novelty boundary.
- A reusable positioning map that any future spin-out can inherit.
- The formalism aligns with ADR 009 rather than competing with it: reconciliation
  obstruction and deterministic boundary now share one formal language (sheaf restriction
  maps / cohomology), which strengthens the determinism narrative.

**Harder:**

- Citation rigor must be maintained — every cross-domain claim ships with its tier or it
  does not ship.
- The formal section adds review surface and assumes a mathematically literate reader; the
  paper must keep an intuitive gloss beside the formalism so it stays accessible to the
  accounting audience.

**Open follow-ups / debt surfaced:**

- ADR numbering debt persists: the README notes collisions on 005 and 008, and the
  preprint's `ontology.tex` cites **ADR-008** for tree-to-graph compatibility while the
  current file is **013-erp-tree-to-graph-compatibility.md**. Resolve in a dedicated
  renumbering session — do not fix ad hoc, as other documents reference current filenames.
- The Gromov–Wasserstein / optimal-transport connection is **Sibling-tier and subordinate
  to ADR 009**: it is a candidate for *mapping-proposal generation under sparse labels* — an
  optimization-based, reproducible alternative to stochastic LLM guessing — never the
  production mapping authority. Production mapping stays deterministic; the human retains
  disposition (co-responsibility architecture).

## References

- Spivak, D. I. (2012). Functorial Data Migration. *Information and Computation* (2012).
  arXiv:1009.1166.
- Spivak, D. I., & Kent, R. E. (2012). Ologs: A Categorical Framework for Knowledge
  Representation. *PLoS ONE* 7(1): e24274.
- Robinson, M. (2017). Sheaves are the canonical data structure for sensor integration.
  *Information Fusion* 36: 208–224.
- Curry, J. (2014). *Sheaves, Cosheaves and Applications*. PhD thesis. arXiv:1303.3255.
- Hansen, J., & Ghrist, R. (2019). Toward a Spectral Theory of Cellular Sheaves.
  *Journal of Applied and Computational Topology* 3. arXiv:1808.01513.
- Ellerman, D. (2014). On Double-Entry Bookkeeping: The Mathematical Treatment.
  *Accounting Education* 23(5): 483–501. arXiv:1407.1898.
- Thiéblin, E., Haemmerlé, O., Hernandez, N., & Trojahn, C. (2020). Survey on complex
  ontology matching. *Semantic Web* 11(4). DOI:10.3233/SW-190366.
- Vauquois, B. (1968). A survey of formal grammars and algorithms for recognition and
  transformation in machine translation. *IFIP Congress*.
- Hasić, D., & Tannier, E. (2019). Gene tree species tree reconciliation. arXiv:1703.08950.
- Mémoli, F. (2011). Gromov–Wasserstein distances and the metric approach to object
  matching. *Foundations of Computational Mathematics* 11(4): 417–487.
- Xu, H., Luo, D., Zha, H., & Carin, L. (2019). Gromov-Wasserstein Learning for Graph
  Matching and Node Embedding. *ICML*. arXiv:1901.06003.
- Cover, T. M. (1965). Geometrical and Statistical Properties of Systems of Linear
  Inequalities with Applications in Pattern Recognition. *IEEE Trans. Electron. Comput.*
  EC-14(3): 326–334.
