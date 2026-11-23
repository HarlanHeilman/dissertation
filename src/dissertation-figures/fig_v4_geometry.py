"""Fig. 3.1, scattering geometries (top row, as in fig_v2_intro_geom.py) with what each measurement records (bottom row).

c) Transmission scattering from a sphere of radius a = 10 nm, the object of (a): the form factor sampled on a
   detector q grid, with the Guinier plateau, the first minimum at qa = 4.49 and the Porod q^-4 decay.
d) Specular reflectivity of the film of (b): the ZnPc film of Chapter 4 at 293 eV (ZnPc 173.7 A, sigma 8.4 A /
   interface 15 A with the anisotropy reversed, sigma 4 A / SiO2 6.9 A, sigma 4 A / Si, sigma 1.2 A), computed with
   the refloxide 4x4 transfer matrix, as in the defense reflectivity animation. Annotated: the s and p critical edges,
   the p-polarized Brewster minimum, the fringe spacing 2 pi / t, and the effect of roughness (the same stack with
   every sigma = 0).
Run with the refl-analysis environment (refloxide, periodictable).
"""
import json, os
import numpy as np
import pandas as pd
import periodictable as pt
from periodictable import xsf
from figlib import *
from matplotlib.patches import Rectangle, Circle, Arc
import refloxide

FACTS = {}
E = 293.0
LAM = 12398.42 / E
K4 = 4 * np.pi / LAM

# ---------------------------------------------------------------- reflectivity of the Chapter 4 stack
oc = pd.read_csv(os.path.expanduser('~/mnt/refl-analysis/@models/optical/znpc/exp.csv'))
r = oc.iloc[(oc.energy - E).abs().argmin()]
zx, zz = complex(r.n_xx, r.n_ixx), complex(r.n_zz, r.n_izz)        # delta + i beta
iso = (2 * zx + zz) / 3
ix, iz = iso - 0.5 * (zx - iso), iso - 0.5 * (zz - iso)            # interface, anisotropy reversed
def bulk(formula, rho):
    n = xsf.index_of_refraction(formula, density=rho, energy=E / 1000)
    return complex(1 - n.real, abs(n.imag))
sio2, si = bulk('SiO2', 2.2), bulk('Si', 2.33)
def diag(a, c):
    return np.diag([a, a, c])
q = np.linspace(0.002, 0.26, 3000)   # 4 pi / lambda = 0.297 per angstrom at 293 eV, so 0.26 is a grazing angle of 61 degrees
def refl(rough=True):
    s = 1.0 if rough else 0.0
    layers = np.array([[0, 0, 0, 0],
                       [173.7, 0, 0, 8.4 * s],
                       [15.0, 0, 0, 4.0 * s],
                       [6.9, 0, 0, 4.0 * s],
                       [0, 0, 0, 1.2 * s]], float)
    tensor = np.array([diag(0, 0), diag(zx, zz), diag(ix, iz), diag(sio2, sio2), diag(si, si)], complex)
    R = refloxide.uniaxial_reflectivity(q, layers, tensor, E)[0]
    return R[:, 1, 1].real, R[:, 0, 0].real          # s, p
Rs, Rp = refl(True)
Rs0, Rp0 = refl(False)
qc_s = K4 * np.sqrt(2 * si.real)           # s sees the in-plane film index, nearly vacuum here, so the substrate sets its edge
qc_p = K4 * np.sqrt(2 * zz.real)           # p sees the out-of-plane film index
hi = q > 0.12
qB = float(q[hi][np.argmin(Rp[hi])])
thB = float(np.degrees(np.arcsin(qB / K4)))
mins = [i for i in range(1, len(q) - 1) if Rs[i] < Rs[i - 1] and Rs[i] < Rs[i + 1] and 0.05 < q[i] < 0.16]
q1, q2 = float(q[mins[0]]), float(q[mins[1]])
FACTS.update(qc_s=float(qc_s), qc_p=float(qc_p), qB=qB, thB=thB, fringe=(q1, q2, q2 - q1, 2 * np.pi / (173.7 + 15 + 6.9)),
             delta_xx=zx.real, delta_zz=zz.real, delta_si=si.real)

# ---------------------------------------------------------------- figure
fig = plt.figure(figsize=(6.5, 4.6))
TOP = 0.50
a = fig.add_axes([0.0, TOP, 0.5, 0.48]); blank(a); a.set_xlim(0, 10.5); a.set_ylim(0, 5.5); a.set_aspect('equal', adjustable='box')
for x in (0.5, 0.9, 1.3, 1.7):
    a.plot([x, x], [1.3, 4.3], color=BLACK, lw=1.2)
a.text(1.0, 4.6, r'$\mathbf{k}$', fontsize=9.5)
a.add_patch(Circle((3.4, 2.8), 0.62, fc='#7F7F7F', ec=BLACK))
arrow(a, 0.15, 2.8, 2.75, 2.8)
for k, r_ in enumerate((0.95, 1.35, 1.75, 2.15)):
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
a.plot(9.4 + 0.95 * np.sinc((yy - 2.8) * 1.6) ** 2, yy, color=RED, lw=1.4)
a.text(9.5, 0.2, 'far field', fontsize=7.5, color=GRAY)
a.text(6.6, 0.35, r'$|\mathbf{q}|=\frac{4\pi}{\lambda}\sin\theta$', fontsize=9, ha='center')
b = fig.add_axes([0.52, TOP, 0.46, 0.48]); blank(b); b.set_xlim(0, 10); b.set_ylim(-1.3, 5.5)
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

# c, transmission scattering from the sphere of (a)
c = fig.add_axes([0.095, 0.09, 0.37, 0.38])
A_ = 100.0
qs = np.logspace(np.log10(0.002), np.log10(0.15), 600)
def P(qq):
    x = qq * A_
    return (3 * (np.sin(x) - x * np.cos(x)) / x ** 3) ** 2
qpts = np.arange(0.003, 0.15, 0.0022)     # detector q grid
c.loglog(qs, P(qs), color=BLACK, lw=1.0)
c.loglog(qpts, P(qpts), 'o', ms=2.6, mfc=RED, mec=RED)
c.axvline(4.493 / A_, color=GRAY, lw=0.8, ls='--')
c.text(4.493 / A_ * 0.94, 2e-6, r'$qa = 4.49$', fontsize=7, color=GRAY, ha='right')
qq = np.array([0.05, 0.15])
c.loglog(qq, 9 * (qq * A_) ** -4 * 3, color=GRAY, lw=0.9, ls=':')
c.text(0.1, 9 * (0.1 * A_) ** -4 * 6, r'$q^{-4}$', fontsize=7.5, color=GRAY)
c.text(0.0024, 0.25, 'Guinier plateau', fontsize=7, color=GRAY)
c.set_xlim(0.002, 0.15); c.set_ylim(1e-7, 3)
c.set_xlabel(r'$q$ (Å$^{-1}$)'); c.set_ylabel('Scattered intensity (arb.)')

# d, reflectivity of the film of (b)
d = fig.add_axes([0.6, 0.09, 0.385, 0.38])
d.semilogy(q, Rs0, color=RED, lw=0.7, ls=(0, (2, 2)), alpha=0.8)
d.semilogy(q, Rp0, color=BLACK, lw=0.7, ls=(0, (2, 2)), alpha=0.8)
d.semilogy(q, Rs, color=RED, lw=1.3, label='s')
d.semilogy(q, Rp, color=BLACK, lw=1.3, label='p')
qd = q[::40]
for y_, col in ((Rs, RED), (Rp, BLACK)):
    d.semilogy(qd, y_[::40], 'o', ms=2.0, mfc='white', mec=col, mew=0.6)
for x_, lab, col, ha, dx in ((qc_p, r'$q_{c,p}$', BLACK, 'right', -0.002), (qc_s, r'$q_{c,s}$', RED, 'left', 0.002)):
    d.axvline(x_, color=col, lw=0.7, ls='--')
    d.text(x_ + dx, 3e-8 if col == BLACK else 3e-9, lab, fontsize=7, color=col, ha=ha)
d.axvline(qB, color=GRAY, lw=0.7, ls='--')
d.text(qB - 0.004, 1e-2, f'Brewster\n{thB:.0f}°', fontsize=7, color=GRAY, ha='right', va='center')
ymid = min(Rs[mins[0]], Rs[mins[1]]) / 12
for qm, im in ((q1, mins[0]), (q2, mins[1])):
    d.plot([qm, qm], [ymid, Rs[im]], color=RED, lw=0.6, ls=':')
d.annotate('', xy=(q1, ymid), xytext=(q2, ymid), arrowprops=dict(arrowstyle='<->', color=RED, lw=0.9))
d.text((q1 + q2) / 2, ymid / 6, r'$\Delta q = 2\pi/t$', fontsize=7.5, color=RED, ha='center')
sel = (q > 0.17) & (q < 0.21)
i3 = np.where(sel)[0][np.argmax(Rs0[sel])]
d.annotate('', xy=(q[i3], Rs[i3] * 1.1), xytext=(q[i3], Rs0[i3] * 12), arrowprops=dict(arrowstyle='->', color=GRAY, lw=0.9))
d.text(q[i3], Rs0[i3] * 15, 'roughness', fontsize=7, color=GRAY, ha='center', va='bottom')
d.set_xlim(0, 0.26); d.set_ylim(1e-9, 2)
d.set_xlabel(r'$q_z$ (Å$^{-1}$)'); d.set_ylabel('Reflectivity')
d.legend(loc='upper center', handlelength=1.4, bbox_to_anchor=(0.6, 1.0), ncol=2)
for ax_, s_, x_, y_ in ((a, 'a', 0.0, 0.985), (b, 'b', 0.52, 0.985), (c, 'c', 0.0, 0.49), (d, 'd', 0.52, 0.49)):
    fig.text(x_, y_, s_, fontsize=LABEL_FS, fontweight='bold', va='top', ha='left')
save(fig, 'fig2-01_scattering-geometry')
json.dump(FACTS, open(os.path.join(OUT, 'fig2-01_facts.json'), 'w'), indent=1, default=float)
print(FACTS)
