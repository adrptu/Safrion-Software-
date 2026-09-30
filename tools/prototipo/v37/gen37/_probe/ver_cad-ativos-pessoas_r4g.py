# Verificador rodada 4 · sonda G: CD-04 habilidades, várias habilitações, vigência, admissão futura, contrato encerrado, filtros e estado
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE); os.chdir(HERE)
from cada_lib import T
T0=time.time()
t=T(); J=t.J
def lg(*a): print(round(time.time()-T0,1),*a, flush=True)
MULTI="""((t)=>{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(x=>x.innerText.trim()===t); if(!l) return false; l.querySelector('input').click(); return true;})"""
def marca(txt): r=J(f"({MULTI})({json.dumps(txt)})"); time.sleep(.2); return r
def st(): return J("(()=>{const b=[...document.querySelectorAll('header button')].find(b=>b.getAttribute('aria-label')); return b?b.innerText.trim()+' | '+getComputedStyle(b).color:null;})()")
def chips(): return J("[...document.querySelectorAll('button[aria-pressed]')].map(b=>b.innerText.replace(/\\s+/g,' ').trim()+(b.getAttribute('aria-pressed')==='true'?'*':''))")
def multis(): return J("[...document.querySelectorAll('aside[role=dialog] input[type=checkbox]')].map(i=>i.parentElement.innerText.trim())")
try:
    t.c.size(1440,1000); t.goto('CD-04.dc.html'); lg('chips',chips())
    t.clk('Cadastrar pessoa'); lg('novo labels:',t.labels()); lg('multi:',multis()); lg('dlg:',t.dlg()[:300].replace('\n',' | '))
    lg('acesso opts',t.fopts('acesso'),'cal opts',t.fopts('cal'),'equipe',t.fv('equipe'),'vinc opts',t.fopts('vinc'))
    t.fset('nome','Tiago'); t.fset('adm','2026-10-05'); t.fset('custo','40')
    for h in ['Operar trator','Irrigar','Aprovar O.S. (agrônomo)','Manutenção de máquinas']: marca(h)
    lg('labels c/ 4 habs:',t.labels())
    t.fset('v31','2027-01-10'); t.fset('v10','2026-10-10'); t.fset('vcrea','2027-06-30'); t.fset('v12','2026-01-01')
    t.btn('Salvar'); time.sleep(.2); lg('salvar:',t.isopen(),t.alerts(),'|',t.toast())
    lg('linha Tiago:',t.rowtxt(0,'Tiago')); lg('st',st()); lg('chips',chips())
    # vigência: até antes da admissão
    t.openrow(0,'Tiago'); t.fset('vinc','Diarista'); t.fset('ate','2026-10-01'); t.btn('Salvar'); time.sleep(.2); lg('ate<adm:',t.alerts())
    t.fset('adm','2026-09-01'); t.fset('ate','2026-09-15'); t.fset('v12','2027-01-01'); t.btn('Salvar'); time.sleep(.2); lg('encerrado:',t.isopen(),t.toast()); lg('linha:',t.rowtxt(0,'Tiago'))
    lg('st',st()); lg('chips',chips())
    t.shot('ver_cad-ativos-pessoas_r4g.png')
    lg('erros:',t.errs())
finally:
    t.fim()
