"""Merge slides 8 and 9 into one slide (slide 8 keeps its title). Left: symmetrized slide-7 transitions GIF (g15), model
and 'why not DFT alone' cards. Right: clustering GIF with the ionization edge (g14), three steps, a Victor card.
Slide 9 is removed. Three click builds: why-not card; clustering panel; Victor card."""
import sys, copy
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from lxml import etree

SRC, OUT = sys.argv[1:3]
G = "/home/claude/omgif/out/"
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
P_ = "{%s}" % NS["p"]; A_ = "{%s}" % NS["a"]
I = lambda v: int(round(v * 914400))
p = Presentation(SRC)
s8 = [s for s in p.slides if s.shapes.title is not None and s.shapes.title.text.startswith("USING DFT TO REVEAL")][0]
s9 = [s for s in p.slides if s.shapes.title is not None and s.shapes.title.text.startswith("CLUSTERING MAKES DFT")][0]
sh8 = {x.name: x for x in s8.shapes}
sh9 = {x.name: x for x in s9.shapes}
PROTO = {k: copy.deepcopy(sh9[k]._element) for k in ("Rounded Rectangle 7", "Rounded Rectangle 28", "Step card 1", "Step badge 1", "Step title 1")}
VICTOR = sh9["Victor photo"]
open("/tmp/victor2." + VICTOR.image.ext, "wb").write(VICTOR.image.blob)
VCROP = (VICTOR.crop_left, VICTOR.crop_top, VICTOR.crop_right, VICTOR.crop_bottom)
VASP = VICTOR.width / VICTOR.height
notes8 = s8.notes_slide.notes_text_frame.text
notes9 = s9.notes_slide.notes_text_frame.text

for n in ("Group 19", "Group 20", "Rounded Rectangle 45", "DFT transitions GIF", "DFT strip caption"):
    sh8[n]._element.getparent().remove(sh8[n]._element)
t_old = s8._element.find(P_ + "timing")
if t_old is not None:
    s8._element.remove(t_old)
tree = s8.shapes._spTree


def next_id():
    return max(int(e.get("id")) for e in tree.iter(P_ + "cNvPr")) + 1


def clone(key, name, x, y, w, h):
    el = copy.deepcopy(PROTO[key])
    c = el.find(".//p:cNvPr", NS); c.set("id", str(next_id())); c.set("name", name)
    for e in c.findall("a:extLst", NS):
        c.remove(e)
    off = el.find(".//a:xfrm/a:off", NS); ext = el.find(".//a:xfrm/a:ext", NS)
    off.set("x", str(I(x))); off.set("y", str(I(y))); ext.set("cx", str(I(w))); ext.set("cy", str(I(h)))
    tree.append(el)
    return el


def set_text(el, t, size=None):
    ps = el.findall(".//a:p", NS)
    rs = ps[0].findall("a:r", NS)
    rs[0].find("a:t", NS).text = t
    for r in rs[1:]:
        ps[0].remove(r)
    if size:
        for rp in el.iter(A_ + "rPr"):
            rp.set("sz", str(int(size * 100)))
        for rp in el.iter(A_ + "endParaRPr"):
            rp.set("sz", str(int(size * 100)))


def place(shape, x, y, w=None, h=None):
    shape.left, shape.top = I(x), I(y)
    if w is not None:
        shape.width = I(w)
    if h is not None:
        shape.height = I(h)


def text(name, x, y, w, h, paras, align="l", anchor=None):
    tb = s8.shapes.add_textbox(I(x), I(y), I(w), I(h)); tb.name = name
    tf = tb.text_frame; tf.word_wrap = True
    if anchor:
        tf._txBody.find("a:bodyPr", NS).set("anchor", anchor)
    for i, (t, size, bold, color, after) in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER}[align]; para.space_after = Pt(after)
        r = para.add_run(); r.text = t; r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = RGBColor.from_string(color)
    return tb


def gif(path, name, x, y, w, descr):
    pc = s8.shapes.add_picture(path, I(x), I(y), I(w)); pc.name = name
    pc._element.find(".//p:cNvPr", NS).set("descr", descr)
    return pc


def sid(name):
    return str([x for x in s8.shapes if x.name == name][0].shape_id)


def to_front(name):
    el = [x for x in s8.shapes if x.name == name][0]._element
    tree.remove(el); tree.append(el)


# ---------------------------------------------------------------- left, DFT
gif(G + "znpc-dft-transitions.gif", "DFT transitions GIF", 0.60, 2.12, 6.0,
    "ZnPc, the five symmetrized transition-potential DFT transitions of the previous slide. Left, the molecule with the "
    "core-hole carbons lit; right, the final orbital and dipoles at the 8 equivalent carbons; bottom, every raw DFT "
    "transition from 283.5 to 300 eV coloured by carbon site, the current one highlighted, under the measured isotropic NEXAFS (solid) and the DFT spectrum after its static +0.45 eV energy correction (dashed), each normalized to its pi* peak.")
cap = text("DFT strip caption", 0.75, 4.84, 5.7, 0.28, [("measured NEXAFS", 11.5, True, "2E3538", 0)], align="c")
for t_, c_, b_ in (("   against   ", "6B7476", False), ("DFT, +0.45 eV static shift", "B4532F", True),
                   (",   sticks by carbon site", "6B7476", False)):
    r_ = cap.text_frame.paragraphs[0].add_run(); r_.text = t_; r_.font.size = Pt(11.5); r_.font.bold = b_
    r_.font.color.rgb = RGBColor.from_string(c_)
to_front("Graphic 9"); place(sh8["Graphic 9"], 0.66, 2.10, 0.95, 0.30)
to_front("Rounded Rectangle 44"); place(sh8["Rounded Rectangle 44"], 4.45, 1.82, 2.15, 0.38)
for rp in sh8["Rounded Rectangle 44"]._element.iter(A_ + "rPr"):
    rp.set("sz", "1500")
place(sh8["Rounded Rectangle 15"], 0.60, 5.22, 6.0, 1.70)
place(sh8["TextBox 41"], 0.68, 5.25, 2.95, 1.62)
place(sh8["Why not DFT alone"], 3.62, 5.25, 2.95, 1.62)
BUL = {"TextBox 41": ["Rigid, no dihedral angles", "Geometry from the crystal", "4 carbon sites, 8 of each",
                      "StoBe TP-DFT, IGLO-III"],
       "Why not DFT alone": ["A sea of 2,924 transitions", "Energies off by 0.3 eV or more", "One molecule, in vacuum",
                             "Widths put in by hand"]}
for n, items in BUL.items():
    ps = sh8[n]._element.findall(".//a:p", NS)
    while len(ps) - 1 < len(items):
        ps[-1].addnext(copy.deepcopy(ps[-1])); ps = sh8[n]._element.findall(".//a:p", NS)
    for p_, t in zip(ps[1:], items):
        rs = p_.findall("a:r", NS); rs[0].find("a:t", NS).text = t
        for r in rs[1:]:
            p_.remove(r)
    for rp in sh8[n]._element.iter(A_ + "rPr"):
        if rp.get("sz") == "1300":
            rp.set("sz", "1350")

# ---------------------------------------------------------------- right, clustering
XR, WR = 6.80, 5.95
clone("Rounded Rectangle 7", "Cluster card", XR, 2.08, WR, 2.86)
gif(G + "znpc-dft-clustering.gif", "Clustering GIF", XR + 0.07, 2.22, WR - 0.14,
    "ZnPc DFT transitions coloured by site, shifted by 0.45 eV, recoloured by cluster, collapsed into one Gaussian per "
    "cluster, joined by one ionization step per carbon site at its IP, then moved to the values refined against "
    "angle-resolved NEXAFS.")
chip = clone("Rounded Rectangle 28", "Cluster chip", XR + 0.75, 1.82, 4.45, 0.38)
set_text(chip, "Hierarchical spectral similarity clustering", 15)
steps = [("1", "Merge overlaps", "labels each resonance"),
         ("2", "Keep sites and dipoles", "orbitals and TDMs kept"),
         ("3", "Refine against NEXAFS", "dipoles held fixed")]
SW, SG, SY, SH = 1.85, 0.20, 5.04, 0.92
for i, (num, head, sub) in enumerate(steps):
    x = XR + i * (SW + SG)
    clone("Step card 1", f"Step card {num}", x, SY, SW, SH)
    b = clone("Step badge 1", f"Step badge {num}", x + 0.08, SY + 0.09, 0.30, 0.30)
    set_text(b, num, 12)
    tt = clone("Step title 1", f"Step title {num}", x + 0.44, SY + 0.07, SW - 0.50, 0.50)
    set_text(tt, head, 12.5)
    text(f"Step sub {num}", x + 0.08, SY + SH - 0.32, SW - 0.14, 0.28, [(sub, 10.5, False, "6B7476", 0)])
clone("Rounded Rectangle 7", "Victor card", XR, 6.06, WR, 0.86)
ph = s8.shapes.add_picture("/tmp/victor2.jpg", I(XR + 0.10), I(6.12), height=I(0.74))
ph.crop_left, ph.crop_top, ph.crop_right, ph.crop_bottom = VCROP
ph.width = int(ph.height * VASP); ph.name = "Victor photo"
ph._element.find(".//p:cNvPr", NS).set("descr", "Victor Murcia")
xv = XR + 0.10 + ph.width / 914400 + 0.14
text("Victor text", xv, 6.10, 3.2, 0.78, [("Clustering by Dr. Victor Murcia", 14, True, "424C4E", 1),
                                          ("Phys. Rev. Lett. 137, 158001, dft-learn", 11.5, False, "A51C30", 0)], anchor="ctr")
text("Victor stat", XR + WR - 1.75, 6.10, 1.65, 0.78, [("2,924 → 19", 17, True, "424C4E", 0),
                                                         ("clusters", 11.5, False, "6B7476", 0)], align="c", anchor="ctr")

# ---------------------------------------------------------------- click builds
cid = [2]


def nid():
    cid[0] += 1
    return cid[0]


def eff(spid, node, grp):
    setc = (f'<p:set><p:cBhvr><p:cTn id="{nid()}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
            f'<p:to><p:strVal val="visible"/></p:to></p:set>')
    fade = (f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{nid()}" dur="500"/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect>')
    return (f'<p:par><p:cTn id="{nid()}" presetID="10" presetClass="entr" presetSubtype="0" fill="hold" grpId="{grp}" nodeType="{node}">'
            f'<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>{setc}{fade}</p:childTnLst></p:cTn></p:par>')


TEXTY = set()
bld = []


def click(names):
    effs = []
    for j, n in enumerate(names):
        i_ = sid(n)
        if n in TEXTY:
            bld.append(f'<p:bldP spid="{i_}" grpId="0" animBg="1"/>')
        effs.append(eff(i_, "clickEffect" if j == 0 else "withEffect", 0))
    return (f'<p:par><p:cTn id="{nid()}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst><p:childTnLst>'
            f'<p:par><p:cTn id="{nid()}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
            + "".join(effs) + '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>')


TEXTY.update(["Why not DFT alone", "Step sub 1", "Step sub 2", "Step sub 3", "Victor text", "Victor stat"])
right = ["Cluster card", "Clustering GIF", "Cluster chip"] + [f"Step {k} {n}" for n in "123" for k in ("card", "badge", "title", "sub")]
c1 = click(["Why not DFT alone"])
c2 = click(right)
c3 = click(["Victor card", "Victor photo", "Victor text", "Victor stat"])
timing = (f'<p:timing xmlns:p="{NS["p"]}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
          f'<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>{c1}{c2}{c3}</p:childTnLst></p:cTn>'
          '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
          '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
          f'</p:childTnLst></p:cTn></p:par></p:tnLst><p:bldLst>{"".join(bld)}</p:bldLst></p:timing>')
anchor = s8._element.find(P_ + "transition")
if anchor is None:
    anchor = s8._element.find(P_ + "clrMapOvr")
anchor.addnext(etree.fromstring(timing))

# ---------------------------------------------------------------- notes
tf = s8.notes_slide.notes_text_frame
blocks = [
    "TIME 2.5 min, three clicks",
    "SOURCE StoBe transition-potential runs for the four inequivalent carbon sites of ZnPc (dft-learn, znpc-cif), 731 "
    "transitions per site, 2,924 in all. Left GIF (omgif g15.py) shows the same five symmetrized transitions as the slide 7 "
    "ZnPc GIF (g12, znpc_orb.py): C3 MO 119 at 284.6 eV, C2 MO 124 at 286.7 eV, C3 MO 133 at 287.6 eV, C1 MO 205 at 292.9 "
    "eV, C4 MO 314 at 297.1 eV (raw DFT energies), D4h-averaged geometry, each state copied to its 8 equivalent carbons. "
    "Right GIF (g14.py): packaged sticks and cluster labels (znpc_sticks_tensor.csv), seed shift 0.45 eV, seed and refined "
    "cluster Gaussians (cluster_gaussians.csv, refined ratios scaled to the seed total), and one erf ionization step per "
    "carbon site at its refined IP (param_change.json, 290.1 to 292.0 eV), width 0.70 eV, total jump set to the measured "
    "jump-to-pi* ratio of exp_bets.csv. The left GIF also overlays the measured isotropic beta (exp_bets.csv, pre-edge "
    "subtracted) and the DFT spectrum (all sticks with their own widths, every DFT energy shifted by the static +0.45 eV), "
    "each normalized to its pi* maximum between 284 and 286 eV. Transition energies quoted on the GIF include the shift "
    "(C3 MO 119 at 285.0, C2 MO 124 at 287.2, C3 MO 133 at 288.1, C1 MO 205 at 293.3, C4 MO 314 at 297.5 eV). Murcia et al., Phys. Rev. Lett. 137, 158001; dft-learn, Zenodo "
    "10.5281/zenodo.14758696; dissertation Chapter 2, Fig. 2.6 and Table 2.1 (19 clusters). DFT error, Jana and Herbert, "
    "JCTC 19, 4100 (2023).",
    "SCRIPT To use all of these transitions we have to know what each one is, and DFT tells us. ZnPc is our model system, "
    "rigid, with its geometry known from the crystal. For each of the four inequivalent carbons we put a half core hole on "
    "that carbon and compute every excitation of its 1s electron into the empty orbitals. These are the same transitions "
    "you just saw. The photon removes a 1s electron from one kind of carbon, there are eight of each, and it lands in a "
    "final orbital with its own dipole, along the normal for a pi star, in the plane for a sigma star. Every transition "
    "traces back to a carbon and an orbital. Underneath, the solid line is what we measure and the dashed line is the "
    "calculation, already moved up by the usual static 0.45 eV correction. Even then the problems are plain, the first "
    "pi* shoulder is too weak, there is an extra peak near 285.7 eV, and above 288 eV the structure does not line up.",
    "CLICK 1. So why not just use DFT? First, it is a sea, 2,924 transitions from four sites, most of them closer together "
    "than their own widths, far more than a spectrum can resolve. Second, the calculation has known errors, absolute "
    "energies off by tenths of an eV, and it is one molecule in vacuum.",
    "CLICK 2. So we cluster. We correct the energy scale with one rigid shift, then merge transitions whose Gaussians "
    "overlap until no two clusters overlap past the threshold. Each cluster becomes one Gaussian that keeps its carbons, its "
    "orbitals and its dipole. Above the ionization potentials, here one step for each carbon site, the electron leaves the "
    "molecule, and that edge is part of the model too. Then we refine against angle-resolved NEXAFS. Energies, widths and "
    "strengths move, the dipoles are held.",
    "CLICK 3. That is the clustering algorithm Victor Murcia developed, published in Physical Review Letters and open as "
    "dft-learn. It takes 2,924 transitions to 19 physical oscillators, each traceable to its atoms, and that is the optical "
    "model we build everything else on.",
    "TRANSITION So what can we ask with an optical model like this?",
    "VERIFY The raw count is 2,924 (731 per site); Chapter 2 quotes 104 transitions in its filtered set. The step width "
    "0.70 eV follows the Alq3 model; the ZnPc fitted step width is not in the packaged files. Previous notes for slides 8 "
    "and 9 are kept below.",
    "OLD SLIDE 8 NOTES " + notes8.replace("\n", " "),
    "OLD SLIDE 9 NOTES " + notes9.replace("\n", " ")]
tf.text = blocks[0]
for b_ in blocks[1:]:
    tf.add_paragraph().text = ""
    tf.add_paragraph().text = b_

# ---------------------------------------------------------------- remove slide 9
lst = p.slides._sldIdLst
SID9 = s9.slide_id
for e in list(lst):
    if int(e.get("id")) == SID9:
        p.part.drop_rel(e.get("{%s}id" % NS["r"]))
        lst.remove(e)
p.save(OUT)
print("saved", len(p.slides))
