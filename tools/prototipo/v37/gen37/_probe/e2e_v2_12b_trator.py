# -*- coding: utf-8 -*-
"""v2 · 12b · Qual trator a OS-0430 usa? Painel da O.S. (Conjunto × Recursos alocados), aba Recursos e app (MB-01 → Abrir ordem da OS-0430)."""
import sys, os, time, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000); OS = 'OS-0430'
b.goto('OS.dc.html'); b.row(OS); p = b.aside()
print('   conjunto:', re.findall(r'CONJUNTO.{0,90}', p)); print('   recursos:', re.findall(r'RECURSOS ALOCADOS.{0,80}', p))
b.clk('×', 'aside[role=dialog]'); b.clk('Recursos'); m = b.main(); i = m.find('OS-0430'); print('   aba Recursos:', [x for x in re.findall(r'.{0,80}OS-0430.{0,60}', m)][:4])
b.size(390, 1500); b.goto('MB-01.dc.html')
r = b.J("(()=>{const as=[...document.querySelectorAll('a')].filter(a=>a.offsetParent!==null&&a.innerText.trim()==='Abrir ordem'); const a=as.find(a=>{let n=a; for(let k=0;k<6&&n;k++){n=n.parentElement; if(n&&n.innerText.indexOf('OS-0430 ·')===0) return true;} return false;}); if(!a) return 'sem'; a.click(); return a.getAttribute('href');})()"); time.sleep(1.5)
for _ in range(20):
    try:
        if b.J("document.readyState") == 'complete': break
    except Exception: pass
    time.sleep(.25)
time.sleep(.6)
m = b.main(); print('   app abrir ordem:', r, b.path(), '|', m[:500]); print('   trator no app:', re.findall(r'.{0,40}Trator.{0,40}', m)[:3])
b.fim()
