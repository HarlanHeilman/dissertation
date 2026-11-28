"""Shared spectrum panel for the KK versions of GIF 2 (benzene) and GIF 12 (ZnPc).
The plot is narrowed to free a right-hand column that reads top to bottom:
beta, measured  ->  Kramers-Kronig  ->  delta, computed."""
import math
from style import *

PX0, PY0, PX1, PY1 = 110, 452, 925, 698      # plot box (px)
CX = 962                                      # legend column left edge


def make_axes(xlim, ylim):
    return Axes(PX0, PY0, PX1, PY1, xlim, ylim)


def ylabel(ctx, ax):
    text(ctx, ax.x0 - 30, (ax.y0 + ax.y1) / 2, "$β$,  $δ$", 38, SLATE, 1.0, "c", rotate=-math.pi / 2)


def legend(ctx, a_beta, a_kk, a_delta, u_arrow=1.0, beta_note="NEXAFS"):
    """a_*: opacities of the three blocks; u_arrow: 0..1 growth of the KK arrow."""
    x = CX
    # beta block
    y = PY0 + 40
    polyline(ctx, [(x, y - 10), (x + 46, y - 10)], CRIMSON, 6.0, a_beta)
    text(ctx, x + 58, y, "$β$", 40, CRIMSON, a_beta)
    text(ctx, x, y + 40, "measured", 30, INK, 0.92 * a_beta)
    text(ctx, x, y + 74, f"({beta_note})", 27, SLATE, 0.92 * a_beta)
    # KK arrow
    ya, yb = y + 92, y + 150
    if a_kk > 0.01 and u_arrow > 0.01:
        yt = ya + (yb - ya) * u_arrow
        src(ctx, SLATE, 0.9 * a_kk)
        ctx.set_line_width(3.2)
        ctx.move_to(x + 22, ya)
        ctx.line_to(x + 22, yt - 8)
        ctx.stroke()
        arrow_head(ctx, x + 22, yt + 6, math.pi / 2, 16, SLATE, 0.9 * a_kk)
    text(ctx, x + 44, (ya + yb) / 2 - 2, "Kramers-", 26, SLATE, 0.95 * a_kk)
    text(ctx, x + 44, (ya + yb) / 2 + 26, "Kronig", 26, SLATE, 0.95 * a_kk)
    # delta block
    y = yb + 44
    polyline(ctx, [(x, y - 10), (x + 46, y - 10)], BLUE, 5.0, a_delta)
    text(ctx, x + 58, y, "$δ$", 40, BLUE, a_delta)
    text(ctx, x, y + 40, "computed", 30, INK, 0.92 * a_delta)
