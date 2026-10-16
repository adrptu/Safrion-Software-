# Retrato do layout vertical de todas as páginas: main [clientHeight, scrollHeight], filhos diretos do main, cartões do section()
# em qualquer nível e áreas que rolam por dentro (.g2rola/.rola) [clientHeight, scrollHeight]. Uso: python3 retrato.py <dir_render> <saida.json>
import os, sys, json
from _base import Chrome, servir, TAMANHOS
R, OUT = sys.argv[1], sys.argv[2]
JS = r"""(()=>{ const m=document.querySelector('main[data-scroll]')||document.querySelector('main'); if(!m) return null; const H=e=>Math.round(e.getBoundingClientRect().height);
 const t=e=>e.textContent.replace(/\s+/g,' ').trim().slice(0,30);
 return {main:[m.clientHeight,m.scrollHeight], filhos:[...m.children].map(d=>[d.tagName,H(d),t(d)]),
   cartoes:[...m.querySelectorAll('div[style*="border-radius: 16px"][style*="flex: 1 1 0"]')].map(d=>[H(d),t(d)]),
   rolas:[...m.querySelectorAll('.g2rola,.rola')].map(d=>[d.clientHeight,d.scrollHeight])}; })()"""
pags = sorted(f for f in os.listdir(R) if f.endswith('.html'))
p, s = servir(R); c = Chrome(); res = {}
try:
    for w, h in TAMANHOS:
        c.aparelho(w, h, toque=(w < 600))
        for f in pags:
            c.goto(f'http://127.0.0.1:{p}/{f}', .9)
            try: res[f'{w} {f}'] = c.js(JS)
            except Exception as e: res[f'{w} {f}'] = {'erro': str(e)[:80]}
finally:
    c.close(); s.terminate()
json.dump(res, open(OUT, 'w'), ensure_ascii=False, indent=0); print('páginas×tamanhos:', len(res))
