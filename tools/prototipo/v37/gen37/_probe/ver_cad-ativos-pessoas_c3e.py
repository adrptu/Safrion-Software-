# Verificador CD-03 (E): chip do filtro do estado; horímetro após nova leitura; plantadeira editada.
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE)
from cada_lib import T
t=T(); J=t.J; t.c.size(1440,1000)
def conta(): return J("(document.body.innerText.match(/(\\d+) de (\\d+)/)||[]).slice(0,1).join('')")
try:
    t.goto('CD-03.dc.html')
    t.clk('1 máquina em manutenção'); print('filtrado:',conta())
    print('toolbar:',J("(()=>{const t=document.querySelectorAll('[role=table]')[0]; let p=t.parentElement.parentElement; return p.innerText.split('\\n').slice(0,8).join(' ¦ ');})()"))
    print('btns c/ "resolver":',J("[...document.querySelectorAll('button,[role=button]')].filter(b=>b.innerText.indexOf('resolver')>=0||(b.getAttribute('aria-label')||'').indexOf('resolver')>=0).map(b=>b.tagName+'|'+b.innerText.trim()+'|'+(b.getAttribute('aria-label')||''))"))
    t.shot('ver_cap_c3_filtro.png')
    J("(()=>{const b=[...document.querySelectorAll('button')].filter(b=>(b.getAttribute('aria-label')||'').indexOf('Em manutenção ou')>=0||b.innerText.indexOf('Em manutenção ou')>=0); if(b.length) b[b.length-1].click();})()"); time.sleep(.3); print('após rm chip:',conta(),'estado ainda filtra?')
    t.clk('Limpar filtros'); print('após limpar:',conta())
    t.openrow(0,'Trator 02'); print('hor inicial:',t.fv('cont_tr')); t.fset('cont_tr','3100'); t.btn('Salvar'); time.sleep(.3); print('salvou 3100 aberto:',t.isopen(),t.toast())
    t.openrow(0,'Trator 02'); print('hor agora:',t.fv('cont_tr')); t.fset('cont_tr','3000'); t.btn('Salvar'); time.sleep(.3); print('3000 depois de 3100 -> aberto:',t.isopen(),'alerts:',t.alerts(),'toast:',t.toast())
    if t.isopen(): t.cancel()
    t.openrow(0,'Plantadeira 24 linhas'); t.fset('linhas_pl','20'); print('larg live:',t.fv('larg_pl')); t.btn('Salvar'); time.sleep(.3)
    print('plant row:',t.rowtxt(0,'Plantadeira 24 linhas')); print('cj T1:',t.anyrow(1,'Trator T1 +'))
    print('erros:',t.errs(),'motor:',t.errs_motor())
finally:
    t.fim()
