"""GIF 2 with the Kramers-Kronig step made explicit (defense-draft-v2).

Unchanged from GIF 2 above the spectrum: benzene ring, transition dipoles, level ladder, swept photon energy.
Spectrum panel now carries both halves of the index n = 1 - delta + i beta on one axis:
  beta (crimson) is built by the energy sweep, as a NEXAFS measurement would build it, and is tagged "measured";
  once beta is complete, delta (blue) is drawn from it, tagged "Kramers-Kronig transform of beta".
delta is the iso delta of spectra.Model: numerical KK of the bare-atom beta (1 eV to 30 keV) plus the
Dawson (KK-paired) term of each Gaussian resonance, so the drawn delta is the KK transform of the drawn beta."""
import math
import numpy as np
from style import *
import spectra as S
import g2
import kkpanel as K
from g2 import EG, BETA, draw_molecule, draw_levels, at

DUR = 10.8
_, DELTA = g2.M.iso()
YLIM = (-0.35, 3.55)
AX = K.make_axes((g2.ELO, g2.EHI), YLIM)
T_D0, T_D1 = 7.05, 8.75          # delta sweep, after beta is complete
T_F0, T_F1 = 10.05, 10.75        # fade before the loop restarts


def energy(t):
    return g2.energy(t)


def fade(t):
    return 1 - ramp(t, T_F0, T_F1)


def legend(ctx, t, fd):
    a1 = fd * ramp(t, 0.5, 1.0)
    a2 = fd * ramp(t, T_D0 - 0.35, T_D0 + 0.05)
    u = ramp(t, T_D0 - 0.35, T_D0 + 0.25)
    a3 = fd * ramp(t, T_D0, T_D0 + 0.4)
    K.legend(ctx, a1, a2, a3, u)


def frame(t):
    surf, ctx = new_frame()
    E = energy(t)
    fd = fade(t)
    draw_molecule(ctx, E, fd)
    draw_levels(ctx, E, fd)

    AX.frame(ctx, xticks=(280, 290, 300, 310, 320), xlabel="Photon energy (eV)", zero=0.0)
    K.ylabel(ctx, AX)
    xip = AX.X(S.IP)
    src(ctx, SLATE, 0.7)
    ctx.set_line_width(2.0)
    ctx.set_dash([8, 6])
    ctx.move_to(xip, AX.y0 - 4)
    ctx.line_to(xip, AX.y1)
    ctx.stroke()
    ctx.set_dash([])
    text(ctx, xip + 10, AX.y0 + 22, "ionization", 30, SLATE, 0.9)
    y0 = AX.Y(0.0)
    m = EG <= E
    if m.sum() > 1:
        pts = AX.pts(EG[m], BETA[m])
        pass  # no fill under beta (v2 feedback)
        polyline(ctx, pts, CRIMSON, 5.5, fd)
    # delta, drawn left to right once beta is complete
    ed = g2.ELO + (g2.EHI - g2.ELO) * (0.5 - 0.5 * math.cos(math.pi * clamp((t - T_D0) / (T_D1 - T_D0))))
    if t > T_D0:
        md = EG <= ed
        if md.sum() > 1:
            polyline(ctx, AX.pts(EG[md], DELTA[md]), BLUE, 4.6, fd)
        if t < T_D1 + 0.3:
            xd, yd = AX.X(ed), AX.Y(at(DELTA, ed))
            a = fd * (1 - ramp(t, T_D1, T_D1 + 0.3))
            glow(ctx, xd, yd, 20, SKY, 0.5 * a)
            ctx.new_path()
            src(ctx, BLUE, a)
            ctx.arc(xd, yd, 6.5, 0, 2 * math.pi)
            ctx.fill()
    if E > 285.6:
        text(ctx, AX.X(286.3), AX.Y(0.55), "$π$^{*}", 40, CRIMSON,
             fd * ramp(E, 285.6, 286.6))
    if E > 294.5:
        text(ctx, AX.X(296.5), AX.Y(2.45), "$σ$^{*}", 40, BLUE,
             fd * ramp(E, 294.5, 295.5), "c")
    legend(ctx, t, fd)
    cx = AX.X(E)
    ca = fd * ramp(t, 0.0, 0.35) * (1 - ramp(t, T_D0 - 0.3, T_D0))
    if ca > 0.01:
        src(ctx, CLAY, 0.9 * ca)
        ctx.set_line_width(2.4)
        ctx.set_dash([6, 6])
        ctx.move_to(cx, AX.y0 - 6)
        ctx.line_to(cx, AX.y1)
        ctx.stroke()
        ctx.set_dash([])
        yv = AX.Y(at(BETA, E))
        glow(ctx, cx, yv, 22, CLAY, 0.45 * ca)
        ctx.new_path()
        src(ctx, CLAY, ca)
        ctx.arc(cx, yv, 7, 0, 2 * math.pi)
        ctx.fill()
    return surf
