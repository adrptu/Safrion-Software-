# -*- coding: utf-8 -*-
"""Capturas do Mapa (IN-04) antes e depois da MUX-F0/F1/F2: 1440 × 900 e 390 × 844, Lagoa Grande (fazenda padrão) nas camadas Integrado,
Satélite e Pragas e doenças; mais o cartão do hover, o painel do pivô, a Lista e o toque no celular.
Uso (de tools/prototipo/v37/gen37/): env CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico python3 -B <este arquivo> <render> <antes|depois> <pasta de saída>
Só lê o render; nenhum dado real."""
import os, sys, time, json
G = os.getcwd(); sys.path.insert(0, G)
from comp_lib import Chrome, servir
from mapa_mux_lib import espera, abre, camada, caixa, pivo_livre, LG_PRONTO

render, tag, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
p, srv = servir(render); c = Chrome(); J = c.js
U = f'http://127.0.0.1:{p}/IN-04.dc.html'
def foto(nome): c.shot(os.path.join(out, f'{tag}_{nome}.png')); print('foto', f'{tag}_{nome}.png', flush=True)
def pronto(): espera(J, "!!(window.__LGI&&window.__LGI.pronto)", 25); time.sleep(1.2)
def clique(t):
    b = caixa(J, t)
    if b: c.mouse(b['x'], b['y']); c.mouse(b['x'], b['y'], 'mousePressed', 'left'); c.mouse(b['x'], b['y'], 'mouseReleased', 'left')
try:
    for larg, alt, toque in ((1440, 900, False), (390, 844, True)):
        c.aparelho(larg, alt, 1, toque); c.goto(U, 1.5)
        if toque:   # sessão nova no celular: a câmera guardada pela vista larga (mapa-cam) não vale para a estreita
            J("sessionStorage.removeItem('mapa-cam')"); c.goto(U, 1.5)
        pronto()
        for cam, nome in (('Integrado', 'integrado'), ('Satélite', 'satelite'), ('Pragas e doenças', 'pragas')):
            camada(J, cam); time.sleep(1.0); foto(f'{larg}_{nome}')
        if not toque:
            camada(J, 'Pragas e doenças'); b = caixa(J, 'PV06') or {'x': 700, 'y': 450}
            c.mouse(b['x'] - 150, b['y'] - 120); time.sleep(.2); c.mouse(b['x'] + 2, b['y'] + 2); time.sleep(.8); foto(f'{larg}_hover_pragas')
            clique('PV06'); time.sleep(1.4); c.mouse(5, 895); time.sleep(.6); foto(f'{larg}_painel_pragas')
            if tag == 'depois':
                J("(()=>{const g=document.querySelector('[role=group][aria-label=\"Ver dados\"]'); const b=g&&[...g.querySelectorAll('button')].find(x=>x.innerText.trim()==='Lista'); b&&b.click();})()"); time.sleep(1.0); foto(f'{larg}_lista_pragas')
                J("(()=>{const g=document.querySelector('[role=group][aria-label=\"Ver dados\"]'); const b=g&&[...g.querySelectorAll('button')].find(x=>x.innerText.trim()==='Mapa'); b&&b.click();})()"); time.sleep(.6)
                J("(()=>{const a=document.querySelector('main aside [aria-label=\"Fechar painel\"]'); a&&a.click();})()"); time.sleep(.6)
                # foco de teclado: o mesmo cartão (Tab até o grupo, setas)
                J("document.querySelector('nav[aria-label=\"Funcionalidades do mapa\"] [aria-selected=true]').focus()")
                for _ in range(30):
                    c.tab(); time.sleep(.08)
                    if J("!!(document.activeElement&&document.activeElement.closest('[data-mux-grupo]'))"): break
                c.tecla('ArrowRight', 'ArrowRight', 39); time.sleep(.6); foto(f'{larg}_foco_teclado')
        else:
            camada(J, 'Pragas e doenças'); b = pivo_livre(J) or {'x': 200, 'y': 500}   # um pivô com o centro livre na vista estreita
            c.toque(b['x'], b['y']); time.sleep(1.6); foto(f'{larg}_toque_painel')
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
