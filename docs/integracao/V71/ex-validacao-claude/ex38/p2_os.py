# Painel da O.S. (OS.dc.html) de todas as ordens das duas fazendas: texto integral do painel, perfil Ana
from base import *
SETV = """((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'NAO ACHEI'; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
PAN = """(()=>{const bs=[...document.querySelectorAll('aside[role=dialog] section[aria-label] > button[aria-expanded="false"]')]; bs.forEach(b=>b.click()); return bs.length;})()"""
s = S()
res = {}
try:
    s.reset('Ana'); s.go('OS.dc.html', 1.5)
    for faz in ['Santa Rita', 'Lagoa Grande']:
        print(faz, s.J(f"({SETV})('select[aria-label=\"Filtrar por fazenda\"]',{json.dumps(faz)})")); time.sleep(.6)
        ids = s.J("[...document.querySelectorAll('[role=row].g2ed')].map(r=>(r.innerText.match(/\\bO[SB]-\\d+/)||[''])[0])")
        print(ids)
        for i in ids:
            s.J(f"(()=>{{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>((r.innerText.match(/\\bO[SB]-\\d+/)||[''])[0])==={json.dumps(i)}); r&&r.click();}})()"); time.sleep(.5)
            for _ in range(3):
                if s.J(PAN): time.sleep(.3)
            t = s.J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?a.innerText:'';})()") or ''
            res[i] = t
            if i in ('OS-0421', 'OS-0420', 'OS-0431', 'OS-0424', 'OS-0417', 'OS-0504'):
                s.c.aparelho(1440, 2600); time.sleep(.3); s.shot(f'os_painel_{i}.png'); s.c.aparelho(1440, 1000)
            s.J("(()=>{const b=document.querySelector('aside[role=dialog] button[aria-label=Fechar]'); b&&b.click();})()"); time.sleep(.3)
    json.dump(res, open(os.path.join(OUT, 'os_paineis.json'), 'w'), ensure_ascii=False, indent=1)
    print('ERRS', s.J("window.__errs"))
finally:
    s.fim()
print(len(res), 'paineis')
