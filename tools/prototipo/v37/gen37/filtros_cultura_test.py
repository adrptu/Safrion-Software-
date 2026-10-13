# -*- coding: utf-8 -*-
"""Cultura e Talhão no filtro principal (proprietário, 13/10/2026: "em ordem de serviço coloque no filtro principal da tela... também cultura e
talhão. nas demais telas que isso for bastante essencial e ajudar o usuário, pode por também"). Confere no navegador:
  F1 Produção (Colheita, Recebimento e Estoque de produto): a faixa "Filtros desta tela" tem Cultura; escolher uma cultura deixa só linhas
     dela (e menos que antes quando há outras); "Todas" volta tudo
  F2 Colheita: Talhão segue a Cultura (só talhões dela) e filtra as linhas pelo talhão
  F3 O.S.: os avisos que eram do seletor de talhão da barra voltaram (revisão do agente de testes, 13/10): "Total: N O.S. distintas" na Tabela
     agrupada e o aviso de talhão que sai do filtro ao trocar a fazenda, com o nome do talhão (não o ID)
  F4 390 px: as listas da faixa com alvo de toque ≥ 32 px; sem rolagem lateral; sem erro de JS
Uso: python3 filtros_cultura_test.py (lê _render ou RENDER_DIR)."""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:700]), flush=True)

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
p, srv = servir(R); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
CULTURAS = ['Café', 'Feijão', 'Mamão Formosa', 'Milho', 'Soja']
ROWS = """JSON.stringify([...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent).flatMap(t=>[...t.querySelectorAll('[role=row]')].slice(1)
  .filter(r=>r.offsetParent&&!r.classList.contains('g2tot')).map(r=>r.innerText.replace(/\\s+/g,' '))))"""
def opts(al): return json.loads(J(f"JSON.stringify([...document.querySelectorAll('select[aria-label=\"{al}\"] option')].map(o=>o.textContent))") or '[]')
def sel(al, val):
    J(f"""(()=>{{const s=document.querySelector('select[aria-label="{al}"]'); if(!s) return; s.value={json.dumps(val)}; s.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.7)
def limpa(): c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1")
def so_da(rows, cu):   # linha de outra cultura = contém o nome de outra cultura e não o desta
    outras = [x for x in CULTURAS if x != cu and not (cu == 'Mamão Formosa' and x == 'Mamão')]
    return [r for r in rows if any(o in r for o in outras) and cu not in r]
try:
    c.aparelho(1440, 900, 1, False); c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__err='';addEventListener('error',e=>{window.__err+=(e.message||'erro')+' | ';});"})
    res = {}
    for pg, cu in (('COLH.dc.html', 'Soja'), ('CARGA.dc.html', 'Soja'), ('PROD.dc.html', 'Soja')):
        limpa(); c.goto(U(pg), 1.4)
        o = opts('Filtrar por cultura'); r0 = json.loads(J(ROWS) or '[]'); sel('Filtrar por cultura', cu); r1 = json.loads(J(ROWS) or '[]')
        ruins = so_da(r1, cu); sel('Filtrar por cultura', 'Todas'); r2 = json.loads(J(ROWS) or '[]')
        res[pg] = (o, len(r0), len(r1), ruins[:2], len(r2))
    chk('F1 Colheita, Recebimento e Estoque de produto: Cultura na faixa; "Soja" deixa só linhas de soja (menos que antes); "Todas" volta tudo',
        all(v[0] and v[0][0] == 'Todas' and 'Soja' in v[0] and v[2] < v[1] and not v[3] and v[4] == v[1] for v in res.values()), res)
    limpa(); c.goto(U('COLH.dc.html'), 1.4)
    t0 = opts('Filtrar por talhão'); sel('Filtrar por cultura', 'Café'); t1 = opts('Filtrar por talhão')
    sel('Filtrar por cultura', 'Todas'); sel('Filtrar por talhão', 'T2'); r = json.loads(J(ROWS) or '[]')
    folhas = [x for x in r if not x.startswith('▾') and not x.startswith('▸')]
    chk('F2 Colheita: o Talhão segue a Cultura (Café → só C1) e "T2" deixa só linhas do T2', t0[:1] == ['Todos'] and len(t0) > 3 and t1 == ['Todos', 'C1'] and folhas and all('T2' in x for x in folhas),
        [t0[:6], t1, folhas[:3]])
    # F3 · O.S.: total do agrupado e aviso do talhão que sai do filtro
    limpa(); c.goto(U('OS.dc.html'), 1.4); J("document.querySelector('[data-visao=\"agrupada\"]').click()"); time.sleep(.8)
    gt = J("(()=>{const n=[...document.querySelectorAll('[role=note]')].find(x=>/O\\.S\\. distintas/.test(x.innerText)&&x.getClientRects().length); return n?n.innerText:'';})()") or ''
    chk('F3 O.S. › Tabela agrupada: "Total: N O.S. distintas" à vista', 'O.S. distintas' in gt, gt)
    limpa(); c.goto(U('OS.dc.html'), 1.4); sel('Filtrar por fazenda', 'Lagoa Grande'); sel('Filtrar por talhão', 'Lagoa Grande|PV04'); sel('Filtrar por fazenda', 'Santa Rita')
    msg = J("(()=>{const n=[...document.querySelectorAll('[role=status]')].find(x=>/saiu do filtro/.test(x.innerText)&&x.getClientRects().length); return n?n.innerText:'';})()") or ''
    chk('F3 O.S.: trocar a fazenda tira o talhão do filtro com aviso, pelo nome ("Pivô 4"), não pelo ID', 'Pivô 4' in msg and 'PV04' not in msg, msg)
    # F4 · celular
    c.aparelho(390, 844, 2, True); alt = {}
    for pg in ('OS.dc.html', 'COLH.dc.html', 'PROD.dc.html'):
        limpa(); c.goto(U(pg), 1.4)
        alt[pg] = [json.loads(J("JSON.stringify([...document.querySelectorAll('.mf-tela select')].map(s=>Math.round(s.getBoundingClientRect().height)))") or '[]'),
                   J("document.documentElement.scrollWidth-document.documentElement.clientWidth")]
    chk('F4 390 px: listas da faixa com alvo ≥ 32 px e sem rolagem lateral', all(v[0] and min(v[0]) >= 32 and (v[1] or 0) <= 0 for v in alt.values()), alt)
    chk('F4 sem erro de JS', not (J("window.__err||''") or ''), J("window.__err||''"))
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas')
sys.exit(1 if FAIL else 0)
