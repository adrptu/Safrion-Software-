# -*- coding: utf-8 -*-
"""INTEL-01 · navegador: Inteligência de vendas (IV) e de compras (IC), pedido do proprietário de 13/10/2026.
Confere, em 1440 × 900 e 390 × 844: menu (Comercial › Inteligência de vendas; Suprimentos › Inteligência de compras) com o destaque
na tela aberta; indicadores; estados honestos (soja "Suspenso" pela saca a conferir, mamão "Sem previsão"; nada vira 0%); o painel
de cada linha diz a conta e o próximo passo; sem erro de JS e sem rolagem lateral no celular. Dados sintéticos. Uso: python3 inteligencia_nav_test.py"""
import sys, json
from ma_lib import MA

PAN = "(()=>{const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getClientRects().length); return a?a.innerText.replace(/\\s+/g,' '):'';})()"
MENU = "JSON.stringify([...document.querySelectorAll('nav a')].map(a=>[a.innerText.trim(),a.getAttribute('href')]).filter(x=>/^(IV|IC|PCOM|VEN|CMP)\\.dc\\.html/.test(x[1]||'')))"
KPI = "(document.querySelector('[aria-label=Indicadores]')||{innerText:''}).innerText.replace(/\\s+/g,' ').toLowerCase()"
m = MA(1440, 900); J = m.J
try:
    # ---------------- Vendas ----------------
    m.ir('', pagina='IV.dc.html', limpa=True); m.sem_erro('IV 1440')
    mn = json.loads(J(MENU) or '[]')
    m.ok(['Inteligência de vendas', 'IV.dc.html'] in mn and ['Painel comercial', 'PCOM.dc.html'] in mn, 'IV no menu Comercial, ao lado do Painel comercial', mn)
    k = J(KPI) or ''
    m.ok('vendas abaixo da referência 0' in k and 'venda sem oferta que cubra 1' in k and 'mamão: vendido sem previsão' in k and 'melhor recebimento líquido r$ 2,88/kg' in k, 'IV: os 3 indicadores (0 abaixo, 1 sem oferta: mamão, melhor líquido R$ 2,88/kg)', k)
    s = m.linha('s:Soja em grão'); mm = m.linha('s:Mamão Formosa · fruta de campo')
    m.ok('Suspenso' in s and '0%' not in s and 'saca a conferir' in s, 'IV safra comercializada: soja "Suspenso" (saca a conferir), nunca 0%', s)
    m.ok('Sem previsão' in mm and 'déficit' in mm.lower(), 'IV safra comercializada: mamão "Sem previsão" com o déficit à vista', mm)
    m.ok('Saca a conferir' in m.linha('p:Soja em grão'), 'IV preço × mercado: soja "Saca a conferir" (fora da média, não zero)', m.linha('p:Soja em grão'))
    m.abre('s:Soja em grão'); p = J(PAN) or ''
    lk = J("[...[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getClientRects().length).querySelectorAll('a[href^=\"VEN.dc.html#\"]')].map(a=>a.getAttribute('href').split('#')[1]).sort().join(',')") or ''
    m.ok('Conta suspensa' in p and 'vendas com saca a conferir' in p.lower() and lk == 'BT-090,CRE-0095,CT-203,PV-030', 'IV painel da soja: motivo e um "Abrir venda" para cada uma das 4 vendas de saca a conferir', [p[:300], lk])
    m.clk('Fechar painel', w=.4); m.abre('s:Mamão Formosa · fruta de campo'); p = J(PAN) or ''
    m.ok('Sem oferta publicada' in p and 'Publique a previsão' in p, 'IV painel do mamão: vendido sem previsão e o próximo passo', p[:400])
    m.clk('Fechar painel', w=.4)
    cl = m.linhas(2)
    if cl: m.abre(cl[0]); p = J(PAN) or ''
    m.ok(bool(cl) and 'Líquido = preço' in p and 'custo do prazo' in p, 'IV recebimento líquido: o painel mostra a conta (preço − frete − custo do prazo)', p[:400])
    # ---------------- Compras ----------------
    m.ir('', pagina='IC.dc.html'); m.sem_erro('IC 1440')
    mn = json.loads(J(MENU) or '[]')
    m.ok(['Inteligência de compras', 'IC.dc.html'] in mn, 'IC no menu Suprimentos', mn)
    b = J(KPI) or ''
    m.ok('r$ 41.363' in b and '1.277,84' in b, 'IC: economia pela melhor cotação R$ 41.363 e R$ 1.277,84/ha (oráculo do inteligencia_unit C3/C4)', b[:500])
    it = m.linhas(0)
    m.abre(it[0]) if it else None; p = J(PAN) or ''
    m.ok(bool(it) and 'Melhor cotação' in p and 'válida até' in p and 'Abrir Compra de insumos' in p, 'IC painel do insumo: melhor cotação, validade de cada uma e o próximo passo', p[:500])
    m.clk('Fechar painel', w=.4)
    # ---------------- celular ----------------
    for pg in ('IV.dc.html', 'IC.dc.html'):
        m.c.size(390, 844); m.ir('', pagina=pg); m.sem_erro(pg + ' 390')
        m.ok(m.largura() <= 0, pg + ' 390: sem rolagem lateral da página', m.largura())
finally:
    sys.exit(m.fim())
