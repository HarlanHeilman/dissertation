"""D4h treatment for GIF 12.
Geometry: averaged over the 16 operations of D4h (Zn at the origin, C4 along the normal, sigma_v through Zn-N).
States: each computed TP state is copied to the 8 chemically equivalent carbons with the in-plane operations (D4):
  mu_g = g mu,   psi_g(r) = psi(g^-1 r);   the drawn field is the signed psi_g of largest magnitude at each point,
so the surface at |psi| = iso is the union of the 8 copies' isosurfaces with their phases."""
import math, numpy as np
from scipy.ndimage import map_coordinates


def Rz(a):
    return np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1.0]])


def d4_ops(X, Z):
    zn = np.where(Z == 30)[0][0]
    c = X[zn]
    N = np.where(Z == 7)[0]
    nb = N[np.argsort(np.linalg.norm(X[N] - c, axis=1))[:4]]
    phis = sorted(math.atan2(*(X[i] - c)[[1, 0]]) % (math.pi / 2) for i in nb)
    phi = float(np.mean(phis))
    M = Rz(phi) @ np.diag([1, -1, 1]) @ Rz(-phi)
    d4 = [Rz(k * math.pi / 2) @ m for k in range(4) for m in (np.eye(3), M)]
    return c, d4


def perm(X, g):
    Y = X @ g.T
    return np.linalg.norm(Y[:, None] - X[None], axis=2).argmin(1)


def symmetrize_geometry(X, Z):
    c, d4 = d4_ops(X, Z)
    X = X - c
    ops = d4 + [np.diag([1, 1, -1.0]) @ g for g in d4]
    acc = np.zeros_like(X)
    for g in ops:
        p = perm(X, g)                 # g maps atom i onto atom p[i]
        acc += X[p] @ g                # g^-1 X[p[i]] (g orthogonal)
    Xs = acc / len(ops)
    return Xs, d4, float(np.abs(Xs - X).max())


def sym_field(st, FR, c_frame_to_orig, d4, lo, hi, h):
    """signed max-|psi| over the 8 copies, on a regular grid in the molecular frame"""
    ax = [np.arange(lo[k], hi[k] + h, h) for k in range(3)]
    Q = np.stack(np.meshgrid(*ax, indexing="ij"), -1).reshape(-1, 3)
    best = np.zeros(len(Q), np.float32)
    for g in d4:
        Qo = (Q @ g) @ FR + c_frame_to_orig                 # g^-1 q, back to the molden frame (Angstrom)
        idx = ((Qo - st["origin"]) / st["step"]).T
        v = map_coordinates(st["psi"], idx, order=3, mode="constant", cval=0.0).astype(np.float32)
        take = np.abs(v) > np.abs(best)
        best[take] = v[take]
    return best.reshape([len(a) for a in ax]), np.array([a[0] for a in ax]), h
