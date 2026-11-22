"""Shared two-parameter reflectivity objective for the optimizer figure.

Bulk thickness versus buried interfacial-layer thickness for the Chapter 3
ZnPc film at 283.7 eV, s and p polarization. Total thickness is sharply
determined, the split between the two layers is not, so the minimum is a
narrow, tilted, rippled valley.
"""
import numpy as np
from figlib import reflectivity
from model import nk
from henke import n_si, n_sio2
E = 283.7
Q = np.linspace(0.012, 0.25, 200)
NB = nk(E, 69.6, 1.64)
NI = nk(E, 38.0, 0.87)
TB0, TI0 = 178.0, 15.0
def model(tb, ti):
    out = []
    for pol in 'sp':
        L = [(1 + 0j, 1 + 0j, 0, 0), (NB[0], NB[1], tb, 6.8), (NI[0], NI[1], ti, 2.0),
             (n_sio2(E), n_sio2(E), 15.0, 3.0), (n_si(E), n_si(E), 0, 3.0)]
        out.append(reflectivity(Q, E, L, pol))
    return np.concatenate(out)
rng = np.random.default_rng(3)
QQ = np.concatenate([Q, Q])
R_TRUE = model(TB0, TI0)
SIG = 0.08 * R_TRUE + 0.5e-6 * QQ
DATA = np.clip(R_TRUE + rng.normal(0, 1, QQ.size) * SIG * 0.5, 1e-10, None)
SIG_LOG = SIG / (DATA * np.log(10))
def resid(p):
    return (np.log10(model(*p)) - np.log10(DATA)) / SIG_LOG
def chi2(p):
    r = resid(p); return float(r @ r) / (QQ.size - 2)
