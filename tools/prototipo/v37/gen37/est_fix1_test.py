# -*- coding: utf-8 -*-
"""Correções do verificador · Estoque, parte 1 (EST.dc.html no Chrome headless, 1440×1000, cenário limpo), na forma do SUP:
lote vencido não volta ao disponível (nem por laudo aprovado), página sem rolagem horizontal nas 4 seções, contador com o mesmo papel da
trilha, a fila separa O.S. impedida de O.S. fora de fase igual às linhas, e Restaurar demonstração limpa o filtro de local.
Fica o propósito da versão anterior (docs/suprimentos-simplificado §9.3); textos da faixa viraram contadores e situações."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from est_lib import Est


def cabe(E): return bool(E.J("document.documentElement.scrollWidth<=innerWidth+1"))


E = Est()
try:
    E.abrir(); E.perfil('Rui')
    # 1 · recebimento de lote vencido: tudo em quarentena; a parcela fica "Vencida · aguarda laudo" e a página não rola de lado
    E.ir('#sec=recebimentos'); E.row('NF 4533')
    for k, v in (('conf', '20000'), ('quar', '20000'), ('val', '08/2026'), ('obs', 'Lote vencido')): E.setv('fx_g_rec_' + k, v)
    E.clk_prim(); t = E.rowtxt('NF 4533', 'S58-0926')
    E.ok('Vencida · aguarda laudo' in t and cabe(E), 'NF 4533 vencida: parcela "Vencida · aguarda laudo" e página sem rolagem', t)
    # 2 · lote vencido: "Vencido" no saldo; o laudo só aceita Reprovado e a função recusa liberar
    E.ir('#sec=saldos'); E.ok('Vencido' in E.cel('S58-0926', 'Item') and E.cel('S58-0926', 'Validade') == '08/2026' and E.cel('S58-0926', 'Disponível') == '0 kg', 'saldo: S58-0926 "Vencido", validade 08/2026, disponível 0 kg', [E.cel('S58-0926', k) for k in ('Item', 'Validade', 'Disponível')])
    E.perfil('Ana'); E.ir('#nf=NF 4533'); ops = E.J("[...document.querySelectorAll('#fx_g_rec_res option')].map(o=>o.value)")
    r = E.mudar("return cenLaudo(c,'Semente de soja 58 W|S58-0926','NF 4533','LAB-1','Aprovado','Ana');")
    st = E.cen("[c.lotes['Semente de soja 58 W|S58-0926'].quarentena, c.movs.filter(m=>m.tipo==='inspecao').length]")
    E.ok(ops == ['Reprovado'] and 'vencido' in r and st == [20000, 0], 'lote vencido: o laudo só oferece Reprovado; aprovar pela função é recusado; 20.000 kg seguem bloqueados', [ops, r, st])
    # 3 · lote vencido que entra por outra tela (cenReceber, Óleo mineral 07/2026) também não volta ao disponível
    print('cenReceber:', E.mudar("return cenReceber(c,'Óleo mineral','O26-07V',40,'L','Almox. defensivos','07/2026','NF 9001',false,'Rui');"))
    E.ir('#sec=saldos'); E.ok('Vencido' in E.cel('O26-07V', 'Item') and E.cel('O26-07V', 'Validade') == '07/2026', 'lote vencido recebido por cenReceber: "Vencido", validade 07/2026', [E.cel('O26-07V', 'Item'), E.cel('O26-07V', 'Validade')])
    # 4 · as 4 seções e os 3 modos de Confira saldos cabem na página (a grade rola dentro da própria caixa)
    res = []
    for s in ('Atenda requisições', 'Receba e inspecione', 'Faça contagens', 'Confira saldos'):
        E.ir_secao(s); res.append((s, cabe(E)))
    for m in ('Movimentos', 'Produção', 'Lotes'):
        E.clk(m); res.append((m, cabe(E)))
    E.ok(all(x for _, x in res), '4 seções e 3 modos sem rolagem horizontal da página', res)
    # 5 · mesma palavra para Rui em toda a tela (contador = almoxarife, como na trilha)
    E.perfil('Rui'); E.ir('#sec=contagens'); E.row('INV-2609'); a = E.aside(); b = E.J("document.body.innerText")
    E.ok('Contado 89.400 kg por Rui (almoxarife)' in a and 'conferente' not in b, 'contador "Rui (almoxarife)" (mesmo papel da trilha), sem "conferente" na tela', a[:200])
    # 6 · a fila separa O.S. impedida (bloqueio) de O.S. fora de fase (consulta), igual às linhas
    E.ir_secao('Atenda requisições')
    sits = E.J("""(()=>{const t=[...document.querySelectorAll('[role=table]')].find(x=>x.offsetParent); const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/[⇅▾▴▼▲]/g,'').replace(/\\s+/g,' ').trim().toUpperCase());
      const io=hs.indexOf('O.S.'), is=hs.indexOf('SITUAÇÃO'); return [...t.querySelectorAll('[role=row]')].filter(r=>r.offsetParent&&r.querySelector('[role=cell]')&&!r.classList.contains('g2kid')).map(r=>{const c=r.querySelectorAll('[role=cell]'); return [c[io].innerText.trim(), c[is].innerText.replace(/\\s+/g,' ').trim()];}); })()""")
    imp = [o for o, s_ in sits if s_.startswith('O.S. impedida')]; lib = [o for o, s_ in sits if s_.startswith('Aguarda liberação')]
    E.ok(imp == ['OS-0420'] and len(lib) >= 1, 'OS-0420 "O.S. impedida"; O.S. a liberar "Aguarda liberação" (consulta)', sits)
    E.row('REQ-031'); a = E.aside()
    E.ok('solicitado 5.000 kg' in a and 'consumido 3.500 kg' in a and 'em custódia 500 kg' in a, 'REQ-031 (em conferência): o painel mostra a conta (solicitado, consumido, custódia)', a[:300])
    # 7 · Restaurar demonstração limpa o filtro de local
    E.ir('#sec=saldos'); E.clk('Câmara fria'); f0 = E.J("[...document.querySelectorAll('main [role=row]')].filter(r=>r.offsetParent&&r.querySelector('[role=cell]')).length")
    E.clk('Restaurar demonstração'); E.clk('Restaurar'); E.ir_secao('Confira saldos')
    n = E.J("[...document.querySelectorAll('main [role=row]')].filter(r=>r.offsetParent&&r.querySelector('[role=cell]')).length")
    on = E.J("[...document.querySelectorAll('[role=group][aria-label=\"Filtrar por local\"] button')].filter(b=>b.getAttribute('aria-pressed')==='true').map(b=>b.innerText.trim())")
    E.ok(f0 == 2 and n > f0 and on in ([], ['Todos os locais']), 'Restaurar demonstração volta o filtro para "Todos os locais" (Câmara fria tinha S58-0801 e o S58-0926 recebido no passo 1)', [f0, n, on])
    er = E.erros(); E.ok(not er, 'sem erro de script', er)
finally:
    ok = E.fim()
sys.exit(0 if ok else 1)
