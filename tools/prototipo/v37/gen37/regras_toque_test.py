# -*- coding: utf-8 -*-
"""UX-C24-REGRAS-01 (revisão Codex de 14/10/2026, S3): o ⓘ que guarda as regras da tela (antes texto do rodapé) e a fonte da camada do Mapa
abre com toque curto no celular, como o ícone de dica. Confere no navegador:
  R1 390 × 844 com toque: tocar no ⓘ "Regras desta tela" (Orçamento, GE-02) abre a dica com o texto das regras; tocar de novo fecha
  R2 390 × 844 com toque: tocar no ⓘ "Fonte e regra da camada" do Mapa abre a dica com a fonte da camada
  R3 o alvo do ⓘ tem pelo menos 44 × 44 px no celular
  R4 1440 × 900: foco pelo teclado abre e Escape fecha; o mouse sobre o ⓘ abre (sem regressão)
  R5 sem erro de JS
Uso: python3 regras_toque_test.py (lê _render ou RENDER_DIR)."""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault('CDP_GL', '1')
from comp_lib import Chrome, servir

OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:700]), flush=True)
R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
p, srv = servir(R); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
DICA = "JSON.stringify((()=>{const d=document.getElementById('g2-dica'); return d&&!d.hidden&&d.getClientRects().length?d.innerText.trim():'';})())"
def dica(): return json.loads(J(DICA) or '""')
def centro(sel): return json.loads(J(f"JSON.stringify((()=>{{const b=document.querySelector({json.dumps(sel)}); if(!b) return null; const r=b.getBoundingClientRect(); return {{x:r.left+r.width/2,y:r.top+r.height/2,w:r.width,h:r.height}};}})())") or 'null')
REG = 'button.g2-info[aria-label="Regras desta tela"]'; CAM = 'main button.g2-info[aria-label="Fonte e regra da camada"]'
try:
    c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__err='';addEventListener('error',e=>{window.__err+=(e.message||'erro')+' | ';});"})
    c.aparelho(390, 844, 2, True); c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1")
    c.goto(U('GE-02.dc.html'), 1.4); regra = J(f"(document.querySelector({json.dumps(REG)})||{{}}).getAttribute&&document.querySelector({json.dumps(REG)}).getAttribute('data-dica')") or ''
    b = centro(REG); d1 = d2 = ''
    if b: c.toque(b['x'], b['y']); time.sleep(.4); d1 = dica(); c.toque(b['x'], b['y']); time.sleep(.4); d2 = dica()
    chk('R1 GE-02 390 px: toque curto no ⓘ "Regras desta tela" abre a dica com as regras; tocar de novo fecha', bool(b) and bool(regra) and d1 == regra.strip() and d2 == '', [b, regra[:80], d1[:80], d2[:80]])
    c.goto(U('IN-04.dc.html'), 1.6); bm = centro(CAM); fonte = J(f"(document.querySelector({json.dumps(CAM)})||{{getAttribute:()=>''}}).getAttribute('data-dica')") or ''
    dm = ''
    if bm: c.toque(bm['x'], bm['y']); time.sleep(.4); dm = dica()
    chk('R2 Mapa 390 px: toque curto no ⓘ da camada abre a dica com a fonte', bool(bm) and bool(fonte) and dm == fonte.strip(), [bm, fonte[:80], dm[:80]])
    chk('R3 alvo do ⓘ ≥ 44 × 44 px no celular (regras e camada)', bool(b) and bool(bm) and min(b['w'], b['h'], bm['w'], bm['h']) >= 44, [b, bm])
    e1 = J("window.__err") or ''
    c.aparelho(1440, 900, 1, False); c.goto(U('GE-02.dc.html'), 1.2)
    J(f"document.querySelector({json.dumps(REG)}).focus()"); c.tecla('Tab', 'Tab', 9, mod=8); c.tecla('Tab', 'Tab', 9); time.sleep(.4); k1 = dica()
    c.tecla('Escape', 'Escape', 27); time.sleep(.3); k2 = dica()
    b4 = centro(REG); c.mouse(b4['x'], b4['y']); time.sleep(.6); h1 = dica()
    chk('R4 1440 px: foco pelo teclado abre e Escape fecha; mouse sobre o ⓘ abre', k1 == regra.strip() and k2 == '' and h1 == regra.strip(), [k1[:60], k2[:60], h1[:60]])
    chk('R5 sem erro de JS', not e1 and not (J("window.__err") or ''), [e1, J("window.__err")])
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas')
sys.exit(1 if FAIL else 0)
