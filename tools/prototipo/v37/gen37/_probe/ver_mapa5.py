# -*- coding: utf-8 -*-
"""Verificador 5: OS-0418 aprovada e liberada no cenário (selo, ação, contagem de decisões); ordem encerrada; toast some?
(IN-04 e, para comparar, EST.dc.html)."""
import json, time
from ver_mapa_lib import Sess
SV="[...document.querySelectorAll('svg [role=button]')]"
def tap(s,t): s.js(f"{SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')).dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"); time.sleep(.35)
def pan(s): return (s.js("(document.querySelector('aside[aria-label]')||{innerText:''}).innerText") or '').replace('\n',' / ')
def setcen(s,fn):
    s.js("(()=>{const t=localStorage.getItem('talhao-os-cenario-v1'); const c=t?JSON.parse(t):JSON.parse(JSON.stringify(CEN0_COPY)); ("+fn+")(c); c.rev=(c.rev||0)+1; localStorage.setItem('talhao-os-cenario-v1',JSON.stringify(c)); window.dispatchEvent(new StorageEvent('storage',{key:'talhao-os-cenario-v1'}));})()"); time.sleep(.45)
def faz(s,v):
    s.js("""((v)=>{const i=document.querySelector('select[aria-label="Filtrar por fazenda"]'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,v); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""+f"({json.dumps(v)})"); time.sleep(.3)
def toast(s): return s.js("[...document.querySelectorAll('[role=status]')].filter(e=>e.offsetParent!==null&&e.innerText.trim()).map(e=>e.innerText.trim()).join(' | ')")
s=Sess(1440,900)
try:
    s.go('IN-04.dc.html'); s.js("localStorage.removeItem('talhao-os-cenario-v1')"); s.go('IN-04.dc.html')
    # semente do cenário a partir do HTML (CEN0 é local ao script da tela): copia do texto da página
    import re, os
    from ver_mapa_lib import R
    seed=re.search(r'const CEN0 *= *(\{.*?\});\n',open(os.path.join(R,'IN-04.dc.html')).read(),re.S).group(1)
    s.js(f"window.CEN0_COPY={seed};")
    print('A) HEAD inicial:',s.head().split(' | ')[-1])
    setcen(s,"c=>{ const o=c.ordens['OS-0418']; o.aprov=true; o.etapa='Liberadas'; o.selos=o.selos.filter(x=>!/Aguardando|Aprovada/.test(x.t)); }")
    print('B) HEAD após OS-0418 liberada:',s.head().split(' | ')[-1])
    print('   indicadores:',s.js("document.querySelector('[role=group][aria-label^=\"Indicadores\"]').innerText.replace(/\\n/g,' ')"))
    tap(s,'P1'); print('   painel P1 Integrado:',pan(s)[:700]); tap(s,'P1')
    print('   rótulo P1 Integrado:',s.js(f"{SV}.find(x=>x.getAttribute('aria-label').startsWith('P1:')).getAttribute('aria-label')"))
    s.click('Irrigação','nav[role=tablist]'); s.click('Programação de hoje')
    print('   rótulo P1 Irrigação/prog:',s.js(f"{SV}.find(x=>x.getAttribute('aria-label').startsWith('P1:')).getAttribute('aria-label')"))
    tap(s,'P1'); print('   painel P1 Irrigação:',pan(s)[:700]); tap(s,'P1')
    setcen(s,"c=>{ const o=c.ordens['OS-0417']; o.etapa='Encerradas'; c.reqs['REQ-031'].itens[0].custodia=0; }")
    s.click('Ordens de serviço','nav[role=tablist]'); tap(s,'P1'); print('C) painel P1 OS após OS-0417 encerrada:',pan(s)[:700]); tap(s,'P1')
    s.js("localStorage.removeItem('talhao-os-cenario-v1')")
    # toast
    faz(s,'Todas'); t0=time.time(); seen=[]
    for i in range(14):
        seen.append(bool(toast(s))); time.sleep(.5)
    print('D) toast visível a cada 0,5 s (IN-04):',''.join('1' if x else '0' for x in seen), 'erros g2toast:',sum('g2toast' in e for e in s.errs()))
    s.go('EST.dc.html'); faz(s,'Boa Vista'); seen=[]
    for i in range(14):
        seen.append(bool(toast(s))); time.sleep(.5)
    print('E) toast visível a cada 0,5 s (EST, outra frente):',''.join('1' if x else '0' for x in seen),'erros g2toast:',sum('g2toast' in e for e in s.errs()))
finally:
    s.close()
