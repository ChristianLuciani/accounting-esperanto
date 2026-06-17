#!/usr/bin/env python3
"""
Figure: Tree -> Graph -> Tree, the Kontablo linearization protocol.

Layout is HORIZONTAL (left -> right):
    [2D local ERP tree]  --import-->  [pseudo-3D Kontablo graph]  --linearize-->  [2D IFRS tree]

Pedagogical intent: let the reader VISUALLY TRACE how one account travels
through Kontablo. A single example account ("Cash") is highlighted in gold all
the way across: its input-tree leaf -> its UUID node in the multi-dimensional
graph -> its IFRS output-tree leaf. The other accounts are mapped faintly so
the traced path stands out.

Three design choices serve the pedagogy:
  (1) The left and right panels are drawn as explicit left-to-right DENDROGRAMS
      (root -> branch -> leaf) so they unmistakably read as single-parent trees.
  (2) The middle graph is drawn in isometric pseudo-3D (single 2D canvas) so the
      cross-panel tracing arrows live in one coordinate system and stay exact.
  (3) An isometric 3-axis frame sits UNDER the graph: each coloured axis is one
      of the three independent dimensions every node lives in, so the reader can
      see *why* the structure is a graph and not a tree.
        blue  solid  = IFRS / Balance-Sheet
        red   dashed = Tax / Regulatory
        violet dotted= Functional / Cost-Centre

Regenerate with:
    cd docs/papers/drafts && python3 figures/fig_tree_graph_tree.py
Outputs: figures/fig_tree_graph_tree.pdf (vector, embedded in the paper)
         figures/fig_tree_graph_tree.png (200 dpi, for visual inspection)
Deterministic: all node positions are fixed; no RNG.
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

# ---- palette (consistent with the rest of the paper) -----------------------
ORANGE_F, ORANGE_E = "#FBE3C9", "#C8742A"   # local / source
BLUE_F,   BLUE_E   = "#D6E4F5", "#2E5FA3"   # Kontablo / universal
GREEN_F,  GREEN_E  = "#D8EED9", "#3C8C42"   # IFRS / output
GOLD               = "#E8A317"              # highlighted traced path
DIM_IFRS, DIM_TAX, DIM_FUN = "#2E5FA3", "#C0392B", "#7D3C98"
GHOST              = "#9AB4D4"
INK                = "#1a1a1a"

# Keep the figure only modestly wider than the text block so that, scaled to
# \textwidth, the in-figure type stays close to the body \small size.
fig, ax = plt.subplots(figsize=(9.4, 6.1))
ax.set_xlim(0, 18)
ax.set_ylim(0, 11.7)
ax.set_aspect("equal")
ax.axis("off")

# Native font sizes are deliberately large; at \textwidth the figure is scaled
# down by ~0.66, landing the body type near the paper's \small.
FS_TITLE, FS_SUB = 14.5, 9.5
FS_NODE, FS_LEAF = 13, 12.5
FS_STAGE, FS_AXIS, FS_LEG = 12.5, 11, 10.5


def node(x, y, text, fc, ec, w=1.95, h=0.92, fs=FS_LEAF, bold=False,
         alpha=1.0, z=3, edge_lw=1.5):
    box = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                         boxstyle="round,pad=0.04,rounding_size=0.12",
                         fc=fc, ec=ec, lw=edge_lw, alpha=alpha, zorder=z)
    ax.add_patch(box)
    ax.text(x, y, text, ha="center", va="center", fontsize=fs,
            fontweight=("bold" if bold else "normal"), zorder=z + 1,
            color=INK, alpha=alpha)
    return (x, y)


def edge(p, q, color="#666", lw=1.5, ls="-", z=1, alpha=1.0, arrow=True,
         ms=13):
    style = "-|>" if arrow else "-"
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=ms,
                                 color=color, lw=lw, ls=ls, alpha=alpha,
                                 shrinkA=3, shrinkB=3, zorder=z))


# ============================================================================
# 1. LEFT: local ERP tree -- explicit left-to-right dendrogram
#    root --> branch --> leaf, leaves aligned on the inner (right) edge.
# ============================================================================
ax.text(2.7, 11.1, "Local ERP Chart", ha="center", fontsize=FS_TITLE,
        fontweight="bold", color=ORANGE_E)
ax.text(2.7, 10.5, "rigid tree · one parent each",
        ha="center", fontsize=FS_SUB, style="italic", color="#888")

l_root = node(1.05, 6.0, "Assets\n(local ERP)", ORANGE_F, ORANGE_E, bold=True,
              w=1.9, h=1.1)
l_cur  = node(2.95, 7.7, "Current\nAssets", ORANGE_F, ORANGE_E, fs=FS_NODE)
l_ncur = node(2.95, 3.7, "Non-current", ORANGE_F, ORANGE_E, fs=FS_NODE, h=0.8)
l_cash = node(5.05, 8.7, "101  Cash",   "#FFF4E6", ORANGE_E, h=0.8)
l_recv = node(5.05, 7.0, "105  Recv.",  "#FFF4E6", ORANGE_E, h=0.8)
l_inv  = node(5.05, 5.3, "151  Invent.", "#FFF4E6", ORANGE_E, h=0.8)
l_ppe  = node(5.05, 3.7, "181  PP&E",   "#FFF4E6", ORANGE_E, h=0.8)

for a, b in [(l_root, l_cur), (l_root, l_ncur)]:
    edge(a, b, ORANGE_E, lw=1.5, arrow=False)
for b in (l_cash, l_recv, l_inv):
    edge(l_cur, b, ORANGE_E, lw=1.2, arrow=False)
edge(l_ncur, l_ppe, ORANGE_E, lw=1.2, arrow=False)

# ============================================================================
# 2. MIDDLE: Kontablo universal graph (isometric pseudo-3D, single canvas)
# ============================================================================
ax.text(9.0, 11.1, "Kontablo Universal Graph", ha="center", fontsize=FS_TITLE,
        fontweight="bold", color=BLUE_E)
ax.text(9.0, 10.5, "UUID nodes · multi-dimensional",
        ha="center", fontsize=FS_SUB, style="italic", color="#888")

dx, dy = 0.55, 0.46                       # isometric depth offset
g_cash = (7.9, 7.7)
g_recv = (10.1, 8.1)
g_inv  = (8.5, 6.0)
g_ppe  = (10.4, 5.9)
front = {"cash": g_cash, "recv": g_recv, "inv": g_inv, "ppe": g_ppe}

# ghost back layer (depth suggestion) + connectors
for (gx, gy) in front.values():
    bx, by = gx + dx, gy + dy
    ax.add_patch(plt.Circle((bx, by), 0.40, fc=BLUE_F, ec=GHOST, lw=0.9,
                            alpha=0.45, zorder=1))
    ax.plot([gx, bx], [gy, by], color=GHOST, lw=0.7, ls=":", alpha=0.6,
            zorder=1)

# dimension edges (front layer) -- colour/style == the three axes below
edge(g_cash, g_recv, DIM_IFRS, lw=1.9, ls="-",  z=2, arrow=False)   # IFRS
edge(g_recv, g_ppe,  DIM_IFRS, lw=1.9, ls="-",  z=2, arrow=False)
edge(g_cash, g_inv,  DIM_TAX,  lw=1.8, ls="--", z=2, arrow=False)   # Tax
edge(g_inv,  g_ppe,  DIM_TAX,  lw=1.8, ls="--", z=2, arrow=False)
edge(g_recv, g_inv,  DIM_FUN,  lw=1.8, ls=":",  z=2, arrow=False)   # Functional
edge(g_cash, g_ppe,  DIM_FUN,  lw=1.8, ls=":",  z=2, arrow=False)

# front nodes (cash highlighted as the traced example)
for key, (gx, gy) in front.items():
    hl = (key == "cash")
    ax.add_patch(plt.Circle((gx, gy), 0.48, fc=(GOLD if hl else BLUE_F),
                            ec=(GOLD if hl else BLUE_E),
                            lw=(2.6 if hl else 1.6), zorder=4,
                            alpha=(0.95 if hl else 1.0)))
    ax.text(gx, gy, key, ha="center", va="center", fontsize=FS_LEAF - 1.5,
            fontweight="bold", color=INK, zorder=5)

# ----------------------------------------------------------------------------
# 2b. isometric 3-axis DIMENSION FRAME under the graph: each coloured axis is
#     one independent dimension, so the reader sees why the centre is a graph.
# ----------------------------------------------------------------------------
ox, oy = 9.0, 2.35                         # origin of the triad
axis_len = 1.25
# z-up = IFRS (solid blue), down-right = Tax (dashed red), down-left = Functional
A_ifrs = (ox,            oy + axis_len)
A_tax  = (ox + 1.25,     oy - 0.70)
A_fun  = (ox - 1.25,     oy - 0.70)
ax.add_patch(plt.Circle((ox, oy), 0.07, fc=INK, ec=INK, zorder=6))
edge((ox, oy), A_ifrs, DIM_IFRS, lw=2.0, ls="-",  z=6, ms=14)
edge((ox, oy), A_tax,  DIM_TAX,  lw=2.0, ls="--", z=6, ms=14)
edge((ox, oy), A_fun,  DIM_FUN,  lw=2.0, ls=":",  z=6, ms=14)
ax.text(ox + 0.12, A_ifrs[1] - 0.05, "IFRS", ha="left", va="top",
        fontsize=FS_AXIS - 1, color=DIM_IFRS, fontweight="bold")
ax.text(A_tax[0] + 0.16, A_tax[1] + 0.02, "Tax", ha="left",
        va="center", fontsize=FS_AXIS - 1, color=DIM_TAX, fontweight="bold")
ax.text(A_fun[0] - 0.16, A_fun[1] + 0.02, "Functional", ha="right",
        va="center", fontsize=FS_AXIS - 1, color=DIM_FUN, fontweight="bold")
ax.text(ox, oy + axis_len + 0.45, "3 independent dimensions", ha="center",
        va="bottom", fontsize=FS_SUB, style="italic", color="#777")

# ============================================================================
# 3. RIGHT: IFRS output tree -- mirror dendrogram (leaf -> branch -> root)
# ============================================================================
ax.text(15.3, 11.1, "IFRS Output Tree", ha="center", fontsize=FS_TITLE,
        fontweight="bold", color=GREEN_E)
ax.text(15.3, 10.5, "linearized · one primary axis",
        ha="center", fontsize=FS_SUB, style="italic", color="#888")

r_cash = node(12.95, 8.7, "Cash &\nEquiv.", "#EAF6EB", GREEN_E, h=0.92)
r_recv = node(12.95, 7.0, "Trade\nRecv.", "#EAF6EB", GREEN_E, h=0.92)
r_inv  = node(12.95, 5.3, "Invent.", "#EAF6EB", GREEN_E, h=0.8)
r_ppe  = node(12.95, 3.7, "PP&E", "#EAF6EB", GREEN_E, h=0.8)
r_cur  = node(15.05, 7.7, "Current\nAssets", GREEN_F, GREEN_E, fs=FS_NODE)
r_ncur = node(15.05, 3.7, "Non-current", GREEN_F, GREEN_E, fs=FS_NODE, h=0.8)
r_root = node(16.95, 6.0, "Balance\nSheet (IFRS)", GREEN_F, GREEN_E, bold=True,
              w=1.9, h=1.1)

for a, b in [(r_root, r_cur), (r_root, r_ncur)]:
    edge(b, a, GREEN_E, lw=1.5, arrow=False)
for b in (r_cash, r_recv, r_inv):
    edge(b, r_cur, GREEN_E, lw=1.2, arrow=False)
edge(r_ppe, r_ncur, GREEN_E, lw=1.2, arrow=False)

# ============================================================================
# 4. CROSS-PANEL MAPPING ARROWS (faint for all, GOLD for the traced example)
# ============================================================================
faint = [(l_recv, g_recv, r_recv), (l_inv, g_inv, r_inv),
         (l_ppe, g_ppe, r_ppe)]
for li, gi, ri in faint:
    edge((li[0] + 1.0, li[1]), (gi[0] - 0.52, gi[1]), "#B9B9B9",
         lw=1.1, z=1, alpha=0.7)
    edge((gi[0] + 0.52, gi[1]), (ri[0] - 1.0, ri[1]), "#B9B9B9",
         lw=1.1, z=1, alpha=0.7)

# GOLD traced path for "Cash"
edge((l_cash[0] + 1.0, l_cash[1]), (g_cash[0] - 0.52, g_cash[1]),
     GOLD, lw=3.0, z=7)
edge((g_cash[0] + 0.52, g_cash[1]), (r_cash[0] - 1.0, r_cash[1]),
     GOLD, lw=3.0, z=7)

# transition stage labels
ax.text(6.5, 9.7, "import", ha="center", fontsize=FS_STAGE, fontweight="bold",
        color="#555")
ax.text(6.5, 9.2, "(Tree → Graph)", ha="center", fontsize=FS_SUB,
        style="italic", color="#999")
ax.text(11.7, 9.7, "linearize", ha="center", fontsize=FS_STAGE,
        fontweight="bold", color="#555")
ax.text(11.7, 9.2, "(Graph → Tree)", ha="center", fontsize=FS_SUB,
        style="italic", color="#999")

# ============================================================================
# 5. legends
# ============================================================================
dim_legend = [
    Line2D([0], [0], color=DIM_IFRS, lw=2.0, ls="-",  label="IFRS / Balance-Sheet dim."),
    Line2D([0], [0], color=DIM_TAX,  lw=2.0, ls="--", label="Tax / Regulatory dim."),
    Line2D([0], [0], color=DIM_FUN,  lw=2.0, ls=":",  label="Functional / Cost-Centre dim."),
]
leg1 = ax.legend(handles=dim_legend, loc="lower center",
                 bbox_to_anchor=(0.5, -0.04), ncol=3, fontsize=FS_LEG,
                 frameon=True, framealpha=0.9, title="Graph dimensions")
leg1.get_title().set_fontsize(FS_LEG)
ax.add_artist(leg1)

trace_legend = [
    Line2D([0], [0], color=GOLD, lw=3.0, label="traced example: one account's journey (Cash)"),
    Line2D([0], [0], color="#B9B9B9", lw=1.4, label="other account mappings"),
]
ax.legend(handles=trace_legend, loc="lower center", bbox_to_anchor=(0.5, 0.04),
          ncol=2, fontsize=FS_LEG, frameon=True, framealpha=0.9)

plt.tight_layout()

HERE = os.path.dirname(os.path.abspath(__file__))
pdf_path = os.path.join(HERE, "fig_tree_graph_tree.pdf")
png_path = os.path.join(HERE, "fig_tree_graph_tree.png")
fig.savefig(pdf_path, bbox_inches="tight")
fig.savefig(png_path, dpi=200, bbox_inches="tight")
print("Saved PDF :", pdf_path)
print("Saved PNG :", png_path)
