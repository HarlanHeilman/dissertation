import os
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
D = os.path.expanduser("~/mnt/dissertation")
prs = Presentation(f"{D}/defense-draft-v1.pptx")
keep = 22
lst = prs.slides._sldIdLst
for i, sid in enumerate(list(lst), 1):
    if i != keep:
        prs.part.drop_rel(sid.rId); lst.remove(sid)
s = prs.slides[0]
heads = {"Conformations": "Structural deformations", "Chemical reactions": "Chemical deformations",
         "Hybridization": "Electronic deformations"}
for sh in s.shapes:
    if sh.has_text_frame and sh.text_frame.text in heads:
        sh.text_frame.paragraphs[0].runs[0].text = heads[sh.text_frame.text]
cards = [731519, 4462139, 8188606]
caps = [("Torsion", "Tautomerization"), ("Electrochemistry", "Photoacid-catalyzed reaction"),
        ("Metal–molecule hybridization", "Applied bias")]
imgs = [("1a-torsion", "1b-tautomerization"), ("2a-electrochemistry", "2b-reaction"),
        ("3a-hybridization", "3b-gate-bias")]
IW = 2926080; IH = int(IW * 640 / 1300)
SL = RGBColor(0x5E, 0x6A, 0x71)
def tb(x, y, w, txt, size, color=SL):
    t = s.shapes.add_textbox(Emu(x), Emu(y), Emu(w), Emu(300000))
    tf = t.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = Emu(0)
    r = tf.paragraphs[0].add_run(); r.text = txt
    r.font.size = Pt(size); r.font.color.rgb = color
    return t
for cx, (c1, c2), (i1, i2) in zip(cards, caps, imgs):
    ix = cx + (3214801 - IW) // 2
    for y_cap, y_img, cap, im in ((2530000, 2800000, c1, i1), (4300000, 4570000, c2, i2)):
        tb(cx + 252000, y_cap, 2900000, cap, 14)
        s.shapes.add_picture(f"{im}.png", Emu(ix), Emu(y_img), Emu(IW), Emu(IH))
NOTES = """TIME
About 30 s, transitional.

SCRIPT
The same molecule can present a different optical response depending on its environment. Structurally, a backbone can twist or a proton can move between tautomers. Chemically, an electrode can oxidize the film while electrolyte anions swell into it to balance the charge, or a photoacid can cleave a protecting group, as in a chemically amplified resist. Electronically, the frontier orbitals can hybridize with a metal, or an applied bias can add an electron to the LUMO or remove one from the HOMO. A reference spectrum from a separate film or from static DFT captures none of these.

TRANSITION
So the optical response has to be measured in place, which is what scattering offers."""
open("speaker-notes.txt","w").write(NOTES + "\n")
prs.save("altering-optical-response.pptx")
print(os.path.getsize("altering-optical-response.pptx"))
