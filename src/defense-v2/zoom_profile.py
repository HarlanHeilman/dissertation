"""Slide 19 figure. Tilt gamma(z) within 6 nm of the oxide from the Table 4.1 gradient model (eq. S16), against the
ML-DFT three-slab interface (Table 7.2), with the length scales that define the diffraction limit marked."""
import numpy as np, matplotlib as mpl, matplotlib.pyplot as plt
from scipy.special import erf
mpl.rcParams.update({"font.family": "Caladea", "font.size": 15, "mathtext.fontset": "stix", "axes.linewidth": 1.1,
                     "xtick.direction": "in", "ytick.direction": "in", "xtick.top": True, "ytick.right": True})
L = 192.7
# gradient, Table 4.1 (h = height above the oxide, Angstrom)
gb, gs, gv, tsi, tv = 69.6, 38.0, 58.7, 14.9, 13.0
h = np.linspace(0, 60, 1200)
z = L - h
gam = gb + (gs - gb) * np.exp(-h / tsi) + (gv - gb) * np.exp(-z / tv)
# ML-DFT slab interface, Table 7.2: interface t = 10.705, roughness to bulk 7.892 (erf step)
ti, sig, gi, gbs = 10.705, 7.892, 47.24, 69.54
w = 0.5 * (1 + erf((h - ti) / (np.sqrt(2) * sig)))
slab = gi + (gbs - gi) * w
ML = 192.74 / 15
fig, ax = plt.subplots(figsize=(6.4, 4.6), dpi=300)
fig.patch.set_alpha(0)
ax.set_facecolor("white")
for k in range(5):
    ax.axvspan(k * ML / 10, (k + 1) * ML / 10, color="#EDE9E7" if k % 2 == 0 else "white", zorder=0, lw=0)
ax.plot(h / 10, slab, "--", color="k", lw=1.8, label="ML-DFT slab (interface 10.7 Å, $\\sigma$ 7.9 Å)", zorder=3)
ax.plot(h / 10, gam, color="#D62728", lw=2.6, label="ML-DFT gradient", zorder=4)
ax.axvline(23.3 / 10, color="#5E6A71", lw=1.4, ls=(0, (5, 3)), zorder=2)
ax.text(23.3 / 10 + 0.06, 40.5, r"$2\pi/q_{\max}$" + "\n23 Å", color="#5E6A71", fontsize=13, va="bottom")
ax.axvline(43.7 / 10, color="#5E6A71", lw=1.4, ls=(0, (1.5, 2.5)), zorder=2)
ax.text(43.7 / 10 + 0.06, 40.5, r"$\lambda$ (283.7 eV)" + "\n44 Å", color="#5E6A71", fontsize=13, va="bottom")
ax.text(ML / 20, 31.3, "1st ML", ha="center", fontsize=12, color="#CA1237")
ax.text(1.5 * ML / 10, 31.3, "2nd ML", ha="center", fontsize=12, color="#5E6A71")
ax.set_xlim(0, 6.0); ax.set_ylim(30, 82)
ax.set_xlabel("Height above the oxide (nm)"); ax.set_ylabel(r"Tilt $\gamma$ (°)")
ax.legend(loc="upper left", bbox_to_anchor=(0.0, 1.0), frameon=False, fontsize=12.5)
fig.tight_layout()
fig.savefig("zoom_profile.png", transparent=False, facecolor="white")
print("gradient gamma at h=0, 1ML, 2ML:", np.interp([0, ML, 2 * ML], h, gam))
