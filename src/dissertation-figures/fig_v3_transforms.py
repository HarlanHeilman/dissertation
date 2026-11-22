"""Revision 3 of Fig. 2.13. One row, R, log10 R, and R q^4, each with the statistical leverage of every
point in an unweighted least-squares fit plotted against q below it."""
import json
from figlib import *
from model import stack

q = np.linspace(0.006, 0.27, 600)
E = 285.1
P0 = dict(t=192.7, sig=6.8, gamma=69.6, rho=1.64)
STEP = dict(t=0.05, sig=0.05, gamma=0.05, rho=0.0005)


def R_of(p):
    return reflectivity(q, E, stack(E, **p), 's')


R = R_of(P0)
rng = np.random.default_rng(11)
sig = 0.08 * R + 0.5e-6 * q
D = np.clip(R + rng.normal(0, 1, q.size) * sig * 0.5, 1e-10, None)

TF = [('R', lambda r: r, r'$R$', 1.0),
      ('log', lambda r: np.log10(r), r'$\log_{10}R$', 1.0),
      ('q4', lambda r: r * q ** 4, r'$Rq^4$ ($10^{-7}$ Å$^{-4}$)', 1e7)]

FACTS = {}
lev = {}
for key, f, _, _ in TF:
    J = []
    for name, h in STEP.items():
        up, dn = dict(P0), dict(P0)
        up[name] += h; dn[name] -= h
        J.append((f(R_of(up)) - f(R_of(dn))) / (2 * h))
    J = np.array(J).T
    Jn = J / np.linalg.norm(J, axis=0)                # leverage is invariant to parameter scaling
    Q, _ = np.linalg.qr(Jn)
    hdiag = np.sum(Q ** 2, axis=1)                    # diagonal of the hat matrix, sums to the parameter count
    rel = hdiag / (len(STEP) / q.size)                # 1 = every point equally important
    neff = hdiag.sum() ** 2 / np.sum(hdiag ** 2) / q.size
    cum = np.cumsum(hdiag) / hdiag.sum()
    q50 = (q[np.searchsorted(cum, 0.25)], q[np.searchsorted(cum, 0.75)])
    lev[key] = (rel, neff, q50)
    FACTS[key] = dict(neff=float(neff), q_iqr=[float(q50[0]), float(q50[1])], max_rel=float(rel.max()))

fig = plt.figure(figsize=(6.5, 3.0))
gs = fig.add_gridspec(2, 3, height_ratios=[1, 0.62], hspace=0.08, wspace=0.42, left=0.085, right=0.99, top=0.93, bottom=0.14)
for j, (key, f, ylab, sc) in enumerate(TF):
    top = fig.add_subplot(gs[0, j])
    bot = fig.add_subplot(gs[1, j], sharex=top)
    top.plot(q, f(D) * sc, 'o', ms=1.4, color=BLACK, mew=0)
    top.plot(q, f(R) * sc, color=RED, lw=1.1)
    top.set_ylabel(ylab)
    plt.setp(top.get_xticklabels(), visible=False)
    rel, neff, (qa, qb) = lev[key]
    bot.axvspan(qa, qb, color=LGRAY, alpha=0.6, lw=0)
    bot.fill_between(q, 1e-3, rel, color=LRED, lw=0)
    bot.plot(q, rel, color=RED, lw=0.9)
    bot.axhline(1, color=GRAY, lw=0.7, ls='--')
    bot.set_yscale('log'); bot.set_ylim(1e-2, 3e2)
    bot.set_xlim(0, 0.27); bot.set_xlabel(r'$q$ (Å$^{-1}$)')
    bot.text(0.97, 0.93, f'$N_{{\\rm eff}}/N$ = {neff:.2f}', transform=bot.transAxes, ha='right', va='top', fontsize=7)
    if j == 0:
        bot.set_ylabel('Leverage\n(× uniform)')
    label(top, 'abc'[j], x=-0.3, y=1.02)
save(fig, 'fig2-13_objective-transforms')
json.dump(FACTS, open(f'{OUT}/facts_fig213_v3.json', 'w'), indent=1)
print(json.dumps(FACTS, indent=1))
