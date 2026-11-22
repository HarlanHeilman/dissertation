"""ZnPc film models used by the Chapter 2 reflectivity figures (cached optical constants)."""
import numpy as np, os, json
from figlib import znpc_index
from henke import n_si, n_sio2
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nk_cache.json')
def nk(E, gamma=69.6, rho=1.64):
    key = f'{E:.2f}_{gamma:.2f}_{rho:.3f}'
    c = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    if key not in c:
        n = znpc_index(np.array([E]), rho=rho, gamma_deg=gamma)
        c[key] = [n['xx'][0].real, n['xx'][0].imag, n['zz'][0].real, n['zz'][0].imag]
        json.dump(c, open(CACHE, 'w'))
    a = c[key]
    return complex(a[0], a[1]), complex(a[2], a[3])
def stack(E, t=192.7, sig=6.8, gamma=69.6, rho=1.64, iso=False, oxide=True):
    nxx, nzz = nk(E, gamma, rho)
    if iso:
        nxx = nzz = (2 * nxx + nzz) / 3
    L = [(1 + 0j, 1 + 0j, 0, 0), (nxx, nzz, t, sig)]
    if oxide:
        L.append((n_sio2(E), n_sio2(E), 15.0, 3.0))
    L.append((n_si(E), n_si(E), 0, 3.0))
    return L
