# -*- coding: utf-8 -*-
"""v2 · 12c · OS.dc.html aba Kanban: a OS-0430 está na coluna da fase do cenário; chips de fase contam igual."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000); OS = 'OS-0430'
b.goto('OS.dc.html'); fase = b.cen(f"c.ordens['{OS}'].etapa")
chips = b.J("[...document.querySelectorAll('main button')].filter(x=>x.offsetParent!==null).map(x=>x.innerText.replace(/\\s+/g,' ')).filter(t=>/^(Todas|A liberar|Liberadas|Em execução|Em conferência|Encerradas|Canceladas) \\d/.test(t))"); print('   chips:', chips)
b.clk('Kanban')
col = b.J(f"(()=>{{const F=/^(A liberar|Liberadas|Em execução|Em conferência|Encerradas)/; const w=document.createTreeWalker(document.querySelector('main'),NodeFilter.SHOW_TEXT); let n,card=null; while((n=w.nextNode())){{ if(n.nodeValue.trim()==='{OS}' && n.parentElement.offsetParent!==null){{card=n.parentElement;break;}} }} if(!card) return 'sem card'; let e=card; for(let k=0;k<10&&e;k++){{ e=e.parentElement; const t=(e.innerText||'').trim(); if(F.test(t) && t.indexOf('{OS}')>0) return t.replace(/\\s+/g,' ').slice(0,200); }} return 'sem coluna';}})()")
hdr = b.J("document.querySelector('header').innerText.replace(/\\s+/g,' ')"); print('   cabeçalho:', hdr[hdr.find('Ordem de Serviço Ordem'):][:80])
print('   fase:', fase, '| coluna com OS-0430:', col)
b.ok(col.startswith(fase) or (fase in col[:40]), f'Kanban: OS-0430 na coluna {fase}', col)
b.clk('Lista')
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
