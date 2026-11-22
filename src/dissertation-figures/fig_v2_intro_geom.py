"""Revision 2. Fig. 1.2 (AR-NEXAFS and cos2 analysis), Fig. 2.1 (geometry), Fig. 2.2 (near and far field)."""
import json
from figlib import *
from matplotlib.patches import Rectangle, Circle, Arc, Ellipse, Polygon

FACTS = {}


def mol(ax, x, y, ang, L=0.5, lw=1.6, c=BLACK):
    dx, dy = L / 2 * np.cos(np.radians(ang)), L / 2 * np.sin(np.radians(ang))
    ax.plot([x - dx, x + dx], [y - dy, y + dy], color=c, lw=lw, solid_capstyle='round')


# =============================================================== Fig 1.2
bb, nx, mu = znpc_tables()
ths = sorted(nx.theta_deg.unique())
c2 = np.cos(np.radians(ths)) ** 2
win = {'pi': (283.6, 286.0), 'sigma': (291.0, 300.0)}
def area(lo, hi):
    out = []
    for th in ths:
        d = nx[nx.theta_deg == th]; m = (d.energy >= lo) & (d.energy <= hi)
        out.append(np.trapezoid((d.intensity_norm - d.dft_step)[m], d.energy[m]))
    return np.array(out)
fits = {}
for k, (lo, hi) in win.items():
    A = area(lo, hi)
    (b, a), cov = np.polyfit(c2, A, 1, cov=True)
    rng = np.random.default_rng(0)
    draws = rng.multivariate_normal([b, a], cov, 4000)
    if k == 'pi':   # vector orbital, I = A[1 + 1/2 (3cos2t - 1)(3cos2a - 1)]
        P2 = draws[:, 0] / (3 * draws[:, 1] + draws[:, 0])
        ang = np.degrees(np.arccos(np.sqrt(np.clip((2 * P2 + 1) / 3, 0, 1))))
    else:           # plane orbital, I = A[1 - 1/4 (3cos2t - 1)(3cos2g - 1)]
        u = -4 * draws[:, 0] / (3 * draws[:, 1] + draws[:, 0])
        ang = np.degrees(np.arccos(np.sqrt(np.clip((1 + u) / 3, 0, 1))))
    fits[k] = dict(A=A, a=a, b=b, ang=float(np.median(ang)), dang=float(np.std(ang)))
FACTS['fig1_2'] = {k: dict(ang=v['ang'], dang=v['dang']) for k, v in fits.items()}

fig = plt.figure(figsize=(6.5, 5.6))
gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.05], hspace=0.38, wspace=0.34, left=0.1, right=0.99, top=0.97, bottom=0.08)
# a energy levels and states
a = fig.add_subplot(gs[0, 0]); blank(a); a.set_xlim(0, 10); a.set_ylim(-0.3, 6.3)
a.plot([0.8, 0.8], [0.3, 5.7], color=BLACK, lw=0.8); a.text(0.35, 3.0, 'energy', rotation=90, va='center', fontsize=7.5)
for y in (5.05, 4.6, 3.8):
    a.plot([1.6, 3.4], [y, y], color=BLACK, lw=1.6)
a.text(3.55, 4.82, r'$\pi^*$', va='center', fontsize=8); a.text(3.55, 3.8, r'$\sigma^*$', va='center', fontsize=8)
a.plot([1.6, 3.4], [0.6, 0.6], color=BLACK, lw=2.2); a.text(3.55, 0.6, 'C 1s', va='center', fontsize=8)
arrow(a, 2.5, 0.7, 2.5, 4.55, color=RED, lw=2)
a.text(2.35, 2.5, r'$h\nu$', fontsize=8.5, color=RED, ha='right')
# orbitals sketch, localized 1s and delocalized pi*
xs_ = np.linspace(5.0, 9.4, 6)
a.plot(xs_, np.full_like(xs_, 2.7), color=BLACK, lw=1.3)
a.plot(xs_, np.full_like(xs_, 2.7), 'o', ms=5, mfc='white', mec=BLACK)
for k, x in enumerate(xs_):
    up = k % 2 == 0
    a.add_patch(Ellipse((x, 3.35), 0.45, 1.0, fc=RED if up else 'white', ec=RED, lw=1, alpha=0.9))
    a.add_patch(Ellipse((x, 2.05), 0.45, 1.0, fc='white' if up else RED, ec=RED, lw=1, alpha=0.9))
a.add_patch(Circle((xs_[1], 2.7), 0.13, fc=BLACK, zorder=5))
a.text(xs_[1] + 0.2, 0.15, 'C 1s on one atom', ha='left', fontsize=7)
a.annotate('', xy=(xs_[1], 2.55), xytext=(xs_[1], 0.4), arrowprops=dict(arrowstyle='-|>', lw=0.9, color=BLACK))
a.text(6.9, 4.3, r'$\pi^*$ over the ring', ha='center', fontsize=7, color=RED)
arrow(a, 9.85, 2.7, 9.85, 4.6, color=RED, lw=1.6); a.text(9.65, 4.75, r'$\mu$', fontsize=8.5, color=RED)
# b geometry, uniaxial edge-on film, E at theta from normal
b = fig.add_subplot(gs[0, 1]); blank(b); b.set_xlim(0, 10); b.set_ylim(0, 6.3)
b.add_patch(Rectangle((0.5, 0.5), 9, 0.5, fc=LGRAY, ec=BLACK))
for x in np.arange(1.0, 9.2, 0.55):
    for y in (1.45, 2.15):
        mol(b, x, y, 74 if (x * 3) % 2 < 1 else 106, L=0.55, lw=1.4)
arrow(b, 5.0, 2.6, 5.0, 5.9, color=BLACK, lw=1.2); b.text(5.15, 5.75, r'$\hat{n}$', fontsize=8.5)
E = np.array([np.sin(np.radians(40)), np.cos(np.radians(40))]) * 3.0
arrow(b, 5.0, 2.6, 5.0 + E[0], 2.6 + E[1], color=RED, lw=2.2); b.text(5.1 + E[0], 2.7 + E[1], r'$\mathbf{E}$', fontsize=9.5, color=RED)
b.add_patch(Arc((5.0, 2.6), 2.4, 2.4, theta1=50, theta2=90, color=RED, lw=1.1)); b.text(5.35, 4.05, 'θ', fontsize=8.5, color=RED)
# zoom: one molecule with its TDMs and tilt
mol(b, 1.9, 4.4, 90 + (90 - 74), L=1.6, lw=3.5)  # molecular plane normal to mu
tdm = np.array([np.sin(np.radians(74)), np.cos(np.radians(74))])
arrow(b, 1.9, 4.4, 1.9 + 1.4 * tdm[0], 4.4 + 1.4 * tdm[1], color=RED, lw=1.8)
b.text(1.9 + 1.5 * tdm[0], 4.55 + 1.4 * tdm[1], r'$\mu_{\pi^*}$', fontsize=8.5, color=RED)
b.plot([1.9, 1.9], [4.4, 5.9], color=GRAY, lw=0.8, ls=':')
b.add_patch(Arc((1.9, 4.4), 1.4, 1.4, theta1=16, theta2=90, color=BLACK, lw=1)); b.text(2.15, 5.25, 'α', fontsize=8.5)
b.text(0.6, 3.15, 'edge-on ZnPc film', fontsize=7.5, color=GRAY)
# c spectra
c = fig.add_subplot(gs[1, 0])
cols = {20: RED, 40: '#E6706C', 54.7: GRAY, 70: '#555555', 90: BLACK}
for th in ths:
    d = nx[nx.theta_deg == th]
    c.plot(d.energy, d.intensity_norm / 1e3, color=cols[th], lw=1.3, label=f'{th:g}°')
for k, (lo, hi) in win.items():
    c.axvspan(lo, hi, color=LRED if k == 'pi' else LGRAY, alpha=0.45, lw=0)
c.text(284.8, 152, r'$\pi^*$', ha='center', fontsize=8.5, color=RED); c.text(295.5, 152, r'$\sigma^*$', ha='center', fontsize=8.5)
c.set_xlim(280, 320); c.set_ylim(0, 162)
c.set_xlabel('Photon energy (eV)'); c.set_ylabel(r'$\mu_m$ ($10^3$ cm$^2$ g$^{-1}$)')
c.legend(title='θ', fontsize=7.5, title_fontsize=7.5, loc='upper right')
# d cos2 fits
dd = fig.add_subplot(gs[1, 1])
xx = np.linspace(0, 1, 50)
for k, col, mk in (('pi', RED, 'o'), ('sigma', BLACK, 's')):
    f_ = fits[k]
    dd.plot(c2, f_['A'] / 1e3, mk, color=col, ms=6, mfc='white' if k == 'sigma' else col)
    dd.plot(xx, (f_['a'] + f_['b'] * xx) / 1e3, color=col, lw=1.4)
dd.text(0.42, 0.04, rf"$\pi^*$, vector orbital, $\alpha$ = {fits['pi']['ang']:.1f} ± {fits['pi']['dang']:.1f}°",
        transform=dd.transAxes, color=RED, fontsize=8, ha='center')
dd.text(0.42, 0.92, rf"$\sigma^*$, plane orbital, $\gamma$ = {fits['sigma']['ang']:.1f} ± {fits['sigma']['dang']:.1f}°",
        transform=dd.transAxes, color=BLACK, fontsize=8, ha='center')
dd.set_xlabel(r'$\cos^2\theta$'); dd.set_ylabel(r'Integrated intensity ($10^3$ eV cm$^2$ g$^{-1}$)')
dd.set_xlim(-0.03, 0.95)
top = dd.secondary_xaxis('top', functions=(lambda x: np.degrees(np.arccos(np.sqrt(np.clip(x, 0, 1)))),
                                           lambda t: np.cos(np.radians(t)) ** 2))
top.set_xticks([90, 70, 54.7, 40, 20]); top.set_xticklabels(['90', '70', '54.7', '40', '20']); top.set_xlabel('θ (°)', fontsize=8)
grid_labels(fig, [[(a, 'a'), (b, 'b')], [(c, 'c'), (dd, 'd')]])
save(fig, 'fig1-02_ar-nexafs')

# =============================================================== Fig 2.1
fig = plt.figure(figsize=(6.5, 2.5))
a = fig.add_axes([0.0, 0.04, 0.5, 0.9]); blank(a); a.set_xlim(0, 10.5); a.set_ylim(0, 5.5); a.set_aspect('equal', adjustable='box')
for x in (0.5, 0.9, 1.3, 1.7):
    a.plot([x, x], [1.3, 4.3], color=BLACK, lw=1.2)
a.text(1.0, 4.6, r'$\mathbf{k}$', fontsize=9.5)
a.add_patch(Circle((3.4, 2.8), 0.62, fc='#7F7F7F', ec=BLACK))
arrow(a, 0.15, 2.8, 2.75, 2.8)
for k, r_ in enumerate((0.95, 1.35, 1.75, 2.15)):   # distorted near-field fronts
    th_ = np.linspace(-1.0, 1.0, 80)
    rr = r_ * (1 + 0.06 * np.cos(5 * th_ + k))
    a.plot(3.4 + rr * np.cos(th_), 2.8 + 1.25 * rr * np.sin(th_), color=BLACK, lw=1.0)
a.text(5.0, 5.0, 'near field', fontsize=7, color=GRAY, ha='left')
a.plot([3.4, 9.3], [2.8, 2.8], color=GRAY, lw=0.8, ls='--')
arrow(a, 3.4, 2.8, 9.2, 4.3)
a.add_patch(Arc((3.4, 2.8), 3.6, 3.6, theta1=0, theta2=14.5, color=BLACK, lw=1)); a.text(5.3, 2.95, '2θ', fontsize=8.5)
a.text(7.8, 4.25, r"$\mathbf{k}'$", fontsize=9.5)
arrow(a, 3.4, 2.8, 2.85, 4.2, color=RED, lw=1.8)
a.text(1.7, 4.95, r"$\mathbf{q}=\mathbf{k}'-\mathbf{k}$", fontsize=8, color=RED)
a.plot([9.4, 9.4], [0.5, 5.1], color=BLACK, lw=1.8)
yy = np.linspace(0.6, 5.0, 400)
prof = np.sinc((yy - 2.8) * 1.6) ** 2
a.plot(9.4 + 0.95 * prof, yy, color=RED, lw=1.4)
a.text(9.5, 0.2, 'far field', fontsize=7.5, color=GRAY)
a.text(6.6, 0.35, r'$|\mathbf{q}|=\frac{4\pi}{\lambda}\sin\theta$', fontsize=9, ha='center')
b = fig.add_axes([0.52, 0.04, 0.46, 0.9]); blank(b); b.set_xlim(0, 10); b.set_ylim(-1.3, 5.5)
b.add_patch(Rectangle((0.5, 0.5), 9, 1.1, fc=LGRAY, ec=BLACK))
b.add_patch(Rectangle((0.5, 1.6), 9, 0.8, fc='white', ec=BLACK))
b.text(9.3, 2.0, 'film', ha='right', va='center', fontsize=7.5, color=GRAY)
b.text(9.3, 1.05, 'substrate', ha='right', va='center', fontsize=7.5, color=GRAY)
arrow(b, 1.3, 4.9, 5.0, 2.4); arrow(b, 5.0, 2.4, 8.7, 4.9)
b.text(2.2, 4.0, r'$\mathbf{k}_i$', fontsize=9.5); b.text(7.7, 4.0, r'$\mathbf{k}_f$', fontsize=9.5)
b.add_patch(Arc((5.0, 2.4), 2.6, 2.6, theta1=146, theta2=180, color=BLACK, lw=1))
b.add_patch(Arc((5.0, 2.4), 2.6, 2.6, theta1=0, theta2=34, color=BLACK, lw=1))
b.text(3.3, 2.55, 'θ', fontsize=8.5); b.text(6.55, 2.55, 'θ', fontsize=8.5)
arrow(b, 5.0, 2.4, 5.0, 4.9, color=RED, lw=1.8)
b.text(5.2, 4.6, r'$q_z=\frac{4\pi}{\lambda}\sin\theta$', fontsize=8.5, color=RED)
b.text(5.0, 0.25, 's, E normal to the plane of incidence\np, E in the plane of incidence', fontsize=7, color=GRAY, va='top', ha='center')
grid_labels(fig, [[(a, 'a'), (b, 'b')]], dy=-0.06)
save(fig, 'fig2-01_scattering-geometry')

# =============================================================== Fig 2.2
# Total scattered field of a few disordered scatterers, with multiple scattering between them (Foldy-Lax,
# 2D scalar), its wavefronts flattening with distance, and the far-field intensity on the detector.
from scipy.special import hankel1, j1
from scipy.ndimage import gaussian_filter1d
LAMD = 1.05; kk = 2 * np.pi / LAMD; A_R = 0.24; ALPHA = 1.2
pts = np.array([[3.15, 3.35], [4.75, 2.35], [5.35, 4.4], [6.4, 3.05], [3.55, 1.55]])
Gf = lambda r: 0.25j * hankel1(0, kk * r)
N = len(pts)
M = np.eye(N, dtype=complex)
for i in range(N):
    for j in range(N):
        if i != j:
            M[i, j] = -ALPHA * Gf(np.hypot(*(pts[i] - pts[j])))
psi = np.linalg.solve(M, np.exp(1j * kk * pts[:, 0]))  # exciting field at each scatterer, neighbours included
XL, XR = 1.4, 14.2
xg = np.linspace(XL, XR, 1300); yg = np.linspace(0.0, 6.0, 560)
X, Y = np.meshgrid(xg, yg)
Ssc = np.zeros_like(X, dtype=complex)
for p, ps in zip(pts, psi):
    Ssc += ALPHA * ps * Gf(np.hypot(X - p[0], Y - p[1]))
ctr = pts.mean(0)
Rg = np.hypot(X - ctr[0], Y - ctr[1])
Fw = Ssc * np.sqrt(np.maximum(Rg, 0.3))
amp = np.abs(Fw); ref = np.percentile(amp[Rg > 3], 60)
ph = np.where(amp > 0.35 * ref, np.angle(Fw), np.nan)
for p in pts:
    ph[np.hypot(X - p[0], Y - p[1]) < A_R + 0.06] = np.nan
fig, ax = plt.subplots(figsize=(6.5, 1.95)); fig.subplots_adjust(0, 0, 1, 1); blank(ax)
ax.set_xlim(-0.2, 23.6); ax.set_ylim(-1.0, 6.3); ax.set_aspect('equal')
# crests of the total scattered field, fading with distance
for x0_, x1_, al in ((XL, 9.0, 0.85), (9.0, 11.6, 0.5), (11.6, XR, 0.22)):
    m = (X >= x0_) & (X <= x1_)
    ax.contour(X, Y, np.where(m, ph, np.nan), levels=[0.0], colors=[BLACK], linewidths=0.6, alpha=al)
# incident plane wave and k
for x in np.arange(0.0, 1.25, LAMD / 2):
    ax.plot([x, x], [1.2, 4.8], color=BLACK, lw=0.9)
# incident k from I0 onto the front scatterer, and the forward-scattered k_s that illuminates the one ahead of it
p1, p2 = pts[0], pts[2]
ax.annotate('', xy=(p1[0] - A_R - 0.05, p1[1]), xytext=(-0.1, p1[1]),
            arrowprops=dict(arrowstyle='-|>,head_width=0.25,head_length=0.45', color=RED, lw=1.5, shrinkA=0, shrinkB=0), zorder=6)
ax.annotate('', xy=(p2[0] - A_R - 0.05, p2[1]), xytext=(-0.1, p2[1]),
            arrowprops=dict(arrowstyle='-|>,head_width=0.25,head_length=0.45', color=RED, lw=1.5, shrinkA=0, shrinkB=0), zorder=6)
ax.text(0.15, p2[1] + 0.12, r'$\mathbf{k}$, $I_0$', fontsize=7.5, va='bottom', bbox=dict(fc='white', ec='none', pad=0.4), zorder=7)
ax.text(0.15, p1[1] - 0.12, r'$\mathbf{k}$, $I_0$', fontsize=7.5, va='top', bbox=dict(fc='white', ec='none', pad=0.4), zorder=7)
u = (p2 - p1) / np.hypot(*(p2 - p1))
ax.annotate('', xy=p2 - u * (A_R + 0.05), xytext=p1 + u * (A_R + 0.02),
            arrowprops=dict(arrowstyle='-|>,head_width=0.25,head_length=0.45', color=RED, lw=1.5, shrinkA=0, shrinkB=0), zorder=6)
mm = (p1 + p2) / 2
ax.text(p1[0] + 0.45, p1[1] - 0.05, r'$\mathbf{k}_s$, secondary', fontsize=7, ha='left', va='top',
        bbox=dict(fc='white', ec='none', pad=0.4), zorder=7)
for p in pts:
    ax.add_patch(Circle(p, A_R, fc='#7F7F7F', ec=BLACK, lw=0.8, zorder=5))
# scatterer size a and spacing d
p0 = pts[4]
yb_ = p0[1] - 0.55
ax.annotate('', xy=(p0[0] - A_R, yb_), xytext=(p0[0] + A_R, yb_),
            arrowprops=dict(arrowstyle='<->', lw=0.8, shrinkA=0, shrinkB=0), zorder=6)
ax.plot([p0[0] - A_R] * 2, [yb_ - 0.1, p0[1]], color=BLACK, lw=0.5, zorder=6); ax.plot([p0[0] + A_R] * 2, [yb_ - 0.1, p0[1]], color=BLACK, lw=0.5, zorder=6)
ax.text(p0[0], yb_ - 0.12, r'$a$', fontsize=8, ha='center', va='top', bbox=dict(fc='white', ec='none', pad=0.5), zorder=7)
pa, pb = pts[1], pts[3]
ax.annotate('', xy=pa, xytext=pb, arrowprops=dict(arrowstyle='<->', lw=0.9, shrinkA=4, shrinkB=4), zorder=6)
mid = (pa + pb) / 2
ax.text(mid[0] + 0.05, mid[1] - 0.45, r'$d$', fontsize=8, ha='center', bbox=dict(fc='white', ec='none', pad=0.5), zorder=7)
# scattered direction k' to the detector
XD = 20.0
phi0 = 0.11
src = p2  # the deeper scatterer, driven by I0 and by its neighbour, radiates toward the detector
ax.annotate('', xy=(src[0] + 8.6 * np.cos(phi0), src[1] + 8.6 * np.sin(phi0)), xytext=src + 0.26 * np.array([np.cos(phi0), np.sin(phi0)]),
            arrowprops=dict(arrowstyle='-|>,head_width=0.25,head_length=0.45', color=RED, lw=1.5, shrinkA=0, shrinkB=0), zorder=6)
ax.text(src[0] + 8.75 * np.cos(phi0), src[1] + 8.6 * np.sin(phi0), r"$\mathbf{k}'$", fontsize=8, va='center',
        bbox=dict(fc='white', ec='none', pad=0.5), zorder=7)
ax.plot([src[0] + 0.26, src[0] + 5.0], [src[1], src[1]], color=GRAY, lw=0.7, ls='--', zorder=6)
ax.add_patch(Arc(src, 8.4, 8.4, theta1=0, theta2=np.degrees(phi0), color=BLACK, lw=0.8, zorder=6))
ax.text(src[0] + 4.3, src[1] + 0.08, r'$2\theta$', fontsize=7.5, zorder=7, va='center', bbox=dict(fc='white', ec='none', pad=0.3))
# distance to the detector, broken because L is far larger than the cluster
ax.annotate('', xy=(ctr[0], -0.55), xytext=(XD, -0.55), arrowprops=dict(arrowstyle='<->', lw=0.9, shrinkA=0, shrinkB=0))
ax.plot([ctr[0]] * 2, [-0.75, 0.6], color=GRAY, lw=0.5, ls=':')
for xb in (15.6, 15.9):
    ax.plot([xb - 0.12, xb + 0.12], [-0.85, -0.25], color=BLACK, lw=0.9)
ax.add_patch(Rectangle((15.62, -0.62), 0.26, 0.14, fc='white', ec='none', zorder=3))
ax.text(11.0, -0.45, r'$L \gg d,\ a$', fontsize=7.5, ha='center', va='bottom', bbox=dict(fc='white', ec='none', pad=0.5))
# detector and the far-field intensity computed from the same scatterers
ax.plot([XD, XD], [0.0, 6.0], color=BLACK, lw=1.6)
from scipy.special import j0
yy = np.linspace(0.02, 5.98, 2000)
phi = (yy - 3.0) / 3.0 * 1.6
qn = 2 * kk * np.abs(np.sin(phi / 2)) + 1e-9
ff = (2 * j1(qn * A_R) / (qn * A_R)) ** 2
rij = np.hypot(*(pts[:, None, :] - pts[None, :, :]).transpose(2, 0, 1)).ravel()
Sq = np.array([np.sum(j0(q_ * rij)) for q_ in qn]) / N  # orientation-averaged structure factor
I = ff * np.clip(Sq, 1e-3, None)
w = I / I.max()
ax.plot(XD + 0.12 + 2.4 * w, yy, color=RED, lw=1.3)
ax.text(XD + 1.0, 0.15, r'$I(2\theta)$', fontsize=7, color=RED, ha='left', va='bottom')
ax.text(XD + 0.4, 6.1, 'far field', ha='left', va='bottom', fontsize=7, color=GRAY)
ax.text(5.0, 6.1, 'near field, neighbours rescatter', ha='center', va='bottom', fontsize=7, color=GRAY)
ax.text(12.0, 6.1, 'propagation', ha='center', va='bottom', fontsize=7, color=GRAY)
FACTS['fig2_2'] = dict(n_scatterers=int(N), lambda_drawn=LAMD, a=A_R, alpha=ALPHA)
save(fig, 'fig2-02_near-far-field')
json.dump(FACTS, open(f'{OUT}/facts_v2a.json', 'w'), indent=1)
print(FACTS)
