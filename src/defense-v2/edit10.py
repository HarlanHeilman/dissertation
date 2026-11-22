"""Slides 8 and 9: DFT and clustering. Slide 8 gets the transition GIF (g13) on the left, the model-system and
'why not DFT on its own' card below it, and keeps the DFT spectrum card on the right. Slide 9 gets the clustering GIF
(g14) on the left, a three-step native pipeline below it, and keeps the cluster figure on the right. Nothing else changes."""
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
      "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006"}
I = lambda v: int(round(v * 914400))
p = Presentation(SRC)
s8 = [s for s in p.slides if s.shapes.title is not None and s.shapes.title.text.startswith("USING DFT TO REVEAL")][0]
s9 = [s for s in p.slides if s.shapes.title is not None and s.shapes.title.text.startswith("CLUSTERING MAKES DFT")][0]


def find(sl, name):
    for sh in sl.shapes:
        if sh.name == name:
            return sh
        if sh.shape_type == 6:
            for c in sh.shapes:
                if c.name == name:
                    return c
    raise KeyError(name)


def drop(sl, *names):
    for n in names:
        el = find(sl, n)._element
        el.getparent().remove(el)


def drop_alt(sl, *names):
    for el in list(sl.shapes._spTree):
        if etree.QName(el).localname == "AlternateContent":
            nm = el.find("mc:Choice", NS).find(".//p:cNvPr", NS).get("name")
            if nm in names:
                sl.shapes._spTree.remove(el)


def place(sh, x, y, w=None, h=None):
    sh.left, sh.top = I(x), I(y)
    if w is not None:
        sh.width = I(w)
    if h is not None:
        sh.height = I(h)


def next_id(sl):
    return max(int(e.get("id")) for e in sl.shapes._spTree.iter("{%s}cNvPr" % NS["p"])) + 1


def clone(sl, proto_el, name, x, y, w, h, front=True):
    el = copy.deepcopy(proto_el)
    c = el.find(".//p:cNvPr", NS); c.set("id", str(next_id(sl))); c.set("name", name)
    for e in c.findall("a:extLst", NS):
        c.remove(e)
    off = el.find(".//a:xfrm/a:off", NS); ext = el.find(".//a:xfrm/a:ext", NS)
    off.set("x", str(I(x))); off.set("y", str(I(y))); ext.set("cx", str(I(w))); ext.set("cy", str(I(h)))
    sl.shapes._spTree.append(el)
    return el


def set_runs(el, paras):
    """paras: list of strings, one per existing paragraph (first run keeps its formatting, the rest are emptied)."""
    ps = el.findall(".//a:p", NS)
    for p_, t in zip(ps, paras):
        rs = p_.findall("a:r", NS)
        rs[0].find("a:t", NS).text = t
        for r in rs[1:]:
            p_.remove(r)


def text(sl, name, x, y, w, h, paras, align="l"):
    tb = sl.shapes.add_textbox(I(x), I(y), I(w), I(h)); tb.name = name
    tf = tb.text_frame; tf.word_wrap = True
    for i, (t, size, bold, color) in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER}[align]
        r = para.add_run(); r.text = t; r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = RGBColor.from_string(color)
    return tb


def gif(sl, path, name, x, y, w, descr):
    pic = sl.shapes.add_picture(path, I(x), I(y), I(w)); pic.name = name
    pic._element.find(".//p:cNvPr", NS).set("descr", descr)
    return pic


def notes(sl, blocks):
    tf = sl.notes_slide.notes_text_frame
    tf.text = blocks[0]
    for b in blocks[1:]:
        tf.add_paragraph().text = ""
        tf.add_paragraph().text = b


# ================================================================ slide 8
drop(s8, "Picture 11", "Picture 12", "TextBox 16", "TextBox 10")
drop_alt(s8, "Arrow: Down 13", "TextBox 14")
gif(s8, G + "znpc-dft-transitions.gif", "DFT transitions GIF", 0.62, 2.02, 6.75,
    "ZnPc, four raw transition-potential DFT transitions drawn at random, one per carbon site. Left, the molecule with "
    "the core-hole carbon lit by the photon; right, the final-state orbital and transition dipole; bottom, every DFT "
    "transition from 283.5 to 300 eV coloured by carbon site, the current one highlighted.")
text(s8, "DFT strip caption", 1.25, 5.33, 5.5, 0.28,
     [("Photon energy (eV), every DFT transition coloured by carbon site", 11, False, "6B7476")], align="c")
place(find(s8, "Rounded Rectangle 15"), 0.62, 5.66, 6.75, 1.26)
tb41 = find(s8, "TextBox 41")
set_runs(tb41._element, ["ZnPc model system", "Rigid, no dihedral angles", "Geometry from the crystal",
                         "StoBe TP-DFT, IGLO-III core hole"])
place(tb41, 0.70, 5.66, 3.30, 1.20)
why = clone(s8, tb41._element, "Why not DFT alone", 3.95, 5.66, 3.40, 1.20)
set_runs(why, ["Why not DFT on its own?", "A sea of 2,924 transitions", "Energies off by tenths of an eV",
               "One molecule, in vacuum"])
for r in why.findall(".//a:p", NS)[0].findall(".//a:solidFill/a:srgbClr", NS):
    r.set("val", "A51C30")
for r in tb41._element.iter("{%s}rPr" % NS["a"]):
    if r.get("sz") == "1500":
        r.set("sz", "1300")
for r in why.iter("{%s}rPr" % NS["a"]):
    if r.get("sz") == "1500":
        r.set("sz", "1300")
place(find(s8, "Graphic 9"), 6.12, 2.10, 1.15, 0.36)
set_runs(find(s8, "Rounded Rectangle 44")._element, ["2,924 transitions"])
notes(s8, [
    "TIME 1.5 min",
    "SOURCE StoBe transition-potential runs for the four inequivalent carbon sites of ZnPc (dft-learn, docs/stobe/example-run/"
    "znpc-cif), 731 transitions per site, 2,924 in all; 1,128 of them fall between 283.7 and 318.4 eV. GIF znpc-dft-"
    "transitions (omgif g13.py, znpc_states13.py) shows four transitions drawn at random with seed 2026 from the top quarter "
    "in strength between 284 and 300 eV, one per site: C1 MO 318 at 299.1 eV (sigma*), C2 MO 184 at 290.0 eV (pi*), C3 MO "
    "119 at 284.6 eV (pi*), C4 MO 314 at 297.1 eV (sigma*). Orbitals are the final MOs of the TP molden files, dipoles "
    "<1s|r|psi_f> at the core-hole atom. Errors, Jana and Herbert, JCTC 19, 4100 (2023), best case 0.3 to 0.4 eV for "
    "K-edge transition energies and larger for higher-lying near-edge states; seed energies need a rigid shift of 0.45 eV "
    "(dissertation Fig. 2.6).",
    "SCRIPT To use all of these transitions we have to know what each one is, and that is what DFT gives us. ZnPc is our "
    "model system, rigid, with no dihedral freedom, its geometry and orientation known from the crystal. For each of the four "
    "inequivalent carbon sites we put a half core hole on that carbon and compute every excitation of its 1s electron into "
    "the empty orbitals. Here are a few of them, picked at random. The photon removes the 1s electron from one carbon, and "
    "it lands in a final orbital, sometimes a pi star with its dipole along the ring normal, sometimes a sigma star in the "
    "plane. Every transition carries an energy, a strength and a dipole, and every one traces back to a carbon and an "
    "orbital, which is how the peaks on the right get chemical names. So why not just use DFT? First, it is a sea. Four "
    "sites give 2,924 transitions, most of them closer together than their own widths, far more than any spectrum can "
    "resolve. Second, the calculation has known errors. Absolute energies are off by tenths of an eV and worse above the "
    "edge, so ours need a rigid shift of 0.45 eV. It is one molecule in vacuum, with no neighbours in a film, and the widths "
    "are put in by hand.",
    "TRANSITION So how do we use this high-dimensional data?",
    "VERIFY The old slide said over 2k transitions; the raw count is 2,924 (731 per site). Chapter 2 quotes 104 transitions "
    "in its filtered set between 283.8 and 318.4 eV; say which count you mean if asked."])

# ================================================================ slide 9
for r in s9.shapes.title._element.iter("{%s}rPr" % NS["a"]):
    for h in r.findall("a:highlight", NS):
        r.remove(h)
drop(s9, "Picture 30", "Picture 1", "Straight Connector 17", "Rectangle 19", "Rectangle 20", "Rectangle 21",
     "Rectangle 22", "Rectangle 23", "Rectangle 24", "Rectangle 25")
card_proto = copy.deepcopy(find(s9, "Rounded Rectangle 68")._element)
title_proto = copy.deepcopy(find(s9, "TextBox 69")._element)
for g in ("Group 77", "Group 78", "Group 79"):
    drop(s9, g)
chip_proto = copy.deepcopy(find(s9, "Rounded Rectangle 28")._element)
drop_alt(s9, "Rounded Rectangle 67")
place(find(s9, "Rounded Rectangle 7"), 0.60, 2.13, 6.72, 3.20)
gif(s9, G + "znpc-dft-clustering.gif", "Clustering GIF", 0.70, 2.25, 6.52,
    "ZnPc DFT transitions coloured by site, shifted by 0.45 eV, recoloured by cluster, collapsed into one Gaussian per "
    "cluster, then moved to the values refined against angle-resolved NEXAFS.")
chip = find(s9, "Rounded Rectangle 28")
place(chip, 2.40, 1.88, 4.50, 0.44)
for rp in chip._element.iter("{%s}rPr" % NS["a"]):
    rp.set("sz", "1600")
set_runs(find(s9, "TextBox 36")._element, ["Clustering algorithm by Victor Murcia, Phys. Rev. Lett. 137, 158001"])
# three-step pipeline
steps = [("1", "Merge overlapping transitions", "labels each resonance"),
         ("2", "Keep sites, orbitals, dipoles", "orbitals and TDMs kept"),
         ("3", "Refine against angle-resolved NEXAFS", "dipoles held fixed")]
W_, GAP, X0, Y0, H_ = 2.04, 0.30, 0.60, 5.48, 1.42
for i, (num, head, sub) in enumerate(steps):
    x = X0 + i * (W_ + GAP)
    clone(s9, card_proto, f"Step card {num}", x, Y0, W_, H_)
    badge = s9.shapes.add_shape(9, I(x + 0.10), I(Y0 + 0.12), I(0.34), I(0.34))   # oval
    badge.name = f"Step badge {num}"
    badge.fill.solid(); badge.fill.fore_color.rgb = RGBColor.from_string("A51C30"); badge.line.fill.background()
    badge.text_frame.text = num
    r = badge.text_frame.paragraphs[0].runs[0]; r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = RGBColor.from_string("FFFFFF")
    badge.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    tt = clone(s9, title_proto, f"Step title {num}", x + 0.52, Y0 + 0.10, W_ - 0.58, 0.80)
    set_runs(tt, [head])
    for rp in tt.iter("{%s}rPr" % NS["a"]):
        rp.set("sz", "1300")
    for rp in tt.iter("{%s}endParaRPr" % NS["a"]):
        rp.set("sz", "1300")
    text(s9, f"Step sub {num}", x + 0.10, Y0 + H_ - 0.38, W_ - 0.2, 0.30, [(sub, 11, False, "6B7476")])
    if i < 2:
        arr = s9.shapes.add_shape(33, I(x + W_ + 0.06), I(Y0 + H_ / 2 - 0.11), I(0.18), I(0.22))   # right arrow
        arr.name = f"Step arrow {i + 1}"
        arr.fill.solid(); arr.fill.fore_color.rgb = RGBColor.from_string("9FA4A5"); arr.line.fill.background()
c2 = clone(s9, chip_proto, "Clusters chip", 8.30, 6.36, 3.80, 0.42)
set_runs(c2, ["2,924 transitions → 19 clusters"])
for rp in c2.iter("{%s}rPr" % NS["a"]):
    rp.set("sz", "1500")
notes(s9, [
    "TIME 1.5 min",
    "SOURCE Murcia et al., Phys. Rev. Lett. 137, 158001 (arXiv 2509.01734); dft-learn (Murcia and Heilman, Zenodo "
    "10.5281/zenodo.14758696). Dissertation Chapter 2, Transitions from ML-refined DFT, Fig. 2.6 and Table 2.1 (19 ZnPc "
    "clusters; hyperparameters OS 0.25 and OVP 52.5, stable for OVP 50 to 55). GIF znpc-dft-clustering (omgif g14.py) uses the "
    "packaged sticks with their cluster labels (znpc_sticks_tensor.csv) and the seed and refined cluster Gaussians "
    "(cluster_gaussians.csv); refined amplitudes keep their ratios and are scaled to the seed total for display.",
    "SCRIPT This is how we use it, with the clustering algorithm Victor Murcia developed. Start with every transition, "
    "coloured by the carbon it came from. First we correct the known energy error with one rigid shift. Then we merge "
    "transitions whose Gaussians overlap, repeatedly, until no two clusters overlap past the threshold and the weakest are "
    "dropped. Each cluster becomes one Gaussian, and the sum of the clusters reproduces the full DFT spectrum. Nothing is "
    "lost chemically, because each cluster still knows which carbons and which orbitals it came from, and it keeps its "
    "transition dipole. On the right you can see that for a few of them, pi star clusters with dipoles within a degree of "
    "the normal, a sigma star cluster near 30 degrees. Finally we refine the clusters against angle-resolved NEXAFS. "
    "Energies, widths and strengths move, the dipoles are held. That takes 2,924 transitions down to 19 physical "
    "oscillators, each traceable to its atoms, and that is the optical model we build everything else on.",
    "TRANSITION So what can we ask with an optical model like this?",
    "VERIFY The old chip said 2k to 12 clusters; the packaged ZnPc model has 19 clusters over 283.7 to 318.4 eV, of which "
    "about 12 lie below 290 eV in the right-hand figure."])


# ================================================================ keep the user's click builds, retargeted
P_ = "{%s}" % NS["p"]


def sid(sl, name):
    return str(find(sl, name).shape_id)


def retarget(sl, mapping, text_names=()):
    t = sl._element.find(P_ + "timing")
    if t is None:
        return
    for c in list(t.iter(P_ + "cTn")):
        if not c.get("presetClass"):
            continue
        par = c.getparent()
        tg = c.find(".//" + P_ + "spTgt")
        sp = tg.get("spid")
        if sp not in mapping:
            continue
        new = mapping[sp]
        if not new:
            par.getparent().remove(par)
            continue
        for e in c.iter(P_ + "spTgt"):
            e.set("spid", new[0])
        for extra in new[1:]:
            cp = copy.deepcopy(par)
            cp.find(P_ + "cTn").set("nodeType", "withEffect")
            for e in cp.iter(P_ + "spTgt"):
                e.set("spid", extra)
            par.addnext(cp)
    # drop clicks that lost every effect, and promote the first remaining effect of a click to clickEffect
    seq = t.find(".//" + P_ + "seq").find(P_ + "cTn").find(P_ + "childTnLst")
    for click in list(seq):
        effs = [c for c in click.iter(P_ + "cTn") if c.get("presetClass")]
        if not effs:
            seq.remove(click)
    for i, click in enumerate(seq):
        effs = [c for c in click.iter(P_ + "cTn") if c.get("presetClass")]
        if effs and i > 0 and not any(e.get("nodeType") == "clickEffect" for e in effs):
            effs[0].set("nodeType", "clickEffect")
    ids = {str(e.get("id")) for e in sl.shapes._spTree.iter(P_ + "cNvPr")}
    bl = t.find(P_ + "bldLst")
    if bl is not None:
        for b in list(bl):
            if b.get("spid") not in ids:
                bl.remove(b)
        have = {b.get("spid") for b in bl}
        for n in text_names:
            i_ = sid(sl, n)
            if i_ not in have:
                etree.SubElement(bl, P_ + "bldP", spid=i_, grpId="0", animBg="1")
    for k, c in enumerate(t.iter(P_ + "cTn"), start=1):
        c.set("id", str(k))


retarget(s8, {"14": [sid(s8, "DFT transitions GIF"), sid(s8, "DFT strip caption")], "13": [], "15": [], "11": [],
              "10": [sid(s8, "Graphic 9")],
              "45": [sid(s8, "Rounded Rectangle 44"), sid(s8, "Why not DFT alone")]},
         text_names=("DFT strip caption", "Why not DFT alone"))
steps_ids = lambda n: [sid(s9, f"Step card {n}"), sid(s9, f"Step badge {n}"), sid(s9, f"Step title {n}"), sid(s9, f"Step sub {n}")]
retarget(s9, {"31": [sid(s9, "Clustering GIF")], "2": [], "18": [], "20": [], "21": [], "22": [], "23": [], "24": [],
              "25": [], "26": [],
              "79": steps_ids(1) + [sid(s9, "Step arrow 1")], "78": steps_ids(2) + [sid(s9, "Step arrow 2")],
              "80": steps_ids(3), "68": [sid(s9, "Clusters chip")]},
         text_names=("Step title 1", "Step title 2", "Step title 3", "Step sub 1", "Step sub 2", "Step sub 3", "Clusters chip"))
p.save(OUT)
print("saved")
