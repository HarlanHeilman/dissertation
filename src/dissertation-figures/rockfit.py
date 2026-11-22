"""Forward-model fit of the rocking scan in Fig. 2.7d.

The model integrates the same geometry as the ray Monte Carlo (Gaussian beam profile of rms sigma_b,
Gaussian divergence, sample of length ELL rotating about its center, photodiode of half height HD at D)
by Gauss-Legendre quadrature over the beam height, so it is smooth in its parameters and can be fit.
Free parameters: amplitude A, angular offset th_off, beam rms sigma_b, and the diode half height hd, which sets
the angular acceptance hd/D and so the position of the cliff. The height is fixed at the knife-edge estimate.
"""
import numpy as np
from scipy.special import erf
from scipy.optimize import curve_fit

ELL, D, HD, SDIV = 10.0, 150.0, 1.5, 1.0e-3 * 150.0
XG, WG = np.polynomial.legendre.leggauss(160)


def window(y, hd=HD):
    """Probability that a ray at height y (mm) on the diode plane lands on the diode, after divergence."""
    return 0.5 * (erf((hd - y) / (np.sqrt(2) * SDIV)) + erf((hd + y) / (np.sqrt(2) * SDIV)))


def integ(f, a, b, sig):
    a, b = max(a, -9 * sig), min(b, 9 * sig)
    if b <= a:
        return 0.0
    y = 0.5 * (b - a) * XG + 0.5 * (b + a)
    phi = np.exp(-0.5 * (y / sig) ** 2) / (np.sqrt(2 * np.pi) * sig)
    return 0.5 * (b - a) * np.sum(WG * phi * f(y))


def model1(th_deg, A, th_off, sig, z=0.0, hd=HD):
    a = np.radians(th_deg - th_off)
    t = np.tan(a)
    w = lambda y: window(y, hd)
    if abs(t) < 1e-12:
        return A * integ(w, z, np.inf, sig)
    if t < 0:
        return A * integ(w, z + ELL / 2 * abs(t), np.inf, sig)
    lo, hi = z - ELL / 2 * t, z + ELL / 2 * t
    t2 = np.tan(2 * a)
    p = integ(w, hi, np.inf, sig)
    r = integ(lambda y: w(y + t2 * (D - (y - z) / t)), lo, hi, sig)
    return A * (p + r)


def model(th, A, th_off, sig, hd, z=0.0):
    return np.array([model1(x, A, th_off, sig, z, hd) for x in np.atleast_1d(th)])


def fit(ts, y, n0, z_fixed=0.0, free_hd=True):
    """Weighted least squares with Poisson weights. Returns parameters, 1 sigma errors, chi2, dof, model."""
    ey = np.sqrt(np.maximum(y, 1.0 / n0) / n0)
    if free_hd:
        f = lambda th, A, o, s, hd: model(th, A, o, s, hd, z_fixed)
        p0, lo, hi = [1.0, 0.0, 0.04, HD], [0.5, -0.3, 0.01, 0.5 * HD], [1.5, 0.3, 0.1, 2.0 * HD]
    else:
        f = lambda th, A, o, s: model(th, A, o, s, HD, z_fixed)
        p0, lo, hi = [1.0, 0.0, 0.04], [0.5, -0.3, 0.01], [1.5, 0.3, 0.1]
    p, cv = curve_fit(f, ts, y, p0=p0, sigma=ey, absolute_sigma=True, bounds=(lo, hi))
    chi2 = float(np.sum(((y - f(ts, *p)) / ey) ** 2))
    return p, np.sqrt(np.diag(cv)), chi2, len(ts) - len(p), f
