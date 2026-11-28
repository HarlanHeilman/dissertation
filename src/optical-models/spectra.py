"""Model optical constants for a benzene-ring molecule near the C 1s edge.

Built the same way as the dissertation's causal oscillator basis:
    n(E) = 1 - (delta_edge + i beta_edge) + sum_i (delta_i + i beta_i)
    beta_i  = A_i/(w_i sqrt(pi)) exp(-x^2),   delta_i = 2 A_i/(w_i pi) D(x),   x = (E - E_i)/w_i
The bare-atom (edge) delta is obtained from a numerical Kramers-Kronig transform of a
bare-atom beta defined from 1 eV to 30 keV, so every curve shown is causal.
Units: beta, delta in 1e-3.
"""
import numpy as np
from scipy.special import erf, dawsn

E1S = 284.2
IP = 290.3   # ionization threshold: the absorption step sits here, above pi*

# (energy eV, gaussian width eV, area in eV*1e-3, symmetry)
#  'vec'  : vector orbital (pi*), TDM normal to the ring plane
#  'pln'  : plane orbital (sigma*), TDM in the ring plane
RES = [
    (285.10, 0.40, 1.90, "vec"),   # C 1s -> pi*, TDM normal to the ring plane
    (293.50, 1.70, 1.60, "pln"),   # C 1s -> sigma*(C-C), TDM in the ring plane
    (301.00, 3.80, 2.60, "pln"),   # broad sigma* shape resonance
]
PI_IDX = [0]
SIG_IDX = [1, 2]


def beta_bare(E):
    E = np.asarray(E, float)
    x = E / 20.0
    valence = 2400.0 * x ** 2 / (1 + x ** 2) ** 2.75  # valence shells, sets the TRK sum
    step = 0.5 * (1 + erf((E - IP) / 0.70))
    kshell = 1.30 * (np.maximum(E, 1.0) / IP) ** -2.6 * step
    return valence + kshell


def _kk_bare(Eeval):
    """delta(E) = (2/pi) P int E' beta(E') / (E^2 - E'^2) dE'  (subtraction method)."""
    g = np.unique(np.concatenate([
        np.logspace(0, np.log10(3.0e4), 60000),
        np.linspace(250, 360, 40000),
        np.linspace(288.0, 292.5, 8000),
    ]))
    bg = beta_bare(g)
    fg = g * bg
    a, b = g[0], g[-1]
    out = np.empty(len(Eeval))
    for i, E in enumerate(Eeval):
        fE = E * float(beta_bare(E))
        d = E * E - g * g
        mask = np.abs(d) > 1e-9
        integrand = np.zeros_like(g)
        integrand[mask] = (fg[mask] - fE) / d[mask]
        reg = np.trapezoid(integrand, g)
        # PV int_a^b dE'/(E^2-E'^2) = (1/2E) ln[ (E+b)(E-a) / ((b-E)(E+a)) ]
        sing = (1 / (2 * E)) * np.log(((E + b) * (E - a)) / ((b - E) * (E + a)))
        out[i] = (2 / np.pi) * (reg + fE * sing)
    return out


def resonance(E, i):
    Ei, w, A, _ = RES[i]
    x = (np.asarray(E, float) - Ei) / w
    b = A / (w * np.sqrt(np.pi)) * np.exp(-x * x)
    d = 2 * A / (w * np.pi) * dawsn(x)
    return b, d


def orient_factor(kind, comp, alpha_deg):
    """Dichroic weight for a uniaxial film; alpha = angle of the pi* TDM from the surface normal.
    Isotropic average of each factor over (xx, yy, zz) is 1."""
    s2 = np.sin(np.radians(alpha_deg)) ** 2
    c2 = 1 - s2
    if kind == "vec":
        return 1.5 * s2 if comp == "xx" else 3 * c2
    return 1.5 * (1 - s2 / 2) if comp == "xx" else 1.5 * s2


class Model:
    def __init__(self, E):
        self.E = np.asarray(E, float)
        self.bb = beta_bare(self.E)
        self.db = _kk_bare(self.E)
        self.rb, self.rd = [], []
        for i in range(len(RES)):
            b, d = resonance(self.E, i)
            self.rb.append(b)
            self.rd.append(d)

    def iso(self):
        return self.bb + sum(self.rb), self.db + sum(self.rd)

    def comp(self, comp, alpha_deg):
        b, d = self.bb.copy(), self.db.copy()
        for i, (_, _, _, kind) in enumerate(RES):
            f = orient_factor(kind, comp, alpha_deg)
            b = b + f * self.rb[i]
            d = d + f * self.rd[i]
        return b, d

    def group(self, idx):
        return sum(self.rb[i] for i in idx)


if __name__ == "__main__":
    E = np.linspace(270, 330, 601)
    m = Model(E)
    b, d = m.iso()
    print("beta range", b.min(), b.max(), "delta range", d.min(), d.max())
    print("bare delta at 270, 283, 300, 330:", np.interp([270, 283, 300, 330], E, m.db))
    bx, dx = m.comp("xx", 72); bz, dz = m.comp("zz", 72)
    print("xx max", bx.max(), "zz max", bz.max())
