"""Shared scene for the remastered reflectivity animations (g12 sweep, g13 readout).
Adapted from an animation by D. M. DeLongchamp (NIST)."""
import math
import numpy as np
import cairo
from style import (BG, INK, SLATE, MUTED, CRIMSON, BLUE, CLAY, IVORY,
                   src, hexrgb, mix, lerp, clamp, ramp, smooth, text, glow, arrow_head,
                   rounded_rect, Axes)

SIZE = (1200, 680)
Z = np.load("xrr_curves.npz")
Q = Z["q"]
RS = np.log10(np.clip(Z["refl"][:, 1, 1].real, 1e-12, None))
RP = np.log10(np.clip(Z["refl"][:, 0, 0].real, 1e-12, None))
RS0 = np.log10(np.clip(Z["refl0"][:, 1, 1].real, 1e-12, None))
LAM = 12398.4193 / float(Z["E"]) / 10.0
Q0, Q1 = Q[0], Q[-1]
T_FILM = float(Z["t_film_nm"])
QC = 4 * math.pi * math.sqrt(2 * float(Z["delta_si"])) / LAM

AX = Axes(690, 60, 1150, 540, (0.0, 2.5), (-9.0, 0.0))
FOOT = (310, 380)
STACK_X = (125, 475)
L_BEAM = 225
LAYERS = [  # name, n label, t label, height, color
    ("ZnPc", "$n$_{1}", "$t$_{1}", 70, mix(BG, CRIMSON, 0.20)),
    ("interface", "$n$_{2}", "$t$_{2}", 4, mix(BG, CLAY, 0.92)),
    ("SiO_{2}", "$n$_{3}", "$t$_{3}", 24, hexrgb("#C3C8CA")),
    ("Si", "$n$_{4}", None, 46, hexrgb("#9AA2A6")),
]
SIG_PX = 5.0


PSI = 0.0   # current lab-frame rotation of the scene (rad); scene text is kept upright


def utext(ctx, x, y, *a, **k):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(PSI)
    w = text(ctx, 0, 0, *a, **k)
    ctx.restore()
    return w


def lab_frame(ctx, psi_deg):
    """Rotate the sample-frame scene about the footprint so the incident beam is fixed.
    Call inside save/restore."""
    global PSI
    PSI = math.radians(psi_deg)
    ctx.translate(*FOOT)
    ctx.rotate(-PSI)
    ctx.translate(-FOOT[0], -FOOT[1])


def theta_deg(q):
    return math.degrees(math.asin(clamp(q * LAM / (4 * math.pi), 0, 1)))


def interp(y, q):
    return float(np.interp(q, Q, y))


def new_ctx():
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, *SIZE)
    ctx = cairo.Context(surf)
    fo = cairo.FontOptions()
    fo.set_antialias(cairo.ANTIALIAS_GRAY)
    fo.set_hint_style(cairo.HINT_STYLE_NONE)
    fo.set_hint_metrics(cairo.HINT_METRICS_OFF)
    ctx.set_font_options(fo)
    src(ctx, BG)
    ctx.paint()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    return surf, ctx


# ---------------------------------------------------------------- stack

def draw_stack(ctx, build=(1, 1, 1, 1), hl=None, labels=1.0, m=0.0, flash=0.0):
    """Layered cross-section that morphs (m 0 -> 1) into a plain film-on-substrate sample.
    labels: float for all, or dict with 'name', 'geo' (t_j and sigma_j), 'n' alphas."""
    if not isinstance(labels, dict):
        labels = {"name": labels, "geo": labels, "n": labels}
    hl = hl or {}
    ms = smooth(m)
    x0 = lerp(STACK_X[0], FOOT[0] - 170, ms)
    x1 = lerp(STACK_X[1], FOOT[0] + 170, ms)
    simple_h = (12, 0, 0, 30)
    simple_c = (mix(BG, CRIMSON, 0.32), mix(BG, CLAY, 0.55), hexrgb("#C3C8CA"), hexrgb("#A3AAAE"))
    heights, cols = [], []
    for k, (name, nl, tl, h, col) in enumerate(LAYERS):
        heights.append(lerp(h, simple_h[k], ms))
        cols.append(tuple(lerp(col[c], simple_c[k][c], ms) for c in range(3)) + (1.0,))
    tops, y = [], FOOT[1]
    for h in heights:
        tops.append(y)
        y += h
    bottom = y
    for i in range(len(LAYERS) - 1, -1, -1):
        b = build[i]
        if b <= 0.01 or heights[i] < 0.3:
            continue
        col = cols[i]
        dy = (1 - smooth(b)) * 26
        ctx.rectangle(x0, tops[i] + dy, x1 - x0, heights[i])
        ctx.set_source_rgba(col[0], col[1], col[2], b)
        ctx.fill()
    sig = SIG_PX * (1 - ms) + 0.8
    if min(build) > 0.99:
        above = [hexrgb(BG)] + cols
        for i, yt in enumerate(tops):
            if (i > 0 and heights[i] < 0.3) or i in (1, 2):   # interface line stays crisp
                continue
            a, b = above[i], above[i + 1] if heights[i] >= 0.3 else above[i + 2]
            g = cairo.LinearGradient(0, yt - sig, 0, yt + sig)
            g.add_color_stop_rgba(0, a[0], a[1], a[2], 1)
            g.add_color_stop_rgba(1, b[0], b[1], b[2], 1)
            ctx.set_source(g)
            ctx.rectangle(x0, yt - sig, x1 - x0, 2 * sig)
            ctx.fill()
    if build[-1] > 0.01:
        fade = 34 * (1 - ms)
        if fade > 1:
            b = hexrgb(BG)
            g = cairo.LinearGradient(0, bottom - fade, 0, bottom + 1)
            g.add_color_stop_rgba(0, b[0], b[1], b[2], 0)
            g.add_color_stop_rgba(1, b[0], b[1], b[2], 1)
            ctx.set_source(g)
            ctx.rectangle(x0, bottom - fade, x1 - x0, fade + 2)
            ctx.fill()
        if ms > 0.01:
            src(ctx, "#8E979B", ms)
            ctx.rectangle(x0, bottom - 9, x1 - x0, 9)
            ctx.fill()
    # interface: a single crisp line
    if heights[1] >= 0.3 and build[1] > 0.01:
        c = cols[1]
        ctx.rectangle(x0, tops[1], x1 - x0, heights[1])
        ctx.set_source_rgba(c[0], c[1], c[2], build[1])
        ctx.fill()
    # interface flash
    if flash > 0.01 and heights[1] >= 0.3:
        yt, hh = tops[1], heights[1]
        c = hexrgb(CLAY)
        for pad, al in ((10, 0.10), (5, 0.18), (0, 0.55)):
            ctx.rectangle(x0 - pad, yt - pad, x1 - x0 + 2 * pad, hh + 2 * pad)
            ctx.set_source_rgba(c[0], c[1], c[2], al * flash)
            ctx.fill()
    # labels
    la = 1 - ramp(m, 0.0, 0.45)
    if la <= 0.01:
        return
    for i, (name, nl, tl, h, col) in enumerate(LAYERS):
        yt, hh = tops[i], heights[i]
        bb = ramp(build[i], 0.5, 1.0) * la
        an, ag, ao = labels["name"] * bb, labels["geo"] * bb, labels["n"] * bb
        thin = h < 30
        fs = 24 if thin else 28
        yc = yt + hh / 2 + (8 if thin else 9)
        dark = name == "Si"
        base = IVORY if dark else SLATE
        if i == 1:    # interface line: one label outside, on the line
            if an > 0.01:
                text(ctx, x1 + 12, yt + hh / 2 + 8, "interface,  $n$_{2}, $t$_{2}", 24, CLAY, an)
            continue
        if an > 0.01:
            text(ctx, x0 - 14, yc, name, fs, INK, 0.95 * an, "r")
        xr = x1 - 16
        if tl:
            ht = hl.get("t", 0) if i == 0 else 0
            w = text(ctx, xr, yc, tl, fs, CLAY if ht > 0.5 else base, ag, "r")
            xr -= w + 6
            text(ctx, xr, yc, ",", fs, base, ao, "r")
            xr -= 10
        hn = hl.get("n", 0)
        text(ctx, xr, yc, nl, fs, CLAY if hn > 0.5 else base, ao, "r")
        hs = hl.get("sigma", 0)
        if i in (0, 3):
            text(ctx, x1 + 12, yt + (26 if i == 0 else 7), f"$σ$_{{{1 if i == 0 else 2}}}", 22,
                 CLAY if hs > 0.5 else SLATE, 0.85 * ag)


def sample_axes(ctx, a):
    """Sample-frame triad, shown only in the zoomed sample view."""
    if a <= 0.01:
        return
    ox, oy = STACK_X[1] + 120, FOOT[1] + 175
    for dx, dy, lab in ((0, -56, "$z$"), (56, 0, "$x$")):
        src(ctx, SLATE, a)
        ctx.set_line_width(2.6)
        ctx.move_to(ox, oy)
        ctx.line_to(ox + dx * 0.8, oy + dy * 0.8)
        ctx.stroke()
        arrow_head(ctx, ox + dx, oy + dy, math.atan2(dy, dx), 14, SLATE, a)
        utext(ctx, ox + dx + (10 if dx else -4), oy + dy + (8 if dx else -6), lab, 26, SLATE, a,
             "l" if dx else "c")


# ---------------------------------------------------------------- instrument

def beam_seg(ctx, x0, y0, x1, y1, alpha):
    for wdt, a in ((14, 0.10), (4.5, 0.95)):
        src(ctx, CLAY, alpha * a)
        ctx.set_line_width(wdt)
        ctx.move_to(x0, y0)
        ctx.line_to(x1, y1)
        ctx.stroke()


def source_glyph(ctx, x, y, ang, a):
    if a <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    rounded_rect(ctx, -30, -14, 46, 28, 6)
    src(ctx, SLATE, a)
    ctx.fill()
    ctx.rectangle(16, -7, 10, 14)
    src(ctx, "#47525A", a)
    ctx.fill()
    ctx.restore()


def ccd_glyph(ctx, x, y, ang, a):
    """Area detector: housing with a pixelated sensor face toward the beam."""
    if a <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    rounded_rect(ctx, -6, -26, 30, 52, 6)
    src(ctx, SLATE, a)
    ctx.fill()
    ctx.rectangle(-10, -22, 7, 44)
    src(ctx, "#3A4449", a)
    ctx.fill()
    src(ctx, "#7C878C", a)
    ctx.set_line_width(1.0)
    for k in range(1, 6):
        ctx.move_to(-10, -22 + k * 44 / 6)
        ctx.line_to(-3, -22 + k * 44 / 6)
        ctx.stroke()
    ctx.restore()


def geometry(th, phase=None):
    tr = math.radians(th)
    fx, fy = FOOT
    kx, ky = math.cos(tr), math.sin(tr)
    return dict(tr=tr, fx=fx, fy=fy, kx=kx, ky=ky,
                sx=fx - L_BEAM * kx, sy=fy - L_BEAM * ky,
                dx=fx + L_BEAM * kx, dy=fy - L_BEAM * ky)


def draw_instrument(ctx, th, src_in=1.0, det_in=1.0, beam_in=1.0, pol_in=1.0, phi=0.0,
                    logR=0.0, tags=0.0, arc=1.0):
    g = geometry(th)
    tr, fx, fy, kx, ky = g["tr"], g["fx"], g["fy"], g["kx"], g["ky"]
    sx, sy, dx, dy = g["sx"], g["sy"], g["dx"], g["dy"]
    # glyphs slide in along the beam line
    ss = (1 - smooth(src_in)) * 90
    source_glyph(ctx, sx - (22 + ss) * kx, sy - (22 + ss) * ky, tr, src_in)
    ds = (1 - smooth(det_in)) * 90
    ccd_glyph(ctx, dx + (8 + ds) * kx, dy - (8 + ds) * ky, -tr, det_in)
    if tags > 0.01:
        utext(ctx, sx - 22 * kx, sy - 22 * ky - 30, "synchrotron", 26, SLATE, tags, "c")
        pa = min(tags, pol_in)
        if pa > 0.01:
            mx, my = sx + 0.42 * L_BEAM * kx, sy + 0.42 * L_BEAM * ky
            utext(ctx, mx + 34, my - 62, "s-polarized", 26, CRIMSON, pa)
        utext(ctx, dx + 10 * kx + 4, dy - 10 * ky - 40, "CCD", 26, SLATE, tags, "c")
    # beam draws from the source to the sample, then to the detector
    if beam_in > 0.01:
        u1 = clamp(beam_in / 0.55)
        ex, ey = lerp(sx, fx - 3 * kx, u1), lerp(sy, fy - 3 * ky, u1)
        beam_seg(ctx, sx, sy, ex, ey, 1.0)
        arrow_head(ctx, ex + 3 * kx, ey + 3 * ky, math.atan2(ky, kx), 20, CLAY, 0.95)
        u2 = clamp((beam_in - 0.55) / 0.45)
        if u2 > 0.01:
            a = 0.22 + 0.78 * clamp((logR + 9.0) / 9.0)
            tx, ty = fx + (L_BEAM - 22) * kx * u2, fy - (L_BEAM - 22) * ky * u2
            beam_seg(ctx, fx, fy, tx, ty, a)
            arrow_head(ctx, tx + 8 * kx, ty - 8 * ky, math.atan2(-ky, kx), 20, CLAY, a)
            glow(ctx, fx, fy, 22, CLAY, 0.45 * u2)
    # polarization
    if pol_in > 0.01:
        col = mix(CRIMSON, BLUE, phi, pol_in)
        mx, my = sx + 0.42 * L_BEAM * kx, sy + 0.42 * L_BEAM * ky
        ex_, ey_ = math.sin(tr), -math.cos(tr)
        sp, cp = math.sin(phi * math.pi / 2), math.cos(phi * math.pi / 2)
        grow = smooth(pol_in)
        half = 46 * sp * grow
        if half > 3:
            ctx.set_source_rgba(*col)
            ctx.set_line_width(4.5)
            ctx.move_to(mx - (half - 10) * ex_, my - (half - 10) * ey_)
            ctx.line_to(mx + (half - 10) * ex_, my + (half - 10) * ey_)
            ctx.stroke()
            ang = math.atan2(ey_, ex_)
            for sgn in (1, -1):
                ctx.save()
                ctx.translate(mx + sgn * half * ex_, my + sgn * half * ey_)
                ctx.rotate(ang + (0 if sgn > 0 else math.pi))
                ctx.move_to(0, 0)
                ctx.line_to(-17, -9)
                ctx.line_to(-13, 0)
                ctx.line_to(-17, 9)
                ctx.close_path()
                ctx.set_source_rgba(*col)
                ctx.fill()
                ctx.restore()
        ca = cp * pol_in
        if ca > 0.02:
            r = 13 * (0.6 + 0.4 * grow)
            ctx.new_path()
            ctx.arc(mx, my, r, 0, 2 * math.pi)
            src(ctx, IVORY, ca)
            ctx.fill_preserve()
            ctx.set_source_rgba(col[0], col[1], col[2], ca)
            ctx.set_line_width(3.5)
            ctx.stroke()
            ctx.arc(mx, my, 4.5, 0, 2 * math.pi)
            ctx.fill()
        utext(ctx, mx + 60 * ex_ - 6, my + 60 * ey_ + 12, "\\b$E$\\b", 34,
             CRIMSON if phi < 0.5 else BLUE, pol_in, "r")
    # incidence angle
    if arc > 0.01:
        ctx.new_path()
        src(ctx, INK, 0.7 * arc)
        ctx.set_line_width(2.4)
        ctx.arc(fx, fy, 78, math.pi, math.pi + tr)
        ctx.stroke()
        src(ctx, INK, 0.45 * arc)
        ctx.set_line_width(1.6)
        ctx.set_dash([4, 5])
        ctx.move_to(fx - 130, fy)
        ctx.line_to(fx, fy)
        ctx.stroke()
        ctx.set_dash([])


# ---------------------------------------------------------------- plot

def draw_axes(ctx, a=1.0):
    if a <= 0.01:
        return
    ax = AX
    ax.frame(ctx, xticks=(0, 0.5, 1.0, 1.5, 2.0, 2.5), xlabel="$q$ (nm^{-1})", size=30, alpha=a)
    for v in (0, -3, -6, -9):
        y = ax.Y(v)
        src(ctx, SLATE, 0.9 * a)
        ctx.set_line_width(3.0)
        ctx.move_to(ax.x0 - 10, y)
        ctx.line_to(ax.x0, y)
        ctx.stroke()
        text(ctx, ax.x0 - 18, y + 10, f"10^{{{v}}}", 28, SLATE, a, "r")
    text(ctx, ax.x0 - 34, ax.y0 - 18, "$R$", 36, INK, a, "c")
    text(ctx, 1150, 668, f"ZnPc on SiO_{{2}}/Si, {float(Z['E']):.1f} eV", 22, MUTED, a, "r")


def curve(ctx, y, qa, qb, color, alpha=1.0, width=3.6, dash=None):
    lo, hi = min(qa, qb), max(qa, qb)
    m = (Q >= lo) & (Q <= hi)
    if m.sum() < 2 or alpha <= 0.01:
        return
    pts = AX.pts(Q[m], np.clip(y[m], -9.0, 0.0))
    ctx.save()
    ctx.rectangle(AX.x0, AX.y0 - 4, AX.x1 - AX.x0 + 4, AX.y1 - AX.y0 + 4)
    ctx.clip()
    src(ctx, color, alpha)
    ctx.set_line_width(width)
    if dash:
        ctx.set_dash(dash)
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.stroke()
    ctx.set_dash([])
    ctx.restore()


def readouts(ctx, th, s_a, p_a, a=1.0):
    if a <= 0.01:
        return
    text(ctx, 40, 62, f"$ϑ$ = {th:.0f}°", 40, INK, a)
    if s_a > 0.01:
        text(ctx, 40, 108, "s-polarized", 32, CRIMSON, s_a * a)
    if p_a > 0.01:
        text(ctx, 40, 108, "p-polarized", 32, BLUE, p_a * a)


def end_labels(ctx, s_a, p_a):
    """Direct labels at the curve ends, in place of a legend."""
    x = AX.X(Q1) + 12
    if s_a > 0.01:
        text(ctx, x, AX.Y(float(RS[-1])) + 10, "s", 32, CRIMSON, s_a)
    if p_a > 0.01:
        text(ctx, x, AX.Y(float(RP[-1])) + 10, "p", 32, BLUE, p_a)
