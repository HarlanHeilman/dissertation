import re, json, os, shutil, subprocess, unicodedata
W=os.path.expanduser
ROOT=W('~/mnt/dissertation'); OUT=W('~/work/latex'); FIGDIR=W('~/work/word-export')
shutil.rmtree(OUT,ignore_errors=True); shutil.rmtree(FIGDIR,ignore_errors=True)
for d in ('chapters','frontmatter','appendices'): os.makedirs(f'{OUT}/{d}')
os.makedirs(FIGDIR)
tex=open('marked.tex').read()
figs=json.load(open('figs.json'))

# ---------- figure groups ----------
def merge(figs):
    used=set(); groups=[]
    byn={f['n']:f for f in figs}
    for f in figs:
        n=f['n']
        if n in used: continue
        if f['caps'] and not f['blips']:
            # partner: adjacent captionless blip drawing
            for m in (n-1,n+1):
                g=byn.get(m)
                if g and g['blips'] and not g['caps'] and m not in used:
                    used|={n,m}; groups.append(dict(markers=sorted([n,m]),pairs=[(g['blips'][0],f['caps'][0])])); break
            continue
        if f['blips'] and not f['caps']:
            # may be claimed by a later caption-only drawing
            g=byn.get(n+1)
            if g and g['caps'] and not g['blips']: continue
            g=byn.get(n-1)
            if g and g['caps'] and not g['blips']: continue
            used.add(n); groups.append(dict(markers=[n],pairs=[(b,None) for b in f['blips']])); continue
        used.add(n)
        groups.append(dict(markers=[n],pairs=list(zip(f['blips'],f['caps']))))
    return groups
groups=merge(figs)
# second pass for blip-only drawings skipped because their caption neighbour came later
claimed={m for g in groups for m in g['markers']}
for f in figs:
    if f['n'] not in claimed:
        groups.append(dict(markers=[f['n']],pairs=[(b,None) for b in f['blips']]))

ESC={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
def esc(s): return ''.join(ESC.get(c,c) for c in s)
caprx=re.compile(r'^(?:Figure|FIG\.)\s*(S?\d+(?:\.\d+)?)\s*(.*)$',re.S)
figlabels=set(); report=[]
def figenv(blip,cap):
    capt,hasmath=cap if cap else ('',False)
    m=caprx.match(capt.strip())
    if m: num,body=m.group(1),m.group(2).strip()
    else: num,body=None,capt.strip()
    src=W('~/work/fx/word/')+blip; ext=os.path.splitext(blip)[1].lower()
    name=f'fig{num.replace(".","-")}' if num else 'unlabeled-'+os.path.splitext(os.path.basename(blip))[0]
    if ext=='.emf':
        subprocess.run(['soffice','--headless','--convert-to','pdf','--outdir','/tmp/emf',src],capture_output=True)
        conv='/tmp/emf/'+os.path.splitext(os.path.basename(blip))[0]+'.pdf'
        if os.path.exists(conv): shutil.copy(conv,f'{FIGDIR}/{name}.pdf'); ext='.pdf'
        else: shutil.copy(src,f'{FIGDIR}/{name}.emf'); report.append(f'{name}: EMF could not be converted')
    else: shutil.copy(src,f'{FIGDIR}/{name}{ext}')
    lab=f'fig:{num}' if num else None
    if lab: figlabels.add(num)
    sm=re.match(r'(.+?[.!?])(\s|$)',body)
    short=sm.group(1) if sm else body
    lines=['\\begin{figure}[tbp]','  \\centering',f'  \\includegraphics[width=\\linewidth]{{{name}}}']
    if body:
        if hasmath: lines.append('  % TODO caption contains equations that were flattened to plain text in the Word export; retypeset them.')
        lines.append(f'  \\caption[{esc(short)}]{{{esc(body)}}}')
    else: lines.append('  \\caption{TODO caption}')
    if lab: lines.append(f'  \\label{{{lab}}}')
    lines.append('\\end{figure}')
    return '\n'.join(lines), (num or name)

# ---------- locate insertion points ----------
def find_marker(n): return tex.find(f'FIGMARKER{n}X')
HEAD=re.compile(r'\\(chapter|section|subsection|subsubsection)[\[{]')
inserts=[]
for g in groups:
    pos=min(find_marker(m) for m in g['markers'] if find_marker(m)>=0)
    linestart=tex.rfind('\n',0,pos)+1
    # inside a heading?
    hs=None
    for hm in HEAD.finditer(tex,max(0,linestart-400),pos):
        hs=hm
    line=tex[linestart:tex.find('\n',pos)]
    capstart=tex.rfind('\\caption{',0,pos)
    if hs and tex.find('\\label{',hs.start())>pos:
        ip=tex.find('}',tex.find('\\label{',hs.start()))+1
    elif capstart>=0 and tex.find('\\end{longtable}',capstart)>pos and tex.rfind('\\begin{longtable}',0,pos)>tex.rfind('\\end{longtable}',0,pos):
        ip=tex.find('\\end{longtable}',pos)+len('\\end{longtable}')
    else:
        nb=tex.find('\n\n',pos); ip=nb if nb>=0 else len(tex)
    envs=[figenv(b,c) for b,c in g['pairs']]
    envs.sort(key=lambda e:(e[1].startswith('S'), [int(x) if x.isdigit() else x for x in re.split(r'[.S]',e[1]) if x]))
    inserts.append((ip,'\n\n'+'\n\n'.join(e[0] for e in envs)+'\n'))
for ip,s in sorted(inserts,reverse=True): tex=tex[:ip]+s+tex[ip:]
# strip markers and word images
tex=re.sub(r' ?FIGMARKER\d+X ?','',tex)
tex=re.sub(r'(\\protect)?\\pandocbounded\{\\includegraphics\[keepaspectratio\]\{media/[^}]*\}\}','',tex)
tex=re.sub(r'\\begin\{figure\}\s*\\centering\s*\\caption\{\}\s*\\end\{figure\}\n?','',tex)
tex=re.sub(r'\\caption\{(?:\s*\\\\\s*|\s*\\strut\s*\\\\)+\s*',r'\\caption{',tex)
# clean headings: \texorpdfstring{ X}{X} leftovers and \hfill\break
tex=re.sub(r'\\texorpdfstring\{\s*\\hfill\\break\s*','\\\\texorpdfstring{',tex)
tex=re.sub(r'\\hfill\\break\s*','',tex)

# ---------- tables ----------
tabcount={}
def tabfix(m):
    body=m.group(2)
    body=re.sub(r'^(?:Table|TABLE)\s*(?:S?[IVX]+|\d+(?:\.\d+)?)?\s*\.?\s*','',body.lstrip())
    return '\\caption{'+body
tex=re.sub(r'\\caption\{(\\protect\\phantomsection\\label\{_Toc\d+\}\{\})?((?:Table|TABLE)[^\n]*)',tabfix,tex)
tex=re.sub(r'\\protect\\phantomsection\\label\{_Toc\d+\}\{\}','',tex)

# ---------- split ----------
chap_rx=re.compile(r'^\\chapter\{',re.M)
starts=[m.start() for m in chap_rx.finditer(tex)]
refpos=tex.find('\\section{REFERENCES}'); apppos=tex.find('\\section{APPENDIX')
def after_label(p): return tex.find('}',tex.find('\\label{',p))+1
chapters=[('ch1-introduction','Introduction \\& Background','chap:introduction'),
 ('ch2-molecular-films','Molecular Films and Their Resonant Optical Response','chap:molecular-films'),
 ('ch3-reflectivity-methods','Fundamentals and Methods of Polarized Resonant Soft X-ray Reflectivity','chap:methods'),
 ('ch4-buried-interfaces','Sub-monolayer Tracking of Molecular States at Buried Interfaces','chap:znpc'),
 ('ch5-individual-resonances','Tracking the Evolution of Individual Resonances','chap:resonances'),
 ('ch6-xray-atlas','X-ray Atlas -- an open science project for optical constants','chap:xray-atlas'),
 ('ch7-conclusion','Conclusion \\& Outlook','chap:conclusion')]
body_starts=[s for s in starts if not tex[s:s+40].startswith(('\\chapter{Table of','\\chapter{Table'))]
assert len(body_starts)==7, [tex[s:s+50] for s in starts]
bounds=body_starts+[refpos]
def shift(s):
    s=re.sub(r'\\subsection(?=[\[{*])',r'\\section',s)
    s=re.sub(r'\\subsubsection(?=[\[{*])',r'\\subsection',s)
    return s
chapnum={}
for i,(fn,title,lab) in enumerate(chapters):
    body=tex[after_label(bounds[i]):bounds[i+1]].strip('\n')
    open(f'{OUT}/chapters/{fn}.tex','w').write(f'\\chapter{{{title}}}\\label{{{lab}}}\n\n'+shift(body)+'\n')
app=tex[after_label(apppos):]
app=re.sub(r'\\end\{document\}\s*$','',app)
open(f'{OUT}/appendices/appA-supporting-information.tex','w').write('\\chapter{Manuscript Supporting Information}\\label{app:supporting-information}\n\n'+app.strip('\n')+'\n')
front=tex[:body_starts[0]]
open(W('~/work/front_raw.tex'),'w').write(front)
json.dump(dict(figlabels=sorted(figlabels),report=report),open(W('~/work/convert_report.json'),'w'),indent=1)
print('groups',len(groups),'figures',len(figlabels),report)
