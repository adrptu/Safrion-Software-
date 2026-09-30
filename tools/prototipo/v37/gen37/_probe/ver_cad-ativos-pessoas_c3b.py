# Verificador CD-03 (B): conjuntos (montar, erros, duplicado, excluir, link da coluna Conjuntos, renomear, inativar).
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE)
from cada_lib import T
t=T(); J=t.J; t.c.size(1440,1000)
MULTI="""((t)=>{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(x=>x.innerText.trim()===t); if(!l) return false; l.querySelector('input').click(); return true;})"""
def marca(txt): r=J(f"({MULTI})({json.dumps(txt)})"); time.sleep(.2); return r
try:
    t.goto('CD-03.dc.html')
    t.clk('Montar conjunto'); print('titulo:',t.title()); print('maq opts:',t.fopts('maq')); print('impl opts:',t.fopts('impl'))
    t.shot('ver_cap_c3_cj_novo.png')
    t.btn('Salvar'); print('vazio:',t.alerts())
    t.fset('maq','Colhedora Axial-Flow 7250'); t.fset('impl','Plantadeira 24 linhas'); marca('Plantio'); print('pot live:',t.fv('pot_c'),'larg:',t.fv('larg_c')); t.btn('Salvar'); print('colh+plant:',t.alerts())
    t.fset('maq','Trator 02'); t.fset('impl','Pulverizador PJ-3030'); marca('Plantio'); marca('Pulverização'); t.btn('Salvar'); print('dup:',t.alerts())
    t.fset('maq','Trator 04'); t.fset('impl','Distribuidor 3 t'); marca('Pulverização'); marca('Adubação a lanço'); print('pot live T4+dist:',t.fv('pot_c'),'larg:',t.fv('larg_c'))
    t.btn('Salvar'); print('T4+dist salvo? aberto:',t.isopen(),'toast:',t.toast()); print('row:',t.rowtxt(1,'Trator 04 + Distribuidor 3 t'))
    print('T4 maq row:',t.rowtxt(0,'Trator 04')); print('Dist row:',t.rowtxt(0,'Distribuidor 3 t'))
    # excluir o conjunto novo
    delb=J(f"""(()=>{{const r={t.ROW(1,'Trator 04 + Distribuidor 3 t')}; if(!r) return 'sem linha'; const b=[...r.querySelectorAll('button')].map(b=>(b.getAttribute('aria-label')||'')+'|'+b.innerText.trim()); return b;}})()"""); print('botoes linha nova:',delb)
    J(f"""(()=>{{const r={t.ROW(1,'Trator 04 + Distribuidor 3 t')}; const b=[...r.querySelectorAll('button')].find(b=>(b.getAttribute('aria-label')||'').startsWith('Excluir')); b&&b.click();}})()"""); time.sleep(.3)
    print('confirm:',J("[...document.querySelectorAll('[role=table]')[1].querySelectorAll('button')].map(b=>b.innerText.trim()).filter(Boolean).join(',')"))
    J("(()=>{const b=[...document.querySelectorAll('[role=table]')[1].querySelectorAll('button')].find(b=>/^(Excluir|Sim|Confirmar)/.test(b.innerText.trim())); b&&b.click();})()"); time.sleep(.4)
    print('apos excluir row:',t.rowtxt(1,'Trator 04 + Distribuidor 3 t'),'T4:',t.rowtxt(0,'Trator 04'),'toast:',t.toast())
    # link 'Plantio' na coluna Conjuntos do T1
    J(f"""(()=>{{const r={t.ROW(0,'Trator T1')}; const b=[...r.querySelectorAll('button')].find(b=>b.innerText.trim()==='Plantio'); b&&b.click();}})()"""); time.sleep(.4)
    print('clique Plantio abre:',t.title(), '| dialogs:',J("document.querySelectorAll('aside[role=dialog]').length"))
    t.shot('ver_cap_c3_cj_t1.png')
    print('cj T1 dlg:',t.dlg()[:900].replace('\n',' / ')); t.cancel()
    # renomear Trator 02
    t.openrow(0,'Trator 02'); t.fset('nome','Trator 02A'); t.btn('Salvar'); time.sleep(.3)
    print('rename toast:',t.toast()); print('cj pulv:',t.anyrow(1,'Pulverizador PJ-3030')); print('cj T1:',t.anyrow(1,'Trator T1 +'))
    print('maq 02A row:',t.rowtxt(0,'Trator 02A'))
    # inativar Trator 02A
    t.openrow(0,'Trator 02A'); t.fset('sit','Inativo'); t.btn('Salvar'); time.sleep(.3)
    print('inativo toast:',t.toast()); print('cj pulv:',t.anyrow(1,'Pulverizador PJ-3030')); print('cj T1:',t.anyrow(1,'Trator T1 +')); print('header:',t.header()[:160])
    print('erros:',t.errs(),'motor:',t.errs_motor())
finally:
    t.fim()
