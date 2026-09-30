# Verificador CD-03 (A): formulário da máquina, classes, custo, armazenagem, fotos do formulário.
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE)
from cada_lib import T
t=T(); J=t.J; t.c.size(1440,1000)
try:
    t.goto('CD-03.dc.html')
    t.openrow(0,'Trator T1'); time.sleep(.3)
    print('T1 titulo:',t.title()); print('T1 dlg:',t.dlg()[:1500].replace('\n',' / '))
    t.shot('ver_cap_c3_t1form.png'); t.cancel()
    t.clk('Cadastrar máquina ou instalação'); print('novo titulo:',t.title())
    t.shot('ver_cap_c3_novo.png')
    for cl in ['Trator','Pulverizador','Plantadeira','Distribuidor','Colhedora','Implemento','Tratamento de sementes','Irrigação','Beneficiamento','Armazenagem']:
        t.fset('classe',cl); L=t.labels(); print(cl,'| exige=',t.fv('exige'),'|',[x for x in L if x not in ('Classe','Nome','Modelo','Condição técnica','Custo por hora','Fonte do custo','Local','Situação')])
    # armazenagem sem custo
    t.fset('classe','Armazenagem'); t.fset('nome','Silo 02'); t.fset('capsc_ar','50000'); t.fset('exige','Não')
    t.btn('Salvar'); print('armaz alerts:',t.alerts(),'aberto:',t.isopen(),'toast:',t.toast()); print('row:',t.rowtxt(0,'Silo 02'))
    # colhedora sem custo -> erro; custo sem fonte
    t.clk('Cadastrar máquina ou instalação'); t.fset('classe','Colhedora'); t.fset('nome','Colhedora 2'); t.fset('plat_co','9'); t.fset('cont_co','10')
    t.btn('Salvar'); print('colh alerts:',t.alerts())
    t.fset('custo_h','500'); t.fset('custo_f',''); t.btn('Salvar'); print('colh fonte vazia:',t.alerts(),'aberto:',t.isopen())
    print('custo_f opts:',t.fopts('custo_f'))
    t.cancel()
    # editar Pulverizador PJ-3030: classe fixa, capacidade
    t.openrow(0,'Pulverizador PJ-3030'); print('PJ classe dis:',t.fdis('classe'),'tanque',t.fv('tanque_pv'),'preq',t.fv('preq_pv'),'barra',t.fv('barra_pv'),'cond',t.fv('cond_t'))
    print('PJ dlg links:',J("[...document.querySelectorAll('aside[role=dialog] a')].map(a=>a.innerText.trim()+'|'+a.getAttribute('href'))"))
    t.cancel()
    print('erros:',t.errs(),'motor:',t.errs_motor())
finally:
    t.fim()
