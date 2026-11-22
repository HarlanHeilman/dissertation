"""Edit slides 2, 12 (split into 12 and 12b) and 25 of the user's latest defense-draft-v2.pptx. Nothing else is touched."""
import copy, sys
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import XyChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from lxml import etree

SRC, OUT = sys.argv[1], sys.argv[2]
A = "/home/claude/assets/"
p = Presentation(SRC)
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main"}
RED, INK, GREY = "CA1237", "1F1F1F", "424C4E"
FREE, DFT = "C65A11", "1F6FB0"
CARD_PROTO = copy.deepcopy([sh for sh in p.slides[12].shapes if sh.name == "Card right 0"][0]._element)


def I(v):
    return int(round(v * 914400))


def find(slide, name):
    return [sh for sh in slide.shapes if sh.name == name][0]


def place(sh, x, y, w=None, h=None):
    sh.left, sh.top = I(x), I(y)
    if w is not None:
        sh.width = I(w)
    if h is not None:
        sh.height = I(h)


def next_id(slide):
    return max(int(e.get("id")) for e in slide.shapes._spTree.iter("{%s}cNvPr" % NS["p"])) + 1


def card(slide, x, y, w, h, name):
    el = copy.deepcopy(CARD_PROTO)
    c = el.find(".//p:cNvPr", NS)
    c.set("id", str(next_id(slide))); c.set("name", name)
    for e in c.findall("a:extLst", NS):
        c.remove(e)
    off = el.find(".//a:xfrm/a:off", NS); ext = el.find(".//a:xfrm/a:ext", NS)
    off.set("x", str(I(x))); off.set("y", str(I(y))); ext.set("cx", str(I(w))); ext.set("cy", str(I(h)))
    tree = slide.shapes._spTree
    # cards sit behind everything except the placeholders
    first = [e for e in tree if e.tag.endswith("}sp") or e.tag.endswith("}pic") or e.tag.endswith("}graphicFrame")]
    tree.insert(list(tree).index(first[0]), el)
    return el


def text(slide, x, y, w, h, paras, name, anchor="t", align="l"):
    """paras is a list of (runs, opts); runs is a list of (text, size, bold, color, italic)."""
    tb = slide.shapes.add_textbox(I(x), I(y), I(w), I(h))
    tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True
    bp = tf._txBody.find("a:bodyPr", NS)
    for k, v in (("lIns", "45720"), ("tIns", "27432"), ("rIns", "45720"), ("bIns", "27432"), ("anchor", anchor)):
        bp.set(k, v)
    for e in list(bp):
        bp.remove(e)
    etree.SubElement(bp, "{%s}noAutofit" % NS["a"])
    for i, (runs, opt) in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[opt.get("align", align)]
        para.space_after = Pt(opt.get("after", 0))
        pPr = para._p.get_or_add_pPr()
        if opt.get("bullet"):
            pPr.set("marL", str(I(0.17))); pPr.set("indent", str(-I(0.17)))
            bc = etree.SubElement(pPr, "{%s}buClr" % NS["a"])
            etree.SubElement(bc, "{%s}srgbClr" % NS["a"]).set("val", opt.get("bucolor", GREY))
            etree.SubElement(pPr, "{%s}buFont" % NS["a"]).set("typeface", "Arial")
            etree.SubElement(pPr, "{%s}buChar" % NS["a"]).set("char", "•")
        else:
            pPr.set("marL", "0"); pPr.set("indent", "0")
            etree.SubElement(pPr, "{%s}buNone" % NS["a"])
        for t, size, bold, color, ital in runs:
            r = para.add_run(); r.text = t
            f = r.font; f.size = Pt(size); f.bold = bold; f.italic = ital
            f.color.rgb = RGBColor.from_string(color)
    return tb


def H(t, color=RED, size=14):
    return ([(t, size, True, color, False)], {"after": 3})


def B(t, size=12.5, color=INK, bullet=False, after=4, bucolor=GREY):
    return ([(t, size, False, color, False)], {"bullet": bullet, "after": after, "bucolor": bucolor})


def pic(slide, path, x, y, w=None, h=None, name="", descr=""):
    pc = slide.shapes.add_picture(path, I(x), I(y), I(w) if w else None, I(h) if h else None)
    pc.name = name
    pc._element.find(".//p:cNvPr", NS).set("descr", descr)
    return pc


def remove(sh):
    sh._element.getparent().remove(sh._element)


def set_notes(slide, txt):
    ns = slide.notes_slide
    body = ns.notes_placeholder
    if body is None:
        src = [s for s in p.slides if s.has_notes_slide and s.notes_slide.notes_placeholder is not None][0]
        ns.shapes._spTree.append(copy.deepcopy(src.notes_slide.notes_placeholder._element))
        body = ns.notes_placeholder
    tf = body.text_frame
    blocks = txt.strip("\n").split("\n\n")
    tf.text = blocks[0]
    for b in blocks[1:]:
        tf.add_paragraph().text = ""
        tf.add_paragraph().text = b


# ---------------------------------------------------------------- slide 2, three stories in talk order
s2 = p.slides[1]
remove([sh for sh in s2.shapes if sh.name == "Fig 4.2a"][1])  # optical-box crop, the model is introduced on slide 12
CW, CY, CH = (12.0 - 0.4) / 3, 2.05, 4.70
XS = [0.63, 0.63 + CW + 0.2, 0.63 + 2 * (CW + 0.2)]
cards = {"Rounded Rectangle 8": 0, "Rounded Rectangle 12": 1, "Rounded Rectangle 17": 2}
heads = {"TextBox 24": 0, "TextBox 27": 1, "TextBox 25": 2}
for n, i in cards.items():
    place(find(s2, n), XS[i], CY, CW, CH)
for n, i in heads.items():
    sh = find(s2, n); place(sh, XS[i] + 0.08, CY + 0.08, CW - 0.16, 0.42)
    for r in sh.text_frame.paragraphs[0].runs:
        r.font.size = Pt(15)
ZT, ZH, PAD = 2.78, 2.62, 0.15


def row(slide, names, i, gap=0.1, hmax=ZH):
    shs = [find(slide, n) for n in names]
    asp = [sh.width / sh.height for sh in shs]
    h = min(hmax, (CW - 2 * PAD - gap * (len(shs) - 1)) / sum(asp))
    tot = h * sum(asp) + gap * (len(shs) - 1)
    x = XS[i] + (CW - tot) / 2; y = ZT + (ZH - h) / 2
    for sh, a in zip(shs, asp):
        place(sh, x, y, h * a, h); x += h * a + gap


row(s2, ["Fig 4.2a", "Picture 7"], 0)
row(s2, ["Picture 26", "Picture 22"], 1)
row(s2, ["Picture 23"], 2, hmax=1.2)
TAG = ["Physically constrained optical tensors resolve molecular orientation and density at the buried interface",
       "Fitting the electronic transitions themselves turns reflectivity into a depth resolved spectroscopy",
       "X-ray Atlas, an open FAIR database of the reference NEXAFS these models are built from"]
for i, t in enumerate(TAG):
    text(s2, XS[i] + PAD, 5.45, CW - 2 * PAD, 0.85, [B(t, 13, GREY)], f"Story tagline {i + 1}")
place(find(s2, "TextBox 9"), XS[0] + PAD, 6.27, CW - 2 * PAD, 0.36)
for r in find(s2, "TextBox 9").text_frame.paragraphs[0].runs:
    r.font.size = Pt(11)

# ---------------------------------------------------------------- slide 12a, the two optical models
s12 = p.slides[11]
for n in ("Fig 4.2a", "Bulk free constants", "TextBox 40", "Card forest"):
    remove(find(s12, n))
place(find(s12, "Card models"), 0.60, 2.05, 3.30, 4.85)
card(s12, 4.05, 2.05, 3.80, 4.85, "Card free")
card(s12, 8.00, 2.05, 4.75, 4.85, "Card ML-DFT")
# shared structure
text(s12, 0.72, 2.12, 3.06, 0.40, [H("Same film structure", GREY)], "Head structure")
pic(s12, A + "m_struct.png", 0.75, 2.58, w=3.00, name="Structure model",
    descr="Film cartoon and three-slab structural model, surface, bulk and interface, each with thickness t and roughness sigma (dissertation Fig. 4.2a).")
text(s12, 0.72, 4.95, 3.06, 1.85, [
    B("Three slabs, each with a thickness t and roughness σ", bullet=True),
    B("Shared by both optical models", bullet=True),
    B("Boundary slabs conventionally absorb contamination or oxide", bullet=True)], "Text structure")
# free tensor
text(s12, 4.17, 2.12, 3.56, 0.40, [H("Traditional, free tensor", FREE)], "Head free")
pic(s12, A + "m_free.png", 4.55, 2.62, w=2.80, name="Free tensor box",
    descr="Free uniaxial tensor, delta and beta along x and z, refit at every energy, blind to whether the slab is ZnPc or contamination.")
text(s12, 4.17, 4.48, 3.56, 0.62, [([("84", 26, True, FREE, False), ("  constants per slab", 13, False, INK, False)], {"align": "c"})],
     "Stat free", anchor="ctr")
text(s12, 4.17, 5.15, 3.56, 1.65, [
    B("δ and β along x and z, refit at every energy", bullet=True, bucolor=FREE),
    B("Fits any material, ZnPc or contamination", bullet=True, bucolor=FREE),
    B("Orientation and density inferred afterward", bullet=True, bucolor=FREE)], "Text free")
# ML-DFT tensor
text(s12, 8.12, 2.12, 4.50, 0.40, [H("Direct, ML-DFT tensor", DFT)], "Head ML-DFT")
pic(s12, A + "m_mldft.png", 8.15, 2.72, w=2.05, name="ML-DFT tensor box",
    descr="ML-DFT tensor n(E; gamma, rho), locked to the ZnPc molecule, accepts ZnPc and rejects contamination.")
text(s12, 8.12, 3.85, 2.12, 0.62, [([("2", 26, True, DFT, False), ("  per slab", 13, False, INK, False)], {"align": "c"})],
     "Stat ML-DFT", anchor="ctr")
text(s12, 8.12, 4.42, 2.12, 0.40, [([("γ and ρ", 13, False, INK, True)], {"align": "c"})], "Stat ML-DFT sub")
pic(s12, A + "m_panelb.png", 10.30, 2.58, h=2.42, name="ML-DFT gamma sweep",
    descr="ML-DFT beta and delta for ZnPc as the tilt gamma runs from 0 to 90 degrees, with the resonant energies 284.2, 285.1, 287 and 289 eV marked (dissertation Fig. 4.2b).")
text(s12, 8.12, 5.15, 4.50, 1.65, [
    B("Optics locked to what ZnPc molecules can do", bullet=True, bucolor=DFT),
    B("Fit orientation γ and density ρ directly", bullet=True, bucolor=DFT),
    B("The same two numbers explain every energy and polarization", bullet=True, bucolor=DFT)], "Text ML-DFT")
set_notes(s12, """TIME 1.5 min

SOURCE Dissertation Fig. 4.2a and 4.2b (refl-analysis notebooks/manuscript FIG2.png, panels cropped); Chapter 1 pp. 6 and 7; Chapter 4 pp. 63 and 64 (four uniaxial components per energy per slab, 84 per slab across 21 energies).

SCRIPT This is the core comparison of the analysis, so I want both models on the table before any data. On the left is the film, and it is the same for both. Three slabs, surface, bulk, and buried interface, each with a thickness and a roughness, and conventionally the boundary slabs are where contamination or oxidation is placed. In the middle is the traditional route, the free tensor. In every slab, at every energy, we fit the in-plane and out-of-plane delta and beta. Nothing in it knows what molecule is there, so it will fit ZnPc and contamination equally well, and orientation and density only come out of a second analysis of those constants. That is 84 constants for one slab. On the right is the direct route. The optics are locked to the ZnPc molecule through the ML-DFT tensor, and a slab is described only by how the molecules are oriented, gamma, and how densely they pack, rho. The plot shows what gamma does. Turning that one angle moves the whole spectrum, every resonance at once, so the same two numbers have to explain every energy and polarization we measured.

TRANSITION So what does the traditional route actually give us on this film?""")

# ---------------------------------------------------------------- slide 12b, parameter explosion
lay = s12.slide_layout
s12b = p.slides.add_slide(lay)
lst = p.slides._sldIdLst
ids = list(lst)
new = ids[-1]; lst.remove(new); lst.insert(list(lst).index(ids[11]) + 1, new)
for sh in list(s12b.shapes):
    remove(sh)
for sh in s12.shapes:
    if sh.is_placeholder:
        s12b.shapes._spTree.append(copy.deepcopy(sh._element))
for sh in s12b.shapes:
    if sh.is_placeholder and sh.placeholder_format.type == 1:  # title
        sh.text_frame.paragraphs[0].runs[0].text = "PARAMETER EXPLOSION"
        for r in sh.text_frame.paragraphs[0].runs[1:]:
            r.text = ""
card(s12b, 0.60, 2.05, 4.20, 4.85, "Card forest")
card(s12b, 4.95, 2.05, 7.80, 2.95, "Card growth")
card(s12b, 4.95, 5.15, 7.80, 1.75, "Card consequence")
pic(s12b, A + "fig43a_nolabel.png", 0.78, 2.12, h=4.70, name="Free constants per slab",
    descr="Birefringence and dichroism of each slab, free-tensor constants at every energy (orange) against the ML-DFT tensor (blue) (dissertation Fig. 4.3a).")
cd = XyChartData()
NE = list(range(1, 22))
sf = cd.add_series("Free tensor")
for n in NE:
    sf.add_data_point(n, 12 * n)
sd = cd.add_series("ML-DFT tensor")
for n in NE:
    sd.add_data_point(n, 6)
gf = s12b.shapes.add_chart(XL_CHART_TYPE.XY_SCATTER_LINES_NO_MARKERS, I(5.05), I(2.50), I(4.55), I(2.42), cd)
gf.name = "Parameter growth chart"
ch = gf.chart
ch.has_legend = False
ch.font.size = Pt(11); ch.font.color.rgb = RGBColor.from_string(GREY)
for ser, col, w in zip(ch.plots[0].series, (FREE, DFT), (2.75, 2.75)):
    ser.format.line.color.rgb = RGBColor.from_string(col); ser.format.line.width = Pt(w); ser.smooth = False
xa, ya = ch.category_axis, ch.value_axis
xa.minimum_scale, xa.maximum_scale, xa.major_unit = 0, 21, 7
ya.minimum_scale, ya.maximum_scale, ya.major_unit = 0, 260, 50
for ax, t in ((xa, "Energies measured"), (ya, "Optical parameters, 3 slabs")):
    ax.has_title = True; ax.axis_title.text_frame.text = t
    r = ax.axis_title.text_frame.paragraphs[0].runs[0]; r.font.size = Pt(11); r.font.bold = False
    r.font.color.rgb = RGBColor.from_string(GREY)
    ax.format.line.color.rgb = RGBColor.from_string("8A8F94")
ya.has_major_gridlines = True
ya.major_gridlines.format.line.color.rgb = RGBColor.from_string("E3DED8")
xa.has_major_gridlines = False
text(s12b, 5.10, 2.12, 4.40, 0.40, [H("Every energy adds parameters", GREY)], "Head growth")
text(s12b, 9.75, 2.45, 2.85, 2.45, [
    ([("252", 30, True, FREE, False)], {"after": 0}),
    B("free constants at our 21 energies", 12.5, INK, after=10),
    ([("6", 30, True, DFT, False)], {"after": 0}),
    B("ML-DFT, at any number of energies", 12.5, INK)], "Stat growth", anchor="ctr")
text(s12b, 5.10, 5.22, 3.75, 1.60, [
    H("Only the bulk is pinned"),
    B("Surface and interface constants carry error bars as large as the signal", 12.5)], "Text bulk pinned")
text(s12b, 8.95, 5.22, 3.70, 1.60, [
    H("Gunk layers make it worse"),
    B("Contamination slabs add their own free constants, so outside the bulk we learn almost nothing", 12.5)],
     "Text gunk")
set_notes(s12b, """TIME 1.5 min

SOURCE Dissertation Fig. 4.3a, all three slabs (refl-analysis notebooks/manuscript FIG3.png); Fig. 4.3b parameter counts (N 286 free against 17 ML-DFT); Chapter 4 pp. 63 to 65. The chart is new, 4 tensor components times 3 slabs per energy against 2 times 3 slabs.

SCRIPT On the left is what the free tensor returns for this film, the birefringence and dichroism of each slab, one pair of orange points per energy, against the ML-DFT tensor in blue. Every orange point is its own fit parameter, and nothing ties one energy to the next. The bulk behaves, and its points follow the ML-DFT curves closely. The surface and the buried interface do not. Their error bars are as large as the signal, and a single energy can sit far off the trend of its neighbours. On the right is why this does not get better with more data. Each new energy adds twelve constants to a three-slab model, so at our twenty-one energies the optics alone are 252 parameters, and the whole model is 286. The ML-DFT model carries six optical parameters however many energies we add, so every new energy tightens the same orientation and density instead of adding new unknowns. Once contamination layers are added at the boundaries, each with its own free constants, we are left knowing the bulk and very little else, which is exactly the region we care about.

TRANSITION So here are both models fit to the same twenty-one energies.

VERIFY The 286 against 17 totals from Fig. 4.3b include structural and instrument parameters; 252 against 6 counts the optical tensor only.""")

# ---------------------------------------------------------------- slide 25, uncertainty and the case for energy scans
s25 = [s for s in p.slides if any(sh.name == "Picture 2" for sh in s.shapes)
       and any(sh.has_text_frame and sh.text_frame.text.startswith("How can we ensure") for sh in s.shapes)][0]
card(s25, 0.60, 2.05, 7.55, 4.85, "Card designs")
card(s25, 8.30, 2.05, 4.45, 2.90, "Card uncertainty")
card(s25, 8.30, 5.10, 4.45, 1.80, "Card next")
place(find(s25, "Picture 2"), 0.72, 2.22, 7.30, 7.30 * 4.07 / 8.28)
text(s25, 0.75, 5.95, 7.25, 0.85, [
    B("Four energies placed on the peaks, at random, or by a Gaussian-process design, against a continuous "
      "energy scan at the same total dose. Grey traces are posterior draws, black is the true edge.", 12, GREY)],
     "Caption designs")
pic(s25, A + "uncert_spectrum.png", 8.40, 2.17, w=4.25, name="Uncertainty spectrum",
    descr="Posterior uncertainty of the index at each energy, as a fraction of the prior, for the four sampling designs of Fig. 5.5; dots mark the measured energies.")
text(s25, 8.42, 5.17, 4.21, 1.68, [
    H("Unmeasured energies stay at the prior", RED, 13.5),
    B("Even the best four energy design leaves most of the edge unconstrained", 12, after=6),
    H("Collect RSoXS as energy scans", RED, 13.5),
    B("The same dose spread across the edge pins the buried optical response", 12)], "Text next")
nt = s25.notes_slide.notes_text_frame.text
set_notes(s25, """TIME 1.5 min

SOURCE Dissertation Fig. 5.5 and Chapter 5 pp. 88 and 89; idea from 10-12.pptx slide 7. Top right panel is new, uncert_spectrum.py, the linearized (Laplace) posterior of the same synthetic polystyrene edge, prior, noise, seeds and probe rules as lr-optical-models manuscript/fig5_sensitivity.ipynb.

SCRIPT The same basis generates causal optical constants, so we can ask how well a measurement pins a spectrum. With a synthetic carbon edge of ten transitions, four energies on the resonances reduce the variance of the index by 78 percent, a random set by 69.7, with 53 plus or minus 19 percent typical across 200 random sets, and a Gaussian-process design by 85.6. A continuous scan with larger noise per point reaches 98.7. The plot on the right shows where that missing information lives. It is the uncertainty left at each energy, as a fraction of what we started with. At the measured energies, the dots, it collapses. Within about an electron volt it climbs back toward the prior, and above 288 eV even the best design knows almost nothing. Four energies give only eight observables against 30 parameters, and even tenfold better precision leaves the on-resonance result near 83 percent, so the number and placement of energies set the limit before precision does. That is the situation for every buried interface in this talk, since above the edge ZnPc was measured at only five energies. To resolve the optical response at a buried interface we have to change how we collect RSoXS, spreading the same dose across the edge as energy scans instead of q scans at a handful of energies.

TRANSITION To summarize the second section.

VERIFY The right panel is the linearized posterior, whose variance reductions are 82.9, 63.7, 88.7 and 99.2 percent against the sampled 78.0, 69.7, 85.6 and 98.7 in Fig. 5.5, so the panel shows no percentages. The five ZnPc energies above the edge are 283.7, 284.2, 285.1, 287 and 289 eV.""")

p.save(OUT)
print("saved", OUT)
