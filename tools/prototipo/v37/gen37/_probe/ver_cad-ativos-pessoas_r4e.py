# Verificador rodada 4 · sonda E: CD-03 estado do cabeçalho até ficar verde, filtro vazio, T1 inativo e conjunto
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE); os.chdir(HERE)
from cada_lib import T
T0=time.time()
t=T(); J=t.J
def lg(*a): print(round(time.time()-T0,1),*a, flush=True)
LIN="(n=>[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row].g2ed')].find(r=>(r.querySelector('b')||{}).innerText===n))"
def abre(nome): r=J(f"(()=>{{const r={LIN}({json.dumps(nome)}); if(!r) return false; (r.querySelector('.g2pw')||r).click(); return true;}})()"); time.sleep(.35); return r
def st(): return J("(()=>{const b=[...document.querySelectorAll('header button')].find(b=>b.getAttribute('aria-label')); return b?b.innerText.trim()+' | '+getComputedStyle(b).color+' | '+getComputedStyle(b).backgroundColor:null;})()")
def conta(): return J("(document.body.innerText.match(/(\\d+) de (\\d+)/)||[]).slice(1,3).join('/')")
try:
    t.c.size(1440,1000); t.goto('CD-03.dc.html'); lg('st0',st())
    # T1 form
    abre('Trator T1'); lg('T1 dlg:',t.dlg()[:900].replace('\n',' | ')); lg('T1 links:',J("[...document.querySelectorAll('aside[role=dialog] a')].map(a=>a.innerText.trim()+'|'+a.getAttribute('href'))"))
    lg('T1 cond_t ro:',t.fdis('cond_t'),t.fv('cond_t'),'classe dis:',t.fdis('classe'))
    t.cancel()
    abre('Máquina TSI'); t.fset('calib','2026-09-20'); t.btn('Salvar'); time.sleep(.2); lg('TSI:',t.toast(),'| st',st())
    abre('Bomba do Pivô 2'); t.fset('calib','2026-09-22'); t.btn('Salvar'); time.sleep(.2); lg('B2:',t.toast(),'| st',st())
    lg('cj TSI:',t.rowtxt(1,'Máquina TSI'))
    abre('Trator T1'); t.fset('sit','Inativo'); t.btn('Salvar'); time.sleep(.2); lg('T1 inativo:',t.toast(),'| st',st())
    lg('linha T1:',t.rowtxt(0,'Trator T1')); lg('cj T1:',t.rowtxt(1,'Trator T1 + Plantadeira'))
    # clicar no estado verde
    t.clk(st().split(' | ')[0]); time.sleep(.2); lg('apos clicar verde: conta',conta(),'txt:',J("document.querySelectorAll('[role=table]')[0].parentElement.parentElement.innerText.replace(/\\s+/g,' ').slice(0,400)"))
    t.shot('ver_cad-ativos-pessoas_r4e_verde.png')
    t.clk('Limpar filtros'); lg('limpar:',conta())
    # reativar T1 → volta a manutenção
    abre('Trator T1'); t.fset('sit','Ativo'); t.btn('Salvar'); time.sleep(.2); lg('T1 ativo:',t.toast(),'| st',st())
    lg('erros:',t.errs())
finally:
    t.fim()
