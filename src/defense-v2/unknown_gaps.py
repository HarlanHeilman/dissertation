"""Slide 25. One spectrum, four measured energies, and the many spectra that pass through them.
Same synthetic polystyrene edge, prior and noise as dissertation Fig. 5.5 (lr-optical-models manuscript/fig5_sensitivity.ipynb),
'On peaks' design. Curves are draws from the linearized posterior, z ~ N(0, C), evaluated through the full model.
Only the resonant part of beta is drawn; the shared continuum is added back from a smooth step so the edge looks familiar."""
import numpy as np, matplotlib as mpl, matplotlib.pyplot as plt
from scipy.special import erf
exec(open("/home/claude/assets/uncert_spectrum.py").read().split("prior = (G**2)")[0].split('mpl.rcParams.update')[0])
mpl.rcParams.update({"font.family": "Caladea", "font.size": 15, "axes.linewidth": 1.1, "mathtext.fontset": "stix",
                     "xtick.direction": "in", "ytick.direction": "in"})
exec("\n".join(l for l in open("/home/claude/assets/uncert_spectrum.py").read().split("\n")
               if l.startswith(("ENERGY", "N_PEAKS", "LOCS0", "WIDTHS0", "AMPS0", "LOC_SCALE", "NL ="))))
from scipy.special import dawsn
src = open("/home/claude/assets/uncert_spectrum.py").read()
exec(src[src.index("def oc("):src.index("def rand_p")])
E = np.linspace(283, 290, 700)
bg = 0.35e-3 + 0.9e-3 * (1 + erf((E - 289.6) / 0.6)) / 2
probes = LOCS0[:4]
C = cov(probes, NOISE)
L = np.linalg.cholesky(C)
rng = np.random.default_rng(7)
Z = rng.standard_normal((60, NL)) @ L.T
curves = oc(Z, E)[:, :E.size] + bg
truth = oc(np.zeros(NL), E)[0, :E.size] + bg
yp = np.interp(probes, E, truth)
fig, ax = plt.subplots(figsize=(8.4, 4.4), dpi=300)
for c in curves:
    ax.plot(E, c * 1e3, color="#8A8F94", lw=0.9, alpha=0.45, zorder=2)
ax.plot(probes, yp * 1e3, "o", ms=11, color="#CA1237", mec="white", mew=1.6, zorder=5)
ax.axvspan(286.15, 290, color="#EDE9E4", zorder=0, lw=0)
ax.text(288.1, 7.3, "not measured", ha="center", va="center", fontsize=17, color="#424C4E", style="italic")
for x, y in ((287.1, 5.6), (288.8, 4.4), (286.5, 3.4)):
    ax.text(x, y, "?", ha="center", va="center", fontsize=30, color="#424C4E", fontweight="bold", zorder=6)
ax.annotate("measured", xy=(probes[1], yp[1] * 1e3), xytext=(283.25, 7.3), fontsize=17, color="#CA1237",
            ha="left", va="center", arrowprops=dict(arrowstyle="-", color="#CA1237", lw=1.2, shrinkB=8))
ax.set_xlim(283, 290); ax.set_ylim(0, 8.3); ax.set_yticks([0, 2, 4, 6, 8]); ax.tick_params(axis="x", pad=7)
ax.set_xlabel("Photon energy (eV)"); ax.set_ylabel(r"$\beta$ ($\times10^{-3}$)")
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
fig.tight_layout(pad=0.3); fig.savefig("/home/claude/assets/unknown_gaps.png", dpi=300)
print(curves.max() * 1e3, truth.max() * 1e3)
