import sys,os,time,json; sys.path.insert(0,'.')
from cadc_lib import T
t=T(); J=t.J
def btn(txt, root=''):
    r=J(f"(()=>{{const b=[...document.querySelectorAll({json.dumps((root+' button').strip())})].find(b=>b.innerText.trim()==={json.dumps(txt)}); if(!b) return false; b.click(); return true;}})()"); time.sleep(.4); return r
def setv(sel,val):
    return J(f"""(()=>{{const i=document.querySelector({json.dumps(sel)}); if(!i) return false; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(P,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}})); return true;}})()""")
try:
  for v in ['62','62,7','62,79','30,5','30,55']:
    t.goto('Main.dc.html'); J("localStorage.clear()"); t.goto('OS.dc.html#OS-0504'); time.sleep(.8)
    btn('Iniciar execução','aside[role=dialog]'); btn('Confirmar início','aside[role=dialog]'); btn('Registrar apontamento','aside[role=dialog]'); time.sleep(.3)
    setv('aside[role=dialog] input[type=date]','2026-09-24'); setv('aside[role=dialog] input[aria-label="Área feita em hectares"]',v); time.sleep(.2)
    val=J("(document.querySelector('aside[role=dialog] input[aria-label=\"Área feita em hectares\"]')||{}).value")
    btn('Salvar apontamento','aside[role=dialog]'); time.sleep(.5)
    ap=J("(()=>{const c=JSON.parse(localStorage.getItem('talhao-os-cenario-v1')||'{}'); return JSON.stringify(((c.ordens||{})['OS-0504']||{}).ap)})()")
    al=J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')")
    print(v,'| campo:',val,'| ap:',ap[:90],'| alerta:',al[:160],'| toast:',t.toast()[:120])
finally:
    t.c.close(); t.srv.terminate()
