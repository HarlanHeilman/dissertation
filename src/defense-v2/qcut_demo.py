"""Slide 17 bottom-right figure. 283.7 eV s and p reflectivity fit with all energies truncated at three q lengths
(nested sampling, refl-analysis bookended_q_truncation_diffraction_de_open, si3 checkpoints), and the interface tilt and
decay length recovered at each, against the diffraction length 2 pi / q_cut."""
import numpy as np, matplotlib as mpl, matplotlib.pyplot as plt
mpl.rcParams.update({"font.family": "Caladea", "font.size": 13, "mathtext.fontset": "stix", "axes.linewidth": 1.0,
                     "xtick.direction": "in", "ytick.direction": "in"})
D = "/home/claude/deopen/"
r = np.load(D + "reflectivity_q_cuts_dynesty_curves.npz", allow_pickle=True)
CUT = [("q_hi", "#23476B"), ("mid", "#2A9D8F"), ("q_lo", "#CA1237")]
# corner-plot summaries, median [68% interval]
PAR = {"q_hi": dict(a=(41.4, 32.6, 47.6), t=(22.7, 17.3, 30.7)),
       "mid": dict(a=(45.5, 35.7, 52.6), t=(26.4, 18.6, 38.2)),
       "q_lo": dict(a=(51.1, 41.4, 57.3), t=(30.8, 20.6, 44.9))}
fig = plt.figure(figsize=(7.6, 2.75), dpi=300)
gs = fig.add_gridspec(1, 3, width_ratios=[2.1, 1, 1], wspace=0.42)
ax = fig.add_subplot(gs[0])
q = r["q_0"]; lr = r["logR_0"]; pol = r["pol_0"]
for p, off, mk in (("s", 0.0, "o"), ("p", -2.0, "^")):
    m = pol == p
    ax.plot(q[m], lr[m] + off, mk, ms=2.2, color="0.55", mfc="none", mew=0.6, zorder=2)
for i, (name, col) in enumerate(CUT):
    qc = r["q_cuts"][i]; qi = r[f"q_{i}"]; fi = r[f"logR_fit_{i}"]; pi_ = r[f"pol_{i}"]
    for p, off in (("s", 0.0), ("p", -2.0)):
        m = (pi_ == p) & (qi <= qc)
        o = np.argsort(qi[m])
        ax.plot(qi[m][o], fi[m][o] + off, color=col, lw=1.4, zorder=3 + i)
    ax.axvline(qc, color=col, lw=1.0, ls=(0, (4, 2)))
ax.set_xlim(0, 0.275); ax.set_xlabel(r"$q$ (Å$^{-1}$)"); ax.set_ylabel(r"log$_{10}R$, 283.7 eV")
ax.set_xticks([0, 0.075, 0.172, 0.27]); ax.set_xticklabels(["0", "0.075", "0.17", "0.27"])
dl = {"q_hi": 23.3, "mid": 36.5, "q_lo": 84.3}
for j, (key, lab, lim) in enumerate((("a", r"Interface tilt $\gamma_{Si}$ (°)", (25, 75)), ("t", r"$\tau_{Si}$ (dots), $2\pi/q$ (bars) (Å)", (0, 95)))):
    b = fig.add_subplot(gs[1 + j])
    for i, (name, col) in enumerate(CUT):
        m, lo, hi = PAR[name][key]
        b.errorbar(i, m, yerr=[[m - lo], [hi - m]], fmt="o", color=col, ms=5, capsize=3, lw=1.6)
        if key == "t":
            b.plot(i, dl[name], "_", color=col, ms=16, mew=2.2)
    if key == "a":
        b.axhline(69.6, color="0.45", lw=1.0, ls=(0, (4, 2))); b.text(2.35, 71.0, "bulk", ha="right", fontsize=10, color="0.4")
    else:
        pass
    b.set_xlim(-0.5, 2.5); b.set_ylim(*lim); b.set_xticks([0, 1, 2]); b.set_xticklabels(["0.27", "0.17", "0.075"], fontsize=10)
    b.set_xlabel(r"$q_{\rm cut}$ (Å$^{-1}$)"); b.set_ylabel(lab)
fig.subplots_adjust(left=0.08, right=0.99, top=0.97, bottom=0.18)
fig.savefig("qcut_demo.png", facecolor="white")
