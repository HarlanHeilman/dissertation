"""Slide 25, swap in the corrected Alq3 design figure (fitted bulk bookend, linearized posterior draws) and fix caption and notes."""
import sys
from pptx import Presentation
from pptx.util import Pt
SRC, OUT = sys.argv[1:3]
p = Presentation(SRC)
s = [s for s in p.slides if s.shapes.title is not None and s.shapes.title.text.startswith("How can we ensure")][0]
old = [sh for sh in s.shapes if sh.name == "Alq3 bulk design"][0]
x, y, w = old.left, old.top, old.width
old._element.getparent().remove(old._element)
pic = s.shapes.add_picture("/home/claude/assets/alq3_design.png", x, y, w); pic.name = "Alq3 bulk design"
pic._element.find(".//{http://schemas.openxmlformats.org/presentationml/2006/main}cNvPr").set("descr",
    "Left, specific refractivity beta/rho of the fitted surface, bulk and substrate bookends of the graded Alq3 fit. Centre, bulk beta/rho with the ten "
    "measured XRR energies (red), posterior draws (grey) that pinch at the measured energies, and the GP-chosen next energy "
    "at 288.60 eV. Right, uncertainty removed over 283 to 290 eV, 78 percent now, 86 percent with one GP energy, 98 percent "
    "for an energy scan at the same dose.")
cap = [sh for sh in s.shapes if sh.name == "Caption design"][0]
cap.text_frame.paragraphs[0].runs[0].text = ("Prior and noise as in Fig. 5.5, applied to the fitted Alq3 bulk. "
                                             "The energy scan spreads the dose of our ten energies across 283 to 290 eV.")
for r in cap.text_frame.paragraphs[0].runs[1:]:
    r.text = ""
nt = s.notes_slide.notes_text_frame
nt.text = "TIME 1.5 min"
for t in ["", "SOURCE Alq3 graded SOS fit (fig3 'graded', dft2+dft4+dft5+dft6+dft7, alq3_fig3_sos_tey), rebuilt with the fig3 "
              "builder (export_alq3_bulk.py) and analysed with alq3_design.py. The analysed spectrum is the fitted bulk bookend, "
              "bulk peak heights and bulk density 1.57 g/cm3. Prior and noise as dissertation Fig. 5.5, applied to its 17 peaks "
              "(location 0.25 eV, width and height log-normal 0.25 and 0.35, noise 1e-4 on beta and delta at each energy). "
              "Plotted as specific refractivity, beta divided by each bookend density, as on slide 24; the percentages are unchanged by the scaling. Linearized (Laplace) posterior; the grey draws, the bars and the GP picks all come from the same Gaussian. Metric is "
              "the fractional variance reduction of n integrated over 283 to 290 eV.",
          "", "SCRIPT On the left are the three spectra we actually fit, the surface, the bulk and the substrate side, and I take "
              "the bulk, in black. In the middle is that bulk spectrum with the ten energies we measured in red. Five sit in the "
              "pre-edge and on the first rise, five between 286.4 and 287.2. Every grey curve is a spectrum consistent with those "
              "measurements. At each measured energy they collapse onto the fit, down to the noise. Between 284.5 and 286.4 eV, "
              "where the 285.6 eV resonance lives, and above 287.2 eV, they spread almost as widely as before we measured. "
              "Together the ten energies remove 78 percent of the uncertainty in the bulk optical constants across the edge. If we "
              "ask a Gaussian process where to measure next, it picks 288.6 eV, and that one energy brings us to 86 percent. Or "
              "we spend the same beam time on a continuous energy scan across the edge, which gets to 98 percent. That is the "
              "case for measuring RSoXS as energy scans at buried interfaces.",
          "", "TRANSITION To summarize the second section.",
          "", "VERIFY Posterior sd of bulk beta is 0.005 to 0.09 x 1e-3 at the measured energies against a prior sd up to 1.57 "
              "x 1e-3, and 0.66 x 1e-3 at 285.3 eV (divide by 1.57 g/cm3 for beta/rho). Three greedy GP picks in order are 288.60, 285.35 and 289.40 eV, giving "
              "86, 93.5 and 96.5 percent. The energy scan is 71 points at 0.1 eV with noise 2.7e-4 per point, the dose of the ten "
              "energies, 98.3 percent. Measured energies are the resonant XRR set, 283.5 to 284.5 and 286.4 to 287.2 eV; 250 eV "
              "is excluded from this fit. The uncertainty collapses to the noise level at measured energies, not to exactly zero; "
              "setting the noise to zero would pinch it fully."]:
    nt.add_paragraph().text = t
p.save(OUT); print("saved")
