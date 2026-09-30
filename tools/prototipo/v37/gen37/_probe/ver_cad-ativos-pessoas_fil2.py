# Verificador: conteúdo do menu de filtro aberto (texto próximo ao cabeçalho).
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE)
from cada_lib import T
t=T(); J=t.J; t.c.size(1440,1000)
FM="""((ti,lab)=>{const tb=document.querySelectorAll('[role=table]')[ti]; const b=[...tb.querySelectorAll('button')].find(b=>(b.getAttribute('aria-label')||'')==='Filtrar '+lab); if(!b) return 'sem botão'; const before=document.body.innerText; b.click(); return 'ok';})"""
try:
    t.goto('CD-03.dc.html'); a=J("document.body.innerText"); J(f"({FM})(0,'Classe e capacidade')"); time.sleep(.4); b=J("document.body.innerText")
    import difflib
    d=[l for l in difflib.ndiff(a.split('\n'),b.split('\n')) if l.startswith('+ ')]; print('CD-03 menu:',d[:20])
    t.goto('CD-04.dc.html'); a=J("document.body.innerText"); J(f"({FM})(0,'Habilitações')"); time.sleep(.4); b=J("document.body.innerText")
    d=[l for l in difflib.ndiff(a.split('\n'),b.split('\n')) if l.startswith('+ ')]; print('CD-04 menu:',d[:20])
finally:
    t.fim()
