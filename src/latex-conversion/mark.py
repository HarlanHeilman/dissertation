# insert FIGMARKER runs before each top-level drawing, and collect figure metadata
import json, zipfile, shutil, copy
from lxml import etree
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main';A='http://schemas.openxmlformats.org/drawingml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships';M='http://schemas.openxmlformats.org/officeDocument/2006/math'
q=lambda ns,t:'{%s}%s'%(ns,t)
doc=etree.parse('fx/word/document.xml'); rels=etree.parse('fx/word/_rels/document.xml.rels')
rid={r.get('Id'):r.get('Target') for r in rels.getroot()}
def bad(el): return any(a.tag.endswith('Fallback') or a.tag.endswith('txbxContent') for a in el.iterancestors())
def captext(tb):
    paras=[]
    for p in tb.iter(q(W,'p')):
        s=''
        for x in p.iter(q(W,'t'),q(M,'t')): s+=x.text or ''
        paras.append(s)
    return ' '.join(paras).strip(), tb.find('.//'+q(M,'oMath')) is not None
draws=[d for d in doc.getroot().iter(q(W,'drawing')) if not bad(d)]
# also VML pict fallbacks outside AlternateContent are left alone
figs=[]
for n,d in enumerate(draws):
    bl=[rid.get(b.get(q(R,'embed'))) for b in d.iter(q(A,'blip'))]
    caps=[captext(t) for t in d.iter(q(W,'txbxContent'))]
    caps=[c for c in caps if c[0]]
    run=next(a for a in d.iterancestors() if a.tag==q(W,'r'))
    nr=etree.Element(q(W,'r')); t=etree.SubElement(nr,q(W,'t')); t.text=f' FIGMARKER{n}X '
    t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
    run.addprevious(nr)
    # drop the drawing itself (and its AlternateContent wrapper); figures are rebuilt from figs.json
    ac=next((a for a in d.iterancestors() if a.tag.endswith('}AlternateContent')),None)
    (ac if ac is not None else d).getparent().remove(ac if ac is not None else d)
    figs.append(dict(n=n,blips=bl,caps=caps))
doc.write('fx/word/document.xml',xml_declaration=True,encoding='UTF-8',standalone=True)
# rezip
zin=zipfile.ZipFile('final.docx'); zout=zipfile.ZipFile('marked.docx','w',zipfile.ZIP_DEFLATED)
for it in zin.infolist():
    data=open('fx/word/document.xml','rb').read() if it.filename=='word/document.xml' else zin.read(it.filename)
    zout.writestr(it,data)
zout.close()
json.dump(figs,open('figs.json','w'),ensure_ascii=False,indent=1)
print(len(figs))
