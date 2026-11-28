"""States for GIF 12 (v2): one representative StoBe TP transition per highlighted refined cluster, in energy order.
For each: exact mu = <1s|r|psi_f>, angle from the local isoindole normal, and psi_f on a 3D grid for isosurfaces."""
import math, pickle, time, numpy as np, molden_mo as M
from znpc_tdm import sphere_grid
D = "/mnt/user-data/uploads/dft-learn/docs/stobe/example-run/znpc-cif"
STATES = [("C3", 119, 1), ("C2", 124, 5), ("C3", (133, 131), 7), ("C1", 205, 13), ("C4", 314, 15)]
# cluster 7 is drawn as its two strongest C3 members together: a pi* (MO 133) and an in-plane state (MO 131),
# whose mix is what the refined cluster tensor sees as a 29 deg tilt
H = 0.22 * M.ANG

import pandas as pd
_st = pd.read_csv("/home/claude/znpc_data/data/csv/znpc_sticks_tensor.csv")
out = []
for site, mos, cl in STATES:
    mos = mos if isinstance(mos, tuple) else (mos,)
    atoms, shells, C = M.load(f"{D}/{site}/{site}tp.molden", set(mos) | {14})
    xyzb = np.array([a[2] for a in atoms])
    Z = np.array([a[1] for a in atoms]); exc = int(np.where(Z == 6)[0][0])
    names = [a[0] for a in atoms]
    xyz = xyzb / M.ANG
    iso = [i for i, nm in enumerate(names) if nm in ("C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "N02")]
    P = xyz[iso]; _, _, vt = np.linalg.svd(P - P.mean(0)); nrm = vt[2] * np.sign(vt[2][2])
    G, w = sphere_grid(atoms[exc][2])
    core = M.mo_on_points(atoms, shells, C[14], G)
    lo = xyzb.min(0) - np.array([3.5, 3.5, 5.0]) * M.ANG
    hi = xyzb.max(0) + np.array([3.5, 3.5, 5.0]) * M.ANG
    axes = [np.arange(lo[k], hi[k] + H, H) for k in range(3)]
    X, Y, Zg = np.meshgrid(*axes, indexing="ij")
    PP = np.c_[X.ravel(), Y.ravel(), Zg.ravel()]
    tdms, psi = [], None
    for mo in mos:
        f = M.mo_on_points(atoms, shells, C[mo], G)
        mu = ((G - atoms[exc][2]) * (core * f * w)[:, None]).sum(0)
        osr = float(_st[(_st.atomid == int(site[1])) & (_st.mo == mo)].os.iloc[0])
        tdms.append((mu / np.linalg.norm(mu), osr))
        p = np.zeros(X.size, np.float32)
        for s0 in range(0, len(PP), 200000):
            p[s0:s0 + 200000] = M.mo_on_points(atoms, shells, C[mo], PP[s0:s0 + 200000])
        p = p.reshape(X.shape)
        psi = p if psi is None else np.where(np.abs(p) > np.abs(psi), p, psi)
    mx = max(o for _, o in tdms)
    tdms = [(u, o / mx) for u, o in tdms]
    th = [round(math.degrees(math.acos(min(1, abs(u @ nrm)))), 1) for u, _ in tdms]
    print(site, mos, "cluster", cl, "theta", th, "rel. strength", [round(o, 2) for _, o in tdms])
    out.append(dict(site=site, mo=mos[0], mos=mos, cluster=cl, theta=th[0], exc=exc, xyz=xyz, Z=Z, names=names,
                    tdm=tdms[0][0], tdms=tdms, normal=nrm, origin=np.array([a[0] for a in axes]) / M.ANG,
                    step=H / M.ANG, psi=psi))
pickle.dump(out, open("znpc_orb.pkl", "wb"))
