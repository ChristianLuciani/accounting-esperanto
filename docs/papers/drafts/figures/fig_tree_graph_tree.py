"""
fig_tree_graph_tree.py
======================
Generates Figure 8: "Tree-to-Graph-to-Tree: the Kontablo linearisation protocol"
as a vertical 3-panel figure.

  TOP    : Local ERP chart-of-accounts (2D tree, orange palette)
  MIDDLE : Kontablo Universal Graph (real 3D axes, blue palette,
           three edge colours for IFRS / Tax / Functional dimensions)
  BOTTOM : IFRS Balance Sheet output (2D tree, green palette)

Run from docs/papers/drafts/:
    python3 figures/fig_tree_graph_tree.py

Outputs (same directory as this script):
    figures/fig_tree_graph_tree.pdf   <- embedded in LaTeX
    figures/fig_tree_graph_tree.png   <- quick visual inspection

Dependencies: matplotlib >= 3.5, networkx >= 2.6
Deterministic: fixed random seed + explicit node positions throughout.
"""

import os
import sys
import warnings
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D          # noqa: F401  (registers projection)

# ---------------------------------------------------------------------------
# Output paths
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
PDF_OUT = os.path.join(HERE, "fig_tree_graph_tree.pdf")
PNG_OUT = os.path.join(HERE, "fig_tree_graph_tree.png")

# ---------------------------------------------------------------------------
# Colour palette  (matches paper conventions)
# ---------------------------------------------------------------------------
C_ORANGE_FILL   = "#FFD699"
C_ORANGE_EDGE   = "#C86400"
C_ORANGE_LABEL  = "#7A3C00"

C_BLUE_FILL     = "#C0D8F5"
C_BLUE_EDGE_N   = "#1E5FA3"
C_BLUE_TEXT     = "#0D3D6B"

C_GREEN_FILL    = "#B8E8C0"
C_GREEN_EDGE    = "#1A7A35"
C_GREEN_LABEL   = "#0D4020"

C_IFRS_DIM      = "#1E5FA3"
C_TAX_DIM       = "#C0392B"
C_FUNC_DIM      = "#7D3C98"

C_ARROW         = "#888888"
C_BG            = "#FAFAFA"

# ---------------------------------------------------------------------------
# Figure layout
# ---------------------------------------------------------------------------
FIG_W = 8.0
FIG_H = 13.5

fig = plt.figure(figsize=(FIG_W, FIG_H), facecolor=C_BG)
fig.patch.set_facecolor(C_BG)

from matplotlib import gridspec
gs = gridspec.GridSpec(
    7, 1,
    figure=fig,
    height_ratios=[0.15, 2.2, 0.45, 3.2, 0.45, 2.2, 0.15],
    hspace=0.0,
)

ax_top  = fig.add_subplot(gs[1])
ax_arr1 = fig.add_subplot(gs[2])
ax_mid  = fig.add_subplot(gs[3], projection="3d")
ax_arr2 = fig.add_subplot(gs[4])
ax_bot  = fig.add_subplot(gs[5])

for ax in (ax_arr1, ax_arr2):
    ax.set_facecolor("none")
    ax.axis("off")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def rounded_box(ax, cx, cy, w, h, fc, ec, lw=1.2):
    from matplotlib.patches import FancyBboxPatch
    box = FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle="round,pad=0.10",
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3,
    )
    ax.add_patch(box)

def node_text(ax, cx, cy, line1, line2="", color="#222222", fs=8):
    txt = line1 + ("\n" + line2 if line2 else "")
    ax.text(cx, cy, txt, ha="center", va="center",
            fontsize=fs, color=color, fontweight="bold",
            multialignment="center", zorder=4)

def tree_edge(ax, x0, y0, x1, y1, color, lw=1.6):
    ax.annotate(
        "", xy=(x1, y1), xytext=(x0, y0),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=lw),
        zorder=2,
    )

# ===========================================================================
# PANEL 1: LOCAL ERP TREE
# ===========================================================================
ax_top.set_facecolor(C_BG)
ax_top.set_xlim(0, 10)
ax_top.set_ylim(-3.8, 1.0)
ax_top.axis("off")

ax_top.text(5, 0.75, "Local ERP Chart of Accounts",
            ha="center", va="center", fontsize=11, fontweight="bold",
            color=C_ORANGE_LABEL)
ax_top.text(5, 0.30, "one parent per node  ·  jurisdiction codes as primary keys",
            ha="center", va="center", fontsize=7.5, color="#999999", style="italic")

BW, BH = 1.9, 0.52

positions_top = {
    "root": (5.0, -0.4),
    "cur":  (2.8, -1.65),
    "ncur": (7.2, -1.65),
    "cash": (1.3, -3.1),
    "recv": (3.2, -3.1),
    "inv":  (5.5, -3.1),
    "ppe":  (8.0, -3.1),
}
labels_top = {
    "root": ("Assets", "(local ERP)"),
    "cur":  ("Current", "Assets"),
    "ncur": ("Non-current", "Assets"),
    "cash": ("101", "Cash"),
    "recv": ("105", "Receivables"),
    "inv":  ("151", "Inventory"),
    "ppe":  ("181", "PP&E"),
}

for key, (cx, cy) in positions_top.items():
    rounded_box(ax_top, cx, cy, BW, BH,
                fc=C_ORANGE_FILL if key == "root" else "#FFF0D9",
                ec=C_ORANGE_EDGE, lw=1.6 if key == "root" else 1.2)
    l1, l2 = labels_top[key]
    node_text(ax_top, cx, cy, l1, l2, color=C_ORANGE_LABEL, fs=8)

for src, dst in [("root","cur"),("root","ncur"),("cur","cash"),("cur","recv"),("cur","inv"),("ncur","ppe")]:
    x0, y0 = positions_top[src]
    x1, y1 = positions_top[dst]
    tree_edge(ax_top, x0, y0 - BH/2, x1, y1 + BH/2, C_ORANGE_EDGE)

# ===========================================================================
# ARROW 1
# ===========================================================================
ax_arr1.set_xlim(0, 10)
ax_arr1.set_ylim(0, 1)
ax_arr1.annotate("", xy=(5, 0.08), xytext=(5, 0.92),
    arrowprops=dict(arrowstyle="-|>", color=C_ARROW, lw=3.0, mutation_scale=20))
ax_arr1.text(5.4, 0.62, "Tree-to-Graph", ha="left", va="center",
             fontsize=9, fontweight="bold", color="#666666")
ax_arr1.text(5.4, 0.28, "(import)", ha="left", va="center",
             fontsize=8, color="#999999", style="italic")

# ===========================================================================
# PANEL 2: KONTABLO UNIVERSAL GRAPH  (3D)
# ===========================================================================
ax_mid.set_facecolor(C_BG)
np.random.seed(42)

node_3d = {
    "cash":  np.array([1.0, 1.0, 1.0]),
    "recv":  np.array([3.0, 2.5, 1.5]),
    "inv":   np.array([1.5, 4.0, 0.8]),
    "ppe":   np.array([4.0, 3.5, 3.0]),
}
node_labels_3d = {
    "cash": "cash\n(UUID-a)",
    "recv": "recv\n(UUID-b)",
    "inv":  "inv\n(UUID-c)",
    "ppe":  "ppe\n(UUID-d)",
}

xs = [p[0] for p in node_3d.values()]
ys = [p[1] for p in node_3d.values()]
zs = [p[2] for p in node_3d.values()]

ax_mid.scatter(xs, ys, zs, s=420, c=C_BLUE_FILL,
               edgecolors=C_BLUE_EDGE_N, linewidths=2.0, zorder=6, depthshade=True)

for key, pos in node_3d.items():
    ax_mid.text(pos[0], pos[1], pos[2] + 0.30,
                node_labels_3d[key], ha="center", va="bottom",
                fontsize=7.5, fontweight="bold", color=C_BLUE_TEXT,
                zorder=7, multialignment="center")

def edge3d(ax, p0, p1, color, lw, ls):
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]],
            color=color, linewidth=lw, linestyle=ls, zorder=4, alpha=0.85)
    dx, dy, dz = p1-p0
    length = np.sqrt(dx**2+dy**2+dz**2)
    if length > 0:
        frac = 0.12/length
        ax.quiver(p1[0]-dx*frac, p1[1]-dy*frac, p1[2]-dz*frac,
                  dx*frac, dy*frac, dz*frac,
                  color=color, linewidth=lw, arrow_length_ratio=1.0, alpha=0.9, zorder=5)

n = node_3d
edge3d(ax_mid, n["cash"], n["recv"], C_IFRS_DIM, 2.2, "-")
edge3d(ax_mid, n["recv"], n["ppe"],  C_IFRS_DIM, 2.2, "-")
edge3d(ax_mid, n["cash"], n["inv"],  C_TAX_DIM,  2.2, "--")
edge3d(ax_mid, n["inv"],  n["ppe"],  C_TAX_DIM,  2.2, "--")
edge3d(ax_mid, n["cash"], n["ppe"],  C_FUNC_DIM, 2.0, ":")
edge3d(ax_mid, n["recv"], n["inv"],  C_FUNC_DIM, 2.0, ":")

ax_mid.set_xlim(0, 5.5)
ax_mid.set_ylim(0, 5.5)
ax_mid.set_zlim(0, 4.5)
ax_mid.set_xlabel("IFRS dim",  labelpad=4, fontsize=8, color=C_IFRS_DIM)
ax_mid.set_ylabel("Tax dim",   labelpad=4, fontsize=8, color=C_TAX_DIM)
ax_mid.set_zlabel("Func dim",  labelpad=4, fontsize=8, color=C_FUNC_DIM)
ax_mid.tick_params(labelsize=0, length=0)
ax_mid.xaxis.pane.fill = False
ax_mid.yaxis.pane.fill = False
ax_mid.zaxis.pane.fill = False
ax_mid.xaxis.pane.set_edgecolor("#DDDDDD")
ax_mid.yaxis.pane.set_edgecolor("#DDDDDD")
ax_mid.zaxis.pane.set_edgecolor("#DDDDDD")
ax_mid.grid(True, color="#EEEEEE", linewidth=0.5)
ax_mid.view_init(elev=22, azim=-55)

ax_mid.set_title(
    "Kontablo Universal Graph\nUUID-keyed nodes  ·  context-free multi-dimensional edges",
    fontsize=10, fontweight="bold", color=C_BLUE_TEXT, pad=8, loc="center",
)

legend_elements = [
    mpatches.Patch(facecolor=C_IFRS_DIM, label="IFRS / Balance Sheet dim."),
    mpatches.Patch(facecolor=C_TAX_DIM,  label="Tax / Regulatory dim."),
    mpatches.Patch(facecolor=C_FUNC_DIM, label="Functional / Cost-Centre dim."),
]
ax_mid.legend(handles=legend_elements, loc="upper left",
              fontsize=7.5, framealpha=0.85, edgecolor="#CCCCCC",
              handlelength=1.4, handleheight=1.0)

# ===========================================================================
# ARROW 2
# ===========================================================================
ax_arr2.set_xlim(0, 10)
ax_arr2.set_ylim(0, 1)
ax_arr2.annotate("", xy=(5, 0.08), xytext=(5, 0.92),
    arrowprops=dict(arrowstyle="-|>", color=C_ARROW, lw=3.0, mutation_scale=20))
ax_arr2.text(5.4, 0.62, "Graph-to-Tree", ha="left", va="center",
             fontsize=9, fontweight="bold", color="#666666")
ax_arr2.text(5.4, 0.28, "(linearize)", ha="left", va="center",
             fontsize=8, color="#999999", style="italic")

# ===========================================================================
# PANEL 3: IFRS OUTPUT TREE
# ===========================================================================
ax_bot.set_facecolor(C_BG)
ax_bot.set_xlim(0, 10)
ax_bot.set_ylim(-3.8, 1.0)
ax_bot.axis("off")

ax_bot.text(5, 0.75, "IFRS Balance Sheet Output",
            ha="center", va="center", fontsize=11, fontweight="bold",
            color=C_GREEN_LABEL)
ax_bot.text(5, 0.30, "linearized for reporting  ·  one dimension selected as primary axis",
            ha="center", va="center", fontsize=7.5, color="#999999", style="italic")

positions_bot = {
    "root": (5.0, -0.4),
    "cur":  (2.8, -1.65),
    "ncur": (7.2, -1.65),
    "cash": (1.3, -3.1),
    "recv": (3.2, -3.1),
    "inv":  (5.5, -3.1),
    "ppe":  (8.0, -3.1),
}
labels_bot = {
    "root": ("Balance Sheet", "(IFRS)"),
    "cur":  ("Current", "Assets"),
    "ncur": ("Non-current", "Assets"),
    "cash": ("Cash &", "Equivalents"),
    "recv": ("Trade", "Receivables"),
    "inv":  ("Inventories", ""),
    "ppe":  ("PP&E", ""),
}

for key, (cx, cy) in positions_bot.items():
    rounded_box(ax_bot, cx, cy, BW, BH,
                fc=C_GREEN_FILL if key == "root" else "#E8F8EC",
                ec=C_GREEN_EDGE, lw=1.6 if key == "root" else 1.2)
    l1, l2 = labels_bot[key]
    node_text(ax_bot, cx, cy, l1, l2, color=C_GREEN_LABEL, fs=8)

for src, dst in [("root","cur"),("root","ncur"),("cur","cash"),("cur","recv"),("cur","inv"),("ncur","ppe")]:
    x0, y0 = positions_bot[src]
    x1, y1 = positions_bot[dst]
    tree_edge(ax_bot, x0, y0 - BH/2, x1, y1 + BH/2, C_GREEN_EDGE)

# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------
fig.subplots_adjust(left=0.06, right=0.96, top=0.98, bottom=0.02)

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    plt.savefig(PDF_OUT, format="pdf", bbox_inches="tight", dpi=300)
    plt.savefig(PNG_OUT, format="png", bbox_inches="tight", dpi=200)

print(f"Saved PDF : {PDF_OUT}")
print(f"Saved PNG : {PNG_OUT}")
