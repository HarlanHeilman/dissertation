"""Slide 25 as a three-step PowerPoint build. Stacked transparent image layers on identical axes, every word a PowerPoint
text box, fade animations on click.
  On arrival   grey spectra that fit the 10 measured energies
  Click 1      grey out; pink (ruled out) and blue survivors of one GP energy in; GP texts in
  Click 2      GP layer and texts out; thin band of a coarse full-spectrum scan in; scan texts in"""
import sys, json, copy
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from lxml import etree

SRC, OUT = sys.argv[1:3]
A = "/home/claude/assets/"
LAY = json.load(open(A + "l25_layout.json"))
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
I = lambda v: int(round(v * 914400))
p = Presentation(SRC)
s = [s for s in p.slides if s.shapes.title is not None and s.shapes.title.text.startswith("How can we ensure")][0]
for sh in list(s.shapes):
    if sh.name in ("Alq3 bulk design",) or sh.name.startswith(("L25 ", "T25 ")):
        sh._element.getparent().remove(sh._element)
old_t = s._element.find("{%s}timing" % P)
if old_t is not None:
    s._element.remove(old_t)

X0, Y0, WP = 0.85, 2.10, 11.6
FW, FH = LAY["fig"]; HP = WP * FH / FW


def fx(f):
    return X0 + f * WP


def fy(f):
    return Y0 + (1 - f) * HP


def ex(e, axkey):
    l, b, w, h = LAY["axes"][axkey]
    return fx(l + w * (e - 283.0) / 7.0)


ids = {}
for name in ("base", "grey", "tossed", "gp", "band", "top"):
    pic = s.shapes.add_picture(A + f"l25_{name}.png", I(X0), I(Y0), I(WP)); pic.name = f"L25 {name}"
    ids[name] = pic.shape_id
alt = {"base": "Axes, and the fitted surface, bulk and substrate specific refractivity of the graded Alq3 fit.",
       "grey": "Bulk spectra that fit the ten measured energies.",
       "tossed": "The same spectra, ruled out by the next measurement.",
       "gp": "Spectra that still fit after one more energy at 288.8 eV, chosen by a Gaussian process.",
       "band": "Thin band of a coarse full-spectrum measurement around the bulk optical constants.",
       "top": "Bulk fit with the ten measured energies as red circles."}
for sh in s.shapes:
    if sh.name.startswith("L25 "):
        sh._element.find(".//{%s}cNvPr" % P).set("descr", alt[sh.name[4:]])


def text(name, x, y, w, h, paras, align="l"):
    tb = s.shapes.add_textbox(I(x), I(y), I(w), I(h)); tb.name = name
    tf = tb.text_frame; tf.word_wrap = True
    for i, (t, size, bold, color) in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = {"l": PP_ALIGN.LEFT, "r": PP_ALIGN.RIGHT, "c": PP_ALIGN.CENTER}[align]
        para.space_after = Pt(1)
        r = para.add_run(); r.text = t; r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = RGBColor.from_string(color)
    ids[name] = tb.shape_id
    return tb


RED, BLUE, GREY, DARK, INK, TOSS = "CA1237", "23476B", "6B7177", "424C4E", "1F1F1F", "C2707D"
lA, bA, wA, hA = LAY["axes"]["Ab"]; lB, bB, wB, hB = LAY["axes"]["Bb"]
text("T25 title film", fx(lA) - 0.05, fy(bA + hA) - 0.40, 3.2, 0.36, [("Fitted film  (10⁻³ cm³/g)", 14, True, INK)])
text("T25 title bulk", fx(lB) - 0.05, fy(bB + hB) - 0.40, 6.5, 0.36, [("Bulk, through our 10 measured energies", 14, True, INK)])
text("T25 legend", fx(lA + wA) - 1.25, fy(bA + hA) + 0.02, 1.2, 0.75,
     [("surface", 12, False, "A51C30"), ("bulk", 12, True, "000000"), ("substrate", 12, False, "3A84C1")], align="r")
tx, ty = fx(lB) + 0.10, fy(bB + hB) + 0.02
text("T25 s1", tx, ty, 4.6, 0.4, [("Every grey curve fits our 10 measured energies", 14, True, DARK)])
text("T25 s2", tx, ty, 4.6, 0.85, [("One more energy, chosen by a Gaussian process", 14, True, BLUE),
                                   (f"{LAY['gp_survive']} of {LAY['pool']:,} still fit, {LAY['gain_gp']:.1f}× more certain", 13, False, INK)])
lD, bD, wD, hD = LAY["axes"]["Bd"]
kx, ky = ex(285.9, "Bd"), fy(bD) - 0.40
text("T25 s2 key", kx, ky, 3.6, 0.32, [("blue still fits, pink is ruled out", 12.5, False, GREY)])
gx = ex(LAY["gp_ev"], "Bb")
text("T25 gp label", gx - 1.30, fy(bB + hB) + 0.02, 1.22, 0.32, [(f"{LAY['gp_ev']:.1f} eV", 13, True, BLUE)], align="r")
text("T25 s3", tx, ty, 4.6, 0.85, [("Full spectrum, measured coarsely", 14, True, DARK),
                                   (f"{LAY['scan_survive']} of {LAY['pool']:,} still fit, {round(LAY['gain_scan'], -1):.0f}\u00d7 more certain", 13, False, INK)])
text("T25 s3 key", kx, ky, 3.6, 0.32, [("every pink curve leaves the thin band", 12.5, False, GREY)])

# ---------------------------------------------------------------- animation
cid = [2]


def nid():
    cid[0] += 1
    return cid[0]


def eff(spid, kind, node, grp):
    """Fade entrance or exit as a p:par string."""
    vis = "visible" if kind == "in" else "hidden"
    setc = (f'<p:set><p:cBhvr><p:cTn id="{nid()}" dur="1" fill="hold"><p:stCondLst><p:cond delay="{0 if kind == "in" else 499}"/></p:stCondLst></p:cTn>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
            f'<p:to><p:strVal val="{vis}"/></p:to></p:set>')
    fade = (f'<p:animEffect transition="{kind}" filter="fade"><p:cBhvr><p:cTn id="{nid()}" dur="500"/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect>')
    body = setc + fade if kind == "in" else fade + setc
    cls = "entr" if kind == "in" else "exit"
    return (f'<p:par><p:cTn id="{nid()}" presetID="10" presetClass="{cls}" presetSubtype="0" fill="hold" grpId="{grp}" nodeType="{node}">'
            f'<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>{body}</p:childTnLst></p:cTn></p:par>')


grp_count, bld = {}, []
TEXT_IDS = {v for k, v in ids.items() if k.startswith("T25 ")}


def click(steps):
    effs = []
    for j, (key, kind) in enumerate(steps):
        spid = ids[key]
        g = grp_count.get(spid, 0); grp_count[spid] = g + 1
        if spid in TEXT_IDS:
            bld.append(f'<p:bldP spid="{spid}" grpId="{g}"/>')
        effs.append(eff(spid, kind, "clickEffect" if j == 0 else "withEffect", g))
    return (f'<p:par><p:cTn id="{nid()}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst><p:childTnLst>'
            f'<p:par><p:cTn id="{nid()}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
            + "".join(effs) + '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>')


c1 = click([("grey", "out"), ("T25 s1", "out"), ("tossed", "in"), ("gp", "in"), ("T25 s2", "in"), ("T25 s2 key", "in"), ("T25 gp label", "in")])
c2 = click([("gp", "out"), ("T25 s2", "out"), ("T25 s2 key", "out"), ("T25 gp label", "out"), ("band", "in"), ("T25 s3", "in"), ("T25 s3 key", "in")])
timing = (f'<p:timing xmlns:p="{P}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
          f'<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>{c1}{c2}</p:childTnLst></p:cTn>'
          '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
          '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
          f'</p:childTnLst></p:cTn></p:par></p:tnLst><p:bldLst>{"".join(bld)}</p:bldLst></p:timing>')
t_el = etree.fromstring(timing)
root = s._element
after = root.find("{%s}clrMapOvr" % P)
tr = root.find("{%s}transition" % P)
anchor = tr if tr is not None else after
anchor.addnext(t_el)

# caption and notes
cap = [sh for sh in s.shapes if sh.name == "Caption design"][0]
cap.text_frame.paragraphs[0].runs[0].text = ("Full spectrum at the same beam time as our 10 energies. A spectrum survives if it agrees within 2\u03c3 at every new point.")
for r in cap.text_frame.paragraphs[0].runs[1:]:
    r.text = ""
nt = s.notes_slide.notes_text_frame
nt.text = "TIME 2 min, two clicks"
for t in ["", "SOURCE Alq3 graded SOS fit (fig3 'graded', alq3_fig3_sos_tey), rebuilt with export_alq3_bulk.py; analysis "
              "alq3_design.py, layers alq3_layers.py. Fitted bulk, peak heights and density 1.57 g/cm3, plotted as specific "
              "refractivity. Prior as dissertation Fig. 5.5 on the 17 peaks; each measured energy fixes bulk beta and delta within "
              "1e-5. 200,000 spectra are drawn from the posterior given the ten energies; a new measurement keeps a spectrum if it "
              "agrees within 2 sigma at every new point.",
          "", "SCRIPT On arrival. On the left are the three spectra we fit, surface, bulk and substrate, per unit density. On the "
              "right is the bulk, absorption and dispersion, with our ten measured energies in red. Every grey curve goes through all "
              "ten measurements. They agree where we measured and disagree everywhere else, between 284.5 and 286.4 eV and above "
              "287.2 eV. That is how uncertain we really are.",
          "", "CLICK 1. So what should we measure next? A Gaussian process picks the single most useful energy, 288.8 eV. Of "
              f"200,000 spectra that fit our data, only {LAY['gp_survive']} also fit that one new point. Pink is ruled out, blue "
              "survives. That makes us about two and a half times more certain overall, but look at the blue curves, between 285 and "
              "286 eV they still go everywhere.",
          "", "CLICK 2. Now spend the same beam time on the whole spectrum instead, measured coarsely, every point less precise. "
              "That is this thin band. Not one of the 200,000 spectra stays inside it everywhere. The coarse full spectrum makes us "
              "hundreds of times more certain. So the next step is to measure the whole energy range at buried interfaces, even if "
              "we measure it weakly.",
          "", "TRANSITION To summarize the second section.",
          "", f"VERIFY Survival with a 2 sigma window, GP point {LAY['gp_survive']} of 200,000 (0.13 percent), coarse scan 0 of "
              "200,000 (one survives at 4 sigma). More certain is the ratio of remaining posterior variance of n over 283 to 290 eV, "
              "10.8 percent now, 4.2 percent with the GP energy (2.6 times), 0.025 percent with the scan (430 times). Scan is 71 "
              "points at 0.1 eV, noise 2.7e-5 each, same total dose as the ten energies. Numbers depend on the assumed noise; at "
              "1e-4 the variance figures are 78, 86 and 98 percent removed. Measured energies are the resonant XRR set, 283.5 to "
              "284.5 and 286.4 to 287.2 eV."]:
    nt.add_paragraph().text = t
p.save(OUT); print("saved", ids)
