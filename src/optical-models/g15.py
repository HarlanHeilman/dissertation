"""GIF 15 (merged DFT slide). The same five symmetrized StoBe transition-potential transitions as the slide 7 ZnPc GIF
(g12: C3 MO 119, C2 MO 124, C3 MO 133, C1 MO 205, C4 MO 314; D4h-averaged geometry, each state copied to its 8
equivalent carbons, final-orbital isosurfaces and dipoles from znpc_orb.py). Left, the ground-state molecule with the
core-hole carbons lit (no photon, 2.2 s per state). Right, the final state and its dipoles. Bottom, every raw DFT transition from 283.5
to 300 eV coloured by carbon site, with the current transition (its raw stick) highlighted."""
import math
import numpy as np
import pandas as pd
from style import *
import g12
from g12 import ST, LAYERS, SX, SY, DEP, V, HMU, draw_skeleton

SIZE = (1500, 680)
PER = 2.2
NS = len(ST)
DUR = NS * PER
SCL = 0.92
OFF = {"L": (22, 18), "R": (782, 18)}
SHIFT = 0.45   # static DFT energy correction (dissertation Fig. 2.6 seed shift)
STK = pd.read_csv("/home/claude/znpc_data/data/csv/znpc_sticks_tensor.csv")
STK = STK.assign(en=STK.en + SHIFT)
STK = STK[STK.en.between(283.5, 300.0)]
SITE_COL = {1: "#2E6F82", 2: "#9DBBC6", 3: "#E2B4AE", 4: "#C2492D"}
for s in ST:
    r = STK[(STK.atomid == int(s["site"][1])) & (STK.mo == s["mo"])].iloc[0]
    s["raw_en"], s["raw_os"] = float(r.en), float(r.os)   # r.en already includes SHIFT
AX = Axes(120, 432, 1440, 622, (283.5, 300.0), (0, 1.25))
# DFT (all sticks, their own widths, static shift SHIFT) against the measured isotropic beta (exp_bets.csv),
# each normalized to its own pi* maximum between 284 and 286 eV
_EG = np.linspace(283.5, 300.0, 1400)
_all = pd.read_csv("/home/claude/znpc_data/data/csv/znpc_sticks_tensor.csv")
DFT = np.zeros_like(_EG)
for en, os_, w in zip(_all.en, _all.os, _all.wid):
    DFT += os_ / w * np.exp(-0.5 * ((_EG - en - SHIFT) / w) ** 2)
_b = pd.read_csv("/home/claude/znpc_data/data/optical/exp_bets.csv")
EXP = np.interp(_EG, _b.Energy.values, _b["βiso"].values) - float(np.interp(283.0, _b.Energy.values, _b["βiso"].values))
_pi = (_EG > 284) & (_EG < 286)
DFT /= DFT[_pi].max(); EXP /= EXP[_pi].max()
SQMAX = float(np.sqrt(STK.os.max()))


def panel(ctx, side):
    ctx.save()
    ctx.translate(*OFF[side])
    ctx.scale(SCL, SCL)


def gx(side, x):
    return OFF[side][0] + SCL * x


def gy(side, y):
    return OFF[side][1] + SCL * y


def frame(t):
    surf, ctx = new_frame(*SIZE)
    k = int(t // PER) % NS
    u = t - k * PER
    s = ST[k]
    out = 1 - ramp(u, PER - 0.25, PER - 0.02)
    fade = ramp(u, 0.0, 0.2) * out
    lit = ramp(u, 0.05, 0.3) * out
    la = ramp(u, 0.4, 0.75) * out
    grow = ramp(u, 0.55, 0.9) * out

    # left, ground state, the 8 equivalent core sites lit (no incoming photon)
    panel(ctx, "L")
    draw_skeleton(ctx)
    for j, m in s["sites"]:
        glow(ctx, SX[j], SY[j], 30, CLAY, 0.8 * lit)
        ctx.new_path(); src(ctx, CLAY, 0.25 + 0.75 * lit); ctx.arc(SX[j], SY[j], 4.8 + 2.0 * lit, 0, 2 * math.pi); ctx.fill()
    ctx.restore()
    text(ctx, gx("L", g12.MCX), 392, f"{s['site']} 1s core hole, 8 equivalent carbons", 30, RUST, fade, "c")

    # arrow between the panels
    x0, x1, ya = 585, 770, gy("L", g12.MCY)
    src(ctx, SLATE, 0.3); ctx.set_line_width(5); ctx.move_to(x0, ya); ctx.line_to(x1 - 12, ya); ctx.stroke()
    arrow_head(ctx, x1, ya, 0.0, 22, SLATE, 0.3)
    ga = ramp(u, 0.2, 0.5) * out
    if ga > 0.01:
        src(ctx, CLAY, ga); ctx.set_line_width(5)
        ctx.move_to(x0, ya); ctx.line_to(x0 + (x1 - 12 - x0) * clamp((u - 0.2) / 0.3), ya); ctx.stroke()
        if u > 0.45:
            arrow_head(ctx, x1, ya, 0.0, 22, CLAY, ga)
    text(ctx, (x0 + x1) / 2, ya - 22, "$μ_{0i}$", 36, INK, 1.0, "c")

    # right, final state (same layers as slide 7), dipoles at the 8 sites
    panel(ctx, "R")
    for front in (False, True):
        if la > 0.005:
            ctx.set_source_surface(LAYERS[k][(front, "fill")], 0, 0)
            ctx.paint_with_alpha((0.85 if front else 1.0) * la)
        if not front:
            draw_skeleton(ctx)
    if grow > 0.02:
        for j, m in sorted(s["sites"], key=lambda q: DEP[q[0]]):
            dx, dy = V(m)
            ex, ey = SX[j], SY[j]
            arrow(ctx, ex - HMU * grow * dx, ey - HMU * grow * dy, ex + HMU * grow * dx, ey + HMU * grow * dy, NAVY, 3.0, 13, grow, both=True)
    ctx.restore()
    kind = "$π$^{*}" if s["bound"] else "$σ$^{*}"
    th = s["thetas"][0]
    text(ctx, gx("R", g12.MCX), 392, f"MO {s['mo']},  {s['raw_en']:.1f} eV,  " + kind + f",  $θ$ = {th:.0f}°", 30, INK, la, "c")

    # bottom, every raw stick, the current one highlighted
    AX.frame(ctx, xticks=(284, 286, 288, 290, 292, 294, 296, 298, 300), xlabel=None, size=24)
    for en, os_, site in zip(STK.en, STK.os, STK.atomid):
        x = AX.X(en); y = AX.Y(0.45 * math.sqrt(os_) / SQMAX)
        src(ctx, SITE_COL[int(site)], 0.6); ctx.set_line_width(1.6)
        ctx.move_to(x, AX.y1); ctx.line_to(x, y); ctx.stroke()
    polyline(ctx, AX.pts(_EG, EXP), INK, 3.2, 0.95)
    polyline(ctx, AX.pts(_EG, DFT), RUST, 3.0, 0.95, dash=[10, 6])
    hl = ramp(u, 0.4, 0.7) * out
    if hl > 0.01:
        xs, ys = AX.X(s["raw_en"]), min(AX.Y(0.45 * math.sqrt(s["raw_os"]) / SQMAX), AX.y1 - 10)
        src(ctx, CLAY, hl); ctx.set_line_width(5); ctx.move_to(xs, AX.y1); ctx.line_to(xs, ys); ctx.stroke()
        glow(ctx, xs, ys, 22, CLAY, 0.8 * hl)
        ctx.new_path(); src(ctx, CLAY, hl); ctx.arc(xs, ys, 7, 0, 2 * math.pi); ctx.fill()
    return surf
