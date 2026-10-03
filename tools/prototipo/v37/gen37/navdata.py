# -*- coding: utf-8 -*-
"""Extrai de cada tela: título, estado, links (rótulo→destino), ações com efeito (rótulo→resultado), formulários (título, campos, confirmar)."""
import json, os, re, html
HERE=os.path.dirname(os.path.abspath(__file__)); PROJ=os.path.join(HERE,'project')
CAT=json.load(open(os.path.join(HERE,'..','catalogo.json')))
def txt(s): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s))).strip()
def screen(n):
    s=open(os.path.join(PROJ,n)).read()
    spec=json.loads(re.search(r'const SPEC = (\[.*?\]);\n',s,re.S).group(1)) if 'const SPEC' in s else []
    body=re.sub(r'<script.*?</script>','',s,flags=re.S)
    nav=re.search(r'<nav aria-label="Áreas".*?</nav>',body,re.S)
    main=body.replace(nav.group(0),'') if nav else body
    title=txt((re.search(r'<h1[^>]*>(.*?)</h1>',main,re.S) or re.search(r'<title>(.*?)</title>',s,re.S)).group(1))
    links=[]
    for m in re.finditer(r'<a\s([^>]*)>(.*?)</a>',main,re.S):
        h=re.search(r'href="([^"#]+\.dc\.html)"',m.group(1))
        if not h: continue
        t=txt(m.group(2)) or (re.search(r'aria-label="([^"]*)"',m.group(1)) or [0,'[ícone]'])[1]
        t=t.replace('›','').strip()[:80]
        if (t,h.group(1)) not in links: links.append((t,h.group(1)))
    acts=[]
    for w in spec:
        if w.get('type')=='msg':
            for o,msg in zip(w['opts'],w['msgs']): acts.append((txt(o),txt(msg)))
    forms=[]
    for m in re.finditer(r'<aside[^>]*>(.*?)</aside>',s,re.S):
        a=m.group(1)
        t=txt((re.search(r'<h2[^>]*>(.*?)</h2>',a,re.S) or [0,''])[1]) if re.search(r'<h2',a) else ''
        labels=[txt(x) for x in re.findall(r'<label[^>]*>(.*?)</label>',a,re.S)]
        labels+= [txt(x) for x in re.findall(r'<span style="font-size: 12px; font-weight: 600; color: [^"]+;">(.*?)</span>',a,re.S)]
        conf=re.findall(r'(?:<button[^>]*>|<a [^>]*>)([^<]{2,60})(?:</button>|</a>)\s*</div></aside>',m.group(0)+'</aside>')
        conf=conf[-1] if conf else ''
        if not conf:
            bb=re.findall(r'>([^<>]{2,60})</(?:button|a)>',a); conf=txt(bb[-1]) if bb else ''
        forms.append(dict(titulo=t,campos=[l for l in labels if l],confirmar=conf))
    drawers=[(w['label'],w.get('done','')) for w in spec if w.get('type')=='drawer']
    chips=[]
    for c in re.findall(r'<span[^>]*border-radius: 999px[^>]*>(?:<span[^>]*></span>)?([^<]{2,60})</span>',main):
        c=txt(c)
        if c and c not in chips: chips.append(c)
    base=n[:5]
    return dict(arquivo=n,familia=base,titulo=title,rota=CAT.get(base,{}).get('rota',''),links=links,acoes=acts,formularios=forms,
                abre_paineis=drawers,selos=chips[:30])
def all_screens():
    fs=sorted(f for f in os.listdir(PROJ) if f.endswith('.dc.html'))
    return {n:screen(n) for n in fs}
if __name__=='__main__':
    D=all_screens(); json.dump(D,open(os.path.join(HERE,'_nav.json'),'w'),ensure_ascii=False,indent=1)
    print(len(D),'telas · links',sum(len(v['links']) for v in D.values()),'· ações',sum(len(v['acoes']) for v in D.values()),'· formulários',sum(len(v['formularios']) for v in D.values()))
    import random
    v=D['CA-01det.dc.html']; print(v['titulo'],v['rota']); print(v['acoes'][:3]); print(v['formularios'][:2]); print(v['links'][:6])
