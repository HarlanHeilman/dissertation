from figlib import *
from matplotlib.patches import FancyBboxPatch

bb, nx, mu = znpc_tables()
E = np.linspace(270, 330, 1201)
n = znpc_index(E)
rho = 1.64
bare = beta_from_mu(E, np.interp(E, mu.energy, mu.mu), rho)

fig = plt.figure(figsize=(6.5, 5.0))
gs = fig.add_gridspec(2, 2, width_ratios=[1.75, 1], wspace=0.12, hspace=0.42, left=0.1, right=0.99, top=0.97, bottom=0.09)

# a beta
ax = fig.add_subplot(gs[0, 0]); axa = ax
ax.axvspan(270, 282, color=LGRAY, alpha=0.5, lw=0)
ax.axvspan(320, 330, color=LGRAY, alpha=0.5, lw=0)
ax.plot(E, bare * 1e3, color=GRAY, ls='--', lw=1.2, label='bare atom')
ax.plot(E, n['zz'].imag * 1e3, color=BLACK, label=r'$\beta_{zz}$')
ax.plot(E, n['xx'].imag * 1e3, color=RED, label=r'$\beta_{xx}$')
ax.text(276, 7.6, 'pre\nedge', ha='center', color=GRAY, fontsize=8, va='top')
ax.text(325, 7.6, 'post\nedge', ha='center', color=GRAY, fontsize=8, va='top')
ax.set_xlim(270, 330); ax.set_ylim(0, 8)
ax.set_xlabel('Photon energy (eV)'); ax.set_ylabel(r'$\beta$ ($\times10^{-3}$)')
ax.legend(loc='center right')

# b delta
ax = fig.add_subplot(gs[1, 0]); axb = ax
ax.axhline(0, color=LGRAY, lw=0.8)
ax.plot(E, (1 - n['zz'].real) * 1e3, color=BLACK, label=r'$\delta_{zz}$')
ax.plot(E, (1 - n['xx'].real) * 1e3, color=RED, label=r'$\delta_{xx}$')
ax.set_xlim(270, 330)
ax.set_xlabel('Photon energy (eV)'); ax.set_ylabel(r'$\delta$ ($\times10^{-3}$)')
ax.legend(loc='lower left', bbox_to_anchor=(-0.02, 0.0), handlelength=1.2)
# inset: wide range beta used by the KK integral
ins = ax.inset_axes([0.62, 0.17, 0.36, 0.3])
Ew = mu.energy.values
ins.loglog(Ew, beta_from_mu(Ew, mu.mu.values, rho), color=GRAY, lw=1)
ins.axvspan(270, 330, color=RED, alpha=0.3, lw=0)
ins.set_xlim(10, 3e4); ins.tick_params(labelsize=7, length=2)
ins.set_xticks([1e1, 1e3]); ins.set_yticks([])
ins.set_xlabel('E (eV)', fontsize=7, labelpad=1)
ins.set_title(r'$\beta$ over the KK domain', fontsize=7, pad=2)

# c conventions
ax = fig.add_subplot(gs[:, 1]); blank(ax); axc = ax
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
boxes = [
    (0.5, 0.86, r'$n = 1-\delta+i\beta$'),
    (0.5, 0.58, r'$\delta=\frac{r_e\lambda^2}{2\pi}n_a f_1$' + '\n' + r'$\beta=\frac{r_e\lambda^2}{2\pi}n_a f_2$'),
    (0.5, 0.32, r'$\epsilon=n^2\simeq1-2\delta+2i\beta$'),
    (0.5, 0.07, r'$\chi=\epsilon-1\simeq-2\delta+2i\beta$'),
]
for x, y, t in boxes:
    ax.text(x, y, t, ha='center', va='center', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.45', fc='white', ec=BLACK, lw=1.0))
for y0, y1 in ((0.79, 0.66), (0.51, 0.39), (0.25, 0.14)):
    arrow(ax, 0.5, y0, 0.5, y1, color=RED, lw=1.6, both=True)
ax.text(0.62, 0.725, r'$\beta=\frac{\lambda}{4\pi}\,\rho\,\mu_m$', ha='left', fontsize=8, color=GRAY)
grid_labels(fig, [[(axa, 'a'), (axc, 'c')], [(axb, 'b')]])
save(fig, 'fig2-03_optical-constants')
