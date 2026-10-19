# -*- coding: utf-8 -*-
"""Menus flutuantes do motor cabem na janela no celular (390 × 844, toque): Agrupar por, Colunas e o filtro de coluna (funil).
Regressão de 16/10: com a TAB-08 no celular o botão "Agrupar por" ficou estreito, à direita, e o menu passava 6 px da borda; a causa era
o limite da posição usar a largura declarada (260/290/280 px) enquanto o menu media mais (padding e borda fora da largura). Correção
na peça comum: box-sizing border-box nos três. Dados sintéticos; render em RENDER_DIR ou _render (contraprova: render de ba0e994).
Uso (de gen37/): CHROME_BIN=… SAFRION_DADOS=sintetico python3 -B popover_390_test.py"""
import sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
OK, FAIL = [], []
def chk(n, c, x=''):
    (OK if c else FAIL).append(n); print(('OK   ' if c else 'FALHA'), n, '' if c else str(x)[:400], flush=True)
p, srv = servir(R); c = Chrome(); J = c.js; B = f'http://127.0.0.1:{p}/'
DENTRO = "(e=>{ if(!e||!e.getClientRects().length) return null; const r=e.getBoundingClientRect(); return {l:Math.round(r.left),r:Math.round(r.right),t:Math.round(r.top),b:Math.round(r.bottom),W:innerWidth,H:innerHeight,ok:r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight}; })"
def toca(sel):
    pt = J(f"(()=>{{const e=document.querySelector({sel!r}); if(!e) return null; e.scrollIntoView({{block:'center'}}); const r=e.getBoundingClientRect(); return [r.x+r.width/2, r.y+r.height/2];}})()")
    if pt: c.toque(*pt); time.sleep(.6)
    return pt
c.aparelho(390, 844, 2, True)
for pg, gid in [('OS', 'g_os'), ('CD-04', 'g_pes'), ('CD-05', None)]:
    c.goto(B + 'Main.dc.html', .3); J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
    c.goto(B + pg + '.dc.html', 1.6)
    g = gid or J("(document.querySelector('[data-g2agb]')||{getAttribute:()=>''}).getAttribute('data-g2agb')")
    toca(f'[data-g2agb="{g}"]'); r = J(f"{DENTRO}(document.querySelector('[data-g2agm=\"{g}\"]'))")
    chk(f'{pg} 390: menu "Agrupar por" aberto e dentro da janela', bool(r) and r['ok'], r)
    c.tecla('Escape', 'Escape', 27); time.sleep(.3)
    toca(f'[data-g2cvb="{g}"]'); r = J(f"{DENTRO}(document.querySelector('[data-g2cv=\"{g}\"]'))")
    chk(f'{pg} 390: painel "Colunas" aberto e dentro da janela', bool(r) and r['ok'], r)
    c.tecla('Escape', 'Escape', 27); time.sleep(.3)
    # funil da última coluna visível (a mais à direita: o caso que encosta na borda)
    pt = J(f"(()=>{{const hs=[...document.querySelectorAll('[data-g2g=\"{g}\"] [role=columnheader]')].filter(h=>h.getClientRects().length); const h=hs[hs.length-1]; const b=h&&[...h.querySelectorAll('button')].reverse().find(x=>/filtr/i.test(x.getAttribute('aria-label')||''));"
           " if(!b) return null; b.scrollIntoView({block:'center',inline:'nearest'}); const r=b.getBoundingClientRect(); return [r.x+r.width/2,r.y+r.height/2];})()")
    if pt: c.toque(*pt); time.sleep(.6)
    r = J(f"{DENTRO}([...document.querySelectorAll('[role=dialog]')].filter(d=>d.getClientRects().length&&getComputedStyle(d).position==='fixed'&&d.querySelector('input')).pop())")
    chk(f'{pg} 390: filtro da última coluna aberto e dentro da janela', bool(pt) and bool(r) and r['ok'], [pt, r])
c.close()
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)}' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
