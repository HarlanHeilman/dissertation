"""Per-state data for the ZnPc excitation figure: geometry, signed per-atom p-lobe vectors of the final MO,
and the TDM direction from the final orbital's p character on the core-hole atom (StoBe TP molden files)."""
import math, pickle, numpy as np, molden_mo as M

D = "/mnt/user-data/uploads/dft-learn/docs/stobe/example-run/znpc-cif"
STATES = [("C1", 205, 292.89389, 57.48731, 13, "α carbon"),
          ("C4", 304, 296.21945, 44.07573, 14, "outer benzo carbon"),
          ("C2", 328, 298.36862, 31.19655, 15, "bridgehead carbon")]
R0 = 0.7 * M.ANG


def p_vectors(atoms, shells, C, weight):
    vec = np.zeros((len(atoms), 3))
    k = 0
    for a, l, ex, co in shells:
        n = len(M.CART[l])
        if l == "p":
            vec[a] += weight(ex, co) * C[k:k + 3]
        k += n
    return vec


def r0_amp(ex, co):          # p radial amplitude at r0 (valence-like lobe), contracted shell normalized
    N = (2 * ex / math.pi) ** 0.75 * (4 * ex) ** 0.5
    return (co * N * np.exp(-ex * R0 ** 2)).sum() * R0 * M.contraction_scale("p", ex, co)


def core_w(ex, co):          # overlap-like weight with a compact 1s
    return (co * ex ** 0.75).sum()


if __name__ == "__main__":
    out = []
    for site, mo, en, th_hf, cl, chem in STATES:
        atoms, shells, Cs = M.load(f"{D}/{site}/{site}tp.molden", {mo})
        C = Cs[mo]
        xyz = np.array([a[2] for a in atoms]) / M.ANG
        Z = np.array([a[1] for a in atoms])
        # best-fit molecular plane
        cen = xyz.mean(0)
        _, _, vt = np.linalg.svd(xyz - cen)
        nrm = vt[2] * np.sign(vt[2][2])
        exc = int(np.where(Z == 6)[0][0])
        lob = p_vectors(atoms, shells, C, r0_amp)
        mu = pickle.load(open("znpc_tdm.pkl", "rb"))[(site, mo)]     # exact <1s|r|psi_f>
        tdm = mu / np.linalg.norm(mu)
        names = [a[0] for a in atoms]
        iso = [i for i, nm in enumerate(names) if nm in ("C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "N02")]
        P = xyz[iso]; _, _, vt2 = np.linalg.svd(P - P.mean(0)); nrm = vt2[2] * np.sign(vt2[2][2])   # local isoindole normal
        th = math.degrees(math.acos(abs(tdm @ nrm)))
        print(site, mo, "exc atom", atoms[exc][0], "theta from orbital", round(th, 1), "stick", round(th_hf, 1),
              "lobe max", round(np.linalg.norm(lob, axis=1).max(), 3), "tdm", np.round(tdm, 3))
        out.append(dict(site=site, mo=mo, en=en, theta=th, theta_hf=th_hf, cluster=cl, chem=chem, xyz=xyz, Z=Z,
                        names=[a[0] for a in atoms], exc=exc, lobes=lob, tdm=tdm, normal=nrm))
    pickle.dump(out, open("znpc_states.pkl", "wb"))
