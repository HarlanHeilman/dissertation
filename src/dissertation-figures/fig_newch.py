"""Figures for the new molecular films chapter, round 2.
growth   section 2, the three growth modes at increasing coverage
orbitals section 3, sp2 hybridization, bonding and antibonding levels, core transitions
dft      section 5, DFT to clusters, clusters to refined model, parameter changes
Visual language follows the hero figures (fig_hero.py)."""
import os
import sys
import json
import numpy as np
import pandas as pd
os.environ.setdefault('FIG_DATA', '/home/claude/work/data')
from fig_hero import *            # figlib style, slab, dipole, harrow, wavy, caption, layer, colors
from figlib import _gauss, znpc_index, znpc_mass_absorption, beta_from_mu
from matplotlib.patches import Arc, Polygon, Circle, Ellipse, Rectangle

D2 = '/home/claude/work/data2'
RAMP = ['#000000', '#5E5E5E', '#A8A8A8', '#EE8A86', '#E0201B']    # 20, 40, 54.7, 70, 90 deg


def frame(fig, rect, W, H):
    ax = fig.add_axes(rect); blank(ax)
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.set_aspect('equal')
    return ax


def plabel(ax, x, y, s):
    ax.text(x, y, s, fontsize=LABEL_FS, fontweight='bold', va='top', ha='left')


def cone_angle(xx, zz):
    """Symmetrized TDM polar angle from a uniaxial tensor, arccos sqrt(zz / (2 xx + zz))."""
    return np.degrees(np.arccos(np.sqrt(np.clip(zz / (2 * xx + zz), 0, 1))))


# ======================================================================================== growth
NS = 18                         # lattice sites across one frame
SP, LH, LL = 0.42, 0.8, 0.7     # site pitch, layer height, molecule length


def column(ax, x0, yb, site, n, z0=0):
    """Stack molecules z0 .. z0+n-1 on one site, herringbone tilt alternating by site."""
    for k in range(z0, z0 + n):
        ang = 90 + (12 if site % 2 else -12)
        slab(ax, x0 + 0.3 + site * SP, yb + 0.5 + 0.42 + k * LH, LL, t=0.12, ang=ang,
             fc=RED if k == 0 else DGRAY, z=3)


def fig_growth():
    W, H = 26.0, 15.6
    fig = plt.figure(figsize=(6.5, 6.5 * H / W))
    ax = frame(fig, [0, 0, 1, 1], W, H)
    FW = NS * SP + 0.2
    XF = [0.3, 0.3 + FW + 0.55, 0.3 + 2 * (FW + 0.55)]
    full = {s: 1 for s in range(NS)}
    rows = [
        ('a', 'Layer-by-layer', 'Frank-van der Merwe',
         [{**{s: 1 for s in range(0, 6)}, **{s: 1 for s in range(10, 13)}}, full, {s: 3 for s in range(NS)}], None),
        ('b', 'Layer-plus-island', 'Stranski-Krastanov',
         [{**{s: 1 for s in range(0, 6)}, **{s: 1 for s in range(10, 13)}}, full, full],
         {2: 2, 3: 3, 4: 3, 5: 3, 6: 3, 7: 3, 8: 2, 11: 2, 12: 3, 13: 3, 14: 3, 15: 3, 16: 2}),
        ('c', 'Island', 'Volmer-Weber',
         [{3: 2, 4: 3, 5: 2, 12: 1, 13: 1},
          {2: 2, 3: 3, 4: 4, 5: 3, 6: 2, 11: 1, 12: 2, 13: 1},
          {1: 3, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4, 8: 3, 10: 2, 11: 3, 12: 4, 13: 4, 14: 4, 15: 3, 16: 2}], None),
    ]
    RH = 4.85
    for j, (lab, name, alt, cov, isl) in enumerate(rows):
        yb = 0.95 + (2 - j) * RH
        plabel(ax, 0.0, yb + RH - 0.05, lab)
        t_ = ax.text(0.95, yb + RH - 0.42, name, fontsize=7.6, fontweight='bold', va='center', ha='left')
        ax.annotate(alt, xy=(1, 0.5), xycoords=t_, xytext=(5, 0), textcoords='offset points', fontsize=7.0,
                    color=DGRAY, va='center', ha='left')
        for x, d in zip(XF, cov):
            layer(ax, x, yb, FW, 0.5, LGRAY)
            for s_, n in d.items():
                column(ax, x, yb, s_, n)
        if isl:                              # islands nucleate on the completed wetting layer
            for s_, n in isl.items():
                column(ax, XF[2], yb, s_, n, z0=1)
    for x, cov in zip(XF, ('0.5 ML', '1 ML', '3 ML')):
        caption(ax, x + FW / 2, 0.45, cov, size=7.2, color=DGRAY, va='center')
    caption(ax, XF[0] + 0.15, 0.95 + 2 * RH + 0.25, 'substrate', size=5.8, color=DGRAY, ha='left', va='center')
    return fig


# ======================================================================================== orbitals
def lvl(ax, x0, x1, y, c=BLACK, lw=1.4):
    ax.plot([x0, x1], [y, y], color=c, lw=lw, solid_capstyle='butt', zorder=3)


def link(ax, x0, y0, x1, y1, c=MGRAY):
    ax.plot([x0, x1], [y0, y1], color=c, lw=0.6, ls=(0, (2, 1.5)), zorder=1)


def glyph(ax, kind, cx, cy):
    """C=C molecular orbital along a horizontal bond; filled and open lobes carry opposite phase."""
    d = 0.42
    col = RED if kind in ('pi', 'pis') else DGRAY
    if kind == 'sig':        # head-on overlap of two sp2 lobes, one continuous lobe between the nuclei
        ax.add_patch(Ellipse((cx, cy), 1.75, 0.6, fc=col, ec=col, lw=0.8, zorder=2, alpha=0.9))
    elif kind == 'sigs':     # opposite phase, node between the nuclei, density pushed outward
        ax.add_patch(Ellipse((cx - d - 0.42, cy), 0.95, 0.55, fc=col, ec=col, lw=0.8, zorder=2))
        ax.add_patch(Ellipse((cx + d + 0.42, cy), 0.95, 0.55, fc='white', ec=col, lw=0.8, zorder=2))
    elif kind == 'pi':       # side-on overlap, continuous lobes above and below the bond axis
        ax.add_patch(Ellipse((cx, cy + 0.36), 1.45, 0.62, fc=col, ec=col, lw=0.8, zorder=2))
        ax.add_patch(Ellipse((cx, cy - 0.36), 1.45, 0.62, fc='white', ec=col, lw=0.8, zorder=2))
    elif kind == 'pis':      # opposite phase on the two p orbitals, node between the nuclei
        for sx, top in ((-d, True), (d, False)):
            ax.add_patch(Ellipse((cx + sx, cy + 0.4), 0.42, 0.7, fc=col if top else 'white', ec=col, lw=0.8, zorder=2))
            ax.add_patch(Ellipse((cx + sx, cy - 0.4), 0.42, 0.7, fc='white' if top else col, ec=col, lw=0.8, zorder=2))
    if kind in ('sigs', 'pis'):
        ax.plot([cx, cx], [cy - 0.6, cy + 0.6], color=MGRAY, lw=0.6, ls=(0, (2, 1.5)), zorder=1)
    ax.plot([cx - d, cx + d], [cy, cy], color=BLACK, lw=0.8, zorder=5)
    for sx in (-d, d):
        ax.add_patch(Circle((cx + sx, cy), 0.08, fc=BLACK, ec='none', zorder=6))


def fig_orbitals():
    W, H = 26.0, 8.4
    fig = plt.figure(figsize=(6.5, 6.5 * H / W))
    ax = frame(fig, [0, 0, 1, 1], W, H)
    yc = 0.45                                         # baseline of the bold panel captions
    heads = [(0.0, 5.6, 'a', 'sp$^2$ hybridization'), (6.4, 9.6, 'b', 'C=C orbitals and core transitions'),
             (16.4, 9.6, 'c', 'Orbital shapes and dipoles')]
    for x, pw_, lab, h in heads:
        plabel(ax, x, H - 0.05, lab)
        caption(ax, x + pw_ / 2 + 0.3, yc, h, size=7.4, weight='bold', va='center')

    # ---- a, one carbon, 2s and 2p mix into three sp2 hybrids, p_z stays out of the mixing
    Ya = dict(s2=2.6, p2=6.2, sp2=5.0, pz=6.2)
    AT, HY, w = 1.4, 3.85, 1.45
    ax.annotate('', xy=(0.45, 7.3), xytext=(0.45, 1.6), arrowprops=dict(arrowstyle='-|>', color=BLACK, lw=0.8, mutation_scale=7))
    caption(ax, 0.6, 7.3, '$E$', size=7.5, ha='left', va='center')
    lvl(ax, AT, AT + w, Ya['s2'])
    for k in range(3):
        lvl(ax, AT + k * 0.52, AT + k * 0.52 + 0.41, Ya['p2'])
    for k in range(3):
        lvl(ax, HY + k * 0.52, HY + k * 0.52 + 0.41, Ya['sp2'])
    lvl(ax, HY + 0.52, HY + 0.93, Ya['pz'], c=RED)
    link(ax, AT + w, Ya['s2'], HY, Ya['sp2']); link(ax, AT + w, Ya['p2'], HY, Ya['sp2'])
    link(ax, AT + w, Ya['p2'], HY + 0.52, Ya['pz'], c=LRED)
    caption(ax, AT + w / 2, Ya['s2'] - 0.2, '2s', size=7.0, va='top')
    caption(ax, AT + w / 2, Ya['p2'] + 0.2, '2p', size=7.0, va='bottom')
    caption(ax, HY + w / 2, Ya['sp2'] - 0.2, r'sp$^2$ ($\times$3)', size=6.8, color=DGRAY, va='top')
    caption(ax, HY + w / 2, Ya['pz'] + 0.2, r'$p_z$', size=7.0, color=RED, va='bottom')
    caption(ax, AT + w / 2, 1.35, 'C atom', size=6.4, color=DGRAY, va='center')
    caption(ax, HY + w / 2, 1.35, 'hybridized C', size=6.4, color=DGRAY, va='center')

    # ---- b, two hybridized carbons form sigma and pi pairs, the C 1s level sits far below
    Y = dict(sp2=4.5, pz=5.55, sig=3.55, pi=4.85, pis=5.95, sigs=6.85, c1s=1.4)
    HL, MO, HR, w = 7.5, 10.45, 13.4, 1.45
    for xh in (HL, HR):
        for k in range(3):
            lvl(ax, xh + k * 0.52, xh + k * 0.52 + 0.41, Y['sp2'])
        lvl(ax, xh + 0.52, xh + 0.93, Y['pz'], c=RED)
    for k, lab, c in (('sig', r'$\sigma$', BLACK), ('pi', r'$\pi$', RED), ('pis', r'$\pi^*$', RED), ('sigs', r'$\sigma^*$', BLACK)):
        lvl(ax, MO, MO + w, Y[k], c=c, lw=1.7)
        caption(ax, MO + 0.42, Y[k] + 0.1, lab, size=7.8, color=c, va='bottom')
        for xa, xb, yh in ((HL + w, MO, Y['sp2'] if k in ('sig', 'sigs') else Y['pz']),
                           (MO + w, HR, Y['sp2'] if k in ('sig', 'sigs') else Y['pz'])):
            xe = (HL + 0.93 if xa == HL + w else xb) if k in ('pi', 'pis') else xa
            if k in ('pi', 'pis'):
                if xa == HL + w:
                    link(ax, HL + 0.93, yh, MO, Y[k], c=LRED)
                else:
                    link(ax, MO + w, Y[k], HR + 0.52, yh, c=LRED)
            else:
                link(ax, xa, Y[k] if xa == MO + w else yh, xb, yh if xa == MO + w else Y[k])
    lvl(ax, MO, MO + w, Y['c1s'], lw=2.6)
    caption(ax, MO - 0.15, Y['c1s'], 'C 1s', size=7.0, ha='right', va='center')
    harrow(ax, MO + 0.95, Y['c1s'] + 0.1, MO + 0.95, Y['pis'] - 0.07, color=RED, lw=1.6, hw=4.5)
    harrow(ax, MO + 1.25, Y['c1s'] + 0.1, MO + 1.25, Y['sigs'] - 0.07, color=DGRAY, lw=1.4, hw=4.5)
    ax.add_patch(Rectangle((MO + 0.7, 2.25), 0.8, 0.3, fc='white', ec='none', zorder=7))
    for yy in (2.25, 2.55):
        ax.plot([MO + 0.7, MO + 1.5], [yy - 0.08, yy + 0.08], color=BLACK, lw=0.7, zorder=8)
    caption(ax, MO + 0.8, 3.0, r'$h\nu$', size=7.2, color=RED, ha='right', va='center')
    for xc, lab in ((HL + w / 2, 'C'), (MO + w / 2, 'C=C'), (HR + w / 2, 'C')):
        caption(ax, xc, 8.15, lab, size=6.4, color=DGRAY, va='center')

    # ---- c, bonding orbitals below, antibonding above, with the dipole of each core transition
    G = {'sig': (19.2, 2.75), 'pi': (23.6, 2.75), 'pis': (19.2, 6.15), 'sigs': (23.6, 6.15)}
    for k, lab, c in (('sig', r'$\sigma$', BLACK), ('pi', r'$\pi$', RED), ('pis', r'$\pi^*$', RED), ('sigs', r'$\sigma^*$', BLACK)):
        gx, gy = G[k]
        glyph(ax, k, gx, gy)
        caption(ax, gx - 1.65, gy, lab, size=8.5, color=c, ha='right', va='center')
    ax.plot([16.9, 26.0], [4.45, 4.45], color=LGRAY, lw=0.6)
    caption(ax, 26.0, 4.6, 'antibonding', size=6.0, color=DGRAY, ha='right', va='bottom')
    caption(ax, 26.0, 4.3, 'bonding', size=6.0, color=DGRAY, ha='right', va='top')
    gx, gy = G['pis']
    harrow(ax, gx + 1.0, gy - 0.65, gx + 1.0, gy + 0.65, color=RED, lw=1.6, hw=4.5)
    caption(ax, gx + 1.15, gy + 0.35, r'$\mu$', size=8, color=RED, ha='left', va='center')
    gx, gy = G['sigs']
    harrow(ax, gx - 0.7, gy + 0.75, gx + 0.7, gy + 0.75, color=DGRAY, lw=1.5, hw=4.5)
    caption(ax, gx + 0.85, gy + 0.75, r'$\mu$', size=8, color=DGRAY, ha='left', va='center')
    return fig


# ======================================================================================== dft
def fig_dft():
    mem = pd.read_csv(f'{D2}/znpc/exp/dft_cluster_members.csv')
    cl = pd.read_csv(f'{D2}/znpc/exp/dft_clusters.csv')
    bb = pd.read_csv(f'{D2}/znpc/bb/buildingblock.csv')
    nx = pd.read_csv(f'{D2}/znpc/exp/nexafs.csv')
    sp = pd.read_csv(f'{D2}/znpc/dft/spectra.csv')
    SHIFT = 0.446990966796875             # rigid shift applied to the DFT energies before refinement
    E0, E1 = 282.5, 318.0
    fig = plt.figure(figsize=(6.5, 5.2))
    outer = fig.add_gridspec(1, 2, width_ratios=[1.65, 1.0], wspace=0.3, left=0.09, right=0.985, top=0.975, bottom=0.085)
    L = outer[0].subgridspec(5, 1, height_ratios=[1.0, 0.42, 0.42, 1.0, 0.3], hspace=0.0)
    a = fig.add_subplot(L[0]); st = fig.add_subplot(L[1], sharex=a)
    b = fig.add_subplot(L[3], sharex=a); rs = fig.add_subplot(L[4], sharex=a)

    # a, every DFT transition broadened against the sum of cluster Gaussians, the transitions themselves below
    w = sp[sp.energy.between(E0, E1)]
    sc = w.dft_original.max()
    a.plot(w.energy, w.dft_original / sc, color=BLACK, lw=1.0, label=f'DFT, {len(mem)} transitions')
    a.plot(w.energy, w.clusters_fit / sc, color=RED, lw=1.0, ls=(0, (3, 1.5)), label=f'{len(cl)} clusters')
    a.set_ylim(0, 1.12); a.set_yticks([0, 0.5, 1.0]); a.set_ylabel('Norm. intensity')
    a.legend(fontsize=6.3, loc='upper right', frameon=False, handlelength=1.6, labelspacing=0.3)
    smax = mem.amplitude.max()
    for r in mem.itertuples():
        st.plot([r.energy_ev, r.energy_ev], [0, r.amplitude / smax], color=RED if r.cluster_id % 2 else DGRAY, lw=0.8,
                solid_capstyle='butt')
    st.set_ylim(0, 1.08); st.set_yticks([]); st.set_ylabel('Osc.', fontsize=7)
    plt.setp(a.get_xticklabels(), visible=False)
    st.set_xlabel('DFT energy (eV)', labelpad=2)

    # b, angle-resolved NEXAFS against the refined cluster model, residuals below
    norm = nx.intensity_norm.max()
    for t_, c in zip(sorted(nx.theta_deg.unique()), RAMP):
        d = nx[(nx.theta_deg == t_) & nx.energy.between(E0, E1)]
        b.plot(d.energy[::3], d.intensity_norm[::3] / norm, 'o', ms=1.5, color=c, mew=0, zorder=2)
        b.plot(d.energy, d.igor_model / norm, color=c, lw=0.9, zorder=3, label=f'{t_:g}°')
        rs.plot(d.energy, 100 * (d.intensity_norm - d.igor_model) / norm, color=c, lw=0.6)
    b.set_ylim(0, 1.08); b.set_yticks([0.5, 1.0]); b.set_ylabel('Norm. intensity')
    b.legend(title='θ, measured and refined', title_fontsize=6.0, fontsize=6.0, loc='upper right', frameon=False,
             handlelength=1.2, labelspacing=0.2, ncol=2, columnspacing=0.8)
    rs.axhline(0, color=GRAY, lw=0.5); rs.set_ylim(-4.5, 4.5); rs.set_yticks([-3, 0, 3]); rs.set_ylabel('Res. (%)', fontsize=7)
    rs.set_xlim(E0, E1); rs.set_xlabel('Photon energy (eV)')
    plt.setp(b.get_xticklabels(), visible=False)
    label(a, 'a', x=-0.14, y=0.93); label(b, 'b', x=-0.14, y=0.93)

    # c, change of every cluster parameter from the DFT seed to the refined value
    R = outer[1].subgridspec(5, 1, hspace=0.12)
    ids = np.arange(len(bb))
    k = 2 * np.sqrt(2 * np.log(2))
    fw_i, fw_f = k * cl.sigma_ev.values, k * bb.sigma_ev.values
    th_i = cone_angle(cl.os_xx.values, cl.os_zz.values); th_f = cone_angle(bb.mol_xx.values, bb.mol_zz.values)
    e_i, e_f = cl.energy_ev.values + SHIFT, bb.location.values
    a_i = cl.amplitude.values / cl.amplitude.sum(); a_f = bb.amplitude.values / bb.amplitude.sum()
    rows = [(fw_f - fw_i, r'$\Delta$FWHM (eV)', DGRAY), (None, r'$\vartheta$ (°)', RED), (th_f - th_i, r'$\Delta\vartheta$ (°)', RED),
            ((e_f - e_i) / fw_i, r'$\Delta E$/FWHM', DGRAY), (np.log10(a_f / a_i), r'log $(A_f/A_i)$', BLACK)]
    axs = []
    for j, (v, yl, c) in enumerate(rows):
        x_ = fig.add_subplot(R[j], sharex=axs[0] if axs else None); axs.append(x_)
        if v is None:
            x_.vlines(ids, th_i, th_f, color=LRED, lw=0.9)
            x_.plot(ids, th_i, 'o', ms=3, color=MGRAY, mew=0, label='DFT')
            x_.plot(ids, th_f, 'o', ms=3, color=RED, mew=0, label='refined')
            x_.set_ylim(-5, 95); x_.set_yticks([0, 45, 90])
            x_.legend(fontsize=5.8, loc='upper left', frameon=False, handletextpad=0.1, borderaxespad=0.1, labelspacing=0.15)
        else:
            x_.axhline(0, color=BLACK, lw=0.6)
            x_.vlines(ids, 0, v, color=c, lw=0.9)
            x_.plot(ids, v, 'o', ms=2.8, color=c, mew=0)
            m = np.abs(v).max() * 1.2
            x_.set_ylim(-m, m)
        x_.set_ylabel(yl, fontsize=6.8, labelpad=1)
        x_.tick_params(labelsize=6.3)
        if j < len(rows) - 1:
            plt.setp(x_.get_xticklabels(), visible=False)
    axs[-1].set_xlabel('Cluster'); axs[-1].set_xticks(range(0, len(bb), 3))
    axs[0].set_xlim(-0.8, len(bb) - 0.2)
    label(axs[0], 'c', x=-0.4, y=0.98)
    return fig


if __name__ == '__main__':
    which = sys.argv[1:] or ['growth', 'orbitals', 'dft']
    for w in which:
        save({'growth': fig_growth, 'orbitals': fig_orbitals, 'dft': fig_dft}[w](), f'molch_{w}')
