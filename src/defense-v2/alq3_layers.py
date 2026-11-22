"""Slide 25 layers for the PowerPoint build. Same analysis as alq3_design.py (fitted Alq3 bulk, Fig. 5.5 prior,
measured energies pinned at sigma = 1e-5, linearized posterior). Every layer is a transparent PNG on identical axes so the
layers stack exactly; all words on the slide are PowerPoint text boxes.

Survival counts. A pool of 200,000 spectra is drawn from the posterior given the ten measured energies. A new measurement
keeps a spectrum if it agrees within 2 sigma at every new point: sigma = 1e-5 for one extra energy at the GP pick, and
sigma_scan = sigma sqrt(71/10) for a 71-point scan from 283 to 290 eV with the same total beam time."""
import json
import numpy as np, matplotlib as mpl, matplotlib.pyplot as plt

src = open("/home/claude/assets/alq3_design.py").read()
head = src[: src.index("# ---------------------------------------------------------------- figure")].replace("for _ in range(3):", "for _ in range(1):")
g = {}
exec(head, g)
E, EW, m, NL, C0, G, oc, jac, MEAS, RHO_B, NOISE, BOOK, CONT, E0, W, DN = (g[k] for k in (
    "E", "EW", "m", "NL", "C0", "G", "oc", "jac", "MEAS", "RHO_B", "NOISE", "BOOK", "CONT", "E0", "W", "DN"))
gp, r0, r1, r_scan, sig_scan = g["picks"][0], g["r0"], g["red"][1], g["r_scan"], g["sig_scan"]
from scipy.special import dawsn

N, K, NSHOW = 200_000, 2.0, 150
rng = np.random.default_rng(11)
Z = rng.standard_normal((N, NL)) @ np.linalg.cholesky(C0).T
keep_gp = (np.abs(Z @ jac(np.array([gp])).T) < K * NOISE).all(1)
scan = np.arange(283.0, 290.0001, 0.1)
keep_scan = (np.abs(Z @ jac(scan).T) < K * sig_scan).all(1)
best = oc(np.zeros(NL), EW)[0]
show = Z[:NSHOW]
surv = Z[keep_gp][:NSHOW]
curves0 = best + show @ G.T
curves1 = best + surv @ G.T
S = 1e3 / RHO_B
numbers = dict(pool=N, tol_sigma=K, gp_ev=float(gp), gp_survive=int(keep_gp.sum()), scan_survive=int(keep_scan.sum()),
               r0=float(r0), r1=float(r1), r_scan=float(r_scan), gain_gp=float((1 - r0) / (1 - r1)),
               gain_scan=float((1 - r0) / (1 - r_scan)), sigma=float(NOISE), sigma_scan=float(sig_scan))
print(json.dumps(numbers, indent=1))

mpl.rcParams.update({"font.family": "Caladea", "font.size": 12.5, "axes.linewidth": 1.0, "mathtext.fontset": "stix",
                     "xtick.direction": "in", "ytick.direction": "in"})
RED, BLUE, GREY, TOSS = "#CA1237", "#23476B", "#8A8F94", "#E7A9B1"
FIG = (12.0, 4.6)
L0, Wl, L1, Wr, B0, Hh, gap = 0.065, 0.235, 0.385, 0.6, 0.12, 0.38, 0.03
AX = {"Ab": [L0, B0 + Hh + gap, Wl, Hh], "Ad": [L0, B0, Wl, Hh], "Bb": [L1, B0 + Hh + gap, Wr, Hh], "Bd": [L1, B0, Wr, Hh]}
YL = {"Bb": (0, 2.45), "Bd": (-0.85, 1.85)}


def frame(layer):
    fig = plt.figure(figsize=FIG, dpi=300)
    ax = {k: fig.add_axes(v) for k, v in AX.items()}
    for k in ("Bb", "Bd"):
        ax[k].set_xlim(283, 290); ax[k].set_ylim(*YL[k])
    ax["Ab"].set_xlim(283, 290); ax["Ad"].set_xlim(283, 290)
    if layer != "base":
        for a in ax.values():
            a.axis("off")
    return fig, ax


def save(fig, name):
    fig.savefig(f"/home/claude/assets/l25_{name}.png", dpi=300, transparent=True)
    plt.close(fig)


# base: every axis, the fitted surface, bulk and substrate per unit density
fig, ax = frame("base")
cm = plt.get_cmap("RdBu")
BCOL = {"surface": cm(0.08), "bulk": "k", "substrate": cm(0.83)}
u = (E[:, None] - E0[None]) / W[None]
for k, (h, rho) in BOOK.items():
    b = rho * CONT[:, 1] + (h[None] * np.exp(-u**2)).sum(1)
    d = rho * CONT[:, 0] + DN * (h[None] * dawsn(u)).sum(1)
    lw = 2.2 if k == "bulk" else 1.5
    ax["Ab"].plot(E, b / rho * 1e3, color=BCOL[k], lw=lw); ax["Ad"].plot(E, d / rho * 1e3, color=BCOL[k], lw=lw)
ax["Ab"].set_ylabel(r"$\beta/\rho$"); ax["Ad"].set_ylabel(r"$\delta/\rho$")
ax["Bb"].set_ylabel(r"bulk $\beta/\rho$"); ax["Bd"].set_ylabel(r"bulk $\delta/\rho$")
ax["Ad"].set_xlabel("Photon energy (eV)"); ax["Bd"].set_xlabel("Photon energy (eV)")
for k in ("Ab", "Bb"):
    plt.setp(ax[k].get_xticklabels(), visible=False)
for a in ax.values():
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
save(fig, "base")


def curves_layer(name, curves, color, lw, alpha):
    fig, ax = frame(name)
    for k, sl in (("Bb", slice(0, m)), ("Bd", slice(m, 2 * m))):
        for c in curves[:, sl]:
            ax[k].plot(EW, c * S, color=color, lw=lw, alpha=alpha)
    return fig, ax


fig, _ = curves_layer("grey", curves0, GREY, 0.6, 0.45); save(fig, "grey")
fig, _ = curves_layer("tossed", curves0, TOSS, 0.6, 0.55); save(fig, "tossed")
fig, ax = curves_layer("gp", curves1[:90], BLUE, 0.6, 0.35)
for k, sl in (("Bb", slice(0, m)), ("Bd", slice(m, 2 * m))):
    ax[k].axvline(gp, color=BLUE, lw=1.5, ls=(0, (5, 3)))
    ax[k].plot([gp], [np.interp(gp, EW, best[sl]) * S], "o", ms=7.5, mfc="white", mec=BLUE, mew=2.0, zorder=6)
save(fig, "gp")
fig, ax = frame("band")
for k, sl in (("Bb", slice(0, m)), ("Bd", slice(m, 2 * m))):
    y = best[sl] * S; w = K * sig_scan * S
    ax[k].fill_between(EW, y - w, y + w, color="#424C4E", alpha=0.5, lw=0)
    ax[k].plot(EW, y - w, color="#424C4E", lw=0.9); ax[k].plot(EW, y + w, color="#424C4E", lw=0.9)
save(fig, "band")
fig, ax = frame("top")
for k, sl in (("Bb", slice(0, m)), ("Bd", slice(m, 2 * m))):
    ax[k].plot(EW, best[sl] * S, color="k", lw=1.5)
    ax[k].plot(MEAS, np.interp(MEAS, EW, best[sl]) * S, "o", ms=6.5, mfc="none", mec=RED, mew=1.8)
save(fig, "top")
json.dump(dict(numbers, fig=FIG, axes=AX, ylim=YL, xlim=[283, 290]), open("/home/claude/assets/l25_layout.json", "w"), indent=1)
