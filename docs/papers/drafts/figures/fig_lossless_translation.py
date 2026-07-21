#!/usr/bin/env python3
"""Generate fig_lossless_translation.png — before/after of ADR-016.

Reproducible figure source (claims-evidence rule): traces the SAME example
node (asset.current.cash, jurisdiction de) through the ontology before and
after the lossless-translation redesign (ADR-016). The "after" panel's
labels are taken directly from the shipped code: core/schemas/level3_accounts.yaml
(groupings: ifrs/cash_flow), localizations/de/skr04_mapping.yaml (local_parent,
facets), and core/harness/resolution.py's rule_id format (tier1:<jur>:<code>).

Usage:
  python docs/papers/drafts/figures/fig_lossless_translation.py

Output: docs/papers/drafts/figures/fig_lossless_translation.png (300 dpi)
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig_lossless_translation.png")

C_GRAY = "#e8e8ec"
C_GRAY_EDGE = "#7a7a7a"
C_LOSS = "#f7dcd7"
C_LOSS_EDGE = "#c0392b"
C_NEW = "#ded4f5"
C_NEW_EDGE = "#6c3fa6"

FS_TITLE = 15
FS_PANEL = 12.5
FS_BOX = 10.5
FS_SUB = 9


def draw_box(ax, x, y, w, h, title, subtitle=None, fc=C_GRAY, ec=C_GRAY_EDGE):
    box = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.1, facecolor=fc, edgecolor=ec,
    )
    ax.add_patch(box)
    if subtitle:
        ax.text(x, y + h * 0.16, title, ha="center", va="center",
                 fontsize=FS_BOX, fontweight="bold", color="#222")
        ax.text(x, y - h * 0.22, subtitle, ha="center", va="center",
                 fontsize=FS_SUB, color="#444")
    else:
        ax.text(x, y, title, ha="center", va="center",
                 fontsize=FS_BOX, fontweight="bold", color="#222")


def draw_arrow(ax, p, q, color="#555"):
    ax.add_patch(FancyArrowPatch(
        p, q, arrowstyle="-|>", mutation_scale=12,
        linewidth=1.1, color=color, shrinkA=2, shrinkB=2,
    ))


fig, (axL, axR) = plt.subplots(1, 2, figsize=(12, 5.0))
for ax in (axL, axR):
    ax.set_xlim(0, 10)
    ax.set_ylim(2.9, 11.4)
    ax.axis("off")

# ---------------------------------------------------------------- Before
axL.text(5, 11.0, "Before", ha="center", fontsize=FS_TITLE, fontweight="bold")
axL.text(5, 10.4, "single-parent tree, opaque local codes", ha="center",
         fontsize=FS_PANEL, style="italic", color="#666")

draw_box(axL, 5, 9.0, 2.4, 0.8, "asset")
draw_arrow(axL, (5, 8.6), (5, 7.9))
draw_box(axL, 5, 7.5, 2.6, 0.8, "asset.current")
draw_arrow(axL, (5, 7.1), (5, 6.4))
draw_box(axL, 5, 6.0, 3.0, 0.8, "asset.current.cash")
draw_arrow(axL, (5, 5.6), (5, 4.6), color=C_LOSS_EDGE)
draw_box(axL, 5, 3.9, 4.6, 1.1, "local_codes (flat)",
         "one opaque code per jurisdiction", fc=C_LOSS, ec=C_LOSS_EDGE)

# ---------------------------------------------------------------- After
axR.text(5, 11.0, "After (ADR-016)", ha="center", fontsize=FS_TITLE, fontweight="bold")
axR.text(5, 10.4, "multi-lens graph, auditable fiber + provenance", ha="center",
         fontsize=FS_PANEL, style="italic", color="#666")

draw_box(axR, 5, 9.4, 3.0, 0.8, "asset.current.cash")
draw_arrow(axR, (4.3, 9.0), (2.6, 8.1))
draw_arrow(axR, (5.7, 9.0), (7.4, 8.1))
draw_arrow(axR, (5, 9.0), (5, 6.8))

draw_box(axR, 2.6, 7.6, 2.9, 1.0, "asset.current", "ifrs lens")
draw_box(axR, 7.4, 7.6, 2.9, 1.0, "operating", "cash_flow lens")

draw_arrow(axR, (5, 6.0), (5, 5.0), color=C_NEW_EDGE)
draw_box(axR, 5, 6.3, 5.6, 1.1, "fiber · de 1600",
         "Kasse · local_parent 1 · vat 19%", fc=C_NEW, ec=C_NEW_EDGE)
draw_box(axR, 5, 4.4, 5.6, 1.1, "MappingQuote",
         "tier1_exact · tier1:de:1600", fc=C_NEW, ec=C_NEW_EDGE)

fig.suptitle(
    "Kontablo lossless translation: the same node (asset.current.cash) before and after",
    fontsize=13, y=0.995,
)
fig.tight_layout(rect=[0, 0.02, 1, 0.96])
fig.savefig(OUT, dpi=300, facecolor="white")
print(f"Wrote {OUT}")
