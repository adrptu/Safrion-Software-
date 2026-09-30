# Verificador rodada 4 · sonda L: confirmar exclusão inline de conjunto novo; rodapé do formulário do T1 (links de origem)
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE); os.chdir(HERE)
from cada_lib import T
T0=time.time()
t=T(); J=t.J
def lg(*a): print(round(time.time()-T0,1),*a, flush=True)
MULTI="""((t)=>{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(x=>x.innerText.trim()===t); if(!l) return false; l.querySelector('input').click(); return true;})"""
def marca(txt): r=J(f"({MULTI})({json.dumps(txt)})"); time.sleep(.2); return r
ROWB="(txt=>[...document.querySelectorAll('[role=table]')[1].querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf(txt)>=0))"
try:
    t.c.size(1440,1000); t.goto('CD-03.dc.html')
    t.clk('Montar conjunto'); t.fset('maq','Trator 02'); t.fset('impl','Distribuidor 3 t'); marca('Adubação a lanço'); t.btn('Salvar'); time.sleep(.2)
    J(f"(()=>{{const r={ROWB}('Trator 02 + Distribuidor 3 t'); [...r.querySelectorAll('button')].find(b=>(b.getAttribute('aria-label')||'').indexOf('Excluir')===0).click();}})()"); time.sleep(.3)
    lg('botões na linha:',J(f"(()=>{{const r={ROWB}('Trator 02 + Distribuidor 3 t'); return [...r.querySelectorAll('button')].map(b=>b.innerText.trim()+'|'+(b.getAttribute('aria-label')||''));}})()"))
    J(f"(()=>{{const r={ROWB}('Trator 02 + Distribuidor 3 t'); const b=[...r.querySelectorAll('button')].find(b=>b.innerText.trim()==='Excluir'); b.click();}})()"); time.sleep(.4)
    lg('existe após confirmar:',t.anyrow(1,'Trator 02 + Distribuidor 3 t'),'| toast:',t.toast(),'| col Trator 02:',t.rowtxt(0,'Trator 02'))
    t.openrow(0,'Trator T1'); J("document.querySelector('aside[role=dialog]').scrollTop=99999"); time.sleep(.3)
    lg('rodapé T1:',J("(()=>{const a=document.querySelector('aside[role=dialog]'); return [...a.querySelectorAll('a')].map(x=>{const r=x.getBoundingClientRect(); return x.innerText.trim()+' @'+Math.round(r.top);});})()"))
    t.shot('ver_cad-ativos-pessoas_r4l_t1fim.png')
    lg('erros:',t.errs())
finally:
    t.fim()
