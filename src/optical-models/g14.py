"""GIF 14. Clustering the ZnPc DFT transitions into an optical model (Murcia's overlap clustering, dft-learn).
  0.0 to 1.8 s   every DFT stick between 283.5 and 300 eV coloured by carbon site, broadened DFT spectrum
  1.8 to 3.0 s   rigid shift of the DFT energy scale by +0.45 eV (the seed shift of dissertation Fig. 2.6)
  3.0 to 4.2 s   sticks recoloured by cluster
  4.2 to 6.2 s   sticks collapse onto their cluster, one Gaussian per cluster (centre = strength-weighted mean,
                 width = seed width, area = summed strength)
  ionization edge (one erf step per carbon site) drawn from the first frame; envelope, sticks and Gaussians sit on it
  6.4 to 8.0 s   Gaussians move to the values refined against angle-resolved NEXAFS (cluster_gaussians.csv,
                 en_f, wid_f, area scaled by amp_f / amp_i); dipoles are held
Data: znpc_sticks_tensor.csv (aligned sticks, cluster labels), cluster_gaussians.csv (seed and refined)."""
import math
import numpy as np
import pandas as pd
from style import *

SIZE = (1600, 720)
DUR = 9.0
SHIFT = 0.45
D = "/home/claude/znpc_data/data"
ST = pd.read_csv(f"{D}/csv/znpc_sticks_tensor.csv")
CG = pd.read_csv(f"{D}/csv/cluster_gaussians.csv").set_index("cluster")
XL = (283.5, 320.0)                      # the full refined range, every cluster (0 to 18) inside it
SITE_COL = {1: "#2E6F82", 2: "#9DBBC6", 3: "#E2B4AE", 4: "#C2492D"}
CL = sorted(int(c) for c in ST.cluster.unique() if int(c) in CG.index)
STOPS = ["#2E7D8C", "#8A8F94", "#E07A6E"]


def ccol(c):
    t = CL.index(c) / max(len(CL) - 1, 1)
    return mix(STOPS[0], STOPS[1], t / 0.5) if t < 0.5 else mix(STOPS[1], STOPS[2], (t - 0.5) / 0.5)


EG = np.linspace(*XL, 1800)
import json
IPS = dict(zip(("C1", "C2", "C3", "C4"), json.load(open(f"{D}/csv/param_change.json"))["global"]["IPs"]))

# The refined state is the converged Igor fit itself (carbon-lab/znpc-optical-model, data/igor/figures/
# model-comparison.pxp, extracted to znpc_fit40.npz): the 40 deg TEY spectrum (expSpec2), the bare-atom-scaled
# ionization step (dftStep1) and each cluster's fitted peak at 40 deg (pk*_spec2, a normalized Gaussian with sigma =
# wid_f; its area is stored). Step + sum of peaks reproduces Igor's fitresults2 to 0.5% and the data to 0.6% rms.
_f = np.load("/home/claude/omgif/znpc_fit40.npz")
EXP = np.interp(EG, _f["E"], _f["exp"])
STEP = np.interp(EG, _f["E"], _f["step"])                                # fixed baseline under every model curve
AREA = dict(zip(range(19), _f["area"]))
PRE = float(np.interp(283.3, _f["E"], _f["exp"]))                       # pre-edge level of the measured spectrum


def gauss(en, wid, area):
    return area / (wid * math.sqrt(2 * math.pi)) * np.exp(-0.5 * ((EG - en) / wid) ** 2)


# seed: centre = strength-weighted DFT energy + SHIFT (where the sticks slide to), seed width, and the fitted area
# scaled back by amp_i / amp_f (the starting amplitudes under the same projection); refined: en_f, wid_f, fitted area
G0, G1 = {}, {}
for c in CL:
    m = ST[ST.cluster == c]
    G0[c] = dict(en=float((m.en * m.os).sum() / m.os.sum()) + SHIFT, wid=float(CG.loc[c, "wid_i"]),
                 area=AREA[c] * float(CG.loc[c, "amp_i"] / CG.loc[c, "amp_f"]))
    G1[c] = dict(en=float(CG.loc[c, "en_f"]), wid=float(CG.loc[c, "wid_f"]), area=AREA[c])
_fin = sum(gauss(**G1[c]) for c in CL) + STEP
FIT_RMS = float(np.sqrt(np.mean((_fin - EXP)[(EG > 283.5)] ** 2)) / EXP.max())


def envelope(shift):
    y = np.zeros_like(EG)
    for en, os_, w in zip(ST.en, ST.os, ST.wid):
        y += os_ / (w * math.sqrt(2 * math.pi)) * np.exp(-0.5 * ((EG - en - shift) / w) ** 2)
    return y


# DFT sticks and envelope stand on the pre-edge level (above the IP the discrete TP states stand in for the
# continuum), the envelope normalized to the measured pi* maximum above that level
ENV0, ENV1 = envelope(0.0), envelope(SHIFT)
_pi = (EG > 284) & (EG < 286)
_kd = float((EXP[_pi].max() - PRE) / ENV1[_pi].max())
ENV0, ENV1 = PRE + _kd * ENV0, PRE + _kd * ENV1
_seed = sum(gauss(**G0[c]) for c in CL) + STEP
YMAX = 1.10 * max(float(EXP.max()), float(_fin.max()), float(ENV0.max()), float(ENV1.max()), float(_seed.max()))
SMAX = float(ST.os.max())
AX = Axes(120, 40, 1560, 600, XL, (0, YMAX))


def base_y(e):
    return float(np.interp(e, EG, STEP))


def setc(ctx, c, a):
    if isinstance(c, str):
        src(ctx, c, a)
    else:
        ctx.set_source_rgba(c[0], c[1], c[2], a)


def frame(t):
    surf, ctx = new_frame(*SIZE)
    src(ctx, "#FCFFFB"); ctx.paint()          # card fill on slide 8
    sh = SHIFT * smooth(ramp(t, 1.8, 3.0))
    rec = ramp(t, 3.0, 4.2)
    col = ramp(t, 4.2, 6.2)
    ref = smooth(ramp(t, 6.4, 8.0))
    AX.frame(ctx, xticks=(285, 290, 295, 300, 305, 310, 315, 320), size=26)

    # ionization edge, always present: one erf step per carbon site at its refined IP
    spts = AX.pts(EG, STEP)
    ctx.new_path(); ctx.move_to(spts[0][0], AX.y1)
    for px, py in spts:
        ctx.line_to(px, py)
    ctx.line_to(spts[-1][0], AX.y1); ctx.close_path()
    c_ = hexrgb(TAUPE); ctx.set_source_rgba(c_[0], c_[1], c_[2], 0.45); ctx.fill()
    polyline(ctx, spts, RUST, 2.4, 1.0)
    for nm, ip in IPS.items():
        X = AX.X(ip)
        src(ctx, RUST, 0.8); ctx.set_line_width(1.6); ctx.set_dash([4, 4])
        ctx.move_to(X, AX.y1); ctx.line_to(X, AX.Y(STEP.max() * 1.08)); ctx.stroke(); ctx.set_dash([])

    # broadened DFT reference (no step)
    env = ENV0 + (ENV1 - ENV0) * (sh / SHIFT)
    ea = (0.85 - 0.45 * col) * (1 - smooth(ramp(t, 6.4, 7.4)))
    if ea > 0.01:
        polyline(ctx, AX.pts(EG, env), SLATE, 2.4, ea, dash=[10, 6] if col > 0.05 else None)

    # sticks: site colour, then cluster colour, then sliding into their cluster centre
    hs = 0.30 * YMAX / math.sqrt(SMAX)
    sa = 0.8 * (1 - smooth(ramp(t, 5.0, 6.2)))
    if sa > 0.01:
        for en, os_, site, c in zip(ST.en, ST.os, ST.atomid, ST.cluster):
            c = int(c)
            if c not in G0:
                continue
            x0 = en + sh
            x = x0 + (G0[c]["en"] - x0) * smooth(col)
            if not XL[0] <= x <= XL[1]:
                continue
            cc = hexrgb(SITE_COL[int(site)]) if rec <= 0 else ccol(c)
            if 0 < rec < 1:
                a_, b_ = hexrgb(SITE_COL[int(site)]), ccol(c)
                cc = tuple(a_[k] + (b_[k] - a_[k]) * rec for k in range(3))
            setc(ctx, cc, sa)
            ctx.set_line_width(1.8)
            X = AX.X(x); yb = AX.Y(PRE)
            ctx.move_to(X, yb); ctx.line_to(X, yb - hs * math.sqrt(os_) * (AX.y1 - AX.y0) / YMAX); ctx.stroke()

    # cluster Gaussians on top of the step, seed then refined
    ga = smooth(ramp(t, 4.6, 6.2))
    if ga > 0.01:
        total = STEP.copy()
        bpts = AX.pts(EG, STEP)
        for c in CL:
            p = {k: G0[c][k] + (G1[c][k] - G0[c][k]) * ref for k in ("en", "wid", "area")}
            y = gauss(**p) * ga
            total += y
            cpts = AX.pts(EG, STEP + y)
            cc = ccol(c)
            ctx.new_path()
            ctx.move_to(*cpts[0])
            for px, py in cpts[1:]:
                ctx.line_to(px, py)
            for px, py in bpts[::-1]:
                ctx.line_to(px, py)
            ctx.close_path()
            ctx.set_source_rgba(cc[0], cc[1], cc[2], 0.42 * ga); ctx.fill()
            ctx.new_path(); ctx.move_to(*cpts[0])
            for px, py in cpts[1:]:
                ctx.line_to(px, py)
            ctx.set_source_rgba(cc[0], cc[1], cc[2], 0.9 * ga); ctx.set_line_width(1.6); ctx.stroke()
        polyline(ctx, AX.pts(EG, total), CRIMSON, 3.4, ga)

    # measured isotropic beta, always on top
    polyline(ctx, AX.pts(EG, EXP), INK, 3.0, 0.95)
    lx = AX.X(309.0)
    src(ctx, INK, 0.95); ctx.set_line_width(3.0); ctx.move_to(lx, 80); ctx.line_to(lx + 44, 80); ctx.stroke()
    text(ctx, lx + 56, 90, "measured, $θ$ = 40°", 28, INK, 0.95, "l")
    if ga > 0.01:
        src(ctx, CRIMSON, ga); ctx.set_line_width(3.4); ctx.move_to(lx, 122); ctx.line_to(lx + 44, 122); ctx.stroke()
        text(ctx, lx + 56, 132, "model", 28, CRIMSON, ga, "l")
    if ea > 0.01:
        yl = 164 if ga > 0.01 else 122
        src(ctx, SLATE, ea); ctx.set_line_width(2.4)
        if col > 0.05:
            ctx.set_dash([10, 6])
        ctx.move_to(lx, yl); ctx.line_to(lx + 44, yl); ctx.stroke(); ctx.set_dash([])
        text(ctx, lx + 56, yl + 10, "DFT", 28, SLATE, ea, "l")

    # dynamic captions
    a1 = ramp(t, 1.8, 2.1) * (1 - ramp(t, 3.4, 3.8))
    if a1 > 0.01:
        text(ctx, AX.X(289.0), 110, "DFT energies  +0.45 eV", 30, RUST, a1, "l")
    a2 = ramp(t, 4.4, 4.8) * (1 - ramp(t, 6.0, 6.3))
    if a2 > 0.01:
        text(ctx, AX.X(289.0), 110, "one Gaussian per cluster", 30, INK, a2, "l")
    a3 = ramp(t, 6.5, 6.9)
    if a3 > 0.01:
        text(ctx, AX.X(289.0), 110, "refined against angle-resolved NEXAFS", 30, NAVY, a3, "l")
    return surf
