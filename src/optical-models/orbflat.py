"""Flat, outlined orbital lobes (the benzene-lobe look) from an isosurface field. Each connected lobe is rasterized
as one shape: a soft fill in its phase colour with a darker outline, lobes painted back to front. Two layers:
below and above the molecular plane, each in a filled and an outline-only (empty state) version."""
import numpy as np, cairo
from scipy import ndimage
from skimage.measure import marching_cubes
from style import hexrgb, IVORY

POS, NEG, EDGE = "#C23A52", "#EBB7C1", "#8E1A30"


def lobes(F, origin, h, lev, minvox=40):
    out = []
    for sgn in (1, -1):
        lab, n = ndimage.label(sgn * F > lev)
        sizes = ndimage.sum_labels(np.ones_like(lab), lab, index=np.arange(1, n + 1))
        objs = ndimage.find_objects(lab)
        for i in np.where(sizes >= minvox)[0] + 1:
            sl = objs[i - 1]
            sl = tuple(slice(max(0, s.start - 2), s.stop + 2) for s in sl)
            sub = np.where(lab[sl] == i, sgn * F[sl], 0.0)
            v, f, nrm, _ = marching_cubes(sub, lev, gradient_direction="descent")
            v = origin + (v + np.array([s.start for s in sl])) * h
            out.append((sgn, v, f, nrm))
    return out


def render(lobe_list, P, VIEW, LIGHT=None, size=(1200, 800), edge_w=2.6):
    """per lobe, back to front: the triangles stroked wide in the edge colour, then filled (with a hairline of the
    same colour to close seams) in the phase colour, so only the silhouette keeps an outline. The outline-only
    version clears the interior instead, so nearer lobes still hide farther outlines."""
    W, H = size
    res = {}
    ec = hexrgb(EDGE)[:3]
    for front in (False, True):
        items = [(v.mean(0) @ VIEW, sgn, v, f) for sgn, v, f, nrm in lobe_list if (v[:, 2].mean() >= 0) == front]
        items.sort(key=lambda it: it[0])
        for name in ("fill", "ring"):
            surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
            ctx = cairo.Context(surf)
            ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            for d, sgn, v, f in items:
                sx, sy = P(v)
                fn = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
                keep = f
                ctx.new_path()
                for a, b, c in keep:
                    if (sx[b] - sx[a]) * (sy[c] - sy[a]) - (sx[c] - sx[a]) * (sy[b] - sy[a]) < 0:
                        b, c = c, b                      # one orientation, so the winding fill is the union
                    ctx.move_to(sx[a], sy[a]); ctx.line_to(sx[b], sy[b]); ctx.line_to(sx[c], sy[c]); ctx.close_path()
                path = ctx.copy_path()
                ctx.set_source_rgb(*ec)
                ctx.set_line_width(edge_w)
                ctx.stroke()
                ctx.append_path(path)
                ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
                if name == "fill":
                    ctx.set_source_rgb(*hexrgb(POS if sgn > 0 else NEG)[:3])
                    ctx.fill()
                else:
                    ctx.set_operator(cairo.OPERATOR_CLEAR)
                    ctx.fill()
                    ctx.set_operator(cairo.OPERATOR_OVER)
            surf.flush()
            res[(front, name)] = surf
    return res
