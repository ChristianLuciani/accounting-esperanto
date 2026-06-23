# Post-ready figure images

PNG exports of the preprint's key figures, sized for social posts (X/LinkedIn).
Rendered from the LaTeX/TikZ sources in `../drafts/figures/` (and the matplotlib
source for the bridge figure). White background, trimmed, ~220 dpi.

| File | Figure | Suggested use |
|---|---|---|
| `fig_world_coverage.png` | Choropleth of all 195 sovereign jurisdictions — statutory-chart overlay + IFRS anchor (60) vs IFRS-direct (135) | "195 jurisdictions / complete global coverage" tweet (12/15), LinkedIn |
| `fig_kontablo_graph_architecture.png` | Local accounts (MX/FR/VN) → universal Kontablo node → IFRS, with an AI agent writing via AP2 | Hero image (launch tweet 1, LinkedIn) |
| `fig_tree_graph_tree.png` | Tree → Graph → Tree universal bridge | Hero / "what graph-based means" |
| `fig_tier_worked_example.png` | One account resolved by each of the three tiers (worked example) | Three-tier / Deterministic Boundary Library tweet |
| `fig_three_tier_pipeline.png` | Three-tier resolution control flow | Alternative to the worked example |
| `fig_cra_loop.png` | Co-responsibility Architecture review loop | Governance / human-accountability tweet |

Regenerate the TikZ exports from source with a TeX toolchain (see
`scripts/build_arxiv_tarball.sh` for the PATH setup); the matplotlib figure is
produced by `../drafts/figures/fig_tree_graph_tree.py`.
