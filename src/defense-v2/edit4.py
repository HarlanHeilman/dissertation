"""Slide 12, replace the cropped Fig. 4.2/4.3 images with the native PowerPoint objects from figs_1.pptx,
grouped and scaled. Slide 25, replace with one simple 'measured vs not measured' visual. Nothing else is touched."""
import copy, sys, io
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.opc.package import Part
from pptx.opc.packuri import PackURI
from lxml import etree

SRC, FIGS, OUT = sys.argv[1:4]
A = "/home/claude/assets/"
p = Presentation(SRC)
fp = Presentation(FIGS)
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
RID = "{%s}" % NS["r"]
EMU = 914400


def I(v):
    return int(round(v * EMU))


def bbox(el):
    x = el.find(".//a:xfrm/a:off", NS) if etree.QName(el).localname != "grpSp" else el.find("p:grpSpPr/a:xfrm/a:off", NS)
    e = x.getnext()
    return (int(x.get("x")) / EMU, int(x.get("y")) / EMU, int(e.get("cx")) / EMU, int(e.get("cy")) / EMU)


def pick(slide, x0, y0, x1, y1, exclude=(), tol=0.03):
    out = []
    for el in slide.shapes._spTree:
        tag = etree.QName(el).localname
        if tag in ("nvGrpSpPr", "grpSpPr", "extLst"):
            continue
        nm = el.find(".//p:cNvPr", NS).get("name")
        if nm in exclude:
            continue
        x, y, w, h = bbox(el)
        if x >= x0 - tol and y >= y0 - tol and x + w <= x1 + tol and y + h <= y1 + tol:
            out.append(el)
    return out


media_cache = {}


def import_rels(el, src_part, dst_part):
    for node in el.iter():
        for att, val in list(node.attrib.items()):
            if not att.startswith(RID):
                continue
            rel = src_part.rels[val]
            tp = rel.target_part
            key = str(tp.partname)
            if key not in media_cache:
                ext = key.rsplit(".", 1)[-1]
                pn = dst_part.package.next_partname("/ppt/media/imgfig%d." + ext)
                media_cache[key] = Part(pn, tp.content_type, dst_part.package, tp.blob)
            node.set(att, dst_part.relate_to(media_cache[key], rel.reltype))


THEME = {"dk1": "000000", "lt1": "FFFFFF", "dk2": "0E2841", "lt2": "E8E8E8", "accent1": "156082", "accent2": "E97132",
         "accent3": "196B24", "accent4": "0F9ED5", "accent5": "A02B93", "accent6": "4EA72E", "hlink": "467886", "folHlink": "96607D"}
CMAP = {"bg1": "lt1", "tx1": "dk1", "bg2": "lt2", "tx2": "dk2"}
FONTS = {"+mn-lt": "Aptos", "+mj-lt": "Aptos Display", "+mn-ea": "Aptos", "+mn-cs": "Aptos"}
AFTER_LATIN = ("ea", "cs", "sym", "hlinkClick", "hlinkMouseOver", "rtl", "extLst")


def freeze_theme(el):
    """Resolve the figure deck's theme colors and fonts so the objects look the same in this deck."""
    Aa = "{%s}" % NS["a"]
    for sc in list(el.iter(Aa + "schemeClr")):
        v = sc.get("val")
        if v == "phClr":
            continue
        new = etree.Element(Aa + "srgbClr"); new.set("val", THEME[CMAP.get(v, v)])
        for ch in sc:
            new.append(ch)
        sc.getparent().replace(sc, new)
    for tag in ("latin", "ea", "cs"):
        for f in el.iter(Aa + tag):
            if f.get("typeface") in FONTS:
                f.set("typeface", FONTS[f.get("typeface")])
    for tb in el.iter("{%s}txBody" % NS["p"]):
        bp = tb.find("a:bodyPr", NS)
        if bp is not None:
            bp.set("wrap", "none")
        for rp in list(tb.iter(Aa + "rPr")) + list(tb.iter(Aa + "endParaRPr")) + list(tb.iter(Aa + "defRPr")):
            if rp.find("a:latin", NS) is None:
                lat = etree.Element(Aa + "latin"); lat.set("typeface", "Aptos")
                nxt = [c for c in rp if etree.QName(c).localname in AFTER_LATIN]
                (nxt[0].addprevious(lat) if nxt else rp.append(lat))


def next_id(slide):
    return max(int(e.get("id")) for e in slide.shapes._spTree.iter("{%s}cNvPr" % NS["p"])) + 1


def make_group(dst, src_slide, members, x, y, w=None, h=None, name="Group"):
    xs = [bbox(m) for m in members]
    cx0 = min(b[0] for b in xs); cy0 = min(b[1] for b in xs)
    cx1 = max(b[0] + b[2] for b in xs); cy1 = max(b[1] + b[3] for b in xs)
    cw, chh = cx1 - cx0, cy1 - cy0
    s = (w / cw) if w else (h / chh)
    w, h = cw * s, chh * s
    nid = next_id(dst)
    P = "{%s}" % NS["p"]; Aa = "{%s}" % NS["a"]
    g = etree.Element(P + "grpSp", nsmap={"p": NS["p"], "a": NS["a"]})
    nv = etree.SubElement(g, P + "nvGrpSpPr")
    c = etree.SubElement(nv, P + "cNvPr"); c.set("id", str(nid)); c.set("name", name)
    etree.SubElement(nv, P + "cNvGrpSpPr"); etree.SubElement(nv, P + "nvPr")
    gp = etree.SubElement(g, P + "grpSpPr"); xf = etree.SubElement(gp, Aa + "xfrm")
    for tag, a1, v1, a2, v2 in (("off", "x", x, "y", y), ("ext", "cx", w, "cy", h), ("chOff", "x", cx0, "y", cy0), ("chExt", "cx", cw, "cy", chh)):
        e = etree.SubElement(xf, Aa + tag); e.set(a1, str(I(v1))); e.set(a2, str(I(v2)))
    nid += 1
    for m in members:
        el = copy.deepcopy(m)
        for cn in el.iter(P + "cNvPr"):
            cn.set("id", str(nid)); nid += 1
            for ex in cn.findall("a:extLst", NS):
                cn.remove(ex)
        for tag in ("stCxn", "endCxn"):
            for e in el.iter(Aa + tag):
                e.getparent().remove(e)
        for node in el.iter():  # text and strokes scale with the group
            if node.get("sz") and etree.QName(node).localname in ("rPr", "defRPr", "endParaRPr"):
                node.set("sz", str(max(100, int(round(int(node.get("sz")) * s / 50.0) * 50))))
            if etree.QName(node).localname == "ln" and node.get("w"):
                node.set("w", str(int(int(node.get("w")) * s)))
        freeze_theme(el)
        import_rels(el, src_slide.part, dst.part)
        g.append(el)
    from pptx.oxml import parse_xml
    g = parse_xml(etree.tostring(g))
    dst.shapes._spTree.append(g)
    return g, s, w, h


def find(slide, name):
    return [sh for sh in slide.shapes if sh.name == name][0]


def remove(sh):
    sh._element.getparent().remove(sh._element)


def place(sh, x, y, w=None, h=None):
    sh.left, sh.top = I(x), I(y)
    if w is not None:
        sh.width = I(w)
    if h is not None:
        sh.height = I(h)


# ---------------------------------------------------------------- slide 12
s12 = [s for s in p.slides if s.shapes.title is not None and s.shapes.title.text == "TRADITIONAL VS DIRECT MEASUREMENT"][0]
f42, f43 = fp.slides[12], fp.slides[14]
for n in ("Structure model", "Free tensor box", "ML-DFT tensor box", "ML-DFT gamma sweep", "Free constants per slab"):
    remove(find(s12, n))
struct = pick(f42, 2.55, 1.85, 5.47, 4.12, exclude=("TextBox 167",))
dft = pick(f42, 5.70, 2.15, 7.31, 2.96)
free = pick(f42, 5.70, 2.97, 7.31, 4.06)
panb = pick(f42, 7.48, 1.95, 9.85, 4.16, exclude=("TextBox 175",))
f43a = [copy.deepcopy(e) for e in pick(f43, 4.80, 0.80, 8.30, 6.60)]
from PIL import Image, ImageDraw
for e in f43a:
    if e.find(".//p:cNvPr", NS).get("name") == "Picture 1":
        CROP = 0.738  # keep panel (a); panel (b) carries the AIC/BIC bars
        blip = e.find(".//a:blip", NS); rid = blip.get(RID + "embed")
        im = Image.open(io.BytesIO(f43.part.rels[rid].target_part.blob))
        im = im.crop((0, 0, im.width, int(im.height * CROP)))
        ImageDraw.Draw(im).rectangle((0, 100, 150, 240), fill="white")  # the (a) label
        buf = io.BytesIO(); im.save(buf, "PNG")
        npart = Part(PackURI("/ppt/media/fig43a_panel_a.png"), "image/png", fp.part.package, buf.getvalue())
        blip.set(RID + "embed", f43.part.relate_to(npart, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"))
        ext = e.find(".//a:xfrm/a:ext", NS); ext.set("cy", str(int(int(ext.get("cy")) * CROP)))
print("members", len(struct), len(dft), len(free), len(panb), len(f43a))
SC = 1.10  # same scale for both tensor boxes
place(find(s12, "Card models"), 0.60, 2.05, 3.15, 4.85)
place(find(s12, "Card free"), 3.90, 2.05, 4.15, 4.85)
place(find(s12, "Card ML-DFT"), 8.20, 2.05, 4.55, 4.85)
for n, x, w in (("Head structure", 0.72, 2.9), ("Text structure", 0.72, 2.95), ("Head free", 4.02, 3.9), ("Text free", 4.02, 3.9),
                ("Head ML-DFT", 8.32, 4.3), ("Text ML-DFT", 8.32, 4.3)):
    sh = find(s12, n); place(sh, x, sh.top / EMU, w)
g, s, w, h = make_group(s12, f42, struct, 0.72, 2.62, w=2.90, name="Structure model (native)")
print("struct", round(s, 2), round(w, 2), round(h, 2))
g, s, w, h = make_group(s12, f42, free, 4.00, 2.65, w=1.61 * SC, name="Free tensor box (native)")
print("free", round(s, 2), round(w, 2), round(h, 2)); free_h = h
g, s, w, h = make_group(s12, f43, f43a, 5.88, 2.55, w=2.07, name="Free constants per slab (native)")
print("f43a", round(s, 2), round(w, 2), round(h, 2))
g, s, w, h = make_group(s12, f42, dft, 8.30, 2.72, w=1.61 * SC, name="ML-DFT tensor box (native)")
print("dft", round(s, 2), round(w, 2), round(h, 2)); dft_h = h
g, s, w, h = make_group(s12, f42, panb, 10.17, 2.55, h=2.35, name="ML-DFT gamma sweep (native)")
print("panb", round(s, 2), round(w, 2), round(h, 2))
place(find(s12, "Stat free"), 3.97, 2.62 + free_h + 0.25, 1.85, 0.62)
place(find(s12, "Stat ML-DFT"), 8.27, 2.70 + dft_h + 0.25, 1.85, 0.62)
place(find(s12, "Stat ML-DFT sub"), 8.27, 2.70 + dft_h + 0.80, 1.85, 0.40)
# fix the z-order, cards first so the new groups sit above them
tree = s12.shapes._spTree
for n in ("Card models", "Card free", "Card ML-DFT"):
    el = find(s12, n)._element; tree.remove(el); tree.insert(2, el)

# ---------------------------------------------------------------- slide 25
s25 = [s for s in p.slides if s.shapes.title is not None and s.shapes.title.text.startswith("How can we ensure")][0]
for n in ("Picture 2", "Caption designs", "Uncertainty spectrum", "Card uncertainty", "Card next", "Text next"):
    remove(find(s25, n))
cd = find(s25, "Card designs"); place(cd, 0.60, 2.05, 12.15, 4.85); cd.name = "Card gaps"
pic = s25.shapes.add_picture(A + "unknown_gaps.png", I(0.80), I(2.20), I(8.40))
pic.name = "Measured vs not measured"
pic._element.find(".//p:cNvPr", NS).set("descr", "A synthetic carbon-edge spectrum measured at four energies (red dots). Grey traces are spectra that agree with those four points; they agree where we measured and spread widely at the energies we did not measure.")
tb = s25.shapes.add_textbox(I(9.45), I(2.55), I(3.10), I(3.90)); tb.name = "Text gaps"
tf = tb.text_frame; tf.word_wrap = True
rows = [("Where we measured", "CA1237", "every curve agrees"),
        ("Where we did not", "424C4E", "many spectra fit the same data"),
        ("At a buried interface", "CA1237", "we need the whole edge, not a few energies")]
for i, (hd, col, body) in enumerate(rows):
    para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    r = para.add_run(); r.text = hd; r.font.size = Pt(17); r.font.bold = True; r.font.color.rgb = RGBColor.from_string(col)
    para.space_after = Pt(1)
    para2 = tf.add_paragraph(); para2.space_after = Pt(16)
    r = para2.add_run(); r.text = body; r.font.size = Pt(15); r.font.color.rgb = RGBColor.from_string("1F1F1F")
ns_ = s25.notes_slide.notes_text_frame
ns_.text = "TIME 1 min"
for t in ["", "SOURCE Synthetic polystyrene carbon edge from dissertation Fig. 5.5 and Chapter 5 pp. 88 and 89 (lr-optical-models manuscript/fig5_sensitivity.ipynb, 'On peaks' design). Grey traces are draws from the linearized posterior given the four red points, unknown_gaps.py.",
          "", "SCRIPT Here is the problem in one picture. We measure a spectrum at four energies, the red points. Every grey curve is a spectrum that agrees with those four points within the noise. Where we measured, they all agree. Below 286 eV they agree because the points pin the peaks there. Above that, where we did not measure, they go everywhere, and nothing in the data can tell them apart. That is the situation at every buried interface in this talk, ZnPc was measured at only five energies above the edge. Even the best placed four energies leave most of the edge unknown. To resolve the optical response at a buried interface we have to change how we collect RSoXS, and measure across the whole edge rather than at a handful of energies.",
          "", "TRANSITION To summarize the second section.",
          "", "BACKUP NUMBERS Fig. 5.5 variance reduction over 283 to 290 eV, on peaks 78.0 percent, random 69.7, GP 85.6, continuous energy scan at equal dose 98.7."]:
    ns_.add_paragraph().text = t

p.save(OUT)
print("saved")
