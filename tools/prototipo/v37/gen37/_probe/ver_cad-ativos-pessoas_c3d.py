# Verificador CD-03 (D): estado vermelho→amarelo→verde, chip do filtro, horímetro após nova leitura, plantadeira editada, calibração futura.
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE)
from cada_lib import T
t=T(); J=t.J; t.c.size(1440,1000)
def st(): return J("(()=>{const b=[...document.querySelectorAll('header button')].find(b=>b.title&&b.title.indexOf('Filtrar')===0); return b?[b.innerText.trim(),getComputedStyle(b).color]:null;})()")
def conta(): return J("(document.body.innerText.match(/(\\d+) de (\\d+)/)||[]).slice(0,1).join('')")
try:
    t.goto('CD-03.dc.html')
    print('estado 0:',st())
    t.clk('1 máquina em manutenção'); print('filtrado:',conta(),'chips:',J("[...document.querySelectorAll('button')].map(b=>b.innerText.trim()).filter(x=>x.indexOf('Em manutenção ou')>=0)"))
    # remover pelo chip
    J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim().indexOf('Em manutenção ou calibração a resolver')>=0); b&&b.click();})()"); time.sleep(.3); print('após chip rm:',conta())
    # horímetro: sobe e depois desce
    t.openrow(0,'Trator 02'); print('hor inicial:',t.fv('cont_tr')); t.fset('cont_tr','3100'); t.btn('Salvar'); time.sleep(.3); print('salvou 3100 aberto:',t.isopen())
    t.openrow(0,'Trator 02'); print('hor agora:',t.fv('cont_tr')); t.fset('cont_tr','3000'); t.btn('Salvar'); time.sleep(.3); print('3000 depois de 3100 -> aberto:',t.isopen(),'alerts:',t.alerts(),'toast:',t.toast())
    t.cancel()
    # plantadeira editada
    t.openrow(0,'Plantadeira 24 linhas'); t.fset('linhas_pl','20'); print('larg live:',t.fv('larg_pl')); t.btn('Salvar'); time.sleep(.3)
    print('plant row:',t.rowtxt(0,'Plantadeira 24 linhas')); print('cj T1:',t.anyrow(1,'Trator T1 +'))
    # calibração futura
    t.openrow(0,'Máquina TSI'); t.fset('calib','2026-10-10'); t.btn('Salvar'); print('calib futura:',t.alerts()); 
    t.fset('calib','2026-09-20'); t.btn('Salvar'); time.sleep(.3); print('TSI row:',t.rowtxt(0,'Máquina TSI')); print('estado:',st())
    t.openrow(0,'Bomba do Pivô 2'); print('B2 interv:',t.fv('interv')); t.fset('calib','2026-09-21'); t.fset('interv','180'); t.btn('Salvar'); time.sleep(.3); print('B2 alerts',t.alerts(),'row:',t.rowtxt(0,'Bomba do Pivô 2')); print('estado:',st())
    t.openrow(0,'Trator T1'); t.fset('sit','Inativo'); t.btn('Salvar'); time.sleep(.3); print('T1 inativo row:',t.rowtxt(0,'Trator T1')); print('estado:',st())
    print('cj TSI:',t.anyrow(1,'Máquina TSI'))
    print('erros:',t.errs(),'motor:',t.errs_motor())
finally:
    t.fim()
