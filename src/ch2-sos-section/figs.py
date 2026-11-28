import sys; sys.path.insert(0, "/home/claude/work/figsrc")
from style import *
import numpy as np, pandas as pd
from scipy.special import dawsn
OUT = "/home/claude/work/figs/"
EXP = "/mnt/user-data/uploads/lr-optical-models/@models/optical/alq3/exp/"
CK = "/mnt/user-data/uploads/lr-optical-models/@models/checkpoints/alq3_best_fit_export/"

# ---------- Alq3 export: edge from the bulk tensor minus the fitted bulk peaks
pk = pd.read_parquet(CK + "alq3_best_fit_peaks_and_step_edge.parquet")
tn = pd.read_parquet(CK + "alq3_best_fit_optical_tensor.parquet")
peaks = pk[pk.component == "peak"].sort_values("energy_eV")
step = pk[pk.component == "step_edge"].iloc[0]
bulk = tn[tn.region == "bulk"].sort_values("energy_eV")
E, beta, delta = bulk.energy_eV.values, bulk.beta.values, bulk.delta.values
E0, W = peaks.energy_eV.values, peaks.width_eV.values
gb = lambda E, e0, w, h: h * np.exp(-((E[:, None] - e0) / w) ** 2)
gd = lambda E, e0, w, h: 2 * h / np.sqrt(np.pi) * dawsn((E[:, None] - e0) / w)
beta_edge = beta - gb(E, E0, W, peaks.height_bulk.values).sum(1)
delta_edge = delta - gd(E, E0, W, peaks.height_bulk.values).sum(1)
HS = peaks.height_bulk_seed.values
bi, di = gb(E, E0, W, HS), gd(E, E0, W, HS)
IP = float(step.energy_eV)
print("IP", IP, "n peaks", len(E0))

# ---------- 1. single-resonance column (3.91 x 5.86 in)
def header(fig, t1, t2, c1):
    fig.text(0.05, 0.965, t1, fontsize=17, color=c1, va="top")
    fig.text(0.05, 0.925, t2, fontsize=12.5, color=SLATE, va="top")

fig = plt.figure(figsize=(3.91, 5.86))
header(fig, "One resonance", "Gaussian β with its Dawson δ", CRIMSON)
x = np.linspace(-3, 3, 1201); fw = 1.0
w = fw / (2 * np.sqrt(np.log(2))); g = fw / 2
axb = fig.add_axes([0.20, 0.53, 0.75, 0.30]); axd = fig.add_axes([0.20, 0.11, 0.75, 0.33], sharex=axb)
axb.fill_between(x, 0, np.exp(-(x / w) ** 2), color=CRIMSON, alpha=0.18, lw=0)
axb.plot(x, np.exp(-(x / w) ** 2), color=CRIMSON, lw=2.0, label="Gaussian")
axb.plot(x, 1 / (1 + (x / g) ** 2), color=SLATE, lw=1.3, ls=(0, (4, 2.5)), label="Lorentz")
axd.plot(x, 2 / np.sqrt(np.pi) * dawsn(x / w), color=BLUE, lw=2.0, label="Dawson")
axd.plot(x, (x / g) / (1 + (x / g) ** 2), color=SLATE, lw=1.3, ls=(0, (4, 2.5)), label="Lorentz")
for a in (axb, axd): a.axhline(0, color=SLATE, lw=0.6); a.set_xlim(-3, 3)
axb.set_ylim(-0.03, 1.12); axb.set_yticks([0, 0.5, 1]); axd.set_ylim(-0.75, 0.75); axd.set_yticks([-0.5, 0, 0.5])
axb.set_ylabel(r"$\beta_i$ / $A_i$"); axd.set_ylabel(r"$\delta_i$ / $A_i$")
plt.setp(axb.get_xticklabels(), visible=False)
axd.set_xlabel(r"$E-E_i$ (eV)")
axb.legend(loc="upper right", fontsize=11, handlelength=1.6, borderaxespad=0)
axd.legend(loc="upper left", fontsize=11, handlelength=1.6, borderaxespad=0)
axb.annotate("", xy=(w, np.exp(-1)), xytext=(0, np.exp(-1)), arrowprops=dict(arrowstyle="->", color=INK, lw=0.9))
axb.plot([0, 0], [0, 1], color=INK, lw=0.6, ls=(0, (2, 2)))
axb.text(w / 2, np.exp(-1) - 0.04, r"$\gamma_i$", ha="center", va="top", fontsize=13)
axb.text(0.06, 1.04, r"$E_i$", ha="left", va="bottom", fontsize=13)
fig.savefig(OUT + "sos-one-resonance.png", dpi=300); plt.close(fig)

# ---------- 2. ionization-edge column
fig = plt.figure(figsize=(3.91, 5.86))
header(fig, "Ionization edge", "erf step with its KK δ", CLAY)
m = (E >= 278) & (E <= 320)
axb = fig.add_axes([0.20, 0.53, 0.75, 0.30]); axd = fig.add_axes([0.20, 0.11, 0.75, 0.33], sharex=axb)
axb.fill_between(E[m], 0, 1e3 * beta_edge[m], color=CLAY, alpha=0.20, lw=0)
axb.plot(E[m], 1e3 * beta_edge[m], color=CLAY, lw=2.0)
axd.plot(E[m], 1e3 * delta_edge[m], color=BLUE, lw=2.0)
for a in (axb, axd): a.axvline(IP, color=SLATE, lw=0.9, ls=(0, (3, 2.5))); a.set_xlim(278, 320)
axb.set_ylim(0, 1.15 * 1e3 * beta_edge[m].max())
axb.text(IP + 0.6, 0.97 * axb.get_ylim()[1], f"IP {IP:.1f} eV", fontsize=11, color=SLATE, va="top")
axb.text(280, 0.22 * axb.get_ylim()[1], "pre edge", fontsize=11, color=SLATE)
axb.text(305, 0.45 * axb.get_ylim()[1], "post edge", fontsize=11, color=SLATE)
axb.set_ylabel(r"$\beta_{\mathrm{edge}}$ ($10^{-3}$)"); axd.set_ylabel(r"$\delta_{\mathrm{edge}}$ ($10^{-3}$)")
plt.setp(axb.get_xticklabels(), visible=False); axd.set_xticks([280, 290, 300, 310, 320])
axd.set_xlabel("Photon energy (eV)")
fig.savefig(OUT + "sos-ionization-edge.png", dpi=300); plt.close(fig)

# ---------- 3. Alq3 composition (card figure)
XLO, XHI = 282.5, 300.0
w_ = (E >= XLO) & (E <= XHI); Ew = E[w_]
inwin = (E0 >= XLO) & (E0 <= XHI)
fig = plt.figure(figsize=(7.0, 4.75))
axs = fig.add_axes([0.11, 0.835, 0.86, 0.12]); axb = fig.add_axes([0.11, 0.47, 0.86, 0.34]); axd = fig.add_axes([0.11, 0.10, 0.86, 0.33])
for a in (axs, axb, axd): a.set_xlim(XLO, XHI)
# resonators: dipole arrows whose length follows sqrt(strength)
area = HS * W
L = np.sqrt(area / area[inwin].max())
for e0, l in zip(E0[inwin], L[inwin]):
    if l < 0.2:
        axs.plot([e0], [0.08], "o", color=DEEP, ms=2.6); continue
    axs.annotate("", xy=(e0, 0.08 + 0.9 * l), xytext=(e0, 0.08), arrowprops=dict(arrowstyle="-|>", color=DEEP, lw=1.3, mutation_scale=8))
    axs.plot([e0], [0.08], "o", color=DEEP, ms=2.6)
axs.set_ylim(0, 1.1); axs.axis("off")
axs.text(XLO - 0.15, 0.5, r"$\boldsymbol{\mu}_i$", ha="right", va="center", fontsize=14, color=DEEP)
axs.text(XHI, 1.02, "ML-DFT resonators, arrow length $\\propto |A_i|^{1/2}$", ha="right", va="bottom", fontsize=10.5, color=SLATE)
S = 1e3
be = beta_edge[w_]
for k in np.where(inwin)[0]:
    axb.fill_between(Ew, S * be, S * (be + bi[w_, k]), color=CRIMSON, alpha=0.20, lw=0)
    axd.fill_between(Ew, 0, S * di[w_, k], color=BLUE, alpha=0.16, lw=0)
axb.plot(Ew, S * be, color=CLAY, lw=1.8, label="edge")
axb.plot(Ew, S * (be + bi[w_].sum(1)), color=INK, lw=1.6, label=r"$\beta = \beta_{\mathrm{edge}} + \Sigma_i \beta_i$")
axd.plot(Ew, S * delta_edge[w_], color=CLAY, lw=1.8)
axd.plot(Ew, S * (delta_edge[w_] + di[w_].sum(1)), color=INK, lw=1.6, label=r"$\delta = \delta_{\mathrm{edge}} + \Sigma_i \delta_i$")
for a in (axb, axd): a.axhline(0, color=SLATE, lw=0.5)
axb.set_ylim(0, 4.1); axd.set_ylim(-1.9, 2.3); axb.set_ylabel(r"$\beta$ ($10^{-3}$)"); axd.set_ylabel(r"$\delta$ ($10^{-3}$)")
plt.setp(axb.get_xticklabels(), visible=False); axd.set_xlabel("Photon energy (eV)")
from matplotlib.patches import Patch
axb.legend(handles=[Patch(fc=CRIMSON, alpha=0.3, label=r"Gaussian $\beta_i$"), axb.lines[0], axb.lines[1]], loc="upper left", fontsize=11, handlelength=1.4, ncol=3, borderaxespad=0, columnspacing=1.2)
axd.legend(handles=[Patch(fc=BLUE, alpha=0.3, label=r"Dawson $\delta_i$"), axd.lines[0], axd.lines[1]], labels=[r"Dawson $\delta_i$", "edge", r"$\delta = \delta_{\mathrm{edge}} + \Sigma_i \delta_i$"], loc="lower left", fontsize=11, handlelength=1.4, ncol=3, borderaxespad=0, columnspacing=1.2)
fig.savefig(OUT + "sos-alq3-composition.png", dpi=300); plt.close(fig)

# ---------- 4. two films (problem slide column A)
def load(f):
    d = pd.read_csv(EXP + f).rename(columns=str.strip).sort_values("energy"); return d.energy.values, d.n_ixx.values
e1, b1 = load("Alq3_model_oc.csv"); e2, b2 = load("alq3_TEY_Dec2025_short.csv")
def affine(e, b, ref_pre, ref_post):
    p, q = b[e < 280].mean(), b[(e > 312) & (e < 320)].mean()
    return ref_pre + (b - p) * (ref_post - ref_pre) / (q - p)
pre1, post1 = b1[e1 < 280].mean(), b1[(e1 > 312) & (e1 < 320)].mean()
b2n = affine(e2, b2, pre1, post1)
fig = plt.figure(figsize=(3.30, 2.55))
ax = fig.add_axes([0.20, 0.20, 0.74, 0.74])
for e, b, c, lab in ((e1, b1, CRIMSON, "100 nm"), (e2, b2n, BLUE, "20 nm")):
    mm = (e >= 283) & (e <= 292); ax.plot(e[mm], 1e3 * b[mm], color=c, lw=1.8, label=lab)
ax.set_xlim(283, 292); ax.set_ylim(0, None); ax.set_xticks([284, 286, 288, 290, 292])
ax.set_xlabel("Photon energy (eV)", fontsize=11); ax.set_ylabel(r"$\beta$ ($10^{-3}$)", fontsize=11)
ax.tick_params(labelsize=10); ax.legend(loc="lower right", fontsize=10.5, handlelength=1.3, borderaxespad=0)
fig.savefig(OUT + "alq3-two-films.png", dpi=300); plt.close(fig)
print("ok")
