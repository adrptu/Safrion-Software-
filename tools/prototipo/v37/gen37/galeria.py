# -*- coding: utf-8 -*-
"""Galeria de conferência visual (skill padrao-safrion, passo 7): uma foto por família de tela × largura (1440 e 390 px), para o agente OLHAR
antes de publicar (teste verde não vê poluição visual nem desalinhamento). Fotos em GALERIA_DIR (padrão: _galeria/).
Famílias obrigatórias (FAMILIAS): lista do motor, agrupada, árvore, cadastro, Atividades do plano (Tabela e Cartões), Planejar safra, Kanban,
formulário (aberto pela primária "Criar…"/"Cadastrar…"), mapa e app de campo. Cobertura conferida (revisão do Codex no #73, 16/10/2026):
página ausente no render, estado que não abre (ex.: formulário) ou foto que não sai REPROVA a rodada completa (saída 1) e o inventário
família × largura diz o que faltou. Com filtro (argumento), roda só as fotos cujo nome contém o filtro e declara COBERTURA PARCIAL: serve para
olhar uma mudança, não substitui a rodada completa. Dados sintéticos; render em RENDER_DIR ou _render.
Uso (de gen37/): CHROME_BIN=… SAFRION_DADOS=sintetico python3 -B galeria.py [filtro]"""
import sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
OUT = os.environ.get('GALERIA_DIR') or os.path.join(HERE, '_galeria')
# abrir o formulário pela primária do cabeçalho ("Criar ordem", "Cadastrar parceiro"…) e esperar o painel (aside role=dialog)
ABRE_FORM = ("(()=>{const b=[...document.querySelectorAll('header button, main button')].find(b=>b.getClientRects().length&&/^(Criar|Cadastrar)\\b/.test(b.innerText.trim()));"
             " if(!b) return 'sem primária de criar'; b.click(); return 'ok';})()")
TEM_FORM = "!!document.querySelector('aside[role=dialog]')"
# (família, nome da foto, endereço, ação JS ou '', condição JS que prova o estado ou '')
FAMILIAS = [
    ('lista do motor', 'os_tabela', 'OS.dc.html', '', "!!document.querySelector('[data-g2g]')"),
    ('agrupada', 'os_agrupada_talhao', 'OS.dc.html?ag=onde', '', "!!document.querySelector('[data-rid^=\"grp@\"]')"),
    ('cartões', 'os_cartoes', 'OS.dc.html?view=cartoes', '', "!!document.querySelector('[data-g2cd]')"),
    ('kanban', 'os_kanban', 'OS.dc.html?view=kanban', '', "!!document.querySelector('main') && /A liberar/.test(document.querySelector('main').innerText)"),
    ('formulário', 'os_form_criar', 'OS.dc.html', ABRE_FORM, TEM_FORM),
    ('árvore', 'cd06_produtos_arvore', 'CD-06.dc.html', '', "!!document.querySelector('[data-g2g] .g2car')"),
    ('cadastro', 'cd05_parceiros', 'CD-05.dc.html', '', "!!document.querySelector('[data-g2g]')"),
    ('cadastro', 'cd01_fazendas', 'CD-01.dc.html', '', "!!document.querySelector('[data-g2g]')"),
    ('tabela própria', 'pa_tabela', 'PA.dc.html?view=tabela#plano=SOJA-AT', '', "!!document.querySelector('.pa-tb')"),
    ('cartões próprios', 'pa_cartoes', 'PA.dc.html#plano=SOJA-AT', '', "!!document.querySelector('.pa-atividade')"),
    ('etapas', 'saf_etapas', 'SAF.dc.html', '', "!!document.querySelector('main')"),
    ('manutenção', 'ma_ordens', 'MA.dc.html?vis=ordens', '', "!!document.querySelector('[data-g2g]')"),
    ('consulta', 'agrofit', 'AG-07.dc.html', '', "!!document.querySelector('[data-g2g]')"),
    ('estoque', 'est', 'EST.dc.html', '', "!!document.querySelector('main')"),
    ('mapa', 'mapa', 'IN-04.dc.html', '', "/Mapa da fazenda/.test(document.body.innerText)"),
    ('app de campo', 'mb01_inicio', 'MB-01.dc.html', '', "!!document.querySelector('body') && document.body.innerText.length>50"),
    ('app de campo', 'mb03_turno', 'MB-03.dc.html', '', "!!document.querySelector('body') && document.body.innerText.length>50"),
]
LARGURAS = [(1440, 900, 1, False), (390, 844, 2, True)]

def main():
    filtro = sys.argv[1] if len(sys.argv) > 1 else ''
    os.makedirs(OUT, exist_ok=True)
    from comp_lib import Chrome, servir
    p, srv = servir(R); c = Chrome(); J = c.js
    B = f'http://127.0.0.1:{p}/'
    inv = []   # (família, nome, largura, situação)
    for w, h, esc, toque in LARGURAS:
        c.aparelho(w, h, esc, toque)
        for fam, nome, url, acao, prova in FAMILIAS:
            if filtro and filtro not in nome: continue
            pagina = url.split('?')[0].split('#')[0]
            if not os.path.exists(os.path.join(R, pagina)):
                inv.append((fam, nome, w, 'FALTA: página ausente no render (' + pagina + ')')); continue
            try:
                c.goto(B + 'Main.dc.html', .3); J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana')")
                c.goto(B + url, 1.6)
                if acao:
                    r = J(acao); time.sleep(.6)
                    if r != 'ok': inv.append((fam, nome, w, 'FALTA: estado não abriu (' + str(r) + ')')); continue
                if prova and not J(prova):
                    inv.append((fam, nome, w, 'FALTA: o estado esperado não apareceu')); continue
                f = os.path.join(OUT, f'{nome}_{w}.png'); c.shot(f)
                inv.append((fam, nome, w, 'ok ' + f) if os.path.exists(f) and os.path.getsize(f) > 0 else (fam, nome, w, 'FALTA: foto não gravada'))
            except Exception as e:
                inv.append((fam, nome, w, 'FALTA: ' + str(e)[:120]))
    c.close()
    print(f'{"família":18} {"foto":24} {"largura":>7}  situação')
    for fam, nome, w, s in inv: print(f'{fam:18} {nome:24} {w:>7}  {s}')
    faltas = [x for x in inv if x[3].startswith('FALTA')]
    esperadas = len(FAMILIAS) * len(LARGURAS)
    if filtro:
        print(f'RESULTADO: COBERTURA PARCIAL (filtro "{filtro}"): {len(inv) - len(faltas)} fotos, {len(faltas)} faltas; não substitui a rodada completa')
        return 1 if faltas else 0
    ok = not faltas and len(inv) == esperadas
    print(f'RESULTADO: {len(inv) - len(faltas)}/{esperadas} fotos em {OUT}' + ('' if ok else f' · REPROVADO: {len(faltas)} faltas') + ' (olhe cada uma antes de publicar)')
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
