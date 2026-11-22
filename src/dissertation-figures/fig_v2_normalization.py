"""Fig. 5.2 only, revision 2. Panel d is now derived from the measured magic-angle spectrum of panel c
(beta from mu_m, delta by Kramers-Kronig with the bare-atom extension), as X-ray Atlas computes it.
Previously panel d showed the isotropic trace of the refined building-block tensor."""
import json
from figlib import *
_save = save
def save(fig, name):
    if name != 'fig5-02_normalization':
        plt.close(fig); return  # superseded by fig_v2_ch5.py or vetoed
    _save(fig, name)
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon, Arc


def box(ax, x, y, w, h, text, ec=BLACK, fs=8.5, fc='white'):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle='round,pad=0.02,rounding_size=0.1',
                                fc=fc, ec=ec, lw=1.1))
    ax.text(x, y, text, ha='center', va='center', fontsize=fs)


# ================================================================ 5.2 normalization
bb, nx, mu = znpc_tables()
pre, post = (270.0, 282.0), (320.0, 330.0)
fig, axs = plt.subplots(2, 2, figsize=(6.5, 4.9)); fig.subplots_adjust(wspace=0.36, hspace=0.5, left=0.1, right=0.98, top=0.94, bottom=0.09); axs = axs.ravel()
thetas = sorted(nx.theta_deg.unique())
for th in thetas:
    d = nx[nx.theta_deg == th]
    E, raw = d.energy.values, d.intensity_raw.values
    c = RED if th == 20 else (BLACK if th == 90 else LGRAY)
    lw = 1.4 if th in (20, 90) else 0.9
    if th == 54.7:
        axs[0].plot(E, raw, color=BLACK, lw=1.2)
    pm = raw[(E >= pre[0]) & (E <= pre[1])].mean(); qm = raw[(E >= post[0]) & (E <= post[1])].mean()
    axs[1].plot(E, (raw - pm) / (qm - pm), color=c, lw=lw, label=f'{th:g}°' if th in (20, 90) else None)
for a in axs[:3]:
    a.axvspan(*pre, color=LGRAY, alpha=0.5, lw=0); a.axvspan(*post, color=LGRAY, alpha=0.5, lw=0)
axs[0].set_ylabel('TEY (arb.)'); axs[0].set_title('Raw TEY, θ = 54.7°', fontsize=8)
axs[1].set_ylabel('Normalized'); axs[1].set_title('Normalized 0 to 1, all θ', fontsize=8); axs[1].legend(fontsize=7.5, loc='upper right')
d = nx[nx.theta_deg == 54.7]
E = d.energy.values
axs[2].plot(E, d.intensity_norm.values / 1e3, color=BLACK, lw=1.2, label='ZnPc')
axs[2].plot(E, np.interp(E, mu.energy, mu.mu) / 1e3, color=RED, ls='--', lw=1.2, label='bare atom')
axs[2].set_ylabel(r'$\mu_m$ ($10^3$ cm$^2$ g$^{-1}$)'); axs[2].set_title('Bare-atom normalized', fontsize=8)
axs[2].legend(fontsize=7.5, loc='upper right')
# d, isotropic optical constants from the measured magic-angle spectrum of c, as X-ray Atlas derives them:
# beta = lambda rho mu_m / (4 pi) on the measured grid, embedded in the bare-atom beta from 10 eV to 30 keV,
# then delta by the Kramers-Kronig transform (exact integration of piecewise-linear beta).
RHO = 1.64
Em, mum = E, d.intensity_norm.values
wide = np.concatenate([mu.energy.values[mu.energy < Em.min()], Em, mu.energy.values[mu.energy > Em.max()]])
mu_w = np.concatenate([mu.mu.values[mu.energy < Em.min()], mum, mu.mu.values[mu.energy > Em.max()]])
o = np.argsort(wide, kind='stable'); wide, mu_w = wide[o], mu_w[o]
wide, iu = np.unique(wide, return_index=True); mu_w = mu_w[iu]  # drop repeated energies
b_w = beta_from_mu(wide, mu_w, RHO)
Ee = np.linspace(270.5, 329.5, 591)
b_iso = beta_from_mu(Ee, np.interp(Ee, Em, mum), RHO)
d_iso = kk_delta(wide, b_w, Ee)
axs[3].plot(Ee, b_iso * 1e3, color=BLACK, label=r'$\beta$'); axs[3].plot(Ee, d_iso * 1e3, color=RED, label=r'$\delta$')
axs[3].axhline(0, color=LGRAY, lw=0.8)
axs[3].set_ylabel(r'$\beta$, $\delta$ ($\times10^{-3}$)'); axs[3].set_title(r'Optical constants, $\rho$ = 1.64 g cm$^{-3}$', fontsize=8)
axs[3].legend(fontsize=7.5)
for k, a in enumerate(axs):
    a.set_xlabel('Photon energy (eV)'); a.set_xlim(270, 330)
grid_labels(fig, [[(axs[0], 'a'), (axs[1], 'b')], [(axs[2], 'c'), (axs[3], 'd')]])
save(fig, 'fig5-02_normalization')

