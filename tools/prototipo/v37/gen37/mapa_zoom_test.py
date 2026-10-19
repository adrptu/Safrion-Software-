# -*- coding: utf-8 -*-
"""Mapa · afastar até ver a fazenda inteira (proprietário, 19/10: "O mapa tem que permitir mais zoom out para ter a visão da fazenda toda").
No Mapa da Lagoa Grande (MapLibre, imagem de satélite), o afastamento parava quando a imagem ainda cobria a tela: a 1440 × 900 a fazenda
ficava cortada em cima e embaixo, e a 390 px, dos lados. Agora o afastamento vai até a imagem inteira caber na tela, com folga.
  Z1 1440 × 900: no menor zoom, a caixa dos pivôs (M.lg.bbox) cabe inteira na área visível do mapa
  Z2 390 × 844 (toque): idem
  Z3 o botão "−" chega ao menor zoom (o mesmo limite do gesto)
  Z4 sem erro de JavaScript
Contraprova: RENDER_DIR=<render anterior> reprova Z1 e Z2 (o menor zoom ainda cortava a fazenda).
Uso (de gen37/): env CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico python3 -B mapa_zoom_test.py"""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
from mapa_mux_lib import chk, OK, FAIL, espera, abre, erros

R0 = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
p, srv = servir(R0); c = Chrome(); J = c.js
U = f'http://127.0.0.1:{p}/IN-04.dc.html'
h = open(os.path.join(R0, 'IN-04.dc.html'), encoding='utf-8').read(); i = h.index('const M = ') + len('const M = ')
_b = json.JSONDecoder().raw_decode(h, i)[0]['lg']['bbox']; BBOX = [_b[0][0], _b[0][1], _b[1][0], _b[1][1]]   # caixa dos pivôs da Lagoa Grande, a mesma que a página usa (oeste, sul, leste, norte)
CABE = """(()=>{const m=window.__LGI&&window.__LGI.map; if(!m) return null; const b=m.getBounds(), x=%s;""" % json.dumps(BBOX) + """
  return {z:+m.getZoom().toFixed(2), zmin:+m.getMinZoom().toFixed(2), cabe:b.getWest()<=x[0]&&b.getSouth()<=x[1]&&b.getEast()>=x[2]&&b.getNorth()>=x[3],
          vis:[b.getWest(),b.getSouth(),b.getEast(),b.getNorth()].map(v=>+v.toFixed(4)), faz:x.map(v=>+v.toFixed(4))};})()"""
def ao_minimo():
    cx, cy = (BBOX[0] + BBOX[2]) / 2, (BBOX[1] + BBOX[3]) / 2   # centrado na fazenda, como abre o Mapa
    J(f"(()=>{{const m=window.__LGI.map; m.jumpTo({{center:[{cx},{cy}],zoom:m.getMinZoom()}});}})()"); time.sleep(.8)
    return J(CABE)
try:
    abre(c, U, 1440, 900, False, faz='Lagoa Grande'); r1 = ao_minimo()
    chk('Z1 1440 × 900: no menor zoom, a fazenda inteira (caixa dos pivôs) cabe na área visível do mapa', bool(r1 and r1['cabe']), r1)
    J(f"(()=>{{const m=window.__LGI.map; m.jumpTo({{center:[{(BBOX[0]+BBOX[2])/2},{(BBOX[1]+BBOX[3])/2}],zoom:m.getMinZoom()+2}});}})()"); time.sleep(.6)
    b = "[...document.querySelectorAll('button')].find(x=>x.getClientRects().length&&/^(Afastar|Diminuir zoom|Zoom out|−)/i.test((x.getAttribute('aria-label')||x.innerText||'').trim()))"
    n = 0
    while n < 12 and J(f"!!{b}"):
        z0 = J("window.__LGI.map.getZoom()"); J(f"{b}.click()"); time.sleep(.5); n += 1
        if abs(J("window.__LGI.map.getZoom()") - z0) < 1e-3: break
    r3 = J(CABE)
    chk('Z3 o botão "−" chega ao menor zoom e a fazenda inteira fica à vista', bool(r3 and abs(r3['z'] - r3['zmin']) < 0.05 and r3['cabe']), [n, r3])
    abre(c, U, 390, 844, True, faz='Lagoa Grande'); r2 = ao_minimo()
    chk('Z2 390 × 844: no menor zoom, a fazenda inteira cabe na área visível do mapa', bool(r2 and r2['cabe']), r2)
except Exception as ex:
    chk('roteiro', False, repr(ex)[:600])
finally:
    try: chk('Z4 sem erro de JavaScript', not erros(J), erros(J)[:3])
    except Exception as ex: chk('Z4 sem erro de JavaScript', False, repr(ex)[:300])
    try: c.close()
    except Exception: pass
    srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas', flush=True); sys.exit(1 if FAIL else 0)
