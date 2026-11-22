"""Slide 25. Bulk optical constants of the Alq3 graded SOS fit (dissertation Fig. 5.3 'graded', dft2+dft4+dft5+dft6+dft7),
what the ten measured XRR energies pin down, the next energy a GP design would add, and an equal-dose energy scan.

Same framework as dissertation Fig. 5.5 (lr-optical-models manuscript/fig5_sensitivity.ipynb), applied to the fitted bulk:
  bulk n(E) = rho_bulk * continuum(E) + sum_k h_k [Gaussian in beta, Dawson partner in delta], continuum fixed;
  prior on each of the 17 peaks as in Fig. 5.5 (location N(0, 0.25 eV), width and height log-normal, 0.25 and 0.35);
  each measured energy returns bulk beta and delta with Gaussian noise sigma = 1e-5, so the fit is pinned there;
  posterior by the Laplace covariance at the best fit; metric = fractional variance reduction of n over 283 to 290 eV.
Input alq3_bulk_export.npz is written by export_alq3_bulk.py from the fig3 builder."""
import numpy as np, matplotlib as mpl, matplotlib.pyplot as plt
from scipy.special import dawsn

D = np.load("/home/claude/assets/alq3_bulk_export.npz")
E, CONT, E0, W = D["e"], D["cont_tab"], D["E0"], D["W"]
MEAS = D["energies"]
# the fitted bulk bookend: bulk peak heights and bulk density of the graded SOS fit
H = D["h_bulk"]; RHO_B = float(D["dens"][1])
BOOK = {"surface": (D["h_vac"], float(D["dens"][0])), "bulk": (D["h_bulk"], float(D["dens"][1])), "substrate": (D["h_si"], float(D["dens"][2]))}
WIN = (E >= 283.0) & (E <= 290.0); EW = E[WIN]; m = EW.size
NK = E0.size; NL = 3 * NK; DN = 2 / np.sqrt(np.pi)
LOC_S, LW, LA, NOISE = 0.25, 0.25, 0.35, 1e-5  # measured energies treated as pinned, about 0.5% of the bulk beta peak


def oc(z, e):
    z = np.atleast_2d(z); e = np.atleast_1d(e)
    loc = E0 + LOC_S * z[:, :NK]; w = W * np.exp(LW * z[:, NK:2 * NK]); a = H * np.exp(LA * z[:, 2 * NK:])
    u = (e[None, :, None] - loc[:, None, :]) / w[:, None, :]
    cb = RHO_B * np.interp(e, E, CONT[:, 1]); cd = RHO_B * np.interp(e, E, CONT[:, 0])
    beta = cb + (a[:, None] * np.exp(-u**2)).sum(-1); delta = cd + DN * (a[:, None] * dawsn(u)).sum(-1)
    return np.concatenate([beta, delta], 1)


def jac(e, h=1e-6):
    s = np.vstack([np.eye(NL) * h, -np.eye(NL) * h]); f = oc(s, e)
    return ((f[:NL] - f[NL:]) / (2 * h)).T


G = jac(EW); PRIOR = float(np.trace(G @ G.T))


def info(e, sig):
    j = jac(np.atleast_1d(e)); return j.T @ j / sig**2


def post_cov(F):
    return np.linalg.inv(np.eye(NL) + F)


def reduction(C):
    return 1 - float(np.trace(G @ C @ G.T)) / PRIOR


def band(C):
    v = np.einsum("ij,jk,ik->i", G, C, G); return np.sqrt(v[:m]), np.sqrt(v[m:])


F0 = info(MEAS, NOISE); C0 = post_cov(F0); r0 = reduction(C0)
# greedy GP picks on a 0.05 eV grid, each maximizing the drop in integrated variance of n
cand = np.round(np.arange(283.0, 290.0001, 0.05), 3)
Jc = {e: jac(np.array([e])) for e in cand}
picks, F, red = [], F0.copy(), [r0]
for _ in range(3):
    best = max(cand, key=lambda e: reduction(post_cov(F + Jc[e].T @ Jc[e] / NOISE**2)))
    F = F + Jc[best].T @ Jc[best] / NOISE**2; picks.append(float(best)); red.append(reduction(post_cov(F)))
C1 = post_cov(F0 + Jc[picks[0]].T @ Jc[picks[0]] / NOISE**2)
scan = np.arange(283.0, 290.0001, 0.1)
sig_scan = NOISE * np.sqrt(scan.size / MEAS.size)          # same total dose as the ten measured energies
r_scan = reduction(post_cov(info(scan, sig_scan)))
sig_scan1 = NOISE * np.sqrt(scan.size / (MEAS.size + 1))   # same dose as ten energies plus the GP pick
print("measured", MEAS)
print(f"reduction, 10 measured energies {r0:.3f}")
sb0, sd0 = band(C0)
print("posterior sd of beta at measured energies (1e-3):", np.round(np.interp(MEAS, EW, sb0) * 1e3, 3))
print("posterior sd of beta, max off the measured energies (1e-3):", round(sb0.max() * 1e3, 3), "at", EW[sb0.argmax()])
print("prior sd of beta, max (1e-3):", round(np.sqrt((G[:m]**2).sum(1)).max() * 1e3, 3))
print("GP picks", picks, "cumulative reductions", np.round(red, 3))
print(f"energy scan at the dose of the 10 energies {r_scan:.5f}, sigma per point {sig_scan:.2e}")

# ---------------------------------------------------------------- figure
mpl.rcParams.update({"font.family": "Caladea", "font.size": 12.5, "axes.linewidth": 1.0, "mathtext.fontset": "stix",
                     "xtick.direction": "in", "ytick.direction": "in"})
RED, BLUE, GREY, INK, DARK = "#CA1237", "#23476B", "#8A8F94", "#1F1F1F", "#424C4E"
fig = plt.figure(figsize=(12.0, 4.6), dpi=300)
L0, Wl, L1, Wr, B0, Hh, gap = 0.065, 0.235, 0.385, 0.6, 0.12, 0.38, 0.03
aAb = fig.add_axes([L0, B0 + Hh + gap, Wl, Hh]); aAd = fig.add_axes([L0, B0, Wl, Hh], sharex=aAb)
aBb = fig.add_axes([L1, B0 + Hh + gap, Wr, Hh]); aBd = fig.add_axes([L1, B0, Wr, Hh], sharex=aBb)
U = r"($10^{-3}$ cm$^3$/g)"

# A, the three fitted bookends (surface, bulk, substrate), per unit density
cm = plt.get_cmap("RdBu")
BCOL = {"surface": cm(0.08), "bulk": "k", "substrate": cm(0.83)}
u_all = (E[:, None] - E0[None]) / W[None]
for k, (h, rho) in BOOK.items():
    b = rho * CONT[:, 1] + (h[None] * np.exp(-u_all**2)).sum(1)
    d = rho * CONT[:, 0] + DN * (h[None] * dawsn(u_all)).sum(1)
    lw = 2.2 if k == "bulk" else 1.5
    aAb.plot(E, b / rho * 1e3, color=BCOL[k], lw=lw); aAd.plot(E, d / rho * 1e3, color=BCOL[k], lw=lw)
for i_, k in enumerate(BOOK):
    aAb.text(0.98, 0.97 - 0.15 * i_, k, transform=aAb.transAxes, va="top", ha="right", fontsize=12,
             color=BCOL[k], fontweight="bold" if k == "bulk" else "normal")
aAb.set_ylabel(r"$\beta/\rho$"); aAd.set_ylabel(r"$\delta/\rho$"); aAd.set_xlabel("Photon energy (eV)")
aAb.set_title("Fitted film  " + U, fontsize=12.5, loc="left", color=INK)
aAb.set_xlim(283, 290)

# B, what the ten energies pin down in the bulk, beta and delta
rng = np.random.default_rng(4)
Z = rng.standard_normal((80, NL)) @ np.linalg.cholesky(C0).T
best = oc(np.zeros(NL), EW)[0]
draws = best + Z @ G.T          # linearized posterior, the same Gaussian behind the numbers and the GP pick
for ax, sl in ((aBb, slice(0, m)), (aBd, slice(m, 2 * m))):
    for c in draws[:, sl]:
        ax.plot(EW, c / RHO_B * 1e3, color=GREY, lw=0.6, alpha=0.4, zorder=2)
    ax.plot(EW, best[sl] / RHO_B * 1e3, color="k", lw=1.5, zorder=4)
    ax.plot(MEAS, np.interp(MEAS, EW, best[sl]) / RHO_B * 1e3, "o", ms=6.5, mfc="none", mec=RED, mew=1.8, zorder=6)
    ax.axvline(picks[0], color=BLUE, lw=1.5, ls=(0, (5, 3)), zorder=5)
    ax.set_xlim(283, 290)
aBb.set_ylabel(r"bulk $\beta/\rho$"); aBd.set_ylabel(r"bulk $\delta/\rho$"); aBd.set_xlabel("Photon energy (eV)")
aBb.set_title("Bulk, through our 10 measured energies", fontsize=12.5, loc="left", color=INK)
aBb.set_ylim(0, 2.6)
gp = picks[0]
aBb.text(gp - 0.07, aBb.get_ylim()[1] * 0.97, f"{gp:.1f} eV", color=BLUE, fontsize=12.5, va="top", ha="right",
         bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=1.2), zorder=7)
left0 = 1 - r0
gain_gp = left0 / (1 - red[1]); gain_scan = left0 / (1 - r_scan)
fmt = lambda g: f"{g:.1f}\u00d7" if g < 10 else f"{float(f'{g:.2g}'):.0f}\u00d7"
for i_, (t, c) in enumerate(((f"one more energy, chosen by GP   {fmt(gain_gp)} more certain", BLUE),
                             (f"full spectrum, measured coarsely   {fmt(gain_scan)} more certain", DARK))):
    aBb.text(0.012, 0.985 - 0.13 * i_, t, transform=aBb.transAxes, color=c, fontsize=12.5, fontweight="bold", va="top", ha="left", zorder=7)
print("gain GP", gain_gp, "gain scan", gain_scan)
for ax in (aAb, aAd, aBb, aBd):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
plt.setp(aAb.get_xticklabels(), visible=False); plt.setp(aBb.get_xticklabels(), visible=False)
fig.savefig("/home/claude/assets/alq3_design.png", dpi=300)
np.savez("/home/claude/assets/alq3_design_numbers.npz", r0=r0, picks=picks, red=red, r_scan=r_scan, sig_scan=sig_scan)
