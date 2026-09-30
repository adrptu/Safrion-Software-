# -*- coding: utf-8 -*-
"""Verificador 4 (IN-04 × cenário): outra tela real (EST.dc.html num iframe da mesma origem) muda o cenário pela API exposta
(window.__cen) e o Mapa, aberto, deve refletir sem recarregar: entrega → custódia; turno → Em execução; sem sinal → aguardando
sinal; sinal → realizado; devolução da sobra da OS-0417 → sem custódia, sem ação e (esperado) sem selo 'Sobras a receber'."""
import json, time
from ver_mapa_lib import Sess
SV="[...document.querySelectorAll('svg [role=button]')]"
def tap(s,t): s.js(f"{SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')).dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"); time.sleep(.35)
def pan(s): return (s.js("(document.querySelector('aside[aria-label]')||{innerText:''}).innerText") or '').replace('\n',' / ')
def item(s,oid):
    return s.js(f"""(()=>{{const a=document.querySelector('aside[aria-label]'); if(!a) return null; const it=[...a.querySelectorAll('div')].filter(d=>d.firstElementChild&&d.firstElementChild.innerText&&d.firstElementChild.innerText.startsWith('{oid} ·')&&d.style.borderRadius==='10px')[0]; return it?it.innerText.replace(/\\n/g,' / '):null;}})()""")
def mud(s,fn):
    r=s.js(f"(()=>{{const w=document.getElementById('estf').contentWindow; const C=w.__cen; const r=C.cenMudar(null,c=>({fn})(c,C)); return r;}})()"); time.sleep(.5); return r
s=Sess(1440,900)
try:
    s.go('IN-04.dc.html'); s.js("localStorage.removeItem('talhao-os-cenario-v1')"); s.go('IN-04.dc.html')
    s.js(f"(()=>{{const f=document.createElement('iframe'); f.id='estf'; f.src='EST.dc.html'; f.style.cssText='position:fixed;left:-3000px;top:0;width:1200px;height:800px;'; document.body.appendChild(f);}})()")
    for _ in range(30):
        if s.js("!!(document.getElementById('estf').contentWindow.__cen)"): break
        time.sleep(.3)
    print('iframe EST com __cen:',s.js("!!(document.getElementById('estf').contentWindow.__cen)"))
    print('fns:',s.js("Object.keys(document.getElementById('estf').contentWindow.__cen)"))
    s.click('Ordens de serviço','nav[role=tablist]')
    tap(s,'P2'); print('0) OS-0424 inicial:',item(s,'OS-0424'))
    print('entrega:',mud(s,"(c,w)=>w.cenEntregar(c,'REQ-039','Fungicida A',20,'Marcos')"))
    print('1) após entrega (sem recarregar):',item(s,'OS-0424'))
    print('confirma+turno:',mud(s,"(c,w)=>{ w.cenConfirmarRecebimento(c,'REQ-039'); return w.cenIniciarTurno(c,'OS-0424'); }"))
    print('2) turno aberto:',item(s,'OS-0424'))
    print('sem sinal + fecha turno 10 ha:',mud(s,"(c,w)=>{ w.cenSinal(c,false); return w.cenFecharTurno(c,10,2,null,''); }"))
    print('3) sem sinal:',item(s,'OS-0424'))
    print('sinal:',mud(s,"(c,w)=>w.cenSinal(c,true)"))
    print('4) com sinal:',item(s,'OS-0424'))
    s.shot('ver_in04_cen_p2.png'); tap(s,'P2')
    print('HEAD:',s.head())
    tap(s,'P1'); print('5) OS-0417 inicial:',item(s,'OS-0417'))
    print('devolve 500 kg:',mud(s,"(c,w)=>w.cenDevolver(c,'REQ-031','MAP 11-52',500,true)"))
    print('6) OS-0417 após devolução:',item(s,'OS-0417'))
    s.shot('ver_in04_cen_p1.png')
    print('selos no cenário OS-0417:',s.js("(()=>{const t=localStorage.getItem('talhao-os-cenario-v1'); return t?JSON.stringify(JSON.parse(t).ordens['OS-0417'].selos):'(sem cenário gravado)';})()"))
    tap(s,'P1')
    s.click('Integrado','nav[role=tablist]'); print('7) Integrado rótulos:',s.js(f"{SV}.map(x=>x.getAttribute('aria-label'))"))
    print('NUMS:',s.js("document.querySelector('[role=group][aria-label^=\"Indicadores\"]').innerText.replace(/\\n/g,' ')"))
    print('erros:',[e for e in s.errs() if 'g2toast' not in e])
    s.js("localStorage.removeItem('talhao-os-cenario-v1')")
finally:
    s.close()
