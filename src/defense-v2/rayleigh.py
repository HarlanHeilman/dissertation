"""Slide 15 left figure. Rayleigh condition in one dimension: two point features imaged through a band-limited
probe, each spread as sinc^2, are just resolved when the maximum of one falls on the first minimum of the other."""
import numpy as np, matplotlib as mpl, matplotlib.pyplot as plt
mpl.rcParams.update({"font.family": "Caladea", "font.size": 13, "mathtext.fontset": "stix", "axes.linewidth": 1.0})
x = np.linspace(-2.2, 3.2, 1200)
a, b = np.sinc(x) ** 2, np.sinc(x - 1) ** 2
fig, ax = plt.subplots(figsize=(3.7, 1.75), dpi=300)
ax.fill_between(x, a + b, color="#C8C3BE", alpha=0.35, lw=0)
ax.plot(x, a, color="#CA1237", lw=1.6, ls=(0, (4, 2)))
ax.plot(x, b, color="#23476B", lw=1.6, ls=(0, (4, 2)))
ax.plot(x, a + b, color="#2E3538", lw=2.0)
ax.annotate("", xy=(1, 1.12), xytext=(0, 1.12), arrowprops=dict(arrowstyle="<->", color="#2E3538", lw=1.2))
ax.text(0.5, 1.17, r"$d_{\min}$", ha="center", va="bottom", fontsize=14)
ax.plot([1, 1], [0, 1.0], color="#5E6A71", lw=0.8, ls=":")
ax.annotate("first minimum", xy=(1.0, 0.01), xytext=(2.45, 0.42), fontsize=10, color="#5E6A71", ha="center",
            arrowprops=dict(arrowstyle="-", color="#5E6A71", lw=0.8))
ax.set_xlim(-2.2, 3.2); ax.set_ylim(0, 1.42)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.set_yticks([]); ax.set_xticks([])
ax.set_xlabel("depth", fontsize=12, color="#5E6A71")
fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.14)
fig.savefig("rayleigh.png", facecolor="white")
