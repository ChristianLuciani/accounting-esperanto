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

The middle graph is drawn in isometric pseudo-3D (single 2D canvas) so that the
cross-panel tracing arrows live in one coordinate system and stay exact. The
three edge colours encode the three independent graph dimensions:
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

fig, ax = plt.subplots(figsize=(13.5, 7.2))
ax.set_xlim(0, 19)
ax.set_ylim(0, 10)
ax.set_aspect("equal")
ax.axis("off")


def node(x, y, text, fc, ec, w=1.7, h=0.66, fs=8.5, bold=False, alpha=1.0,
         z=3, edge_lw=1.3):
    box = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                         boxstyle="round,pad=0.04,rounding_size=0.10",
                         fc=fc, ec=ec, lw=edge_lw, alpha=alpha, zorder=z)
    ax.add_patch(box)
    ax.text(x, y, text, ha="center", va="center", fontsize=fs,
            fontweight=("bold" if bold else "normal"), zorder=z + 1,
            color="#1a1a1a", alpha=alpha)
    return (x, y)


def edge(p, q, color="#666", lw=1.3, ls="-", z=1, alpha=1.0, arrow=True):
    style = "-|>" if arrow else "-"
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=10,
                                 color=color, lw=lw, ls=ls, alpha=alpha,
                                 shrinkA=2, shrinkB=2, zorder=z))


# ============================================================================
# 1. LEFT: local ERP tree (2D, leaves on the right edge for tracing)
# ============================================================================
ax.text(2.3, 9.5, "Local ERP Chart of Accounts", ha="center", fontsize=10.5,
        fontweight="bold", color=ORANGE_E)
ax.text(2.3, 9.05, "rigid 2-D tree  ·  one parent per account",
        ha="center", fontsize=7.5, style="italic", color="#888")

l_root = node(1.5, 8.0, "Assets\n(local ERP)", ORANGE_F, ORANGE_E, bold=True)
l_cur  = node(1.3, 6.3, "Current\nAssets", ORANGE_F, ORANGE_E, fs=8)
l_ncur = node(1.3, 3.4, "Non-current", ORANGE_F, ORANGE_E, fs=8)
# leaves aligned at x~3.8 for clean tracing
l_cash = node(3.8, 7.0, "101  Cash", "#FFF4E6", ORANGE_E, fs=8)
l_recv = node(3.8, 6.0, "105  Recv.", "#FFF4E6", ORANGE_E, fs=8)
l_inv  = node(3.8, 5.0, "151  Invent.", "#FFF4E6", ORANGE_E, fs=8)
l_ppe  = node(3.8, 3.4, "181  PP&E", "#FFF4E6", ORANGE_E, fs=8)

for a, b in [(l_root, l_cur), (l_root, l_ncur)]:
    edge(a, b, ORANGE_E, lw=1.2, arrow=False)
for b in (l_cash, l_recv, l_inv):
    edge(l_cur, b, ORANGE_E, lw=1.0, arrow=False)
edge(l_ncur, l_ppe, ORANGE_E, lw=1.0, arrow=False)

# ============================================================================
# 2. MIDDLE: Kontablo universal graph (isometric pseudo-3D, single canvas)
# ============================================================================
ax.text(9.5, 9.5, "Kontablo Universal Graph", ha="center", fontsize=10.5,
        fontweight="bold", color=BLUE_E)
ax.text(9.5, 9.05, "UUID-keyed nodes  ·  multi-dimensional edges",
        ha="center", fontsize=7.5, style="italic", color="#888")

# isometric depth offset
dx, dy = 0.5, 0.42
# front-layer node centres
g_cash = (8.3, 6.6)
g_recv = (10.6, 6.9)
g_inv  = (9.0, 4.6)
g_ppe  = (11.0, 4.5)
front = {"cash": g_cash, "recv": g_recv, "inv": g_inv, "ppe": g_ppe}

# ghost back layer (depth suggestion) + connectors
for (gx, gy) in front.values():
    bx, by = gx + dx, gy + dy
    ax.add_patch(plt.Circle((bx, by), 0.34, fc=BLUE_F, ec=GHOST, lw=0.8,
                            alpha=0.45, zorder=1))
    ax.plot([gx, bx], [gy, by], color=GHOST, lw=0.6, ls=":", alpha=0.6,
            zorder=1)

# dimension edges (front layer)
edge(g_cash, g_recv, DIM_IFRS, lw=1.6, ls="-",  z=2)              # IFRS
edge(g_recv, g_ppe,  DIM_IFRS, lw=1.6, ls="-",  z=2)
edge(g_cash, g_inv,  DIM_TAX,  lw=1.5, ls="--", z=2)             # Tax
edge(g_inv,  g_ppe,  DIM_TAX,  lw=1.5, ls="--", z=2)
edge(g_recv, g_inv,  DIM_FUN,  lw=1.5, ls=":",  z=2)             # Functional
edge(g_cash, g_ppe,  DIM_FUN,  lw=1.5, ls=":",  z=2)

# front nodes (cash highlighted as the traced example)
for key, (gx, gy) in front.items():
    hl = (key == "cash")
    ax.add_patch(plt.Circle((gx, gy), 0.40, fc=(GOLD if hl else BLUE_F),
                            ec=(GOLD if hl else BLUE_E),
                            lw=(2.4 if hl else 1.4), zorder=4,
                            alpha=(0.95 if hl else 1.0)))
    ax.text(gx, gy, key, ha="center", va="center", fontsize=7.5,
            fontweight="bold", color="#1a1a1a", zorder=5)
    ax.text(gx, gy - 0.62, "UUID", ha="center", va="center", fontsize=5.5,
            style="italic", color="#7a7a7a", zorder=5)

# ============================================================================
# 3. RIGHT: IFRS output tree (2D, leaves on the left edge)
# ============================================================================
ax.text(16.6, 9.5, "IFRS Balance-Sheet Output", ha="center", fontsize=10.5,
        fontweight="bold", color=GREEN_E)
ax.text(16.6, 9.05, "linearized 2-D tree  ·  one dimension as primary axis",
        ha="center", fontsize=7.5, style="italic", color="#888")

r_cash = node(15.0, 7.0, "Cash &\nEquiv.", "#EAF6EB", GREEN_E, fs=7.5)
r_recv = node(15.0, 6.0, "Trade\nRecv.", "#EAF6EB", GREEN_E, fs=7.5)
r_inv  = node(15.0, 5.0, "Invent.", "#EAF6EB", GREEN_E, fs=7.5)
r_ppe  = node(15.0, 3.4, "PP&E", "#EAF6EB", GREEN_E, fs=7.5)
r_cur  = node(17.2, 6.3, "Current\nAssets", GREEN_F, GREEN_E, fs=8)
r_ncur = node(17.2, 3.4, "Non-current", GREEN_F, GREEN_E, fs=8)
r_root = node(17.6, 8.0, "Balance\nSheet (IFRS)", GREEN_F, GREEN_E, bold=True)

for a, b in [(r_root, r_cur), (r_root, r_ncur)]:
    edge(b, a, GREEN_E, lw=1.2, arrow=False)
for b in (r_cash, r_recv, r_inv):
    edge(b, r_cur, GREEN_E, lw=1.0, arrow=False)
edge(r_ppe, r_ncur, GREEN_E, lw=1.0, arrow=False)

# ============================================================================
# 4. CROSS-PANEL MAPPING ARROWS (faint for all, GOLD for the traced example)
# ============================================================================
faint = [(l_recv, g_recv, r_recv), (l_inv, g_inv, r_inv),
         (l_ppe, g_ppe, r_ppe)]
for li, gi, ri in faint:
    edge((li[0] + 0.9, li[1]), (gi[0] - 0.45, gi[1]), "#B9B9B9",
         lw=1.0, z=1, alpha=0.7)
    edge((gi[0] + 0.45, gi[1]), (ri[0] - 0.9, ri[1]), "#B9B9B9",
         lw=1.0, z=1, alpha=0.7)

# GOLD traced path for "Cash"
edge((l_cash[0] + 0.9, l_cash[1]), (g_cash[0] - 0.45, g_cash[1]),
     GOLD, lw=2.6, z=6)
edge((g_cash[0] + 0.45, g_cash[1]), (r_cash[0] - 0.9, r_cash[1]),
     GOLD, lw=2.6, z=6)

# transition stage labels
ax.text(6.0, 8.2, "import", ha="center", fontsize=8.5, fontweight="bold",
        color="#666")
ax.text(6.0, 7.8, "(Tree → Graph)", ha="center", fontsize=7, style="italic",
        color="#999")
ax.text(13.1, 8.2, "linearize", ha="center", fontsize=8.5, fontweight="bold",
        color="#666")
ax.text(13.1, 7.8, "(Graph → Tree)", ha="center", fontsize=7, style="italic",
        color="#999")

# ============================================================================
# 5. legends
# ============================================================================
dim_legend = [
    Line2D([0], [0], color=DIM_IFRS, lw=1.8, ls="-",  label="IFRS / Balance-Sheet dim."),
    Line2D([0], [0], color=DIM_TAX,  lw=1.8, ls="--", label="Tax / Regulatory dim."),
    Line2D([0], [0], color=DIM_FUN,  lw=1.8, ls=":",  label="Functional / Cost-Centre dim."),
]
leg1 = ax.legend(handles=dim_legend, loc="lower center",
                 bbox_to_anchor=(0.5, -0.02), ncol=3, fontsize=7.5,
                 frameon=True, framealpha=0.9, title="Graph dimensions")
leg1.get_title().set_fontsize(7.5)
ax.add_artist(leg1)

trace_legend = [
    Line2D([0], [0], color=GOLD, lw=2.6, label="traced example: one account's journey (Cash)"),
    Line2D([0], [0], color="#B9B9B9", lw=1.2, label="other account mappings"),
]
ax.legend(handles=trace_legend, loc="upper center", bbox_to_anchor=(0.5, 0.07),
          ncol=2, fontsize=7.5, frameon=True, framealpha=0.9)

plt.tight_layout()

HERE = os.path.dirname(os.path.abspath(__file__))
pdf_path = os.path.join(HERE, "fig_tree_graph_tree.pdf")
png_path = os.path.join(HERE, "fig_tree_graph_tree.png")
fig.savefig(pdf_path, bbox_inches="tight")
fig.savefig(png_path, dpi=200, bbox_inches="tight")
print("Saved PDF :", pdf_path)
print("Saved PNG :", png_path)
