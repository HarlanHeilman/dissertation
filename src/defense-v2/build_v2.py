"""Build defense-draft-v2.pptx from defense-draft-v1.pptx.

Slides touched: 6 (KK GIFs), 7 (highlight, typo, notes), 11 to 19 (Chapter 1 / ZnPc story rebuilt).
Slide 8 (clustering) is left as is, highlight included.
"""
import copy, re
from pathlib import Path
import numpy as np, pandas as pd
from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.chart.data import CategoryChartData, XyChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION, XL_MARKER_STYLE
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

SRC = "/home/claude/in/defense-draft-v1.pptx"
OUT = "/home/claude/build/defense-draft-v2.pptx"
A = Path("/home/claude/assets")
G = Path("/home/claude/omgif/out")
M = Path("/mnt/user-data/uploads/refl-analysis/notebooks/manuscript")

CRIM, INK, SLATE, MUTED = "CA1237", "1F1F1F", "5E6A71", "6B7476"
DFTB, FREEO = "1F77B4", "D9711C"          # Fig. 4.3 colors: ML-DFT blue, Free orange
SURF, BULK, INTF, SUBS = "A9D3EC", "F6C8AE", "9CC38A", "7F8588"

prs = Presentation(SRC)
S = list(prs.slides)
NSA = "http://schemas.openxmlformats.org/drawingml/2006/main"

# card template, copied from slide 16 so new cards carry the deck's white rounded card and theme shadow
_card_tpl = None
for sh in S[15].shapes:
    if sh.name == "Rounded Rectangle 37":
        _card_tpl = copy.deepcopy(sh._element)
assert _card_tpl is not None


def rgb(h):
    return RGBColor.from_string(h)


def _next_id(slide):
    ids = [int(e.get("id")) for e in slide._element.iter() if e.tag.endswith("}cNvPr")]
    return max(ids + [1]) + 1


def card(slide, x, y, w, h, name="Card", fill=None):
    el = copy.deepcopy(_card_tpl)
    el.find(".//" + qn("p:cNvPr")).set("id", str(_next_id(slide)))
    el.find(".//" + qn("p:cNvPr")).set("name", name)
    xf = el.find(".//" + qn("a:xfrm")); off = xf.find(qn("a:off")); ext = xf.find(qn("a:ext"))
    off.set("x", str(int(Inches(x)))); off.set("y", str(int(Inches(y))))
    ext.set("cx", str(int(Inches(w)))); ext.set("cy", str(int(Inches(h))))
    if fill:
        el.find(".//" + qn("a:srgbClr")).set("val", fill)
    slide.shapes._spTree.append(el)
    return el


def _runs(p, text, size, color, bold=False, italic=False):
    """mini markup: _{sub} ^{sup}"""
    parts = re.split(r"(_\{[^}]*\}|\^\{[^}]*\})", text)
    for part in parts:
        if not part:
            continue
        base = 0
        if part.startswith("_{"):
            part, base = part[2:-1], -25000
        elif part.startswith("^{"):
            part, base = part[2:-1], 30000
        r = p.add_run(); r.text = part
        f = r.font; f.size = Pt(size); f.bold = bold; f.italic = italic; f.color.rgb = rgb(color)
        if base:
            r._r.get_or_add_rPr().set("baseline", str(base))


def tb(slide, x, y, w, h, paras, anchor="t", margin=0.05, name=None):
    """paras: list of dicts {t, size, color, bold, italic, align, after, bullet}"""
    s = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        s.name = name
    tf = s.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(margin); tf.margin_top = tf.margin_bottom = Inches(0.03)
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}[anchor]
    bp = tf._txBody.find(qn("a:bodyPr"))
    for c in list(bp):
        bp.remove(c)
    etree.SubElement(bp, qn("a:noAutofit"))
    for i, pd_ in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[pd_.get("align", "l")]
        p.space_after = Pt(pd_.get("after", 3))
        pPr = p._p.get_or_add_pPr()
        if pd_.get("bullet"):
            pPr.set("marL", "228600"); pPr.set("indent", "-228600")
            bf = etree.SubElement(pPr, qn("a:buFont")); bf.set("typeface", "Arial")
            bc = etree.SubElement(pPr, qn("a:buChar")); bc.set("char", "•")
        else:
            pPr.set("marL", "0"); pPr.set("indent", "0"); etree.SubElement(pPr, qn("a:buNone"))
        _runs(p, pd_["t"], pd_.get("size", 15), pd_.get("color", INK), pd_.get("bold", False), pd_.get("italic", False))
    return s


def H(t, size=16, color=CRIM):
    return dict(t=t, size=size, color=color, bold=True, after=3)


def B(t, size=15, color=INK, **k):
    d = dict(t=t, size=size, color=color, after=4); d.update(k); return d


def box(slide, x, y, w, h, fill, line=None, shape=MSO_SHAPE.RECTANGLE, text=None, size=12, color=INK, bold=False, name=None):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        s.name = name
    s.shadow.inherit = False
    if fill:
        s.fill.solid(); s.fill.fore_color.rgb = rgb(fill)
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = rgb(line); s.line.width = Pt(1.25)
    else:
        s.line.fill.background()
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = 0.12
    if text is not None:
        tf = s.text_frame; tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.06); tf.margin_top = tf.margin_bottom = Inches(0.02)
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        _runs(p, text, size, color, bold)
    return s


def arrow(slide, x0, y0, x1, y1, color=SLATE, w=2.0):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x0), Inches(y0), Inches(x1), Inches(y1))
    c.line.color.rgb = rgb(color); c.line.width = Pt(w)
    ln = c.line._get_or_add_ln()
    te = etree.SubElement(ln, qn("a:tailEnd")); te.set("type", "triangle"); te.set("w", "med"); te.set("len", "med")
    return c


def pic(slide, path, x, y, w=None, h=None, name=None, descr=None):
    p = slide.shapes.add_picture(str(path), Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)
    if name:
        p.name = name
    if descr:
        p._element.find(".//" + qn("p:cNvPr")).set("descr", descr)
    return p


def clear(slide, keep=()):
    """Remove every shape except placeholders and named keeps."""
    tree = slide.shapes._spTree
    for el in list(tree):
        tag = etree.QName(el).localname
        if tag in ("nvGrpSpPr", "grpSpPr"):
            continue
        if tag == "AlternateContent":
            tree.remove(el); continue
        ph = el.find(".//" + qn("p:ph"))
        nm = el.find(".//" + qn("p:cNvPr"))
        if ph is not None:
            continue
        if nm is not None and nm.get("name") in keep:
            continue
        tree.remove(el)
    t = slide._element.find(qn("p:timing"))
    if t is not None:
        slide._element.remove(t)


def set_title(slide, text):
    t = slide.shapes.title
    p = t.text_frame.paragraphs[0]
    runs = p.runs
    for hl in t._element.iter(qn("a:highlight")):
        hl.getparent().remove(hl)
    runs[0].text = text
    for r in runs[1:]:
        p._p.remove(r._r)
    for extra in t.text_frame.paragraphs[1:]:
        extra._p.getparent().remove(extra._p)


def notes(slide, text):
    ns = slide.notes_slide
    if ns.notes_text_frame is None:
        donor = S[10].notes_slide.notes_placeholder._element
        el = copy.deepcopy(donor)
        el.find(".//" + qn("p:cNvPr")).set("id", str(_next_id(ns)))
        ns.shapes._spTree.append(el)
    slide.notes_slide.notes_text_frame.text = text


def style_chart(ch, size=12):
    ch.font.size = Pt(size); ch.font.name = "Cambria"; ch.font.color.rgb = rgb(INK)


def picture_by_name(slide, name):
    for s in slide.shapes:
        if s.name == name:
            return s
    raise KeyError(name)


# ===================================================================== slide 6
s6 = S[5]
set_title(s6, "ORIGIN OF RESONANT RESPONSE")
for sh in s6.shapes:
    if sh.shape_type == 13 and sh.name in ("Animation 2", "Picture 33"):
        rid = sh._element.find(".//" + qn("a:blip")).get(qn("r:embed"))
        part = s6.part.related_part(rid)
        new = G / ("optical-model-2-local-bonds-kk.gif" if sh.name == "Animation 2" else "znpc-local-states-kk.gif")
        part._blob = new.read_bytes()
        sh._element.find(".//" + qn("p:cNvPr")).set(
            "descr", "Animated schematic. Swept photon energy builds the measured beta; delta then follows from beta by "
                     "a Kramers-Kronig transform." if sh.name == "Animation 2" else
                     "Animated ZnPc transitions with the measured isotropic beta and its Kramers-Kronig delta.")
    if sh.name == "TextBox 38":
        ps = sh.text_frame.paragraphs
        ps[1].runs[0].text = "NEXAFS near the edge measures β"
        ps[2].runs[0].text = "Kramers-Kronig computes δ from β"
        newp = copy.deepcopy(ps[2]._p); ps[2]._p.addnext(newp)
        sh.text_frame.paragraphs[3].runs[0].text = "Angle resolution labels each orbital"
    if sh.name == "Rounded Rectangle 37":
        sh.height = Inches(1.36)
notes(s6, """TIME 1.75 min

SOURCE Original animations made for the defense (dissertation Claude outputs/optical-model-gifs, KK versions g2k and g12k). Left, the schematic benzene-ring model of Chapter 2, one pi* and two sigma* Gaussian-Dawson oscillators on an ionization step at 290.3 eV, with delta from a numerical Kramers-Kronig transform of the full beta (bare atom 1 eV to 30 keV plus the Dawson partner of each resonance). Right, ZnPc, the measured isotropic beta (exp_bets.csv, carbon-lab/znpc-optical-model) and delta from a numerical Kramers-Kronig transform of that beta, with dft.csv tails outside 270 to 330 eV and a constant 0.345e-3 that matches the packaged KK-consistent model exp.csv (residual shape difference 0.04e-3 rms).

SCRIPT On the left is the carbon edge of a ring molecule. Bonding leaves an empty pi star orbital below the ionization threshold, so the 1s electron is promoted into a bound, local state and gives a sharp resonance before the step. Above the step, sigma star resonances sit in the continuum along the bonds. As the photon energy sweeps, the red curve is beta, the absorption, and this is the half of the index that NEXAFS measures. The refractive half, delta, is not measured separately. Once beta is known across the whole edge, causality fixes delta through the Kramers-Kronig relations, and that is the blue curve drawn after the sweep. The dispersive wiggle at every resonance comes from that transform. On the right is the same picture for a molecule we actually use, ZnPc, where each feature is a family of transitions from different carbon sites and the delta is computed from the measured beta in exactly the same way.

TRANSITION To use all of these transitions, we need to know what each one is.

VERIFY Benzene-ring spectra are schematic, not a measured dataset; the label says measured to describe what NEXAFS supplies.""")

# ===================================================================== slide 7
s7 = S[6]
set_title(s7, "USING DFT TO REVEAL COMPLEX EXCITATIONS")
for sh in s7.shapes:
    if sh.name == "Group 20" or sh.has_text_frame:
        pass
for el in s7._element.iter(qn("a:t")):
    if el.text and "RIDGED" in el.text:
        el.text = el.text.replace("RIDGED - no dihedral angles", "Rigid, no dihedral angles")
notes(s7, """TIME 1.25 min

SOURCE Dissertation Chapter 2, Transitions from ML-Refined DFT (pp. 25 and 26) and Fig. 2.6; StoBe transition-potential runs for the four inequivalent carbon sites (dft-learn, znpc-cif).

SCRIPT ZnPc is our model system. It is a rigid planar macrocycle with no dihedral freedom, its geometry and orientation come from the crystal structure, and its nitrogen heteroatoms challenge both the calculation and the measurement. For each of the four inequivalent carbon sites we compute the excitation of a carbon 1s electron into the empty orbitals with transition-potential DFT. Every transition carries an energy, a strength, and a transition dipole, and every one can be traced to a site and an orbital, so the peaks in the spectrum get chemical names, the imine, bridgehead, inner, and outer carbons. The broadened calculation agrees with the measured spectrum qualitatively. The difficulty is the number of transitions. The calculation returns thousands, many closer together than their own widths, and no spectrum can resolve that many independent quantities.

TRANSITION Clustering reduces those transitions to the few that a spectrum can resolve.

VERIFY The slide says over 2k transitions; Chapter 2 quotes 104 transitions in the filtered calculation between 283.8 and 318.4 eV. Say which count the slide refers to (raw StoBe output against the filtered set).""")

# ===================================================================== slide 11  (free tensor, parameter explosion)
s11 = S[10]
clear(s11)
set_title(s11, "TRADITIONAL VS DIRECT MEASUREMENT")
card(s11, 0.60, 2.05, 6.55, 4.85, "Card models")
pic(s11, A / "fig42_a.png", 0.70, 3.09, w=6.35, name="Fig 4.2a",
    descr="Three-slab ZnPc film with thickness and roughness per slab, and the two optical models, ML-DFT parameterized by orientation and density against a free tensor per energy (dissertation Fig. 4.2a).")
card(s11, 7.30, 2.05, 5.45, 4.85, "Card forest")
pic(s11, A / "fig43_bulk.png", 7.40, 2.45, w=5.25, name="Bulk free constants",
    descr="Bulk-slab birefringence and dichroism, free tensor points at each energy against the ML-DFT curves (dissertation Fig. 4.3a, bulk panel).")
tb(s11, 7.45, 5.45, 5.15, 0.6, [B("84 free constants per slab, against 2", 16, CRIM, bold=True, align="c", after=0)], anchor="m")
notes(s11, """TIME 2.0 min

SOURCE Dissertation Fig. 4.2a and Fig. 4.3a bulk panel (refl-analysis notebooks/manuscript FIG2.png and FIG3.png); Chapter 1 pp. 6 and 7; Chapter 4 pp. 63 and 64 (four uniaxial components per energy per slab, 84 per slab across 21 energies).

SCRIPT On the left is how we model the film, and the two ways to model its optics. The structure is the same either way, three slabs, surface, bulk, and buried interface, each with a thickness and a roughness, and conventionally the boundary slabs are where contamination or oxidation is placed. The traditional route, the free tensor, fits four optical constants in every slab at every energy. It will fit any material, and orientation and density come only from a second analysis. Our route locks the optics to the ZnPc molecule through the ML-DFT tensor, so a slab is described by how those molecules are oriented and how densely they pack, and the same two numbers have to explain every energy and polarization. On the right is what the traditional route produces for the bulk slab alone. Every orange point is its own fit parameter, one pair of constants per energy, and nothing ties one energy to the next, so each new energy adds parameters rather than tightening the ones we have. That is 84 constants for this slab. The blue curves are the ML-DFT tensor, which describes the same slab with two.

TRANSITION So what happens when both models meet the same data?

VERIFY The 84 count is optical parameters for one slab; Fig. 4.3b totals with structural and instrument parameters are 286 against 17.""")



# ===================================================================== slide 12 (old 13): model comparison
s12 = S[12]
clear(s12)
set_title(s12, "Integrating the molecular model directly into the analysis")
card(s12, 0.60, 2.05, 12.15, 4.85, "Card schematic")
pic(s12, A / "fig42_a.png", 1.35, 2.15, h=4.65, name="Fig 4.2a",
    descr="Three-slab ZnPc film with thickness and roughness per slab, and the two optical models, ML-DFT locked to ZnPc and parameterized by orientation and density, against a free tensor per energy (dissertation Fig. 4.2a).")
notes(s12, """TIME 1.5 min

SOURCE Dissertation Fig. 4.2a (panel cut from refl-analysis notebooks/manuscript/FIG2.png) and Chapter 4 pp. 63 and 64; Chapter 2, Molecular and Film Reference Frames, for the projection through tilt and density.

SCRIPT Here are the two models we compare, drawn the same way. The structure is shared. The film is three slabs, surface, bulk, and buried interface, each with its own thickness and roughness, and in the conventional picture the boundary slabs are where contamination or oxidation is placed. The difference is entirely in the optics. On the bottom is the free tensor, four constants per slab at every energy, which will fit any material and leaves orientation and density for a second analysis. On top is the ML-DFT tensor. Its energy and polarization dependence is fixed by the ZnPc molecule, and a slab is described only by how those molecules are oriented and how densely they pack, a tilt gamma and a density rho. The details of that projection are in Chapter 2; what matters here is that the same two numbers have to explain every energy and polarization, and a layer that is not ZnPc cannot be absorbed into them. It shows up as misfit at ZnPc's own resonances.

TRANSITION So what happens when both models meet the same data?""")

# ===================================================================== slide 14 (old 14): building the model + OFET
s14 = S[13]
set_title(s14, "MOLECULE AND FILM OPTICAL REFERENCE FRAME")
tree = s14.shapes._spTree
for el in list(tree):
    if etree.QName(el).localname not in ("sp", "pic", "grpSp", "cxnSp", "graphicFrame", "AlternateContent"):
        continue
    if el.find(".//" + qn("p:ph")) is not None:
        continue
    off = next((e for e in el.iter(qn("a:off")) if e.get("x") is not None), None)
    ext = next((e for e in el.iter(qn("a:ext")) if e.get("cx") is not None), None)
    if off is None or ext is None:
        continue
    x0, y0_ = Emu(int(off.get("x"))).inches, Emu(int(off.get("y"))).inches
    h0 = Emu(int(ext.get("cy"))).inches
    if x0 >= 8.25 and y0_ < 4.55 and y0_ + h0 <= 4.62:
        tree.remove(el)
card(s14, 8.32, 2.33, 4.40, 2.18, "Card OFET")
# OFET schematic, bottom gate, top contact
ox, oy = 8.50, 2.58
box(s14, ox, oy + 0.38, 0.30, 0.18, "C9A14A", name="Source")
box(s14, ox + 1.28, oy + 0.38, 0.30, 0.18, "C9A14A", name="Drain")
tb(s14, ox - 0.05, oy + 0.08, 0.42, 0.3, [B("S", 12, SLATE, bold=True, align="c", after=0)])
tb(s14, ox + 1.23, oy + 0.08, 0.42, 0.3, [B("D", 12, SLATE, bold=True, align="c", after=0)])
box(s14, ox, oy + 0.56, 1.58, 0.58, BULK, text="ZnPc", size=12, name="ZnPc layer")
box(s14, ox, oy + 1.06, 1.58, 0.08, CRIM, name="Channel")
box(s14, ox, oy + 1.14, 1.58, 0.16, "C8C3BE", name="Oxide")
box(s14, ox, oy + 1.30, 1.58, 0.32, "424C4E", text="Si gate", size=11, color="FFFFFF", name="Gate")
tb(s14, ox - 0.05, oy + 1.66, 1.75, 0.3, [B("channel, 1st ML on SiO₂", 11, CRIM, align="c", after=0)])
tb(s14, 10.22, 2.43, 2.45, 2.05, [H("Our film is a transistor", 15),
                                  B("Si/SiO₂/ZnPc is the bottom-gate OFET stack. Gate charge collects in the first ZnPc layers on the oxide, the region the rest of this talk resolves.", 13, after=0)])
notes(s14, """TIME 1.75 min

SOURCE Dissertation Chapter 2, Molecular and Film Reference Frames (pp. 27 to 29) and Fig. 2.7; Chapter 4 p. 62 and Appendix B Fig. S2 (GIXRD and GIWAXS, edge-on herringbone, (200) out of plane at 0.50 A^-1, pi stacking at 1.89 A^-1); film tensor equations from Appendix B Sec. 2.

SCRIPT To build the model for our film we need three things. The molecule supplies the tensor; each refined cluster is a dipole fixed in the molecular frame. The film supplies the ensemble. GIWAXS shows ZnPc on native-oxide silicon grows edge-on in the herringbone phase with no preferred azimuth, so the film is uniaxial and averaging the molecular tensor over azimuth at a tilt gamma gives the two film components written here. Density then scales the whole tensor. The maps on the right show what that buys. Each color is a tilt from face-on to edge-on, and the whole energy dependence of beta and delta follows from that one angle. Finally, this is not just a convenient sample. Silicon with its native oxide under a ZnPc film is the standard bottom-gate organic field-effect transistor. When the gate is biased, charge collects and moves in the first molecular layers on the oxide, which is exactly the buried region that the rest of this talk measures.

TRANSITION So how does this tensor compare with the free one on the same data?

VERIFY The OFET framing is not in the dissertation text. Confirm the claim that charge transport is confined to the first few monolayers at the dielectric, and add a citation if you want one on the slide (e.g. Dodabalapur et al., Science 1995, if you agree it is the right reference). The user brief called these the injection layers; the slide says channel.""")

# ===================================================================== slide 15 (old 15): results, GIXRD + fits + selection
s15 = S[14]
clear(s15)
set_title(s15, "DIRECT MEASUREMENT OF BURIED MOLECULAR STATES")
card(s15, 0.60, 2.05, 8.55, 3.45, "Card reflectivity")
pic(s15, A / "fig42_fits.png", 0.70, 2.17, w=8.35, name="Fig 4.2 c-e",
    descr="s and p reflectivity at diagnostic, pre-edge, and resonant energies with free-tensor (solid) and ML-DFT (dashed) slab fits (dissertation Fig. 4.2c to e).")
card(s15, 0.60, 5.65, 8.55, 1.25, "Card strip")
def bars(slide, x0, y0, rows, ncol=3, name="bar"):
    for r_, (rot, col) in enumerate(rows):
        for j in range(ncol):
            bb = box(slide, x0 + 0.10 + j * 0.30, y0 + r_ * 0.30, 0.05, 0.27, col, name=f"{name}{r_}{j}")
            bb.rotation = rot
EDGE, FACE = (20, "424C4E"), (55, CRIM)
strip = [("Patterning hypothesis", "substrate templates every layer", [EDGE, EDGE, EDGE], False),
         ("Measured", "first layer differs, bulk forms above it", [EDGE, EDGE, FACE], False),
         ("Charge transport", "current flows in the first layers on the oxide", [EDGE, EDGE, FACE], True)]
for k, (hh, bb_, rows, transport) in enumerate(strip):
    x0 = 0.72 + k * 2.83
    bars(s15, x0, 5.74, rows, name=f"strip{k}_")
    box(s15, x0 + 0.02, 6.66, 0.98, 0.07, "C8C3BE", name=f"oxide{k}")
    if transport:
        box(s15, x0 + 0.02, 5.70, 0.16, 0.08, "C9A14A", name="S strip")
        box(s15, x0 + 0.84, 5.70, 0.16, 0.08, "C9A14A", name="D strip")
        arrow(s15, x0 + 0.05, 6.52, x0 + 1.00, 6.52, CRIM, 2.5)
    tb(s15, x0 + 1.10, 5.70, 1.65, 1.15, [B(hh, 13, CRIM, bold=True, after=2), B(bb_, 12, INK, after=0)], anchor="m")
    if k < 2:
        ln = s15.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x0 + 2.78), Inches(5.78), Inches(x0 + 2.78), Inches(6.77))
        ln.line.color.rgb = rgb("D9D4CF"); ln.line.width = Pt(1.0)
# right column, three visual cards
RX, RW = 9.35, 3.40
cards15 = [("Consistent with GIXRD", "Edge-on herringbone bulk, γ ≈ 70°"),
           ("At the buried interface", "Still ZnPc, more face-on and less dense"),
           ("In a real device", "This layer is the OFET channel")]
for k, (hh, bb) in enumerate(cards15):
    yy = 2.05 + k * 1.675
    card(s15, RX, yy, RW, 1.52, f"Card right {k}")
    tb(s15, RX + 1.55, yy + 0.08, RW - 1.62, 1.38, [H(hh, 14), B(bb, 13, after=0)], anchor="m")
# 1. GIWAXS thumbnail
pic(s15, A / "si2_a.png", RX + 0.10, 2.05 + 0.27, w=1.40, name="GIWAXS",
    descr="GIWAXS of ZnPc on native-oxide silicon (dissertation Fig. S2a).")
# 2. mini slab stack with the interface highlighted
y2 = 2.05 + 1.675
box(s15, RX + 0.15, y2 + 0.20, 1.25, 0.20, SURF, name="mini surface")
box(s15, RX + 0.15, y2 + 0.40, 1.25, 0.55, BULK, name="mini bulk")
box(s15, RX + 0.15, y2 + 0.95, 1.25, 0.16, CRIM, name="mini interface")
box(s15, RX + 0.15, y2 + 1.11, 1.25, 0.20, SUBS, name="mini oxide")
# 3. mini OFET
y3 = 2.05 + 2 * 1.675
ox = RX + 0.12
box(s15, ox, y3 + 0.20, 0.26, 0.13, "C9A14A", name="S")
box(s15, ox + 1.04, y3 + 0.20, 0.26, 0.13, "C9A14A", name="D")
box(s15, ox, y3 + 0.33, 1.30, 0.50, BULK, name="ZnPc")
box(s15, ox, y3 + 0.77, 1.30, 0.07, CRIM, name="channel")
box(s15, ox, y3 + 0.84, 1.30, 0.14, "C8C3BE", name="SiO2")
box(s15, ox, y3 + 0.98, 1.30, 0.32, "424C4E", text="gate", size=10, color="FFFFFF", name="gate")
notes(s15, """TIME 2.0 min

SOURCE Dissertation Fig. 4.2c to e (refl-analysis notebooks/manuscript/FIG2.png bottom row); Appendix B Fig. S2a (GIWAXS); Table 7.2 (ML-DFT slab, bulk 69.54 deg and 1.638 g/cm3, interface 47.24 deg and 1.0 g/cm3); Chapter 4 pp. 62 to 66.

SCRIPT Here are both tensors fit to all twenty-one energies, the free tensor as solid lines and the ML-DFT tensor dashed. The diagnostic energies on the left carry the full q range and pin the structure. The pre-edge series in the middle tracks the critical angles, which follow the birefringence of edge-on ZnPc. The resonant series on the right is the part of the data that knows about chemistry and orbitals, and there the ML-DFT model fits as well or better, with an order of magnitude fewer parameters. On the right is what that fit says. The bulk comes out edge-on near seventy degrees, consistent with the herringbone texture GIXRD shows for this film. At the buried interface the layer is still ZnPc, but more face-on and less dense, and no contamination is needed to fit it. And that matters for devices, because silicon, oxide, and ZnPc is the bottom-gate transistor stack, so the layer we just measured is the transistor channel.

TRANSITION Here is what that tells us about the material.

VERIFY OFET framing is not in the dissertation text; confirm wording.""")


# ===================================================================== slide 16: what we learn
s16 = S[15]
lab_new = {
    "Free surface": ["Free surface", "γ = 52.2°, ρ = 1.8 g cm⁻³"],
    "Bulk": ["Bulk", "γ = 69.5°, ρ = 1.64 g cm⁻³"],
}
for sh in s16.shapes:
    if not sh.has_text_frame:
        continue
    txt = sh.text_frame.text
    body = sh._element.find(qn("p:txBody"))
    def rewrite(lines, color):
        ps = body.findall(qn("a:p"))
        for p in ps[1:]:
            body.remove(p)
        p0 = ps[0]
        for r in list(p0):
            if etree.QName(r).localname in ("r", "m", "AlternateContent") or r.tag.endswith("}m"):
                p0.remove(r)
        for i, line in enumerate(lines):
            p = p0 if i == 0 else copy.deepcopy(p0)
            for r in list(p):
                if etree.QName(r).localname != "pPr":
                    p.remove(r)
            r = etree.SubElement(p, qn("a:r")); rp = etree.SubElement(r, qn("a:rPr"))
            rp.set("lang", "en-US"); rp.set("sz", "1200"); rp.set("b", "1" if i == 0 else "0")
            f = etree.SubElement(rp, qn("a:solidFill")); c = etree.SubElement(f, qn("a:srgbClr")); c.set("val", color)
            t = etree.SubElement(r, qn("a:t")); t.text = line
            if i:
                body.append(p)
    if txt.startswith("Free surface"):
        rewrite(["Free surface", "γ = 52.2°, ρ = 1.8 g cm⁻³"], "957D71")
    elif txt.startswith("Bulk"):
        rewrite(["Bulk", "γ = 69.5°, ρ = 1.64 g cm⁻³", "herringbone"], "424C4E")
    elif txt.startswith("Silicon interface"):
        rewrite(["Silicon interface", "γ = 47.2°, ρ = 1.0 g cm⁻³"], CRIM)
    elif txt.startswith("No contamination"):
        rewrite(["No contamination is needed",
                 "A tensor that admits only ZnPc fits the resonances better than the free tensor, so the boundary layers are ZnPc in another state, not adventitious carbon or oxide."], INK)
    elif txt.startswith("Substrate adhesion"):
        rewrite(["Substrate adhesion favors face-on",
                 "The interface layer tilts 22° further toward face-on than the bulk, within about one molecular layer of the oxide."], INK)
    elif txt.startswith("Lower packing"):
        rewrite(["Lower packing density in the OFET channel",
                 "Density falls from 1.64 to about 1.0 g cm⁻³ at the oxide, the layer that carries gate-induced charge in a transistor."], INK)
MC = "{http://schemas.openxmlformats.org/markup-compatibility/2006}AlternateContent"
labels16 = {"TextBox 35": (["Free surface", "γ = 52.2°, ρ = 1.8 g cm⁻³"], "957D71"),
            "TextBox 24": (["Bulk", "γ = 69.5°, ρ = 1.64 g cm⁻³ (herringbone)"], "424C4E"),
            "TextBox 13": (["Silicon interface", "γ = 47.2°, ρ = 1.0 g cm⁻³"], CRIM)}
for ac in list(s16.shapes._spTree.iter(MC)):
    nm = ac.find(".//" + qn("p:cNvPr")).get("name")
    if nm in labels16:
        off = next(e for e in ac.iter(qn("a:off")) if e.get("x") is not None)
        x, y = Emu(int(off.get("x"))).inches, Emu(int(off.get("y"))).inches
        ac.getparent().remove(ac)
        lines, col = labels16[nm]
        tb(s16, x, y, 2.05, 0.7, [B(lines[0], 12, col, bold=True, after=0), B(lines[1], 12, col, after=0)], name=nm)
# header lines of the three cards back to crimson 16 pt, bodies 15 pt
for sh in s16.shapes:
    if sh.has_text_frame and sh.text_frame.text.split("\n")[0] in (
            "No contamination is needed", "Substrate adhesion favors face-on", "Lower packing density in the OFET channel"):
        ps = sh.text_frame.paragraphs
        for r in ps[0].runs:
            r.font.size = Pt(16); r.font.bold = True; r.font.color.rgb = rgb(CRIM)
        for p in ps[1:]:
            for r in p.runs:
                r.font.size = Pt(15); r.font.bold = False; r.font.color.rgb = rgb(INK)
for sh in list(s16.shapes):
    if sh.name in ("Rounded Rectangle 37", "Rounded Rectangle 39", "Rounded Rectangle 43", "TextBox 38", "TextBox 40", "TextBox 44"):
        sh._element.getparent().remove(sh._element)
for k, (hh, items) in enumerate([
        ("What we learn", ["Every layer is ZnPc, no contamination layer is needed",
                           "The interface layer is 22° more face-on and less dense",
                           "The bulk matches herringbone ZnPc"]),
        ("What the slab model cannot say", ["Three separate slabs are no longer physically motivated",
                                            "The interface slab is rougher (σ 7.9 Å) than it is thick (10.7 Å)",
                                            "Growth should give a continuous gradient from pinned interfaces"])]):
    yy = 2.05 + k * 2.50
    card(s16, 6.62, yy, 6.13, 2.35, f"Card {hh}")
    tb(s16, 6.80, yy + 0.10, 5.85, 2.15, [H(hh, 16)] + [B(t, 15, bullet=True, after=6) for t in items])
notes(s16, """TIME 2.0 min

SOURCE Dissertation Table 7.2 (ML-DFT slab: surface 52.21(7) deg, 1.8(3) g/cm3; bulk 69.54(1) deg, 1.638(3) g/cm3; interface 47.24(9) deg, 1.0(6) g/cm3, 10.705 A thick, roughness 7.892 A); Chapter 4 pp. 64 to 66; Chapter 3 orientation gradient section and Appendix B eqs. S10 to S16.

SCRIPT Because the tensor only knows ZnPc, the fit reads directly as a picture of the film. The bulk matches herringbone ZnPc, edge-on near seventy degrees at a density of 1.64. The surface and interface layers are different, but both still carry the resonant anisotropy only oriented ZnPc produces, so no contamination layer is needed; the boundary layers are ZnPc in another state. At the oxide that state is more than twenty degrees further toward face-on and less dense. That result also undercuts the slab model that produced it. The slabs were there to hold three different materials, and there is now only one. The interface slab is 10.7 angstroms thick with 7.9 angstroms of roughness, so it is more transition than layer. And growth physics says what to expect instead. Each new layer takes its order from the one beneath it, so tilt and density should relax continuously from a pinned state at each interface into the bulk.

TRANSITION So we replace the slabs with a gradient built on that physics.

VERIFY Slab tilts follow Table 7.2; Fig. 4.3a labels 53.2, 70.07, and 50 degrees. Interface density 1.0(6) is poorly constrained.""")


# ===================================================================== slide 17: continued issues and pathway
s17 = S[16]
clear(s17)
set_title(s17, "But what is really going on at the interface?")
c17 = [
    ("1", "Slabs lose their reason",
     "Three slabs were introduced to hold contamination. With every layer fit as ZnPc, separate slabs are no longer physically motivated."),
    ("2", "The interface slab is rougher than it is thick",
     "10.7 Å thick with 7.9 Å roughness, its interfacial width √(2π)σ = 19.8 Å exceeds the slab itself. That is a Névot-Croce limit, not a layer."),
    ("3", "Growth predicts a gradient",
     "Each deposited layer takes its order from the one beneath it, so tilt and density should relax smoothly from pinned interface states (Ginzburg-Landau)."),
]
for k, (n, hh, bb) in enumerate(c17):
    x = 0.60 + k * 4.10
    card(s17, x, 2.05, 3.95, 2.85, f"Issue {n}")
    box(s17, x + 0.18, 2.20, 0.42, 0.42, CRIM, shape=MSO_SHAPE.OVAL, text=n, size=15, color="FFFFFF", bold=True)
    tb(s17, x + 0.72, 2.13, 3.12, 0.62, [H(hh, 15)], anchor="m")
    tb(s17, x + 0.15, 2.80, 3.68, 2.05, [B(bb, 15, after=0)])
card(s17, 0.60, 5.10, 12.15, 1.80, "Card pathway")
steps17 = [
    ("Free tensor", "A gradient needs a tensor in every depth slice at every energy", FREEO),
    ("ML-DFT tensor", "Bulk state plus two decay lengths, γ(z) and ρ(z)", DFTB),
    ("Testable growth models", "Pinned states at each interface relax into the bulk over τ_{Si} and τ_{vac}", CRIM),
]
for k, (hh, bb, col) in enumerate(steps17):
    x = 0.80 + k * 4.0
    box(s17, x, 5.28, 3.55, 1.45, "F6F4F3", line=col, shape=MSO_SHAPE.ROUNDED_RECTANGLE, name=f"Path {k}")
    tb(s17, x + 0.08, 5.32, 3.40, 1.38, [B(hh, 15, col, bold=True, after=3), B(bb, 13, INK, after=0)], anchor="m")
    if k < 2:
        arrow(s17, x + 3.57, 6.005, x + 3.98, 6.005, SLATE, 2.25)
notes(s17, """TIME 1.5 min

SOURCE Dissertation Chapter 4, Sub-monolayer interfacial physics (p. 66); Table 7.2 (interface slab 10.705 A, roughness 7.892 A); Fig. S9c (interfacial width sqrt(2 pi) sigma); Chapter 3, Orientation gradient theoretical foundation, and Appendix B eqs. S10 to S16.

SCRIPT That result also undercuts the model we used to get it. First, the three slabs were there to hold three different materials. If every layer is ZnPc, there is no physical reason for three separate slabs. Second, look at the interface slab. It is 10.7 angstroms thick with 7.9 angstroms of roughness, so its interfacial width is about twenty angstroms, nearly twice its thickness. That is the Nevot-Croce limit, a smooth transition dressed up as a layer. Third, the physics of growth says what to expect instead. Each new layer takes its order from the one beneath it, so tilt and density should relax continuously from a pinned state at each interface into the bulk. Treating tilt and density as order parameters in a Ginzburg-Landau free energy gives exactly that, an exponential relaxation from each boundary. The bottom row is the pathway. With a free tensor such a gradient is out of reach, since every depth slice needs its own tensor at every energy. With the ML-DFT tensor it costs a bulk state and two decay lengths, so a structural hypothesis about growth becomes something the data can accept or reject.

TRANSITION So we put the gradient model to the data.""")

# ===================================================================== slide 18: gradient results + OFET
s18 = S[17]
keep18 = ("Picture 10", "Picture 11", "Picture 16", "Picture 13", "Picture 18", "TextBox 22", "TextBox 7")
clear(s18, keep=keep18)
set_title(s18, "What causes this reorientation?")
card(s18, 0.59, 2.05, 5.80, 2.85, "Card growth")
card(s18, 0.59, 5.05, 5.80, 1.90, "Card literature")
card(s18, 6.47, 2.05, 6.68, 3.17, "Card fit")
# re-stack pictures above the new cards
for sh in list(s18.shapes):
    if sh.name in keep18:
        el = sh._element; el.getparent().remove(el); s18.shapes._spTree.append(el)
for sh in s18.shapes:
    if sh.name == "Picture 10":
        sh.left, sh.top, sh.width, sh.height = Inches(0.72), Inches(2.18), Inches(2.02), Inches(2.54)
tb(s18, 2.85, 2.15, 3.45, 2.70, [
    H("Competing interactions at the growth front", 15),
    B("Substrate adhesion pins the first layer face-on", 14, bullet=True, after=5),
    B("π-π cohesion builds edge-on herringbone above it", 14, bullet=True, after=5),
    B("At the free surface, a denser state near the magic angle", 14, bullet=True, after=0)], name="Growth text")
for sh in s18.shapes:
    if sh.shape_type == 13 and sh.name in ("Picture 11", "Picture 13", "Picture 16"):
        sh.top = Inches(5.47)
    if sh.name == "TextBox 22":
        sh.top = Inches(5.06)
card(s18, 6.47, 5.35, 3.25, 1.60, "Card interface")
tb(s18, 6.57, 5.40, 3.07, 1.52, [H("First monolayer on SiO₂", 15),
                                 B("γ = 38(1)°, ρ = 0.87(7) g cm⁻³", 14, after=2),
                                 B("relaxes to bulk over τ_{Si} = 14.9 Å", 14, after=0)])
card(s18, 9.90, 5.35, 3.25, 1.60, "Card OFET")
tb(s18, 10.0, 5.40, 3.07, 1.52, [H("Measured in the OFET channel", 15),
                                 B("Charge is injected into and carried by this face-on, low-density layer", 14, after=0)])
notes(s18, """TIME 2.0 min

SOURCE Dissertation Fig. 4.4 and Table 4.1 (surface 58.7(6) degrees, 2.0(1) g/cm3, tau_vac 13(1) A; bulk 69.6(2) degrees, 1.64(1) g/cm3; interface 38(1) degrees, 0.87(7) g/cm3, tau_Si 14.9(1) A; reduced chi-square 9.9 against 15.1, N 12 against 17); Chapter 4, Surface vs bulk dynamics in film growth (p. 68). Literature panels as in v1 (Isamu et al. 2022, Derrien et al. 2022, Yang et al. 2015).

SCRIPT Here is the gradient model fit to the diagnostic and resonant profiles, in red against the slab model in black. The fringe phase error the slab model had at 283.7 eV is gone, the Brewster region is reproduced, and it does this with twelve parameters instead of seventeen, at a reduced chi-square of 9.9 against 15.1. The recovered film has a herringbone bulk near seventy degrees. At the oxide the tilt drops to thirty-eight degrees and the density to 0.87, and it relaxes to the bulk over fifteen angstroms, about one molecular layer. At the free surface the film is denser and tilts toward the magic angle. Our reading is a competition at the growth front. Adhesion to the substrate favors flat-lying molecules, pi-pi cohesion favors edge-on stacking, and the gradient traces the crossover. That argues against the usual picture in which the substrate patterns the bulk texture, and it means coverage checkpoint studies record a transient growth front rather than the buried interface. Finally, this is the transistor channel. The face-on, low-density first layer is where an OFET injects and carries its charge, and this is a direct, nondestructive measurement of it.

TRANSITION And that first layer is far thinner than the resolution we are supposed to have.

VERIFY The injection wording follows the brief; the dissertation does not discuss the OFET. Confirm the statement and whether you want a citation.""")

# ===================================================================== slide 19: diffraction limit
s19 = S[18]
clear(s19)
set_title(s19, "Beyond the diffraction limit?")
card(s19, 0.60, 2.05, 3.95, 4.85, "Card limit")
tb(s19, 0.75, 2.10, 3.70, 0.85, [H("Rayleigh condition", 15),
                                 B("Two features are resolved when the maximum of one falls on the first minimum of the other", 12, INK, after=0)])
pic(s19, A / "rayleigh.png", 0.72, 2.98, w=3.70, name="Rayleigh condition",
    descr="Two sinc-squared images whose separation puts the maximum of one on the first minimum of the other, with their sum.")
tb(s19, 0.75, 4.80, 3.70, 1.00, [B("In terms of the wavelength", 13, CRIM, bold=True, after=2),
                                 B("d_{min} = λ / (2 sin θ_{max}) ≥ λ / 2", 15, INK, after=2),
                                 B("λ = 43.7 Å at 283.7 eV, so λ/2 ≈ 22 Å", 12, SLATE, after=0)])
tb(s19, 0.75, 5.80, 3.70, 1.08, [B("In terms of q_{max} = (4π/λ) sin θ_{max}", 13, CRIM, bold=True, after=2),
                                 B("d_{min} = 2π / q_{max}", 15, INK, after=2),
                                 B("full range, 0.27 Å⁻¹ → 23 Å", 12, SLATE, after=0),
                                 B("resonant series, 0.075 Å⁻¹ → 84 Å", 12, SLATE, after=0)])
card(s19, 4.75, 2.05, 8.00, 2.40, "Card interface")
pic(s19, A / "interface_zoom.png", 5.53, 2.08, h=2.33, name="Interface zoom",
    descr="Bottom five nanometers of the regenerated growth strip, lying contact islands in red, beside the gradient and slab tilt profiles, with monolayer lines and 2 pi over q max.")
card(s19, 4.75, 4.50, 8.00, 2.40, "Card qcut")
pic(s19, A / "qcut_demo.png", 5.53, 4.53, h=2.33, name="q cut demo",
    descr="283.7 eV s and p reflectivity fit with the q range cut at 0.27, 0.17, and 0.075 inverse angstroms, and the interface tilt and decay length recovered at each.")
notes(s19, """TIME 2.25 min

SOURCE Dissertation Chapter 4 p. 67 (2 pi/q_max > 23 A) and Table 4.1; q ranges from refl-analysis @data/xrr/znpc (283.7 eV to 0.270 A^-1, resonant energies to 0.0746 to 0.0758 A^-1); lambda = 12398.4/283.7 = 43.7 A; 1 ML = 192.74/15 A. Top right is new. The Fig. 4.4c growth strip regenerated zoomed onto the bottom 5 nm (fig4_panel_b_growth.py with the FIG4 notebook settings and the published graded fit bookended_multienergy_logY_polish_open_sliced; lying contact islands recoloured red, PATCH_STYLE color, no glow) beside gamma(h) from Table 4.1 and the Table 7.2 slab. Bottom right is new, from @models/fitting_results/bookended_q_truncation_diffraction_de_open nested-sampling checkpoints (si3, q_hi, mid, q_lo), every energy held to q <= q_cut: interface tilt 41.4 deg [32.6, 47.6], 45.5 [35.7, 52.6], 51.1 [41.4, 57.3]; tau_Si 22.7 A [17.3, 30.7], 26.4 [18.6, 38.2], 30.8 [20.6, 44.9] for q_cut 0.270, 0.172, 0.075 (68 percent intervals from the corner plots).

SCRIPT How small a feature can reflectivity resolve? The classical answer is the Rayleigh condition. Two features are just resolved when the diffraction maximum of one falls on the first minimum of the other. Written with the wavelength, that separation is lambda over two sine theta max, so no measurement at this energy can do better than half a wavelength, about 22 angstroms. In reflectivity we write the same thing with the momentum transfer. Since q max is four pi over lambda times sine theta max, the limit becomes two pi over q max. For our widest profile, out to 0.27 inverse angstroms, that is 23 angstroms; the resonant profiles stop at 0.075, which is 84 angstroms. A monolayer of ZnPc is 12.9. On the top right is the bottom of the film, the reconstruction beside the tilt profile on the same height axis. The flat-lying molecules sit in the first layer, and the tilt has recovered most of the way to the bulk by the second monolayer, below the 23 angstrom line. The slab model, dashed, cannot describe a change inside its interface layer at all. On the bottom is the test of whether we really sense this. We refit the data with every energy cut to three q lengths, the full 0.27, then 0.17, then 0.075, which throws away the high-q fringes that set the limit. The fits on the left overlap. In the middle, the interface tilt stays well apart from the bulk at all three cuts. On the right, the interface decay length, the dots, stays near 25 to 30 angstroms while the diffraction length, the bars, grows to 84. With the q range cut by almost a factor of four, we still recover the interface thickness consistently, well below the diffraction limit, because the tensor ties the amplitude and phase of the fringes together across energy and polarization.

TRANSITION To summarize the first part of this work.

VERIFY The slide uses the dissertation convention d = 2 pi/q_max, which equals lambda/(2 sin theta_max). The first zero of the Fourier depth kernel for a q window [0, q_max] gives pi/q_max, a factor of two smaller (11.6 A at full range, 42 A at the resonant cut; the q-truncation scripts label cuts this way). The interface decay length at the 0.075 cut, 31 A, sits below either version. These nested-sampling runs come from the q-truncation study, not the Table 4.1 fit (their full-q interface tilt is 41 deg and tau_Si 23 A against 38(1) deg and 14.9 A in Table 4.1). The intervals overlap across cuts, and the medians drift upward as q shrinks.""")


# ===================================================================== order
lst = prs.slides._sldIdLst
ids = list(lst)
drops = [ids[11], ids[12], ids[16]]
build_el, divider_el = ids[13], ids[42]
for el in drops:
    lst.remove(el)
    prs.part.drop_rel(el.get(qn("r:id")))
lst.remove(build_el)
divider_el.addnext(build_el)

prs.save(OUT)
print("saved", OUT)
