"""GIF 12 (ZnPc) with the Kramers-Kronig step made explicit (defense-draft-v2).
Unchanged above the spectrum except the isoindole site cutout, which moves up beside the ladder to free the
legend column. Spectrum: measured isotropic beta (exp_bets.csv, as in GIF 12) and delta_iso from a numerical KK
transform of that beta (10 eV to 500 keV, dft.csv tails joined at 270.2 and 330 eV; /home/claude/kk/znpc_kk.py),
plus a constant 0.345e-3 so delta matches the packaged KK-consistent model exp.csv (the f1 anchor that the
10 eV lower limit leaves out; residual shape difference 0.04e-3 rms)."""
import math
import numpy as np
from style import *
import g12
import kkpanel as K
from g12 import EG, BETA, ST, strength, energy, fade, at, draw_molecule, draw_levels

DUR = g12.DUR
_z = np.load("/home/claude/kk/znpc_kk.npz")
_off = float(np.mean(_z["delta_expcsv"] - _z["delta"]))
DELTA = np.interp(EG, _z["E"], _z["delta"] + _off) * 1e3
BETA_ = BETA * 1e3 if BETA.max() < 0.1 else BETA
AX = K.make_axes((g12.ELO, g12.EHI), (-0.95, 2.55))
g12.AX = AX
g12.CUT_SC = 15.5
g12.CUT_X0, g12.CUT_Y0 = 1104, 342


def highlight(ctx, s, a):
    lo, hi = s["E"] - 2.5 * s["W"], s["E"] + 2.5 * s["W"]
    m = (EG >= lo) & (EG <= hi)
    pts = AX.pts(EG[m], BETA_[m])
    y0 = AX.Y(0.0)
    g = cairo.LinearGradient(AX.X(lo), 0, AX.X(hi), 0)
    c = hexrgb(CRIMSON if s["bound"] else SKY)
    for q in np.linspace(0, 1, 21):
        e = lo + q * (hi - lo)
        g.add_color_stop_rgba(q, c[0], c[1], c[2], (0.45 if s["bound"] else 0.75) * a * math.exp(-0.5 * ((e - s["E"]) / s["W"]) ** 2))
    ctx.move_to(pts[0][0], y0)
    for p in pts:
        ctx.line_to(*p)
    ctx.line_to(pts[-1][0], y0)
    ctx.close_path()
    ctx.set_source(g)
    ctx.fill()


def frame(t):
    surf, ctx = new_frame()
    fd = fade(t)
    E = energy(t)
    draw_molecule(ctx, t, fd)
    draw_levels(ctx, t, fd)

    AX.frame(ctx, xticks=(280, 290, 300, 310, 320), xlabel="Photon energy (eV)", zero=0.0)
    K.ylabel(ctx, AX)
    y0 = AX.Y(0.0)
    pts = AX.pts(EG, BETA_)
    # no fill under beta (v2 feedback)
    for k, s in enumerate(ST):
        a = strength(t, k) * fd
        if a > 0.01:
            highlight(ctx, s, a)
    polyline(ctx, AX.pts(EG, DELTA), BLUE, 4.6, 1.0)
    polyline(ctx, pts, CRIMSON, 5.5, 1.0)
    pk = EG[np.argmax(BETA_)]
    text(ctx, AX.X(pk) + 16, AX.Y(BETA_.max()) + 26, "$π$^{*}", 40, CRIMSON, 1.0)
    text(ctx, AX.X(299.0), AX.Y(at(BETA_, 298.5) + 0.42), "$σ$^{*}", 40, BLUE, 1.0, "c")
    K.legend(ctx, 1.0, 1.0, 1.0, 1.0)
    cx = AX.X(E)
    src(ctx, CLAY, 0.9 * fd)
    ctx.set_line_width(2.4)
    ctx.set_dash([6, 6])
    ctx.move_to(cx, AX.y0 - 6)
    ctx.line_to(cx, AX.y1)
    ctx.stroke()
    ctx.set_dash([])
    for arr, col in ((DELTA, BLUE), (BETA_, CLAY)):
        yv = AX.Y(at(arr, E))
        glow(ctx, cx, yv, 22, col if col == CLAY else SKY, 0.45 * fd)
        ctx.new_path()
        src(ctx, col, fd)
        ctx.arc(cx, yv, 7 if col == CLAY else 6, 0, 2 * math.pi)
        ctx.fill()
    return surf
