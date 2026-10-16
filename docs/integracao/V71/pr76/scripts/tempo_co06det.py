# CO-06det em 390 × 844: altura dos filhos do main e das áreas que rolam por dentro logo ao carregar e 1,5 s / 3 s depois.
# Mostra que a diferença do retrato nessa tela é instabilidade da medida (igual nos dois renders). Uso: python3 tempo_co06det.py <dir_render> [...]
import os, sys, json, time
from _base import Chrome, servir
JS = r"""(()=>{ const m=document.querySelector('main[data-scroll]'); const H=e=>Math.round(e.getBoundingClientRect().height);
 return {filhos:[...m.children].map(d=>[H(d),getComputedStyle(d).minHeight,d.textContent.replace(/\s+/g,' ').trim().slice(0,24)]), rolas:[...m.querySelectorAll('.g2rola,.rola')].map(d=>[d.clientHeight,d.scrollHeight])}; })()"""
for R in sys.argv[1:]:
    p, s = servir(R); c = Chrome()
    try:
        c.aparelho(390, 844, toque=True)
        for k in range(3):
            c.goto(f'http://127.0.0.1:{p}/CO-06det.dc.html', .9); time.sleep(k * 1.5)
            print(os.path.basename(os.path.normpath(R)), f'+{k*1.5:.1f}s', json.dumps(c.js(JS), ensure_ascii=False), flush=True)
    finally:
        c.close(); s.terminate()
