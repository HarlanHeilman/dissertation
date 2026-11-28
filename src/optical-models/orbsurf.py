"""Pre-rendered, shaded MO isosurfaces for GIF 12. Two layers per state (below and above the molecular plane),
so the skeleton can be drawn between them. 2x supersampled, box-filtered down."""
import math, numpy as np, cairo
from skimage.measure import marching_cubes
from style import hexrgb

POS, NEG = "#B8263F", "#E8A3B0"          # phases: crimson and rose, as the benzene lobes


def iso_level(psi, frac):
    """|psi| at which the enclosed density is frac of the density in the box"""
    d = np.sort((psi.astype(np.float64) ** 2).ravel())[::-1]
    c = np.cumsum(d)
    return float(math.sqrt(d[np.searchsorted(c, frac * c[-1])]))


def mesh(st, lev, to_frame, up=2):
    from scipy.ndimage import zoom
    psi = zoom(st["psi"].astype(np.float32), up, order=3)     # cubic upsampling for smooth surfaces
    step = st["step"] * (np.array(st["psi"].shape) - 1) / (np.array(psi.shape) - 1)
    out = []
    for sgn in (1, -1):
        v, f, n, _ = marching_cubes(sgn * psi, lev, step_size=1, gradient_direction="descent")
        v = st["origin"] + v * step
        v, n = to_frame(v), to_frame(n, vec=True)
        out.append((sgn, v, f, n))
    return out, lev


def render_layers(meshes, P, VIEW, LIGHT, size=(1200, 800), ss=2):
    W, H = size
    layers = []
    Hh = LIGHT + VIEW
    Hh = Hh / np.linalg.norm(Hh)
    for front in (False, True):
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W * ss, H * ss)
        ctx = cairo.Context(surf)
        ctx.scale(ss, ss)
        ctx.set_antialias(cairo.ANTIALIAS_NONE)
        tris = []
        for sgn, v, f, n in meshes:
            cz = v[f].mean(1)[:, 2]
            keep = (cz >= 0) if front else (cz < 0)
            ff = f[keep]
            nn = n[ff].mean(1)
            nn /= np.linalg.norm(nn, axis=1, keepdims=True) + 1e-12
            vis = nn @ VIEW > -0.05
            ff, nn = ff[vis], nn[vis]
            depth = v[ff].mean(1) @ VIEW
            lam = np.clip(nn @ LIGHT, 0, 1)
            spec = np.clip(nn @ Hh, 0, 1) ** 28
            rim = 1 - np.clip(nn @ VIEW, 0, 1)
            base = np.array(hexrgb(POS if sgn > 0 else NEG)[:3])
            col = base[None, :] * (0.52 + 0.48 * lam[:, None]) * (1 - 0.18 * rim[:, None] ** 2) + 0.38 * spec[:, None]
            sx, sy = P(v)
            tris.append((depth, ff, np.clip(col, 0, 1), sx, sy))
        allt = [(d[i], k, i) for k, (d, *_) in enumerate(tris) for i in range(len(d))]
        allt.sort()
        for _, k, i in allt:
            d, ff, col, sx, sy = tris[k]
            a, b, c = ff[i]
            ctx.move_to(sx[a], sy[a]); ctx.line_to(sx[b], sy[b]); ctx.line_to(sx[c], sy[c]); ctx.close_path()
            ctx.set_source_rgb(*col[i])
            ctx.fill_preserve()
            ctx.set_line_width(0.6)
            ctx.stroke()
        surf.flush()
        A = np.ndarray((H * ss, W * ss, 4), np.uint8, surf.get_data()).astype(np.float32)
        A = A.reshape(H, ss, W, ss, 4).mean((1, 3))
        out = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        np.ndarray((H, W, 4), np.uint8, out.get_data())[:] = np.round(A).astype(np.uint8)
        out.mark_dirty()
        layers.append(out)
    return layers
