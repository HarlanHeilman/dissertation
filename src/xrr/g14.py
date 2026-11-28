"""Reflectivity animation, two clips.
A  sample frame: labeled stack with a buried interface, index conventions (energy, tensor),
   synchrotron and CCD, beam, s polarization, pull back into the lab frame. Ends in the lab
   frame with the optical-constant conventions still on screen.
B  conventions leave, plot appears, s scan, return to start, s to p, p scan. Ends on both curves.
Each clip plays once and holds; the last frame of A is the first frame of B."""
import math
from style import BG, CRIMSON, BLUE, INK, SLATE, CLAY, src, mix, lerp, clamp, ramp, glow, text, arrow
import xrr_common as X

SIZE = X.SIZE
TH0 = 12.0
ZS, C, S = 1.45, (300, 410), (600, 400)

NAMES, NOPT = (-1.0, -0.5), (-1.0, -0.5)   # labels already present at t = 0
FLASH_HOLD, FLASH_OFF = 0.8, 1.4          # interface highlighted at t = 0, fades by 1.4 s
CONV1, CONV2 = (1.6, 2.1), (2.5, 3.0)
SRC, DET, BEAM, POL = (3.9, 4.5), (4.3, 4.9), (5.1, 6.1), (6.3, 6.9)
A_END = 7.4                   # A ends in the sample frame, instrument set, s polarized
CONV_OUT = (7.6, 8.1)
ZOOM = (7.7, 9.5)
ARC = (9.2, 9.7)
PLOT, READ = (8.8, 9.8), (9.4, 10.0)
LOWER = (10.2, 10.9)
S0, S1 = 11.6, 16.1
B0, B1 = 16.9, 18.1
R0, R1 = 18.4, 19.6
P0, P1 = 20.0, 24.5
FRINGE = 25.1                 # thickness readout (fringe spacing) after the p scan
ROUGH = 26.5                  # roughness readout
DUR = 28.3
Q_C = float(X.Z["qc_kink"])                                  # kink at the first fringe of R_s
Q_B, TH_B = float(X.Z["qB_pmin"]), float(X.Z["thB_pmin"])     # minimum of R_p
QA_F, QB_F = 0.763, 1.097                                    # adjacent R_s minima for the fringe bracket
Q_R = 2.206                                                   # R_s fringe maximum used for the roughness arrow
PHASES = [("A-sample-and-setup", 0.0, A_END), ("B-reflectivity", A_END, DUR)]


def q_at(t):
    if t < S0:
        return X.Q0
    if t < S1:
        return lerp(X.Q0, X.Q1, ramp(t, S0, S1))
    if t < B0:
        return X.Q1
    if t < P0:
        return lerp(X.Q1, X.Q0, ramp(t, B0, B1))
    return lerp(X.Q0, X.Q1, ramp(t, P0, P1))


def theta_at(t):
    if t < LOWER[1]:
        return lerp(TH0, X.theta_deg(X.Q0), ramp(t, *LOWER))
    return X.theta_deg(q_at(t))


def flash_at(t):
    """Interface highlighted in the opening frame, then eased off."""
    return 1.0 - ramp(t, FLASH_HOLD, FLASH_OFF)


def paren(ctx, x, y0, y1, side, a):
    bulge = 12 * side
    src(ctx, INK, a)
    ctx.set_line_width(2.2)
    ctx.move_to(x, y0)
    ctx.curve_to(x + bulge, y0 + (y1 - y0) * 0.25, x + bulge, y0 + (y1 - y0) * 0.75, x, y1)
    ctx.stroke()


def conventions(ctx, t):
    """Top band, screen space. Energy dependence left, tensor right."""
    out = 1 - ramp(t, *CONV_OUT)
    a1 = ramp(t, *CONV1) * out
    a2 = ramp(t, *CONV2) * out
    if a1 > 0.01:
        text(ctx, 300, 34, "energy", 24, SLATE, a1, "c")
        text(ctx, 300, 92, "$n$($E$) = 1 − $δ$($E$) + $iβ$($E$)", 36, INK, a1, "c")
    if a2 > 0.01:
        text(ctx, 830, 34, "polarization (tensor)", 24, SLATE, a2, "c")
        rows = [("$n_{xx}$", "0", "0"), ("0", "$n_{xx}$", "0"), ("0", "0", "$n_{zz}$")]
        cx0, dx, ry0, dy = 760, 64, 70, 30
        top, bot = ry0 - 24, ry0 + 2 * dy + 10
        text(ctx, cx0 - 66, ry0 + dy, "$n$_{1}, $n$_{2} =", 30, INK, a2, "r")
        paren(ctx, cx0 - 44, top, bot, -1, a2)
        for r, row in enumerate(rows):
            for c, e in enumerate(row):
                text(ctx, cx0 + c * dx, ry0 + r * dy, e, 26, INK, a2, "c")
        paren(ctx, cx0 + 2 * dx + 44, top, bot, 1, a2)
        text(ctx, cx0 + 2 * dx + 76, ry0 + dy, "$n$_{3}, $n$_{4} isotropic", 28, INK, a2)


def frame(t):
    surf, ctx = X.new_ctx()
    z = ramp(t, *ZOOM)
    s = lerp(ZS, 1.0, z)
    ox = lerp(S[0] - ZS * C[0], 0.0, z)
    oy = lerp(S[1] - ZS * C[1], 0.0, z)
    phi = ramp(t, R0, R1)
    q = q_at(t)
    th = theta_at(t)
    if t < LOWER[1]:
        logR = 0.0
    elif t < P0:
        logR = lerp(X.interp(X.RS, q), X.interp(X.RP, q), phi)
    else:
        logR = X.interp(X.RP, q)

    X.draw_axes(ctx, ramp(t, *PLOT))
    if t > S0:
        X.curve(ctx, X.RS, X.Q0, q if t < S1 else X.Q1, CRIMSON)
    if t > P0:
        X.curve(ctx, X.RP, X.Q0, q, BLUE)
    X.end_labels(ctx, ramp(t, S1 - 0.2, S1 + 0.3), ramp(t, P1 - 0.2, P1 + 0.3))

    # critical angle (revealed as the s scan passes it) and Brewster angle (as the p scan passes it)
    ax = X.AX

    def t_cross(qq, a0, a1):
        for k in range(600):
            tt = a0 + (a1 - a0) * k / 599
            if q_at(tt) >= qq:
                return tt
        return a1

    ca = ramp(t, t_cross(Q_C, P0, P1), t_cross(Q_C, P0, P1) + 0.5)
    if ca > 0.01:
        x = ax.X(Q_C)
        src(ctx, SLATE, 0.7 * ca)
        ctx.set_line_width(2.2)
        ctx.set_dash([6, 6])
        ctx.move_to(x, ax.y1)
        ctx.line_to(x, ax.Y(0.0))
        ctx.stroke()
        ctx.set_dash([])
        text(ctx, x + 12, ax.Y(-6.0), "critical edge", 24, SLATE, ca)
        text(ctx, x + 12, ax.Y(-6.85), "$q$_{c} = (4$π$/$λ$)√(2$δ$)", 30, INK, ca)
    ba = ramp(t, t_cross(Q_B, P0, P1), t_cross(Q_B, P0, P1) + 0.5)
    if ba > 0.01:
        x = ax.X(Q_B)
        src(ctx, BLUE, 0.7 * ba)
        ctx.set_line_width(2.2)
        ctx.set_dash([6, 6])
        ctx.move_to(x, ax.y1)
        ctx.line_to(x, ax.Y(X.interp(X.RP, Q_B)) + 10)
        ctx.stroke()
        ctx.set_dash([])
        text(ctx, x - 12, ax.Y(-7.75), "Brewster angle", 24, SLATE, ba, "r")
        text(ctx, x - 12, ax.Y(-8.55), f"$ϑ$_{{B}} ≈ {TH_B:.0f}°", 30, INK, ba, "r")

    # thickness: fringe spacing between adjacent R_s minima
    fa = ramp(t, FRINGE, FRINGE + 0.6)
    if fa > 0.01:
        xa, xb = ax.X(QA_F), ax.X(QB_F)
        yb = ax.Y(-2.05)
        src(ctx, CLAY, 0.55 * fa)
        ctx.set_line_width(1.6)
        ctx.set_dash([3, 5])
        for qq in (QA_F, QB_F):
            ctx.move_to(ax.X(qq), yb + 10)
            ctx.line_to(ax.X(qq), ax.Y(X.interp(X.RS, qq)) - 8)
            ctx.stroke()
        ctx.set_dash([])
        xm = (xa + xb) / 2
        half = (xb - xa) / 2 * fa
        arrow(ctx, xm, yb, xm - half, yb, CLAY, 2.6, 12, 0.95)
        arrow(ctx, xm, yb, xm + half, yb, CLAY, 2.6, 12, 0.95)
        la = ramp(t, FRINGE + 0.4, FRINGE + 1.0)
        text(ctx, xm, yb - 18, "$Δq$ = 2$π$/$t$", 30, INK, la, "c")
        text(ctx, xm, yb - 58, "fringe spacing", 24, SLATE, la, "c")

    # roughness: sigma = 0 R_s from the same kernel, dashed, with the drop to the real R_s
    ra = ramp(t, ROUGH, ROUGH + 0.8)
    if ra > 0.01:
        X.curve(ctx, X.RS0, 0.9, X.Q1, CRIMSON, 0.45 * ra, 2.6, [7, 6])
        qx = Q_R
        y0, y1 = ax.Y(X.interp(X.RS0, qx)), ax.Y(X.interp(X.RS, qx))
        aa = ramp(t, ROUGH + 0.4, ROUGH + 1.0)
        if aa > 0.01:
            arrow(ctx, ax.X(qx), y0 + 4, ax.X(qx), lerp(y0 + 4, y1 - 6, aa), CLAY, 2.6, 12, 0.95)
        la = ramp(t, ROUGH + 0.5, ROUGH + 1.1)
        text(ctx, ax.X(1.68), ax.Y(-2.3), "roughness", 24, SLATE, la)
        text(ctx, ax.X(1.68), ax.Y(-3.15), "exp(−$q$^{2}$σ$^{2})", 30, INK, la)

    ctx.save()
    ctx.translate(ox, oy)
    ctx.scale(s, s)
    X.lab_frame(ctx, th * z)
    X.draw_stack(ctx, labels={"name": ramp(t, *NAMES), "geo": ramp(t, *NAMES),
                              "n": ramp(t, *NOPT)}, m=ramp(t, ZOOM[0], ZOOM[0] + 1.3),
                 flash=flash_at(t))
    X.sample_axes(ctx, ramp(t, *CONV2) * (1 - ramp(t, ZOOM[0], ZOOM[0] + 0.6)))
    tags = min(ramp(t, *SRC), ramp(t, *DET)) * (1 - ramp(t, ZOOM[0], ZOOM[0] + 0.6))
    X.draw_instrument(ctx, th, src_in=ramp(t, *SRC), det_in=ramp(t, *DET),
                      beam_in=clamp((t - BEAM[0]) / (BEAM[1] - BEAM[0])),
                      pol_in=ramp(t, *POL), phi=phi, logR=logR, tags=tags, arc=ramp(t, *ARC))
    ctx.restore()

    conventions(ctx, t)

    vis = (ramp(t, S0 - 0.5, S0 - 0.1) * (1 - ramp(t, S1, S1 + 0.3))
           + ramp(t, R1, P0 - 0.1) * (1 - ramp(t, P1, P1 + 0.4)))
    if vis > 0.01:
        cx, cy = X.AX.X(q), X.AX.Y(clamp(logR, -9, 0))
        glow(ctx, cx, cy, 20, CRIMSON if phi < 0.5 else BLUE, 0.45 * vis)
        ctx.new_path()
        ctx.arc(cx, cy, 7.5, 0, 2 * math.pi)
        ctx.set_source_rgba(*mix(CRIMSON, BLUE, phi, vis))
        ctx.fill()

    a_s = ramp(t, *READ) * (1 - ramp(t, R0, (R0 + R1) / 2))
    a_p = ramp(t, (R0 + R1) / 2, R1)
    if a_s > 0.01:
        text(ctx, 40, 108, "s-polarized", 32, CRIMSON, a_s)
    if a_p > 0.01:
        text(ctx, 40, 108, "p-polarized", 32, BLUE, a_p)
    ta = ramp(t, *READ)
    if ta > 0.01:
        text(ctx, 40, 62, f"$ϑ$ = {th:.0f}°", 40, INK, ta)
    return surf


def static_stack(path_png, path_svg, scale=2.0):
    """Labeled sample-frame stack (with buried interface and sample axes), no instrument."""
    import cairo
    w, h = 900, 300
    for kind, path in (("png", path_png), ("svg", path_svg)):
        if kind == "png":
            surf = cairo.ImageSurface(cairo.FORMAT_RGB24, int(w * scale), int(h * scale))
        else:
            surf = cairo.SVGSurface(path, w * scale, h * scale)
        ctx = cairo.Context(surf)
        src(ctx, BG)
        ctx.paint()
        ctx.scale(scale, scale)
        ctx.translate(-X.STACK_X[0] + 200, -X.FOOT[1] + 40)
        X.draw_stack(ctx)
        X.sample_axes(ctx, 1.0)
        if kind == "png":
            surf.write_to_png(path)
        surf.finish()
