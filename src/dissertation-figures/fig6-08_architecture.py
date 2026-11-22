"""Fig. 6.8 (formerly Fig. 5.9), architecture of X-ray Atlas and the lineage of optical models.

Final version from the 2026-11-08 session: REST API /api/v1 as the only path to the database,
web application as a client of the API, ORCID and Zenodo through the API, panel b annotation removed.
Run from any directory; writes fig6-08_architecture.{png,pdf,svg} next to this script or to FIG_OUT.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams["font.family"] = "Liberation Sans"  # Arial-metric
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["pdf.fonttype"] = 42

OUT = os.environ.get("FIG_OUT", os.path.dirname(os.path.abspath(__file__)))
NAME = "fig6-08_architecture"

W, H = 930, 572
fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(H, 0)
ax.axis("off")

RED = "#e02020"
GRAY = "#808080"


def box(x0, y0, x1, y1, text, ec="black", fc="white", fs=12.5, lw=1.8, r=7):
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0,
                                boxstyle=f"round,pad=0,rounding_size={r}",
                                ec=ec, fc=fc, lw=lw, zorder=2))
    if text:
        ax.text((x0 + x1) / 2, (y0 + y1) / 2, text, ha="center", va="center",
                fontsize=fs, zorder=3, linespacing=1.1)


def arrow(p, q):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="<|-|>", mutation_scale=11,
                                 lw=1.5, color="black", shrinkA=2, shrinkB=2,
                                 zorder=4))


# ---- panel a ----
ax.text(6, 22, "a", fontsize=15, fontweight="bold", va="center")

box(282, 12, 625, 430, None, fc="#f3f3f3", r=10)
ax.text(453.5, 45, "X-ray Atlas", ha="center", va="center", fontsize=12.5,
        fontweight="bold", zorder=3)

IX0, IX1 = 313, 594
DB = (85, 163)
API = (200, 278)
WEB = (315, 393)
box(IX0, DB[0], IX1, DB[1], "database and files")
box(IX0, API[0], IX1, API[1], "REST API /api/v1", ec=RED)
box(IX0, WEB[0], IX1, WEB[1], "web application")

xc = (IX0 + IX1) / 2
arrow((xc, DB[1]), (xc, API[0]))
arrow((xc, API[1]), (xc, WEB[0]))

LX0, LX1 = 28, 217
ORC = (150, 228)
ZEN = (262, 340)
box(LX0, ORC[0], LX1, ORC[1], "ORCID sign in")
box(LX0, ZEN[0], LX1, ZEN[1], "Zenodo DOIs")
arrow((LX1, sum(ORC) / 2), (IX0, API[0] + 24))
arrow((LX1, sum(ZEN) / 2), (IX0, API[1] - 24))

RX0, RX1 = 698, 902
PY = (105, 183)
CLI = (210, 288)
BR = WEB
box(RX0, PY[0], RX1, PY[1], "Python xrayatlas", ec=RED)
box(RX0, CLI[0], RX1, CLI[1], "CLI xatlas", ec=RED)
box(RX0, BR[0], RX1, BR[1], "browser")
arrow((RX0, sum(PY) / 2), (IX1, API[0] + 24))
arrow((RX0, sum(CLI) / 2), (IX1, API[1] - 24))
arrow((RX0, sum(BR) / 2), (IX1, sum(WEB) / 2))

# ---- panel b ----
ax.text(6, 483, "b", fontsize=15, fontweight="bold", va="center")
BY = (497, 558)
bx = [(27, 217), (252, 442), (478, 668), (703, 893)]
labels = ["dataset\nrevision", "default\nmodel", "your fork\nversion 1, 2",
          "citation"]
for (x0, x1), lab in zip(bx, labels):
    box(x0, BY[0], x1, BY[1], lab, ec=RED if "fork" in lab else "black",
        fs=10.5)
for (a0, a1), (b0, b1) in zip(bx[:-1], bx[1:]):
    ax.add_patch(FancyArrowPatch((a1, sum(BY) / 2), (b0, sum(BY) / 2),
                                 arrowstyle="-|>", mutation_scale=11, lw=1.5,
                                 color="black", shrinkA=1, shrinkB=1,
                                 zorder=4))

for ext in ("png", "pdf", "svg"):
    fig.savefig(os.path.join(OUT, f"{NAME}.{ext}"), dpi=300 if ext == "png" else None,
                facecolor="white")
print("saved", NAME)
