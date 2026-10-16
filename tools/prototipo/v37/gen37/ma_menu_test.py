# -*- coding: utf-8 -*-
"""Navegação da Manutenção (proprietário, 13/10/2026: barra lateral sempre recolhida, um ícone por módulo, sem submenus).
Confere: o ícone Manutenção leva à tela de entrada MOD-MAN.dc.html (13/10, proprietário: "o menu de manutenção está sem os submenus na
tela igual os demais"), um cartão por visão (Sem ordem · Ordens · Ativos · Planos → MA.dc.html#vis=…), e fica destacado (aria-current="page"
e fundo verde) em qualquer visão, sem subitens nem expandir; o cartão abre a MA na visão dele e "‹ Manutenção" volta ao cartão; as 4 visões
ficam também no seletor da própria tela (botões; lista no celular) e no endereço #vis=…; trocar de visão muda a lista sem recarregar.
Corrida da v57: com o painel da OM aberto ao lado, a troca de visão logo após abrir às vezes se perdia (o # antigo voltava); aqui a troca
é repetida pelo seletor e pelo endereço #vis= e precisa valer e ficar. Uso: python3 ma_menu_test.py (lê _render)."""
import sys, json, re, time
from ma_lib import MA
from ui37 import INICIO37, HUB37
HUB = HUB37['Manutenção']

m = MA(1440, 900); J = m.J
VIS = ['semordem', 'ordens', 'ativos', 'planos']
TIT = ['Sem ordem', 'Ordens', 'Ativos', 'Planos']
LISTA = {'semordem': r'^[a-z]:', 'ordens': r'^OM-\d+$', 'ativos': r'^[a-z]+\d+$', 'planos': r'^PM-\d+$'}   # data-rid das linhas de cada visão
VERDE = 'rgb(30, 122, 76)'
NAV = ("JSON.stringify([...document.querySelectorAll('nav[aria-label=Menu] a')].map(a=>[a.getAttribute('aria-label'),a.getAttribute('title'),"
       "a.getAttribute('href'),a.getAttribute('aria-current'),a.innerText.trim(),getComputedStyle(a).backgroundColor]))")
SUB = "[...document.querySelectorAll('nav[aria-label=Menu] button,nav[aria-label=Menu] .ml-tog')].filter(e=>e.getClientRects().length).length"
TELA = ("JSON.stringify([location.hash,[...document.querySelectorAll('main .ma-vis button')].map(b=>[b.innerText.replace(/\\s*\\d+\\s*$/,'').trim(),b.getAttribute('aria-pressed')]),"
        "(document.querySelector('main .ma-vis-m select')||{}).value||'',"
        "(()=>{const t=[...document.querySelectorAll('[role=table]')].filter(t=>t.getClientRects().length)[0]; return t?[...t.querySelectorAll('[role=row][data-rid]')].map(r=>r.getAttribute('data-rid')):[];})()])")


def tela():
    try: return json.loads(J(TELA) or '["",[],"",[]]')
    except Exception: return ['', [], '', []]


def mostra(v):
    """a tela está na visão v: endereço #vis=v, seletor com as 4 visões e só v marcado (botões e lista do celular), linhas da visão v"""
    h, sel, sv, rows = tela(); i = VIS.index(v)
    return (h.split('&')[0] == '#vis=' + v and [x[0] for x in sel] == TIT and [x[1] for x in sel] == ['true' if k == i else 'false' for k in range(4)]
            and sv == v and bool(rows) and all(re.match(LISTA[v], r) for r in rows))


def espera(cond, lim=3.0):
    """espera a condição observável até lim segundos; no limite devolve False (falha explícita)"""
    t0 = time.time()
    while True:
        try:
            if cond(): return True
        except Exception: pass
        if time.time() - t0 > lim: return False
        time.sleep(.05)


def vale_e_fica(v):
    """a corrida da v57 desfazia a troca depois de feita (o # antigo voltava): a visão nova precisa aparecer e continuar ali"""
    if not espera(lambda: mostra(v)): return False
    time.sleep(.4)   # espera fixa de propósito: o defeito é a volta tardia do estado antigo
    return mostra(v)


try:
    for i, v in enumerate(VIS):
        m.ir('vis=' + v, perfil='Otávio', limpa=(i == 0)); na = espera(lambda: mostra(v), 10)   # sob carga a MA demora a montar
        L = json.loads(J(NAV) or '[]')
        man = [x for x in L if x[0] == 'Manutenção']; cur = [x[0] for x in L if x[3] == 'page']; sub = J(SUB)
        m.ok(man == [['Manutenção', 'Manutenção', HUB, 'page', '', VERDE]] and cur == ['Manutenção']
             and all(x[5] != VERDE for x in L if x[0] != 'Manutenção') and [x[2] for x in L if (x[2] or '').startswith(('MA', 'MOD-MAN'))] == [HUB]
             and sub == 0 and na,
             f'visão {v}: um só ícone Manutenção → {HUB}, destacado, sem texto e sem subitens; o seletor da tela com as 4 visões e só "{TIT[i]}" marcado; a lista é a da visão',
             [man, cur, sub, tela()])
    # o ícone Manutenção abre, a partir do início (Mapa), a tela de entrada: um cartão por visão, na ordem do seletor, ícone destacado
    CARDS = "JSON.stringify([...document.querySelectorAll('a.mod-cartao')].filter(a=>a.getClientRects().length).map(a=>[a.getAttribute('href'),a.innerText.trim(),!!a.querySelector('svg path')]))"
    m.ir('', perfil='Otávio', pagina=INICIO37); ini = espera(lambda: J(f"location.pathname.split('/').pop()==='{INICIO37}'&&document.readyState==='complete'"), 10)
    J("window.__antes=1"); r = m.clk('Manutenção', 'nav[aria-label=Menu]', w=0)
    foi = ini and espera(lambda: J(f"!window.__antes&&location.pathname.split('/').pop()==='{HUB}'&&document.readyState==='complete'&&document.querySelectorAll('a.mod-cartao').length===5"), 10)
    cs = json.loads(J(CARDS) or '[]'); cur = [x[0] for x in json.loads(J(NAV) or '[]') if x[3] == 'page']
    m.ok(r == 'ok' and foi and cs == [['PMAN.dc.html', 'Painel', True]] + [['MA.dc.html#vis=' + v, t, True] for v, t in zip(VIS, TIT)] and cur == ['Manutenção'],
         f'no início ({INICIO37}), tocar o ícone Manutenção abre a tela de entrada ({HUB}) com o Painel e os 4 cartões (ícone e nome curto: Sem ordem · Ordens · Ativos · Planos), ícone destacado', [r, foi, cs, cur])
    # o cartão "Ordens" abre a MA na visão Ordens; "‹ Manutenção" volta à tela de entrada com o foco no cartão aberto
    J("[...document.querySelectorAll('a.mod-cartao')].find(a=>a.innerText.trim()==='Ordens').click()")
    foi = espera(lambda: J("location.pathname.split('/').pop()==='MA.dc.html'&&document.readyState==='complete'"), 10) and espera(lambda: mostra('ordens'), 10)
    vt = J("(()=>{const a=document.querySelector('a.volta37'); return a?[a.getAttribute('href'),a.innerText.replace(/\\s+/g,' ').trim()].join(' | '):'';})()") or ''
    J("document.querySelector('a.volta37').click()")
    de = espera(lambda: J(f"location.pathname.split('/').pop()==='{HUB}'&&(document.activeElement&&document.activeElement.getAttribute('href'))==='MA.dc.html#vis=ordens'"), 6)
    m.ok(foi and vt == HUB + ' | ‹ Manutenção' and de, 'o cartão "Ordens" abre a MA na visão Ordens (só "Ordens" marcado); "‹ Manutenção" volta à tela de entrada com o foco no cartão', [foi, vt, tela()[0], de])
    # trocar de visão pelo seletor da própria tela: mesma tela (sem recarregar); endereço, marca e lista mudam
    m.ir('vis=ordens', perfil='Otávio'); pan = espera(lambda: m.pan().startswith('OM-') and mostra('ordens'), 10); J("window.__mesma=1")
    r = m.clk('Planos', 'main .ma-vis', w=0); foi = vale_e_fica('planos')
    cur = [x[0] for x in json.loads(J(NAV) or '[]') if x[3] == 'page']
    m.ok(r == 'ok' and pan and foi and J("window.__mesma===1") and cur == ['Manutenção'],
         'tocar "Planos" no seletor estando em Ordens (painel da OM aberto) troca a visão na mesma tela: #vis=planos, "Planos" marcado e a lista dos planos', [r, pan, tela(), cur])
    # celular (390 px): o seletor vira a lista "Visão"; escolher "Ativos" troca a visão na mesma tela, sem rolagem lateral
    m.c.size(390, 844); m.ir('vis=ordens', perfil='Otávio'); cel = espera(lambda: mostra('ordens'), 10); J("window.__mesma=1")
    vis_m = J("(()=>{const s=document.querySelector('main .ma-vis-m select'); return s&&s.getClientRects().length?[...s.options].map(o=>o.value):null;})()")
    m.setv('main .ma-vis-m select', 'ativos'); foi = vale_e_fica('ativos')
    m.ok(cel and vis_m == VIS and foi and J("window.__mesma===1") and m.largura() <= 0, 'celular: a lista "Visão" traz as 4 visões; escolher "Ativos" troca a visão na mesma tela', [vis_m, tela(), m.largura()])
    m.c.size(1440, 900)
    # corrida da v57, sem o menu: com o painel da OM aberto ao lado, trocar logo após abrir, pelo seletor e pelo endereço #vis=
    for modo in ('seletor', 'endereço #vis='):
        falhou = []
        for i in range(8):
            m.ir('vis=ordens'); alvo = 'ativos' if i % 2 else 'planos'
            pan = espera(lambda: m.pan().startswith('OM-') and '&om=' in m.hash(), 10)   # pré-condição: o painel da OM aberto ao lado (sob carga a MA demora a montar)
            if modo == 'seletor': m.clk(TIT[VIS.index(alvo)], 'main .ma-vis', w=.05)
            else: J(f"location.hash='vis={alvo}'"); time.sleep(.05)
            if not (pan and vale_e_fica(alvo)): falhou.append((i, pan, tela()[0]))
        m.ok(not falhou, f'com o painel da OM aberto ao lado, 8 trocas de visão pelo {modo}, logo após abrir, valem e ficam (o # antigo não volta)', falhou)
finally:
    sys.exit(m.fim())   # o código de saída segue o resultado (na v57 saía 0 mesmo com falha)
