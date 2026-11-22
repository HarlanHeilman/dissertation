"""Figs. 5.2, 5.3, 5.4, 5.9 and the Fig. 4.4 e-g preview."""
import json
from figlib import *
_save = save
def save(fig, name):
    if name in ('fig5-03_angle-convention', 'fig5-09_architecture', 'fig4-04efg_preview'):
        plt.close(fig); return  # superseded by fig_v2_ch5.py or vetoed
    _save(fig, name)
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon, Arc


def box(ax, x, y, w, h, text, ec=BLACK, fs=8.5, fc='white'):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle='round,pad=0.02,rounding_size=0.1',
                                fc=fc, ec=ec, lw=1.1))
    ax.text(x, y, text, ha='center', va='center', fontsize=fs)


# ================================================================ 5.2 normalization
bb, nx, mu = znpc_tables()
pre, post = (270.0, 282.0), (320.0, 330.0)
fig, axs = plt.subplots(2, 2, figsize=(6.5, 4.9)); fig.subplots_adjust(wspace=0.36, hspace=0.5, left=0.1, right=0.98, top=0.94, bottom=0.09); axs = axs.ravel()
thetas = sorted(nx.theta_deg.unique())
for th in thetas:
    d = nx[nx.theta_deg == th]
    E, raw = d.energy.values, d.intensity_raw.values
    c = RED if th == 20 else (BLACK if th == 90 else LGRAY)
    lw = 1.4 if th in (20, 90) else 0.9
    if th == 54.7:
        axs[0].plot(E, raw, color=BLACK, lw=1.2)
    pm = raw[(E >= pre[0]) & (E <= pre[1])].mean(); qm = raw[(E >= post[0]) & (E <= post[1])].mean()
    axs[1].plot(E, (raw - pm) / (qm - pm), color=c, lw=lw, label=f'{th:g}°' if th in (20, 90) else None)
for a in axs[:3]:
    a.axvspan(*pre, color=LGRAY, alpha=0.5, lw=0); a.axvspan(*post, color=LGRAY, alpha=0.5, lw=0)
axs[0].set_ylabel('TEY (arb.)'); axs[0].set_title('Raw TEY, θ = 54.7°', fontsize=8)
axs[1].set_ylabel('Normalized'); axs[1].set_title('Normalized 0 to 1, all θ', fontsize=8); axs[1].legend(fontsize=7.5, loc='upper right')
d = nx[nx.theta_deg == 54.7]
E = d.energy.values
axs[2].plot(E, d.intensity_norm.values / 1e3, color=BLACK, lw=1.2, label='ZnPc')
axs[2].plot(E, np.interp(E, mu.energy, mu.mu) / 1e3, color=RED, ls='--', lw=1.2, label='bare atom')
axs[2].set_ylabel(r'$\mu_m$ ($10^3$ cm$^2$ g$^{-1}$)'); axs[2].set_title('Bare-atom normalized', fontsize=8)
axs[2].legend(fontsize=7.5, loc='upper right')
Ee = np.linspace(270, 330, 601)
n = znpc_index(Ee)
b_iso = (2 * n['xx'].imag + n['zz'].imag) / 3; d_iso = (2 * (1 - n['xx'].real) + (1 - n['zz'].real)) / 3
axs[3].plot(Ee, b_iso * 1e3, color=BLACK, label=r'$\beta$'); axs[3].plot(Ee, d_iso * 1e3, color=RED, label=r'$\delta$')
axs[3].axhline(0, color=LGRAY, lw=0.8)
axs[3].set_ylabel(r'$\beta$, $\delta$ ($\times10^{-3}$)'); axs[3].set_title(r'Optical constants, $\rho$ = 1.64 g cm$^{-3}$', fontsize=8)
axs[3].legend(fontsize=7.5)
for k, a in enumerate(axs):
    a.set_xlabel('Photon energy (eV)'); a.set_xlim(270, 330)
grid_labels(fig, [[(axs[0], 'a'), (axs[1], 'b')], [(axs[2], 'c'), (axs[3], 'd')]])
save(fig, 'fig5-02_normalization')

# ================================================================ 5.3 angles
fig = plt.figure(figsize=(9.5, 3.6))
ax = fig.add_axes([0.0, 0.0, 0.5, 1.0]); blank(ax); ax.set_xlim(0, 10); ax.set_ylim(0, 7.5)
P = np.array([[1.0, 1.4], [6.4, 1.4], [8.8, 3.2], [3.4, 3.2]])
ax.add_patch(Polygon(P, fc=LGRAY, ec=BLACK, lw=1.1))
o = np.array([4.9, 2.3])
arrow(ax, *o, 4.9, 6.9, color=BLACK, lw=1.4); ax.text(5.05, 6.8, r'$\hat{n}$ (sample normal)', fontsize=8)
arrow(ax, *o, 7.6, 2.3, color=BLACK, lw=1.2); ax.text(7.7, 2.05, r'$\hat{x}$', fontsize=8.5)
E_tip = o + np.array([2.2, 3.4])
arrow(ax, *o, *E_tip, color=RED, lw=2.2); ax.text(E_tip[0] + 0.1, E_tip[1], r'$\mathbf{E}$', fontsize=10, color=RED)
proj = o + np.array([2.2, 0.75])
ax.plot([E_tip[0], proj[0]], [E_tip[1], proj[1]], color=GRAY, ls=':', lw=1)
ax.plot([o[0], proj[0]], [o[1], proj[1]], color=GRAY, ls='--', lw=1)
ax.add_patch(Arc(o, 2.2, 3.2, theta1=57, theta2=90, color=RED, lw=1.2)); ax.text(5.25, 4.0, 'θ', fontsize=9.5, color=RED)
ax.add_patch(Arc(o, 3.0, 1.0, theta1=0, theta2=20, color=RED, lw=1.2)); ax.text(6.55, 2.45, 'φ', fontsize=9.5, color=RED)
ax.text(1.2, 0.6, 'θ, polar angle of E from the sample normal\nφ, azimuth of E in the sample plane', fontsize=7.5, color=GRAY)
label(ax, 'a', x=0.0, y=0.97)
def proj(v):
    x, y, z = v
    return np.array([x * 0.95 - y * 0.55, z * 1.0 + y * 0.32 + x * 0.12])
for k, (th, ph) in enumerate(((90, 45), (45, 90))):
    a = fig.add_axes([0.55 + 0.23 * k, 0.1, 0.2, 0.75]); blank(a); a.set_xlim(-1.6, 1.6); a.set_ylim(-1.0, 1.9)
    corners = [proj(v) for v in ((-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0))]
    a.add_patch(Polygon(corners, fc=LGRAY, ec=BLACK, lw=1.0))
    o2 = proj((0, 0, 0))
    for v, c in (((1.2, 0, 0), GRAY), ((0, 0, 1.4), BLACK)):
        e = proj(v); arrow(a, *o2, *e, color=c, lw=1.2)
    a.text(*proj((1.3, 0, 0)), 'x', fontsize=7.5, color=GRAY); a.text(*(proj((0, 0, 1.45)) + [0.08, 0]), 'n', fontsize=7.5)
    t, p = np.radians(th), np.radians(ph)
    e = proj((1.3 * np.sin(t) * np.cos(p), 1.3 * np.sin(t) * np.sin(p), 1.3 * np.cos(t)))
    arrow(a, *o2, *e, color=RED, lw=2.2)
    a.text(0, -0.95, f'(θ, φ) = ({th}°, {ph}°)', ha='center', fontsize=8)
    if k == 0:
        a.text(-1.6, 1.85, 'b', fontsize=11, fontweight='bold', va='top')
save(fig, 'fig5-03_angle-convention')

# ================================================================ 5.4 contribution workflow
fig, ax = plt.subplots(figsize=(6.5, 4.3)); fig.subplots_adjust(0, 0, 1, 1); blank(ax)
ax.set_xlim(0, 13); ax.set_ylim(0, 8.6)
FS = 7.5
W, H = 3.0, 1.25
X = (2.0, 6.5, 11.0)
Y = (7.7, 5.5, 3.3, 1.1)
# row 1, left to right
r1 = ['ORCID\nsign in', 'molecule\nInChI, SMILES,\nCAS, PubChem', 'sample\nprocessing route']
for x, t in zip(X, r1):
    box(ax, x, Y[0], W, H, t, fs=FS)
for k in range(2):
    arrow(ax, X[k] + W / 2, Y[0], X[k + 1] - W / 2, Y[0], color=BLACK, lw=1.1, hw=4)
# row 2, right to left, ending at the validation gate
box(ax, X[2], Y[1], W, H, 'experiment\nfacility, edge,\nmode, geometry', fs=FS)
box(ax, X[1], Y[1], W, H, 'CSV traces\ncolumn mapping', fs=FS)
gate = np.array([[X[0], Y[1] + 0.8], [X[0] + 1.5, Y[1]], [X[0], Y[1] - 0.8], [X[0] - 1.5, Y[1]]])
ax.add_patch(Polygon(gate, fc='white', ec=RED, lw=1.3))
ax.text(X[0], Y[1], 'structural\nvalidation', ha='center', va='center', fontsize=FS)
arrow(ax, X[2], Y[0] - H / 2, X[2], Y[1] + H / 2, color=BLACK, lw=1.1, hw=4)
arrow(ax, X[2] - W / 2, Y[1], X[1] + W / 2, Y[1], color=BLACK, lw=1.1, hw=4)
arrow(ax, X[1] - W / 2, Y[1], X[0] + 1.5, Y[1], color=BLACK, lw=1.1, hw=4)
ax.annotate('', xy=(X[1] - 0.6, Y[1] - H / 2), xytext=(X[0] + 0.4, Y[1] - 0.65),
            arrowprops=dict(arrowstyle='-|>', color=RED, lw=1.1, connectionstyle='arc3,rad=0.35'))
ax.text(X[1] - 0.25, Y[1] - 1.0, 'errors returned, nothing stored', ha='left', va='center', fontsize=7, color=RED)
# row 3, left to right
arrow(ax, X[0], Y[1] - 0.8, X[0], Y[2] + H / 2, color=BLACK, lw=1.1, hw=4)
ax.text(X[0] + 0.15, (Y[1] - 0.8 + Y[2] + H / 2) / 2, 'pass', fontsize=7, va='center')
r3 = ['derive OD,\nmass absorption,\nβ, δ (Kramers-Kronig)', 'quality metrics\nresolution, SNR,\nnormalization',
      'revision 1.0.0\nchecksum of\nderived columns']
for x, t in zip(X, r3):
    box(ax, x, Y[2], W + (0.3 if x == X[0] else 0), H, t, fs=FS)
arrow(ax, X[0] + W / 2 + 0.15, Y[2], X[1] - W / 2, Y[2], color=BLACK, lw=1.1, hw=4)
arrow(ax, X[1] + W / 2, Y[2], X[2] - W / 2, Y[2], color=BLACK, lw=1.1, hw=4)
# row 4, right to left
box(ax, X[2], Y[3], W, H, 'Zenodo deposit\nversioned DOI', fs=FS)
box(ax, X[1], Y[3], W, H, 'public dataset\nd/<tag>', fs=FS)
arrow(ax, X[2], Y[2] - H / 2, X[2], Y[3] + H / 2, color=BLACK, lw=1.1, hw=4)
arrow(ax, X[2] - W / 2, Y[3], X[1] + W / 2, Y[3], color=BLACK, lw=1.1, hw=4)
ax.annotate('', xy=(X[0], Y[2] - H / 2), xytext=(X[1] - W / 2, Y[3]),
            arrowprops=dict(arrowstyle='-|>', color=GRAY, lw=1.0, ls='--', connectionstyle='arc3,rad=-0.3'))
ax.text(X[0] - 0.2, Y[3] - 0.05, 'renormalization,\nnew revision', ha='center', va='center', fontsize=7, color=GRAY)
save(fig, 'fig5-04_contribution-workflow')

# ================================================================ 5.9 architecture
fig = plt.figure(figsize=(11, 4.2))
ax = fig.add_axes([0.0, 0.0, 0.62, 1.0]); blank(ax); ax.set_xlim(0, 13); ax.set_ylim(0, 8)
box(ax, 2.0, 6.6, 3.0, 1.1, 'PostgreSQL\nrecords and revisions')
box(ax, 2.0, 4.6, 3.0, 1.1, 'storage bucket\nauxiliary files, tensors')
box(ax, 2.0, 2.6, 3.0, 1.1, 'Zenodo\nversioned DOIs')
box(ax, 6.5, 5.6, 3.0, 1.4, 'web application\ntRPC procedures\nvisibility, review')
box(ax, 6.5, 3.0, 3.0, 1.1, 'REST /api/v1\nOpenAPI', ec=RED)
box(ax, 11.1, 6.6, 2.8, 1.0, 'browser')
box(ax, 11.1, 4.6, 2.8, 1.0, 'Python xrayatlas', ec=RED)
box(ax, 11.1, 2.6, 2.8, 1.0, 'CLI xatlas', ec=RED)
box(ax, 6.5, 0.9, 3.0, 0.9, 'ORCID sign in, tokens')
for (x0, y0, x1, y1) in ((3.5, 6.6, 5.0, 5.9), (3.5, 4.6, 5.0, 5.3), (3.5, 2.6, 5.0, 2.9), (8.0, 5.9, 9.7, 6.6),
                         (6.5, 4.9, 6.5, 3.55), (8.0, 3.2, 9.7, 4.5), (8.0, 2.9, 9.7, 2.6), (6.5, 1.35, 6.5, 2.45)):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle='<|-|>', color=BLACK, lw=1.1))
ax.text(9.6, 0.9, 'one credential file\nshared by both clients', fontsize=7, color=GRAY)
label(ax, 'a', x=0.0, y=0.98)
b = fig.add_axes([0.64, 0.02, 0.36, 0.94]); blank(b); b.set_xlim(0, 8); b.set_ylim(0, 8)
box(b, 1.6, 6.8, 2.6, 1.0, 'dataset\nrevision 1.0.2')
box(b, 1.6, 4.7, 2.6, 1.0, 'default model\nm/<tag> v1')
box(b, 5.6, 5.9, 2.6, 0.9, 'fork A  v1, v2', ec=RED)
box(b, 5.6, 3.6, 2.6, 0.9, 'fork B  v1', ec=RED)
box(b, 1.6, 2.3, 2.6, 1.0, 'default model v2\nmerged from fork A')
box(b, 5.6, 1.3, 2.6, 1.0, 'citation\nmodel + datasets\n+ ancestors')
for (x0, y0, x1, y1, c) in ((1.6, 6.3, 1.6, 5.2, BLACK), (2.9, 4.9, 4.3, 5.8, RED), (2.9, 4.5, 4.3, 3.7, RED),
                            (4.3, 5.6, 2.9, 2.6, GRAY), (1.6, 4.2, 1.6, 2.8, BLACK), (2.9, 2.0, 4.3, 1.4, BLACK)):
    arrow(b, x0, y0, x1, y1, color=c, lw=1.3)
b.text(3.3, 5.75, 'fork', fontsize=7, color=RED); b.text(4.05, 2.7, 'merge\nproposal', fontsize=7, color=GRAY)
b.text(0.2, 7.6, 'pinned', fontsize=7, color=GRAY)
label(b, 'b', x=0.0, y=0.99)
save(fig, 'fig5-09_architecture')

# ================================================================ 4.4 e-g preview
s = json.load(open(f'{DATA}/sos.json'))
L, tv, ts_ = 192.7, 13.0, 14.9
z = np.linspace(0, L, 300)
def prof(v_, b_, s_):
    return b_ + (v_ - b_) * np.exp(-z / tv) + (s_ - b_) * np.exp(-(L - z) / ts_)
rho = prof(s['density_vac'], s['density_bulk'], s['density_si'])
gam = np.degrees(prof(s['alpha_vac'], s['alpha_bulk'], s['alpha_si']))
labs = s['peak_labels']
fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.0)); fig.subplots_adjust(wspace=0.38)
styles = {'pk0': (BLACK, '-'), 'pk1': (RED, '-'), 'pk5': (GRAY, '-'), 'pk9': (RED, '--')}
energies = {'pk0': 284.2, 'pk1': 285.1, 'pk5': 287.1, 'pk9': 288.9}
for p in s['free_labels']:
    i = labs.index(p); A = s['amplitudes'][i]
    h = prof(s['height_vac'][i], s['height_bulk'][i], s['height_si'][i])
    th = np.degrees(prof(s['theta_vac'][i], s['theta_bulk'][i], s['theta_si'][i]))
    c, ls = styles[p]
    axs[0].plot(z, h / rho / A, color=c, ls=ls, label=f'{energies[p]} eV')
    axs[1].plot(z, th, color=c, ls=ls)
    half = z < L / 2
    axs[2].plot(gam[half], (h / rho / A)[half], color=c, ls=ls, lw=0.9)
    axs[2].plot(gam[~half], (h / rho / A)[~half], color=c, ls=ls, lw=2.0)
axs[0].axhline(1, color=LGRAY, lw=0.8); axs[2].axhline(1, color=LGRAY, lw=0.8)
axs[0].set_xlabel('Depth from vacuum (Å)'); axs[0].set_ylabel('Strength per molecule\n(relative to NEXAFS)')
axs[1].set_xlabel('Depth from vacuum (Å)'); axs[1].set_ylabel('TDM cone angle ϑ (°)')
axs[2].set_xlabel('Local molecular tilt γ (°)'); axs[2].set_ylabel('Strength per molecule')
axs[0].legend(fontsize=7)
axs[2].text(0.3, 0.93, 'thick, SiO$_2$ side   thin, vacuum side', transform=axs[2].transAxes, fontsize=7, color=GRAY)
axs[1].text(0.5, 0.55, 'current fit, angles not yet depth resolved', transform=axs[1].transAxes, ha='center',
            fontsize=7, color=GRAY)
for k, a in enumerate(axs):
    label(a, 'efg'[k], x=-0.28)
save(fig, 'fig4-04efg_preview')
