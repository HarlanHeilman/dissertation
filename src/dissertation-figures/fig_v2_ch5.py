"""Revision 2. Fig. 5.3 (angle convention with incident wave) and Fig. 5.9 (simplified architecture)."""
from figlib import *
from matplotlib.patches import Polygon, Arc, FancyBboxPatch


def box(ax, x, y, w, h, text, ec=BLACK, fs=9, fc='white', bold=False):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle='round,pad=0.02,rounding_size=0.12',
                                fc=fc, ec=ec, lw=1.2))
    ax.text(x, y, text, ha='center', va='center', fontsize=fs, fontweight='bold' if bold else 'normal')


# ================================================================ 5.3
fig, ax = plt.subplots(figsize=(5.2, 3.2)); fig.subplots_adjust(0, 0, 1, 1); blank(ax); ax.set_xlim(0, 10); ax.set_ylim(0, 6.6)
P = np.array([[0.8, 0.6], [6.6, 0.6], [9.2, 2.4], [3.4, 2.4]])
ax.add_patch(Polygon(P, fc=LGRAY, ec=BLACK, lw=1.1))
o = np.array([5.0, 1.5])
arrow(ax, *o, 5.0, 6.3, color=BLACK, lw=1.4); ax.text(5.12, 6.15, r'$\hat{n}$', fontsize=9.5)
arrow(ax, *o, 7.7, 1.5, color=BLACK, lw=1.1); ax.text(7.8, 1.32, r'$\hat{x}$', fontsize=9.5)
# incident wave as a squiggle travelling toward the sample, oscillating along E
kdir = np.array([1.0, -0.42]); kdir /= np.linalg.norm(kdir)
Edir = np.array([0.55, 0.835]); Edir /= np.linalg.norm(Edir)
start = o - 4.2 * kdir
s = np.linspace(0, 3.6, 400)
path = start[None, :] + s[:, None] * kdir[None, :] + 0.32 * np.sin(2 * np.pi * s / 0.6)[:, None] * Edir[None, :]
ax.plot(path[:, 0], path[:, 1], color=RED, lw=1.6)
arrow(ax, *(start + 3.6 * kdir), *(o - 0.15 * kdir), color=RED, lw=1.4)
ax.text(*(start + [0.0, 0.55]), r'incident beam, $\mathbf{k}$', fontsize=8, color=RED)
# E vector at the sample and its angles
E_tip = o + 3.2 * Edir
arrow(ax, *o, *E_tip, color=RED, lw=2.4)
ax.text(E_tip[0] + 0.1, E_tip[1] + 0.05, r'$\mathbf{E}$', fontsize=11, color=RED)
proj = o + np.array([3.2 * Edir[0], 0.55])
ax.plot([E_tip[0], proj[0]], [E_tip[1], proj[1]], color=GRAY, ls=':', lw=1.1)
ax.plot([o[0], proj[0]], [o[1], proj[1]], color=GRAY, ls='--', lw=1.1)
ax.add_patch(Arc(o, 2.0, 2.0, theta1=np.degrees(np.arctan2(Edir[1], Edir[0])), theta2=90, color=BLACK, lw=1.2))
ax.text(5.25, 2.75, 'θ', fontsize=10)
ax.add_patch(Arc(o, 3.4, 1.0, theta1=0, theta2=43.8, color=BLACK, lw=1.2))
ax.text(6.85, 1.6, 'φ', fontsize=10)
ax.text(0.9, 0.15, r'θ, polar angle of $\mathbf{E}$ from the sample normal.   φ, azimuth of $\mathbf{E}$ in the sample plane.',
        fontsize=7.5, color=GRAY)
save(fig, 'fig5-03_angle-convention')

# ================================================================ 5.9
fig = plt.figure(figsize=(6.5, 4.5))
ax = fig.add_axes([0.0, 0.3, 1.0, 0.7]); blank(ax); ax.set_xlim(0, 12), ax.set_ylim(0.7, 6.1)
ax.add_patch(FancyBboxPatch((3.6, 1.0), 4.4, 5.0, boxstyle='round,pad=0.02,rounding_size=0.15', fc='#F4F4F4',
                            ec=BLACK, lw=1.2))
ax.text(5.8, 5.55, 'X-ray Atlas', ha='center', fontsize=8.5, fontweight='bold')
box(ax, 5.8, 4.5, 3.6, 0.9, 'database and files')
box(ax, 5.8, 3.2, 3.6, 0.9, 'web application')
box(ax, 5.8, 1.9, 3.6, 0.9, 'REST API /api/v1', ec=RED)
box(ax, 1.5, 4.5, 2.4, 0.9, 'ORCID sign in')
box(ax, 1.5, 1.9, 2.4, 0.9, 'Zenodo DOIs')
box(ax, 10.3, 4.8, 2.6, 0.9, 'browser')
box(ax, 10.3, 3.2, 2.6, 0.9, 'Python xrayatlas', ec=RED)
box(ax, 10.3, 1.6, 2.6, 0.9, 'CLI xatlas', ec=RED)
for (x0, y0, x1, y1) in ((2.7, 4.5, 3.95, 4.5), (2.7, 1.9, 3.95, 1.9), (7.65, 3.4, 9.0, 4.6), (7.65, 1.9, 9.0, 3.1),
                         (7.65, 1.8, 9.0, 1.6)):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle='<|-|>', color=BLACK, lw=1.1))
b = fig.add_axes([0.0, 0.0, 1.0, 0.27]); blank(b); b.set_xlim(0, 8), b.set_ylim(0, 3.2)
chain = [(1.0, 'dataset\nrevision'), (2.95, 'default\nmodel'), (4.9, 'your fork\nversion 1, 2'), (6.85, 'citation')]
for k, (x, t) in enumerate(chain):
    box(b, x, 2.2, 1.6, 1.1, t, ec=RED if k == 2 else BLACK, fs=7.5)
for (x0, x1) in ((1.82, 2.13), (3.77, 4.08), (5.72, 6.03)):
    arrow(b, x0, 2.2, x1, 2.2, color=BLACK, lw=1.1, hw=4)
b.text(3.925, 0.75, 'models pin a dataset revision, forks keep their parents,\nand a citation lists the model, the datasets, and every ancestor',
       ha='center', fontsize=7.5, color=GRAY)
fig.text(0.0, 0.99, 'a', fontsize=LABEL_FS, fontweight='bold', va='top')
fig.text(0.0, 0.27, 'b', fontsize=LABEL_FS, fontweight='bold', va='top')
save(fig, 'fig5-09_architecture')
