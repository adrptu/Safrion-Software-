# Verificador CD-03 (C): conjunto substituto Trator 02 + Plantadeira -> coluna Conjuntos da plantadeira; foto.
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE)
from cada_lib import T
t=T(); J=t.J; t.c.size(1440,1000)
MULTI="""((t)=>{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(x=>x.innerText.trim()===t); if(!l) return false; l.querySelector('input').click(); return true;})"""
def marca(txt): r=J(f"({MULTI})({json.dumps(txt)})"); time.sleep(.2); return r
try:
    t.goto('CD-03.dc.html')
    t.clk('Montar conjunto'); t.fset('maq','Trator 02'); t.fset('impl','Plantadeira 24 linhas'); marca('Plantio'); t.btn('Salvar'); time.sleep(.3)
    print('toast:',t.toast())
    print('Plantadeira row:',t.rowtxt(0,'Plantadeira 24 linhas'))
    print('links:',J(f"""(()=>{{const r={t.ROW(0,'Plantadeira 24 linhas')}; return [...r.querySelectorAll('button')].map(b=>b.innerText.trim());}})()"""))
    J(f"""(()=>{{const r={t.ROW(0,'Plantadeira 24 linhas')}; r.scrollIntoView({{block:'center'}});}})()"""); time.sleep(.3)
    t.shot('ver_cap_c3_plantio2.png')
    # clicar no 2º "Plantio" abre qual conjunto?
    J(f"""(()=>{{const r={t.ROW(0,'Plantadeira 24 linhas')}; const b=[...r.querySelectorAll('button')].filter(b=>b.innerText.trim()==='Plantio'); b[1]&&b[1].click();}})()"""); time.sleep(.4)
    print('2º Plantio abre:',t.title())
finally:
    t.fim()
