"""Slide 14 top-right panel. Ginzburg-Landau setup for the gradient model (dissertation Ch. 3, pp. 33 and 34):
order parameters dgamma and drho, quadratic bulk well, gradient stiffness, pinned interface, exponential relaxation
over one shared coherence length; any property set by (gamma, rho) follows the same profile to linear order."""
import numpy as np, matplotlib as mpl, matplotlib.pyplot as plt
mpl.rcParams.update({"font.family": "STIXGeneral", "mathtext.fontset": "stix", "font.size": 9,
                     "axes.linewidth": 0.8, "axes.edgecolor": "#2E3538"})
CR, INK, SL, GR = "#CA1237", "#1F1F1F", "#5E6A71", "#9FA4A5"
fig = plt.figure(figsize=(3.10, 1.48), dpi=400)

# free energy functional
fig.text(0.5, 0.965, r"$F=\int_0^L\left[\,f+\frac{1}{2}c_\rho(\partial_z\Delta\rho)^2+\frac{1}{2}c_\gamma(\partial_z\Delta\gamma)^2\right]dz+F_v+F_{Si}$",
         ha="center", va="top", fontsize=9.5, color=INK)

# bulk well, pinned state relaxing to the minimum
a0 = fig.add_axes([0.04, 0.27, 0.38, 0.48])
d = np.linspace(-1.3, 0.75, 300)
a0.plot(d, 0.5 * d ** 2, color=INK, lw=1.1)
ds = -1.0
a0.annotate("", xy=(-0.16, 0.06), xytext=(ds + 0.13, 0.5 * ds ** 2 - 0.04),
            arrowprops=dict(arrowstyle="-|>", color=SL, lw=0.8, mutation_scale=7, connectionstyle="arc3,rad=0.3"))
a0.plot(ds, 0.5 * ds ** 2 + 0.035, "o", ms=5.5, color=CR, zorder=5)
a0.plot(0, 0.035, "o", ms=5.5, color=GR, zorder=5)
a0.text(ds - 0.12, 0.5 * ds ** 2 + 0.05, r"$\Delta_{Si}$", color=CR, ha="right", va="center", fontsize=9)
a0.text(0.0, 0.16, "bulk", color=SL, ha="center", va="bottom", fontsize=8.5)
a0.text(0.75, 0.95, r"$f=\frac{a}{2}\Delta^2$", ha="right", va="top", fontsize=9, color=INK)
a0.set_xlim(-1.55, 0.8); a0.set_ylim(-0.03, 0.95)
a0.set_xticks([]); a0.set_yticks([])
for s in ("top", "right", "left"):
    a0.spines[s].set_visible(False)
a0.set_xlabel(r"$\Delta\gamma,\ \Delta\rho$", fontsize=9, labelpad=1.5)

# relaxation with height, one coherence length
a1 = fig.add_axes([0.58, 0.27, 0.39, 0.48])
h = np.linspace(0, 5, 300)
a1.plot(h, np.exp(-h), color=CR, lw=1.5)
a1.plot([1, 1], [0, np.exp(-1)], color=SL, lw=0.7, ls=(0, (2, 2)))
a1.text(4.95, 0.95, r"$\Delta(h)=\Delta_{Si}\,e^{-h/\tau}$", ha="right", va="top", fontsize=9, color=INK)
a1.text(4.95, 0.62, r"$\tau=\sqrt{c/a}$", ha="right", va="top", fontsize=9, color=SL)
a1.set_xlim(0, 5); a1.set_ylim(0, 1.05)
a1.set_xticks([1]); a1.set_xticklabels([r"$\tau$"])
a1.set_yticks([1]); a1.set_yticklabels([r"$\Delta_{Si}$"])
a1.tick_params(direction="in", length=2.2, pad=1.5, labelsize=8.5)
for s in ("top", "right"):
    a1.spines[s].set_visible(False)
a1.set_xlabel(r"$h$ above SiO$_2$", fontsize=8.5, labelpad=0.5)

# anything set by the molecular state rides the same gradient
fig.text(0.5, 0.01, r"any property $X(\gamma,\rho)$,  $X(h)=X_b+\Delta X_{Si}\,e^{-h/\tau}$",
         ha="center", va="bottom", fontsize=8.5, color=SL)
fig.savefig("gl_panel.png", facecolor="white")
