# -*- coding: utf-8 -*-
"""EX-40.6 · "Água no solo" (AG-02) × Irrigação: onde se registra, quem lê e se o balanço usa a CAD (executado + leitura do código)."""
import os, sys, json, time, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e40lib import S, G, clique, BTN, BTNC
s = S(); s.reset('Ana')
s.go('AG-02.dc.html', espera=1.5)
ag = s.J("""(()=>{const n=x=>(x||'').replace(/\\s+/g,' ').trim(); const h=[...document.querySelectorAll('*')].find(e=>e.children.length===0&&n(e.textContent)==='Água no solo');
  if(!h) return null; let sec=h; while(sec.parentElement&&!/AGS-00/.test(sec.innerText)) sec=sec.parentElement; return n(sec.innerText).slice(0,1600);})()""")
s.p('# EX-40.6 · AG-02 "Água no solo" (render b87f79b, Ana)'); s.p(ag)
s.go('IR-01.dc.html#P2', espera=2.5)
time.sleep(1.0)
pan = s.J("(()=>{const d=[...document.querySelectorAll('aside[role=dialog],[role=dialog]')].find(e=>e.getClientRects().length); return d?d.innerText.replace(/\\s+/g,' ').slice(0,1800):'';})()")
s.p('\n# IR-01 · painel do setor Pivô 2 (#P2)'); s.p(pan)
s.shot('p4_IR-01_P2.png')
cad = s.J("(()=>{const d=[...document.querySelectorAll('aside[role=dialog],[role=dialog]')].find(e=>e.getClientRects().length); if(!d) return null; const l=[...d.querySelectorAll('label,div,span')].find(e=>e.children.length<3&&/Água disponível no solo/.test(e.innerText)); return l?l.innerText.replace(/\\s+/g,' ').slice(0,300):null;})()")
s.p(f'\ncampo "Água disponível no solo (referência)": {cad!r}')
lnk = s.J("[...document.querySelectorAll('a[href]')].filter(a=>/AG-02/.test(a.getAttribute('href'))).map(a=>a.innerText.trim()+' → '+a.getAttribute('href')).slice(0,5)")
s.p(f'links da Irrigação para AG-02: {lnk}')
s.p(f"erros JS: {s.errs()}")
s.fim()
# leitura do código: o balanço (irrigacao_estado.js) chama soloCAD? quem chama soloCAD?
g = subprocess.run(['grep', '-n', 'soloCAD\\|soloAguaDo', G + '/irrigacao_estado.js', G + '/areas/irrigacao.py', G + '/areas/analise_solo.py', G + '/solo.js'], capture_output=True, text=True).stdout
s.p('\n# leitura do código (grep soloCAD/soloAguaDo)'); s.p(g)
s.save('p4_ag02_irr.log', '\n'.join(s.log) + '\n')
