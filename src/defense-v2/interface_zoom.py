"""Slide 15 top-right figure. Bottom 5 nm of the regenerated Fig. 4.4c growth strip (islands recoloured) beside the tilt profile, sharing one height axis.
Gradient gamma(h) from Table 4.1 (eq. S16); slab interface from Table 7.2 (erf step). Height calibrated from the Fig. 4.4b ticks
(127 px per nm, 0 nm at y = 252.5 px, substrate top at L = 192.7 A)."""
import numpy as np, matplotlib as mpl, matplotlib.pyplot as plt
from PIL import Image
from scipy.special import erf
mpl.rcParams.update({"font.family": "Caladea", "font.size": 13, "mathtext.fontset": "stix", "axes.linewidth": 1.0,
                     "xtick.direction": "in", "ytick.direction": "in"})
PX_NM, Y0, L = 127.0, 252.5, 19.27
ysub = Y0 + L * PX_NM
HTOP, HBOT = 5.0, -0.6
img = Image.open("substrate_strip.png")   # render_substrate_zoom.py, heights 5.0 to -0.6 nm
ML = 1.2849
h = np.linspace(0, HTOP, 800)
gb, gs, gv, tsi, tv = 69.6, 38.0, 58.7, 1.49, 1.30
gam = gb + (gs - gb) * np.exp(-h / tsi) + (gv - gb) * np.exp(-(L - h) / tv)
w = 0.5 * (1 + erf((h - 1.0705) / (np.sqrt(2) * 0.7892)))
slab = 47.24 + (69.54 - 47.24) * w
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.6, 2.75), dpi=300, gridspec_kw={"width_ratios": [1.15, 1], "wspace": 0.04})
a0.imshow(img, extent=[0, 1, HBOT, HTOP], aspect="auto", interpolation="lanczos")
a0.set_xticks([]); a0.set_ylabel("Height above oxide (nm)")
for ax in (a0, a1):
    ax.set_ylim(HBOT, HTOP)
    for k in (1, 2, 3):
        ax.axhline(k * ML, color="#5E6A71", lw=0.8, ls=(0, (2, 2)), zorder=5)
    ax.axhline(2.33, color="#CA1237", lw=1.4, ls=(0, (6, 3)), zorder=6)
a1.axhspan(HBOT, 0, color="#9FA4A5", alpha=0.5, lw=0)
a1.plot(slab, h, "--", color="k", lw=1.6, label="slab")
a1.plot(gam, h, color="#D62728", lw=2.4, label="gradient")
a1.set_xlim(30, 75); a1.set_xlabel(r"Tilt $\gamma$ (°)"); a1.set_yticklabels([])
a1.text(31.2, 2.33 + 0.22, r"$2\pi/q_{\max}$ = 23 Å", color="#CA1237", fontsize=11, va="bottom")
for k in (1, 2):
    a1.text(74.3, k * ML + 0.08, f"{k} ML", color="#5E6A71", fontsize=10, ha="right")
a1.legend(loc="upper left", frameon=False, fontsize=11, bbox_to_anchor=(0.0, 0.93))
fig.subplots_adjust(left=0.08, right=0.99, top=0.98, bottom=0.17)
fig.savefig("interface_zoom.png", facecolor="white")
