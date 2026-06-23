#!/usr/bin/env python3
"""Generate fig_world_coverage.png — world map of Kontablo jurisdiction coverage.

Reproducible figure source (claims-evidence rule): colors are derived directly
from core/schemas/jurisdiction_coverage.yaml (the same manifest that backs the
195/60 claims), never hand-assigned.

Basemap: Natural Earth 110m Admin 0 - Countries (public domain).
  https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip
Pass the directory containing the unzipped shapefile as argv[1]
(default: /tmp/ne110).

Usage:
  python docs/papers/drafts/figures/fig_world_coverage.py [shapefile_dir]

Output: docs/papers/drafts/figures/fig_world_coverage.png (300 dpi)
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Patch
from matplotlib.collections import PatchCollection
import shapefile  # pyshp
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
COVERAGE = os.path.join(ROOT, "core", "schemas", "jurisdiction_coverage.yaml")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig_world_coverage.png")
SHP_DIR = sys.argv[1] if len(sys.argv) > 1 else "/tmp/ne110"

# Design system (matches the TikZ palette of the paper):
#   statutory overlay = blue, IFRS-direct = green, non-sovereign extra = grey-blue
C_STATUTORY = "#aecbe8"   # ~ blue!15-ish, slightly stronger for print
C_IFRS = "#cdeacd"        # ~ green!15
C_EXTRA = "#d9d9e3"       # non-sovereign extras (TW/HK/MO) — mapped, not in the 195
C_UNMATCHED = "#f5f5f5"   # basemap polygons not matched to a manifest entry
EDGE = "#7a7a7a"

doc = yaml.safe_load(open(COVERAGE, encoding="utf-8"))
rows = doc["jurisdictions"]
mode_by_iso2 = {r["iso"].upper(): r["mapping_mode"] for r in rows}
n_stat = sum(1 for r in rows if r["mapping_mode"] == "statutory_chart")
n_ifrs = sum(1 for r in rows if r["mapping_mode"] == "ifrs_direct")
assert len(rows) == 195, f"manifest count drifted: {len(rows)}"

# Non-sovereign extras mapped in localizations/ but outside the 195 manifest.
EXTRAS = {"TW", "HK", "MO"}

sf = shapefile.Reader(os.path.join(SHP_DIR, "ne_110m_admin_0_countries"))
fields = [f[0] for f in sf.fields[1:]]
i_iso2 = fields.index("ISO_A2_EH") if "ISO_A2_EH" in fields else fields.index("ISO_A2")

fig, ax = plt.subplots(figsize=(11, 5.6), dpi=300)
patches_by_color = {}

matched = set()
for shaperec in sf.iterShapeRecords():
    iso2 = str(shaperec.record[i_iso2]).upper()
    if iso2 in mode_by_iso2:
        color = C_STATUTORY if mode_by_iso2[iso2] == "statutory_chart" else C_IFRS
        matched.add(iso2)
    elif iso2 in EXTRAS:
        color = C_EXTRA
    else:
        color = C_UNMATCHED
    shape = shaperec.shape
    pts = shape.points
    parts = list(shape.parts) + [len(pts)]
    for j in range(len(parts) - 1):
        seg = pts[parts[j]:parts[j + 1]]
        if len(seg) > 2:
            patches_by_color.setdefault(color, []).append(Polygon(seg))

for color, patches in patches_by_color.items():
    ax.add_collection(PatchCollection(
        patches, facecolor=color, edgecolor=EDGE, linewidth=0.25))

ax.set_xlim(-180, 180)
ax.set_ylim(-60, 85)
ax.set_aspect("equal")
ax.axis("off")

legend = [
    Patch(facecolor=C_STATUTORY, edgecolor=EDGE,
          label=f"Statutory-chart overlay + IFRS anchor ({n_stat})"),
    Patch(facecolor=C_IFRS, edgecolor=EDGE,
          label=f"IFRS-direct (no mandated national chart) ({n_ifrs})"),
    Patch(facecolor=C_EXTRA, edgecolor=EDGE,
          label="Non-sovereign extras mapped (TW, HK, MO)"),
]
ax.legend(handles=legend, loc="lower left", fontsize=7.5, frameon=False)

plt.tight_layout(pad=0.2)
plt.savefig(OUT, bbox_inches="tight")
print(f"matched {len(matched)} manifest jurisdictions to basemap polygons "
      f"(microstates lack polygons at 110m scale; they are still in the manifest)")
print(f"wrote {OUT}")
