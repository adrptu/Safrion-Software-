# Verificador rodada 4 · sonda B: CD-03 cadastro novo — campos por classe, "Exige calibração" automático, custo obrigatório, Armazenagem, painel rolável
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE); os.chdir(HERE)
from cada_lib import T
t=T(); J=t.J
try:
    t.c.size(1440,1000); t.goto('CD-03.dc.html')
    t.clk('Cadastrar máquina ou instalação')
    print('titulo:',t.title()); print('dlg0:',t.dlg()[:400].replace('\n',' | '))
    print('opts classe:',t.fopts('classe'),'val:',t.fv('classe'),'custo_f:',t.fv('custo_f'),'exige:',t.fv('exige'))
    for cl in ['Trator','Pulverizador','Plantadeira','Distribuidor','Colhedora','Implemento','Tratamento de sementes','Irrigação','Beneficiamento','Armazenagem']:
        t.fset('classe',cl); time.sleep(.1)
        print(cl,'| exige=',t.fv('exige'),'|',t.labels())
    # painel: rolagem e botão Salvar visível
    print('aside:',J("(()=>{const a=document.querySelector('aside[role=dialog]'); const r=a.getBoundingClientRect(); const s=[...a.querySelectorAll('*')].filter(e=>e.scrollHeight>e.clientHeight+2&&['auto','scroll'].includes(getComputedStyle(e).overflowY)).map(e=>e.tagName+':'+e.scrollHeight+'/'+e.clientHeight); const b=[...a.querySelectorAll('button')].find(b=>b.innerText.trim()==='Salvar'); const br=b.getBoundingClientRect(); return {top:r.top,h:r.height,scroll:s,salvar:[br.top,br.bottom,innerHeight]};})()"))
    # Armazenagem sem custo grava
    t.fset('nome','Silo 02'); t.fset('capsc','30000'); t.fset('calib','2026-09-20'); t.fset('interv','90'); t.btn('Salvar'); time.sleep(.3)
    print('armazenagem salvar -> aberto:',t.isopen(),'alerts:',t.alerts(),'toast:',t.toast())
    print('linha Silo 02:',t.rowtxt(0,'Silo 02'))
    t.cancel()
    # Irrigação: horímetro e custo obrigatório
    t.clk('Cadastrar máquina ou instalação'); t.fset('classe','Irrigação'); t.fset('nome','Bomba 3'); t.fset('vazao','200'); t.btn('Salvar'); time.sleep(.3)
    print('irrig sem custo/interv alerts:',t.alerts())
    t.fset('custo_h','50'); print('custo_f apos custo:',t.fv('custo_f')); t.btn('Salvar'); time.sleep(.3); print('alerts2:',t.alerts())
    t.fset('interv','30'); t.fset('cont_ir','10'); t.btn('Salvar'); time.sleep(.3)
    print('aberto:',t.isopen(),'toast:',t.toast(),'row:',t.rowtxt(0,'Bomba 3'),'header:',t.header()[:120])
    t.cancel()
    # classe trocada depois de preencher: valor escondido de outra classe some?
    t.clk('Cadastrar máquina ou instalação'); t.fset('classe','Trator'); t.fset('pot','200'); t.fset('classe','Colhedora'); t.fset('nome','Colhedora 2'); t.fset('plat','9'); t.fset('custo_h','700'); t.fset('cont_co','0'); t.btn('Salvar'); time.sleep(.3)
    print('colhedora: aberto',t.isopen(),t.alerts(),'row:',t.rowtxt(0,'Colhedora 2'))
    # nome duplicado
    t.clk('Cadastrar máquina ou instalação'); t.fset('nome','trator t1'); t.fset('pot','100'); t.fset('custo_h','10'); t.fset('cont_tr','0'); t.btn('Salvar'); time.sleep(.3); print('dup:',t.alerts()); t.cancel()
    print('erros:',t.errs())
finally:
    t.fim()
