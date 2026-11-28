"""Exact-in-basis transition dipoles mu = <1s|r|psi_f> from the TP molden files, integrated on a
radial (log) x angular (Fibonacci) grid centred on the core-hole atom. Core orbital = alpha MO 14 (occ 0.5)."""
import math, pickle, numpy as np, molden_mo as M
from znpc_states import D

def sphere_grid(center, nr=220, nang=974, rmin=1e-4, rmax=1.4):
    r = np.logspace(math.log10(rmin), math.log10(rmax), nr) * M.ANG       # bohr
    dr = np.gradient(r)
    k = np.arange(nang) + 0.5
    phi = np.arccos(1 - 2 * k / nang); th = math.pi * (1 + 5 ** 0.5) * k
    u = np.c_[np.cos(th) * np.sin(phi), np.sin(th) * np.sin(phi), np.cos(phi)]
    P = (r[:, None, None] * u[None, :, :]).reshape(-1, 3) + center
    w = (r ** 2 * dr)[:, None].repeat(nang, 1).ravel() * (4 * math.pi / nang)
    return P, w

def tdm(site, mos):
    atoms, shells, C = M.load(f"{D}/{site}/{site}tp.molden", set(mos) | {14})
    Z = np.array([a[1] for a in atoms]); exc = int(np.where(Z == 6)[0][0])
    c0 = atoms[exc][2]
    P, w = sphere_grid(c0)
    core = M.mo_on_points(atoms, shells, C[14], P)
    print(site, "core norm in sphere", round(float((core ** 2 * w).sum()), 4))
    res = {}
    for mo in mos:
        f = M.mo_on_points(atoms, shells, C[mo], P)
        mu = ((P - c0) * (core * f * w)[:, None]).sum(0)
        res[mo] = mu
    return res

if __name__ == "__main__":
    checks = {"C1": [117, 124, 205, 211], "C4": [304], "C2": [328]}
    xyz = None
    out = {}
    for site, mos in checks.items():
        r = tdm(site, mos)
        for mo, mu in r.items():
            u = mu / np.linalg.norm(mu)
            th = math.degrees(math.acos(abs(u[2])))
            out[(site, mo)] = mu
            print(f"  {site} MO {mo}: |mu|^2 = {mu @ mu:.3e}, dir = {np.round(u, 3)}, theta from z = {th:.1f}")
    pickle.dump(out, open("znpc_tdm.pkl", "wb"))
