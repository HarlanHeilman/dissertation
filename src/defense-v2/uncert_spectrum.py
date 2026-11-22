"""Slide 25 companion panel. Linearized (Laplace) posterior uncertainty of n = 1 - delta + i beta versus energy
for the four sampling designs of dissertation Fig. 5.5 (lr-optical-models manuscript/fig5_sensitivity.ipynb,
same synthetic polystyrene edge, prior, noise, seeds and probe rules). The continuum is shared by every draw, so
only the 30 peak latents enter the covariance. Plotted is sqrt(var_post / var_prior) of n at each energy."""
import numpy as np, matplotlib as mpl, matplotlib.pyplot as plt
from scipy.special import dawsn
mpl.rcParams.update({"font.family": "Caladea", "font.size": 12, "mathtext.fontset": "stix", "axes.linewidth": 1.0,
                     "xtick.direction": "in", "ytick.direction": "in"})
ENERGY = np.linspace(280.0, 320.0, 1000); XLIM = (283.0, 290.0)
N_PEAKS, N_PROBES, NOISE, SCAN_STEP, MIN_GAP, SEED = 10, 4, 1e-4, 0.1, 0.3, 3
LOCS0 = np.array([284.05, 284.55, 285.15, 285.85, 286.55, 287.25, 288.05, 288.75, 289.55, 291.5])
WIDTHS0 = np.array([0.30, 0.28, 0.32, 0.30, 0.38, 0.45, 0.55, 0.70, 0.90, 1.50])
AMPS0 = np.array([1.4e-3, 4.8e-3, 2.2e-3, 3.6e-3, 1.5e-3, 2.4e-3, 1.3e-3, 1.6e-3, 0.9e-3, 0.55e-3])
LOC_SCALE = np.array([0.22, 0.28, 0.28, 0.28, 0.25, 0.25, 0.22, 0.22, 0.20, 0.20]); LW, LA = 0.25, 0.35
NL = 3 * N_PEAKS; DN = 2 / np.sqrt(np.pi)
def oc(z, e):
    z = np.atleast_2d(z); e = np.atleast_1d(e)
    l = LOCS0 + LOC_SCALE * z[:, :10]; w = WIDTHS0 * np.exp(LW * z[:, 10:20]); a = AMPS0 * np.exp(LA * z[:, 20:])
    u = (e[None, :, None] - l[:, None, :]) / w[:, None, :]
    return np.concatenate([(a[:, None] * np.exp(-u**2)).sum(-1), DN * (a[:, None] * dawsn(u)).sum(-1)], 1)
def jac(e, h=1e-6):
    s = np.vstack([np.eye(NL) * h, -np.eye(NL) * h]); f = oc(s, e)
    return ((f[:NL] - f[NL:]) / (2 * h)).T
E_WIN = ENERGY[(ENERGY >= XLIM[0]) & (ENERGY <= XLIM[1])]; G = jac(E_WIN); m = E_WIN.size
def cov(p, sig):
    j = jac(p); return np.linalg.inv(np.eye(NL) + j.T @ j / sig**2)
def rand_p(rng):
    while True:
        p = np.sort(rng.uniform(*XLIM, size=N_PROBES))
        if np.all(np.diff(p) >= MIN_GAP): return p
def gp_p():
    c = G @ G.T; picks = []
    for _ in range(N_PROBES):
        g = np.empty(m)
        for j in range(m):
            i = [j, j + m]; k = c[:, i]; g[j] = np.trace(k @ np.linalg.solve(c[np.ix_(i, i)] + NOISE**2 * np.eye(2), k.T))
        j = int(np.argmax(g)); i = [j, j + m]; k = c[:, i]
        c = c - k @ np.linalg.solve(c[np.ix_(i, i)] + NOISE**2 * np.eye(2), k.T); picks.append(E_WIN[j])
    return np.sort(picks)
scan = np.arange(XLIM[0], XLIM[1] + 1e-9, SCAN_STEP)
S = {"On peaks": (LOCS0[:4], NOISE), "Random": (rand_p(np.random.default_rng(SEED)), NOISE), "GP": (gp_p(), NOISE),
     "Energy scan": (scan, NOISE * np.sqrt(scan.size / N_PROBES))}
prior = (G**2).sum(1); prior_n = prior[:m] + prior[m:]
fig, ax = plt.subplots(figsize=(4.6, 2.55), dpi=400)
COL = {"On peaks": "#E07B39", "Random": "#8A8F94", "GP": "#23476B", "Energy scan": "#CA1237"}
for k, (p, sg) in S.items():
    C = cov(p, sg); post = np.einsum("ij,jk,ik->i", G, C, G); pn = post[:m] + post[m:]
    red = 1 - pn.sum() / prior_n.sum()
    r = np.sqrt(pn / prior_n)
    ax.plot(E_WIN, r, color=COL[k], lw=1.6 if k != "Random" else 1.2, label=k)
    if k != "Energy scan":
        ax.plot(p, np.interp(p, E_WIN, r), "o", ms=4.5, color=COL[k], mec="white", mew=0.6, zorder=5)
    print(k, np.round(p, 2), f"reduction {red:.3f}", f"max remaining {r.max():.2f}, mean {r.mean():.2f}")
ax.axhline(1, color="0.6", lw=0.8, ls=(0, (4, 2))); ax.text(283.08, 1.0, "prior", ha="left", va="bottom", fontsize=10, color="0.45")
ax.set_xlim(*XLIM); ax.set_ylim(0, 1.08)
ax.set_xlabel("Photon energy (eV)"); ax.set_ylabel(r"$\sigma_n$ / $\sigma_n^{\,prior}$")
ax.legend(frameon=False, fontsize=9.5, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=4, handlelength=1.2, columnspacing=0.9, borderaxespad=0.1)
fig.tight_layout(pad=0.3); fig.savefig("/home/claude/assets/uncert_spectrum.png", dpi=400)
