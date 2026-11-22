import re, docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_BREAK

C = [
 ('1.2', 'fig1-02_history', 'Ch. 1, history subsections (1.2, 1.3)',
  'Development of resonant soft X-ray characterization and the reflectivity methods this work builds on. '
  '**a)** Milestones in order, with reflectivity and optical modeling (red, filled) and resonant scattering and spectroscopy (black, open). Events are evenly spaced and not to scale in time. '
  '**b)** Measurement geometries discussed in this work, transmission RSoXS onto an area detector, specular reflectivity with momentum transfer q_z normal to the film, and grazing incidence with diffraction from ordered molecules.',
  'Each milestone needs its citation in the text (Parratt 1954, Berreman 1972, Névot and Croce 1980, Stöhr 1992, Dürr 1999 and Kortright 2000, Wang, Araki, and Ade 2005, Araki and Mitchell 2006, Virgili 2007, Wang 2010 and Gann 2012, Collins 2012, Tumbleston 2014, Thelen 2020, Murcia 2022, Ferron 2022 and 2023). Verify the years against the reference manager.'),
 ('1.3', 'fig1-03_transition-dipoles', 'Ch. 1, TDM paragraph (comment 18)',
  'Transition dipole moments set the polarization dependence of resonant absorption. '
  '**a)** ZnPc macrocycle seen edge on, with the π* transition dipole μ_π* along the macrocycle normal, an in-plane σ* dipole μ_σ*, and the electric field E at angle Θ to μ_π*. '
  '**b)** Absorption into a single transition scales as cos²Θ (red), and a dipole perpendicular to it as sin²Θ (black, dashed), crossing near the magic angle of 54.7°. '
  '**c)** Edge-on and face-on films and the resulting π* absorption for s polarization (E in the film plane) and p polarization near grazing incidence (E close to the film normal).',
  'Schematic. Bar heights in c are illustrative.'),
 ('1.4', 'fig1-04_roadmap', 'Ch. 1, roadmap paragraph (comment 24)',
  'Organization of this dissertation. Chapter 2 supplies the optical and reflectivity methods used by Chapters 3 and 4, which address questions Q1 and Q2 and questions Q3 and Q4, respectively. The Chapter 3 optical model carries into Chapter 4 (red arrow). Chapter 5 provides the reference spectra both chapters depend on (gray arrow), and Chapter 6 collects the answers.',
  'Optional figure.'),
 ('2.1', 'fig2-01_scattering-geometry', 'Ch. 2, scattering in the far field (replaces the current Fig. 2.1)',
  'Scattering geometries and momentum transfer. '
  '**a)** Transmission scattering of a plane wave E₀ = e^{ikz} with wavevector k by a finite scatterer into the far field, with scattered wavevector k′, scattering angle 2θ, and momentum transfer q = k′ − k of magnitude |q| = (4π/λ) sin θ. '
  '**b)** Specular reflection from a film on a substrate at grazing angle θ, where the momentum transfer q_z = (4π/λ) sin θ lies along the film normal. s polarization places E normal to the plane of incidence and p polarization places E in it.',
  'Panel a redraws the existing schematic in the same style and adds 2θ and |q| (comment 35).'),
 ('2.2', 'fig2-02_fraunhofer', 'Ch. 2, Fraunhofer regime (comments 37, 38, 39)',
  'Every measurement in this work lies deep in the far field. '
  '**a)** A scatterer of size a illuminated at wavelength λ and observed at distance L, with the Fresnel number F = a²/(Lλ) separating the near field (F ≳ 1) from the far field (F ≪ 1). '
  '**b)** F as a function of scatterer size at 284 eV (λ = 4.37 nm) for L = 0.1 m (gray, dashed) and L = 0.5 m (black). Vertical lines mark the π-stacking distance (0.34 nm), the ZnPc in-plane diameter (1.45 nm), the Chapter 3 film thickness (19.3 nm), and 100 nm domains. The far-field condition holds for every structure below a* = (Lλ)^{1/2} ≈ 47 µm at L = 0.5 m.',
  'Replace the lowercase l in the text with d and define a and L as in panel a. Correction to plan-v2, the beam footprint is not the relevant size, a* is.'),
 ('2.3', 'fig2-03_optical-constants', 'Ch. 2, optical constants and tensors (placeholders 13 to 15)',
  'Optical constants of the Chapter 3 ZnPc film from the refined building-block model. '
  '**a)** In-plane β_xx (red) and out-of-plane β_zz (black) of the edge-on film, with the bare-atom absorption (gray, dashed) and the pre-edge (270 to 282 eV) and post-edge (320 to 330 eV) normalization windows shaded. '
  '**b)** δ_xx and δ_zz from the Kramers-Kronig transform of β. Inset, the bare-atom β from 10 eV to 30 keV that closes the transform, with the measured window in red. '
  '**c)** Equivalent descriptions of the optical response through the atomic scattering factors f₁ and f₂, the permittivity ε, and the susceptibility χ, with β = λρμ_m/(4π) from the mass absorption μ_m.',
  'Computed from buildingblock.csv, nexafs.csv, and igor_mu.csv in lr-optical-models at ρ = 1.64 g cm⁻³, KK by exact integration of piecewise-linear β. Note that the KK equation in the draft has its sign flipped. With δ(E) = (2/π) P∫ E′β(E′)/(E² − E′²) dE′, δ is positive far above the edge as it must be.'),
 ('2.4', 'fig2-04_initial-final-states', 'Ch. 2, transition dipole moments (comment 43)',
  'Initial and final states of a carbon K-edge transition. '
  '**a)** Energy levels, with a photon near 285 eV promoting a C 1s electron into the lowest unoccupied π* orbital. '
  '**b)** The C 1s initial state is localized on a single carbon (black), while the π* final state is delocalized across the conjugated framework, drawn as p-orbital lobes of alternating phase (red and white) above and below the molecular plane. '
  '**c)** The resulting transition dipole μ_if = ⟨f|r|i⟩ is normal to the molecular plane, and the transition rate follows Fermi\'s golden rule, Γ ∝ |⟨f|e·r|i⟩|².',
  'Schematic. A computed π* isosurface from the ZnPc StoBe output can replace panel b if wanted.'),
 ('2.7', 'fig2-07_alignment', 'Ch. 2, sample alignment (placeholder 21)',
  'Iterative sample alignment at beamline 11.0.1.2. '
  '**a)** Knife-edge scan of the sample height, with the half-intensity point z₀ placing the sample surface at the beam center. '
  '**b)** Rocking scan in the flat geometry, showing the region where the sample blocks the beam, the rise once the surface is parallel to it, the added signal reflected onto the finite photodiode, and the cliff where the reflected beam leaves the diode. '
  '**c)** θ-2θ check with the detector at 2°, where the offset of the peak from 1° measures the residual angular misalignment. '
  '**d)** Convergence of the height and angle corrections over successive iterations.',
  'Illustrative curves, not measured scans. Replace with logged alignment scans if available.'),
 ('2.8', 'fig2-08_dynamic-range', 'Ch. 2, scan configuration',
  'Covering the reflectivity dynamic range with overlapping series. '
  '**a)** Simulated s-polarized reflectivity of the Chapter 3 ZnPc film at 285.1 eV (gray, right axis) and the counts per frame for each series (alternating black and red), with the incident flux of each series raised by the factor shown relative to the first. The dashed and dotted lines mark the 2¹⁶ pixel well and the CMOS noise floor of 30 counts. The deepest fringe near q = 0.135 Å⁻¹ falls below the floor. '
  '**b)** Dynamic range available from the detector, the higher-order suppressor (HOS, about three decades), and exposure time (0.002 to 10 s, 3.7 decades), for the CCD (floor near 500 counts, 8.8 decades in total) and the CMOS detector (10.0 decades), against the 6.7 decades this simulated profile requires.',
  'Model film 192.7 Å ZnPc (γ = 69.6°, ρ = 1.64 g cm⁻³, σ = 6.8 Å) on 15 Å SiO2 and Si. Series boundaries follow a simple rule (start a new series when the local maximum drops below 30 times the floor). Detector floors and suppressor and exposure ranges are the values stated in the Chapter 2 text.'),
 ('2.10', 'fig2-10_stitching-uncertainty', 'Ch. 2, stitching and measurement uncertainty (placeholders 22 to 25)',
  'Stitching and the reflectivity error budget. '
  '**a)** Counts from two consecutive series (n − 1 black, n red) measured at different incident flux, with the shared overlap points shaded. '
  '**b)** Ratio of the two series at each overlap point with counting errors and the inverse-variance weighted scale factor S_n (red line) and its uncertainty (band). '
  '**c)** Relative uncertainty components of the stitched reflectivity, counting statistics, background subtraction, the accumulated stitch scale uncertainty, and the empirical envelope aR + bq with a = 0.08 and b = 0.5 × 10⁻⁶ from Chapter 3, together with their sum in quadrature (red). The envelope dominates away from fringe minima.',
  'Simulated with Poisson counts on the Fig. 2.8 profile. Background (40 pixels at 9 counts² read variance) and stitch scale (1 percent per stitch) magnitudes are illustrative, a and b are the Chapter 3 values.'),
 ('2.11', 'fig2-11_transfer-matrix', 'Ch. 2, simulating reflectivity (3A.3)',
  'Transfer-matrix calculation of polarized reflectivity. '
  '**a)** Film stack with interface matrices L_i (red) and propagation matrices P_i (gray), the field vector Ψ obeying ∂_zΨ = i(ω/c)ΔΨ in each layer, and the stack matrix Γ_N from which the reflection coefficients follow. Edge-on molecules make the film uniaxial with ε = diag(ε_xx, ε_xx, ε_zz). '
  '**b, c)** s- and p-polarized reflectivity at 285.1 eV of the Chapter 3 ZnPc film treated as isotropic (black, trace-averaged index) and uniaxial (red). Anisotropy shifts the p-polarized fringes and removes the deep minima that the isotropic model predicts.',
  'Computed with an exact 2x2 recursion per polarization, which equals the 4x4 Berreman result when the optic axis is along the film normal. Can be regenerated with refloxide for consistency.'),
 ('2.12', 'fig2-12_interfaces', 'Ch. 2, interfaces and roughness (3A.4, requested)',
  'Interfacial roughness models and where each applies. '
  '**a)** Depth profile of δ_xx for a 192.7 Å ZnPc film on Si at 283.7 eV with σ = 15 Å. Névot-Croce and Debye-Waller keep the computed profile sharp (red) and act only as multiplicative damping of each Fresnel coefficient, so the error-function profile (gray, dashed) is a display convention. The graded interface replaces each interface with an error-function profile cut into 1 Å slices (red), the only one of the three that changes the profile itself. '
  '**b)** Reflectivity relative to the sharp-interface film for each model at σ = 15 Å. '
  '**c)** Ratio of the multiplicative models to the graded interface for σ = 5 Å (dashed) and 15 Å (solid). Névot-Croce stays within 0.6 percent at 5 Å and departs by up to 41 percent at 15 Å, Debye-Waller departs by up to 3 and 52 percent. '
  '**d)** Regimes of validity in σk_z and ξ/ξ_diff, with ξ the in-plane correlation length and ξ_diff = λ/(1 − cos θ). The red trajectory follows the Chapter 3 film (σ = 6.8 Å, assumed ξ = 50 nm) from q = 0.01 to 0.25 Å⁻¹, reaching σk_z = 0.85 in the crossover band at the highest q.',
  'Regime thresholds from the refloxide roughness selection guide. ξ = 50 nm is an assumption, replace with an AFM correlation length if one exists.'),
 ('2.13', 'fig2-13_objective-transforms', 'Ch. 2, objective transforms (3B.2)',
  'Transforming the reflectivity changes where an unweighted objective looks for information. '
  '**a)** Simulated s-polarized reflectivity of the Chapter 3 film at 285.1 eV (points, with σ = aR + bq) and the model (red) on a linear scale. '
  '**b)** The same on log₁₀R. **c)** The same as Rq⁴, which removes the Fresnel q⁻⁴ decay. '
  '**d)** Cumulative share of the thickness sensitivity (∂y/∂t)² carried by points below q for an unweighted objective in R (black), log₁₀R (red), and Rq⁴ (red, dashed). Half of it lies below q = 0.030, 0.135, and 0.162 Å⁻¹, respectively. With propagated uncertainties every transform gives the same weighted χ² (gray, dotted), so the choice matters only for unweighted or mis-weighted fits and for the shape of the noise distribution.',
  'This qualifies the plan text. log R and R q⁴ do not change a properly weighted χ², they change unweighted objectives and the Gaussian assumption.'),
 ('2.14', 'fig2-14_optimizers', 'Ch. 2, optimizers (3B.3, requested)',
  'Four optimizers on the same sharp, correlated, nonlinear reflectivity objective. The surface is log₁₀χ²_ν of s- and p-polarized reflectivity at 283.7 eV for the Chapter 3 film split into a bulk layer of thickness t_bulk and a buried interfacial layer of thickness t_int, fit on log R. Total thickness is sharply determined while the split between the layers is not, producing narrow tilted valleys around a single deep minimum (star, t_bulk = 178 Å, t_int = 15 Å). All runs start from the same point (black circle, 195 Å, 30 Å). '
  '**a)** Levenberg-Marquardt descends into the nearest valley and stops at (210.4 Å, 14.1 Å), log₁₀χ²_ν = 1.52, after 69 evaluations. '
  '**b)** L-BFGS-B reaches the same local minimum after 48 evaluations. '
  '**c)** Differential evolution population at generations 0 (gray), 4 (light red), and 39 (red), converging to the global minimum (178.0 Å, 15.0 Å), log₁₀χ²_ν = −0.58, after 984 evaluations. '
  '**d)** Random-walk Metropolis chain of 4000 steps at the true likelihood, which finds the minimum from this start but accepts only 1 percent of proposals in the sharp valley.',
  'Bulk layer γ = 69.6°, ρ = 1.64 g cm⁻³, σ = 6.8 Å, interfacial layer γ = 38°, ρ = 0.87 g cm⁻³, σ = 2 Å, on 15 Å SiO2 and Si, data with σ = aR + bq noise.'),
 ('4.4 e to g', 'fig4-04efg_preview', 'Ch. 4, tracing dipole evolution (comment 130), PREVIEW',
  'Depth dependence of the four refined resonances. '
  '**e)** Oscillator strength per molecule relative to the NEXAFS-refined value for the resonances at 284.2 (black), 285.1 (red), 287.1 (gray), and 288.9 eV (red, dashed) as a function of depth from the vacuum interface. '
  '**f)** Transition dipole cone angle ϑ of each resonance with depth. '
  '**g)** Strength per molecule against the local molecular tilt γ(z), with the SiO₂ side drawn thick and the vacuum side thin.',
  'Preview from the accepted fit (znpc_fig4/sos.json), which keeps cone angles constant with depth, so panel f is flat until the T4.3 local refit. Profiles use the Chapter 3 exponential form with τ_vac = 13 Å, τ_Si = 14.9 Å, and t = 192.7 Å, check against the pipeline. Rerun fig_ch4_ch5.py on the new checkpoint.'),
 ('5.2', 'fig5-02_normalization', 'Ch. 5, normalization and channels (placeholders 39 to 41)',
  'From raw signal to optical constants for the ZnPc dataset used in Chapter 3. '
  '**a)** Raw total electron yield at θ = 54.7° with the pre-edge (270 to 282 eV) and post-edge (320 to 330 eV) windows shaded. '
  '**b)** 0 to 1 normalization of every polarization geometry, from θ = 20° (red) to 90° (black), exposing the linear dichroism. '
  '**c)** Mass absorption after bare-atom normalization (black) against the bare-atom absorption of ZnPc (red, dashed). '
  '**d)** Isotropic β (black) and its Kramers-Kronig partner δ (red) at ρ = 1.64 g cm⁻³.',
  'Data from nexafs.csv and igor_mu.csv (X-ray Atlas accession 193bc0c5). Window choices are the ones used here, state the Atlas defaults if they differ.'),
 ('5.3', 'fig5-03_angle-convention', 'Ch. 5, angle dependence (placeholder 42)',
  'Polarization geometry stored with every trace. '
  '**a)** θ is the polar angle of the electric field E from the sample normal n̂ and φ is its azimuth in the sample plane measured from x̂. '
  '**b)** The geometries (90°, 45°) and (45°, 90°) are distinct records, so each trace keeps its ordered (θ, φ) pair.',
  'Matches e_field_polar and e_field_azimuth in the Atlas schema. Polar angles from −360° to 360° are accepted to allow laboratory motor angles.'),
 ('5.4', 'fig5-04_contribution-workflow', 'Ch. 5, contribution workflow (placeholders 43, 46)',
  'Contribution workflow. A contributor signs in with ORCID, resolves the molecule by InChI, SMILES, CAS number, or PubChem CID, describes the sample and the experiment, and maps the columns of each uploaded trace. Structural validation rejects malformed uploads before anything is stored (red). Accepted uploads are converted into optical density, mass absorption, β, and δ, scored by the quality metrics, recorded as revision 1.0.0 with a checksum of the derived columns, deposited to Zenodo under a versioned DOI, and published. A later change of normalization creates a new revision and a new Zenodo version (gray, dashed).',
  'Screenshots of the upload form (planned panel b) still need to be captured from the live site.'),
 ('5.9', 'fig5-09_architecture', 'Ch. 5, programmatic access',
  'Architecture and the optical model lineage. '
  '**a)** The web application and the REST /api/v1 interface share one database, a storage bucket for auxiliary files and tensors, and the Zenodo mirror. The browser, the xrayatlas Python package, and the xatlas command line client use the same routes, and the two programmatic clients share one credential file issued after ORCID sign in. '
  '**b)** Optical models pin a dataset revision. Every dataset has a default model, forks create independent models (red), an accepted merge proposal creates a new version with two parents (gray), and a citation carries the model, its linked dataset revisions, and every ancestor.',
  'Matches the feat/optical-models design documents.'),
]

def add_runs(p, text, size=10.5):
    for k, part in enumerate(re.split(r'\*\*(.+?)\*\*', text)):
        r = p.add_run(part); r.font.size = Pt(size)
        if k % 2: r.bold = True

d = docx.Document()
st = d.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10.5)
d.add_heading('Figure batch for the dissertation, captions and notes', 1)
p = d.add_paragraph('Generated 5 November 2026. Every figure is in figs/new as PNG (300 dpi), SVG (editable text), and PDF. Captions follow the existing style with bold panel letters. Notes below each caption are for Harlan and are not part of the caption.')
for num, fn, where, cap, note in C:
    d.add_heading(f'Figure {num}', 2)
    q = d.add_paragraph(); r = q.add_run(f'{fn}   |   {where}'); r.font.size = Pt(8.5); r.italic = True
    q = d.add_paragraph(); r = q.add_run(f'Figure {num} '); r.bold = True; r.font.size = Pt(10.5)
    add_runs(q, cap)
    q = d.add_paragraph(); r = q.add_run('Note. ' + note); r.font.size = Pt(9); r.italic = True
d.save('/home/claude/figs/out/figure-captions.docx')
bad = [(n, ch) for n, *_, cap, note in C for ch in (':', '–', '—') if ch in cap + note]
print('punctuation issues', bad)
