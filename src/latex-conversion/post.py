import re, os, json, glob, unicodedata
W=os.path.expanduser; OUT=W('~/work/latex')
rep=json.load(open(W('~/work/convert_report.json'))); figl=set(rep['figlabels'])
files=glob.glob(OUT+'/chapters/*.tex')+glob.glob(OUT+'/appendices/*.tex')
# ---- table labels ----
tabn={}
def number_tables(path,chap):
    s=open(path).read(); k=[0]
    def f(m):
        k[0]+=1; lab=f'tab:{chap}.{k[0]}' if chap!='S' else f'tab:S{k[0]}'
        return m.group(0)
    # insert label right after caption closing brace: find \caption{ ... }\tabularnewline
    out=''; i=0
    for m in re.finditer(r'\\caption\{',s):
        if 'longtable' not in s[max(0,m.start()-1500):m.start()] : continue
    pieces=s.split('\\tabularnewline')
    return s
# simpler: label tables via caption -> \caption{...}\label{} using brace matching
def match_brace(s,i):
    d=0
    for j in range(i,len(s)):
        if s[j]=='{' and s[j-1]!='\\': d+=1
        elif s[j]=='}' and s[j-1]!='\\':
            d-=1
            if d==0: return j
    return -1
tablabels=set()
for p in sorted(files):
    s=open(p).read()
    fn=os.path.basename(p)
    chap='S' if fn.startswith('app') else fn[2]
    k=0; out=[]; i=0
    while True:
        j=s.find('\\begin{longtable}',i)
        if j<0: out.append(s[i:]); break
        c=s.find('\\caption{',j); e=s.find('\\end{longtable}',j)
        if 0<=c<e:
            k+=1; cb=match_brace(s,c+8); lab=f'tab:{chap}.{k}' if chap!='S' else f'tab:S{k}'
            tablabels.add(lab[4:])
            out.append(s[i:cb+1]+f'\\label{{{lab}}}'); i=cb+1
        else:
            out.append(s[i:e]); i=e
    s=''.join(out)
    open(p,'w').write(s)
for p in sorted(files):
    s=open(p).read()
    # ---- cross references ----
    def fref(m):
        word,sp,num=m.group(1),m.group(2),m.group(3)
        if num in figl: return f'{word}~\\ref{{fig:{num}}}'
        return m.group(0)
    s=re.sub(r'\b(Figures?|Figs?\.|FIG\.)(\s+|~)(S?\d+(?:\.\d+)?)(?=[a-z]?\b|[a-z(),;:.\\]|$)',lambda m: fref(m) if not m.group(3).endswith('.') else m.group(0),s)
    def tref(m):
        num=m.group(3)
        if num in tablabels: return f'{m.group(1)}~\\ref{{tab:{num}}}'
        return m.group(0)
    s=re.sub(r'\b(Tables?|TABLE)(\s+|~)(S?\d+(?:\.\d+)?)\b',tref,s)
    open(p,'w').write(s)
print('tables',sorted(tablabels))
# report unresolved hardcoded references
for p in sorted(files):
    s=open(p).read()
    left=re.findall(r'\b(?:Figures?|Figs?\.|FIG\.|Tables?|TABLE)\s+S?\d+(?:\.\d+)?',s)
    if left: print(os.path.basename(p),'unresolved:',sorted(set(left)))
