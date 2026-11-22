"""Revision 3, Fig. 2.7, panel d adds a forward-model fit of the rocking scan.
Revision 2, Fig. 2.7. Finite beam and finite photodiode alignment, ray-traced traces with sparse points."""
import json
from figlib import *
from matplotlib.patches import Rectangle, Polygon
from scipy.optimize import curve_fit

rng = np.random.default_rng(4)
SIGB = 0.04            # beam rms height (mm)
ELL = 10.0             # sample length (mm)
D = 150.0              # rotation axis to photodiode (mm)
HD = 1.5               # photodiode half height (mm)
NR = 200000
Y = rng.normal(0, SIGB, NR)
DIV = rng.normal(0, 1.0e-3, NR)   # beam divergence (rad)


def signal(zs, th_deg, yd=0.0):
    t = np.tan(np.radians(th_deg))
    if abs(t) < 1e-12:
        passing = Y > zs; refl = np.zeros_like(Y, bool); xh = np.zeros_like(Y)
    elif t > 0:
        lo, hi = zs - ELL / 2 * t, zs + ELL / 2 * t
        passing = Y > hi; refl = (Y >= lo) & (Y <= hi); xh = (Y - zs) / t
    else:
        front = zs + ELL / 2 * abs(t)
        passing = Y > front; refl = np.zeros_like(Y, bool); xh = np.zeros_like(Y)
    y_pass = Y + DIV * D
    y_ref = Y + np.tan(2 * np.radians(th_deg)) * (D - xh) + DIV * D
    hit = (passing & (np.abs(y_pass - yd) < HD)) | (refl & (np.abs(y_ref - yd) < HD))
    return hit.mean()


def sparse(xs, f, n0=4000):
    lam = np.array([f(x) for x in xs]) * n0
    return rng.poisson(lam) / n0


FACTS = {}
fig = plt.figure(figsize=(6.5, 7.4))
gs = fig.add_gridspec(3, 2, width_ratios=[1.45, 1], hspace=0.45, wspace=0.32, left=0.02, right=0.98, top=0.97, bottom=0.07)
PANELS = []


def beam(ax, x0, x1, yc, h, color=RED):
    for k, al in zip(np.linspace(1, 0.25, 4), (0.18, 0.18, 0.18, 0.18)):
        ax.add_patch(Rectangle((x0, yc - h * k), x1 - x0, 2 * h * k, fc=color, ec='none', alpha=al))
    ax.plot([x0, x1], [yc, yc], color=color, lw=0.8, ls=':')


def tilted_scene(ax, yc, h, cx, cy, half, thick, ang, xd, x0=0.2, show_pass=True, show_block=True):
    """Finite beam on a rigid, rotated rectangular sample. Returns the reflected band at the diode plane."""
    a_ = np.radians(ang); t_ = np.tan(a_); t2 = np.tan(2 * a_)
    ca, sa = np.cos(a_), np.sin(a_)
    xl, yl = cx - half * ca, cy - half * sa
    xr, yr = cx + half * ca, cy + half * sa
    corners = [(xl, yl), (xr, yr), (xr + thick * sa, yr - thick * ca), (xl + thick * sa, yl - thick * ca)]
    ax.add_patch(Polygon(corners, fc=LGRAY, ec=BLACK, lw=1.0, zorder=3))
    lo, hi = yc - h, yc + h
    y0, y1 = max(lo, yl), min(hi, yr)
    xh = lambda y: cx + (y - cy) / t_
    yd = lambda y: y + t2 * (xd - xh(y))
    if show_block and lo < yl:  # stopped by the leading face
        yb = np.linspace(lo, yl, 20)
        xf = xl + (yl - yb) * t_
        ax.add_patch(Polygon([(x0, lo)] + list(zip(xf, yb)) + [(x0, yl)], fc=RED, alpha=0.12, ec='none', zorder=1))
    if show_pass and hi > yr:  # passes over the sample
        ax.add_patch(Polygon([(x0, max(lo, yr)), (xd, max(lo, yr)), (xd, hi), (x0, hi)], fc=RED, alpha=0.22, ec='none', zorder=1))
    if y1 > y0:  # strikes the surface and reflects
        ax.add_patch(Polygon([(x0, y0), (xh(y0), y0), (xh(y1), y1), (x0, y1)], fc=RED, alpha=0.45, ec='none', zorder=2))
        ax.add_patch(Polygon([(xh(y0), y0), (xh(y1), y1), (xd, yd(y1)), (xd, yd(y0))], fc=RED, alpha=0.55, ec='none', zorder=4))
        for y_ in np.linspace(y0, y1, 4)[1:-1]:
            ax.plot([x0, xh(y_), xd], [y_, y_, yd(y_)], color=RED, lw=0.6, zorder=5)
        for y_ in (y0, y1):
            ax.plot([x0, xh(y_), xd], [y_, y_, yd(y_)], color=RED, lw=0.9, zorder=5)
    xend = xh(yc) if yl <= yc <= yr else (xl + (yl - yc) * t_ if yc < yl else xd)
    ax.plot([x0, xend], [yc, yc], color=RED, lw=0.6, ls=':', zorder=2)
    return dict(xr=xr, yr=yr, xl=xl, yl=yl, yd=(yd(y0), yd(y1)), band=(y0, y1))


def diode(ax, x, yc, h):
    ax.add_patch(Rectangle((x, yc - h), 0.35, 2 * h, fc=BLACK, ec=BLACK))
    ax.text(x + 0.17, yc - h - 0.35, 'photodiode', ha='center', va='top', fontsize=7.5, color=GRAY)


# ---------------- row 1, knife edge
a = fig.add_subplot(gs[0, 0]); blank(a); a.set_xlim(0, 12); a.set_ylim(-2.6, 2.6)
beam(a, 0.2, 10.3, 0.0, 0.5)
for zz, al in ((-1.6, 0.25), (-0.9, 0.45), (0.0, 1.0)):
    a.add_patch(Rectangle((3.0, zz - 1.2), 4.0, 1.2, fc=LGRAY if al == 1 else 'white', ec=BLACK, lw=1.0, alpha=al,
                          ls='-' if al == 1 else '--'))
arrow(a, 7.5, -2.0, 7.5, -0.2, color=BLACK, lw=1.3); a.text(7.7, -1.1, 'z', fontsize=9.5, style='italic')
a.add_patch(Rectangle((7.0, -0.5), 3.3, 0.5, fc='white', ec='none', alpha=0.85))
a.text(8.6, -0.25, 'blocked', fontsize=7, color=GRAY, ha='center', va='center')
diode(a, 10.4, 0.0, 1.1)
a.annotate('', xy=(0.6, -0.5), xytext=(0.6, 0.5), arrowprops=dict(arrowstyle='<->', lw=0.9))
a.text(0.75, 0.6, 'finite beam', fontsize=7.5, color=RED)
a.text(3.1, 1.5, 'sample raised through the beam at θ = 0', fontsize=7.5)
PANELS.append((a, 'a'))
b = fig.add_subplot(gs[0, 1])
zs = np.arange(-0.15, 0.1501, 0.025)
zf = np.linspace(-0.16, 0.16, 400)
y = sparse(zs, lambda z: signal(z, 0.0))
fe = lambda z, A, z0, s: 0.5 * A * (1 - erf((z - z0) / (np.sqrt(2) * s)))
p, cv = curve_fit(fe, zs, y, p0=[1, 0, 0.04])
b.plot(zf * 1e3, fe(zf, *p), color=RED, lw=1.4)
b.plot(zs * 1e3, y, 'o', color=BLACK, ms=3.5, mfc='white', mew=0.9)
b.axvline(p[1] * 1e3, color=RED, lw=0.8, ls='--')
b.set_xlabel('Sample height z (µm)'); b.set_ylabel('Photodiode signal')
b.text(0.97, 0.88, f'step 25 µm\n$z_0$ = {p[1]*1e3:.1f} ± {np.sqrt(cv[1,1])*1e3:.1f} µm', transform=b.transAxes,
       ha='right', fontsize=7.5, va='top')
FACTS['knife'] = dict(z0_um=float(p[1] * 1e3), dz0_um=float(np.sqrt(cv[1, 1]) * 1e3), step_um=25, sigma_um=float(p[2] * 1e3))
PANELS.append((b, 'b'))

# ---------------- row 2, rocking scan in the flat geometry
a = fig.add_subplot(gs[1, 0]); blank(a); a.set_xlim(0, 12); a.set_ylim(-2.6, 2.6)
ang = 4.0  # drawn exaggerated, just below the cliff so the reflection still lands on the diode
sc = tilted_scene(a, 0.0, 0.5, 4.6, 0.0, 2.6, 1.1, ang, 10.4)
a.text(1.0, -0.62, 'blocked by\nthe sample', fontsize=7, color=GRAY, ha='center', va='top')
# a larger tilt sends the reflection over the diode, the cliff in d
a.plot([sc['xr'], 10.4], [sc['yr'], 1.75], color=GRAY, lw=0.9, ls='--', zorder=5)
diode(a, 10.4, 0.0, 1.1)
a.text(8.85, -0.6, 'reflected onto\nthe diode', fontsize=7, color=RED, ha='center', va='top')
a.text(10.2, 2.2, 'larger tilt misses\nthe diode (cliff)', fontsize=7, color=GRAY, ha='right')
a.text(3.1, 1.55, 'rocking θ at fixed z$_0$, detector at 0°', fontsize=7.5)
PANELS.append((a, 'c'))
b = fig.add_subplot(gs[1, 1])
ts = np.arange(-0.6, 0.6001, 0.05)
tf = np.linspace(-0.6, 0.6, 900)
z0 = 0.0
y = sparse(ts, lambda th: signal(z0, th))
yf = np.array([signal(z0, th) for th in tf])
# forward-model fit of the sparse scan, with the height fixed at the knife-edge estimate
from rockfit import fit as rock_fit
z_knife = FACTS['knife']['z0_um'] * 1e-3
pr, er, chi2r, dofr, fr = rock_fit(ts, y, 4000, z_fixed=z_knife, free_hd=True)
pk, ek, chi2k, dofk, _ = rock_fit(ts, y, 4000, z_fixed=z_knife, free_hd=False)
b.plot(tf, yf, color=LGRAY, lw=1.0)
b.plot(tf, fr(tf, *pr), color=RED, lw=1.4)
b.plot(ts, y, 'o', color=BLACK, ms=3.5, mfc='white', mew=0.9)
half_max = yf.max() / 2
above = tf[yf >= half_max]
cen = (above.min() + above.max()) / 2
for xv in (above.min(), above.max()):
    b.plot([xv, xv], [half_max - 0.04, half_max + 0.04], color=GRAY, lw=1.2)
b.axhline(half_max, color=LGRAY, lw=0.8, ls=':')
b.axvline(cen, color=GRAY, lw=0.8, ls='--')
b.axvline(pr[1], color=RED, lw=0.8, ls='--')
b.text(0.03, 0.80, f'FWHM midpoint {cen:.2f}°', transform=b.transAxes, fontsize=7, va='top', color=GRAY,
       bbox=dict(fc='white', ec='none', pad=0.6))
b.text(0.03, 0.70, f'fit {pr[1]:.3f} ± {er[1]:.3f}°', transform=b.transAxes, fontsize=7,
       bbox=dict(fc='white', ec='none', pad=0.6),
       va='top', color=RED)
icl = int(np.argmin(np.diff(yf)))
b.annotate('cliff', xy=(tf[icl], yf[icl]), xytext=(tf[icl] + 0.1, yf[icl] + 0.12), fontsize=7.5, color=GRAY,
           arrowprops=dict(arrowstyle='-', color=GRAY, lw=0.7))
b.set_xlabel(r'Sample angle $\theta_s$ (°)'); b.set_ylabel('Photodiode signal')
b.text(0.03, 0.92, 'step 0.05°', transform=b.transAxes, fontsize=7.5, va='top')
FACTS['rock'] = dict(fwhm_center_deg=float(cen), cliff_deg=float(tf[icl]), step_deg=0.05,
                     fit_z_fixed_um=float(z_knife * 1e3), fit_th_off=float(pr[1]), fit_dth_off=float(er[1]),
                     fit_sigma_um=float(pr[2] * 1e3), fit_dsigma_um=float(er[2] * 1e3), fit_hd_mm=float(pr[3]),
                     fit_dhd_mm=float(er[3]), fit_chi2=chi2r, fit_dof=dofr,
                     known_hd_th_off=float(pk[1]), known_hd_dth_off=float(ek[1]), known_hd_chi2=chi2k, known_hd_dof=dofk)
PANELS.append((b, 'd'))

# ---------------- row 3, theta-2theta at 1 and 2 degrees
a = fig.add_subplot(gs[2, 0]); blank(a); a.set_xlim(0, 12); a.set_ylim(-2.6, 2.6)
ang = 8.0  # drawn exaggerated
cx = 4.6
sc = tilted_scene(a, -1.0, 0.5, cx, -1.0, 3.8, 0.6, ang, 10.4, show_pass=False, show_block=False)
yd = 0.5 * sum(sc['yd'])
diode(a, 10.4, yd, 0.75)
a.plot([cx, 9.6], [-1.0, -1.0], color=GRAY, lw=0.8, ls='--', zorder=6)
a.text(8.6, -1.45, r'$\theta_d$ = 2°', fontsize=8, color=BLACK)
a.text(1.0, 1.55, r'whole beam reflected onto the diode, $\theta_s$ near 1°', fontsize=7.5)
PANELS.append((a, 'e'))
b = fig.add_subplot(gs[2, 1])
yd_mm = D * np.tan(np.radians(2.0))
ts = np.arange(0.55, 1.4501, 0.04)
tf = np.linspace(0.55, 1.45, 600)
y = sparse(ts, lambda th: signal(0.0, th, yd=yd_mm))
g = lambda x, A, m, w, s: 0.5 * A * (erf((x - m + w) / s) - erf((x - m - w) / s))
p, cv = curve_fit(g, ts, y, p0=[1, 1.02, 0.28, 0.03], bounds=([0, 0.8, 0.1, 0.01], [2, 1.2, 0.5, 0.2]))
b.plot(tf, [signal(0.0, th, yd=yd_mm) for th in tf], color=LGRAY, lw=1.0)
b.plot(tf, g(tf, *p), color=RED, lw=1.4)
b.plot(ts, y, 'o', color=BLACK, ms=3.5, mfc='white', mew=0.9)
b.axvline(p[1], color=RED, lw=0.8, ls='--')
b.set_xlabel(r'Sample angle $\theta_s$ (°)'); b.set_ylabel('Photodiode signal')
b.text(0.5, 0.45, f'step 0.04°\n$\\theta_0$ = {p[1]:.3f} ± {np.sqrt(cv[1,1]):.3f}°', transform=b.transAxes,
       ha='center', va='top', fontsize=7.5, bbox=dict(fc='white', ec='none', pad=1.5))
FACTS['th2th'] = dict(theta0=float(p[1]), dtheta0=float(np.sqrt(cv[1, 1])), step_deg=0.04)
PANELS.append((b, 'f'))
grid_labels(fig, [PANELS[0:2], PANELS[2:4], PANELS[4:6]])
save(fig, 'fig2-07_alignment')
json.dump(FACTS, open(f'{OUT}/facts_align.json', 'w'), indent=1); print(FACTS)
