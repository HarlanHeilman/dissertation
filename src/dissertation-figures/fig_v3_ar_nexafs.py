"""Revision 3 of Fig. 1.2. Single row. Ring schematic, AR-NEXAFS with cDFT cluster decomposition,
per-cluster amplitude against theta, and the effective TDM angle of each cluster."""
import json
from figlib import *
from figlib import _gauss
from matplotlib.patches import Ellipse, Circle, Polygon
from matplotlib.colors import LinearSegmentedColormap
from scipy.optimize import nnls

E_LO, E_HI = 283.5, 300.0
bb, nx, _ = znpc_tables()
ths = np.array(sorted(nx.theta_deg.unique()))
c2 = np.cos(np.radians(ths)) ** 2
keep = bb[bb.location <= E_HI].index.values          # clusters centered in the window

# per-angle non-negative amplitudes of every cluster, widths and centers fixed at the refined building block
amps, fitcurves = [], {}
for th in ths:
    d = nx[(nx.theta_deg == th) & (nx.energy >= E_LO) & (nx.energy <= E_HI)]
    E = d.energy.values
    G = np.stack([_gauss(E, r.location, r.sigma_ev) for r in bb.itertuples()], 1)
    x, _r = nnls(G, (d.intensity_norm - d.dft_step).values)
    amps.append(x)
    fitcurves[th] = (E, d.intensity_norm.values, d.dft_step.values, G * x)
amps = np.array(amps)

# vector-orbital form, I = A0 [1 + 1/2 (3cos2t - 1)(3cos2a - 1)], linear in cos2(theta)
rng = np.random.default_rng(0)
res = []
for k in keep:
    (b1, a1), cov = np.polyfit(c2, amps[:, k], 1, cov=True)
    dr = rng.multivariate_normal([b1, a1], cov, 4000)
    xx, zz = dr[:, 1], dr[:, 1] + dr[:, 0]
    al = np.degrees(np.arctan(np.sqrt(np.clip(2 * xx / zz, 0, None))))
    A0 = a1 + b1 / 3
    res.append(dict(k=int(k), E=float(bb.location[k]), A0=A0, alpha=float(np.median(al)), dalpha=float(np.std(al))))
FACTS = {'fig1_2_v3': res}
json.dump(FACTS, open(f'{OUT}/facts_fig12_v3.json', 'w'), indent=1)

cmap = LinearSegmentedColormap.from_list('cl', [RED, '#8E1512', '#2B0605'])
Es = np.array([r['E'] for r in res])
col = {r['k']: cmap((r['E'] - Es.min()) / (Es.max() - Es.min())) for r in res}
tcol = {20: '#B8B8B8', 40: '#8F8F8F', 54.7: '#666666', 70: '#3A3A3A', 90: BLACK}

SHOW = [284.22, 285.06, 287.07, 288.87, 293.50, 298.52]
sel = [r for r in res if any(abs(r['E'] - e) < 0.02 for e in SHOW)]
scol = dict(zip([r['k'] for r in sel], [RED, '#8E1512', '#EE8A86', '#A8A8A8', '#5E5E5E', BLACK]))
fig = plt.figure(figsize=(6.2, 2.35))
gs = fig.add_gridspec(1, 3, width_ratios=[2.05, 2.2, 1.55], wspace=0.38, left=0.0, right=0.995, top=0.9, bottom=0.2)

# ---------------------------------------------------------------- a  energy ladder and conjugated ring
a = fig.add_subplot(gs[0]); blank(a); a.set_xlim(0, 20); a.set_ylim(0, 15); a.set_aspect('equal')
# ladder
arrow(a, 0.9, 1.0, 0.9, 14.2, color=BLACK, lw=0.9, hw=5)
a.text(0.35, 14.2, '$E$', fontsize=8.5, ha='right', va='center')
a.plot([1.8, 4.6], [2.2, 2.2], color=BLACK, lw=2.4, solid_capstyle='butt')
a.plot([1.8, 4.6], [10.6, 10.6], color=BLACK, lw=1.4, solid_capstyle='butt')
a.plot([1.8, 4.6], [12.6, 12.6], color=BLACK, lw=1.4, solid_capstyle='butt')
a.text(5.0, 2.2, 'C 1s', fontsize=7.5, va='center')
a.text(5.0, 10.6, r'$\pi^*$', fontsize=8.5, va='center', color=RED)
a.text(5.0, 12.6, r'$\sigma^*$', fontsize=8.5, va='center')
arrow(a, 3.2, 2.45, 3.2, 10.35, color=RED, lw=2.0, hw=7)
a.text(2.85, 6.4, r'$h\nu$', fontsize=8.5, color=RED, ha='right', va='center')
# ring in perspective with p orbitals normal to it
cx, cy, rx, ry = 13.4, 6.4, 4.6, 1.7
phi = np.radians(np.arange(0, 360, 60))
vx, vy = cx + rx * np.cos(phi), cy + ry * np.sin(phi)
t = np.linspace(-np.pi / 2, np.pi / 2, 80)
L, Wd = 2.1, 0.8


def lobe(x0, y0, sgn, fc, z):
    r = L * np.cos(t) ** 2
    xs, ys = x0 + Wd * r * np.sin(t), y0 + sgn * r * np.cos(t)
    a.add_patch(Polygon(np.c_[xs, ys], closed=True, fc=fc, ec=RED, lw=0.9, zorder=z))


def p_orbital(i, z):
    lobe(vx[i], vy[i], +1, RED, z)
    lobe(vx[i], vy[i], -1, 'white', z)


back = [i for i in np.argsort(-vy) if vy[i] > cy]
front = [i for i in np.argsort(-vy) if vy[i] <= cy]
for i in back:
    p_orbital(i, 1)
a.add_patch(Polygon(np.c_[vx, vy], closed=True, fill=False, ec=BLACK, lw=1.5, zorder=2))
a.add_patch(Ellipse((cx, cy), 2 * rx * 0.6, 2 * ry * 0.6, fill=False, ec=BLACK, lw=0.8, zorder=2))
arrow(a, cx, cy, cx, 14.3, color=RED, lw=2.4, hw=8)
a.text(cx + 0.6, 13.7, r'$\boldsymbol{\mu}$', fontsize=10.5, color=RED, va='center')
for i in front:
    p_orbital(i, 4)
for i in range(6):
    a.add_patch(Circle((vx[i], vy[i]), 0.22, fc=BLACK, zorder=5 if vy[i] <= cy else 2.5))

# ---------------------------------------------------------------- b  AR-NEXAFS and cluster decomposition
b = fig.add_subplot(gs[1])
for th in ths:
    E, y, step, comp = fitcurves[th]
    b.plot(E[::2], y[::2] / 1e3, 'o', ms=1.8, color=tcol[th], mew=0)
    b.plot(E, (step + comp.sum(1)) / 1e3, color=tcol[th], lw=1.0, label=(f'θ = {th:g}°' if th == ths[0] else f'{th:g}°'))
b.set_xlim(E_LO, E_HI); b.set_ylim(0, 122)
for r in sel:
    b.plot(r['E'], 116, 'v', ms=4.5, color=scol[r['k']], mec=BLACK if scol[r['k']] in ('#EE8A86', '#A8A8A8') else scol[r['k']], mew=0.4, clip_on=False)
    b.axvline(r['E'], ymin=0, ymax=0.93, color=scol[r['k']], lw=0.6, ls=':', zorder=0)
b.set_xlabel('Photon energy (eV)'); b.set_ylabel(r'$\mu_m$ ($10^3$ cm$^2$ g$^{-1}$)')
leg = b.legend(fontsize=6.3, loc='lower right', ncol=1, handlelength=1.1, handletextpad=0.4, labelspacing=0.2, borderaxespad=0.3, frameon=True, facecolor='white', edgecolor='none', framealpha=1)
leg.set_zorder(5)

# ---------------------------------------------------------------- c  amplitude against theta, main transitions
c = fig.add_subplot(gs[2])
tt = np.linspace(15, 90, 200)
ends = []
for r in sel:
    al = np.radians(r['alpha'])
    model = 1 + 0.5 * (3 * np.cos(np.radians(tt)) ** 2 - 1) * (3 * np.cos(al) ** 2 - 1)
    c.plot(tt, model, color=scol[r['k']], lw=1.1, label=f"{r['E']:.1f} eV")
    c.plot(ths, amps[:, r['k']] / r['A0'], 'o', ms=3.0, color=scol[r['k']], mew=0)
    ends.append([model[-1], r])
ends.sort(key=lambda e: e[0])
ys = [e[0] for e in ends]
for i in range(1, len(ys)):                         # keep labels apart
    ys[i] = max(ys[i], ys[i - 1] + 0.075)
for (y0, r), yl in zip(ends, ys):
    c.annotate(f"{r['alpha']:.1f}°", xy=(90, y0), xytext=(93.0, yl), textcoords='data',
               fontsize=6.3, color=scol[r['k']], va='center', ha='left', annotation_clip=False,
               arrowprops=dict(arrowstyle='-', lw=0.5, color=scol[r['k']], shrinkA=0, shrinkB=1))
c.axvline(54.7, color=GRAY, lw=0.6, ls=':')
c.set_xlim(15, 90); c.set_xticks([20, 40, 54.7, 70, 90]); c.set_xticklabels(['20', '40', '54.7', '70', '90'])
c.set_ylim(0.25, 1.5); c.set_xlabel('θ (°)'); c.set_ylabel(r'Amplitude / $A_0$')
c.text(1.0, 1.03, r'$\alpha$', transform=c.transAxes, fontsize=8, ha='left', va='bottom', color=GRAY)
c.legend(fontsize=6.2, loc='lower right', handlelength=1.1, borderaxespad=0.2, labelspacing=0.25)

for ax, s, x in ((a, 'a', 0.0), (b, 'b', -0.16), (c, 'c', -0.3)):
    label(ax, s, x=x, y=1.02)
save(fig, 'fig1-02_ar-nexafs')
for r in res:
    print(f"{r['k']:2d} {r['E']:.2f} alpha {r['alpha']:.1f} +- {r['dalpha']:.1f}")
