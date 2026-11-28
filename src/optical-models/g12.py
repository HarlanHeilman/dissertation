"""GIF 12. ZnPc counterpart of GIF 2 for a slide-to-slide swap: same canvas, ladder, axes and styling.
Spectrum: ML-refined isotropic beta (carbon-lab/znpc-optical-model, exp_bets.csv). The cursor steps, in energy order,
through three refined clusters (1 pi*, 13 mixed, 15 sigma*). For each, one StoBe TP transition from a different carbon
site is drawn: its final MO as shaded isosurfaces (phases crimson and rose, per-state isovalue ISO), mu = <1s|r|psi_f> at the core-hole atom, angle from the local isoindole normal (znpc_orb.py)."""
import math, json, pickle, os
import numpy as np
import pandas as pd
from style import *
import orbsym, orbflat

DUR = 9.9
ELO, EHI = 280.0, 320.0
D = "/home/claude/znpc_data/data"
_b = pd.read_csv(f"{D}/optical/exp_bets.csv")
_b = _b[(_b.Energy >= ELO - 0.5) & (_b.Energy <= EHI + 0.5)]
EG = np.linspace(ELO, EHI, 801)
BETA = np.interp(EG, _b.Energy.values, _b["βiso"].values)
_pc = json.load(open(f"{D}/csv/param_change.json"))
IPS = dict(zip(("C1", "C2", "C3", "C4"), _pc["global"]["IPs"]))
PK = {p["cluster"]: p for p in _pc["peaks"]}

_pcl = pd.read_csv(f"{D}/csv/znpc_params_cluster.csv", encoding="utf-8-sig").iloc[:, :13]
ST = sorted(pickle.load(open("/home/claude/omgif/znpc_orb.pkl", "rb")), key=lambda s: PK[s["cluster"]]["en_f"])
NS = len(ST)
for s in ST:
    s["E"] = PK[s["cluster"]]["en_f"]
    s["W"] = PK[s["cluster"]]["wid_f"]
    s["IP"] = IPS[s["site"]]
    s["bound"] = s["E"] < s["IP"]
ISO = {("C3", 119): 0.060, ("C2", 124): 0.060, ("C3", 133): 0.055, ("C1", 205): 0.027, ("C4", 314): 0.055}       # |psi| isovalues (bohr^-3/2), chosen per state

AX = Axes(110, 470, 1150, 668, (ELO, EHI), (0, BETA.max() * 1.12))

# ------------------------------------------------------------------ timing
WIN = [(0.35 + 1.85 * k, 0.35 + 1.85 * k + 1.6) for k in range(5)]


def strength(t, k):
    a, b = WIN[k]
    return ramp(t, a + 0.05, a + 0.35) * (1 - ramp(t, b - 0.3, b))


def presence(t, k):
    a, b = WIN[k]
    return ramp(t, a - 0.16, a) * (1 - ramp(t, b, b + 0.12))


def _ease(u):
    u = clamp(u)
    return 0.5 - 0.5 * math.cos(math.pi * u)


def glide(t, vals):
    v = vals[0]
    for k in range(1, NS):
        v = v + (vals[k] - vals[k - 1]) * _ease((t - (WIN[k - 1][1] - 0.15)) / (WIN[k][0] - WIN[k - 1][1] + 0.3))
    return v


def energy(t):
    return glide(t, [s["E"] for s in ST])


def ip_now(t):
    return glide(t, [s["IP"] for s in ST])


def fade(t):
    return ramp(t, 0.0, 0.3) * (1 - ramp(t, WIN[-1][1], WIN[-1][1] + 0.45))


def at(arr, E):
    return float(np.interp(E, EG, arr))


# ------------------------------------------------------------------ molecule view (same as the benzene ring)
MCX, MCY = 315, 236
SQ = 0.42
CPHI = math.sqrt(1 - SQ ** 2)
XYZ0 = ST[0]["xyz"]
ZN = np.where(ST[0]["Z"] == 4, 6, ST[0]["Z"])        # StoBe ECP carbons carry Z=4
_c = XYZ0.mean(0)
_, _, _vt = np.linalg.svd(XYZ0 - _c)
_n = _vt[2] * np.sign(_vt[2][2])
FR = np.array([_vt[0], np.cross(_n, _vt[0]), _n])   # rows: screen-x, depth (front +), molecular normal
XYZ_RAW = (XYZ0 - _c) @ FR.T
XYZ, D4, SYM_SHIFT = orbsym.symmetrize_geometry(XYZ_RAW, ZN)   # D4h-averaged, Zn at the origin
ZN_OFF = XYZ_RAW[np.where(ZN == 30)[0][0]]
SC = 220.0 / np.abs(XYZ[:, 0]).max()
VIEW = np.array([0.0, CPHI, SQ])                      # toward the viewer
LIGHT = np.array([-0.45, 0.45, 0.77])
LIGHT /= np.linalg.norm(LIGHT)


def P(p):
    p = np.asarray(p, float)
    return MCX + SC * p[..., 0], MCY + SC * (SQ * p[..., 1] - CPHI * p[..., 2])


def V(v):
    v = np.asarray(v, float)
    return SC * v[..., 0], SC * (SQ * v[..., 1] - CPHI * v[..., 2])


def to_frame(p, vec=False):
    p = np.asarray(p, float)
    return p @ FR.T if vec else (p - _c) @ FR.T


for s in ST:
    s["tdm_m"] = to_frame(s["tdm"], True)
    s["nrm_m"] = to_frame(s["normal"], True)

_CACHE = "/tmp/g12_flat.pkl"


def _layers():
    if os.path.exists(_CACHE):
        raw = pickle.load(open(_CACHE, "rb"))
    else:
        raw = []
        ext = np.abs(XYZ).max(0)
        lo = -ext - np.array([3.0, 3.0, 0.0]); lo[2] = -4.5
        hi = ext + np.array([3.0, 3.0, 0.0]); hi[2] = 4.5
        for s in ST:
            F, org, h = orbsym.sym_field(s, FR, ZN_OFF @ FR + _c, D4, lo, hi, 0.13)
            from scipy.ndimage import zoom
            from scipy.ndimage import gaussian_filter
            F = gaussian_filter(F, 0.11 / h)              # light smoothing (0.11 A) of the spliced field
            F = zoom(F, 2, order=3)                        # smoother silhouettes
            h = h * 0.5
            lob = orbflat.lobes(F, org, h, ISO[(s["site"], s["mo"])], minvox=300)
            # drop detached lobes far from every atom (diffuse Rydberg-like tails)
            lob = [L for L in lob if np.linalg.norm(XYZ[None] - L[1].mean(0)[None, None], axis=2).min() < 2.2]
            L = orbflat.render(lob, P, VIEW, LIGHT)
            raw.append({k: (bytes(v.get_data()), v.get_width(), v.get_height(), v.get_stride()) for k, v in L.items()})
            print(s["site"], s["mo"], "lobes", len(lob))
        pickle.dump(raw, open(_CACHE, "wb"))
    return [{k: cairo.ImageSurface.create_for_data(bytearray(b), cairo.FORMAT_ARGB32, w, h, st)
             for k, (b, w, h, st) in r.items()} for r in raw]


LAYERS = _layers()

# the 8 equivalent core sites of each state, with their dipoles
for s in ST:
    e = s["exc"]
    s["sites"] = []
    tl = [(to_frame(u, True), w) for u, w in s["tdms"]]
    s["eff"] = len(tl) > 1
    if s["eff"]:
        # one cluster-equivalent dipole per site: tilt alpha with cos^2(alpha) = Tzz / tr(T) of the cluster tensor,
        # leaning toward the in-plane member. Its 8 D4 copies sum to exactly the cluster's uniaxial tensor.
        r = _pcl.iloc[s["cluster"]]
        al = math.acos(math.sqrt(r.zz / (r.xx + r.yy + r.zz)))
        ip = max(tl, key=lambda q: math.hypot(q[0][0], q[0][1]))[0].copy()
        ip[2] = 0
        ip /= np.linalg.norm(ip)
        tl = [(math.cos(al) * np.array([0, 0, 1.0]) + math.sin(al) * ip, 1.0)]
    for g in D4:
        y = XYZ[e] @ g.T
        j = int(np.linalg.norm(XYZ - y, axis=1).argmin())
        for u, w in tl:                                   # arrow length ~ |mu| ~ sqrt(oscillator strength)
            m = (g @ u) * math.sqrt(w)
            s["sites"].append((j, m * (1 if m[2] >= 0 else -1)))
    s["thetas"] = [math.degrees(math.acos(min(1.0, abs(u[2])))) for u, w in tl]   # from the molecular normal
    s["theta_cl"] = float(_pcl.theta[s["cluster"]])


def bonds():
    out = []
    for i in range(len(XYZ)):
        for j in range(i + 1, len(XYZ)):
            d = np.linalg.norm(XYZ[i] - XYZ[j])
            zi, zj = ZN[i], ZN[j]
            if 1 in (zi, zj):
                if d < 1.2:
                    out.append((i, j, "h"))
            elif 30 in (zi, zj):
                if d < 2.15:
                    out.append((i, j, "zn"))
            elif d < 1.6:
                out.append((i, j, "cc"))
    return out


BONDS = bonds()
SX, SY = P(XYZ)
DEP = XYZ @ VIEW
ORDER = np.argsort(DEP)


def depth_alpha(d):
    return 0.6 + 0.4 * (d - DEP.min()) / (DEP.max() - DEP.min())


def draw_skeleton(ctx):
    for i, j, kind in sorted(BONDS, key=lambda b: DEP[b[0]] + DEP[b[1]]):
        al = depth_alpha(0.5 * (DEP[i] + DEP[j]))
        if kind == "cc":
            src(ctx, DEEP, al)
            ctx.set_line_width(4.0)
        elif kind == "h":
            src(ctx, SLATE, 0.8 * al)
            ctx.set_line_width(2.6)
        else:
            src(ctx, SLATE, 0.7 * al)
            ctx.set_line_width(2.0)
            ctx.set_dash([4, 4])
        ctx.move_to(SX[i], SY[i])
        ctx.line_to(SX[j], SY[j])
        ctx.stroke()
        ctx.set_dash([])
    for i in ORDER:
        z = ZN[i]
        al = depth_alpha(DEP[i])
        ctx.new_path()
        if z == 30:
            src(ctx, SLATE)
            ctx.arc(SX[i], SY[i], 12, 0, 2 * math.pi)
            ctx.fill_preserve()
            src(ctx, INK)
            ctx.set_line_width(2)
            ctx.stroke()
            text(ctx, SX[i], SY[i] + 6, "Zn", 16, IVORY, 1.0, "c")
            ctx.new_path()
            continue
        r, fill, edge, lw = {1: (4.2, IVORY, MUTED, 1.4), 6: (4.6, IVORY, DEEP, 2.0), 7: (5.2, ICE, NAVY, 2.0)}[z]
        src(ctx, fill, al)
        ctx.arc(SX[i], SY[i], r, 0, 2 * math.pi)
        ctx.fill_preserve()
        src(ctx, edge, al)
        ctx.set_line_width(lw)
        ctx.stroke()


HMU = 1.9          # half-length of each dipole arrow, Angstrom


def _occ(k):
    """occupancy of state k's lobes, skeleton atoms and dipole arrows (integral image)"""
    A = np.zeros((800, 1200), np.float32)
    for key in ((False, "fill"), (True, "fill")):
        l = LAYERS[k][key]
        l.flush()
        A = np.maximum(A, np.ndarray((800, l.get_stride() // 4, 4), np.uint8, l.get_data())[:, :1200, 3] / 255.0)
    for x, y in zip(SX, SY):
        A[max(0, int(y) - 6):int(y) + 7, max(0, int(x) - 6):int(x) + 7] = 1
    for j, m in ST[k]["sites"]:
        dx, dy = V(m)
        for u in np.linspace(-1, 1, 25):
            x, y = SX[j] + u * HMU * dx, SY[j] + u * HMU * dy
            A[max(0, int(y) - 5):int(y) + 6, max(0, int(x) - 5):int(x) + 6] = 1
    return np.cumsum(np.cumsum(A, 0), 1)


def _box_sum(I, x0, y0, x1, y1):
    x0, y0 = int(max(0, min(1199, x0))), int(max(0, min(799, y0)))
    x1, y1 = int(max(0, min(1199, x1))), int(max(0, min(799, y1)))
    return I[y1, x1] - I[y0, x1] - I[y1, x0] + I[y0, x0]


def place_labels(k):
    """mu label at the arrow tip with the most free space around it; C 1s label below, led to the nearest site"""
    s = ST[k]
    I = _occ(k)
    best = None
    for j, m in s["sites"]:
        dx, dy = V(m)
        for sgn in (1, -1):
            tx, ty = SX[j] + sgn * HMU * dx, SY[j] + sgn * HMU * dy
            for side in ("l", "r"):
                for ox in (10, 24):
                    lx = tx + (ox if side == "l" else -ox)
                    for oy in range(-60, 40, 8):
                        ly = ty + oy
                        x0 = lx if side == "l" else lx - 110
                        box = (x0 - 4, ly - 28, x0 + (170 if len(s["tdms"]) > 1 else 124), ly + 46)
                        sc = _box_sum(I, *box) + 4000 * ((box[0] < 50) + (box[2] > 705) + (box[1] < 30) + (box[3] > 440)) \
                            + 4 * (ox + abs(oy + 12))
                        if best is None or sc < best[0]:
                            best = (sc, lx, ly, side, box, tx, ty)
    mu_lab, mb = best[1:4] + best[5:7], best[4]
    best = None
    for j, m in s["sites"]:
        ex, ey = SX[j], SY[j]
        if ey < MCY:
            continue
        for side in ("r", "l"):
            lx = ex - 46 if side == "r" else ex + 46
            ly = 410
            box = (lx - 250, ly - 26, lx + 4, ly + 8) if side == "r" else (lx - 4, ly - 26, lx + 250, ly + 8)
            over = not (box[2] < mb[0] or box[0] > mb[2] or box[3] < mb[1] or box[1] > mb[3])
            sc = 40000 * ((box[0] < 30) + (box[2] > 715)) + 5000 * over + 2 * abs(ex - MCX) + 0.5 * _box_sum(I, *box)
            if best is None or sc < best[0]:
                best = (sc, lx, ly, side, j)
    return mu_lab, best[1:]


LABELS = [place_labels(k) for k in range(NS)]


def draw_molecule(ctx, t, fd):
    orb = []
    for k in range(NS):
        vis = presence(t, k) * fd
        orb.append((k, vis, strength(t, k) * fd))
    for front in (False, True):
        for k, vis, res in orb:
            if vis < 0.005:
                continue
            fa = (0.85 if front else 1.0) * vis * res
            ctx.set_source_surface(LAYERS[k][(front, "ring")], 0, 0)
            ctx.paint_with_alpha(0.55 * vis * (1 - res))          # empty state: outline only, as the dashed benzene lobes
            if fa > 0.005:
                ctx.set_source_surface(LAYERS[k][(front, "fill")], 0, 0)
                ctx.paint_with_alpha(fa)
        if not front:
            draw_skeleton(ctx)
    for k, s in enumerate(ST):
        vis = presence(t, k) * fd
        if vis < 0.01:
            continue
        res = strength(t, k) * fd
        pa = vis * (0.25 + 0.75 * res)
        for j, m in s["sites"]:
            glow(ctx, SX[j], SY[j], 30, CLAY, 0.75 * res)
        for j, m in sorted(s["sites"], key=lambda q: DEP[q[0]]):
            dx, dy = V(m)
            ex, ey = SX[j], SY[j]
            arrow(ctx, ex - HMU * dx, ey - HMU * dy, ex + HMU * dx, ey + HMU * dy, NAVY, 3.0, 13, pa, both=True)
            src(ctx, CLAY, vis * (0.6 + 0.4 * res))
            ctx.new_path()
            ctx.arc(ex, ey, 4.8, 0, 2 * math.pi)
            ctx.fill()
        (lx, ly, side, tx, ty), (cx1, cy1, cside, jc) = LABELS[k]
        text(ctx, lx, ly + 4, "$μ$", 34, NAVY, pa, side)
        text(ctx, lx, ly + 36, f"$θ$ = {s['thetas'][0]:.0f}°" + (" (cluster)" if s["eff"] else ""), 26, NAVY, pa, side)
        text(ctx, cx1, cy1, f"C 1s, site {s['site']} ×8", 30, INK, 0.9 * vis, cside)
        src(ctx, SLATE, 0.6 * vis)
        ctx.set_line_width(1.6)
        ctx.move_to(cx1 + (4 if cside == "r" else -4), cy1 - 12)
        ctx.line_to(SX[jc] + (-5 if cside == "r" else 5), SY[jc] + 7)
        ctx.stroke()


# ------------------------------------------------------------------ level ladder (as GIF 2)
LY_TOP, LY_BOT = 50, 318
LX0, LX1 = 735, 1150
_LE = [280.0, 285.1, 290.3, 293.5, 301.0, 320.0]
_LYv = [318, 262, 200, 164, 118, 56]


def LY(h):
    return float(np.interp(h, _LE, _LYv))


Y1S = 402


# four core platforms, one per chemically distinct carbon, offset by the refined site IPs (deeper = lower)
SITES = ("C1", "C2", "C3", "C4")
BAR_W, BAR_GAP = 40, 13
BAR_X = {nm: LX0 + 52 + BAR_W / 2 + i * (BAR_W + BAR_GAP) for i, nm in enumerate(SITES)}
_ipm = min(IPS.values())
BAR_Y = {nm: Y1S + 9.0 * (IPS[nm] - _ipm) - 6 for nm in SITES}
SITE_ATOM = {"C1": 0, "C2": 1, "C3": 2, "C4": 3}           # one of each class, in one isoindole unit


def site_weight(t, nm):
    return sum(strength(t, k) for k, s in enumerate(ST) if s["site"] == nm)


def site_presence(t, nm):
    return sum(presence(t, k) for k, s in enumerate(ST) if s["site"] == nm)


def _cutout_geometry():
    """top-down view of one isoindole unit (with its meso N), long axis horizontal"""
    cen = XYZ[[0, 1, 2, 3]].mean(0)
    keep = [i for i in range(len(XYZ)) if ZN[i] in (6, 7) and np.linalg.norm(XYZ[i] - cen) < 3.6]
    P2 = XYZ[keep][:, :2]
    c2 = XYZ[[0, 1, 2, 3, 4, 5, 6, 7]][:, :2].mean(0)
    npyr = min((i for i in keep if ZN[i] == 7), key=lambda i: np.linalg.norm(XYZ[i, :2]))   # pyrrole N, next to Zn
    ax = c2 - XYZ[npyr, :2]
    ax /= np.linalg.norm(ax)                       # pyrrole on the left, benzo ring on the right, as C1 ... C4
    R2 = np.array([ax, [-ax[1], ax[0]]])
    Q = (P2 - c2) @ R2.T
    return keep, Q


CUT_IDX, CUT_Q = _cutout_geometry()
CUT_SC = 20.0
CUT_X0, CUT_Y0 = 1068, 494


def draw_cutout(ctx, t, fd):
    pos = {i: (CUT_X0 + CUT_SC * q[0], CUT_Y0 - CUT_SC * q[1]) for i, q in zip(CUT_IDX, CUT_Q)}
    for a in CUT_IDX:
        for b in CUT_IDX:
            if a < b:
                d = np.linalg.norm(XYZ[a] - XYZ[b])
                hb = 1 in (ZN[a], ZN[b])
                if d < (1.2 if hb else 1.6):
                    src(ctx, SLATE if hb else DEEP, 0.8)
                    ctx.set_line_width(1.6 if hb else 2.6)
                    ctx.move_to(*pos[a])
                    ctx.line_to(*pos[b])
                    ctx.stroke()
    for i in CUT_IDX:
        x, y = pos[i]
        ctx.new_path()
        r, fill, edge = {1: (2.6, IVORY, MUTED), 6: (3.2, IVORY, DEEP), 7: (3.6, ICE, NAVY)}[ZN[i]]
        src(ctx, fill)
        ctx.arc(x, y, r, 0, 2 * math.pi)
        ctx.fill_preserve()
        src(ctx, edge)
        ctx.set_line_width(1.4)
        ctx.stroke()
    for nm, i in SITE_ATOM.items():
        x, y = pos[i]
        w = site_weight(t, nm) * fd
        glow(ctx, x, y, 22, CLAY, 0.8 * w)
        ctx.new_path()
        src(ctx, IVORY)
        ctx.arc(x, y, 5.6, 0, 2 * math.pi)
        ctx.fill_preserve()
        src(ctx, CLAY if w > 0.05 else DEEP, 1.0)
        ctx.set_line_width(2.0)
        ctx.stroke()
        if w > 0.01:
            src(ctx, CLAY, w)
            ctx.arc(x, y, 3.6, 0, 2 * math.pi)
            ctx.fill()
        q = CUT_Q[CUT_IDX.index(i)]
        cq = CUT_Q[:8].mean(0)
        d = (q - cq) / (np.linalg.norm(q - cq) + 1e-9)
        if nm == "C2":
            d = np.array([0.0, 1.0 if q[1] >= cq[1] else -1.0])     # bridgehead: label straight out of the ring
        lx, ly = x + 19 * d[0], y - 19 * d[1] + 7
        text(ctx, lx, ly, nm, 19, CLAY if w > 0.3 else INK, 0.95, "c")


def draw_levels(ctx, t, fd):
    E = energy(t)
    pi_a = sum(strength(t, k) for k, s in enumerate(ST) if s["bound"]) * fd
    sig_a = sum(strength(t, k) for k, s in enumerate(ST) if not s["bound"]) * fd
    res = pi_a + sig_a
    pi0 = sum(strength(t, k) for k, s in enumerate(ST) if s["bound"] and abs(s["E"] - 285.1) <= 0.3) * fd
    # continuum: fades in above the site IPs, no hard threshold line
    ipm = float(np.mean(list(IPS.values())))
    g = cairo.LinearGradient(0, LY(ipm - 1.0), 0, LY_TOP - 10)
    c = hexrgb(TAUPE)
    g.add_color_stop_rgba(0, c[0], c[1], c[2], 0.0)
    g.add_color_stop_rgba(0.25, c[0], c[1], c[2], 0.14)
    g.add_color_stop_rgba(1, c[0], c[1], c[2], 0.42)
    ctx.set_source(g)
    ctx.rectangle(LX0 + 40, LY_TOP - 10, LX1 - LX0 - 40, LY(ipm - 1.0) - LY_TOP + 10)
    ctx.fill()
    for k, s in enumerate(ST):
        vis = presence(t, k) * fd
        if vis < 0.01:
            continue
        if s["bound"]:
            if abs(s["E"] - 285.1) > 0.3:                  # higher pi* levels get their own bar
                yE = LY(s["E"])
                src(ctx, CRIMSON, vis * (0.35 + 0.55 * strength(t, k)))
                ctx.set_line_width(5.0)
                ctx.move_to(LX0 + 70, yE)
                ctx.line_to(LX0 + 250, yE)
                ctx.stroke()
                src(ctx, CRIMSON, 0.20 * vis * strength(t, k))
                rounded_rect(ctx, LX0 + 62, yE - 11, 196, 22, 11)
                ctx.fill()
            continue
        y0, y1 = LY(s["E"] + s["W"]), LY(s["E"] - s["W"])
        src(ctx, SKY, vis * (0.22 + 0.55 * strength(t, k)))
        rounded_rect(ctx, LX0 + 70, y0, 180, y1 - y0, min(10, (y1 - y0) / 2))
        ctx.fill()
    text(ctx, LX0 + 262, LY(296.5) + 14, "$σ$^{*}", 42, BLUE, 0.6 + 0.4 * sig_a)
    text(ctx, LX1 - 8, LY_TOP + 34, "continuum", 30, SLATE, 0.9, "r")
    src(ctx, CRIMSON, 0.55 + 0.45 * pi0)
    ctx.set_line_width(6.0)
    ctx.move_to(LX0 + 70, LY(285.1))
    ctx.line_to(LX0 + 250, LY(285.1))
    ctx.stroke()
    if pi0 > 0.01:
        src(ctx, CRIMSON, 0.22 * pi0)
        rounded_rect(ctx, LX0 + 62, LY(285.1) - 12, 196, 24, 12)
        ctx.fill()
    text(ctx, LX0 + 262, LY(285.1) + 14, "$π$^{*}", 42, CRIMSON, 0.6 + 0.4 * pi_a)

    # four 1s platforms
    for nm in SITES:
        x, y = BAR_X[nm], BAR_Y[nm]
        w = site_weight(t, nm) * fd
        src(ctx, INK, 0.9)
        ctx.set_line_width(5)
        ctx.move_to(x - BAR_W / 2, y)
        ctx.line_to(x + BAR_W / 2, y)
        ctx.stroke()
        electron(ctx, x + 8, y, 6)
        hole(ctx, x - 8, y, 6, w)
        electron(ctx, x - 8, y, 6, 1 - w)
        text(ctx, x, y + 26, nm, 20, CLAY if w > 0.3 else SLATE, 0.95, "c")
    text(ctx, LX0 + 262, Y1S + 13, "C 1s", 38, INK)

    ax = glide(t, [BAR_X[s["site"]] for s in ST])
    y1s = glide(t, [BAR_Y[s["site"]] for s in ST])
    tip = LY(E)
    yb = 352
    src(ctx, CLAY, 0.95)
    ctx.set_line_width(4)
    ctx.move_to(ax, y1s - 10)
    ctx.line_to(ax, yb + 8)
    ctx.stroke()
    ctx.move_to(ax, yb - 8)
    ctx.line_to(ax, tip + 14)
    ctx.stroke()
    src(ctx, CLAY)
    ctx.set_line_width(3)
    for dy in (-8, 8):
        ctx.move_to(ax - 14, yb + dy + 5)
        ctx.line_to(ax + 14, yb + dy - 5)
        ctx.stroke()
    arrow_head(ctx, ax, tip, -math.pi / 2, 22, CLAY)
    text(ctx, LX0 + 58, yb + 14, "h$ν$", 40, CLAY, 1.0, "r")
    glow(ctx, ax, tip, 40, CLAY if pi_a > sig_a else SKY, 0.6 * res)
    electron(ctx, ax, tip - 2, 11, res)
    draw_cutout(ctx, t, fd)


# ------------------------------------------------------------------ spectrum
def highlight(ctx, s, a):
    lo, hi = s["E"] - 2.5 * s["W"], s["E"] + 2.5 * s["W"]
    m = (EG >= lo) & (EG <= hi)
    pts = AX.pts(EG[m], BETA[m])
    g = cairo.LinearGradient(AX.X(lo), 0, AX.X(hi), 0)
    c = hexrgb(CRIMSON if s["bound"] else SKY)
    for q in np.linspace(0, 1, 21):
        e = lo + q * (hi - lo)
        g.add_color_stop_rgba(q, c[0], c[1], c[2], (0.45 if s["bound"] else 0.75) * a * math.exp(-0.5 * ((e - s["E"]) / s["W"]) ** 2))
    ctx.move_to(pts[0][0], AX.y1)
    for p in pts:
        ctx.line_to(*p)
    ctx.line_to(pts[-1][0], AX.y1)
    ctx.close_path()
    ctx.set_source(g)
    ctx.fill()


def frame(t):
    surf, ctx = new_frame()
    fd = fade(t)
    E = energy(t)
    draw_molecule(ctx, t, fd)
    draw_levels(ctx, t, fd)

    AX.frame(ctx, xticks=(280, 290, 300, 310, 320), xlabel="Photon energy (eV)")
    text(ctx, AX.x0 - 30, (AX.y0 + AX.y1) / 2, "Absorption", 36, SLATE, 1.0, "c", rotate=-math.pi / 2)
    pts = AX.pts(EG, BETA)
    fill_under(ctx, pts, AX.y1, CRIMSON, 0.10)
    for k, s in enumerate(ST):
        a = strength(t, k) * fd
        if a > 0.01:
            highlight(ctx, s, a)
    polyline(ctx, pts, CRIMSON, 5.5, 1.0)
    pk = EG[np.argmax(BETA)]
    text(ctx, AX.X(pk) + 16, AX.Y(BETA.max()) + 26, "$π$^{*}", 40, CRIMSON, 1.0)
    text(ctx, AX.X(303.0), AX.Y(at(BETA, 298.5)) - 14, "$σ$^{*}", 40, BLUE, 1.0, "c")
    cx = AX.X(E)
    src(ctx, CLAY, 0.9 * fd)
    ctx.set_line_width(2.4)
    ctx.set_dash([6, 6])
    ctx.move_to(cx, AX.y0 - 6)
    ctx.line_to(cx, AX.y1)
    ctx.stroke()
    ctx.set_dash([])
    yv = AX.Y(at(BETA, E))
    glow(ctx, cx, yv, 22, CLAY, 0.45 * fd)
    ctx.new_path()
    src(ctx, CLAY, fd)
    ctx.arc(cx, yv, 7, 0, 2 * math.pi)
    ctx.fill()
    return surf
