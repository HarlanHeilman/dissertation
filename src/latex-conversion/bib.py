import re, os, glob, unicodedata
W=os.path.expanduser; OUT=W('~/work/latex')
src=open(W('~/work/cited.bib')).read()
entries=re.split(r'\n(?=@)',src.strip())
STOP={'a','an','the','on','of','in','and','for','to','with','by','from','at','la','le','der','die','das','des','du','via','is'}
def asc(s): return unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode()
def field(e,name):
    m=re.search(r'\n\s*'+name+r'\s*=\s*\{',e)
    if not m: return ''
    i=m.end(); d=1; j=i
    while d and j<len(e):
        if e[j]=='{': d+=1
        elif e[j]=='}': d-=1
        j+=1
    return e[i:j-1]
def strip_field(e,name):
    m=re.search(r'\n\s*'+name+r'\s*=\s*\{',e)
    if not m: return e
    i=m.end(); d=1; j=i
    while d: 
        if e[j]=='{': d+=1
        elif e[j]=='}': d-=1
        j+=1
    if j<len(e) and e[j]==',': j+=1
    return e[:m.start()]+e[j:]
keymap={}; used=set(); out=[]
for e in entries:
    m=re.match(r'@(\w+)\{([^,]+),',e); typ,key=m.group(1),m.group(2)
    au=field(e,'author') or field(e,'editor') or field(e,'title')
    first=re.sub(r'[{}\\]','',au.split(' and ')[0])
    last=first.split(',')[0] if ',' in first else first.split()[-1] if first.split() else 'anon'
    last=re.sub(r'[^a-z]','',asc(last).lower()) or 'anon'
    yr=re.search(r'\d{4}',field(e,'date') or field(e,'year')); yr=yr.group(0) if yr else 'nd'
    words=[w for w in re.findall(r'[a-z]+',asc(re.sub(r'[{}\\]','',field(e,'title'))).lower()) if w not in STOP]
    nk=f'{last}{yr}{words[0] if words else ""}'
    base=nk; c=ord('a')
    while nk in used: nk=base+chr(c); c+=1
    used.add(nk); keymap[key]=nk
    e=e.replace(f'{{{key},',f'{{{nk},',1)
    e=strip_field(e,'abstract')
    out.append(e)
open(OUT+'/references.bib','w').write('\n\n'.join(out)+'\n')
for p in glob.glob(OUT+'/**/*.tex',recursive=True):
    s=open(p).read()
    s=re.sub(r'\\(autocite|cite|textcite|parencite)(\[[^\]]*\])?\{([^}]*)\}',lambda m:'\\%s%s{%s}'%(m.group(1),m.group(2) or '',','.join(keymap.get(k.strip(),k.strip()) for k in m.group(3).split(','))),s)
    open(p,'w').write(s)
missing=set()
for p in glob.glob(OUT+'/**/*.tex',recursive=True):
    for m in re.finditer(r'\\autocite\{([^}]*)\}',open(p).read()):
        for k in m.group(1).split(','):
            if k not in used: missing.add(k)
print(len(out),'entries; missing keys',missing)
print(list(keymap.values())[:12])
