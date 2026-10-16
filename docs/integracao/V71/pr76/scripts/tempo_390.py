# Repetição da medida do retrato.py em 390 × 844 para as telas dadas, logo ao carregar e 1,5 s / 3 s depois, em cada render.
# Separa instabilidade de tempo (a mesma sequência nos dois renders) de efeito da mudança. Uso: python3 tempo_390.py <tela,tela> <dir_render> [...]
import os, sys, json, time
from _base import Chrome, servir
JS = r"""(()=>{ const m=document.querySelector('main[data-scroll]')||document.querySelector('main'); const H=e=>Math.round(e.getBoundingClientRect().height);
 return {main:[m.clientHeight,m.scrollHeight], cartoes:[...m.querySelectorAll('div[style*="border-radius: 16px"][style*="flex: 1 1 0"]')].map(d=>H(d)),
   rolas:[...m.querySelectorAll('.g2rola,.rola')].map(d=>[d.clientHeight,d.scrollHeight])}; })()"""
telas = sys.argv[1].split(',')
for R in sys.argv[2:]:
    p, s = servir(R); c = Chrome()
    try:
        c.aparelho(390, 844, toque=True)
        for f in telas:
            for k in range(3):
                c.goto(f'http://127.0.0.1:{p}/{f}.dc.html', .9); time.sleep(k * 1.5)
                print(os.path.basename(os.path.normpath(R)), f, f'+{k*1.5:.1f}s', json.dumps(c.js(JS), ensure_ascii=False), flush=True)
    finally:
        c.close(); s.terminate()
