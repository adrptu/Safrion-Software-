# -*- coding: utf-8 -*-
"""Padronização do design system (proprietário, 15/10/2026: "tem várias tela com design system diferente, padronize tudo de melhor que
definimos e evoluimos"). Confere no navegador as regras dos componentes comuns, não tela a tela:
  T · alvo de toque (DS-ALVO-20261015): a 390 × 844 com toque, botão do componente (BTN_ST/btn, _MINI, ação de célula g2cta) e escolha em
      pílula (chip de filtro rápido, aria-pressed) têm pelo menos 44 px de altura; a 1440 × 900 com mouse nada cresce (compacto < 44 px).
Uso (de gen37/, depois de build.py e montar_render.py): python3 ds_padrao_test.py · RENDER_DIR=<dir> serve outro _render."""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:900]), flush=True)
R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
p, srv = servir(R); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
def abre(pg, w=1.2): c.goto(U(pg), w); time.sleep(.3)

# ---------- T · alvo de toque ----------
# componente: estilo inline com a variável do alvo (BTN_ST, btn, _MINI, act), a ação de célula (.g2cta) e a escolha em pílula com estado
ALVOS = r"""JSON.stringify((()=>{const vis=e=>e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden';
  const n=s=>(s||'').replace(/\s+/g,' ').trim();
  return [...document.querySelectorAll('main button, main a[href], header button, header a[href]')].filter(vis).filter(e=>!e.closest('[role=dialog],aside,.menu-lat'))
    .filter(e=>/--g2-alvo/.test(e.getAttribute('style')||'')||e.classList.contains('g2cta')||(e.hasAttribute('aria-pressed')&&/border-radius: 999px/.test(e.getAttribute('style')||'')))
    .map(e=>({t:n(e.innerText||e.getAttribute('aria-label')).slice(0,30),h:Math.round(e.getBoundingClientRect().height*10)/10,k:e.classList.contains('g2cta')?'g2cta':(e.hasAttribute('aria-pressed')?'chip':'btn')}));})())"""
PAG_T = ['AG-01.dc.html', 'GE-02.dc.html', 'PL-03.dc.html', 'IR-01.dc.html', 'CO-02.dc.html', 'VE-01.dc.html']
try:
    c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__err='';addEventListener('error',e=>{window.__err+=(e.message||'erro')+' | ';});"})
    c.aparelho(390, 844, 2, True)
    baixos = {}; tipos = set(); total = 0
    for pg in PAG_T:
        abre(pg); a = json.loads(J(ALVOS) or '[]'); total += len(a); tipos |= {x['k'] for x in a}
        b = [x for x in a if x['h'] < 44]
        if b: baixos[pg] = b[:5]
    chk('T1 390 px com toque: botão do componente, ação de célula da grade e chip de filtro rápido com alvo ≥ 44 px (6 telas)',
        total >= 20 and not baixos and {'btn', 'g2cta', 'chip'} <= tipos, [total, sorted(tipos), baixos])
    c.aparelho(1440, 900, 1, False)
    abre('AG-01.dc.html'); a = json.loads(J(ALVOS) or '[]')
    chk('T2 1440 px com mouse: nada cresce (ação de célula e chip continuam compactos, < 44 px)',
        a and min(x['h'] for x in a) < 40 and any(x['k'] == 'g2cta' and x['h'] < 40 for x in a), a[:6])
    st = json.loads(J("JSON.stringify((()=>{const b=document.querySelector('a.g2cta,button.g2cta'); if(!b) return null; const s=getComputedStyle(b); return [s.paddingTop+' '+s.paddingRight,s.borderTopLeftRadius,s.fontSize,s.fontWeight];})())") or 'null')
    chk('T3 ação de célula da grade (g2cta) com o desenho do _MINI do engine: 5px 10px, raio 8 px, 12 px/700', st == ['5px 10px', '8px', '12px', '700'], st)
    chk('T9 sem erro de JS', not (J("window.__err") or ''), J("window.__err"))
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas')
sys.exit(1 if FAIL else 0)
