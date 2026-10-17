# -*- coding: utf-8 -*-
"""Fotos da frente DRILL-RECOLHIDO (TAB-12): Planejar safra › etapa 2 › "Talhões e cultivos", com 1 fazenda (S2627) e com 2 fazendas
(S27SF + Boa Vista incluída pela faixa "Trabalhando em"), a 1440 × 900 e 390 × 844, na abertura. Rodar uma vez por render:
  RENDER_DIR=<_render> FOTO_TAG=antes|depois python3 -B docs/integracao/V73/drill-recolhido/fotos.py
Saída: <tag>_saf2_<1faz|2faz>_<1440|390>.jpg nesta pasta. Dados sintéticos; emulação no Chrome headless, não é aparelho físico."""
import os, sys, time, base64
AQUI = os.path.dirname(os.path.abspath(__file__))
G = os.path.abspath(os.path.join(AQUI, '..', '..', '..', '..', 'tools', 'prototipo', 'v37', 'gen37')); sys.path.insert(0, G)
from comp_lib import Chrome, servir
R = os.environ['RENDER_DIR']; TAG = os.environ.get('FOTO_TAG', 'depois')
p, srv = servir(R); c = Chrome(); J = c.js; B = f'http://127.0.0.1:{p}/'
def espera(expr, lim=8.0):
    fim = time.monotonic() + lim
    while time.monotonic() < fim:
        try:
            if J('(()=>{try{return !!(' + expr + ')}catch(e){return false}})()'): return True
        except Exception: pass
        time.sleep(.1)
    return False
def foto(nome):
    J("(()=>{ const t=document.querySelector('[role=table][data-g2g^=\"g_cult_\"]'); if(t) t.scrollIntoView({block:'start'}); })()"); time.sleep(.4)
    d = c.call('Page.captureScreenshot', {'format': 'jpeg', 'quality': 70})
    open(os.path.join(AQUI, f'{TAG}_{nome}.jpg'), 'wb').write(base64.b64decode(d['data'])); print('foto', f'{TAG}_{nome}.jpg', flush=True)
try:
    for w in (1440, 390):
        h, e, t = (900, 1, False) if w > 500 else (844, 2, True); c.aparelho(w, h, e, t)
        for faz, h2 in (('1faz', '#saf=S2627&passo=cultivos'), ('2faz', '#saf=S27SF&passo=cultivos')):
            c.goto(B + 'Main.dc.html', .2); J("localStorage.clear();sessionStorage.clear();localStorage.setItem('safrion.perfilDemo','Ana')")
            c.goto(B + f'SAF.dc.html?f={faz}{w}{h2}', 1.4); espera("document.querySelector('[role=table]')")
            if faz == '2faz':
                J("document.getElementById('sfz-add')&&document.getElementById('sfz-add').click()"); espera("!!document.getElementById('sfz-pop')")
                J("(()=>{ const l=[...document.querySelectorAll('#sfz-pop label')].find(l=>l.querySelector('b')&&l.querySelector('b').innerText.trim()==='Boa Vista'); if(l) l.querySelector('input').click(); })()")
                espera("/Boa Vista entrou/.test(document.body.innerText)"); c.tecla('Escape', 'Escape', 27); espera("!document.getElementById('sfz-pop')"); time.sleep(.6)
            foto(f'saf2_{faz}_{w}')
finally:
    c.close(); srv.terminate()
