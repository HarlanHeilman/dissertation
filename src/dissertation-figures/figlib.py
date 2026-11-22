"""Shared style and physics for the dissertation figure batch.

Style follows the existing Chapter 2 artwork: black line work, red for the
quantity of interest, gray for context, bold lowercase panel labels, sans
serif text, no grid, open axes.
"""
import os
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.special import erf

DATA = os.environ.get('FIG_DATA', '/home/claude/work/data')  # folder holding buildingblock.csv, nexafs.csv, igor_mu.csv, sos.json
OUT = os.environ.get('FIG_OUT', '/home/claude/figs/out')
os.makedirs(OUT, exist_ok=True)

BLACK = '#000000'
RED = '#E0201B'
LRED = '#F2A7A5'
GRAY = '#808080'
LGRAY = '#D0D0D0'

mpl.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Liberation Sans', 'DejaVu Sans'],
    'mathtext.fontset': 'custom',
    'mathtext.rm': 'Liberation Sans', 'mathtext.it': 'Liberation Sans:italic',
    'mathtext.bf': 'Liberation Sans:bold',
    'font.size': 8, 'axes.labelsize': 8.5, 'axes.titlesize': 8.5,
    'xtick.labelsize': 7.5, 'ytick.labelsize': 7.5, 'legend.fontsize': 7,
    'axes.linewidth': 0.8, 'lines.linewidth': 1.3, 'xtick.major.width': 0.8, 'ytick.major.width': 0.8,
    'xtick.major.size': 3, 'ytick.major.size': 3, 'legend.handlelength': 1.6,
    'axes.spines.top': False, 'axes.spines.right': False,
    'xtick.direction': 'out', 'ytick.direction': 'out',
    'legend.frameon': False, 'svg.fonttype': 'none', 'pdf.fonttype': 42,
    'savefig.dpi': 300, 'axes.edgecolor': BLACK,
})


# Dissertation page, letter paper with 1 in margins, 11 pt body text.
PAGE_W, PAGE_H = 6.5, 9.0
LABEL_FS = 11


def label(ax, s, x=-0.12, y=1.04, fig=None):
    """Bold lowercase panel label in the corner of an axes."""
    ax.text(x, y, s, transform=ax.transAxes, fontsize=LABEL_FS, fontweight='bold',
            va='bottom', ha='left')


def flabel(fig, s, x, y):
    fig.text(x, y, s, fontsize=LABEL_FS, fontweight='bold', va='top', ha='left')


def save(fig, name):
    fig.canvas.draw()
    bb = fig.get_tightbbox(fig.canvas.get_renderer())
    w, h = bb.width, bb.height
    for ext in ('png', 'svg', 'pdf'):
        fig.savefig(f'{OUT}/{name}.{ext}', bbox_inches='tight', pad_inches=0.04, facecolor='white')
    plt.close(fig)
    flag = '' if (w <= PAGE_W + 0.05 and h <= PAGE_H - 1.0) else '  <-- exceeds page'
    print(f'saved {name}  {w:.2f} x {h:.2f} in{flag}')


def arrow(ax, x0, y0, x1, y1, color=RED, lw=2.0, both=False, hw=6, **kw):
    style = '<|-|>' if both else '-|>'
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle=f'{style},head_width={hw/20},head_length={hw/12}',
                                color=color, lw=lw, shrinkA=0, shrinkB=0), **kw)


def blank(ax):
    ax.set_axis_off()


# ------------------------------------------------------------------ optics
HC = 12398.42  # eV A


def lam(E):
    return HC / E  # Angstrom


def _gauss(E, c, s):
    return np.exp(-0.5 * ((E - c) / s) ** 2) / (s * np.sqrt(2 * np.pi))


def znpc_tables():
    bb = pd.read_csv(f'{DATA}/buildingblock.csv')
    nx = pd.read_csv(f'{DATA}/nexafs.csv')
    mu = pd.read_csv(f'{DATA}/igor_mu.csv')
    return bb, nx, mu


def znpc_mass_absorption(E, gamma_deg=None, component='xx'):
    """Mass absorption (cm2/g) of ZnPc from the refined building-block model.

    gamma_deg None returns the measured film tensor (Chapter 3 film), else the
    film tensor rebuilt from the molecular tensor (4 x mol) at tilt gamma
    measured from the substrate normal to the macrocycle normal.
    """
    bb, nx, mu = znpc_tables()
    step_e = nx[nx.theta_deg == nx.theta_deg.unique()[0]][['energy', 'dft_step']].values
    Eb, mub = mu.energy.values, mu.mu.values
    cont = np.interp(E, Eb, mub)
    inside = (E >= step_e[0, 0]) & (E <= step_e[-1, 0])
    cont = np.where(inside, np.interp(E, step_e[:, 0], step_e[:, 1]), cont)
    out = np.zeros_like(E, dtype=float)
    for r in bb.itertuples():
        if gamma_deg is None:
            a = r.film_xx if component == 'xx' else r.film_zz
        else:
            g = np.radians(gamma_deg)
            mxx, mzz = 4 * r.mol_xx, 4 * r.mol_zz
            if component == 'xx':
                a = 0.5 * (mxx * (1 + np.cos(g) ** 2) + mzz * np.sin(g) ** 2)
            elif component == 'zz':
                a = mxx * np.sin(g) ** 2 + mzz * np.cos(g) ** 2
            else:
                a = (2 * mxx + mzz) / 3
        out += a * _gauss(E, r.location, r.sigma_ev)
    return out + cont


def beta_from_mu(E, mu_mass, rho):
    return rho * mu_mass * (lam(E) * 1e-8) / (4 * np.pi)


def kk_delta(E, beta, E_eval):
    """delta(E) = (2/pi) P int E' beta(E') / (E^2 - E'^2) dE', beta piecewise linear."""
    a, b = E[:-1], E[1:]
    s = (beta[1:] - beta[:-1]) / (b - a)
    p = beta[:-1] - s * a
    out = np.empty_like(E_eval, dtype=float)
    for k, e in enumerate(E_eval):
        def F(x):
            with np.errstate(divide='ignore', invalid='ignore'):
                l1 = np.log(np.abs(e * e - x * x))
                l2 = np.log(np.abs((e + x) / (e - x)))
            l1 = np.where(np.isfinite(l1), l1, np.log(2 * e))  # singular part cancels between neighbours
            l2 = np.where(np.isfinite(l2), l2, np.log(2 * e))
            return p_ * (-0.5 * l1) + s_ * (-x + 0.5 * e * l2)
        p_, s_ = p, s
        out[k] = (2 / np.pi) * np.sum(F(b) - F(a))
    return out


def znpc_index(E_eval, rho=1.64, gamma_deg=None):
    """Return dict of complex n for xx and zz on E_eval, via KK on a wide grid."""
    _, _, mu = znpc_tables()
    wide = np.unique(np.concatenate([mu.energy.values[(mu.energy < 268) | (mu.energy > 332)],
                                     np.linspace(268, 332, 3201)]))
    res = {}
    for c in ('xx', 'zz'):
        b_w = beta_from_mu(wide, znpc_mass_absorption(wide, gamma_deg, c), rho)
        d = kk_delta(wide, b_w, E_eval)
        b = beta_from_mu(E_eval, znpc_mass_absorption(E_eval, gamma_deg, c), rho)
        res[c] = 1 - d + 1j * b
    return res


# ------------------------------------------------------------------ reflectivity
def _kz(k0, kx, exx, ezz, pol):
    if pol == 's':
        kz = np.sqrt(exx * k0 ** 2 - kx ** 2 + 0j)
    else:
        kz = np.sqrt(exx / ezz + 0j) * np.sqrt(ezz * k0 ** 2 - kx ** 2 + 0j)
    return np.where(kz.imag < 0, -kz, kz)


def reflectivity(q, E, layers, pol='s', rough='nc'):
    """Exact specular reflectivity of a stack of uniaxial layers (optic axis along z).

    layers: list of (n_xx, n_zz, thickness_A, sigma_A) from ambient (first, thickness ignored)
    to substrate (last, thickness ignored); sigma is the roughness of the interface on top of
    each layer. For a tensor diagonal in the film frame s and p decouple, and this 2x2
    recursion is identical to the 4x4 Berreman result.
    """
    k0 = 2 * np.pi / lam(E)
    sin_t = q / (2 * k0)
    kx = k0 * np.sqrt(1 - sin_t ** 2)
    kzs, exs = [], []
    for nxx, nzz, d, sig in layers:
        exx, ezz = nxx ** 2, nzz ** 2
        kzs.append(_kz(k0, kx, exx, ezz, pol)); exs.append(exx)
    X = np.zeros_like(q, dtype=complex)
    for j in range(len(layers) - 2, -1, -1):
        ki, kj = kzs[j], kzs[j + 1]
        if pol == 's':
            r = (ki - kj) / (ki + kj)
        else:
            r = (ki / exs[j] - kj / exs[j + 1]) / (ki / exs[j] + kj / exs[j + 1])
        sig = layers[j + 1][3]
        if rough == 'none' or sig == 0:
            pass
        elif rough == 'nc':
            r = r * np.exp(-2 * ki * kj * sig ** 2)
        elif rough == 'dw':
            r = r * np.exp(-2 * ki ** 2 * sig ** 2)
        if j + 1 == len(layers) - 1:
            X = r
        else:
            ph = np.exp(2j * kj * layers[j + 1][2])
            X = (r + X * ph) / (1 + r * X * ph)
    return np.abs(X) ** 2


def graded_layers(layers, dz=1.0, nsig=4):
    """Replace every rough interface by an erf profile cut into slices of thickness dz."""
    z_int, depth = [], 0.0
    for i in range(1, len(layers)):
        z_int.append(depth)
        if i < len(layers) - 1:
            depth += layers[i][2]
    total = depth
    lo = -nsig * max(l[3] for l in layers[1:]) - 5
    hi = total + nsig * max(l[3] for l in layers[1:]) + 5
    zc = np.arange(lo, hi, dz) + dz / 2
    nxx = np.full_like(zc, layers[0][0], dtype=complex)
    nzz = np.full_like(zc, layers[0][1], dtype=complex)
    for i in range(1, len(layers)):
        sig = max(layers[i][3], 1e-6)
        w = 0.5 * (1 + erf((zc - z_int[i - 1]) / (np.sqrt(2) * sig)))
        nxx = nxx + (layers[i][0] - layers[i - 1][0]) * w
        nzz = nzz + (layers[i][1] - layers[i - 1][1]) * w
    sl = [(layers[0][0], layers[0][1], 0, 0)] + [(a, b, dz, 0) for a, b in zip(nxx, nzz)] + \
         [(layers[-1][0], layers[-1][1], 0, 0)]
    return sl, zc, nxx, nzz


SI_N = {283.7: 1 - 4.9e-3 + 1j * 5.5e-4, 285.1: 1 - 4.7e-3 + 1j * 5.4e-4}  # bare-atom Si, approximate


def grid_labels(fig, rows, dy=0.0, pad=0.0):
    """Place bold panel letters so every column shares one x and every row shares one y.

    rows is a list of rows, each a list of (axes, letter) pairs ordered by column. The x of a column
    is the leftmost tight-bbox edge of its axes (tick labels included), the y of a row is the
    highest axes top in that row, so letters line up in a clean grid.
    """
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    inv = fig.transFigure.inverted()
    ncol = max(len(rw) for rw in rows)
    xs = []
    for c in range(ncol):
        x0 = min(inv.transform(ax.get_tightbbox(r))[0, 0] for rw in rows if c < len(rw) for ax, _ in [rw[c]])
        xs.append(x0 - pad)
    for rw in rows:
        y = max(min(inv.transform(ax.get_tightbbox(r))[1, 1], ax.get_position().y1 + 0.08) for ax, _ in rw) + dy
        for c, (ax, s) in enumerate(rw):
            fig.text(xs[c], y, s, fontsize=LABEL_FS, fontweight='bold', va='top', ha='left')
