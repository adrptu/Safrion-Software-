# -*- coding: utf-8 -*-
"""MAPA-REAL F2 · tela "sem dado" (Codex 6270730787, item 1). O Mapa recebe da montagem (lagoa_sat.sat_v) None no índice sem leitura
válida; aqui a página do Mapa é servida com esse caso injetado no dado da página (PV05 sem NDMI na cena mais recente da Lagoa Grande),
sem mexer no código da tela.
  D1 Satélite em NDMI, PV05: o painel diz "sem dado de NDMI" e "Sem dado · leitura mascarada ou inválida", lista os outros índices com valor e o NDMI "sem dado";
     nunca "sem cultura", nunca 0
  D2 Satélite em NDVI, PV05: o NDVI tem valor e a lista mostra "NDMI · sem dado" (o resto do pivô segue)
  D3 sem erro de JavaScript
Contraprova: RENDER_DIR=<render da base e32ada5e> reprova D1 e D2 (lá o null vira "sem cultura").
Uso (de gen37/): env CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico python3 -B mapa_real_semdado_test.py"""
import os, sys, json, time, shutil, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
from mapa_mux_lib import chk, OK, FAIL, espera, abre, fazenda, camada, filtro, caixa, erros

R0 = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
D = tempfile.mkdtemp(prefix='semdado_')
for f in os.listdir(R0):
    if f != 'IN-04.dc.html': os.symlink(os.path.join(R0, f), os.path.join(D, f))
h = open(os.path.join(R0, 'IN-04.dc.html'), encoding='utf-8').read(); i = h.index('const M = ') + len('const M = ')
M, fim = json.JSONDecoder().raw_decode(h, i)
CEN = next(k for k, s in M['sat'].items() if s.get('real') and isinstance(s['v'].get('PV05'), list))
M['sat'][CEN]['v']['PV05'][M['idxn'].index('NDMI')] = None
open(os.path.join(D, 'IN-04.dc.html'), 'w', encoding='utf-8').write(h[:i] + json.dumps(M, ensure_ascii=False).replace('</', '<\\/') + h[fim:])
p, srv = servir(D); c = Chrome(); J = c.js
U = f'http://127.0.0.1:{p}/IN-04.dc.html'
PAINEL = "(()=>{const a=document.querySelector('main aside[data-mux-painel]'); return a?a.innerText.replace(/\\s+/g,' ').trim():'';})()"
def abre_pv05(ix):
    abre(c, U, 1440, 900, False, faz='Lagoa Grande'); camada(J, 'Satélite'); filtro(J, 'Índice', ix); filtro(J, 'Cena', CEN); time.sleep(.4)
    b = caixa(J, 'PV05'); c.mouse(b['x'], b['y'], 'mousePressed', 'left'); c.mouse(b['x'], b['y'], 'mouseReleased', 'left')
    espera(J, "!!document.querySelector('main aside[data-mux-painel]')", 4); time.sleep(.6); return J(PAINEL) or ''
try:
    t = abre_pv05('NDMI')
    chk(f'D1 NDMI sem leitura no PV05 (cena {CEN}): rótulo "sem dado de NDMI", estado "Sem dado · leitura mascarada ou inválida", os outros índices com valor e "NDMI · sem dado"; nunca "sem cultura" nem NDMI 0',
        'sem dado de NDMI' in t and 'Sem dado · leitura mascarada ou inválida' in t and 'NDMI · sem dado' in t and 'NDVI 0,' in t and 'sem cultura' not in t and 'NDMI 0,' not in t, t[:900])
    t = abre_pv05('NDVI')
    chk('D2 NDVI do PV05 segue com valor e a lista mostra "NDMI · sem dado"', 'NDVI 0,' in t and 'NDMI · sem dado' in t and 'Sem dado de NDVI' not in t, t[:900])
except Exception as ex:
    chk('roteiro', False, repr(ex)[:600])
finally:
    try: chk('D3 sem erro de JavaScript', not erros(J), erros(J)[:3])
    except Exception as ex: chk('D3 sem erro de JavaScript', False, repr(ex)[:300])
    try: c.close()
    except Exception: pass
    srv.terminate(); shutil.rmtree(D, ignore_errors=True)
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas', flush=True); sys.exit(1 if FAIL else 0)
