# -*- coding: utf-8 -*-
"""'Restaurar demonstração' (MB-01) com outro quadro aberto na mesma origem (como no Canvas) — Chrome real, ≤ 15 verificações.
O quadro do MB-03 volta ao início e uma mudança feita nele depois não ressuscita o estado antigo.
Uso: python3 app_restaurar_test.py   (compile antes: areas.mobile.build())"""
import time
from app_lib import App

a = App(['MB-01', 'MB-03'])
F = "document.getElementById('fx').contentWindow.document"
try:
    a.abrir('MB-01'); a.clk('Restaurar demonstração')
    a.J("(()=>{const f=document.createElement('iframe'); f.id='fx'; f.src='MB-03.dc.html'; f.style='position:fixed;left:0;top:0;width:390px;height:900px;opacity:0'; document.body.appendChild(f);})()")
    time.sleep(0.5); time.sleep(0.5)
    a.J(f"[...{F}.querySelectorAll('button')].find(b=>b.title==='Iniciar turno na OS-0421').click()"); time.sleep(0.5)
    hq = a.J(f"{F}.querySelector('header').innerText")
    a.ok('turno aberto' in hq and a.foot() == 'Fechar turno · OS-0421', 'turno iniciado no quadro do MB-03 chega ao MB-01 (' + a.foot() + ')')
    a.clk('Restaurar demonstração'); time.sleep(0.5)
    hq = a.J(f"{F}.querySelector('header').innerText")
    a.ok('sem turno aberto' in hq and a.foot() == 'Iniciar turno · OS-0421', 'Restaurar no MB-01: o quadro do MB-03 também volta ao início')
    a.J(f"[...{F}.querySelectorAll('button')].find(b=>b.innerText.trim()==='Sem sinal').click()"); time.sleep(0.5)
    a.ok(a.cen("!c.app.turno") and a.cen("c.app.online") is False and a.foot() == 'Iniciar turno · OS-0421',
         'mudança feita no outro quadro depois do Restaurar não ressuscita o turno antigo')
    a.ok(not a.erros(), 'sem erros JS ' + str(a.erros()))
    a.J("document.getElementById('fx').remove()"); a.clk('Restaurar demonstração')
finally:
    a.fim()
