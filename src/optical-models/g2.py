"""GIF 2. Local bonds make local empty states. A C 1s electron on one ring carbon is
promoted into the pi* and sigma* orbitals that the bonds create; the level ladder shows the
transition, the ring shows where the state lives, and the spectrum builds the fine structure
on top of the bare-atom edge."""
import math
import numpy as np
from style import *
import spectra as S

DUR = 8.5
ELO, EHI = 280.0, 320.0
EG = np.linspace(ELO, EHI, 801)
M = S.Model(EG)
BETA, _ = M.iso()
BARE = M.bb
PIW = M.group(S.PI_IDX)
SIGW = M.group(S.SIG_IDX)
PIW_N = PIW / PIW.max()
SIGW_N = SIGW / SIGW.max()
RESN = (BETA - BETA.min()) / (BETA.max() - BETA.min())   # absorption strength, 0 to 1

AX = Axes(110, 470, 1150, 668, (ELO, EHI), (0, BETA.max() * 1.12))

# molecule geometry
MCX, MCY, R, SQ = 315, 236, 150, 0.42
EXC = 2  # excited carbon index (front left)


def ring_pt(j, rr=R):
    a = math.radians(60 * j)          # j=0 right vertex; +y is down, so j=1,2 are in front
    return MCX + rr * math.cos(a), MCY + SQ * rr * math.sin(a)


def _g(E, e0, s):
    return np.exp(-0.5 * ((E - e0) / s) ** 2)


# slow the sweep where the resonances are, so the pi* moment is held on screen
DWELL = 1 + 14 * _g(EG, 285.1, 0.7) + 4 * _g(EG, 290.3, 0.8) + 4 * _g(EG, 293.5, 1.5) + 1.2 * _g(EG, 301.0, 2.5)
CUM = np.concatenate([[0], np.cumsum(0.5 * (DWELL[1:] + DWELL[:-1]) * np.diff(EG))])
CUM /= CUM[-1]
T0, T1 = 0.4, 6.8


def energy(t):
    u = clamp((t - T0) / (T1 - T0))
    u = 0.5 - 0.5 * math.cos(math.pi * u)
    return float(np.interp(u, CUM, EG))


def fade(t):
    return 1 - ramp(t, 7.7, 8.4)


def at(arr, E):
    return float(np.interp(E, EG, arr))


ROSE = "#E3A9B3"

# level diagram mapping
LY_TOP, LY_BOT = 50, 318
LX0, LX1 = 735, 1150


_LE = [280.0, 285.1, 290.3, 293.5, 301.0, 320.0]
_LYv = [318, 262, 200, 164, 118, 56]


def LY(h):
    return float(np.interp(h, _LE, _LYv))


Y1S = 402


def draw_levels(ctx, E, fd):
    pi_a = at(PIW_N, E) * fd
    sig_a = at(SIGW_N, E) * fd
    # continuum above IP
    ip = 290.3
    g = cairo.LinearGradient(0, LY(ip), 0, LY_TOP - 10)
    c = hexrgb(TAUPE)
    g.add_color_stop_rgba(0, c[0], c[1], c[2], 0.10)
    g.add_color_stop_rgba(1, c[0], c[1], c[2], 0.42)
    ctx.set_source(g)
    ctx.rectangle(LX0 + 40, LY_TOP - 10, LX1 - LX0 - 40, LY(ip) - LY_TOP + 10)
    ctx.fill()
    # sigma* shape resonances inside the continuum
    for e0, hw in ((293.5, 1.2), (301.0, 2.6)):
        y0, y1 = LY(e0 + hw), LY(e0 - hw)
        src(ctx, SKY, 0.22 + 0.55 * sig_a)
        rounded_rect(ctx, LX0 + 70, y0, 180, y1 - y0, min(10, (y1 - y0) / 2))
        ctx.fill()
    text(ctx, LX0 + 262, LY(296.5) + 14, "$σ$^{*}", 42, BLUE, 0.6 + 0.4 * sig_a)
    text(ctx, LX1 - 8, LY_TOP + 34, "continuum", 30, SLATE, 0.9, "r")
    # IP
    src(ctx, SLATE, 0.8)
    ctx.set_line_width(2.4)
    ctx.set_dash([8, 6])
    ctx.move_to(LX0 + 40, LY(ip))
    ctx.line_to(LX1, LY(ip))
    ctx.stroke()
    ctx.set_dash([])
    text(ctx, LX1 - 6, LY(ip) - 12, "ionization", 30, SLATE, 0.9, "r")
    # pi* levels (bound, below IP)
    for e0, wdt in ((285.1, 6.0),):
        glow(ctx, LX0 + 195, LY(e0), 150, CRIMSON, 0.0)
        src(ctx, CRIMSON, 0.55 + 0.45 * pi_a)
        ctx.set_line_width(wdt)
        ctx.move_to(LX0 + 70, LY(e0))
        ctx.line_to(LX0 + 250, LY(e0))
        ctx.stroke()
    if pi_a > 0.01:
        src(ctx, CRIMSON, 0.22 * pi_a)
        rounded_rect(ctx, LX0 + 62, LY(285.1) - 12, 196, 24, 12)
        ctx.fill()
    text(ctx, LX0 + 262, LY(285.1) + 14, "$π$^{*}", 42, CRIMSON, 0.6 + 0.4 * pi_a)
    # 1s
    src(ctx, INK, 0.9)
    ctx.set_line_width(5)
    ctx.move_to(LX0 + 70, Y1S)
    ctx.line_to(LX0 + 250, Y1S)
    ctx.stroke()
    text(ctx, LX0 + 262, Y1S + 13, "C 1s", 38, INK)

    # transition arrow of length h nu, with an axis break
    ax = LX0 + 125
    tip = LY(E)
    yb = 360
    src(ctx, CLAY, 0.95)
    ctx.set_line_width(4)
    ctx.move_to(ax, Y1S - 12)
    ctx.line_to(ax, yb + 8)
    ctx.stroke()
    ctx.move_to(ax, yb - 8)
    ctx.line_to(ax, tip + 14)
    ctx.stroke()
    src(ctx, BG)
    for dy in (-8, 8):
        pass
    src(ctx, CLAY)
    ctx.set_line_width(3)
    for dy in (-8, 8):
        ctx.move_to(ax - 14, yb + dy + 5)
        ctx.line_to(ax + 14, yb + dy - 5)
        ctx.stroke()
    arrow_head(ctx, ax, tip, -math.pi / 2, 22, CLAY)
    text(ctx, ax - 22, (Y1S + LY(ELO)) / 2 + 26, "h$ν$", 40, CLAY, 1.0, "r")

    # electrons
    res = at(RESN, E) * fd
    electron(ctx, ax + 46, Y1S, 11)
    hole(ctx, ax, Y1S, 11, res)
    electron(ctx, ax, Y1S, 11, 1 - res)
    glow(ctx, ax, tip, 40, CLAY if E < ip else SKY, 0.6 * res)
    electron(ctx, ax, tip - 2, 11, res)


def draw_molecule(ctx, E, fd):
    pi_a = at(PIW_N, E) * fd
    sig_a = at(SIGW_N, E) * fd
    res = at(RESN, E) * fd
    dist = [min(abs(j - EXC), 6 - abs(j - EXC)) for j in range(6)]
    wloc = [math.exp(-d / 1.1) for d in dist]
    order = sorted(range(6), key=lambda j: ring_pt(j)[1])  # back to front

    def lobes(upper):
        for j in order:
            x, y = ring_pt(j)
            sgn = (1 if j % 2 == 0 else -1) * (1 if upper else -1)
            cy = y - 58 if upper else y + 58
            amp = pi_a * wloc[j]
            ctx.save()
            ctx.translate(x, cy)
            ctx.scale(1, 2.35)
            ctx.arc(0, 0, 22, 0, 2 * math.pi)
            ctx.restore()
            base = CRIMSON if sgn > 0 else ROSE
            src(ctx, IVORY, 0.55)
            ctx.fill_preserve()
            src(ctx, base, 0.85 * amp)
            ctx.fill_preserve()
            src(ctx, CRIMSON, 0.30 + 0.6 * amp)
            ctx.set_line_width(2.0)
            if amp < 0.15:
                ctx.set_dash([5, 5])
            ctx.stroke()
            ctx.set_dash([])

    lobes(False)
    # C-H bonds and H atoms
    for j in order:
        x, y = ring_pt(j)
        hx, hy = ring_pt(j, R + 70)
        src(ctx, SLATE, 0.8)
        ctx.set_line_width(5)
        ctx.move_to(x, y)
        ctx.line_to(hx, hy)
        ctx.stroke()
        ctx.new_path()
        src(ctx, IVORY)
        ctx.arc(hx, hy, 13, 0, 2 * math.pi)
        ctx.fill_preserve()
        src(ctx, MUTED)
        ctx.set_line_width(2)
        ctx.stroke()
    # sigma* along bonds at the excited carbon
    ex, ey = ring_pt(EXC)
    for nb in ((EXC + 1) % 6, (EXC - 1) % 6, "H"):
        if nb == "H":
            bx, by = ring_pt(EXC, R + 70)
        else:
            bx, by = ring_pt(nb)
        mx, my = (ex + bx) / 2, (ey + by) / 2
        L = math.hypot(bx - ex, by - ey)
        ang = math.atan2(by - ey, bx - ex)
        if sig_a > 0.01:
            for sc, a in ((1.0, 0.30), (0.62, 0.55)):
                ctx.save()
                ctx.translate(mx, my)
                ctx.rotate(ang)
                ctx.scale((L / 2 + 22) * sc, 22 * sc)
                ctx.arc(0, 0, 1, 0, 2 * math.pi)
                ctx.restore()
                src(ctx, SKY, a * sig_a)
                ctx.fill()
    # ring bonds (aromatic, drawn as the deck's deep-crimson bars)
    pts = [ring_pt(j) for j in range(6)]
    src(ctx, DEEP)
    ctx.set_line_width(9)
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.close_path()
    ctx.stroke()
    for j, (x, y) in enumerate(pts):
        ctx.new_path()
        src(ctx, IVORY)
        ctx.arc(x, y, 10 if j != EXC else 13, 0, 2 * math.pi)
        ctx.fill_preserve()
        src(ctx, DEEP)
        ctx.set_line_width(3)
        ctx.stroke()
    lobes(True)
    # transition dipoles at the excited carbon, each fading in with its own resonance
    #   pi*   : normal to the ring plane, along the lobe axis (vertical in this view)
    #   sigma*: in the ring plane, along the C-C bonds at the excited carbon
    pa = 0.18 + 0.82 * pi_a
    arrow(ctx, ex, ey + 128, ex, ey - 128, DEEP, 4.2, 20, pa, both=True)
    text(ctx, ex + 18, ey + 124, "$μ_{π*}$", 36, DEEP, pa)
    sa = 0.18 + 0.82 * sig_a
    for nb in ((EXC + 1) % 6, (EXC - 1) % 6):
        bx, by = ring_pt(nb)
        ux, uy = bx - ex, by - ey
        L = math.hypot(ux, uy)
        ux, uy = ux / L, uy / L
        mx, my = (ex + bx) / 2, (ey + by) / 2
        nx, ny = -uy, ux                       # offset outward from the ring centre so the arrow sits beside its bond
        if (mx - MCX) * nx + (my - MCY) * ny < 0:
            nx, ny = -nx, -ny
        mx, my = mx + 24 * nx, my + 24 * ny
        h = L / 2 + 6
        arrow(ctx, mx - h * ux, my - h * uy, mx + h * ux, my + h * uy, NAVY, 3.6, 18, sa, both=True)
    bx, by = ring_pt((EXC - 1) % 6)
    text(ctx, (ex + bx) / 2, (ey + by) / 2 + 66, "$μ_{σ*}$", 36, NAVY, sa, "c")
    # absorbing core site
    glow(ctx, ex, ey, 46, CLAY, 0.85 * res)
    src(ctx, CLAY, 0.6 + 0.4 * res)
    ctx.new_path()
    ctx.arc(ex, ey, 6.5, 0, 2 * math.pi)
    ctx.fill()
    # label on the excited carbon's 1s
    text(ctx, ex - 40, ey + 92, "C 1s", 34, INK, 0.9, "r")
    src(ctx, SLATE, 0.6)
    ctx.set_line_width(1.6)
    ctx.move_to(ex - 36, ey + 80)
    ctx.line_to(ex - 10, ey + 12)
    ctx.stroke()


def frame(t):
    surf, ctx = new_frame()
    E = energy(t)
    fd = fade(t)
    draw_molecule(ctx, E, fd)
    draw_levels(ctx, E, fd)

    AX.frame(ctx, xticks=(280, 290, 300, 310, 320), xlabel="Photon energy (eV)")
    text(ctx, AX.x0 - 30, (AX.y0 + AX.y1) / 2, "Absorption", 36, SLATE, 1.0, "c", rotate=-math.pi / 2)
    # ionization threshold, the same line as in the level ladder
    xip = AX.X(S.IP)
    src(ctx, SLATE, 0.7)
    ctx.set_line_width(2.0)
    ctx.set_dash([8, 6])
    ctx.move_to(xip, AX.y0 - 4)
    ctx.line_to(xip, AX.y1)
    ctx.stroke()
    ctx.set_dash([])
    text(ctx, xip + 10, AX.y0 + 22, "ionization", 30, SLATE, 0.9)
    m = EG <= E
    if m.sum() > 1:
        pts = AX.pts(EG[m], BETA[m])
        fill_under(ctx, pts, AX.y1, CRIMSON, 0.10 * fd)
        polyline(ctx, pts, CRIMSON, 5.5, fd)
    if E > 285.6:
        text(ctx, AX.X(285.1) + 16, AX.Y(at(BETA, 285.1)) + 26, "$π$^{*}", 40, CRIMSON,
             fd * ramp(E, 285.6, 286.6))
    if E > 294.5:
        text(ctx, AX.X(296.5), AX.Y(at(BETA, 293.5)) - 10, "$σ$^{*}", 40, BLUE,
             fd * ramp(E, 294.5, 295.5), "c")
    cx = AX.X(E)
    ca = fd * ramp(t, 0.0, 0.35)
    src(ctx, CLAY, 0.9 * ca)
    ctx.set_line_width(2.4)
    ctx.set_dash([6, 6])
    ctx.move_to(cx, AX.y0 - 6)
    ctx.line_to(cx, AX.y1)
    ctx.stroke()
    ctx.set_dash([])
    yv = AX.Y(at(BETA, E)) if fd > 0.5 else AX.Y(at(BETA, E))
    glow(ctx, cx, yv, 22, CLAY, 0.45 * ca)
    ctx.new_path()
    src(ctx, CLAY, ca)
    ctx.arc(cx, yv, 7, 0, 2 * math.pi)
    ctx.fill()
    return surf
