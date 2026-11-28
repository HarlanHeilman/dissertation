import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem
from ase import Atoms
from ase.optimize import BFGS
from ase.io import write
from tblite.ase import TBLite

def ligand():
    m = Chem.AddHs(Chem.MolFromSmiles("[O-]c1cccc2cccnc12"))
    AllChem.EmbedMolecule(m, randomSeed=7); AllChem.MMFFOptimizeMolecule(m)
    pos = m.GetConformer().GetPositions(); sym = [a.GetSymbol() for a in m.GetAtoms()]
    iO = sym.index("O"); iN = sym.index("N")
    return np.array(sym), pos, iO, iN

def virtual_al(pos, iO, iN, dO=1.86, dN=2.05):
    O, N = pos[iO], pos[iN]
    c = pos.mean(0)
    n = np.linalg.svd(pos - c)[2][2]  # plane normal
    u = (N - O); L = np.linalg.norm(u); u /= L
    a = (dO**2 - dN**2 + L**2) / (2 * L); h = np.sqrt(dO**2 - a**2)
    v = np.cross(n, u); base = O + a * u
    P1, P2 = base + h * v, base - h * v
    return P1 if np.linalg.norm(P1 - c) > np.linalg.norm(P2 - c) else P2

def kabsch(A, B):  # rotation R, t with R@A_i + t ~ B_i
    ca, cb = A.mean(0), B.mean(0)
    H = (A - ca).T @ (B - cb); U, S, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T)); D = np.diag([1, 1, d])
    R = Vt.T @ D @ U.T
    return R, cb - R @ ca

V = {"+x": (1, 0, 0), "-x": (-1, 0, 0), "+y": (0, 1, 0), "-y": (0, -1, 0), "+z": (0, 0, 1), "-z": (0, 0, -1)}
def build(pairs):
    sym, pos, iO, iN = ligand(); P = virtual_al(pos, iO, iN)
    S, X = ["Al"], [np.zeros(3)]
    for o, n in pairs:
        tgt = np.array([[0, 0, 0], 1.86 * np.array(V[o], float), 2.05 * np.array(V[n], float)])
        R, t = kabsch(np.array([P, pos[iO], pos[iN]]), tgt)
        S += list(sym); X += list((R @ pos.T).T + t)
    return Atoms(S, positions=np.array(X))

isomers = {"mer": [("+y", "+z"), ("+x", "-y"), ("-x", "-z")],
           "fac": [("+x", "-y"), ("+y", "-z"), ("+z", "-x")]}
for name, pairs in isomers.items():
    at = build(pairs)
    d = at.get_all_distances(); np.fill_diagonal(d, 9); print(name, len(at), "min dist", d.min().round(2))
    at.calc = TBLite(method="GFN2-xTB", charge=0, multiplicity=1, verbosity=0)
    BFGS(at, logfile=None).run(fmax=0.05, steps=400)
    e = at.get_potential_energy(); mu = at.calc.get_dipole_moment() if hasattr(at.calc, "get_dipole_moment") else at.calc.results["dipole"]
    mu = np.asarray(mu); print(name, "E (eV)", round(e, 3), "dipole e*A", mu.round(3), "|mu| D", round(np.linalg.norm(mu) * 4.80321, 2))
    write(f"/home/claude/work/alq3/{name}.xyz", at)
    np.save(f"/home/claude/work/alq3/{name}_dipole.npy", mu)
