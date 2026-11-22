"""Slide 25, beta/rho and delta/rho with pinned measurements and on-plot annotations; caption and notes to match."""
import sys
from pptx import Presentation
SRC, OUT = sys.argv[1:3]
I = lambda v: int(round(v * 914400))
p = Presentation(SRC)
s = [s for s in p.slides if s.shapes.title is not None and s.shapes.title.text.startswith("How can we ensure")][0]
old = [sh for sh in s.shapes if sh.name == "Alq3 bulk design"][0]
old._element.getparent().remove(old._element)
pic = s.shapes.add_picture("/home/claude/assets/alq3_design.png", I(0.85), I(2.10), I(11.6)); pic.name = "Alq3 bulk design"
pic._element.find(".//{http://schemas.openxmlformats.org/presentationml/2006/main}cNvPr").set("descr",
    "Left, specific refractivity beta/rho and delta/rho of the fitted surface, bulk and substrate of the graded Alq3 fit. "
    "Right, bulk beta/rho and delta/rho with the ten measured XRR energies (red circles); grey posterior draws pass through "
    "every measured point and spread between them. One more energy at 288.8 eV, chosen by a Gaussian process, makes the "
    "bulk 2.6 times more certain; the full spectrum measured coarsely with the same beam time makes it 430 times more certain.")
cap = [sh for sh in s.shapes if sh.name == "Caption design"][0]
cap.top, cap.height = I(6.55), I(0.33)
cap.text_frame.paragraphs[0].runs[0].text = ("The full spectrum uses the same beam time as our 10 energies, spread over every point.")
for r in cap.text_frame.paragraphs[0].runs[1:]:
    r.text = ""
nt = s.notes_slide.notes_text_frame
nt.text = "TIME 1.5 min"
for t in ["", "SOURCE Alq3 graded SOS fit (fig3 'graded', dft2+dft4+dft5+dft6+dft7, alq3_fig3_sos_tey), rebuilt with the fig3 "
              "builder (export_alq3_bulk.py) and analysed with alq3_design.py. Analysed spectrum is the fitted bulk, bulk peak "
              "heights and bulk density 1.57 g/cm3, plotted as specific refractivity like slide 24. Prior as dissertation Fig. 5.5 "
              "on its 17 peaks (location 0.25 eV, width and height log-normal 0.25 and 0.35). Each measured energy fixes bulk beta "
              "and delta to within 1e-5, about half a percent of the beta peak, so the traces pass through the points. Linearized "
              "posterior; the grey draws, the percentages and the GP pick come from the same Gaussian. Metric is the fractional "
              "variance reduction of n integrated over 283 to 290 eV.",
          "", "SCRIPT On the left are the three spectra we actually fit, surface, bulk and substrate side, per unit density, and "
              "I take the bulk. On the right is that bulk, absorption on top and dispersion below, with the ten energies we "
              "measured as red circles. Every grey curve is a bulk spectrum that goes through all ten measurements. Where we "
              "measured, they are pinned. Between 284.5 and 286.4 eV, where the 285.6 eV resonance lives, and above 287.2 eV, "
              "they still disagree, in both beta and delta. So what do we measure next? A Gaussian process says the most useful "
              "single energy is 288.8 eV, and adding it makes the bulk about two and a half times more certain. Or we take the "
              "same beam time and spread it over the whole spectrum, measuring every point more coarsely, and the bulk becomes "
              "hundreds of times more certain. That is the case for collecting RSoXS as energy scans at buried interfaces.",
          "", "TRANSITION To summarize the second section.",
          "", "VERIFY More certain is the ratio of remaining posterior variance of n over 283 to 290 eV, 10.8 percent now, 4.2 percent with the GP energy (2.6 times), 0.025 percent with the scan (430 times). Posterior sd of bulk beta at the measured energies is 0.004 to 0.010 x 1e-3, against 0.54 x 1e-3 at 288.5 "
              "eV and a prior sd up to 1.57 x 1e-3 (divide by 1.57 g/cm3 for beta/rho). Three greedy GP picks in order are 288.80, "
              "289.40 and 285.45 eV, giving 96, 98 and 99 percent. The energy scan is 71 points at 0.1 eV with noise 2.7e-5 per "
              "point, the dose of the ten energies, 99.97 percent. The percentages depend on the assumed noise; at 1e-4, as in "
              "Fig. 5.5, they are 78, 86 and 98 percent with the GP pick at 288.6 eV. Measured energies are the resonant XRR set, "
              "283.5 to 284.5 and 286.4 to 287.2 eV; 250 eV is excluded from this fit."]:
    nt.add_paragraph().text = t
p.save(OUT); print("saved")
