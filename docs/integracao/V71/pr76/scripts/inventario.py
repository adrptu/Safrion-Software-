# Inventário: caixa de borda 16 px dentro do main (cartão do section(), kpi, card()) com o conteúdo passando da borda inferior
# (scrollHeight > clientHeight + 2, overflow visível). Uso: python3 inventario.py <dir_render>   (uma linha por página com achado)
import os, sys, json
from _base import Chrome, servir, TAMANHOS
R = sys.argv[1]
JS = r"""(()=>{ const out=[]; document.querySelectorAll('main div[style*="border-radius: 16px"]').forEach(d=>{ if(!d.offsetParent) return;
  if(getComputedStyle(d).overflowY!=='visible') return; if(d.scrollHeight>d.clientHeight+2) out.push([d.parentElement.matches('main')?'filho':'aninhado', d.clientHeight, d.scrollHeight,
  d.style.flex||'', d.textContent.replace(/\s+/g,' ').trim().slice(0,30)]); }); return out; })()"""
pags = sorted(f for f in os.listdir(R) if f.endswith('.html'))
p, s = servir(R); c = Chrome(); n = 0
try:
    for w, h in TAMANHOS:
        c.aparelho(w, h, toque=(w < 600))
        for f in pags:
            c.goto(f'http://127.0.0.1:{p}/{f}', .9)
            try: v = c.js(JS)
            except Exception as e: v = [['erro', str(e)[:80]]]
            if v: n += 1; print(w, f, json.dumps(v, ensure_ascii=False), flush=True)
finally:
    c.close(); s.terminate()
print('TOTAL', n, 'páginas×tamanhos com cartão espremido')
