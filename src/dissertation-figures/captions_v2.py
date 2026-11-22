import ast, json, re, docx
from docx.shared import Pt

OUT = '/home/claude/figs/out'
src = open('/home/claude/figs/captions.py').read()
old = {c[0]: c for c in ast.literal_eval(src[src.index('C = [') + 4:src.index('def add_runs')].strip())}
U = json.load(open(f'{OUT}/facts_unc.json'))
A = json.load(open(f'{OUT}/facts_align.json'))
V = json.load(open(f'{OUT}/facts_v2a.json'))
R = json.load(open(f'{OUT}/facts_refl.json'))
RD = json.load(open(f'{OUT}/facts_reduction.json'))
md = R.get('fig2_11', {}).get('median_log_dev') or {'single film': 0.228, 'bilayer': 0.133, 'multilayer, 6 periods': 0.308}

C = [
 ('1.2', 'fig1-02_ar-nexafs', 'Ch. 1, transition dipoles and AR-NEXAFS (comment 18, replaces the TDM schematic and Fig. 2.4)',
  'Angle-resolved NEXAFS reads molecular orientation from the transition dipole. '
  '**a)** A photon near 285 eV promotes a C 1s electron, localized on one carbon, into a π* orbital delocalized over the conjugated ring, giving a transition dipole μ normal to the molecular plane. '
  '**b)** Edge-on ZnPc film with the π* transition dipole μ_π* at angle α from the surface normal n̂ and the electric field E at angle θ from n̂. '
  '**c)** Mass absorption of the ZnPc film for θ = 20° (red) to 90° (black), with the π* (283.6 to 286.0 eV, red) and σ* (291 to 300 eV, gray) integration windows shaded. '
  f'**d)** Integrated π* (red, filled) and σ* (black, open) intensity against cos²θ with linear fits. The vector-orbital form I = A[1 + ½(3cos²θ − 1)(3cos²α − 1)] gives α = {V["fig1_2"]["pi"]["ang"]:.1f} ± {V["fig1_2"]["pi"]["dang"]:.1f}° for π*, and the plane-orbital form I = A[1 − ¼(3cos²θ − 1)(3cos²γ − 1)] gives γ = {V["fig1_2"]["sigma"]["ang"]:.1f} ± {V["fig1_2"]["sigma"]["dang"]:.1f}° for σ*.',
  'Spectra from nexafs.csv. Fits are linear least squares in cos²θ with uncertainties from the fit covariance only. These tilt values are the integrated-window estimate, distinct from the Chapter 3 tensor fit (γ = 69.6°), and the text should say which one each claim rests on.'),
 ('2.1', 'fig2-01_scattering-geometry', 'Ch. 2, scattering in the far field (replaces the current Fig. 2.1)',
  'Scattering geometries and momentum transfer. '
  '**a)** A plane wave with wavevector k scatters from a finite object. Curved wavefronts near the object (near field) flatten with distance, and the detector records the far-field pattern along k′ at scattering angle 2θ, with momentum transfer q = k′ − k of magnitude |q| = (4π/λ) sin θ. '
  '**b)** Specular reflection from a film on a substrate at grazing angle θ, where q_z = (4π/λ) sin θ lies along the film normal. s polarization places E normal to the plane of incidence and p polarization places E in it.',
  'Panel a adds the near and far field requested in the figure review.'),
 ('2.2', 'fig2-02_near-far-field', 'Ch. 2, scattering in the far field (comments 37, 38, 39)',
  'The far-field pattern emerges from local interactions. A plane wave with wavevector k carrying the incident intensity I₀ illuminates five scatterers of size a separated by distances of order d. Two incident rays are marked, one onto a front scatterer and one onto a scatterer deeper in the cluster. The front scatterer scatters forward along k_s, so the deeper scatterer is driven both by I₀ and by this secondary illumination, and it is the field it radiates along k′ that reaches the detector. Black lines are crests of the total scattered field, computed with multiple scattering between the scatterers. Near the cluster the crests are distorted by these interactions, and with distance they flatten into the outgoing wavefronts. A detector at L ≫ d, a records only the far-field intensity I(2θ) (red), the orientation-averaged pattern of these scatterers, a forward peak set by their spacing and size with weaker side maxima.',
  'Two-dimensional scalar Foldy-Lax calculation with point scatterers of strength 1.2 and a drawn wavelength of 1.05 units, for illustration. The L axis is broken because the detector distance is many orders of magnitude larger than the cluster.'),
 ('2.3',) + old['2.3'][1:],
 ('2.7', 'fig2-07_alignment', 'Ch. 2, sample alignment (placeholder 21)',
  'Iterative sample alignment with a finite beam and a finite photodiode. '
  f'**a)** Knife-edge geometry, with the sample raised through the beam at θ = 0 until it blocks half of it. '
  f'**b)** Photodiode signal against sample height in {A["knife"]["step_um"]} µm steps with an error-function fit, which places the surface at z₀ = {A["knife"]["z0_um"]:.1f} ± {A["knife"]["dz0_um"]:.1f} µm for a beam of σ ≈ {A["knife"]["sigma_um"]:.0f} µm. '
  '**c)** Rocking geometry at fixed z₀ with the detector at 0°, drawn just below the cliff. The lower part of the beam is blocked by the leading face of the sample, the upper part passes over it (light red), and the part striking the surface reflects onto the diode (dark red). A larger tilt sends the reflection over the diode (gray, dashed), which is the cliff in d. '
  f'**d)** Rocking scan in {A["rock"]["step_deg"]}° steps. The rise from blocking and reflection is cut by a sharp cliff near θ_s = {A["rock"]["cliff_deg"]:.2f}° where the reflected beam leaves the diode, so the half-maximum midpoint (red, dashed) sits at {A["rock"]["fwhm_center_deg"]:.2f}° for a true offset of zero. '
  '**e)** θ-2θ geometry with the detector at θ_d = 2°, where the whole beam strikes the sample surface and reflects onto the diode near θ_s = 1°. Angles are exaggerated and the sample is drawn as a rigid rotated block. '
  f'**f)** θ-2θ scan in {A["th2th"]["step_deg"]}° steps with a soft-edged top-hat fit, which locates the center at θ₀ = {A["th2th"]["theta0"]:.3f} ± {A["th2th"]["dtheta0"]:.3f}°, a sub-step localization roughly thirty times finer than the step.',
  'Ray Monte Carlo with beam σ = 40 µm, 1 mrad divergence, 10 mm sample, diode half height 1.5 mm at 150 mm. Illustrative scans, not logged data. The term sub-step localization borrows from localization microscopy, where fitting a known shape places an edge or center well below the sampling interval. It differs from resolving two features, which the step still limits.'),
 ('2.9', 'fig2-09_reduction', 'Ch. 2, reduction and stitching (placeholders 22 to 25, replaces refl-reduction.png)',
  f'Reduction of measured CCD frames into a stitched reflectivity, ZnPc at {RD["E"]:.1f} eV, s polarization (CCD Scan 85302). '
  f'**a)** A 2 × 2 binned CCD frame at θ = {RD["frame"]["theta"]:.2f}° and {RD["frame"]["exposure"]:g} s on a logarithmic scale, with the specular region enlarged below. The specular counts are summed in a 13 × 13 pixel box on the spot (solid) and the background is the mean of two equal boxes 28 pixels to either side (dashed). '
  '**b)** Background-subtracted specular count rate, counts divided by the exposure t plus the shutter offset t₀ = 3.9 ms, with uncertainties, for the four series, each with its own exposure and higher order suppressor position, and the direct beam I₀ (star). Each new series repeats the last angles of the previous one. '
  f'**c)** Stitched reflectivity with propagated uncertainties, each series divided by I₀ (star, R = 1) and by the running product of stitch factors (S₂,₁ = {RD["S"][0]["S"]:.1f} ± {RD["S"][0]["dS"]:.1f}, S₃,₂ = {RD["S"][1]["S"]:.2f} ± {RD["S"][1]["dS"]:.2f}, S₄,₃ = {RD["S"][2]["S"]:.2f} ± {RD["S"][2]["dS"]:.2f}), each from an orthogonal-distance fit of R_n = S R_(n−1) through the origin on the overlap angles. Inset, R₂/R₁ at the overlap angles and S₂,₁ with its uncertainty (red band).',
  f'Frames, angles, exposures and HOS positions are the measured ones from 17 November 2024. The normalization and stitch follow pxr-reduce (https://github.com/ALS-RSOXS/pxr-reduce, PrsoxrLoader), with its shutter offset, direct-beam I₀, overlap selection that skips the repeated first frames, and ODR stitch fit. The spot and background boxes are set here (13 × 13 pixels, background averaged over both sides), without the dezinger and median filter that pxr-reduce applies, and without beam-current normalization, which changes the ring current at the 0.1 percent level for this scan. Only the first {RD["q_max"]:.2f} Å⁻¹ of this scan is shown. Error bars combine a {100*RD["rel_repeat"]:.1f} percent repeat scatter, the background floor, the stitch factor uncertainties and the I₀ scatter, so most are smaller than the markers.'),
 ('2.11', 'fig2-11_transfer-matrix', 'Ch. 2, simulating reflectivity (3A.3)',
  'Multiple reflections make exact solution of the stack necessary. '
  '**a)** Every interface reflects and transmits, and all reflected orders interfere at the detector. The field vector Ψ obeys ∂_zΨ = i(ω/c)ΔΨ in each layer, interface matrices L_i and propagation matrices P_i compose to the stack matrix Γ_N, and the reflection coefficients follow from Γ_N. Short strokes mark edge-on molecules in layer 1 and face-on molecules in layer 2, each layer uniaxial with ε = diag(ε_xx, ε_xx, ε_zz). The kinematic limit keeps only one reflection per interface. '
  '**b to d)** s-polarized reflectivity at 285.1 eV from the transfer matrix (red) and the kinematic approximation (black, dashed) for the Chapter 3 single film (b), an edge-on 100 Å layer over a face-on 90 Å layer (c), and six edge-on and face-on periods of 40 Å each (d). '
  f'The kinematic result diverges below the critical angle, misplaces the deep minima, and in the multilayer predicts Bragg structure that multiple reflections redistribute. The median deviation is {md["single film"]:.2f}, {md["bilayer"]:.2f}, and {md["multilayer, 6 periods"]:.2f} decades for b, c, and d.',
  'Exact 2x2 recursion per polarization, equal to the 4x4 Berreman result for an optic axis along the film normal. Kinematic curves use R = 16π²/q⁴ |Σ Δρ_j e^{iqz_j}|².'),
 ('2.12', 'fig2-12_interfaces', 'Ch. 2, interfaces and roughness (3A.4, requested)',
  'Three interface models with the same σ = 20 Å for a 192.7 Å ZnPc film on Si at 283.7 eV. '
  '**a)** Real-space pictures drawn at equal horizontal and vertical scale, with the wavelength λ = 43.7 Å marked along the lateral direction and 2σ at the right (red). Névot-Croce describes roughness with a short in-plane correlation length ξ, Debye-Waller roughness with a long ξ, and the graded interface describes interdiffusion with no in-plane structure. '
  '**b)** Depth profiles of δ_xx. Névot-Croce and Debye-Waller compute the same sharp profile (red) and the same laterally averaged error-function profile (black, dashed), so their depth profiles are identical. They differ only in the factor applied to each Fresnel coefficient, exp(−2k_{z,i}k_{z,i+1}σ²) for Névot-Croce and exp(−2k_{z,i}²σ²) for Debye-Waller, and therefore only in the reflectivity. The graded interface slices the error-function profile into 1 Å layers and computes it directly (red), with the sharp profile for reference (gray, dashed).',
  'Both damping factors match figlib.reflectivity. Real-space surfaces are illustrative Gaussian-filtered noise. The regime boundary between the two factors compares ξ with λ/(1 − cos θ), several thousand Å at these angles, which the text should state, since the λ bar gives only the length scale. At σ = 20 Å the s reflectivity of the two factors departs from the graded result by up to 28 percent (Névot-Croce) and 51 percent (Debye-Waller) below q = 0.15 Å⁻¹, if a number is wanted in the text.'),
 ('2.13', 'fig2-13_objective-transforms', 'Ch. 2, objective transforms (3B.2)',
  'Transforming the reflectivity changes where an unweighted objective looks for information. '
  '**a)** Simulated s-polarized reflectivity of the Chapter 3 film at 285.1 eV (points, with σ = aR + bq) and the model (red) on a linear scale. '
  '**b)** The same on log₁₀R. **c)** The same as Rq⁴, which removes the Fresnel q⁻⁴ decay. '
  '**d)** Misfit produced by a 2 Å thickness error in each representation, smoothed and scaled to its maximum, for R (black), log₁₀R (red), and Rq⁴ (red, dashed). An unweighted fit in R sees only the critical-angle region, log₁₀R concentrates on the fringe minima, and Rq⁴ spreads the misfit across the mid and high q range.',
  'With propagated uncertainties every transform gives the same weighted χ², so the choice matters only for unweighted or misweighted fits and for the shape of the noise distribution. Say so in the text.'),
 ('2.14',) + old['2.14'][1:],
 ('2.15', 'fig2-15_uncertainty', 'Ch. 2, parameter uncertainty (new, 3B.3)',
  'From a global optimum to parameter uncertainty on the Fig. 2.14 objective. '
  f'**a)** Differential evolution on log₁₀χ²_ν, with the population at generations 0 (gray), 4 (light red), and 8 (red), reaching ({U["x_de"][0]:.1f} Å, {U["x_de"][1]:.1f} Å) after {U["n_de"]} evaluations. The red box marks the basin enlarged in b and c. The population carries no curvature information. '
  f'**b)** The same log₁₀χ²_ν surface over that basin ({2*U["window"]["half"][0]:.2f} Å by {2*U["window"]["half"][1]:.2f} Å), with the DE best point (star), the final DE members inside the window (light red), and the local polish by L-BFGS-B (red, {U["n_lbfgs"]} evaluations) and Nelder-Mead (black, {U["n_nm"]} evaluations), both converging to ({U["x_min"][0]:.2f} Å, {U["x_min"][1]:.2f} Å). '
  f'**c)** Affine-invariant ensemble MCMC on the same surface and window as b, 32 walkers for 3000 steps after 1000 steps of burn-in, acceptance {U["acc"]:.2f}. '
  f'**d)** Posterior samples and 1σ and 2σ contours from MCMC (black, dashed), the finite-difference Hessian at the minimum (red), and the L-BFGS-B inverse Hessian (red, dotted). MCMC gives σ = {U["sd_mc"][0]:.3f} Å and {U["sd_mc"][1]:.3f} Å with correlation {U["corr_mc"]:.2f}, matching the finite-difference Hessian ({U["sd_fd"][0]:.3f} Å, {U["sd_fd"][1]:.3f} Å, {U["corr_fd"]:.2f}). The L-BFGS-B estimate overstates σ(t_bulk) at {U["sd_lbfgs"][0]:.3f} Å and understates the correlation at {U["corr_lbfgs"]:.2f}.',
  'L-BFGS-B builds its inverse Hessian from the few steps it takes, and after zero steps it returns the identity, so σ = 1 in fit units with no meaning. Check which Hessian produced the Chapter 3 error bars.'),
 ('2.16', 'fig2-16_automation', 'Ch. 2, autonomous measurement (restyled)',
  'Decision loop for autonomous reflectivity. A Gaussian process chooses the next condition (polarization, photon energy, and angle range) or the next sample. A new sample is found and passed to the alignment checker, and a new condition goes straight to it. A polarization change triggers a 15 min wait, and the sample is realigned unless it passes the check at 1° and 2°. Each condition is measured one series at a time, with the intensity optimized for the next series and data collected until the beam is lost, until the condition is complete (red), which returns control to the Gaussian process.',
  'Corrected from the original, which labeled both branches of condition complete as No.'),
 ('5.2',) + old['5.2'][1:],
 ('5.3', 'fig5-03_angle-convention', 'Ch. 5, angle dependence (placeholder 42)',
  'Polarization geometry stored with every trace. The incident wave (red) carries the electric field E, with θ the polar angle of E from the sample normal n̂ and φ its azimuth in the sample plane measured from x̂. Each trace keeps its ordered (θ, φ) pair, so geometries such as (90°, 45°) and (45°, 90°) remain distinct records.',
  'Matches e_field_polar and e_field_azimuth in the Atlas schema. Polar angles from −360° to 360° are accepted to allow laboratory motor angles.'),
 ('5.4',) + old['5.4'][1:],
 ('5.9', 'fig5-09_architecture', 'Ch. 5, programmatic access',
  'Architecture and optical model lineage. '
  '**a)** X-ray Atlas holds the database and files behind the web application and the REST /api/v1 interface. ORCID handles sign in and Zenodo issues DOIs. The browser reaches the web application, while the xrayatlas Python package and the xatlas command line client (red) share the REST interface. '
  '**b)** An optical model pins a dataset revision. The default model can be forked into independent versions (red), and a citation lists the model, its dataset revisions, and every ancestor in the chain.',
  'Matches the feat/optical-models design documents.'),
]

REMOVED = [
 ('fig1-02_history', 'removed at review'), ('fig1-03_transition-dipoles', 'replaced by Fig. 1.2 AR-NEXAFS'),
 ('fig1-04_roadmap', 'removed at review'), ('fig2-04_initial-final-states', 'folded into Fig. 1.2a'),
 ('fig2-08_dynamic-range', 'not used, kept in figs/new/_unused'), ('fig2-10_stitching-uncertainty', 'replaced by Fig. 2.9 built from real CCD frames'),
 ('fig4-04efg_preview', 'vetoed, replaced by a check of fig4_znpc_fits.ipynb against the updated ZnPc fit'),
]


def add_runs(p, text, size=10.5):
    for k, part in enumerate(re.split(r'\*\*(.+?)\*\*', text)):
        r = p.add_run(part); r.font.size = Pt(size)
        if k % 2: r.bold = True


d = docx.Document()
st = d.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10.5)
d.add_heading('Figure batch for the dissertation, captions and notes (revision 2)', 1)
d.add_paragraph('Generated 6 November 2026, revision 4. Every figure is sized to the 6.5 × 9 in text block of a letter page with 1 in margins, with 7 to 8.5 pt figure text against the 11 pt body. Every figure is in figs/new as PNG (300 dpi), SVG (editable text), and PDF. '
                'Captions follow the existing style with bold panel letters. Notes below each caption are for Harlan and are not part of the caption. '
                'Numbers follow the file names and will shift once the removed figures leave the sequence.')
for num, fn, where, cap, note in C:
    d.add_heading(f'Figure {num}', 2)
    q = d.add_paragraph(); r = q.add_run(f'{fn}   |   {where}'); r.font.size = Pt(8.5); r.italic = True
    q = d.add_paragraph(); r = q.add_run(f'Figure {num} '); r.bold = True; r.font.size = Pt(10.5)
    add_runs(q, cap)
    q = d.add_paragraph(); r = q.add_run('Note. ' + note); r.font.size = Pt(9); r.italic = True
d.add_heading('Removed or replaced', 2)
for fn, why in REMOVED:
    d.add_paragraph(f'{fn}, {why}', style='List Bullet')
d.add_paragraph('Reduction. Chapter 2 cites pxr-reduce (https://github.com/ALS-RSOXS/pxr-reduce) as the community reduction and stitching code in place of Fig. 2.10.')
d.save(f'{OUT}/figure-captions.docx')
bad = [(n, ch) for n, *_, cap, note in C for ch in (':', '–', '—') if ch in cap + note]
print('punctuation issues', bad, len(C), 'captions')
