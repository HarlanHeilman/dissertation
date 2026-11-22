"""Figures 2.8, 2.10, 2.11, 2.12, 2.13, computed with the exact uniaxial recursion."""
import json
from figlib import *
from model import stack, nk
from henke import n_si, n_sio2
from matplotlib.patches import Rectangle, Ellipse

FACTS = {}
q = np.linspace(0.006, 0.27, 700)

# ======================================================================= 2.11
fig = plt.figure(figsize=(10.5, 3.9))
gs = fig.add_gridspec(2, 2, width_ratios=[1.05, 1], hspace=0.12, wspace=0.28)
ax = fig.add_subplot(gs[:, 0]); blank(ax); ax.set_xlim(0, 10); ax.set_ylim(0, 10)
layers = [('vacuum', 8.2, 9.8, 'white'), ('ZnPc film\n'+r'$\epsilon=$diag$(\epsilon_{xx},\epsilon_{xx},\epsilon_{zz})$', 4.4, 8.2, '#F7F7F7'),
          ('SiO$_2$', 3.4, 4.4, '#E6E6E6'), ('Si substrate', 0.6, 3.4, '#D0D0D0')]
for name, y0, y1, c in layers:
    ax.add_patch(Rectangle((1.0, y0), 8.6, y1 - y0, fc=c, ec=BLACK if name != 'vacuum' else 'none', lw=1.0))
    ax.text(9.45, (y0 + y1) / 2 + (1.2 if 'ZnPc' in name else 0), name, ha='right', va='center', fontsize=8.5, color=GRAY if name == 'vacuum' else BLACK)
for k, y in enumerate((8.2, 4.4, 3.4)):
    ax.text(0.85, y, f'$L_{k+1}$', ha='right', va='center', fontsize=10, color=RED)
for k, (y0, y1) in enumerate(((4.4, 8.2), (3.4, 4.4))):
    ax.annotate('', xy=(1.55, y0), xytext=(1.55, y1), arrowprops=dict(arrowstyle='<->', color=GRAY, lw=1))
    ax.text(1.7, (y0 + y1) / 2, f'$P_{k+1}$', va='center', fontsize=10, color=GRAY)
# molecules in the film, edge-on lines
for x in np.arange(2.6, 5.9, 0.55):
    for y in (5.0, 6.25):
        ax.plot([x - 0.12, x + 0.12], [y - 0.45, y + 0.45], color=BLACK, lw=1.2)
# incident and reflected beams
arrow(ax, 2.2, 9.7, 4.3, 8.25, color=RED, lw=2)
arrow(ax, 4.5, 8.25, 6.6, 9.7, color=RED, lw=2)
ax.text(2.4, 9.0, r'$\mathbf{k}_i$', fontsize=10, color=RED)
ax.text(6.3, 9.0, r'$\mathbf{k}_r$', fontsize=10, color=RED)
ax.text(3.3, 9.55, 's, p', fontsize=9)
ax.plot([4.4, 6.2], [8.2, 4.45], color=RED, lw=0.9, ls=(0, (2, 2)))
ax.text(5.0, 1.6, r'$\Gamma_N = L_1P_1L_2P_2\,\cdots\,L_NP_NL_{N+1}$', ha='center', fontsize=10.5,
        bbox=dict(boxstyle='round,pad=0.35', fc='white', ec=BLACK, lw=0.9))
ax.text(5.0, 0.15, r'$\partial_z\Psi = i\,(\omega/c)\,\Delta\Psi$,   $\Psi=(E_x,H_y,E_y,-H_x)^T$', ha='center', fontsize=9)
label(ax, 'a', x=0.0, y=0.97)

E = 285.1
for row, pol in enumerate('sp'):
    ax = fig.add_subplot(gs[row, 1])
    Ri = reflectivity(q, E, stack(E, iso=True), pol)
    Ru = reflectivity(q, E, stack(E), pol)
    ax.semilogy(q, Ri, color=BLACK, lw=1.4, label='isotropic')
    ax.semilogy(q, Ru, color=RED, lw=1.6, label='uniaxial')
    ax.set_ylabel(f'$R_{pol}$')
    ax.text(0.97, 0.88, f'{pol} polarization, {E} eV', transform=ax.transAxes, ha='right', fontsize=9)
    if row == 0:
        ax.legend(loc='lower left'); ax.tick_params(labelbottom=False); label(ax, 'b', x=-0.16)
    else:
        ax.set_xlabel(r'$q$ (Å$^{-1}$)'); label(ax, 'c', x=-0.16)
    ax.set_xlim(0, 0.27)
save(fig, 'fig2-11_transfer-matrix')

# ======================================================================= 2.12
E = 283.7
nxx, nzz = nk(E)
si = n_si(E)
base = [(1 + 0j, 1 + 0j, 0, 0), (nxx, nzz, 192.7, 0.0), (si, si, 0, 0.0)]
def with_sig(sig):
    return [base[0], (nxx, nzz, 192.7, sig), (si, si, 0, sig)]
R0 = reflectivity(q, E, base, 's', rough='none')
fig = plt.figure(figsize=(10.5, 7.0))
gs = fig.add_gridspec(6, 3, width_ratios=[1, 1.15, 1.05], hspace=1.3, wspace=0.42)
names = [('nc', 'Névot-Croce'), ('dw', 'Debye-Waller'), ('graded', 'Graded interface')]
zz = np.linspace(-60, 250, 800)
sig = 15.0
sharp = np.where(zz < 0, 0, np.where(zz < 192.7, (1 - nxx.real), (1 - si.real))) * 1e3
disp = (0.5 * (1 + erf(zz / (np.sqrt(2) * sig))) * (1 - nxx.real) +
        0.5 * (1 + erf((zz - 192.7) / (np.sqrt(2) * sig))) * ((1 - si.real) - (1 - nxx.real))) * 1e3
Rm = {}
for sg in (5.0, 15.0):
    L = with_sig(sg)
    sl, *_ = graded_layers(L)
    Rm[sg] = dict(nc=reflectivity(q, E, L, 's', rough='nc'), dw=reflectivity(q, E, L, 's', rough='dw'),
                  graded=reflectivity(q, E, sl, 's', rough='none'))
for r, (key, nm) in enumerate(names):
    axp = fig.add_subplot(gs[2 * r:2 * r + 2, 0])
    if key == 'graded':
        _, zc, gxx, _ = graded_layers(with_sig(sig))
        axp.plot(zz, sharp, color=GRAY, lw=0.9, ls='--')
        axp.plot(zc, (1 - gxx.real) * 1e3, color=RED, lw=1.8)
    else:
        axp.plot(zz, disp, color=GRAY, lw=0.9, ls='--')
        axp.plot(zz, sharp, color=RED, lw=1.8)
    axp.set_ylabel(r'$\delta_{xx}$ ($\times10^{-3}$)')
    axp.text(0.03, 0.88, nm, transform=axp.transAxes, fontsize=9.5, fontweight='bold')
    axp.set_xlim(-60, 250)
    if r == 0:
        label(axp, 'a', x=-0.32)
    if r < 2:
        axp.tick_params(labelbottom=False)
    else:
        axp.set_xlabel('Depth z (Å)')
axb = fig.add_subplot(gs[0:3, 1])
for key, c, ls in (('nc', BLACK, '-'), ('dw', RED, '-'), ('graded', GRAY, '--')):
    axb.semilogy(q, Rm[15.0][key] / R0, color=c, ls=ls, lw=1.5, label=dict(names)[key])
axb.set_ylim(1e-4, 2); axb.set_xlim(0, 0.27); axb.set_ylabel(r'$R/R_{sharp}$')
axb.text(0.97, 0.9, 'σ = 15 Å', transform=axb.transAxes, ha='right', fontsize=9)
axb.legend(loc='lower left', fontsize=8.5); axb.tick_params(labelbottom=False)
label(axb, 'b', x=-0.25)
axc = fig.add_subplot(gs[3:6, 1])
axc.axhline(1, color=LGRAY, lw=0.8)
for key, c in (('nc', BLACK), ('dw', RED)):
    for sg, ls in ((5.0, '--'), (15.0, '-')):
        axc.plot(q, Rm[sg][key] / Rm[sg]['graded'], color=c, ls=ls, lw=1.4,
                 label=f'{"NC" if key == "nc" else "DW"}, σ = {sg:.0f} Å')
axc.set_xlim(0, 0.27); axc.set_ylim(0.5, 1.15)
axc.set_xlabel(r'$q$ (Å$^{-1}$)'); axc.set_ylabel(r'$R/R_{graded}$')
axc.legend(loc='lower left', fontsize=8, ncol=2)
label(axc, 'c', x=-0.25)
FACTS['fig2_12_dev'] = {f'{k}_{sg:.0f}': float(np.max(np.abs(Rm[sg][k] / Rm[sg]['graded'] - 1))) for k in ('nc', 'dw') for sg in (5.0, 15.0)}
# validity map
axm = fig.add_subplot(gs[:, 2])
axm.set_xscale('log'); axm.set_yscale('log')
axm.set_xlim(1e-2, 10); axm.set_ylim(1e-2, 1e2)
axm.add_patch(Rectangle((1e-2, 1e-2), 0.3 - 1e-2, 0.3 - 1e-2, fc='white', ec=BLACK, lw=1.2))
axm.add_patch(Rectangle((1e-2, 3), 0.3 - 1e-2, 100 - 3, fc='white', ec=BLACK, lw=1.2))
axm.add_patch(Rectangle((1, 1e-2), 10 - 1, 100 - 1e-2, fc=LGRAY, ec=BLACK, lw=1.2))
axm.add_patch(Rectangle((0.3, 1e-2), 0.7, 100, fc='white', ec=GRAY, lw=0.8, hatch='///', alpha=0.6))
axm.add_patch(Rectangle((1e-2, 0.3), 0.29, 2.7, fc='white', ec=GRAY, lw=0.8, hatch='///', alpha=0.6))
axm.text(0.055, 0.055, 'Névot\nCroce', ha='center', va='center', fontsize=9.5)
axm.text(0.055, 17, 'Debye\nWaller', ha='center', va='center', fontsize=9.5)
axm.text(3.2, 1.0, 'graded', ha='center', va='center', fontsize=9.5, rotation=90)
axm.text(0.55, 0.03, 'crossover', ha='center', fontsize=8, rotation=90, color=GRAY)
# trajectory for the Chapter 3 film, sigma 6.8 A, assumed xi = 50 nm
lamA = lam(E); qq = np.linspace(0.01, 0.25, 200)
th = np.arcsin(qq * lamA / (4 * np.pi))
alpha = 6.8 * qq / 2
beta = 500.0 / (lamA / (1 - np.cos(th)))
axm.plot(alpha, beta, color=RED, lw=2)
axm.annotate('', xy=(alpha[-1], beta[-1]), xytext=(alpha[-12], beta[-12]),
             arrowprops=dict(arrowstyle='-|>', color=RED, lw=2))
axm.text(1.15, 0.015, 'Chapter 3 film\nσ = 6.8 Å, ξ = 50 nm\nq from 0.01 to 0.25 Å$^{-1}$', color=RED, fontsize=8)
axm.set_xlabel(r'$\sigma k_z$'); axm.set_ylabel(r'$\xi/\xi_{diff}$')
axm.spines['top'].set_visible(True); axm.spines['right'].set_visible(True)
label(axm, 'd', x=-0.22, y=1.01)
FACTS['fig2_12'] = dict(E=E, alpha_qmax=float(alpha[-1]), beta_qmin=float(beta[0]), beta_qmax=float(beta[-1]))
save(fig, 'fig2-12_interfaces')

# ======================================================================= 2.13
E = 285.1
L0 = stack(E)
R = reflectivity(q, E, L0, 's')
rng = np.random.default_rng(11)
sig = 0.08 * R + 0.5e-6 * q
D = np.clip(R + rng.normal(0, 1, q.size) * sig * 0.5, 1e-10, None)
fig, axs = plt.subplots(1, 4, figsize=(11, 2.9))
fig.subplots_adjust(wspace=0.45)
axs[0].errorbar(q, D, sig, fmt='o', ms=1.6, color=BLACK, elinewidth=0.5)
axs[0].plot(q, R, color=RED, lw=1.2); axs[0].set_ylabel('$R$')
axs[1].plot(q, np.log10(D), 'o', ms=1.6, color=BLACK); axs[1].plot(q, np.log10(R), color=RED, lw=1.2)
axs[1].set_ylabel(r'$\log_{10}R$')
axs[2].plot(q, D * q ** 4 * 1e7, 'o', ms=1.6, color=BLACK); axs[2].plot(q, R * q ** 4 * 1e7, color=RED, lw=1.2)
axs[2].set_ylabel(r'$Rq^4$ ($10^{-7}$ Å$^{-4}$)')
# where the thickness information sits for an unweighted objective in each space
dt = 0.5
Rp = reflectivity(q, E, stack(E, t=192.7 + dt), 's'); Rm = reflectivity(q, E, stack(E, t=192.7 - dt), 's')
cases = [('R', (Rp - Rm), BLACK, '-'), (r'$\log_{10}R$', np.log10(Rp) - np.log10(Rm), RED, '-'),
         (r'$Rq^4$', (Rp - Rm) * q ** 4, RED, '--')]
for nm, g, c, ls in cases:
    w = np.cumsum(g ** 2); axs[3].plot(q, w / w[-1], color=c, ls=ls, label=nm)
gw = np.cumsum(((Rp - Rm) / sig) ** 2)
axs[3].plot(q, gw / gw[-1], color=GRAY, lw=1.0, ls=':', label='weighted, any')
axs[3].set_ylabel('cumulative weight on $t$'); axs[3].legend(loc='upper left', fontsize=8, bbox_to_anchor=(0.0, 0.92))
for k, a in enumerate(axs):
    a.set_xlabel(r'$q$ (Å$^{-1}$)'); a.set_xlim(0, 0.27); label(a, 'abcd'[k], x=-0.3)
save(fig, 'fig2-13_objective-transforms')
qs = {nm: float(q[np.searchsorted(np.cumsum(g ** 2) / np.sum(g ** 2), 0.5)]) for nm, g, c, ls in cases}
FACTS['fig2_13'] = dict(E=E, q_half=qs)

# ======================================================================= 2.8
E = 285.1
R = reflectivity(q, E, stack(E), 's')
floor_cmos, well = 30.0, 65536.0
I0 = 2.0e4  # counts per frame at the lowest gain, chosen so the direct beam sits inside the well
from scipy.ndimage import maximum_filter1d
env = maximum_filter1d(R, 61)
series, start = [], 0
gain = 0.5 * well / (I0 * env[0])
for i in range(q.size):
    if env[i] * I0 * gain < 30 * floor_cmos and i - start > 20:
        series.append((start, i + 1, gain)); start = i - 6
        gain = 0.5 * well / (I0 * env[start:start + 40].max())
series.append((start, q.size, gain))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 3.4), gridspec_kw=dict(width_ratios=[1.35, 1], wspace=0.35))
for k, (s0, s1, g) in enumerate(series):
    c = RED if k % 2 else BLACK
    a1.semilogy(q[s0:s1], R[s0:s1] * I0 * g, color=c, lw=1.6)
    rel = g / series[0][2]
    a1.text(q[s0], env[s0] * I0 * g * 1.5, f'×{rel:.0f}' if rel < 1e3 else f'×10$^{{{np.log10(rel):.1f}}}$',
            fontsize=7.5, color=c)
a1.axhline(well, color=GRAY, ls='--', lw=0.9); a1.axhline(floor_cmos, color=GRAY, ls=':', lw=0.9)
a1.text(0.268, well * 1.3, 'pixel well 2$^{16}$', ha='right', fontsize=8, color=GRAY)
a1.text(0.268, floor_cmos * 1.3, 'CMOS floor', ha='right', fontsize=8, color=GRAY)
a1.set_ylim(5, 4e5)
a1.set_xlabel(r'$q$ (Å$^{-1}$)'); a1.set_ylabel('Counts per frame')
ax_r = a1.twinx(); ax_r.semilogy(q, R, color=LGRAY, lw=0.8, zorder=0); ax_r.set_ylabel('$R$', color=GRAY)
ax_r.spines['right'].set_visible(True); ax_r.tick_params(colors=GRAY)
label(a1, 'a', x=-0.13)
span_req = np.log10(R.max() / R.min())
items = [('CCD', np.log10(well / 500)), ('CMOS', np.log10(well / floor_cmos))]
hos, expo = 3.0, np.log10(10 / 0.002)
for k, (nm, det) in enumerate(items):
    left = 0
    for w, c, h in ((det, BLACK, ''), (hos, 'white', '///'), (expo, RED, '')):
        a2.barh(k, w, left=left, color=c, edgecolor=BLACK, hatch=h, height=0.5)
        left += w
    a2.text(left + 0.15, k, f'{left:.1f}', va='center', fontsize=9)
a2.axvline(span_req, color=RED, ls='--', lw=1.2)
a2.text(span_req, 1.45, f'required\n{span_req:.1f} decades', ha='center', fontsize=8, color=RED)
a2.set_yticks([0, 1]); a2.set_yticklabels([i[0] for i in items])
a2.set_xlabel('Dynamic range (decades)'); a2.set_xlim(0, 12); a2.set_ylim(-0.6, 1.9)
from matplotlib.patches import Patch
a2.legend(handles=[Patch(fc=BLACK, label='detector'), Patch(fc='white', ec=BLACK, hatch='///', label='HOS'),
                   Patch(fc=RED, label='exposure')], loc='lower right', fontsize=8)
label(a2, 'b', x=-0.2)
FACTS['fig2_08'] = dict(E=E, n_series=len(series), span=float(span_req), ccd=float(items[0][1]),
                        cmos=float(items[1][1]), hos=hos, exposure=float(expo))
save(fig, 'fig2-08_dynamic-range')

# ======================================================================= 2.10
E = 285.1
R = reflectivity(q, E, stack(E), 's')
(p0, p1, g_prev), (n0, n1, g_n) = series[1], series[2]
i0, i1 = p0, p1
ov = slice(n0, i1)
I0 = 2.0e4
rng = np.random.default_rng(5)
Np = R[i0:i1] * I0 * g_prev; Np_m = rng.poisson(Np)
Nn = R[n0:n1] * I0 * g_n; Nn_m = rng.poisson(Nn)
qa, qb = q[i0:i1], q[n0:n1]
no = i1 - n0
fig, axs = plt.subplots(1, 3, figsize=(11, 3.1)); fig.subplots_adjust(wspace=0.4)
a = axs[0]
a.semilogy(qa, Np_m, 'o', ms=2.2, color=BLACK, label='series $n-1$')
a.semilogy(qb, Nn_m, 's', ms=2.2, color=RED, label='series $n$')
a.axvspan(q[n0], q[i1 - 1], color=LGRAY, alpha=0.6, lw=0)
a.set_xlabel(r'$q$ (Å$^{-1}$)'); a.set_ylabel('Counts'); a.legend(loc='lower left')
label(a, 'a', x=-0.25)
a = axs[1]
ratio = Np_m[-no:] / Nn_m[:no]
rerr = ratio * np.sqrt(1 / np.maximum(Np_m[-no:], 1) + 1 / np.maximum(Nn_m[:no], 1))
w = 1 / rerr ** 2; S = np.sum(w * ratio) / np.sum(w); dS = 1 / np.sqrt(np.sum(w))
a.errorbar(q[ov], ratio, rerr, fmt='o', color=BLACK, ms=3, capsize=2)
a.axhline(S, color=RED, lw=1.6); a.axhspan(S - dS, S + dS, color=LRED, alpha=0.6, lw=0)
a.set_xlabel(r'$q$ (Å$^{-1}$)'); a.set_ylabel(r'$N_{n-1}/N_n$')
label(a, 'b', x=-0.25)
a = axs[2]
Rall = reflectivity(q, E, stack(E), 's')
gains = np.ones_like(q); gg = 1.0
for (s0, s1, g) in series:
    gains[s0:s1] = g
N = Rall * I0 * gains
comp = {'counting': 1 / np.sqrt(N), 'background': np.sqrt(40 * 9.0) / N,
        'stitch scale': np.array([0.01 * np.sqrt(k) for k in np.cumsum(np.r_[0, np.diff(gains) > 0])]),
        'envelope $aR+bq$': (0.08 * Rall + 0.5e-6 * q) / Rall}
tot = np.sqrt(sum(v ** 2 for v in comp.values()))
for (nm, v), c, ls in zip(comp.items(), (BLACK, GRAY, BLACK, RED), ('-', '-', '--', '--')):
    a.semilogy(q, v, color=c, ls=ls, lw=1.2, label=nm)
a.semilogy(q, tot, color=RED, lw=2.0, label='total')
a.set_ylim(1e-3, 3); a.set_xlabel(r'$q$ (Å$^{-1}$)'); a.set_ylabel(r'$\sigma_R/R$')
a.legend(loc='upper left', fontsize=7.5, ncol=2)
label(a, 'c', x=-0.25)
FACTS['fig2_10'] = dict(S=float(S), dS=float(dS))
save(fig, 'fig2-10_stitching-uncertainty')
json.dump(FACTS, open('/home/claude/figs/out/facts_refl.json', 'w'), indent=1)
print(json.dumps(FACTS, indent=1))
