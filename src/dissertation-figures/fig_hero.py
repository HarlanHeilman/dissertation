"""Hero schematics, first round. Fig. 1.1 (organic materials across length scales and the measurement gap)
and Fig. 2.1 (packing sets emergent properties). Flat line work, red for the quantity of interest, gray for context."""
import sys
import numpy as np
from figlib import *
from matplotlib.patches import FancyBboxPatch, Rectangle, Ellipse, Circle, Polygon, PathPatch, ConnectionPatch, FancyArrowPatch
from matplotlib.path import Path
from matplotlib import transforms
from scipy.ndimage import gaussian_filter

DGRAY = '#5E5E5E'
MGRAY = '#A8A8A8'
PALE = '#EFEFEF'
DRED = '#8E1512'
PRED = '#F6D3D2'
OUTDIR = OUT


def slab(ax, x, y, L, t=0.22, ang=0.0, fc=DGRAY, ec='none', z=3, lobes=False, lc=None, lw=0.0):
    """A planar molecule seen edge-on, drawn as a rounded slab of length L centered at (x, y), rotated by ang degrees.
    Optional p-orbital lobes stand normal to the slab."""
    tr = transforms.Affine2D().rotate_deg_around(x, y, ang) + ax.transData
    p = FancyBboxPatch((x - L / 2, y - t / 2), L, t, boxstyle=f'round,pad=0,rounding_size={t/2}',
                       fc=fc, ec=ec, lw=lw, zorder=z, transform=tr)
    ax.add_patch(p)
    if lobes:
        c = lc or fc
        for s in (-0.28, 0.0, 0.28):
            for sgn in (1, -1):
                e = Ellipse((x + s * L, y + sgn * (t / 2 + 0.11)), 0.1, 0.2, fc=c if sgn > 0 else 'white',
                            ec=c, lw=0.6, zorder=z - 1, transform=tr)
                ax.add_patch(e)
    return p


def harrow(ax, x0, y0, x1, y1, color=RED, lw=1.6, hw=5, z=6):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0), zorder=z,
                arrowprops=dict(arrowstyle=f'-|>,head_width={hw/20},head_length={hw/12}', color=color, lw=lw,
                                shrinkA=0, shrinkB=0))


def wavy(ax, x0, y0, x1, y1, color=RED, lw=1.0, n=4, amp=0.07, head=True, z=6):
    d = np.array([x1 - x0, y1 - y0]); L = np.hypot(*d); u = d / L; nrm = np.array([-u[1], u[0]])
    s = np.linspace(0, L * 0.82, 120)
    pts = np.array([x0, y0]) + np.outer(s, u) + np.outer(amp * np.sin(2 * np.pi * n * s / (L * 0.82)), nrm)
    ax.plot(pts[:, 0], pts[:, 1], color=color, lw=lw, zorder=z, solid_capstyle='round')
    if head:
        harrow(ax, *pts[-1], x1, y1, color=color, lw=lw, hw=4, z=z)


def caption(ax, x, y, s, size=7.5, color=BLACK, weight='normal', ha='center', va='top', **kw):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va, **kw)


# ======================================================================================== Fig. 1.1
def fig_1_1():
    fig = plt.figure(figsize=(6.5, 2.17))
    ax = fig.add_axes([0, 0, 1, 1]); blank(ax)
    W, H = 26.0, 9.8
    ax.set_xlim(0, W); ax.set_ylim(1.1, H); ax.set_aspect('equal')

    # four stages, left to right, joined by zoom cones
    boxes = [(0.3, 3.3, 5.6, 5.6), (7.1, 3.3, 5.6, 5.6), (13.9, 3.3, 5.6, 5.6), (20.7, 3.3, 5.0, 5.6)]
    titles = ['Technologies', 'Nanostructure', 'Buried interface', 'Molecular state']
    scales = ['mm to µm', '100 nm', '< 10 nm', '< 1 nm']
    for (x, y, w, h), t, sc in zip(boxes, titles, scales):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.35', fc='white',
                                    ec=BLACK, lw=0.8, zorder=1))
        caption(ax, x + w / 2, y + h + 0.95, t, size=8.5, weight='bold', va='center')
        caption(ax, x + w / 2, y + h + 0.35, sc, size=7, color=DGRAY, va='center')

    # zoom cones from a small square in each box to the next box
    zooms = [(4.4, 4.9, 0.7), (9.6, 3.75, 0.9), (15.3, 4.45, 0.9)]
    for (zx, zy, zs), (nx, ny, nw, nh) in zip(zooms, boxes[1:]):
        ax.add_patch(Rectangle((zx, zy), zs, zs, fc='none', ec=RED, lw=0.9, zorder=8))
        for (px, py), (qx, qy) in [((zx + zs, zy + zs), (nx, ny + nh)), ((zx + zs, zy), (nx, ny))]:
            ax.plot([px, qx], [py, qy], color=RED, lw=0.6, ls=(0, (2, 1.5)), zorder=0)

    # ---- stage 1, four technologies on a 2 x 2 grid centered in the box
    x0, y0 = 0.3, 3.3
    c1, c2 = x0 + 2.8 - 1.35, x0 + 2.8 + 1.35          # column centers
    rt, rb = y0 + 3.75, y0 + 1.05                         # bottom edge of the top and bottom icon rows
    lt, lb = y0 + 3.45, y0 + 0.78                         # label tops of the two rows
    iw = 1.9
    # devices, a layered stack
    for i_, c in enumerate([MGRAY, RED, DGRAY, LGRAY]):
        ax.add_patch(Rectangle((c1 - iw / 2, rt + i_ * 0.32), iw, 0.32, fc=c, ec='white', lw=0.4, zorder=2))
    caption(ax, c1, lt, 'devices', size=6.5, color=DGRAY)
    # lithography, resist lines on a substrate
    ax.add_patch(Rectangle((c2 - iw / 2, rt), iw, 0.15, fc=LGRAY, ec='none', zorder=2))
    for k in range(4):
        ax.add_patch(Rectangle((c2 - iw / 2 + 0.12 + k * 0.48, rt + 0.15), 0.27, 1.13, fc=DGRAY, ec='none', zorder=2))
    caption(ax, c2, lt, 'lithography', size=6.5, color=DGRAY)
    # membranes and carriers
    mc = (c1, rb + 0.85)
    ax.add_patch(Circle(mc, 0.82, fc='none', ec=DGRAY, lw=2.6, zorder=2))
    ax.add_patch(Circle(mc, 0.82, fc='none', ec='white', lw=0.7, zorder=3))
    for k in range(5):
        a_ = 2 * np.pi * k / 5 + 0.3
        ax.add_patch(Circle((mc[0] + 0.38 * np.cos(a_), mc[1] + 0.38 * np.sin(a_)), 0.11, fc=RED, ec='none', zorder=3))
    caption(ax, c1, lb, 'membranes', size=6.5, color=DGRAY)
    # thin films, the region zoomed next
    rng = np.random.default_rng(3)
    f = gaussian_filter(rng.standard_normal((60, 60)), 4.5)
    ax.imshow(f > 0, extent=(c2 - 0.85, c2 + 0.85, rb, rb + 1.7), cmap=mpl.colors.ListedColormap([LGRAY, LRED]),
              interpolation='bicubic', zorder=2)
    caption(ax, c2, lb, 'thin films', size=6.5, color=DGRAY)

    # ---- stage 2, nanostructure (two-phase morphology)
    x0, y0 = 7.1, 3.3
    f = gaussian_filter(rng.standard_normal((126, 140)), 7)
    ax.imshow(f > 0.0, extent=(x0 + 0.35, x0 + 5.25, y0 + 0.8, y0 + 5.25),
              cmap=mpl.colors.ListedColormap([PALE, LRED]), interpolation='bicubic', zorder=2)
    ax.contour(np.linspace(x0 + 0.35, x0 + 5.25, 140), np.linspace(y0 + 5.25, y0 + 0.8, 126), f, levels=[0],
               colors=[DRED], linewidths=0.7, zorder=3)
    ax.add_patch(Rectangle((x0 + 0.35, y0 + 0.35), 4.9, 0.45, fc=LGRAY, ec='none', zorder=4))
    caption(ax, x0 + 0.5, y0 + 0.58, 'substrate', size=6.5, color=DGRAY, ha='left', va='center', zorder=5)

    # ---- stage 3, buried interface between two layers, interfacial molecules in another state
    x0, y0 = 13.9, 3.3
    ax.add_patch(Rectangle((x0 + 0.3, y0 + 0.3), 5.0, 1.15, fc=LGRAY, ec='none', zorder=1))
    caption(ax, x0 + 0.5, y0 + 0.55, 'substrate', size=6.5, color=DGRAY, ha='left', va='center')
    # interfacial molecules lying down, red
    for i in range(7):
        slab(ax, x0 + 0.85 + i * 0.68, y0 + 1.68, 0.56, t=0.16, ang=8 * (-1) ** i, fc=RED, z=4)
    # bulk molecules standing
    for r in range(3):
        for i in range(10):
            slab(ax, x0 + 0.65 + i * 0.47, y0 + 2.75 + r * 0.9, 0.72, t=0.15, ang=90 + 12 * (-1) ** (i + r), fc=DGRAY, z=4)
    ax.add_patch(Rectangle((x0 + 0.3, y0 + 1.38), 5.0, 0.62, fc=PRED, ec='none', zorder=2))
    caption(ax, x0 + 5.2, y0 + 2.12, '?', size=11, color=RED, weight='bold', ha='right', va='bottom')

    # ---- stage 4, a molecule and its state, orientation and electronic structure
    x0, y0 = 20.7, 3.3
    cx, cy = x0 + 1.45, y0 + 2.6
    th = np.radians(np.arange(0, 360, 60))
    hx, hy = cx + 1.0 * np.cos(th), cy + 0.4 * np.sin(th)
    ax.add_patch(Polygon(np.c_[hx, hy], closed=True, fc='white', ec=BLACK, lw=1.3, zorder=4))
    for px, py in zip(hx, hy):
        ax.add_patch(Ellipse((px, py + 0.36), 0.2, 0.5, fc=RED, ec=RED, lw=0.6, zorder=5))
        ax.add_patch(Ellipse((px, py - 0.36), 0.2, 0.5, fc='white', ec=RED, lw=0.6, zorder=3))
    harrow(ax, cx, cy, cx, cy + 2.0, color=RED, lw=1.6, hw=5)
    caption(ax, cx + 0.2, cy + 1.85, r'$\mathbf{\mu}$', size=9, color=RED, ha='left', va='center')
    caption(ax, cx, y0 + 1.0, 'orientation', size=6.5, color=DGRAY)
    # energy levels
    lx = x0 + 3.2
    for yy, lab, c in [(y0 + 1.55, 'C 1s', BLACK), (y0 + 3.5, r'$\pi^*$', RED), (y0 + 4.2, r'$\sigma^*$', BLACK)]:
        ax.plot([lx, lx + 0.8], [yy, yy], color=c, lw=1.4 if c == RED else 1.1, solid_capstyle='butt', zorder=4)
        caption(ax, lx + 0.9, yy, lab, size=7, color=c, ha='left', va='center')
    harrow(ax, lx + 0.4, y0 + 1.65, lx + 0.4, y0 + 3.4, color=RED, lw=1.2, hw=4)
    caption(ax, lx + 0.4, y0 + 1.0, 'electronic\nstate', size=6.5, color=DGRAY, va='top', linespacing=0.95)

    # ---- measurement reach along the bottom
    yb = 2.25
    ax.plot([0.3, 25.7], [yb + 0.55, yb + 0.55], color=LGRAY, lw=0.6, zorder=0)
    bars = [(0.3, 12.7, 'X-ray and neutron scattering, microscopy', DGRAY, 'structure'),
            (20.7, 25.7, 'spectroscopy', DGRAY, 'state')]
    for xa, xb, lab, c, what in bars:
        ax.add_patch(FancyBboxPatch((xa, yb - 0.32), xb - xa, 0.5, boxstyle='round,pad=0,rounding_size=0.25', fc=c, ec='none', zorder=2))
        caption(ax, (xa + xb) / 2, yb - 0.07, lab, size=6.8, color='white', va='center')
        caption(ax, (xa + xb) / 2, yb - 0.6, what, size=6.8, color=DGRAY, va='top', style='italic')
    ax.add_patch(FancyBboxPatch((13.9, yb - 0.32), 5.6, 0.5, boxstyle='round,pad=0,rounding_size=0.25', fc='white',
                                ec=RED, lw=1.0, ls=(0, (3, 2)), zorder=2))
    caption(ax, 16.7, yb - 0.07, 'structure and state', size=6.8, color=RED, va='center', weight='bold')
    caption(ax, 16.7, yb - 0.6, 'needed together, not reached', size=6.8, color=RED, va='top', style='italic')
    return fig


# ======================================================================================== Fig. 2.1
METAL = '#6F7F91'      # opaque metal electrode
TCO = '#C9D3DD'        # transparent conductor
GLASS = '#EEF2F5'


def dipole(ax, x, y, L, vertical=False, color=RED, lw=1.3, z=7):
    d = (0, L / 2) if vertical else (L / 2, 0)
    ax.annotate('', xy=(x + d[0], y + d[1]), xytext=(x - d[0], y - d[1]), zorder=z,
                arrowprops=dict(arrowstyle='<|-|>,head_width=0.18,head_length=0.28', color=color, lw=lw, shrinkA=0, shrinkB=0))


def layer(ax, x, y, w, h, fc, text=None, tc='white', size=6.2, z=1):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec='none', zorder=z))
    if text:
        caption(ax, x + 0.12, y + h / 2, text, size=size, color=tc, ha='left', va='center', zorder=z + 5)


def fig_2_1():
    W, Y0, Y1 = 26.0, 0.45, 8.1
    fig = plt.figure(figsize=(6.5, 6.5 * (Y1 - Y0) / W))
    ax = fig.add_axes([0, 0, 1, 1]); blank(ax)
    ax.set_xlim(0, W); ax.set_ylim(Y0, Y1); ax.set_aspect('equal')
    pw, gap = 5.9, 0.73
    X = [0.25 + i * (pw + gap) for i in range(4)]
    heads = ['In-plane transport', 'Vertical transport', 'Light outcoupling', 'Interfacial hybridization']
    devs = ['organic transistor', 'organic photovoltaic', 'organic light-emitting diode', 'organic spin valve']
    for x, h, dv, lab in zip(X, heads, devs, 'abcd'):
        caption(ax, x + pw / 2, 1.55, h, size=8.2, weight='bold', va='center')
        caption(ax, x + pw / 2, 0.95, dv, size=7, color=DGRAY, va='center')
        ax.text(x, Y1 - 0.05, lab, fontsize=LABEL_FS, fontweight='bold', va='top', ha='left')
    yb = 2.6

    # ---- a, organic transistor, edge-on molecules between source and drain on a gate dielectric
    x = X[0]
    layer(ax, x, yb, pw, 0.42, METAL, 'gate')
    layer(ax, x, yb + 0.42, pw, 0.45, LGRAY, 'dielectric', tc=DGRAY)
    for xs, t in ((x + 0.05, 'S'), (x + pw - 1.05, 'D')):
        ax.add_patch(Rectangle((xs, yb + 0.87), 1.0, 1.45, fc=METAL, ec='none', zorder=2))
        caption(ax, xs + 0.5, yb + 1.6, t, size=7.5, color='white', va='center', weight='bold', zorder=6)
    for i in range(10):
        slab(ax, x + 1.38 + i * 0.36, yb + 1.55, 1.2, t=0.13, ang=90, fc=DGRAY, z=3)
    harrow(ax, x + 1.25, yb + 2.5, x + pw - 1.25, yb + 2.5, color=RED, lw=1.5)
    caption(ax, x + pw / 2, yb + 2.65, 'charge', size=6.5, color=RED, va='bottom')
    # key, in the free space of panel a
    kx, ky = x + 0.35, yb + 4.65
    slab(ax, kx + 0.55, ky, 1.0, t=0.14, fc=DGRAY, z=3)
    caption(ax, kx + 1.3, ky, 'molecule', size=6.8, ha='left', va='center')
    dipole(ax, kx + 0.55, ky - 0.62, 1.0, lw=1.1)
    caption(ax, kx + 1.3, ky - 0.62, 'transition dipole', size=6.8, ha='left', va='center')

    # ---- b, organic photovoltaic, face-on donor under face-on acceptor, charge separating at the heterointerface
    x = X[1]
    w = pw
    pitch, nrow = 0.4, 4
    band = nrow * pitch + 0.1
    layer(ax, x, yb, w, 0.36, GLASS, 'glass', tc=DGRAY, size=6.0)
    layer(ax, x, yb + 0.36, w, 0.28, TCO, 'ITO', tc=DGRAY, size=6.0)
    yd0 = yb + 0.64; yd1 = yd0 + band; ya0 = yd1; ya1 = ya0 + band
    layer(ax, x, yd0, w, band, '#E9E9E9')
    layer(ax, x, ya0, w, band, '#F9F9F9')
    layer(ax, x, ya1, w, 0.36, METAL, 'Al', size=6.0)
    cols = [x + 0.72 + k * 1.48 for k in range(4)]
    rd = [yd0 + 0.25 + r * pitch for r in range(nrow)]          # donor rows, bottom to top
    ra = [ya0 + 0.25 + r * pitch for r in range(nrow)]          # acceptor rows, bottom to top
    for cx_ in cols:
        for yy in rd:
            slab(ax, cx_, yy, 1.2, t=0.14, fc=DGRAY, z=3)
        for yy in ra:
            slab(ax, cx_, yy, 1.2, t=0.14, fc=MGRAY, z=3)
    for yy, fc, t in ((rd[1], '#E9E9E9', 'donor'), (ra[2], '#F9F9F9', 'acceptor')):
        ax.add_patch(Rectangle((cols[3] - 0.75, yy - 0.12), x + w - (cols[3] - 0.75), 0.24, fc=fc, ec='none', zorder=8))
        ax.text(cols[3] + 0.02, yy, t, fontsize=6.6, color=BLACK, ha='center', va='center', zorder=9)
    # absorption, light enters through the glass into the donor
    for dx in (0.72, 2.2, 3.68):
        wavy(ax, x + dx - 0.25, yb - 0.5, x + dx, yb + 0.12, color=RED, lw=0.9, amp=0.05, n=2.5)
    caption(ax, x + 4.0, yb - 0.25, r'$h\nu$', size=7.5, color=RED, ha='left', va='center')
    # charge separation across the interface, electron hops into the acceptor stack, hole back down the donor stack
    cx_ = cols[1]
    def charge(px, py, sign, c):
        ax.add_patch(Circle((px, py), 0.16, fc=c, ec='white', lw=0.7, zorder=9))
        ax.text(px, py, sign, fontsize=7, color='white', ha='center', va='center', fontweight='bold', zorder=10)
    ex, hx = cx_ + 0.28, cx_ - 0.28
    harrow(ax, ex, rd[-1] + 0.1, ex, ra[2] - 0.17, color=RED, lw=1.6, hw=4.5, z=8)
    charge(ex, ra[2], '\u2212', RED)
    harrow(ax, hx, rd[-1] - 0.1, hx, rd[-3] + 0.17, color=DGRAY, lw=1.6, hw=4.5, z=8)
    charge(hx, rd[-3], '+', DGRAY)

    # ---- c, OLED, split in two. Left, flat-lying emitters whose horizontal dipoles send light out.
    #      Right, standing emitters whose vertical dipoles send light along the film, where it is trapped.
    x = X[2]
    w = pw
    pitch, nrow = 0.4, 4
    band = nrow * pitch + 0.1
    layer(ax, x, yb, w, 0.36, METAL)
    ye0 = yb + 0.36; ye1 = ye0 + band
    layer(ax, x, ye0, w, band, '#F1F1F1')
    layer(ax, x, ye1, w, 0.28, TCO)
    caption(ax, x + w - 0.1, yb + 0.18, 'Al', size=6.0, color='white', ha='right', va='center', zorder=6)
    caption(ax, x + w - 0.1, ye1 + 0.14, 'ITO', size=6.0, color=DGRAY, ha='right', va='center', zorder=6)
    xm = x + w / 2
    # left half, flat-lying film
    lcols = [x + 0.78, x + 2.18]
    rows = [ye0 + 0.25 + r * pitch for r in range(nrow)]
    for ci, cx_ in enumerate(lcols):
        for ri, yy in enumerate(rows):
            if ci == 0 and ri == 3:
                continue
            slab(ax, cx_, yy, 1.15, t=0.14, fc=DGRAY, z=3)
    dipole(ax, lcols[0], rows[3], 1.15, lw=1.6)
    for dx in (-0.45, 0.0, 0.45):
        wavy(ax, lcols[0] + dx * 0.4, rows[3] + 0.2, lcols[0] + dx * 1.4, ye1 + 2.2, color=RED, lw=0.9)
    caption(ax, (x + xm) / 2 + 0.55, ye1 + 1.85, 'escapes', size=6.6, color=RED, ha='left', va='center')
    # right half, standing film
    scols = [xm + 0.35 + k * 0.42 for k in range(7)]
    sy = (ye0 + ye1) / 2
    for k, cx_ in enumerate(scols):
        if k == 1:
            continue
        slab(ax, cx_, sy, band - 0.35, t=0.14, ang=90, fc=DGRAY, z=3)
    dipole(ax, scols[1], sy, band - 0.35, vertical=True, color=RED, lw=1.6)
    # guided wave running along the film toward the edge
    from matplotlib import patheffects as pe
    halo = [pe.withStroke(linewidth=3.2, foreground='#F1F1F1')]
    d = np.array([x + w - 0.12 - (scols[1] + 0.22), 0.0]); L = d[0]
    t_ = np.linspace(0, L * 0.88, 200)
    xs = scols[1] + 0.22 + t_
    ys = sy + 0.09 * np.sin(2 * np.pi * 4.5 * t_ / (L * 0.88))
    ax.plot(xs, ys, color=RED, lw=1.0, zorder=6, path_effects=halo, solid_capstyle='round')
    ax.annotate('', xy=(x + w - 0.12, sy), xytext=(xs[-1], ys[-1]), zorder=6,
                arrowprops=dict(arrowstyle='-|>,head_width=0.18,head_length=0.28', color=RED, lw=1.0, shrinkA=0, shrinkB=0,
                                path_effects=halo))
    caption(ax, (xm + x + w) / 2, ye1 + 0.55, 'trapped', size=6.6, color=RED, ha='center', va='bottom')
    # split between the two halves
    ax.plot([xm, xm], [yb - 0.15, ye1 + 1.4], color=MGRAY, lw=0.8, ls=(0, (3, 2)), zorder=7)

    # ---- d, organic spin valve, first layer hybridized with the ferromagnetic contact
    x = X[3]
    sc = x + 1.05                                     # stack center
    layer(ax, x, yb, 2.15, 0.5, METAL, 'Co', size=6.0)
    for k in range(3):
        harrow(ax, x + 1.0 + k * 0.38, yb + 0.1, x + 1.0 + k * 0.38, yb + 0.42, color='white', lw=0.9, hw=3)
    ax.add_patch(Ellipse((sc, yb + 0.58), 1.95, 0.4, fc=PRED, ec='none', zorder=2))
    slab(ax, sc, yb + 0.8, 1.6, t=0.15, ang=0, fc=RED, z=4)
    for i in range(6):
        slab(ax, sc, yb + 1.3 + i * 0.45, 1.6, t=0.15, ang=0, fc=DGRAY, z=4)
    # frontier levels, bulk against the first layer
    bx0, bx1 = x + 2.75, x + 3.55
    ix0, ix1 = x + 4.45, x + 5.25
    LU_b, HO_b, LU_i, HO_i = yb + 3.85, yb + 1.25, yb + 3.15, yb + 1.95
    for yy in (LU_b, HO_b):
        ax.plot([bx0, bx1], [yy, yy], color=DGRAY, lw=1.5, solid_capstyle='butt')
    for yy in (LU_i, HO_i):
        ax.add_patch(Rectangle((ix0, yy - 0.17), ix1 - ix0, 0.34, fc=PRED, ec='none'))
        ax.plot([ix0, ix1], [yy, yy], color=RED, lw=1.5, solid_capstyle='butt')
    for y1, y2 in ((LU_b, LU_i), (HO_b, HO_i)):
        ax.plot([bx1, ix0], [y1, y2], color=MGRAY, lw=0.6, ls=(0, (2, 1.5)))
    caption(ax, (bx0 + bx1) / 2, LU_b + 0.12, 'LUMO', size=6.2, color=DGRAY, va='bottom')
    caption(ax, (bx0 + bx1) / 2, HO_b + 0.12, 'HOMO', size=6.2, color=DGRAY, va='bottom')
    caption(ax, (bx0 + bx1) / 2, yb + 0.25, 'bulk', size=6.6, color=DGRAY, va='center')
    caption(ax, (ix0 + ix1) / 2, yb + 0.25, 'interface', size=6.6, color=RED, va='center')
    return fig


if __name__ == '__main__':
    which = sys.argv[1:] or ['1.1', '2.1']
    if '1.1' in which:
        save(fig_1_1(), 'hero_fig1-01_scales')
    if '2.1' in which:
        save(fig_2_1(), 'hero_fig2-01_packing')
