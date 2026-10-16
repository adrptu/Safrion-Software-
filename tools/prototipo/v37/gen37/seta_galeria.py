# -*- coding: utf-8 -*-
"""Galeria antes/depois da TAB-11 (seta única, 16/10/2026; skill padrao-safrion, passo 7): as telas da captura do proprietário e as que tinham
seta própria, a 1440 × 900 e a 390 × 844 (toque), para OLHAR antes de entregar. Cada foto é o estado em que a seta aparece aberta e fechada.
Uso (de gen37/): CHROME_BIN=… SAFRION_DADOS=sintetico python3 -B seta_galeria.py <rótulo> [RENDER_DIR]   · fotos JPEG em SETA_GAL_DIR
(padrão: ../../../../docs/integracao/V73/seta/fotos), com o nome <tela>_<largura>_<rótulo>.jpg. Dados sintéticos."""
import os, sys, time, base64
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
ROT = sys.argv[1] if len(sys.argv) > 1 else 'depois'
R = sys.argv[2] if len(sys.argv) > 2 else (os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render'))
OUT = os.environ.get('SETA_GAL_DIR') or os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', 'docs', 'integracao', 'V73', 'seta', 'fotos'))
os.makedirs(OUT, exist_ok=True)
# abre a 1ª seta fechada (botão com aria-expanded=false) que casa o seletor, para a foto ter as duas posições
ABRE = "((sel)=>{ const b=[...document.querySelectorAll(sel)].find(b=>b.getClientRects().length&&b.getAttribute('aria-expanded')==='false'); if(!b) return 'sem seta fechada'; b.scrollIntoView({block:'center'}); b.click(); return 'ok'; })"
CLICA_TXT = "((t)=>{ const b=[...document.querySelectorAll('button')].find(b=>b.getClientRects().length&&b.innerText.replace(/\\s+/g,' ').trim().replace(/^[▸▾]\\s*/,'').replace(/\\s*▾$/,'')===t); if(!b) return 'sem '+t; b.click(); return 'ok'; })"
TELAS = [   # (nome, endereço, ações [(js, espera)])
    ('cd01_arvore', 'CD-01.dc.html', []),                                            # a captura do proprietário: grupo e talhões
    ('co06_lotes', 'CO-06.dc.html', [(f"{ABRE}('[role=list] button[aria-expanded]')", .6)]),
    ('pa_atividades_tabela', 'PA.dc.html?view=tabela#plano=SOJA-AT', [(f"{ABRE}('.pa-tb .g2car')", .6)]),
    ('pa_atividades_cartoes', 'PA.dc.html#plano=SOJA-AT', [(f"{ABRE}('.pa-atividade .g2car')", .6)]),
    ('saf_capacidade', 'SAF.dc.html#saf=S2627&passo=operacoes', [(f"{CLICA_TXT}('Capacidade por mês')", .9)]),
    ('ma_ativo_blocos', 'MA.dc.html#ativo=a01', []),
    ('ma_plano_servicos', 'MA.dc.html#plano=PM-01', [(f"{ABRE}('.pm-sv .g2car')", .6)]),
    ('colh_colheita', 'COLH.dc.html', []),
    ('cd06_cartoes', 'CD-06.dc.html?view=cartoes', [(f"{ABRE}('[data-g2cd] .g2cd-nk')", .6)]),
    ('os_painel_secoes', 'OS.dc.html#OS-0420', []),
]
p, srv = servir(R); c = Chrome(); J = c.js; B = f'http://127.0.0.1:{p}/'; fotos = []
try:
    for w in (1440, 390):
        h, e, t = (900, 1, False) if w > 500 else (844, 2, True)
        c.aparelho(w, h, e, t); c.goto(B + 'Main.dc.html', .3); J("localStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
        for nome, url, acoes in TELAS:
            c.call('Page.navigate', {'url': 'about:blank'}); time.sleep(.1); c.goto(B + url, 1.2); r = []
            for js, esp in acoes: r.append(J(js)); time.sleep(esp)
            d = c.call('Page.captureScreenshot', {'format': 'jpeg', 'quality': 78, 'captureBeyondViewport': False})
            f = os.path.join(OUT, f'{nome}_{w}_{ROT}.jpg'); open(f, 'wb').write(base64.b64decode(d['data'])); fotos.append(f)
            print(f'{w} {nome}: {" ".join(map(str, r)) or "estado inicial"} → {os.path.relpath(f, HERE)}', flush=True)
            J("try{localStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')}catch(e){}")
finally:
    c.close(); srv.terminate()
print(f'{len(fotos)} fotos em {OUT}')
