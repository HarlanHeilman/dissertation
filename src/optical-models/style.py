"""Shared palette, typography, and drawing primitives for the optical-model hero GIFs.

Palette follows the deck (WSU crimson + Anthropic warm neutrals), matching the
pi-overlap strip and BHJ film figures already in the defense deck.
"""
import math
import cairo

W, H = 1200, 800
FPS = 25


def hexrgb(h, a=1.0):
    h = h.lstrip("#")
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


BG = "#EDE9E7"        # slide background (theme lt2)
IVORY = "#FAF9F5"
INK = "#2E3538"
SLATE = "#5E6A71"
MUTED = "#9FA4A5"
RULE = "#C8C3BE"
CRIMSON = "#981E32"
DEEP = "#6C1524"
CLAY = "#D97757"
RUST = "#B4532F"
BLUE = "#2F5F8F"
SKY = "#6A9BCC"
ICE = "#EAF2FA"
TAUPE = "#C9A99B"
NAVY = "#23476B"

WORD_FONT = "Caladea"
MATH_FONT = "FreeSerif"


def src(ctx, h, a=1.0):
    ctx.set_source_rgba(*hexrgb(h, a))


def lerp(a, b, t):
    return a + (b - a) * t


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ramp(t, t0, t1):
    """0 before t0, 1 after t1, smoothstep between."""
    if t1 == t0:
        return 1.0 if t >= t1 else 0.0
    return smooth((t - t0) / (t1 - t0))


def mix(h1, h2, t, a=1.0):
    c1, c2 = hexrgb(h1), hexrgb(h2)
    return tuple(lerp(c1[i], c2[i], t) for i in range(3)) + (a,)


def new_frame(w=None, h=None):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, w or W, h or H)
    ctx = cairo.Context(surf)
    fo = cairo.FontOptions()
    fo.set_antialias(cairo.ANTIALIAS_GRAY)
    fo.set_hint_style(cairo.HINT_STYLE_NONE)
    fo.set_hint_metrics(cairo.HINT_METRICS_OFF)
    ctx.set_font_options(fo)
    src(ctx, BG)
    ctx.paint()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    return surf, ctx


# ---------------------------------------------------------------- text

def _parse(s):
    """Tiny markup. $...$ toggles math italic (FreeSerif); _{..} subscript; ^{..} superscript;
    \\b toggles bold words. Returns list of (text, math, level, bold)."""
    out, i, math_on, bold = [], 0, False, False
    buf = ""

    def flush(level=0):
        nonlocal buf
        if buf:
            out.append((buf, math_on, level, bold))
            buf = ""

    while i < len(s):
        ch = s[i]
        if ch == "$":
            flush(); math_on = not math_on; i += 1; continue
        if ch == "\\" and s[i + 1:i + 2] == "b":
            flush(); bold = not bold; i += 2; continue
        if ch in "_^" and s[i + 1:i + 2] == "{":
            flush()
            j = s.index("}", i)
            out.append((s[i + 2:j], math_on, -1 if ch == "_" else 1, bold))
            i = j + 1
            continue
        buf += ch
        i += 1
    flush()
    return out


def _face(ctx, mathf, bold, size, italic_words=False):
    if mathf:
        ctx.select_font_face(MATH_FONT, cairo.FONT_SLANT_ITALIC,
                             cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    else:
        ctx.select_font_face(WORD_FONT, cairo.FONT_SLANT_ITALIC if italic_words else cairo.FONT_SLANT_NORMAL,
                             cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)


def _seg_size(size, level, mathf):
    s = size * (0.66 if level else 1.0)
    if mathf:
        s *= 1.08   # FreeSerif runs small next to Caladea
    return s


def text_width(ctx, s, size, italic_words=False):
    w = 0
    for t, m, lvl, b in _parse(s):
        _face(ctx, m, b, _seg_size(size, lvl, m), italic_words)
        w += ctx.text_extents(t).x_advance
    return w


def text(ctx, x, y, s, size=30, color=INK, alpha=1.0, anchor="l", italic_words=False, rotate=0.0):
    """Draw marked-up text with baseline at y. anchor: l, c, r."""
    w = text_width(ctx, s, size, italic_words)
    ctx.save()
    ctx.translate(x, y)
    if rotate:
        ctx.rotate(rotate)
    dx = {"l": 0, "c": -w / 2, "r": -w}[anchor]
    src(ctx, color, alpha)
    for t, m, lvl, b in _parse(s):
        fs = _seg_size(size, lvl, m)
        _face(ctx, m, b, fs, italic_words)
        dy = {0: 0, -1: size * 0.26, 1: -size * 0.40}[lvl]
        ctx.move_to(dx, dy)
        ctx.show_text(t)
        dx += ctx.text_extents(t).x_advance
    ctx.new_path()
    ctx.restore()
    return w


# ---------------------------------------------------------------- primitives

def glow(ctx, x, y, r, color, alpha):
    if alpha <= 0.002:
        return
    ctx.new_path()
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    c = hexrgb(color)
    g.add_color_stop_rgba(0, c[0], c[1], c[2], alpha)
    g.add_color_stop_rgba(0.45, c[0], c[1], c[2], alpha * 0.45)
    g.add_color_stop_rgba(1, c[0], c[1], c[2], 0)
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()


def electron(ctx, x, y, r=9, alpha=1.0):
    if alpha <= 0.01:
        return
    ctx.new_path()
    g = cairo.RadialGradient(x - r * 0.35, y - r * 0.4, 0, x, y, r * 1.05)
    for off, col in ((0, ICE), (0.5, SKY), (1, BLUE)):
        c = hexrgb(col)
        g.add_color_stop_rgba(off, c[0], c[1], c[2], alpha)
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill_preserve()
    src(ctx, NAVY, 0.9 * alpha)
    ctx.set_line_width(1.4)
    ctx.stroke()


def hole(ctx, x, y, r=9, alpha=1.0):
    if alpha <= 0.01:
        return
    ctx.new_path()
    src(ctx, IVORY, 0.85 * alpha)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill_preserve()
    src(ctx, BLUE, 0.9 * alpha)
    ctx.set_line_width(1.6)
    ctx.set_dash([3.2, 2.6])
    ctx.stroke()
    ctx.set_dash([])


def arrow_head(ctx, x, y, ang, size, color, alpha=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.move_to(0, 0)
    ctx.line_to(-size, -size * 0.55)
    ctx.line_to(-size * 0.78, 0)
    ctx.line_to(-size, size * 0.55)
    ctx.close_path()
    src(ctx, color, alpha)
    ctx.fill()
    ctx.restore()


def arrow(ctx, x0, y0, x1, y1, color, width=3.0, head=16, alpha=1.0, both=False, dash=None):
    ang = math.atan2(y1 - y0, x1 - x0)
    L = math.hypot(x1 - x0, y1 - y0)
    if L < 1:
        return
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    sx, sy = x0, y0
    ex, ey = x1 - ux * head * 0.7, y1 - uy * head * 0.7
    if both:
        sx, sy = x0 + ux * head * 0.7, y0 + uy * head * 0.7
    src(ctx, color, alpha)
    ctx.set_line_width(width)
    if dash:
        ctx.set_dash(dash)
    ctx.move_to(sx, sy)
    ctx.line_to(ex, ey)
    ctx.stroke()
    ctx.set_dash([])
    arrow_head(ctx, x1, y1, ang, head, color, alpha)
    if both:
        arrow_head(ctx, x0, y0, ang + math.pi, head, color, alpha)


def wave_packet(ctx, cx, cy, ang, half, wavelength, amp, phase, color=CLAY, alpha=1.0, width=3.2,
                env_power=2.0):
    """Gaussian-enveloped sinusoid centred at (cx,cy) travelling along angle ang."""
    if alpha <= 0.01 or amp <= 0.05:
        return
    ux, uy = math.cos(ang), math.sin(ang)
    px, py = -uy, ux
    n = 140
    pts = []
    k = 2 * math.pi / wavelength
    for i in range(n + 1):
        s = -half + 2 * half * i / n
        env = math.exp(-abs(s / (half * 0.48)) ** env_power)
        off = amp * env * math.sin(k * s - phase)
        pts.append((cx + ux * s + px * off, cy + uy * s + py * off))
    for wdt, a in ((width * 3.2, 0.16), (width, 1.0)):
        src(ctx, color, alpha * a)
        ctx.set_line_width(wdt)
        ctx.move_to(*pts[0])
        for p in pts[1:]:
            ctx.line_to(*p)
        ctx.stroke()


def rounded_rect(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def polyline(ctx, pts, color, width=3.0, alpha=1.0, dash=None):
    if len(pts) < 2:
        return
    src(ctx, color, alpha)
    ctx.set_line_width(width)
    if dash:
        ctx.set_dash(dash)
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.stroke()
    ctx.set_dash([])


def fill_under(ctx, pts, ybase, color, alpha):
    if len(pts) < 2:
        return
    src(ctx, color, alpha)
    ctx.move_to(pts[0][0], ybase)
    for p in pts:
        ctx.line_to(*p)
    ctx.line_to(pts[-1][0], ybase)
    ctx.close_path()
    ctx.fill()


class Axes:
    """Minimal axes: maps data to pixels and draws a baseline with ticks."""

    def __init__(self, x0, y0, x1, y1, xlim, ylim):
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.xlim, self.ylim = xlim, ylim

    def X(self, v):
        return self.x0 + (v - self.xlim[0]) / (self.xlim[1] - self.xlim[0]) * (self.x1 - self.x0)

    def Y(self, v):
        return self.y1 - (v - self.ylim[0]) / (self.ylim[1] - self.ylim[0]) * (self.y1 - self.y0)

    def pts(self, xs, ys):
        return [(self.X(a), self.Y(b)) for a, b in zip(xs, ys)]

    def frame(self, ctx, xticks=(), xlabel=None, ylabel=None, size=34, tick_labels=True, zero=None,
              alpha=1.0):
        src(ctx, SLATE, 0.9 * alpha)
        ctx.set_line_width(3.0)
        ctx.move_to(self.x0, self.y1)
        ctx.line_to(self.x1, self.y1)
        ctx.stroke()
        ctx.move_to(self.x0, self.y1)
        ctx.line_to(self.x0, self.y0)
        ctx.stroke()
        if zero is not None:
            src(ctx, RULE, alpha)
            ctx.set_line_width(1.4)
            ctx.move_to(self.x0, self.Y(zero))
            ctx.line_to(self.x1, self.Y(zero))
            ctx.stroke()
        for v in xticks:
            x = self.X(v)
            src(ctx, SLATE, 0.9 * alpha)
            ctx.set_line_width(3.0)
            ctx.move_to(x, self.y1)
            ctx.line_to(x, self.y1 + 10)
            ctx.stroke()
            if tick_labels:
                text(ctx, x, self.y1 + 44, f"{v:g}", size, SLATE, alpha, "c")
        if xlabel:
            text(ctx, (self.x0 + self.x1) / 2, self.y1 + (88 if tick_labels else 48), xlabel, size,
                 SLATE, alpha, "c")
        if ylabel:
            text(ctx, self.x0 - 18, (self.y0 + self.y1) / 2, ylabel, size, SLATE, alpha, "c",
                 rotate=-math.pi / 2)
