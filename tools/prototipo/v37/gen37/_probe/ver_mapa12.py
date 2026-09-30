# -*- coding: utf-8 -*-
"""Verificador 12 (rodada 2): IN-04 a 1440×1000 — todas as camadas e filtros: erros de JS, rolagem, vocabulário antigo, capturas."""
import json, time, re
from ver_mapa_lib import Sess
SV="[...document.querySelectorAll('svg [role=button]')]"
def labs(s): return s.js(f"{SV}.map(x=>x.getAttribute('aria-label')+' '+x.getAttribute('fill'))")
def nums(s): return s.js("(document.querySelector('[role=group][aria-label^=\"Indicadores\"]')||{innerText:''}).innerText.replace(/\\n/g,' ')")
def selv(s,lbl,v):
    return s.js("""((l,v)=>{const i=[...document.querySelectorAll('select')].find(x=>(x.getAttribute('aria-label')||'')===l); if(!i) return 'sem select '+l; Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,v); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""+f"({json.dumps(lbl)},{json.dumps(v)})")
BAD=re.compile(r'pol[ií]tica|PA-0\d|exce[cç][aã]o de [aá]gua|os0422',re.I)
s=Sess(1440,1000)
try:
    s.go('IN-04.dc.html'); s.js("localStorage.removeItem('talhao-os-cenario-v1')"); s.go('IN-04.dc.html')
    print('HEAD:',s.head()); print('NUMS:',nums(s))
    print('selects:',s.js("[...document.querySelectorAll('select')].map(x=>(x.getAttribute('aria-label')||'?')+'='+x.value+' ['+[...x.options].map(o=>o.value).join('|')+']')"))
    tabs=s.js("[...document.querySelectorAll('nav[role=tablist] [role=tab], nav[role=tablist] button')].map(b=>b.innerText.trim()).filter(Boolean)")
    print('TABS:',tabs)
    s.shot('ver_r2_in04_integrado.png')
    for t in tabs:
        r=s.click(t,'nav[role=tablist]')
        b=s.body(); m=s.js("({sh:document.documentElement.scrollHeight,sw:document.documentElement.scrollWidth})")
        bad=BAD.findall(b)
        sels=s.js("[...document.querySelectorAll('main select, section select')].map(x=>x.getAttribute('aria-label')).filter(l=>l&&l!=='Filtrar por fazenda'&&l!=='Filtrar por safra')")
        print(f'[{t}] click={r} m={m} bad={bad} sels={sels} nums={nums(s)}')
        # percorre opções dos filtros da camada
        for l in sels or []:
            opts=s.js(f"[...[...document.querySelectorAll('select')].find(x=>x.getAttribute('aria-label')==={json.dumps(l)}).options].map(o=>o.value)")
            for o in opts[1:]+opts[:1]:
                selv(s,l,o); time.sleep(.25)
                bb=s.body(); bd=BAD.findall(bb)
                if bd: print('   BAD',t,l,o,bd)
        print('   errs:',s.errs())
    print('erros finais:',s.errs())
finally:
    s.close()
