# -*- coding: utf-8 -*-
"""MUX-CORTE (19/10/2026): o rótulo do pivô no Mapa (Lagoa Grande) mostra o valor inteiro, em todas as camadas, a 1440 e a 390 px.
Antes, o valor ficava numa linha só, com reticências: 34 rótulos cortados a 1440 px (número, unidade ou estado), entre eles o "em colheita · 484,89 k…"
da camada Colheita e produtividade em kg/ha (P5 da UNID-PROD).
  R1 1440 × 900: em cada camada da barra, nenhum valor visível cortado (largura nem altura) e nenhum "·" solto no começo de linha
  R2 390 × 844 com toque: o mesmo
  R3 Colheita e produtividade com o Mamão em kg/ha (Ana): o rótulo do Pivô 19 traz a situação e a produtividade com a unidade inteira
  R4 nenhum erro de JavaScript
Contraprova: o render da v143 (sem a quebra) reprova R1 (34 cortes) e R3.
Uso (de gen37/): env CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico [RENDER_DIR=…] python3 -B mapa_rotulo_corte_test.py"""
import os, sys, json, time, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault('CDP_GL', '1')
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
OK = FAIL = 0
def chk(nome, cond, info=''):
    global OK, FAIL
    if cond: OK += 1; print('OK   ', nome)
    else: FAIL += 1; print('FALHA', nome, '·', str(info)[:900])
# valor visível (span) cortado na largura ou na altura; "·" sem o espaço rígido antes (abriria a linha seguinte)
CORTE = r"""JSON.stringify(Object.values(window.__LGI.markers).map(m=>m.getElement()).filter(e=>e.getClientRects().length).map(e=>{ const s=e.children[1];
  const vis=getComputedStyle(s).display!=='none'&&s.textContent.trim()!==''; return [e.children[0].textContent, s.textContent,
  vis&&(s.scrollWidth>s.clientWidth+1||s.scrollHeight>s.clientHeight+1), vis&&/(^|[^ ])·/.test(s.textContent)]; }).filter(x=>x[2]||x[3]))"""
TABS = "JSON.stringify([...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] [role=tab]')].map(b=>b.innerText.trim()))"
def camada(nome):
    J(f"(()=>{{const b=[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] [role=tab]')].find(b=>b.innerText.trim()==={json.dumps(nome)}); if(b) b.click();}})()")
    time.sleep(1.4)
def espera(e, s=30):
    f = time.time() + s
    while time.time() < f:
        if J(e): return True
        time.sleep(.3)
    return False
p, srv = servir(R); c = Chrome(); J = c.js
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))"})
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
erros = []
def abre(w, h, toque):
    c.aparelho(w, h, 1 if w > 400 else 2, toque)
    c.goto(U('Main.dc.html'), .3)
    # a Ana escolhe kg/ha para o Mamão (a preferência fica no navegador, por perfil × cultura: g2unidChave)
    J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana');"
      "localStorage.setItem('safrion.pref.unidprod:Ana:Mamão Formosa','kg'); sessionStorage.setItem('mapa-ctx','{\"mf_faz\":\"Lagoa Grande\"}'); 1")
    c.goto(U('IN-04.dc.html'), 1.0); espera("!!(window.__LGI&&window.__LGI.pronto)")
try:
    p19 = ''
    for w, h, toque, rot in ((1440, 900, False, 'R1 1440 px'), (390, 844, True, 'R2 390 px com toque')):
        abre(w, h, toque); tabs = json.loads(J(TABS) or '[]'); ruins = {}
        for t in tabs:
            camada(t); r = json.loads(J(CORTE) or '[]')
            if r: ruins[t] = r
            if w == 1440 and t == 'Colheita e produtividade':
                p19 = J("(()=>{ const m=window.__LGI.markers['PV19']; return m?m.getElement().children[1].textContent.replace(/\\s+/g,' ').trim():''; })()") or ''
        erros.extend(J("window.__e") or [])
        chk(f'{rot}: em {len(tabs)} camadas, nenhum valor de rótulo cortado nem "·" no começo de linha', len(tabs) >= 9 and not ruins,
            {k: (len(v), v[:3]) for k, v in ruins.items()} or tabs)
    chk('R3 Colheita e produtividade (Mamão em kg/ha): o Pivô 19 mostra a situação e a produtividade com a unidade inteira',
        bool(re.fullmatch(r'em colheita · [\d.]+,\d+ kg/ha', p19)), p19)
    chk('R4 nenhum erro de JavaScript', not erros, erros[:5])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {OK}/{OK+FAIL} ok')
sys.exit(1 if FAIL else 0)
