"""Precompute R_s and R_p for the remastered reflectivity animation.

Stack (from the ZnPc graded fit, collapsed to uniform slabs) with a buried interface layer
below the reflectivity resolution (2 pi / q_max = 2.5 nm at q_max = 2.5 nm^-1):
vacuum / ZnPc 173.7 A (sigma 8.4 A) / interface 15 A (sigma 4 A) / SiO2 6.9 A (sigma 4 A) / Si (sigma 1.2 A).
The interface carries the ZnPc optical constants with the orientation reversed (anisotropy
scaled by -0.5 about the isotropic average), same density.
ZnPc tensor from refl-analysis @models/optical/znpc/exp.csv; SiO2 and Si from xraydb.
Kernel: refloxide.python.tmm.uniaxial_reflectivity (4x4).
Usage: python3 xrr_data.py exp.csv [energy_eV]"""
import numpy as np, pandas as pd, xraydb, sys
from refloxide.python.tmm import uniaxial_reflectivity

E = float(sys.argv[2]) if len(sys.argv) > 2 else 293.0
csv = sys.argv[1] if len(sys.argv) > 1 else "exp.csv"
d = pd.read_csv(csv)
r = d.iloc[(d.energy - E).abs().argmin()]


def iso(f, rho):
    de, be = xraydb.xray_delta_beta(f, rho, E)[:2]
    return np.diag([de + 1j * be] * 3)


nx, nz = r.n_xx + 1j * r.n_ixx, r.n_zz + 1j * r.n_izz
navg = (2 * nx + nz) / 3
ix, iz = navg - 0.5 * (nx - navg), navg - 0.5 * (nz - navg)
vac = np.zeros((3, 3), complex)
tensor = np.array([vac, np.diag([nx, nx, nz]), np.diag([ix, ix, iz]), iso("SiO2", 2.2), iso("Si", 2.33)])
layers = np.array([[0, 0, 0, 0], [173.7, 0, 0, 8.37], [15.0, 0, 0, 4.0], [6.88, 0, 0, 4.0],
                   [0, 0, 0, 1.2]], float)
lam = 12398.4193 / E
th = np.linspace(0.05, 60, 3000)
q = 4 * np.pi * np.sin(np.radians(th)) / lam
refl = np.asarray(uniaxial_reflectivity(q, layers, tensor, E)[0])
layers0 = layers.copy(); layers0[:, 3] = 0.0
refl0 = np.asarray(uniaxial_reflectivity(q, layers0, tensor, E)[0])
noint = np.delete(layers, 2, axis=0); noint[1, 0] += 15.0
refl_noint = np.asarray(uniaxial_reflectivity(q, noint, np.delete(tensor, 2, axis=0), E)[0])
d_si = float(xraydb.xray_delta_beta("Si", 2.33, E)[0])

# features read off the simulated stack curves
from scipy.signal import argrelextrema
qn = q * 10
rs_, rp_ = np.log10(refl[:, 1, 1].real), np.log10(refl[:, 0, 0].real)
mx = argrelextrema(rs_, np.greater, order=10)[0]
# critical-edge knee of R_p: intersection of the plateau tangent and the steep-drop tangent
# (linear fits to log R_p before the knee and on the drop into the first p minimum)
mn_p = argrelextrema(rp_, np.less, order=10)[0]
q_notch = float(qn[mn_p[0]])
f1 = (qn > 0.02) & (qn < 0.4 * q_notch)
f2 = (qn > 0.72 * q_notch) & (qn < 0.92 * q_notch)
a1, b1 = np.polyfit(qn[f1], rp_[f1], 1)
a2, b2 = np.polyfit(qn[f2], rp_[f2], 1)
qc_kink = float((b2 - b1) / (a1 - a2))
hi = qn > 1.5
iP = int(np.argmin(np.where(hi, rp_, 9)))
qB_pmin, thB_pmin = float(qn[iP]), float(th[iP])  # Brewster = R_p minimum

# critical angle and Brewster angle from the simulation: bare Si substrate through the same 4x4 kernel.
# q_c = steepest descent (inflection) of log R_s (absorption rounds and shifts the edge above the
# delta-only estimate); Brewster = minimum of R_p / R_s.
Rb = np.asarray(uniaxial_reflectivity(q, np.zeros((2, 4)), np.array([vac, iso("Si", 2.33)]), E)[0])
bs, bp = np.log10(Rb[:, 1, 1].real), np.log10(Rb[:, 0, 0].real)
m = q * 10 < 1.0
qc_sim = float(q[m][np.argmin(np.gradient(bs, q)[m])] * 10)
iB = int(np.argmin(bp - bs))
qB_sim, thB_sim = float(q[iB] * 10), float(th[iB])
thc_sim = float(np.degrees(np.arcsin(qc_sim / 10 * lam / (4 * np.pi))))
np.savez("xrr_curves.npz", theta=th, q=q * 10, refl=refl, refl0=refl0, refl_noint=refl_noint, E=E,
         t_film_nm=(layers[1, 0] + layers[2, 0]) / 10, delta_si=d_si,
         qc_sim=qc_sim, thc_sim=thc_sim, qB_sim=qB_sim, thB_sim=thB_sim,
         qc_kink=qc_kink, qB_pmin=qB_pmin, thB_pmin=thB_pmin)
print("E", E, "qc delta-only", 4 * np.pi * np.sqrt(2 * d_si) / (lam / 10), "qc sim", qc_sim, thc_sim, "Brewster", qB_sim, thB_sim)
