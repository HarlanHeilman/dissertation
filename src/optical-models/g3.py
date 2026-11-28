"""GIF 3. The index is complex, and only its imaginary part is measured. A transmission
NEXAFS sweep samples beta(E); the complex plane shows that beta alone leaves n on a
horizontal line of possibilities. A sliding Kramers-Kronig weight then builds delta(E) from
beta at every energy, and n(E) = 1 - delta + i beta traces its loop through the resonances."""
import math
import numpy as np
from style import *
import spectra as S

DUR = 9.0
ELO, EHI = 280.0, 320.0
EG = np.linspace(ELO, EHI, 801)
M = S.Model(EG)
BETA, DELTA = M.iso()

AB = Axes(600, 62, 1150, 300, (ELO, EHI), (0, 3.2))
AD = Axes(600, 392, 1150, 640, (ELO, EHI), (-0.3, 3.5))
# complex plane, equal aspect: x = Re(n) - 1 = -delta, y = Im(n) = beta
CP = Axes(78, 372, 448, 712, (-3.7, 0.55), (0, 3.9))

P1A, P1B = 0.35, 3.75     # measurement sweep
P2A, P2B = 4.35, 7.85     # Kramers-Kronig sweep
FADE_A, FADE_B = 8.45, 8.95

# NEXAFS samples: 0.4 eV steps, 0.1 eV through the pi* region
SAMP = np.unique(np.round(np.concatenate([np.arange(280, 320.01, 0.4), np.arange(284.3, 286.0, 0.1)]), 2))
SB = np.interp(SAMP, EG, BETA)


def at(arr, E):
    return float(np.interp(E, EG, arr))


def ease(u):
    u = clamp(u)
    return 0.5 - 0.5 * math.cos(math.pi * u)


def e_meas(t):
    return ELO + (EHI - ELO) * ease((t - P1A) / (P1B - P1A))


def e_kk(t):
    return ELO + (EHI - ELO) * ease((t - P2A) / (P2B - P2A))


V, SP, SPAN, XS = 160.0, 120.0, 480.0, -40.0
BEAM_Y = 160
FILM_X = 236
DET_X = 418


def draw_measurement(ctx, t, E, active):
    T = math.exp(-0.30 * at(BETA, E))
    text(ctx, 34, 66, f"h$ν$ = {E:.0f} eV", 40, INK)
    # beam guide
    src(ctx, CLAY, 0.2)
    ctx.set_line_width(2)
    ctx.set_dash([2, 7])
    ctx.move_to(20, BEAM_Y)
    ctx.line_to(DET_X, BEAM_Y)
    ctx.stroke()
    ctx.set_dash([])
    for k in range(int(SPAN / SP)):
        xp = XS + ((V * t + k * SP) % SPAN)
        if xp > DET_X - 20:
            continue
        frac = smooth(clamp((xp - FILM_X + 20) / 40))
        amp = 22 * (1 - frac + frac * T)
        a = 1.0 if xp < DET_X - 70 else clamp((DET_X - 20 - xp) / 50)
        wave_packet(ctx, xp, BEAM_Y, 0, 52, 15, amp, 2 * math.pi * 2.0 * t, CLAY, a)
    # film
    src(ctx, CRIMSON, 0.22)
    rounded_rect(ctx, FILM_X - 11, BEAM_Y - 82, 22, 164, 5)
    ctx.fill_preserve()
    src(ctx, CRIMSON, 0.9)
    ctx.set_line_width(2.5)
    ctx.stroke()
    text(ctx, FILM_X, BEAM_Y + 122, "film", 32, CRIMSON, 0.95, "c")
    # detector with intensity bar
    src(ctx, SLATE)
    rounded_rect(ctx, DET_X, BEAM_Y - 62, 40, 124, 8)
    ctx.fill()
    src(ctx, IVORY, 0.25)
    rounded_rect(ctx, DET_X + 10, BEAM_Y - 50, 20, 100, 4)
    ctx.fill()
    hgt = 100 * T
    src(ctx, CLAY, 0.95)
    rounded_rect(ctx, DET_X + 10, BEAM_Y + 50 - hgt, 20, hgt, 4)
    ctx.fill()
    text(ctx, 112, BEAM_Y + 72, "I_{0}", 34, SLATE, 0.95, "c", italic_words=True)
    text(ctx, 336, BEAM_Y + 72, "I", 34, SLATE, 0.95, "c", italic_words=True)


def draw_kernel(ctx, E, a):
    """Shade beta(E') by the weight E'/(E^2 - E'^2): blue where it adds, clay where it subtracts."""
    if a < 0.01:
        return
    step = 2
    for xpix in range(int(AB.x0) + 1, int(AB.x1), step):
        Ep = AB.xlim[0] + (xpix - AB.x0) / (AB.x1 - AB.x0) * (EHI - ELO)
        d = E - Ep
        if abs(d) < 0.05:
            continue
        wgt = min(1.0, 0.55 / abs(d))
        col = BLUE if d > 0 else CLAY
        src(ctx, col, 0.55 * wgt * a)
        yb = AB.Y(at(BETA, Ep))
        ctx.rectangle(xpix, yb, step, AB.y1 - yb)
        ctx.fill()


def frame(t):
    surf, ctx = new_frame()
    fd = 1 - ramp(t, FADE_A, FADE_B)
    phase2 = t >= P2A - 0.3
    Em = e_meas(t)
    Ek = e_kk(t)
    E = Ek if phase2 else Em

    ma = 1 - 0.62 * ramp(t, P1B + 0.1, P2A - 0.2) * (1 - ramp(t, FADE_A, FADE_B))
    ctx.push_group()
    draw_measurement(ctx, t, Em if not phase2 else Ek, True)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(ma)

    # ---- beta panel
    AB.frame(ctx, xticks=(280, 290, 300, 310, 320), tick_labels=False)
    text(ctx, AB.x0 - 26, (AB.y0 + AB.y1) / 2 + 8, "$β$", 44, CRIMSON, 1.0, "c")
    tag_a = fd * (1 - ramp(t, 0, 0.0))
    text(ctx, AB.x1, AB.y0 + 6, "measured", 32, CRIMSON, fd, "r")
    if phase2:
        draw_kernel(ctx, Ek, fd * ramp(t, P2A - 0.3, P2A) * (1 - ramp(t, P2B, P2B + 0.4)))
    shown = SAMP <= (EHI + 1 if phase2 else Em)
    if phase2:
        polyline(ctx, AB.pts(EG, BETA), CRIMSON, 2.2, 0.45 * fd)
    for e, b in zip(SAMP[shown], SB[shown]):
        ctx.new_path()
        src(ctx, CRIMSON, fd)
        ctx.arc(AB.X(e), AB.Y(b), 4.6, 0, 2 * math.pi)
        ctx.fill()

    # ---- delta panel
    AD.frame(ctx, xticks=(280, 290, 300, 310, 320), xlabel="Photon energy (eV)", zero=0.0)
    text(ctx, AD.x0 - 26, (AD.y0 + AD.y1) / 2 + 8, "$δ$", 44, BLUE, 1.0, "c")
    kk_a = fd * ramp(t, P2A - 0.6, P2A)
    text(ctx, AD.x1, AD.y0 + 6, "Kramers-Kronig", 32, BLUE, kk_a, "r")
    if phase2:
        m = EG <= Ek
        if m.sum() > 1:
            polyline(ctx, AD.pts(EG[m], DELTA[m]), BLUE, 5.0, fd)

    # ---- cursor across both panels
    ca = ramp(t, 0.0, 0.3) * (1 - ramp(t, P1B + 0.1, P1B + 0.4)) if not phase2 else \
        ramp(t, P2A - 0.3, P2A) * fd
    cx = AB.X(E)
    src(ctx, CLAY, 0.9 * ca)
    ctx.set_line_width(2.4)
    ctx.set_dash([6, 6])
    ctx.move_to(cx, AB.y0)
    ctx.line_to(cx, AD.y1)
    ctx.stroke()
    ctx.set_dash([])
    for ax, val in ((AB, at(BETA, E)), (AD, at(DELTA, E))):
        if ax is AD and not phase2:
            continue
        glow(ctx, cx, ax.Y(val), 22, CLAY, 0.45 * ca)
        ctx.new_path()
        src(ctx, CLAY, ca)
        ctx.arc(cx, ax.Y(val), 7, 0, 2 * math.pi)
        ctx.fill()

    # ---- complex plane
    src(ctx, SLATE, 0.9)
    ctx.set_line_width(3)
    x0 = CP.X(0.0)
    ctx.move_to(CP.x0, CP.y1)
    ctx.line_to(CP.x1, CP.y1)
    ctx.stroke()
    ctx.move_to(x0, CP.y1)
    ctx.line_to(x0, CP.y0)
    ctx.stroke()
    arrow_head(ctx, CP.x1 + 4, CP.y1, 0, 16, SLATE, 0.9)
    arrow_head(ctx, x0, CP.y0 - 4, -math.pi / 2, 16, SLATE, 0.9)
    text(ctx, CP.x1 + 8, CP.y1 + 46, "Re $n$ − 1", 32, SLATE, 1.0, "r")
    text(ctx, x0 - 14, CP.y0 + 14, "Im $n$", 32, SLATE, 1.0, "r")
    text(ctx, CP.x0 - 40, CP.y0 - 18, "$n$ = 1 − $δ$ + $iβ$", 38, INK, 1.0, "l")
    if not phase2:
        b = at(BETA, Em)
        la = ramp(t, 0.0, 0.3) * (1 - ramp(t, P1B + 0.2, P2A - 0.1))
        y = CP.Y(b)
        src(ctx, CRIMSON, 0.75 * la)
        ctx.set_line_width(3)
        ctx.set_dash([3, 8])
        ctx.move_to(CP.x0, y)
        ctx.line_to(CP.x1, y)
        ctx.stroke()
        ctx.set_dash([])
        text(ctx, CP.x0 + 4, y - 14, "$β$ alone", 32, CRIMSON, la)
        text(ctx, CP.X(-2.7), y + 14, "?", 40, CRIMSON, 0.7 * la, "c")
        text(ctx, CP.X(-1.0), y + 14, "?", 40, CRIMSON, 0.7 * la, "c")
    else:
        m = EG <= Ek
        xs, ys = -DELTA[m], BETA[m]
        if m.sum() > 1:
            pts = CP.pts(xs, ys)
            polyline(ctx, pts, INK, 3.4, 0.85 * fd)
        nx, ny = CP.X(-at(DELTA, Ek)), CP.Y(at(BETA, Ek))
        glow(ctx, nx, ny, 28, CLAY, 0.6 * ca)
        ctx.new_path()
        src(ctx, CLAY, ca)
        ctx.arc(nx, ny, 9, 0, 2 * math.pi)
        ctx.fill()
    return surf
