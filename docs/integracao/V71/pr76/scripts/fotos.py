# Fotos rolando até o fim do main, em 1440 × 900 e 390 × 844. Uso: python3 fotos.py <dir_render> <rótulo> <dir_saida> TELA [TELA...]
import os, sys, time
from _base import Chrome, servir, TAMANHOS
R, ROT, OUT, telas = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
os.makedirs(OUT, exist_ok=True); p, s = servir(R); c = Chrome()
try:
    for w, h in TAMANHOS:
        c.aparelho(w, h, toque=(w < 600))
        for f in telas:
            c.goto(f'http://127.0.0.1:{p}/{f}.dc.html', .9); time.sleep(1.2)
            c.js("(()=>{const m=document.querySelector('main[data-scroll]'); m.scrollTop=m.scrollHeight;})()"); time.sleep(.5)
            c.shot(os.path.join(OUT, f'{f}_{w}_{ROT}.png'))
finally:
    c.close(); s.terminate()
print('fotos:', len(telas) * len(TAMANHOS))
