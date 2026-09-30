# -*- coding: utf-8 -*-
"""Passo 2 · EST.dc.html: a REQ da OS-0430 aparece para entrega; entregar os 3 itens a Marcos (pela tela)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000); OS = 'OS-0430'
b.goto('EST.dc.html')
RQ = b.cen(f"c.ordens['{OS}'].req"); print('   requisição da OS-0430 no cenário (mesma origem):', RQ)
b.ok(bool(RQ) and b.cen(f"c.ordens['{OS}'].etapa") == 'Liberadas', 'EST enxerga o cenário da O.S. (OS-0430 Liberadas, requisição criada)', RQ)
etapas = b.J("[...document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')].map(x=>x.innerText.replace(/\\s+/g,' '))"); print('   etapas:', etapas)
b.J("document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')[1].click()"); time.sleep(.4)
g, d, o = b.rowtxt(RQ, 'Glifosato 480'), b.rowtxt(RQ, '2,4-D 806'), b.rowtxt(RQ, 'Óleo mineral')
print('  ', g); print('  ', d); print('  ', o)
b.ok(all('A entregar' in t for t in (g, d, o)) and '320 L' in g and '160 L' in d and '80 L' in o, f'{RQ}: 3 itens a entregar 320/160/80 L', (g, d, o))
for prod, q in (('Glifosato 480', '320'), ('2,4-D 806', '160'), ('Óleo mineral', '80')):
    r = b.row(RQ, prod); a = b.aside()
    qv, quem = b.val('#fx_g_ent_qtd'), b.val('#fx_g_ent_quem')
    print(f'   {prod}: abrir={r} qtd={qv} quem={quem} | {a[:260]}')
    if quem != 'Marcos': print('   ajuste quem:', b.setv('#fx_g_ent_quem', 'Marcos'))
    if qv != q: print('   ajuste qtd:', b.setv('#fx_g_ent_qtd', q))
    s = b.clk('Salvar', 'aside[role=dialog]'); t = b.toast(); print('   salvar:', s, '| toast:', t, '| erro:', b.alerts('aside[role=dialog]'))
    b.ok(qv == q and quem == 'Marcos', f'formulário de entrega de {prod} já vem com {q} L e Marcos', (qv, quem))
st = b.cen(f"c.reqs['{RQ}'].itens.map(i=>i.prod+':'+i.entregue+'/'+i.custodia+'/'+i.quem+'/'+i.confirmado).join(' ')"); print('   cenário:', st)
b.ok(st.count('/Marcos/false') == 3 and ':320/320' in st and ':160/160' in st and ':80/80' in st, 'cenário: 3 itens entregues a Marcos, em custódia, aguardando o app', st)
g = b.rowtxt(RQ, 'Glifosato 480'); print('   linha:', g)
b.ok('Aguardando confirmação no app' in g, 'linha mostra "Aguardando confirmação no app"', g)
b.shot('e2e_02_est_entregue.png')
er = b.erros(); b.ok(not er, 'sem erro de JS no Estoque', er)
b.fim()
