# Verificador rodada 4 · sonda F: CD-03 conjuntos — editar conjunto existente, renomear máquina, potência reduzida depois, excluir conjunto novo
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE); os.chdir(HERE)
from cada_lib import T
T0=time.time()
t=T(); J=t.J
def lg(*a): print(round(time.time()-T0,1),*a, flush=True)
LIN="(n=>[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row].g2ed')].find(r=>(r.querySelector('b')||{}).innerText===n))"
def abre(nome): r=J(f"(()=>{{const r={LIN}({json.dumps(nome)}); if(!r) return false; (r.querySelector('.g2pw')||r).click(); return true;}})()"); time.sleep(.35); return r
def st(): return J("(()=>{const b=[...document.querySelectorAll('header button')].find(b=>b.getAttribute('aria-label')); return b?b.innerText.trim():null;})()")
try:
    t.c.size(1440,1000); t.goto('CD-03.dc.html')
    t.openrow(1,'Trator 02 + Pulverizador PJ-3030'); lg('cj dlg:',t.dlg()[:500].replace('\n',' | ')); lg('ro?',t.fdis('maq'),'maq',t.fv('maq'),'impl',t.fv('impl'),'larg',t.fv('larg_c'),'pot',t.fv('pot_c'))
    t.fset('maq','Trator 04'); lg('pot live:',t.fv('pot_c')); t.btn('Salvar'); time.sleep(.2); lg('alerts:',t.alerts()); t.cancel()
    # potência do Trator 02 reduzida para 90 cv depois do conjunto montado
    abre('Trator 02'); t.fset('pot_tr','90'); t.btn('Salvar'); time.sleep(.2); lg('T02 90cv:',t.toast(),t.alerts())
    lg('cj k1 depois:',t.rowtxt(1,'Trator 02 + Pulverizador PJ-3030'))
    lg('cj T1 substituto:',t.rowtxt(1,'Trator T1 + Plantadeira'))
    # potência mínima da plantadeira aumentada para 200 cv
    abre('Plantadeira 24 linhas'); t.fset('preq_pl','200'); t.btn('Salvar'); time.sleep(.2); lg('plant 200:',t.toast(),t.alerts())
    lg('cj T1 depois:',t.rowtxt(1,'Trator T1 + Plantadeira'))
    # renomear Trator 03
    abre('Trator 03'); t.fset('nome','Trator 03A'); t.btn('Salvar'); time.sleep(.2); lg('ren:',t.toast())
    lg('cj ren:',t.rowtxt(1,'Trator 03A + Distribuidor'),'| col Distribuidor:',t.rowtxt(0,'Distribuidor 3 t'))
    # montar conjunto novo e excluir
    t.clk('Montar conjunto'); t.fset('maq','Trator 03A'); t.fset('impl','Esqueletadeira'); J("(()=>{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(x=>x.innerText.trim()==='Poda'); l.querySelector('input').click();})()"); time.sleep(.2)
    t.btn('Salvar'); time.sleep(.2); lg('novo:',t.toast(),t.alerts())
    r=t.anyrow(1,'Trator 03A + Esqueletadeira'); lg('linha nova:',r)
    lg('del btns:',J("(()=>{const r=[...document.querySelectorAll('[role=table]')[1].querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('Trator 03A + Esqueletadeira')>=0); return r?[...r.querySelectorAll('button')].map(b=>(b.getAttribute('aria-label')||b.innerText).trim()):null;})()"))
    lg('erros:',t.errs())
finally:
    t.fim()
