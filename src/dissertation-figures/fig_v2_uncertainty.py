"""Revision 3, Fig. 2.15. One row. a DE on the full surface, b L-BFGS-B and Nelder-Mead polish in the basin,
c MCMC in the basin, d covariance comparison."""
import json
from figlib import *
from surface import *
from scipy.optimize import minimize
from scipy.optimize._differentialevolution import DifferentialEvolutionSolver
from matplotlib.patches import Ellipse
from matplotlib.lines import Line2D

B = [(130.0, 230.0), (0.0, 60.0)]
nll = lambda p: 0.5 * float(resid(p) @ resid(p))
FACTS = {}

# ------------------------------------------------------------------ a, differential evolution
solver = DifferentialEvolutionSolver(nll, B, popsize=15, rng=1, polish=False, init='latinhypercube', tol=1e-8)
snaps = {}
for g in range(9):
    if g in (0, 4, 8):
        snaps[g] = solver._scale_parameters(solver.population).copy()
    if g < 8:
        next(solver)
x_de = solver.x.copy(); n_de = int(solver._nfev)

# ------------------------------------------------------------------ b, local polish
paths = {}
for meth in ('L-BFGS-B', 'Nelder-Mead'):
    path, cnt = [x_de.copy()], {'n': 0}
    def fc(p):
        cnt['n'] += 1; return nll(p)
    opts = dict(eps=1e-6) if meth == 'L-BFGS-B' else dict(xatol=1e-4, fatol=1e-6, initial_simplex=[x_de, x_de + [0.3, 0], x_de + [0, 0.3]])
    r = minimize(fc, x_de, method=meth, bounds=B if meth == 'L-BFGS-B' else None, callback=lambda x: path.append(x.copy()),
                 options=opts)
    paths[meth] = (np.array(path), cnt['n'], r)
x0 = paths['L-BFGS-B'][2].x
cov_lbfgs = paths['L-BFGS-B'][2].hess_inv.todense()
def hessian(f, x, h):
    n = len(x); H = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            ei = np.eye(n)[i] * h[i]; ej = np.eye(n)[j] * h[j]
            H[i, j] = (f(x + ei + ej) - f(x + ei - ej) - f(x - ei + ej) + f(x - ei - ej)) / (4 * h[i] * h[j])
    return H
cov_fd = np.linalg.inv(hessian(nll, x0, np.array([0.02, 0.02])))

# ------------------------------------------------------------------ c, ensemble MCMC in the basin
rng = np.random.default_rng(5)
nw, ns, a_ = 32, 3000, 2.0
W = rng.multivariate_normal(x0, cov_fd, nw); lp = np.array([-nll(w) for w in W])
chain = np.empty((ns, nw, 2)); acc = 0
for s in range(ns):
    for k in range(nw):
        j = rng.integers(nw - 1); j = j + (j >= k)
        z = ((a_ - 1) * rng.random() + 1) ** 2 / a_
        y = W[j] + z * (W[k] - W[j]); ly = -nll(y)
        if np.log(rng.random()) < np.log(z) + ly - lp[k]:
            W[k], lp[k] = y, ly; acc += 1
    chain[s] = W
post = chain[1000:].reshape(-1, 2); cov_mc = np.cov(post.T)

sd = lambda C: np.sqrt(np.abs(np.diag(C))).tolist()
cr = lambda C: float(C[0, 1] / np.sqrt(abs(C[0, 0] * C[1, 1])))
FACTS = dict(x_de=x_de.tolist(), n_de=n_de, x_min=x0.tolist(),
             n_lbfgs=paths['L-BFGS-B'][1], n_nm=paths['Nelder-Mead'][1], x_nm=paths['Nelder-Mead'][2].x.tolist(),
             sd_fd=sd(cov_fd), sd_lbfgs=sd(cov_lbfgs), sd_mc=sd(cov_mc), corr_fd=cr(cov_fd), corr_lbfgs=cr(cov_lbfgs),
             corr_mc=cr(cov_mc), acc=acc / (nw * ns), n_mc=nw * ns)
print(json.dumps(FACTS, indent=1))

# ------------------------------------------------------------------ surfaces
ts = np.linspace(*B[0], 81); ti = np.linspace(*B[1], 49)
TT, II = np.meshgrid(ts, ti)
Zfull = np.log10(np.array([[chi2((a, b)) for a in ts] for b in ti]))
w0, w1 = 4.2 * np.sqrt(cov_fd[0, 0]), 4.2 * np.sqrt(cov_fd[1, 1])
# one window for b and c, centered between the DE best point and the minimum, on the same log10 chi2 surface as a
cw = (x_de + x0) / 2
hw0 = max(w0, 1.4 * abs(x_de[0] - x0[0]) + 0.1); hw1 = max(w1, 1.4 * abs(x_de[1] - x0[1]) + 0.05)
lt = np.linspace(cw[0] - hw0, cw[0] + hw0, 31); li = np.linspace(cw[1] - hw1, cw[1] + hw1, 31)
LT, LI = np.meshgrid(lt, li)
Zloc = np.log10(np.array([[chi2((a, b)) for a in lt] for b in li]))
lz = lambda P: np.log10(np.array([chi2(p) for p in np.atleast_2d(P)]))
inwin = lambda P: (np.abs(P[:, 0] - cw[0]) < hw0) & (np.abs(P[:, 1] - cw[1]) < hw1)
FACTS['window'] = dict(center=cw.tolist(), half=[hw0, hw1])


from matplotlib.ticker import MaxNLocator
def surf3d(ax, X, Y, Z, rs=2, cs=2):
    ax.plot_surface(X, Y, Z, rstride=rs, cstride=cs, color='white', edgecolor=GRAY, lw=0.3, shade=False, zorder=1)
    ax.xaxis.pane.fill = ax.yaxis.pane.fill = ax.zaxis.pane.fill = False
    ax.grid(False); ax.tick_params(labelsize=7.5, pad=-1)
    for a_ in (ax.xaxis, ax.yaxis, ax.zaxis):
        a_.set_major_locator(MaxNLocator(3))
    ax.view_init(elev=38, azim=-58)
    ax.set_zticks([]); ax.zaxis.line.set_color((0, 0, 0, 0))


from scipy.interpolate import RegularGridInterpolator
Ion = RegularGridInterpolator((TT[0, :], II[:, 0]), Zfull.T, bounds_error=False, fill_value=None)
fig = plt.figure(figsize=(6.5, 6.4))
ax = fig.add_axes([-0.04, 0.53, 0.54, 0.47], projection='3d', computed_zorder=False)
surf3d(ax, TT, II, Zfull, 2, 3)
for g, c, s_ in ((0, LGRAY, 6), (4, LRED, 7), (8, RED, 7)):
    P = snaps[g]
    ax.scatter(P[:, 0], P[:, 1], Ion((P[:, 0], P[:, 1])) + 0.06, color=c, s=s_, depthshade=False, zorder=5,
               edgecolor=BLACK if g == 8 else 'none', linewidth=0.3)
zf = Zfull.min() - 0.15
bx = np.array([[-7, -4.5], [7, -4.5], [7, 4.5], [-7, 4.5], [-7, -4.5]]) + x0
ax.plot(bx[:, 0], bx[:, 1], [zf] * 5, color=RED, lw=1.2, zorder=6)
ax.plot([x0[0], x0[0]], [x0[1], x0[1]], [zf, Zfull.min()], color=RED, lw=0.8, ls=':', zorder=6)
ax.text(x0[0] + 14, x0[1] - 14, zf, 'basin\nin b, c', color=RED, fontsize=7, zorder=7)
ax.set_zlim(zf, Zfull.max())
ax.set_xlabel(r'$t_{bulk}$ (Å)', fontsize=7.5, labelpad=-3); ax.set_ylabel(r'$t_{int}$ (Å)', fontsize=7.5, labelpad=-3)
ax.set_zlabel('')
ax.text2D(0.5, 0.97, 'Differential evolution', transform=ax.transAxes, ha='center', fontsize=8.5)
ax.text2D(0.07, 0.98, 'a', transform=ax.transAxes, fontsize=11, fontweight='bold', va='top')

ax = fig.add_axes([0.47, 0.53, 0.54, 0.47], projection='3d', computed_zorder=False)
surf3d(ax, LT, LI, Zloc)
dz = 0.04 * (Zloc.max() - Zloc.min())
P8 = snaps[8][inwin(snaps[8])]
if len(P8):
    ax.scatter(P8[:, 0], P8[:, 1], lz(P8) + dz, color=LRED, s=10, depthshade=False, zorder=5, edgecolor='none')
for meth, c, mk in (('L-BFGS-B', RED, 'o'), ('Nelder-Mead', BLACK, 's')):
    pth = paths[meth][0]
    ax.plot(pth[:, 0], pth[:, 1], lz(pth) + dz, color=c, lw=1.5, marker=mk, ms=2.5, zorder=6)
ax.scatter([x_de[0]], [x_de[1]], lz(x_de) + dz, marker='*', s=70, color=RED, edgecolor=BLACK, linewidth=0.5,
           depthshade=False, zorder=7)
ax.set_xlabel(r'$t_{bulk}$ (Å)', fontsize=7.5, labelpad=-3); ax.set_ylabel(r'$t_{int}$ (Å)', fontsize=7.5, labelpad=-3)
ax.set_zlabel('')
ax.text2D(0.5, 0.97, 'Local polish from the DE best', transform=ax.transAxes, ha='center', fontsize=8.5)
ax.legend(handles=[Line2D([], [], color=RED, marker='*', ms=7, ls='none', mec=BLACK, mew=0.5, label='DE best'),
                   Line2D([], [], color=RED, marker='o', ms=3, label=f"L-BFGS-B, {paths['L-BFGS-B'][1]} evals"),
                   Line2D([], [], color=BLACK, marker='s', ms=3, label=f"Nelder-Mead, {paths['Nelder-Mead'][1]} evals")],
          loc='upper left', fontsize=7, bbox_to_anchor=(0.06, 0.9), ncol=1)
ax.text2D(0.07, 0.98, 'b', transform=ax.transAxes, fontsize=11, fontweight='bold', va='top')

ax = fig.add_axes([-0.04, 0.0, 0.54, 0.47], projection='3d', computed_zorder=False)
surf3d(ax, LT, LI, Zloc)
sub = post[rng.choice(len(post), 1500, replace=False)]
sub = sub[inwin(sub)]
ax.scatter(sub[:, 0], sub[:, 1], lz(sub) + dz, color=RED, s=1.2, alpha=0.6, depthshade=False, zorder=5)
ax.set_xlabel(r'$t_{bulk}$ (Å)', fontsize=7.5, labelpad=-3); ax.set_ylabel(r'$t_{int}$ (Å)', fontsize=7.5, labelpad=-3)
ax.set_zlabel('')
ax.text2D(0.5, 0.97, 'Ensemble MCMC in the basin', transform=ax.transAxes, ha='center', fontsize=8.5)
ax.text2D(0.07, 0.97, 'c', transform=ax.transAxes, fontsize=11, fontweight='bold', va='top')


def ellipse(ax, mu, C, nsig, **kw):
    w, v = np.linalg.eigh(C)
    ang = np.degrees(np.arctan2(v[1, 1], v[0, 1]))
    ax.add_patch(Ellipse(mu, 2 * nsig * np.sqrt(w[1]), 2 * nsig * np.sqrt(w[0]), angle=ang, fill=False, **kw))


x_, y_, wd, ht = 0.62, 0.075, 0.25, 0.23
axj = fig.add_axes([x_, y_, wd, ht])
axt = fig.add_axes([x_, y_ + ht + 0.008, wd, 0.07], sharex=axj)
axr = fig.add_axes([x_ + wd + 0.006, y_, 0.07, ht], sharey=axj)
axj.plot(post[::25, 0], post[::25, 1], '.', color=GRAY, ms=1.0, alpha=0.25, zorder=0)
for ns_ in (1, 2):
    ellipse(axj, x0, cov_fd, ns_, ec=RED, lw=2.0, zorder=2)
    ellipse(axj, x0, cov_lbfgs, ns_, ec=RED, lw=1.0, ls=':', zorder=2)
    ellipse(axj, x0, cov_mc, ns_, ec=BLACK, lw=1.0, ls=(0, (3, 2)), zorder=3)
axj.set_xlim(x0[0] - w0, x0[0] + w0); axj.set_ylim(x0[1] - w1, x0[1] + w1)
axj.set_xlabel(r'$t_{bulk}$ (Å)', fontsize=7.5); axj.set_ylabel(r'$t_{int}$ (Å)', fontsize=7.5)
axj.tick_params(labelsize=7); axj.xaxis.set_major_locator(MaxNLocator(3)); axj.yaxis.set_major_locator(MaxNLocator(4))
for ax_, i, orient in ((axt, 0, 'vertical'), (axr, 1, 'horizontal')):
    gg = np.linspace(x0[i] - (w0, w1)[i], x0[i] + (w0, w1)[i], 300)
    ax_.hist(post[:, i], bins=45, density=True, color=LGRAY, orientation=orient, ec='none')
    for C, c, ls in ((cov_fd, RED, '-'), (cov_lbfgs, RED, ':'), (cov_mc, BLACK, (0, (3, 2)))):
        s_ = np.sqrt(abs(C[i, i])); pdf = np.exp(-0.5 * ((gg - x0[i]) / s_) ** 2) / (s_ * np.sqrt(2 * np.pi))
        (ax_.plot(gg, pdf, color=c, ls=ls, lw=1.2) if orient == 'vertical' else ax_.plot(pdf, gg, color=c, ls=ls, lw=1.2))
    ax_.axis('off')
fig.text(0.5, 0.455, 'd', fontsize=11, fontweight='bold', va='top')
axj.legend(handles=[Line2D([], [], color=BLACK, ls=(0, (3, 2)), label='MCMC samples, covariance'),
                    Line2D([], [], color=RED, label='finite-difference Hessian'),
                    Line2D([], [], color=RED, ls=':', label='L-BFGS-B inverse Hessian')],
           loc='lower left', bbox_to_anchor=(-0.05, 1.32), fontsize=7, ncol=1, frameon=False)
save(fig, 'fig2-15_uncertainty')
json.dump(FACTS, open(f'{OUT}/facts_unc.json', 'w'), indent=1)
