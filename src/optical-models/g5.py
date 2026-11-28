"""GIF 5. Angle-resolved NEXAFS measures the tensor. p-polarized spectra at grazing (20 deg),
normal (90 deg), and magic (54.7 deg) incidence on a flat-lying film; the linear dichroism
mu(20) - mu(90); then the uniaxial decomposition with the magic-angle spectrum as beta_iso:
    beta_zz - beta_xx = LD / cos^2(20),  2 beta_xx + beta_zz = 3 beta_iso
For perfectly aligned flat rings the pi* resonance gives beta_zz = 3 beta_iso and beta_xx = 0."""
import math
import numpy as np
from style import *
import spectra as S
import g4

DUR = 13.0
ELO, EHI = 280.0, 320.0
EG = g4.EG
BXX, BZZ = g4.BXX, g4.BZZ
BISO = (2 * BXX + BZZ) / 3


def mu_theta(th_deg):
    t = math.radians(th_deg)
    return BXX * math.sin(t) ** 2 + BZZ * math.cos(t) ** 2


ANG = [20.0, 90.0, 54.7]
NAMES = ["grazing", "normal", "magic angle"]
MU = [mu_theta(a) for a in ANG]
LD = MU[0] - MU[1]
LDP = LD / math.cos(math.radians(20.0)) ** 2
BZZ_D = BISO + 2 * LDP / 3
BXX_D = BISO - LDP / 3

AM = Axes(640, 62, 1150, 292, (ELO, EHI), (0, 8.9))
AL = Axes(640, 392, 1150, 642, (ELO, EHI), (-1.8, 8.9))

BLK = 1.9
P_LD = (5.9, 7.5)
P_C = (7.8, 9.6)
FADE = (12.0, 12.8)

P0 = (300, 352)          # beam footprint, at the film surface
SUB = (70, 470, 460, 42)


def col_for(th_deg):
    s2 = math.sin(math.radians(th_deg)) ** 2
    return mix(BLUE, CRIMSON, s2)


def angle_at(t):
    # block k: swing 0.5 s from the previous angle, then hold
    if t >= 3 * BLK:
        return ANG[2]
    k = int(t // BLK)
    prev = ANG[k - 1] if k > 0 else ANG[2]
    u = ramp(t - k * BLK, 0.0, 0.5)
    return lerp(prev, ANG[k], u)


def sweep_frac(t, k):
    return ramp(t - k * BLK, 0.55, 1.65)


def draw_curve(ctx, ax, y, frac, color_rgba, width, alpha=1.0, dash=None):
    n = int(len(EG) * clamp(frac))
    if n < 2:
        return
    pts = ax.pts(EG[:n], y[:n])
    c = color_rgba
    ctx.set_source_rgba(c[0], c[1], c[2], alpha)
    ctx.set_line_width(width)
    if dash:
        ctx.set_dash(dash)
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.stroke()
    ctx.set_dash([])


def draw_geometry(ctx, t, th):
    x, y, w, h = SUB
    src(ctx, "#B9BEC0")
    rounded_rect(ctx, x, y, w, h, 6)
    ctx.fill()
    src(ctx, "#8E979B")
    ctx.rectangle(x, y + 26, w, h - 26)
    ctx.fill()
    tr = math.radians(th)
    Evec = np.array([math.sin(tr), 0.0, math.cos(tr)])
    for (mx, my) in [(cx, cy) for cy in (440, 382) for cx in (160, 300, 440)]:
        ctx.save()
        ctx.translate(mx, my)
        ctx.scale(0.78, 0.78)
        g4.draw_molecule(ctx, 0, 0, 90.0, Evec)
        ctx.restore()
    # incoming beam
    k = (math.cos(tr), math.sin(tr))
    L = 300
    sx, sy = P0[0] - L * k[0], P0[1] - L * k[1]
    ex, ey = P0[0] - 4 * k[0], P0[1] - 4 * k[1]
    tx, ty = P0
    src(ctx, CLAY, 0.35)
    ctx.set_line_width(2)
    ctx.set_dash([3, 7])
    ctx.move_to(sx, sy)
    ctx.line_to(tx, ty)
    ctx.stroke()
    ctx.set_dash([])
    span = 330.0
    v = span * 9 / DUR
    for j in range(3):
        s = (v * t + j * 110) % span
        if s > L - 70:
            continue
        a = clamp(s / 40) * clamp((L - 70 - s) / 40)
        wave_packet(ctx, sx + s * k[0], sy + s * k[1], math.atan2(k[1], k[0]), 46, 15, 16,
                    2 * math.pi * 2 * t, CLAY, a)
    arrow_head(ctx, ex, ey, math.atan2(k[1], k[0]), 22, CLAY, 0.9)
    # E vector at mid-beam, perpendicular to k in the plane of incidence
    mx, my = sx + 0.40 * L * k[0], sy + 0.40 * L * k[1]
    e = (math.sin(tr), -math.cos(tr))
    glow(ctx, mx + 52 * e[0], my + 52 * e[1], 26, CLAY, 0.35)
    arrow(ctx, mx - 52 * e[0], my - 52 * e[1], mx + 52 * e[0], my + 52 * e[1], CLAY, 5, 20, 1.0, both=True)
    text(ctx, mx + 66 * e[0] + (16 if e[0] >= 0 else -16), my + 66 * e[1] + 12, "\\b$E$\\b", 40, CLAY, 1.0,
         "l" if e[0] >= 0 else "r")
    # incidence angle, measured from the surface
    ctx.new_path()
    src(ctx, INK, 0.75)
    ctx.set_line_width(2.4)
    ctx.arc(tx, ty, 74, math.pi, math.pi + tr)
    ctx.stroke()
    src(ctx, INK, 0.5)
    ctx.set_line_width(1.6)
    ctx.set_dash([4, 5])
    ctx.move_to(tx - 120, ty)
    ctx.line_to(tx, ty)
    ctx.stroke()
    ctx.set_dash([])
    text(ctx, 40, 62, f"$ϑ$ = {th:.1f}°" if abs(th - 54.7) < 0.05 else f"$ϑ$ = {th:.0f}°", 42, INK)
    name = None
    for a, nm in zip(ANG, NAMES):
        if abs(th - a) < 0.3:
            name = nm
    if name:
        text(ctx, 40, 108, name, 34, SLATE)


def draw_steps(ctx, t):
    labels = ["Measure three angles", "Linear dichroism", "Uniaxial tensor"]
    active = 0 if t < P_LD[0] - 0.2 else (1 if t < P_C[0] - 0.2 else 2)
    if t >= FADE[0]:
        active = -1
    y = 600
    for i, lab in enumerate(labels):
        yy = y + i * 54
        on = i == active
        ctx.new_path()
        src(ctx, CRIMSON if on else RULE)
        ctx.arc(58, yy - 11, 17, 0, 2 * math.pi)
        ctx.fill()
        text(ctx, 58, yy - 1, str(i + 1), 24, IVORY, 1.0, "c")
        text(ctx, 90, yy, lab, 32, CRIMSON if on else SLATE, 1.0 if on else 0.75)


def frame(t):
    surf, ctx = new_frame()
    fd = 1 - ramp(t, *FADE)
    th = angle_at(t)
    draw_geometry(ctx, t, th)
    draw_steps(ctx, t)

    # ---- measured spectra
    AM.frame(ctx, xticks=(280, 290, 300, 310, 320), tick_labels=False)
    text(ctx, AM.x0 - 30, (AM.y0 + AM.y1) / 2 + 8, "$μ$", 44, INK, 1.0, "c")
    dim_meas = 0.35 if P_LD[0] - 0.3 <= t < FADE[0] else 1.0
    for k in range(3):
        f = sweep_frac(t, k) if t < 3 * BLK else 1.0
        if t < k * BLK:
            continue
        a = fd * (1.0 if (k < 2 and t >= P_LD[0] - 0.3 and t < P_C[0] - 0.3) else dim_meas)
        if k == 2 and P_C[0] - 0.3 <= t < FADE[0]:
            a = fd
        current = (t < 3 * BLK) and int(t // BLK) == k
        draw_curve(ctx, AM, MU[k], f, col_for(ANG[k]), 5.0 if current else 3.2, a)
    lab_pos = [(286.0, float(MU[0].max()) - 0.3), (296.5, float(np.interp(293.5, EG, MU[1])) + 1.5),
               (286.0, float(MU[2].max()) + 0.5)]
    for k in range(3):
        if t >= k * BLK + 1.0:
            text(ctx, AM.X(lab_pos[k][0]), AM.Y(lab_pos[k][1]), f"{ANG[k]:g}°", 32, INK,
                 fd * ramp(t, k * BLK + 1.0, k * BLK + 1.3))

    # ---- lower panel
    AL.frame(ctx, xticks=(280, 290, 300, 310, 320), xlabel="Photon energy (eV)", zero=0.0)
    ld_on = ramp(t, P_LD[0] - 0.3, P_LD[0])
    comp_on = ramp(t, P_C[0] - 0.3, P_C[0])
    text(ctx, AL.x0 - 30, (AL.y0 + AL.y1) / 2 + 8, "LD", 36, CLAY, fd * ld_on * (1 - comp_on), "c")
    text(ctx, AL.x0 - 30, (AL.y0 + AL.y1) / 2 + 8, "$β$", 44, INK, fd * comp_on, "c")
    if t >= P_LD[0] - 0.3:
        f = ramp(t, P_LD[0], P_LD[1])
        draw_curve(ctx, AL, LD, f, hexrgb(CLAY), 4.5, fd * (1 - 0.75 * comp_on))
        text(ctx, AL.x1, AL.y0 + 6, "LD = $μ$(20°) − $μ$(90°)", 30, CLAY, fd * ld_on * (1 - comp_on), "r")
    if t >= P_C[0] - 0.3:
        draw_curve(ctx, AL, BISO, 1.0, hexrgb(INK), 3.0, fd * comp_on, dash=[8, 6])
        f = ramp(t, P_C[0], P_C[1])
        draw_curve(ctx, AL, BZZ_D, f, hexrgb(BLUE), 5.0, fd)
        draw_curve(ctx, AL, BXX_D, f, hexrgb(CRIMSON), 5.0, fd)
        an = fd * ramp(t, P_C[1], P_C[1] + 0.5)
        pk = float(BZZ_D.max())
        text(ctx, AL.X(286.0), AL.Y(pk) + 14, "$β$_{zz} = 3$β$_{iso}", 32, BLUE, an)
        text(ctx, AL.X(286.8), AL.Y(float(BISO.max())) + 12, "$β$_{iso}", 30, INK, an)
        text(ctx, AL.X(286.0), AL.Y(0) + 30, "$β$_{xx} = 0", 30, CRIMSON, an)
        text(ctx, AL.X(305.5), AL.Y(float(np.interp(301, EG, BXX_D))) - 16, "$β$_{xx}", 30, CRIMSON, an)
    return surf
