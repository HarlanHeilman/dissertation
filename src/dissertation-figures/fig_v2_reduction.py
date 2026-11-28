"""Fig. 2.9, reduction and stitching from real CCD frames (ZnPc, CCD Scan 85302, 285.0 eV, s polarization).

Input is ccd_85302_285eV.npz, written on the device from the raw FITS files: per frame the sample angle,
exposure, higher order suppressor (HOS) position, the specular spot position, the pedestal-subtracted sum in a
13 x 13 pixel box on the spot, and the matching background from two boxes 28 pixels to either side.
"""
import json
import os
from figlib import *
from matplotlib.patches import Rectangle, ConnectionPatch
from matplotlib.colors import LogNorm, LinearSegmentedColormap

NPZ = os.environ.get('CCD_NPZ', os.path.expanduser('~/mnt/dissertation/data/dissertation-figures/ccd_85302_285eV.npz'))
d = np.load(NPZ)
T = d['table']
E = float(d['energy'])
lmb = 12398.42 / E
frame, th, expo, hos, row, col, S, B, ped, peak = T.T
q = 4 * np.pi * np.sin(np.radians(th)) / lmb
I = S - B  # background-subtracted specular counts (ADU)
R_PIX = 6
BG_OFF = 28
SIG_PIX = 20.6  # rms of a blank region of the pedestal-subtracted frame (ADU per pixel)

# series are runs of constant exposure and HOS
key = [(round(e, 4), round(h, 2)) for e, h in zip(expo, hos)]
sid = np.zeros(len(T), int)
for k in range(1, len(T)):
    sid[k] = sid[k - 1] + (key[k] != key[k - 1])
nser = sid.max() + 1

# relative scatter of the repeated first points of each series, the empirical per-frame noise
rel = []
for n in range(nser):
    m = sid == n
    t_first = th[m][0]
    v = I[m & (th == t_first)]
    if len(v) > 2 and t_first > 0:
        rel.append(v.std(ddof=1) / v.mean())
REL = float(np.median(rel))
floor = SIG_PIX * (2 * R_PIX + 1) * np.sqrt(1 + 0.5)  # ROI plus averaged background boxes


def err(v):
    return np.sqrt((REL * v) ** 2 + floor ** 2)


# As in pxr-reduce: counts per second with the shutter offset added to the exposure, I0 from the direct-beam
# frames, R = rate / I0, stitch factors from an orthogonal-distance fit R_post = S R_pre through the origin on the
# angles the new series repeats, excluding the repeated first frames, and each series divided by the running product.
from scipy.odr import ODR, Model, RealData
T_OFF = 0.00389278  # [s], pxr-reduce default exposure_offset
rate = I / (expo + T_OFF)
rate_e = err(I) / (expo + T_OFF)
direct = (th == 0) & (sid == 0)
I0 = rate[direct].mean()
I0e = rate[direct].std(ddof=1)
Rr = rate / I0


def collapse(m):
    """Average repeated angles inside a mask, returning theta, mean rate, its error, n."""
    out = []
    for t_ in np.unique(th[m]):
        mm = m & (th == t_)
        out.append((t_, rate[mm].mean(), np.sqrt(np.sum(rate_e[mm] ** 2)) / mm.sum(), mm.sum()))
    return np.array(out)


ser = [collapse(sid == n) for n in range(nser)]
lin = Model(lambda b_, x: b_[0] * x)
scales = [1.0]
ratios = []
for n in range(1, nser):
    post = np.where(sid == n)[0]
    rep = int(np.sum(th[post] == th[post[0]]))
    post = post[rep:]
    pre = np.where(sid == n - 1)[0]
    common = [t_ for t_ in np.unique(th[pre]) if t_ in th[post]]
    xa = np.array([Rr[pre][th[pre] == t_].mean() for t_ in common])
    yb = np.array([Rr[post][th[post] == t_].mean() for t_ in common])
    ea = np.array([rate_e[pre][th[pre] == t_].mean() for t_ in common]) / I0
    eb = np.array([rate_e[post][th[post] == t_].mean() for t_ in common]) / I0
    fit = ODR(RealData(xa, yb), lin, beta0=[1.0]).run()
    Sn, dSn = float(fit.beta[0]), float(fit.sd_beta[0])
    r_ = yb / xa
    rr = np.column_stack([common, r_, r_ * np.hypot(ea / xa, eb / yb)])
    ratios.append(dict(n=n, rr=rr, S=Sn, dS=dSn))
    scales.append(scales[-1] * Sn)
FACTS = dict(E=E, I0=float(I0), n_series=int(nser), rel_repeat=REL,
             series=[dict(exposure=float(expo[sid == n][0]), hos=float(hos[sid == n][0]),
                          theta=[float(th[sid == n].min()), float(th[sid == n].max())], n=int((sid == n).sum()))
                     for n in range(nser)],
             S=[dict(n=r['n'], S=float(r['S']), dS=float(r['dS']), npts=int(len(r['rr']))) for r in ratios])

# ------------------------------------------------------------------ figure
fig = plt.figure(figsize=(6.5, 2.35))
gs = fig.add_gridspec(2, 3, width_ratios=[0.78, 1.25, 1.25], height_ratios=[1.25, 1], wspace=0.42, hspace=0.12,
                      left=0.045, right=0.99, top=0.95, bottom=0.2)
raw = d['frame201']
img = raw - np.median(raw)
r201 = T[frame == 201][0]
ry, rx = int(r201[4]), int(r201[5])
norm = LogNorm(vmin=0.75 * np.median(raw), vmax=raw.max())  # pedestal renders dark red, the spot yellow to white
CMAP = 'hot'
zx0, zx1, zy0, zy1 = rx - BG_OFF - R_PIX - 3, rx + BG_OFF + R_PIX + 4, ry - 11, ry + 12
# a, full frame and enlarged region with the integration boxes
axa = fig.add_subplot(gs[0, 0])
axa.imshow(raw, cmap=CMAP, norm=norm, origin='upper', interpolation='nearest')
axa.add_patch(Rectangle((zx0 - 0.5, zy0 - 0.5), zx1 - zx0, zy1 - zy0, fill=False, ec='white', lw=0.9))
axa.set_xticks([]); axa.set_yticks([])
axz = fig.add_subplot(gs[1, 0])
axz.imshow(raw[zy0:zy1, zx0:zx1], cmap=CMAP, norm=norm, origin='upper', interpolation='nearest',
           extent=(zx0 - 0.5, zx1 - 0.5, zy1 - 0.5, zy0 - 0.5))
axz.add_patch(Rectangle((rx - R_PIX - 0.5, ry - R_PIX - 0.5), 2 * R_PIX + 1, 2 * R_PIX + 1, fill=False, ec='white', lw=1.0))
for dx in (-BG_OFF, BG_OFF):
    axz.add_patch(Rectangle((rx + dx - R_PIX - 0.5, ry - R_PIX - 0.5), 2 * R_PIX + 1, 2 * R_PIX + 1, fill=False,
                            ec='white', lw=0.8, ls=(0, (2, 1.5))))
axz.set_xticks([]); axz.set_yticks([])
for ax_ in (axa, axz):
    for sp in ax_.spines.values():
        sp.set_visible(True); sp.set_linewidth(0.8); sp.set_color(BLACK)
for (xa, ya), (xb, yb) in (((zx0, zy1), (0, 1)), ((zx1, zy1), (1, 1))):
    fig.add_artist(ConnectionPatch(xyA=(xa - 0.5, ya - 0.5), coordsA=axa.transData, xyB=(xb, yb), coordsB=axz.transAxes,
                                   color=BLACK, lw=0.5))
axz.text(0.5, -0.06, 'specular (solid), background (dashed)', transform=axz.transAxes, fontsize=6, ha='center',
         va='top', color=GRAY)
# b, raw specular counts per series
axb = fig.add_subplot(gs[:, 1])
cols = [BLACK, RED, GRAY, '#8B1A1A']
mk = ['o', 's', '^', 'D']
for n in range(nser):
    c = ser[n]; c = c[c[:, 0] > 0]
    qq = 4 * np.pi * np.sin(np.radians(c[:, 0])) / lmb
    e_ = c[:, 2]
    axb.errorbar(qq, c[:, 1], e_, fmt=mk[n], color=cols[n], ms=2.4, mfc='white' if n % 2 else cols[n], mew=0.7,
                 elinewidth=0.6, capsize=0, label=f'{n + 1}, {FACTS["series"][n]["exposure"]:g} s')
axb.set_yscale('log')
axb.errorbar([0], [I0], [I0e], fmt='*', color=RED, ms=6, mec=BLACK, mew=0.4, elinewidth=0.6, capsize=0)
axb.text(0.004, I0 * 1.5, r'$I_0$', fontsize=7, color=RED)
axb.set_ylim(2e5, 3e8); axb.set_xlim(-0.004, 0.103)
axb.set_xlabel(r'$q$ (Å$^{-1}$)'); axb.set_ylabel(r'Count rate (ADU s$^{-1}$)')
axb.legend(loc='upper right', fontsize=6, handletextpad=0.2, borderaxespad=0.1, labelspacing=0.25, title='series',
           title_fontsize=6)
# c, stitched reflectivity
axc = fig.add_subplot(gs[:, 2])
for n in range(nser):
    c = ser[n]; c = c[c[:, 0] > 0]
    qq = 4 * np.pi * np.sin(np.radians(c[:, 0])) / lmb
    Rn = c[:, 1] / (scales[n] * I0)
    relS = np.sqrt(sum((ratios[j]['dS'] / ratios[j]['S']) ** 2 for j in range(n))) if n else 0.0
    eR = Rn * np.sqrt((c[:, 2] / c[:, 1]) ** 2 + relS ** 2 + (I0e / I0) ** 2)
    axc.errorbar(qq, Rn, eR, fmt=mk[n], color=cols[n], ms=2.0, mfc='white' if n % 2 else cols[n], mew=0.6,
                 elinewidth=0.7, capsize=0)
axc.errorbar([0], [1.0], [I0e / I0], fmt='*', color=RED, ms=6, mec=BLACK, mew=0.4, elinewidth=0.6, capsize=0, zorder=5)
axc.text(0.004, 1.25, r'$I_0$', fontsize=7, color=RED, va='bottom')
axc.set_yscale('log'); axc.set_ylim(3e-5, 3)
# inset, the first stitch factor from the overlap angles
ins = axc.inset_axes([0.12, 0.09, 0.28, 0.27])
r0 = ratios[0]
tq = 4 * np.pi * np.sin(np.radians(r0['rr'][:, 0])) / lmb
ins.axhspan(r0['S'] - r0['dS'], r0['S'] + r0['dS'], color=LRED, alpha=0.7, lw=0)
ins.axhline(r0['S'], color=RED, lw=1.0)
ins.errorbar(tq, r0['rr'][:, 1], r0['rr'][:, 2], fmt='o', color=BLACK, ms=2.2, elinewidth=0.6, capsize=1.2)
ins.set_xlim(tq.min() - 0.0007, tq.max() + 0.0007)
ins.set_xticks([]); ins.tick_params(labelsize=5.5, length=2, pad=1)
ins.yaxis.set_major_locator(plt.MaxNLocator(3))
ins.set_title(rf'$S_{{2,1}}$ = {r0["S"]:.1f} ± {r0["dS"]:.1f}', fontsize=6, pad=2)
ins.set_ylabel(r'$R_2/R_1$', fontsize=5.5, labelpad=1)
ins.set_xlabel('overlap angles', fontsize=5.5, labelpad=1)
FACTS_PXR = True; axc.set_xlim(-0.004, 0.103)
axc.set_xlabel(r'$q$ (Å$^{-1}$)'); axc.set_ylabel('$R$')
axc.text(0.97, 0.95, r'$R_n=\dfrac{I_n/(t+t_0)}{S_{n,n-1}\cdots S_{2,1}\,I_0}$', transform=axc.transAxes, ha='right', va='top', fontsize=7.5)
for ax_ in (axb, axc):
    ax_.set_xticks([0, 0.05, 0.1])
grid_labels(fig, [[(axb, 'b'), (axc, 'c')]])
fig.text(0.0, axa.get_position().y1, 'a', fontsize=LABEL_FS, fontweight='bold', va='top', ha='left')
FACTS['frame'] = dict(n=201, theta=float(r201[1]), exposure=float(r201[2]), hos=float(r201[3]))
FACTS['q_max'] = float(q.max())
save(fig, 'fig2-09_reduction')
json.dump(FACTS, open(f'{OUT}/facts_reduction.json', 'w'), indent=1)
print(json.dumps(FACTS, indent=1))
