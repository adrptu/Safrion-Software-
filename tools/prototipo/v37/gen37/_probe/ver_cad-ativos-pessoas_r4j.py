# Verificador rodada 4 · sonda J: capturas dos formulários (T1, Montar conjunto, Lucas, Beto) em 1440x1000 e cortes no painel
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE); os.chdir(HERE)
from cada_lib import T
T0=time.time()
t=T(); J=t.J
def lg(*a): print(round(time.time()-T0,1),*a, flush=True)
CUT="""[...document.querySelectorAll('aside[role=dialog] *')].filter(e=>{const s=getComputedStyle(e); return (s.overflow==='hidden'||s.textOverflow==='ellipsis'||s.overflowX==='hidden') && e.scrollWidth>e.clientWidth+1 && e.clientWidth>0;}).map(e=>e.tagName+':'+(e.innerText||e.value||'').replace(/\\s+/g,' ').slice(0,60)+' ['+e.scrollWidth+'>'+e.clientWidth+']').slice(0,20)"""
AW="(()=>{const a=document.querySelector('aside[role=dialog]'); return [a.scrollWidth,a.clientWidth,a.getBoundingClientRect().width];})()"
try:
    t.c.size(1440,1000); t.goto('CD-03.dc.html')
    t.openrow(0,'Trator T1'); lg('T1 cut:',J(CUT),J(AW)); t.shot('ver_cad-ativos-pessoas_r4j_t1.png'); t.cancel()
    t.clk('Montar conjunto'); t.fset('maq','Trator 03'); t.fset('impl','Plantadeira 24 linhas'); t.btn('Salvar'); time.sleep(.2); lg('cj cut:',J(CUT),J(AW)); t.shot('ver_cad-ativos-pessoas_r4j_cj.png'); t.cancel()
    t.goto('CD-04.dc.html')
    t.openrow(0,'Lucas'); lg('Lucas cut:',J(CUT),J(AW)); t.shot('ver_cad-ativos-pessoas_r4j_lucas.png'); t.cancel()
    t.openrow(0,'Beto'); lg('Beto acesso:',t.fopts('acesso'),t.fdis('acesso')); t.fset('acesso','Solicitar acesso ao app'); t.btn('Salvar'); time.sleep(.2); lg('Beto:',t.toast(),'|',t.rowtxt(0,'Beto'))
    t.openrow(0,'Beto'); lg('Beto reaberto:',t.fv('acesso'),t.fdis('acesso'),t.fopts('acesso')); t.shot('ver_cad-ativos-pessoas_r4j_beto.png'); t.cancel()
    lg('erros:',t.errs())
finally:
    t.fim()
