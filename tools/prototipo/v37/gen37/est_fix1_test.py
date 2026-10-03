# -*- coding: utf-8 -*-
"""Correções do verificador · Estoque, parte 1 (EST.dc.html no Chrome headless, 1440×1000, cenário limpo, ≤ 15 verificações, < 40 s):
lote vencido não volta ao disponível, grades sem rolagem horizontal (etapas 1, 4 e 5), faixa da etapa 2 com O.S. impedida,
contador com o mesmo papel da trilha e Restaurar demonstração limpando o filtro de local."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from est_lib import Est

# grade visível: [scrollWidth, clientWidth] da área que rola
OVF = "[...document.querySelectorAll('[role=table]')].filter(x=>x.offsetParent).map(x=>[x.parentElement.scrollWidth,x.parentElement.clientWidth])"
# botão/chip inteiro dentro da área visível da grade (linha que contém ts, elemento com texto t)
INTEIRO = """((ts,t)=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>ts.every(x=>r.innerText.indexOf(x)>=0)); if(!r) return 'sem linha';
  const e=[...r.querySelectorAll('button,span')].find(x=>x.innerText.trim()===t); if(!e) return 'sem '+t; const box=r.closest('[role=table]').parentElement.getBoundingClientRect(), b=e.getBoundingClientRect();
  return b.left>=box.left-0.5&&b.right<=box.right+0.5;})"""


def cabe(E): return all(s <= c for s, c in E.J(OVF))


E = Est()
try:
    E.abrir()
    # 1 · recebimento de lote vencido: tudo em quarentena, situação "Vencido" e a grade continua cabendo
    E.clk('Conferir NF 4533')
    E.setv('fx_g_rec_conf', '20000'); E.setv('fx_g_rec_apto', '0'); E.setv('fx_g_rec_quar', '20000'); E.setv('fx_g_rec_val', '08/2026'); E.setv('fx_g_rec_obs', 'Lote vencido'); E.salvar()
    t = E.rowtxt('NF 4533'); print('NF 4533:', t, E.J(OVF))
    E.ok('Vencido' in t and 'Aguarda laudo' not in t and cabe(E), 'NF 4533 vencida: situação "Vencido" (não "Aguarda laudo") e grade sem rolagem', t)
    # 2 · etapa 4: lote vencido sem "Liberar após inspeção"; faixa separa vencido de inspeção
    E.etapa(4); t = E.rowtxt('S58-0926'); k = E.k(); print('S58-0926:', t, '| k4:', k)
    E.ok('Liberar após inspeção' not in t and 'vencido: não volta ao disponível' in t and 'Vencido · 08/2026' in t, 'lote vencido S58-0926: sem "Liberar após inspeção", motivo na coluna Bloqueado', t)
    E.ok('Bloqueado para inspeção: KCl 60% 10.000 kg' in k and 'vencido, fora do disponível: Semente de soja 58 W 20.000 kg' in k, 'faixa da etapa 4 separa inspeção de vencido', k)
    E.ok(cabe(E) and E.J(f"({INTEIRO})(['K26-11'],'Liberar após inspeção')") is True, 'etapa 4 sem rolagem; "Liberar após inspeção" do KCl inteiro na tela', E.J(OVF))
    st = E.cen("[c.lotes['Semente de soja 58 W|S58-0926'].quarentena, c.movs.filter(m=>m.tipo==='inspecao').length]")
    E.ok(st == [20000, 0], 'cenário: 20.000 kg do lote vencido seguem bloqueados, nenhuma liberação', st)
    # 3 · lote vencido que entra por outra tela (cenReceber, Óleo mineral 07/2026) também fica sem liberação
    print('cenReceber:', E.mudar("return cenReceber(c,'Óleo mineral','O26-07V',40,'L','Almox. defensivos','07/2026','NF 9001',false);"))
    E.abrir(); E.etapa(4); t = E.rowtxt('O26-07V'); print('O26-07V:', t)
    E.ok('Liberar após inspeção' not in t and 'Vencido · 07/2026' in t, 'lote vencido recebido por cenReceber: sem "Liberar após inspeção"', t)
    # 4 · etapa 5: grade cabe e "Aprovar ajuste" inteiro, antes e depois de uma nova contagem com diferença
    E.etapa(5)
    E.ok(cabe(E) and E.J(f"({INTEIRO})(['INV-2609'],'Aprovar ajuste')") is True, 'etapa 5 sem rolagem; "Aprovar ajuste" da INV-2609 inteiro', E.J(OVF))
    ops = E.J("[...document.querySelectorAll('#fx_g_cnt_contador option')].map(o=>o.value)") if E.clk('+ Nova contagem') == 'ok' else []
    print('contadores:', ops)
    E.setv('fx_g_cnt_lote', E.J("[...document.querySelector('#fx_g_cnt_lote').options].map(o=>o.value).find(v=>v.startsWith('D26-01'))")); E.setv('fx_g_cnt_cont', '290'); E.salvar()
    E.ok(cabe(E) and E.J(f"({INTEIRO})(['INV-2612'],'Aprovar ajuste')") is True and E.J(f"({INTEIRO})(['INV-2612'],'Recontar')") is True,
         'nova contagem INV-2612 com diferença: grade sem rolagem, Recontar e Aprovar ajuste inteiros', E.J(OVF))
    # 5 · mesma palavra para Rui em toda a tela (contador = almoxarife, como na trilha)
    E.row('INV-2609'); a = E.val('fx_g_cnt_contador'); b = E.J("document.body.innerText"); E.fechar()
    E.ok(ops == ['Paula (almoxarife)', 'Rui (almoxarife)'] and a == 'Rui (almoxarife)' and 'conferente' not in b,
         'contador "Rui (almoxarife)" (mesmo papel da trilha), sem "conferente" na tela', [ops, a])
    # 6 · faixa da etapa 2 separa consulta por fase de bloqueio por O.S. impedida
    E.etapa(2); k = E.k(); print('k2:', k)
    E.ok('2 só consulta (O.S. fora de Liberadas e Em execução) · 1 bloqueado por O.S. impedida' in k, 'faixa da etapa 2: 2 só consulta por fase e 1 bloqueado por O.S. impedida', k)
    # 7 · Restaurar demonstração limpa o filtro de local
    E.etapa(4); E.clk('Câmara fria'); f0 = E.J("[...document.querySelectorAll('[role=row].g2kid')].length")
    E.clk('Restaurar demonstração'); E.clk('Restaurar')
    on = E.J("[...document.querySelectorAll('button[aria-pressed=true]')].map(b=>b.innerText)"); n = E.J("[...document.querySelectorAll('[role=row].g2kid')].length"); print('filtro:', f0, on, n)
    E.ok(f0 == 2 and on == ['Todos os locais'] and n > f0,'Restaurar demonstração volta o filtro para "Todos os locais"', [f0, on, n])
    er = E.erros(); E.ok(not er, 'sem erro de script', er)
finally:
    ok = E.fim()
sys.exit(0 if ok else 1)
