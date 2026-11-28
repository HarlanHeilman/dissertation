"""Highlights for the ML-refined ZnPc figure: refined cluster (energy, width, tilt) + the dominant StoBe transition
in that cluster from the named site (its final MO gives the lobes; its dipole gives the azimuth)."""
import math, pickle, json, numpy as np, pandas as pd, molden_mo as M
from znpc_states import D, p_vectors, r0_amp
from znpc_tdm import sphere_grid

HL = [(7, "C3"), (10, "C1"), (12, "C2")]
pc = pd.read_csv("/home/claude/znpc_data/data/csv/znpc_params_cluster.csv", encoding="utf-8-sig").iloc[:, :13]
pk = pd.DataFrame(json.load(open("/home/claude/znpc_data/data/csv/param_change.json"))["peaks"])
st = pd.read_csv("/home/claude/znpc_data/data/csv/znpc_sticks_tensor.csv")
out = []
for cl, site in HL:
    sid = int(site[1])
    d = st[(st.cluster == cl) & (st.atomid == sid)].sort_values("os", ascending=False).iloc[0]
    mo = int(d.mo)
    atoms, shells, C = M.load(f"{D}/{site}/{site}tp.molden", {mo, 14})
    xyz = np.array([a[2] for a in atoms]) / M.ANG
    Z = np.array([a[1] for a in atoms]); exc = int(np.where(Z == 6)[0][0])
    names = [a[0] for a in atoms]
    iso = [i for i, nm in enumerate(names) if nm in ("C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "N02")]
    P = xyz[iso]; _, _, vt = np.linalg.svd(P - P.mean(0)); nrm = vt[2] * np.sign(vt[2][2])
    G, w = sphere_grid(atoms[exc][2])
    core = M.mo_on_points(atoms, shells, C[14], G)
    f = M.mo_on_points(atoms, shells, C[mo], G)
    mu = ((G - atoms[exc][2]) * (core * f * w)[:, None]).sum(0); mu /= np.linalg.norm(mu)
    th_stick = math.degrees(math.acos(abs(mu @ nrm)))
    th_cl = float(pc.theta[cl])
    # keep the stick's azimuth, set the polar angle to the refined cluster tilt
    s = 1 if mu @ nrm >= 0 else -1
    inpl = mu - (mu @ nrm) * nrm
    inpl = inpl / np.linalg.norm(inpl) if np.linalg.norm(inpl) > 1e-6 else np.cross(nrm, [1, 0, 0])
    t = math.radians(th_cl)
    tdm = s * math.cos(t) * nrm + math.sin(t) * inpl
    lob = p_vectors(atoms, shells, C[mo], r0_amp)
    r = pk[pk.cluster == cl].iloc[0]
    print(f"cluster {cl} {site}: refined {r.en_f:.2f} eV sigma {r.wid_f:.2f}, tilt {th_cl:.1f} deg; dominant stick MO {mo} "
          f"{d.en:.2f} eV os {d.os:.4f}, stick tilt {th_stick:.1f}")
    out.append(dict(cluster=cl, site=site, mo=mo, en=float(r.en_f), wid=float(r.wid_f), theta=th_cl, theta_stick=th_stick,
                    xyz=xyz, Z=Z, names=names, exc=exc, lobes=lob, tdm=tdm, normal=nrm))
pickle.dump(out, open("znpc_hl.pkl", "wb"))
