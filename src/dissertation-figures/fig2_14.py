from figlib import *
from surface import *
from scipy.optimize import least_squares, minimize
from scipy.optimize._differentialevolution import DifferentialEvolutionSolver
from mpl_toolkits.mplot3d import Axes3D  # noqa

TB, RB = (130, 230), (0.0, 60.0)
ts = np.linspace(*TB, 101); rs = np.linspace(*RB, 61)
TT, RR = np.meshgrid(ts, rs)
Z = np.log10(np.array([[chi2((t, r)) for t in ts] for r in rs]))
START = np.array([195.0, 30.0])
f = lambda p: np.log10(chi2(p))

# Levenberg-Marquardt, record every evaluation and keep the improving ones
ev = []
def res_rec(p):
    ev.append(p.copy()); return resid(p)
least_squares(res_rec, START, method='lm', x_scale=[10, 10])
lm_path, best = [START], f(START)
for p in ev:
    v = f(p)
    if v < best - 1e-9:
        best = v; lm_path.append(p)
lm_n = len(ev)

# L-BFGS-B with bounds
lb_path = [START.copy()]; cnt = {'n': 0}
def fc(p):
    cnt['n'] += 1; return f(p)
minimize(fc, START, method='L-BFGS-B', bounds=[TB, RB], callback=lambda x: lb_path.append(x.copy()),
         options=dict(eps=1e-4))
lb_n = cnt['n']

# Differential evolution population snapshots
solver = DifferentialEvolutionSolver(f, [TB, RB], popsize=12, rng=1, polish=False, init='latinhypercube')
snaps = {}
for g in range(40):
    if g in (0, 4, 39):
        snaps[g] = solver._scale_parameters(solver.population).copy()
    next(solver)
de_best = solver.x; de_n = solver._nfev

# random-walk Metropolis from the same start
rng = np.random.default_rng(7)
x = START.copy(); NU = QQ.size - 2; lx = -0.5 * chi2(x) * NU
acc = 0
chain = [x.copy()]; step = np.array([1.5, 1.5])
for i in range(4000):
    y = x + rng.normal(0, 1, 2) * step
    if not (TB[0] < y[0] < TB[1] and RB[0] < y[1] < RB[1]):
        chain.append(x.copy()); continue
    ly = -0.5 * chi2(y) * NU
    if np.log(rng.random()) < ly - lx:
        x, lx = y, ly; acc += 1
    chain.append(x.copy())
chain = np.array(chain); mc_n = 4000

fig = plt.figure(figsize=(6.5, 6.0))
panels = [('a', 'Levenberg-Marquardt', np.array(lm_path), lm_n),
          ('b', 'L-BFGS-B', np.array(lb_path), lb_n),
          ('c', 'Differential evolution', None, de_n),
          ('d', 'Markov chain Monte Carlo', chain, mc_n)]
for k, (lab, title, path, n) in enumerate(panels):
    ax = fig.add_subplot(2, 2, k + 1, projection='3d', computed_zorder=False)
    ax.plot_surface(TT, RR, Z, rstride=2, cstride=3, color='white', edgecolor=GRAY, lw=0.3, shade=False, zorder=1)
    ax.view_init(elev=42, azim=-62)
    ax.set_xlabel(r'$t_{bulk}$ (Å)', labelpad=2); ax.set_ylabel(r'$t_{int}$ (Å)', labelpad=2)
    ax.set_zlabel(r'log$_{10}\,\chi^2_\nu$', labelpad=2)
    ax.tick_params(labelsize=7, pad=0)
    ax.xaxis.pane.fill = ax.yaxis.pane.fill = ax.zaxis.pane.fill = False
    ax.grid(False)
    lift = 0.06
    ax.scatter([TB0], [TI0], [Z.min() + lift], color=BLACK, marker='*', s=50, depthshade=False, zorder=10)
    ax.scatter([START[0]], [START[1]], [f(START) + lift], color=BLACK, marker='o', s=25, depthshade=False)
    if lab == 'c':
        for g, c, s_ in ((0, LGRAY, 10), (4, LRED, 14), (39, RED, 34)):
            P = snaps[g]
            ax.scatter(P[:, 0], P[:, 1], [f(p) + lift for p in P], color=c, s=s_, depthshade=False,
                       edgecolor=BLACK if g == 39 else 'none', linewidth=0.3, zorder=6)
    else:
        zz = [f(p) + lift for p in path]
        if lab == 'd':
            ax.plot(path[::4, 0], path[::4, 1], zz[::4], color=RED, lw=0.6, alpha=0.85, zorder=5)
        else:
            ax.plot(path[:, 0], path[:, 1], zz, color=RED, lw=1.3, marker='o', ms=2, zorder=5)
    ax.text2D(0.5, 0.97, title, transform=ax.transAxes, fontsize=9, ha='center', va='top')
    extra = f', {100*acc/mc_n:.0f}% accepted' if lab == 'd' else ''
    ax.text2D(0.02, 0.86, f'{n} evaluations{extra}', transform=ax.transAxes, fontsize=7.5, color=GRAY)
    ax.text2D(-0.02, 0.98, lab, transform=ax.transAxes, fontsize=11, fontweight='bold', va='top')
fig.subplots_adjust(left=0.0, right=0.94, bottom=0.03, top=0.99, wspace=0.12, hspace=0.06)
save(fig, 'fig2-14_optimizers')
print('LM end', lm_path[-1], 'LB end', lb_path[-1], 'DE', de_best, 'MC end', chain[-1], chain[:, 0].std(), acc)
import json
json.dump(dict(start=START.tolist(), truth=[TB0, TI0], lm=dict(n=lm_n, end=np.array(lm_path[-1]).tolist(), f=f(lm_path[-1])),
               lb=dict(n=lb_n, end=np.array(lb_path[-1]).tolist(), f=f(lb_path[-1])),
               de=dict(n=int(de_n), end=de_best.tolist(), f=f(de_best)), mc=dict(n=mc_n, acc=acc, end=chain[-1].tolist()),
               f_truth=f(np.array([TB0, TI0]))), open('/home/claude/figs/out/facts_opt.json', 'w'), indent=1)
