# -*- coding: utf-8 -*-
"""F3 da base verde (19/10/2026): o "×" de fechar dos painéis laterais tem alvo de toque de 44 px com ponteiro grosso (DS-ALVO-20261015),
pela regra comum do ALVO_CSS (engine), sem mudar o desktop. Painéis abertos pela tela, como o usuário faria.
  A1 390 × 844 com toque: em cada painel aberto (CF-06 Metas, CF-01 Usuários, O.S., Manutenção) o "×" mede ≥ 44 × 44 px
  A2 1440 × 900 com mouse: o mesmo "×" continua com 32 × 32 px (o desktop não muda)
  A3 o fundo escuro, que também fecha o painel, não ganha tamanho (continua cobrindo a tela, sem largura fixa)
  A4 nenhum erro de JavaScript
Contraprova: o render da composição 5bc0b340 reprova A1 (o "×" fica com 32 px com toque).
Uso (de gen37/): env CHROME_BIN=… SAFRION_DADOS=sintetico [RENDER_DIR=…] python3 -B alvo_fechar_test.py"""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
OK = FAIL = 0
def chk(nome, cond, info=''):
    global OK, FAIL
    if cond: OK += 1; print('OK   ', nome)
    else: FAIL += 1; print('FALHA', nome, '·', str(info)[:900])
# painel e linha que o abre (a primeira linha da tabela da tela)
TELAS = [('CF-06.dc.html', '[data-g2g=g_metas] [role=row][data-rid]'), ('CF-01.dc.html', '[role=row][data-rid]'),
         ('OS.dc.html', '[role=row][data-rid]'), ('MA.dc.html', '[role=row][data-rid]')]
XIS = """JSON.stringify([...document.querySelectorAll("button[aria-label^='Fechar']")].filter(b=>b.getClientRects().length&&/width: 32px/.test(b.getAttribute('style')||''))
  .map(b=>{ const r=b.getBoundingClientRect(); return [Math.round(r.width),Math.round(r.height)]; }))"""
FUNDO = """JSON.stringify([...document.querySelectorAll("button[aria-label^='Fechar'][tabindex='-1']")].filter(b=>b.getClientRects().length).map(b=>{ const r=b.getBoundingClientRect(); return [Math.round(r.width),Math.round(r.height),innerWidth]; }))"""
p, srv = servir(R); c = Chrome(); J = c.js
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))"})
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
erros = []
def abre(pg, sel):
    c.goto(U(pg), 1.8)
    J(f"(()=>{{ const r=document.querySelector({json.dumps(sel)}); if(r) (r.querySelector('.g2pw')||r.querySelector('[role=cell]')||r).click(); }})()"); time.sleep(.8)
    erros.extend(J("window.__e") or [])
try:
    med = {}
    for w, h, toque in ((390, 844, True), (1440, 900, False)):
        c.aparelho(w, h, 2 if toque else 1, toque); c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1")
        for pg, sel in TELAS:
            abre(pg, sel); med[(w, pg)] = (json.loads(J(XIS) or '[]'), json.loads(J(FUNDO) or '[]'), J("matchMedia('(pointer:coarse)').matches"))
    print('      medidas:', {f'{k[0]} {k[1]}': v for k, v in med.items()})
    com = [(pg, med[(390, pg)]) for pg, _ in TELAS if med[(390, pg)][0]]
    chk('A1 390 px com toque: o "×" dos painéis abertos mede ≥ 44 × 44 px (pelo menos 3 telas)',
        len(com) >= 3 and all(v[2] and all(x[0] >= 44 and x[1] >= 44 for x in v[0]) for _, v in com), com)
    des = [(pg, med[(1440, pg)]) for pg, _ in TELAS if med[(1440, pg)][0]]
    chk('A2 1440 px com mouse: o mesmo "×" continua com 32 × 32 px', len(des) >= 3 and all(not v[2] and all(x == [32, 32] for x in v[0]) for _, v in des), des)
    fundo = [x for k, v in med.items() for x in v[1]]
    chk('A3 o fundo escuro que fecha o painel continua cobrindo a tela (sem o alvo de 44 px)', bool(fundo) and all(x[0] >= x[2] - 1 for x in fundo), fundo)
    chk('A4 nenhum erro de JavaScript', not erros, erros[:5])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {OK}/{OK+FAIL} ok')
sys.exit(1 if FAIL else 0)
