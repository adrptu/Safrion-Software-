# -*- coding: utf-8 -*-
"""Verificador App 9: 'Restaurar demonstração' com outro quadro aberto (Canvas), links duplicados/auto-link de envios."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_app_lib import V
v = V()
IF = "document.getElementById('fx').contentWindow"
try:
    v.abrir('MB-01'); v.clk('Restaurar demonstração')
    v.J("(()=>{const f=document.createElement('iframe'); f.id='fx'; f.src='MB-03.dc.html'; f.style='position:fixed;left:600px;top:0;width:400px;height:900px'; document.body.appendChild(f);})()")
    time.sleep(2.5)
    # no quadro MB-03: iniciar turno na OS-0421 (grava pelo próprio quadro)
    print('   iframe foot:', v.J(f"{IF}.document.querySelector('main').nextElementSibling.innerText.trim()"))
    v.J(f"{IF}.document.querySelector('main').nextElementSibling.querySelector('button,a').click()"); time.sleep(1.0)
    print('   depois de iniciar no quadro: MB-01 foot', v.foot(), '| quadro hdr:', v.J(f"{IF}.document.querySelector('header').innerText.replace(/\\s+/g,' ')"))
    v.clk('Restaurar demonstração'); time.sleep(1.0)
    fr_hdr = v.J(f"{IF}.document.querySelector('header').innerText.replace(/\\s+/g,' ')"); fr_foot = v.J(f"{IF}.document.querySelector('main').nextElementSibling.innerText.trim()")
    print('   após Restaurar no MB-01: MB-01 foot', v.foot(), '| quadro MB-03:', fr_hdr, '|', fr_foot)
    v.ok('sem turno aberto' in fr_hdr, 'quadro MB-03 aberto volta ao início após Restaurar demonstração no MB-01: ' + fr_hdr)
    # o quadro faz outra mudança (Sem sinal): o cenário restaurado sobrevive?
    v.J(f"[...{IF}.document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Sem sinal').click()"); time.sleep(1.0)
    print('   depois de Sem sinal no quadro: turno no cenário =', v.cen("c.app.turno && c.app.turno.os"), '| MB-01 foot', v.foot())
    v.ok(v.cen("!c.app.turno"), 'mudança no outro quadro não ressuscita o turno apagado pelo Restaurar')
    v.J("document.getElementById('fx').remove()")
    v.abrir('MB-01'); v.clk('Restaurar demonstração')
    # links de envios
    for t in ('MB-03', 'MB-03x-recibo'):
        v.abrir(t)
        print('  ', t, 'links p/ MB-03x-recibo:', v.J("[...document.querySelectorAll('main a[href=\"MB-03x-recibo.dc.html\"]')].map(a=>a.innerText.trim()).join(' | ')"))
finally:
    v.fim()
