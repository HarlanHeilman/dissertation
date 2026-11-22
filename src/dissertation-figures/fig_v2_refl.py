"""Revision 2. Fig. 2.11 (TMM with multilayers), 2.12 (roughness, 3 x 3), 2.13 (transforms), 2.16 (automation)."""
import json
from figlib import *
from model import stack, nk
from henke import n_si, n_sio2
from matplotlib.patches import Rectangle, Polygon, FancyBboxPatch
from scipy.ndimage import gaussian_filter1d
from scipy.special import erfinv

FACTS = {}
q = np.linspace(0.006, 0.27, 900)


def kinematic(q, E, layers, sig=3.0):
    """Born (kinematic) specular reflectivity for s polarization from the in-plane index."""
    lmb = lam(E)
    rho = [2 * np.pi * (1 - L[0]) / lmb ** 2 for L in layers]
    z, amp = 0.0, np.zeros_like(q, dtype=complex)
    for j in range(1, len(layers)):
        amp += (rho[j] - rho[j - 1]) * np.exp(1j * q * z) * np.exp(-0.5 * (q * sig) ** 2)
        if j < len(layers) - 1:
            z += layers[j][2]
    return (16 * np.pi ** 2 / q ** 4) * np.abs(amp) ** 2


# ================================================================ Fig 2.11
E = 285.1
edge = nk(E, 69.6, 1.64); face = nk(E, 10.0, 1.64)
si, ox = n_si(E), n_sio2(E)
vac = (1 + 0j, 1 + 0j, 0, 0)
cases = [
    ('single film', [vac, (edge[0], edge[1], 192.7, 3.0), (ox, ox, 15, 3.0), (si, si, 0, 3.0)]),
    ('bilayer', [vac, (edge[0], edge[1], 100.0, 3.0), (face[0], face[1], 90.0, 3.0), (ox, ox, 15, 3.0), (si, si, 0, 3.0)]),
    ('multilayer, 6 periods', [vac] + [(edge[0], edge[1], 40.0, 3.0), (face[0], face[1], 40.0, 3.0)] * 6 +
     [(ox, ox, 15, 3.0), (si, si, 0, 3.0)]),
]
fig = plt.figure(figsize=(6.5, 4.6))
gs = fig.add_gridspec(2, 3, height_ratios=[0.85, 1], hspace=0.25, wspace=0.2, left=0.1, right=0.99, top=0.98, bottom=0.09)
PAN = []
ax = fig.add_subplot(gs[0, :]); blank(ax); ax.set_xlim(0, 21); ax.set_ylim(0, 6.2)
lays = [('', 4.6, 6.2, 'white'), ('layer 1', 3.4, 4.6, '#F2F2F2'), ('layer 2', 2.2, 3.4, '#E2E2E2'),
        ('substrate', 0.3, 2.2, '#C8C8C8')]
for nm, y0, y1, c in lays:
    ax.add_patch(Rectangle((1.0, y0), 13.0, y1 - y0, fc=c, ec=BLACK if nm else 'none', lw=1))
    if nm:
        ax.text(13.85, (y0 + y1) / 2, nm, ha='right', va='center', fontsize=7.5, color=GRAY, zorder=4,
                bbox=dict(fc=c, ec='none', pad=1.5))
# molecules filling each slab, edge-on (herringbone) in layer 1 and face-on in layer 2
def ticks(y_rows, tilt, ln, dxs, stagger=0.0):
    for r, yr in enumerate(y_rows):
        for k, xc in enumerate(np.arange(2.25 + stagger * (r % 2), 13.8, dxs)):
            t = np.radians(tilt * (1 if k % 2 == 0 else -1))
            dx, dy = 0.5 * ln * np.sin(t), 0.5 * ln * np.cos(t)
            ax.plot([xc - dx, xc + dx], [yr - dy, yr + dy], color=BLACK, lw=1.0, alpha=0.55, zorder=2,
                    solid_capstyle='round')
ticks((3.7, 4.3), 20.4, 0.42, 0.34)
ticks((2.5, 2.8, 3.1), 80.0, 0.3, 0.5, stagger=0.25)
for k, y in enumerate((4.6, 3.4, 2.2)):
    ax.text(0.85, y, f'$L_{k+1}$', ha='right', va='center', fontsize=8.5, color=RED)
for k, (y0, y1) in enumerate(((3.4, 4.6), (2.2, 3.4))):
    ax.annotate('', xy=(1.4, y0), xytext=(1.4, y1), arrowprops=dict(arrowstyle='<->', color=GRAY, lw=1))
    ax.text(1.55, (y0 + y1) / 2, f'$P_{k+1}$', va='center', fontsize=8.5, color=GRAY, zorder=4,
            bbox=dict(fc=('#F2F2F2', '#E2E2E2')[k], ec='none', pad=1))
# incident and multiply reflected partial waves
xs, slope = 2.8, 1.2
arrow(ax, xs, 6.0, xs + 1.4 / slope * 1.0, 4.6, color=RED, lw=2.2)
x = xs + 1.4 / slope; y = 4.6; dx = 1.2 / slope
pts = [(x, y)]
for k in range(5):
    yy = 3.4 if k % 2 == 0 else 4.6
    x = x + dx; pts.append((x, yy))
for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
    ax.plot([x0, x1], [y0, y1], color=RED, lw=1.6 - 0.15 * pts.index((x0, y0)), alpha=0.95, zorder=5)
for k, (xp, yp) in enumerate(pts):
    if yp == 4.6:
        arrow(ax, xp, 4.6, xp + 1.4 / slope, 6.0, color=RED, lw=max(2.0 - 0.6 * k / 2, 0.6))
ax.text(xs - 0.1, 5.7, r'$\mathbf{k}_i$', color=RED, fontsize=8.5, ha='right')
ax.text(9.6, 5.55, 'every reflected order interferes', fontsize=7.5, color=RED)
ax.text(17.6, 4.7, r'$\partial_z\Psi=i(\omega/c)\Delta\Psi$', fontsize=9, ha='center')
ax.text(17.6, 3.7, r'$\Gamma_N=L_1P_1L_2P_2\cdots L_NP_NL_{N+1}$', fontsize=9, ha='center')
ax.text(17.6, 2.7, r'$R_{kl}=|r_{kl}(\Gamma_N)|^2$', fontsize=9, ha='center')
ax.text(17.6, 1.4, 'kinematic limit counts\nonly one reflection', fontsize=7.5, ha='center', color=GRAY)
PAN.append((ax, 'a'))
dev = {}
for k, (nm, L) in enumerate(cases):
    a = fig.add_subplot(gs[1, k])
    R = reflectivity(q, E, L, 's')
    Rk = kinematic(q, E, L)
    a.semilogy(q, np.minimum(Rk, 10), color=BLACK, ls='--', lw=1.2, label='kinematic')
    a.semilogy(q, R, color=RED, lw=1.5, label='transfer matrix')
    a.set_ylim(1e-8, 3); a.set_xlim(0, 0.27)
    a.set_xlabel(r'$q$ (Å$^{-1}$)')
    if k == 0:
        a.set_ylabel(r'$R_s$'); a.legend(loc='lower left', fontsize=7.5)
    a.text(0.97, 0.9, nm, transform=a.transAxes, ha='right', fontsize=8)
    m = q > 0.05
    dev[nm] = float(np.median(np.abs(np.log10(Rk[m] / R[m]))))
    PAN.append((a, 'bcd'[k]))
    if k: a.set_yticklabels([])
FACTS['fig2_11'] = dict(E=E, median_log_dev=dev)
grid_labels(fig, [[PAN[0]], PAN[1:]], pad=0.03)
save(fig, 'fig2-11_transfer-matrix')

# ================================================================ Fig 2.12
E = 283.7
nxx, nzz = nk(E)
si = n_si(E)
SIG = 20.0
def L_(s):
    return [vac, (nxx, nzz, 192.7, s), (si, si, 0, s)]
rng = np.random.default_rng(2)
LAM = 12398.42 / E
XW = 300.0
fig = plt.figure(figsize=(6.5, 3.45))
gs = fig.add_gridspec(2, 3, height_ratios=[0.75, 1], hspace=0.22, wspace=0.36, left=0.1, right=0.95, top=0.88, bottom=0.12)
xx = np.linspace(0, XW, 1800)
names = [('nc', 'Névot-Croce', 2.0, 'short ξ, fine roughness', 'sharp step, damped by\n' + r'$e^{-2k_{z,i}k_{z,i+1}\sigma^2}$'),
         ('dw', 'Debye-Waller', 11.0, 'long ξ, broad facets', 'sharp step, damped by\n' + r'$e^{-2k_{z,i}^2\sigma^2}$'),
         ('graded', 'Graded interface', None, 'interdiffusion', 'erf profile sliced\nand computed')]
zz = np.linspace(-60, 250, 800)
dsub, dfilm = (1 - si.real) * 1e3, (1 - nxx.real) * 1e3
sharp = np.where(zz < 0, 0, np.where(zz < 192.7, dfilm, dsub))
disp = (0.5 * (1 + erf(zz / (np.sqrt(2) * SIG))) * dfilm +
        0.5 * (1 + erf((zz - 192.7) / (np.sqrt(2) * SIG))) * (dsub - dfilm))
top_axes, bot_axes = [], []
for c, (key, nm, xi, desc, how) in enumerate(names):
    a = fig.add_subplot(gs[0, c]); top_axes.append(a)
    a.set_xlim(0, XW); a.set_ylim(-62, 82); a.set_aspect('equal', adjustable='box')
    a.set_xticks([]); a.set_yticks([])
    for sp in a.spines.values():
        sp.set_visible(False)
    cmap = mpl.colors.LinearSegmentedColormap.from_list('g', ['#F2F2F2', '#8C8C8C'])
    if key == 'graded':
        zg = np.linspace(-62, 82, 300)
        pr = 0.5 * (1 + erf(-zg / (np.sqrt(2) * SIG)))
        a.imshow(np.tile(pr[:, None], (1, 50)), extent=(0, XW, -62, 82), origin='lower', cmap=cmap,
                 aspect='auto', vmin=0, vmax=1)
        a.set_aspect('equal', adjustable='box')
    else:
        h = gaussian_filter1d(rng.normal(0, 1, xx.size), xi / (xx[1] - xx[0]))
        h = np.clip(h / h.std() * SIG, -56, 56)
        a.fill_between(xx, -62, h, color='#8C8C8C', lw=0)
        a.fill_between(xx, h, 82, color='#F2F2F2', lw=0)
        a.plot(xx, h, color=BLACK, lw=0.9)
    # lateral wavelength scale in the vacuum band
    x0 = 12
    a.plot([x0, x0 + LAM], [70, 70], color=BLACK, lw=1.4, solid_capstyle='butt')
    for xv in (x0, x0 + LAM):
        a.plot([xv, xv], [65, 75], color=BLACK, lw=1.2)
    a.text(x0 + LAM + 6, 70, f'λ = {LAM:.1f} Å', fontsize=7, va='center')
    # vertical rms scale just outside the right edge
    a.annotate('', xy=(XW + 9, -SIG), xytext=(XW + 9, SIG), annotation_clip=False,
               arrowprops=dict(arrowstyle='<->', color=RED, lw=1, shrinkA=0, shrinkB=0))
    a.text(XW + 20, 0, '2σ', color=RED, fontsize=7.5, ha='left', va='center', clip_on=False)
    a.set_title(nm, fontsize=8.5, loc='center', pad=11)
    a.text(0.5, 1.03, desc, transform=a.transAxes, fontsize=7, color=GRAY, ha='center', va='bottom')
    # depth profile
    a = fig.add_subplot(gs[1, c]); bot_axes.append(a)
    a.plot(zz, sharp if key == 'graded' else disp, color=GRAY if key == 'graded' else BLACK, lw=1.0, ls='--')
    if key == 'graded':
        _, zc, gxx, _ = graded_layers(L_(SIG))
        a.plot(zc, (1 - gxx.real) * 1e3, color=RED, lw=1.8)
    else:
        a.plot(zz, sharp, color=RED, lw=1.8)
    a.set_xlim(-60, 250); a.set_ylim(-3.6, 7.2); a.set_xlabel('Depth z (Å)')
    if c == 0:
        a.set_ylabel(r'$\delta_{xx}$ ($\times10^{-3}$)')
    a.text(0.5, 0.95, how, transform=a.transAxes, ha='center', va='top', fontsize=7, color=GRAY)
# panel letters on one left margin, each level with the top of its row
fig.canvas.draw()
grid_labels(fig, [[(top_axes[0], 'a')], [(bot_axes[0], 'b')]])
save(fig, 'fig2-12_interfaces')

# ================================================================ Fig 2.13
E = 285.1
R = reflectivity(q, E, stack(E), 's')
rng = np.random.default_rng(11)
sig = 0.08 * R + 0.5e-6 * q
Dd = np.clip(R + rng.normal(0, 1, q.size) * sig * 0.5, 1e-10, None)
R2 = reflectivity(q, E, stack(E, t=192.7 + 2.0), 's')
fig, axs = plt.subplots(2, 2, figsize=(6.5, 4.9)); fig.subplots_adjust(wspace=0.38, hspace=0.42, left=0.1, right=0.98, top=0.97, bottom=0.1); axs = axs.ravel()
axs[0].errorbar(q, Dd, sig, fmt='o', ms=1.6, color=BLACK, elinewidth=0.5); axs[0].plot(q, R, color=RED, lw=1.2)
axs[0].set_ylabel('$R$')
axs[1].plot(q, np.log10(Dd), 'o', ms=1.6, color=BLACK); axs[1].plot(q, np.log10(R), color=RED, lw=1.2)
axs[1].set_ylabel(r'$\log_{10}R$')
axs[2].plot(q, Dd * q ** 4 * 1e7, 'o', ms=1.6, color=BLACK); axs[2].plot(q, R * q ** 4 * 1e7, color=RED, lw=1.2)
axs[2].set_ylabel(r'$Rq^4$ ($10^{-7}$ Å$^{-4}$)')
for nm, d_, c, ls in (('in R', np.abs(R2 - R), BLACK, '-'), (r'in $\log_{10}R$', np.abs(np.log10(R2) - np.log10(R)), RED, '-'),
                      (r'in $Rq^4$', np.abs(R2 - R) * q ** 4, RED, '--')):
    from scipy.ndimage import maximum_filter1d
    env = gaussian_filter1d(maximum_filter1d(d_, 61), 6)
    axs[3].plot(q, env / env.max(), color=c, ls=ls, lw=1.5, label=nm)
axs[3].set_ylabel('Misfit from a 2 Å\nthickness error (scaled)')
axs[3].legend(fontsize=7, loc='lower center', bbox_to_anchor=(0.5, 1.0), ncol=3, handlelength=1.4, columnspacing=1.0)
for k, a in enumerate(axs):
    a.set_xlabel(r'$q$ (Å$^{-1}$)'); a.set_xlim(0, 0.27)
grid_labels(fig, [[(axs[0], 'a'), (axs[1], 'b')], [(axs[2], 'c'), (axs[3], 'd')]])
save(fig, 'fig2-13_objective-transforms')

# ================================================================ Fig 2.16 automation flowchart
def node(ax, x, y, w, h, t, ec=BLACK, fs=7.5, diamond=False):
    if diamond:
        ax.add_patch(Polygon([(x, y + h / 2), (x + w / 2, y), (x, y - h / 2), (x - w / 2, y)], fc='white', ec=ec, lw=1.2))
    else:
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle='round,pad=0.02,rounding_size=0.12',
                                    fc='white', ec=ec, lw=1.2))
    ax.text(x, y, t, ha='center', va='center', fontsize=fs)
def link(ax, pts, c=BLACK, lbl=None, lpos=None, lc=None):
    xs_, ys_ = zip(*pts)
    ax.plot(xs_[:-1] + (xs_[-1],), ys_[:-1] + (ys_[-1],), color=c, lw=1.2)
    ax.annotate('', xy=pts[-1], xytext=pts[-2], arrowprops=dict(arrowstyle='-|>', color=c, lw=1.2, shrinkA=0, shrinkB=0))
    if lbl:
        ax.text(*lpos, lbl, fontsize=7.5, color=lc or c)
fig, ax = plt.subplots(figsize=(6.5, 4.4)); fig.subplots_adjust(0, 0, 1, 1); blank(ax); ax.set_xlim(0, 21); ax.set_ylim(0, 11)
node(ax, 10.5, 10.0, 5.2, 1.2, 'Gaussian process\nnext condition or next sample?', ec=RED)
node(ax, 2.6, 7.3, 3.2, 1.2, 'find sample')
node(ax, 7.2, 7.3, 3.4, 1.2, 'alignment checker')
node(ax, 7.2, 4.9, 3.4, 1.5, 'polarization\nchanged?', diamond=True)
node(ax, 3.0, 3.4, 2.8, 1.0, 'wait 15 min')
node(ax, 7.2, 2.3, 3.4, 1.5, 'aligned at\n1° and 2°?', diamond=True)
node(ax, 7.2, 0.6, 3.0, 0.9, 'realign sample')
node(ax, 12.6, 7.3, 3.6, 1.2, 'measure one condition')
node(ax, 12.6, 4.9, 3.6, 1.2, 'optimize intensity\nfor the next series')
node(ax, 12.6, 2.4, 3.6, 1.2, 'measure until the\nbeam is lost')
node(ax, 17.8, 4.9, 3.4, 1.5, 'condition\ncomplete?', diamond=True)
link(ax, [(7.9, 10.0), (2.6, 10.0), (2.6, 7.9)], lbl='new sample', lpos=(3.0, 10.15))
link(ax, [(10.5, 9.4), (10.5, 8.6), (7.2, 8.6), (7.2, 7.9)], lbl='new condition', lpos=(7.5, 8.75))
link(ax, [(4.2, 7.3), (5.5, 7.3)])
link(ax, [(7.2, 6.7), (7.2, 5.65)])
link(ax, [(5.5, 4.9), (3.0, 4.9), (3.0, 3.9)], lbl='yes', lpos=(3.8, 5.05))
link(ax, [(3.0, 2.9), (3.0, 2.3), (5.5, 2.3)])
link(ax, [(7.2, 4.15), (7.2, 3.05)], lbl='no', lpos=(7.35, 3.5))
link(ax, [(7.2, 1.55), (7.2, 1.05)], lbl='no', lpos=(7.35, 1.2))
link(ax, [(8.9, 2.3), (9.9, 2.3), (9.9, 7.3), (10.8, 7.3)], lbl='yes', lpos=(9.0, 2.45))
link(ax, [(8.7, 0.6), (9.9, 0.6), (9.9, 2.3)])
link(ax, [(12.6, 6.7), (12.6, 5.5)])
link(ax, [(12.6, 4.3), (12.6, 3.0)])
link(ax, [(14.4, 2.4), (17.8, 2.4), (17.8, 4.15)])
link(ax, [(16.1, 4.9), (14.4, 4.9)], lbl='no', lpos=(15.0, 5.05))
link(ax, [(17.8, 5.65), (17.8, 10.0), (13.1, 10.0)], c=RED, lbl='yes', lpos=(17.95, 7.5))
ax.text(0.3, 1.2, 'condition = polarization,\nphoton energy, angle range', fontsize=7.5, color=GRAY)
save(fig, 'fig2-16_automation')
json.dump(FACTS, open(f'{OUT}/facts_v2refl.json', 'w'), indent=1); print(FACTS)
