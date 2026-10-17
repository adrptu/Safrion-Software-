# -*- coding: utf-8 -*-
"""INTEL-01 e INTEL-02 · navegador: Inteligência de vendas (IV) e de compras (IC), pedidos do proprietário de 13/10/2026 (INTEL-02: "mais
relativo aos preços, tendências, melhor mês para compra e venda": a seção de preço e melhor mês fica no topo de cada tela).
Confere, em 1440 × 900 e 390 × 844: navegação sem submenus (13/10/2026): o cartão "Inteligência" na tela de entrada do Comercial (logo
depois do Painel) e do Suprimentos, com o ícone do módulo marcado na tela aberta e "‹ Módulo" de volta; indicadores; estados honestos
(soja "Suspenso" pela saca a conferir, mamão "Sem previsão"; nada vira 0%); o painel de cada linha diz a conta e o próximo passo; sem erro
de JS e sem rolagem lateral no celular. Dados sintéticos. Uso: python3 inteligencia_nav_test.py"""
import sys, json, time
from ma_lib import MA

PAN = "(()=>{const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getClientRects().length); return a?a.innerText.replace(/\\s+/g,' '):'';})()"
# navegação sem submenus (13/10/2026, ui37.MENU2/HUB37/CURTO37/VOLTA37): o ícone do módulo marcado (aria-current) e "‹ Módulo" na tela;
# os cartões da tela de entrada (href, nome curto) na ordem do menu
NAV = "JSON.stringify((()=>{const n=document.querySelector('nav[aria-label=Menu]'); const v=document.querySelector('a.volta37'); return {cur:n?[...n.querySelectorAll('a[aria-current=page]')].map(a=>a.getAttribute('aria-label')):null, volta:v?[v.getAttribute('href'),v.innerText.replace(/\\s+/g,' ').trim()]:null};})())"
CARDS = "JSON.stringify([...document.querySelectorAll('a.mod-cartao')].filter(a=>a.getClientRects().length).map(a=>[a.getAttribute('href'),a.innerText.replace(/\\s+/g,' ').trim()]))"
KPI = "[...document.querySelectorAll('[aria-label=Indicadores]')].map(x=>x.innerText).join(' ').replace(/\\s+/g,' ').toLowerCase()"
KPI1 = "(document.querySelector('[aria-label=Indicadores]')||{innerText:''}).innerText.replace(/\\s+/g,' ').toLowerCase()"
# TAB-07 (DS-MODULOS-2, 17/10/2026): grupos de indicadores acima da 1ª lista (devem ser 0), os filtros rápidos da 1ª lista e o selo do cabeçalho
ACIMA = "(g=>{const l=document.querySelector('[role=table][data-g2g='+g+']'); if(!l) return -1; const lt=l.getBoundingClientRect().top; return [...document.querySelectorAll('[aria-label=Indicadores]')].filter(x=>x.getClientRects().length&&x.getBoundingClientRect().bottom<=lt).length;})"
QF = "(g=>[...document.querySelectorAll('button[aria-pressed]')].filter(b=>{const s=b.closest('section'); return !!s&&!!s.querySelector('[data-g2g='+g+']');}).map(b=>b.innerText.replace(/\\s+/g,' ').trim().toLowerCase()))"
CAB = "((document.querySelector('header h1')||{}).parentElement||{innerText:''}).innerText.replace(/\\s+/g,' ').toLowerCase()"
SAZ = "(()=>{const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getClientRects().length); if(!a) return 0; const t=a.innerText; return (t.match(/▮/g)||[]).length>0 ? (t.split('\\n').filter(l=>/▮/.test(l)).length) : 0;})()"
m = MA(1440, 900); J = m.J
def espera(js, ate=20.0):
    """espera a condição observável (a página nova pronta), não um tempo fixo; falha no limite fica explícita no ok seguinte"""
    t0 = time.time()
    while time.time() - t0 < ate:
        try:
            if J(js): return True
        except Exception: pass
        time.sleep(.1)
    return False
def pronta(pg, extra='true'): return f"location.pathname.endsWith('/{pg}') && document.readyState==='complete' && !!document.body && ({extra})"
TELA = "!!document.querySelector('[aria-label=Indicadores]') && [...document.querySelectorAll('[role=row][data-rid]')].some(r=>r.getClientRects().length)"
def pelo_modulo(volta, hub, cartao, pg):
    """como o usuário: "‹ Módulo" → tela de entrada → cartão; devolve (nav da tela, cartões, erros da tela de entrada, chegou, erros da tela)"""
    nv = json.loads(J(NAV) or '{}'); m.clk(volta)
    espera(pronta(hub, "document.querySelectorAll('a.mod-cartao').length>0")); cs = json.loads(J(CARDS) or '[]'); e_hub = m.errs()
    m.clk(cartao, '.mod-grade'); ok = espera(pronta(pg, TELA)); time.sleep(.3)
    return nv, cs, e_hub, ok, m.errs()
try:
    # ---------------- Vendas ----------------
    m.ir('', pagina='IV.dc.html', limpa=True); m.sem_erro('IV 1440')
    nv, cs, e_hub, chegou, e_iv = pelo_modulo('Voltar para Comercial', 'MOD-COM.dc.html', 'Inteligência', 'IV.dc.html')
    par = [['PCOM.dc.html', 'Painel'], ['IV.dc.html', 'Inteligência']]
    m.ok(nv.get('cur') == ['Comercial'] and nv.get('volta') == ['MOD-COM.dc.html', '‹ Comercial'] and cs[:1] == par[:1] and par[1] in cs and chegou and not e_hub and not e_iv,
         'IV na tela de entrada do Comercial, que começa pelo Painel (PAINEL-01) (ícone Comercial marcado; "‹ Comercial" → cartão "Inteligência" abre a IV sem erro de JS)', [nv, cs, chegou, e_hub, e_iv])
    # TAB-07 (17/10/2026): o oráculo antigo pedia os cartões "em alta / vender agora / melhor mês" acima da lista; a regra os tira de lá e a
    # contagem fica no filtro rápido e no selo do cabeçalho (contraprova: o render anterior tem 1 grupo acima da lista e reprova aqui)
    ac = J(f"{ACIMA}('g_ivm')"); qf = J(f"{QF}('g_ivm')") or []; cab = J(CAB) or ''
    m.ok(ac == 0 and 'vender agora 1' in qf and 'vender agora: soja' in cab, 'INTEL-02 IV + TAB-07: sem cartões acima da lista; "Vender agora 1" no filtro rápido e no selo do cabeçalho', [ac, qf, cab])
    sj = m.linha('m:Soja em grão'); mi = m.linha('m:Milho em grão'); ma = m.linha('m:Mamão Formosa · fruta de campo'); fj = m.linha('m:Feijão em grão')
    m.ok('R$ 129,40/sc' in sj and 'Alta' in sj and 'Vender agora' in sj and 'set' in sj, 'INTEL-02 IV: soja R$ 129,40/sc em alta, melhor mês set, "Vender agora"', sj)
    # regra do ganho líquido (revisão Codex de 13/10, INTEL-02; oráculo e contraprova em inteligencia_unit P5/P11–P13): o alvo é o mês de maior
    # ganho depois do custo do dinheiro (1,2% a.m.), não o de maior ganho bruto (fev); o milho tem ganho líquido até dez
    m.ok('Queda' in mi and 'Esperar até dez' in mi and '+7,2% na época' in mi and '3,6% depois do custo do dinheiro' in mi and 'Sem ganho em esperar' not in mi,
         'INTEL-02 IV: milho em queda; o melhor mês depois do custo do dinheiro é dez (+7,2% na época, 3,6% líquido)', mi)
    m.ok('Vender na colheita' in ma and 'perecível' in ma, 'INTEL-02 IV: mamão perecível vende na colheita (a época orienta o plano)', ma)
    m.ok('Sem série de preço' in fj and 'R$ 0' not in fj, 'INTEL-02 IV: feijão sem fonte de preço fica sem série (ausente ≠ zero)', fj)
    m.abre('m:Soja em grão'); p = J(PAN) or ''
    m.ok('preço por mês no histórico' in p.lower() and 'últimos 12 meses' in p.lower() and 'sintética' in p and (J(SAZ) or 0) == 12, 'INTEL-02 IV painel da soja: 12 meses de sazonalidade em barras, últimos 12 meses e o rótulo de série sintética', [p[:300], J(SAZ)])
    m.clk('Fechar painel', w=.4)
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
    cl = m.linhas(3)
    if cl: m.abre(cl[0]); p = J(PAN) or ''
    m.ok(bool(cl) and 'Líquido = preço' in p and 'custo do prazo' in p, 'IV recebimento líquido: o painel mostra a conta (preço − frete − custo do prazo)', p[:400])
    # ---------------- Compras ----------------
    m.ir('', pagina='IC.dc.html'); m.sem_erro('IC 1440')
    nv, cs, e_hub, chegou, e_ic = pelo_modulo('Voltar para Suprimentos', 'MOD-SUP.dc.html', 'Inteligência', 'IC.dc.html')
    m.ok(nv.get('cur') == ['Suprimentos'] and nv.get('volta') == ['MOD-SUP.dc.html', '‹ Suprimentos'] and ['IC.dc.html', 'Inteligência'] in cs and chegou and not e_hub and not e_ic,
         'IC na tela de entrada do Suprimentos (ícone Suprimentos marcado; "‹ Suprimentos" → cartão "Inteligência" abre a IC sem erro de JS)', [nv, cs, chegou, e_hub, e_ic])
    b1 = J(KPI1) or ''; ac = J(f"{ACIMA}('g_icm')"); qf = J(f"{QF}('g_icm')") or []
    m.ok(ac == 0 and 'comprar agora 4' in qf and 'economia esperando o mês certo' in b1 and 'r$ 23.103,6' in b1,
         'INTEL-02 IC + TAB-07: sem cartões acima da lista; "Comprar agora 4" no filtro rápido; a economia esperando o mês certo abre os indicadores, depois da lista', [ac, qf, b1])
    se = m.linha('m:Semente de soja 58 W'); gl = m.linha('m:Glifosato 480')
    m.ok('Esperar' in se and 'pedir até 05/10' in se and 'R$ 13.554' in se, 'INTEL-02 IC: semente 58 W espera out, pedindo até 05/10 (necessidade 15/10 − 10 dias de entrega)', se)
    m.ok('Comprar agora' in gl and '28/09' in gl, 'INTEL-02 IC: glifosato com uso em 28/09 compra agora', gl)
    m.abre('m:Semente de soja 58 W'); p = J(PAN) or ''
    m.ok('mais barato' in p.lower() and 'planejar safra' in p.lower() and (J(SAZ) or 0) == 12, 'INTEL-02 IC painel: sazonalidade em 12 meses e a necessidade do Planejar safra', [p[:300], J(SAZ)])
    m.clk('Fechar painel', w=.4)
    b = J(KPI) or ''
    m.ok('r$ 41.363' in b and '1.277,84' in b, 'IC: economia pela melhor cotação R$ 41.363 e R$ 1.277,84/ha (oráculo do inteligencia_unit C3/C4)', b[:500])
    it = m.linhas(1)
    m.abre(it[0]) if it else None; p = J(PAN) or ''
    m.ok(bool(it) and 'Melhor cotação' in p and 'válida até' in p and 'Abrir Compra de insumos' in p, 'IC painel do insumo: melhor cotação, validade de cada uma e o próximo passo', p[:500])
    m.clk('Fechar painel', w=.4)
    # ---------------- celular ----------------
    for pg in ('IV.dc.html', 'IC.dc.html'):
        m.c.size(390, 844); m.ir('', pagina=pg); m.sem_erro(pg + ' 390')
        m.ok(m.largura() <= 0, pg + ' 390: sem rolagem lateral da página', m.largura())
finally:
    sys.exit(m.fim())
