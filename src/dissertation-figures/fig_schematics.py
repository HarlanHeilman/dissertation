"""Line-art schematics for Chapters 1 and 2 (Figs. 1.2, 1.3, 1.4, 2.1, 2.2, 2.4, 2.7)."""
from figlib import *
from matplotlib.patches import Rectangle, Ellipse, Circle, FancyBboxPatch, Arc, Polygon


def box(ax, x, y, w, h, text, fc='white', ec=BLACK, fs=9, bold=False, color=BLACK):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle='round,pad=0.02,rounding_size=0.08',
                                fc=fc, ec=ec, lw=1.1))
    ax.text(x, y, text, ha='center', va='center', fontsize=fs, fontweight='bold' if bold else 'normal', color=color)


def mol(ax, x, y, ang, L=0.5, lw=1.6, c=BLACK):
    dx, dy = L / 2 * np.cos(np.radians(ang)), L / 2 * np.sin(np.radians(ang))
    ax.plot([x - dx, x + dx], [y - dy, y + dy], color=c, lw=lw, solid_capstyle='round')


# ============================================================== 1.2 history
fig = plt.figure(figsize=(11, 5.6))
ax = fig.add_axes([0.02, 0.42, 0.96, 0.55]); blank(ax)
ax.set_xlim(0, 16); ax.set_ylim(-2.6, 2.6)
ev = [
    ('1954', 'Parratt recursion for\nX-ray reflectivity', 0),
    ('1972', 'Berreman 4×4\nanisotropic optics', 0),
    ('1980', 'Névot-Croce\ninterfacial roughness', 0),
    ('1992', 'NEXAFS orientation\nanalysis (Stöhr)', 1),
    ('1999-2000', 'resonant scattering\nat metal L edges', 1),
    ('2005', 'resonant reflectivity\nof low-Z films', 0),
    ('2006', 'carbon K-edge\nRSoXS', 1),
    ('2007', 'first RSoXS\nmaterials study', 1),
    ('2010-2012', 'dedicated RSoXS\nat ALS 11.0.1.2', 1),
    ('2012', 'polarized RSoXS,\nlocal orientation', 1),
    ('2014', 'orientation and\nOPV performance', 1),
    ('2020', 'P-RSoXR orientation\ndepth profiles', 0),
    ('2022', 'ML-clustered DFT\noptical models', 2),
    ('2022-2023', 'buried interfacial\norientation', 0),
    ('2026', 'this work', 2),
]
xs = np.linspace(0.6, 15.4, len(ev))
ax.plot([0.2, 15.8], [0, 0], color=BLACK, lw=1.6)
for k, (yr, txt, kind) in enumerate(ev):
    up = k % 2 == 0
    c = RED if kind in (0, 2) and kind != 1 else BLACK
    c = RED if kind == 0 else (BLACK if kind == 1 else RED)
    y = 0.55 if up else -0.55
    ax.plot([xs[k], xs[k]], [0, y * 0.75], color=c, lw=1.2)
    ax.plot(xs[k], 0, 'o', ms=6, mfc='white' if kind == 1 else c, mec=c, mew=1.4)
    ax.text(xs[k], y + (0.05 if up else -0.05), yr, ha='center', va='bottom' if up else 'top', fontsize=8.5,
            fontweight='bold', color=c)
    ax.text(xs[k], y + (0.5 if up else -0.5), txt, ha='center', va='bottom' if up else 'top', fontsize=7.5,
            color=BLACK, fontweight='bold' if kind == 2 else 'normal')
ax.plot(0.5, -2.35, 'o', ms=6, color=RED); ax.text(0.7, -2.35, 'reflectivity and optical models', color=RED, fontsize=8.5, va='center')
ax.plot(5.0, -2.35, 'o', ms=6, mfc='white', mec=BLACK, mew=1.4); ax.text(5.2, -2.35, 'resonant scattering and spectroscopy', fontsize=8.5, va='center')
ax.text(15.8, -2.35, 'events evenly spaced, not to scale in time', ha='right', fontsize=7.5, color=GRAY, va='center')
label(ax, 'a', x=0.0, y=0.92)

# b geometries
titles = ['transmission RSoXS', 'specular reflectivity', 'grazing incidence']
for k in range(3):
    a = fig.add_axes([0.05 + 0.32 * k, 0.02, 0.27, 0.36]); blank(a)
    a.set_xlim(0, 10); a.set_ylim(0, 6)
    a.text(5, 5.7, titles[k], ha='center', fontsize=9.5)
    if k == 0:
        a.add_patch(Rectangle((3.6, 1.2), 0.35, 3.4, fc=LGRAY, ec=BLACK))
        arrow(a, 0.3, 2.9, 3.55, 2.9)
        a.plot([8.8, 8.8], [0.6, 5.2], color=BLACK, lw=2)
        for r_ in (0.7, 1.4, 2.1):
            a.add_patch(Arc((8.8, 2.9), 0.6 * r_, 2 * r_, theta1=90, theta2=270, color=RED, lw=1.2))
        a.plot([3.95, 8.8], [2.9, 2.9], color=GRAY, lw=0.8, ls='--')
        arrow(a, 3.95, 2.9, 8.7, 4.4, color=RED, lw=1.4)
        a.text(6.6, 3.0, '2θ', fontsize=9, color=RED)
        a.text(9.3, 0.5, 'area\ndetector', fontsize=7.5, ha='center', color=GRAY)
    elif k == 1:
        a.add_patch(Rectangle((1, 0.8), 8, 0.9, fc=LGRAY, ec=BLACK))
        a.add_patch(Rectangle((1, 1.7), 8, 0.5, fc='white', ec=BLACK))
        arrow(a, 1.6, 4.6, 5, 2.2)
        arrow(a, 5, 2.2, 8.4, 4.6)
        a.add_patch(Arc((5, 2.2), 2.4, 2.4, theta1=180 - 35, theta2=180, color=BLACK, lw=1))
        a.add_patch(Arc((5, 2.2), 2.4, 2.4, theta1=0, theta2=35, color=BLACK, lw=1))
        a.text(3.4, 2.35, 'θ', fontsize=9); a.text(6.4, 2.35, 'θ', fontsize=9)
        arrow(a, 5, 2.2, 5, 4.4, color=BLACK, lw=1.4)
        a.text(5.2, 4.2, r'$q_z$', fontsize=10)
        a.text(9.2, 1.95, 'film', fontsize=7.5, va='center', color=GRAY)
    else:
        a.add_patch(Rectangle((1, 1.0), 8, 0.8, fc=LGRAY, ec=BLACK))
        for x in np.arange(1.6, 8.8, 0.6):
            mol(a, x, 2.15, 80, L=0.55, lw=1.3)
        arrow(a, 0.6, 2.9, 4.8, 2.45)
        arrow(a, 5.0, 2.45, 9.0, 3.0, color=GRAY, lw=1.2)
        arrow(a, 5.0, 2.45, 8.4, 5.0, color=RED, lw=1.4)
        arrow(a, 5.0, 2.45, 9.2, 4.0, color=RED, lw=1.4)
        a.text(5.6, 4.9, 'diffraction', fontsize=7.5, color=RED)
    label(a, 'b' if k == 0 else '', x=-0.05, y=0.95)
save(fig, 'fig1-02_history')

# ============================================================== 1.3 TDM
fig = plt.figure(figsize=(10.5, 3.6))
a = fig.add_axes([0.02, 0.05, 0.28, 0.85]); blank(a); a.set_xlim(0, 6); a.set_ylim(0, 6)
mol(a, 2.6, 2.8, 0, L=3.4, lw=4.5)
arrow(a, 2.6, 2.8, 2.6, 5.2); arrow(a, 2.6, 2.8, 2.6, 0.4)
a.text(2.8, 5.0, r'$\mu_{\pi^*}$', color=RED, fontsize=11)
arrow(a, 2.6, 2.8, 5.4, 2.8, color=RED, lw=1.3)
a.text(4.6, 2.35, r'$\mu_{\sigma^*}$', color=RED, fontsize=10)
arrow(a, 2.6, 2.8, 4.1, 4.9, color=BLACK, lw=1.6)
a.text(4.15, 4.95, r'$\mathbf{E}$', fontsize=11)
a.add_patch(Arc((2.6, 2.8), 2.0, 2.0, theta1=54, theta2=90, color=BLACK, lw=1))
a.text(2.85, 4.0, r'$\Theta$', fontsize=10)
a.text(0.6, 3.05, 'ZnPc\nmacrocycle', fontsize=8, color=GRAY, va='bottom')
label(a, 'a', x=0.0, y=0.98)
# b angular dependence
b = fig.add_axes([0.38, 0.2, 0.25, 0.68])
th = np.linspace(0, 90, 200)
b.plot(th, np.cos(np.radians(th)) ** 2, color=RED, label=r'$I\propto\cos^2\Theta$')
b.plot(th, np.sin(np.radians(th)) ** 2, color=BLACK, ls='--', label=r'$\sin^2\Theta$')
b.axvline(54.7, color=GRAY, lw=0.8, ls=':'); b.text(56, 0.9, 'magic\nangle', fontsize=7.5, color=GRAY, va='top')
b.set_xlabel(r'Angle $\Theta$ between $\mathbf{E}$ and $\mu$ (°)'); b.set_ylabel('Relative absorption')
b.set_xlim(0, 90); b.set_ylim(0, 1.05); b.legend(loc='center right', fontsize=8.5)
label(b, 'b', x=-0.3)
# c edge-on vs face-on films with s and p
c = fig.add_axes([0.69, 0.05, 0.3, 0.85]); blank(c); c.set_xlim(0, 7); c.set_ylim(0, 6)
for row, (name, ang, ys) in enumerate((('edge-on', 80, 3.6), ('face-on', 5, 0.7))):
    c.add_patch(Rectangle((0.3, ys - 0.25), 3.4, 0.25, fc=LGRAY, ec=BLACK, lw=0.8))
    for x in np.arange(0.6, 3.6, 0.45):
        for dy in (0.25, 0.75, 1.25):
            mol(c, x, ys + dy, ang, L=0.38, lw=1.4)
    c.text(2.0, ys + 1.75, name, ha='center', fontsize=9)
    # absorption bars at the pi* resonance for s (E in plane) and p (E near normal at grazing)
    s_val, p_val = (0.95, 0.12) if row == 0 else (0.1, 0.9)
    for k, (lab, v) in enumerate((('s', s_val), ('p', p_val))):
        c.add_patch(Rectangle((4.5 + 0.9 * k, ys), 0.6, 1.5 * v, fc=RED if k == 0 else 'white', ec=RED, lw=1.4))
        c.text(4.8 + 0.9 * k, ys - 0.35, lab, ha='center', fontsize=9)
    c.text(5.25, ys + 1.75, r'$\pi^*$ absorption', ha='center', fontsize=8)
label(c, 'c', x=0.0, y=0.98)
save(fig, 'fig1-03_transition-dipoles')

# ============================================================== 1.4 roadmap
fig, ax = plt.subplots(figsize=(10.5, 3.8)); blank(ax); ax.set_xlim(0, 12); ax.set_ylim(0, 5.4)
box(ax, 1.3, 2.7, 2.2, 1.2, 'Chapter 1\nintroduction\nQ1 to Q4', fs=8.5)
box(ax, 4.2, 2.7, 2.6, 1.6, 'Chapter 2\nfundamentals and methods\nof polarized resonant\nsoft X-ray reflectivity', fs=8.5)
box(ax, 7.5, 4.2, 2.6, 1.3, 'Chapter 3\nsub-monolayer interfacial\nstate (Q1, Q2)', fs=8.5, ec=RED)
box(ax, 7.5, 2.1, 2.6, 1.3, 'Chapter 4\nindividual resonances\nwith depth (Q3, Q4)', fs=8.5, ec=RED)
box(ax, 4.2, 0.6, 2.6, 0.9, 'Chapter 5  X-ray Atlas\nreusable optical constants', fs=8.5)
box(ax, 10.7, 3.15, 2.0, 1.3, 'Chapter 6\nconclusion and\noutlook', fs=8.5)
for (x0, y0, x1, y1) in ((2.4, 2.7, 2.9, 2.7), (5.5, 3.1, 6.2, 4.0), (5.5, 2.4, 6.2, 2.2), (8.8, 4.0, 9.7, 3.4),
                         (8.8, 2.2, 9.7, 2.9), (7.5, 3.55, 7.5, 2.75)):
    arrow(ax, x0, y0, x1, y1, color=RED, lw=1.6)
arrow(ax, 5.5, 0.6, 6.4, 1.45, color=GRAY, lw=1.2)
ax.text(6.55, 0.75, 'reference spectra for\nChapters 3 and 4', fontsize=7.5, color=GRAY)
ax.text(7.65, 3.05, 'optical model', fontsize=7.5, color=RED)
save(fig, 'fig1-04_roadmap')

# ============================================================== 2.1 geometry
fig = plt.figure(figsize=(10.5, 3.3))
a = fig.add_axes([0.0, 0.05, 0.48, 0.88]); blank(a); a.set_xlim(0, 10); a.set_ylim(0, 5.5)
for x in (0.6, 1.0, 1.4, 1.8):
    a.plot([x, x], [1.3, 4.3], color=BLACK, lw=1.2)
a.text(0.9, 4.6, r'$\mathbf{k}$', fontsize=11)
a.add_patch(Circle((4.0, 2.8), 0.75, fc='#7F7F7F', ec=BLACK))
for xx, yy in np.random.default_rng(1).uniform(-0.55, 0.55, (25, 2)):
    if xx * xx + yy * yy < 0.4:
        a.plot(4.0 + xx, 2.8 + yy, '.', color='white', ms=2)
arrow(a, 0.2, 2.8, 4.0, 2.8)
a.plot([4.0, 8.8], [2.8, 2.8], color=GRAY, lw=0.8, ls='--')
arrow(a, 4.0, 2.8, 8.8, 4.6)
a.plot([8.9, 8.9], [0.8, 5.0], color=BLACK, lw=1.6)
a.add_patch(Arc((4.0, 2.8), 3.0, 3.0, theta1=0, theta2=20.5, color=BLACK, lw=1))
a.text(5.65, 3.0, '2θ', fontsize=10)
a.text(7.6, 4.75, r"$\mathbf{k}'$", fontsize=11)
arrow(a, 4.0, 2.8, 3.4, 4.3, color=RED, lw=1.8)
a.text(3.0, 4.35, r"$\mathbf{q}=\mathbf{k}'-\mathbf{k}$", fontsize=9.5, color=RED)
a.text(5.0, 0.35, r'$|\mathbf{q}|=\frac{4\pi}{\lambda}\sin\theta$', fontsize=10.5, ha='center')
a.text(1.2, 0.8, r'$E_0=e^{ikz}$', fontsize=10, ha='center')
a.text(9.1, 0.6, 'far field', fontsize=8, color=GRAY)
label(a, 'a', x=0.0, y=0.98)
b = fig.add_axes([0.52, 0.05, 0.48, 0.88]); blank(b); b.set_xlim(0, 10); b.set_ylim(0, 5.5)
b.add_patch(Rectangle((0.5, 0.5), 9, 1.1, fc=LGRAY, ec=BLACK))
b.add_patch(Rectangle((0.5, 1.6), 9, 0.8, fc='white', ec=BLACK))
b.text(9.3, 2.0, 'film', ha='right', va='center', fontsize=8, color=GRAY)
b.text(9.3, 1.05, 'substrate', ha='right', va='center', fontsize=8, color=GRAY)
arrow(b, 1.3, 4.9, 5.0, 2.4); arrow(b, 5.0, 2.4, 8.7, 4.9)
b.text(2.2, 4.0, r'$\mathbf{k}_i$', fontsize=11); b.text(7.7, 4.0, r'$\mathbf{k}_f$', fontsize=11)
b.add_patch(Arc((5.0, 2.4), 2.6, 2.6, theta1=146, theta2=180, color=BLACK, lw=1))
b.add_patch(Arc((5.0, 2.4), 2.6, 2.6, theta1=0, theta2=34, color=BLACK, lw=1))
b.text(3.3, 2.55, 'θ', fontsize=10); b.text(6.55, 2.55, 'θ', fontsize=10)
arrow(b, 5.0, 2.4, 5.0, 4.9, color=RED, lw=1.8)
b.text(5.2, 4.6, r'$q_z=\frac{4\pi}{\lambda}\sin\theta$', fontsize=10, color=RED)
b.plot([5.0, 5.0], [0.5, 2.4], color=GRAY, lw=0.8, ls=':')
b.text(0.7, 3.4, 's, E normal to the plane of incidence\np, E in the plane of incidence', fontsize=8, color=GRAY, va='top')
label(b, 'b', x=0.0, y=0.98)
save(fig, 'fig2-01_scattering-geometry')

# ============================================================== 2.2 Fraunhofer
fig = plt.figure(figsize=(10.5, 3.5))
a = fig.add_axes([0.0, 0.08, 0.42, 0.85]); blank(a); a.set_xlim(0, 10); a.set_ylim(0, 5)
a.add_patch(Rectangle((1.6, 2.0), 0.25, 1.0, fc='#7F7F7F', ec=BLACK))
a.annotate('', xy=(1.35, 2.0), xytext=(1.35, 3.0), arrowprops=dict(arrowstyle='<->', lw=1))
a.text(1.35, 3.25, 'a', fontsize=11, ha='center', va='center', style='italic')
arrow(a, 0.1, 2.5, 1.55, 2.5)
a.text(0.3, 2.75, 'λ', fontsize=11)
for k, r_ in enumerate((0.7, 1.3, 1.9)):
    a.add_patch(Arc((1.85, 2.5), r_, 1.6 * r_, theta1=-60, theta2=60, color=BLACK, lw=1))
a.plot([9.3, 9.3], [0.6, 4.4], color=BLACK, lw=2)
xx = np.linspace(0.8, 4.2, 300)
a.plot(9.3 - 0.9 * np.sinc((xx - 2.5) * 1.6) ** 2, xx, color=RED, lw=1.6)
a.annotate('', xy=(1.85, 0.6), xytext=(9.3, 0.6), arrowprops=dict(arrowstyle='<->', lw=1))
a.text(5.6, 0.25, 'L', fontsize=11, ha='center', style='italic')
a.text(3.4, 4.6, r'Fresnel number  $F=a^2/(L\lambda)$', fontsize=10)
a.text(2.6, 3.6, r'near field, $F\gtrsim1$', fontsize=8.5, color=GRAY)
a.text(6.0, 3.6, r'far field, $F\ll1$', fontsize=8.5, color=RED)
label(a, 'a', x=0.0, y=0.98)
b = fig.add_axes([0.53, 0.18, 0.44, 0.72])
E = 284.0; lmb = lam(E) * 1e-10
aa = np.logspace(-10, -3, 300)
for L, c, ls in ((0.1, GRAY, '--'), (0.5, BLACK, '-')):
    b.loglog(aa, aa ** 2 / (L * lmb), color=c, ls=ls, label=f'L = {L} m')
b.axhline(1, color=RED, lw=1.2)
b.axhspan(1, 1e8, color=LRED, alpha=0.35, lw=0)
marks = [(0.34e-9, 'π stack'), (1.45e-9, 'ZnPc'), (19.3e-9, 'film t'), (1e-7, '100 nm\ndomains')]
for x, t in marks:
    b.axvline(x, color=GRAY, lw=0.7, ls=':')
    b.text(x * 1.15, 1e-17, t, fontsize=7.5, rotation=90, va='bottom', color=GRAY)
astar = np.sqrt(0.5 * lmb)
b.plot(astar, 1, 'o', color=RED, ms=5)
b.text(astar * 0.4, 30, rf'$a^*=\sqrt{{L\lambda}}\approx{astar*1e6:.0f}$ µm', fontsize=8.5, color=RED, ha='right')
b.set_xlim(1e-10, 1e-3); b.set_ylim(1e-18, 1e6)
b.set_xlabel('Scatterer size a (m)'); b.set_ylabel('F'); b.legend(loc='lower right')
b.text(2e-10, 1e3, 'near field', fontsize=8.5, color=RED)
label(b, 'b', x=-0.18)
save(fig, 'fig2-02_fraunhofer')

# ============================================================== 2.4 states
fig = plt.figure(figsize=(10.5, 3.6))
a = fig.add_axes([0.02, 0.08, 0.27, 0.85]); blank(a); a.set_xlim(0, 6); a.set_ylim(-0.5, 6.2)
a.plot([0.8, 5.2], [5.6, 5.6], color=GRAY, lw=1, ls='--'); a.text(5.3, 5.6, 'vacuum', va='center', fontsize=8, color=GRAY)
for y, t in ((4.9, r'$\pi^*$ (LUMO)'), (4.55, r'$\pi^*$'), (3.9, r'$\sigma^*$')):
    a.plot([2.2, 4.2], [y, y], color=BLACK, lw=1.6); a.text(4.35, y, t, va='center', fontsize=8.5)
a.plot([2.2, 4.2], [0.6, 0.6], color=BLACK, lw=2.2); a.text(4.35, 0.6, 'C 1s', va='center', fontsize=9)
a.plot([2.7, 3.7], [0.6, 0.6], 'o', color=BLACK, ms=4)
arrow(a, 3.0, 0.7, 3.0, 4.82, color=RED, lw=2)
a.text(2.85, 2.6, r'$h\nu\approx285$ eV', fontsize=9, color=RED, ha='right')
a.plot([1.0, 1.0], [0.3, 5.3], color=BLACK, lw=0.8); a.text(0.8, 2.9, 'energy', rotation=90, va='center', fontsize=8.5)
label(a, 'a', x=0.0, y=0.98)
b = fig.add_axes([0.33, 0.08, 0.38, 0.85]); blank(b); b.set_xlim(0, 8); b.set_ylim(0, 6)
# ring of carbons, side view projection, with p-orbital lobes above and below
xs_ = np.linspace(1.0, 7.0, 7)
b.plot(xs_, np.full_like(xs_, 3.0), color=BLACK, lw=1.4)
b.plot(xs_, np.full_like(xs_, 3.0), 'o', ms=6, mfc='white', mec=BLACK)
for k, x in enumerate(xs_):
    up_red = k % 2 == 0
    b.add_patch(Ellipse((x, 3.75), 0.55, 1.2, fc=RED if up_red else 'white', ec=RED, lw=1.1, alpha=0.9))
    b.add_patch(Ellipse((x, 2.25), 0.55, 1.2, fc='white' if up_red else RED, ec=RED, lw=1.1, alpha=0.9))
b.add_patch(Circle((xs_[2], 3.0), 0.16, fc=BLACK, zorder=5))
b.text(xs_[2], 0.9, 'C 1s localized\non one atom', ha='center', fontsize=8.5)
b.annotate('', xy=(xs_[2], 2.85), xytext=(xs_[2], 1.4), arrowprops=dict(arrowstyle='-|>', color=BLACK, lw=1))
b.text(7.6, 4.9, r'$\pi^*$ delocalized over the ring', ha='right', fontsize=8.5, color=RED)
label(b, 'b', x=0.0, y=0.98)
c = fig.add_axes([0.75, 0.08, 0.24, 0.85]); blank(c); c.set_xlim(0, 5); c.set_ylim(0, 6)
mol(c, 2.5, 3.0, 0, L=3.2, lw=4)
arrow(c, 2.5, 3.0, 2.5, 5.2); arrow(c, 2.5, 3.0, 2.5, 0.8)
c.text(2.7, 5.0, r'$\mu_{if}=\langle f|\mathbf{r}|i\rangle$', fontsize=9.5, color=RED)
c.text(2.5, 0.25, r'$\Gamma_{i\to f}\propto|\langle f|\mathbf{e}\cdot\mathbf{r}|i\rangle|^2$', fontsize=9.5, ha='center')
label(c, 'c', x=0.0, y=0.98)
save(fig, 'fig2-04_initial-final-states')

# ============================================================== 2.7 alignment
fig, axs = plt.subplots(1, 4, figsize=(11, 2.8)); fig.subplots_adjust(wspace=0.42)
z = np.linspace(-1.0, 1.0, 300)
I = 0.5 * (1 - erf(z / 0.25))
a = axs[0]; a.plot(z, I, color=BLACK); a.axhline(0.5, color=GRAY, ls=':', lw=0.8); a.axvline(0, color=RED, lw=1.2)
a.text(0.05, 0.55, r'$z_0$, half intensity', color=RED, fontsize=8)
a.set_xlabel('Sample z (mm)'); a.set_ylabel('Photodiode signal'); a.set_title('knife edge', fontsize=9)
th = np.linspace(-1, 1, 400)
direct = 0.5 * (1 + erf((th + 0.25) / 0.12)) * 0.5 + 0.5 * (th < 0) * 0
refl = np.where((th > 0) & (th < 0.55), 0.5 * (1 - np.exp(-th / 0.08)), 0) * (th < 0.55)
sig = np.where(th < 0, 0.5 * (1 + erf((th + 0.25) / 0.12)) * 0.5, 0.5 * (1 - 0.0)) * 1.0
sig = np.where(th < 0, 0.25 * (1 + erf((th + 0.25) / 0.12)), 0.5 + refl * 0.6)
sig = np.where(th > 0.55, 0.5 * np.exp(-(th - 0.55) / 0.01) + 0.0, sig)
sig = np.where(th > 0.55, 0.02, sig)
a = axs[1]; a.plot(th, sig, color=BLACK); a.axvline(0, color=RED, lw=1.2)
a.text(-0.95, 0.75, 'blocked', fontsize=7.5, color=GRAY); a.text(0.1, 0.42, 'reflected\nonto diode', fontsize=7.5, color=GRAY)
a.text(0.6, 0.15, 'cliff', fontsize=7.5, color=GRAY)
a.set_xlabel(r'$\theta_s$ (°)'); a.set_title('rocking scan, flat geometry', fontsize=9)
t2 = np.linspace(0, 2, 300)
a = axs[2]; a.plot(t2, np.exp(-0.5 * ((t2 - 1.02) / 0.05) ** 2), color=BLACK); a.axvline(1.0, color=RED, lw=1.2)
a.annotate('', xy=(1.02, 0.5), xytext=(1.0, 0.5), arrowprops=dict(arrowstyle='<->', lw=0.8))
a.text(1.1, 0.6, r'offset in $\theta_s$', fontsize=7.5, color=GRAY)
a.set_xlabel(r'$\theta_s$ (°), $\theta_d=2°$'); a.set_title(r'$\theta$-2$\theta$ check', fontsize=9)
it = np.arange(1, 7)
a = axs[3]; a.semilogy(it, 0.4 * 0.3 ** (it - 1), 'o-', color=BLACK, label=r'$|\Delta z|$ (mm)')
a.semilogy(it, 0.5 * 0.35 ** (it - 1), 's--', color=RED, label=r'$|\Delta\theta_s|$ (°)')
a.set_xlabel('Iteration'); a.legend(fontsize=8); a.set_title('convergence', fontsize=9)
for k, x in enumerate(axs):
    label(x, 'abcd'[k], x=-0.28)
    if k < 3:
        x.set_yticks([])
save(fig, 'fig2-07_alignment')
