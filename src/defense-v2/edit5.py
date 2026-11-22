"""Slide 12 adds parameter-scaling charts; slide 25 becomes the Alq3 bulk design figure; full Fig. 4.3 goes to the
auxiliary section after 'ZnPc films on native-oxide silicon'. Helpers come from edit4.py."""
import sys, copy
src = open("/home/claude/cur/edit4.py").read()
exec(src[: src.index("# ---------------------------------------------------------------- slide 12")])
from pptx.chart.data import XyChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.util import Pt
from pptx.dml.color import RGBColor
FREE, DFT, GREY, INK, RED = "C65A11", "1F6FB0", "424C4E", "1F1F1F", "CA1237"
CARD_PROTO = copy.deepcopy(find([s for s in p.slides if s.shapes.title is not None and s.shapes.title.text == "TRADITIONAL VS DIRECT MEASUREMENT"][0], "Card models")._element)


def card(slide, x, y, w, h, name):
    el = copy.deepcopy(CARD_PROTO)
    c = el.find(".//p:cNvPr", NS); c.set("id", str(next_id(slide))); c.set("name", name)
    off = el.find(".//a:xfrm/a:off", NS); ext = el.find(".//a:xfrm/a:ext", NS)
    off.set("x", str(I(x))); off.set("y", str(I(y))); ext.set("cx", str(I(w))); ext.set("cy", str(I(h)))
    tree = slide.shapes._spTree
    first = [e for e in tree if etree.QName(e).localname in ("sp", "pic", "graphicFrame", "grpSp")]
    tree.insert(list(tree).index(first[0]), el)


def textbox(slide, x, y, w, h, paras, name):
    tb = slide.shapes.add_textbox(I(x), I(y), I(w), I(h)); tb.name = name
    tf = tb.text_frame; tf.word_wrap = True
    for i, (runs, after) in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); para.space_after = Pt(after)
        for t, size, bold, color in runs:
            r = para.add_run(); r.text = t; r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = RGBColor.from_string(color)
    return tb


def scaling_chart(slide, x, y, w, h, per_energy, const, color, name, label):
    cd = XyChartData(); s = cd.add_series(name)
    for n in range(1, 22):
        s.add_data_point(n, per_energy * n + const)
    gf = slide.shapes.add_chart(XL_CHART_TYPE.XY_SCATTER_LINES_NO_MARKERS, I(x), I(y), I(w), I(h), cd)
    gf.name = name
    ch = gf.chart; ch.has_legend = False
    ch.font.size = Pt(10); ch.font.color.rgb = RGBColor.from_string(GREY)
    ch.has_title = False
    ser = ch.plots[0].series[0]
    ser.format.line.color.rgb = RGBColor.from_string(color); ser.format.line.width = Pt(2.75); ser.smooth = False
    pt = ser.points[20]; dl = pt.data_label; dl.has_text_frame = True; dl.text_frame.text = label
    dl.position = XL_LABEL_POSITION.ABOVE
    rr = dl.text_frame.paragraphs[0].runs[0]; rr.font.size = Pt(14); rr.font.bold = True; rr.font.color.rgb = RGBColor.from_string(color)
    xa, ya = ch.category_axis, ch.value_axis
    xa.minimum_scale, xa.maximum_scale, xa.major_unit = 0, 21, 7
    ya.minimum_scale, ya.maximum_scale, ya.major_unit = 0, 100, 40
    ya.has_title = True; ya.axis_title.text_frame.text = "per slab"
    ry = ya.axis_title.text_frame.paragraphs[0].runs[0]; ry.font.size = Pt(10); ry.font.bold = False
    ry.font.color.rgb = RGBColor.from_string(GREY)
    xa.has_title = True; xa.axis_title.text_frame.text = "energies measured"
    rx = xa.axis_title.text_frame.paragraphs[0].runs[0]; rx.font.size = Pt(10); rx.font.bold = False
    rx.font.color.rgb = RGBColor.from_string(GREY)
    for ax in (xa, ya):
        ax.format.line.color.rgb = RGBColor.from_string("8A8F94")
    ya.has_major_gridlines = True; ya.major_gridlines.format.line.color.rgb = RGBColor.from_string("E3DED8")
    xa.has_major_gridlines = False
    return gf


# ---------------------------------------------------------------- slide 12, scaling with energy
s12 = [s for s in p.slides if s.shapes.title is not None and s.shapes.title.text == "TRADITIONAL VS DIRECT MEASUREMENT"][0]
for n in ("Stat free", "Stat ML-DFT", "Stat ML-DFT sub"):
    remove(find(s12, n))
scaling_chart(s12, 3.92, 3.80, 1.95, 1.50, 4, 0, FREE, "Free parameters vs energies", "84")
scaling_chart(s12, 8.22, 3.65, 1.93, 1.62, 0, 2, DFT, "ML-DFT parameters vs energies", "2")
nt = s12.notes_slide.notes_text_frame
nt.add_paragraph().text = ""
nt.add_paragraph().text = ("ADDED The small charts are parameters per slab against the number of energies fit. The free tensor adds four "
                           "constants per energy and reaches 84 at our 21 energies. The ML-DFT tensor stays at two, orientation and "
                           "density, however many energies we add, so every new energy tightens the same two numbers.")

# ---------------------------------------------------------------- slide 25, Alq3 bulk, measured energies, GP and energy scan
s25 = [s for s in p.slides if s.shapes.title is not None and s.shapes.title.text.startswith("How can we ensure")][0]
for n in ("Measured vs not measured", "Text gaps"):
    remove(find(s25, n))
pic = s25.shapes.add_picture(A + "alq3_design.png", I(0.72), I(2.12), I(11.9))
pic.name = "Alq3 bulk design"
pic._element.find(".//p:cNvPr", NS).set("descr", "Left, beta of the graded Alq3 fit at every depth, film centre in black. Centre, the film-centre beta with the ten measured XRR energies (red), spectra that agree with them (grey) and the GP-chosen next energy at 285.40 eV. Right, uncertainty removed over 283 to 290 eV, 79 percent now, 90 percent with one GP energy, 99 percent for an energy scan at the same dose.")
textbox(s25, 0.85, 6.33, 11.6, 0.5, [([("Prior and noise as in Fig. 5.5, applied to the fitted Alq3 film centre. "
                                        "The energy scan spreads the dose of our ten energies across 283 to 290 eV.", 12, False, GREY)], 0)],
        "Caption design")
ns_ = s25.notes_slide.notes_text_frame
ns_.text = "TIME 1.5 min"
for t in ["", "SOURCE Alq3 graded SOS fit (fig3 'graded', dft2+dft4+dft5+dft6+dft7, alq3_fig3_sos_tey), rebuilt with the fig3 builder "
              "(export_alq3_bulk.py) and analysed with alq3_design.py. Film centre, z = L/2 of 237 A. Prior and noise as dissertation "
              "Fig. 5.5, applied to the 17 peaks of the film-centre spectrum (location 0.25 eV, width and height log-normal 0.25 and 0.35, "
              "noise 1e-4 on beta and delta at each energy), Laplace posterior, variance of n integrated over 283 to 290 eV.",
          "", "SCRIPT Let us take the actual film. On the left is the fitted Alq3 film at every depth, and I pick its centre, in black. "
              "In the middle is that spectrum with the ten energies we measured in red. Five sit in the pre-edge and on the first "
              "rise, five sit between 286.4 and 287.2. Every grey curve agrees with those ten points as well as the fit does. They "
              "agree where we measured, and between 284.5 and 286.4 eV, right where the 285.6 eV resonance from the last slide lives, "
              "they spread widely, and above 287.2 we know very little. Together the ten energies remove 79 percent of the uncertainty "
              "in the optical constants across the edge. If we ask a Gaussian process where to measure next, it puts the next energy at "
              "285.4 eV, in that gap, and one more energy brings us to 90 percent. Or we change how we collect, and spend the same beam "
              "time on a continuous energy scan across the edge, which gets to 99 percent. That is the case for measuring RSoXS as "
              "energy scans at buried interfaces.",
          "", "TRANSITION To summarize the second section.",
          "", "VERIFY Three greedy GP picks in order are 285.40, 288.60 and 289.40 eV, giving 90, 95 and 97 percent. The energy "
              "scan is 71 points at 0.1 eV with noise 2.7e-4 per point, the dose of the ten energies. The fitted bulk anchor is not "
              "used because the substrate-side decay length sits at its 240 A bound, so the film never reaches it; the film centre is "
              "the bulk the film has. Measured energies are the resonant XRR set, 283.5 to 284.5 and 286.4 to 287.2 eV; 250 eV is "
              "excluded from this fit."]:
    ns_.add_paragraph().text = t

# ---------------------------------------------------------------- auxiliary, full Fig. 4.3
anchor = [s for s in p.slides if s.shapes.title is not None and s.shapes.title.text == "ZnPc films on native-oxide silicon"][0]
ns = p.slides.add_slide(anchor.slide_layout)
lst = p.slides._sldIdLst; ids = list(lst); new = ids[-1]; lst.remove(new)
lst.insert([int(e.get("id")) for e in lst].index(anchor.slide_id) + 1, new)
for sh in list(ns.shapes):
    remove(sh)
for sh in anchor.shapes:
    if sh.is_placeholder:
        ns.shapes._spTree.append(copy.deepcopy(sh._element))
for sh in ns.shapes:
    if sh.is_placeholder and sh.placeholder_format.type == 1:
        runs = sh.text_frame.paragraphs[0].runs
        runs[0].text = "Free and ML-DFT slab fits compared"
        for r in runs[1:]:
            r.text = ""
card(ns, 0.60, 2.05, 5.30, 4.85, "Card figure")
card(ns, 6.10, 2.05, 6.65, 4.85, "Card caption")
f43 = fp.slides[14]
full = pick(f43, 4.80, 0.80, 8.30, 6.60)
make_group(ns, f43, full, 0.0, 2.12, h=4.70, name="Fig 4.3 (native)")
grp = ns.shapes[-1]; place(grp, 0.60 + (5.30 - grp.width / EMU) / 2, 2.12)
textbox(ns, 6.30, 2.20, 6.30, 4.60, [
    ([("(a) Birefringence and dichroism of each slab", 15, True, RED)], 3),
    ([("Free-tensor constants at every energy (orange) against the ML-DFT tensor (blue). The bulk free constants follow the "
       "ML-DFT curves; surface and interface carry error bars as large as the signal.", 13, False, INK)], 12),
    ([("(b) Model selection", 15, True, RED)], 3),
    ([("Parameter count N, reduced χ², AIC and BIC for the two three-slab models; lower is better. ML-DFT uses 17 "
       "parameters against 286, fits better (χ²ᵥ 6.9 against 9.4) and is preferred by both information criteria "
       "(AIC 220 against 781, BIC 819 against 2973).", 13, False, INK)], 12),
    ([("Dissertation Fig. 4.3.", 12, False, GREY)], 0)], "Caption Fig 4.3")
nsl = ns.notes_slide
if nsl.notes_placeholder is None:
    srcn = [x for x in p.slides if x.has_notes_slide and x.notes_slide.notes_placeholder is not None][0]
    nsl.shapes._spTree.append(copy.deepcopy(srcn.notes_slide.notes_placeholder._element))
nsl.notes_placeholder.text_frame.text = ("SOURCE Dissertation Fig. 4.3, copied from figs_1.pptx (native picture and legend). "
                                        "Backup for the model comparison on slide 12; the AIC and BIC values live here rather than in the main talk.")
p.save(OUT)
print("saved", len(p.slides))
