# Inventário de botões candidatos por tela (estado inicial, perfil Ana). Saída: inv_botoes.json
import json,time,os,glob
from lib import *
R='/tmp/claude-0/v69b/tools/prototipo/v37/gen37/_render'
import sys
telas=sorted(os.path.basename(p)[:-8] for p in glob.glob(R+'/*.dc.html'))
k,nparte=int(sys.argv[1]),int(sys.argv[2]); telas=telas[k::nparte]
CAND=r"""(()=>{ const n=s=>(s||'').replace(/\s+/g,' ').trim();
 const vis=e=>{ const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'; };
 const all=[...document.querySelectorAll('button,[role=button],a[href]')].filter(e=>!e.closest('[role=dialog],.menu-lat,nav[aria-label],[role=tablist]'));
 const out=[]; const seen={};
 all.forEach((e,i)=>{ if(!vis(e)) return; let t=n(e.innerText)||n(e.getAttribute('aria-label'))||n(e.title); const href=e.tagName==='A'?e.getAttribute('href'):null;
   if(href&&/\.dc\.html/.test(href)&&!href.startsWith('#')) return;
   if(/⇅$/.test(t)) return;
   const k=t; seen[k]=(seen[k]||0)+1; if(seen[k]>1) return;
   out.push({t, i, verde:getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)', dis:!!e.disabled||e.getAttribute('aria-disabled')==='true', row:!!e.closest('tr,[role=row]')}); });
 return out; })()"""
c=novo(); res={}
try:
    for t in telas:
        try:
            abre(c,t); res[t]=c.js(CAND)
        except Exception as ex: res[t]={'erro':str(ex)}
finally: c.close()
json.dump(res,open(f'inv_botoes_{k}.json','w'),ensure_ascii=False,indent=0)
print(len(telas), sum(len(v) for v in res.values() if isinstance(v,list)))
