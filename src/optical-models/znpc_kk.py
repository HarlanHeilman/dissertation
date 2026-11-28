"""delta_iso(E) for ZnPc by numerical Kramers-Kronig transform of the measured isotropic beta.
Inside 270.2-330 eV: exp_bets.csv beta_iso (ML-refined NEXAFS beta). Outside: dft.csv broadband beta (10 eV - 500 keV),
scaled to join the measured beta at both ends. delta = (2/pi) P int E' b(E')/(E^2 - E'^2) dE' (subtraction form)."""
import numpy as np, pandas as pd
D = "/home/claude/znpc_data/data/optical"
b = pd.read_csv(f"{D}/exp_bets.csv"); w = pd.read_csv(f"{D}/dft.csv")
Ew = w.energy.values; bw = (2 * w.n_ixx.values + w.n_izz.values) / 3
Em = b.Energy.values; bm = b["βiso"].values
lo, hi = Em[0], Em[-1]
s_lo = bm[0] / np.interp(lo, Ew, bw); s_hi = bm[-1] / np.interp(hi, Ew, bw)

def beta_wide(E):
    E = np.asarray(E, float)
    out = np.where(E < lo, s_lo * np.interp(E, Ew, bw), np.where(E > hi, s_hi * np.interp(E, Ew, bw), np.interp(E, Em, bm)))
    return out

G = np.unique(np.concatenate([np.logspace(1, np.log10(Ew[-1]), 80000), np.linspace(250, 360, 60000), Em]))
BG = beta_wide(G); FG = G * BG
def delta(Eeval):
    a, c = G[0], G[-1]
    out = np.empty(len(Eeval))
    for i, E in enumerate(Eeval):
        fE = E * float(beta_wide(E))
        d = E * E - G * G
        m = np.abs(d) > 1e-9
        ig = np.zeros_like(G); ig[m] = (FG[m] - fE) / d[m]
        sing = (1 / (2 * E)) * np.log(((E + c) * (E - a)) / ((c - E) * (E + a)))
        out[i] = (2 / np.pi) * (np.trapezoid(ig, G) + fE * sing)
    return out

if __name__ == "__main__":
    print("join scales", s_lo, s_hi)
    EE = np.linspace(280, 320, 801)
    dk = delta(EE)
    e = pd.read_csv(f"{D}/exp.csv")
    de = (2 * np.interp(EE, e.energy, e.n_xx) + np.interp(EE, e.energy, e.n_zz)) / 3
    bb = np.interp(EE, Em, bm)
    for E0 in (280, 283.85, 285.1, 287, 290, 295, 300, 307.9, 320):
        print(E0, "beta %.3f  dKK %.3f  d_exp.csv %.3f (1e-3)" % (np.interp(E0, EE, bb) * 1e3, np.interp(E0, EE, dk) * 1e3, np.interp(E0, EE, de) * 1e3))
    print("rms diff", np.sqrt(np.mean((dk - de) ** 2)) * 1e3, " mean diff", np.mean(dk - de) * 1e3)
    np.savez("/home/claude/kk/znpc_kk.npz", E=EE, beta=bb, delta=dk, delta_expcsv=de)
