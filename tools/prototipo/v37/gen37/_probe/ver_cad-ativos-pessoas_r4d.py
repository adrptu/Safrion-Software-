# Verificador rodada 4 · sonda D: CD-03 cadastros novos (Armazenagem sem custo, Irrigação, troca de classe, duplicado) e estado recalculado
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE); os.chdir(HERE)
from cada_lib import T
T0=time.time()
t=T(); J=t.J
def lg(*a): print(round(time.time()-T0,1),*a, flush=True)
try:
    t.c.size(1440,1000); t.goto('CD-03.dc.html'); lg('carregou')
    t.clk('Cadastrar máquina ou instalação'); t.fset('classe','Armazenagem'); lg('custo_f default:',t.fv('custo_f'))
    for k,v in [('nome','Silo 02'),('capsc_ar','30000'),('calib','2026-09-20'),('interv','90')]: t.fset(k,v)
    t.btn('Salvar'); time.sleep(.2)
    lg('armazenagem: aberto',t.isopen(),'alerts',t.alerts(),'toast',t.toast()); lg(' linha:',t.rowtxt(0,'Silo 02'))
    t.cancel()
    t.clk('Cadastrar máquina ou instalação'); t.fset('classe','Irrigação')
    for k,v in [('nome','Bomba 3'),('vazao_ir','200'),('custo_h','50'),('cont_ir','10'),('interv','30')]: t.fset(k,v)
    t.btn('Salvar'); time.sleep(.2)
    lg('irrig: aberto',t.isopen(),'alerts',t.alerts(),'toast',t.toast()); lg(' linha:',t.rowtxt(0,'Bomba 3')); lg(' header:',t.header()[60:140])
    t.cancel()
    t.clk('Cadastrar máquina ou instalação'); t.fset('classe','Trator'); t.fset('pot_tr','200'); t.fset('classe','Colhedora')
    for k,v in [('nome','Colhedora 2'),('plat_co','9'),('custo_h','700'),('cont_co','0')]: t.fset(k,v)
    t.btn('Salvar'); time.sleep(.2); lg('colhedora: aberto',t.isopen(),t.alerts(),'linha:',t.rowtxt(0,'Colhedora 2'))
    t.cancel()
    t.clk('Cadastrar máquina ou instalação')
    for k,v in [('nome','trator t1'),('pot_tr','100'),('custo_h','10'),('cont_tr','0')]: t.fset(k,v)
    t.btn('Salvar'); time.sleep(.2); lg('dup:',t.alerts()); t.cancel()
    # Montar conjunto com a nova colhedora sem implemento → largura herdada da plataforma
    t.clk('Montar conjunto'); t.fset('maq','Colhedora 2'); lg('larg_c:',t.fv('larg_c'),'pot_c:',t.fv('pot_c'))
    t.fset('impl','Plantadeira 24 linhas'); t.btn('Salvar'); time.sleep(.2); lg('colhedora+plantadeira alerts:',t.alerts())
    t.fset('impl','Sem implemento'); t.btn('Salvar'); time.sleep(.2); lg('sem ops alerts:',t.alerts())
    J("(()=>{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(x=>x.innerText.trim()==='Colheita de grãos'); l.querySelector('input').click();})()"); time.sleep(.2)
    t.btn('Salvar'); time.sleep(.2); lg('salvo? aberto',t.isopen(),t.alerts(),t.toast()); lg(' cj:',t.rowtxt(1,'Colhedora 2'))
    lg(' linha maq:',t.rowtxt(0,'Colhedora 2'))
    # duplicado
    t.clk('Montar conjunto'); t.fset('maq','Trator 02'); t.fset('impl','Pulverizador PJ-3030'); J("(()=>{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(x=>x.innerText.trim()==='Pulverização'); l.querySelector('input').click();})()"); time.sleep(.2)
    t.btn('Salvar'); time.sleep(.2); lg('dup cj:',t.alerts()); t.cancel()
    lg('erros:',t.errs())
finally:
    t.fim()
