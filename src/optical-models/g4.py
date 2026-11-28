"""GIF 4. The index is a tensor because absorption follows |E . mu|^2. The polarization E
rotates from in plane (x) to the surface normal (z); ring molecules in a flat-lying film light up
in proportion to (E . mu)^2 for their own pi* transition dipole, the measured spectrum moves
between beta_xx and beta_zz, and the matching diagonal component of n is highlighted."""
import math
import numpy as np
from style import *
import spectra as S

DUR = 8.0
ELO, EHI = 280.0, 320.0
EG = np.linspace(ELO, EHI, 801)

# flat-lying (face-on) rings, perfectly aligned: ring plane parallel to the substrate, pi* TDM along z
MOLS = [(x, y) for y in (452, 368) for x in (130, 315, 500)]
TILTS = [90.0] * len(MOLS)        # ring-plane angle from the normal, degrees (90 = lying flat)
BAR = 150
SUB_Y = 488
DIAL = (150, 170, 92)
ROSE = "#E3A9B3"
# pi* TDM angle from the normal implied by the drawn tilts (uniaxial average)
ALPHA = float(np.degrees(np.arccos(np.sqrt(np.mean(np.sin(np.radians(TILTS)) ** 2)))))
M = S.Model(EG)
BXX, _ = M.comp("xx", ALPHA)
BZZ, _ = M.comp("zz", ALPHA)
AS = Axes(690, 66, 1150, 336, (ELO, EHI), (0, max(BXX.max(), BZZ.max()) * 1.1))


def theta(t):
    return math.radians(45 + 45 * math.cos(2 * math.pi * t / DUR))   # 90 -> 0 -> 90 deg


def draw_molecule(ctx, cx, cy, tilt_deg, Evec):
    """Ring seen edge-on (bar) with pi lobes normal to the ring plane. The pi* TDM is the
    lobe axis; the sigma* TDM lies along the bar, in the ring plane."""
    tr = math.radians(tilt_deg)
    b = np.array([math.sin(tr), math.cos(tr)])         # along the ring plane (x, z)
    mu = np.array([math.cos(tr), -math.sin(tr)])       # pi* TDM, normal to the ring plane
    e2 = np.array([Evec[0], Evec[2]])
    ip = float(np.dot(e2, mu)) ** 2
    isg = float(np.dot(e2, b)) ** 2

    def P(s, u):   # point s along the bar, u along the normal -> screen
        return cx + s * b[0] + u * mu[0], cy - (s * b[1] + u * mu[1])

    # sigma* glow along the ring plane
    if isg > 0.01:
        for sc, a in ((1.0, 0.22), (0.6, 0.4)):
            ctx.save()
            ctx.translate(cx, cy)
            ctx.rotate(-math.atan2(b[1], b[0]))
            ctx.scale(BAR / 2 + 18 * sc, 20 * sc)
            ctx.arc(0, 0, 1, 0, 2 * math.pi)
            ctx.restore()
            src(ctx, SKY, a * isg)
            ctx.fill()
    # pi lobes
    ang = -math.atan2(mu[1], mu[0])
    for s in (-48, 0, 48):
        x, y = P(s, 0)
        glow(ctx, x, y, 52, CRIMSON, 0.30 * ip)
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(ang)
        ctx.scale(32, 12)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        src(ctx, IVORY, 0.7)
        ctx.fill_preserve()
        src(ctx, CRIMSON, 0.12 + 0.6 * ip)
        ctx.fill_preserve()
        src(ctx, CRIMSON, 0.45 + 0.5 * ip)
        ctx.set_line_width(1.8)
        ctx.stroke()
    # ring, seen edge-on in this side view
    x0, y0 = P(-BAR / 2, 0)
    x1, y1 = P(BAR / 2, 0)
    src(ctx, DEEP)
    ctx.set_line_width(11)
    ctx.move_to(x0, y0)
    ctx.line_to(x1, y1)
    ctx.stroke()
    for s in (-48, 0, 48):
        x, y = P(s, 0)
        ctx.new_path()
        src(ctx, IVORY)
        ctx.arc(x, y, 3.2, 0, 2 * math.pi)
        ctx.fill()
    # pi* transition dipole
    xa, ya = P(0, -40)
    xb, yb = P(0, 40)
    arrow(ctx, xa, ya, xb, yb, CRIMSON, 3.2, 14, 0.55 + 0.45 * ip, both=True)


def draw_dial(ctx, th):
    cx, cy, R = DIAL
    src(ctx, IVORY, 0.8)
    ctx.arc(cx, cy, R + 14, 0, 2 * math.pi)
    ctx.fill()
    src(ctx, RULE)
    ctx.set_line_width(2)
    ctx.arc(cx, cy, R + 14, 0, 2 * math.pi)
    ctx.stroke()
    arrow(ctx, cx - R, cy, cx + R + 6, cy, SLATE, 2.2, 13, 0.8)
    arrow(ctx, cx, cy + R, cx, cy - R - 6, SLATE, 2.2, 13, 0.8)
    text(ctx, cx + R + 4, cy + 38, "$x$", 32, SLATE)
    text(ctx, cx - 38, cy - R + 8, "$z$", 32, SLATE)
    # theta arc from z axis
    ctx.new_path()
    src(ctx, CLAY, 0.7)
    ctx.set_line_width(2.4)
    ctx.arc(cx, cy, 40, -math.pi / 2, -math.pi / 2 + th)
    ctx.stroke()
    ex, ez = math.sin(th) * (R - 6), math.cos(th) * (R - 6)
    glow(ctx, cx + ex, cy - ez, 30, CLAY, 0.35)
    arrow(ctx, cx - ex, cy + ez, cx + ex, cy - ez, CLAY, 5.5, 22, 1.0, both=True)
    lx, lz = math.sin(th) * (R + 40), math.cos(th) * (R + 40)
    text(ctx, cx + lx, cy - lz + 14, "\\b$E$\\b", 42, CLAY, 1.0, "c")
    text(ctx, cx + R + 60, cy + 70, f"$ϑ$ = {math.degrees(th):.0f}°", 36, INK)


def draw_matrix(ctx, th):
    s2, c2 = math.sin(th) ** 2, math.cos(th) ** 2
    x0, y0 = 760, 470
    dx, dy = 112, 84
    cols = [x0 + dx * i for i in range(3)]
    rows = [y0 + dy * i for i in range(3)]
    # highlights
    for i, (w, col) in enumerate(((s2, CRIMSON), (0.0, MUTED), (c2, BLUE))):
        cx, cy = cols[i], rows[i] - 12
        glow(ctx, cx, cy, 70, col, 0.55 * w)
        if w > 0.02:
            ctx.new_path()
            src(ctx, col, 0.85 * w)
            ctx.set_line_width(3)
            ctx.arc(cx, cy, 42, 0, 2 * math.pi)
            ctx.stroke()
    names = ["xx", "yy", "zz"]
    for i in range(3):
        for j in range(3):
            if i == j:
                col = [CRIMSON, SLATE, BLUE][i]
                a = [0.55 + 0.45 * s2, 0.55, 0.55 + 0.45 * c2][i]
                text(ctx, cols[j], rows[i], f"$n$_{{{names[i]}}}", 46, col, a, "c")
            else:
                text(ctx, cols[j], rows[i], "0", 40, MUTED, 0.9, "c")
    # brackets
    top, bot = rows[0] - 58, rows[2] + 26
    for side, xb in ((-1, cols[0] - 70), (1, cols[2] + 70)):
        src(ctx, INK)
        ctx.set_line_width(4)
        ctx.move_to(xb - side * 0, top)
        ctx.curve_to(xb + side * 22, top + 60, xb + side * 22, bot - 60, xb, bot)
        ctx.stroke()
    text(ctx, cols[0] - 92, rows[1] + 4, "$n$ =", 46, INK, 1.0, "r")
    text(ctx, cols[2] + 98, rows[0] - 4, "sin^{2}$ϑ$", 34, CRIMSON, 0.35 + 0.65 * s2)
    text(ctx, cols[2] + 98, rows[2] - 4, "cos^{2}$ϑ$", 34, BLUE, 0.35 + 0.65 * c2)


def frame(t):
    surf, ctx = new_frame()
    th = theta(t)
    Evec = np.array([math.sin(th), 0.0, math.cos(th)])

    # substrate
    src(ctx, "#B9BEC0")
    rounded_rect(ctx, 30, SUB_Y, 570, 46, 6)
    ctx.fill()
    src(ctx, "#8E979B")
    ctx.rectangle(30, SUB_Y + 30, 570, 16)
    ctx.fill()
    for (x, y), tl in zip(MOLS, TILTS):
        draw_molecule(ctx, x, y, tl, Evec)
    draw_dial(ctx, th)
    text(ctx, 315, SUB_Y + 92, "flat-lying ring molecules", 32, SLATE, 0.95, "c")

    # spectrum
    s2, c2 = math.sin(th) ** 2, math.cos(th) ** 2
    AS.frame(ctx, xticks=(280, 290, 300, 310, 320), tick_labels=False)
    for v in (280, 300, 320):
        text(ctx, AS.X(v), AS.y1 + 42, f"{v}", 32, SLATE, 1.0, "c")
    text(ctx, AS.x0 + (AS.x1 - AS.x0) / 2, AS.y1 + 80, "Photon energy (eV)", 32, SLATE, 1.0, "c")
    text(ctx, AS.x0 - 26, (AS.y0 + AS.y1) / 2 + 8, "$β$", 44, INK, 1.0, "c")
    polyline(ctx, AS.pts(EG, BXX), CRIMSON, 2.4, 0.6, dash=[7, 6])
    polyline(ctx, AS.pts(EG, BZZ), BLUE, 2.4, 0.6, dash=[7, 6])
    cur = BXX * s2 + BZZ * c2
    col = mix(BLUE, CRIMSON, s2)
    pts = AS.pts(EG, cur)
    ctx.set_source_rgba(col[0], col[1], col[2], 0.12)
    ctx.move_to(pts[0][0], AS.y1)
    for p in pts:
        ctx.line_to(*p)
    ctx.line_to(pts[-1][0], AS.y1)
    ctx.close_path()
    ctx.fill()
    ctx.set_source_rgba(*col)
    ctx.set_line_width(5.5)
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.stroke()
    text(ctx, AS.X(287.0), AS.Y(float(BZZ.max())) + 10, "$β$_{zz}", 36, BLUE, 0.95)
    text(ctx, AS.X(305.0), AS.Y(float(np.interp(301, EG, BXX))) - 20, "$β$_{xx}", 36, CRIMSON, 0.95)

    draw_matrix(ctx, th)
    return surf
