import pickle, time, numpy as np, molden_mo as M
STATES = [("C3", 119), ("C1", 124), ("C1", 211), ("C1", 117)]
H = 0.30 * M.ANG  # 0.30 A spacing, in bohr


def grid_for(atoms):
    xyz = np.array([a[2] for a in atoms])
    lo = xyz.min(0) - np.array([3.0, 3.0, 4.0]) * M.ANG
    hi = xyz.max(0) + np.array([3.0, 3.0, 4.0]) * M.ANG
    axes = [np.arange(lo[k], hi[k] + H, H) for k in range(3)]
    return axes


if __name__ == "__main__":
    out = {}
    for site, mo in STATES:
        atoms, shells, C = pickle.load(open(f"{site}_mo.pkl", "rb"))
        axes = grid_for(atoms)
        X, Y, Z = np.meshgrid(*axes, indexing="ij")
        P = np.c_[X.ravel(), Y.ravel(), Z.ravel()]
        t = time.time()
        psi = M.mo_on_points(atoms, shells, C[mo], P).reshape(X.shape)
        norm = (psi ** 2).sum() * H ** 3
        # TDM direction ~ p character of the final orbital on the core-hole atom
        exc = [i for i, a in enumerate(atoms) if a[1] == 6][0]
        k = 0
        pv = np.zeros(3)
        for a, l, ex, co in shells:
            ncomp = len(M.CART[l])
            if a == exc and l == "p":
                # weight each p shell by its overlap with a compact 1s (tight exponents dominate)
                w = (co * ex ** 0.75).sum()
                pv += w * C[mo][k:k + 3]
            k += ncomp
        out[(site, mo)] = dict(axes=axes, psi=psi.astype(np.float32), exc=exc, pdir=pv / np.linalg.norm(pv))
        print(site, mo, psi.shape, "norm", round(norm, 3), "p-dir", np.round(pv / np.linalg.norm(pv), 3), round(time.time() - t, 1), "s")
    pickle.dump(out, open("mo_grids.pkl", "wb"))
