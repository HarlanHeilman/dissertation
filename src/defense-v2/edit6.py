"""Slide 12, print the parameter counts per slab and times three slabs on the scaling charts."""
import sys
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
SRC, OUT = sys.argv[1:3]
p = Presentation(SRC)
s = [s for s in p.slides if s.shapes.title is not None and s.shapes.title.text == "TRADITIONAL VS DIRECT MEASUREMENT"][0]
I = lambda v: int(round(v * 914400))
C = "{http://schemas.openxmlformats.org/drawingml/2006/chart}"
for sh in s.shapes:
    if sh.name in ("Free parameters vs energies", "ML-DFT parameters vs energies"):
        for d in list(sh.chart._chartSpace.iter(C + "dLbls")):
            d.getparent().remove(d)


def stat(x, y, w, big, small, color, name):
    tb = s.shapes.add_textbox(I(x), I(y), I(w), I(0.6)); tb.name = name
    tf = tb.text_frame; tf.word_wrap = True
    for i, (t, size, bold, col) in enumerate(((big, 15, True, color), (small, 11.5, False, "1F1F1F"))):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        r = para.add_run(); r.text = t; r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = RGBColor.from_string(col)


def find(n):
    return [sh for sh in s.shapes if sh.name == n][0]


for n, y, h in (("Free parameters vs energies", 3.78, 1.22), ("ML-DFT parameters vs energies", 3.66, 1.30)):
    sh = find(n); sh.top, sh.height = I(y), I(h)
for n in ("Text structure", "Text free", "Text ML-DFT"):
    find(n).top = I(5.58)
stat(3.97, 5.00, 1.90, "84 per slab", "\u00d7 3 slabs = 252", "C65A11", "Stat free")
stat(8.27, 4.96, 1.90, "2 per slab", "\u00d7 3 slabs = 6", "1F6FB0", "Stat ML-DFT")
p.save(OUT); print("saved")
