# -*- coding: utf-8 -*-
"""MAP-04 · faixa branca da camada do Mapa com a mesma altura em todas as camadas (proprietário, 16/10/2026: "deixe a espessura da parte branca
da opção solo igual aos demais, manter um padrão visual") e funil na faixa das fazendas do Planejar safra (16/10: "não falta o símbolo do
filtro que é nosso padrão?"). Mede, nas 2 fazendas e nas 9 camadas, a distância da barra de camadas ao mapa: no computador (1440, 1280, 1024)
uma linha só e a mesma altura; no celular (390, toque) a mesma altura em todas. A 1440 os números do Solo aparecem inteiros e o 1º número de toda camada fica à vista (o resto rola na própria faixa); nenhuma
largura cria rolagem lateral da página. Contraprova: o render de ff3903d reprova F1 (Solo com 78 px, as demais com 47) e S1 (sem funil).
Uso (de gen37/): CHROME_BIN=… SAFRION_DADOS=sintetico python3 -B mapa_faixa_test.py   (RENDER_DIR=<render> para a contraprova)"""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
OK, FAIL = [], []
def chk(n, c, x=''):
    (OK if c else FAIL).append(n); print(('OK   ' if c else 'FALHA'), n, '' if c else str(x)[:500], flush=True)
p, srv = servir(R); c = Chrome(); J = c.js; U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
TRI = "[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] button')]"
NOMES = ['Integrado', 'Satélite', 'Solo', 'Pragas e doenças', 'Ordens de serviço', 'Irrigação', 'Estádio', 'Colheita e produtividade', 'Custos']
MED = ("(()=>{const nav=" + TRI + "[0].closest('nav'); const m=(document.getElementById('mapa-real')||document.querySelector('.mapa-area')).getBoundingClientRect();"
       " const n=document.querySelector('[role=group][aria-label^=\"Indicadores de\"]');"
       " const r=n?n.getBoundingClientRect():null; const f=n?n.firstElementChild:null; const fr=f?f.getBoundingClientRect():null;"
       " return {band:Math.round(m.top-nav.getBoundingClientRect().bottom), numCut:n?n.scrollWidth>n.clientWidth+1:false, primeiro:!f||(fr.left>=r.left-1&&fr.right<=r.right+1), pageX:document.documentElement.scrollWidth>innerWidth+1};})()")
def espera(e, s=15):
    f = time.time() + s
    while time.time() < f:
        if J(e): return True
        time.sleep(.25)
    return False
try:
    for faz in ['Lagoa Grande', 'Santa Rita']:
        for w, toque in [(1440, False), (1280, False), (1024, False), (390, True)]:
            c.aparelho(w, 900 if not toque else 844, 1, toque); c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1")
            J(f"sessionStorage.setItem('mapa-ctx',JSON.stringify({{mf_faz:{json.dumps(faz)}}})); 1"); c.goto(U('IN-04.dc.html'), 2.0)
            espera(f"{TRI}.length>=9")
            med = {}
            for nm in NOMES:
                J(f"(()=>{{const b={TRI}.find(b=>b.innerText.trim()==={json.dumps(nm)}); b&&b.click();}})()")
                espera(f"(()=>{{const b={TRI}.find(b=>b.innerText.trim()==={json.dumps(nm)}); return b&&/rgb\\(228, 243, 233\\)/.test(getComputedStyle(b).backgroundColor);}})()", 6)
                time.sleep(.6); med[nm] = J(MED)
            bs = {k: v['band'] for k, v in med.items()}
            chk(f'F1 {faz} {w}: mesma altura em todas as camadas', max(bs.values()) - min(bs.values()) <= 1, bs)
            if not toque:
                chk(f'F2 {faz} {w}: uma linha só (≤ 56 px)', max(bs.values()) <= 56, bs)
            if w == 1440:   # o caso reclamado (Solo) inteiro; nas demais, o 1º número sempre à vista e o resto rola na própria faixa
                chk(f'F3 {faz} 1440: números do Solo inteiros e o 1º número de toda camada à vista', not med['Solo']['numCut'] and all(v['primeiro'] for v in med.values()),
                    {k: (v['numCut'], v['primeiro']) for k, v in med.items()})
            chk(f'F4 {faz} {w}: sem rolagem lateral da página', not any(v['pageX'] for v in med.values()), [k for k, v in med.items() if v['pageX']])
    # S1: a faixa das fazendas do Planejar safra usa a peça comum dos filtros (funil + "Fazendas" + chips). Ela só aparece em safra de várias
    # fazendas (o fluxo visível está em saf_fazendas_test); aqui se confere a peça na página gerada
    h = open(os.path.join(R, 'SAF.dc.html'), encoding='utf-8').read(); k = h.find('id="saf-fazendas"'); seg = h[h.rfind('<div', 0, k):k + 1600] if k >= 0 else ''
    s1 = dict(achou=k >= 0, comum='class="mf-tela"' in seg[:120], funil='data-dica="Filtros"' in seg and '<svg' in seg, rotulo='>Fazendas<' in seg, chips='as="fz"' in seg)
    chk('S1 Planejar safra: faixa das fazendas na peça comum, com funil, rótulo e chips', all(s1.values()), s1)
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)}/{len(OK)+len(FAIL)}')
sys.exit(0 if not FAIL else 1)
