"""Six display graphics for the 'Altering the optical response' slide.

Visual grammar shared by all six: the reference state is drawn in gray, the
perturbed state in colour (crimson for structural and chemical changes, blue for
added electrons, clay for added holes). Each spectrum strip is schematic (no
energy scale), gray = reference film, colour = perturbed state.
"""
import math, os, sys
import cairo
from style import (hexrgb, src, text, text_width, arrow, arrow_head, electron, glow,
                   polyline, fill_under, rounded_rect,
                   INK, SLATE, MUTED, RULE, CRIMSON, DEEP, CLAY, RUST, BLUE, SKY, ICE,
                   TAUPE, NAVY, IVORY)

W, H = 1300, 640           # 3.25 in x 1.60 in at 400 dpi
CARD = "#F4F1EE"
GRAY = "#A7A9A8"
GRAYD = "#8A8F90"
LAB = 52                   # label size, px (about 9.4 pt at 400 dpi)
OUT = sys.argv[1] if len(sys.argv) > 1 else "out"


# ------------------------------------------------------------------ helpers

def erf(x):
    return math.erf(x)


def model(x, peaks, step=(0.80, 0.30, 0.04)):
    xs, S, w = step
    y = S * 0.5 * (1 + erf((x - xs) / w))
    for x0, A, s in peaks:
        y += A * math.exp(-0.5 * ((x - x0) / s) ** 2)
    return y


def spectrum(ctx, curves, edge, box=(780, 70, 1280, 560), ymax=1.15):
    x0, y0, x1, y1 = box
    # axes
    src(ctx, SLATE)
    ctx.set_line_width(4)
    ctx.move_to(x0, y0 + 10); ctx.line_to(x0, y1); ctx.stroke()
    arrow(ctx, x0, y1, x1, y1, SLATE, width=4, head=20)
    text(ctx, x1 - 4, y1 + 58, "$E$", LAB, SLATE, anchor="r")
    text(ctx, x0 - 16, y0 + 40, "$β$", LAB, SLATE, anchor="r")
    text(ctx, x1, y0 + 34, edge, LAB * 0.9, SLATE, anchor="r")
    n = 260
    for fn, color, width, fill in curves:
        pts = []
        for i in range(n + 1):
            u = i / n
            v = fn(u)
            pts.append((x0 + 8 + u * (x1 - x0 - 30), y1 - 4 - v / ymax * (y1 - y0 - 20)))
        if fill:
            fill_under(ctx, pts, y1 - 2, color, fill)
        polyline(ctx, pts, color, width)


def disc(ctx, x, y, r, fill=CARD, a=1.0):
    src(ctx, fill, a)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()


def atom_label(ctx, x, y, s, color, size=LAB):
    text(ctx, x, y + size * 0.34, s, size, color, anchor="c")


def bond(ctx, p, q, color, w=5.5, shrink=(0, 0)):
    (x0, y0), (x1, y1) = p, q
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    a, b = shrink
    polyline(ctx, [(x0 + ux * a, y0 + uy * a), (x1 - ux * b, y1 - uy * b)], color, w)


def inner_double(ctx, p, q, c, color, w=5.0, off=13, trim=0.2):
    """Second line of a ring double bond, offset toward ring centre c."""
    (x0, y0), (x1, y1) = p, q
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = c[0] - mx, c[1] - my
    L = math.hypot(dx, dy)
    ox, oy = dx / L * off, dy / L * off
    sx = x0 + (x1 - x0) * trim + ox
    sy = y0 + (y1 - y0) * trim + oy
    ex = x1 - (x1 - x0) * trim + ox
    ey = y1 - (y1 - y0) * trim + oy
    polyline(ctx, [(sx, sy), (ex, ey)], color, w)


def outer_double(ctx, p, q, color, w=5.0, off=7):
    (x0, y0), (x1, y1) = p, q
    L = math.hypot(x1 - x0, y1 - y0)
    nx, ny = -(y1 - y0) / L * off, (x1 - x0) / L * off
    polyline(ctx, [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny)], color, w)
    polyline(ctx, [(x0 - nx, y0 - ny), (x1 - nx, y1 - ny)], color, w)


def hexagon(cx, cy, R, start=90):
    return [(cx + R * math.cos(math.radians(start - 60 * k)),
             cy - R * math.sin(math.radians(start - 60 * k))) for k in range(6)]


def equilibrium(ctx, x0, x1, y, color=SLATE):
    g = 9
    polyline(ctx, [(x0, y - g), (x1, y - g)], color, 4.5)
    polyline(ctx, [(x1 - 22, y - g - 14), (x1, y - g)], color, 4.5)
    polyline(ctx, [(x0, y + g), (x1, y + g)], color, 4.5)
    polyline(ctx, [(x0 + 22, y + g + 14), (x0, y + g)], color, 4.5)


def clay_hole(ctx, x, y, r=17):
    src(ctx, IVORY)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill_preserve()
    src(ctx, RUST)
    ctx.set_line_width(4)
    ctx.set_dash([7, 5])
    ctx.stroke()
    ctx.set_dash([])


def level(ctx, x0, x1, y, color, w=7):
    polyline(ctx, [(x0, y), (x1, y)], color, w)


# ------------------------------------------------------------------ 1a torsion

def proj(p, az=-58, el=20, s=46, ox=0, oy=0):
    a, e = math.radians(az), math.radians(el)
    x, y, z = p
    xr = x * math.cos(a) - y * math.sin(a)
    yr = x * math.sin(a) + y * math.cos(a)
    sx = xr
    up = yr * math.sin(e) + z * math.cos(e)
    depth = -yr * math.cos(e) + z * math.sin(e)
    return (ox + s * sx, oy - s * up, depth)


def biphenyl(ctx, ox, oy, phi, col_bond, col_fill, col_tdm, s=40, ref=False):
    r, dc = 1.40, 2.14
    rings = []
    for side, ang in ((-1, 0.0), (1, phi)):
        c = (side * dc, 0.0, 0.0)
        b = (0.0, math.cos(ang), math.sin(ang))        # in-plane, perpendicular to x
        n = (0.0, -math.sin(ang), math.cos(ang))       # ring normal
        atoms = []
        for k in range(6):
            t = math.radians(60 * k)
            atoms.append((c[0] + r * math.cos(t), r * math.sin(t) * b[1], r * math.sin(t) * b[2]))
        rings.append((c, atoms, n))
    P = lambda p: proj(p, s=s, ox=ox, oy=oy)
    # TDMs behind first (lower half), rings, then TDMs (upper half)
    L = 1.75
    for c, atoms, n in rings:
        lo = P((c[0] - n[0] * L, c[1] - n[1] * L, c[2] - n[2] * L))
        cc = P(c)
        polyline(ctx, [lo[:2], cc[:2]], col_tdm, 5.5)
        arrow_head(ctx, lo[0], lo[1], math.atan2(lo[1] - cc[1], lo[0] - cc[0]), 22, col_tdm)
    for c, atoms, n in rings:
        pts = [P(a)[:2] for a in atoms]
        src(ctx, col_fill, 0.30 if not ref else 0.22)
        ctx.move_to(*pts[0])
        for q in pts[1:]:
            ctx.line_to(*q)
        ctx.close_path(); ctx.fill()
        for k in range(6):
            polyline(ctx, [pts[k], pts[(k + 1) % 6]], col_bond, 5.5)
    # inter-ring bond
    a = P((-dc + r, 0, 0)); b = P((dc - r, 0, 0))
    polyline(ctx, [a[:2], b[:2]], col_bond, 5.5)
    for c, atoms, n in rings:
        for q in atoms:
            pp = P(q)
            disc(ctx, pp[0], pp[1], 7.5, IVORY)
            src(ctx, col_bond); ctx.set_line_width(3)
            ctx.arc(pp[0], pp[1], 7.5, 0, 2 * math.pi); ctx.stroke()
    tips = []
    for c, atoms, n in rings:
        cc = P(c)
        hi = P((c[0] + n[0] * L, c[1] + n[1] * L, c[2] + n[2] * L))
        polyline(ctx, [cc[:2], hi[:2]], col_tdm, 5.5)
        arrow_head(ctx, hi[0], hi[1], math.atan2(hi[1] - cc[1], hi[0] - cc[0]), 22, col_tdm)
        tips.append((cc, hi))
    return tips


def d_torsion(ctx):
    t0 = biphenyl(ctx, 220, 320, 0.0, GRAYD, GRAY, GRAYD, s=72, ref=True)
    tips = biphenyl(ctx, 730, 320, math.radians(-55), DEEP, CRIMSON, NAVY, s=72)
    arrow(ctx, 440, 320, 515, 320, SLATE, width=4.5, head=18)
    text(ctx, t0[0][1][0] - 26, t0[0][1][1] + 22, "$μ$", LAB, GRAYD, anchor="r")
    # angle mark between the two TDMs of the twisted molecule
    (c1, h1), (c2, h2) = tips
    a1 = math.atan2(h1[1] - c1[1], h1[0] - c1[0])
    a2 = math.atan2(h2[1] - c2[1], h2[0] - c2[0])
    cx, cy, R = c2[0], c2[1], 92
    # reference direction (parallel to TDM 1) drawn faint from ring-2 centre
    polyline(ctx, [(cx, cy), (cx + 1.25 * R * math.cos(a1), cy + 1.25 * R * math.sin(a1))], NAVY, 3,
             alpha=1.0, dash=[8, 7])
    src(ctx, NAVY)
    ctx.set_line_width(3.5)
    lo, hi = sorted((a1, a2))
    ctx.arc(cx, cy, R, lo, hi); ctx.stroke()
    m = (a1 + a2) / 2
    text(ctx, cx + (R + 34) * math.cos(m), cy + (R + 34) * math.sin(m) + 18, "$φ$", LAB, NAVY, anchor="c")


# ------------------------------------------------------------------ 1b tautomer

def pyridine_frame(cx, cy, R):
    # vertices: N1 210 deg, C2 150, C3 90, C4 30, C5 -30, C6 -90
    angs = [210, 150, 90, 30, -30, -90]
    return [(cx + R * math.cos(math.radians(a)), cy - R * math.sin(math.radians(a))) for a in angs]


def tautomer(ctx, cx, cy, R, lactam, cb, cN):
    v = pyridine_frame(cx, cy, R)
    c = (cx, cy)
    N1, C2 = v[0], v[1]
    rN = LAB * 0.45
    for k in range(6):
        p, q = v[k], v[(k + 1) % 6]
        bond(ctx, p, q, cb, shrink=(rN if k == 0 else 0, rN if (k + 1) % 6 == 0 else 0))
    doubles = [(2, 3), (4, 5)] + ([] if lactam else [(0, 1)])
    for i, j in doubles:
        inner_double(ctx, v[i], v[j], c, cb)
    # exocyclic O on C2 along 150 deg
    a = math.radians(150)
    O = (C2[0] + R * math.cos(a), C2[1] - R * math.sin(a))
    if lactam:
        outer_double(ctx, C2, (O[0] + rN * math.cos(a) * -1, O[1] - rN * math.sin(a) * -1), cb)
    else:
        bond(ctx, C2, O, cb, shrink=(0, rN))
    # glow on N, the probed site
    glow(ctx, N1[0], N1[1], 46, CRIMSON if lactam else GRAY, 0.35)
    atom_label(ctx, *O, "O", cb)
    atom_label(ctx, *N1, "N", cN)
    # migrating H, clay in both tautomers
    if lactam:
        a = math.radians(210)
        Hh = (N1[0] + 1.05 * R * math.cos(a), N1[1] - 1.05 * R * math.sin(a))
        bond(ctx, N1, Hh, cb, shrink=(rN, rN))
    else:
        a = math.radians(90)
        Hh = (O[0] + 1.05 * R * math.cos(a), O[1] - 1.05 * R * math.sin(a))
        bond(ctx, O, Hh, cb, shrink=(rN, rN))
    atom_label(ctx, *Hh, "H", RUST)


def d_tautomer(ctx):
    tautomer(ctx, 215, 330, 92, False, GRAYD, GRAYD)
    equilibrium(ctx, 350, 440, 330)
    tautomer(ctx, 610, 330, 92, True, DEEP, CRIMSON)


# ------------------------------------------------------------------ 2a intercalation

def edge_on(ctx, x, y, color, tilt=18, L=44, w=10):
    a = math.radians(tilt)
    dx, dy = L / 2 * math.cos(a), -L / 2 * math.sin(a)
    polyline(ctx, [(x - dx, y - dy), (x + dx, y + dy)], color, w)


def ion(ctx, x, y, sign, r=17):
    col = RUST if sign > 0 else BLUE
    disc(ctx, x, y, r, IVORY)
    src(ctx, col); ctx.set_line_width(4)
    ctx.arc(x, y, r, 0, 2 * math.pi); ctx.stroke()
    polyline(ctx, [(x - 8, y), (x + 8, y)], col, 4)
    if sign > 0:
        polyline(ctx, [(x, y - 8), (x, y + 8)], col, 4)


def d_echem(ctx):
    """Film on a working electrode under bias. Molecules in the top rows are oxidized
    (new oxidation state, crimson), electrons leave to the electrode, and electrolyte
    anions intercalate to compensate the charge."""
    xL, xR = 30, 860
    yE, yF, yS = 90, 220, 470
    src(ctx, ICE, 1.0); ctx.rectangle(xL, yE, xR - xL, yF - yE); ctx.fill()
    src(ctx, SLATE, 0.85); ctx.rectangle(xL, yS, xR - xL + 120, 46); ctx.fill()
    rows = 4
    dy = (yS - yF) / rows
    for i in range(rows):
        y = yF + dy * (i + 0.5)
        col = CRIMSON if i == 0 else (DEEP if i == 1 else GRAY)
        for j in range(11):
            edge_on(ctx, xL + 40 + j * 74 + (18 if i % 2 else 0), y, col)
    polyline(ctx, [(xL, yF), (xR, yF)], SLATE, 3)
    for k, (x, y) in enumerate([(70, 130), (160, 190), (250, 125), (340, 185), (430, 130), (520, 190),
                                (610, 125), (700, 185), (790, 130)]):
        ion(ctx, x, y, 1 if k in (1, 4, 7) else -1)
    for x, y in ((112, yF + dy * 0.5 + 4), (262, yF + dy * 0.5 - 6), (412, yF + dy * 1.0), (562, yF + dy * 0.5 + 2),
                 (337, yF + dy * 1.5 - 4), (712, yF + dy * 0.5 - 4), (787, yF + dy * 1.0 + 2), (637, yF + dy * 1.5 - 2)):
        ion(ctx, x, y, -1, r=15)
    # electrons leave the oxidized molecules to the electrode
    xe = 925
    polyline(ctx, [(xR - 10, yF + dy * 0.6), (xe, yF + dy * 0.6)], BLUE, 4, dash=[8, 7])
    arrow(ctx, xe, yF + dy * 0.6, xe, yS - 4, BLUE, width=4.5, head=20)
    electron(ctx, xe, yF + dy * 1.5, r=15)
    electron(ctx, xe, yF + dy * 2.4, r=15)
    text(ctx, xe + 28, yF + dy * 1.1, "e^{−}", LAB, BLUE)


# ------------------------------------------------------------------ 2b chemical reaction

def ring(ctx, cx, cy, R, start, cb):
    v = hexagon(cx, cy, R, start=start)
    for k in range(6):
        bond(ctx, v[k], v[(k + 1) % 6], cb, w=5)
    for i, j in ((0, 1), (2, 3), (4, 5)):
        inner_double(ctx, v[i], v[j], (cx, cy), cb, w=4.5, off=10)


def styryl_pair(ctx, cx, cy, y_pair, product, cb):
    """Two stilbene units stacked; product = cyclobutane from [2+2] addition."""
    R, half, link = 40, 38, 30
    for y in y_pair:
        c1, c2 = (cx - half, cy + y), (cx + half, cy + y)
        if product:
            bond(ctx, c1, c2, cb)
        else:
            polyline(ctx, [(c1[0], c1[1] - 7), (c2[0], c2[1] - 7)], cb, 5)
            polyline(ctx, [(c1[0] + 8, c1[1] + 7), (c2[0] - 8, c2[1] + 7)], cb, 5)
        bond(ctx, c1, (c1[0] - link, c1[1]), cb)
        bond(ctx, c2, (c2[0] + link, c2[1]), cb)
        ring(ctx, c1[0] - link - R, c1[1], R, 0, cb)
        ring(ctx, c2[0] + link + R, c2[1], R, 0, cb)
    if product:
        src(ctx, CRIMSON, 0.16)
        ctx.rectangle(cx - half, cy + y_pair[0], 2 * half, y_pair[1] - y_pair[0]); ctx.fill()
        for x in (cx - half, cx + half):
            bond(ctx, (x, cy + y_pair[0]), (x, cy + y_pair[1]), cb)


def d_reaction(ctx):
    styryl_pair(ctx, 180, 320, (-62, 62), False, GRAYD)
    arrow(ctx, 385, 320, 495, 320, SLATE, width=4.5, head=20)
    text(ctx, 440, 292, "$hν$", LAB, RUST, anchor="c")
    styryl_pair(ctx, 700, 320, (-48, 48), True, DEEP)


# ------------------------------------------------------------------ 3a hybridization

def d_hybrid(ctx):
    yL, yH, yF = 170, 400, 270          # LUMO, HOMO, Fermi level
    # labels
    text(ctx, 160, yL + 18, "LUMO", LAB * 0.9, INK, anchor="r")
    text(ctx, 160, yH + 18, "HOMO", LAB * 0.9, INK, anchor="r")
    # free molecule column
    a0, a1 = 180, 290
    level(ctx, a0, a1, yL, GRAYD)
    level(ctx, a0, a1, yH, GRAYD)
    electron(ctx, (a0 + a1) / 2 - 22, yH - 20, r=15); electron(ctx, (a0 + a1) / 2 + 22, yH - 20, r=15)
    # metal block
    m0, m1 = 580, 695
    g = cairo.LinearGradient(0, yF, 0, 520)
    c1, c2 = hexrgb(SLATE, 0.55), hexrgb(SLATE, 0.95)
    g.add_color_stop_rgba(0, *c1); g.add_color_stop_rgba(1, *c2)
    ctx.set_source(g); ctx.rectangle(m0, yF, m1 - m0, 520 - yF); ctx.fill()
    src(ctx, SLATE); ctx.set_line_width(3); ctx.rectangle(m0, 110, m1 - m0, 410); ctx.stroke()
    # Fermi level across adsorbed + metal
    polyline(ctx, [(355, yF), (m1, yF)], SLATE, 3.5, dash=[10, 8])
    text(ctx, m1 + 12, yF + 18, "$E$_{F}", LAB, SLATE)
    # adsorbed column: broadened levels as horizontal DOS lobes
    b0 = 360
    shiftL = 55                                   # LUMO pulled toward E_F
    yl = yL + shiftL
    def lobe(yc, gam, amp, fill_below_y=None, color=CRIMSON):
        pts = []
        for i in range(161):
            y = yc - 4 * gam + 8 * gam * i / 160
            d = amp * gam ** 2 / ((y - yc) ** 2 + gam ** 2)
            pts.append((b0 + d, y))
        if fill_below_y is not None:
            sub = [p for p in pts if p[1] >= fill_below_y]
            src(ctx, BLUE, 0.45)
            ctx.move_to(b0, sub[0][1])
            for p in sub:
                ctx.line_to(*p)
            ctx.line_to(b0, sub[-1][1]); ctx.close_path(); ctx.fill()
        src(ctx, color, 0.14)
        ctx.move_to(b0, pts[0][1])
        for p in pts:
            ctx.line_to(*p)
        ctx.line_to(b0, pts[-1][1]); ctx.close_path(); ctx.fill()
        polyline(ctx, pts, color, 5)
    lobe(yl, 26, 165, fill_below_y=yF)
    lobe(yH + 10, 14, 150)
    polyline(ctx, [(b0, 110), (b0, 520)], SLATE, 3)
    # tie lines
    polyline(ctx, [(a1 + 8, yL), (b0 - 6, yl)], GRAY, 3, dash=[7, 7])
    polyline(ctx, [(a1 + 8, yH), (b0 - 6, yH + 10)], GRAY, 3, dash=[7, 7])
    text(ctx, (a0 + a1) / 2, 575, "free", LAB * 0.85, SLATE, anchor="c")
    text(ctx, b0 + 90, 575, "adsorbed", LAB * 0.85, SLATE, anchor="c")
    text(ctx, (m0 + m1) / 2, 575, "metal", LAB * 0.85, SLATE, anchor="c")


# ------------------------------------------------------------------ 3b gate bias

def d_gate(ctx):
    # device stack
    x0, x1 = 110, 320
    yC, yD, yG, yB = 230, 330, 450, 520
    src(ctx, CRIMSON, 0.16); ctx.rectangle(x0, yC, x1 - x0, yD - yC); ctx.fill()
    src(ctx, TAUPE, 0.55); ctx.rectangle(x0, yD, x1 - x0, yG - yD); ctx.fill()
    src(ctx, SLATE, 0.85); ctx.rectangle(x0, yG, x1 - x0, yB - yG); ctx.fill()
    for xa in (x0, x1 - 70):
        src(ctx, SLATE, 0.85); ctx.rectangle(xa, yC - 46, 70, 46); ctx.fill()
    text(ctx, x0 + 35, yC - 10, "S", LAB * 0.85, IVORY, anchor="c")
    text(ctx, x1 - 35, yC - 10, "D", LAB * 0.85, IVORY, anchor="c")
    text(ctx, (x0 + x1) / 2, yB - 18, "gate", LAB * 0.85, IVORY, anchor="c")
    for k in range(6):
        electron(ctx, x0 + 22 + k * 34, yD - 16, r=12)
    text(ctx, x0 - 14, (yG + yB) / 2 + 18, "+$V$_{G}", LAB, BLUE, anchor="r")
    # level diagram, three columns
    yL, yH = 210, 420
    text(ctx, 482, yL + 18, "LUMO", LAB * 0.9, INK, anchor="r")
    text(ctx, 482, yH + 18, "HOMO", LAB * 0.9, INK, anchor="r")
    cols = [(500, GRAYD, "0", SLATE), (610, BLUE, "+$V$_{G}", BLUE), (720, RUST, "−$V$_{G}", RUST)]
    for xc, col, lab, lc in cols:
        level(ctx, xc, xc + 90, yL, col)
        level(ctx, xc, xc + 90, yH, col)
        text(ctx, xc + 45, 150, lab, LAB * 0.9, lc, anchor="c")
    for xc, _, _, _ in cols[:2]:
        electron(ctx, xc + 25, yH - 20, r=14); electron(ctx, xc + 65, yH - 20, r=14)
    electron(ctx, 610 + 45, yL - 20, r=14)
    electron(ctx, 720 + 25, yH - 20, r=14); clay_hole(ctx, 720 + 65, yH - 20, r=14)


# ------------------------------------------------------------------ 2b photoacid / CAR deprotection

def zig(p, ang_deg, b):
    a = math.radians(ang_deg)
    return (p[0] + b * math.cos(a), p[1] - b * math.sin(a))


def backbone(ctx, top, cb, b):
    """Polymer backbone stub under a pendant ring: CH joined to a short zigzag with wavy ends."""
    ch = (top[0], top[1] + b)
    bond(ctx, top, ch, cb)
    l1 = zig(ch, 210, b); r1 = zig(ch, -30, b)
    bond(ctx, ch, l1, cb); bond(ctx, ch, r1, cb)
    for p, d in ((l1, -1), (r1, 1)):
        pts = [(p[0] + d * 6 * k, p[1] + 9 * math.sin(k * 1.4)) for k in range(7)]
        polyline(ctx, pts, cb, 4.5)


def pendant_ring(ctx, cx, cy, R, cb):
    v = hexagon(cx, cy, R, start=90)
    for k in range(6):
        bond(ctx, v[k], v[(k + 1) % 6], cb)
    for i, j in ((0, 1), (2, 3), (4, 5)):
        inner_double(ctx, v[i], v[j], (cx, cy), cb)
    return v[0], v[3]          # top, bottom vertices


def d_pag(ctx):
    b, R, rO = 54, 56, LAB * 0.45
    # reactant, tBOC-protected hydroxystyrene unit
    top, bot = pendant_ring(ctx, 120, 360, R, GRAYD)
    backbone(ctx, bot, GRAYD, b)
    O1 = zig(top, 90, b)
    bond(ctx, top, O1, GRAYD, shrink=(0, rO))
    C = zig(O1, 30, b)
    bond(ctx, O1, C, GRAYD, shrink=(rO, 0))
    O2 = zig(C, 90, b)
    outer_double(ctx, C, (O2[0], O2[1] + rO), GRAYD)
    O3 = zig(C, -30, b)
    bond(ctx, C, O3, GRAYD, shrink=(0, rO))
    Cq = zig(O3, 30, b)
    bond(ctx, O3, Cq, GRAYD, shrink=(rO, 0))
    for ang in (90, -30, 30):
        bond(ctx, Cq, zig(Cq, ang, b * 0.9), GRAYD)
    for p, s in ((O1, "O"), (O2, "O"), (O3, "O")):
        atom_label(ctx, *p, s, GRAYD)
    # photoacid generation feeding the catalytic step
    ax0, ax1, ay = 420, 560, 360
    arrow(ctx, ax0, ay, ax1, ay, SLATE, width=4.5, head=20)
    xm = (ax0 + ax1) / 2
    text(ctx, xm, 130, "PAG", LAB * 0.9, SLATE, anchor="c")
    arrow(ctx, xm, 150, xm, 270, RUST, width=4, head=18)
    text(ctx, xm + 16, 225, "$hν$", LAB * 0.9, RUST)
    text(ctx, xm, 330, "H^{+}", LAB, RUST, anchor="c")
    # products, hydroxystyrene unit plus CO2 and isobutylene
    top, bot = pendant_ring(ctx, 690, 360, R, DEEP)
    backbone(ctx, bot, DEEP, b)
    Op = zig(top, 90, b)
    bond(ctx, top, Op, DEEP, shrink=(0, rO))
    Hh = zig(Op, 30, b * 1.45)
    bond(ctx, Op, Hh, DEEP, shrink=(rO, rO))
    glow(ctx, Op[0], Op[1], 46, CRIMSON, 0.35)
    atom_label(ctx, *Op, "O", CRIMSON)
    atom_label(ctx, *Hh, "H", RUST)
    text(ctx, 850, 300, "+ CO_{2}", LAB * 0.9, SLATE)
    # isobutylene
    c0 = (900, 420)
    text(ctx, 850, 440, "+", LAB * 0.9, SLATE)
    c1 = zig(c0, 0, b)
    outer_double(ctx, c0, c1, SLATE, off=7)
    bond(ctx, c1, zig(c1, 50, b * 0.9), SLATE)
    bond(ctx, c1, zig(c1, -50, b * 0.9), SLATE)


# ------------------------------------------------------------------ 3a hybridization (molecular picture)

def lobe(ctx, x, y, rx, ry, color, a_fill, a_line=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(rx, ry)
    ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()
    src(ctx, color, a_fill); ctx.fill_preserve()
    src(ctx, color, a_line); ctx.set_line_width(3); ctx.stroke()


def chain(ctx, cx, cy, n, d, cb):
    xs = [cx + (k - (n - 1) / 2) * d for k in range(n)]
    polyline(ctx, [(xs[0], cy), (xs[-1], cy)], cb, 6)
    for x in xs:
        disc(ctx, x, cy, 9, IVORY)
        src(ctx, cb); ctx.set_line_width(3.5); ctx.arc(x, cy, 9, 0, 2 * math.pi); ctx.stroke()
    return xs


def metal(ctx, x0, x1, y, r=24):
    for row, yy in enumerate((y, y + 2 * r * 0.88)):
        x = x0 + (r if row else 0)
        while x <= x1:
            g = cairo.RadialGradient(x - r * 0.35, yy - r * 0.4, 0, x, yy, r * 1.05)
            for off, col in ((0, "#E7E9EA"), (0.55, "#A9B1B5"), (1, SLATE)):
                c = hexrgb(col); g.add_color_stop_rgba(off, c[0], c[1], c[2], 1)
            ctx.set_source(g); ctx.arc(x, yy, r, 0, 2 * math.pi); ctx.fill()
            x += 2 * r


def d_hybrid2(ctx):
    n, d = 6, 50
    # free molecule, isolated p_z lobes
    yA = 300
    xs = [200 + (k - 2.5) * d for k in range(n)]
    for x in xs:
        lobe(ctx, x, yA - 44, 15, 36, GRAY, 0.30, 0.9)
        lobe(ctx, x, yA + 44, 15, 36, GRAY, 0.15, 0.9)
    chain(ctx, 200, yA, n, d, GRAYD)
    arrow(ctx, 390, yA + 20, 480, yA + 20, SLATE, width=4.5, head=20)
    # adsorbed molecule, lower lobes merge into the metal states
    cx, yB, ym = 720, 230, 420
    g = cairo.LinearGradient(0, yB, 0, ym)
    c1, c2 = hexrgb(CRIMSON), hexrgb(SKY)
    g.add_color_stop_rgba(0, c1[0], c1[1], c1[2], 0.05)
    g.add_color_stop_rgba(0.55, c1[0], c1[1], c1[2], 0.22)
    g.add_color_stop_rgba(1, c2[0], c2[1], c2[2], 0.35)
    cloud(ctx, cx, yB + 80, 230, 120, CRIMSON, 0.30)
    cloud(ctx, cx, ym - 10, 240, 70, SKY, 0.40)
    xs = [cx + (k - 2.5) * d for k in range(n)]
    for x in xs:
        lobe(ctx, x, yB - 40, 14, 32, CRIMSON, 0.28)
        lobe(ctx, x, yB + 60, 19, 56, CRIMSON, 0.16)
    chain(ctx, cx, yB, n, d, DEEP)
    metal(ctx, cx - 200, cx + 200, ym + 24)


# ------------------------------------------------------------------ 3b charging under gate bias

def anthracene(ctx, cx, cy, R, cb):
    dx = R * math.sqrt(3)
    for k in (-1, 0, 1):
        v = hexagon(cx + k * dx, cy, R, start=90)
        for i in range(6):
            bond(ctx, v[i], v[(i + 1) % 6], cb, w=5)
        src(ctx, cb); ctx.set_line_width(3.5)
        ctx.arc(cx + k * dx, cy, R * 0.52, 0, 2 * math.pi); ctx.stroke()


def cloud(ctx, cx, cy, rx, ry, color, a):
    ctx.save(); ctx.translate(cx, cy); ctx.scale(rx, ry)
    g = cairo.RadialGradient(0, 0, 0, 0, 0, 1)
    c = hexrgb(color)
    g.add_color_stop_rgba(0, c[0], c[1], c[2], a)
    g.add_color_stop_rgba(0.6, c[0], c[1], c[2], a * 0.6)
    g.add_color_stop_rgba(1, c[0], c[1], c[2], 0)
    ctx.set_source(g); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.fill(); ctx.restore()


def badge(ctx, x, y, sign, col, r=22):
    disc(ctx, x, y, r, IVORY)
    src(ctx, col); ctx.set_line_width(4); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.stroke()
    polyline(ctx, [(x - 10, y), (x + 10, y)], col, 4.5)
    if sign > 0:
        polyline(ctx, [(x, y - 10), (x, y + 10)], col, 4.5)


def levels(ctx, cx, yl, yh, col, nl, nh, hole=False):
    level(ctx, cx - 50, cx + 50, yl, col, w=6)
    level(ctx, cx - 50, cx + 50, yh, col, w=6)
    if nl:
        electron(ctx, cx, yl - 17, r=13)
    xs = [cx - 20, cx + 20]
    for k in range(2):
        if k < nh:
            electron(ctx, xs[k], yh - 17, r=13)
        elif hole:
            clay_hole(ctx, xs[k], yh - 17, r=13)


def d_charge(ctx):
    R, cy = 40, 230
    yl, yh = 360, 430
    spec = [(170, BLUE, -1, 1, 2, False), (500, GRAYD, 0, 0, 2, False), (830, RUST, 1, 0, 1, True)]
    for cx, col, sgn, nl, nh, hl in spec:
        if sgn:
            cloud(ctx, cx, cy, 150, 85, SKY if sgn < 0 else CLAY, 0.45)
        anthracene(ctx, cx, cy, R, DEEP if sgn else GRAYD)
        if sgn:
            badge(ctx, cx + (112 if sgn > 0 else -112), cy - 62, sgn, col)
        levels(ctx, cx, yl, yh, col, nl, nh, hl)
    text(ctx, 335, yl + 18, "LUMO", LAB * 0.8, INK, anchor="c")
    text(ctx, 335, yh + 18, "HOMO", LAB * 0.8, INK, anchor="c")
    text(ctx, 665, yl + 18, "LUMO", LAB * 0.8, INK, anchor="c")
    text(ctx, 665, yh + 18, "HOMO", LAB * 0.8, INK, anchor="c")
    arrow(ctx, 385, cy, 300, cy, BLUE, width=4.5, head=20)
    text(ctx, 342, cy - 22, "+$V$_{G}", LAB * 0.9, BLUE, anchor="c")
    arrow(ctx, 615, cy, 700, cy, RUST, width=4.5, head=20)
    text(ctx, 658, cy - 22, "−$V$_{G}", LAB * 0.9, RUST, anchor="c")


def d_echem2(ctx):
    """Ordered film on a working electrode. Top row oxidized (crimson), charge-balancing
    anions from the electrolyte sit between the oxidized molecules, electrons exit to the electrode."""
    xL, xR = 30, 800
    yE, yF, yS = 80, 210, 430
    src(ctx, ICE, 1.0); ctx.rectangle(xL, yE, xR - xL, yF - yE); ctx.fill()
    src(ctx, SLATE, 0.85); ctx.rectangle(xL, yS, xR - xL + 140, 44); ctx.fill()
    polyline(ctx, [(xL, yF), (xR, yF)], SLATE, 3)
    rows, n, pitch = 3, 9, 84
    dy = (yS - yF) / rows
    xs = [xL + 50 + j * pitch for j in range(n)]
    for i in range(rows):
        y = yF + dy * (i + 0.5)
        for x in xs:
            edge_on(ctx, x, y, CRIMSON if i == 0 else GRAY, tilt=0, L=50, w=11)
    # intercalated anions between oxidized molecules
    y0 = yF + dy * 0.5
    for j in range(0, n - 1, 2):
        ion(ctx, (xs[j] + xs[j + 1]) / 2, y0, -1, r=15)
    # tidy electrolyte row
    for k, x in enumerate(range(90, 800, 120)):
        ion(ctx, x, 145, 1 if k % 2 else -1)
    # electrons to the electrode
    xe = 890
    polyline(ctx, [(xs[-1] + 34, y0), (xe, y0)], BLUE, 4, dash=[8, 7])
    arrow(ctx, xe, y0, xe, yS - 4, BLUE, width=4.5, head=20)
    electron(ctx, xe, y0 + 70, r=15)
    electron(ctx, xe, y0 + 140, r=15)
    text(ctx, xe + 26, y0 + 40, "e^{−}", LAB, BLUE)


def d_echem3(ctx):
    """Film on a working electrode. Ordered near the electrode, swollen and disordered where
    electrolyte penetrates; oxidized molecules (crimson) mixed with charge-balancing anions."""
    import random
    rnd = random.Random(11)
    xL, xR = 30, 800
    yE, yS = 70, 440
    row_y = [205, 268, 330, 388]           # top rows spread apart (swelling)
    dis = [1.0, 0.55, 0.15, 0.0]           # disorder per row
    # electrolyte with a ragged front reaching into the top rows
    src(ctx, ICE, 1.0)
    ctx.move_to(xL, yE); ctx.line_to(xR, yE)
    xs_b = [xR - k * 20 for k in range(0, 39)] + [xL]
    for x in xs_b:
        ctx.line_to(x, 250 + 22 * math.sin(x / 47.0) + 10 * math.sin(x / 13.0))
    ctx.close_path(); ctx.fill()
    src(ctx, SLATE, 0.85); ctx.rectangle(xL, yS, xR - xL + 140, 44); ctx.fill()
    pitch = 84
    for i, (y, d) in enumerate(zip(row_y, dis)):
        col = CRIMSON if i == 0 else (DEEP if i == 1 else GRAY)
        for j in range(9):
            x = xL + 50 + j * pitch + rnd.uniform(-18, 18) * d
            yy = y + rnd.uniform(-16, 16) * d
            tilt = rnd.uniform(-55, 55) * d
            edge_on(ctx, x, yy, col, tilt=tilt, L=50, w=11)
    # anions intercalated among the oxidized molecules
    for x, y in ((92, 180), (250, 232), (345, 196), (500, 238), (590, 186), (735, 228), (180, 296), (420, 290)):
        ion(ctx, x, y, -1, r=15)
    # electrolyte ions, solvated and random
    pts = [(70, 110), (150, 150), (235, 98), (300, 150), (390, 112), (470, 155), (545, 100),
           (625, 148), (705, 108), (770, 152)]
    for k, (x, y) in enumerate(pts):
        ion(ctx, x + rnd.uniform(-10, 10), y + rnd.uniform(-8, 8), 1 if k in (1, 4, 7) else -1)
    # electrons to the electrode
    xe, y0 = 890, 205
    polyline(ctx, [(xR - 20, y0), (xe, y0)], BLUE, 4, dash=[8, 7])
    arrow(ctx, xe, y0, xe, yS - 4, BLUE, width=4.5, head=20)
    electron(ctx, xe, y0 + 75, r=15)
    electron(ctx, xe, y0 + 150, r=15)
    text(ctx, xe + 26, y0 + 40, "e^{−}", LAB, BLUE)


def grad_lobe(ctx, x, y, rx, ry, c_top, c_bot, a_top, a_bot, line):
    ctx.save(); ctx.translate(x, y); ctx.scale(rx, ry)
    ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()
    g = cairo.LinearGradient(0, y - ry, 0, y + ry)
    t, b = hexrgb(c_top), hexrgb(c_bot)
    g.add_color_stop_rgba(0, t[0], t[1], t[2], a_top)
    g.add_color_stop_rgba(1, b[0], b[1], b[2], a_bot)
    ctx.set_source(g); ctx.fill_preserve()
    g2 = cairo.LinearGradient(0, y - ry, 0, y + ry)
    lt = hexrgb(line); lb = hexrgb(BLUE)
    g2.add_color_stop_rgba(0, lt[0], lt[1], lt[2], 1)
    g2.add_color_stop_rgba(0.55, lt[0], lt[1], lt[2], 1)
    g2.add_color_stop_rgba(1, lb[0], lb[1], lb[2], 0.0)
    ctx.set_source(g2); ctx.set_line_width(3); ctx.stroke()


def d_hybrid3(ctx):
    n, d = 6, 50
    yA = 280
    for x in [200 + (k - 2.5) * d for k in range(n)]:
        lobe(ctx, x, yA - 44, 15, 36, GRAY, 0.30, 0.9)
        lobe(ctx, x, yA + 44, 15, 36, GRAY, 0.15, 0.9)
    chain(ctx, 200, yA, n, d, GRAYD)
    arrow(ctx, 385, yA, 475, yA, SLATE, width=4.5, head=20)
    cx, yB, r = 715, 262, 24
    ytop = 392                                  # metal surface (top of first atom row)
    # metal electron density
    for k in range(9):
        glow(ctx, cx - 4 * 2 * r + k * 2 * r, ytop + r, 46, SKY, 0.55)
    xs = [cx + (k - 2.5) * d for k in range(n)]
    for x in xs:
        lobe(ctx, x, yB - 40, 14, 32, CRIMSON, 0.28)
        y0, y1 = yB + 8, ytop + 18
        grad_lobe(ctx, x, (y0 + y1) / 2, 19, (y1 - y0) / 2, CRIMSON, SKY, 0.30, 0.55, CRIMSON)
    metal(ctx, cx - 8 * r, cx + 8 * r, ytop + r)
    chain(ctx, cx, yB, n, d, DEEP)
    # charge transfer from metal into the molecule
    xe = cx + 3.4 * d + 30
    arrow(ctx, xe, ytop - 6, xe, yB + 14, BLUE, width=4, head=18)
    electron(ctx, xe, (ytop + yB) / 2 + 10, r=14)
    text(ctx, xe + 22, (ytop + yB) / 2 + 26, "e^{−}", LAB * 0.9, BLUE)


def battery(ctx, cx, cy, L=200, Hb=90):
    x0, y0 = cx - L / 2, cy - Hb / 2
    src(ctx, IVORY); rounded_rect(ctx, x0, y0, L, Hb, 16); ctx.fill()
    src(ctx, TAUPE, 0.75); rounded_rect(ctx, x0 + L * 0.62, y0, L * 0.38, Hb, 16); ctx.fill()
    src(ctx, TAUPE, 0.75); ctx.rectangle(x0 + L * 0.62, y0, 20, Hb); ctx.fill()
    src(ctx, SLATE); ctx.set_line_width(4); rounded_rect(ctx, x0, y0, L, Hb, 16); ctx.stroke()
    src(ctx, SLATE); rounded_rect(ctx, x0 + L - 2, cy - 20, 18, 40, 5); ctx.fill()
    text(ctx, x0 + 40, cy + 20, "−", LAB * 1.1, SLATE, anchor="c")
    text(ctx, x0 + L - 40, cy + 20, "+", LAB * 1.1, SLATE, anchor="c")
    return x0, x0 + L + 16


def d_battery(ctx):
    R, cy = 40, 230
    yl, yh = 370, 440
    xa, xc = 165, 845                          # anion (left), cation (right)
    for cx, col, sgn in ((xa, BLUE, -1), (xc, RUST, 1)):
        cloud(ctx, cx, cy, 150, 85, SKY if sgn < 0 else CLAY, 0.45)
        anthracene(ctx, cx, cy, R, DEEP)
        badge(ctx, cx + (-112 if sgn < 0 else 112), cy - 62, sgn, col)
    levels(ctx, xa, yl, yh, BLUE, 1, 2)
    levels(ctx, xc, yl, yh, RUST, 0, 1, hole=True)
    text(ctx, 505, yl + 18, "LUMO", LAB * 0.8, INK, anchor="c")
    text(ctx, 505, yh + 18, "HOMO", LAB * 0.8, INK, anchor="c")
    bl, br = battery(ctx, 497, cy)
    wl0, wr0 = xa + 112, xc - 112                # molecule edges
    polyline(ctx, [(wl0, cy), (bl, cy)], SLATE, 5)
    polyline(ctx, [(br, cy), (wr0, cy)], SLATE, 5)
    # electrons leave the negative terminal into the left molecule, and leave the right molecule
    for x0, x1 in ((bl - 18, wl0 + 26), (wr0 - 6, br + 30)):
        electron(ctx, (x0 + x1) / 2 + 8, cy, r=13)
        arrow(ctx, (x0 + x1) / 2 - 12, cy - 30, (x0 + x1) / 2 - 52, cy - 30, BLUE, width=3.5, head=14)


# ------------------------------------------------------------------ render

DISPLAYS = [
    ("1a-torsion", d_torsion), ("1b-tautomerization", d_tautomer),
    ("2a-electrochemistry", d_echem3), ("2a-electrochemistry-ordered", d_echem2), ("2b-reaction", d_pag),
    ("3a-hybridization", d_hybrid3), ("3b-gate-bias", d_battery),
]


def setup(ctx):
    fo = cairo.FontOptions()
    fo.set_antialias(cairo.ANTIALIAS_GRAY)
    fo.set_hint_style(cairo.HINT_STYLE_NONE)
    fo.set_hint_metrics(cairo.HINT_METRICS_OFF)
    ctx.set_font_options(fo)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)


def extents(fn):
    rec = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, None)
    ctx = cairo.Context(rec); setup(ctx); fn(ctx)
    return rec.ink_extents()


def render(name, fn, scale):
    x, y, w, h = extents(fn)
    tx = (W - w * scale) / 2 - x * scale
    ty = (H - h * scale) / 2 - y * scale
    os.makedirs(OUT, exist_ok=True)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf); setup(ctx); ctx.translate(tx, ty); ctx.scale(scale, scale)
    fn(ctx)
    surf.write_to_png(f"{OUT}/{name}.png")
    k = 72 / 400
    svg = cairo.SVGSurface(f"{OUT}/{name}.svg", W * k, H * k)
    ctx = cairo.Context(svg); setup(ctx); ctx.scale(k, k); ctx.translate(tx, ty); ctx.scale(scale, scale)
    fn(ctx)
    svg.finish()


if __name__ == "__main__":
    M = 24
    fits = {}
    for name, fn in DISPLAYS:
        x, y, w, h = extents(fn)
        fits[name] = min((W - 2 * M) / w, (H - 2 * M) / h)
        print(name, round(w), round(h), round(fits[name], 3))
    common = min(fits.values())
    for name, fn in DISPLAYS:
        render(name, fn, common)
    # contact sheet on card colour for checking
    from PIL import Image
    sheet = Image.new("RGB", (W * 3 + 80, H * 2 + 60), CARD)
    for i, (name, _) in enumerate(DISPLAYS):
        im = Image.open(f"{OUT}/{name}.png")
        col, row = i // 2, i % 2
        sheet.paste(im, (20 + col * (W + 20), 20 + row * (H + 20)), im)
    sheet.save(f"{OUT}/contact.png")
