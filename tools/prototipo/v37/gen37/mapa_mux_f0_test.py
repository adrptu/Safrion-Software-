# -*- coding: utf-8 -*-
"""MUX-F0 · Destinos, nomes e ícone do Mapa (IN-04), aceite da §8.2 de docs/integracao/V73/MAPA-UX/confronto-claude-codex.md (pedido do
proprietário de 16/10/2026; implantação de 17/10). Chrome a 1440 × 900 (mouse) e a 390 × 844 (toque).
  F0-1 "Nova O.S. neste talhão" (camada Ordens de serviço) e "Abrir ordens" com um talhão escolhido levam #tal=Fazenda|Talhão; a O.S. abre com o
       talhão já escolhido no filtro do topo (Filtrar por talhão = "Santa Rita|T4")
  F0-2 com o contexto salvo na Santa Rita, IN-04.dc.html#talhao=PV05 abre a Lagoa Grande com o P5 escolhido; #talhao=PV99 mostra o aviso
       (visível, role=status) e não escolhe nenhum talhão
  F0-3 Satélite sem link para o AG-06 (Eficácia e histórico de pragas), na faixa e no painel
  F0-4 Colheita e produtividade › Situação com o link do módulo na faixa (COLH); Solo leva ao AG-02 pelo painel do talhão (na faixa, o link
       cortava os números a 1440: MAP-04)
  F0-5 as ações de Colheita e produtividade levam o ícone que a barra das funções já usa (engine.ICONS['Colheita'])
  F0-6 no IN-04 o pivô tem um nome só, "P5": no marcador, no título do painel e no nome acessível; "Pivô 5" não aparece no painel
  F0-7 sem erro de JavaScript (as duas larguras)
Medidas (antes → depois): destinos sem contexto (AG-06 na faixa e no painel, Nova O.S. e Abrir ordens sem talhão); ações de Colheita sem ícone;
nomes do mesmo pivô no IN-04.
Contraprova: RENDER_DIR=<render da base 0b3d0d4> reprova F0-1 a F0-6.
Uso (de gen37/): env CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico RENDER_DIR=$PWD/_render python3 -B mapa_mux_f0_test.py"""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
import engine as E
from mapa_mux_lib import chk, OK, FAIL, espera, abre, fazenda, camada, filtro, caixa, painel, erros, tal_el, LG_PRONTO

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
p, srv = servir(R); c = Chrome(); J = c.js
U = f'http://127.0.0.1:{p}/IN-04.dc.html'
MED = {}
def clica_tal(tid):
    J("(()=>{const b=%s; if(b&&b.tagName!=='BUTTON') b.dispatchEvent(new MouseEvent('click',{bubbles:true})); })()" % tal_el(tid))
def clica_pivo(pid):
    """Pivô da Lagoa Grande: o clique é no polígono do mapa (o botão do marcador não pega o ponteiro), como a pessoa."""
    b = caixa(J, pid) or {}
    if b: c.mouse(b['x'], b['y']); c.mouse(b['x'], b['y'], 'mousePressed', 'left'); c.mouse(b['x'], b['y'], 'mouseReleased', 'left')
def links():
    return json.loads(J("JSON.stringify([...document.querySelectorAll('main a[href]')].filter(a=>a.getClientRects().length).map(a=>[a.innerText.replace(/\\s+/g,' ').trim(),a.getAttribute('href')]))") or '[]')
try:
    for larg, alt, toque in ((1440, 900, False), (390, 844, True)):
        tag = f'{larg}'
        # ---------- F0-1 destinos da O.S. com o talhão ----------
        abre(c, U, larg, alt, toque, faz='Santa Rita'); camada(J, 'Ordens de serviço'); clica_tal('T4'); espera(J, "!!document.querySelector('main aside[aria-label]')", 4); time.sleep(.3)
        nova = json.loads(J("JSON.stringify([...document.querySelectorAll('main aside[aria-label] a')].filter(a=>/Nova O\\.S\\. neste talhão/.test(a.innerText)).map(a=>a.getAttribute('href')))") or '[]')
        abr = [h for t, h in links() if t.startswith('Abrir ordens')]
        exp = 'OS.dc.html#tal=' + 'Santa%20Rita%7CT4'
        MED[f'destinos_os_{tag}'] = {'nova': nova, 'abrir_ordens': abr}
        chk(f'F0-1a {tag}: "Nova O.S. neste talhão" e "Abrir ordens" (com o T4 escolhido) levam #tal=Santa Rita|T4', nova == [exp] and abr == [exp], [nova, abr])
        if larg == 1440:
            c.goto(f'http://127.0.0.1:{p}/{exp}', 1.2); espera(J, "(document.querySelector('select[aria-label=\"Filtrar por talhão\"]')||{}).value==='Santa Rita|T4'", 8)
            v = J("(document.querySelector('select[aria-label=\"Filtrar por talhão\"]')||{}).value") or ''
            chk('F0-1b a O.S. abre com o talhão já escolhido (Filtrar por talhão = Santa Rita|T4)', v == 'Santa Rita|T4', v)
        # ---------- F0-2 #talhao= troca a fazenda; ID inexistente avisa ----------
        abre(c, U, larg, alt, toque, faz='Santa Rita')   # contexto salvo na Santa Rita
        c.goto(U + '#talhao=PV05', 1.2); espera(J, "(document.querySelector('[data-mux-grupo=LG] [data-talhao=PV05]')||{getAttribute:()=>''}).getAttribute('aria-pressed')==='true'", 25)
        fz = J("(document.querySelector('select[aria-label=\"Filtrar por fazenda\"]')||{}).value"); ap = J("(document.querySelector('[data-mux-grupo=LG] [data-talhao=PV05]')||{getAttribute:()=>null}).getAttribute('aria-pressed')")
        t2 = J("(document.querySelector('main aside[aria-label] h2')||{}).innerText||''")
        chk(f'F0-2a {tag}: com o contexto na Santa Rita, #talhao=PV05 abre a Lagoa Grande com o P5 escolhido (aria-pressed e painel)', fz == 'Lagoa Grande' and ap == 'true' and t2.startswith('P5 ·'), [fz, ap, t2])
        c.goto(U + '#talhao=PV99', 1.2); espera(J, "/PV99/.test((document.querySelector('.mux-msg')||{}).innerText||'')", 10)
        av = J("(()=>{const m=document.querySelector('.mux-msg'); return m&&m.getClientRects().length?[m.getAttribute('role'),m.innerText]:null;})()")
        sel = J("document.querySelectorAll('[data-mux-grupo] [aria-pressed=true]').length+document.querySelectorAll('main aside[aria-label]').length")
        chk(f'F0-2b {tag}: #talhao=PV99 mostra o aviso visível e acessível (role=status) e não escolhe nenhum talhão', bool(av) and av[0] == 'status' and 'PV99' in av[1] and sel == 0, [av, sel])
        # ---------- F0-3 Satélite sem AG-06 ----------
        abre(c, U, larg, alt, toque, faz='Santa Rita'); camada(J, 'Satélite'); clica_tal('P1'); espera(J, "!!document.querySelector('main aside[aria-label]')", 4); time.sleep(.3)
        ag6 = [h for t, h in links() if 'AG-06' in (h or '')]
        MED[f'ag06_{tag}'] = ag6
        chk(f'F0-3 {tag}: Satélite sem link para o AG-06 na faixa e no painel do P1', not ag6 and painel(J) != '', ag6)
        # ---------- F0-4 Solo e Colheita › Situação com o link do módulo ----------
        # Solo: o link do módulo na faixa cortava os números a 1440 (MAP-04, pedido do proprietário de 16/10, mapa_faixa_test F3); o AG-02 fica no
        # painel do talhão com laudo ("Abrir <laudo>") e a faixa mantém os números inteiros
        camada(J, 'Solo'); clica_tal('T1'); espera(J, "!!document.querySelector('main aside[aria-label]')", 4); time.sleep(.3)
        l_solo = [(t, h) for t, h in links() if (h or '').startswith('AG-02.dc.html#') and t.startswith('Abrir') and 'registrar' not in h]
        cort = J("(()=>{const n=document.querySelector('[role=group][aria-label^=\"Indicadores de\"]'); return n?n.scrollWidth>n.clientWidth+1:null;})()")
        camada(J, 'Colheita e produtividade'); filtro(J, 'Mostrar', 'Situação'); l_col = [(t, h) for t, h in links() if (h or '').startswith('COLH.dc.html') and t.startswith('Abrir Previsão')]
        chk(f'F0-4 {tag}: Colheita › Situação com o link do módulo (Abrir Previsão e colheita › COLH); Solo leva ao AG-02 pelo painel do T1 e a faixa do Solo não corta os números (a 1440)',
            bool(l_solo) and bool(l_col) and (cort is False or larg != 1440), [l_solo, cort, l_col])
        # ---------- F0-5 ícone das ações de Colheita ----------
        ICO = E.ICONS.get('Colheita', '')
        acs = []
        for t in ('T1', 'T2', 'P1', 'P2', 'T4', 'T3', 'T7', 'C1'):
            clica_tal(t); espera(J, "!!document.querySelector('main aside[aria-label]')", 3); time.sleep(.2)
            acs += json.loads(J("JSON.stringify([...document.querySelectorAll('main aside[aria-label] > div:last-child a, main aside[aria-label] > div:last-child button')].map(a=>[a.innerText.trim(),[...a.querySelectorAll('svg path')].map(p=>p.getAttribute('d'))]))") or '[]')
            clica_tal(t); time.sleep(.2)
        sem = [a[0] for a in acs if ICO not in a[1]]
        MED[f'colheita_sem_icone_{tag}'] = [len(sem), len(acs)]
        chk(f'F0-5 {tag}: as ações de Colheita e produtividade levam o ícone da barra (engine.ICONS[Colheita])', bool(acs) and not sem and bool(ICO), [sem, len(acs)])
        # ---------- F0-6 nome único do pivô ----------
        abre(c, U, larg, alt, toque, faz='Lagoa Grande'); camada(J, 'Integrado')
        if toque:   # no celular o P5 pode nascer embaixo da legenda: escolhe pelo endereço #talhao= (o mesmo destino do cadastro)
            c.goto(U + '#talhao=PV05', 1.2); espera(J, LG_PRONTO, 25)
        else: clica_pivo('PV05')
        espera(J, "!!document.querySelector('main aside[aria-label]')", 6); time.sleep(.4)
        mk = J("(()=>{const b=document.querySelector('[data-mux-grupo=LG] [data-talhao=PV05]'); return b?[b.querySelector('b').innerText,b.getAttribute('aria-label')]:null;})()") or [None, '']
        tt = J("(document.querySelector('main aside[aria-label] h2')||{}).innerText||''"); pn = painel(J)
        nomes = {x for x in ('P5', 'Pivô 5', 'PV05') if (x in (mk[0] or '') or (mk[1] or '').startswith(x + ',') or tt.startswith(x + ' ·') or (x != 'PV05' and x + ' ' in pn + ' '))}
        MED[f'nomes_pivo_{tag}'] = sorted(nomes)
        chk(f'F0-6 {tag}: o pivô se chama P5 no marcador, no título do painel e no nome acessível; "Pivô 5" fora do painel', mk[0] == 'P5' and (mk[1] or '').startswith('P5, ') and tt.startswith('P5 ·') and 'Pivô 5' not in pn, [mk, tt, pn[:160]])
        ee = erros(J); chk(f'F0-7 {tag}: sem erro de JavaScript', not ee, ee[:3])
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print('MEDIDAS', json.dumps(MED, ensure_ascii=False))
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falha(s)' + (' · ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
