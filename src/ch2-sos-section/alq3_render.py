import sys; sys.path.insert(0, "/home/claude/work/figsrc")
from style import *
import numpy as np
from ase.io import read
from matplotlib.patches import Circle, FancyArrowPatch, Polygon
from matplotlib.colors import to_rgb
OUT = "/home/claude/work/figs/"
COL = {"C": "#3A3F44", "H": "#E4E0DA", "N": BLUE, "O": CRIMSON, "Al": "#A7ADB2"}
RAD = {"C": 0.34, "H": 0.20, "N": 0.36, "O": 0.36, "Al": 0.52}

def frame(mu, tilt_deg=20, spin_deg=0):
    """Rotation taking the dipole to screen +y, then tipping the view down by tilt."""
    z = mu / np.linalg.norm(mu)
    a = np.array([1.0, 0.3, 0.2]); a -= a.dot(z) * z; a /= np.linalg.norm(a)
    b = np.cross(z, a)
    R = np.array([a, z, b])  # rows: screen x, screen y (dipole), depth
    s, t = np.radians(spin_deg), np.radians(tilt_deg)
    Ry = np.array([[np.cos(s), 0, np.sin(s)], [0, 1, 0], [-np.sin(s), 0, np.cos(s)]])
    Rx = np.array([[1, 0, 0], [0, np.cos(t), -np.sin(t)], [0, np.sin(t), np.cos(t)]])
    return Rx @ Ry @ R

def shade(c, f):
    r = np.array(to_rgb(c)); return tuple(np.clip(r + (1 - r) * f, 0, 1)) if f > 0 else tuple(r * (1 + f))

def render(ax, name, spin, tilt=18, scale=1.0):
    at = read(f"/home/claude/work/alq3/{name}.xyz")
    mu = np.load(f"/home/claude/work/alq3/{name}_dipole.npy")
    sym = at.get_chemical_symbols(); P = at.positions - at.positions[0]
    R = frame(mu, tilt, spin); Q = (R @ P.T).T * scale
    zr = Q[:, 2]; zn = (zr - zr.min()) / np.ptp(zr)
    d = np.linalg.norm(P[:, None] - P[None], axis=-1)
    bonds = []
    for i in range(len(sym)):
        for j in range(i + 1, len(sym)):
            lim = 2.25 if "Al" in (sym[i], sym[j]) else (1.25 if "H" in (sym[i], sym[j]) else 1.65)
            if d[i, j] < lim: bonds.append((i, j))
    items = [("a", zr[i], i) for i in range(len(sym))] + [("b", (zr[i] + zr[j]) / 2 - 0.01, (i, j)) for i, j in bonds]
    for kind, z, k in sorted(items, key=lambda t: t[1]):
        fog = -0.35 * (1 - zn[k] if kind == "a" else 1 - (zn[k[0]] + zn[k[1]]) / 2)
        if kind == "b":
            i, j = k; m = (Q[i] + Q[j]) / 2
            for a_, b_ in ((i, m), (j, m)):
                pa = Q[a_] if isinstance(a_, (int, np.integer)) else a_
                ax.plot([pa[0], b_[0]], [pa[1], b_[1]], color=shade(COL[sym[a_]], fog * 0.6 + 0.05), lw=3.2 * scale, solid_capstyle="round", zorder=z)
        else:
            i = k; r = RAD[sym[i]] * scale; c = COL[sym[i]]
            ax.add_patch(Circle(Q[i][:2], r, fc=shade(c, fog * 0.6), ec=shade(c, -0.45), lw=0.5, zorder=z))
            ax.add_patch(Circle(Q[i][:2] + np.array([-0.3, 0.3]) * r, 0.38 * r, fc=shade(c, 0.45), ec="none", alpha=0.7, zorder=z + 1e-4))
    top = Q[:, 1].max()
    m = np.linalg.norm(mu) * 4.80321
    L = 0.55 * m
    xa = Q[:, 0].max() + 1.1
    ax.add_patch(FancyArrowPatch((xa, -L / 2), (xa, L / 2), arrowstyle="-|>,head_length=0.55,head_width=0.32", mutation_scale=18, lw=3.2, color=CLAY, zorder=100))
    ax.text(xa + 0.45, 0, rf"$\mu$ = {m:.1f} D", ha="left", va="center", fontsize=12, color=CLAY)
    return Q, m

if __name__ == "__main__":
    fig = plt.figure(figsize=(6.3, 2.75))
    for k, (name, spin, lab, sub) in enumerate((("mer", 25, "mer-Alq3", "O atoms in one plane"), ("fac", 55, "fac-Alq3", "O atoms on one face"))):
        ax = fig.add_axes([0.0 + 0.5 * k, 0.17, 0.5, 0.82])
        Q, m = render(ax, name, spin, scale=0.82)
        ax.set_xlim(-5.6, 10.0); ax.set_ylim(-5.0, 5.2); ax.set_aspect("equal"); ax.axis("off")
        ax.text(0.35, -0.02, lab, transform=ax.transAxes, ha="center", va="top", fontsize=13.5, color=INK)
        ax.text(0.35, -0.115, sub, transform=ax.transAxes, ha="center", va="top", fontsize=10.5, color=SLATE)
    fig.text(0.995, 0.005, "GFN2-xTB geometries and dipoles", ha="right", va="bottom", fontsize=9, color=SLATE, style="italic")
    fig.savefig(OUT + "alq3-isomers-3d.png", dpi=300)
