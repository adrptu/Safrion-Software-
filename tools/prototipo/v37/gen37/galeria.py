# -*- coding: utf-8 -*-
"""Galeria de conferência visual (skill padrao-safrion, passo 7): uma tela de cada família, em 1440 px e 390 px, para o agente OLHAR antes
de publicar (teste verde não vê poluição visual nem desalinhamento). Fotos em GALERIA_DIR (padrão: _galeria/), uma por tela e largura.
Famílias: lista do motor (O.S.), árvore (Produtos), agrupada (O.S. por talhão), cadastro (Parceiros, Fazendas), Atividades do plano
(Tabela e Cartões), Planejar safra, Kanban, formulário, Mapa e app de campo. Dados sintéticos; render em RENDER_DIR ou _render.
Uso (de gen37/): CHROME_BIN=… SAFRION_DADOS=sintetico python3 -B galeria.py [filtro]   (filtro: parte do nome da foto)"""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
OUT = os.environ.get('GALERIA_DIR') or os.path.join(HERE, '_galeria')
# (nome, endereço, ação JS depois de carregar ou '')
TELAS = [
    ('os_tabela', 'OS.dc.html', ''),
    ('os_cartoes_talhao', 'OS.dc.html?view=cartoes', ''),
    ('pa_tabela', 'PA.dc.html?view=tabela#plano=SOJA-AT', ''),
    ('pa_cartoes', 'PA.dc.html#plano=SOJA-AT', ''),
    ('saf_etapa2_tabela', 'SAF.dc.html', ''),
    ('saf_etapa2_cartoes', 'SAF.dc.html?view=cartoes', ''),
    ('cd05_parceiros', 'CD-05.dc.html', ''),
    ('cd05_parceiros_cartoes', 'CD-05.dc.html?view=cartoes', ''),
    ('cd01_fazendas', 'CD-01.dc.html', ''),
    ('cd06_produtos_arvore', 'CD-06.dc.html', ''),
    ('cd06_produtos_cartoes', 'CD-06.dc.html?view=cartoes', ''),
    ('ma_ativos', 'MA.dc.html', ''),
    ('agrofit', 'AG-08.dc.html', ''),
    ('est_recebimento', 'EST.dc.html', ''),
    ('mapa', 'Main.dc.html', ''),
    ('cadastros_inicio', 'CD.dc.html', ''),
]
def main():
    filtro = sys.argv[1] if len(sys.argv) > 1 else ''
    os.makedirs(OUT, exist_ok=True)
    p, srv = servir(R); c = Chrome(); J = c.js
    B = f'http://127.0.0.1:{p}/'
    feitas = []
    for w, h, esc, toque in [(1440, 900, 1, False), (390, 844, 2, True)]:
        c.aparelho(w, h, esc, toque)
        for nome, url, acao in TELAS:
            if filtro and filtro not in nome: continue
            if not os.path.exists(os.path.join(R, url.split('?')[0].split('#')[0])): continue
            c.goto(B + 'Main.dc.html', .3); J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
            c.goto(B + url, 1.6)
            if acao: J(acao); time.sleep(.5)
            f = os.path.join(OUT, f'{nome}_{w}.png'); c.shot(f); feitas.append(f)
    c.close()
    print('\n'.join(feitas)); print(f'RESULTADO: {len(feitas)} fotos em {OUT} (olhe cada uma antes de publicar)')
if __name__ == '__main__':
    main()
