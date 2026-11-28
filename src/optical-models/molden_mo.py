"""Minimal molden reader and MO evaluator for the StoBe transition-potential runs.
Cartesian GTOs (no [5D] flag in these files): s; p x,y,z; d xx,yy,zz,xy,xz,yz. Coordinates Angstrom -> bohr."""
import math
import numpy as np

ANG = 1.0 / 0.52917721067


def _dfact(n):
    return 1.0 if n <= 0 else n * _dfact(n - 2)


CART = {"s": [(0, 0, 0)], "p": [(1, 0, 0), (0, 1, 0), (0, 0, 1)],
        "d": [(2, 0, 0), (0, 2, 0), (0, 0, 2), (1, 1, 0), (1, 0, 1), (0, 1, 1)]}


def load(path, want_alpha):
    """Return atoms [(label, Z, xyz_bohr)], shells [(atom_idx, l, exps, coefs)], {mo_index: coeff vector} for alpha MOs."""
    atoms, shells, mos = [], [], {}
    with open(path) as f:
        lines = f.read().splitlines()
    i = 0
    n = len(lines)
    while i < n:
        s = lines[i].strip()
        if s.startswith("[Atoms]"):
            i += 1
            while not lines[i].strip().startswith("["):
                p = lines[i].split()
                atoms.append((p[0], int(p[2]), np.array([float(p[3]), float(p[4]), float(p[5])]) * ANG))
                i += 1
            continue
        if s.startswith("[GTO]"):
            i += 1
            while not lines[i].strip().startswith("["):
                p = lines[i].split()
                if len(p) == 2 and p[1] == "0":
                    a = int(p[0]) - 1
                    i += 1
                    while i < n and lines[i].strip():
                        q = lines[i].split()
                        l, npr = q[0], int(q[1])
                        ex, co = [], []
                        for k in range(npr):
                            e, c = lines[i + 1 + k].replace("D", "E").split()[:2]
                            ex.append(float(e)); co.append(float(c))
                        shells.append((a, l, np.array(ex), np.array(co)))
                        i += 1 + npr
                i += 1
            continue
        if s.startswith("[MO]"):
            i += 1
            ialpha = 0
            while i < n and not lines[i].strip().startswith("["):
                if lines[i].startswith("Sym="):
                    spin = lines[i + 2].split()[1]
                    i += 4
                    vals = []
                    while i < n and lines[i][:1] == " " and not lines[i].startswith("Sym="):
                        vals.append(float(lines[i].split()[1]))
                        i += 1
                    if spin == "Alpha":
                        ialpha += 1
                        if ialpha in want_alpha:
                            mos[ialpha] = np.array(vals)
                else:
                    i += 1
            continue
        i += 1
    return atoms, shells, mos


LMAP = {"s": 0, "p": 1, "d": 2}
NORMALIZE_CONTRACTION = True


def contraction_scale(l, ex, co):
    """Factor making the contracted shell unit-normalized (primitives already normalized)."""
    L = LMAP[l]
    ai, aj = ex[:, None], ex[None, :]
    # overlap of two normalized primitives of the same cartesian component x^L
    s = (2 * np.sqrt(ai * aj) / (ai + aj)) ** (L + 1.5)
    S = (co[:, None] * co[None, :] * s).sum()
    return 1.0 / math.sqrt(S)


def basis_on_points(atoms, shells, P, cutoff=1e-7):
    """Yield (basis_index, values) for every cartesian basis function on points P (N,3) in bohr."""
    idx = 0
    for a, l, ex, co in shells:
        r = P - atoms[a][2]
        r2 = np.einsum("ij,ij->i", r, r)
        amin = ex.min()
        mask = r2 < (-math.log(cutoff) / amin)
        comps = CART[l]
        if not mask.any():
            idx += len(comps)
            continue
        rm, r2m = r[mask], r2[mask]
        for (lx, ly, lz) in comps:
            L = lx + ly + lz
            norm = (2 * ex / math.pi) ** 0.75 * (4 * ex) ** (L / 2) / math.sqrt(
                _dfact(2 * lx - 1) * _dfact(2 * ly - 1) * _dfact(2 * lz - 1))
            cs = contraction_scale(l, ex, co) if NORMALIZE_CONTRACTION else 1.0
            radial = (co * norm * cs)[None, :] * np.exp(-r2m[:, None] * ex[None, :])
            ang = rm[:, 0] ** lx * rm[:, 1] ** ly * rm[:, 2] ** lz
            v = np.zeros(len(P))
            v[mask] = radial.sum(1) * ang
            yield idx, v
            idx += 1


def mo_on_points(atoms, shells, C, P):
    out = np.zeros(len(P))
    for k, v in basis_on_points(atoms, shells, P):
        if abs(C[k]) > 1e-6:
            out += C[k] * v
    return out


def nbasis(shells):
    return sum(len(CART[l]) for _, l, _, _ in shells)
