# -*- coding: utf-8 -*-
"""v2 · 3m · App pela MB-01: "Iniciar turno" no cartão da OS-0430, Sem sinal na MB-01, fechar 60 ha na MB-03, MB-01 mostra "1 registro aguardando sinal"."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(390, 1500); OS = 'OS-0430'
b.goto('MB-01.dc.html')
tt = b.J("[...document.querySelectorAll('button')].filter(x=>x.offsetParent!==null&&x.innerText.trim().startsWith('Iniciar turno')).map(x=>x.innerText.trim()+' | title='+(x.getAttribute('title')||''))"); print('   botões Iniciar:', tt)
r = b.J(f"(()=>{{const bs=[...document.querySelectorAll('button')].filter(x=>x.offsetParent!==null&&x.innerText.trim()==='Iniciar turno'); const x=bs.find(x=>{{let n=x; for(let k=0;k<6&&n;k++){{n=n.parentElement; if(n&&n.innerText.indexOf('{OS} ·')===0) return true;}} return false;}}) || bs.find(x=>(x.getAttribute('title')||'').indexOf('{OS}')>=0); if(!x) return 'sem botão'; x.click(); return 'ok';}})()"); time.sleep(.5)
t = b.toast(); p = b.path(); st = b.cen(f"[c.app.turno && c.app.turno.os, c.ordens['{OS}'].etapa]"); print('   iniciar no cartão:', r, '|', t, '| tela:', p, '| cenário:', st)
b.ok(st == [OS, 'Em execução'], 'MB-01: "Iniciar turno" no cartão da OS-0430 abre o turno nela', (r, t, st))
if not p.endswith('MB-01.dc.html'): b.goto('MB-01.dc.html')
foot = b.J("[...document.querySelectorAll('a,button')].filter(e=>e.offsetParent!==null&&/font-size: 17px/.test(e.getAttribute('style')||'')).map(e=>e.innerText.trim()+' → '+(e.getAttribute('href')||''))"); print('   rodapé com turno aberto:', foot)
b.ok(any(OS in f for f in foot or []), 'MB-01 com turno aberto: ação principal leva ao turno da OS-0430', foot)
r = b.clk('Sem sinal'); print('   sem sinal MB-01:', r, b.toast(), b.cen("c.app.online"))
b.goto('MB-03.dc.html'); print('   MB-03:', b.main()[:260])
b.setv('#ft_ha', '60'); b.setv('#ft_h', '5'); r = b.clk('Fechar turno'); print('   fechar:', r, b.toast())
b.goto('MB-01.dc.html'); m = b.main(); print('   MB-01:', m[:200])
st = b.cen(f"[c.app.fila.length, c.ordens['{OS}'].realizado, c.app.online]")
b.ok('1 registro aguardando sinal' in m and st == [1, 0, False], 'MB-01 mostra "1 registro aguardando sinal" (fila 1, realizado 0)', (st, m[:200]))
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
